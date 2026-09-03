# Automatic Marianne model/profile refresh runbook

The runner captures the exact pre-run technique state, installs the bundled
transaction technique only for one fresh nine-movement Marianne score, restores
the preimage on every exit, and returns the exact `mzt run` exit code. This
includes successful runs and failures before target backup. It does not install
a provider, client, plugin, model, credential, or auth flow.

## Run

```bash
python scripts/run_refresh.py \
  --request-path request.md \
  --project-root /path/to/marianne/project
```

For an intentional persistent local technique installation, use the separate
explicit mode; the score runner never invokes it:

```bash
python scripts/refreshctl.py install-technique technique/SKILL.md
```

External defaults are relocatable beneath the invoking user's home:

- artifacts: `~/.marianne/workspaces/model-profile-refresh`;
- backups: `~/.marianne/backups/model-profile-refresh/<UTC timestamp>`.

Each invocation appends a unique transaction ID beneath both base roots. Those
transaction directories and protected recovery/technique directories are mode
`0700`; protected indices, state, and blobs are mode `0600`, independently of
the invoking umask. The runner does not chmod unrelated pre-existing parent
roots. It also renders a private transaction-local score whose concrete
Marianne workspace is beneath that transaction artifact directory. Override the
bases with `--workspace-root` and `--backup-root`. This machine's local
commissioning uses:

```bash
python scripts/run_refresh.py \
  --project-root ~/Projects/WORSKPACES/marianne-model-profile-refresh/worktrees/core \
  --workspace-root ~/Projects/WORSKPACES/marianne-model-profile-refresh/score-runs \
  --backup-root ~/Projects/WORSKPACES/marianne-model-profile-refresh/score-backups/manual
```

## Artifacts and status

Each transaction artifact root contains `authority-roots.json`, the concrete
runtime score, `inventory.json`, `update-manifest.json`, the public
`backup/index.json` mirror, `changed-paths.json`, `commissioning.json`,
`transaction.json`, `receipt.json`, and `receipt.md`. Protected recovery bytes
stay beneath the backup root with `backup/recovery-index.json` and the protected
`backup/transaction-state.json`. The latter binds the recovery-index digest,
manifest digest, transaction ID, exact accepted path spellings, resolved scope,
pre-apply parent-chain resolution and identity, and caller authority digest
before apply. The receipt distinguishes deterministic static commissioning
from live model verification.

A successful no-op has an empty changed-path list and a success receipt. A
required commissioning failure produces a rolled-back receipt after exact
restore. For Google facts, an already-installed Gemini CLI can perform one
fixed, non-mutating, timeout-bounded smoke with an existing `GEMINI_API_KEY`,
`GOOGLE_API_KEY`, or complete supported Vertex environment. Existing OAuth
state is detected by file presence only and reported as unsupported by the
bounded headless adapter. Missing auth is `unauthenticated`; timeout, nonzero
exit, or invalid output is `failed`. Provider output and credential values are
never written to artifacts. Non-Google clients remain unsupported rather than
being fabricated as live-smoked.

## Recovery

The ordered finalize movement restores automatically when a recorded required
gate fails. The wrapper also attempts restore if `mzt` itself exits before that
movement and that same transaction's protected transaction state exists, while
preserving the original `mzt` exit code. Restore preflights the state, manifest,
caller authority, exact recovery entry set, and every blob before its first
restore-attempt capture or target mutation. Modified indices,
substituted/missing/extra paths, changed or redirected parent chains, scope or
transaction mismatch, out-of-authority paths, and corrupt blobs are rejected.
Prior transaction state and receipts are never consulted. A pre-backup failure
gets its own `failed_before_backup` receipt. The separately protected technique
preimage is restored on every runner exit, including successful runs. If either
compensation reports failure, preserve backup and working state and inspect the
protected `backup/transaction-state.json` and `backup/recovery-index.json`; do
not retry destructive mutation blindly.
