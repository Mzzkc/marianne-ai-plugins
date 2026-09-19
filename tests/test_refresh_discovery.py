from .test_refresh_coverage import ctl, scope_fixture, manifest, authority
import json


def fixture(tmp_path):
    scope = scope_fixture(tmp_path)
    scope['admission_version'] = 3
    scope['unresolved'] = [{'id': 'local-route', 'model': 'creator/model', 'path': str(tmp_path/'local.yaml')}]
    m = manifest(tmp_path)
    m.update(schema_version=3, unresolved_results=[{'id':'local-route','status':'resolved','provider':'new-vendor','evidence_urls':['https://new.example/model']}])
    m['provider_results'].append({'provider':'new-vendor','status':'no_change','reason':'Official model registry matches local model','facts':[],'evidence_urls':['https://new.example/model']})
    return scope, m


def test_new_local_creator_is_admitted_before_backup(tmp_path):
    scope,m=fixture(tmp_path); p,h=authority(tmp_path,scope)
    assert ctl.validate_manifest_authority(m,p,h,'trial') == []
    m['provider_results'].pop()
    assert ctl.validate_manifest_authority(m,p,h,'trial')


def test_discovery_cannot_add_unobserved_provider_or_forget_shipped_one(tmp_path):
    scope,m=fixture(tmp_path);p,h=authority(tmp_path,scope)
    m['provider_results'].append({'provider':'unasked','status':'no_change','reason':'irrelevant','facts':[],'evidence_urls':['https://example.org']})
    assert ctl.validate_manifest_authority(m,p,h,'trial')
    m['provider_results'].pop();m['provider_results'].pop(0)
    assert ctl.validate_manifest_authority(m,p,h,'trial')


def test_blocked_shared_file_rejected_but_independent_target_admitted(tmp_path):
    scope,m=fixture(tmp_path)
    m['provider_results'][1]['status']='blocked'
    m['provider_results'][0].update(status='changes',facts=[{'id':'a','model':'new-a','evidence_urls':['https://a.example/model']}])
    t={'path':str(tmp_path/'independent.yaml'),'classification':'active','disposition':'change','fact_ids':['a'],'dependency_providers':['vendor-a'],'checks':[{'contains':'new-a'}]}
    m['targets']=[t];p,h=authority(tmp_path,scope)
    assert ctl.validate_manifest_authority(m,p,h,'trial') == []
    t['path']=scope['providers'][0]['routes'][0]['path']
    assert any('deferred' in e for e in ctl.validate_manifest_authority(m,p,h,'trial'))
    t['path']=str(tmp_path/'independent.yaml');t['dependency_providers'].append('vendor-b')
    assert any('dependency' in e for e in ctl.validate_manifest_authority(m,p,h,'trial'))


def test_blocked_unknown_route_is_explicit_and_its_file_cannot_change(tmp_path):
    scope,m=fixture(tmp_path);m['provider_results'].pop();m['unresolved_results']=[{'id':'local-route','status':'blocked','reason':'Official ownership unavailable'}]
    p,h=authority(tmp_path,scope)
    assert ctl.validate_manifest_authority(m,p,h,'trial')==[]
    m['unresolved_results']=[]
    assert ctl.validate_manifest_authority(m,p,h,'trial')


def test_discovery_cannot_opt_itself_into_legacy_authority(tmp_path):
    scope,m=fixture(tmp_path);scope.pop('admission_version');p,h=authority(tmp_path,scope)
    assert ctl.validate_manifest_authority(m,p,h,'trial')


def test_deferrals_reported_and_no_facts_from_blocked_provider(tmp_path):
    _,m=fixture(tmp_path);m['provider_results'][1]['status']='blocked'
    assert ctl.refresh_deferrals(m)['providers']==['vendor-b']
    m['provider_results'][1]['facts']=[{'id':'bad','model':'m','evidence_urls':['https://example.org']}]
    assert ctl.validate_manifest(m)


def test_v3_partial_transaction_keeps_valid_target_and_exposes_deferrals(tmp_path):
    import hashlib
    scope,m=fixture(tmp_path)
    work=tmp_path/'runtime'; work.mkdir()
    target=tmp_path/'independent.yaml';target.write_text('models: []\n')
    m['provider_results'][1]['status']='blocked'
    m['provider_results'][0].update(status='changes',facts=[{'id':'a','model':'new-a','evidence_urls':['https://a.example/model']}])
    m['targets']=[{'path':str(target),'classification':'active','disposition':'change','fact_ids':['a'],'dependency_providers':['vendor-a'],'checks':[{'pointer':'/models/@name=new-a/name','equals':'new-a'}]}]
    p,h=authority(tmp_path,scope);a=json.loads(p.read_text());a['runtime_paths']=[str(work)];p.write_text(json.dumps(a));h=hashlib.sha256(p.read_bytes()).hexdigest()
    mp=work/'manifest.json';mp.write_text(json.dumps(m))
    ctl.create_backup(mp,work/'backup',authority_path=p,authority_sha256=h,transaction_id='trial')
    target.write_text('models:\n  - name: new-a\n')
    ledger=work/'ledger.json';ledger.write_text(json.dumps({'schema_version':1,'transaction_id':'trial','changed_paths':[str(target)]}))
    result=ctl.static_commission(mp,work/'backup/transaction-state.json',ledger)
    assert result['static']['passed'],result
    cp=work/'commission.json';cp.write_text(json.dumps(result))
    ctl.live_commission(mp,cp,transaction_id='trial')
    tx=ctl.finalize_transaction(mp,work/'backup/transaction-state.json',cp,work/'transaction.json',transaction_id='trial',authority_path=p,authority_sha256=h)
    assert tx['transaction_status']=='partial'
    assert tx['deferrals']['providers']==['vendor-b']
    assert 'new-a' in target.read_text()
    # Accepted discovery is immutable after backup.
    m['unresolved_results'][0]['provider']='replacement';mp.write_text(json.dumps(m))
    assert ctl.verify_changed_paths(mp,work/'backup/transaction-state.json')


def test_v3_backup_cannot_skip_caller_authority(tmp_path):
    import pytest
    _,m=fixture(tmp_path);p=tmp_path/'manifest.json';p.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='caller authority'):
        ctl.create_backup(p,tmp_path/'backup')


def test_receipt_stage_retains_partial_changed_paths(tmp_path):
    from pathlib import Path
    import yaml, subprocess, shlex
    from jinja2 import Template
    bundle=Path(__file__).parents[1]/'marianne/skills/marianne-model-profile-refresh/score'
    data={'transaction_id':'trial'}
    for name in ['update-manifest','commissioning']:
        (tmp_path/f'{name}.json').write_text(json.dumps(data))
    (tmp_path/'changed-paths.json').write_text(json.dumps({**data,'changed_paths':['/example/profile.yaml']}))
    (tmp_path/'transaction.json').write_text(json.dumps({**data,'transaction_status':'partial','deferrals':{'providers':['vendor'],'routes':[]}}))
    score=yaml.safe_load((bundle/'model-profile-refresh.yaml').read_text())
    command=Template(score['prompt']['template']).render(stage=9,bundle_root_q=shlex.quote(str(bundle)),refresh_artifact_root_q=shlex.quote(str(tmp_path)),transaction_id_q='trial')
    subprocess.run(['bash','-c',command],check=True)
    receipt=json.loads((tmp_path/'receipt.json').read_text())
    assert receipt['changed_paths']==['/example/profile.yaml']
    assert receipt['transaction_status']=='partial'
