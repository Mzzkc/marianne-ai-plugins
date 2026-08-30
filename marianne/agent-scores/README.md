# Persistent agent scores

This generated package contains Marianne's released persistent cast. Each of
the 33 agents has:

- a portable semantic seed;
- a four-file personal active cadenza seed;
- `full-lifecycle.yaml` for durable end-to-end work;
- `targeted-work.yaml` for bounded work with explicit integration debt; and
- `lifecycle-integration.yaml` for consolidation, reflection, seed-conflict
  adjudication, resurrection, and later-recall proof.

`roster.yaml` is the discovery index. Keystone is included. Runtime is not:
the local Runtime tree remains a cycle-zero seed and is not propagated until
lived development justifies it. Files named `musician-XXXX` are DJ-project
instrument profiles and are never part of this cast.

These files are generated from the compiler's `generic-fleet.yaml`; do not
edit them independently. Regenerate the complete package after changing a
canonical seed, lifecycle shape, cadenza seed, or technique contract.

Preview box-local installation before granting write authority:

```bash
marianne-agents install-package "${CLAUDE_PLUGIN_ROOT}/agent-scores" \
  --techniques-source "${CLAUDE_PLUGIN_ROOT}/techniques" \
  --dry-run
```

The authorized command without `--dry-run` reconciles seeds and installs
score templates, personal cadenzas, and runtime technique documents. It never replaces
lived L1-L4 divergence. Managed scores, cadenza templates, and techniques are
updated only when their installed bytes still match the previous package
baseline; otherwise a conflict is recorded and the local bytes remain. The
roster binds the seed version and SHA-256 of every packaged agent asset, so an
installer refuses mixed, torn, or locally altered package generations before
it writes agent data.
Custom `--agents-dir` and `--techniques-dir` values are supported: installation
rewrites the copied score paths to those resolved box roots and creates the
per-agent workspace parent without changing the portable package.

Before running a score, validate it and bind its phase requirements to current
instrument evidence. Binding replaces the deliberately non-runtime
`REQUIRES-LIVE-BINDING-*` workspace with a fresh engagement workspace. Use a
new bound-score directory for each engagement; never reuse lifecycle snapshots.
See `../docs/ref/modern-agents.md`. The shipped routes are portable fallbacks,
not claims about a box's provider, model, entitlement, quota, or latency state.
