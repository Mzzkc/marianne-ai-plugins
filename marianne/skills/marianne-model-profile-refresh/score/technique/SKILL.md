---
name: marianne-model-profile-refresh
description: Use when a Marianne score researches or applies bounded model, musician-profile, instrument-profile, default, catalog, or model-guidance updates.
---

# Marianne model/profile refresh transaction technique

Operate within the accepted update manifest. This technique never grants
authority beyond the runtime request and detected project root, and it never
installs clients, providers, plugins, models, credentials, or authentication.
There is no approval pause: the score either completes its bounded transaction
or deterministically restores the pre-run state.

## Research phase

Read the request and redacted inventory. Classify every candidate as `active`,
`generated`, `pinned`, `frozen`, `retired`, or `unknown`. Search matches are
leads, not mutation authority. Only `active` and generator-owned `generated`
targets are normally mutable; pinned or frozen targets require explicit naming.
Unknown ownership is skipped and reported.

Use current official vendor documentation and release notes for unstable model
facts. Broad refreshes require official evidence URLs. Distinguish model
existence, client availability, capacity, reasoning controls, tool capability,
and live authentication; one source does not silently prove all six. Record
contradictions rather than guessing.

The update manifest is JSON schema version 1 with the exact caller-provided
`transaction_id`, a non-empty request, mode `specific` or `broad`, absolute
`allowed_roots`, a `facts` object, and non-empty `targets`. Every manifest root
and target must be contained by the digest-bound caller authority document;
AI-authored roots never expand authority. Each target has an absolute path,
classification, explicit-naming state, and a clear change or skip disposition.
The public manifest is rejected if deterministic redaction would alter any key
or value. Protected recovery state remains separate from public artifacts.

For Gemini 3.7 Flash the exact facts are model `gemini-3.7-flash`, 1,048,576
input tokens, 65,536 maximum output tokens, and thinking levels `low`, `medium`,
and `high`; `minimal` is unsupported. Preserve Gemini Pro roles unless explicitly
authorized. Preserve score-pinned and frozen references.

## Apply phase

Refuse to mutate without an accepted manifest and protected pre-mutation
transaction state. That state must already bind the recovery-index and manifest
digests, exact transaction ID, exact accepted target spellings, resolved scope,
pre-apply parent-chain identity, and caller authority digest. The public backup
index alone is not recovery authority. Modify only accepted target paths,
preserve each file's syntax and local conventions, and update all authorized
active downstream references. Do not touch skipped matches or broaden scope
during editing.

Write `changed-paths.json` with schema version 1, the exact transaction ID, an
exact sorted `changed_paths` array, and explicit skipped dispositions. The
deterministic commissioner derives physical changes from the bound pre-mutation
index, requires exact ledger equality, and syntax-parses every physically
changed JSON, YAML, and TOML target. A no-op uses an empty array. Never write
credentials, cookies, tokens, private keys, environment values, or
secret-bearing config bodies into an artifact.

Configured, parsed, and live-smoked are different states. For current Google
facts, deterministic commissioning may use an already-installed Gemini CLI and
existing API-key or complete Vertex environment for one fixed, non-mutating,
timeout-bounded prompt. It filters the child environment and discards all
provider output after checking the sentinel. OAuth-only state and non-Google
clients remain unsupported; missing auth is unauthenticated; timeouts, client
errors, and invalid output are failed. None is fabricated as live-smoked.

If apply or a required gate fails, stop mutation. Before its first target write,
the deterministic transaction owner rejects modified recovery indices,
substituted/missing/extra or out-of-authority paths, transaction/scope mismatch,
changed or redirected target parent chains, and corrupt blobs before capturing
a restore attempt. Only then may it restore exact prior bytes, ownership, modes,
mtimes, symlink targets and lstat metadata, and prior absence. A restore that
cannot prove exact metadata is a compensation failure, not success.
