# Job, Sheet, and Prompt Configuration Schema

This contract lists all fields, types, and defaults for the main configuration models in a Marianne score.

## JobConfig

The top-level model representing a complete Marianne score.

| Field Name | Type | Default Value | Description |
|---|---|---|---|
| `name` | `str` | *Required* | Unique name of the job. |
| `description` | `str \| None` | `None` | Human-readable description of the job. |
| `workspace` | `Path` | `Path("./workspace")` | Relative or absolute path to the output directory. Resolved relative to the score parent. |
| `instrument` | `str \| None` | `None` | Resolved primary execution instrument profile name (e.g. `gemini-cli`, `claude-code`). |
| `instrument_config` | `dict[str, Any]` | `{}` | Flat key-value parameters overriding resolved instrument defaults. |
| `instrument_fallbacks` | `list[str]` | `[]` | Fallback instrument profiles tried when the primary instrument fails. |
| `instruments` | `dict[str, InstrumentDef]` | `{}` | Local named instrument definitions referencing registered profiles with overrides. |
| `movements` | `dict[int, MovementDef]` | `{}` | Sequential execution phase movement overrides (instruments/voices). |
| `sheet` | `SheetConfig` | *Required* | Sheet division, dependency, and fan-out parameters. |
| `prompt` | `PromptConfig` | *Required* | Main prompt template, file, and injection configurations. |
| `spec` | `SpecCorpusConfig` | `SpecCorpusConfig()` | Configuration for locating and loading spec corpus passages. |
| `retry` | `RetryConfig` | `RetryConfig()` | Retry count and timing parameters. |
| `rate_limit` | `RateLimitConfig` | `RateLimitConfig()` | API-level and CLI-level rate-limiting configuration. |
| `circuit_breaker` | `CircuitBreakerConfig` | `CircuitBreakerConfig()` | Failure thresholds that trigger instrument fallback. |
| `cost_limits` | `CostLimitConfig` | `CostLimitConfig()` | Job-level and sheet-level USD cost limit controls. |
| `learning` | `LearningConfig` | `LearningConfig()` | Output outcome recording and global pattern registry configuration. |
| `grounding` | `GroundingConfig` | `GroundingConfig()` | Grounding validation post-execution verification hooks. |
| `ai_review` | `AIReviewConfig` | `AIReviewConfig()` | AI-led adversarial output verification config. |
| `logging` | `LogConfig` | `LogConfig()` | Conductor log levels, files, and format specifications. |
| `workspace_lifecycle` | `WorkspaceLifecycleConfig` | `WorkspaceLifecycleConfig()` | Cleanup and archive rules for `--fresh` and restart actions. |
| `isolation` | `IsolationConfig` | `IsolationConfig()` | Git worktree parallel execution environment config. |
| `code_execution` | `CodeExecutionConfig` | `CodeExecutionConfig()` | Opt-in execution of generated code blocks in bubblewrap sandbox. |
| `conductor` | `ConductorConfig` | `ConductorConfig()` | Conductor identity metadata and developer guidelines. |
| `parallel` | `ParallelConfig` | `ParallelConfig()` | Concurrent execution parameters for independent sheets. |
| `stale_detection` | `StaleDetectionConfig` | `StaleDetectionConfig()` | Deadlock and hung execution killing threshold parameters. |
| `checkpoints` | `CheckpointConfig` | `CheckpointConfig()` | Pre-execution approval triggers and interactive gating. |
| `bridge` | `BridgeConfig \| None` | `None` | Ollama bridge and local MCP server configs. |
| `cross_sheet` | `CrossSheetConfig \| None` | `None` | Passing context/files between sequential sheets. |
| `judgment` | `JudgmentConfig` | `JudgmentConfig()` | Automated resolving client config for paused FERMATA sheets. |
| `feedback` | `FeedbackConfig` | `FeedbackConfig()` | Regex-based developer feedback extraction block parameters. |
| `techniques` | `dict[str, TechniqueConfig]` | `{}` | Composable ECS techniques (skill, mcp, protocol) mapped by name. |
| `agent_card` | `AgentCard \| None` | `None` | A2A protocol discovery card representing job capabilities. |
| `validations` | `list[ValidationRule]` | `[]` | Post-sheet verification checks applied to all sheets. |
| `notifications` | `list[NotificationConfig]` | `[]` | Desktop, slack, or email notification receivers. |
| `on_success` | `list[PostSuccessHookConfig]` | `[]` | Execution hooks triggered after clean job completions. |
| `concert` | `ConcertConfig` | `ConcertConfig()` | Parent/child concert orchestration chain attributes. |
| `state_backend` | `Literal["json", "sqlite"]` | `"sqlite"` | Storage format for sheet states (`sqlite` recommended). |
| `state_path` | `Path \| None` | `None` | Custom path to store checkpoint database (default is workspace). |
| `pause_between_sheets_seconds` | `int` | `2` | Stagger delay in seconds between sheets. |

---

## SheetConfig

Controls partitioning, parallelization, dependencies, and fan-out parameters.

| Field Name | Type | Default Value | Description |
|---|---|---|---|
| `size` | `int` | *Required* | Number of items bundled in a single sheet (must be >= 1). |
| `total_items` | `int` | *Required* | Total logical items representing the composition size (must be >= 1). |
| `start_item` | `int` | `1` | First item sequence number (1-indexed). |
| `descriptions` | `dict[int, str]` | `{}` | Sheet description labels shown in progress reports. |
| `dependencies` | `dict[int, list[int]]` | `{}` | Directed Acyclic Graph (DAG) dependencies mapping sheet to prerequisites. |
| `spec_tags` | `dict[int, list[str]]` | `{}` | Per-sheet spec tag filters used to prune injected spec corpus passages. |
| `skip_when` | `dict[int, SkipWhenCommand]` | `{}` | Shell command predicates that bypass sheet execution on exit 0. |
| `prompt_extensions` | `dict[int, list[str]]` | `{}` | Inline text or file pathways extending prompts for specific sheet numbers. |
| `prelude` | `list[InjectionItem]` | `[]` | Shared background materials injected into prompts for all sheets. |
| `cadenzas` | `dict[int, list[InjectionItem]]` | `{}` | Per-sheet context injection files or directories. |
| `fan_out` | `dict[int, int]` | `{}` | Parametric stage harmonization count mapping stage numbers to instance counts. |
| `fan_out_stage_map` | `dict[int, dict[str, int]] \| None` | `None` | Recomputed stage/instance mapping metadata. |
| `per_sheet_instruments` | `dict[int, str]` | `{}` | Single sheet instrument name overrides. |
| `per_sheet_instrument_config` | `dict[int, dict[str, Any]]` | `{}` | Single sheet parameter override maps. |
| `per_sheet_fallbacks` | `dict[int, list[str]]` | `{}` | Single sheet fallback chain lists. An empty list disables fallback. |
| `instrument_map` | `dict[str, list[int]]` | `{}` | Multi-sheet bulk instrument maps. |

---

## PromptConfig

Main configuration structure for templating prompt structures.

| Field Name | Type | Default Value | Description |
|---|---|---|---|
| `template` | `str \| None` | `None` | Inline Jinja2 template body. XOR with `template_file`. |
| `template_file` | `Path \| None` | `None` | Relative path to a `.j2` template file. XOR with `template`. |
| `variables` | `dict[str, Any]` | `{}` | Static variables injected into the Jinja2 rendering context. |
| `stakes` | `str \| None` | `None` | Motivational stakes block appended to the tail of prompt templates. |
| `thinking_method` | `str \| None` | `None` | Thinking instructions injected to enforce reasoning patterns. |
| `prompt_extensions` | `list[str]` | `[]` | Global prompt instructions appended to the default preamble. |
