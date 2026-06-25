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

- `00-cadenza-coordination.md` - the coordination contract.
- `01-task-board.md` - current-cycle work claims.
- `02-agent-status.md` - compact live status and handoffs.
- `03-findings.md` - evidence-backed facts other agents can rely on.
- `04-decision-log.md` - choices that affect other work.
- `05-directives.md` - composer or conductor instructions.
- `06-handoff-index.md` - pointers to detailed artifacts elsewhere.

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

1. Read every direct file in `shared/active/` before making a plan.
2. Read `shared/directives/` if directive files exist.
3. Claim overlapping work in `shared/active/01-task-board.md` before starting.
4. Update `shared/active/02-agent-status.md` when starting, blocking, handing
   off, reviewing, or completing material work.
5. Record reusable facts in `shared/active/03-findings.md` or a detailed file
   in `shared/findings/` with an active pointer.
6. Record decisions in `shared/active/04-decision-log.md` or a detailed file in
   `shared/decisions/` with an active pointer.
7. Add handoff pointers to `shared/active/06-handoff-index.md`.
8. Move stale detail out of `shared/active/` when it no longer needs to be in
   every prompt.

Use owner-scoped ids in shared active tables: `{agent}-T-001` for tasks,
`{agent}-F-001` for findings, `{agent}-D-001` for decisions, and
`{agent}-H-001` for handoffs. Do not allocate global numeric ids under
parallel execution; another agent can choose the same number at the same time.

## Claim Example

```markdown
| canyon-T-001 | canyon | claimed | Map workspace seeding compiler boundary. | `shared/plans/workspace-seed-plan.md` |
```

If another agent has already claimed overlapping work, update that row with a
coordination note instead of starting a competing implementation.

## Finding Example

```markdown
| sentinel-F-001 | high | sentinel | Generated scores inject `shared/active`, but compile did not seed it. | `compiler/src/.../sheets.py`, temp compile output | confirmed |
```

Findings require evidence: a file path, command output summary, test name, log
line, or exact source. Unsupported claims do not belong in shared state.

## Decision Example

```markdown
| north-D-001 | north | Treat cadenza coordination as primary and A2A as optional. | Disk artifacts survive job boundaries and can be rendered as cadenzas. | compiler, docs, tests | 2026-06-21 |
```

Decisions must include the reason and impacted surfaces.

## A2A Boundary

Use A2A only for live, best-effort delegation or inbox checks. Any result that
must survive process boundaries, retries, conductor restarts, or later agent
cycles must be written to the shared workspace. If A2A and cadenza artifacts
disagree, treat the durable file record as authoritative until reconciled.

## Curation Rule

The active folder is not a dump. Keep detailed reports in `shared/plans/`,
`shared/findings/`, `shared/decisions/`, or agent-local cycle state, and keep
`shared/active/` as the compact coordination layer that every agent needs now.
