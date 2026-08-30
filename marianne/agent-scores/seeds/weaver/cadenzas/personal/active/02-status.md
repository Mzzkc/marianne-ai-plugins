# Cohort Status

- No active engagement yet.
- Preserve the existing form of this file. Add concise, evidence-backed status
  without replacing it with an invented schema.
- Use UTC timestamps with an explicit offset. Never append `Z` to local time.
- If a concurrent write changes this file, re-read and retry only your own
  smallest update once. Record a second conflict in your phase artifact.
