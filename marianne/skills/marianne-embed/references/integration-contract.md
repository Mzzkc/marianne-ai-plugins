# Marianne Embed Integration Contract

## Bridge Usage

Run the bundled bridge with the Python environment that can import Marianne, or
pass the source checkout:

```bash
python scripts/marianne_bridge.py daemon_status \
  --marianne-root /home/me/Projects/marianne-ai-compose < /dev/null
```

All commands read a JSON object from stdin and write one JSON object to stdout.
Logs from Marianne imports are redirected to stderr.

## Commands

### `daemon_status`

Payload:

```json
{}
```

Result:

```json
{ "ok": true, "connected": false, "message": "Cannot connect..." }
```

### `start_conductor`

Use only for explicit operator action. Do not stop/restart from embedded apps
while jobs are active.

Payload:

```json
{
  "mzt_bin": "/path/to/.venv/bin/mzt",
  "cwd": "/path/to/project",
  "profile": "dev"
}
```

### `validate_score`

Validate from a path:

```json
{ "path": "/path/to/scores/post-mill.yaml", "workspace_path": "/path/to/project" }
```

Validate unsaved content:

```json
{
  "filename": "edited-score.yaml",
  "content": "name: ...",
  "workspace_path": "/path/to/project"
}
```

### `submit_job`

Payload:

```json
{
  "config_path": "/path/to/scores/job.yaml",
  "workspace": "/optional/workspace",
  "client_cwd": "/path/the/user/app/means",
  "fresh": false,
  "dry_run": false,
  "start_sheet": null,
  "self_healing": false,
  "self_healing_auto_confirm": false,
  "escalation": true,
  "runtime_variables": {
    "run_label": "dashboard-2026-06-19"
  }
}
```

Require confirmation before `fresh: true`. Validate before submit. Refuse submit
if `daemon_status.connected` is false unless the user has explicitly started the
conductor and status has been refreshed.

If submitting unsaved editor content, write it to a durable app-owned `.yaml`
file before calling `submit_job`. Do not use a temporary file that is deleted as
soon as the HTTP request returns; the conductor stores the submitted path and may
read it later when the queued task starts.

The bridge returns `ok: false` when the daemon response status is `rejected` or
`error`. If you call daemon IPC directly, apply the same rule: only `accepted`
and `pending` are successful submissions.

### `list_jobs`, `job_status`, `pause`, `resume`, `cancel`

`list_jobs`:

```json
{ "limit": 50 }
```

Job-specific commands:

```json
{ "job_id": "post-mill", "workspace": "/optional/workspace" }
```

## Backend Pattern

Use a short-lived child process bridge unless your app already runs inside the
same Python environment as Marianne. This keeps import-time logging, dependency
versions, and async event loops isolated from the host app.

Pseudo-code:

```text
validate(score)
status = daemon_status()
if !status.connected: return 409
check required read-only external credentials/account safety gates
if score_is_inline: config_path = persist_durable_yaml(score)
audit("submit_requested", payload_without_secrets)
response = submit_job(payload)
if response.submit.status not in ["accepted", "pending"]: return 409
audit("submit_accepted", response)
```

## UI Pattern

Show domain concepts, not Marianne internals:

- "Run clip generator" instead of "submit clip-mill.yaml".
- "Schedule approved clips" instead of "post-mill fresh run".
- "Validate settings" before "Run".
- "Start conductor" only when status is down.
- Disable run buttons when conductor is down.
- Warn on `fresh`, `start_sheet`, and score/settings edits.

## Settings Editing

When exposing score-adjacent settings:

1. Save to the real file the score reads.
2. Validate YAML before writing.
3. Make a timestamped backup before replacing the file.
4. Run score validation after saving when practical.
5. Do not imply an edit affects behavior until you have traced the score path
   that reads it.

## Artifact-Derived Status And Reports

Use source artifacts as the authority for dashboards and wrapper reports:

- Job state comes from daemon status/list responses, not the lifetime of an
  `mzt run` subprocess.
- Logs can come from file logs, observer events, snapshots, interactive
  transcripts, or conductor events. Show explicit unavailable/no-lines states
  when none exist.
- For `job_status` views, do not infer active work from every non-terminal
  sheet. Prefer `job.current_sheet` when present; otherwise choose sheets whose
  status is actively executing or blocked in place, such as `dispatched`,
  `running`, `waiting`, `rate_limited`, or `retry_scheduled`. Treat `pending`
  as queued future work, not the active sheet, and render the actual sheet
  status verbatim.
- Reports that include counts should be generated from JSON artifacts or checked
  against them before display. Do not let model prose become the source of truth.
- Do not present a report file as the result of the current run merely because
  the expected path exists. Verify freshness with a job id, run id, timestamp,
  or artifact metadata; otherwise label the file as stale/previous.
- If an embedded action depends on external account-safety gates, preflight
  them with the same read-only account query the score depends on. Do not treat
  an exported token or configured CLI as authorization proof; invalid scopes,
  expired OAuth grants, and wrong organizations should stop before submit.
- External rate limits should produce a deferred state with retry metadata when
  no side effects happened. Continue downstream only through explicit skipped
  artifacts so dashboards can show "nothing was attempted" accurately.

## Known Pitfalls

- Dashboard HTTP routes may be incomplete compared to `JobRequest`.
- Dashboard pages can also have stale frontend assumptions. Verify live browser
  behavior, not just endpoint status: editor widgets should mount once, fetches
  should have zero failed requests, and displayed analytics fields should match
  API response names and units.
- Dashboard log views must not sit blank forever. A missing source and an empty
  source are different states; render both explicitly.
- Importing Marianne can log to stdout; redirect stdout while importing/calling
  if your process must emit machine JSON.
- `mzt run` submits work and returns when the conductor is running. Do not treat
  the CLI process lifetime as the job lifetime.
- Completed CLI exit code is not the same as validation success.
- Relative config paths need `client_cwd` or absolute paths.
