# Marianne Score Essentials

> Needed for ALL scores. Covers the critical syntax distinction, core variables, validation engineering, config structure, YAML gotchas, common pitfalls, and the pre-flight checklist.

---

## THE CRITICAL DISTINCTION: Two Syntax Systems

Marianne uses **two different** template systems in the same YAML file. Confusing them is the #1 source of broken configs.

### Jinja2 (`{{ }}`) --- Prompt pipeline

```yaml
prompt:
  template: |
    Process sheet {{ sheet_num }} of {{ total_sheets }}.
    Write to {{ workspace }}/output-{{ sheet_num }}.md
```

- Jinja2 engine at render time
- Supports conditionals, loops, filters, macros, arithmetic
- Uses `{{ variable }}`, `{% if %}`, `{% for %}`
- `StrictUndefined` --- typos cause errors (good)

### Python format strings (`{}`) --- Validations and commands

```yaml
validations:
  - type: file_exists
    path: "{workspace}/output-{sheet_num}.md"
  - type: command_succeeds
    command: 'test -f "{workspace}/report.md"'
```

- Python `str.format()` (paths) or manual `str.replace()` (commands)
- Single braces only: `{workspace}`, `{sheet_num}`
- NO conditionals, loops, or expressions

### What goes wrong

```yaml
# WRONG --- Jinja syntax in validation path
validations:
  - type: file_exists
    path: "{{ workspace }}/output.md"
    # .format() treats {{ as literal {, producing "{ workspace }/output.md"

# CORRECT
validations:
  - type: file_exists
    path: "{workspace}/output.md"
```

```yaml
# WRONG --- format syntax in prompt template
prompt:
  template: |
    Write to {workspace}/output.md
    # Jinja ignores single braces --- rendered literally

# CORRECT
prompt:
  template: |
    Write to {{ workspace }}/output.md
```

**Rule**: Jinja `{{ }}` in the **prompt pipeline** (templates, prelude/cadenza paths, capture_files). Format `{}` in the **validation engine** (validation paths, commands, working_directory, skip_when).

| Field | Syntax | Engine |
|---|---|---|
| `prompt.template` / `prompt.template_file` | `{{ workspace }}` | Jinja2 |
| `sheet.prelude[].file` | `{{ workspace }}` | Jinja2 |
| `sheet.cadenzas[N][].file` | `{{ workspace }}` | Jinja2 |
| `cross_sheet.capture_files[]` | `{{ workspace }}` | Manual `{{ }}` replacement |
| `validations[].path` | `{workspace}` | Python `.format()` |
| `validations[].command` | `{workspace}` | Manual `{}` replacement (shell-quoted) |
| `validations[].working_directory` | `{workspace}` | Python `.format()` |
| `skip_when[N].command` | `{workspace}` | Manual `{}` replacement |

---

## Template Variables

### Core (always available in prompts)

| Variable | Type | Description |
|---|---|---|
| `sheet_num` | int | Current sheet number (1-indexed) |
| `total_sheets` | int | Total sheets in job (after fan-out expansion) |
| `start_item` | int | First item number for this sheet |
| `end_item` | int | Last item number for this sheet |
| `workspace` | str | Absolute workspace path |
| `instrument_name` | str | Name of the instrument executing this sheet (e.g., `claude-code`) |

### Validation Variables

Available in validation `path`, `command`, and `working_directory` fields:

| Variable | Available |
|---|---|
| `{workspace}` | Always |
| `{sheet_num}` | Always |
| `{start_item}` | Always |
| `{end_item}` | Always |
| `{stage}` | When fan-out configured |
| `{instance}` | When fan-out configured |

**NOT available in validations**: `job_name`, `total_sheets`, user variables, `previous_outputs`. Use `command_succeeds` for complex validation logic that needs data not in the validation context.

---

## Validation Engineering

### How Validations Actually Work

Validations run **after each sheet execution**, not at the end of the job. Each sheet independently passes or fails. The engine:

1. **Before execution**: snapshots mtimes for all `file_modified` rules
2. **After execution**: runs validations by stage, with per-rule retries
3. **Staged fail-fast**: if any stage N rule fails, stages N+1+ are skipped
4. **Path security**: all paths must resolve inside the workspace (traversal blocked)
5. **Command timeout**: `command_succeeds` has a 3600-second (1 hour) default limit
6. **Command safety**: `{workspace}` values are shell-quoted via `shlex.quote()`

### The 9 Runtime Validation Types

| Type | Checks | Path Expansion | Good For |
|---|---|---|---|
| `file_exists` | File exists and is a file | `{workspace}`, `{sheet_num}` | Basic output verification |
| `file_modified` | mtime changed since sheet started | `{workspace}`, `{sheet_num}` | Proving agent changed a file |
| `content_contains` | Literal substring in file | `{workspace}`, `{sheet_num}` | Structural markers (headings, tags) |
| `content_regex` | Python regex match in file | `{workspace}`, `{sheet_num}` | Flexible pattern matching |
| `command_succeeds` | Shell command exits 0 | `{workspace}`, `{sheet_num}` | Tests, linting, builds, complex checks |
| `path_in_scope` | Resolved path stays inside an allowed scope | `{workspace}`, `{sheet_num}` | Guarding generated paths and traversal-sensitive artifacts |
| `field_match` | JSON/YAML field equals a literal or another file field | `{workspace}`, `{sheet_num}` | Cross-artifact facts, exact status values, report facts |
| `file_sha256` | File digest matches expected SHA-256 | `{workspace}`, `{sheet_num}` | Integrity checks for inputs and generated artifacts |
| `csv_unique_key` | CSV key column has no duplicate values | `{workspace}`, `{sheet_num}` | Cumulative logs, manifests, ledgers |

### Validation Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `type` | required | --- | One of the runtime validation types |
| `path` | str | None | File path with `{workspace}`, `{sheet_num}` expansion |
| `pattern` | str | None | Literal string or regex pattern |
| `command` | str | None | Shell command (for command_succeeds) |
| `working_directory` | str | None | CWD for command (default: workspace) |
| `path_scope` | str | `{workspace}` | Allowed root for `path_in_scope` |
| `field_path` | str | None | Dot/bracket path for `field_match` |
| `expected_value` | any | None | Literal comparison value for `field_match` |
| `source_path` | str | None | Reference file for `field_match` comparisons |
| `source_field_path` | str | `field_path` | Reference field path for `field_match` |
| `sha256` | str | None | Expected digest for `file_sha256` |
| `key_field` | str | None | Unique CSV column for `csv_unique_key` |
| `description` | str | None | Human-readable name (shown in status and completion prompts) |
| `stage` | int (1-10) | 1 | Execution order; fail-fast between stages |
| `condition` | str | None | When this validation applies |
| `retry_count` | int (0-10) | 3 | Retries for race conditions |
| `retry_delay_ms` | int (0-5000) | 200 | Delay between retries |

### Static Score Checks

`mzt validate` also runs launch-time checks before a score reaches the
conductor. Current high-signal checks include:

| Code | Severity | Meaning |
|---|---|---|
| V001 | ERROR | Jinja syntax error in a prompt template |
| V002 | ERROR | Workspace parent directory missing |
| V003 | ERROR | Template file missing |
| V007 | ERROR | Invalid regex in a validation pattern |
| V008 | ERROR | Validation rule is missing required fields for its type |
| V009 | ERROR | Evolved score references stale previous-version paths |
| V305 | ERROR | Bash `${#...}` length syntax collides with Jinja comments |
| V306 | ERROR | Static `path_in_scope` check resolves outside allowed scope |
| V307 | ERROR/WARNING | Raw `cli` sheet renders invalid bash/markdown, or can fall back to non-raw instruments |
| V308 | WARNING | Fan-out movement has partial concrete instrument assignment coverage |
| V309 | WARNING | Exact section-label validation is absent from the prompt |

For raw `cli` sheets, the rendered prompt is executed as shell. Write shell,
not markdown:

```yaml
instrument: cli
prompt:
  template: |
    set -euo pipefail
    python scripts/build_report.py "{{ workspace }}/report.md"
instrument_fallbacks: []
```

If a validation requires an exact label, put that literal label in the prompt:

```yaml
prompt:
  template: |
    Write {{ workspace }}/review.md with:
    ## Verdict
    Explain whether the score is ready.
validations:
  - type: content_contains
    path: "{workspace}/review.md"
    pattern: "## Verdict"
```

For fan-out instruments, map concrete expanded sheets or use movement-level
instrument assignment when you mean the whole movement:

```yaml
movements:
  2:
    name: Review
    instrument: codex-cli
sheet:
  fan_out:
    2: 3
  dependencies:
    2: [1]
```

### Writing Good Validations

**Principles:**

1. **Every sheet needs at least one validation.** No validations = sheet always "passes" = you learn nothing.
2. **Layer coarse to fine.** Stage 1: file exists. Stage 2: structure correct. Stage 3: tests pass.
3. **Match validations to prompt instructions.** If your prompt says "write to X," validate X exists. If it says "include a summary section," validate that section.
4. **Use `command_succeeds` for real verification.** File existence proves little. Run the tests. Check the build. Lint the code.
5. **Validate outcomes, not process.** For every goal in the prompt, ask: "Can the agent pass all my validations without achieving this goal?" If yes, your validations are decorative. See the "Process validations" anti-pattern below.

### Validation Anti-Patterns

**Too weak** --- file existence alone:
```yaml
# BAD: Only checks existence, not quality
- type: file_exists
  path: "{workspace}/analysis.md"

# BETTER: Layered verification
- type: file_exists
  path: "{workspace}/analysis.md"
  stage: 1
- type: content_contains
  path: "{workspace}/analysis.md"
  pattern: "## Findings"
  stage: 2
- type: command_succeeds
  command: 'test $(wc -w < "{workspace}/analysis.md") -ge 200'
  stage: 2
  description: "Analysis has substantive content"
```

**Too broad** --- regex matches anything:
```yaml
# BAD: Matches any file with text
- type: content_regex
  pattern: ".*"

# BETTER: Specific structural check
- type: content_regex
  pattern: "(?s)## Summary.*## Recommendations"
  description: "Has both Summary and Recommendations sections"
```

**Too strict** --- exact prose matching:
```yaml
# BAD: Breaks on minor rephrasing
- type: content_contains
  pattern: "The analysis shows that the total count is 42."

# BETTER: Structural markers, not exact prose
- type: content_regex
  pattern: "(?i)(analysis|summary).*\\btotal\\b.*\\d+"
```

**Non-coding tasks**: For writing, philosophy, creative work --- file existence + structural markers (headings, word count) are your best bet. You can't validate whether a philosophical argument is *good* via regex. Use `command_succeeds` with `wc -w` for minimum substance.

**Process validations instead of outcome validations** --- the most dangerous anti-pattern because the score *looks* like it's working:

Structural validations (file exists, tests pass, imports work, lint clean) measure whether the agent *did work*. They don't measure whether the agent *achieved the goal*. Agents optimize for what's measured. If every validation can pass without the core problem being fixed, the agent will fix peripheral issues, write tests against the current (broken) behavior, produce reports declaring victory, and never touch the actual problem. The score completes. Nothing changed.

**The litmus test:** For every goal in the prompt, ask: *"Can the agent pass all my validations without achieving this goal?"* If yes, add a validation that can't.

**Example 1 --- prompt says "add pagination to the list endpoint":**
```yaml
# BAD: Agent can refactor nearby code, make tests pass, and never add pagination
- type: command_succeeds
  command: 'pytest tests/test_api.py -x -q'
- type: file_modified
  path: "{workspace}/src/api/routes.py"

# GOOD: Hit the endpoint and verify pagination actually works
- type: command_succeeds
  command: |
    cd {workspace} && python -c "
    from app.routes import app
    from app.testing import client
    resp = client(app).get('/items?page=2&per_page=5')
    data = resp.json()
    assert 'page' in data and 'total_pages' in data, 'Response missing pagination fields'
    assert len(data['items']) <= 5, 'per_page limit not enforced'
    "
  description: "Pagination endpoint returns paginated response"
```

**Example 2 --- prompt says "replace raw SQL with the ORM":**
```yaml
# BAD: Agent can fix lint, add comments, write new tests --- raw SQL still there
- type: command_succeeds
  command: 'ruff check {workspace}/src/'
- type: command_succeeds
  command: 'pytest tests/ -x -q'

# GOOD: Directly asserts the goal --- no raw SQL remains
- type: command_succeeds
  command: '! grep -rn "execute(\"SELECT\|execute(\"INSERT\|execute(\"UPDATE" {workspace}/src/'
  description: "No raw SQL queries remain in source"
```

**Example 3 --- prompt says "write a design doc comparing approach A vs B":**
```yaml
# BAD: Agent writes anything to the file and it passes
- type: file_exists
  path: "{workspace}/design.md"
- type: content_contains
  path: "{workspace}/design.md"
  pattern: "IMPLEMENTATION_COMPLETE: yes"

# GOOD: Validates the deliverable has the structure the prompt asked for
- type: content_regex
  path: "{workspace}/design.md"
  pattern: "(?si)## .*approach a.*## .*approach b"
  description: "Doc has sections for both approaches"
- type: content_regex
  path: "{workspace}/design.md"
  pattern: "(?si)(pro|advantage|strength|upside|benefit).*\\n.*(con|disadvantage|weakness|downside|drawback)"
  description: "Doc contains pros/cons comparison"
- type: command_succeeds
  command: 'test $(wc -w < "{workspace}/design.md") -ge 800'
  description: "Doc has substantive content (800+ words)"
```

### Conditional Validations

```yaml
# Supported: >=, <=, ==, !=, >, <
# Combine with "and" (no "or" --- use separate rules)
validations:
  - type: file_exists
    path: "{workspace}/01-setup.md"
    condition: "sheet_num == 1"
  - type: file_exists
    path: "{workspace}/synthesis.md"
    condition: "stage >= 3"
  - type: command_succeeds
    command: 'pytest tests/'
    condition: "stage == 2 and instance == 1"
```

### Staged Validations (Build Pipeline)

```yaml
validations:
  # Stage 1: Fast checks
  - type: command_succeeds
    command: 'ruff check {workspace}/src/'
    stage: 1
    description: "Lint passes"
  # Stage 2: Tests (only if lint passes)
  - type: command_succeeds
    command: 'cd {workspace} && pytest -x'
    stage: 2
    description: "Tests pass"
```

---

## Config Structure Reference

### Required Fields

```yaml
name: "job-name"              # Unique identifier
workspace: "./my-workspace"   # Directory for artifacts (resolved to absolute)

sheet:
  size: 5                     # Items per sheet (>= 1)
  total_items: 25             # Total work items

prompt:
  template: |                 # Inline Jinja2 template
    Your prompt here for sheet {{ sheet_num }}.
```

### Instrument

```yaml
# Use a named instrument (run `mzt instruments list` to see available)
instrument: claude-code
instrument_config:
  timeout_seconds: 1800         # Per-sheet timeout (30 min default)
  model: claude-sonnet-4-6      # Model override
```

Functional `instrument_config` keys: `model`,
`timeout_seconds`, `interactive`, `interactive_max_nudges`,
`interactive_nudge_message`. **Unknown keys are silently ignored** — old
`backend:`-era knobs like `skip_permissions`, `disable_mcp`, and
`allowed_tools` do nothing here (the built-in profiles already pass
auto-approve and MCP-disable flags; tool restrictions need a custom
profile).

Per-sheet overrides:

```yaml
sheet:
  per_sheet_instrument_config:
    7:
      timeout_seconds: 28800    # sheet 7 gets 8 hours
```

Built-in instruments: `claude-code`, `gemini-cli`, `codex-cli`, `opencode`, `goose`, `crush`, `cline-cli`, `aider`, `cli`. Plus any CLI tool via YAML profiles in `~/.marianne/instruments/`.

### Legacy `backend:` Syntax — REMOVED

The `backend:` block was removed (#347). A score containing one fails at
parse time with `Unknown field 'backend'`. Convert: `type: claude_cli` →
`instrument: claude-code`; `cli_model` → `instrument_config.model`;
`timeout_seconds` → `instrument_config.timeout_seconds`;
`timeout_overrides` → `sheet.per_sheet_instrument_config`; drop
`skip_permissions`/`disable_mcp` (handled by the instrument profile).

---

## Jinja in YAML --- Gotchas

### Always use `|` for templates

```yaml
# CORRECT --- literal block preserves newlines
prompt:
  template: |
    Line one.
    Line two.

# WRONG --- folded block collapses newlines
prompt:
  template: >
    Line one.
    Line two.
```

### Quote Jinja in YAML values

```yaml
# WRONG --- YAML parser chokes on bare {{
path: {{ workspace }}/file.md

# CORRECT --- quoted
path: "{{ workspace }}/file.md"
```

### Escape literal `{{ }}` in content

```yaml
prompt:
  template: |
    {% raw %}
    The format is: {{ variable_name }}
    {% endraw %}

    # Or: {{ '{{' }} variable_name {{ '}}' }}
```

### Double-escape regex in YAML

```yaml
# WRONG --- \d in YAML is just d
pattern: "\d+\.\s+"

# CORRECT --- double-escaped
pattern: "\\d+\\.\\s+"

# ALSO CORRECT --- single-quoted YAML (no escaping)
pattern: '\d+\.\s+'
```

### StrictUndefined catches typos

`UndefinedError` means a variable name is wrong. Common: `workshpace` (workspace), `sheetnum` (sheet_num), `totalSheets` (total_sheets).

---

## Common Pitfalls

| # | Pitfall | What Happens | Fix |
|---|---|---|---|
| 1 | `{{ }}` in validation paths | `.format()` treats `{{` as literal `{` | Use `{workspace}` not `{{ workspace }}` |
| 2 | `{}` in prompt template | Jinja ignores single braces | Use `{{ workspace }}` in templates |
| 3 | No validations | Sheet always "passes" | Always add meaningful validations |
| 4 | `file_exists` only | File may exist from previous run | Combine with `file_modified` or content checks |
| 5 | Prescriptive prompts | Agent can't adapt; brittle | Specify outcomes, not commands |
| 6 | Expecting `skip_permissions`/`disable_mcp` in `instrument_config` to do anything | Keys silently ignored | Built-in profiles already pass auto-approve + MCP-disable flags; delete the keys |
| 7 | Expecting MCP tools in a sheet | Profiles disable MCP by default (child-process explosion) | Custom profile without `mcp_disable_args`, or conductor MCP pool |
| 8 | `sheet_num` with fan-out | Changes after expansion | Use `stage` for conditionals |
| 9 | `fan_out` without `dependencies` | Stages run out of order | Always declare dependencies |
| 10 | `fan_out` without `parallel` | Sequential execution (slow) | Enable parallel for concurrency |
| 11 | Variable shadows core name | `variables.workspace` overrides real | Don't reuse: workspace, sheet_num, stage, etc. |
| 12 | `>` folded string for template | Newlines collapse | Always use `\|` literal block |
| 13 | `job_name` in template | Not a variable --- UndefinedError | Put in `prompt.variables` if needed |
| 14 | External `timeout` wrapper | SIGKILL corrupts state | Use `instrument_config.timeout_seconds` |
| 15 | No `fresh: true` in self-chain | Loads COMPLETED state, zero work | Always `fresh: true` for self-chaining |
| 16 | Regex without double-escape | `\d` in YAML is just `d` | Use `\\d` or single-quoted strings |
| 17 | Config changes after first run | Resume auto-reloads from YAML | Use `--no-reload` for cached snapshot |
| 18 | Condition with `or` | Not supported --- evaluates wrong | Use separate validation rules |
| 19 | `capture_files` uses `{}` | Capture files ARE Jinja-processed | Use `{{ workspace }}` in capture_files |
| 20 | Relative paths (workspace, `job_path`) | Resolve from daemon CWD, not score file dir | Use absolute paths everywhere — workspace, `on_success.job_path`, prelude files |
| 21 | Summary-only synthesis | Produces summaries, not insights | Ask for convergences, tensions, emergence |
| 22 | `command_succeeds` default 3600s | Full test suite outgrows timeout | Set `timeout_seconds` per-rule; see "Validation Timeouts" section |
| 23 | Integer keys in variable dicts | JSON roundtrip converts `{1: ...}` to `{"1": ...}`; Jinja2 `dict[instance]` fails because `instance` is int but key is string | Fixed in engine (auto-normalizes keys to **int** at render time). Use `dict[instance]` directly — key and variable are both int after normalization. **Do NOT use `dict[instance\|string]`**: it re-stringifies the int, missing the now-int keys → `UndefinedError` on every fan-out instance (caught by validation V304) |
| 24 | Stale detection kills verification stages | Agent runs pytest/mypy/ruff as child processes; no stdout → killed at idle_timeout | Use `idle_timeout_seconds: 1800`+, or fan-out verification into parallel instances |
| 25 | Process-only validations | Validations check file exists + tests pass + imports work, but never verify stated goals. Agent passes everything without fixing the actual problem. | For every goal in the prompt, ask: "Can the agent pass all validations without achieving this?" If yes, add one that can't. |
| 26 | Workspace = project root | `workspace_lifecycle.archive_on_fresh` archives or wipes the workspace directory. If workspace = project root, the entire project is destroyed. | NEVER set workspace to the project root. Use `./workspaces/{name}-workspace` or a dedicated absolute path. Check for `.git/`, `package.json`, `pyproject.toml` at workspace path. |
| 27 | `--fresh` when `resume` was intended | `--fresh` wipes ALL completed work and starts over. If you cancelled a score to fix config, using `--fresh` destroys all progress. | Use `mzt resume <score-id> -c fixed.yaml` to reload the YAML and continue from where you stopped. Use `--no-reload` only when you deliberately want the cached config snapshot. Only use `--fresh` for intentionally new runs. |

---

## Pre-Flight Checklist

```bash
# 1. Validate config structure
mzt validate my-score.yaml

# 2. Simulate execution (shows sheet division, rendered prompts)
mzt run my-score.yaml --dry-run

# 3. Verify:
#    - Every sheet has at least one applicable validation?
#    - Validation paths use {workspace} not {{ workspace }}?
#    - Prompt template uses {{ workspace }} not {workspace}?
#    - No backend:-era keys (skip_permissions, disable_mcp, allowed_tools)?
#    - Dependencies declared for parallel/fan-out?
#    - Timeouts appropriate for task complexity?
#    - Stale detection timeout >= 1800s for verification/build stages?
#    - Absolute workspace path?
```

### `mzt validate` Codes

| Code | Severity | Meaning |
|---|---|---|
| V001 | ERROR | Jinja syntax error in template |
| V002 | ERROR | Workspace parent missing (auto-fixable) |
| V003 | ERROR | Template file not found |
| V007 | ERROR | Invalid regex in validation pattern |
| V008 | ERROR | Validation rule is missing required fields |
| V009 | ERROR | Evolved score references stale previous-version paths |
| V101 | WARNING | Undefined template variables (false positives for `{% set %}`) |
| V103 | WARNING | Very short timeout |
| V108 | WARNING | Missing prelude/cadenza files (skips templated paths) |
| V305 | ERROR | Bash `${#...}` length syntax collides with Jinja comments |
| V306 | ERROR | `path_in_scope` resolves outside allowed scope |
| V307 | ERROR/WARNING | Raw `cli` bash is invalid/markdown, or can fall back to non-raw instruments |
| V308 | WARNING | Fan-out instrument assignment covers only part of expanded movement |
| V309 | WARNING | Prompt omits an exact section label required by validation |

---

## Mental Model: Execution Flow

1. **Config loaded** --- YAML parsed into Pydantic models; fan-out expanded
2. **State loaded** --- resume from checkpoint or start fresh
3. **For each sheet** (sequential or parallel via DAG):
   a. **Skip check** --- evaluate skip_when (command predicates)
   b. **Context built** --- SheetContext with variables + cross-sheet data
   c. **Injections resolved** --- prelude/cadenza files read
   d. **Prompt rendered** --- Jinja2 processes template
   e. **Instrument executes** --- headless CLI call, or a driven tmux session for interactive instruments (claude-code default)
   f. **Output captured** --- stdout/stderr (truncated to ~10KB)
   g. **Validations run** --- staged, conditional, with retries
   h. **On failure** --- completion mode (>50% pass) or full retry with backoff
   i. **State saved** --- checkpoint after every state change
4. **On all sheets complete** --- run `on_success` hooks

---

## Reference

- Example scores: `${CLAUDE_PLUGIN_ROOT}/docs/examples/` directory
- Fan-out gallery: [claude-compositions](https://github.com/Mzzkc/marianne-score-playspace) (7 creative scores)
- Operational guide: command skill (invoke via `/marianne:command`)

---

*Marianne Score Essentials --- extracted from the score-authoring reference.*
