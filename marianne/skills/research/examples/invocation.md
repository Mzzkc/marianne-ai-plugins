# Adaptive score invocation

Use dedicated paths under `SCORES` for source/configuration and `WORKSPACES` for run artifacts.

```sh
python3 scripts/configure.py --roster "$HOME/Projects/SCORES/example/roster.json" \
  --input "$HOME/Projects/SCORES/example/input" \
  --workspace "$HOME/Projects/WORKSPACES/example-research" \
  --out "$HOME/Projects/SCORES/example/generated-score"
# Install only generated-score/profiles/*.yaml into ~/.marianne/instruments/.
# Verify mzt conductor-status PID is this installation's mzt start, then: kill -HUP PID
mzt validate "$HOME/Projects/SCORES/example/generated-score/research.yaml"
mzt run "$HOME/Projects/SCORES/example/generated-score/research.yaml" --json
```

Do not add `--fresh`: generation already prepared the workspace. Followups receive 430 seconds outside the wrapper: 420 child seconds, five kill-grace seconds, and five receipt seconds. A timeout preserves its receipt and retained bodies; it does not fabricate a completed finding.

Exit 124 or ordinary provider errors in an optional lane may retain immutable partial receipts and continue. Exit 130, 137, or 144 holds the score and preserves the original code for conductor diagnosis; do not guess its cause.
