#!/usr/bin/env python3
"""Generate a real native successful-parent research→consumer chain; never submit."""
import argparse,hashlib,json,shlex,sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import trial

def portable(path):
 path=Path(path).expanduser().resolve()
 try:return '~/' + str(path.relative_to(Path.home()))
 except ValueError:return str(path)

def bind(parent,child,out,profile,model,task,seconds):
 parent=parent.resolve();child=child.resolve();out=out.resolve();trial.require(parent!=child and parent not in child.parents and child not in parent.parents,'disjoint consumer workspace required');receipt=trial.verify_delivery(parent)
 helper=ROOT/'scripts/concert.py';verify='python3 '+shlex.quote(str(ROOT/'scripts/trial.py'))+' verify-delivery '+shlex.quote(str(parent));finish='python3 '+shlex.quote(str(helper))+' consumer-check --parent '+shlex.quote(str(parent))+' --child {workspace}'
 cfg={'name':out.name+'-consumer','workspace':portable(child),'instrument':profile,'instrument_config':{'model':model,'timeout_seconds':seconds,'interactive':False},'retry':{'max_retries':0,'max_completion_attempts':0},'movements':{1:{'name':'verify-parent','instrument':'cli'},2:{'name':'consume-research','instrument':profile},3:{'name':'verify-consumer','instrument':'cli'}},'sheet':{'size':1,'total_items':3,'dependencies':{2:[1],3:[2]},'per_sheet_fallbacks':{1:[],2:[],3:[]},'cadenzas':{2:[{'directory':str(parent/'shared-cadenza'),'as':'context','required':True}]+[{'file':str(parent/f),'as':'context','required':True} for f in ['answer.md','delivery.json']]}},'prompt':{'template':'{% if sheet_num == 1 %}\nset -eu\n'+verify+'\n{% elif sheet_num == 2 %}\nCURRENT CONSUMER TASK: '+task+'\nUse the verified parent research and original controlling context; remaining originals are accessible through the exact supplied index. No new search, installation, application edits, global memory writes or jobs unless separately commissioned. Write useful natural prose to {{ workspace }}/consumer.md.\n{% else %}\n'+finish.replace('{workspace}','"{{ workspace }}"')+'\n{% endif %}'},'validations':[{'type':'command_succeeds','command':verify,'condition':'sheet_num == 1','retry_count':0},{'type':'command_succeeds','command':finish,'condition':'sheet_num == 3','retry_count':0}]}
 if profile=='cli':
  cfg['sheet']['cadenzas']={}
  cfg['prompt']['template']='{% if sheet_num == 1 %}\n'+verify+'\n{% elif sheet_num == 2 %}\n'+task+'\n{% else %}\n'+finish.replace('{workspace}','"{{ workspace }}"')+'\n{% endif %}'
 out.mkdir(parents=True,exist_ok=True);(out/'consumer.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False));return cfg

def wrapper(score,child,profile,model,task,seconds):
 score=score.resolve();out=score.parent;cfg=yaml.safe_load(score.read_text());parent=Path(cfg['workspace']).expanduser().resolve();cfg['workspace']=portable(parent);trial.require(parent!=child.resolve() and parent not in child.resolve().parents and child.resolve() not in parent.parents,'disjoint consumer workspace')
 task_path=out/'consumer-task.txt';task_path.write_text(task);task_sha=trial.digest(task_path)
 args=['python3',str(ROOT/'scripts/concert.py'),'bind','--parent',str(parent),'--child',str(child.resolve()),'--out',str(out),'--profile',profile,'--model',model,'--task-file',str(task_path),'--task-sha256',task_sha,'--seconds',str(seconds)];command=shlex.join(args);ending='python3 '+shlex.quote(str(out/'scripts/trial.py'))+' finish "{{ workspace }}" '
 legacy='python3 "{{ score_dir }}/scripts/trial.py" finish "{{ workspace }}" '
 cfg['prompt']['template']=cfg['prompt']['template'].replace(legacy,ending)
 trial.require(ending in cfg['prompt']['template'],'parent must use the proven deterministic finish stage');cfg['prompt']['template']=cfg['prompt']['template'].replace(ending,ending+'\n'+command)
 cfg['on_success']=[{'type':'run_job','job_path':'consumer.yaml','job_workspace':str(child.resolve()),'fresh':True,'detached':True}];cfg['concert']={'enabled':True,'max_chain_depth':1,'inherit_workspace':False}
 path=out/'research-concert.yaml';path.write_text(yaml.safe_dump(cfg,sort_keys=False));decl=score.with_suffix('.generated-inputs.yaml');path.with_suffix('.generated-inputs.yaml').write_bytes(decl.read_bytes());return path

def consumer_check(parent,child):
 receipt=trial.verify_delivery(parent);p=child/'consumer.md';trial.require(p.is_file() and p.read_text().strip(),'missing consumer output');trial.write(child/'consumer-receipt.json',{'parent_answer_sha256':receipt['answer_sha256'],'parent_input_receipt_sha256':receipt['input_receipt_sha256'],'consumer_sha256':trial.digest(p)})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['wrapper','bind','consumer-check']);p.add_argument('--score',type=Path);p.add_argument('--parent',type=Path);p.add_argument('--child',type=Path,required=True);p.add_argument('--out',type=Path);p.add_argument('--profile');p.add_argument('--model');p.add_argument('--task');p.add_argument('--task-file',type=Path);p.add_argument('--task-sha256');p.add_argument('--seconds',type=int,default=300);a=p.parse_args()
 if a.task_file:
  if a.task_sha256:trial.require(trial.digest(a.task_file)==a.task_sha256,'consumer task source changed')
  a.task=a.task_file.read_text()
 if a.command=='wrapper':print(wrapper(a.score,a.child,a.profile,a.model,a.task,a.seconds))
 elif a.command=='bind':bind(a.parent,a.child,a.out,a.profile,a.model,a.task,a.seconds)
 else:consumer_check(a.parent,a.child)
