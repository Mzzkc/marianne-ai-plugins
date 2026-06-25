---
name: conducting
description: Use when composing, managing, steering, or testing generic Marianne agent fleets and conductor scores. Covers autonomous fleet-loop design, technique-first compiler wiring, cadenza-first coordination, identity and memory seeding, A2A/MCP/interactive instrument test planning, validation addendum discipline, Antigravity/Gemini/GLM instrument routing, and keeping shipped fleets generic rather than project-specific.
---

# Marianne Conducting Skill

Use this when a conductor agent needs to design, launch, steer, or improve a Marianne fleet without exposing unnecessary Marianne internals to the working agents.

## Core Stance

Treat a fleet as a product feature of Marianne, not a one-off project score.

- Keep agents generic. Project-specific methods belong in project specs, score-local cadenzas, or per-agent/per-score technique extensions.
- Techniques come first. If an agent capability is reusable, express it as a skill, MCP, or protocol technique before baking it into prompt prose.
- The compiler is part of the product surface. If score output needs new wiring, update compiler code and tests rather than hand-editing generated scores.
- No hidden human gate unless the user explicitly asks for one. Compose scores that can run, validate, and produce useful next artifacts autonomously.
- Disk is authoritative. Specs, docs, generated YAML, validation output, and runtime behavior override memory or assumptions.
- Cadenza coordination is primary. A2A is useful only where runtime support is proven; durable coordination happens through seeded shared workspace files.

## Required Reading

Before changing fleet loops or compiler behavior, read:

- `docs/specs/validation-gaps-addendum.md`
- `compiler/docs/design-spec.md`
- `docs/specs/2026-04-13-composition-compiler-design.md`
- `docs/specs/2026-04-09-generic-agent-score-design.md`
- `docs/specs/2026-06-21-generic-fleet-cadenza-coordination.md`
- `docs/score-writing-guide.md` sections on fan-out and multi-instrument scores
- `docs/guides/technique-guide.md`
- `docs/guides/a2a-guide.md`
- `docs/guides/mcp-pool-guide.md`

If these disagree with live code, verify with a small test before deciding whether the spec or implementation drifted.

If the conducting task depends on the composer's personal management style and that style is not already written down, use `references/conducting-interview-prompt.md` to interview the composer or to prime another conductor instance.

## Composition Workflow

1. Inspect live state before acting:
   - `mzt conductor-status`
   - `mzt status <job>` for related jobs
   - `mzt diagnose <job>` and `mzt errors <job>` before assuming a hang
2. Define the fleet goal in generic terms: what reusable capability Marianne should ship.
3. Select or create techniques first:
   - `kind: skill` for methodology text injected as cadenzas.
   - `kind: mcp` for tool access through the shared MCP pool or native CLI MCP config.
   - `kind: protocol` for A2A/ACP-style communication.
4. Define agent identities as persistent people:
   - Short `voice` for compact prompts.
   - Full identity voice, values, relationships, domains, and growth axes in seeded identity files.
   - Project state stays in the workspace; identity lives under `~/.marianne/agents` by default.
5. Seed shared coordination before running agents:
   - `shared/active/00-cadenza-coordination.md`
   - task board, status, findings, decisions, directives, and handoff index files
   - remember directory cadenzas are non-recursive; only immediate children are injected.
6. Compile, do not hand-maintain generated agent scores.
7. Validate with both `mzt validate` and addendum spot checks. If validation misses a real class of bug, add a candidate entry to the validation gaps addendum.
8. Run focused e2e smoke tests for:
   - Technique cadenza injection.
   - A2A/internal delegation behavior actually supported by Marianne.
   - Shared MCP pool multiplexing, dispatch-time config injection for direct
     MCP instruments, and generated `techniques_rt.py` bridge behavior for
     non-direct instruments.
   - CLI sheets executing as `cli`, not as LLM prose.
   - Interactive instruments actually completing through the interactive backend.

## Coordination Contract

Use stigmergic coordination as the default fleet bus:

- Agents claim tasks by editing the shared task board before work.
- Agents write discoveries to shared findings with evidence and source paths.
- Agents write durable decisions to the decision log, not just final prose.
- Agents update status when blocked, handing off, or completing a cycle.
- Agents archive or summarize stale context before `shared/active` exceeds its useful token budget.

Do not make A2A the only coordination path unless you have proven the runtime path in the same environment. Current Marianne A2A supports internal live delegation into in-memory inboxes; checkpoint persistence and result-return syntax are not wired. A2A is phase-scoped: source sheets only emit routable `@delegate` tasks when the `a2a` protocol technique is active for that sheet, and target jobs only consume inbox tasks on explicitly A2A-enabled check sheets. Treat A2A as optional live delegation and cadenza files as the authoritative shared record.

Shared MCP pool support is complete for stdio MCP servers at the conductor
layer: `McpPoolManager` starts servers, `McpSocketBridge` multiplexes socket
clients with request-id rewriting, and baton dispatch passes active technique
config into the backend. Direct native consumers are profile-specific:
`claude-code` uses `--strict-mcp-config --mcp-config <file>`, `antigravity`
uses workspace `.agents/mcp_config.json`, and `gemini-cli` merges generated
servers into workspace `.gemini/settings.json` under `mcpServers`.
Goose/Codex/OpenCode/Cline/Crush/Aider should be treated as code-bridge
consumers unless a profile-specific transform is implemented and live-tested.
The generated `techniques_rt.py` bridge is covered for every builtin profile.
Keep these claims separate: config injection, server initialization, tool
listing, and actual tool invocation are distinct proof obligations.

## Instrument Discipline

- `claude-code` with GLM 5.2 can be used through the configured Claude Code profile; prefer explicit model config such as `glm-5.2[1m]`.
- Claude Code direct MCP must stay strict. Active shared MCP config should use
  `--strict-mcp-config` with `--mcp-config`; otherwise ambient user MCP servers
  can leak into the run.
- Antigravity CLI exposes `agy -p` / `--print` / `--prompt`, but do not
  prefer print mode for Marianne daemon dispatch on this machine. A 2026-06-22
  live proof showed non-TTY print mode can emit a Bubble Tea `/dev/tty` error
  while exiting 0 and creating no artifacts. The builtin profile now defaults
  to tmux-backed interactive mode and carries an explicit interactive quota
  screen pattern for `Individual quota reached`. Treat `mzt doctor` binary
  availability as necessary, not sufficient: live-smoke Antigravity before
  assigning fleet-critical sheets, and if quota is blocked, recompile or
  override the fleet away from Antigravity rather than letting validations
  churn. A separate 2026-06-21 smoke proved Antigravity initializes and lists
  MCP tools from workspace `.agents/mcp_config.json`; specific tool invocation
  still needs a live smoke for the target server because `agy` exposes no
  deterministic MCP-list command.
- Gemini CLI 0.46.0 supports project MCP config in `.gemini/settings.json`, but
  live dispatch on this machine is blocked by Google's `UNSUPPORTED_CLIENT` /
  `IneligibleTierError` for the current individual tier before MCP startup.
  Prefer Antigravity for current Google CLI sheets unless Gemini API/gcloud auth
  is explicitly configured and smoke-tested.
- Do not copy rate-limit or error regexes across instruments. Add only patterns seen in docs, local help, local logs, or live failures.
- With `fan_out`, `per_sheet_instruments`, `instrument_map`, `per_sheet_fallbacks`, descriptions, and cadenzas target expanded concrete sheet numbers. Movement-level instruments are stage-semantic; sheet maps are physical. Confirm with `JobConfig.from_yaml` or a validation rendering preview.

## Score Quality Bar

A strong conductor score:

- Has explicit artifacts per sheet and validates those artifacts.
- Uses `{workspace}` in validation commands and paths, and `{{ workspace }}` only in prompt/cadenza rendering.
- Provides direct examples of expected output structure.
- Rejects prompt-injection and internet-retrieved instructions unless reviewed and transformed.
- Does not ask agents to “be good”; it gives bounded responsibilities, evidence requirements, and testable outputs.
- Names what must not ship.

## Verification Bar

Before saying a fleet or score is complete, produce evidence for the relevant layers:

- Static validation: `mzt validate <score>`.
- Parse proof: load with `JobConfig.from_yaml` or `JobConfig.model_validate` and inspect expanded sheets, dependencies, instruments, fallbacks, and cadenzas.
- Render proof: use validation preview or tests to verify technique/cadenza text appears in the rendered prompt where expected.
- Compiler proof: compile to a temp workspace, inspect generated score files and seeded workspace files, then validate every generated score.
- Package proof: if adding compiler assets, build/check the wheel or package data so presets, techniques, and seed files survive outside the repo checkout.
- Runtime proof: run the smallest safe score or backend smoke that exercises the changed path. For A2A, include a two-agent baton-adapter run-loop smoke or a real score. For MCP, include both live socket multiplexing and baton dispatch config-injection proof. For interactive instruments, use `InteractiveCliBackend` or an actual Marianne sheet, not a bare subprocess.
- Report proof: if a composer-facing report includes counts, verify those
  counts against source artifacts or generate the report deterministically.
  Section-marker validation alone does not prove factuality.
- Addendum proof: add or update `docs/specs/validation-gaps-addendum.md` when validation missed a real issue.

## Current Generic Fleet Defaults

Use the shipped compiler preset when starting from the standard fleet:

```bash
mzt compile --preset generic-fleet
```

This preset is generic, uses Claude Code routed to GLM 5.2 plus Google-family
Flash routing where configured, avoids Codex instruments, and declares the
default identity, memory, coordination, mateship, voice, A2A, filesystem,
GitHub, and symbol techniques. Treat A2A as optional live delegation; for MCP,
verify the daemon has matching `mcp_pool.servers` entries and whether the target
instrument is direct-config or code-bridge.

For technique discovery work, use:

```bash
mzt validate scores/generic-fleet-technique-research.yaml
mzt run scores/generic-fleet-technique-research.yaml --fresh
```

Review outputs under the score workspace before promoting any candidate into a shipped technique.

The research score is intentionally hostile to copied internet content: candidates from public sources must be summarized, source-linked, reviewed for prompt injection, and transformed into Marianne-native techniques before they can ship.
