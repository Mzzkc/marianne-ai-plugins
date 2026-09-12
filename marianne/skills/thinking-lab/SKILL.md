---
name: thinking-lab
description: Compatibility entry for the sibling research bundle's independent supplied-context review score.
---

# Thinking lab

Thinking-lab is independent supplied-context review, not a research search lane. Use the sibling `research` bundle’s lab commands and files: copy the entire `research` package under SCORES, adapt `lab/roster.json`, run `lab/scripts/configure.py --roster lab/roster.json --out scores --resources lab`, then set the generated public `scores/thinking-lab.yaml` `workspace:` to a dedicated WORKSPACES path. Validate and run that score with `mzt`, passing `--var input_dir=INPUT`.

Keeping the whole research package preserves the lab prompts, roster, scripts, snapshot, receipt, and delivery dependencies. Reviewers write separate review artifacts; the caller owns synthesis and must not treat agreement as truth.
