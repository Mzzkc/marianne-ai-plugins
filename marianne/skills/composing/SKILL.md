---
name: composing
description: Use when designing or changing a Marianne score, persistent-agent workflow, concert, fan-out, evaluator loop, or release-grade orchestration YAML.
---

# Composing Marianne Scores

Composition designs a system of minds. The score is not ready because its YAML
parses; it is ready when its context, authority, outcomes, repair loop, and exact
release candidate are provable.
Use this skill directly from the task's authority, requirements and current evidence.
Its output is the performance design and its checked realization. Reuse supplied
decisions; sibling skills provide optional specialist help, not prerequisite invocations.

## Decide and investigate

Use Marianne for substantial execution. Compose the construction, consumer
integration, independent qualification, repair and recovery the outcome needs;
a single call or one-/two-sheet shortcut must not replace that performance.
Genuinely atomic operations may remain small within it. Sheet count is not quality.

For an unchanged qualified stock engagement, use conducting and supported venue
controls; invocation does not require a new composition design. For a new or
changed workflow, reuse the closest shipped score and justify the behavioral gap
before custom construction. Keep the whole commission owned through acceptance.

A new research subject, date, title, model or timeout is an assignment/casting
change, not by itself a design gap. First reuse a suitable person's qualified
provided engagement through task/cadenza inputs; leave its managed score intact.
Ephemeral work remains appropriate when situated learning has no future value.
Score-local model/config bindings can reuse qualified routes where supported;
do not replace distinct wrapper/tool/guard/budget behavior without equivalence proof.

Before casting, decide whether the work should reuse a persistent person,
construct a new persistent person, or use an ephemeral worker. Read
`${CLAUDE_PLUGIN_ROOT}/docs/ref/modern-agents.md` whenever future learning,
identity, relationships, or lifecycle memory may matter. Never reach for a
legacy file under `plugins/marianne/agents/` or a DJ-only `musician-XXXX`
profile as a modern-agent template.

Use current venue capability evidence; have its owner resolve consequential gaps.
Missing production readiness need not block safe construction or independent work.
For new or changed composition, read:

1. `scores/rosetta-corpus/INDEX.md` and `forces.md`.
2. Each selected pattern's full file, not its name or a summary.
3. `plugins/marianne/docs/ref/instrument-catalog.yaml` and current venue reports
   before assigning instruments; the venue owner uses `mzt doctor` when needed.
4. The relevant `${CLAUDE_PLUGIN_ROOT}/docs/ref/` syntax references before writing
   YAML; score-authoring can assist when a separate syntax specialist is useful.

Disk and runtime behavior outrank pattern prose. Inspect the selected example's
actual dependency and validation controls: a report-exists check does not enact
a behavioral gate merely because the pattern advertises one.

## Instrument selection

Match phase requirements to current qualified capabilities and the user's casting
preferences. Read [model-specific guidance](references/instrument-selection.md)
when selecting Gemini, GLM, or a vulnerability-discovery engagement.
Compare total delivery effort: context fit, modality, actual write/test capability,
privacy, entitlement, queueing, latency, review and likely repair. A cheap call
that transfers work to consumers is not a cheaper outcome. Native route ranking
and inventory assertions do not establish comparative economics or live actuation.
Reserve capacity for dependent children and integration; parallelize ready work
that can safely join its consumers.

## Design gate

Before YAML, write `composition-design.yaml` with these required sections:

- `goal`: statement and observable completion;
- `authority`: project root and mutation authority;
- `forces`: active forces with evidence;
- `stages`: IDs, dependencies, produced artifacts, actual consumers and join owners;
- `context_flow`: source, destination, and mechanism for every load-bearing input;
- `injections`: paths, destinations, and whether required;
- `proof_obligations`: behavioral checks per artifact and integrated consumer journey,
  public acceptance criteria and independent controls;
- `compatibility`: explicit `preserve`, `intentional_break`, or
  `not_applicable` policy, rationale, and every migration target;
- `test_disposition`: each removed test classified as a retired contract,
  migrated contract with replacement, or redundant contract with replacement;
- `verification_context`: `source_binding`, an `import_probe` that prints the
  imported module path, and `process_control` with `one_suite_at_a_time: true`
  plus a `yielded_process_cleanup` procedure;
- `repair_loop`: repair stage, reevaluation stage, maximum iterations, and escalation
  when the remaining delivery window cannot cover repair and qualification;
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
YAML in one unreviewed stage is not a gate. Use the separately validated stage
within existing authority; routine design review need not require user rebriefing.
The checker establishes structural conditions, not semantic completeness, an
executed design review or proof that the proposed dependency graph will deliver.

Within those existing sections, arrange construction → actual consumer → independent
review → bounded repair → reevaluation → release. Use native dependencies and
supported continuation so each authorized transition has an owner and activation;
Root should not need to recommission each join. Exercise the uncertain interface
with representative material early, preserving the full destination. Carry the
original delivery window across successors and reserve integration/repair time.
Give the principal the affected caller chain, complete representative inputs,
direct consumer/reviewer access and applicable adoption authority. Put downstream
use and an early applicable broad regression after shared-contract changes, before
more dependent construction. Budget admission through consumed result with variance,
installation and provided life, not just command duration. On repeated recovery,
require a changed premise and feasible remaining delivery reserve within that window.

## Compose

- Derive the stage DAG from artifact dependencies and selected pattern
  invariants.
- Give each artifact one owner and an outcome validation. Its owner coordinates
  directly with the actual consumer through repair and successful consumption.
  A local PASS advances that join; it does not close the whole commission.
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
  the affected pass. Inherit still-applicable evidence for unchanged subjects;
  perform required full-suite and real-environment qualification before release.

## Release gate

Use a project/task scoped filename matching the score `name`; native submission
derives its default job ID from the filename. Run required gates fail-fast and lock
the exact score and injected inputs, using the owner's complete qualified recipe:

```bash
bash -euo pipefail <<'SH'
score_path=/absolute/SCORES/project-task/project-task.yaml
project_root=/absolute/project
release_checker=/absolute/plugin/skills/composing/scripts/check_score_release.py
lock_path=/absolute/SCORES/project-task/composition-lock.json
mzt validate "$score_path"
python "$release_checker" "$score_path" --project-root "$project_root" --lock "$lock_path" --write-lock
python "$release_checker" "$score_path" --project-root "$project_root" --lock "$lock_path"
SH
```

The candidate digest joins the evaluated score and injected inputs present at checking to
release. A digest mismatch requires fresh evaluation; never release a
repaired-but-unrerun candidate. Structural PASS and a matching lock do not prove
product behavior, reviewer independence, or application-source identity. Bind
those claims to their actual executed candidate through the existing verification
and release stages. Generated outputs require proof at their actual consumer.
The base release checker requires injected files to exist when checked and locked;
it does not support deferred generated-input declarations. Use a qualified staged
handoff or route that capability gap to its owner, preserving required attachments
and behavioral checks. An installed extension needs its own applicable evidence.
Before release, compare the exact diff to the scope and to every report claim;
an unreported source edit is a failed gate even when tests pass.
When delivery includes main integration or installation, retain its owner and
independent ordinary-consumer judgment through that adoption. Hold only an actually
ungranted action; source qualification alone cannot establish installed behavior.

Return the checked design, exact subject, remaining obligations and activation needs
to the caller. Conducting can coordinate the performance; command handles operations,
expert resolves technical capability gaps and score-authoring offers YAML assistance.
None is required merely to invoke this skill or complete its authorized design work.
