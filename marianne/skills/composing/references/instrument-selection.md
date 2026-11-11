# Model-specific composition guidance

Read when selecting the named model or composing the specialized security work below.
Current venue evidence still governs availability and fit.

## Capability classes in scores

Prefer a configured class such as `strong`, `workhorse`, `fast`, `writing`,
`vision`, or `local` when the score describes a kind of work instead of a fixed
route. Marianne expands the class to an ordered profile chain before dispatch,
then appends declared fallbacks. `mzt instruments classes show --json` reports
the layers and their digests; `mzt instruments classes check` reports broken
chains and route availability. Setup can write a machine-specific user layer
with `mzt instruments classes write --if-absent`.

An alias in the score wins over a profile, and a profile wins over a class with
the same name. `cli` therefore remains a shell profile. Use an alias or named
profile for a fixed model, a reviewed `expected_route`, or a sheet that cannot
accept heterogeneous fallback profiles. Class entry settings support `model`,
`effort` and `tools`; availability is checked before authors rely on a chain, while runtime
fallback still handles a route that disappears later.

## Current Gemini 3.8 Flash guidance

The catalog's current stable Gemini Flash route is `gemini-3.8-flash`, with a
1,048,576-token input limit and a 65,536-token output limit. Use high thinking for load-bearing coding and agentic work when the task is clear, bounded, and
backed by observable proof obligations. Use medium thinking as the balanced default for general work. Use low thinking for cheap, bounded work. The model
rejects the `minimal` level, so never request `minimal` for Gemini 3.8 Flash.

Keep four evidence lanes distinct when selecting it: catalog availability
through `antigravity`, configured profile availability in the
target installation, dispatch compatibility for the selected instrument and
profile, and live verification with working authentication. Evidence in one
lane does not establish another. Do not claim comparative quality or benchmark
superiority from the catalog entry; its qualitative ratings remain provisional
pending independent evaluation.

## Current GLM specialist guidance

Do not freeze a convenient local profile alias into a score. GLM 5.3 Flash may
be selected only when current profile and live evidence prove a Z.AI route,
the exact released model ID, entitlement, limits, vision capability, and
invocation contract. `opencode-ox-alpha` may remain a historical box-local
alias; it is not a free OpenRouter route or a portable score contract. Bind
semantic phase requirements through live evidence and retain the routing
receipt. Treat free or subscription-included metering as one cost dimension,
not as evidence of low latency, quota, queue, or rate-limit risk.
When GLM 5.3 is selected for substantial work, use high or max reasoning.

For authorized defensive cybersecurity and vulnerability discovery, commission
a specialized vulnerability-discovery score. It must gate target authority and
scope before execution, keep discovery non-destructive, split the search into
explicit vulnerability classes or components, require reproducible findings
and independent severity triage, and route accepted findings through
regression-backed remediation and coordinated disclosure. Instrument selection
does not broaden the composer's authority or bypass provider guardrails.

## Right-sizing per sheet

Today a generated score tends to put one instrument on every sheet. Three
per-sheet controls exist: the model (an alias `config: {model: ...}` or
`instrument_config.model`), `instrument_config.effort`
(`minimal|low|medium|high|xhigh|max`, GH #535) and `instrument_config.tools`
(GH #534). For each sheet record the role, the model tier, the effort, the
toolset and the reason. Order of leverage: toolset, then model tier, then effort.

| Role | Model tier | Effort | Toolset |
|------|-----------|--------|---------|
| Recon, inventory | small | absent | read-only file tools; add search only if it must search |
| Build | middle | absent | what the edits and tests need, no more |
| Rubric review | middle | absent | file read and write for the report |
| Adversarial review | top | absent; `max` only with a stated reason | read plus the commands that probe the claim |
| Synthesis | middle | absent | file read and write |
| Gate, release | small | absent | file read, or the checks it runs |
| Deterministic command | none: use the `cli` instrument | not applicable | not applicable |

A tier is a capability class or a pinned model. A sheet that could be a `cli`
command should be one.

### Measured facts

- Toolset, one call per row, fixed request preamble on claude-code: no `tools`
  key 29 tools / 28,549 tokens; two tools 10,739; empty list 8,266. This is the
  fixed preamble, not a task's total cost.
- Across about 250 musician sessions the fixed prefix was 43% of context tokens
  and tool results 42%; output was 2.5%.
- Effort, three runs per arm on Claude Sonnet 5.5: `max` produced about 2.3
  times the reasoning of `high`; `low`, `medium` and `high` were
  indistinguishable. On Haiku effort had no measurable effect. On that model
  the lever is not to use `max` unless the sheet needs it; lowering below `high`
  is not a proven saving. Other harnesses' mappings exist but are unmeasured.
- Five builtin profiles declare an effort mapping: claude-code, antigravity,
  codex-cli, opencode, crush. `tools` is mapped on claude-code only.

### Guard rails

- Never narrow tools below what the sheet's validations require it to produce.
- V335 (effort) and V337 (tools) refuse a key the profile cannot deliver. In a
  mixed fallback chain put `tools` and `effort` on the entry whose profile maps
  them, and run `mzt validate`. V336 notes a seat that names no model.
- Independence rules for maker/judge pairs outrank cost.
- Right-sizing never removes a fallback.
