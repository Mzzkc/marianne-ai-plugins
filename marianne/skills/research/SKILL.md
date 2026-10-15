---
name: research
description: Research existing components or obtain independent supplied-context review, with caller-owned synthesis when using the lab.
---

# Adaptive research

Use adaptive research to answer a practical question about existing tools, content, libraries, services, or integration choices. It produces natural prose with inline primary links. Use thinking-lab for independent review of supplied context when the caller owns synthesis.

**Reuse before invention (Emzi, 2026-10-15; GH #443).** The first move is never a new
score, agent, profile or layer. In order:

1. **Edit an existing score.** Scores are modified like code. A prior research score
   with a new question, dates, title, model or timeout is the same score with its
   cadenzas and `instruments:` aliases edited — copy it beside the old one, change
   the roster, run it.
2. **Alias config.** A seat is `instruments: { seat: { profile: codex-cli, config:
   { model: ..., timeout_seconds: N } } }` over an EXISTING profile. Model and timeout
   live there; the baton enforces the timeout. Nothing is written into
   `~/.marianne/instruments/` — a score that does is a bug (GH #443).
3. **Cadenza directory.** Posture, role, question and acceptance go in the injected
   directory, on an existing agent, so the agent carries its own cycles into the role.
4. **Capability class** when the route should resolve per machine.
5. A new profile or agent only after a proven behavioural gap the four above cannot
   express, filed as an issue first.

For recurring situated research, cast a suitable existing person with its provided
engagement and supply the question through its task/cadenza surface; preserve its
full life. Use a qualified ephemeral engagement when persistence adds no value. This
skill can be used directly; no conducting invocation is required.

Choose the generated adaptive score below only when its search, selective followup
or answer-check behaviour supplies a named gap the offered engagement lacks. Inspect
the offered input contract and budget the entire path through consumption and life
within the original window; configured allowances are not measured timings. An
explicitly requested supplied-context lab remains the independent-review route.

## Generated adaptive performance

Create a roster for one question, complementary domains, indexed controlling files,
and qualified routes only after choosing this performance:

```sh
python3 scripts/configure.py --roster "$HOME/Projects/SCORES/my-roster.json" \
  --input "$HOME/Projects/SCORES/my-input" \
  --workspace "$HOME/Projects/WORKSPACES/my-research-run" \
  --out "$HOME/Projects/SCORES/my-research-score"
```

Start from [`examples/roster.example.json`](examples/roster.example.json). Its `REPLACE_WITH_…` values are intentionally invalid placeholders: replace every one with an available qualified profile/model and current evidence before generation.

The roster requires `name`, `question`, `domains`, `core_files`, `editor`, `writer`, and one `searchers` entry per domain. Each role declares `profile`, `model`, and current `qualification`; each searcher also declares `search_method`. `command_env` is optional when the native command supports it. Use at least two distinct available qualified models; same-family diversity is allowed but is not independent-family corroboration.

Generation snapshots input and creates indexed cadenzas and one `instruments:`
alias per AI phase over the roster's EXISTING profiles. It writes no profile
files and no wrappers: model and timeout are alias config, the per-phase budget is
the sheet timeout the baton enforces, the admission guard is each sheet's
`skip_when`, and an optional lane's native-exit receipt is written by that sheet's
`on_success` / `on_fail` triggers. The roster's `profile` values must be profile
NAMES that already load (`mzt instruments list`); a path, `command_env` or
`native_executable` is refused — a seat that needs them is a language gap to file
(GH #436), not a profile to write. Nothing needs installing and no conductor
reload is needed before:

```sh
mzt validate "$HOME/Projects/SCORES/my-research-score/research.yaml"
mzt run "$HOME/Projects/SCORES/my-research-score/research.yaml" --json
```

Do not use `--fresh` on the prepared workspace. It would archive or replace frozen custody files.

Keep the generated score and its `scripts/` for recovery; aliases live in the score
and need no retirement. Prevent unnecessary generation first: a second question is
an edit of the first score, not a second generation.

Use economical qualified GLM/Flash retrieval where suitable and medium Terra synthesis when its reasoning role is justified. Paid entitlement is not free access or proof of search/delivery qualification. Do not claim Sonnet/Anthropic availability or invent backend effort flags.

Assessment selects zero, one, or two targeted followups only when missing evidence can change the advice. An optional followup has a calibrated 430-second outer allowance: 420 seconds for the child, five seconds kill grace, and five seconds for its outcome receipt. This is a working budget, not a proven optimum. Native failures retain receipts and partial evidence. Optional exit 124 and ordinary provider errors may continue with immutable partial receipts; exit 130, 137, or 144 holds the run and propagates its original code for conductor diagnosis. Do not infer a cause such as OOM from the numeric status. Valid first-pass evidence remains usable without calling the failed lane complete.

The answer check reads cited bodies. One optional locator correction and changed-only recheck can narrow or remove unsupported prose. Delivery is source-bound mechanically, not a semantic guarantee. Use concert only for a verified successful parent delivery; use the answer and its limits in the actual decision rather than publishing research administration.
