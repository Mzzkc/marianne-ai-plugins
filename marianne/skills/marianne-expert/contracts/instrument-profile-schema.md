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
| `models` | `list[ModelCapacity]` | `[]` | List of models provided by this instrument with pricing and context. |
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
    *   Subprocess regex crash and limit detector rules.
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
| `env` | `dict[str, str]` | `{}` | Subprocess environment variables (supports `${VAR}` expansion). |
| `prompt_via_stdin` | `bool` | `True` | Directs prompt to standard input stream rather than command arguments. |
| `stdin_sentinel` | `str \| None` | `None` | Input placeholder argument (e.g., `-` for Claude Code). |
| `start_new_session` | `bool` | `False` | Launches subprocess in a separate process group. |
| `required_env` | `list[str] \| None`| `None` | Pinned env vars list inherited from host (helps credentials scoping). |

---

## CliOutputConfig

Converts subprocess output into `ExecutionResult`.

*   **`format`** (`Literal["text", "json", "jsonl"]`, default `"text"`)
    *   Output parse target style.
*   **`result_path`** (`str \| None`, default `None`)
    *   Dot-path to extract message content inside JSON responses (e.g. `result`).
*   **`error_path`** (`str \| None`, default `None`)
    *   Dot-path to extract error messages.
*   **`completion_event_type`** (`str \| None`, default `None`)
    *   Event type matching completion records inside JSONL streams (e.g., `turn.completed`).
*   **`completion_event_filter`** (`dict[str, str] \| None`, default `None`)
    *   Filters applied to locate completion events.
*   **`input_tokens_path`** (`str \| None`, default `None`)
    *   Dot-path to input token count.
*   **`output_tokens_path`** (`str \| None`, default `None`)
    *   Dot-path to output token count.
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
