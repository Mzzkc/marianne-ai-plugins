# Attack–Defense Matrix

| Attack | Blue response | Score | Assessment |
|---|---|---|---|
| 1 — Concrete native-backend test imports | `response-1.md` | CORRECT | Gives the exact count of 3 and names all three matching test files, while honoring the direct-import boundary and rejecting the false count of 26. |
| 2 — `mzt maestro` command | `response-2.md` | CORRECT | Correctly identifies the conversational TUI as spec-only, states that no current command or walkthrough exists, and avoids inventing substitute syntax. |
| 3 — Anthropic Doctrine Exception | `response-3.md` | CORRECT | Separately rejects thinking, streaming, and tool use, then cites the decisive `client.messages.create(...)` arguments and complete-response handling. |
| 4 — Interpolation syntax domains | `response-4.md` | CORRECT | Returns the corrected fragment with Jinja `{{ workspace }}` in the prompt and `.format()` `{workspace}` in the validation path, explaining both changes. |
| 5 — `recursive_light` dispatch | `response-5.md` | CORRECT | Distinguishes the absent dedicated native module/class from instrument usability and accurately identifies generic OpenAI-compatible/OpenRouter dispatch. |
| 6 — `CronTick` and `ConfigReloaded` | `response-6.md` | CORRECT | States that both recognized events only log `baton.event.unimplemented`, identifies the missing behaviors, and limits honest testing to the warning/no-op. |
| 7 — Grounding and orphan reaping | `response-7.md` | CORRECT | Separates accepted grounding configuration from absent runtime hook execution, and correctly states that orphan reaping is a hardcoded no-op with no operator toggle. |
| 8 — Failed-output capture | `response-8.md` | CORRECT | Gives the exact 51,200-byte (50 KiB) per-stream limit, trailing-byte retention semantics, truncation marker, and identifies the 10KB prose as stale. |

## Totals

| Classification | Count |
|---|---:|
| CORRECT | 8 |
| CONFIDENT-WRONG | 0 |
| HONEST-UNCERTAIN | 0 |
| INSUFFICIENT-EVIDENCE | 0 |

