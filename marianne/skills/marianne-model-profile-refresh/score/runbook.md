# Automatic Marianne model/profile refresh runbook

The runner installs the bundled transaction technique, starts one fresh
nine-movement Marianne score, and returns the exact `mzt run` exit code. It does
not install a provider, client, plugin, model, credential, or auth flow.

## Run

```bash
python scripts/run_refresh.py \
  --request-path request.md \
  --project-root /path/to/marianne/project
```

External defaults are relocatable beneath the invoking user's home:

- artifacts: `~/.marianne/workspaces/model-profile-refresh`;
- backups: `~/.marianne/backups/model-profile-refresh/<UTC timestamp>`.

Each invocation appends a unique transaction ID beneath both base roots. The
runner also renders a transaction-local score whose concrete Marianne workspace
is beneath that transaction artifact directory. Override the bases with
`--workspace-root` and `--backup-root`. This machine's local
commissioning uses:

```bash
python scripts/run_refresh.py \
  --project-root /home/emzi/Projects/WORSKPACES/marianne-model-profile-refresh/worktrees/core \
  --workspace-root /home/emzi/Projects/WORSKPACES/marianne-model-profile-refresh/score-runs \
  --backup-root /home/emzi/Projects/WORSKPACES/marianne-model-profile-refresh/score-backups/manual
```

## Artifacts and status

Each transaction artifact root contains `authority-roots.json`, the concrete
runtime score, `inventory.json`, `update-manifest.json`, the public
`backup/index.json` mirror, `changed-paths.json`, `commissioning.json`,
`transaction.json`, `receipt.json`, and `receipt.md`. Protected recovery bytes
stay beneath the backup root. The receipt distinguishes deterministic static
commissioning from live model verification.

A successful no-op has an empty changed-path list and a success receipt. A
required commissioning failure produces a rolled-back receipt after exact
restore. Unsupported or unauthenticated live access is reported as such; it is
not converted into a live-smoke claim.

## Recovery

The ordered finalize movement restores automatically when a recorded required
gate fails. The wrapper also attempts restore if `mzt` itself exits before that
movement and that same transaction's backup index exists, while preserving the
original `mzt` exit code. Prior transaction indexes and receipts are never
consulted. A pre-backup failure gets its own `failed_before_backup` receipt. If
compensation reports failure, preserve both backup and working state
and inspect the protected `backup/recovery-index.json`; do not retry destructive
mutation blindly.
