# Marianne Expert Runtime Bootstrap

## Problem

This bootstrap prevents a capable agent from treating Marianne vocabulary, stale
documentation, or future-facing design as executable runtime truth. Marianne is
a score-based orchestration system: composers write YAML scores, the conductor
daemon owns execution state, the baton dispatches sheets, musicians execute
through instruments, and validations decide whether outputs satisfy the score
contract [C002, C003, C004, C015]. The likely wrong action is to read only the
music metaphor and assume every named surface is implemented, restart-safe, or
security-neutral [C026, C027, C028, C029, C030, C031, C032, C033]. The boundary
that creates the mistake is source precedence: executable code and tests win,
generated evidence records the snapshot, documentation explains intent only
when code does not refute it, and stale prose is drift evidence [C005, C019,
C021, C023, C029, C030, C031, C033, C047, C048]. This document is the always
loaded one-read mental model for acting inside the Marianne Expert Runtime Kit;
every load-bearing behavior statement cites the triangulated claim IDs from
`triangulation/triangulation.jsonl` [C001, C002, C003].

Before using this snapshot, run `scripts/preflight.py`. The bundle is evidence
for its pinned SHA, not a substitute for a live checkout. For current behavior,
current worktree source and tests outrank every bundled claim. Fingerprint dirty
files so later observations remain attributable. Online official sources are
appropriate for current external facts, but do not override executable local
behavior. Session access and product implementation status are separate axes:
being played by a Marianne score proves a Marianne harness is present; it does
not prove cron, grounding, A2A persistence, or any other feature is wired.

Evidence map:

- Rendering and validation syntax: prompt templates use Jinja2 double braces,
  while validation paths use Python single-brace `.format()` expansion [C001,
  C002, C003].
- Dispatch and concurrency: `dispatch_ready()` is a stateless free function
  that enforces global, per-model, rate-limit, and stagger gates [C004, C005,
  C006, C007, C008].
- Technique routing and compact interfaces: techniques are ECS-style `skill`,
  `mcp`, or `protocol` components resolved during agent-cycle phases, with
  routing across prose, code, tools, and A2A requests and compact MCP stubs for
  prompt economy [C010, C011, C012, C013, C014].
- Validation command safety: Marianne defines nine retryable validation types,
  runs command validations in new sessions, refuses daemon-pgid sharing, and
  terminates validation process groups with SIGTERM, a two-second grace period,
  then SIGKILL [C015, C016, C017, C018].
- Backend snapshot at the pinned SHA: instrument profiles and backend clients
  are not the same layer; `recursive_light` runs through the generic
  OpenAI-compatible path, while `AnthropicApiBackend` and `OllamaBackend`
  remain specialized native clients [C020, C021, C022, C023, C024, C025].
  Re-enumerate current consumers and behavior before extending, relocating, or
  deleting these paths; the bundle does not decide their current disposition.
- A2A limits: A2A routing has in-memory runtime state, while completed and
  failed A2A task events are defined and observer-serialized but not executed by
  runtime propagation [C026, C027, C028].
- Spec-only or runtime-unwired surfaces: `CronTick`, `ConfigReloaded`, and
  grounding are present as event or config surfaces, but scheduling, reload, and
  grounding hooks are not active runtime controls [C029, C030, C031].
- Process and orphan cleanup behavior: process startup uses locked PID files,
  but orphan reaping is a known-broken inline safety no-op with no module-level
  disabled flag [C032, C033, C034].
- CLI, costing, paths, prompt config, and compatibility aliases: version output,
  uncertain cost fallback, job-level state backend selection, score-relative
  workspace paths, prompt-template exclusivity, and old terminology aliases are
  implemented [C035, C036, C037, C038, C039, C040].
- Status enums, schema versions, severity, error categories, and capture limit:
  job states, sheet states, outcome categories, SQLite schema version, learning
  schema version, severity ordering, error category parsing, and output capture
  limit are implemented with corrected caveats where noted [C041, C042, C043,
  C044, C045, C046, C047, C048].

## Mechanism

Think in two Mariannes. The first Marianne is the product/runtime: it executes
scores through a conductor daemon, baton event loop, dispatch function, musician
adapter, instruments, validations, state stores, and learning records [C004,
C012, C015, C034, C041, C042, C043, C044, C045]. The second Marianne is the
authoring/spec Marianne: it uses the same score vocabulary to describe future
or partial capabilities, but those names do not become runtime behavior until
source and tests wire them into the product/runtime [C027, C028, C029, C030,
C031]. The bootstrap reader must keep those Mariannes separate: "defines" may
mean an event class, "configures" may mean a schema field, and "implements"
means executable behavior exists for the stated boundary [C026, C027, C028,
C029, C030, C031].

The stable vocabulary is musical but concrete. A composer writes a declarative
YAML score; the score expands into sheets, where each sheet is a first-class
execution unit with identity, instrument information, prompt data, context
injection, and validations [C002, C003, C040]. The conductor daemon owns process
and job lifecycle surfaces, including PID-file locking when starting the daemon
[C034]. The baton owns event-driven coordination, and `dispatch_ready()` is the
stateless free function that moves eligible sheets toward execution through a
callback rather than as a `BatonCore` method [C004]. A musician is the execution
adapter path that renders prompt context, resolves techniques, invokes an
instrument/backend profile, captures output and cost, and reports results for
validation and state update [C003, C012, C036, C048]. An instrument profile is
not necessarily a native Python backend; profile registration can point to
generic HTTP/OpenAI-compatible execution, plugin CLI execution, or one of the
remaining specialized native clients [C021, C023, C024, C025].

The two-syntax rule is non-negotiable. Prompt templates are raw Jinja2
templates stored on `Sheet` and rendered at dispatch time, because cross-sheet
context can exist only after earlier sheets complete [C002, C003]. Validation
paths are expanded by Python `str.format()` with single-brace placeholders such
as `{workspace}` and `{sheet_num}`; using Jinja-style `{{ workspace }}` in a
validation path is the wrong syntax for that lifecycle point [C001]. Prompt
syntax and validation syntax differ because they run in different engines at
different times, not because the project inconsistently names placeholders
[C001, C002, C003].

The execution lifecycle starts from parsed score data and constructed sheet
entities, then waits for baton state to make sheets ready [C002, C003, C004].
`dispatch_ready()` inspects ready sheets, stops when the global concurrency
ceiling is full, applies per-`instrument:model` limits with per-instrument
fallback, skips currently rate-limited instruments, and spaces same-instrument
bursts with a monotonic stagger gate when configured [C005, C006, C007, C008].
The docs say one configuration reference denies enforced global concurrency,
but source/tests show `dispatch_ready()` enforces the global ceiling; treat
source/tests as runtime truth and record the contrary prose as stale [C005].
Once a sheet executes, validations determine acceptance; command validations
are powerful and security-sensitive because `command_succeeds` is privileged
bash intended for trusted score authors, and the engine contains process-group
guards rather than a sandbox boundary [C015, C016, C017, C018].

Technique support is implemented as a compact routing layer, not as vague
prompt decoration. The ECS-style technique config defines component kinds
`skill`, `mcp`, and `protocol`; a technique declares its kind; the baton resolves
active techniques for a sheet during agent-cycle phases [C010, C011, C012].
The router classifies output categories including prose, code block, tool call,
and the exact enum member `A2A_REQUEST`, with routing priority omitted from the
short claim but present in the design evidence [C013]. The interface generator
creates compact Python stubs for MCP tools to reduce prompt token usage [C014].

Backend reality is sharper than the older docs. The docs say
`recursive_light` is a native backend, but source/tests show it is registered
and operational through the generic OpenAI-compatible/OpenRouter-shaped HTTP
path with no dedicated native backend module; treat the registered generic path
as runtime truth and record native-backend wording as contradicted [C021]. The
docs say the backends package contains native HTTP executors, but source/tests
show only `AnthropicApiBackend` and `OllamaBackend` remain specialized native
clients while generic HTTP executors were retired or moved under
execution/instruments; treat those two clients as runtime truth and record broad
native HTTP wording as ambiguous or stale [C023, C024, C025]. The Anthropic SDK
is a hard dependency, and the backend pool still carries an Anthropic doctrine
exception, but that does not make every HTTP-profile instrument a specialized
native backend [C020, C022, C024].

A2A is partial. A2A runtime structures such as `_a2a_inboxes` are in memory and
not checkpointed, so they are not restart-persistent [C026]. `A2ATaskCompleted`
and `A2ATaskFailed` are defined event classes and serialized observer surfaces,
but execution does not fire or handle them as propagation events [C027, C028].
That means a score may route A2A requests within a running process boundary,
but this kit must not promise durable inbox recovery or completed/failed task
event execution [C026, C027, C028].

Several surfaces are deliberately not runtime capabilities. The docs say
`CronTick` submits and reschedules jobs, but source/tests show the baton event
loop only logs an unimplemented warning; treat the warning-only handler as
runtime truth and record scheduling prose as stale [C029]. The docs say
`ConfigReloaded` rebuilds pending sheets, but source/tests show the handler only
logs an unimplemented warning; treat that as spec-only runtime behavior and
record rebuild prose as stale [C030]. The docs say grounding performs output
validation, but source/tests show grounding configuration validates
structurally while runtime does not invoke grounding hooks; treat config-only
runtime-unwired status as truth and record active-integrity wording as stale
[C031].

Process cleanup has a safety-shaped negative space. Orphan cleanup is a
known-broken safety no-op motivated by observed WSL2 shutdown risk [C032]. The
docs say or imply a module-level disabled flag exists for orphan reaping, but
source/tests show there is no such flag and the relevant method bodies hardcode
no-op behavior; treat the inline no-op as runtime truth and record the flag
claim as false [C033]. PID-file locking is implemented with `fcntl.flock()` at
conductor start, so single-daemon startup coordination exists even though
orphan reaping is disabled [C034].

Configuration and compatibility have precise boundaries. The CLI version
callback prints `marianne.__version__` [C035]. Cost tracking falls back to
`cost_uncertain` and zero dollars when an instrument lacks pricing [C036].
`JobConfig` supports `state_backend` values `json` and `sqlite`, but
`DaemonConfig` state backend remains SQLite, so do not promote job-level
support into a daemon-wide JSON state claim [C037]. Relative workspace paths in
score YAML resolve against the score file parent without confinement, which is
security-sensitive for untrusted scores because `..` or absolute paths can
escape expected workspace assumptions [C038]. `PromptConfig` rejects
simultaneous inline `template` and `template_file` values [C039]. `Sheet`
preserves backward-compatible aliases for old `stage`, `instance`,
`fan_count`, and `total_stages` terminology while the new vocabulary uses
`movement`, `voice`, `voice_count`, and `total_movements` [C040].

Status and diagnostic constants are part of the mental model because downstream
tools branch on them. `JobStatus` has seven states: `PENDING`, `RUNNING`,
`COMPLETED`, `FAILED`, `PAUSED`, `PAUSED_AT_CHAIN`, and `CANCELLED` [C041].
`SheetStatus` has eleven scheduling states from `PENDING` through `CANCELLED`
[C042]. `OutcomeCategory` has six outcome classes [C043]. The SQLite state
backend schema version is 4, and the learning store base schema version is 15
[C044, C045]. `Severity` is an `IntEnum` where lower numeric values represent
higher severity [C046]. The original claim says `ErrorCode.category` parses the
second digit, but source/tests show it reads `value[1]`, the first numeric digit
after `E`; treat first-digit parsing as runtime truth and record second-digit
wording as false [C047]. Output capture uses `MAX_OUTPUT_CAPTURE_BYTES = 51200`
bytes, retaining trailing output; if the stale 10KB test docstring appears,
treat the 50 KiB constant and assertions as runtime truth [C048].

## Evidence

The evidence basis is the triangulated 48-claim bundle in this workspace, with
`evidence/claims.jsonl` identifying claim text and source locations and
`triangulation/triangulation.jsonl` assigning final status [C001, C002, C003,
C004, C005, C006, C007, C008]. Source slices and direct source reads verify the
runtime split between Jinja prompt rendering and Python `.format()` validation
path expansion [C001, C002, C003]. Direct source reads also verify that
`dispatch_ready()` is a free function with explicit global concurrency,
per-model/per-instrument, rate-limit, and stagger checks [C004, C005, C006,
C007, C008].

The implemented core includes score execution, baton engine, conductor daemon,
validations, techniques ECS, learning store, compiler, instrument profiles, MCP
pool, and the two specialized native clients named in the status evidence
[C010, C011, C012, C014, C015, C024, C025, C034, C044, C045]. The implemented
but security-sensitive surfaces include privileged validation commands and
score-relative path resolution without confinement [C015, C038]. The
implemented but security-risk surface includes the baton event inbox as an
intentionally unbounded `asyncio.Queue`, which can create daemon OOM/DoS risk
if event production outruns consumption [C009].

The partial, spec-only, unwired, stale, and false surfaces are as important as
the implemented surfaces. A2A runtime state is partially implemented and
in-memory only [C026]. A2A completion and failure events are spec-only
execution surfaces serialized for observers, not fired or handled by execution
[C027, C028]. `CronTick` and `ConfigReloaded` are spec-only warning handlers
[C029, C030]. Grounding is config-only runtime-unwired [C031]. Orphan cleanup is
a known-broken safety no-op, and the alleged module-level reaping flag is false
[C032, C033]. The `claude_cli_legacy` relocation wording in the backends
docstring is stale and must not become a compatibility claim [C019]. The output
capture limit is implemented at 51,200 bytes despite a stale 10KB test comment
[C048].

The backend contradiction cluster is the highest-risk naming trap in this kit.
`recursive_light` is implemented via a generic OpenAI-compatible path and has
no dedicated native backend module [C021]. The backends package contains only
`AnthropicApiBackend` and `OllamaBackend` as specialized native Python clients;
any broader native HTTP executor wording must name those two and explain that
generic executors were retired or relocated [C023, C024, C025]. The Anthropic
SDK dependency and doctrine exception support the Anthropic native client, not
a general claim that all HTTP instruments use native backend modules [C020,
C022, C024].

## Trap

Tempting sentence: "Marianne already has scheduling, config reload, grounding
integrity checks, restart-persistent A2A, and native backends for every HTTP
profile." Correction: `CronTick` and `ConfigReloaded` are spec-only warning
handlers, grounding is config-only runtime-unwired, A2A runtime state is
in-memory only, and native backend language must distinguish generic
OpenAI-compatible profile execution from `AnthropicApiBackend` and
`OllamaBackend` [C021, C023, C026, C029, C030, C031].

Tempting sentence: "Validation paths and prompts both use `{{ variable }}`."
Correction: prompts use Jinja2 double braces at dispatch time, while validation
paths use Python single-brace `.format()` expansion [C001, C002, C003]. The
concrete consequence is a score that looks readable in prose but fails
validation path expansion or checks the wrong file [C001].

Tempting sentence: "The cleanup flag can be toggled to reap orphan backends."
Correction: source/tests show no module-level disabled flag, and orphan reaping
is hardcoded as an inline no-op because active cleanup caused WSL2 shutdown
risk [C032, C033]. The concrete consequence is an operator searching for a flag
that does not exist instead of treating orphan cleanup as a known-broken safety
boundary [C033].

Tempting sentence: "Error categories come from the second numeric digit."
Correction: source/tests show `ErrorCode.category` reads the first numeric
digit at `value[1]` [C047]. The concrete consequence is wrong error routing for
codes such as `E103`, `E204`, or `E999` [C047].

## Verify

Before publishing or acting from this bootstrap, check the document against the
triangulation file: every factual runtime sentence must carry an adjacent
`[C###]` citation, and every citation must exist in
`triangulation/triangulation.jsonl` [C001, C048]. Scan runtime verbs: use
"implements" only for implemented behavior, "defines" for schemas/events,
"serializes" for observer-visible but non-executed events, "configures" for
config-only surfaces, and "does not" for contradicted or unwired behavior
[C026, C027, C028, C029, C030, C031, C033]. Inspect the final status for every
claim used: preserve `implemented_with_stale_docs`, `implemented_security_sensitive`,
`implemented_security_risk`, `implemented_untested`, `partially_implemented`,
`spec_only`, `config_only_runtime_unwired`, `known_broken_safety_noop`,
`false_claim`, `stale_docstring`, and `implemented_with_stale_test_comment`
instead of smoothing them into generic "supported" language [C005, C009, C015,
C017, C019, C026, C027, C028, C029, C030, C031, C032, C033, C038, C047, C048].

Run these manual checks when editing: confirm the evidence map includes all
required clusters; confirm the two-syntax rule remains prompt/Jinja versus
validation/`.format()`; confirm `recursive_light` is never described as a
dedicated native backend; confirm the native-client boundary names
`AnthropicApiBackend` and `OllamaBackend`; confirm A2A completion/failure
events are not described as executed; confirm A2A runtime state is not described
as restart-persistent; confirm `CronTick`, `ConfigReloaded`, and grounding do
not receive active runtime verbs; confirm orphan cleanup remains a no-op with no
toggle flag; confirm job-level JSON state support is not expanded into a daemon
JSON-state claim [C001, C002, C003, C021, C023, C024, C025, C026, C027, C028,
C029, C030, C031, C032, C033, C037].

Use source precedence for contradictions: code and tests beat docs, source
slices beat stale comments, and corrected behavior from
`evidence/implementation-status.json` beats original disputed wording [C005,
C019, C021, C023, C029, C030, C031, C033, C047, C048]. Validate the file shape
against `chapter-spec.yaml`: one H1, required sections in order, bootstrap word
count inside the allowed range, evidence map present after the problem, trap
section naming tempting wrong sentences and consequences, and this no-overclaim
block present after the required sections [C001, C048].

## Do not overclaim

- Memory system, unconscious local model, smart conductor, concierge Telegram,
  and maestro TUI are spec-only in the implementation-status snapshot, not
  implemented runtime capabilities [C029, C030, C031].
- A2A completion and failure events are defined and observer-serialized, but
  execution does not fire or handle them [C027, C028].
- A2A runtime state is in memory only and not restart-persistent [C026].
- `JobConfig` supports JSON and SQLite state backends, but daemon configuration
  remains SQLite; do not claim daemon-wide JSON state backend support [C037].
