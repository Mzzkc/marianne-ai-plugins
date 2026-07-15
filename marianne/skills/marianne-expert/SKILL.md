---
name: marianne-expert
description: Use when Marianne composing, operating, debugging, architecture, source development, embedding, runtime commissioning, or current-versus-pinned evidence reconciliation is required.
---

# Marianne Expert

Release sentinel: `MARIANNE_EXPERT_RELEASE_V1_1`.

1. Run `scripts/preflight.py` before conclusions. Pass explicit source-write
   authorization and runtime context; never infer either from writable files.
2. Treat access as a capability vector: pinned kit, current source read, source
   write authorization, CLI, conductor IPC, Marianne harness, and online
   primary sources may coexist independently.
3. Read `BOOTSTRAP.md`, then use `TASK-MAP.md` to load one relevant playbook and
   only the necessary contracts/evidence.
4. Match evidence to the claim: current source/tests for current behavior; git
   and pinned material for history; official current sources for external
   facts. Report contradictions instead of averaging them.
5. Keep session access separate from product feature status. Never simulate a
   job, mutation, online check, or memory append.
6. Before edits, fingerprint dirty overlap, record compatibility authority and
   test disposition, and preserve existing work. After edits, run the
   playbook's targeted, full-suite, and live verification where available.
7. Append memory only when the caller supplies a destination and authority;
   otherwise return a provenance record for the caller to persist.
