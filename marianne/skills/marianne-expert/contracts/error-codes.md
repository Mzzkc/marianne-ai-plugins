# Error Codes and Retry Behavior

Marianne categorizes execution and runtime failures using a structured error taxonomy (`E0xx` to `E9xx`). Each error code has defined severity levels and retry guidelines.

---

## Error Categories

| Code Prefix | Category | Retriable | Severity | Description |
|---|---|---|---|---|
| `E0xx` | Execution | Varies | Varies | Subprocess execution failures. |
| `E1xx` | Rate Limit / Capacity | Yes | ERROR/WARNING | API throttling and resource exhaustion. |
| `E2xx` | Validation | Yes | ERROR/WARNING | Sheet verification check failures. |
| `E3xx` | Configuration | No | ERROR | Malformed score configuration fields. |
| `E4xx` | State | Varies | ERROR/CRITICAL | Checkpoint file loading/saving failures. |
| `E5xx` | Backend | Varies | ERROR/CRITICAL | Client connection and auth failures. |
| `E6xx` | Preflight | No | ERROR | Prerequisite path or limit checks failures. |
| `E9xx` | Network / Transient | Yes | ERROR | Generic connection or DNS failures. |

---

## Detailed Error Code Index

### E0xx: Execution Errors

| Code | Name | Retriable | Severity | Default Delay | Description |
|---|---|---|---|---|---|
| `E001` | `EXECUTION_TIMEOUT` | Yes | ERROR | 60s | Subprocess duration exceeded the limit. |
| `E002` | `EXECUTION_KILLED` | Yes | ERROR | 30s | Subprocess was killed by an external signal. |
| `E003` | `EXECUTION_CRASHED` | No | CRITICAL | - | Subprocess crashed (e.g. segfault, abort). |
| `E004` | `EXECUTION_INTERRUPTED` | No | ERROR | - | Execution was interrupted by the user. |
| `E005` | `EXECUTION_OOM` | No | CRITICAL | - | Process terminated due to out-of-memory. |
| `E006` | `EXECUTION_STALE` | Yes | WARNING | 120s | No output received within idle timeout. |
| `E009` | `EXECUTION_UNKNOWN` | Yes | ERROR | 10s | Subprocess returned non-zero exit code. |

---

### E1xx: Rate Limit / Capacity

| Code | Name | Retriable | Severity | Default Delay | Description |
|---|---|---|---|---|---|
| `E101` | `RATE_LIMIT_API` | Yes | ERROR | 1 hour | API rate limit returned from remote server. |
| `E102` | `RATE_LIMIT_CLI` | Yes | ERROR | 15 min | CLI-level client rate limiting detected. |
| `E103` | `CAPACITY_EXCEEDED` | Yes | WARNING | 5 min | Service is overloaded. Retry later. |
| `E104` | `QUOTA_EXHAUSTED` | Yes | ERROR | Dynamic | Usage budget limits reached. |

---

### E2xx: Validation Errors

| Code | Name | Retriable | Severity | Default Delay | Description |
|---|---|---|---|---|---|
| `E201` | `VALIDATION_FILE_MISSING` | Yes | ERROR | 5s | Expected output file was not created. |
| `E202` | `VALIDATION_CONTENT_MISMATCH` | Yes | ERROR | 5s | File content does not match pattern rules. |
| `E203` | `VALIDATION_COMMAND_FAILED` | Yes | ERROR | 10s | Post-run check command returned non-zero. |
| `E204` | `VALIDATION_TIMEOUT` | Yes | WARNING | 30s | Post-run check command timed out. |
| `E209` | `VALIDATION_GENERIC` | Yes | ERROR | 5s | Generic verification step failure. |

---

### E3xx: Configuration Errors

| Code | Name | Retriable | Severity | Description |
|---|---|---|---|---|
| `E301` | `CONFIG_INVALID` | No | ERROR | YAML schema validation fails. |
| `E302` | `CONFIG_MISSING_FIELD` | No | ERROR | Required YAML fields are missing. |
| `E303` | `CONFIG_PATH_NOT_FOUND` | No | ERROR | Path referenced in config is missing. |
| `E304` | `CONFIG_PARSE_ERROR` | No | ERROR | Invalid JSON/YAML syntax. |
| `E305` | `CONFIG_MCP_ERROR` | No | ERROR | MCP plugin parameters are misconfigured. |
| `E306` | `CONFIG_CLI_MODE_ERROR` | No | ERROR | Execution options are mismatching. |
| `E307` | `MODEL_NOT_FOUND` | No | ERROR | Selected model name is invalid for instrument. |

---

### E4xx: State Errors

| Code | Name | Retriable | Severity | Description |
|---|---|---|---|---|
| `E401` | `STATE_CORRUPTION` | No | CRITICAL | Checkpoint file is corrupted. |
| `E402` | `STATE_LOAD_FAILED` | Yes | ERROR | File load I/O exception. |
| `E403` | `STATE_SAVE_FAILED` | Yes | ERROR | File write I/O exception. |
| `E404` | `STATE_VERSION_MISMATCH` | No | ERROR | Checkpoint database version incompatible. |

---

### E5xx: Backend Errors

| Code | Name | Retriable | Severity | Default Delay | Description |
|---|---|---|---|---|---|
| `E501` | `BACKEND_CONNECTION` | Yes | ERROR | 30s | Connection to backend service failed. |
| `E502` | `BACKEND_AUTH` | No | CRITICAL | - | Credentials verification failed. |
| `E503` | `BACKEND_RESPONSE` | Yes | ERROR | 15s | Received invalid payload structure. |
| `E504` | `BACKEND_TIMEOUT` | Yes | ERROR | 60s | Connection attempt timed out. |
| `E505` | `BACKEND_NOT_FOUND` | No | CRITICAL | - | Binary harness or endpoint is missing. |

---

### E6xx: Preflight Errors

| Code | Name | Retriable | Severity | Description |
|---|---|---|---|---|
| `E601` | `PREFLIGHT_PATH_MISSING` | No | ERROR | Expected file or dir doesn't exist on start. |
| `E602` | `PREFLIGHT_PROMPT_TOO_LARGE` | No | ERROR | Estimated token count exceeds context limits. |
| `E603` | `PREFLIGHT_WORKING_DIR_INVALID` | No | ERROR | Working directory is not a directory or not writable. |
| `E604` | `PREFLIGHT_VALIDATION_SETUP` | No | ERROR | Verification rules configuration has errors. |

---

### E9xx: Network / Transient

| Code | Name | Retriable | Severity | Default Delay | Description |
|---|---|---|---|---|---|
| `E901` | `NETWORK_CONNECTION_FAILED` | Yes | ERROR | 30s | Server unreachable or connection reset. |
| `E902` | `NETWORK_DNS_ERROR` | Yes | ERROR | 30s | Hostname resolution failed. |
| `E903` | `NETWORK_SSL_ERROR` | Yes | ERROR | 30s | Certificate validation failed. |
| `E904` | `NETWORK_TIMEOUT` | Yes | ERROR | 60s | Network socket read/write timed out. |
| `E999` | `UNKNOWN` | Yes | ERROR | 30s | Catch-all for unhandled exceptions. |
