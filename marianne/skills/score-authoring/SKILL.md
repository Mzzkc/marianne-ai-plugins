---
name: score-authoring
description: Use when writing, reviewing, or fixing Marianne score YAML configs, including persistent-agent identity, memory, technique, cadenza, and lifecycle attachment. Do NOT use for running/debugging jobs (use command instead).
---

# Marianne Score Authoring Skill

> **Purpose**: Write correct, effective Marianne score configs. Routes to the appropriate reference docs based on score complexity.

---

## Triggers

| Use This Skill | Skip This Skill |
|---|---|
| Writing new Marianne score YAML | Debugging existing Marianne errors (use `/marianne:command`) |
| Reviewing/fixing score configs | Running/monitoring jobs |
| Understanding available features | CLI operations only |
| Designing multi-stage workflows | |

Invoking a qualified stock engagement with supported task inputs and route binding
is conducting, not new score authoring. Use this skill directly for an authorized
YAML task; no prior conducting or composing invocation is required. Consume a supplied
design. When changing the DAG, prompt logic, attachment contract or guarantees,
establish the goal, authority, inputs, consumers, proof, repair and release decisions
before encoding them. Composing can own a separate design commission when needed.
**Reuse before invention (GH #443).** Edit an existing score first — scores are
modified like code; a new subject, date, model or timeout is an edit, not a new
score. A seat is a score alias over an EXISTING profile:
`instruments: { seat: { profile: codex-cli, config: { model: …, timeout_seconds: N } } }`.
Role and posture are a cadenza directory on an existing agent. Portable routes are a
capability class. A new profile, agent or layer comes only after a proven behavioural
gap, filed as an issue first. The test for a profile: it needs a DIFFERENT
`cli.command.executable`, output `format`, prompt delivery, or error vocabulary
than any builtin has. A model, a timeout, `interactive`, a capability tag or a
reasoning level is a pin, and a pin is an alias. A user-layer copy of a builtin
with only the model changed is the worst of both: it replaces the builtin whole,
so every key the builtin gains later (first-output bound, quota vocabulary,
cache token paths) is missing from that seat forever (2026-11-10: three such
copies carried 1,166 score references and lacked three to six builtin keys each).
When a fork carries an override everyone needs, send it to the builtin as a PR.
A score never writes into `~/.marianne/instruments/`;
a generator that does is a bug. For a new subject on an unchanged provided
engagement, supply supported task/cadenza inputs without editing the managed score.
A profile alias binds an instrument; it does not create a persistent person.
**Bind per role, not one alias for the whole score.** `instrument: strong` on every
sheet is the wrong pattern: recon, build, review and synthesis want different
models, and the score is where that is said. Pin the model on every model seat (`instrument_config.model` or the alias `config`): an unpinned `claude-code` or `codex-cli` seat follows the operator's own CLI default, and `mzt validate` notes it (V336). Give each role its own alias and
bind it on the movements or sheets that play that role. An alias may carry a
`chain` of entries with `select` modifiers: `spread` gives a fan-out's voices
distinct models from one alias (three reviewers, three models, no agreement
by shared blind spot); `cycle` rotates across sheets; `cheapest`/`widest`
order by the profile's model table; `balance` lets the conductor start on the
least-loaded entry at dispatch. Modifiers compose in the order written. The
chain's remaining entries are that sheet's fallbacks, so one alias states the
route and its recovery together.
For portable model work, `instrument: strong` (or another configured capability
class) resolves to an ordered profile chain from `~/.marianne/classes.yaml` and
the packaged default. Check the effective chain with `mzt instruments classes
show` and availability with `mzt instruments classes check` before relying on
it; for a local (`ollama`) entry the check also verifies the server serves the
profile's model, so a missing pull shows up here and in `mzt validate`, not at
sheet 1. A local `kind: http` profile declares its model's real `context_window`
(and `max_output_tokens` when known): the HTTP executor caps `max_tokens` at it,
and a small local server refuses the 16,384 default with HTTP 400 otherwise;
`mzt instruments check` reads the server's live context from `GET /props` and
`mzt validate` warns (V234) when the profile declares more. A
profile in the project's `.marianne/instruments/` is loaded by the conductor
only when it was started from that directory; submit refuses the score
otherwise and names both directories. A sheet that sets `instrument_config.response_format` (`type: json_schema`)
must run on an instrument that can enforce it: an HTTP profile, or a CLI
profile that declares `cli.command.json_schema_flag` (the `claude-code` builtin
does; `opencode` and `codex-cli` do not). `mzt validate` warns V311 otherwise,
for a class chain and for a plain `instrument:` binding alike, because every
dispatch of that sheet would be refused. The sheet must also run headless:
claude-code and antigravity run interactively when the score is silent, and the
interactive backend cannot enforce a schema, so a schema sheet on them carries
`interactive: false` (V331 warns otherwise, GH #478). The schema itself needs a top-level `type: object` and no
top-level `oneOf`/`allOf`/`anyOf` — Claude Code forwards it as a tool
`input_schema` and the API refuses those shapes (V332, GH #486); put a
discriminated union under one required property. The validated object is
kept whole as the sheet's `structured_output` in `mzt status --json` and
`job.status` (up to 64 KiB, else `structured_output_omitted: true`), so a
downstream reader needs no tools-enabled sheet to write it (GH #489). `doctor`, `instruments list`, `instruments check`, `classes check` and
`classes write` share that one probe (ready / unavailable / unreachable /
unchecked), so a chain `classes write` emits is one `classes check` accepts on
the same machine, and "Marianne is ready" means an agent instrument can run
(the raw shell `cli` profile does not count). `classes write` ranks shipped
profiles; a personal or venue profile is seated only where its `class_hints`
say (`{strong: "after opencode", fast: first}`), never by name alone, and only where it passes the class's probe: a refused (profile, class) pair is named in the map's header comment and on the terminal with its cause (an `http` endpoint lacks `file_editing`, so it never seats in `workhorse`; route it through opencode). An installed harness whose
provider is not configured passes that probe and refuses at sheet 1 instead;
the shipped `goose`, `crush` and `opencode` profiles carry that refusal text
as `errors.unavailable_patterns`, so the sheet moves to the next chain entry
on its first attempt without a retry charge (GH #389). A private profile for
a harness that refuses in its own words needs its own pattern there, or the
sheet runs to its timeout on every misconfigured entry. A chain may name profiles this machine lacks: the job starts at the
first entry that can run (V311 says which, and it warns rather than refuses
even when nothing in the chain is installed yet — a fresh install sees that
on `mzt init`'s starter score until one instrument is on PATH, except that a machine whose only ready instrument is a loopback `http` server gets a starter bound to that profile, passing replies between sheets instead of files); only a class
with no registered entry is refused (V310). A sheet bound through an alias renders `{{ instrument_alias }}` (the alias name) beside `{{ instrument_name }}` (the profile it resolved to, which changes on fallback) — stamp evidence with the alias when a roster of seats must join. Score aliases and registered profile names take precedence over classes;
In a `command_succeeds` command every `{placeholder}` is one shell-quoted word;
split a space-separated variable in the shell (`read -r -a xs <<< {list}`),
never as a bash array literal (`xs=({list})` is one element; V333 warns; GH #477).
Declare movement outputs with `movements: {2: {produces: ['{workspace}/report-{sheet_num}.md']}}`
when downstream cadenzas read them or concurrent sheets need ownership boundaries.
Paths are workspace-relative or `{workspace}`-prefixed; `{sheet_num}` is the
concrete producing sheet, including each fan-out voice. A shared path belongs to
every declaring voice. For the same path, explicit `produces:` ownership takes
precedence over `sheet.stdout_to`, then the existing sheet-gated `file_exists`
proxy; independent outputs from all three are combined. A declaration does not
write a file or verify its contents. Gate each stage's own output with a
`file_exists` validation scoped to that sheet (`condition: "sheet_num == N"`).
V109 then catches a cadenza that reads the file before its producer runs,
while V108 exempts declared cadenza outputs from static missing-file errors
(prelude inputs must already exist),
and the conductor names a sheet that writes a later sheet's file (an
`artifact:` warning in `mzt status`) instead of letting the fabrication pass
as upstream input; `workspace_lifecycle.foreign_artifacts: quarantine` moves
such a file to the job's scratch quarantine before downstream sheets run.
`instrument: cli` stays the deterministic shell profile. Use an alias when the
score requires a fixed model or route. A class cannot override `expected_route`.
For consequential new/changed behavior, reuse an approved design or obtain a
separately validated design before YAML. Design and encoding in one unreviewed
stage is not that gate; unchanged syntax repairs inherit the existing review.
For substantial work, encode the required
construction, consumer integration, independent review, repair and reevaluation;
one or two sheets are not a substitute for those behaviors. Atomic operations
can remain small within that performance. A schema sheet also gets the profile's `cli.command.schema_extra_flags` instead of its `extra_flags` when the profile declares them: the `claude-code` builtin runs schema sheets at `--effort high` because `--effort max` with `--json-schema` emits nothing until the sheet timeout on Claude Code 2.1.307, so a schema sheet that stalls at 0 bytes on a copied profile is missing that key, not a bigger timeout. Never splice one inside an interpreter's string literal (`python3 -c "open('{var}/x')"`): a value shlex wraps — `~/path`, anything with a space — keeps its quotes there, so `expanduser()` sees `'~/path'`. Pass it as argv: `python3 -c "...sys.argv[1]..." {var}`.

---

## Quick Syntax Reference

Before the first paid run of a score you wrote or changed, read what the
musicians will actually receive: `mzt validate SCORE --render-prompts -`
prints every sheet's full rendered prompt, identical renders grouped under one
heading (`## Sheets 2-3`); `--render-prompts prompts.md` writes it instead.
Findings tell you a key is wrong; the dump tells you a prompt reads wrong.


Three timers, three different knobs — do not mix them:
`instrument_config.timeout_seconds` is the per-sheet execution timeout;
the same typed settings work in `movements.<N>.instrument_config`,
`sheet.per_sheet_instrument_config.<N>`, and `instruments.<alias>.config`.
Unknown keys at all four scopes warn as V010/V011. A whole unknown block at the root (`deliver:`, `for_each:`) is V010 WARNING: the loader drops it and the runtime does nothing with it — never ship a score that relies on a key `mzt validate` warns about. A reviewed CLI route
may set `provider` alongside `model` without losing it at YAML load.
A bare `timeout:` is a key at none of them — wherever it appears it is
unknown, and V010 names the `timeout_seconds` of the surface it sits in (an
alias's `config`, a movement's or sheet's `instrument_config`, a `run:`
action's own bound), falling back to the root `instrument_config.timeout_seconds`
only at the root. A hint never widens one seat's or one action's bound to the
whole score.
For known slow CLI startup (for example during a backup), set
`instrument_config.first_output_timeout_seconds: 240` to widen the initial
zero-byte silence bound for that sheet; a smaller finite positive value narrows
it. Omit the key to inherit the profile, or set `null` to disable this bound.
The sheet timeout still caps execution, and this bound is inert after the first
stdout or stderr byte. The same four override scopes apply; HTTP and interactive
backends warn and ignore this CLI-only setting.

`instrument_config.effort: <level>` sets one sheet's reasoning effort (GH #535),
at the same four scopes and on an alias chain entry's `config`. Reasoning is
about nine tenths of a Claude sheet's output tokens and the `claude-code`
builtin runs headless sheets at `max`, so set it by role instead of leaving
every sheet at the default: keep the default (omit the key) for design,
architecture, build, debugging and adversarial-review sheets; use `medium` for
a review or evidence check against a written rubric and for synthesis of
already-judged inputs; use `low` for recon, inventory, mechanical edits, format
conversion and release sheets (tag, changelog, publish). When a lowered sheet
starts failing its validations, raise it one level before touching the prompt.
The one measured step (2026-11-11, three runs of one small task): on Sonnet,
`max` spent about 2.3 times the reasoning tokens of `high`, while `low`,
`medium` and `high` did not differ, and Haiku showed no usable effect. So
`max` to `high` is where the saving is known; the lower levels are role advice,
not yet a measured gain.
The words are Marianne's, the same for every instrument, lowest first:
`minimal`, `low`, `medium`, `high`, `xhigh`, `max`; any other word fails at
load. Each profile maps them to its harness's own through its `effort:` block,
so write the level, not a flag: `claude-code` and `antigravity` `--effort`,
`codex-cli` `-c model_reasoning_effort=`, `opencode` `--variant` and `crush`
`--reasoning-effort` per model. `minimal` is the least the seat offers (`low` on
Claude Code, Antigravity and Codex). Those mappings were declared from help
text and local model catalogs; only `claude-code`'s was run, so claim no saving
elsewhere. `gemini-cli`, `aider`, `goose`, `claude-code-ollama` and HTTP
`ollama` have no mapping, so never set `effort` at score scope in a score whose
sheets or fallbacks reach them (or an old user-layer copy of a builtin): put it
on the alias, class entry or movement that owns the seat. It also rides on a
class entry in `classes.yaml`; on the primary a score scope wins. A schema
sheet on `claude-code` takes `minimal` to `high` only, and an interactive sheet
on `opencode` is refused. `mzt validate` reports V335 (ERROR) naming the
accepted levels; dispatch refuses the same sheets. A fallback takes `effort`
only from its own entry.
`effort: null` at a narrower scope restores the profile default.

`instrument_config.tools: [<name>, ...]` narrows one sheet's toolset (GH #534),
at the same scopes and on an alias chain entry or class entry. The names are the
harness's own (Claude Code: `Bash`, `Read`, `Edit`, `Write`, `Grep`, `Glob`);
there is no shared vocabulary. `[]` means no tools, an absent key the harness
default. Narrow by role: `[Read, Grep, Glob]` for recon, inventory and review
sheets that only look; `[Bash, Read, Edit, Write]` for sheets that change files
or run commands; `[]` for pure text work (summarise, judge, rewrite supplied
text). Keep every tool the prompt tells the sheet to use, since a sheet cannot
call a tool it was not given. Measured on Claude Code only: a one-turn probe
sent 28.8k tokens with 29 tools and 14.0k with four, tool definitions being about
half the fixed prefix every request pays; one small read-only task cost about 40%
less with four tools (three runs per arm, so direction, not size). Claim nothing
for other harnesses. Only `claude-code` and `claude-code-ollama` declare a
`tools:` mapping (`--tools`, the flag that removes definitions; `--allowedTools`
is permission-only and is not used); on any other profile the key is refused,
so set it on the alias, class entry or movement that owns a Claude Code seat.
`mzt validate` reports V337 (ERROR) for a profile with no mapping or a name
outside its `known` list; dispatch refuses the same sheets.

For an interactive sheet that needs screen-aware continuation, opt in with
`instrument_config.interactive_nudge_policy: model` and set
`instrument_config.interactive_nudge_instrument` to a registered inexpensive
headless instrument. `instrument_config.interactive_nudge_timeout_seconds`
is a finite positive per-call bound (30 seconds by default), within the sheet
deadline. Keep the default `static` policy when a fixed input is enough.
Model-call errors or invalid replies fall back to `interactive_nudge_message`;
an unrecoverable decision stops nudging and validations still judge success.
Without a configured model instrument, continuation stays static with a warning.
These knobs share the same four override scopes as the other instrument settings.

A `kind: mcp` technique names a server the conductor's pool already runs
(`config.server`); the pool runs any stdio MCP server, so a new tool is a
pool entry plus a technique, never new Marianne code. REA (Reverse Engineer
Anything) is the shipped example (GH #499): attach it when a sheet must read a
binary, bundle, APK, firmware or runtime capture; its analysis state is shared
across every musician on the conductor, so the sheet opens its target and
closes it (`close_binary`, `snapshot_path` to keep the analysis) before it
ends, and `mzt doctor` reports REA's own toolchain gaps under Providers.
Start from `examples/engineering/artifact-analysis.yaml` rather than a blank
technique block: give the tool to the maker only (a numbered movement in
`phases`, such as `["2"]`), make every claim cite an `evidence_id` from the
bundle the tool itself exported, and keep the judge off the tool so it checks
the bundle, not the maker's memory of it.

`stale_detection.idle_timeout_seconds` is the opt-in no-output idle timer; it
measures writes under the sheet's workspace, so a sheet that builds in the
project's worktree or a scratch clone names those roots in
`stale_detection.watch_paths` or it is killed as idle while working (GH #516);
`schedule.max_wall_seconds` bounds one scheduled tick of a recurring score.
Set it under `schedule:`; the old root spelling warns as V328 for one release.
The conductor's `job_timeout_seconds` counts only accumulated RUNNING time,
including resumed work, so pauses and downtime do not spend that limit.
A one-shot score has no absolute tick deadline — per-sheet timeouts, idle
detection and the conductor's accumulated RUNNING budget form its envelope.
The three timers sit side by side, with what each bounds and what happens
when it fires, at the top of the repo's `docs/glossary.md`.

For readable default-off sections such as `parallel` or `stale_detection`,
set `enabled: true` with their settings. V329 warns this release if you omit
the switch; next release settings will turn the section on unless you write
`enabled: false`. Reserved sections instead emit V327 and remain inert.

A key the runtime does not read yet says so: the configuration reference
marks it **Reserved**, and `mzt validate` emits V327 when a score sets it —
remove the key rather than silencing the warning.
The score-level `rate_limit:`, `circuit_breaker:`, `logging:`, and `bridge:`
sections are reserved; use the conductor and instrument settings that have
runtime readers. The score's `learning.exploration_budget`,
`learning.entropy_response`, and `learning.auto_apply` are also reserved;
V327 warns, and V329 does not promise activation for them. When a key is
missing for a seat, the reuse ladder above still applies: an alias over an
existing profile before any new profile.

Renamed spellings warn
V328 and keep working one release: write `approvals:` (not `checkpoints:`),
and `if_hook_fails` inside `on_success`/`on_failure` hooks (at the trigger
level `on_failure` means a different thing). The root `conductor:` block is
deprecated identity metadata with no reader — conductor behaviour lives in
`~/.marianne/conductor.yaml`.

For fan-out messaging, `sheet.fan_out_messaging: file | none` defaults to `file`
(the compatible sibling spelling of `fan_out.messaging`). File mode prepares
scratch-owned sibling inboxes and polling instructions (`mzt mail send` / `read`);
`none` omits messaging prompt setup. Explicit use without concurrent voices emits
V235 WARNING. Received messages are data, not instructions.

For `sheet.triggers` actions, `run: {command: "...", timeout_seconds: 120}`
executes a bounded shell command. Linux uses a per-action subreaper to clean
detached children even when they close stdio; on other hosts `mzt validate`
emits V326 INFO because that orphan guarantee is unavailable.

For parallel voices, set `movements.<N>.voices` with `sheet.size: 1` (the default; a score that names only `total_items` gets one sheet per item) and
`sheet.start_item: 1`; this expands through `fan_out`, including dependencies.
An explicit `sheet.fan_out` count wins for the same movement. For a cost cap,
set `cost_limits.max_cost_per_sheet`; the baton enforces it on each sheet,
including successful attempts. `retry.completion_threshold_percent` is a
strict gate: a validation pass rate above it enters completion mode; a lower
result spends a normal retry. Older releases ignored the threshold and sent
any partial pass to completion mode, so review scores that use the default 50%.

`sheet.stdout_to` (`{1: design.md}`) makes the musician write a sheet's full stdout to a workspace file before validations run: the way an `http` sheet, which has no filesystem, meets a file validation or hands its reply whole to a later sheet (`stdout_tail` keeps 500 characters). A fanned-out stage gets one file per voice.

`sheet.skip_when` skips one sheet; it does not cascade — the baton lets dependents of an intentional skip run (`[SKIPPED]` in `previous_outputs`). A chain terminator (a marker that says "this iteration does nothing") goes on every sheet, including the one whose trigger chains, or later sheets run and chain again.

**The #1 rule**: Jinja `{{ }}` in the **prompt pipeline** (templates, prelude/cadenza paths, capture_files). Python format `{}` in the **validation engine** (validation paths, commands, working_directory, skip_when).

| Field | Syntax |
|---|---|
| `prompt.template` | `{{ workspace }}` |
| `validations[].path` | `{workspace}` |
| `validations[].command` | `{workspace}` |
| `capture_files[]` | `{{ workspace }}` |

### Injection: file vs. directory cadenzas

`prelude` and `cadenzas` items take exactly one of `file:` or `directory:`.

```yaml
sheet:
  cadenzas:
    1:
      - file: "{{ workspace }}/setup.md"        # one file
        as: skill
        required: true
    2:
      - directory: "/abs/path/to/inputs"        # whole directory at once
        as: context
```

`required` defaults to `false` for legacy compatibility. Set it to `true` for
every load-bearing persistent-agent identity, memory, and cadenza attachment so
missing context fails before execution. Runtime context-delivery receipts prove
the resolved paths and hashes actually assembled into the prompt; they do not
prove that the recipient applied the context or achieved the intended behavior.

`max_bytes` caps what one item injects (a directory sums its files). A ledger that grows with every sheet — an `active/` directory, a memory file — needs it: over the cap a `required` item fails the sheet before execution naming the size, an optional one is dropped with a warning, and nothing ships an over-sized prompt that only the conductor-wide token warning would have noticed after assembly (V334 warns when a static path is already over; GH #474). Pair it with a Consolidate stage that rotates the ledger into `archive/`.

**Directory cadenzas are NOT recursive** — only the immediate children of the directory are injected. Subdirectories are silently ignored. If you need a deeper tree, flatten the input dir or list each subdir as its own cadenza item. A common pattern: a small `instrument: cli` preflight stage curates/copies the relevant files into one flat directory the cadenza points at.

See `patterns.md` → "Prelude & Cadenza" for full file/directory injection rules.

For a persistent agent, read
`${CLAUDE_PLUGIN_ROOT}/docs/ref/modern-agents.md` before authoring. Do not encode
the person as an instrument profile, treat registry membership as attachment,
or use a legacy plugin helper or `musician-XXXX` profile. Start from the shipped
full-lifecycle, targeted-work, or lifecycle-integration score when it matches;
compose a custom score only when the engagement needs a different DAG.

### Deterministic and release-grade sheets

A loop span carries up to three bounds: `until` (the goal), `max_iterations`
(passes), `cost_limit_usd` (money). Money is measured from the tokens each
route reports at its profile's price; a subscription or local route prices at
$0, so on such a venue `mzt validate` warns V228 and `max_iterations` is the
only working cap. Write `max_iterations` as the number of passes the work can
justify, never the default 50, and treat V228 as "this venue cannot stop on
money", not as a reason to delete the cap.

For a deterministic `cli` sheet, set an explicit empty replacement chain:

```yaml
sheet:
  per_sheet_fallbacks:
    3: []
```

Without this, an inherited AI fallback can reinterpret a failed shell command
and conceal that the deterministic gate never ran.

For multi-stage, evaluator, source-modifying, or release-producing scores, verify
the design above, compatibility/test disposition, candidate provenance, distinct
review and bounded repair through adoption. A narrow syntax repair to an unchanged
contract does not require recommissioning its design. The plugin's shared
`composing/scripts/check_design.py` and `composing/scripts/check_score_release.py`
are reusable tools; using them does not require invoking composing. Run the design
checker for a new/changed design and, after `mzt validate`, the release checker to resolve load-bearing injections,
enforce workspace/fallback/validation policy, and write the exact candidate
digest. Any score or injection change after evaluation requires reevaluation.
These are structural and identity checks, not proof of the product outcome.
The keys this skill teaches, the schema's own descriptions, `mzt validate`'s
words and `docs/configuration-reference.md` are one language checked by
`tests/scripts/check_language.py` in the venue's suite: a key you find in only one of
them is a bug to file (`bug` + `documentation`), not a trick to work around.
Use `mzt validate --strict` when warnings are part of the release gate. Review
each warning in score context before listing its WARN/INFO code in
`validate.suppress`; V012 rejects ERROR-tier and unknown codes. V010/V011
report unknown YAML fields that the score loader ignores, so correct genuine
typos before release. INFO findings appear with `--verbose` or in `--json`.
An instrument position may name a capability class (`instrument: strong`,
fallbacks too) instead of a profile; the class resolves through the machine's
class-map layers into an ordered profile chain. Never pin `instrument_config.
model` against a class primary (V323) — write a score alias for a fixed model
or set the model on the class entry. An alias must name a profile, never a
class (V321), and a `cli` (raw shell) sheet must not list a class among its
fallbacks (V307).
Prompt size is never the author's problem on a shipped agent profile: each one
delivers the prompt over stdin (`antigravity` print mode as one stream-json
line), so prelude and cadenza injection may run to hundreds of KB. The raw
`cli` profile passes its command in argv by design, and any custom profile with
`prompt_via_stdin: false` is capped by the kernel's per-argument limit
(128 KiB) and fails to spawn (`E2BIG`) above it.
For a design file, supply `goal`, `authority`, `forces`, `stages` (each AI stage with `sizing`), `context_flow`,
`injections`, `proof_obligations`, `compatibility`, `test_disposition`,
`verification_context`, `repair_loop` and `release`. Record candidate/import
provenance, serialized whole tests and yielded-process cleanup in verification;
make release depend on affected reevaluation and exact candidate identity.
Give each consequential output an actual consumer and behavioral validation;
connect failed consumption to owned repair and reevaluation using supported
execution and recovery controls. A pattern example inherits no stronger
guarantee than its actual configured checks execute.
Use task-scoped score filenames matching `name`, fail-fast gate invocations and
the same explicit lock path when writing and checking. Keep a complete qualified
invocation, including test-only prerequisites. Encode owners/activation for failed
consumption and interrupted return; report an unsupported transition instead of
inventing YAML semantics. Return the exact YAML, checks run, capabilities still
unqualified and the next authorized operation to the caller.

---

### Telemetry opt-in

A score may carry `telemetry: {enabled: true, spool_path: …}` (GH #146). It only
stages a sanitized envelope locally, and only once the user has given consent
with `mzt telemetry consent`; nothing is sent without `mzt telemetry flush
--push`. Leave it out of shipped examples. `endpoint` and `submit_mode` are
reserved: the schema accepts them and no runtime reads them.

## Reference Docs

Load the docs matching your score's complexity tier:

| Tier | What to Load | Covers |
|---|---|---|
| **1** (simple pipeline) | `essentials.md` | Syntax, core variables, validations, config, YAML gotchas, pitfalls, pre-flight checklist |
| **2** (fan-out + synthesis) | `essentials.md` + `patterns.md` | + Design philosophy, fan-out patterns, Jinja mastery, prompt engineering, cross-sheet/parallel config |
| **3-5** (concert, self-chain, complex) | `essentials.md` + `patterns.md` + `advanced.md` | + Retry/rate limiting, circuit breaker, concert mode, post-success hooks, isolation, stale detection |

### Loading Instructions

Read the reference docs from `${CLAUDE_PLUGIN_ROOT}/docs/ref/`:

```
${CLAUDE_PLUGIN_ROOT}/docs/ref/essentials.md   — always load
${CLAUDE_PLUGIN_ROOT}/docs/ref/patterns.md     — load for tier 2+
${CLAUDE_PLUGIN_ROOT}/docs/ref/advanced.md     — load for tier 3+
```

**When this skill is invoked directly** (e.g., `/marianne:score-authoring`), select
the tier from the actual score or requested behavior. Load deeper references when
their features are implicated; the invocation itself does not require all tiers.

---

## Additional Resources

- Example scores: `${CLAUDE_PLUGIN_ROOT}/docs/examples/` directory
- Fan-out gallery: [claude-compositions](https://github.com/Mzzkc/marianne-score-playspace)
- Operational guide: command skill (invoke via `/marianne:command`)
