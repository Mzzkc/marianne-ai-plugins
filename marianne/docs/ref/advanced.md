# Marianne Score Advanced

> Concert mode, chaining, isolation, operational config, stale detection, and verification strategies. Load this alongside essentials.md and patterns.md for tier 4-5 scores.

---

## Config: Retry, Rate Limiting, Circuit Breaker, Cost Limits, Stale Detection

### Retry & Rate Limiting

```yaml
retry:
  max_retries: 3
  base_delay_seconds: 10
  max_delay_seconds: 3600       # 1 hour cap
  exponential_base: 2.0
  jitter: true
  max_completion_attempts: 3    # Completion prompts before full retry
  completion_threshold_percent: 50  # % passing to trigger completion mode

rate_limit:
  wait_minutes: 60
  max_waits: 24                 # 24 hours at default
```

### Other Configuration Sections

```yaml
circuit_breaker:
  enabled: true
  failure_threshold: 5          # Consecutive failures before OPEN
  recovery_timeout_seconds: 300

cost_limits:
  enabled: true
  max_cost_per_sheet: 2.00      # USD
  max_cost_per_job: 50.00

stale_detection:
  enabled: true
  idle_timeout_seconds: 1800    # 30min; see "Stale Detection" section

state_backend: sqlite           # json | sqlite (default: sqlite)
pause_between_sheets_seconds: 10
```

---

## Concert Mode (Self-Chaining)

```yaml
workspace_lifecycle:
  archive_on_fresh: true
  max_archives: 10

concert:
  enabled: true
  max_chain_depth: 5

on_success:
  - type: run_job
    job_path: "/absolute/path/to/my-score.yaml"   # MUST be absolute
    detached: true
    fresh: true                 # CRITICAL for self-chaining
```

---

## Post-Success Hooks

**Always use absolute paths for `job_path`.** Relative paths resolve from the daemon's CWD, not the score file's directory. If the conductor starts from a different directory, the chain silently breaks (file not found, hook result lost).

```yaml
on_success:
  - type: run_job               # Chain to another score
    job_path: "/home/user/project/next-job.yaml"  # Absolute!
    detached: true
    fresh: true
  - type: run_command           # Shell command
    command: "curl -X POST https://api.example.com/done"
  - type: run_script            # Script file
    command: "./deploy.sh"
```

---

## Isolation (Git Worktrees)

```yaml
isolation:
  enabled: true
  mode: worktree
  cleanup_on_success: true
  cleanup_on_failure: false     # Keep for debugging
  fallback_on_error: true
```

---

## Stale Detection and Verification Stages

Stale detection monitors stdout activity only. Child processes (pytest, mypy, ruff) run silently — if they take longer than `idle_timeout_seconds`, the entire process group is killed. This is the #1 cause of stuck verification stages.

**Fix: Either set a lenient timeout or fan-out verification into parallel instances.**

```yaml
# Option A: Lenient timeout (simpler)
stale_detection:
  enabled: true
  idle_timeout_seconds: 1800    # 30min — safe for heavy subprocesses

# Option B: Fan-out verification (more robust, parallelizes the work)
sheet:
  fan_out:
    9: 3    # Split verification into 3 parallel checks (tests / types / lint)
```

---

## Validation Timeouts

Measure first (`time pytest tests/ -x -q`), then set `timeout_seconds` to **max(measured × 1.5, 900)**. Test suites grow — leave room. Over 15 minutes? Split into targeted validations.

---

*Marianne Score Advanced --- extracted from the score-authoring reference.*

---

## Flow control: loops and triggers

Declare `sheet.loops` by an inclusive sheet span such as `1` or `2-5`.
Every loop needs `count`, an `until` expression, or both; `max_iterations`
remains a safety cap. A loop executes its range once before deciding whether
to repeat. Nested spans are allowed, but partially overlapping spans are not.
The index is available in prompts as `{{ loops.pass_no }}` and
`{{ pass_no }}`, in scoped validations as `{pass_no}`, and in expressions as
`loop.pass_no`. Under `fan_out`, author the stage numbers; Marianne expands
them into concrete sheet ranges during load.

```yaml
sheet:
  size: 1
  total_items: 2
  loops:
    1:
      index: pass_no
      until: 'file("done.txt").exists'
      max_iterations: 5
  triggers:
    1:
      on_fail:
        - escalate: Inspect the failed pass before resuming.
```

Expressions can read declared variables, loop indices, sheet facts, and
bounded file facts. They evaluate at the loop boundary. A file condition can
use `.exists`, `.modified`, `.contains("text")`, or `.matches("regex")`.
`validation(...)` and `output(...)` are reserved and fail score load. An
undefined runtime variable fails the condition when reached.

`on_success` and `on_fail` take ordered lists of single-action objects:
`goto`, `skip`, `pause`, `escalate`, `run`, `concert`, or `continue`.
An `on_fail` handler owns the failure; it replaces ordinary retry, fallback,
completion mode, and healing for that sheet. `run` executes a bounded command
off the baton loop and may repeat after a crash. Make its side effects
idempotent; `MARIANNE_FLOW_ATTEMPT` records the replay count. A `concert`
action submits a child score without waiting for it. Flow state and sheet
state persist together in the job checkpoint.

See `examples/patterns/convergence-loop.yaml` and
`docs/configuration-reference.md` in the Marianne venue for a runnable
CLI-only example and the full field contract.
