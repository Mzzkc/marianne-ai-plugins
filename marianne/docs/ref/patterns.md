# Marianne Score Patterns

> Fan-out, synthesis, multi-stage design, Jinja mastery, and prompt engineering. Load this alongside essentials.md for tier 2+ scores.

---

## Score Design Philosophy

Five principles from real-world score composition.

### 1. Scores Are Programs for Minds, Not Machines

A shell script tells bash exactly what to do. A score tells a mind what to *accomplish*. Be clear about outcomes, flexible about methods. The agent reasons, plans, and adapts --- your job is to describe the destination, not the route.

### 2. Fan-Out Is Parallel Cognition

When you fan out a stage, you're creating multiple independent perspectives, not running the same thing faster. The synthesis stage is where emergence happens --- independent outputs collide, contradict, and combine into something none of them could reach alone. Convergence from isolation is real; convergence from coordination is manufactured.

### 3. Data in Variables, Logic in Templates

`prompt.variables` is your data layer --- guest lists, review criteria, stage definitions, difficulty levels. The template is logic that processes that data. When the data changes (new guests, different criteria), the template doesn't change. This separation makes scores reusable and maintainable.

### 4. Macros Are Your House Style

Encode standards as macros --- output format, quality criteria, citation conventions. New stages inherit standards automatically. Update in one place.

### 5. The Workspace Is Shared Memory

Files in `{{ workspace }}` are how stages communicate beyond `previous_outputs`. Write structured output (markdown with consistent headers, JSON) so downstream stages can parse reliably. The workspace is the score's memory; treat it like a schema.

---

## Template Variables (Fan-Out, Cross-Sheet, Injection, User)

### Fan-Out (when `sheet.fan_out` configured)

| Variable | Alias | Type | Description |
|---|---|---|---|
| `stage` | `movement` | int | Logical stage (1-indexed, stable across expansion) |
| `instance` | `voice` | int | Instance within fan-out group (1-indexed) |
| `fan_count` | `voice_count` | int | Total instances in this stage's fan-out |
| `total_stages` | `total_movements` | int | Pre-expansion stage count |

The aliases `movement`, `voice`, `voice_count`, and `total_movements` follow Marianne's orchestral vocabulary. Both forms work — use whichever reads better in your score.

Without fan-out: `stage` = `sheet_num`, `total_stages` = `total_sheets`, `instance` = 1, `fan_count` = 1.

### Cross-Sheet (when `cross_sheet` configured)

| Variable | Type | Description |
|---|---|---|
| `previous_outputs` | dict[int, str] | Stdout from previous sheets, keyed by sheet_num |
| `previous_files` | dict[str, str] | Captured file contents, keyed by file path |

### Injection (when preludes/cadenzas configured)

| Variable | Type | Description |
|---|---|---|
| `injected_context` | list[str] | Content from `context` category injections |
| `injected_skills` | list[str] | Content from `skill` category injections |
| `injected_tools` | list[str] | Content from `tool` category injections |

### User Variables (from `prompt.variables`)

Any key defined in `prompt.variables` is available directly. **Warning**: user variables that shadow core variables (`sheet_num`, `workspace`, `stage`, etc.) will OVERRIDE them. Don't reuse core variable names.

---

## Jinja Mastery

Progressive techniques from basic to advanced. Every Marianne score uses these.

### Conditionals: The Multi-Stage Backbone

```yaml
prompt:
  template: |
    {% if stage == 1 %}
    Research the topic. Write to {{ workspace }}/01-research.md
    {% elif stage == 2 %}
    Analyze the research. Write to {{ workspace }}/02-analysis.md
    {% elif stage == 3 %}
    Synthesize findings. Write to {{ workspace }}/03-synthesis.md
    {% endif %}
```

**Nested conditionals** for fan-out specialization:

```yaml
prompt:
  variables:
    perspectives:
      1: "economic"
      2: "environmental"
      3: "social"
  template: |
    {% if stage == 2 %}
    Analyze from the {{ perspectives[instance] }} perspective.
    {% if instance == 1 %}
    Focus on costs, ROI, market dynamics.
    {% elif instance == 2 %}
    Focus on ecological impact, sustainability.
    {% elif instance == 3 %}
    Focus on equity, access, community effects.
    {% endif %}
    {% endif %}
```

### Data Structures as Fan-Out Specifications

The most powerful pattern: lookup dictionaries that drive per-instance behavior.

```yaml
prompt:
  variables:
    lenses:
      1:
        name: "historian"
        voice: "You are a historian. Ground everything in precedent."
        focus: "How did we get here? What patterns recur?"
      2:
        name: "engineer"
        voice: "You are a systems thinker. Focus on mechanisms."
        focus: "What are the moving parts? Where are leverage points?"
      3:
        name: "skeptic"
        voice: "You are a skeptic. Challenge every assumption."
        focus: "What are we wrong about?"
  template: |
    {% if stage == 2 %}
    {{ lenses[instance].voice }}
    Your focus: {{ lenses[instance].focus }}
    Save to {{ workspace }}/02-{{ lenses[instance].name }}.md
    {% endif %}
```

Change the data, the prompts change. Template logic unchanged.

### Loops, Filters, and Ranges

```yaml
prompt:
  template: |
    {# List iteration with loop helpers #}
    {% for check in checkpoints %}
    {{ loop.index }}. {{ check }}{% if loop.last %} (CRITICAL){% endif %}
    {% endfor %}

    {# Dict iteration for cross-sheet context #}
    {% for key, output in previous_outputs.items() %}
    --- Stage {{ key }} ---
    {{ output | truncate(1500) }}
    {% endfor %}

    {# Range-based loop for fan-out references #}
    {% for i in range(1, fan_count + 1) %}
    - {{ workspace }}/02-review-{{ i }}.md
    {% endfor %}

    {# Filter chains #}
    Guest list: {{ guests | map(attribute="name") | sort | join(", ") }}

    {# Ternary expressions #}
    {{ "FINAL STAGE" if stage == total_stages else "Intermediate stage" }}
```

Useful filters: `truncate(n)`, `default(val)`, `join(sep)`, `sort`, `unique`, `map(attribute=x)`, `length`, `round`, `upper`/`lower`/`title`, `replace(old, new)`, `trim`, `wordcount`.

String concatenation uses `~`: `"file-" ~ lens.name ~ ".md"`.

### Macros: Reusable Prompt Blocks

```yaml
prompt:
  template: |
    {% macro output_spec(filename, format="markdown") %}
    ## Output Specification
    - **File**: {{ workspace }}/{{ filename }}
    - **Format**: {{ format }}
    - Ensure the file is complete and well-structured
    {% endmacro %}

    {% macro quality_bar(level="standard") %}
    {% if level == "high" %}
    Triple-check accuracy. Cite sources. No hedging.
    {% elif level == "draft" %}
    Prioritize coverage over polish. Mark uncertainties with [?].
    {% endif %}
    {% endmacro %}

    {% if stage == 1 %}
    Research the topic.
    {{ output_spec("01-research.md") }}
    {{ quality_bar("draft") }}
    {% elif stage == 2 %}
    Write the final analysis.
    {{ output_spec("02-analysis.md", "structured report") }}
    {{ quality_bar("high") }}
    {% endif %}
```

Define once, use everywhere. When you add a new stage, compose from existing blocks.

### Template Limitations

1. **No `{% include %}` or `{% extends %}`** --- templates loaded via `from_string()`, no filesystem loader
2. **No side effects** --- Jinja2 is rendering-only; the agent reads files and runs commands
3. **No dynamic fan-out** --- `fan_out:` is YAML config, evaluated before templates render
4. **V101 false positives** --- `{% set var = value %}` triggers undefined variable warnings; ignore them

---

## Fan-Out Patterns

Fan-out is structured pluralism. Seven patterns have emerged from real scores.

| Pattern | What It Does | When to Use |
|---|---|---|
| **Adversarial** | Independent critiques of same position | Hard questions with genuine tension |
| **Perspectival** | Same question, different analytical frameworks | Multi-domain analysis (TDF-style) |
| **Functional** | Same goal, different planning domains | Event planning, project management |
| **Graduated** | Same content, different difficulty levels | Education, progressive curricula |
| **Generative** | Same seed, different creative lenses | Worldbuilding, creative exploration |
| **Mosaic** | Same world, different stories/viewpoints | Fiction collections, case studies |
| **Translational** | Same source, different representational modes | Meaning analysis, cross-disciplinary |
| **Expert** | Same codebase, different review specializations | Code quality, security audits |

### Architecture

All fan-out scores follow the same 3-4 stage shape:

```
Stage 1: Setup/Framing (1 sheet)
    ├── Stage 2: Fan-out instances (N parallel sheets)
    └── Stage 3: Synthesis (1 sheet, waits for all N)
        └── Stage 4: (optional) Final position / compilation
```

```yaml
sheet:
  size: 1
  total_items: 3          # or 4 if final stage included
  fan_out:
    2: N                   # N parallel instances
  dependencies:
    2: [1]                 # Fan-out depends on setup
    3: [2]                 # Synthesis depends on ALL instances (fan-in)

parallel:
  enabled: true
  max_concurrent: N
```

### Writing Synthesis Prompts

The synthesis stage is the hardest to write and the most important. It must do three things:

1. **Find rhymes** --- where did independent outputs converge without coordination?
2. **Resolve conflicts** --- where do they disagree? Find readings that make BOTH true.
3. **Discover emergence** --- what questions/patterns appeared from the collision that weren't in any single input?

```yaml
# BAD: Just asks for summary
template: |
  Summarize the expert reviews.

# GOOD: Asks for emergence
template: |
  Read all expert reviews. Your task is NOT to summarize.

  Find:
  1. **Convergences** --- Where did independent reviewers reach the same conclusion?
     This is signal. It wasn't coordinated.
  2. **Tensions** --- Where do they disagree? Don't resolve by averaging.
     Find a reading that makes both positions true.
  3. **Gaps** --- What did nobody address? The blind spots are the most interesting.
  4. **Emergence** --- What insight exists in the collision of perspectives
     that no single reviewer stated?

  Take a position. Don't hedge.
```

### Integer Keys in Instance-Lookup Dicts

When using `variables` dicts keyed by instance number (common in fan-out), the engine automatically normalizes string keys to integers. This handles the JSON roundtrip issue (resume path converts `{1: ...}` to `{"1": ...}`). Both forms work:

```yaml
# Both work — engine normalizes on render
investigation_focus:
  1:
    name: "Bug Scan"    # YAML loads as int key 1
  2:
    name: "Architecture" # Template: focus_map[instance] works

# Template access:
# {% set focus = investigation_focus[instance] %}  ← works with both key types
```

### Design for Independence

Parallel instances DON'T see each other. That's the mechanism, not a limitation. Real convergence requires isolation. If instances could coordinate, the convergence would be manufactured.

### Shared Interfaces Need Upstream Contracts

When parallel instances build components that must integrate (e.g., a client and a server, a CLI and a library, a UI and an API), each instance will independently invent its own interface. Three agents, three different function signatures. The synthesis/integration stage finds the mess, but by then the work is done wrong.

**Fix:** Define shared interfaces in an upstream stage (plan or setup) and reference them from parallel instances. If stage 2 instances must agree on an API, stage 1 must specify it.

## Per-Sheet Instruments

Assign different instruments to different sheets. Useful for cost optimization (cheap instruments for simple work, expensive for complex) or multi-vendor workflows.

### Per-Sheet Assignment

```yaml
instrument: claude-code          # Default for all sheets

sheet:
  per_sheet_instruments:
    1: gemini-cli                # Sheet 1 uses Gemini
    5: claude-code               # Sheet 5 uses Claude (same as default)
  per_sheet_instrument_config:
    1:
      timeout_seconds: 600
```

### Batch Assignment via instrument_map

```yaml
sheet:
  instrument_map:
    gemini-cli: [1, 2, 3]       # Cheap sweeps
    claude-code: [4, 5]          # Deep analysis
```

### Movement-Level Instruments

```yaml
movements:
  1:
    name: "Research"
    instrument: gemini-cli       # All sheets in movement 1
  2:
    name: "Analysis"
    instrument: claude-code      # All sheets in movement 2
```

Resolution order: per-sheet → movement → score-level default.

---

## Prompt Engineering

### The Cardinal Rule: Outcomes, Not Methods

Marianne orchestrates **general-purpose AI agents**. They reason, plan, and execute. Your prompt defines what success looks like, not the keystrokes to get there.

```yaml
# BAD: Micromanaging the agent
prompt:
  template: |
    Run these commands in order:
    1. cd {{ workspace }}
    2. git checkout -b fix-bug
    3. Open src/main.py
    4. Find line 42 and change "foo" to "bar"
    5. Run pytest
    6. git commit -m "fix: change foo to bar"

# GOOD: Outcome-focused
prompt:
  template: |
    Fix the bug where `foo` should be `bar` in src/main.py.

    Requirements:
    - The fix must pass all existing tests
    - Commit with a conventional commit message
    - Work in {{ workspace }}
```

**Why prescriptive prompts fail**: fragility (steps don't match reality), lost agency (agent can't adapt), context waste (agent already knows its tools), version coupling (commands break as tools evolve).

### What to Include

1. **Goal** --- what should be different when this sheet completes?
2. **Context** --- what does the agent need to know about the project/domain?
3. **Constraints** --- what must be true about the output? (Mirror your validations.)
4. **Output specification** --- where should artifacts be written? What format?
5. **Quality criteria** --- what separates good from mediocre?

### Tell the Agent About Validations

Marianne automatically injects validation rules into prompts, but being explicit in the template helps the agent aim:

```yaml
prompt:
  template: |
    Write analysis to {{ workspace }}/analysis.md.

    Your output MUST include:
    - A "## Findings" section (validated)
    - At least 3 numbered findings (validated)
    - A "## Recommendations" section (validated)

validations:
  - type: content_contains
    path: "{workspace}/analysis.md"
    pattern: "## Findings"
  - type: content_regex
    path: "{workspace}/analysis.md"
    pattern: "\\d+\\.\\s+\\w+"
  - type: content_contains
    path: "{workspace}/analysis.md"
    pattern: "## Recommendations"
```

---

## Config: Cross-Sheet, Prelude/Cadenza, Parallel, Skip Conditions

### Cross-Sheet Context

```yaml
cross_sheet:
  auto_capture_stdout: true
  max_output_chars: 2000        # Per-sheet truncation
  lookback_sheets: 3            # 0 = all previous
  capture_files:                # Jinja syntax (prompt pipeline)
    - "{{ workspace }}/sheet-{{ sheet_num - 1 }}-result.md"
```

### Prelude & Cadenza

Inject content into a sheet's prompt context. Choose **file** for one specific artifact, **directory** for a whole input bucket.

```yaml
sheet:
  prelude:                              # Injected into ALL sheets
    - file: "{{ workspace }}/shared-context.md"
      as: context                       # After template body
    - file: "{{ workspace }}/coding-standards.md"
      as: skill                         # Before template body
  cadenzas:                             # Per-sheet injections
    1:
      - file: "{{ workspace }}/setup.md"
        as: skill
    2:
      - directory: "/abs/path/to/inputs"   # ← directory cadenza
        as: context
```

Categories: `context` (background, after body), `skill` (methodology, before body), `tool` (actions, before body).

#### File vs. directory injection

Each `InjectionItem` has exactly one of `file:` or `directory:`. Setting both is a config error; setting neither is also an error.

- **`file:`** — inject one file's content. Path supports Jinja templating against the score's variables.
- **`directory:`** — glob the directory's files and inject them all. Text files are inlined. Binary files (images, PDFs, audio, etc., classified by extension) are injected as structured read instructions with absolute paths so the agent can fetch them via its own tools.

#### Directory cadenzas are NOT recursive

A directory cadenza globs **only the immediate children** of the directory. Subdirectories are ignored. If you need the whole tree, either flatten the input dir, or list the relevant subdirectories as separate cadenza items.

```yaml
# This injects /abs/inputs/prompt.md and /abs/inputs/code.py.
# It does NOT inject /abs/inputs/sub/extra.md — sub/ is skipped.
- directory: "/abs/inputs"
  as: context
```

Common gotchas:

- A README staged at the root of the input dir gets injected; a README inside `inputs/docs/` does not.
- If you nest by mistake (e.g., `inputs/inputs/prompt.md`), the inner `prompt.md` is silently ignored — directory cadenzas only see one level.
- Empty input dirs log a warning; the sheet still runs but reviewers see no injected content.

When a recursive view is genuinely required, a small preflight stage (often `instrument: cli`) can flatten or copy a curated subtree into the directory the cadenza points at.

#### Path resolution

Both `file:` and `directory:` paths support Jinja templating against the score's render context (e.g., `{{ workspace }}`, user variables). Relative paths resolve against the sheet's workspace, not the score file's directory — for cadenza sources outside the workspace, use absolute paths.

### Parallel Execution

```yaml
sheet:
  dependencies:
    2: [1]
    3: [1]                      # Parallel with 2
    4: [2, 3]                   # After both

parallel:
  enabled: true
  max_concurrent: 3
  fail_fast: true
```

**Always declare dependencies when parallel is enabled.** Without them, all sheets run immediately.

### Skip Conditions

```yaml
sheet:
  skip_when:                    # Command-based (exit 0 = skip); #119
    6:
      command: 'grep -q "COMPLETE" "{workspace}/output.md"'
      description: "Skip if already complete"
      timeout_seconds: 10
```

---

## Patterns by Use Case

### Batch Processing

```yaml
name: "batch-process"
workspace: "./batch-workspace"
instrument: claude-code
instrument_config:
  timeout_seconds: 1800
sheet:
  size: 10
  total_items: 100
prompt:
  template: |
    Process items {{ start_item }} through {{ end_item }}.
    Write results to {{ workspace }}/batch-{{ sheet_num }}.md
validations:
  - type: file_exists
    path: "{workspace}/batch-{sheet_num}.md"
  - type: command_succeeds
    command: 'test $(wc -w < "{workspace}/batch-{sheet_num}.md") -ge 100'
    description: "Has substantive content"
```

### Multi-Phase Pipeline

```yaml
sheet:
  size: 1
  total_items: 4
prompt:
  template: |
    {% if stage == 1 %}
    ## Research
    Write findings to {{ workspace }}/01-research.md.
    {% elif stage == 2 %}
    ## Analysis
    Read {{ workspace }}/01-research.md. Write to {{ workspace }}/02-analysis.md.
    {% elif stage == 3 %}
    ## Implementation
    Implement based on {{ workspace }}/02-analysis.md. Ensure tests pass.
    {% elif stage == 4 %}
    ## Review
    Review all work. Write report to {{ workspace }}/04-review.md.
    {% endif %}
validations:
  - type: file_exists
    path: "{workspace}/01-research.md"
    condition: "stage == 1"
  - type: file_exists
    path: "{workspace}/02-analysis.md"
    condition: "stage == 2"
  - type: command_succeeds
    command: 'cd {workspace} && pytest tests/ -x'
    condition: "stage == 3"
  - type: file_exists
    path: "{workspace}/04-review.md"
    condition: "stage == 4"
```

### Fan-Out with Synthesis

```yaml
sheet:
  size: 1
  total_items: 3
  fan_out:
    2: 3
  dependencies:
    2: [1]
    3: [2]
parallel:
  enabled: true
  max_concurrent: 3
cross_sheet:
  auto_capture_stdout: true
  max_output_chars: 3000
  lookback_sheets: 5
prompt:
  variables:
    lenses:
      1:
        name: "architect"
        voice: "You are a software architect."
        focus: "Design patterns, modularity, scalability"
      2:
        name: "tester"
        voice: "You are a testing expert."
        focus: "Edge cases, coverage, reliability"
      3:
        name: "security"
        voice: "You are a security analyst."
        focus: "Vulnerabilities, attack surfaces, data safety"
  template: |
    {% if stage == 1 %}
    Read the codebase at {{ workspace }} and write a project overview
    to {{ workspace }}/01-overview.md.
    {% elif stage == 2 %}
    {{ lenses[instance].voice }}
    Read {{ workspace }}/01-overview.md for context.
    Focus: **{{ lenses[instance].focus }}**
    Write findings to {{ workspace }}/02-review-{{ instance }}.md.
    Be specific: cite file paths and line numbers.
    {% elif stage == 3 %}
    Read all reviews:
    {% for i in range(1, fan_count + 1) %}
    - {{ workspace }}/02-review-{{ i }}.md ({{ lenses[i].name }})
    {% endfor %}

    Find convergences, tensions, and gaps. Don't summarize.
    Write to {{ workspace }}/03-synthesis.md.
    {% endif %}
validations:
  - type: file_exists
    path: "{workspace}/01-overview.md"
    condition: "stage == 1"
  - type: file_exists
    path: "{workspace}/02-review-{instance}.md"
    condition: "stage == 2"
  - type: command_succeeds
    command: 'test $(wc -w < "{workspace}/02-review-{instance}.md") -ge 300'
    condition: "stage == 2"
    description: "Review has substantive content"
  - type: file_exists
    path: "{workspace}/03-synthesis.md"
    condition: "stage == 3"
  - type: content_contains
    path: "{workspace}/03-synthesis.md"
    pattern: "## "
    condition: "stage == 3"
    description: "Synthesis has section headers"
```

---

*Marianne Score Patterns --- extracted from the score-authoring reference.*
