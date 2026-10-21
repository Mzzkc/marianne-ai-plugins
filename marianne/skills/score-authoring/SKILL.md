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
gap, filed as an issue first. A score never writes into `~/.marianne/instruments/`;
a generator that does is a bug. For a new subject on an unchanged provided
engagement, supply supported task/cadenza inputs without editing the managed score.
A profile alias binds an instrument; it does not create a persistent person.
For portable model work, `instrument: strong` (or another configured capability
class) resolves to an ordered profile chain from `~/.marianne/classes.yaml` and
the packaged default. Check the effective chain with `mzt instruments classes
show` and availability with `mzt instruments classes check` before relying on
it; for a local (`ollama`) entry the check also verifies the server serves the
profile's model, so a missing pull shows up here and in `mzt validate`, not at
sheet 1. A sheet that sets `instrument_config.response_format` (`type: json_schema`)
must run on an instrument that can enforce it: an HTTP profile, or a CLI
profile that declares `cli.command.json_schema_flag` (the `claude-code` builtin
does; `opencode` and `codex-cli` do not). `mzt validate` warns V311 otherwise,
for a class chain and for a plain `instrument:` binding alike, because every
dispatch of that sheet would be refused. `doctor`, `instruments list`, `instruments check`, `classes check` and
`classes write` share that one probe (ready / unavailable / unreachable /
unchecked), so a chain `classes write` emits is one `classes check` accepts on
the same machine, and "Marianne is ready" means an agent instrument can run
(the raw shell `cli` profile does not count). An installed harness whose
provider is not configured passes that probe and refuses at sheet 1 instead;
the shipped `goose`, `crush` and `opencode` profiles carry that refusal text
as `errors.unavailable_patterns`, so the sheet moves to the next chain entry
on its first attempt without a retry charge (GH #389). A private profile for
a harness that refuses in its own words needs its own pattern there, or the
sheet runs to its timeout on every misconfigured entry. A chain may name profiles this machine lacks: the job starts at the
first entry that can run (V311 says which, and it warns rather than refuses
even when nothing in the chain is installed yet — a fresh install sees that
on `mzt init`'s starter score until one instrument is on PATH); only a class
with no registered entry is refused (V310). Score aliases and registered profile names take precedence over classes;
`instrument: cli` stays the deterministic shell profile. Use an alias when the
score requires a fixed model or route. A class cannot override `expected_route`.
For consequential new/changed behavior, reuse an approved design or obtain a
separately validated design before YAML. Design and encoding in one unreviewed
stage is not that gate; unchanged syntax repairs inherit the existing review.
For substantial work, encode the required
construction, consumer integration, independent review, repair and reevaluation;
one or two sheets are not a substitute for those behaviors. Atomic operations
can remain small within that performance.

---

## Quick Syntax Reference

Three timers, three different knobs — do not mix them:
`instrument_config.timeout_seconds` is the per-sheet execution timeout;
the same typed settings work in `movements.<N>.instrument_config`,
`sheet.per_sheet_instrument_config.<N>`, and `instruments.<alias>.config`.
Unknown keys at all four scopes warn as V010/V011. A reviewed CLI route
may set `provider` alongside `model` without losing it at YAML load.
A bare `timeout:` is a key at none of them — wherever it appears it is
unknown, and V010 names the `timeout_seconds` of the surface it sits in (an
alias's `config`, a movement's or sheet's `instrument_config`, a `run:`
action's own bound), falling back to the root `instrument_config.timeout_seconds`
only at the root. A hint never widens one seat's or one action's bound to the
whole score.
`stale_detection.idle_timeout_seconds` is the opt-in no-output idle timer;
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

For `sheet.triggers` actions, `run: {command: "...", timeout_seconds: 120}`
executes a bounded shell command. Linux uses a per-action subreaper to clean
detached children even when they close stdio; on other hosts `mzt validate`
emits V326 INFO because that orphan guarantee is unavailable.

For parallel voices, set `movements.<N>.voices` with `sheet.size: 1` and
`sheet.start_item: 1`; this expands through `fan_out`, including dependencies.
An explicit `sheet.fan_out` count wins for the same movement. For a cost cap,
set `cost_limits.max_cost_per_sheet`; the baton enforces it on each sheet,
including successful attempts. `retry.completion_threshold_percent` is a
strict gate: a validation pass rate above it enters completion mode; a lower
result spends a normal retry. Older releases ignored the threshold and sent
any partial pass to completion mode, so review scores that use the default 50%.

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

**Directory cadenzas are NOT recursive** — only the immediate children of the directory are injected. Subdirectories are silently ignored. If you need a deeper tree, flatten the input dir or list each subdir as its own cadenza item. A common pattern: a small `instrument: cli` preflight stage curates/copies the relevant files into one flat directory the cadenza points at.

See `patterns.md` → "Prelude & Cadenza" for full file/directory injection rules.

For a persistent agent, read
`${CLAUDE_PLUGIN_ROOT}/docs/ref/modern-agents.md` before authoring. Do not encode
the person as an instrument profile, treat registry membership as attachment,
or use a legacy plugin helper or `musician-XXXX` profile. Start from the shipped
full-lifecycle, targeted-work, or lifecycle-integration score when it matches;
compose a custom score only when the engagement needs a different DAG.

### Deterministic and release-grade sheets

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
For a design file, supply `goal`, `authority`, `forces`, `stages`, `context_flow`,
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
