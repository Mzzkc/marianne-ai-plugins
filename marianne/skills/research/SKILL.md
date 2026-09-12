---
name: research
description: Research existing solutions through strategy, assigned parallel searches across distinct models, and synthesis; or request independent supplied-context reviews with caller-owned synthesis (thinking-lab).
---

# Research

Choose the mode by the question you need answered:

| Mode | Use | Native AI calls with default two seats |
|---|---|---|
| Search A | Discover and compare existing solutions: strategy → assigned parallel searches → synthesis | 4 |
| Search B | Same discovery plus one bounded fresh evidence challenge before synthesis | 5 |
| Independent review (thinking-lab) | Independent reviews of supplied code/design/context; caller synthesizes | 2 |

A is a capable baseline. B adds up to three decision-changing evidence checks.
Neither is established as superior. The paired live comparison and independent
source-truth evaluation are separate commissioning work, not a claim from tests.
Do not feed prior answers, evaluator rubrics, or another variant's outputs to performers.

The score assets are relative to this skill directory: `scores/research-a.yaml`,
`scores/research-b.yaml`, and `scores/thinking-lab.yaml`. Legacy plugin entry
`scores/prep/thinking-lab.yaml` is a symlink to the same authoritative lab score;
`scores/thinking-lab.yaml` is also supported. Existing separately operated local
scores are untouched. The old unreleased single-seat collector is retired from
public invocation; its safety controls remain in `scripts/snapshot.py` and tests.

## Prepare and configure

Supply a flat UTF-8 text directory outside the run workspace. `prompt.md` is
required and nonempty; all immediate files are delivered byte-exactly. Nested
directories, binary/NUL/invalid UTF-8 and over-bound inputs fail. The default total
bound is 262144 bytes; raise `--var max_input_bytes=...` deliberately. Textual
symlinks are dereferenced into the snapshot. Keep credentials out of shared input.
Each new request needs its own workspace and `--fresh`; never run two requests in
the same workspace. All modes use required directory cadenzas for complete
original context, plus the current run receipt, at EVERY AI stage.

`roster.json` is the authoring surface for research/review musician bindings,
model names, backend-supported config settings, role budgets and seat count.
Config transports only settings actually honored by the selected backend. Native
PluginCliBackend does not automatically turn arbitrary `variant`, `high` or
`effort` keys into command flags; storing them in config does not establish effort.
The generated `scores/roster.json`
is the frozen copy consumed by preparation. Edit the source roster and regenerate
all entries with `python3 scripts/configure.py`. Seat IDs are consecutive
`search-1`…`search-N`, with 2–8 distinct declared families/routes. Questions are
created dynamically by strategy; native seat count is fixed by generation.
Adding/removing a seat does not change research prompt logic. Never hand-edit
aliases alone: regenerate and run `scripts/check_graph.py` with source-bound
Marianne imports so runtime routing and the receipt agree.

The portable default has two complementary search seats: OpenCode
`zai-coding-plan/glm-5.3-flash` and Antigravity `gemini-3.8-flash-high`. The
complete Gemini model ID selects its high tier; do not add arbitrary effort keys
or flags. Do not add unsupported `variant` or effort configuration to the
portable OpenCode binding. Gemini Flash is also the strategist and B challenger.
`codex-cli` synthesis explicitly uses mid-sized `gpt-5.6-terra`. Use stronger
synthesis only when a concrete failed obligation justifies it; use economical,
qualified search-capable routes for retrieval. The roster remains configurable
from 2 through 8 seats.

Thinking-lab stays a distinct supplied-context independent-review mode: its
default two reviewers inherit the roster, while a caller may configure a larger
review-capable cast when the supplied design or code warrants it. Do not imply
frontier review capability from the default routes alone.

Gemini Flash high has prior real search-and-primary-fetch evidence. The OpenCode
GLM route is locally available, but availability does not establish search or
delivery qualification; its earlier 600-second timeout is historical evidence
and does not justify a blind rerun. A prior Sonnet-named route did not expose
enough metadata to establish the actual model, so its probe and comparison do
not prove distinct-family execution or Sonnet performance. Do not describe the
GLM route as ready or superior from availability alone. Each route still needs
working authentication and sufficient quota. Probe and freeze actual model,
family, search, retrieval and tool provenance before live work. Model listing or
paid subscription entitlement proves neither web access nor free service;
monetary cost is unknown. If a route fails qualification, substitute a verified
distinct family or regenerate both A/B with the same roster. Local personal
profile names belong in local run bindings, never portable defaults.

For local bindings, copy this resource bundle under your SCORES directory, edit
its roster, then regenerate there. Or use `scripts/configure.py --roster /abs/roster.json
--out /abs/SCORES/run-scores --resources /abs/research-resource-bundle` to keep
immutable shared resources and local generated YAML. The output directory receives
the frozen roster; preparation uses that file. Corresponding roles in A/B must
have identical model, effort, timeout and source-access allowances.

## Direct use and conducting

From this skill directory, with a dedicated workspace:

```bash
mzt run scores/research-a.yaml --fresh --workspace /absolute/WORKSPACES/research-a --var input_dir=/absolute/context
mzt run scores/research-b.yaml --fresh --workspace /absolute/WORKSPACES/research-b --var input_dir=/absolute/context
mzt run scores/thinking-lab.yaml --fresh --workspace /absolute/WORKSPACES/review --var input_dir=/absolute/context
```

The lab retains `~/workspaces/thinking-lab-input` as its legacy input default;
explicit per-request paths are preferred. Preserve `review-N.md` semantics and
read the individual reviews. Caller synthesis should assess evidence and unique
insights, not majority vote. A collaborative implementation round is a separate
explicitly authorized build task; research does not automatically start it.

For conductor submission, use the current command/conducting workflow, pass the
same score/workspace/input variables, retain the returned job ID, and monitor typed
terminal status plus artifacts. A submission receipt is not completion. No blind
retries, recursive gap loop or automatic package adoption. AI retry/completion
attempts and all fallback chains are empty/zero in these scores.

Role timeout defaults: strategy 300s, each search 600s, synthesis 360s, B challenge
360s. The comparison commissioning ceilings are A 1500s and B 1860s; root must
monitor/enforce these wall-clock ceilings, including queue/hook overhead. They
are not an implemented score-wide deadline or a quality promise.

Read `synthesis.json`/`synthesis.md`, individual `search-N.json`, strategy and B's
`challenge.json`. Lab emits independent `review-N.md` with current-run hash sidecars.
The final deterministic gate writes `delivery/status.json`. Full completion needs
all required seats (and B challenge) plus valid synthesis. Partial/no_web, malformed,
missing or stale reports cannot trigger successful handoff. Failed native stages
may stop the DAG before delivery; `status.json` remains partial and useful files
remain. To package such evidence explicitly, run `python3 scripts/research.py deliver
--workspace /abs/run`; exit 4 means partial, never successful research.

## Concert delivery

See [the executable wrapper example](examples/concert-delivery.md). Use existing
native `on_success` / `run_job`; there is no new chaining API. The generator writes
a score-relative downstream YAML path and a disjoint fresh child workspace. Bindings
are baked into each generated child score's `prompt.variables` and required
cadenzas; native run_job does NOT propagate arbitrary parent `--var` values.
This example fixes its downstream consumer to `codex-cli`; the research roster
does not configure that role. For local adaptation, generate a consumer through
`concert.consumer(..., profile="your-qualified-profile")` or change the generated
consumer score binding before conducting it; verify its actual route separately.
The consumer is generated only after successful delivery and validates the exact
parent run ID and source hashes before its AI stage. Detached hooks prove child
submission, not child completion; wait for the child terminal result separately.

The delivered human report includes requirement ID/text and mandatory/preference
status, plus candidate ID/name/canonical-identity legends from validated records.
Search delivery also includes the validated `strategy.json`, covered by the
delivery digest manifest; lab delivery has no strategy artifact.

The flat delivery directory contains numbered `original-NNNN.txt` byte copies,
`report.md`, `result.json`, `run-receipt.json`, and typed `status.json`. Its manifest
maps transport names to exact original filenames/digests and binds the original
snapshot directory. This prevents user filenames such as `report.md` or
`status.json` from colliding. The next consumer gets BOTH that complete exact-name
original snapshot directory and the flat delivery directory as required cadenzas,
plus the current receipt. Lane files and archives remain outside delivery.

## Verification and limits

`prompts/contracts.md` describes structured outputs; `research.py` checks coverage,
references, run identity and delivery eligibility. It does not assess semantic
relevance, source truth or actual model identity. Native graph and provider-free
PromptRenderer tests record all-stage directory-inline receipts using clearly
labeled benign fixtures. They are plumbing proof, not generated research or a
release lock. The generic release checker cannot pre-resolve run-generated inputs
and currently omits score_dir in its injection context; record its failure rather
than precreating pretend research artifacts. Root owns exact-source acceptance,
live all-stage receipts, comparative evaluation, publication and propagation.
