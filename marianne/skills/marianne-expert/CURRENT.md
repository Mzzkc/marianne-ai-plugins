# Current capability orientation

This is a dated navigation aid, not a new universal preflight. Use the relevant
source path below and reuse still-applicable session evidence. Refresh when the
checkout, dirty overlap, installed executor, routing inventory, authority or
capability being relied upon changes. Existing qualified engagement use does not
require source-development verification or a fresh whole-system audit.

## Evidence boundary

The bundled `VERSION`, claims, source slices, triangulation and original release
verdict describe source `65f2dc3b9a0d46341813e91af74f9960dc908446`. They remain
historical evidence. This orientation was checked on 2026-10-04 against runtime
`489e0ed685046b5d341ad40d2e1a528c31e097ce`; compiler and plugin working trees had
local changes. Source paths below are relative to the runtime checkout. Source
capability is not proof of installed parity, current provider capacity or an
active engagement. A default `mzt conductor-status` response concerns that
endpoint, not every venue.

## The scheduling reversal

C029's warning-only `CronTick` describes the pinned snapshot. In the examined
current source, `src/marianne/daemon/baton/core.py:1440` invokes the supplied cron
handler, and `src/marianne/daemon/manager.py:799` constructs the recurrence
controller and wires `RecurrenceController.handle_tick` into the adapter. The
implementation lives in `src/marianne/daemon/recurrence.py`.

Executed against that source:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_recurrence_controller.py tests/test_recurrence_integration.py
```

**23 passed in 3.69s.** These temporary-state tests exercise controlled
controller, registry, baton and manager effects; this is not a live venue qualification
or authority to launch a recurring job. `ConfigReloaded` still took the
unimplemented-warning branch at `core.py:1479`. Correcting C029 does not certify
other historical limitations. Inspect each depended-on boundary before replacing
an existing mechanism or promising a capability.

## Useful implementation seams

- **Persistent engagements:** `compiler/src/marianne_compiler/sheets.py` supplies
  full, targeted and integration shapes; `agent_package.py:_compile_shape` makes
  packaged engagements finite with `self_chain=False`. A persistent person does
  not imply continuous execution. Use the modern-agent reference for owner duties.
- **Routing:** `compiler/src/marianne_compiler/capabilities.py` binds semantic
  phase requirements to verified inventory fields and fresh engagement workspaces.
  The inventory is a supplied evidence contract, not a live actuation test.
- **Dispatch and recovery:** `src/marianne/daemon/baton/dispatch.py` owns
  readiness and capacity; `adapter.py:recover_job` preserves settled work and
  attempt state. Recovery is not reconstruction of lost application permission.
- **Context and validation:** `baton/musician.py` writes delivery receipts at the
  task boundary; `execution/validation/engine.py` executes configured checks.
  `baton/core.py` can complete successful execution with zero validations.
  Neither receipts nor native COMPLETED prove product meaning or acceptance.
- **Continuation:** `daemon/manager.py:_execute_hooks_task` runs success hooks
  separately; a failed hook can downgrade its parent. Submission does not prove
  child completion. Resume resets the run clock, not the original delivery window.

Use these seams to answer a concrete capability or failure question. Topology,
consumer joins, independent acceptance and bounded repair belong to
[composing](../composing/SKILL.md); priorities and continuing outcome ownership
belong to conducting. Source inspection here does not assign the conductor
runtime maintenance or create a second custody system.
