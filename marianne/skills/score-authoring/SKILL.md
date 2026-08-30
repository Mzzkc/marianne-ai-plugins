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

---

## Quick Syntax Reference

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
the resolved paths and hashes actually assembled into the prompt.

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

For multi-stage, evaluator, source-modifying, or release-producing scores, use
the composing skill's design gate. After `mzt validate`, run
`composing/scripts/check_score_release.py` to resolve load-bearing injections,
enforce workspace/fallback/validation policy, and write the exact candidate
digest. Any score or injection change after evaluation requires reevaluation.

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

**When this skill is invoked directly** (e.g., `/marianne:score-authoring`), load all three docs — the caller may need any level of detail.

---

## Additional Resources

- Example scores: `${CLAUDE_PLUGIN_ROOT}/docs/examples/` directory
- Fan-out gallery: [claude-compositions](https://github.com/Mzzkc/marianne-score-playspace)
- Operational guide: command skill (invoke via `/marianne:command`)
