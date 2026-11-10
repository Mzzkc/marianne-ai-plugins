---
name: command
description: Use when submitting, monitoring, debugging, or recovering Marianne score and persistent-agent lifecycle runs. Covers runtime job_id handles, delivery receipts, lifecycle debt, diagnostics, recovery, and anti-patterns that lose work. Do NOT use for writing score configs (use score-authoring instead).
---

# Marianne Command Skill

> **Purpose**: Submit, monitor, debug, and recover Marianne score runs. Covers the conductor, runtime job_id handles, diagnostics, config reload, recovery, and the anti-patterns that lose work.

---

## Triggers

| Use This Skill | Skip This Skill |
|---|---|
| Running/monitoring Marianne scores | Writing new score configs (use marianne-score-authoring) |
| Debugging failed or stuck score runs | |
| Resuming interrupted score runs | |
| Understanding validation failures | |
| Conductor operations | |

---

## Conductor: The Required Foundation

Use this skill directly within the caller's authorized operational scope. Expert's
operate/debug playbooks provide deeper diagnosis when needed; invoking expert,
conducting or composing is not a prerequisite. Reuse the supplied score and complete
qualified invocation. Check current `mzt COMMAND --help` for flags and current
source for disputed semantics; old recipes are not live capability evidence.

Return the actual `job_id`, admitted/terminal state, meaningful validation results,
surviving artifacts, failed stage and supported next action. Distinguish message
delivery, activation, native completion and product acceptance. Routine controls do
not assign an ordinary conductor daemon maintenance or implementation authority.

**The conductor (daemon) is required for `mzt run`.** Without a running conductor, only `--dry-run` and `mzt validate` work.
Daemon start/stop/restart requires authority over that service. Ordinary job control
does not grant authority to disrupt other active performances.

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
| `mzt stop` | Stop the conductor (**only when no scores are running**). Prints the in-flight sheets the graceful drain will wait on. A boundary-paused job does not hold the drain: its unfinished sheet is ended at once and re-runs on resume, so `mzt pause` every active job, then `mzt stop --wait`, restarts promptly (GH #476) |
| `mzt stop --wait=` | Also wait (30s default, `--wait=N`) for the exit; on timeout it re-probes and names what the drain is still waiting on |
| `mzt stop --force` | Force-kill the conductor --- **NEVER with active scores** |
| `mzt restart` | Stop and restart |
| `mzt restart --profile dev` | Restart with a profile |
| `mzt conductor-status` | Check if conductor is running |
| `mzt conductor-status --json` | Raw daemon status (config generation, live per-model caps) |
| `mzt instruments resolve SCORE` | What each sheet's binding resolves to on THIS machine — alias/class → profile, model, fallbacks — and how many distinct bindings a fan-out really has. Run it before trusting a score's diversity or tier claims. |
| `mzt instruments check NAME --live` / `mzt doctor --live` | Prove a profile against its installed CLI with a real prompt (and schema mode if declared). Run after installing or upgrading a CLI, after editing a profile, and before a long run; readiness only proves the binary is on PATH |
| `mzt instruments prices` | Which model price rows have drifted from models.dev (builtin and user layers apart). Run before trusting a cost figure or sizing a `cost_limit_usd`; `--write` updates builtin rows only, `--offline`/`--snapshot` compare against a saved copy. Exit 1 means drift remains |
| `mzt conductor reload` | Hot-reload config + instrument profiles WITHOUT restart (GH #408) |

`mzt conductor reload` re-reads the config file and instrument profile
directories on the running conductor (same path as SIGHUP) and prints what
was `applied` and what was `declined` (restart-only fields keep the running
value). Reloads are fail-closed: an invalid config changes nothing. Prefer
this over `mzt restart` whenever the change is reloadable — a restart
orphans nothing but still pauses admission; a reload does not. Cap changes
apply live: raised caps dispatch waiting sheets, lowered caps drain without
cancelling in-flight work.

### How Scores Route Through the Conductor

Fleet members (`type: fleet`) are jobs named `<fleet>--<stem>` (GH #514): `mzt status <fleet>--integration`, never `mzt status integration`, which may be an unrelated older job. When a wave member fails, the fleet drops the groups that depend on it (`fleet.group_dependencies_failed` in the log); fix and resubmit that member under its fleet ID, then `mzt resume <fleet>` re-arms the dropped groups once their dependencies are complete (GH #515). When you run `mzt run config.yaml`, the CLI checks for a running conductor via Unix socket. If found, the score is submitted through IPC and the CLI returns a runtime `job_id`. The conductor manages score execution, rate limit coordination across concurrent runs, and event routing. If no conductor is found, the command exits with an error.

**The conductor runs submitted scores.** `mzt run` is a client that submits a score and returns. The conductor keeps executing the score regardless of whether your terminal stays open. `job_id` is the runtime identifier the conductor returns for that submitted score.

**NEVER stop the conductor while scores are actively running.** Killing the daemon can orphan in-flight musician processes and corrupt score state --- sheets can get stuck as `in_progress` with no validation or cleanup. To reload config on a running score, use `mzt modify my-job -c new.yaml --resume --wait`. Before an authorized service stop, have its owner settle affected work through supported controls; a paused parent alone does not prove all active children stopped.

"Marianne conductor busy or unresponsive (PID n alive); running state is
unknown" is not "not running": the conductor is alive and blocked on disk (its
listen queue is full, so a connect lands and the first write fails). Do not
start or restart it; `mzt conductor-status` shows the PID, whether it is alive,
the host I/O pressure and the event-loop lag even when the socket is silent.
Wait for pressure to clear and retry a read-only command. Absence needs two
proofs, a missing socket or a refused connection with no live PID (GH #455).

---

## Score Lifecycle

For a persistent-agent score, first read
`${CLAUDE_PLUGIN_ROOT}/docs/ref/modern-agents.md`. Keep the runtime `job_id`
separate from the semantic agent ID. Before submission, confirm the canonical
agent data root, run any package/seed update in `--dry-run`, validate the exact
score, inspect live instrument evidence, and verify all load-bearing injections
are explicit and `required: true`.

### Submitting a Score

```bash
mzt run config.yaml              # Submit (routes through conductor)
mzt run config.yaml --dry-run    # Preview without running (no conductor needed)
mzt run config.yaml --fresh      # Fresh start (clears previous state)
mzt run config.yaml -s 5         # Start from sheet 5
mzt run config.yaml --self-healing      # Auto-diagnose + fix on retry exhaustion
mzt run config.yaml --self-healing --yes  # Auto-confirm suggested fixes
mzt run config.yaml -j           # JSON output
mzt run config.yaml --job-id NAME  # Name this run (one score, many commissions)
```

The default job ID is the score's filename stem. To run a shipped score for a
second commission, keep the file and name the run: `mzt run score.yaml --job-id
NAME --var ...` (a score without `workspace:` then gets `~/workspaces/NAME`).
Consume the returned handle and use it for status, pause, resume and cancel.
A renamed copy is for a score whose behaviour changes, not for a new run (GH #505).
Run all required pre-admission gates in a fail-fast invocation. A later successful
command cannot repair an earlier failed gate. Keep context/queue/setup/validation
and result-consumption time inside the engagement's original delivery budget.

| Option | Short | Description |
|---|---|---|
| `--dry-run` | `-n` | Preview execution (no conductor needed) |
| `--start-sheet` | `-s` | Override starting sheet |
| `--fresh` | | Clear previous state and start over |
| `--self-healing` | | Auto-diagnose and remediate on failure |
| `--yes` | | Auto-confirm self-healing fixes |
| `--json` | `-j` | Machine-readable output |

Workspace overrides are an expert/debug path, not ordinary composer guidance. In normal use, the score's `workspace:` field and the conductor registry determine where state and artifacts live.

### Monitoring

Use the runtime `job_id` returned by `mzt run` for these commands. Examples
below use `my-job` as that handle.

```bash
mzt status my-job                # Check status
mzt status my-job --watch        # Live monitoring (refreshes every 5s)
mzt status my-job -W -i 10       # Watch with 10s interval
mzt status my-job -j             # JSON output (`loops` carries each span's pass / exit reason / spend)
mzt list                         # Every live score run (never paged out)
mzt list --all                   # Plus terminal history, --limit (20) caps only that part
mzt list --status running        # Filter by status
mzt logs my-job                  # View conductor-owned log sources
mzt logs my-job --follow         # Tail score-specific logs
mzt logs my-job --lines 200      # Last 200 lines
mzt logs my-job --level ERROR    # ERROR and above
mzt history my-job               # Every attempt: instrument, outcome, exit, cause
```

| Command | Key Options |
|---|---|
| `status` | `--watch` / `-W`, `--interval` / `-i`, `--json` / `-j` |
| `list` | `--all`, `--status` / `-s`, `--limit` / `-l` |
| `logs` | `--follow` / `-F`, `--lines` / `-n`, `--level` / `-l`, `--json` / `-j` |
| `history` | `--json` / `-j` |

For each attempted sheet, inspect the hash-only receipt below
`<workspace>/.marianne/context-receipts/<job>/`. Join it to terminal sheet and
validation evidence before claiming that identity, memory, techniques, or a
cadenza reached the performer. A registry entry, association, or agent name is
not delivery evidence.

After targeted work, verify the immediate AAR/recent-memory write and the
pending lifecycle debt file. Do not clear or summarize away that debt. Run the
agent's lifecycle-integration score when authorized, retain before/after memory
hashes and agent-authored seed-conflict resolutions, then require a later
engagement to recall and apply a grounded learning.

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

**How it works:** Creates a pause signal file in the workspace. The running score checks for this file between sheets, saves state, and transitions to PAUSED. Signal file is removed after acknowledgment.

### Resuming

```bash
mzt resume my-job                # Resume (auto-reloads config from YAML)
mzt resume my-job -c fixed.yaml  # Resume with a different config file
mzt resume my-job --no-reload    # Resume using cached snapshot
mzt resume my-job --force        # Force resume a completed score run
mzt resume my-job --self-healing # Resume with self-healing
```

| Option | Short | Description |
|---|---|---|
| `--config` | `-c` | Override config file |
| `--no-reload` | | Use cached snapshot instead of auto-reloading |
| `--force` | `-f` | Resume even if completed |
| `--self-healing` | | Enable auto-diagnosis on failure |

### Modifying Running Scores

For a new assignment on an unchanged provided engagement, use its supported
task/cadenza surface instead of editing the managed score. Editing a cadenza after
dispatch does not prove the active prompt received it. Check the supported steering
operation's actual delivery and later behavioral adoption. If that operation is
unavailable, have the authorized owner settle affected work before continuing only
unfinished obligations with corrected context; preserve earned prefix, original
deadline and life. Config reload alone is not proof of live prompt replacement.

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
mzt clear                        # Clear completed/failed/cancelled score runs
mzt clear --job my-job           # Clear a specific runtime job_id
mzt clear --status failed        # Clear only failed score runs
mzt clear --older-than 3600      # Clear score runs older than 1 hour
mzt clear --yes                  # Skip confirmation
```

### Other Commands

```bash
mzt validate config.yaml         # Pre-flight check (no conductor needed)
mzt validate config.yaml --strict # Fail on unsuppressed warnings as well as errors
mzt validate config.yaml --json   # Stable issue keys plus summary/suppressed
mzt diagnose my-job              # Full diagnostic report
mzt errors my-job --verbose      # Error details with stdout/stderr
mzt dashboard                    # Start web dashboard (default port 8000); /orchestra is the fleet on stage, live + replay
mzt help                         # List commands, including patterns-list
mzt doctor                       # Environment health; lists user profiles no submitted score names (GH #443);
                                 # Providers: REA's own toolchain gaps for each mcp_pool.servers entry that runs it (GH #499)
mzt telemetry status|consent|export|flush # Opt-in community telemetry: off by default, never automatic; see docs/telemetry.md (GH #146)
#   and names a personal profile whose ambient credentials no longer reach it (GH #335 filters by default)
```

Skills ship from the plugin tree, and every harness keeps its own copy, so a
skill edit is invisible to conductors until it is distributed. One tool does the
whole distribution, on every host where the checkout lives:

```bash
python3 plugins/scripts/install_skills.py status    # which harness roots lag the source
python3 plugins/scripts/install_skills.py install   # all roots current, preimages archived, verified
python3 plugins/scripts/install_skills.py verify    # recompute every installed copy against source
```

It discovers the harness roots present on the host (Claude Code, Codex, Gemini,
ZCode, OpenCode, the shared `.agents` surface, the registered Claude plugin cache,
and the Windows-side roots when run inside WSL), archives each target's exact
preimage before writing, and refuses a dirty source tree. Run it on each host
after a skill commit lands; `status` exits 1 while any root lags.

`mzt doctor` reports, under "Instrument hygiene", every `~/.marianne/instruments/`
or `.marianne/instruments/` profile that no score the conductor has been given
names and no class chain includes. It never deletes them. Read the list as the
reuse rule's symptom: a seat is an alias over an existing profile, so archive the
file or submit the score that needs it, and course-correct the score or generator
that wrote it.
Migrating a fork to an alias: find the builtin it copies (`cli.command.executable`
tells you), diff the two ignoring `name`/`default_model`/`models`, send any
override everyone needs to the builtin, rewrite each score's seat as
`{profile: <builtin>, config: {model: <pin>}}` at that score's next natural edit
(never mid-run), and archive the file with a manifest once `grep -rl <name>` over
the live SCORES tree is empty. Doctor counts references from jobs the conductor
has been given, so a file last used months ago still reads as referenced there;
the grep is the truth.

`mzt validate` exits 0 with warnings by default, 1 for errors (or unsuppressed
warnings under `--strict`), and 2 when YAML cannot be read or parsed into a
score. `--errors-only` filters displayed findings without changing the exit
rule. INFO findings require `--verbose` in terminal output. A score may list
reviewed WARN/INFO codes under `validate.suppress`; V012 rejects attempts to
suppress an ERROR or an unknown code.

Scores may name a capability class (`instrument: strong`) instead of a profile.
Validation then reads the same three class-map layers the conductor reads
(packaged default, `~/.marianne/classes.yaml`, venue `.marianne/classes.yaml`;
the venue file is relative to each process's working directory, so the
conductor started from `$HOME` reads the user file as its venue layer and a
project venue file the score depends on is refused at submit, GH #510)
and reports class problems with position and fix hint: V310 ERROR when a class
cannot resolve on this machine, V311 WARNING when part of its chain cannot run
here (the job starts at the first available entry), V321/V322 for alias
misuse, V323 when a `model` is pinned against a class primary, V324 for an
invalid classes file the score depends on, and V325 INFO showing each used
class's resolved chain. `--json` carries the per-sheet resolution and every
layer path with its sha256 under `summary.classes`.

---

## Diagnose the affected operation

Reuse current status and the reported failure. Start with native status when state
is unknown, then request only diagnostics needed for the affected boundary. A known
causal result does not require replaying the entire diagnostic ladder. Distinguish
product, fixture/observer and venue failures before choosing the repair owner.

```bash
# 1. Establish state when not already known
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

# Use targeted manual investigation when the native evidence leaves a material gap
```

### Understanding `mzt status` Output

The Cost Summary's token counts are summed from every sheet's attempts. `Input
tokens` is what the harness calls input, which on Anthropic and OpenAI excludes
tokens served from the prompt cache; a profile with `cache_read_tokens_path`
adds a `Cache read` line with that count and its share of input. Read the share
before judging a sheet's token efficiency: a long agentic sheet is mostly cache
reads, and a change that only lowers `Input tokens` has not touched most of
what the provider processed.

A cost that looks wrong (not zero, wrong) is usually a stale price row, not a
counting bug: `mzt instruments prices` names the rows that differ from the
provider's current prices. A `$0.00` on a subscription route is the plan's row,
not a measurement.

- **Status**: RUNNING, COMPLETED, FAILED, PAUSED, CANCELLED
- **Validation**: Pass/Fail per sheet (a sheet can execute successfully but fail validation)
- **Sheets**: N/M completed, which failed, which skipped
- **Loops**: one line per `sheet.loops` span with its pass or exit reason and spend. `condition_met`
  is the loop finishing its job (also when the finishing pass reached a cap: `until` is judged
  first); `cost_limit_exceeded` or `max_iterations` means the `until` was NOT
  met and the next stage ran on an unfinished span: read the span's last ledger before trusting
  anything downstream, and raise the cap or the iteration count in the score if the work was real.
- **Cost**: the job tracker's total when one wrote it, otherwise the sum of every sheet's accumulated
  attempt cost `(from sheets)`, which is the figure the loop and sheet caps read; `$0.00` with
  `cost-uncertain` sheets means no priced route, not free work.
- **Rate limits**: Current wait count
- **Instrument column**: `codex-cli (was claude-code: execution_timeout after 30m)` means the
  fallback played and the primary spent 30 minutes first; the duration beside the status is
  the winning attempt's only. `mzt diagnose` lists every attempt with its instrument,
  duration, outcome and error code under the timeline, and under a failed attempt the
  cause the classifier picked (`agent process killed by SIGKILL before signalling
  completion`) — read that line before the logs; the category word (`TRANSIENT`) is the
  symptom class, the line is the cause.

**Critical insight**: `exit_code=0` does not establish successful validation.
`validation_passed=true` proves only the configured checks; weak checks can still
accept an unusable result. Consumer meaning and independent acceptance remain separate.

### Common Failure Patterns

| Symptom | Likely Cause | Fix |
|---|---|---|
| File exists but "missing" | Wrong path syntax (`{{ }}` vs `{}`) | Check validation path syntax |
| Validation always passes | No validations configured, or too broad | Add meaningful validations |
| Pattern doesn't match | Regex anchors, escaping, or content changed | Test regex with `python3 -c "import re; ..."` |
| Command fails | Wrong `working_directory` or shell assumptions | Check CWD, test command manually |
| Sheet "passes" but work is bad | Validations too weak (file_exists only) | Add content checks or command validations |
| Config changes ignored | `--no-reload` used or file deleted | Config auto-reloads by default; check YAML file exists |
| Score run hangs forever | Custom instrument profile lacks an auto-approve flag, or an interactive session is stuck on an unhandled dialog | Built-in profiles auto-approve; for custom profiles set `auto_approve_flag`; for interactive stalls check `tmux -L marianne attach -t <session>` and add a `startup_gates` entry |
| Chained score does nothing | Missing `fresh: true` in hook | Add `fresh: true` to self-chain hooks |
| The final sheet passed but no `--chainN--` child appeared | The concert submission was refused — the conductor log has `flow.concert.refused` with the reason (`mzt status` shows the job COMPLETED either way); before 6025cc63 a parent resumed with `--config <copy>` refused its own child as an active duplicate | Read the refusal reason; a depth limit or missing child score is the score's to fix; re-run the score's next iteration by hand with `mzt run --fresh` |
| An interactive sheet fails E999 with `agent process killed by SIGKILL` / `exited with status N before signalling completion` | The agent's own process ended (tmux kept the dead pane and read its status): a signal names the killer's shape (SIGKILL: OOM/earlyoom/an external kill; SIGTERM: a shutdown or cleanup), an exit status is the CLI's own failure — read `~/.marianne/interactive-logs/<session>.log` for its last screen | Fix the cause the status names; a retry is scheduled automatically |
| An interactive sheet fails E999 with `agent session vanished` | tmux no longer holds the session at all: the `marianne` tmux server died or something killed the session by name | Check `tmux -L marianne ls`, the conductor log for `interactive_session_control_failure`, and anything sweeping `mzt-*` sessions |
| A sheet sits at 0 bytes of output until the sheet timeout, then the next instrument finishes in a minute | The agent session died at start (a stall is not thinking); the shipped streaming profiles end it after `first_output_timeout_seconds` (90 s) as a stale timeout and fall back; a custom `jsonl` profile needs the key set | Set `cli.first_output_timeout_seconds` on streaming profiles; read `mzt diagnose` for the `plugin_cli_first_output_stall` line |
| A sheet with a `kind: mcp` technique reports `provider_unavailable` from REA, or two artifact jobs read each other's target | REA's engine (Ghidra 12.1.x, Hopper, IDA) is missing or wrong-versioned, or a previous sheet left its target open on the pool's one shared REA session | `mzt doctor` Providers names the gap in REA's words; the sheet records it under Limitations instead of guessing. Every analyst sheet ends with `close_binary`; run one REA score at a time until the pool scopes state per job (GH #499) |
| A `kind: mcp` sheet's `tools/list` or `tools/call` hangs until its own timeout while `initialize` answers instantly, and the conductor log has `mcp_bridge.upstream_read_failed` | The pool bridge's upstream reader died (a reply line over its bound, or the server closed stdout) on a conductor older than GH #520; the process is alive so the pool kept the socket | On GH #520 and later the client gets JSON-RPC error `-32000 MCP pool bridge '<name>': <reason>` and the monitor restarts the server; before it, `systemctl --user restart marianne-conductor.service` when nothing is running |

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

**Modify a running score's config:**
```bash
mzt modify my-job -c updated.yaml --resume --wait
```

---

## Recovery Procedures

### Rate Limit Recovery

Marianne auto-waits when rate limited (default: 60 minutes, up to 24 cycles).
A sheet shown WAITING whose instrument is not under "waiting for rate limit" in
`mzt status` is stranded (its fallback advanced while a refusal was in flight);
a bare `mzt clear-rate-limits` re-queues it, as does pause then resume.
A loop member reopened for its next pass that shows its rate-limited PRIMARY
(`antigravity (was …)` gone, back to `antigravity`) and sits PENDING while its
fallback seats idle is GH #521 on conductors before it; `mzt clear-rate-limits -i
<instrument>` makes dispatch re-hit the limit and take the fallback. On GH #521
and later, dispatch advances the chain itself.
A quota refusal counts as a rate limit wherever the CLI reports it: stderr, or
the terminal record of a `json`/`jsonl` stream (Codex `usage_limit_exceeded`;
Claude Code `is_error` + `api_error_status: 429`, "hit your weekly limit"; the
Z.AI gateway's "Weekly/Monthly Limit Exhausted. Your limit will reset at <ISO
time>" on either claude-code or opencode, GH #509). If a sheet instead burns
retries as E009 on such text, that is a profile pattern gap: file it against the
builtin profile (GH #507). A user-layer copy of a builtin replaces it whole, so a
pattern the builtin gains is missing there until re-copied; `mzt instruments
check <name> --live` shows what the route actually answers.

```bash
mzt status my-job    # Shows PAUSED (rate_limited)

# Resume only after capacity returns, within a supported state and remaining budget
mzt resume my-job
```

### Validation Failure Recovery

```bash
# 1. Check WHICH validation failed
mzt errors my-job --verbose

# 2a. Work complete but validation config is wrong --- fix YAML and resume
mzt resume my-job    # auto-reloads fixed config

# 2b. Work incomplete: resume only after the owner has a material repair/recovery premise
mzt resume my-job
```

An exhausted retry count calls for an owner decision, not an automatic reset.
If capacity or a causal repair is still unavailable, return the surviving work,
affected obligation and qualified alternatives within the original delivery window.

### Interrupted Score Recovery

```bash
# For an interrupted run whose current state supports resumption
mzt resume my-job
```

Preserve completed work and failed history; recover the smallest unfinished
obligation through current supported controls. Resume does not prove provider-session
continuity or reset the commission's deadline. On refusal, diagnose the actual
cause before another attempt; do not escalate blindly to force or fresh. After two
failed successors for one outcome, return the changed-premise/remaining-reserve
decision to its accountable owner instead of automatically repeating the attempt.

### State Corruption Recovery

Preserve state and evidence before repair. Do not delete a state database to make
an interrupted run appear new. For completed work incorrectly marked failed,
`mzt recover my-job --dry-run` can check its validations without changing state;
applying recovery requires the relevant operational authority and applicable checks.
That command does not establish repair of arbitrary checkpoint corruption. Route
actual corruption to the authorized venue owner and retain the unfinished obligation.
Confirm actual skipped/executed sheets after any supported partial continuation;
a requested starting sheet alone is not evidence that prior purposes stayed skipped.

### `--fresh` vs `resume`

| Situation | Use |
|---|---|
| Score run interrupted mid-progress | `mzt resume my-job` |
| Score run failed, config needs fixing | `mzt resume my-job` (auto-reloads fixed YAML) |
| Self-chaining: completed an iteration | `--fresh` (via hook config) |
| User explicitly wants to start over | `mzt run my-score.yaml --fresh` |
| Score run was cancelled or partially failed | `mzt resume my-job` (try first) |

**`--fresh` re-registers the score and re-runs all sheets.** Archiving depends on
`workspace_lifecycle.archive_on_fresh`; do not assume a preserved or archived subject
without checking the actual configured behavior. Reserve fresh starts for intended,
authorized replay, not recovery of already completed work.

---

## Remediate a failed job by hand

`mzt remediate JOB_ID [--sheet N] [--dry-run|--yes] [--json]` runs the same
remedy registry and healing coordinator the conductor's self-healing uses, from
the persisted job context and attempt history. It proposes or applies a remedy
and never changes checkpoint status or restarts execution: resume the job
yourself afterwards (GH #147).

## Self-Healing

```bash
mzt run score.yaml --self-healing
mzt run score.yaml --self-healing --yes    # Auto-confirm fixes
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

**Score runs don't need setsid.** `mzt run` submits work to the conductor and returns. The score runs in the daemon regardless of your terminal session. Only the conductor itself needs to be detached.

---

## Concert/Chaining Operations

### Self-Chaining

Self-chaining scores chain into themselves via `on_success` hooks for iterative improvement:

```yaml
on_success:
  - type: run_job
    job_path: "/absolute/path/to/my-score.yaml"  # MUST be absolute
    fresh: true              # REQUIRED --- clears state
concert:
  enabled: true
  max_chain_depth: 10        # Safety limit
```

**`fresh: true` is mandatory.** Without it, the chained score loads COMPLETED state and does zero work.

### Monitoring Chains

```bash
mzt list --all                       # See all score runs (current and chained)
mzt status quality-continuous-3      # Check specific runtime job_id in chain
mzt history quality-continuous-3     # View history of a chained score run
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
| E501 | Yes | Connection failed / runtime job_id not found |
| E502 | No | Auth/authorization failed / score run not in valid state |
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
| Repeat diagnosis despite a current causal result | Consumes the delivery window | Reuse status/evidence and inspect only the unresolved boundary |
| Kill running score (SIGKILL) | Orphans musicians, corrupts state | `mzt pause` for graceful stop |
| Edit config during run | Changes ignored until reload | Pause first, then `mzt modify` |
| Use `--fresh` on interrupted scores | Re-runs completed purposes | Preserve work and recover the unfinished obligation |
| Stop conductor with active scores | Orphans in-flight musicians | Service owner settles affected work before an authorized stop |

---

## Global Options

All commands support:

| Option | Short | Description |
|---|---|---|
| `--version` | `-V` | Show version |
| `--verbose` | `-v` | Detailed output |
| `--quiet` | `-q` | Errors only |
| `--log-level` | `-L` | DEBUG, INFO, WARNING, ERROR |
| `--log-file` | | CLI-process diagnostic log path |
| `--log-format` | | CLI-process log format: json, console, or both |

---

## Quick Reference

```
CONDUCTOR                         DEBUGGING ORDER
---------                         ---------------
start [--foreground|--profile]    1. mzt status ...
stop [--force]                    2. mzt diagnose ...
restart [--profile]               3. mzt errors --verbose
conductor-status                  4. Manual investigation

SCORE RUNS                        ERROR CATEGORIES
----------                        ----------------
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

*Marianne Command Skill --- operational guide for running, monitoring, and debugging Marianne AI Compose score runs.*
