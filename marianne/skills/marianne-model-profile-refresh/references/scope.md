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

Keep a specific request bounded to its named provider/family and relevant
active downstream references. Do not silently turn it into a system-wide
refresh. For a broad request, census all active state before selecting targets.

Require every target to be an exact canonical absolute path contained by the
caller-provided allowed roots. Require explicit naming for any eligible pinned
or frozen mutation. Preserve Gemini Pro roles when a request names only a Flash
refresh. Record a change or skip disposition for every candidate found during
the census.

Reject scope expansion after backup. If applying the accepted change reveals a
new candidate, leave it unchanged, record it, and require a separate
transaction unless the existing manifest already grants exact authority.
