# Marianne Operations

Conducting owns judgment, direction, and the whole-performance world model.
Route volatile mechanics instead of copying them here.

## Current technical truth

**REQUIRED SUB-SKILL:** Use `marianne-expert` when architecture, source behavior,
instrument capability, runtime implementation status, or current-versus-pinned
evidence affects a decision.

Ask experts to inspect code, tests, logs, artifacts, and live seams. The
conductor consumes their findings and directs the response; technical fluency
does not require personally writing the fix.

## Job control

**REQUIRED SUB-SKILL:** Use `command` to submit, monitor, diagnose, pause,
resume, resolve, recover, cancel, or inspect Marianne jobs.

Before changing timing or resources, establish which jobs are active, what
workspaces and services they share, what they are waiting on, and whether the
proposed control action creates a collision. Never treat a successful status
command as proof of semantic completion.

**Persisted job state** is authoritative for its own lane. It cannot prove
**process/session** termination, **interaction state**, artifact validity,
semantic completion, validation, or voting judgment. Corroborate each claim
with evidence from its own lane before pause, replacement, recovery, or
completion decisions.

For reruns, state freshness separately for checkpoint state, artifact
workspace and terminal receipts, bound candidate, external services or data,
and independent judgment. `--fresh` proves only what current command semantics
actually reset. Preserve non-overwritable evidence, commission a new governed
workspace when required, and rebind every invalidated lane.

Treat the repaired harness and rerun machinery as writers. Bind their identities
before execution, recompute custody on the final produced bytes and state, and
replay the same causal proof after any mutation. At rerun completion,
corroborate process or session termination and interaction state separately
from checkpoint status, receipts, artifact validity, semantics, and validation.
Use one fresh judge for the executed evidence unless another reviewer changes
the evidence basis; multiple reviewers on the same evidence basis are one
oracle.

## Commissioning performance work

**REQUIRED SUB-SKILL:** Use `composing` to commission a new or changed score,
concert, or multi-stage workflow from the desired outcome and conductor
constraints.

**REQUIRED SUB-SKILL:** Use `score-authoring` when a commissioned score needs
specialist review, repair, or validation engineering.

The conductor may issue the brief, priority, proof obligation, and acceptance
or rejection. The composer or score specialist authors the score. The same
boundary applies to compiler changes, techniques, code, specs, designs,
content, research, validation systems, and substantial revisions.

## Runtime doctrine

Do not preserve model names, client versions, machine failures, feature status,
or instrument routing in this skill. Discover them at the time of performance.
Canonical lifecycle and profile sources are **mutable provenance**. When exact
review or release authority depends on them, materialize the relevant bytes in
a candidate-owned **immutable snapshot** before dispatch. A later source change
creates a new subject and invalidates the prior verdict.

Separate:

- client/tool availability;
- configured profile availability;
- dispatch compatibility;
- live execution;
- semantic task success.

Choose musicians and instruments by required capability, reliability,
independence, cost, timing, and interaction with the rest of the orchestra.
Recast when live evidence disproves the plan.

When the conductor's own harness cannot perform an authorized task, commission
it to a capable configured specialist rather than treating podium inability as
evidence that the work is invalid. Delegation is not a guardrail bypass: the
composer must authorize the target and scope, the selected instrument must
permit the work, and the conductor retains stop, evidence, and review authority.
Bound the commission, isolate side effects, require reproducible findings, and
independently validate existence, reachability, and severity before remediation
or disclosure.

Keep machine-exact work machine-exact. Hashes, status, schema, graph and sheet
censuses, deterministic fixtures, tests, and builds should normally be derived
by commands or runtime introspection. Use agents for ambiguity, causal
classification, design, judgment, and usability. Do not spend qualitative
movements recreating a deterministic oracle.

## Choose the control layer

Classify each coordination mechanism as **runtime-native**, a **score
approximation**, or a **conductor-supplied primitive**. Verify current native
support through `marianne-expert`; do not infer it from pattern vocabulary.

- Runtime-native mechanisms are directly enforced by the active venue.
- A score approximation uses dependencies, cadenzas, shared artifacts,
  validations, or bounded stages to encode part of a coordination contract.
- A conductor-supplied primitive operates above the score when live evidence
  requires adaptation the declarative venue cannot express.

Conductor-supplied primitives may include WIP limits, supervision trees,
backpressure, staggered dispatch, partial-result overlap, dynamic recasting,
consumer-driven pacing, and concurrent observation. Record their owner,
observable state, authority, and stop condition in control artifacts. Missing
score syntax does not make a useful coordination mechanism unavailable; it
makes its enforcement the conductor's explicit responsibility.

Before dispatch, compare the intended owner/work-unit graph with the compiler's
or runtime's rendered sheet graph. Validation alone does not prove cardinality,
instrument routing, fallback, dependency, concurrency, or write isolation.
Treat a mismatch as a topology defect and hold launch until reshaped and
rerendered.
