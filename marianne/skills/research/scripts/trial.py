#!/usr/bin/env python3
"""Owned trial mechanics. Shape/hash/skip checks are not semantic verification."""
import argparse, hashlib, json, sys, shutil, urllib.request, urllib.error, copy, fcntl
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime, timezone
D=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(D/'resources'))
import research
import passages
import correction
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def write(p,x): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def rows(p): return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def require(ok,msg):
 if not ok: raise ValueError(msg)
def within(w,p):
 q=(w/p).resolve(); require(q.is_relative_to(w.resolve()),'path outside owned workspace'); return q
def original_check(w):
 r=read(w/'input-receipt.json'); require(r.get('files'),'empty original receipt'); require({f['original_name'] for f in r['files']}=={p.name for p in (w/'input-snapshot').iterdir()},'snapshot inventory changed')
 for f in r['files']: require(digest(w/f['path'])==f['sha256'],'original changed: '+f['path'])
 return r
def prepare(w,source,config):
 require(not w.exists(),'fresh workspace required; refuse replacing anything'); w.mkdir(parents=True)
 files=[]; inputs=sorted(source.iterdir()); require(inputs and all(p.is_file() for p in inputs),'nonempty flat input directory required')
 require(sum(p.stat().st_size for p in inputs)<=config['max_input_bytes'],'input exceeds configured byte cap; do not truncate')
 for p in inputs:
  p.read_text();out=w/'input-snapshot'/p.name;out.parent.mkdir(exist_ok=True);shutil.copyfile(p,out)
  files.append({'original_name':p.name,'path':str(out.relative_to(w)),'bytes':out.stat().st_size,'sha256':digest(out)})
 require(set(config['core_files']) <= {p.name for p in inputs},'core files absent')
 write(w/'input-receipt.json',{'schema':'research-originals-v1','files':files,'source':str(source)})
 write(w/'context-index.json',{'note':'All originals remain accessible; index does not prove every file was read.','files':files})
 write(w/'research-config.json',config)
 for n in range(1,len(config['domains'])+3):
  x=w/f'discovery-{n}';x.mkdir();(x/'bodies').mkdir();(x/'findings.jsonl').touch();(x/'sources.jsonl').touch();(x/'queries.jsonl').touch()
 shared=w/'shared-cadenza';shared.mkdir()
 for name in config['core_files']:shutil.copyfile(w/'input-snapshot'/name,shared/name)
 for name in ['input-receipt.json','context-index.json','research-config.json']:shutil.copyfile(w/name,shared/name)
 (shared/'000__CURRENT_TASK.md').write_text(config['current_task']+'\n')
 original_check(w)

def validate_frame(w):
 f=read(w/'frame.json'); require(isinstance(f.get('question'),str) and f['question'].strip(),'frame question')
 a=f.get('assignments'); count=len(read(w/'research-config.json')['domains']); require(isinstance(a,list) and len(a)==count,'one assignment per configured domain')
 require([x.get('id') for x in a]==list(range(1,count+1)),'configured assignment IDs')
 for x in a:
  for k in ['domain','question','query_directions','decision_criteria']: require(x.get(k),'missing frame '+k)
 return f
def selection(w):
 x=read(w/'selection.json'); a=x.get('assignments'); require(isinstance(a,list) and len(a)<=2,'zero to two selections')
 ids=[s.get('slot') for s in a]; require(ids==list(range(1,len(a)+1)),'contiguous unique slots')
 for s in a:
  for k in ['question','why_it_changes_advice','query_directions','stop_condition']: require(isinstance(s.get(k),str) and s[k].strip(),'missing selection '+k)
 require(isinstance(x.get('reason'),str) and x['reason'].strip(),'selection reason required')
 return x
def evidence_check(w):
 e=read(w/'evidence.json')
 for s in e['sources']: require(digest(within(w,s['body_path']))==s['sha256'],'retained source changed')
 return e
def check_review(w,corrected=False):
 r=read(w/('recheck-v3.json' if corrected else 'claim-check-v3.json')); answer=read(w/('answer-corrected.json' if corrected else 'answer-draft.json'))
 require(r.get('answer_sha256')==digest(w/('answer-corrected.json' if corrected else 'answer-draft.json')),'review answer binding')
 require(isinstance(r.get('checks'),list) and r['checks'],'nonempty checks')
 statements={}
 for si,sec in enumerate(answer['sections']):
  for pi,p in enumerate(sec['paragraphs']):
   for ti,st in enumerate(p if isinstance(p,list) else [p]): statements[f"{si}/{pi}/{ti}"]=st
 ev=evidence_check(w); source_map={s['id']:s for s in ev['sources']}; passage_map=passages.verify(w,ev)
 seen=set()
 for c in r['checks']:
  require(c.get('locator') in statements,'unknown statement locator'); st=statements[c['locator']]
  require(c['locator'] not in seen,'duplicate review locator'); seen.add(c['locator'])
  require(c.get('claim')==st['text'],'check does not quote exact located answer claim')
  require(c.get('verdict') in ['supported','defect','unverified'],'check verdict')
  require(isinstance(c.get('reason'),str) and c['reason'].strip(),'check reason')
  require(isinstance(c.get('evidence'),list),'check evidence list')
  if c['verdict']=='supported': require(c['evidence'],'supported requires body evidence')
  for e in c['evidence']:
   require(e.get('source_id') in st['source_ids'],'review evidence is not cited by exact claim'); require(e.get('source_id') in source_map,'unknown check source'); s=source_map[e['source_id']]
   require('quote' not in e,'typed quotes are forbidden in v2; select exact passage IDs')
   ids=e.get('passage_ids'); require(isinstance(ids,list) and ids and len(ids)==len(set(ids)),'nonempty unique passage IDs required')
   require(all(i in passage_map.get(e['source_id'],{}) for i in ids),'unknown or mismatched source passage ID')
 require(isinstance(r.get('coverage_complete'),bool),'honest coverage required')
 if r['coverage_complete']:
  require(seen==set(statements),'complete check omits answer statements')
 return r
def repair_needed(w,r,corrected=False):
 a=read(w/('answer-corrected.json' if corrected else 'answer-draft.json')); eligible=set()
 for si,sec in enumerate(a['sections']):
  for pi,p in enumerate(sec['paragraphs']):
   for ti,st in enumerate(p if isinstance(p,list) else [p]):
    if st['kind'] in ['fact','inference','recommendation']:eligible.add(f"{si}/{pi}/{ti}")
 checked={c['locator']:c for c in r['checks']}
 return any(c['verdict']=='defect' for c in r['checks']) or any(loc not in checked or checked[loc]['verdict']!='supported' for loc in eligible)
def admit(w,role):
 original_check(w)
 if role.startswith('followup-'): require(int(role.split('-')[1]) in [x['slot'] for x in selection(w)['assignments']], 'unselected optional work')
 if role in ['correct','recheck']: require(repair_needed(w,check_review(w)),'no unsupported/defective material warrants correction')
def sources(w,n):
 result=rows(w/f'discovery-{n}/sources.jsonl'); ids=set()
 for s in result:
  require(s.get('id','').startswith(f'search-{n}:S'),'source ID namespace'); require(s['id'] not in ids,'duplicate source ID'); ids.add(s['id'])
  require(s.get('kind') in ['primary','lead'],'source kind'); require(s.get('url','').startswith(('https://','http://')),'HTTP source URL')
  p=within(w,s['body_path']); require(p.is_file() and digest(p)==s.get('sha256'),'source body/hash mismatch')
 return result
def validate_search(w,n):
 ss=sources(w,n); fs=rows(w/f'discovery-{n}/findings.jsonl'); ids={s['id'] for s in ss if s['kind']=='primary' and s.get('status')=='ok'}
 require(fs,'no findings written')
 for f in fs:
  require(f.get('tool') and f.get('statement') and f.get('relevance'),'finding needs tool, statement and relevance')
  require(isinstance(f.get('source_ids'),list) and f['source_ids'] and set(f['source_ids'])<=ids,'finding needs successful primary IDs')
 return ss,fs
def optional_parts(w,n):
 errors=[]
 try:ss=sources(w,n)
 except (ValueError,OSError,KeyError,TypeError) as exc:return [],[],['invalid source custody: '+str(exc)]
 try:
  fs=rows(w/f'discovery-{n}/findings.jsonl');ids={x['id'] for x in ss if x['kind']=='primary' and x['status']=='ok'}
  for f in fs:require(f.get('tool') and f.get('statement') and f.get('relevance') and isinstance(f.get('source_ids'),list) and f['source_ids'] and set(f['source_ids'])<=ids,'invalid optional finding')
 except (ValueError,OSError,KeyError,TypeError) as exc:fs=[];errors.append('invalid findings: '+str(exc))
 return ss,fs,errors
def record_optional(w,n,exit_code):
 path=w/f'optional-{n}-native-exit.json'
 with path.open('x') as f:json.dump({'native_exit_code':exit_code,'timeout_exit124':exit_code==124,'signal_or_forced_kill_exit137':exit_code==137,'observed_at':datetime.now(timezone.utc).isoformat(),'authority':'task wrapper after native process exited; exclusive receipt, not model-authored'},f,indent=2)
 ss,fs,errors=optional_parts(w,n);lane=w/f'discovery-{n}'
 status='held' if exit_code in [130,137,144] else 'complete' if exit_code==0 and fs and not errors else 'partial'
 write(w/f'optional-{n}-outcome.json',{'status':status,'native_receipt_sha256':digest(path),'sources_ledger_sha256':digest(lane/'sources.jsonl'),'findings_ledger_sha256':digest(lane/'findings.jsonl'),'native_exit_code':exit_code,'valid_findings':len(fs),'intact_primary_bodies':sum(x['status']=='ok' and x['kind']=='primary' for x in ss),'errors':errors,'evidence_state':'findings' if fs else 'unassessed bodies' if any(x['status']=='ok' for x in ss) else 'no result'})
def optional_validate(w,n):
 r=read(w/f'optional-{n}-outcome.json');native=read(w/f'optional-{n}-native-exit.json');lane=w/f'discovery-{n}'
 require(r['native_receipt_sha256']==digest(w/f'optional-{n}-native-exit.json') and r['native_exit_code']==native['native_exit_code'],'native exit receipt drift')
 require(r['sources_ledger_sha256']==digest(lane/'sources.jsonl') and r['findings_ledger_sha256']==digest(lane/'findings.jsonl'),'optional ledger drift')
 ss,fs,errors=optional_parts(w,n);require(errors==r['errors'] and len(fs)==r['valid_findings'] and sum(x['status']=='ok' and x['kind']=='primary' for x in ss)==r['intact_primary_bodies'],'optional evidence drift')
 require(r['status']==('held' if native['native_exit_code'] in [130,137,144] else 'complete' if native['native_exit_code']==0 and fs and not errors else 'partial'),'optional status invented');require(r['status']!='held','kill/cancellation-class exit requires conductor diagnosis; no automatic continuation');require(r['evidence_state']==('findings' if fs else 'unassessed bodies' if any(x['status']=='ok' for x in ss) else 'no result'),'optional evidence state invented');return r,ss,fs
def collect(w,adaptive=False,first=False):
 nums=list(range(1,len(read(w/'research-config.json')['domains'])+1));ss=[];fs=[];optional=[]
 for n in nums:
  a,b=validate_search(w,n);ss+=a;fs+=b
 if adaptive and not first:
  for selected in selection(w)['assignments']:
   n=len(nums)+selected['slot'];r,a,b=optional_validate(w,n);optional.append({'lane':n,**r});ss+=a;fs+=b
 referenced={i for f in fs for i in f['source_ids']}
 write(w/('first-evidence.json' if first else 'evidence.json'),{'sources':ss,'findings':fs,'included_discovery':nums+[x['lane'] for x in optional],'optional_outcomes':optional,'unassessed_source_ids':[x['id'] for x in ss if x['status']=='ok' and x['kind']=='primary' and x['id'] not in referenced]})
 if not first:passages.make(w,read(w/'evidence.json'))
def answer(w,corrected=False):
 e=evidence_check(w); ids={s['id'] for s in e['sources'] if s['kind']=='primary' and s['status']=='ok'}
 a=read(w/('answer-corrected.json' if corrected else 'answer-draft.json')); research.validate_answer(a,ids,set());return a

def finish(w):
 r=check_review(w); defects=repair_needed(w,r); a=answer(w,defects)
 if defects:r=check_review(w,True)
 require(not repair_needed(w,r,defects),'Final answer retains unsupported or defective material; delivery withheld')
 src={s['id']:s for s in evidence_check(w)['sources']}; used={}; lines=['# '+a['title'],'']
 for sec in a['sections']:
  if sec['heading']:lines+=['## '+sec['heading'],'']
  for para in sec['paragraphs']:
   parts=[]
   for s in para if isinstance(para,list) else [para]:
    urls=list(dict.fromkeys(src[i]['url'] for i in s['source_ids']))
    for i in s['source_ids']: used.setdefault(src[i]['url'],src[i].get('title') or urlparse(src[i]['url']).netloc)
    parts.append(s['text']+(' '+ ' '.join('['+used[u]+']('+u+')' for u in urls) if urls else ''))
   lines+=[' '.join(parts),'']
 lines+=['## Works cited','']+[f'- [{title}]({url})' for url,title in used.items()]+['']
 (w/'answer.md').write_text('\n'.join(lines));write(w/'delivery.json',{'answer_sha256':digest(w/'answer.md'),'corrected':defects,'review_complete':r['coverage_complete'],'remaining_defects':sum(c['verdict']=='defect' for c in r['checks']),'unverified_checks':sum(c['verdict']=='unverified' for c in r['checks']),'semantic_acceptance':'Not implied by shape validation.','remaining_unsupported_material':repair_needed(w,r,defects)})

 r=read(w/'delivery.json');r.update(optional_outcomes=evidence_check(w).get('optional_outcomes',[]),research_status='partial' if any(x['status']!='complete' for x in evidence_check(w).get('optional_outcomes',[])) else 'complete',input_receipt_sha256=digest(w/'input-receipt.json'),evidence_sha256=digest(w/'evidence.json'),review_sha256=digest(w/('recheck-v3.json' if defects else 'claim-check-v3.json')),answer_json_sha256=digest(w/('answer-corrected.json' if defects else 'answer-draft.json')));write(w/'delivery.json',r)
def verify_delivery(w):
 original_check(w);evidence_check(w);r=read(w/'delivery.json')
 for key,name in [('answer_sha256','answer.md'),('input_receipt_sha256','input-receipt.json'),('evidence_sha256','evidence.json'),('review_sha256','recheck-v3.json' if r['corrected'] else 'claim-check-v3.json'),('answer_json_sha256','answer-corrected.json' if r['corrected'] else 'answer-draft.json')]:require(r[key]==digest(w/name),'delivery subject changed: '+name)
 review=check_review(w,r['corrected']);require(not repair_needed(w,review,r['corrected']),'unsupported material in delivery');return r

def fetch(w,n,url,kind):
 require(kind in ['primary','lead'],'kind'); lane=w/f'discovery-{n}'; require(lane.is_dir(),'owned lane absent')
 # Serialize allocation through commit within one lane; other lanes remain independent.
 with (lane/'.fetch.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  return _fetch_locked(w,n,url,kind,lane)
def _fetch_locked(w,n,url,kind,lane):
 old=rows(lane/'sources.jsonl'); nums=[int(s['id'].rsplit(':S',1)[1]) for s in old]+[int(p.stem[1:]) for p in (lane/'bodies').glob('S*.txt') if p.stem[1:].isdigit()]; seq=max(nums,default=0)+1; sid=f'search-{n}:S{seq}'; start=datetime.now(timezone.utc).isoformat(); code=None; status='failed'
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MarianneResearch/1.0'}),timeout=25) as r:
   code=r.status; data=r.read(4*1024*1024+1); require(len(data)<=4*1024*1024,'body exceeds4MiB; not silently truncated'); status='ok' if 200<=code<300 else 'failed'
 except urllib.error.HTTPError as e: code=e.code; data=e.read(4*1024*1024)
 except Exception as e: data=str(e).encode()
 p=lane/'bodies'/f'S{seq}.txt'
 with p.open('xb') as body_file: body_file.write(data)
 s={'id':sid,'url':url,'kind':kind,'status':status,'http_status':code,'body_path':str(p.relative_to(w)),'sha256':digest(p),'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'acquisition':'trial.py urllib; actual response body, semantic primary status caller-declared'}
 with (lane/'sources.jsonl').open('a') as f:f.write(json.dumps(s)+'\n')
 print(json.dumps(s))

def main():
 p=argparse.ArgumentParser();p.add_argument('operation');p.add_argument('workspace',type=Path);p.add_argument('arg',nargs='?');p.add_argument('extra',nargs='?');p.add_argument('--kind',default='primary'); a=p.parse_args();w=a.workspace.resolve();op=a.operation
 if op=='prepare':prepare(w,Path(a.arg),read(Path(a.extra)))
 elif op=='fetch':fetch(w,int(a.arg),a.extra,a.kind)
 elif op=='originals':original_check(w)
 elif op=='frame':validate_frame(w)
 elif op=='selection':selection(w)
 elif op=='optional-outcome':
  record_optional(w,int(a.arg),int(a.extra))
  if int(a.extra) in [130,137,144]:return int(a.extra)
 elif op=='optional-validate':optional_validate(w,int(a.arg))
 elif op=='admit':admit(w,a.arg)
 elif op=='skip':
  role=a.arg
  if role.startswith('followup-'):skip=int(role.split('-')[1]) not in [x['slot'] for x in selection(w)['assignments']]
  else:skip=not repair_needed(w,check_review(w))
  return 0 if skip else 1
 elif op=='search':validate_search(w,int(a.arg))
 elif op=='collect-first':collect(w,first=True)
 elif op=='collect':collect(w,adaptive=a.arg=='adaptive')
 elif op=='answer':answer(w,a.arg=='corrected')
 elif op=='review':check_review(w,a.arg=='corrected')
 elif op=='patches':correction.apply(w,sys.modules[__name__])
 elif op=='merge-recheck':correction.merge(w,sys.modules[__name__])
 elif op=='passages':passages.make(w,evidence_check(w));passages.verify(w,evidence_check(w))
 elif op=='finish':finish(w)
 elif op=='verify-delivery':verify_delivery(w)
 else:raise ValueError('unknown operation')
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print(f'ERROR: {e}',file=sys.stderr);sys.exit(2)
