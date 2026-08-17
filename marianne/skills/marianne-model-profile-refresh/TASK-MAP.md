# Marianne model/profile refresh task map

Load the smallest route that covers the current invocation. All routes retain
the same no-approval-pause, updates-only, bounded transaction contract.

| Intent or state | Route | Required references |
|---|---|---|
| Direct-agent update or audit with Marianne available | Run the complete transaction through `score/run_refresh.py`; use the helper subcommands in `score/scripts/refreshctl.py` only for deterministic transaction stages. | `references/scope.md`, plus `references/research.md` for current facts, `references/backup-surfaces.md` before backup, and `references/commissioning.md` before acceptance |
| Direct-agent update without Marianne | Execute the same uninterrupted stages directly. Use `score/scripts/refreshctl.py` for deterministic inventory, manifest validation, backup, static commissioning, restore, receipt, and lock operations; perform only the bounded research and apply judgments between those gates. | All four references, loaded at their named stage |
| Marianne musician research assignment | Produce only the evidence-backed, authority-bounded update manifest required by the injected score-safe technique. | `references/scope.md`, `references/research.md` |
| Marianne musician apply assignment | Modify only accepted targets after the runtime has written the compensation record; produce the exact changed-path ledger. | `references/scope.md`, `references/backup-surfaces.md`, `references/commissioning.md` |
| Failed commissioning with intact backup | Stop mutation and invoke deterministic restore; verify exact pre-run state before reporting `rolled_back`. | `references/backup-surfaces.md`, `references/commissioning.md` |
| Failed compensation or unproved restore | Preserve both backup and working state, emit a high-severity manual-recovery receipt, and stop. Never retry destructive mutation blindly. | `references/backup-surfaces.md`, `references/commissioning.md` |

Use `score/technique/SKILL.md` only inside score musician phases. Use this
public router for direct-agent orchestration and progressive reference routing.
