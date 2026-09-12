---
name: marianne-search
description: Compatibility entry for the sibling research skill's caller-bound adaptive search score.
---

# Marianne search

Use the sibling `research` skill bundle for adaptive research commands and files. Its commands are relative to that bundle, not this shim directory: `research/scripts/configure.py --roster R --input I --workspace W --out O` generates `O/research.yaml`; install only `O/profiles/*.yaml` into `~/.marianne/instruments/`, verify the PID from `mzt conductor-status` is this installation’s `mzt start`, send that verified PID `HUP`, then validate and run the score with `mzt`.

The score preserves indexed context, searches complementary domains, selects zero to two material followups, and delivers a checked natural answer with inline primary citations. Partial outcomes remain explicit. This shim replaces public A/B selection; historical comparisons stay outside the package.
