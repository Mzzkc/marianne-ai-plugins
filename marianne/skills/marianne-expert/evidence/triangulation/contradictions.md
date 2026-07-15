# Triangulation contradictions

The 48-claim triangulation found seven claims with cross-source disagreement. Code and executable tests are treated as authoritative when prose conflicts with them. One additional docs-only assertion and two stale comments are recorded after the primary contradictions so they cannot continue to masquerade as runtime behavior.

## Primary contradicted claims

### C021 — `recursive_light` is not a dedicated native backend

The documentation describes `recursive_light` as a native Python backend comparable to Anthropic and Ollama. No `backends/recursive_light.py` exists. The registered instrument is operational, but it is dispatched through the generic OpenAI-compatible/OpenRouter path. The stale documentation turns “implemented through a generic executor” into “implemented as a native backend.”

### C023 — “native HTTP executors” is ambiguous and architecture-dependent

The claim and conventions spec say the backends package contains native HTTP executors. Code investigation interpreted that as false because generic/native HTTP executors were retired or relocated under `execution/instruments`; tests interpreted the two remaining specialized clients (`AnthropicApiBackend` and `OllamaBackend`) as native executors. The corrected statement names those two clients explicitly and avoids implying that the retired generic executor architecture remains.

### C029 — `CronTick` is spec-only

Design prose says a cron tick submits a score as a new job and schedules the next tick. The baton event loop only emits an `unimplemented` warning. There is no job submission or rescheduling path. This is spec-only-described-as-built and must not be presented as an available scheduler.

### C030 — `ConfigReloaded` is spec-only

Design prose says a configuration reload rebuilds pending sheets. The implemented handler only emits an `unimplemented` warning. Live reload is therefore a documented design, not runtime behavior.

### C031 — grounding is config-wired but runtime-unwired

Documentation says configured grounding hooks validate outputs. `GroundingConfig` and related validation/scaffolding exist, but the runtime never invokes the hooks. This is especially hazardous drift because a valid configuration can create false assurance that an integrity control ran.

### C033 — no module-level orphan-reaping flag exists

The claim says orphan cleanup is controlled by a module-level disabled flag. Code and tests refute it: the relevant methods return no-op results inline. Operators cannot find or toggle the alleged flag. The true status is a hardcoded safety no-op motivated by observed WSL2 shutdowns.

### C047 — error category uses the first numeric digit

The claim says `ErrorCode` categories are parsed from the second digit. The implementation reads `self.value[1]`, the first numeric digit immediately after the `E` prefix. Both code and tests refute the original wording.

## Docs-only and stale narrative artifacts

### C005 — one configuration reference denies an enforced limit

Code, tests, and other docs show that `dispatch_ready()` enforces the global concurrency ceiling. A contradictory line in `configuration-reference.md` says the limit is not yet enforced. That isolated docs-only statement is stale.

### C019 — deleted `claude_cli_legacy` relocation

The `marianne.backends` package docstring says `ClaudeCliBackend` was relocated to `marianne.execution.instruments.claude_cli_legacy`, but that module was deleted. Some test patch targets also retain the old path. This is a stale docstring/reference, not an implemented compatibility location.

### C048 — stale 10KB test docstring

The implementation and assertion agree on 51,200 bytes (50 KiB) and preserve the trailing captured bytes. A test docstring still describes a 10KB limit. The comment is stale even though the executable assertion is correct.

## Resolution

The implementation-status evidence now records the generic `recursive_light` path, the two specialized native clients, config reload as spec-only, grounding as runtime-unwired, and orphan cleanup as an inline safety no-op. The contradiction count is **7**; the additional docs-only C005 assertion and stale C019/C048 narratives are tracked separately.
