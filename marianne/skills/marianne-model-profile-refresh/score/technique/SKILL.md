---
name: marianne-model-profile-refresh
description: Use when a Marianne score researches or applies bounded model, musician-profile, instrument-profile, default, catalog, or model-guidance updates.
---

# Marianne model/profile refresh transaction technique

Follow the assigned research or apply phase. Authority comes from the runtime's
digest-bound caller document, not the worker's proposed manifest or project
root alone. Never install clients, providers, plugins, models, credentials or
authentication flows. Do not launch another refresh.

## Research phase

Read the request, inventory and caller authority's `refresh_scope`. Account for
all shipped and locally declared providers in the assigned scope using current official model and
client evidence. Installed clients or reachable profiles cannot narrow scope;
providers with no local route still require an evidenced result. The
same research movement integrates their results and resolves shared-file edits.
Do not narrow broad scope to providers you happened to discover. Keep blocked
and unresolved findings explicit; never turn missing research into no-change.

Classify targets as `active`, `generated`, `pinned`, `frozen`, `retired` or
`unknown`. Only active and generator-owned generated targets are normally
mutable; eligible pinned/frozen targets require explicit naming. Search matches
are leads, not authority. Preserve defaults exactly; preserve existing roles unless the
request and evidence justify changing them. Generated consumers use their
existing generator. The shipped instrument-catalog.yaml is authoritative active
source; its generated_at/generated_by history does not make it generated output.
The companion instrument-catalog.md is derived. Locate a documented generator
for that consumer or explicitly defer it; do not invent a generator requirement
for the YAML source itself.

Write a schema-v3 JSON manifest containing the exact `transaction_id`, request,
mode `broad`, absolute `allowed_roots`, `provider_results` and
`unresolved_results` and `targets`. Every root and target must fit caller authority. Provider results:

```json
{
  "provider": "provider-id-from-scope",
  "status": "changes",
  "reason": "What current evidence establishes and why this changes local configuration",
  "evidence_urls": ["https://official.example/models"],
  "facts": [{"id": "fact-id", "model": "discovered-model-id",
             "evidence_urls": ["https://official.example/models"], "claims": {}}]
}
```

Statuses are `changes`, `no_change`, `blocked` or `deferred`. Evidence-backed
no-change is valid coverage. Missing provider rows always prevent apply.
Blocked means evidence could not support a decision; deferred means a supported
change cannot be safely included now (for example a shared-file dependency).
Blocked/deferred rows use facts: [] and explain the affected routes/files.
They produce an explicit partial outcome, never an all-clear success. Facts need unique
IDs, a model ID and their own nonempty `evidence_urls`; `claims` is optional.
Every provider result also needs a nonempty `reason`; no-change results use
`facts: []` when no facts need to drive changes. URL presence is not source support: verify that the
source actually warrants accepted claims. For every provider, state the current
relevant releases you checked and their relationship to local/catalog references.
Use specific official model/release pages where available. A generic homepage
and "catalog-only, no change" sentence is not substantive coverage. Do not
invent edits merely to make research look thorough.

Account for every `refresh_scope.unresolved` ID exactly once in
`unresolved_results`, using `{"id": "route-id", "status": "resolved",
"provider": "assigned-provider-id", "evidence_urls": ["https://official.example/models"]}`.
Resolve to an existing or newly discovered creator using primary evidence.
A new provider is permitted only when joined to an inventory unresolved ID,
and requires its own complete provider_results row. Research discovered creators
before proposing the final manifest. Do not conflate brokers and creators.
If ownership cannot be established, use status: blocked with a nonempty reason.
This defers its source files; it does not excuse missing coverage. Caller roots
and baseline providers stay fixed. Admission/backup seal the discovered manifest;
no provider, target or fact changes are allowed afterward.
Use an empty array if the scope has no unresolved routes.

Use the resolved canonical regular-file path for changes, not a symlink alias;
its exact bytes must be covered by the target backup.

Each target has an exact canonical absolute `path`, `classification`,
`disposition` (`change`), `fact_ids`, `dependency_providers`, and `checks`.
List every creator and broker on which that target's changes depend.
The runtime refuses dependencies marked blocked/deferred and whole files that
contain their inventory routes (including unresolved source_paths). If a shared
file is affected, defer every proposed change to that file. The shared catalog
and its Markdown companion are also deferred whenever any provider/route is
blocked or deferred. Do not relabel a deferred improvement as no_change.
Only status: changes may carry executable facts, and every fact must have a target. A change must
reference its accepted model facts and include bounded configured expectations:

```json
{"pointer": "/models/0/name", "equals": "discovered-model-id"}
```

or a containment expectation:

```json
{"pointer": "/runs_models", "contains": "discovered-model-id"}
```

For a text target, a check with `contains` and no pointer asserts a literal
substring. Use checks appropriate to the actual target; shared files can
reference several facts. Only actual proposed changes belong in targets. An entirely no-change
manifest uses an empty targets array. Do not create artificial edits to
satisfy the contract. No public field or value may require secret redaction.

## Apply phase

Mutation begins only after accepted admission and protected backup. Edit only
accepted change targets within the same authority used by research and backup.
No scope expansion after backup. The protected
state binds manifest/recovery digests, transaction, exact accepted paths,
parent-chain identity and caller authority. The public index is not recovery
authority. Do not rewrite protected transaction data.

Write `changed-paths.json` with schema version 1, exact transaction ID and the
sorted unique physical `changed_paths`; a no-op has an empty list. Keep secrets
out of artifacts. The runtime compares observed governed changes with this
ledger and checks syntax and configured expectations. Known operational state
is handled by its bound observation policy, never by worker-authored waivers.

Use relevant existing integration checks against candidate code. Keep their
results distinct from configured, parsed and per-fact live evidence. Unsupported
live adapters remain unsupported; never claim a route worked because its YAML
parsed. The runtime owns compensation and terminal receipts. On failed required
checks stop mutation and preserve recovery authority; do not perform improvised
rollback or keep editing around a failed gate.

Automatic refresh preserves existing default_model values exactly; a deliberate
change of default is a separate caller-authorized configuration task. Admission
rejects proposed default replacements and commissioning compares defaults to
protected preimages, including changes omitted from worker checks.

The apply cadenza receives only a compact digest-bound backup receipt. Complete
recovery data stays on disk; never paste its scope_snapshot into an AI prompt.
The backup stage checks the total immutable apply inputs against a350000-byte
budget before dispatch. Inventory size is not an excuse to cast a larger model.
Qualified service prefixes in inventory create separate broker dependencies;
provider ownership and route-service identity are different relationships.
