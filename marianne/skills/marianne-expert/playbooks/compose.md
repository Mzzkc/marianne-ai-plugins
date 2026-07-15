# Composing a Score

## Problem

Score authors fail when they compose from the metaphor instead of the runtime contract. A "concert" can sound like an unconstrained swarm, but Marianne actually executes a score through concrete sheet expansion, prompt rendering, instrument resolution, dispatch gates, technique injection, and post-sheet validations. The likely wrong action is to write an elegant YAML file whose prompts, dependencies, instruments, or validations do not line up with the artifacts the runtime can prove. The governing boundary is split across template syntax, dispatch, instrument profiles, techniques, validation command safety, score path handling, and partial/spec-only surfaces [C001, C002, C003, C004, C005, C010, C015, C020, C031, C038, C040]. Grounding is config_only_runtime_unwired, so it must not be used as the validation litmus test for score correctness [C031].

## Mechanism

Use this decision tree before writing YAML.

First, decide the work shape. If each sheet performs the same operation over item ranges, use a linear batch: `sheet.size > 1`, `sheet.total_items` equal to the item count, and a prompt that uses `{{ start_item }}` and `{{ end_item }}` [C002, C003, C040]. If each phase has distinct instructions, use one logical stage per sheet: `sheet.size: 1`, `sheet.total_items` equal to the number of stages, and branch the prompt on `stage` or `movement`; those aliases are preserved in the runtime context [C040]. If independent perspectives improve the result, use fan-out: one setup stage, one fan-out stage with multiple `instance` or `voice` values, and one synthesis stage that depends on the fan-out stage [C040]. Dependencies and dispatch still pass through the scheduler, where `dispatch_ready()` enforces global concurrency despite stale docs saying otherwise, per-instrument/model limits, rate-limit skips, and stagger delays [C004, C005, C006, C007, C008].

Second, apply the forces framework. The forces are independence, coupling, artifact surface, risk, cost, and validation observability. High independence pushes toward fan-out; high coupling pushes toward a linear pipeline or explicit dependencies [C004, C005, C006]. A narrow artifact surface pushes toward simple file outputs and `content_contains` or `field_match`; a broad artifact surface needs staged validations and possibly `command_succeeds`, which is implemented_security_sensitive privileged bash for trusted score authors [C015]. High risk pushes toward smaller sheets, stronger validations, and explicit synthesis; high cost pushes toward fewer voices, stricter parallel limits, and cheaper instruments through profile selection [C005, C006, C020]. Low validation observability is a stop signal: redesign the artifact before adding sheets.

Third, choose instruments by capability boundary, not provider preference. The score can name a primary `instrument`, provide `instrument_config`, define local `instruments`, and override at movement or sheet level [C037, C020]. Prefer profile-driven CLI or generic HTTP instruments unless the source-backed exception is real [C020, C021, C023]. The docs say `recursive_light` is a native Python backend, but source/tests show it operates through the generic OpenAI-compatible/OpenRouter path. Treat the generic path as runtime truth and record the native-backend wording as stale or contradicted [C021]. Broad native-client wording is also unsafe: the retained specialized native clients are Anthropic and Ollama, while generic HTTP executor behavior was retired or relocated under instrument execution [C023, C024, C025].

Fourth, design injections deliberately. Put invariant project context in `sheet.prelude`, sheet-specific files in `sheet.cadenzas`, and methodology in `techniques` when it is reusable across scores [C010, C011, C012]. Technique components are `skill`, `mcp`, or `protocol`; runtime resolution determines active techniques by phase, skill techniques inject text methodology, MCP techniques connect registered tool pools, and protocol techniques classify coordination surfaces [C010, C011, C012, C013, C014]. Do not confuse protocol routing with durable completion semantics: A2A inbox state is in-memory only, and completion/failure events are observer-serialized rather than executed by the runtime [C026, C027, C028].

Fifth, engineer the litmus test. A score is composed only when every required output is named in the prompt, written to `{{ workspace }}`, and checked by a validation path using single-brace Python `.format()` syntax [C001, C002, C003]. Prompts render Jinja2 at dispatch time; validation paths expand with Python `.format()` from the sheet context [C001, C002, C003]. Relative workspace paths resolve against the score file's parent without confinement, so score files are trusted input and `path_in_scope` should be used when untrusted path escape matters [C038, C015].

Golden example:

```yaml
name: expert-review
workspace: ./workspace
instrument: codex-cli

sheet:
  size: 1
  total_items: 3
  fan_out:
    2: 3
  dependencies:
    2: [1]
    3: [2]

parallel:
  enabled: true
  max_concurrent: 3

prompt:
  variables:
    lenses:
      1: correctness
      2: security
      3: maintainability
  template: |
    {% if stage == 1 %}
    Inventory the source. Save {{ workspace }}/01-inventory.md.
    {% elif stage == 2 %}
    Review from the {{ lenses[instance] }} lens.
    Save {{ workspace }}/02-{{ lenses[instance] }}.md.
    {% elif stage == 3 %}
    Synthesize all review files into {{ workspace }}/03-synthesis.md.
    {% endif %}

validations:
  - type: file_modified
    path: "{workspace}/01-inventory.md"
    condition: "stage == 1"
  - type: content_contains
    path: "{workspace}/03-synthesis.md"
    pattern: "Priority"
    condition: "stage == 3"
```

This is golden because the fan-out shape has explicit dependencies, the prompt writes deterministic artifacts, validation uses single-brace paths, and the synthesis litmus checks a content obligation rather than mere file existence [C001, C002, C003, C005, C015, C040].

Broken example:

```yaml
name: vague-concert
workspace: ../../shared
instrument: recursive_light

sheet:
  size: 1
  total_items: 3
  fan_out:
    "{{ reviewer_count }}": 3

prompt:
  template: |
    Do the review and use grounding to verify the result.
    Save somewhere useful.

grounding:
  enabled: true

validations:
  - type: file_exists
    path: "{{ workspace }}/result.md"
```

This is broken because fan-out is YAML configuration rather than a prompt-rendered value, the prompt does not name a concrete artifact, grounding config does not run output hooks, the validation path uses Jinja syntax instead of `.format()`, and the workspace path assumes trust while escaping the score directory [C001, C002, C003, C031, C038].

## Evidence

Composition begins with the score schema: `JobConfig` carries the score name, workspace, primary instrument, local instrument definitions, movement and sheet controls, prompt configuration, techniques, validations, and state backend selection [C037, C038, C039, C010, C015]. Prompt rendering is deferred Jinja2 at dispatch, while validation paths are Python `.format()` expansions from the sheet context [C001, C002, C003]. The prompt context includes sheet and orchestral aliases such as `stage`/`movement`, `instance`/`voice`, `fan_count`/`voice_count`, and `total_stages`/`total_movements` [C040].

Dispatch evidence governs the forces framework. `dispatch_ready()` is the scheduling boundary [C004]. The docs say global concurrency is not enforced, but source/tests show `dispatch_ready()` enforces it. Treat enforcement as runtime truth and record the configuration-reference denial as stale [C005]. Per-instrument/model limits, rate-limit skips, and stagger gates are implemented separately [C006, C007, C008].

Technique and instrument evidence prevents overcomposition. Techniques are implemented as ECS-style components with `skill`, `mcp`, and `protocol` kinds, phase activation, active-technique resolution, router classification, and compact MCP interface generation [C010, C011, C012, C013, C014]. Instrument profiles are the implemented execution extension surface, and backend wording must preserve the corrected `recursive_light` and native-client boundaries [C020, C021, C023, C024, C025].

Validation evidence defines the litmus test. The nine retryable validation types are `file_exists`, `file_modified`, `content_contains`, `content_regex`, `command_succeeds`, `path_in_scope`, `field_match`, `file_sha256`, and `csv_unique_key` [C015]. `command_succeeds` is trusted-author bash, validation commands spawn in their own process group, the daemon-process-group refusal exists but is implemented_untested, and cleanup sends SIGTERM then SIGKILL on exit paths [C015, C016, C017, C018]. Output capture keeps 51,200 bytes / 50 KiB of trailing output; any 10KB test comment is stale when capture size matters [C048].

## Trap

Tempting sentence: "The score is good because it describes the intended work."

Corrected sentence: "The score is good only if the prompt names deterministic artifacts, those artifacts are written under the resolved workspace, and validations prove the observable result with the correct syntax." The consequence of the tempting sentence is a concert that appears meaningful but passes or fails for stale files, wrong path expansion, or missing artifacts [C001, C002, C003, C015].

Tempting sentence: "Use grounding, cron, A2A completion, or a native backend label to make the composition stronger."

Corrected sentence: "Use implemented validation and profile mechanisms; grounding is config_only_runtime_unwired, A2A completion/failure events are observer-serialized rather than executed, and `recursive_light` is generic OpenAI-compatible rather than a dedicated native backend." The consequence is promising behavior the runtime does not perform [C021, C026, C027, C028, C031].

## Verify

Before publishing or running a score, perform these checks:

1. Decision tree: name the selected shape as linear batch, stage pipeline, fan-out/fan-in, or mixed-instrument pipeline; confirm `sheet.size`, `sheet.total_items`, dependencies, and fan-out align with that shape [C004, C005, C040].
2. Forces: write one sentence each for independence, coupling, artifact surface, risk, cost, and validation observability. If validation observability is weak, change the artifact contract before adding more sheets [C015].
3. Instruments: run the score through profile vocabulary, not stale backend vocabulary. Reject broad "native" wording unless it preserves `recursive_light` as generic OpenAI-compatible and names Anthropic/Ollama as the retained specialized clients [C020, C021, C023, C024, C025].
4. Injections: confirm stable context is in prelude/cadenzas or a named technique, and confirm protocol techniques do not claim durable A2A completion semantics [C010, C011, C012, C026, C027, C028].
5. Litmus test: for every output, the prompt contains `{{ workspace }}/...`, the validation uses `{workspace}/...`, and at least one validation checks freshness, content, structure, digest, command success, scope, or uniqueness rather than only existence [C001, C002, C003, C015].
6. Safety and contradiction scan: label `command_succeeds` as trusted-author bash, treat relative workspaces as security-sensitive, do not claim grounding runtime hooks, and resolve contradicted claims by source/tests over stale docs [C015, C031, C038].
