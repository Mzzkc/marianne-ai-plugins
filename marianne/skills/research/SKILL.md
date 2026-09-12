---
name: research
description: Research existing components or obtain independent supplied-context review, with caller-owned synthesis when using the lab.
---

# Adaptive research

Use adaptive research to answer a practical question about existing tools, content, libraries, services, or integration choices. It produces natural prose with inline primary links. Use thinking-lab for independent review of supplied context when the caller owns synthesis.

Create a roster for one question, complementary domains, indexed controlling files, and actual available routes. Generate a task-local score:

```sh
python3 scripts/configure.py --roster "$HOME/Projects/SCORES/my-roster.json" \
  --input "$HOME/Projects/SCORES/my-input" \
  --workspace "$HOME/Projects/WORKSPACES/my-research-run" \
  --out "$HOME/Projects/SCORES/my-research-score"
```

Start from [`examples/roster.example.json`](examples/roster.example.json). Its `REPLACE_WITH_…` values are intentionally invalid placeholders: replace every one with an available qualified profile/model and current evidence before generation.

The roster requires `name`, `question`, `domains`, `core_files`, `editor`, `writer`, and one `searchers` entry per domain. Each role declares `profile`, `model`, and current `qualification`; each searcher also declares `search_method`. `command_env` is optional when the native command supports it. Use at least two distinct available qualified models; same-family diversity is allowed but is not independent-family corroboration.

Generation snapshots the input and creates indexed cadenzas, task-local wrappers, and profile aliases under the output directory. Before validation or launch, install only the generated `profiles/*.yaml` aliases into `~/.marianne/instruments/`; their wrappers remain at their generated absolute SCORES paths. Unique roster-name prefixes prevent collisions. The base profiles must already be available before generation. Run `mzt conductor-status`, verify the reported PID is this installation’s `mzt start` process, then use `kill -HUP PID` to reload profiles without restarting the conductor or in-flight work. Then run:

```sh
mzt validate "$HOME/Projects/SCORES/my-research-score/research.yaml"
mzt run "$HOME/Projects/SCORES/my-research-score/research.yaml" --json
```

Do not use `--fresh` on the prepared workspace. It would archive or replace frozen custody files.

Use economical qualified GLM/Flash retrieval where suitable and medium Terra synthesis when its reasoning role is justified. Paid entitlement is not free access or proof of search/delivery qualification. Do not claim Sonnet/Anthropic availability or invent backend effort flags.

Assessment selects zero, one, or two targeted followups only when missing evidence can change the advice. An optional followup has a calibrated 430-second outer allowance: 420 seconds for the child, five seconds kill grace, and five seconds for its outcome receipt. This is a working budget, not a proven optimum. Native failures retain receipts and partial evidence. Optional exit 124 and ordinary provider errors may continue with immutable partial receipts; exit 130, 137, or 144 holds the run and propagates its original code for conductor diagnosis. Do not infer a cause such as OOM from the numeric status. Valid first-pass evidence remains usable without calling the failed lane complete.

The answer check reads cited bodies. One optional locator correction and changed-only recheck can narrow or remove unsupported prose. Delivery is source-bound mechanically, not a semantic guarantee. Use concert only for a verified successful parent delivery; use the answer and its limits in the actual decision rather than publishing research administration.
