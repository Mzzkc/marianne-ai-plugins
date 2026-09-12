# Caller-bound adaptive research

This package supplies one adaptive score. Earlier public A/B resources are migration history and are archived outside the shipped package.

## Generate and run

Start with [`examples/roster.example.json`](examples/roster.example.json). Every `REPLACE_WITH_…` value is deliberately unusable until replaced with an available qualified profile, model, and current evidence.


Use a roster with `name`, `question`, `domains`, `core_files`, `editor`, `writer`, and one qualified searcher per domain. A role has `profile`, `model`, and `qualification`; a searcher adds `search_method` and may add supported `command_env`.

```sh
python3 scripts/configure.py --roster "$HOME/Projects/SCORES/my-roster.json" \
  --input "$HOME/Projects/SCORES/my-input" \
  --workspace "$HOME/Projects/WORKSPACES/my-research-run" \
  --out "$HOME/Projects/SCORES/my-research-score"
# Install only generated profiles/*.yaml into ~/.marianne/instruments/.
# Verify the PID from mzt conductor-status is this installation's mzt start, then: kill -HUP PID
mzt validate "$HOME/Projects/SCORES/my-research-score/research.yaml"
mzt run "$HOME/Projects/SCORES/my-research-score/research.yaml" --json
```

The generated score owns the prepared WORKSPACES directory. Do not run it with `--fresh`. It has frame, parallel search, assessment, zero to two targeted followups, synthesis, whole-answer check, optional one correction/recheck, and delivery. The selected `core_files` are injected in full at every AI stage alongside the complete-original index and receipt; every other original remains addressable in the hash-bound snapshot. A partial optional lane preserves receipts and bodies but is never called complete. Optional exit 124 and ordinary provider errors may continue with immutable partial receipts. Exit 130, 137, or 144 sets held status and propagates the original code for conductor diagnosis; do not infer OOM or another cause from that status alone.

## Concert

Generate the concert wrapper **before** starting its parent research score:

```sh
python3 scripts/concert.py wrapper \
  --score "$HOME/Projects/SCORES/my-research-score/research.yaml" \
  --child "$HOME/Projects/WORKSPACES/my-research-consumer" \
  --profile available-consumer --model model-id \
  --task 'Use the research answer for the stated decision' --seconds 300
mzt validate "$HOME/Projects/SCORES/my-research-score/research-concert.yaml"
mzt run "$HOME/Projects/SCORES/my-research-score/research-concert.yaml" --json
```

The wrapper binds the parent before its child is submitted on parent success. Wait for the child job to reach its terminal state before consuming `consumer.md`. For an already completed parent, do not replay it: use `concert.py bind --parent P --child C --out O --profile PROFILE --model MODEL --task TEXT --seconds N`, then validate and run the generated `O/consumer.yaml`.

## Independent lab

Copy the **entire research package** beneath SCORES, not only `lab/`. Adapt the copied `lab/roster.json`, then regenerate the public lab score and set its `workspace:` to a dedicated WORKSPACES directory:

```sh
python3 lab/scripts/configure.py --roster lab/roster.json --out scores --resources lab
mzt validate "$HOME/Projects/SCORES/my-research-package/scores/thinking-lab.yaml"
mzt run "$HOME/Projects/SCORES/my-research-package/scores/thinking-lab.yaml" --json \
  --var input_dir="$HOME/Projects/SCORES/my-lab-input"
```

The public score is `scores/thinking-lab.yaml`. Keeping the whole package preserves its lab prompts, roster, scripts, snapshot, receipt, and delivery dependencies. Lab reviewers are independent supplied-context reviewers, not research lanes; the caller owns synthesis.
