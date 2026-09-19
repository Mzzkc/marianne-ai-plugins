# Commissioning and acceptance

Keep these evidence lanes distinct:

1. **Configured:** each declared change has fact references and configured
   expectations that hold in its structured target.
2. **Parsed:** changed structured targets pass their supported parser.
3. **Integrated:** relevant existing profile/catalog and downstream checks pass
   against the candidate source.
4. **Live-smoked:** a bounded probe succeeds through an already-integrated,
   authenticated supported client.

Target checks use JSON pointers with `equals` or `contains`; they check the
configured values the manifest actually promised. They supplement the exact
byte ledger and syntax checks, not source review or all integration tests.
Do not invent integration success when no relevant test was run.

Physical changes must equal the sorted unique changed-path ledger. The bound
runtime observation policy distinguishes known operational telemetry from
configuration and profile surfaces. Genuine out-of-manifest governed edits,
additions and deletions remain failures; the worker cannot exempt them.
Accepted target changes are always part of commissioning.

Live evidence is recorded per model fact. The existing bounded Google adapter
uses an installed Gemini CLI with supported existing authentication. Routes
without an adapter and OAuth-only routes remain `unsupported`; missing supported
authentication is `unauthenticated`; client errors, timeout and invalid output
are `failed`. Do not install or authenticate to manufacture evidence. Optional
unsupported probes are not live success; required live failures stop acceptance.

On a required failure the runtime restores exact accepted preimages. Report
`rolled_back` only after exact bytes and metadata are verified. Failed or
unproved compensation preserves recovery state and requires manual recovery.
A completed Marianne job is distinct from the transaction outcome: the runner
must observe the matching final receipt before reporting success, rollback or
failure. Attempted changes rolled back are not retained updates.
