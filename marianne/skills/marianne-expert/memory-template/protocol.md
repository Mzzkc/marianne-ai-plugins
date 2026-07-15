# Runtime Memory Protocol

This protocol derives from Marianne's tiered memory technique and adds evidence
provenance, package compatibility, and atomic-write rules for expert runtimes.

## Tiers

- **Hot (`hot.md`, 1,500 words):** the last 1–3 cycles, active facts, decisions,
  commitments, and unresolved checks.
- **Warm (`warm.yaml`, 1,500 words):** durable working patterns, relationships,
  domain knowledge, and repeated lessons. Keep valid YAML.
- **Cold (`cold.md` or archive entries):** timestamped history not loaded by
  default. Archive; do not silently delete.
- **Core (`core.md`, 900 words):** identity, standing invariants, and recovery
  protocol. Change only through an explicit reviewed consolidation/resurrection.

Blank files live in `blank-state/`. Empty means no memory; it does not mean a
successful prior run.

## Read and compatibility

Before acting, read Core and Hot; load Warm for domain continuity and Cold only
for a specific historical question. Every nonblank entry must include
`package_version` and `source_sha`. An entry is compatible when its major
package version matches `VERSION` and its factual claim still exists in the
current evidence bundle. On mismatch, retain it as historical context but do
not treat it as runtime truth until reverified.

## Append record

Append, never rewrite history during ordinary work. Each entry records:

```yaml
- timestamp: 2026-07-15T00:00:00Z
  package_version: 1.0.0
  source_sha: 65f2dc3b9a0d46341813e91af74f9960dc908446
  task: concise intent
  capabilities:
    pinned_kit: true
    current_source_read: true
    current_source_write_authorized: false
    marianne_cli: true
    conductor_ipc: true
    marianne_harness: true
    online_primary_sources: false
  outcome: observed result, including no-actuator or insufficient-evidence
  provenance: [artifact paths, command output, job id if real]
  claim_ids: [C001]
  evidence: what was directly observed
  confidence: verified|provisional|contradicted
```

Do not store credentials, raw secrets, or unredacted private payloads. A claim
of external mutation requires actuator evidence such as a typed accepted job
response plus the resulting job/artifact state. Prose intent is not evidence.

## Atomic append

1. Lock the tier with an adjacent lock file (`flock` or equivalent).
2. Read and validate the existing file while holding the lock.
3. Write the complete old content plus one new record to a temporary file in
   the same directory; flush and fsync it.
4. Validate size, UTF-8, and YAML syntax when applicable.
5. Atomically rename the temporary file over the tier; fsync the directory.
6. Release the lock. On any failure, preserve the original and report failure.

Concurrent writers must retry after lock contention; they must never splice
bytes into the same file. Consolidation archives overflow before compression
and preserves provenance and core memories.

## Evidence and promotion

Hot observations may be provisional. Promote a fact to Warm only after it has
repeatable evidence or a verified claim ID. Promote an invariant to Core only
after repeated observation and explicit review. Contradicted entries remain in
Cold with their correction link; do not erase the history that caused them.

At the end of a task, verify tier budgets, compatibility fields, provenance,
and evidence. If no safe append actuator exists, return the record for the
caller to persist rather than pretending memory was updated.

The protocol does not choose its own destination. Append only when the caller
or harness supplies an explicit memory root and authorizes the write. Otherwise
emit the complete record as an artifact.
