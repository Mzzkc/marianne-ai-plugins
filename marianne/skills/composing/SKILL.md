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

1. `scores/rosetta-corpus/INDEX.md` and `forces.md`. Then
   `python3 -I scores/rosetta-corpus/tools/unproven.py scores/rosetta-corpus`:
   the proof ledger says which patterns a proof score has exercised and which
   none has. Composers reach for the same seven patterns run after run
   (GH #354); a familiar pattern is not evidence that it fits, and the
   selection guide's compositions are not ranked.
2. Each selected pattern's full file, not its name or a summary. Consult its
   `proof_score:` frontmatter pointer alongside the ledger before selecting;
   `unproven.py --usage [DIR]` audits citations in produced score YAML.
3. `plugins/marianne/docs/ref/instrument-catalog.yaml` and current venue reports
   before assigning instruments; the venue owner uses `mzt doctor` when needed.
4. The relevant `${CLAUDE_PLUGIN_ROOT}/docs/ref/` syntax references before writing
   YAML; score-authoring can assist when a separate syntax specialist is useful.

Disk and runtime behavior outrank pattern prose. Inspect the selected example's
actual dependency and validation controls: a report-exists check does not enact
a behavioral gate merely because the pattern advertises one.

## Instrument selection

Choose per role. One alias (or one class) across every sheet discards the
granularity Marianne exists for: a recon sheet, a build sheet, three parallel
reviewers and a synthesis sheet want different models and budgets. Declare an
alias per role, bind it where that role plays, and for fan-out reviewers use a
`chain` with `select: [spread]` (distinct models per voice) and `balance`
(least-loaded entry at dispatch) so independence and throughput come from the
score, not from luck. A maker/judge PAIR (one analyst, one reviewer; one builder,
one verdict) is not a fan-out: `spread` only separates voices within one alias.
Cast the pair as two explicit chains in opposite orders, so the same index never
names the same profile and one unavailable head moves one seat, not both. Never
bind either seat to a capability class: a class resolves per venue, and a venue's
class layer can seat both on one model after the money is spent
(`examples/engineering/artifact-analysis.yaml`, 2026-11-09: both seats on
codex-cli; the release gate, which reads both context receipts, refused it).

Cast every seat as an alias over a BUILTIN profile with `config: {model, …}`;
name a user-layer profile only when it changes the executable, output format,
prompt delivery or error vocabulary, and say which in the design's `forces`. A
user-layer copy that only pins a model silently drops every key the builtin gains
after the copy; `mzt doctor` lists such files under "Instrument hygiene" once
nothing submitted names them.
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
- Point musicians at `$MARIANNE_SCRATCH` for probe clones, mutants and worktrees:
  the conductor exports it on every CLI/interactive sheet and deletes it when the
  job ends (`workspace_lifecycle.scratch`). A clone in a system temp directory
  outlives the job and is never reaped.
- Use Jinja `{{ }}` in prompts/injection paths and Python format `{}` in
  validations.
- Use `cli` for deterministic commands. Set
  `per_sheet_fallbacks: {N: []}` for every deterministic CLI sheet so an LLM
  cannot reinterpret a failed command.
- Give AI sheets capability-matched fallbacks, except isolated evaluators where
  fallback would destroy independence.
- An independent oracle is only as independent as the inputs it pins. When
  RED freezes blind-authored tests, freeze every input the assertions read
  (tests and map, ancestor `conftest.py` files, imported assertion helpers,
  static fixtures, golden documents), re-hash them at every later boundary,
  and ship a control that edits one fixture after RED and must be refused;
  a pin set over test modules alone is a gate a builder can walk around
  (GH #518).
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
  On Linux every CLI/interactive instrument runs under the instrument
  supervisor (`cli.command.supervise`, default on): a helper an agent disowns
  dies with the attempt, and the instrument's I/O class is `low`, so a search
  from `/` cannot stall the conductor. A profile sets `supervise: false` only
  when the binary must be the conductor's direct child.
- Keep private evaluator answers outside worker-readable workspaces.
- An exemption list is an evaluator answer. If the judged party can write "this
  difference is intended", scope each entry to exactly what may differ (a field, a
  line pattern, an exit code), compare the rest, refuse an unscoped entry, and let
  only the gate admit one. A filename that waives a whole output hid 114 failures
  in one rewrite proof (GH #530); `examples/engineering/assets/differential_compare.py`
  is the shipped shape.
- A deterministic `cli` verifier inside a repair loop must route its failure
  back into the span (`triggers.<n>.on_fail: [{goto: <builder>}]`, V224
  acknowledged) or exit 0 with a diagnostic the next sheet reads: the engine
  ends a loop with a FAILED member as `range_failed` and never re-runs the
  builder on its own, so a loop that exists in YAML can be one that cannot
  iterate (GH #513).
- A check that must fail the JOB sits on a sheet with no retries and no
  fallback (a `cli` sheet, `per_sheet_fallbacks: {N: []}`), never on the
  judgment sheet it judges: a failed attempt is retried, and a retried judge
  with the same inputs and the knowledge that REWORK fails its sheet can
  reclassify a confirmed defect as "hardening" (GH #519). Preserve each
  attempt's verdict under `review/evidence/` so approval without repair is
  visible and refusable.
- Size a loop's `cost_limit_usd` from the work, not a default, and give every
  cap-ended loop a reader: a loop whose `until` is unmet at its cap or pass
  limit proceeds with a warning, so the next stage must detect the shortfall
  (the marker absent, the record still false) and carry it to the final gate.
  A coverage loop also needs a way to name what the host cannot reach (a
  privilege, a device, a credential): an exclusion ledger with reason,
  evidence and commit, audited at the end, rather than a flat floor that
  spends the budget chasing it. When `mzt validate` answers V228 ("cost_limit_usd
  cannot stop a route that reports no cost"), the cap is inert on that venue:
  subscription routes price their tokens at $0, so `max_iterations` is the only
  bound. Do not raise the cap or remove it; set `max_iterations` to the number of
  passes the work can justify and keep `cost_limit_usd` for venues that price the
  route. A score that must stop on money alone needs a priced route in the span.
- Route repair back through reevaluation. Any post-evaluation change invalidates
  the affected pass. Inherit still-applicable evidence for unchanged subjects;
  perform required full-suite and real-environment qualification before release.

## Release gate

Run a shipped score as-is: point it at the commission with `--var` inputs and
name the run with `mzt run --job-id NAME` (the job ID, and the auto-managed
workspace when the score omits `workspace:`). Copy a score only when its
behaviour must change, and then edit the copy like code under a project/task
scoped filename matching its `name`. Concurrency and quota routing are the
venue's (instrument limits, rate-limit-aware chains), never a reason to fork;
a forked shipped score stops being the thing that gets dogfooded (GH #505).
Run required gates fail-fast and lock the exact score and injected inputs,
using the owner's complete qualified recipe:

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

To make the lock mandatory at admission, submit with `mzt run "$score_path"
--require-lock "$lock_path"`: the conductor verifies the lock against the exact
score bytes and refuses a missing, stale or malformed lock, so shell control
flow around a failed gate cannot reach RUNNING (GH #403).

For a strict release gate, use `mzt validate "$score_path" --strict` after
reviewing existing warnings. A score can acknowledge specific WARN/INFO codes
with `validate.suppress: [Vxxx]`; V012 refuses ERROR-tier and unknown codes.
The JSON result keeps its existing keys and adds `summary` and `suppressed`.

Prefer a capability class (`instrument: workhorse`) over a hard profile chain
for portable compositions: the class resolves per machine through the class-map
layers, and `mzt validate` reports the resolved chain (V325) plus every layer
path and sha256 it read under `summary.classes`. Class portability rules: no
`model` pinned against a class primary (V323), no class as an alias profile
(V321), and machine-local availability gaps surface as V311 warnings naming
the first runnable entry.

Structural gates prove a score parses and its inputs exist; they do not prove its
first sheet can run. Before release, execute the first sheet of every score (a
fresh workspace, the real injections, `--var` inputs as the fleet will pass them)
far enough that its validations judge it, and read the result: an over-cap
required injection, a `cli` sheet's prerequisite (a branch, a binary, a path), a
class that resolves to nothing, all fail there and nowhere earlier. Any sheet
that runs a whole test suite carries a MEASURED runtime from this venue at the
parallelism the fleet will use, with headroom, never an estimate: four suites on
six cores took 68 minutes against a one-hour cap that pass 3 had "reasoned" to
150 s (candidate-advantage-orchestra, 2026-11-09: three members failed at
runtime after every static gate passed; the memory-primitive orchestra carried
a 105 KB required injection the same way). A dry run is the gate row that
executes; a lock without it certifies bytes, not behaviour.

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
