"""Generic refresh admission, observation and commissioning boundaries."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest

SCRIPT = Path(__file__).parents[1] / 'marianne/skills/marianne-model-profile-refresh/score/scripts/refreshctl.py'
spec = importlib.util.spec_from_file_location('generic_refreshctl', SCRIPT)
ctl = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ctl
spec.loader.exec_module(ctl)


def fixture(tmp_path, required=False):
    target = tmp_path / 'profile.yaml'
    target.write_text('models: []\n')
    workspace = tmp_path / 'runtime'
    workspace.mkdir()
    manifest = {'schema_version': 2, 'transaction_id': 'trial', 'request': 'refresh', 'mode': 'broad',
                'allowed_roots': [str(tmp_path)],
                'provider_results': [{'provider': 'vendor', 'status': 'changes', 'reason': 'release',
                                      'evidence_urls': ['https://vendor.example/models'],
                                      'facts': [{'id': 'new', 'model': 'new', 'evidence_urls': ['https://vendor.example/models'],
                                                 'live_contract_required': required}]}],
                'targets': [{'path': str(target), 'classification': 'active', 'disposition': 'change',
                             'fact_ids': ['new'], 'checks': [{'pointer': '/models/@name=new/context_window', 'equals': 1000}]}]}
    mp = workspace / 'manifest.json'
    mp.write_text(json.dumps(manifest))
    authority = workspace / 'authority.json'
    authority.write_text(json.dumps({'schema_version': 1, 'transaction_id': 'trial', 'allowed_roots': [str(tmp_path)],
                                    'runtime_paths': [str(workspace)],
                                    'refresh_scope': {'mode': 'broad', 'providers': [{'id': 'vendor'}], 'unresolved': []}}))
    ctl.create_backup(mp, workspace / 'backup', authority_path=authority,
                      authority_sha256=hashlib.sha256(authority.read_bytes()).hexdigest(), transaction_id='trial')
    return target, workspace, mp


def test_v2_ignores_transaction_artifacts_and_verifies_configured_model(tmp_path):
    target, workspace, mp = fixture(tmp_path)
    target.write_text('models:\n  - name: new\n    context_window: 1000\n')
    (workspace / 'client.log').write_text('runner output')
    ledger = workspace / 'ledger.json'
    ledger.write_text(json.dumps({'schema_version': 1, 'transaction_id': 'trial', 'changed_paths': [str(target)]}))
    result = ctl.static_commission(mp, workspace / 'backup/transaction-state.json', ledger)
    assert result['static']['passed'], result
    assert result['observed_changed_paths'] == [str(target)]


def test_explicit_target_inside_excluded_runtime_stays_observed(tmp_path):
    target, workspace, mp = fixture(tmp_path)
    # The entire parent is an authority-bound runtime exclusion; the exact target
    # must override it while a neighboring runtime file stays excluded.
    authority = workspace / 'authority.json'
    auth = json.loads(authority.read_text())
    auth['runtime_paths'] = [str(tmp_path)]
    authority.write_text(json.dumps(auth))
    ctl.create_backup(mp, workspace / 'backup2', authority_path=authority,
                      authority_sha256=hashlib.sha256(authority.read_bytes()).hexdigest(), transaction_id='trial')
    target.write_text('models: [new]\n')
    (tmp_path / 'noise').write_text('ignored runtime')
    changed, errors = ctl.observed_changed_paths(mp, workspace / 'backup2/transaction-state.json')
    assert changed == [str(target)]
    assert not errors


@pytest.mark.parametrize('required', [False, True])
def test_live_evidence_is_per_fact_and_required_unsupported_rolls_back(tmp_path, required):
    target, workspace, mp = fixture(tmp_path, required)
    target.write_text('models:\n  - name: new\n    context_window: 1000\n')
    cp = workspace / 'commissioning.json'
    cp.write_text(json.dumps({'transaction_id': 'trial', 'static': {'passed': True, 'errors': [], 'candidate_snapshot': ctl._target_snapshot(json.loads(mp.read_text()))}}))
    live = ctl.live_commission(mp, cp, transaction_id='trial')['live']
    assert live['results'][0]['fact_id'] == 'new'
    assert live['results'][0]['state'] == 'unsupported'
    result = ctl.finalize_transaction(mp, workspace / 'backup/transaction-state.json', cp,
                                      workspace / 'transaction.json', transaction_id='trial')
    assert result['transaction_status'] == ('rolled_back' if required else 'success')
    if required:
        assert target.read_text() == 'models: []\n'


def test_failed_optional_live_fact_is_not_success(tmp_path):
    target, workspace, mp = fixture(tmp_path)
    cp = workspace / 'commissioning.json'
    cp.write_text(json.dumps({'transaction_id': 'trial', 'static': {'passed': True, 'errors': [], 'candidate_snapshot': ctl._target_snapshot(json.loads(mp.read_text()))},
                              'live': {'state': 'failed', 'results': [{'fact_id': 'new', 'state': 'failed'}]}}))
    result = ctl.finalize_transaction(mp, workspace / 'backup/transaction-state.json', cp,
                                      workspace / 'transaction.json', transaction_id='trial')
    assert result['transaction_status'] == 'rolled_back'


def test_unique_model_selector_and_structured_contains():
    assert ctl._pointer_value({'models': [{'name': 'x', 'limits': [1, 2]}]}, '/models/@name=x/limits') == [1, 2]
    with pytest.raises(ValueError, match='exactly one'):
        ctl._pointer_value({'models': [{'name': 'x'}, {'name': 'x'}]}, '/models/@name=x')


def test_comment_cannot_satisfy_model_membership(tmp_path):
    target, workspace, mp = fixture(tmp_path)
    data = json.loads(mp.read_text())
    data['targets'][0]['checks'] = [{'contains': 'new'}]
    target.write_text('models: []\n# new\n')
    assert any('configured model missing' in e for e in ctl._configured_checks(data))


@pytest.mark.parametrize('value', [None, {}, 'bad'])
def test_malformed_fact_references_return_errors(tmp_path, value):
    _, _, mp = fixture(tmp_path)
    data = json.loads(mp.read_text())
    data['targets'][0]['fact_ids'] = value
    assert ctl.validate_manifest(data)


def test_unchanged_declared_target_fails(tmp_path):
    _, workspace, mp = fixture(tmp_path)
    ledger = workspace / 'ledger.json'
    ledger.write_text(json.dumps({'schema_version': 1, 'transaction_id': 'trial', 'changed_paths': []}))
    result = ctl.static_commission(mp, workspace / 'backup/transaction-state.json', ledger)
    assert any('no observed change' in e for e in result['static']['errors'])


def test_v2_reuses_google_adapter_only_for_proven_native_profile(tmp_path, monkeypatch):
    target, workspace, mp = fixture(tmp_path)
    data = json.loads(mp.read_text())
    data['provider_results'][0]['provider'] = 'google'
    mp.write_text(json.dumps(data))
    cp = workspace / 'commissioning.json'
    cp.write_text(json.dumps({'transaction_id': 'trial', 'static': {'passed': True, 'errors': [], 'candidate_snapshot': ctl._target_snapshot(json.loads(mp.read_text()))}}))
    probes = []
    monkeypatch.setattr(ctl, '_probe_google_cli', lambda *args: probes.append(args) or ctl._live_record('live_smoked', False, 'mock probe'))
    # A model name by itself is insufficient to bind a native client adapter.
    target.write_text('models:\n  - name: new\n')
    assert ctl.live_commission(mp, cp, transaction_id='trial')['live']['state'] == 'unsupported'
    assert not probes
    target.write_text('name: gemini-cli\nkind: cli\ncli:\n  command:\n    executable: gemini\nmodels:\n  - name: new\n')
    result = ctl.live_commission(mp, cp, transaction_id='trial')['live']
    assert result['results'][0]['state'] == 'live_smoked'
    assert len(probes) == 1


def test_static_false_without_errors_cannot_finalize_success(tmp_path):
    _, workspace, mp = fixture(tmp_path)
    cp = workspace / 'commissioning.json'
    cp.write_text(json.dumps({'transaction_id': 'trial', 'static': {'passed': False, 'errors': []}}))
    ctl.live_commission(mp, cp, transaction_id='trial')
    result = ctl.finalize_transaction(mp, workspace / 'backup/transaction-state.json', cp,
                                      workspace / 'transaction.json', transaction_id='trial')
    assert result['transaction_status'] == 'rolled_back'
    assert 'static commissioning did not pass' in result['gate_errors']


def test_poststatic_profile_corruption_rolls_back(tmp_path):
    target, workspace, mp = fixture(tmp_path)
    target.write_text('models:\n  - name: new\n    context_window: 1000\n')
    ledger = workspace / 'ledger.json'
    ledger.write_text(json.dumps({'schema_version': 1, 'transaction_id': 'trial', 'changed_paths': [str(target)]}))
    cp = workspace / 'commissioning.json'
    static = ctl.static_commission(mp, workspace / 'backup/transaction-state.json', ledger)
    assert static['static']['passed']
    cp.write_text(json.dumps(static))
    ctl.live_commission(mp, cp, transaction_id='trial')
    target.write_text('models: []\n# changed after commissioning\n')
    result = ctl.finalize_transaction(mp, workspace / 'backup/transaction-state.json', cp,
                                      workspace / 'transaction.json', transaction_id='trial')
    assert result['transaction_status'] == 'rolled_back'
    assert 'candidate changed after static commissioning' in result['gate_errors']
    assert target.read_text() == 'models: []\n'


def test_target_snapshot_covers_link_and_resolved_bytes(tmp_path):
    leaf = tmp_path / 'profile.yaml'
    leaf.write_text('models: []\n')
    link = tmp_path / 'alias.yaml'
    link.symlink_to(leaf.name)
    manifest = {'allowed_roots': [str(tmp_path)], 'targets': [{'path': str(link)}]}
    before = ctl._target_snapshot(manifest)
    assert before[str(link)] == {'kind': 'symlink', 'value': leaf.name}
    assert before[str(leaf)]['kind'] == 'file'
    leaf.write_text('models: [new]\n')
    assert before != ctl._target_snapshot(manifest)
