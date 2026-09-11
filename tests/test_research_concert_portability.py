"""Generated local concert paths respect native home-path validation."""
from pathlib import Path
import yaml
from tests import test_research as fixtures


def test_home_paths_are_portable_and_hook_anchors_to_score(tmp_path, monkeypatch):
    # Native validation and Path.expanduser share HOME in this isolated fixture.
    monkeypatch.setenv('HOME', str(tmp_path))
    inp, ws, receipt = fixtures.prepare(tmp_path)
    fixtures.complete(ws, receipt)
    fixtures.research.deliver(ws)
    child = tmp_path / 'child'
    cfg = fixtures.concert.consumer(ws, child, fixtures.ASSETS)
    assert cfg['workspace'] == '~/child'
    assert all(next(v for k, v in item.items() if k in ('file', 'directory')).startswith('~/')
               for item in cfg['sheet']['cadenzas'][2])
    path = fixtures.put(tmp_path / 'consumer.yaml', yaml.safe_dump(cfg))
    native, sheets, renderer = fixtures.native(path, child, inp)
    rendered = fixtures.render(renderer, sheets[1])
    assert 'BENIGN_SECOND_CONTEXT' in rendered.prompt
    assert receipt['run_id'] in rendered.prompt
    expected = {str(ws / 'input-snapshot' / row['name']): row['sha256'] for row in receipt['files']}
    actual = {row['resolved_path']: row['source_sha256'].removeprefix('sha256:')
              for row in rendered.context_manifest if row['delivery_kind'] == 'directory-inline'
              and Path(row['resolved_path']).parent == ws / 'input-snapshot'}
    assert actual == expected
    wrapper = fixtures.concert.wrapper(fixtures.ASSETS / 'scores/research-b.yaml', ws,
                                       child, inp, tmp_path / 'concert', fixtures.ASSETS)
    data = yaml.safe_load(wrapper.read_text())
    assert data['workspace'] == '~/workspace'
    assert (wrapper.parent / data['on_success'][0]['job_path']).resolve() == tmp_path / 'concert/consumer.yaml'
    assert not any(str(v).startswith(str(tmp_path)) for v in data['prompt']['variables'].values())
