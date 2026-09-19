# Marianne model/profile refresh task map

Use the full score for refreshes; the runtime owns transaction mechanics and
returns a compact outcome. Load only references needed for the assigned work.

| Intent or state | Route | References |
|---|---|---|
| Broad update or audit | `score/scripts/run_refresh.py`; all shipped providers must be accounted for | `references/scope.md`, `references/research.md` |
| Request focused on one provider or family | Same full score; focus edits without reducing research coverage of all shipped providers | `references/scope.md`, `references/research.md` |
| Paused/interrupted observation | Same runner with `--resume-workspace` pointing to the existing transaction workspace; preserve its authority and technique state | `score/runbook.md` |
| Research musician | Read immutable scope; produce complete evidence-backed schema-v2 manifest without mutating targets | `references/scope.md`, `references/research.md` |
| Apply musician | Edit only accepted targets after protected backup; emit exact changed-path ledger | `references/scope.md`, `references/backup-surfaces.md`, `references/commissioning.md` |
| Required check failure | Runtime compensates and verifies restoration before reporting rollback | `references/backup-surfaces.md`, `references/commissioning.md` |
| Unproved compensation | Preserve recovery and working state; report manual recovery required | `references/backup-surfaces.md` |

`refreshctl.py install-technique` is a separate intentional persistent install,
not part of ordinary refresh invocation. Do not use it to replace an active
transaction's temporary technique. Schema-v1 recovery remains supported; new
broad work uses the coverage contract.
