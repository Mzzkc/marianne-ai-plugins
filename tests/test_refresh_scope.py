"""Scope comes from declared active relationships, never profile-name guessing."""
import importlib.util
from pathlib import Path

import pytest
import yaml

SCRIPT = Path(__file__).resolve().parents[1] / 'marianne/skills/marianne-model-profile-refresh/score/scripts/refresh_scope.py'
spec = importlib.util.spec_from_file_location('refresh_scope_test', SCRIPT)
scope = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scope)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data))


def fixture(tmp_path):
    project = tmp_path / 'project'
    home = tmp_path / '.marianne'
    catalog = project / 'plugins/marianne/docs/ref/instrument-catalog.yaml'
    write(catalog, {'instruments': {'broker': {'runs_models': ['alpha', 'beta']}},
                    'musicians': {'alpha': {'provider': 'first', 'aliases': ['declared-alias']},
                                  'beta': {'provider': 'second'}}})
    write(project / 'src/marianne/instruments/builtins/broker.yaml', {'name': 'broker'})
    return project, home, catalog


def test_broker_is_not_provider_and_installed_known_profile_is_active(tmp_path):
    project, home, _ = fixture(tmp_path)
    write(home / 'instruments/broker.yaml', {'name': 'broker', 'models': [{'name': 'alpha'}]})
    result = scope.build_scope(project, [home])
    assert [p['id'] for p in result['providers']] == ['first', 'second']
    assert all(r['classification'] == 'active' for p in result['providers'] for r in p['routes'])
    assert any(str(home) in r['path'] for p in result['providers'] for r in p['routes'])


def test_unknown_inherited_and_pinned_profiles_preserve_edit_classification_but_add_provider(tmp_path):
    project, home, _ = fixture(tmp_path)
    write(home / 'instruments/task.yaml', {'name': 'task', 'extends': 'broker',
          'models': [{'name': 'alpha'}], 'provider': 'invented'})
    write(home / 'instruments/pinned.yaml', {'name': 'broker', 'classification': 'pinned'})
    result = scope.build_scope(project, [home])
    assert {r['classification'] for r in result['skipped']} == {'unknown', 'pinned'}
    assert 'invented' in {p['id'] for p in result['providers']}
    assert all(r['classification'] in {'unknown', 'pinned'} for p in result['providers'] for r in p['routes'] if str(home) in r['path'])


def test_declared_alias_resolves_but_suffix_guess_is_visible_with_stable_id(tmp_path):
    project, home, _ = fixture(tmp_path)
    write(project / 'src/marianne/instruments/builtins/broker.yaml',
          {'name': 'broker', 'models': [{'name': 'declared-alias'}, {'name': 'alpha-high'}]})
    result = scope.build_scope(project, [home])
    assert any(r['model'] == 'declared-alias' for r in result['providers'][0]['routes'])
    assert [r['model'] for r in result['unresolved']] == ['alpha-high']
    missing = result['unresolved'][0]
    assert missing['candidate_providers'] == ['first', 'second']
    assert missing['id'] == scope.build_scope(project, [home])['unresolved'][0]['id']


def test_catalog_broker_prose_is_excluded_but_unknown_concrete_model_is_not(tmp_path):
    project, home, catalog = fixture(tmp_path)
    data = yaml.safe_load(catalog.read_text())
    data['instruments']['broker']['runs_models'] += ['any provider configured for broker', 'missing']
    write(catalog, data)
    result = scope.build_scope(project, [home])
    assert [r['model'] for r in result['unresolved']] == ['missing']
    assert result['skipped'][0]['classification'] == 'generic-route-placeholder'


def test_provider_subset_cannot_narrow_required_shipped_coverage(tmp_path):
    project, home, _ = fixture(tmp_path)
    with pytest.raises(ValueError, match='all shipped providers'):
        scope.build_scope(project, [home], ['second'])
    result = scope.build_scope(project, [home], ['first', 'second'])
    assert result['mode'] == 'broad'
    assert [p['id'] for p in result['providers']] == ['first', 'second']


def test_catalog_only_and_explicit_builtin_providers_are_mandatory(tmp_path):
    project, home, catalog = fixture(tmp_path)
    data = yaml.safe_load(catalog.read_text())
    data['musicians']['catalog-only'] = {'provider': 'third'}
    write(catalog, data)
    write(project / 'src/marianne/instruments/builtins/additional.yaml',
          {'name': 'additional', 'provider': 'fourth'})
    result = scope.build_scope(project, [home])
    by_id = {row['id']: row for row in result['providers']}
    assert set(by_id) == {'first', 'second', 'third', 'fourth'}
    assert by_id['third']['routes'] == []
    assert by_id['fourth']['routes'] == []


def test_private_explicit_provider_adds_coverage_without_removing_shipped(tmp_path):
    project, home, _ = fixture(tmp_path)
    write(home / 'instruments/custom.yaml', {'name': 'custom', 'classification': 'active',
          'provider': 'not-shipped', 'models': [{'name': 'custom-model'}]})
    result = scope.build_scope(project, [home])
    assert {p['id'] for p in result['providers']} == {'first', 'second', 'not-shipped'}
    assert result['unresolved'] == []


def test_unknown_local_model_row_provider_and_unresolved_alias_dedup(tmp_path):
    project, home, _ = fixture(tmp_path)
    for name in ('task-one', 'task-two'):
        write(home / f'instruments/{name}.yaml', {'name': name,
              'models': [{'name': 'declared-local', 'provider': 'local-vendor'}, {'name': 'unmapped-local'}]})
    result = scope.build_scope(project, [home])
    assert {p['id'] for p in result['providers']} == {'first', 'second', 'local-vendor'}
    assert len(result['unresolved']) == 1
    assert result['unresolved'][0]['model'] == 'unmapped-local'
    assert len(result['unresolved'][0]['source_paths']) == 2
    assert all(r['classification'] == 'unknown' for p in result['providers'] if p['id'] == 'local-vendor' for r in p['routes'])


def test_ordinary_app_uses_installed_catalog_and_builtin_resources(tmp_path, monkeypatch):
    project, home, catalog = fixture(tmp_path)
    application = tmp_path / 'ordinary-app'
    application.mkdir()
    monkeypatch.setattr(scope, '_installed_catalog_path', lambda: catalog)
    monkeypatch.setattr(scope, '_installed_builtin_dir', lambda: project / 'src/marianne/instruments/builtins')
    write(application / '.marianne/instruments/local.yaml',
          {'name': 'local', 'models': [{'name': 'alpha'}]})
    result = scope.build_scope(application, [home])
    assert {p['id'] for p in result['providers']} == {'first', 'second'}
    assert any(str(application) in r['path'] for p in result['providers'] for r in p['routes'])
    assert any('builtins' in r['path'] for p in result['providers'] for r in p['routes'])


def test_shipped_catalog_suffices_without_installed_runtime_package(tmp_path, monkeypatch):
    _, _, catalog = fixture(tmp_path)
    application = tmp_path / 'app'
    application.mkdir()
    monkeypatch.setattr(scope, '_installed_catalog_path', lambda: catalog)
    monkeypatch.setattr(scope, '_installed_builtin_dir', lambda: None)
    result = scope.build_scope(application, [])
    assert {p['id'] for p in result['providers']} == {'first', 'second'}
    assert all(p['routes'] == [] for p in result['providers'])


def test_sidecar_maps_unknown_local_provider_before_scope_is_sealed(tmp_path):
    project, home, _ = fixture(tmp_path)
    write(home / 'instruments/task.yaml', {'name': 'task', 'models': [{'name': 'novel-model'}]})
    assert scope.build_scope(project, [home])['unresolved']
    write(home / 'model-providers.yaml', {'schema_version': 1,
          'providers': {'local-vendor': {'models': ['novel-model']}}})
    result = scope.build_scope(project, [home])
    assert result['unresolved'] == []
    assert {p['id'] for p in result['providers']} == {'first', 'second', 'local-vendor'}
    assert next(p for p in result['providers'] if p['id'] == 'local-vendor')['routes'][0]['classification'] == 'unknown'


def test_invalid_sidecar_fails_instead_of_silently_skipping_provider(tmp_path):
    project, home, _ = fixture(tmp_path)
    write(home / 'model-providers.yaml', {'schema_version': 1, 'providers': {'local': {'models': 'not-a-list'}}})
    with pytest.raises(ValueError, match='invalid provider metadata'):
        scope.build_scope(project, [home])


def test_opencode_explicit_service_provider_and_namespaced_model(tmp_path):
    import json
    project, home, _ = fixture(tmp_path)
    configuration = tmp_path / 'opencode'
    configuration.mkdir()
    (configuration / 'opencode.json').write_text(json.dumps({'provider': {'service-key': {'models': {'novel-model': {}}}}}))
    write(home / 'instruments/task.yaml', {'name': 'task', 'models': [{'name': 'service-key/novel-model'}]})
    result = scope.build_scope(project, [home, configuration])
    assert {p['id'] for p in result['providers']} == {'first', 'second', 'service-key'}
    assert result['unresolved'] == []
