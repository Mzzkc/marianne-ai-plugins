---
name: marianne-model-profile-refresh
description: Use when users ask to "update Marianne models", "refresh instrument profiles", "upgrade musician profiles", "audit stale model IDs", or "run the Marianne model updater".
---

# Marianne model/profile refresh

Run the complete bundled score through `score/scripts/run_refresh.py`. It owns
inventory, scope admission, backup, apply, commissioning, compensation and the
terminal receipt. The caller receives a compact outcome and any unresolved
limitation; submitting a job is not completion. There is no approval pause after
invocation within the caller's authorized scope.

This capability updates existing integrations only. Never install clients,
providers, plugins, models, credentials or authentication flows. Keep secrets
out of public inventory, manifests and receipts. Profile identity is not agent
identity: do not edit portable seeds, L1-L4 memory, lifecycle debt,
relationships or cadenza associations. For persistent-agent implications, read
`../../docs/ref/modern-agents.md` relative to this skill directory; an available
plugin-root variable is only a shortcut.

## Scope and evidence

Every refresh researches **all providers Marianne ships**: every distinct
provider in the shipped musician catalog and any explicit shipped builtin
provider declarations, plus locally declared providers. Installed clients and reachable active routes do not
narrow this denominator. Providers with no local route still receive a research
result. The caller does not need to know new release names. Missing or blocked
provider results prevent apply; evidence-backed no-change is valid coverage.
A targeted request can focus proposed edits, but cannot waive research coverage.

Preserve existing roles and defaults unless evidence and the request justify
changing them. Preserve pinned, frozen, retired, historical and unknown-authority
references according to `references/scope.md`. Search matches do not grant
mutation authority.

## Runtime ownership

The schema-v2 manifest binds provider results, exact targets and configured
expectations to the runtime's caller authority. Backup precedes mutation; the
protected transaction state binds exact paths, digests, parent-chain identity
and recovery entries. Known runtime telemetry is handled by the bound
observation policy; genuine governed configuration drift still fails checks.
The worker cannot waive an unexpected write. Failed required checks trigger
exact compensation, and an unproved restore remains a recovery failure.

Configured expectations, syntax, integration tests and live probes establish
different things. URLs alone do not prove source support; a parsed file does
not prove a route works. Unsupported live adapters remain unsupported.

The runner observes terminal state and its matching transaction receipt before
reporting success. A paused or interrupted observation retains transaction and
temporary-technique state for `--resume-workspace`; it does not remove a
technique from musicians that may still be running. Existing schema-v1 protected
transactions remain recoverable.

## Route

Read `TASK-MAP.md` and the references for your assignment. Use the full score
route when Marianne is available; do not recreate custody with manual commands.
If Marianne is unavailable, report the limitation without installing it. The
bundled helper also supports explicit deterministic recovery and maintenance.
Research/apply musicians use `score/technique/SKILL.md`, the bounded score-safe
projection, rather than recursively launching another refresh.
