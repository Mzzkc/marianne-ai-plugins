---
name: composing
description: Use when turning a goal into a Marianne score, persistent-agent engagement, multi-stage AI workflow, concert, fan-out, evaluator loop, or release-grade orchestration YAML.
---

# Composing Marianne Scores

Composition designs a system of minds. The score is not ready because its YAML
parses; it is ready when its context, authority, outcomes, repair loop, and exact
release candidate are provable.

## Decide and investigate

Compose only when coordination earns its overhead: distinct stages, parallel
work, different instruments, costly downstream contamination, recovery, or
reuse. Otherwise recommend a prompt or command.

Before casting, decide whether the work should reuse a persistent person,
construct a new persistent person, or use an ephemeral worker. Read
`${CLAUDE_PLUGIN_ROOT}/docs/ref/modern-agents.md` whenever future learning,
identity, relationships, or lifecycle memory may matter. Never reach for a
legacy file under `plugins/marianne/agents/` or a DJ-only `musician-XXXX`
profile as a modern-agent template.

Inspect the venue and current runtime before design. Read:

1. `scores/rosetta-corpus/INDEX.md` and `forces.md`.
2. Each selected pattern's full file, not its name or a summary.
3. `plugins/marianne/docs/ref/instrument-catalog.yaml` and `mzt doctor` before
   assigning instruments.
4. The score-authoring skill before writing YAML.

Disk and runtime behavior outrank pattern prose.

## Current Gemini 3.8 Flash guidance

The catalog's current stable Gemini Flash route is `gemini-3.8-flash`, with a
1,048,576-token input limit and a 65,536-token output limit. Use high thinking for load-bearing coding and agentic work when the task is clear, bounded, and
backed by observable proof obligations. Use medium thinking as the balanced default for general work. Use low thinking for cheap, bounded work. The model
rejects the `minimal` level, so never request `minimal` for Gemini 3.8 Flash.

Keep four evidence lanes distinct when selecting it: catalog availability
through `antigravity`, configured profile availability in the
target installation, dispatch compatibility for the selected instrument and
profile, and live verification with working authentication. Evidence in one
lane does not establish another. Do not claim comparative quality or benchmark
superiority from the catalog entry; its qualitative ratings remain provisional
pending independent evaluation.

## Current GLM specialist guidance

Do not freeze a convenient local profile alias into a score. GLM 5.3 Flash may
be selected only when current profile and live evidence prove a Z.AI route,
the exact released model ID, entitlement, limits, vision capability, and
invocation contract. `opencode-ox-alpha` may remain a historical box-local
alias; it is not a free OpenRouter route or a portable score contract. Bind
semantic phase requirements through live evidence and retain the routing
receipt. Treat free or subscription-included metering as one cost dimension,
not as evidence of low latency, quota, queue, or rate-limit risk.
When GLM 5.3 is selected for substantial work, use high or max reasoning.

For authorized defensive cybersecurity and vulnerability discovery, commission
a specialized vulnerability-discovery score. It must gate target authority and
scope before execution, keep discovery non-destructive, split the search into
explicit vulnerability classes or components, require reproducible findings
and independent severity triage, and route accepted findings through
regression-backed remediation and coordinated disclosure. Instrument selection
does not broaden the composer's authority or bypass provider guardrails.

## Design gate

Before YAML, write `composition-design.yaml` with these required sections:

- `goal`: statement and observable completion;
- `authority`: project root and mutation authority;
- `forces`: active forces with evidence;
- `stages`: IDs, dependencies, and produced artifacts;
- `context_flow`: source, destination, and mechanism for every load-bearing input;
- `injections`: paths, destinations, and whether required;
- `proof_obligations`: behavioral checks per artifact;
- `compatibility`: explicit `preserve`, `intentional_break`, or
  `not_applicable` policy, rationale, and every migration target;
- `test_disposition`: each removed test classified as a retired contract,
  migrated contract with replacement, or redundant contract with replacement;
- `verification_context`: `source_binding`, an `import_probe` that prints the
  imported module path, and `process_control` with `one_suite_at_a_time: true`
  plus a `yielded_process_cleanup` procedure;
- `repair_loop`: repair stage, reevaluation stage, and maximum iterations;
- `release`: release stage, reevaluation dependency, and candidate-hash policy.

When persistence is chosen, also record the selected person or new durable gap,
canonical L1-L4 authority, portable seed, required identity/memory/technique and
cadenza attachments, lifecycle score shape, immediate writeback, pending debt,
agent-authored conflict adjudication, delivery-receipt check, and later-recall
test.

Run:

```bash
python scripts/check_design.py composition-design.yaml
```

User approval or a separately validated stage must cross this gate. Design and
YAML in one unreviewed stage is not a gate.

## Compose

- Derive the stage DAG from artifact dependencies and selected pattern
  invariants.
- Give each artifact one owner and an outcome validation.
- Inject required content; do not merely tell an agent to find it.
- Resolve every prelude and cadenza using runtime workspace semantics.
- Keep the artifact workspace separate from `project_root`.
- Use Jinja `{{ }}` in prompts/injection paths and Python format `{}` in
  validations.
- Use `cli` for deterministic commands. Set
  `per_sheet_fallbacks: {N: []}` for every deterministic CLI sheet so an LLM
  cannot reinterpret a failed command.
- Give AI sheets capability-matched fallbacks, except isolated evaluators where
  fallback would destroy independence.
- Validate outcomes, not file existence. Negative-test empty, stale, malformed,
  and placeholder artifacts.
- Do not assume compatibility. The caller decides whether a contract survives;
  update every named consumer when an intentional break is authorized.
- Test disposition follows contract disposition: delete retired-contract tests,
  migrate retained behavior, and identify the existing replacement for
  redundant tests. Raw line counts are diagnostic, not a release rule.
- Bind verification to the candidate checkout, prove import provenance before
  the suite, run one full suite at a time, and poll yielded processes to
  completion or terminate and reap their scoped process group before rerunning.
- Keep private evaluator answers outside worker-readable workspaces.
- Route repair back through reevaluation. Any post-evaluation change invalidates
  the prior pass.

## Release gate

Run static validation, then lock the exact score and injected inputs:

```bash
mzt validate score.yaml
python scripts/check_score_release.py score.yaml \
  --project-root /absolute/project --write-lock
python scripts/check_score_release.py score.yaml \
  --project-root /absolute/project --lock composition-lock.json
```

The candidate digest joins evaluation to release. A digest mismatch requires a
fresh evaluation; never release a repaired-but-unrerun candidate.
Before release, compare the exact diff to the scope and to every report claim;
an unreported source edit is a failed gate even when tests pass.

For runtime work, use the command skill. For YAML details, use score-authoring.
