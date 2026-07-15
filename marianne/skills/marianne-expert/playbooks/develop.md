# Developing Against Marianne

## Problem

Marianne developers are most likely to break the runtime by editing the wrong layer: changing score YAML when the public interface is an instrument profile, adding prose about a technique when the runtime only resolves ECS components, or preserving native-backend wording after executor behavior moved behind generic instrument profiles. The governing boundary is that score configuration, instrument profiles, technique components, validation commands, and execution contracts are separate extension points with different trust and test requirements. Use this page when adding an instrument profile, adding a technique, writing tests for dispatch or validation behavior, or planning backend removal. Claims about Anthropic, Ollama, and `recursive_light` in the bundled evidence describe its pinned snapshot; inspect current source before treating any of those registrations or classes as present [C020, C021, C023, C024, C025].

## Mechanism

The public score interface is `JobConfig`: scores choose a primary `instrument`, optional `instrument_config`, local `instruments` definitions, per-sheet instrument overrides, prompt configuration, validations, and `techniques` by name [C037, C038, C039, C010, C011]. Relative workspace paths resolve against the score file's parent directory without confinement, so a development recipe must treat score files as trusted project input before telling a user to run one [C038].

Add an instrument profile by defining an `InstrumentProfile` shape, not by adding a new bespoke executor first. A profile names the instrument, declares `kind` as `cli` or `http`, lists capabilities and models, chooses a default model, and then fills either CLI command/output parsing or HTTP connection fields [C020, C023, C024, C025]. CLI profiles describe subprocess construction, environment variables, stdin prompting, MCP config passing, output formats, token extraction, and interactive TUI support [C020]. HTTP profiles may claim only wire schemas the current generic executor actually implements. Add a reusable schema codec when another wire contract is required; do not create a provider-named Python executor as an architectural exception.

Add a technique by declaring a named `TechniqueConfig` under `techniques`, selecting `kind: skill`, `kind: mcp`, or `kind: protocol`, and setting `phases` to the agent cycle phases where it is active; `"all"` activates it everywhere, and an empty list disables it [C010, C011, C012]. Skill techniques inject text methodology as cadenza context, MCP techniques point at registered MCP pool servers, and protocol techniques carry coordination wiring [C010, C012, C014]. The router classifies output shapes including prose, code blocks, tool calls, and the exact `A2A_REQUEST` enum member; it routes and classifies but does not turn every protocol surface into durable execution [C013, C026, C027, C028].

Test patterns should follow the layer being changed. For scheduling and concurrency, test `dispatch_ready()` as a stateless free function; it enforces global concurrency, per-instrument/model concurrency, rate-limit skips, and stagger delays [C004, C005, C006, C007, C008]. For validation behavior, test retryable validation types and process lifecycle boundaries; `command_succeeds` is an implemented_security_sensitive privileged bash surface for trusted score authors, spawns with `start_new_session=True`, refuses daemon process-group hijacking, and terminates validation process groups with SIGTERM, a two-second grace period, then SIGKILL [C015, C016, C017, C018]. For prompt/config changes, distinguish validation path expansion using Python `.format()` from prompt rendering using deferred Jinja2 double-brace syntax [C001, C002, C003, C039].

At the pinned SHA, `AnthropicApiBackend` and `OllamaBackend` still existed [C020, C022, C023, C024, C025]. That is historical evidence, not current architecture. Re-enumerate current importers, registrations, profile capabilities, wire behavior, and tests before acting. A profile name alone does not prove an executor preserves endpoint, authentication, response, error, usage, streaming, or tool-loop semantics.

Compatibility is an authority decision, not a default. Record compatibility authority
before a refactor: `preserve`, `intentional_break`, or
`not_applicable`, plus the consumers/examples that must change. An unpublished
single-user surface may be intentionally broken when the composer says so;
do not manufacture legacy aliases for hypothetical users.

Classify every removed test by contract disposition:

1. **Retired** — the product behavior is intentionally removed. Delete the test
   and update profiles, capabilities, docs, defaults, and consumers so none
   still claim it.
2. **Migrated** — the behavior remains behind a new boundary. Write and observe
   the replacement test before deleting the implementation-coupled one.
3. **Redundant** — another current test already proves the same contract. Name
   that replacement before deletion.

Tests of deleted class names, registration bridges, and SDK mock targets are
usually retired. Wire envelopes, error mapping, token usage, tool behavior, and
public discovery are product contracts only when the new profile/capability
surface still promises them. Raw deleted-line counts are warnings, not gates.

The clean provider boundary is generic CLI and HTTP executors plus schema
codecs. Provider-named YAML files are data presets, not architectural
exceptions, and should ship only when the composer wants that instrument as a
first-class product surface. Before the final claim, compare the exact diff to
the stated scope; never report that a subsystem was untouched while its files
remain modified.

Verification must execute candidate source, not whichever editable checkout a
shared virtual environment happens to contain. Record a candidate-source
binding such as `PYTHONPATH="$PWD/src"`, then run an import provenance probe
that prints `package.__file__` (and the load-bearing submodule `__file__`) before
tests. Use the same interpreter and binding for targeted and full verification.
Run one full suite at a time. If a tool yields a running process, retain its
handle and poll it to completion; before any rerun, terminate and reap only that
scoped process or process group. A second suite beside an abandoned first suite
is not independent verification.

## Evidence

The pinned evidence establishes instrument profiles as the public extension surface and records the provider topology that existed at its source SHA [C020, C021, C023, C024, C025]. Use it to identify historical contradictions, then use current source and tests to state the present executor set. Never turn a pinned class inventory into current release guidance.

Technique extension is implemented through ECS-style component configuration: `TechniqueKind` defines skill, MCP, and protocol; `TechniqueConfig` records kind and phase activation; runtime resolution determines active techniques for a sheet; the router classifies outputs; and interface generation emits compact Python stubs for MCP tools [C010, C011, C012, C013, C014]. A2A is only partially implemented beyond routing: inbox state is in memory only, and completion/failure events are serialized for observers but not executed by the runtime [C026, C027, C028].

Dispatch and validation test seams are source-backed. `dispatch_ready()` is the dispatch unit to test and enforces global concurrency despite one stale configuration reference denying enforcement [C004, C005]. Per-model limits, rate-limit gates, and stagger comparisons are implemented separately [C006, C007, C008]. Validation commands are powerful process surfaces: retryable types include `command_succeeds`, command validation runs in a separate process group, the guard against sharing the daemon process group exists but is implemented_untested, and cleanup kills the group on exit paths [C015, C016, C017, C018].

The non-extension surfaces matter because developers often overclaim them while documenting new features. The docs say `CronTick` submits and reschedules jobs, but source/tests show it only logs an unimplemented warning. Treat spec_only as runtime truth and record the scheduler prose as stale or contradicted [C029]. The docs say `ConfigReloaded` rebuilds pending sheets, but source/tests show it only logs an unimplemented warning. Treat spec_only as runtime truth and record reload prose as stale or contradicted [C030]. The docs say grounding hooks validate outputs, but source/tests show configuration validates structurally and runtime does not invoke hooks. Treat config_only_runtime_unwired as runtime truth and record active-output-validation prose as stale or contradicted [C031]. The docs say a module-level orphan-reaping disabled flag exists, but source/tests show cleanup methods are inline no-ops. Treat known_broken_safety_noop as runtime truth and record the flag claim as false [C032, C033].

## Trap

Tempting sentence: "To add a provider, create a native backend and document it as a native HTTP executor."

Correction: "Add a profile-driven CLI or a supported generic HTTP schema; when a new wire contract is necessary, add a reusable codec at the shared boundary." The consequence of the tempting sentence is a forked execution architecture and stale docs that make downstream developers test the wrong module [C021, C023, C024, C025].

Tempting sentence: "A technique with protocol config gives durable A2A task completion semantics."

Correction: "Technique routing and A2A request classification are implemented, but A2A runtime state is in-memory only and completion/failure events are observer-serialized, not executed." The consequence is false reliability claims across daemon restarts or completion workflows [C013, C026, C027, C028].

Tempting sentence: "Validation commands are just tests, so any score can run them."

Correction: "`command_succeeds` is privileged bash for trusted score authors, and relative score paths resolve without confinement." The consequence is handing command execution and path escape capability to untrusted score input [C015, C038].

## Verify

1. For an instrument profile change, run the current profile discovery/check path, then inspect whether execution uses CLI profile fields or a supported shared HTTP schema. Reject provider-specific executor classes unless current architecture and explicit composer authority require a shared codec instead [C020, C021, C023, C024, C025].
2. For a technique change, verify the score declares `kind`, `phases`, and kind-specific config; then test active-technique resolution for the intended phase and avoid claiming executed A2A completion semantics [C010, C011, C012, C026, C027, C028].
3. For dispatch changes, test `dispatch_ready()` directly for global ceiling, per-instrument/model ceiling, rate-limit skip, and stagger behavior; include a stale-doc check if any prose says global concurrency is not enforced [C004, C005, C006, C007, C008].
4. For validation changes, label `command_succeeds` as trusted-author bash before any recipe uses it, assert separate process-group spawning and cleanup, and remember the daemon-process-group guard is implemented_untested [C015, C016, C017, C018].
5. Scan the page or patch for "schedules," "reloads," "grounds," "reaps," and "native." Revise any sentence that turns `CronTick`, `ConfigReloaded`, grounding hooks, orphan cleanup, or generic provider execution into an implemented runtime feature [C021, C023, C029, C030, C031, C032, C033].
6. For pinned claims, cite the claim ID. For current-worktree claims, cite the
   live path, HEAD, dirty fingerprint, and verification command. Use official
   current sources for external facts. Never force a current observation into
   an old claim ID merely to satisfy the bundle taxonomy.
