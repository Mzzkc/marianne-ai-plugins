"""Governed configuration drift remains visible during unrelated client activity."""
from pathlib import Path
import hashlib
import importlib.util
import os
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'marianne/skills/marianne-model-profile-refresh/score/scripts/refresh_observation.py'
spec = importlib.util.spec_from_file_location('refresh_observation', SCRIPT)
observation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observation)


def put(path, body='initial'):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    return path


def changed(before, after):
    return {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}


@pytest.fixture
def home(tmp_path, monkeypatch):
    path = tmp_path / 'home'; path.mkdir()
    monkeypatch.setenv('HOME', str(path))
    monkeypatch.setenv('XDG_CONFIG_HOME', str(path / '.config'))
    monkeypatch.setenv('XDG_DATA_HOME', str(path / '.local/share'))
    return path


def test_telemetry_and_cache_churn_does_not_hide_real_configuration_changes(home):
    roots = [home / n for n in ['.claude', '.codex', '.gemini', '.marianne', '.config/opencode', '.local/share/opencode']]
    configs = [put(home / n) for n in ['.claude/settings.json', '.codex/config.toml', '.gemini/settings.json', '.marianne/instruments/a.yaml', '.config/opencode/opencode.json']]
    telemetry = [put(home / n) for n in ['.claude/sessions/a.json', '.claude/stats-cache.json', '.codex/state_5.sqlite-wal', '.codex/models_cache.json', '.gemini/antigravity-cli/conversations/a.json', '.marianne/daemon-state.db-wal', '.marianne/conductor.log', '.local/share/opencode/storage/a.json']]
    before = observation.snapshot(roots, [])
    for path in telemetry:
        path.write_text('concurrent telemetry update')
    put(home / '.codex/sessions/new.json')
    configs[0].write_text('undeclared config mutation')
    added = put(home / '.marianne/instruments/new.yaml')
    configs[3].unlink()
    after = observation.snapshot(roots, [])
    assert changed(before, after) == {str(configs[0]), str(configs[3]), str(added)}
    assert all(str(p) not in after for p in telemetry)
    assert before[str(configs[1])]['value'] == hashlib.sha256(b'initial').hexdigest()


def test_repository_logs_json_sqlite_and_nested_client_names_are_not_runtime(home):
    repo = home / 'project'
    retained = [put(repo / n) for n in ['logs/settings.json', 'data/config.sqlite', 'cache/config.json', '.claude/projects/source.json', 'plugins/logs/rules.yaml']]
    generated = [put(repo / n) for n in ['.git/index', '.venv/a.py', 'src/__pycache__/x.pyc', '.pytest_cache/result']]
    before = observation.snapshot([repo], [])
    for path in retained + generated:
        path.write_text('modified')
    after = observation.snapshot([repo], [])
    assert changed(before, after) == {str(p) for p in retained}
    assert all(str(p) not in after for p in generated)


def test_installed_plugin_cache_is_source_and_nested_logs_remain_governed(home):
    paths = [put(home / n) for n in ['.claude/plugins/cache/vendor/skill/SKILL.md', '.codex/plugins/cache/vendor/config.json', '.marianne/instruments/logs/route.yaml', '.gemini/antigravity-cli/mcp/config.json', '.claude/hooks/new.json', '.codex/rules/policy.rules']]
    before = observation.snapshot([home], [])
    for path in paths:
        path.write_text('source drift')
    assert changed(before, observation.snapshot([home], [])) == {str(p) for p in paths}


def test_subdirectory_root_retains_client_policy_and_unknown_files(home):
    root = home / '.codex'
    ignored = put(root / 'sessions/run.json')
    governed = put(root / 'future-settings.json')
    assert observation.snapshot([ignored.parent], []) == {}
    assert str(governed) in observation.snapshot([root], [])


def test_symlinks_record_literal_target_without_outside_file_reads(home, tmp_path, monkeypatch):
    authority = home / 'project'; authority.mkdir()
    outside = put(tmp_path / 'outside/secret', 'not to be read')
    link = authority / 'linked'; link.symlink_to(outside.parent, target_is_directory=True)
    root_link = home / 'root-link'; root_link.symlink_to(outside)
    actual_open = observation.os.open
    def guarded_open(path, flags, *args, **kwargs):
        assert str(path) not in {str(outside), str(outside.parent), 'secret', 'linked', 'root-link'}
        return actual_open(path, flags, *args, **kwargs)
    monkeypatch.setattr(observation.os, 'open', guarded_open)
    before = observation.snapshot([authority, root_link], [])
    assert before[str(link)] == {'kind': 'symlink', 'value': str(outside.parent)}
    assert before[str(root_link)]['kind'] == 'symlink'
    assert str(outside) not in before
    link.unlink(); link.symlink_to(tmp_path / 'missing')
    assert changed(before, observation.snapshot([authority, root_link], [])) == {str(link)}


def test_symlink_ancestor_refused_and_exclusion_does_not_follow_link(home, tmp_path):
    outside = put(tmp_path / 'outside/secret')
    root = home / 'project'; root.mkdir()
    link = root / 'link'; link.symlink_to(outside.parent, target_is_directory=True)
    with pytest.raises(OSError):
        observation.snapshot([link / 'secret'], [])
    # Excluding outside data must not suppress the governed link itself.
    assert str(link) in observation.snapshot([root], [outside.parent])
    assert observation.snapshot([root], [root]) == {}


def test_missing_root_addition_and_file_deletion(home):
    root = home / 'new-authority'
    assert observation.snapshot([root], []) == {}
    file = put(root / 'profile.yaml')
    before = observation.snapshot([root], [])
    file.unlink()
    assert changed(before, observation.snapshot([root], [])) == {str(file)}
    assert observation.policy_version == observation.POLICY_VERSION


def test_required_targets_override_ignored_and_excluded_ancestors_only(home):
    root = home / '.codex'
    target = put(root / 'sessions/accepted/config.json')
    sibling = put(root / 'sessions/accepted/telemetry.json')
    adjacent = put(root / 'sessions/other/config.json')
    before = observation.snapshot([root], [root / 'sessions'], required_paths=[target])
    assert set(before) == {str(target)}
    target.write_text('changed accepted target')
    sibling.write_text('normal session churn')
    adjacent.write_text('normal session churn')
    assert changed(before, observation.snapshot([root], [root / 'sessions'], required_paths=[target])) == {str(target)}
    target.unlink()
    assert changed(before, observation.snapshot([root], [root / 'sessions'], required_paths=[target])) == {str(target)}


def test_required_generated_path_and_new_target_remain_exact(home):
    root = home / 'repo'
    target = root / '__pycache__/accepted.json'
    sibling = put(root / '__pycache__/normal.pyc')
    assert observation.snapshot([root], [], required_paths=[target]) == {}
    put(target)
    result = observation.snapshot([root], [], required_paths=[target])
    assert set(result) == {str(target)} and str(sibling) not in result


def test_required_paths_never_extend_authority_or_follow_links(home, tmp_path):
    root = home / 'repo'; root.mkdir()
    outside = put(tmp_path / 'outside/secret')
    with pytest.raises(ValueError, match='outside'):
        observation.snapshot([root], [], required_paths=[outside])
    link = root / '__pycache__'; link.symlink_to(outside.parent, target_is_directory=True)
    result = observation.snapshot([root], [], required_paths=[link / 'secret'])
    assert result == {str(link): {'kind': 'symlink', 'value': str(outside.parent)}}
    assert str(outside) not in result
