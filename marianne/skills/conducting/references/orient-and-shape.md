# Orient and Shape

Use this before committing the orchestra or whenever the world model is no
longer trustworthy.

## Build the world model

Establish:

1. **Composer** — desired end state, intended meaning, non-negotiables,
   acceptance concerns, and longer-term direction.
2. **Venue libretto** — standards, conventions, existing design, safety rules,
   ownership boundaries, and local ways of working.
3. **Reality** — current artifacts, runtime state, technical constraints,
   available capabilities, active performances, scarce resources, and known
   failures.
4. **Future** — what later work this performance should enable, what contracts
   it must preserve, and which short-term choices would make the future harder.

Learn through direct reading, reversible probes, composer dialogue,
reconnaissance musicians, domain experts, and concise briefs. Technical fluency
lets the conductor ask better questions and judge reports; it is not authority
to perform the specialist's work.

If vision and libretto appear to conflict, recover intended meaning rather than
obeying the first literal formulation. Ask the composer when available. If not,
continue reversible work, preserve existing design, record assumptions, and
hold any irreversible choice that could damage the long-term vision.

## Reuse the orientation snapshot

Create one proportional **orientation snapshot**. For each load-bearing input,
record source identity, observed state, observation time or version, authority,
volatility, and a **recheck trigger**. Compile the minimum role-specific
**context packet** each musician needs. On reopen, route deltas and reread only
changed inputs or inputs whose volatility trigger fired; do not repeat full
context archaeology by default.

Name freshness by lane. A fresh checkpoint does not make the artifact
workspace, candidate, service or data, or independent judgment fresh. Record
which freshness claims a decision needs, their evidence, and their invalidation
triggers.

## Shape the performance graph

For every end state, record:

- outcome and relation to the vision;
- owner, supporters, decision authority, and control owner;
- inputs, where context lands, and missing information;
- dependencies and timing;
- artifacts and behavioral evidence required;
- shared files, services, interfaces, compute, credentials, rate limits, and
  human attention, plus disk, processes, context, provider capacity, retained
  workspaces, cleanup ownership, and stop conditions;
- downstream consumers and future contracts;
- effects on every other end state and overlapping subjects.

Classify each interaction:

- **beneficial** — one result strengthens or validates another;
- **neutral** — coexistence is safe and requires no coordination;
- **dangerous** — collision, contradiction, resource contention, hidden order,
  or incompatible assumptions require direction.

Sequence, isolate, merge, or commission an integration owner for dangerous
interactions. Do not infer safety because individual jobs are green.

## Make the first graph vertical

Decompose the end state into user-visible capabilities before completing
subsystems. Name and commission the smallest honest end-to-end journey through
the highest-uncertainty seams; it may be explicitly non-production, but every
boundary must execute. Horizontal layers that never meet a user defer contact
with exactly the risks that matter most. Interpret the composer's quality and
trust standards iteratively: an honest, explicitly non-final vertical slice
early, then deepen until the complete trusted lifecycle is proven — not
silence until every authority layer is complete.

Declare a **capability matrix** before the first large commission: the named
user-visible capabilities, their weights, and the physically exercised journey
that proves each. Every progress percentage derives from that denominator.
Documents, scores, commits, tests, and audits count only as evidence for a
capability; a conductor's intuitive percentage is not a status metric.

Give each lane an **assurance budget**: wall clock, model-call ceiling,
allowed review waves, disk, and a named escalation trigger. Limits do not
silently expand; exceptions are recorded with their reason. Timebox the
meta-build too: a system that promises fast commissioning is itself developed
in bounded working sessions with an executable product slice at each milestone.
Proportionality never relaxes security where data, identity, or authority is
sensitive — the governor limits assurance by marginal risk reduction and
journey movement, it does not abolish fail-closed boundaries.

## Cast for the end state

Choose the smallest orchestra that covers the required expertise, independence,
and throughput. Assign authorship and validation to different musicians when
bias or correctness matters. Add principals, alignment analysts, adversarial
users, dogfooders, or co-conductors when they improve trajectory visibility or
management scale.

Use deterministic commands for exact hashes, status, schema, builds, tests,
censuses, and bounded mechanical edits. Use finite musicians for bounded
qualitative work. Persistence is earned only when recurring situated memory,
relationships, and development improve future performances enough to repay its
lifecycle and resource cost. A prestigious available agent is not a reason to
persist a one-off task.

One musician with one strong proof may be enough. A fleet is justified by the
work, not by the availability of agents.

## Enter closure mode deliberately

Enter **closure mode** only when the desired end state is stable, remaining
failures are enumerable, and the evidence needed to release can be named. Make
all release gates visible, freeze scope expansion unless new material evidence
changes the subject, and choose the shortest truthful causal path through the
remaining gates. Leave closure mode when the subject, world model, or failure
set materially changes.
