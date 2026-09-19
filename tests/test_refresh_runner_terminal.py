"""Runner contract tests: acceptance is not completion, and cleanup waits for quiescence."""
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

SCRIPT = Path(__file__).parents[1] / 'marianne/skills/marianne-model-profile-refresh/score/scripts/run_refresh.py'


@pytest.fixture
def runner():
    spec = importlib.util.spec_from_file_location('runner_terminal', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def simulation(tmp_path, monkeypatch, runner):
    monkeypatch.setattr(runner.Path, 'home', classmethod(lambda cls: tmp_path))
    monkeypatch.setattr(runner, 'new_transaction_id', lambda: 'txn-test')
    monkeypatch.setattr(runner, 'build_scope', lambda *args: {'mode': 'broad', 'providers': []})
    monkeypatch.setattr(runner.time, 'sleep', lambda _: None)
    workspace = tmp_path / 'work' / 'txn-test'
    backup = tmp_path / 'backup' / 'txn-test'
    technique = tmp_path / 'technique'
    technique.write_text('original')
    observations = iter([])
    calls = []
    terminal_receipt = None
    with_backup = False

    def run(cmd, **kwargs):
        nonlocal observations
        calls.append(cmd)
        if 'install-temporary-technique' in cmd:
            state = backup / 'technique-recovery/technique-state.json'
            state.parent.mkdir(parents=True)
            state.write_text('{}')
            technique.write_text('temporary')
        elif cmd[:2] == ['mzt', 'run']:
            assert '--json' in cmd
            if with_backup:
                path = backup / 'backup/transaction-state.json'
                path.parent.mkdir()
                path.write_text('{}')
            return subprocess.CompletedProcess(cmd, 0, json.dumps({'job_id': 'job-test', 'status': 'accepted'}))
        elif cmd[:2] == ['mzt', 'status']:
            assert technique.read_text() == 'temporary'
            status = next(observations)
            if status.get('status') in {'completed', 'failed', 'cancelled'} and terminal_receipt:
                (workspace / 'receipt.json').write_text(json.dumps(terminal_receipt))
            return subprocess.CompletedProcess(cmd, 0, json.dumps({'job_id': 'job-test', 'sheets': {}, **status}))
        elif 'restore-temporary-technique' in cmd:
            technique.write_text('original')
        elif 'receipt' in cmd:
            index = cmd.index('receipt')
            Path(cmd[index + 2]).write_text(Path(cmd[index + 1]).read_text())
        return subprocess.CompletedProcess(cmd, 0, '')

    monkeypatch.setattr(runner.subprocess, 'run', run)

    def execute(states, receipt=None, backed_up=False, resume=False):
        nonlocal observations, terminal_receipt, with_backup
        observations = iter(states)
        terminal_receipt, with_backup = receipt, backed_up
        args = ['--project-root', str(tmp_path), '--workspace-root', str(tmp_path / 'work'),
                '--backup-root', str(tmp_path / 'backup'), '--poll-interval', '.001']
        if resume:
            args += ['--resume-workspace', str(workspace)]
        return runner.main(args)

    return execute, calls, workspace, technique


def test_waits_through_running_and_requires_success_receipt(simulation):
    execute, calls, workspace, technique = simulation
    assert execute([{'status': 'running'}, {'status': 'completed'}],
                   {'transaction_id': 'txn-test', 'transaction_status': 'success'}) == 0
    assert sum(c[:2] == ['mzt', 'status'] for c in calls) == 2
    assert technique.read_text() == 'original'


def test_completed_rollback_is_failure_without_second_restore(simulation):
    execute, calls, _, technique = simulation
    assert execute([{'status': 'completed'}],
                   {'transaction_id': 'txn-test', 'transaction_status': 'rolled_back'}, True) == 1
    assert not any('restore' in c for c in calls)
    assert technique.read_text() == 'original'


@pytest.mark.parametrize('status', ['failed', 'completed'])
def test_postbackup_missing_receipt_compensates_once(simulation, status):
    execute, calls, workspace, technique = simulation
    assert execute([{'status': status}], backed_up=True) == 1
    assert sum('restore' in c for c in calls) == 1
    assert json.loads((workspace / 'receipt.json').read_text())['transaction_status'] == 'rolled_back'
    assert technique.read_text() == 'original'


def test_paused_retains_technique_and_resume_does_not_resubmit(simulation):
    execute, calls, workspace, technique = simulation
    assert execute([{'status': 'paused'}], backed_up=True) == 2
    assert technique.read_text() == 'temporary'
    assert not any('restore' in c or 'restore-temporary-technique' in c for c in calls)
    assert execute([{'status': 'completed'}],
                   {'transaction_id': 'txn-test', 'transaction_status': 'success'}, resume=True) == 0
    assert sum(c[:2] == ['mzt', 'run'] for c in calls) == 1
    assert technique.read_text() == 'original'


def test_terminal_with_active_sibling_waits_before_restore(simulation):
    execute, calls, _, _ = simulation
    assert execute([{'status': 'failed', 'sheets': {'2': {'status': 'in_progress'}}},
                    {'status': 'failed'}], backed_up=True) == 1
    restore_index = next(i for i, c in enumerate(calls) if 'restore' in c)
    assert sum(c[:2] == ['mzt', 'status'] for c in calls[:restore_index]) == 2


def test_wrong_transaction_receipt_never_success(simulation):
    execute, _, _, _ = simulation
    assert execute([{'status': 'completed'}],
                   {'transaction_id': 'foreign', 'transaction_status': 'success'}) == 1


def test_timeout_preserves_active_job(runner, monkeypatch):
    ticks = iter([0, 0, 0, 2, 2])
    monkeypatch.setattr(runner.time, 'monotonic', lambda: next(ticks))
    monkeypatch.setattr(runner.time, 'sleep', lambda _: None)
    monkeypatch.setattr(runner, '_run_json', lambda *args: (0, {'job_id': 'job', 'status': 'running'}))
    assert runner._observe({'job_id': 'job'}, 1, .01) is None


def test_repeated_finish_does_not_compensate_twice(simulation, runner):
    execute, calls, workspace, _ = simulation
    assert execute([{'status': 'failed'}], backed_up=True) == 1
    state = json.loads((workspace / 'runner-state.json').read_text())
    assert runner._finish(state, workspace, {'status': 'failed'}) == 1
    assert sum('restore' in c for c in calls) == 1


def test_finalizer_rollback_without_receipt_is_not_restored_again(simulation, runner):
    execute, calls, workspace, _ = simulation
    assert execute([{'status': 'paused'}], backed_up=True) == 2
    (workspace / 'transaction.json').write_text(json.dumps({
        'transaction_id': 'txn-test', 'transaction_status': 'rolled_back', 'restored': True}))
    assert execute([{'status': 'failed'}], resume=True) == 1
    assert not any('restore' in c for c in calls)
    assert json.loads((workspace / 'receipt.json').read_text())['transaction_status'] == 'rolled_back'


def test_ambiguous_submission_preserves_technique(simulation, runner, monkeypatch):
    execute, calls, workspace, technique = simulation
    original = runner.subprocess.run

    def run(cmd, **kwargs):
        if cmd[:2] == ['mzt', 'run']:
            raise subprocess.TimeoutExpired(cmd, 60)
        return original(cmd, **kwargs)

    monkeypatch.setattr(runner.subprocess, 'run', run)
    assert execute([]) == 2
    assert technique.read_text() == 'temporary'
    assert not any('restore-temporary-technique' in c for c in calls)


@pytest.mark.parametrize('value', ['nan', 'inf', '0', '-1'])
def test_observation_bounds_must_be_finite_positive(runner, value):
    with pytest.raises(SystemExit, match='finite and positive'):
        runner.main(['--wait-timeout', value])


def test_cancelled_normalized_sheets_are_not_quiescence(simulation):
    execute, calls, workspace, technique = simulation
    assert execute([{'status': 'cancelled', 'sheets': {'2': {'status': 'cancelled'}}}], backed_up=True) == 2
    assert technique.read_text() == 'temporary'
    assert not any('restore' in c or 'restore-temporary-technique' in c for c in calls)
    assert not (workspace / 'runner-compensation.json').exists()


def test_rejected_existing_job_is_not_adopted_or_observed(simulation, runner, monkeypatch):
    execute, calls, workspace, technique = simulation
    original = runner.subprocess.run
    def run(cmd, **kwargs):
        if cmd[:2] == ['mzt', 'run']:
            return subprocess.CompletedProcess(cmd, 1, json.dumps({'job_id': 'foreign-job', 'status': 'rejected', 'message': 'already active'}))
        return original(cmd, **kwargs)
    monkeypatch.setattr(runner.subprocess, 'run', run)
    assert execute([]) == 1
    state = json.loads((workspace / 'runner-state.json').read_text())
    assert state['job_id'] is None
    assert state['submission']['reported_job_id'] == 'foreign-job'
    assert not any(c[:2] == ['mzt', 'status'] or 'restore' in c for c in calls)
    assert technique.read_text() == 'original'


@pytest.mark.parametrize('response,code', [({'job_id': 'job-test'}, 0), ({'job_id': 'job-test', 'status': 'accepted'}, 1), ({'status': 'accepted'}, 0)])
def test_ambiguous_response_preserves_technique_without_adoption(simulation, runner, monkeypatch, response, code):
    execute, calls, workspace, technique = simulation
    original = runner.subprocess.run
    def run(cmd, **kwargs):
        if cmd[:2] == ['mzt', 'run']:
            return subprocess.CompletedProcess(cmd, code, json.dumps(response))
        return original(cmd, **kwargs)
    monkeypatch.setattr(runner.subprocess, 'run', run)
    assert execute([]) == 2
    assert json.loads((workspace / 'runner-state.json').read_text())['job_id'] is None
    assert technique.read_text() == 'temporary'
    assert not any('restore' in c or 'restore-temporary-technique' in c for c in calls)


def test_pending_submission_is_owned_and_observed(simulation, runner, monkeypatch):
    execute, _, _, technique = simulation
    original = runner.subprocess.run
    def run(cmd, **kwargs):
        result = original(cmd, **kwargs)
        if cmd[:2] == ['mzt', 'run']:
            return subprocess.CompletedProcess(cmd, 0, json.dumps({'job_id': 'job-test', 'status': 'pending'}))
        return result
    monkeypatch.setattr(runner.subprocess, 'run', run)
    assert execute([{'status': 'completed'}], {'transaction_id': 'txn-test', 'transaction_status': 'success'}) == 0
    assert technique.read_text() == 'original'


def test_cli_does_not_offer_provider_denominator_override(runner):
    with pytest.raises(SystemExit):
        runner.build_parser().parse_args(['--provider', 'example'])


def test_authority_binds_runtime_paths_outside_configuration_observation(simulation):
    execute, _, workspace, _ = simulation
    assert execute([{'status': 'paused'}]) == 2
    authority = json.loads((workspace / 'authority-roots.json').read_text())
    assert authority['runtime_paths'] == [str(workspace), str(workspace.parents[1] / 'backup/txn-test')]
