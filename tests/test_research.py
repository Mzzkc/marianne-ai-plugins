"""Provider-free causal contracts; native runtime imports must be source-bound."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'marianne/skills/research'
sys.path.insert(0, str(ASSETS / 'scripts'))
import research

def test_unknown_seat_and_unowned_questions_refused():
    receipt = {'run_id': 'current', 'mode': 'A', 'roster': {'seats': [
        {'id': 'search-1', 'family': 'one', 'profile': 'one', 'model': 'one'},
        {'id': 'search-2', 'family': 'two', 'profile': 'two', 'model': 'two'}]}}
    strategy = {'schema_version':1, 'kind':'research-strategy', 'run_id': 'current', 'requirements': [{'id':'R1', 'text':'Needed', 'mandatory':True}],
                'questions': [{'id':'Q1','text':'Decisive?', 'requirement_ids':['R1'], 'mandatory':True,
                'evidence_goal':'primary implementation', 'queries':['capability'], 'priority':'high'}],
                'assignments': {'search-1':['Q1'], 'search-2':['Q1']}}
    research.validate_strategy(strategy, receipt)
    import pytest
    strategy['assignments']['search-2'] = ['missing']
    with pytest.raises(research.ContractError):
        research.validate_strategy(strategy, receipt)

import copy
import hashlib
import json
import subprocess
import concurrent.futures
import pytest
import yaml
import configure
import concert
import check_graph
from marianne.core.config import JobConfig
from marianne.core.sheet import build_sheets
from marianne.daemon.baton.prompt import PromptRenderer
from marianne.daemon.baton.state import AttemptContext, AttemptMode

import os
EVIDENCE = Path(os.environ.get('RESEARCH_TEST_EVIDENCE', '/tmp/research-native-context-fixtures'))
ROSTER = json.loads((ASSETS/'roster.json').read_text())

def put(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value) if isinstance(value,dict) else value)
    return path

def env(kind, receipt):
    return {'schema_version':1,'kind':'research-'+kind,'run_id':receipt['run_id']}

def statement(kind, value, source_ids=(), requirement_ids=()):
    return {'kind':kind, 'text':value, 'source_ids':list(source_ids), 'requirement_ids':list(requirement_ids)}


def test_atomic_fact_statement_requires_a_validated_source():
    with pytest.raises(research.ContractError, match='fact requires source_ids'):
        research.validate_statement(
            {'kind':'fact', 'text':'Fixture claim', 'source_ids':[]},
            {'S1'},
            set(),
            'fixture statement',
        )


def test_statement_renderer_links_every_validated_source():
    rendered = research.render_statement(
        {'kind':'inference', 'text':'Fixture conclusion', 'source_ids':['search-1:S1','search-2:S2']},
        {
            'search-1:S1': {'title':'First source', 'url':'https://example.test/one'},
            'search-2:S2': {'title':'Second source', 'url':'https://example.test/two'},
        },
    )
    assert rendered == 'Inference: Fixture conclusion ([First source](https://example.test/one); [Second source](https://example.test/two))'


def test_input_source_binds_current_receipt_member_and_digest(tmp_path):
    _, _, receipt = prepare(tmp_path)
    original = receipt['files'][0]
    source = {'id':'I1', 'title':'Provided context', 'source_type':'input',
              'input_name':original['name'], 'input_sha256':original['sha256'],
              'supported_claim':'Fixture context states the blue constraint'}
    assert research.sources([source], receipt)['I1'] == source
    for key, value in [('input_name','missing.md'), ('input_sha256','0' * 64), ('url','file:///tmp/escape')]:
        bad = copy.deepcopy(source); bad[key] = value
        with pytest.raises(research.ContractError):
            research.sources([bad], receipt)

def prepare(tmp,mode='A',roster=None):
    inp=tmp/'input'; ws=tmp/'workspace'
    put(inp/'prompt.md','BENIGN_ORIGINAL_PROMPT: compare synthetic widgets.\n')
    put(inp/'context.txt','BENIGN_SECOND_CONTEXT: retain the blue constraint.\n')
    receipt=research.prepare(ws,inp,roster or copy.deepcopy(ROSTER),mode)
    return inp,ws,receipt

def strategy(receipt):
    seats=receipt['roster']['seats']
    v={**env('strategy',receipt),'requirements':[{'id':'R1','text':'blue constraint','mandatory':True}],
       'questions':[{'id':f'Q{i+1}','text':f'Piece {i+1}?','mandatory':True,'requirement_ids':['R1'],'evidence_goal':'inspect primary source','queries':['synthetic widget'],'priority':'high'} for i in range(len(seats))],
       'assignments':{s['id']:[f'Q{i+1}'] for i,s in enumerate(seats)}}
    if receipt['mode']=='B':
        v.update(cross_component=True,integration_question_ids=['Q1'],verification_plan=[{'question_ids':['Q1'],'primary_evidence':'implementation','different_source_type':'release history','blind_spot':'native option'}])
        v['assignments']['search-2'].append('Q1')
    return v

def search(receipt,st,sid,status='complete'):
    no=status=='no_web'
    return {**env('search',receipt),'seat':sid,'status':status,'scope':'Synthetic test evidence only; not live research','tool_evidence':'BENIGN fixture simulated search/fetch for contract exercise',
            'queries':[] if no else [{'query':'synthetic','tool':'fixture'}],
            'sources':[] if no else [{'id':'S1','title':'Fixture primary','url':'https://docs.python.org/3/library/','accessed_at':'2026-09-11T12:00:00Z','supported_claim':'BENIGN fixture claim, not a live finding','source_type':'docs'}],
            'candidates':[] if no else [{'id':sid+':C1','name':'Synthetic widget','canonical_identity':'synthetic-widget','identity':statement('fact','Fixture source identifies this candidate',['S1']),'integration':statement('proposal','adapter needed'),'remaining_custom_work':statement('proposal','blue adapter'),'fit':{'R1':{'status':'supported','reason':statement('fact','fixture assertion',['S1'])}}}],
            'question_accounts':[{'id':q,'status':'unknown' if no else 'answered','finding':statement('unknown','unavailable') if no else statement('fact','fixture evidence',['S1']),'candidate_ids':[] if no else [sid+':C1']} for q in st['assignments'][sid]],
            'rejected_alternatives':[],'uncovered_questions':st['assignments'][sid] if no else [],'reason':statement('unknown','fixture unavailable route') if status!='complete' else ''}

def complete(ws,r,status='complete'):
    st=strategy(r); put(ws/'strategy.json',st); research.assignments(ws)
    for row in r['roster']['seats']: put(ws/(row['id']+'.json'),search(r,st,row['id'],status if row['id']=='search-1' else 'complete'))
    if r['mode']=='B': put(ws/'challenge.json',{**env('challenge',r),'status':'complete','summary':statement('unknown','Fixture evidence settled; no targets'),'sources':[],'new_candidates':[],'targets':[]})
    cited=['search-2:S1']
    sy={**env('synthesis',r),'status':'complete' if status=='complete' else 'partial','recommendation':'adapt','summary':statement('recommendation','BENIGN_CURRENT_SYNTHESIS: use synthetic widget conditionally',cited),'ranking_rationale':statement('inference','blue constraint first',cited),'strongest_alternative':statement('inference','another synthetic widget',cited),'remaining_custom_work':statement('proposal','adapter'),'unresolved_gaps':[],'contradictions':[],
        'ranked_approaches':[{'id':'A1','candidate_ids':['search-2:C1'],'rationale':statement('inference','fixture fit',cited),'counterarguments':statement('inference','adapter effort',cited),'integration':statement('proposal','compose adapter'),'remaining_custom_work':statement('proposal','blue adapter'),'constraint_matrix':{'R1':{'status':'supported','reason':statement('fact','fixture primary',cited)}}}]}
    if r['mode']=='B': sy.update(challenge_effect='none',challenge_dispositions={})
    put(ws/'synthesis.json',sy)
    return st,sy

def native(path,ws,inp):
    cfg=JobConfig.from_yaml(path)
    cfg.workspace=ws
    cfg.prompt.variables['input_dir']=str(inp)
    sheets=build_sheets(cfg)
    renderer=PromptRenderer(cfg.prompt,len(sheets),cfg.sheet.total_items,cfg.parallel.enabled)
    return cfg,sheets,renderer

def render(renderer,s,attempt=1):
    return renderer.render(s,AttemptContext(attempt_number=attempt,mode=AttemptMode.NORMAL),raw_prompt=s.instrument_name=='cli')

@pytest.mark.parametrize('mode',['A','B','lab'])
def test_native_runtime_all_stage_context_and_dag(tmp_path,mode):
    inp,ws,r=prepare(tmp_path,mode)
    if mode!='lab': complete(ws,r)
    else:
        for i in range(len(r['roster']['seats'])):
            name=f'review-{i+1}'; put(ws/(name+'.md'),'Independent benign review')
            put(ws/(name+'.json'),{**env('review',r),'review':name,'sha256':research.digest(ws/(name+'.md'))})
    filename='thinking-lab.yaml' if mode=='lab' else f'research-{mode.lower()}.yaml'
    cfg,sheets,renderer=native(ASSETS/'scores'/filename,ws,inp)
    graph=check_graph.check(cfg,r['roster'])
    manifests=[]
    for s in sheets:
        rp=render(renderer,s)
        if s.instrument_name=='cli':
            assert subprocess.run(['bash','-n'],input=rp.prompt,text=True,capture_output=True).returncode==0
            continue
        assert 'BENIGN_ORIGINAL_PROMPT' in rp.prompt and 'BENIGN_SECOND_CONTEXT' in rp.prompt
        assert r['run_id'] in rp.prompt
        originals=[x for x in rp.context_manifest if x['source']=='cadenza' and x['category']=='context' and x['delivery_kind']=='directory-inline' and Path(x['resolved_path']).parent==ws/'input-snapshot']
        assert {Path(x['resolved_path']).name:x['source_sha256'].removeprefix('sha256:') for x in originals}=={x['name']:x['sha256'] for x in r['files']}
        again=render(renderer,s,2)
        assert again.context_manifest==rp.context_manifest
        manifests.append({'sheet':s.num,'instrument':s.instrument_name,'manifest':rp.context_manifest})
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    put(EVIDENCE/(mode+'-receipt.json'),{'label':'BENIGN PROVIDER-FREE FIXTURES; not a release lock or live run','runtime_source':str(Path(sys.modules['marianne'].__file__).resolve()),'graph':graph,'original_manifest':r['files'],'stages':manifests})
    assert research.deliver(ws)==0


@pytest.mark.parametrize('mode',['A','B','lab'])
def test_live_run_boundary_brackets_full_original_context(tmp_path,mode):
    inp,ws,r=prepare(tmp_path,mode)
    if mode != 'lab': complete(ws,r)
    else:
        for i in range(len(r['roster']['seats'])):
            name=f'review-{i+1}'; put(ws/(name+'.md'),'Independent benign review')
            put(ws/(name+'.json'),{**env('review',r),'review':name,'sha256':research.digest(ws/(name+'.md'))})
    filename='thinking-lab.yaml' if mode=='lab' else f'research-{mode.lower()}.yaml'
    _,sheets,renderer=native(ASSETS/'scores'/filename,ws,inp)
    for sheet in sheets:
        if sheet.instrument_name == 'cli': continue
        prompt = render(renderer,sheet).prompt
        original = prompt.index('BENIGN_ORIGINAL_PROMPT')
        assert prompt.index('CURRENT RUN BOUNDARY') < original
        directive = prompt.index('LIVE STAGE:')
        assert directive > prompt.index('BENIGN_SECOND_CONTEXT')
        assert 'AUTHORITATIVE OUTPUT:' in prompt[directive:]
        assert 'CURRENT CONTRACT:' in prompt[directive:]
        assert 'filesystem-hunt' in prompt

@pytest.mark.parametrize('mode',['A','B'])
def test_rendered_prepare_shell_metacharacters(tmp_path,mode):
    inp=tmp_path/"in 'q $(touch INJECTED) `id`; dir"; ws=tmp_path/"ws 'q $(touch WS_INJECTED) `id` & dir"; ws.mkdir()
    put(inp/'prompt.md','benign task'); put(inp/'second.txt','benign context')
    cfg,sheets,renderer=native(ASSETS/'scores'/f'research-{mode.lower()}.yaml',ws,inp)
    script=render(renderer,sheets[0]).prompt
    result=subprocess.run(['bash','-c',script],cwd=tmp_path,text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    assert not (tmp_path/'INJECTED').exists() and not (tmp_path/'WS_INJECTED').exists()
    assert research.current(ws)['input_dir']==str(inp)

@pytest.mark.parametrize('change',['seat','owner','requirement','question','empty_seat','duplicate','stale','integration'])
def test_strategy_causal_controls(tmp_path,change):
    _,ws,r=prepare(tmp_path,'B'); st=strategy(r)
    research.validate_strategy(st,r)
    if change=='seat': st['assignments']['unknown']=st['assignments'].pop('search-1')
    elif change=='owner': st['assignments'][r['roster']['seats'][-1]['id']]=['Q2']
    elif change=='requirement': st['questions'][0]['requirement_ids']=['missing']
    elif change=='question': st['assignments']['search-1']=['missing']
    elif change=='empty_seat': st['assignments']['search-1']=[]
    elif change=='duplicate': st['questions'].append(copy.deepcopy(st['questions'][0]))
    elif change=='stale': st['run_id']='earlier'
    elif change=='integration': st['assignments']['search-2']=['Q2']
    with pytest.raises(research.ContractError): research.validate_strategy(st,r)

@pytest.mark.parametrize('change',['family','route','account','candidate_join','source_join','unknown_fit','stale','no_web_claim','bad_schema'])
def test_research_joins_and_routing_controls(tmp_path,change):
    _,ws,r=prepare(tmp_path); st=strategy(r); p=search(r,st,'search-1')
    research.validate_search(p,r,st,'search-1')
    if change in ('family','route'):
        roster=copy.deepcopy(ROSTER)
        if change=='family': roster['seats'][1]['family']=roster['seats'][0]['family']
        else: roster['seats'][1].update(profile=roster['seats'][0]['profile'],model=roster['seats'][0]['model'])
        with pytest.raises(research.ContractError): research.validate_roster(roster,'A')
        return
    if change=='account': p['question_accounts']=[]
    elif change=='candidate_join': p['question_accounts'][0]['candidate_ids']=['missing']
    elif change=='source_join': p['candidates'][0]['fit']['R1']['source_ids']=['missing']
    elif change=='unknown_fit': p['candidates'][0]['fit']['R1']['status']='yes'
    elif change=='stale': p['run_id']='prior'
    elif change=='no_web_claim': p['status']='no_web'
    elif change=='bad_schema': p['schema_version']=42
    with pytest.raises(research.ContractError): research.validate_search(p,r,st,'search-1')

@pytest.mark.parametrize('count',[2,4])
def test_changed_musician_and_cardinality_native(tmp_path,count):
    roster=copy.deepcopy(ROSTER)
    if count==2: roster['seats']=roster['seats'][:2]
    else: roster['seats'].extend([
        {'id':'search-3','family':'fixture-three','profile':'fixture-native-three','model':'fixture-three'},
        {'id':'search-4','family':'fixture-four','profile':'fixture-native-four','model':'fixture-four'},
    ])
    roster['seats'][0].update(profile='fixture-substitute',model='fixture-model',family='fixture-family')
    for mode in ('A','B','lab'):
        inp,ws,r=prepare(tmp_path/mode,mode,roster)
        if mode!='lab': complete(ws,r)
        cfgdict=configure.score(mode,roster,ASSETS)
        path=put(tmp_path/mode/'score.yaml',yaml.safe_dump(cfgdict))
        cfg,sheets,renderer=native(path,ws,inp)
        check_graph.check(cfg,roster)
        for s in sheets:
            if s.instrument_name!='cli':
                assert 'BENIGN_SECOND_CONTEXT' in render(renderer,s).prompt
        assert len([s for s in sheets if s.instrument_name!='cli']) == (count if mode=='lab' else count+2+(mode=='B'))

@pytest.mark.parametrize('change',['directory','receipt','only_summary','new_ai','missing_prompt'])
def test_missing_original_context_fails_causally(tmp_path,change):
    inp,ws,r=prepare(tmp_path); complete(ws,r)
    cfg,sheets,renderer=native(ASSETS/'scores/research-a.yaml',ws,inp)
    if change=='missing_prompt':
        (ws/'input-snapshot/prompt.md').unlink()
        with pytest.raises((OSError,ValueError)): render(renderer,sheets[1])
        return
    if change=='directory':
        import shutil; shutil.rmtree(ws/'input-snapshot')
        with pytest.raises((OSError,ValueError)): render(renderer,sheets[1])
        return
    if change=='receipt':
        (ws/'run-receipt.json').unlink()
        with pytest.raises((OSError,ValueError)): render(renderer,sheets[1])
        return
    if change=='only_summary':
        cfg.sheet.cadenzas[2]=[x for x in cfg.sheet.cadenzas[2] if not x.directory]
    else:
        cfg.movements[1].instrument='codex-cli'
    with pytest.raises(research.ContractError): check_graph.check(cfg,r['roster'])

@pytest.mark.parametrize('status',['partial','no_web'])
def test_partial_delivery_refuses_success_chaining(tmp_path,status):
    _,ws,r=prepare(tmp_path); complete(ws,r,status)
    if status == 'no_web':
        assert research.validate_search(research.read(ws/'search-1.json'), r, strategy(r), 'search-1') == {}
    assert research.deliver(ws)==4
    assert research.read(ws/'delivery/status.json')['status']=='partial'
    assert (ws/'delivery/report.md').exists()
    with pytest.raises(research.ContractError): concert.consumer(ws,tmp_path/'child',ASSETS)

@pytest.mark.parametrize('change',['missing_search','missing_synthesis','stale_synthesis','bad_source_join','missing_challenge','over_three_targets'])
def test_delivery_gate_and_challenge_controls(tmp_path,change):
    _,ws,r=prepare(tmp_path,'B'); st,sy=complete(ws,r)
    if change=='missing_search': (ws/(r['roster']['seats'][-1]['id']+'.json')).unlink()
    elif change=='missing_synthesis': (ws/'synthesis.json').unlink()
    elif change=='stale_synthesis': sy['run_id']='old'; put(ws/'synthesis.json',sy)
    elif change=='bad_source_join': sy['ranked_approaches'][0]['constraint_matrix']['R1']['source_ids']=['search-2:missing']; put(ws/'synthesis.json',sy)
    elif change=='missing_challenge': (ws/'challenge.json').unlink()
    else:
        ch=research.read(ws/'challenge.json'); ch['targets']=[{'id':f'T{i}'} for i in range(4)]; put(ws/'challenge.json',ch)
    assert research.deliver(ws)==4
    assert research.read(ws/'status.json')['status']=='partial'


def test_two_requests_freshness_and_concurrent_boundary(tmp_path):
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        a,b=list(pool.map(lambda p:prepare(p),[tmp_path/'one',tmp_path/'two']))
    assert a[2]['run_id']!=b[2]['run_id']
    inp,ws,r=a; complete(ws,r); assert research.deliver(ws)==0
    old=research.read(ws/'synthesis.json')
    put(inp/'prompt.md','CHANGED_SECOND_REQUEST')
    new=research.prepare(ws,inp,ROSTER,'A')
    assert new['run_id']!=r['run_id'] and new['input_sha256']!=r['input_sha256']
    assert not (ws/'delivery').exists() and not (ws/'synthesis.json').exists()
    complete(ws,new); put(ws/'synthesis.json',old)
    assert research.deliver(ws)==4


def test_input_source_renders_delivery_original_link_for_collision_name(tmp_path):
    inp, ws, _ = prepare(tmp_path)
    put(inp/'report.md', 'ORIGINAL_REPORT_COLLISION')
    receipt = research.prepare(ws, inp, ROSTER, 'A')
    complete(ws, receipt)
    original = next(row for row in receipt['files'] if row['name'] == 'report.md')
    search_record = research.read(ws/'search-2.json')
    search_record['sources'] = [{'id':'I1', 'title':'Provided report', 'source_type':'input',
                                 'input_name':'report.md', 'input_sha256':original['sha256'],
                                 'supported_claim':'Provided report supplies fixture context'}]
    for candidate in search_record['candidates']:
        candidate['identity']['source_ids'] = ['I1']
        candidate['fit']['R1']['reason']['source_ids'] = ['I1']
    for account in search_record['question_accounts']:
        account['finding']['source_ids'] = ['I1']
    put(ws/'search-2.json', search_record)
    synthesis = research.read(ws/'synthesis.json')
    def rebind(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'source_ids': value[key] = ['search-2:I1' if ref == 'search-2:S1' else ref for ref in item]
                else: rebind(item)
        elif isinstance(value, list):
            for item in value: rebind(item)
    rebind(synthesis)
    put(ws/'synthesis.json', synthesis)
    assert research.deliver(ws) == 0
    manifest = research.read(ws/'delivery/status.json')
    copied = next(row for row in manifest['originals'] if row['name'] == 'report.md')
    report = (ws/'delivery/report.md').read_text()
    assert f"]({copied['delivery_name']})" in report
    workspace_report = (ws/'synthesis.md').read_text()
    assert f"](delivery/{copied['delivery_name']})" in workspace_report
    assert (ws/'delivery'/copied['delivery_name']).read_text() == 'ORIGINAL_REPORT_COLLISION'


def test_direct_and_concert_original_hashes_and_synthesis(tmp_path):
    inp,ws,r=prepare(tmp_path)
    # Names that collide with report/status and transport originals are accepted.
    for name in ['report.md','status.json','run-receipt.json','original-0001.txt']:
        put(inp/name,'ORIGINAL_COLLISION_'+name)
    r=research.prepare(ws,inp,ROSTER,'A'); complete(ws,r)
    assert research.deliver(ws)==0
    manifest=research.verify_delivery(ws/'delivery',ws/'input-snapshot',r['run_id'])
    assert len(manifest['originals'])==6
    cfgdict=concert.consumer(ws,tmp_path/'child',ASSETS)
    path=put(tmp_path/'consumer.yaml',yaml.safe_dump(cfgdict)); cfg,sheets,renderer=native(path,tmp_path/'child',inp)
    check_graph.check(cfg,original=str(ws/'input-snapshot'),receipt=str(ws/'run-receipt.json'))
    # Execute the real deterministic consumer preflight, not an imagined hook.
    result=subprocess.run(['bash','-c',render(renderer,sheets[0]).prompt],text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    rp=render(renderer,sheets[1]); assert 'BENIGN_CURRENT_SYNTHESIS' in rp.prompt and 'BENIGN_SECOND_CONTEXT' in rp.prompt
    original_receipts={Path(x['resolved_path']).name:x['source_sha256'].removeprefix('sha256:') for x in rp.context_manifest if x.get('delivery_kind')=='directory-inline' and Path(x['resolved_path']).parent==ws/'input-snapshot'}
    assert original_receipts=={x['name']:x['sha256'] for x in r['files']}
    EVIDENCE.mkdir(parents=True,exist_ok=True); put(EVIDENCE/'consumer-receipt.json',{'label':'BENIGN provider-free consumer assembly; no child job submitted','manifest':rp.context_manifest,'parent_original_manifest':r['files']})
    parent=concert.wrapper(ASSETS/'scores/research-a.yaml',ws,tmp_path/'child',inp,tmp_path/'wrappers',ASSETS)
    loaded=JobConfig.from_yaml(parent)
    assert (parent.parent / loaded.on_success[0].job_path).resolve() == (parent.parent / 'consumer.yaml').resolve()
    assert loaded.on_success[0].fresh
    with pytest.raises(research.ContractError): research.verify_delivery(ws/'delivery',ws/'input-snapshot','old-run')
    put(ws/'delivery/report.md','tampered')
    with pytest.raises(research.ContractError): research.verify_delivery(ws/'delivery',ws/'input-snapshot',r['run_id'])


def test_complete_challenger_ledger_and_disposition_joins(tmp_path):
    _,ws,r=prepare(tmp_path,'B'); st,sy=complete(ws,r)
    discovery=research.read(ws/'search-1.json')
    ch={**env('challenge',r),'status':'complete','summary':statement('fact','Corrected fixture target',['S1']),'sources':discovery['sources'],'new_candidates':[],
        'targets':[{'id':'T1','question_ids':['Q1'],'candidate_ids':['search-1:C1'],'reason':statement('fact','fixture decisive conflict',['S1']),'decision_consequence':statement('recommendation','confidence changes',['S1']),'source_type_rationale':statement('inference','code instead of docs',['S1']),'disposition':'corrected','source_ids':['S1']}]}
    put(ws/'challenge.json',ch)
    sy.update(challenge_effect='confidence',challenge_dispositions={'T1':statement('recommendation','Accept correction conditional on fixture evidence',['challenge:S1'])})
    put(ws/'synthesis.json',sy); assert research.deliver(ws)==0
    sy['challenge_dispositions']={}; put(ws/'synthesis.json',sy)
    assert research.deliver(ws)==4
    sy['challenge_dispositions']={'T1':'accepted'}; put(ws/'synthesis.json',sy)
    ch['targets'][0]['candidate_ids']=['missing']; put(ws/'challenge.json',ch)
    assert research.deliver(ws)==4


def test_assignment_mutation_refused(tmp_path):
    _,ws,r=prepare(tmp_path); complete(ws,r)
    p=research.read(ws/'assignment-search-1.json'); p['strategy_sha256']='old'; put(ws/'assignment-search-1.json',p)
    with pytest.raises(research.ContractError): research.validate_file(ws,'search-1')


def test_changed_actual_native_routing_disagrees_with_roster(tmp_path):
    cfg=JobConfig.from_yaml(ASSETS/'scores/research-a.yaml')
    cfg.instruments['search-2'].profile='opencode'
    with pytest.raises(research.ContractError): check_graph.check(cfg,ROSTER)


def test_default_roster_uses_available_glm_and_gemini_routes_and_midsize_synthesis():
    assert [(row['profile'], row['model']) for row in ROSTER['seats']] == [
        ('opencode', 'zai-coding-plan/glm-5.3-flash'),
        ('antigravity', 'gemini-3.8-flash-high'),
    ]
    assert ROSTER['strategist'] == ROSTER['challenger'] == {
        'profile': 'antigravity', 'model': 'gemini-3.8-flash-high'
    }
    assert ROSTER['synthesizer'] == {'profile': 'codex-cli', 'model': 'gpt-5.6-terra'}
    for mode, calls in [('A', 4), ('B', 5), ('lab', 2)]:
        assert len([row for row in configure.score(mode, ROSTER, ASSETS)['movements'].values()
                    if row['instrument'] != 'cli']) == calls


def test_legacy_lab_invocation_resolves_canonical_score(tmp_path):
    inp,ws,r=prepare(tmp_path,'lab')
    for path in [ROOT/'marianne/scores/prep/thinking-lab.yaml',ROOT/'marianne/scores/thinking-lab.yaml']:
        cfg,sheets,renderer=native(path,ws,inp)
        assert cfg.source_path== (ASSETS/'scores/thinking-lab.yaml').resolve()
        assert 'BENIGN_SECOND_CONTEXT' in render(renderer,sheets[1]).prompt


def test_concert_generated_parent_executes_binding_after_delivery(tmp_path):
    inp,ws,r=prepare(tmp_path); complete(ws,r)
    wrappers=tmp_path/"scores 'q $(touch CHAIN_INJECTED)"
    parent=concert.wrapper(ASSETS/'scores/research-a.yaml',ws,tmp_path/'child',inp,wrappers,ASSETS)
    cfg,sheets,renderer=native(parent,ws,inp)
    # Execute native preparation, then stage explicitly BENIGN performer outputs.
    prep=subprocess.run(['bash','-c',render(renderer,sheets[0]).prompt],text=True,capture_output=True,cwd=tmp_path)
    assert prep.returncode==0,prep.stderr
    assert concert.portable(ASSETS/'prompts/contracts.md') in render(renderer,sheets[1]).prompt
    r=research.current(ws); complete(ws,r)
    # Execute final deterministic delivery plus actual child YAML generation.
    result=subprocess.run(['bash','-c',render(renderer,sheets[-1]).prompt],text=True,capture_output=True,cwd=tmp_path)
    assert result.returncode==0,result.stderr
    assert not (tmp_path/'CHAIN_INJECTED').exists()
    child=JobConfig.from_yaml(wrappers/'consumer.yaml')
    assert child.prompt.variables['parent_run_id']==r['run_id']
    # Reusing a bound consumer after parent preparation must fail before its AI call.
    cs=build_sheets(child); cr=PromptRenderer(child.prompt,len(cs),2,False)
    research.prepare(ws,inp,ROSTER,'A')
    result=subprocess.run(['bash','-c',render(cr,cs[0]).prompt],text=True,capture_output=True)
    assert result.returncode!=0


def test_new_gates_execute_with_hostile_workspace_and_validation_engine(tmp_path):
    inp=tmp_path/'input'; put(inp/'prompt.md','benign task'); put(inp/'context.txt','second sentinel')
    ws=tmp_path/"ws 'q $(touch GATE_INJECTED) `id`; dir"
    r=research.prepare(ws,inp,ROSTER,'A'); complete(ws,r)
    import shutil
    for script in ['research.py','snapshot.py']: shutil.copyfile(ASSETS/'scripts'/script,ws/script)
    cfg,sheets,renderer=native(ASSETS/'scores/research-a.yaml',ws,inp)
    for index in [2,-1]:
        result=subprocess.run(['bash','-c',render(renderer,sheets[index]).prompt],cwd=tmp_path,text=True,capture_output=True)
        assert result.returncode==0,result.stderr
    # Use the current validation engine's actual command substitution path.
    from marianne.execution.validation.engine import ValidationEngine
    import asyncio
    engine=ValidationEngine(ws,{'workspace':str(ws),'sheet_num':4})
    rule=next(v for v in cfg.validations if v.condition=='sheet_num == 4')
    result=asyncio.run(engine._check_command_succeeds(rule))
    assert result.passed,result
    assert not (tmp_path/'GATE_INJECTED').exists()


@pytest.mark.parametrize('change',['extra_original','parent_receipt'])
def test_consumer_refuses_changed_parent_context(tmp_path,change):
    _,ws,r=prepare(tmp_path); complete(ws,r); assert research.deliver(ws)==0
    if change=='extra_original': put(ws/'input-snapshot/forbidden-prior-report.md','extra injected context')
    else:
        active=research.read(ws/'run-receipt.json'); active['run_id']='other-run'; put(ws/'run-receipt.json',active)
    with pytest.raises(research.ContractError): research.verify_delivery(ws/'delivery',ws/'input-snapshot',r['run_id'])


@pytest.mark.parametrize('change',['missing_digests','untyped_manifest','partial_result'])
def test_consumer_typed_manifest_consistency(tmp_path,change):
    _,ws,r=prepare(tmp_path); complete(ws,r); assert research.deliver(ws)==0
    path=ws/'delivery/status.json'; manifest=research.read(path)
    if change=='missing_digests': manifest['artifacts']={}
    elif change=='untyped_manifest': manifest.pop('schema_version')
    else:
        result=research.read(ws/'delivery/result.json'); result['status']='partial'; put(ws/'delivery/result.json',result)
        manifest['artifacts']['result.json']=research.digest(ws/'delivery/result.json')
    put(path,manifest)
    with pytest.raises(research.ContractError): research.verify_delivery(ws/'delivery',ws/'input-snapshot',r['run_id'])


@pytest.mark.parametrize('mode', ['A', 'B'])
@pytest.mark.parametrize('mandatory', [True, False])
def test_delivered_report_defines_requirements_and_candidate_identities(tmp_path, mode, mandatory):
    _, ws, receipt = prepare(tmp_path, mode)
    st, synthesis = complete(ws, receipt)
    st['requirements'][0].update(text='Distinctive amber retention requirement', mandatory=mandatory)
    put(ws/'strategy.json', st)
    research.assignments(ws)
    search_record = research.read(ws/'search-2.json')
    search_record['candidates'][0].update(name='Distinctive Copper Candidate', canonical_identity='urn:fixture:copper-project')
    put(ws/'search-2.json', search_record)
    if mode == 'B':
        new_candidate = copy.deepcopy(search_record['candidates'][0])
        new_candidate.update(id='challenge:C7', name='Distinctive Violet Candidate', canonical_identity='urn:fixture:violet-project')
        challenge = {**env('challenge', receipt), 'status':'complete', 'summary':statement('fact','Benign new-candidate fixture',['S1']),
                         'sources':search_record['sources'], 'new_candidates':[new_candidate],
                         'targets':[{'id':'T7','question_ids':['Q2'],'candidate_ids':['challenge:C7'],
                                     'reason':statement('fact','Benign omission',['S1']),'decision_consequence':statement('recommendation','Fixture alternative',['S1']),
                                     'source_type_rationale':statement('inference','Fixture primary evidence',['S1']),'disposition':'confirmed','source_ids':['S1']}]}
        put(ws/'challenge.json', challenge)
        synthesis['ranked_approaches'][0]['candidate_ids'].append('challenge:C7')
        synthesis.update(challenge_effect='ranking', challenge_dispositions={'T7':statement('recommendation','Include the fixture alternative',['challenge:S1'])})
        put(ws/'synthesis.json', synthesis)
    research.validate_file(ws, 'synthesis')
    original_hashes = {p.name:research.digest(p) for p in (ws/'input-snapshot').iterdir()}
    assert research.deliver(ws) == 0
    report = (ws/'delivery/report.md').read_text()
    assert 'R1' in report and 'Distinctive amber retention requirement' in report
    assert ('Mandatory' if mandatory else 'Preference') in report
    assert 'search-2:C1' in report and 'Distinctive Copper Candidate' in report
    assert 'urn:fixture:copper-project' in report
    if mode == 'B':
        assert 'challenge:C7' in report and 'Distinctive Violet Candidate' in report
        assert 'urn:fixture:violet-project' in report
    assert research.read(ws/'delivery/strategy.json') == st
    manifest = research.verify_delivery(ws/'delivery', ws/'input-snapshot', receipt['run_id'])
    assert manifest['artifacts']['strategy.json'] == research.digest(ws/'strategy.json')
    assert research.read(ws/'delivery/result.json') == synthesis  # presentation cannot change judgments
    assert {p.name:research.digest(p) for p in (ws/'input-snapshot').iterdir()} == original_hashes
    (ws/'delivery/strategy.json').write_text('{}')
    with pytest.raises(research.ContractError):
        research.verify_delivery(ws/'delivery', ws/'input-snapshot', receipt['run_id'])

@pytest.mark.parametrize('mode',['A','B','lab'])
def test_indexed_context_preserves_all_originals_and_delivers_only_shared_core(tmp_path,mode):
    roster=copy.deepcopy(ROSTER)
    roster['context']={'mode':'indexed','shared_context_files':['prompt.md','context.txt']}
    inp,ws,receipt=prepare(tmp_path,mode,roster)
    put(inp/'unindexed.txt','BENIGN_UNINDEXED_ORIGINAL')
    receipt=research.prepare(ws,inp,roster,mode)
    if mode == 'lab':
        for i in range(len(roster['seats'])):
            name=f'review-{i+1}'; put(ws/(name+'.md'),'Independent benign review')
            put(ws/(name+'.json'),{**env('review',receipt),'review':name,'sha256':research.digest(ws/(name+'.md'))})
    else:
        complete(ws,receipt)
    score_path=tmp_path/'indexed.yaml'; score_path.write_text(yaml.safe_dump(configure.score(mode,roster,ASSETS),sort_keys=False))
    cfg,sheets,renderer=native(score_path,ws,inp)
    assert check_graph.check(cfg,roster)['context_mode']=='indexed'
    assert research.read(ws/'context-index.json')['shared_context_files']==['prompt.md','context.txt']
    assert {x['name']:x['sha256'] for x in research.read(ws/'context-index.json')['files']}=={x['name']:x['sha256'] for x in receipt['files']}
    for sheet in sheets:
        if sheet.instrument_name=='cli': continue
        prompt=render(renderer,sheet).prompt
        assert 'BENIGN_ORIGINAL_PROMPT' in prompt and 'BENIGN_SECOND_CONTEXT' in prompt
        assert 'BENIGN_UNINDEXED_ORIGINAL' not in prompt
        files=[Path(x['resolved_path']).name for x in render(renderer,sheet).context_manifest if x['source']=='cadenza' and x['category']=='context']
        assert 'context-index.json' in files and 'run-receipt.json' in files
        assert 'unindexed.txt' not in files
    assert research.deliver(ws)==0


def test_indexed_context_refuses_tampered_index_hash_or_path(tmp_path):
    roster=copy.deepcopy(ROSTER); roster['context']={'mode':'indexed','shared_context_files':['prompt.md']}
    _,ws,_=prepare(tmp_path,'A',roster)
    for field,value in [('sha256','0'*64),('snapshot_path','input-snapshot/../escape.md')]:
        index=research.read(ws/'context-index.json'); index['files'][0][field]=value; put(ws/'context-index.json',index)
        with pytest.raises(research.ContractError): research.current(ws)
        research.prepare(ws,tmp_path/'input',roster,'A')


def test_indexed_sparse_candidate_fit_requires_real_applicable_requirement(tmp_path):
    roster=copy.deepcopy(ROSTER); roster['context']={'mode':'indexed','shared_context_files':['prompt.md']}
    _,ws,receipt=prepare(tmp_path,'A',roster); st=strategy(receipt)
    st['requirements'].append({'id':'R2','text':'secondary preference','mandatory':False})
    put(ws/'strategy.json',st); research.assignments(ws)
    record=search(receipt,st,'search-1'); record['candidates'][0]['fit']={'R1':{'status':'supported','reason':statement('fact','applicable fixture',['S1'])}}
    put(ws/'search-1.json',record)
    assert research.validate_file(ws,'search-1')
    for fit in ({}, {'R404':{'status':'unknown','reason':statement('unknown','not applicable')}}):
        record['candidates'][0]['fit']=fit; put(ws/'search-1.json',record)
        with pytest.raises(research.ContractError): research.validate_file(ws,'search-1')
