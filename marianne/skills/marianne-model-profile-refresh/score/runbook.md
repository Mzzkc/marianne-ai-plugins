# Automatic Marianne model/profile refresh runbook

Run the full score. One research movement covers all shipped provider
assignments; deterministic admission requires the complete set before backup
and apply. No separate research framework or caller-maintained custody ledger
is needed. This updates existing integrations and never installs clients,
providers, models or authentication.

## Run

From the bundled score directory:

```bash
python scripts/run_refresh.py \
  --request-path request.md \
  --project-root /path/to/marianne/project
```

Coverage always includes every provider Marianne ships plus providers declared
by venue-owned `model-providers.yaml` or supported client metadata, including catalog-only
providers with no installed client. Do not supply selectors that reduce the
set. A focused request may constrain edits, while all shipped providers remain
research assignments. The runner binds this population and observation policy
into caller authority. The same allowed roots govern research, backup and apply;
project-root-only assumptions do not override accepted home configuration targets.

Artifact and backup bases default beneath the invoking user's home:
`~/.marianne/workspaces/model-profile-refresh` and
`~/.marianne/backups/model-profile-refresh/<UTC timestamp>`. Override them with
`--workspace-root` and `--backup-root`. Each invocation gets a unique transaction
ID. Protected transaction directories use mode `0700`, protected files `0600`;
unrelated parent directory permissions remain untouched.

## Completion and resumption

The runner observes asynchronous runtime completion and the matching terminal
transaction receipt. Submission success alone is never refresh success. It
retains the temporary technique until the transaction settles. If observation
is interrupted or the job pauses, retain the existing workspace and resume:

```bash
python scripts/run_refresh.py --resume-workspace /path/to/transaction-workspace
```

Cancelled status alone does not prove that writers have stopped; the runner
retains recovery state until the venue can establish settlement. Ambiguous
submission likewise requires job ownership reconciliation before resumption.

Do not start another transaction to resume the first or remove its temporary
technique while musicians may still need it. Terminal settlement restores the
pre-run technique. An intentional persistent installation is a separate action:

```bash
python scripts/refreshctl.py install-technique technique/SKILL.md
```

## Artifacts and outcome

Caller authority contains `refresh_scope`; inventory associates providers with
shipped providers and any known profile/catalog routes. `update-manifest.json` is schema v2, with complete
provider results, exact targets, fact references and configured expectations.
All-no-change work may have no targets. Blocked or incomplete research does not
apply. Old schema-v1 protected transactions retain recovery support.

Workspace artifacts include the concrete runtime score, inventory, manifest,
changed-path ledger, commissioning record, transaction result and receipts.
Protected backup state binds exact target preimages and authority; public
reports are not recovery authority. Known runtime/cache activity is separated
from governed profile/configuration drift by runtime-owned observation rules.

The compact receipt distinguishes providers checked, proposed/retained changes,
no-change/blocked limitations, configured and integration evidence, per-fact
live states and terminal outcome. Unsupported live routes remain unsupported.
Source URLs and parser success alone do not establish factual or live validity.

## Recovery

Required failures after backup trigger runtime compensation, including failures
that prevent the ordinary finalize movement from executing. Report rollback
only after exact restoration. Before restoring, the helper checks protected
state and recovery digests, authority, entry set, parent chains and blobs.
An unproved restore preserves working and backup state and reports manual
recovery required; never retry destructive mutation blindly. Operational logs
and unrelated files are not reverted as though the transaction owned the machine.
