"""Existing natural-answer contract extracted without legacy search CLI entrypoints."""

class ContractError(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise ContractError(message)

def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f'{label}: nonempty text required')
    return value

def objects(value, label, nonempty=False):
    require(isinstance(value, list) and all(isinstance(x, dict) for x in value), f'{label}: object array required')
    require(not nonempty or bool(value), f'{label}: must not be empty')
    return value

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

def validate_answer(answer, source_ids, requirement_ids):
    require(isinstance(answer, dict), 'answer: object required')
    text(answer.get('title'), 'answer.title')
    sections = objects(answer.get('sections'), 'answer.sections', True)
    for section_index, section in enumerate(sections):
        heading = section.get('heading')
        require(isinstance(heading, str), f'answer.sections[{section_index}].heading: string required')
        require(bool(heading) or section_index == 0, 'answer: empty heading is permitted only for the opening section')
        paragraphs = section.get('paragraphs')
        require(isinstance(paragraphs, list) and bool(paragraphs), f'answer.sections[{section_index}].paragraphs: nonempty array required')
        for paragraph_index, paragraph in enumerate(paragraphs):
            statements = validate_statements(paragraph, source_ids, requirement_ids, f'answer.sections[{section_index}].paragraphs[{paragraph_index}]')
            require(all(statement['kind'] != 'requirement' for statement in statements), 'answer: requirement statements are private analysis')
    return answer
