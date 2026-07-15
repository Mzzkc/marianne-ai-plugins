---
name: composing
description: Use when turning a goal into a Marianne score, multi-stage AI workflow, concert, fan-out, evaluator loop, or release-grade orchestration YAML.
---

# Composing Marianne Scores

Composition designs a system of minds. The score is not ready because its YAML
parses; it is ready when its context, authority, outcomes, repair loop, and exact
release candidate are provable.

## Decide and investigate

Compose only when coordination earns its overhead: distinct stages, parallel
work, different instruments, costly downstream contamination, recovery, or
reuse. Otherwise recommend a prompt or command.

Inspect the venue and current runtime before design. Read:

1. `scores/rosetta-corpus/INDEX.md` and `forces.md`.
2. Each selected pattern's full file, not its name or a summary.
3. `plugins/marianne/docs/ref/instrument-catalog.yaml` and `mzt doctor` before
   assigning instruments.
4. The score-authoring skill before writing YAML.

Disk and runtime behavior outrank pattern prose.

## Design gate

Before YAML, write `composition-design.yaml` with these required sections:

- `goal`: statement and observable completion;
- `authority`: project root and mutation authority;
- `forces`: active forces with evidence;
- `stages`: IDs, dependencies, and produced artifacts;
- `context_flow`: source, destination, and mechanism for every load-bearing input;
- `injections`: paths, destinations, and whether required;
- `proof_obligations`: behavioral checks per artifact;
- `repair_loop`: repair stage, reevaluation stage, and maximum iterations;
- `release`: release stage, reevaluation dependency, and candidate-hash policy.

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

For runtime work, use the command skill. For YAML details, use score-authoring.
