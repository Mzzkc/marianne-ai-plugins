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

A retained schema-v3 candidate with blocked/deferred coverage reports `partial`
and lists deferred provider/route IDs. Runner exit 3 distinguishes this from
full success. All admitted changes still require the same configured, syntax,
observation, snapshot and required-live checks; failures compensate the entire
accepted target set. A no-op with deferrals is partial, not full success.

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

The home-anchored Claude marketplace registry is compared semantically except
for each entry's runtime lastUpdated timestamp. Sources, install locations,
unknown fields and malformed contents remain governed. Known Claude security
log/session-warning files are runtime data; other security files remain governed.
Exact accepted targets always use raw byte hashes, overriding these exclusions.
