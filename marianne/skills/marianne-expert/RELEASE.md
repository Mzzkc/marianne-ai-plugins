# RELEASE — Marianne Expert 1.1.0

## Verdict: **PENDING_ACTING_ACCEPTANCE**

The 1.0.0 factual defense remains historical evidence, not the 1.1.0 release
gate. Version 1.1.0 is released only after the Marianne C1 acting acceptance
finishes and the evaluated package digest equals the installed package digest.

## Changes

- Replaced exclusive advise/adapter/source levels with an independent
  capability vector.
- Added explicit source-write authorization and Marianne-harness context.
- Made current worktree state and dirty-file fingerprints first-class evidence.
- Separated session access from product feature status.
- Added conditional official-source probing for current external facts.
- Made memory destination and authority explicit.
- Added relocatable exact-file release manifests and agent metadata.
- Retired the claim that the historical publisher concert is a bundled,
  self-regenerating release mechanism.

## Required release evidence

1. Plugin unit tests and skill validators pass.
2. The package manifest verifies after relocation.
3. Codex and Agents installations are byte-identical.
4. A Marianne-run expert records `marianne_harness: true`, current source state,
   explicit authority, and the candidate release sentinel.
5. The expert reconciles the raw C1 handoff against live source before edits.
6. C1 targeted tests, full suite, documentation scans, and live instrument
   checks pass after the final repair.
7. Any change after evaluation invalidates the candidate digest and triggers a
   fresh evaluation.

## Pinned evidence compatibility

The bundled evidence remains pinned to
`65f2dc3b9a0d46341813e91af74f9960dc908446`. It describes that snapshot only.
Current behavior claims cite current HEAD and dirty fingerprints instead of
being forced into historical claim IDs.

## Memory

Memory append is optional. The caller or Marianne harness must supply both an
explicit memory root and write authority. Without them, the expert emits a
provenance record as an artifact and does not pretend persistence occurred.
