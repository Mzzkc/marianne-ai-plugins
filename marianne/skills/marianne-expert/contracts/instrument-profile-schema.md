# Instrument Profile Schema

Marianne uses YAML-based instrument profiles to describe execution harnesses (CLI or HTTP) for running prompts. This contract lists all schema fields, types, and validation rules.

---

## InstrumentProfile (Top-level)

| Field Name | Type | Default Value | Description |
|---|---|---|---|
| `name` | `str` | *Required* | Unique name used in score YAML (must be >= 1 character). |
| `display_name` | `str` | *Required* | Human-readable label for status reports. |
| `description` | `str \| None` | `None` | Brief summary of the instrument's purpose. |
| `kind` | `Literal["cli", "http"]` | *Required* | Underlying API interface style. |
| `capabilities` | `set[str]` | `set()` | Capabilities tags (e.g. `tool_use`, `file_editing`, `mcp`, `structured_output`). |
| `code_mode` | `CodeModeConfig \| None` | `None` | TS sandbox interfaces and timeouts (opt-in). |
| `models` | `list[ModelCapacity]` | `[]` | List of models provided by this instrument with pricing and context. For `kind: http` the bound model's `max_output_tokens` (or smaller `context_window`) caps the request's `max_tokens`, so a small local model does not get the 16,384 transport default and a 400. | Each row carries `cost_per_1k_input`/`cost_per_1k_output` and optional `cost_per_1k_cache_read`/`cost_per_1k_cache_write` (unset charges cache tokens at the input rate); a sheet is priced at its bound model's row, then the default model's, then the first. `mzt instruments prices` reports rows that differ from models.dev and `--write` updates builtin rows only.
| `default_model` | `str \| None` | `None` | Fallback model selected when no model is requested in config. |
| `default_timeout_seconds`| `float` | `1800.0` | Sheet timeout threshold (seconds). |
| `execution_status` | `Literal["ready", "warning", "unsupported"]` | `"ready"` | General readiness check flag. |
| `execution_status_detail` | `str \| None` | `None` | Details explaining non-ready statuses. |
| `raw_prompt` | `bool` | `False` | Passes prompt verbatim without adding preambles or validations. |
| `cli` | `CliProfile \| None` | `None` | CLI commands execution configurations (required when `kind="cli"`). |
| `http` | `HttpProfile \| None` | `None` | HTTP endpoints configurations (required when `kind="http"`). |

---

## CliProfile

Applies when `kind="cli"`.

*   **`command`** (`CliCommand`, *Required*)
    *   Subprocess construction configurations.
*   **`output`** (`CliOutputConfig`, *Required*)
    *   Output parser patterns.
*   **`errors`** (`CliErrorConfig`, default empty)
    *   Subprocess regex crash and limit detector rules. Pattern lists, first
        match wins: `auth_error_patterns` → AUTH_FAILURE, `unavailable_patterns`
        → INSTRUMENT_UNAVAILABLE (the harness's own "no provider configured" /
        "provider not found" refusal; chain advances on attempt 1 without a
        retry charge, GH #389), then `crash_patterns`, `stale_patterns`,
        `timeout_patterns`, `capacity_patterns`; `rate_limit_patterns` (scanned on stderr and, for json/jsonl output profiles, the structured stream's terminal error record) pauses
        the instrument. Every pattern is compiled at load.
*   **`interactive`** (`InteractiveCliConfig \| None`, default `None`)
    *   Tmux-based TUI driver configuration.

---

## CliCommand

Details how to construct subprocess execution arrays.

| Field Name | Type | Default Value | Description |
|---|---|---|---|
| `executable` | `str` | *Required* | Binary executable name (e.g., `claude`, `gemini`). |
| `subcommand` | `str \| None` | `None` | Subcommand arguments (e.g. `exec`, `run`). |
| `prompt_flag` | `str \| None` | `None` | Flag prefixed before prompt argument. None = positional argument. |
| `model_flag` | `str \| None` | `None` | Model selection switch flag. |
| `auto_approve_flag` | `str \| None` | `None` | Auto-approve dialogs bypass flag (e.g. `--yes`). |
| `output_format_flag` | `str \| None` | `None` | Output format configuration flag. |
| `output_format_value` | `str \| None` | `None` | Value for output format flag (e.g. `json`). |
| `system_prompt_flag` | `str \| None` | `None` | System prompt path file flag. |
| `allowed_tools_flag` | `str \| None` | `None` | Tool restriction flag. |
| `mcp_config_flag` | `str \| None` | `None` | MCP configuration path flag. |
| `mcp_config_workspace_path`| `str \| None`| `None` | Workspace-relative path to copy MCP config JSON. |
| `mcp_config_workspace_merge_key`| `str \| None`| `None` | JSON key to merge MCP configurations into (e.g. `mcpServers`). |
| `mcp_config_prefix_args` | `list[str]` | `[]` | Flags added before MCP configs (e.g. `--strict-mcp-config`). |
| `mcp_disable_args` | `list[str]` | `[]` | Flags sent when MCP is disabled. |
| `timeout_flag` | `str \| None` | `None` | Execution timeout flag. |
| `working_dir_flag` | `str \| None` | `None` | Working directory flag. |
| `extra_flags` | `list[str]` | `[]` | Hardcoded flags appended to all runs. |
| `schema_extra_flags` | `list[str] \| None` | `None` | Flags used instead of `extra_flags` on a schema sheet. `None` inherits `extra_flags`. |
| `env` | `dict[str, str]` | `{}` | Subprocess environment variables (supports `${VAR}` expansion). |
| `prompt_via_stdin` | `bool` | `True` | Directs prompt to standard input stream rather than command arguments. |
| `stdin_sentinel` | `str \| None` | `None` | Input placeholder argument (e.g., `-` for Claude Code). |
| `start_new_session` | `bool` | `False` | Launches subprocess in a separate process group. |
| `required_env` | `list[str] \| None`| `None` | Pinned env vars list inherited from host (helps credentials scoping). |
| `json_schema_flag` | `str \| None` | `None` | Flag that makes the CLI enforce a JSON schema (`--json-schema` on Claude Code; the shipped `claude-code` profile declares it). Without it a sheet's `json_schema` `response_format` is refused at dispatch and V311 warns. Needs `output.format: json`. |

---

## EffortConfig (`effort:`, top level)

Maps the Marianne reasoning vocabulary (`minimal < low < medium < high < xhigh < max`, GH #535) that a sheet writes as `instrument_config.effort` to the harness's own word. No block = the key is refused on this profile (V335).

| Field | Type | Default | Description |
|---|---|---|---|
| `delivery` | `flag \| config_override \| body_field` | required | `flag`: `<flag> <native>`. `config_override`: `<flag> <key>=<native>`. `body_field`: HTTP request JSON `<key>` = native (HTTP only; CLI uses the other two). |
| `flag` | `str \| None` | `None` | Effort flag, or the override switch (`-c`). Required by `flag` and `config_override`. |
| `key` | `str \| None` | `None` | Config key or dotted body path. Required by `config_override` and `body_field`. |
| `levels` | `dict[str, str]` | `{}` | Marianne level to native word; levels may share a word. `{}` = each model row decides. |
| `schema_levels` | `list[str] \| None` | `None` | Levels a schema sheet may use (`claude-code`: `minimal`..`high`; `max` with `--json-schema` hangs). `None` = all mapped. |
| `interactive` | `bool` | `True` | `false` refuses an interactive sheet that sets effort (`opencode`). |

A model row's `effort_levels` (`dict | None`) overrides `levels` for that model; `{}` = no control. Defaults already in `extra_flags`, `schema_extra_flags` or `cli.interactive.extra_args` must be native values the block maps.

---

## CliOutputConfig

Converts subprocess output into `ExecutionResult`.

*   **`format`** (`Literal["text", "json", "jsonl"]`, default `"text"`)
    *   Output parse target style.
*   **`result_path`** (`str \| None`, default `None`)
    *   Dot-path to extract message content inside JSON responses (e.g. `result`).
*   **`error_path`** (`str \| None`, default `None`)
    *   Dot-path to extract error messages.
*   **`error_flag_path`** (`str \| None`, default `None`)
    *   JSON only. Dot-path to a terminal boolean error flag. When the value is exactly `true`, the attempt fails even at a successful exit code, with `CLI reported an error (<path>)` unless `error_path` gives a message. Unset keeps exit-code-only success. For CLIs that exit 0 on a semantic refusal (`qwen-code` uses `is_error`).
*   **`completion_event_type`** (`str \| None`, default `None`)
    *   Event type matching completion records inside JSONL streams (e.g., `turn.completed`).
*   **`completion_event_filter`** (`dict[str, str] \| None`, default `None`)
    *   Filters applied to locate completion events.
*   **`input_tokens_path`** (`str \| None`, default `None`)
    *   Dot-path to input token count.
*   **`output_tokens_path`** (`str \| None`, default `None`)
    *   Dot-path to output token count.
*   **`cache_read_tokens_path`** (`str \| None`, default `None`)
    *   Dot-path to the input tokens the provider served from its prompt cache (Anthropic `usage.cache_read_input_tokens`, OpenAI `usage.cached_input_tokens`). Billed at the cache rate; the first number a token-efficiency change moves. Unset records 0.
*   **`cache_write_tokens_path`** (`str \| None`, default `None`)
    *   Dot-path to the input tokens written into the prompt cache this attempt.
*   **`aggregate_tokens`** (`bool`, default `False`)
    *   Combines all wildcard token path matches (needed for multi-model tools).

---

## HttpProfile

Applies when `kind="http"`.

*   **`base_url`** (`str`, *Required*)
    *   API base URL pathway.
*   **`endpoint`** (`str`, default `"/v1/chat/completions"`)
    *   Endpoint URL suffix.
*   **`schema_family`** (`Literal["openai", "anthropic", "gemini"]`, *Required*)
    *   Request formatting template style.
*   **`auth_env_var`** (`str \| None`, default `None`)
    *   Environment variable containing API keys.
