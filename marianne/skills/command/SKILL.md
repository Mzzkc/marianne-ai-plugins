---
name: command
description: Use when the user is running, monitoring, debugging, or recovering Marianne jobs. Covers the conductor, job lifecycle, diagnostics, config reload, recovery, self-healing, concert operations, and anti-patterns that lose work. Do NOT use for writing score configs (use score-authoring instead).
---

# Marianne Command Skill

> **Purpose**: Run, monitor, debug, and recover Marianne jobs. Covers the conductor, job lifecycle, diagnostics, config reload, recovery, and the anti-patterns that lose work.

---

## Triggers

| Use This Skill | Skip This Skill |
|---|---|
| Running/monitoring Marianne jobs | Writing new score configs (use marianne-score-authoring) |
| Debugging failed or stuck jobs | |
| Resuming interrupted jobs | |
| Understanding validation failures | |
| Conductor operations | |

---

## Conductor: The Required Foundation

**The conductor (daemon) is required for `mzt run`.** Without a running conductor, only `--dry-run` and `mzt validate` work.

### Starting the Conductor

```bash
# Foreground (development, see logs directly)
mzt start --foreground

# Background (production)
mzt start

# Detached from scripts (survives session end)
setsid mzt start &
```

### Conductor Commands

| Command | Purpose |
|---|---|
| `mzt start` | Start the conductor daemon |
| `mzt start --foreground` | Start in foreground (development) |
| `mzt start --profile dev` | Start with dev profile (debug logging, strace on) |
| `mzt start --profile intensive` | Start with intensive profile (48h timeout, high limits) |
| `mzt start --profile minimal` | Start with minimal profile (profiler + learning off) |
| `mzt stop` | Stop the conductor (**only when no jobs are running**) |
| `mzt stop --force` | Force-kill the conductor --- **NEVER with active jobs** |
| `mzt restart` | Stop and restart |
| `mzt restart --profile dev` | Restart with a profile |
| `mzt conductor-status` | Check if conductor is running |

### How Jobs Route Through the Conductor

When you run `mzt run config.yaml`, the CLI checks for a running conductor via Unix socket. If found, the job is submitted through IPC and the CLI returns. The conductor manages job lifecycle, rate limit coordination across concurrent jobs, and event routing. If no conductor is found, the command exits with an error.

**The conductor runs your jobs.** `mzt run` is a client that submits work and returns. The job continues in the daemon regardless of whether your terminal stays open.

**NEVER stop the conductor while jobs are actively running.** Killing the daemon orphans all in-flight Claude agent processes and corrupts job state --- sheets get stuck as `in_progress` with no validation or cleanup. To reload config on a running job, use `mzt modify -c new.yaml --resume --wait`. To safely stop: pause all jobs first, wait for pauses to take effect, then `mzt stop`.

---

## Job Lifecycle

### Submitting a Job

```bash
mzt run config.yaml              # Submit (routes through conductor)
mzt run config.yaml --dry-run    # Preview without running (no conductor needed)
mzt run config.yaml --fresh      # Fresh start (clears previous state)
mzt run config.yaml -s 5         # Start from sheet 5
mzt run config.yaml -w /path     # Override workspace directory
mzt run config.yaml --self-healing      # Auto-diagnose + fix on retry exhaustion
mzt run config.yaml --self-healing --yes  # Auto-confirm suggested fixes
mzt run config.yaml -j           # JSON output
```

| Option | Short | Description |
|---|---|---|
| `--dry-run` | `-n` | Preview execution (no conductor needed) |
| `--start-sheet` | `-s` | Override starting sheet |
| `--workspace` | `-w` | Override workspace directory |
| `--fresh` | | Clear previous state and start over |
| `--self-healing` | | Auto-diagnose and remediate on failure |
| `--yes` | | Auto-confirm self-healing fixes |
| `--json` | `-j` | Machine-readable output |

`mzt run` is the only command that accepts `-w`/`--workspace`. All other commands resolve job context from the conductor's registry using the job ID.

### Monitoring

```bash
mzt status my-job                # Check status
mzt status my-job --watch        # Live monitoring (refreshes every 5s)
mzt status my-job -W -i 10       # Watch with 10s interval
mzt status my-job -j             # JSON output
mzt list                         # List active jobs
mzt list --all                   # All jobs including completed/failed
mzt list --status running        # Filter by status
mzt logs my-job                  # View log entries
mzt logs my-job --follow         # Tail logs
mzt logs my-job --lines 200      # Last 200 lines
mzt logs my-job --level ERROR    # ERROR and above
mzt history my-job               # Execution history
```

| Command | Key Options |
|---|---|
| `status` | `--watch` / `-W`, `--interval` / `-i`, `--json` / `-j` |
| `list` | `--all`, `--status` / `-s`, `--limit` / `-l` |
| `logs` | `--follow` / `-F`, `--lines` / `-n`, `--level` / `-l`, `--json` / `-j` |
| `history` | `--json` / `-j` |

### Pausing

```bash
mzt pause my-job                 # Graceful pause at next sheet boundary
mzt pause my-job --wait          # Wait for acknowledgment
mzt pause my-job --wait -t 30    # Wait with 30s timeout
```

| Option | Short | Description |
|---|---|---|
| `--wait` | | Wait for pause acknowledgment |
| `--timeout` | `-t` | Wait timeout seconds (default: 60) |
| `--json` | `-j` | JSON output |

**How it works:** Creates a pause signal file in the workspace. The running job checks for this file between sheets, saves state, and transitions to PAUSED. Signal file is removed after acknowledgment.

### Resuming

```bash
mzt resume my-job                # Resume (auto-reloads config from YAML)
mzt resume my-job -c fixed.yaml  # Resume with a different config file
mzt resume my-job --no-reload    # Resume using cached snapshot
mzt resume my-job --force        # Force resume a completed job
mzt resume my-job --self-healing # Resume with self-healing
```

| Option | Short | Description |
|---|---|---|
| `--config` | `-c` | Override config file |
| `--no-reload` | | Use cached snapshot instead of auto-reloading |
| `--force` | `-f` | Resume even if completed |
| `--self-healing` | | Enable auto-diagnosis on failure |

### Modifying Running Jobs

`mzt modify` requires a new config file (`-c` is mandatory).

```bash
mzt modify my-job -c updated.yaml              # Pause and apply new config
mzt modify my-job -c updated.yaml --resume      # Pause, apply, and resume
mzt modify my-job -c updated.yaml --resume --wait  # Wait for pause before resume
```

| Option | Short | Description |
|---|---|---|
| `--config` | `-c` | New configuration file (required) |
| `--resume` | `-r` | Resume with new config after pausing |
| `--wait` | | Wait for pause acknowledgment |
| `--timeout` | `-t` | Timeout for pause acknowledgment (default: 60) |

### Registry Cleanup

```bash
mzt clear                        # Clear completed/failed/cancelled jobs
mzt clear --job my-job           # Clear specific job
mzt clear --status failed        # Clear only failed jobs
mzt clear --older-than 3600      # Clear jobs older than 1 hour
mzt clear --yes                  # Skip confirmation
```

### Other Commands

```bash
mzt validate config.yaml         # Pre-flight check (no conductor needed)
mzt diagnose my-job              # Full diagnostic report
mzt errors my-job --verbose      # Error details with stdout/stderr
mzt dashboard                    # Start web dashboard (default port 8000)
mzt patterns                     # View global learning patterns
```

---

## Debugging Protocol (Mandatory Order)

**ALWAYS follow this sequence. Do NOT skip to manual investigation.**

```bash
# 1. ALWAYS start here
mzt status my-job

# 2. If failed --- get diagnostics
mzt diagnose my-job

# 3. Error details
mzt errors my-job --verbose

# 4. Filter errors by sheet, type, or code
mzt errors my-job --sheet 3
mzt errors my-job --type rate_limit
mzt errors my-job --code E201

# 5. Include log snippets in diagnostic
mzt diagnose my-job --include-logs

# 6. THEN manual investigation if needed
```

### Understanding `mzt status` Output

- **Status**: RUNNING, COMPLETED, FAILED, PAUSED, CANCELLED
- **Validation**: Pass/Fail per sheet (a sheet can execute successfully but fail validation)
- **Sheets**: N/M completed, which failed, which skipped
- **Rate limits**: Current wait count

**Critical insight**: `exit_code=0` does NOT mean success. Only `validation_passed=true` means success.

### Common Failure Patterns

| Symptom | Likely Cause | Fix |
|---|---|---|
| File exists but "missing" | Wrong path syntax (`{{ }}` vs `{}`) | Check validation path syntax |
| Validation always passes | No validations configured, or too broad | Add meaningful validations |
| Pattern doesn't match | Regex anchors, escaping, or content changed | Test regex with `python3 -c "import re; ..."` |
| Command fails | Wrong `working_directory` or shell assumptions | Check CWD, test command manually |
| Sheet "passes" but work is bad | Validations too weak (file_exists only) | Add content checks or command validations |
| Config changes ignored | `--no-reload` used or file deleted | Config auto-reloads by default; check YAML file exists |
| Job hangs forever | Custom instrument profile lacks an auto-approve flag, or an interactive session is stuck on an unhandled dialog | Built-in profiles auto-approve; for custom profiles set `auto_approve_flag`; for interactive stalls check `tmux -L marianne attach -t <session>` and add a `startup_gates` entry |
| Chained job does nothing | Missing `fresh: true` in hook | Add `fresh: true` to self-chain hooks |

---

## Config Auto-Reload on Resume

**Marianne auto-reloads config from the original YAML file on resume.** The cached `config_snapshot` is a fallback when the file no longer exists on disk.

### Priority Order

1. Explicit `--config file.yaml` (always wins)
2. Auto-reload from stored `config_path` (default, if file exists)
3. Cached `config_snapshot` (fallback when file is gone or `--no-reload`)
4. Error (nothing available)

### Common Workflows

**Fix a config error and resume:**
```bash
# Edit the YAML file, then just resume --- auto-reloads
mzt resume my-job
```

**Use a completely different config:**
```bash
mzt resume my-job -c fixed.yaml
```

**Deterministic replay from cached snapshot:**
```bash
mzt resume my-job --no-reload
```

**Modify a running job's config:**
```bash
mzt modify my-job -c updated.yaml --resume --wait
```

---

## Recovery Procedures

### Rate Limit Recovery

Marianne auto-waits when rate limited (default: 60 minutes, up to 24 cycles).

```bash
mzt status my-job    # Shows PAUSED (rate_limited)

# If max_waits exhausted, just resume
mzt resume my-job
```

### Validation Failure Recovery

```bash
# 1. Check WHICH validation failed
mzt errors my-job --verbose

# 2a. Work complete but validation config is wrong --- fix YAML and resume
mzt resume my-job    # auto-reloads fixed config

# 2b. Work incomplete --- Marianne retries automatically
mzt resume my-job
```

### Interrupted Job Recovery

```bash
# First: always try resume
mzt resume my-job

# If resume fails with stale PID --- auto-clears since fix b474d45
mzt resume my-job    # Retrying usually works

# If job is truly stuck, force resume
mzt resume my-job --force
```

### State Corruption Recovery

```bash
# Start fresh from specific sheet
rm workspace/.marianne-state.db    # SQLite backend
mzt run job.yaml --start-sheet N
```

### `--fresh` vs `resume`

| Situation | Use |
|---|---|
| Job interrupted mid-progress | `mzt resume my-job` |
| Job failed, config needs fixing | `mzt resume my-job` (auto-reloads fixed YAML) |
| Self-chaining: completed an iteration | `--fresh` (via hook config) |
| User explicitly wants to start over | `mzt run my-score.yaml --fresh` |
| Job was cancelled or partially failed | `mzt resume my-job` (try first) |

**`--fresh` deletes checkpoint state and archives workspace artifacts.** It wipes hours of work if used on an interrupted job. When in doubt, try `resume` first.

---

## Self-Healing

```bash
mzt run job.yaml --self-healing
mzt run job.yaml --self-healing --yes    # Auto-confirm fixes
mzt resume my-job --self-healing
```

**How it works**: After all retries exhausted, diagnostic context is collected, applicable remedies identified and ranked, automatic fixes applied without prompting, suggested fixes prompt unless `--yes`.

**Built-in remedies**: create missing workspace, create parent directories, fix path separators (backslashes on Unix), suggest Jinja fixes, diagnose auth/CLI errors.

---

## Detached Execution

The conductor should be detached for long-running or unattended operation:

```bash
# CORRECT: Fully detached conductor
setsid mzt start &

# Development: foreground (stays attached to terminal)
mzt start --foreground
```

**Why setsid for the conductor?** Creates an independent session group. The conductor survives terminal close, context compaction, and session end.

**Jobs don't need setsid.** `mzt run` submits work to the conductor and returns. The job runs in the daemon regardless of your terminal session. Only the conductor itself needs to be detached.

---

## Concert/Chaining Operations

### Self-Chaining

Self-chaining scores chain into themselves via `on_success` hooks for iterative improvement:

```yaml
on_success:
  - type: run_job
    job_path: "/absolute/path/to/my-score.yaml"  # MUST be absolute
    detached: true
    fresh: true              # REQUIRED --- clears state
concert:
  enabled: true
  max_chain_depth: 10        # Safety limit
```

**`fresh: true` is mandatory.** Without it, the chained job loads COMPLETED state and does zero work.

### Monitoring Chains

```bash
mzt list --all                       # See all jobs (current and chained)
mzt status quality-continuous-3      # Check specific job in chain
mzt history quality-continuous-3     # View history of a chained job
```

---

## Error Codes

```
E0xx Execution    E4xx State
E1xx Rate Limit   E5xx Backend
E2xx Validation   E6xx Preflight
E3xx Config       E9xx Network
```

### E0xx: Execution Errors

| Code | Retry? | Meaning |
|---|---|---|
| E001 | Yes | Timeout (command exceeded time limit) |
| E002 | Yes | Killed by signal (external termination) |
| E003 | No | Crash (segfault, bus error, abort) |
| E004 | No | Interrupted by user (SIGINT/Ctrl+C) |
| E005 | No | Out of memory (OOM killer) |
| E009 | Yes | Unknown execution error |

### E1xx: Rate Limit / Capacity

| Code | Retry? | Meaning |
|---|---|---|
| E101 | Yes | API rate limit (wait ~1hr) |
| E102 | Yes | CLI rate limit (wait ~15min) |
| E103 | Yes | Capacity exceeded (wait ~5min) |

### E2xx: Validation Errors

| Code | Retry? | Meaning |
|---|---|---|
| E201 | Yes | Expected file missing |
| E202 | Yes | Content doesn't match pattern |
| E203 | Yes | Validation command failed |
| E204 | Yes | Validation timed out |
| E209 | Yes | Generic validation needed |

### E3xx: Configuration Errors

| Code | Retry? | Meaning |
|---|---|---|
| E301 | No | Invalid configuration |
| E302 | No | Missing required field |
| E303 | No | Config file not found |
| E304 | No | YAML/JSON parse error |
| E305 | No | MCP/plugin error |
| E306 | No | CLI mode mismatch |

### E4xx: State Errors

| Code | Retry? | Meaning |
|---|---|---|
| E401 | No | Checkpoint corruption |
| E402 | Yes | State load failed |
| E403 | Yes | State save failed |
| E404 | No | State version mismatch |

### E5xx: Backend Errors

| Code | Retry? | Meaning |
|---|---|---|
| E501 | Yes | Connection failed / Job not found |
| E502 | No | Auth/authorization failed / Job not in valid state |
| E503 | Yes | Invalid response / Cannot create signal |
| E504 | Yes | Backend timeout / Pause not acknowledged |
| E505 | No | Backend not found (ENOENT) / Invalid config |

### E6xx: Preflight Errors

| Code | Retry? | Meaning |
|---|---|---|
| E601 | No | Required path missing |
| E602 | No | Prompt too large |
| E603 | No | Working directory invalid |
| E604 | No | Validation setup invalid |

### E9xx: Network Errors

| Code | Retry? | Meaning |
|---|---|---|
| E901 | Yes | Connection failed/refused |
| E902 | Yes | DNS resolution failed |
| E903 | Yes | SSL/TLS error |
| E904 | Yes | Network timeout |
| E999 | Yes | Unknown error |

---

## Anti-Patterns

| Never | Why | Do Instead |
|---|---|---|
| `timeout 600 mzt run ...` | SIGKILL corrupts state | Let Marianne handle timeouts internally |
| Assume exit_code=0 is success | Validations may have failed | Check `validation_details` |
| Debug manually first | Marianne tools provide context | `status` -> `diagnose` -> `errors` |
| Kill running job (SIGKILL) | Orphans agents, corrupts state | `mzt pause` for graceful stop |
| Edit config during run | Changes ignored until reload | Pause first, then `mzt modify` |
| Use `--fresh` on interrupted jobs | Destroys checkpoint state | Try `resume` first |
| Stop conductor with active jobs | Orphans all in-flight agents | Pause all jobs first |

---

## Global Options

All commands support:

| Option | Short | Description |
|---|---|---|
| `--version` | `-V` | Show version |
| `--verbose` | `-v` | Detailed output |
| `--quiet` | `-q` | Errors only |
| `--log-level` | `-L` | DEBUG, INFO, WARNING, ERROR |
| `--log-file` | | Path for log output |
| `--log-format` | | json, console, or both |

---

## Quick Reference

```
CONDUCTOR                         DEBUGGING ORDER
---------                         ---------------
start [--foreground|--profile]    1. mzt status ...
stop [--force]                    2. mzt diagnose ...
restart [--profile]               3. mzt errors --verbose
conductor-status                  4. Manual investigation

JOBS                              ERROR CATEGORIES
----                              ----------------
run <config> [--dry-run|--fresh]  E0xx Execution
status <job> [--watch]            E1xx Rate limit
pause <job> [--wait]              E2xx Validation
resume <job> [-c|--no-reload]     E3xx Config
modify <job> -c <cfg> [--resume]  E4xx State
diagnose <job>                    E5xx Backend
errors <job> [--verbose]          E6xx Preflight
list [--all|--status]             E9xx Network
logs <job> [--follow]
history <job>                     GLOBAL OPTIONS
clear [--job|--status]            --------------
validate <config>                 -v, --verbose
dashboard [--port]                -q, --quiet
                                  -L, --log-level
                                  --log-file
                                  --log-format
```

---

*Marianne Command Skill --- operational guide for running, monitoring, and debugging Marianne AI Compose jobs.*
