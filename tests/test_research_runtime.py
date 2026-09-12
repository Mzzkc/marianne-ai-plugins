"""Portable benign regressions for the shipped research helper and composer."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import pytest
import yaml

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE if (HERE/'scripts/trial.py').is_file() else HERE/'marianne/skills/research'

def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def command(op,w,*args,ok=True):
 p=subprocess.run([sys.executable,str(ROOT/'scripts/trial.py'),op,str(w),*map(str,args)],capture_output=True,text=True)
 if ok:assert p.returncode==0,p.stderr
 else:assert p.returncode!=0
 return p
@pytest.fixture
def run(tmp_path):
 inputs=tmp_path/'input space';inputs.mkdir();(inputs/'prompt.md').write_text('Fixture research question.');(inputs/'detail.txt').write_text('Full controlled fixture context.');(inputs/'extra.txt').write_text('Indexed extra original.')
 w=tmp_path/'workspace space';cfg={'question':'Fixture','domains':['one','two'],'core_files':['prompt.md','detail.txt'],'max_input_bytes':4096,'current_task':'Fixture current task.'};p=tmp_path/'config.json';write(p,cfg);command('prepare',w,inputs,p)
 return w

def source(w,n=1):
 p=w/f'discovery-{n}/bodies/S1.txt';p.write_text('The fixture component exists.');s={'id':f'search-{n}:S1','url':'https://example.invalid/primary','kind':'primary','status':'ok','body_path':str(p.relative_to(w)),'sha256':sha(p)};(w/f'discovery-{n}/sources.jsonl').write_text(json.dumps(s)+'\n');return s

def base_evidence(w):
 for n in [1,2]:
  s=source(w,n);(w/f'discovery-{n}/findings.jsonl').write_text(json.dumps({'tool':'Fixture','statement':'Component exists.','relevance':'Fixture','source_ids':[s['id']]})+'\n')
 write(w/'selection.json',{'reason':'First pass enough','assignments':[]});command('collect',w,'adaptive')

def answer_and_review(w,defect=False):
 s={'kind':'fact','text':'The fixture component exists.','source_ids':['search-1:S1'],'requirement_ids':[]};a={'title':'Fixture','sections':[{'heading':'','paragraphs':[s,s]}]};write(w/'answer-draft.json',a)
 r={'answer_sha256':sha(w/'answer-draft.json'),'coverage_complete':True,'checks':[{'locator':f'0/{n}/0','claim':s['text'],'verdict':'defect' if defect and n==1 else 'supported','reason':'Fixture source.','evidence':[{'source_id':'search-1:S1','passage_ids':['P0001']}]} for n in [0,1]]};write(w/'claim-check-v3.json',r);return a,r

def test_original_custody_has_no_fixed_project_count(run):
 receipt=json.loads((run/'input-receipt.json').read_text());assert len(receipt['files'])==3;assert (run/'shared-cadenza/detail.txt').read_text()=='Full controlled fixture context.'
 (run/'input-snapshot/extra.txt').write_text('drift');command('originals',run,ok=False)

def test_concurrent_fetch_reserves_distinct_bodies(run):
 class Handler(BaseHTTPRequestHandler):
  def do_GET(self):time.sleep(.15);self.send_response(200);self.end_headers();self.wfile.write(self.path.encode())
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  (run/'discovery-1/bodies/S4.txt').write_text('reserved')
  ps=[subprocess.Popen([sys.executable,str(ROOT/'scripts/trial.py'),'fetch',str(run),'1',f'http://127.0.0.1:{server.server_port}/{n}'],stdout=subprocess.PIPE,stderr=subprocess.PIPE) for n in [1,2]]
  for p in ps:_,err=p.communicate();assert p.returncode==0,err
  rows=[json.loads(x) for x in (run/'discovery-1/sources.jsonl').read_text().splitlines()];assert {s['id'] for s in rows}=={'search-1:S5','search-1:S6'};assert all(sha(run/s['body_path'])==s['sha256'] for s in rows);assert (run/'discovery-1/bodies/S4.txt').read_text()=='reserved'
 finally:server.shutdown()

@pytest.mark.parametrize('exit_code,with_body,expected',[(124,True,'partial'),(124,False,'partial'),(7,True,'partial'),(130,True,'held'),(137,True,'held'),(144,True,'held')])
def test_optional_outcomes_preserve_native_status(run,exit_code,with_body,expected):
 if with_body:source(run,3)
 command('optional-outcome',run,3,exit_code,ok=expected!='held');r=json.loads((run/'optional-3-outcome.json').read_text());assert r['status']==expected and r['native_exit_code']==exit_code;assert (run/'discovery-3/findings.jsonl').read_bytes()==b''
 command('optional-outcome',run,3,0,ok=False);command('optional-validate',run,3,ok=expected!='held')
 if expected!='held':
  native=run/'optional-3-native-exit.json';write(native,{});command('optional-validate',run,3,ok=False)

def test_exact_patch_preserves_untouched_claim_and_receipt(run):
 base_evidence(run);a,r=answer_and_review(run,True);command('review',run)
 write(run/'corrections.json',{'replacements':[{'locator':'0/0/0','statement':None}]});command('patches',run,ok=False)
 write(run/'corrections.json',{'replacements':[{'locator':'0/1/0','statement':None}]});command('patches',run);corrected=json.loads((run/'answer-corrected.json').read_text());assert corrected['sections'][0]['paragraphs']==[[a['sections'][0]['paragraphs'][0]]]
 write(run/'changed-checks.json',{'answer_sha256':sha(run/'answer-corrected.json'),'checks':[]});command('merge-recheck',run);command('finish',run);command('verify-delivery',run)
 (run/'answer.md').write_text('drift');command('verify-delivery',run,ok=False)

def test_same_text_cannot_borrow_other_statement_citation(run):
 base_evidence(run);a,r=answer_and_review(run);a['sections'][0]['paragraphs'][1]=dict(a['sections'][0]['paragraphs'][1],source_ids=['search-2:S1']);write(run/'answer-draft.json',a);r['answer_sha256']=sha(run/'answer-draft.json');write(run/'claim-check-v3.json',r);command('review',run,ok=False)

def test_generator_adaptive_edges_guards_and_bounds(tmp_path):
 inp=tmp_path/'input';inp.mkdir();(inp/'prompt.md').write_text('Fixture.');profile=tmp_path/'profile.yaml';profile.write_text(yaml.safe_dump({'name':'fixture','cli':{'command':{'executable':sys.executable}},'models':[]}))
 row={'profile':str(profile),'model':'fixture-model','qualification':'Benign fixture; never dispatched'};roster={'name':'fixture-research','question':'Fixture','domains':['one','two'],'core_files':['prompt.md'],'editor':row,'writer':row,'searchers':[dict(row,model='fixture-model-a',search_method='fixture'),dict(row,model='fixture-model-b',search_method='fixture')]};rp=tmp_path/'roster.json';write(rp,roster);out=tmp_path/'score with spaces';w=tmp_path/'workspace with spaces'
 p=subprocess.run([sys.executable,str(ROOT/'scripts/configure.py'),'--roster',str(rp),'--input',str(inp),'--workspace',str(w),'--out',str(out)],capture_output=True,text=True);assert p.returncode==0,p.stderr
 cfg=yaml.safe_load((out/'research.yaml').read_text());names={x['name']:n for n,x in cfg['movements'].items()};assert cfg['sheet']['dependencies'][names['search-1']]==cfg['sheet']['dependencies'][names['search-2']]==[names['frame']];assert cfg['parallel']['max_concurrent']==2
 for label in ['followup-1','followup-2','correct','recheck']:assert names[label] in cfg['sheet']['skip_when']
 assert cfg['instruments']['fixture-research-followup-1']['config']['timeout_seconds']==430
 assert (out/'profiles/fixture-research-followup-1.sh').read_text().count('optional-outcome')==1
 task='Write to {{ workspace }}/consumer.md';child=tmp_path/'child workspace'
 env=dict(os.environ,HOME=str(tmp_path))
 p=subprocess.run([sys.executable,str(ROOT/'scripts/concert.py'),'wrapper','--score',str(out/'research.yaml'),'--child',str(child),'--profile','cli','--model','fixture','--task',task],env=env,capture_output=True,text=True);assert p.returncode==0,p.stderr
 wrapped=yaml.safe_load((out/'research-concert.yaml').read_text());assert wrapped['workspace']=='~/workspace with spaces'
 assert wrapped['on_success'][0]['job_workspace']==str(child)
 assert task not in wrapped['prompt']['template'] and (out/'consumer-task.txt').read_text()==task
 assert sha(out/'consumer-task.txt') in wrapped['prompt']['template']

@pytest.mark.parametrize('change',['uncited','unknown-source','requirement-kind','empty-sections','empty-paragraph'])
def test_natural_answer_rejects_malformed_or_uncited_content(run,change):
 base_evidence(run);a,_=answer_and_review(run)
 statement=a['sections'][0]['paragraphs'][0]
 if change=='uncited':statement['source_ids']=[]
 elif change=='unknown-source':statement['source_ids']=['search-99:S1']
 elif change=='requirement-kind':statement['kind']='requirement'
 elif change=='empty-sections':a['sections']=[]
 else:a['sections'][0]['paragraphs']=[[]]
 write(run/'answer-draft.json',a);command('answer',run,ok=False)

def test_natural_delivery_cites_used_sources_not_raw_discovery(run):
 base_evidence(run);a,_=answer_and_review(run);command('review',run);command('finish',run)
 prose=(run/'answer.md').read_text();assert a['sections'][0]['paragraphs'][0]['text'] in prose
 assert 'https://example.invalid/primary' in prose and 'Works cited' in prose
 assert 'Component exists.' not in prose

def test_concert_child_native_render_preserves_context_and_task(run,tmp_path):
 from marianne.core.config import JobConfig
 from marianne.core.sheet import build_sheets
 from marianne.daemon.baton.prompt import PromptRenderer
 from marianne.daemon.baton.state import AttemptContext,AttemptMode
 base_evidence(run);answer_and_review(run);command('review',run);command('finish',run)
 child=tmp_path/'child workspace';out=tmp_path/'consumer source';task='Summarize useful findings.'
 args=[sys.executable,str(ROOT/'scripts/concert.py'),'bind','--parent',str(run),'--child',str(child),'--out',str(out),'--profile','fixture','--model','fixture','--task',task]
 p=subprocess.run(args,capture_output=True,text=True);assert p.returncode==0,p.stderr
 cfg=JobConfig.from_yaml(out/'consumer.yaml');cfg.workspace=child;sheets=build_sheets(cfg)
 rendered=PromptRenderer(cfg.prompt,3,3,False).render(sheets[1],AttemptContext(attempt_number=1,mode=AttemptMode.NORMAL)).prompt
 for f in (run/'shared-cadenza').iterdir():assert f.read_text() in rendered
 assert (run/'answer.md').read_text() in rendered and task in rendered
 (run/'input-snapshot/extra.txt').write_text('drift')
 p=subprocess.run(args,capture_output=True,text=True);assert p.returncode!=0

@pytest.mark.parametrize('prep_alias',[False,True])
def test_public_lab_alias_native_context_snapshot_and_delivery(tmp_path,prep_alias):
 from marianne.core.config import JobConfig
 from marianne.core.sheet import build_sheets
 from marianne.daemon.baton.prompt import PromptRenderer
 from marianne.daemon.baton.state import AttemptContext,AttemptMode
 plugin=tmp_path/'plugin';(plugin/'skills').mkdir(parents=True);(plugin/'skills/research').symlink_to(ROOT,target_is_directory=True);(plugin/'scores/prep').mkdir(parents=True)
 entry=plugin/('scores/prep/thinking-lab.yaml' if prep_alias else 'scores/thinking-lab.yaml');entry.symlink_to('../../skills/research/scores/thinking-lab.yaml' if prep_alias else '../skills/research/scores/thinking-lab.yaml')
 inp=tmp_path/'input';inp.mkdir();(inp/'prompt.md').write_text('Independent benign review.');(inp/'detail.md').write_text('Entire original fixture detail.')
 w=tmp_path/'lab workspace';w.mkdir();cfg=JobConfig.from_yaml(entry);cfg.workspace=w;cfg.prompt.variables['input_dir']=str(inp);sheets=build_sheets(cfg)
 def render(sheet):return PromptRenderer(cfg.prompt,4,4,False).render(sheet,AttemptContext(attempt_number=1,mode=AttemptMode.NORMAL)).prompt
 p=subprocess.run(['bash','-c',render(sheets[0])],cwd=w,capture_output=True,text=True);assert p.returncode==0,p.stderr
 receipt=json.loads((w/'run-receipt.json').read_text())
 for n in [1,2]:
  f=w/f'review-{n}.md';f.write_text('Independent fixture review '+str(n));write(w/f'review-{n}.json',{'schema_version':1,'kind':'research-review','run_id':receipt['run_id'],'review':f'review-{n}','sha256':sha(f)})
  assert all(f.read_text() in render(sheets[n]) for f in inp.iterdir())
 p=subprocess.run(['bash','-c',render(sheets[-1])],cwd=w,capture_output=True,text=True);assert p.returncode==0,p.stderr
 args=[sys.executable,str(w/'research.py'),'verify-delivery','--delivery',str(w/'delivery'),'--original-dir',str(w/'input-snapshot'),'--run-id',receipt['run_id']]
 p=subprocess.run(args,capture_output=True,text=True);assert p.returncode==0,p.stderr
 (w/'input-snapshot/detail.md').write_text('tampered')
 p=subprocess.run(args,capture_output=True,text=True);assert p.returncode!=0
