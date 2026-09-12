#!/usr/bin/env python3
"""Generate local native wrappers, never submit them. Portable paths and fresh child."""
import argparse
import json
import os
import shlex
from pathlib import Path
import yaml
from configure import SQ, injection
from research import current, verify_delivery, require

ROOT=Path(__file__).resolve().parents[1]

def portable(path):
    """Keep native YAML paths portable without changing their resolved target."""
    path = Path(path).resolve()
    try:
        return '~/' + str(path.relative_to(Path.home()))
    except ValueError:
        return str(path)


def consumer(parent_workspace, child_workspace, resources=ROOT, profile='codex-cli'):
    parent_workspace=parent_workspace.resolve(); child_workspace=child_workspace.resolve(); resources=resources.resolve()
    require(child_workspace != parent_workspace and parent_workspace not in child_workspace.parents and child_workspace not in parent_workspace.parents, 'consumer workspace must be disjoint')
    receipt=current(parent_workspace)
    original=parent_workspace/'input-snapshot'; delivery=parent_workspace/'delivery'
    verify_delivery(delivery,original,receipt['run_id'])
    verify='python3 '+shlex.quote(str(resources/'scripts/research.py'))+' verify-delivery --delivery '+shlex.quote(str(delivery))+' --original-dir '+shlex.quote(str(original))+' --run-id '+shlex.quote(receipt['run_id'])
    return {'name':'research-consumer','workspace':portable(child_workspace),'workspace_lifecycle':{'archive_on_fresh':True},'instrument':profile,'instrument_config':{'timeout_seconds':360},'retry':{'max_retries':0,'max_completion_attempts':0},'movements':{1:{'name':'verify-parent','instrument':'cli'},2:{'name':'consume-original-and-decision','instrument':profile}},'sheet':{'size':1,'total_items':2,'dependencies':{2:[1]},'per_sheet_fallbacks':{1:[],2:[]},'cadenzas':{2:[injection(portable(original),True),injection(portable(original/'prompt.md')),injection(portable(parent_workspace/'run-receipt.json')),injection(portable(delivery),True)]}},'prompt':{'variables':{'parent_run_id':receipt['run_id']},'template':SQ+'{% if stage == 1 %}\nset -euo pipefail\n'+verify+'\n{% else %}\nRead the complete original context and current research delivery. The parent run ID is\n{{ parent_run_id }}. Explain the recommendation in light of the ORIGINAL constraints,\nremaining uncertainty and custom work. For a lab, synthesize the independent reviews\nonly because this downstream consumer was explicitly selected. No package adoption or\nimplementation. Write {{ workspace }}/consumer.md and include the parent run ID.\n{% endif %}\n'},'validations':[{'type':'content_contains','path':'{workspace}/consumer.md','pattern':receipt['run_id'],'condition':'sheet_num == 2'},{'type':'command_succeeds','command':verify,'condition':'sheet_num == 2','retry_count':0}]}

def wrapper(parent_score, parent_workspace, child_workspace, input_dir, out_dir, resources=ROOT):
    out_dir=out_dir.resolve(); out_dir.mkdir(parents=True,exist_ok=True)
    require(parent_workspace.resolve()!=child_workspace.resolve(), 'separate consumer workspace required')
    cfg=yaml.safe_load(parent_score.read_text()); cfg['workspace']=portable(parent_workspace)
    # Resolve resource references when relocating YAML: prompt, prelude and cadenza paths
    # belong to the source bundle, not the generated wrapper's directory.
    cfg['prompt']['variables']['resources']=os.path.relpath(resources.resolve(), parent_workspace.resolve())
    cfg['prompt']['variables']['input_dir']=os.path.relpath(input_dir.resolve(), parent_workspace.resolve())
    cfg['prompt']['template']=cfg['prompt']['template'].replace("{% set resources = score_dir ~ '/..' %}\n",'')
    cfg['prompt']['template']=cfg['prompt']['template'].replace('{{ score_dir }}/..',portable(resources))
    cfg['prompt']['template']=cfg['prompt']['template'].replace('{{ sq(score_dir) }}/roster.json',shlex.quote(str((out_dir/'roster.json').resolve())))
    for items in [cfg['sheet'].get('prelude', []), *cfg['sheet']['cadenzas'].values()]:
        for item in items:
            for key in ('file','directory'):
                if key in item: item[key]=item[key].replace('{{ score_dir }}/..',portable(resources))
    roster=json.loads((parent_score.parent/'roster.json').read_text())
    (out_dir/'roster.json').write_text(json.dumps(roster,indent=2)+'\n')
    bind='python3 '+shlex.quote(str(resources.resolve()/'scripts/concert.py'))+' bind --parent-workspace '+shlex.quote(str(parent_workspace.resolve()))+' --child-workspace '+shlex.quote(str(child_workspace.resolve()))+' --out-dir '+shlex.quote(str(out_dir))+' --resources '+shlex.quote(str(resources.resolve()))
    ending='python3 {{ sq(workspace) }}/research.py deliver --workspace {{ sq(workspace) }}\n'
    require(ending in cfg['prompt']['template'],'parent must contain deterministic delivery gate')
    cfg['prompt']['template']=cfg['prompt']['template'].replace(ending,ending+bind+'\n')
    cfg['on_success']=[{'type':'run_job','job_path':'consumer.yaml','job_workspace':str(child_workspace.resolve()),'fresh':True,'detached':True}]
    # No inherited workspace; child creation only occurs after successful delivery.
    cfg['concert']={'enabled':True,'max_chain_depth':1,'inherit_workspace':False}
    (out_dir/'parent.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
    return out_dir/'parent.yaml'

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['wrapper','bind']); p.add_argument('--parent-score',type=Path); p.add_argument('--parent-workspace',type=Path,required=True); p.add_argument('--child-workspace',type=Path,required=True); p.add_argument('--input-dir',type=Path); p.add_argument('--out-dir',type=Path,required=True); p.add_argument('--resources',type=Path,default=ROOT); a=p.parse_args()
    if a.command=='wrapper': print(wrapper(a.parent_score,a.parent_workspace,a.child_workspace,a.input_dir,a.out_dir,a.resources))
    else:
        cfg=consumer(a.parent_workspace,a.child_workspace,a.resources); a.out_dir.mkdir(parents=True,exist_ok=True)
        (a.out_dir/'consumer.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
