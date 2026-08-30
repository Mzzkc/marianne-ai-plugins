# Stigmergic Cadenza Coordination

## Purpose

This technique teaches Marianne agents to coordinate through durable files in
the shared workspace. The primary communication path is stigmergic: agents
leave state, claims, findings, decisions, and handoffs where the next agent can
read them. A2A can supplement this with live delegation when it is available,
but A2A is not the authoritative coordination record.

## Shared Workspace

```text
workspace/
  shared/
    active/       <- flat live cadenza loaded into agent context
    plans/        <- detailed plans and task breakdowns
    findings/     <- durable fact registry and investigation reports
    decisions/    <- architectural and operational decisions
    directives/   <- composer or conductor directives
    specs/        <- relevant copied or summarized specs
    archive/      <- stale active files and historical detail
  agents/
    {name}/       <- agent-local work, reports, and cycle state
  collective/
    tasks.md      <- durable backlog
    status.md     <- cross-cycle status summary
```

Directory cadenzas are not recursive. Files that must be visible to all agents
now must be direct children of `shared/active/`.

## Active Cadenza Files

Generated generic fleets seed these starter files in `shared/active/`:

- `01-task-board.md` - current-cycle work claims.
- `02-status.md` - the current cohort state in its existing local form.
- `03-urgent-directives.md` - controlling conductor instructions.
- `04-handoffs.md` - exact subject/evidence/next-owner transitions.

Agents may add more active files, but they must keep the folder curated.

## Concurrent Write Safety

The shared active files are hot files during parallel phases. A write conflict
is normal coordination pressure, not a reason to stop.

- Read the latest file immediately before editing it.
- Prefer adding your own owner-scoped row over rewriting another agent's row.
- If the tool reports that the file changed since you read it, re-read the
  file and retry the smallest row-level change once.
- If the row already exists, update only your own row unless another agent
  explicitly asked for a change.
- If a second conflict blocks the update, write the detailed artifact under
  `shared/plans/`, `shared/findings/`, `shared/decisions/`, or
  `agents/{name}/cycle-state/`, then add a compact blocked note to your own
  status/report. Do not spin on the same shared file.

## Required Loop

When this technique is active:

1. Read all four direct files before making a plan.
2. Treat `shared/active/03-urgent-directives.md` as controlling ordinary plans.
3. Claim overlapping work in `shared/active/01-task-board.md` before starting.
4. Preserve the existing form of `shared/active/02-status.md`; add concise,
   evidence-bound status without inventing a replacement schema.
5. Record reusable facts in `shared/findings/` and decisions in
   `shared/decisions/`, with compact pointers in the relevant task or handoff.
6. Add exact subject/evidence/remaining-boundary/next-owner tuples to
   `shared/active/04-handoffs.md` when continuity crosses an owner or session.
7. Move stale detail out of `shared/active/` when it no longer needs to be in
   every prompt.

Use owner-scoped task ids such as `{agent}-T-001`. Do not allocate global
numeric ids under parallel execution; another agent can choose the same number.

## Claim Example

```markdown
| canyon-T-001 | canyon | claimed | Map workspace seeding compiler boundary. | `shared/plans/workspace-seed-plan.md` |
```

If another agent has already claimed overlapping work, update that row with a
coordination note instead of starting a competing implementation.

## Handoff Example

```markdown
- Canyon → Forge; exact score `scores/canyon.yaml` at SHA-256 `...`; compiler
  gates passed; implementation remains; Forge owns the tests-first successor.
```

Handoffs require exact evidence and the unresolved boundary. A roster name or
verbal completion claim is not an attached, transferable handoff.

## A2A Boundary

Use A2A only for live, best-effort delegation or inbox checks. Any result that
must survive process boundaries, retries, conductor restarts, or later agent
cycles must be written to the shared workspace. If A2A and cadenza artifacts
disagree, treat the durable file record as authoritative until reconciled.

## Curation Rule

The active folder is not a dump. Keep detailed reports in `shared/plans/`,
`shared/findings/`, `shared/decisions/`, or agent-local cycle state, and keep
`shared/active/` as the compact coordination layer that every agent needs now.
