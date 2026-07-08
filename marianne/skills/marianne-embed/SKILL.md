---
name: marianne-embed
description: Use when embedding Marianne behind another app, local dashboard, web service, automation wrapper, or agent-facing tool. Covers daemon IPC bridges, hidden score submission and runtime job_id monitoring, score validation, runtime variables, conductor lifecycle guardrails, and building a product-facing abstraction over Marianne without exposing Marianne internals. Do not use for authoring score YAML from scratch or ordinary CLI run debugging unless the task is specifically about wrapping those operations.
---

# Marianne Embed

Build applications that use Marianne as an internal orchestration engine. Keep
the user-facing surface domain-specific; hide `mzt`, workspaces, sockets, and
score internals unless the operator explicitly needs them.

## Default Architecture

Use a thin backend adapter:

1. Validate score content or config path before every submit.
2. Check conductor status.
3. Submit scores through daemon IPC, not a long-running `mzt run` process.
4. Poll/list submitted scores through daemon IPC; preserve `job_id` as the conductor's runtime handle.
5. Keep an app-local audit log for every submit, cancel, resume, and settings write.
6. Expose product verbs in the UI: `Generate clips`, `Schedule approved clips`,
   `Verify posts`, not `run scores/post-mill.yaml --fresh`.
7. If the app submits edited or inline score content, persist it to a durable
   app-owned YAML path before submit. The conductor stores a path and may read it
   after the request returns.

Prefer the bundled bridge script for JSON IPC. Resolve `scripts/` relative to
this skill directory:

```bash
python scripts/marianne_bridge.py daemon_status \
  --marianne-root /path/to/marianne-ai-compose < /dev/null
```

For payload schemas and examples, read `references/integration-contract.md`.

## Guardrails

- Never stop or restart the conductor from an app while submitted scores are active.
- Treat `fresh` as destructive: require explicit user confirmation.
- Do not assume Marianne's dashboard HTTP API exposes all daemon fields. Audit it
  first; daemon `JobRequest` has historically been broader than dashboard submit.
- Do not treat a submit RPC as successful just because IPC returned. Check the
  daemon response status; only `accepted` and `pending` mean the conductor took
  the score.
- Do not parse human CLI output when a typed daemon method or JSON command exists.
- Redirect or isolate Marianne logs so machine JSON channels stay parseable.
- Use `client_cwd` when submitting relative score paths from an app.
- Preserve `runtime_variables`, `start_sheet`, `dry_run`, `self_healing`,
  `self_healing_auto_confirm`, `escalation`, `workspace`, and `fresh` if your UI
  exposes them.
- Make dashboard widgets idempotent. Alpine auto-calls an `init()` method; avoid
  also calling it with `x-init` unless there is a once-only guard.
- Make log panes truthful: show explicit unavailable, loading, no-lines, and
  disconnected states. A blank panel is a bug, not a neutral state.
- Treat operational reports as artifact-derived. If an LLM writes prose, validate
  counts against source JSON/files before showing them as facts.
- External API rate limits or provider outages should become explicit deferred
  states when no mutation occurred. Do not let downstream stages imply uploads,
  posts, archives, or other side effects happened.

## When To Use Other Marianne Skills

- Writing or fixing score YAML: use the Marianne score-authoring skill.
- Operating a score directly as a composer or debugging a failed run: use the Marianne
  command skill.
- Embedding Marianne behind another tool or service: use this skill.

## Implementation Pattern

Keep three layers separate:

- **Adapter**: imports Marianne APIs or invokes the bundled bridge.
- **Domain service**: maps app verbs to score IDs, runtime `job_id`s, config paths, runtime vars,
  validation policy, and audit records.
- **UI/API**: renders domain controls and refuses unsafe transitions.

Return JSON envelopes from adapters:

```json
{ "ok": true, "connected": true }
{ "ok": false, "error": "Conductor is not running" }
```

Avoid leaking stack traces, socket paths, or raw score text to end users unless
the app is explicitly an operator console.
