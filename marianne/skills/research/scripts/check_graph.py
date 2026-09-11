#!/usr/bin/env python3
"""Source-bound native graph check. Does not claim a release lock or web qualification."""
import argparse
import json
from pathlib import Path
from marianne.core.config import JobConfig
from marianne.core.sheet import build_sheets
from research import ContractError, require, binding

def check(config, roster=None, original='{{ workspace }}/input-snapshot', receipt='{{ workspace }}/run-receipt.json'):
    sheets=build_sheets(config); ai=[s for s in sheets if s.instrument_name!='cli']
    for s in sheets:
        require(not s.instrument_fallbacks, f'sheet {s.num}: no fallback allowed')
        if s.instrument_name=='cli': continue
        require(any(i.directory==original and i.required and i.as_.value=='context' for i in s.cadenza), f'sheet {s.num}: required complete original directory missing')
        require(any(i.file==receipt and i.required and i.as_.value=='context' for i in s.cadenza), f'sheet {s.num}: required current receipt missing')
    if roster and config.name!='thinking-lab':
        # Movement metadata owns role names.
        search=[s for s in sheets if config.movements[s.movement].name.startswith('search-')]
        require(len(search)==len(roster['seats']), 'native fixed seat cardinality disagrees with roster')
        for s,row in zip(search,roster['seats']):
            require(s.instrument_name==row['profile'], 'resolved seat profile differs from roster')
            require(s.instrument_config.get('model','default')==row['model'], 'resolved model differs from roster')
        count=len(roster['seats']); mode='B' if config.name=='research-b' else 'A'
        require(len(ai)==count+2+(mode=='B'), 'unexpected AI call count')
        strategy=2; assignment=3; searches=list(range(4,4+count)); synth=4+count+(mode=='B')
        require(config.sheet.dependencies.get(assignment)==[strategy], 'strategy must precede assignment gate')
        for sn in searches:
            require(config.sheet.dependencies.get(sn)==[assignment], 'search must follow assignment gate')
            wanted={'{{ workspace }}/strategy.json','{{ workspace }}/assignment-search-'+str(sn-3)+'.json'}
            require(wanted <= {i.file for i in sheets[sn-1].cadenza if i.required},'search missing strategy/assignment')
        upstream={'{{ workspace }}/strategy.json'}|{'{{ workspace }}/search-'+str(i+1)+'.json' for i in range(count)}
        if mode=='B':
            require(config.sheet.dependencies.get(synth-1)==searches, 'challenge must follow all searches')
            require(upstream <= {i.file for i in sheets[synth-2].cadenza if i.required},'challenge missing all upstream')
            upstream.add('{{ workspace }}/challenge.json')
        require(config.sheet.dependencies.get(synth)==([synth-1] if mode=='B' else searches), 'synthesis dependency mismatch')
        require(upstream <= {i.file for i in sheets[synth-1].cadenza if i.required},'synthesis missing all upstream')
    return {'score':config.name,'sheets':len(sheets),'ai_calls':len(ai),'all_ai_original_context':True}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('score',type=Path); a=p.parse_args()
    roster=json.loads((a.score.parent/'roster.json').read_text())
    print(json.dumps(check(JobConfig.from_yaml(a.score),roster),indent=2))
