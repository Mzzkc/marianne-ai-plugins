# Marianne Expert Task Map

Read `BOOTSTRAP.md` first, then choose one row. Open only the routed material.

| Intent | Playbook | Add these references | Primary verification |
|---|---|---|---|
| Write or review score YAML | `playbooks/compose.md` | `contracts/score-schema.md`, `contracts/validation-types.md`, `templates/`, `examples/golden/`, `examples/broken/` | `tools/check-score.py SCORE` |
| Run, monitor, pause, resume, or cancel | `playbooks/operate.md` | `contracts/cli-commands.md`, `evidence/implementation-status.json` | Verify an actuator exists; inspect typed state and artifacts |
| Diagnose a failure | `playbooks/debug.md` | `contracts/error-codes.md`, `examples/incidents/`, relevant claim slices | Search exact error; reproduce with the narrowest safe probe |
| Reason about architecture | `playbooks/architecture.md` | `evidence/triangulation/`, `contracts/` | Join each runtime assertion to a claim and final status |
| Modify Marianne source | `playbooks/develop.md` | relevant contract, claim, slice, and triangulation record | Targeted tests, then the repository's full applicable suite |
| Embed Marianne behind an app/tool | `playbooks/embed.md` | `contracts/cli-commands.md`, status contracts, implementation status | Validate before submit; check daemon response and typed job state |

## Capability vector

Run `scripts/preflight.py` and preserve each field independently:

- `pinned_kit`: bundled snapshot evidence is available.
- `current_source_read`: a current checkout can be inspected.
- `current_source_write_authorized`: the caller explicitly authorized edits.
- `marianne_cli`: an `mzt` client is available.
- `conductor_ipc`: the client reached a conductor.
- `marianne_harness`: this task is itself playing as a Marianne sheet.
- `online_primary_sources`: an explicit network probe reached the official URL.

A source checkout does not imply edit authority. A running conductor does not
prove a product feature is implemented. A task played by Marianne must record
the harness even if it never invokes `mzt` from inside the sheet.

Use `tools/search.sh QUERY` to find a route when the intent is ambiguous. If a
claim may have drifted beyond the pinned source SHA, state that limitation and
inspect current source before acting.
