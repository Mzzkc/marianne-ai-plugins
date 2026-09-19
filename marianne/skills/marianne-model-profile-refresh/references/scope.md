# Scope classification

Classify every discovered candidate before mutation. Treat search matches as
leads, never as authority.

| Classification | Meaning | Default disposition |
|---|---|---|
| `active` | Current built-in or private profile, musician, catalog, fleet default, or operational guidance | Eligible when relevant to the requested provider/family |
| `generated` | Current output derived from an authoritative active source | Update through its generator |
| `pinned` | Score-local or project-local model choice whose exact version preserves reproducibility | Skip unless explicitly named |
| `frozen` | Versioned migration, release receipt, lock, or historical benchmark | Skip unless explicitly named |
| `retired` | Inactive configuration retained for recovery or history | Skip and report |
| `unknown` | Ambiguous ownership or lifecycle | Skip and report rather than infer authority |

The research denominator is always all providers Marianne ships: distinct
provider values in the shipped musician catalog plus explicit builtin provider
declarations. Local installation and active route reachability never remove a
provider. A catalog-only provider may have no routes but still requires an
evidenced result. Venue-owned `.marianne/model-providers.yaml` metadata and supported native
client provider configuration add local providers before scope is sealed. Known catalog model identities also
associate local routes. Unknown, pinned and frozen profile classifications
preserve their mutation limits without excluding their provider from research.
Unrecognized model routes remain explicit unresolved questions; repeated local
aliases share one question with their source paths retained. Caller authority's `refresh_scope` binds it before research.

A request naming a provider or family may focus mutations; it must not narrow
research coverage. Missing or blocked results stop apply. Broker client names
do not determine provider identity. Unresolved concrete model associations need
explicit supported resolution; generic catalog prose about broker capability is
not a concrete model route.

Require every target to be an exact canonical absolute path contained by the
caller-provided allowed roots. Require explicit naming for any eligible pinned
or frozen mutation. Preserve specialized roles and defaults unless the request and evidence
justify changing them. Record a change or skip disposition for every candidate found during
the census.

Reject scope expansion after backup. If applying the accepted change reveals a
new candidate, leave it unchanged, record it, and require a separate
transaction unless the existing manifest already grants exact authority.

## Local provider identities

The updater reads `model-providers.yaml` in the project or authorized user
`.marianne` directory. This is updater metadata, not an instrument profile:

```yaml
schema_version: 1
providers:
  vendor-id:
    models: [exact-model-id, exact-alias]
```

Use source-supported provider identities and exact model strings. The updater
also reads explicit provider service keys and namespaced model IDs from standard
OpenCode `opencode.json` configuration. It does not infer a model vendor from a
broker name. Other formats or unrecognized routes remain explicit unresolved
items until supported mappings are supplied. Invalid/conflicting metadata stops
census instead of silently dropping a provider.

Do not add `provider` fields to native Marianne instrument or model entries:
the current InstrumentProfile/ModelCapacity schemas forbid those extra fields.
Maintain this separate mapping when the catalog cannot identify a local model.
Unknown or pinned profiles remain protected from edits even when their provider
is added to research coverage. Mappings must exist before the runner seals scope.
A direct agent follows the same all-shipped-plus-local denominator and can
research unknown identities before admission; it cannot omit them to proceed.

Outside a Marianne source checkout, census uses this installed plugin's catalog
and available installed Marianne builtin resources. An ordinary application
working directory does not need its own copy of Marianne source.
