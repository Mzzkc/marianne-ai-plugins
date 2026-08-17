# Commissioning and acceptance

Commission in distinct evidence lanes:

1. **Configured:** the requested facts and exact target ledger are present.
2. **Parsed:** every physically changed JSON, JSONC, YAML, and TOML surface
   passes the applicable syntax or schema parser.
3. **Integrated:** targeted Marianne instrument/profile, score, plugin, catalog,
   and downstream-reference checks pass from the candidate source.
4. **Live-smoked:** a bounded, non-mutating probe succeeds through an already
   authenticated supported client.

Never use a configured or parsed result as a live-smoked claim. Report missing
client support as `unsupported`, missing existing authentication as
`unauthenticated`, and an omitted probe as `not_attempted`. Do not install or
bypass authentication to manufacture live evidence.

Derive physical changes from the protected before index. Require exact equality
with the sorted, unique changed-path ledger, and parse every observed structured
target even when the path is unauthorized. Fail commissioning if an active
retired reference remains without an explicit skip disposition, a plugin/runtime
digest drifts, or a required pre-existing live contract regresses.

On any required failure, stop mutation and restore in reverse order. Emit
`rolled_back` only after exact prior bytes and metadata are proved. Treat an
unproved restore as a compensation failure, preserve all recovery evidence, and
emit a high-severity manual-recovery receipt. Keep deterministic verification
separate from live model verification in every receipt.
