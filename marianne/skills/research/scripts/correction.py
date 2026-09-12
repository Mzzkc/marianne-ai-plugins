"""Bounded locator replacements and changed-claim review joins; no model orchestration."""
import copy

def units(answer):
 return {f'{si}/{pi}/{ti}':s for si,sec in enumerate(answer['sections']) for pi,p in enumerate(sec['paragraphs']) for ti,s in enumerate(p if isinstance(p,list) else [p])}
def targets(answer,review):
 checks={c['locator']:c for c in review['checks']}
 return {loc for loc,s in units(answer).items() if (loc in checks and checks[loc]['verdict']=='defect') or (s['kind'] in ['fact','inference','recommendation'] and (loc not in checks or checks[loc]['verdict']!='supported'))}
def construct(answer,review,patch,require):
 require(set(patch)=={'replacements'},'correction contains unrequested fields');rs=patch['replacements'];require(isinstance(rs,list),'replacements list')
 required=targets(answer,review);replacements={}
 for r in rs:
  require(isinstance(r,dict) and set(r)=={'locator','statement'},'replacement shape')
  loc=r['locator'];require(loc in required and loc not in replacements,'unapproved or duplicate correction locator');require(r['statement'] is None or isinstance(r['statement'],dict),'statement object or null');replacements[loc]=r['statement']
 require(set(replacements)==required,'correction must cover exactly the selected unsupported/defective locators')
 out={'title':answer['title'],'sections':[]};mapping={}
 for si,sec in enumerate(answer['sections']):
  newsec={'heading':sec['heading'],'paragraphs':[]};pending=[]
  for pi,p in enumerate(sec['paragraphs']):
   newp=[];orig=[]
   for ti,s in enumerate(p if isinstance(p,list) else [p]):
    old=f'{si}/{pi}/{ti}';v=replacements.get(old,s)
    if v is not None:newp.append(copy.deepcopy(v));orig.append(old)
   if newp:
    np=len(newsec['paragraphs']);newsec['paragraphs'].append(newp)
    for nt,old in enumerate(orig):pending.append((np,nt,old))
  if newsec['paragraphs']:
   ns=len(out['sections']);out['sections'].append(newsec)
   for np,nt,old in pending:mapping[f'{ns}/{np}/{nt}']={'original_locator':old,'changed':old in replacements}
 return out,mapping

def apply(w,t):
 answer=t.read(w/'answer-draft.json');review=t.check_review(w);patch=t.read(w/'corrections.json')
 projected,mapping=construct(answer,review,patch,t.require)
 ids={s['id'] for s in t.evidence_check(w)['sources'] if s['kind']=='primary' and s['status']=='ok'};t.research.validate_answer(projected,ids,set())
 t.write(w/'answer-corrected.json',projected)
 original_checks={c['locator']:c for c in review['checks']};inherited=[];changed=[];newunits=units(projected);oldunits=units(answer)
 for loc,m in mapping.items():
  old=m['original_locator']
  if m['changed']:changed.append({'locator':loc,'original_locator':old,'old_statement':oldunits[old],'new_statement':newunits[loc]})
  elif old in original_checks:
   c=copy.deepcopy(original_checks[old]);t.require(c['claim']==newunits[loc]['text'],'unchanged text drift');c['locator']=loc;inherited.append(c)
 t.write(w/'recheck-input.json',{'answer_sha256':t.digest(w/'answer-corrected.json'),'original_review_sha256':t.digest(w/'claim-check-v3.json'),'patch_sha256':t.digest(w/'corrections.json'),'changed':changed,'inherited_checks':inherited,'removed_original_locators':sorted(targets(answer,review)-{m['original_locator'] for m in mapping.values()})})

def merge(w,t):
 inp=t.read(w/'recheck-input.json');t.require(inp['answer_sha256']==t.digest(w/'answer-corrected.json'),'corrected answer changed after patch');t.require(inp['original_review_sha256']==t.digest(w/'claim-check-v3.json'),'original proof changed');t.require(inp['patch_sha256']==t.digest(w/'corrections.json'),'patch changed')
 expected,mapping=construct(t.read(w/'answer-draft.json'),t.check_review(w),t.read(w/'corrections.json'),t.require);t.require(expected==t.read(w/'answer-corrected.json'),'unrequested corrected-answer edits')
 changes={loc for loc,m in mapping.items() if m['changed']};original_checks={c['locator']:c for c in t.check_review(w)['checks']};inherited=[]
 for loc,m in mapping.items():
  if not m['changed'] and m['original_locator'] in original_checks:
   c=copy.deepcopy(original_checks[m['original_locator']]);c['locator']=loc;inherited.append(c)
 t.require(inherited==inp['inherited_checks'],'inherited check metadata changed')
 new=t.read(w/'changed-checks.json');t.require(new.get('answer_sha256')==inp['answer_sha256'],'changed review answer binding');t.require(isinstance(new.get('checks'),list),'changed checks list')
 locs=[c.get('locator') for c in new['checks']];t.require(len(locs)==len(set(locs)) and set(locs)==changes,'review must cover exactly changed remaining locators')
 merged={'answer_sha256':inp['answer_sha256'],'coverage_complete':True,'checks':inherited+new['checks'],'provenance':{'inherited_unchanged':len(inherited),'reviewed_changed':len(new['checks']),'removed':inp['removed_original_locators']}}
 # Unknown/proposal rows may have lacked prior review; that is honest incomplete coverage.
 merged['coverage_complete']=len(merged['checks'])==len(units(expected))
 t.write(w/'recheck-v3.json',merged);t.check_review(w,True)
