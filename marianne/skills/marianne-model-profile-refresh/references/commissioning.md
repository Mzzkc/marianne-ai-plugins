# Commissioning and acceptance

Commission in distinct evidence lanes:

1. **Configured:** the requested facts and exact target ledger are present.
2. **Parsed:** every physically changed JSON, JSONC, YAML, and TOML surface
   passes the applicable syntax or schema parser.
3. **Integrated:** targeted Marianne instrument/profile, score, plugin, catalog,
   and downstream-reference checks pass from the candidate source.
4. **Live-smoked:** a bounded, non-mutating probe succeeds through an already
   authenticated supported client.

Never use a configured or parsed result as a live-smoked claim. For current
Google facts, the helper may run one fixed, non-mutating, timeout-bounded prompt
with an already-installed Gemini CLI and existing API-key or complete supported
Vertex environment. It validates the model argument, filters the child
environment, accepts only the exact JSON response sentinel, and discards all
provider output. Gemini OAuth-only state and clients without a bounded adapter
are `unsupported`; missing supported authentication is `unauthenticated`;
timeouts, client errors, and invalid output are `failed`; an omitted probe is
`not_attempted`. Do not install, reauthenticate, or bypass authentication to
manufacture live evidence.

Derive physical changes from the protected bound transaction state. Require
exact equality with the sorted, unique changed-path ledger, and parse every
observed structured target even when the path is unauthorized. Fail
commissioning if an active retired reference remains without an explicit skip
disposition, a plugin/runtime digest drifts, or a required pre-existing live
contract regresses.

On any required failure, stop mutation and restore in reverse order. Emit
`rolled_back` only after exact prior bytes and metadata are proved. Treat an
unproved restore as a compensation failure, preserve all recovery evidence, and
emit a high-severity manual-recovery receipt. Keep deterministic verification
separate from live model verification in every receipt.
