#!/usr/bin/env python3
"""Research contracts and delivery. No network, provider invocation or package adoption."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse
import snapshot

class ContractError(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise ContractError(message)

def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f'{label}: nonempty text required')
    return value

def read(path):
    try:
        value = json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        raise ContractError(f'{path}: {exc}') from exc
    require(isinstance(value, dict), f'{path}: object required')
    return value

def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def objects(value, label, nonempty=False):
    require(isinstance(value, list) and all(isinstance(x, dict) for x in value), f'{label}: object array required')
    require(not nonempty or bool(value), f'{label}: must not be empty')
    return value

def indexed(value, label, nonempty=True):
    rows = objects(value, label, nonempty)
    ids = [text(x.get('id'), label + '.id') for x in rows]
    require(len(set(ids)) == len(ids), f'{label}: duplicate IDs')
    return dict(zip(ids, rows))

def refs(value, known, label, nonempty=False):
    require(isinstance(value, list) and all(isinstance(x, str) for x in value), f'{label}: string array required')
    require(len(value) == len(set(value)), f'{label}: duplicate references')
    require(not nonempty or bool(value), f'{label}: empty references')
    require(set(value) <= set(known), f'{label}: nonexistent references {set(value)-set(known)}')
    return set(value)

STATEMENT_KINDS = {'fact', 'inference', 'recommendation', 'requirement', 'proposal', 'unknown'}
CITED_STATEMENT_KINDS = {'fact', 'inference', 'recommendation'}

def validate_statement(value, source_ids, requirement_ids, label):
    require(isinstance(value, dict), f'{label}: atomic statement object required')
    kind = value.get('kind')
    require(kind in STATEMENT_KINDS, f'{label}: invalid statement kind')
    text(value.get('text'), label + '.text')
    cited = refs(value.get('source_ids'), source_ids, label + '.source_ids')
    requirements = refs(value.get('requirement_ids', []), requirement_ids, label + '.requirement_ids')
    if kind in CITED_STATEMENT_KINDS:
        require(bool(cited), f'{label}: {kind} requires source_ids')
    else:
        require(not cited, f'{label}: {kind} must not claim external sources')
    if kind == 'requirement':
        require(bool(requirements), f'{label}: requirement requires requirement_ids')
    else:
        require(not requirements, f'{label}: only requirement statements may reference requirement_ids')
    return value

def validate_statements(value, source_ids, requirement_ids, label):
    rows = value if isinstance(value, list) else [value]
    require(bool(rows), f'{label}: at least one atomic statement required')
    return [validate_statement(row, source_ids, requirement_ids, f'{label}[{index}]') for index, row in enumerate(rows)]

def validate_fit_statement(value, status, source_ids, requirement_ids, label):
    rows = validate_statements(value, source_ids, requirement_ids, label)
    if status == 'unknown':
        require(all(row['kind'] == 'unknown' for row in rows), f'{label}: unknown fit requires unknown statements')
    else:
        require(all(row['kind'] in CITED_STATEMENT_KINDS for row in rows), f'{label}: {status} fit requires cited statements')
    return rows

def render_statement(value, source_map, requirement_ids=()):
    label = value['kind'].capitalize()
    citations = citation_links(value, source_map)
    requirements = [f"[{rid}](#requirement-{rid})" for rid in value.get('requirement_ids', [])]
    links = citations + requirements
    return f"{label}: {value['text']}" + (f" ({'; '.join(links)})" if links else '')

def citation_links(value, source_map):
    rows = value if isinstance(value, list) else [value]
    return [f"[{source_map[s]['title']}]({source_map[s]['url']})" for row in rows for s in row['source_ids']]

def render_statements(value, source_map, requirement_ids=()):
    rows = value if isinstance(value, list) else [value]
    return ' '.join(render_statement(row, source_map, requirement_ids) for row in rows)

def binding(row):
    return (row['profile'], row.get('model', 'default'))

def validate_roster(roster, mode):
    seats = indexed(roster.get('seats'), 'seats')
    require(2 <= len(seats) <= 8, 'configure 2..8 fixed seats before execution')
    for sid, row in seats.items():
        require(sid == f'search-{list(seats).index(sid)+1}', 'seat IDs must be consecutive search-N')
        for key in ('profile', 'family', 'model'):
            text(row.get(key), f'{sid}.{key}')
    require(len({binding(x) for x in seats.values()}) == len(seats), 'seat routes must be distinct')
    require(len({x['family'] for x in seats.values()}) == len(seats), 'seat model families must be distinct; aliases are not evidence')
    for role in ('strategist', 'synthesizer', 'challenger'):
        row = roster.get(role)
        require(isinstance(row, dict), f'roster.{role} required')
        text(row.get('profile'), role + '.profile')
    return seats

def envelope(payload, receipt, kind):
    require(payload.get('schema_version') == 1, f'{kind}: schema_version must be 1')
    require(payload.get('kind') == kind, f'kind must be {kind}')
    require(payload.get('run_id') == receipt['run_id'], f'{kind}: stale/cross-request run_id')

def validate_strategy(strategy, receipt):
    envelope(strategy, receipt, 'research-strategy')
    reqs = indexed(strategy.get('requirements'), 'requirements')
    for rid, row in reqs.items():
        text(row.get('text'), rid)
        require(isinstance(row.get('mandatory'), bool), rid + ': mandatory boolean required')
    questions = indexed(strategy.get('questions'), 'questions')
    covered = set()
    for qid, row in questions.items():
        for key in ('text', 'evidence_goal', 'priority'):
            text(row.get(key), qid + '.' + key)
        require(isinstance(row.get('mandatory'), bool), qid + ': mandatory boolean required')
        covered |= refs(row.get('requirement_ids'), reqs, qid, True)
        require(isinstance(row.get('queries'), list) and all(isinstance(x,str) and x.strip() for x in row['queries']) and row['queries'], qid + ': query angles required')
    require({k for k,v in reqs.items() if v['mandatory']} <= covered, 'mandatory requirement lacks a question')
    seats = {x['id'] for x in receipt['roster']['seats']}
    assignments = strategy.get('assignments')
    require(isinstance(assignments, dict) and set(assignments) == seats, 'assignments must name exactly configured seats')
    owned = set()
    for sid, ids in assignments.items():
        owned |= refs(ids, questions, sid, True)
    require(set(questions) <= owned, 'question lacks an owner')
    if receipt['mode'] == 'B':
        plans = objects(strategy.get('verification_plan'), 'verification_plan', True)
        for row in plans:
            refs(row.get('question_ids'), questions, 'verification_plan', True)
            for key in ('primary_evidence', 'different_source_type', 'blind_spot'):
                text(row.get(key), key)
        require(isinstance(strategy.get('cross_component'), bool), 'B cross_component boolean required')
        if strategy['cross_component']:
            overlap = refs(strategy.get('integration_question_ids'), questions, 'integration_question_ids', True)
            for q in overlap:
                require(sum(q in ids for ids in assignments.values()) >= 2, 'integration question needs explicit corroborating owner')
    return reqs, questions

def sources(rows):
    result = indexed(rows, 'sources', False)
    for sid, row in result.items():
        url = urlparse(text(row.get('url'), sid + '.url'))
        require(url.scheme in ('http','https') and bool(url.netloc) and url.hostname not in snapshot.PLACEHOLDER_HOSTS, 'source URL must be retrievable, non-placeholder HTTP(S)')
        for key in ('title', 'accessed_at', 'supported_claim', 'source_type'):
            text(row.get(key), sid + '.' + key)
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(row['accessed_at'].replace('Z','+00:00'))
            require(dt.tzinfo is not None, 'accessed_at needs timezone')
        except ValueError as exc:
            raise ContractError('accessed_at must be an ISO datetime') from exc
    return result

def candidate_rows(rows, reqs, source_ids, prefix=None):
    result = indexed(rows, 'candidates', False)
    for cid, row in result.items():
        require(prefix is None or cid.startswith(prefix + ':'), 'candidate ID must be seat-prefixed')
        for key in ('canonical_identity', 'name'):
            text(row.get(key), cid + '.' + key)
        validate_statements(row.get('identity'), source_ids, set(reqs), cid + '.identity')
        for key in ('integration', 'remaining_custom_work'):
            validate_statements(row.get(key), source_ids, set(reqs), cid + '.' + key)
        fit = row.get('fit')
        require(isinstance(fit, dict) and set(fit) == set(reqs), cid + ': account for every requirement (unknown allowed)')
        for rid, cell in fit.items():
            require(isinstance(cell, dict) and cell.get('status') in ('supported','contradicted','unknown'), 'invalid fit cell')
            require('source_ids' not in cell, cid + '.' + rid + ': cite through reason statements, not a duplicate source_ids field')
            validate_fit_statement(cell.get('reason'), cell['status'], source_ids, set(reqs), cid + '.' + rid)
    return result

def validate_search(payload, receipt, strategy, sid):
    envelope(payload, receipt, 'research-search')
    reqs, questions = validate_strategy(strategy, receipt)
    require(payload.get('seat') == sid, 'wrong search seat')
    require(payload.get('status') in ('complete','partial','no_web'), 'invalid search status')
    evidence = sources(payload.get('sources'))
    accounts = indexed(payload.get('question_accounts'), 'question_accounts')
    require(set(accounts) == set(strategy['assignments'][sid]), 'search must account for exactly assigned questions')
    for row in accounts.values():
        require(row.get('status') in ('answered','unknown'), 'invalid question outcome')
        require('source_ids' not in row, 'question finding: cite through finding statements, not a duplicate source_ids field')
        validate_fit_statement(row.get('finding'), 'supported' if row['status']=='answered' else 'unknown', evidence, set(reqs), 'question finding')
    candidates = candidate_rows(payload.get('candidates'), reqs, evidence, sid)
    for row in accounts.values():
        refs(row.get('candidate_ids'), candidates, 'question candidate IDs')
    for key in ('scope', 'tool_evidence'):
        text(payload.get(key), key)
    require(isinstance(payload.get('queries'), list), 'queries required')
    for row in objects(payload['queries'], 'queries'):
        text(row.get('query'), 'query'); text(row.get('tool'), 'query tool')
    rejected = objects(payload.get('rejected_alternatives'), 'rejected_alternatives')
    for index, row in enumerate(rejected):
        validate_statements(row.get('statement'), evidence, set(reqs), f'rejected_alternatives[{index}]')
    require(isinstance(payload.get('uncovered_questions'), list), 'uncovered_questions array required')
    uncovered=refs(payload['uncovered_questions'], questions, 'uncovered_questions')
    require({k for k,v in accounts.items() if v['status']=='unknown'} <= uncovered, 'unknown accounts must appear in uncovered_questions')
    if payload['status'] == 'no_web':
        require(not candidates and not evidence and all(x['status']=='unknown' for x in accounts.values()), 'no_web cannot carry verified claims')
    else:
        require(bool(payload['queries']), 'actual search queries required')
    if payload['status'] != 'complete':
        validate_statements(payload.get('reason'), evidence, set(reqs), 'partial/no_web reason')
    return candidates

def discoveries(workspace, receipt, strategy):
    joined = {}; reports = []
    for row in receipt['roster']['seats']:
        sid = row['id']; payload = read(workspace / (sid + '.json'))
        joined.update(validate_search(payload, receipt, strategy, sid))
        reports.append(payload)
    return joined, reports

def validate_challenge(payload, receipt, strategy, candidates):
    envelope(payload, receipt, 'research-challenge')
    require(payload.get('status') in ('complete','partial','no_web'), 'invalid challenge status')
    evidence = sources(payload.get('sources'))
    new = candidate_rows(payload.get('new_candidates'), {x['id']:x for x in strategy['requirements']}, evidence, 'challenge')
    require(not set(new)&set(candidates), 'duplicate challenge candidate')
    targets = indexed(payload.get('targets'), 'targets', False)
    require(len(targets) <= 3, 'challenge limited to three targets')
    for row in targets.values():
        refs(row.get('question_ids'), {x['id'] for x in strategy['questions']}, 'target questions', True)
        refs(row.get('candidate_ids'), set(candidates)|set(new), 'target candidates')
        require(row.get('disposition') in ('confirmed','corrected','unresolved'), 'target disposition required')
        refs(row.get('source_ids'), evidence, 'target evidence', row['disposition'] != 'unresolved')
        for key in ('reason', 'decision_consequence', 'source_type_rationale'):
            validate_statements(row.get(key), evidence, {x['id'] for x in strategy['requirements']}, key)
    validate_statements(payload.get('summary'), evidence, {x['id'] for x in strategy['requirements']}, 'challenge summary/no-targets reason')
    if payload['status'] != 'complete':
        validate_statements(payload.get('reason'), evidence, {x['id'] for x in strategy['requirements']}, 'challenge partial reason')
    if payload['status'] == 'no_web':
        require(not evidence and not new and all(t['disposition']=='unresolved' for t in targets.values()), 'no_web challenge claims forbidden')
    require(all(any(cid in t['candidate_ids'] for t in targets.values()) for cid in new), 'new candidate needs bounded target')
    return new

def validate_synthesis(payload, receipt, strategy, candidates, reports, challenge=None):
    envelope(payload, receipt, 'research-synthesis')
    require(payload.get('status') in ('complete','partial'), 'invalid synthesis status')
    require(payload.get('recommendation') in ('reuse','adapt','build','undetermined'), 'invalid recommendation')
    reqs = {x['id']: x for x in strategy['requirements']}
    all_sources = {r['seat']+':'+s['id'] for r in reports for s in r['sources']}
    if challenge:
        all_sources |= {'challenge:'+s['id'] for s in challenge['sources']}
    for key in ('summary','ranking_rationale','strongest_alternative','remaining_custom_work'):
        validate_statements(payload.get(key), all_sources, reqs, key)
    approaches = indexed(payload.get('ranked_approaches'), 'ranked_approaches', False)
    for row in approaches.values():
        refs(row.get('candidate_ids'), candidates, 'approach candidate references', True)
        for key in ('rationale','counterarguments','integration','remaining_custom_work'):
            validate_statements(row.get(key), all_sources, reqs, key)
        require(isinstance(row.get('constraint_matrix'), dict) and set(row['constraint_matrix']) == set(reqs), 'approach must cover every requirement')
        for cell in row['constraint_matrix'].values():
            require(isinstance(cell,dict) and cell.get('status') in ('supported','contradicted','unknown'), 'invalid matrix fit')
            require('source_ids' not in cell, 'matrix reason: cite through reason statements, not a duplicate source_ids field')
            validate_fit_statement(cell.get('reason'), cell['status'], all_sources, reqs, 'matrix reason')
    require(bool(approaches) or payload['recommendation']=='undetermined', 'no ranked evidence requires undetermined recommendation')
    gaps = objects(payload.get('unresolved_gaps'), 'unresolved_gaps')
    for index, row in enumerate(gaps):
        statements = validate_statements(row, all_sources, reqs, f'unresolved_gaps[{index}]')
        require(all(statement['kind'] == 'unknown' for statement in statements), 'unresolved gaps must be unknown statements')
    require(isinstance(payload.get('contradictions'),list), 'contradictions required')
    for row in objects(payload['contradictions'], 'contradictions'):
        validate_statements(row.get('claim'), all_sources, reqs, 'contradiction claim')
        validate_statements(row.get('resolution'), all_sources, reqs, 'contradiction resolution/condition')
        refs(row.get('candidate_ids'), candidates, 'contradiction candidates', True)
    if challenge is not None:
        require(payload.get('challenge_effect') in ('eligibility','ranking','confidence','none','unresolved'), 'B incremental effect required')
        dispositions = payload.get('challenge_dispositions')
        require(isinstance(dispositions,dict) and set(dispositions)=={x['id'] for x in challenge['targets']}, 'dispose every challenge target')
        for target, val in dispositions.items():
            validate_statements(val, all_sources, reqs, f'synthesis target resolution {target}')
    if any(x['status'] != 'complete' for x in reports) or (challenge and challenge['status']!='complete'):
        require(payload['status']=='partial', 'incomplete coverage cannot be complete synthesis')

def current(workspace):
    receipt = read(workspace / 'run-receipt.json')
    require(receipt.get('kind') == 'research-run-receipt' and receipt.get('schema_version')==1, 'current typed receipt required')
    snapshot_dir = workspace / 'input-snapshot'
    require(snapshot_dir.is_dir(), 'missing original directory')
    expected = {x['name']:x['sha256'] for x in receipt['files']}
    require({p.name for p in snapshot_dir.iterdir()} == set(expected), 'snapshot membership changed')
    require(all((snapshot_dir/n).is_file() and digest(snapshot_dir/n)==h for n,h in expected.items()), 'original context digest changed')
    validate_roster(receipt['roster'],receipt['mode'])
    return receipt

def prepare(workspace, input_dir, roster, mode, max_bytes=262144):
    validate_roster(roster, mode)
    workspace.mkdir(parents=True, exist_ok=True)
    snapshot.cmd_prepare(argparse.Namespace(input_dir=str(input_dir), workspace=str(workspace), max_bytes=max_bytes))
    # Invalidate all current outputs before any performer; historical archives are outside delivery.
    for pat in ('strategy.json','assignment-*.json','search-*.json','challenge.json','synthesis.json','synthesis.md','review-*.md','review-*.json'):
        for p in workspace.glob(pat): p.unlink()
    if (workspace/'delivery').exists(): shutil.rmtree(workspace/'delivery')
    receipt = read(workspace/'run-receipt.json')
    receipt.update(kind='research-run-receipt', mode=mode, roster=roster)
    write(workspace/'run-receipt.json',receipt)
    write(workspace/'status.json', {'kind':'research-status','schema_version':1,'run_id':receipt['run_id'],'status':'partial','reason':'required research stages not yet validated'})
    return receipt

def validate_file(workspace, role):
    receipt = current(workspace)
    if role.startswith('review-'):
        value=read(workspace/(role+'.json')); envelope(value,receipt,'research-review')
        require(value.get('review')==role, 'wrong review identity')
        body=workspace/(role+'.md'); require(body.is_file() and body.read_text().strip(), 'nonempty independent review required')
        require(value.get('sha256')==digest(body), 'review receipt must hash current review')
        return value
    strategy = read(workspace/'strategy.json'); envelope(strategy, receipt, 'research-strategy')
    validate_strategy(strategy,receipt)
    if role == 'strategy': return strategy
    if role.startswith('search-'):
        assignment=read(workspace/('assignment-'+role+'.json'))
        envelope(assignment,receipt,'research-assignment')
        require(assignment.get('seat')==role and assignment.get('question_ids')==strategy['assignments'][role] and assignment.get('strategy_sha256')==digest(workspace/'strategy.json'),'stale/changed assignment')
        return validate_search(read(workspace/(role+'.json')),receipt,strategy,role)
    candidates,reports=discoveries(workspace,receipt,strategy)
    challenge=None
    if receipt['mode']=='B':
        challenge=read(workspace/'challenge.json')
        candidates.update(validate_challenge(challenge,receipt,strategy,candidates))
    if role=='challenge': return challenge
    result=read(workspace/'synthesis.json')
    validate_synthesis(result,receipt,strategy,candidates,reports,challenge)
    return result

def assignments(workspace):
    strategy=validate_file(workspace,'strategy'); receipt=current(workspace)
    for sid,ids in strategy['assignments'].items():
        write(workspace/('assignment-'+sid+'.json'),{'schema_version':1,'kind':'research-assignment','run_id':receipt['run_id'],'seat':sid,'question_ids':ids,'strategy_sha256':digest(workspace/'strategy.json')})

def source_map(reports, challenge=None):
    result = {r['seat']+':'+s['id']:s for r in reports for s in r['sources']}
    if challenge:
        result.update({'challenge:'+s['id']:s for s in challenge['sources']})
    return result

def markdown(result, strategy, candidates, reports, challenge=None):
    evidence = source_map(reports, challenge)
    requirement_ids = {row['id'] for row in strategy['requirements']}
    local_evidence = {report['seat']:{source['id']:source for source in report['sources']} for report in reports}
    if challenge:
        local_evidence['challenge'] = {source['id']:source for source in challenge['sources']}
    lines=['# Research decision', '', render_statements(result['summary'], evidence), '', '**Recommendation:** '+result['recommendation'], '', render_statements(result['ranking_rationale'], evidence)]
    lines += ['', '## Requirements']
    for row in strategy['requirements']:
        classification = 'Mandatory' if row['mandatory'] else 'Preference'
        lines += ['', f"### <a id=\"requirement-{row['id']}\"></a>{row['id']} — {classification}", 'Original requirement: '+row['text']]
    lines += ['', '## Candidate identities']
    for cid, row in candidates.items():
        identity_sources = '; '.join(citation_links(row['identity'], local_evidence[cid.split(':', 1)[0]]))
        lines += ['', f"### {cid}", 'Name: '+row['name']+f' ({identity_sources})', '', 'Canonical identity: '+row['canonical_identity']+f' ({identity_sources})']
    lines += ['', '## Search findings']
    for report in reports:
        lines += ['', f"### {report['seat']}"]
        for account in report['question_accounts']:
            lines += [f"- {account['id']}: {render_statements(account['finding'], local_evidence[report['seat']])}"]
    if challenge:
        lines += ['', '## Challenge findings', render_statements(challenge['summary'], local_evidence['challenge'])]
        for target in challenge['targets']:
            lines += [f"- {target['id']}: {render_statements(target['reason'], local_evidence['challenge'])}", f"  Consequence: {render_statements(target['decision_consequence'], local_evidence['challenge'])}"]
    for rank,row in enumerate(result['ranked_approaches'],1):
        lines += ['', f"## {rank}. {row['id']}", render_statements(row['rationale'], evidence), '', 'Candidates: '+', '.join(row['candidate_ids']), '', render_statements(row['integration'], evidence), '', 'Counterarguments: '+render_statements(row['counterarguments'], evidence), '', 'Remaining custom work: '+render_statements(row['remaining_custom_work'], evidence), '', '| Requirement | Fit | Evidence / reason |','|---|---|---|']
        for rid,cell in row['constraint_matrix'].items(): lines += [f"| {rid} | {cell['status']} | {render_statements(cell['reason'], evidence)} |"]
    lines += ['', '## Strongest alternative', render_statements(result['strongest_alternative'], evidence), '', '## Remaining custom work', render_statements(result['remaining_custom_work'], evidence), '', '## Unresolved gaps'] + ['- '+render_statements(x, evidence) for x in result['unresolved_gaps']]
    lines += ['', '## Contradictions']
    for row in result['contradictions']:
        lines += ['- Claim: '+render_statements(row['claim'], evidence), '  Resolution: '+render_statements(row['resolution'], evidence)]
    if 'challenge_effect' in result:
        lines += ['', '## Verification effect', result['challenge_effect']]
        for target, disposition in result['challenge_dispositions'].items():
            lines += [f"- {target}: {render_statements(disposition, evidence, requirement_ids)}"]
    return '\n'.join(lines)+'\n'

def deliver(workspace):
    receipt=current(workspace); mode=receipt['mode']; status='partial'; reason=''; result=None; strategy_for_delivery=None
    try:
        if mode=='lab':
            reviews=[f'review-{i+1}' for i in range(len(receipt['roster']['seats']))]
            for role in reviews: validate_file(workspace,role)
            report='# Independent reviews — caller owns synthesis\n\n'+'\n\n'.join((workspace/(r+'.md')).read_text() for r in reviews)
            result={'schema_version':1,'kind':'research-lab-result','run_id':receipt['run_id'],'status':'complete','reviews':reviews,'synthesis':'caller-owned'}
        else:
            result=validate_file(workspace,'synthesis')
            strategy_for_delivery=validate_file(workspace,'strategy')
            candidates, reports=discoveries(workspace,receipt,strategy_for_delivery)
            if mode=='B':
                candidates.update(validate_challenge(read(workspace/'challenge.json'),receipt,strategy_for_delivery,candidates))
            report=markdown(result,strategy_for_delivery,candidates,reports,read(workspace/'challenge.json') if mode=='B' else None)
            for row in receipt['roster']['seats']:
                p=read(workspace/(row['id']+'.json'))
                report+='\n## Sources: '+row['id']+'\n'+''.join(f"- {s['id']}: [{s['title']}]({s['url']}) — {s['supported_claim']} ({s['accessed_at']})\n" for s in p['sources'])
            if mode=='B':
                p=read(workspace/'challenge.json')
                report+='\n## Challenge sources\n'+''.join(f"- {s['id']}: [{s['title']}]({s['url']}) — {s['supported_claim']}\n" for s in p['sources'])
            (workspace/'synthesis.md').write_text(report)
        status=result['status']; reason='validated' if status=='complete' else 'incomplete required coverage'
    except (ContractError,OSError) as exc:
        strategy_for_delivery=None
        reason=str(exc); report='# Partial research\n\n'+reason+'\n\nUseful lane artifacts remain in the run workspace.\n'
        result={'schema_version':1,'kind':'research-partial','run_id':receipt['run_id'],'status':'partial','reason':reason}
    # Encode original names injectively; originals themselves remain byte/name-exact in input-snapshot.
    delivery=workspace/'delivery'
    if delivery.exists(): shutil.rmtree(delivery)
    delivery.mkdir()
    originals=[]
    for i,row in enumerate(receipt['files'],1):
        name=f'original-{i:04d}.txt'; shutil.copyfile(workspace/'input-snapshot'/row['name'],delivery/name)
        originals.append({**row,'delivery_name':name})
    (delivery/'report.md').write_text(report); write(delivery/'result.json',result)
    write(delivery/'run-receipt.json',receipt)
    artifact_names=['report.md','result.json','run-receipt.json']
    if strategy_for_delivery is not None:
        shutil.copyfile(workspace/'strategy.json',delivery/'strategy.json')
        artifact_names.append('strategy.json')
    manifest={'schema_version':1,'kind':'research-delivery','run_id':receipt['run_id'],'input_sha256':receipt['input_sha256'],'status':status,'reason':reason,'original_directory':str((workspace/'input-snapshot').resolve()),'originals':originals,'artifacts':{n:digest(delivery/n) for n in artifact_names}}
    write(delivery/'status.json',manifest); write(workspace/'status.json',manifest)
    return 0 if status=='complete' else 4

def verify_delivery(delivery, original_dir, expected_run_id):
    manifest=read(delivery/'status.json'); require(manifest.get('schema_version')==1 and manifest.get('kind')=='research-delivery' and manifest.get('status')=='complete','successful typed delivery required')
    require(manifest.get('run_id')==expected_run_id, 'stale parent delivery')
    active=current(original_dir.parent)
    expected_artifacts={'report.md','result.json','run-receipt.json'}
    if active['mode'] != 'lab': expected_artifacts.add('strategy.json')
    require(isinstance(manifest.get('artifacts'),dict) and set(manifest['artifacts'])==expected_artifacts, 'complete delivery artifact digest set required')
    require(active['run_id']==expected_run_id, 'parent current receipt differs from bound run')
    require({p.name for p in original_dir.iterdir()} == {x['name'] for x in manifest['originals']}, 'extra/missing original context files')
    receipt=read(delivery/'run-receipt.json'); require(receipt==active, 'transport receipt differs from current parent receipt')
    require(receipt['run_id']==expected_run_id and receipt['input_sha256']==manifest['input_sha256'],'receipt join failed')
    require(Path(manifest['original_directory']).resolve()==original_dir.resolve(),'wrong original directory binding')
    require({x['name']:x['sha256'] for x in manifest['originals']}=={x['name']:x['sha256'] for x in receipt['files']}, 'parent manifest originals mismatch')
    for row in manifest['originals']:
        require(Path(row['name']).name==row['name'] and Path(row['delivery_name']).name==row['delivery_name'], 'unsafe manifest filename')
        require(digest(original_dir/row['name'])==row['sha256']==digest(delivery/row['delivery_name']), 'original delivery hash mismatch')
    for name, sha in manifest['artifacts'].items():
        require(Path(name).name==name and digest(delivery/name)==sha,'delivery artifact digest mismatch')
    result=read(delivery/'result.json')
    envelope(result,receipt,'research-lab-result' if receipt['mode']=='lab' else 'research-synthesis')
    require(result.get('status')=='complete','consumer requires complete typed result')
    if receipt['mode'] != 'lab':
        validate_strategy(read(delivery/'strategy.json'),receipt)
    return manifest

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['prepare','assignments','validate','deliver','verify-delivery']); p.add_argument('--workspace',type=Path); p.add_argument('--input-dir'); p.add_argument('--roster',type=Path); p.add_argument('--mode',choices=['A','B','lab']); p.add_argument('--max-bytes',type=int,default=262144); p.add_argument('--role'); p.add_argument('--delivery',type=Path); p.add_argument('--original-dir',type=Path); p.add_argument('--run-id')
    a=p.parse_args(argv)
    try:
        if a.command=='prepare': prepare(a.workspace,a.input_dir,read(a.roster),a.mode,a.max_bytes)
        elif a.command=='assignments': assignments(a.workspace)
        elif a.command=='validate': validate_file(a.workspace,a.role)
        elif a.command=='deliver': return deliver(a.workspace)
        else: verify_delivery(a.delivery,a.original_dir,a.run_id)
        return 0
    except (ContractError,snapshot.InputError,snapshot.ReportError,OSError,TypeError,KeyError) as exc:
        print('research: '+str(exc),file=sys.stderr); return 3

if __name__=='__main__': sys.exit(main())
