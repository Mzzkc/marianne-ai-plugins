# Instrument Catalog — CHANGELOG

Append-only log of changes to `instrument-catalog.yaml`.

---

## 2026-08-15 — GLM 5.3 one-million-context rollout

**Drove by:** live OpenCode model-registry evidence and composer operational
calibration. `zai-coding-plan/glm-5.3` reports a 1,000,000-token context limit,
131,072-token output limit, reasoning support, and tool-call support.

### Changes

- Added `glm-5.3` as the current GLM entry, with separate provenance for live
  capacity facts and composer-supplied capability calibration.
- Recorded Fable 5-level performance only for well-bounded, clearly specified
  tasks at high/max reasoning with observable proof obligations, attributed to
  post-training rather than inherited benchmarks.
- Added authorized defensive cybersecurity and vulnerability discovery as a
  specialist use, gated by explicit scope, non-destructive reproduction,
  independent triage, regression-backed remediation, and coordinated
  disclosure.
- Repointed every current GLM 5.2 use-case selection to GLM 5.3. GLM 5.2
  remains in the musician history and this append-only changelog.
- Kept volatile model names out of conducting doctrine; conducting now carries
  a provider-neutral rule for commissioning an authorized task to a configured
  specialist without treating delegation as a guardrail bypass.

### Honesty boundary

No GLM 5.3 public benchmark, license, parameter count, architecture, or
open-weight status is claimed. The Fable comparison and security suitability
are composer operational calibration, not a cross-rating pass.

## 2026-07-16 — GPT-5.6 folded into Codex (clean break)

**Drove by:** correction of the instrument/musician boundary. The earlier
standalone `gpt-5.6` profile duplicated the Codex executable contract and
incorrectly treated a model family as an instrument.

### Changes
- **Rejected** the standalone `gpt-5.6` instrument. No alias, shim, or
  deprecation period remains.
- **Added** GPT-5.6 Sol, Terra, Luna, and their `[1m]` variants to
  `codex-cli.runs_models`.
- **Added** factual Sol/Terra/Luna musician entries using the source set
  verified 2026-07-15: vendor documentation, `codex doctor`, and the local
  Codex model cache.
- **Left Codex's default model unset.** Marianne passes no model flag unless a
  score explicitly supplies `instrument_config.model`.
- **Marked** GPT-5.5 as superseded for new Codex work and repointed current
  recommendation chains to GPT-5.6.

### Honesty boundary
- Model identifiers, context windows, output limits, prices, and Codex
  capabilities are verified.
- Comparative catalog ratings remain empty pending a future thinking-lab
  cross-rating pass; this correction does not fabricate ratings.

---

## 2026-06-14 — GLM 5.1 → 5.2 interim repoint (provisional)

**Drove by:** the live opencode instrument moved from `zai-coding-plan/glm-5.1` to `zai-coding-plan/glm-5.2` (Z.AI Coding Plan). Composers following the catalog's chains must be guided to the current model.

**Honesty caveat — this is a MANUAL interim edit, not a lab fact-fold.** GLM 5.2 is a *different release* from 5.1. Only existence + Z.AI Coding Plan availability were verified (by direct session use). All ratings, benchmarks, license, architecture, and context-window figures are **null/pending** — do NOT cite 5.1's verified numbers (e.g., SWE-Bench Pro 58.4, MIT license) for 5.2. A lab fact-fold pass (`scores/instrument-catalog-build-fold.yaml`) is needed to populate them.

### Changes
- **Added** `glm-5.2` model entry — PROVISIONAL. `verified_via: [user_session_observation_2026_06_14]`. `ratings: {}`, `benchmarks: {}`, `license: null`. Tags conservative (`heavy, subscription`) — `open-weights`/`oss-default` NOT claimed pending license verification. Chunking quirk carried over **defensively**, labelled "inherited from 5.1, unverified for 5.2."
- **Repointed** all `use_case_chains` picks from `glm-5.1` → `glm-5.2`: `code_generation` (last_resort), `code_translation` (last_resort), `reasoning_verification` (fallback), `careful_long_running_analysis` (primary), `cross_vendor_review` (3 typical_pairs), `open_default_general` (primary).
- **Neutralized** chain comments/rationales that asserted 5.1-specific verified facts (MIT license, SWE-Bench Pro 58.4). The careful_long_running_analysis rationale now attributes the "trusted over Gemini" testimony to the GLM family/lineage and marks 5.2 placement provisional.
- **Retained** `glm-5.1` entry unchanged as the documented prior release; updated only its `notes` to record the succession.
- **Updated** `generated_at` → 2026-06-14; appended the interim-edit provenance to `generated_by`.

### Items deferred
- glm-5.2 ratings, benchmarks, license, architecture, context window → next lab fact-fold pass.
- Whether the chunking-tool-call quirk persists in 5.2 → re-test in the next thinking-lab run (chunking guidance is now baked in, so the sheet should complete this time).

---

## 2026-04-30 — Move to plugins/marianne/docs/ref/

**Drove by:** plugin-distribution coherence — the composing skill's preflight reads the catalog, the skill ships in `plugins/marianne/`, and the catalog should travel with it.

**Moved files:**
- `scores/rosetta-corpus/instrument-catalog.yaml` → `plugins/marianne/docs/ref/instrument-catalog.yaml`
- `scores/rosetta-corpus/instrument-catalog.md`   → `plugins/marianne/docs/ref/instrument-catalog.md`
- `scores/rosetta-corpus/CHANGELOG-instrument-catalog.md` → `plugins/marianne/docs/ref/CHANGELOG-instrument-catalog.md`

**Updated path references:**
- 4 catalog scores: `scores/instrument-catalog-{build,build-fold,refresh,refresh-fold}.yaml`
- Composing skill: `plugins/marianne/skills/composing/SKILL.md` Tier 2.5 preflight + Select Instruments section
- Refresh-fold tag-lint: now includes `deprecated` and `sunset` in the accepted-extras set
- Self-reference: catalog YAML now has top-level `location:` field

**Why not also move instrument profiles** (`src/marianne/instruments/builtins/`): those are Pydantic-loaded code-level configuration consumed at runtime by `InstrumentProfileLoader` / `InstrumentRegistry`. They have a separate override mechanism (`~/.marianne/instruments/`, `.marianne/instruments/`). Catalog is reference data; profiles are runtime config.

---

## 2026-04-29 — Fact-fold (v1 → v1.1)

**Drove by:** version-research agent + gap-research agent + 3-of-5 thinking-lab cross-rating reviews (Opus 4.7, Gemini 3.1 Pro, GPT-5.5) + user direct testimony on GLM 5.1.

**Lab results:** 3 reviews returned (Opus, Gemini Pro, GPT-5.5). Gemma 4 sheet timed out; GLM 5.1 sheet failed permanently due to too-large tool-call issue (a known GLM quirk now documented as `quirks:` on every GLM entry plus a saved feedback memory). Lab pass for Gemma + GLM ratings is deferred to next refresh once chunking guidance is wired into the prompt.

### Existing entries — corrections

| Entry | Change |
|---|---|
| `claude-opus-4-7` | context_window 200000 → **1000000** (released 2026-04-16). Adaptive thinking is now the only thinking-on mode. |
| `claude-sonnet-4-6` | Added `context_window_beta: 1000000` (1M context in beta as of 2026-04-29). |
| `gpt-5` | Marked `status: deprecated`, `deprecated_date: 2026-02-13` — retired from ChatGPT. |
| `o4-mini` | Marked `status: deprecated` — fully deprecated as of 2026-04-29. |
| `imagen-3` | Marked `status: sunset`, `migrate_by: 2026-06-30`. |
| `gemini-2.5-pro` | Added `status: deprecating` with dates: 2026-06-17 (API), 2026-10-16 (Vertex). |
| `deepseek-v3` | Added `status: deprecating`, `endpoint_retires: 2026-07-24T15:59:00Z`. Successor: `deepseek-v4-pro`. |
| `openrouter/minimax/minimax-m2.5:free` | Added `supersession_pending: minimax-m2.7`. |
| `zai-coding-plan/glm-5-turbo`, `zai-coding-plan/glm-4.7-flash`, `openrouter/z-ai/glm-4.5-air:free` | Added `quirks:` field with chunked-tool-call guidance. Added `user_direct_testimony` to `verified_via`. |

### New entries (47 added)

**Frontier (max tier):**
- `glm-5.1` — **MIT-licensed, frontier-class, SWE-Bench Pro 58.4 (beats GPT-5.4, Opus 4.6, Gemini 3.1 Pro)**. Per user direct testimony, trusted over Gemini for careful long-running analysis. Catalog primary for the new `careful_long_running_analysis` chain.
- `glm-5` (Z.AI hosted flagship), `glm-5v-turbo` (vision variant).
- `qwen3-coder-480b-a35b-instruct` (Apache-2.0, 256K context, free OR — new primary in code chains).
- `qwen3-235b-a22b` (Apache-2.0 general flagship).

**Open-weight LLMs:**
- `qwen3.6-27b` (released 2026-04-22, dense, 262K → 1M YaRN, Apache-2.0).
- `qwen3.6-35b-a3b` (released 2026-04-16, MoE, 3B active, Apache-2.0).
- `qwen3-32b` (Apache-2.0, single-GPU friendly).
- `qwq-32b` (Apache-2.0 reasoning).
- `deepseek-v4-pro` / `deepseek-v4-flash` (preview, 1M context, replaces V3).
- `mistral-small-4` (released 2026-03-16, Apache-2.0, 119B/6B-active, multimodal — merges Magistral+Pixtral+Devstral).
- `mistral-nemo-12b` (Apache-2.0, 128K context, local generalist).
- `mistral-large-2` (Mistral hosted flagship).
- `phi-4-reasoning` (MIT, 14B, 75.3% AIME 2024 — separate from `phi-4:14b` base).
- `phi-4-multimodal` (MIT, 5.6B unified speech+vision+text).

**Embeddings & reranking:**
- `cohere-embed-v4` (multimodal embeddings, 128K context).
- `jina-embeddings-v3`, `jina-reranker-v2-base-multilingual` (Apache-2.0).
- `mixedbread-ai/mxbai-embed-large-v1` (Apache-2.0).
- `stella-en-1.5b-v5` (MIT, top of MTEB).
- `nomic-embed-vision-v1.5` (multimodal, Apache-2.0).

**Speech (audio-in):**
- `nvidia-canary-1b` (CC-BY-NC-4.0, multilingual ASR + translation).
- `nvidia-parakeet-tdt-0.6b-v2` (CC-BY-4.0, streaming-capable).
- `facebook/seamless-m4t-v2-large` (CC-BY-NC-4.0, speech-to-speech translation).

**Speech (speech-out):**
- `f5-tts` (MIT, voice cloning).
- `xtts-v2` (Coqui Public Model License, 17 languages).
- `bark` (MIT, generative audio + speech + sound effects).
- `sesame-csm` (Apache-2.0, conversational, 24kHz, in HF Transformers — released March 2025, not 2026 as some sources claimed).
- `openvoice-v2` (MIT, voice cloning, 9 native + zero-shot).

**Image/video:**
- `wan2.1-t2v-14b` (Apache-2.0 video).
- `mochi-1` (Apache-2.0 video).
- `cogvideox-5b` (custom CogVideoX license, 720x480, 8fps, 49 frames).
- `pixart-sigma` (CreativeML OpenRAIL++-M, 512/1024/2K resolutions).
- `sdxl-lightning` (CreativeML OpenRAIL++-M, distilled SDXL).
- `ideogram-v3`, `recraft-v3`, `hidream-i1-full`.
- `stable-video-diffusion-img2vid-xt` — added but immediately marked `status: deprecated` (xt-1-1 is successor).

**Multimodal LLMs:**
- `llava-onevision-qwen2-72b` (Apache-2.0).
- `minicpm-v-2.6` (Apache-2.0, edge multimodal).

**Regional / specialized:**
- `jais-30b-chat` (Arabic).
- `tiny-aya` (Cohere, 70+ languages).
- `yi-large` — added but immediately marked `status: deprecated` (Yi-Lightning replaced as flagship 2024-10-16).
- `openrouter/free` (meta-router, released 2026-02-01).

### Tag dimensions expanded

Added to `task` dimension: `math`, `careful-long-running`, `multilingual`, `regional`, `retrieval-augmented`, `transcription`, `streaming`, `conversational`, `routing`, `general`, `vision` (cross-listed with modality).

### Use-case chain updates

- **`code_generation`** — `qwen3-coder-480b-a35b-instruct` is new primary; `glm-5.1` added to last_resort.
- **`code_translation`** — `qwen3-coder-480b-a35b-instruct` is new primary; `deepseek-v4-pro` displaces `deepseek-v3`.
- **`reasoning_verification`** — Added `qwq-32b`, `phi-4-reasoning`. Removed `o4-mini` (deprecated). Added `glm-5.1` to fallback.
- **`careful_long_running_analysis`** — **NEW chain.** Primary: `glm-5.1`. Fallback: `claude-opus-4-7`. Per user direct testimony.
- **`long_document_synthesis`** — Added `claude-opus-4-7` (now 1M context) and `deepseek-v4-pro`.
- **`cross_vendor_review`** — Added GLM 5.1 as a peer reviewer in 3 of the typical pairs. `qwen3-coder-480b-a35b-instruct` paired with claude-sonnet-4-6.
- **`open_default_general`** — Promoted Qwen3 family + GLM 5.1 to primary. Llama 3.3:70b moved to fallback.
- **`speech_synthesis`** — F5-TTS, Sesame CSM, OpenVoice v2, XTTS-v2, Bark added; primary is now `kokoro-tts, f5-tts, sesame-csm`.
- **`image_generation`** — SDXL Lightning, PixArt-Σ, HiDream, Ideogram, Recraft added. `imagen-3` removed (sunset).
- **`video_generation`** — Wan 2.1, Mochi-1, CogVideoX added. SVD-img2vid-xt removed (deprecated).
- **`text_embeddings`** — Open primaries (Stella, Mixedbread, BGE, Nomic) replace BGE-only. Cohere Embed v4 added for multimodal.
- **`reranking`** — **NEW chain.** Open rerankers (BGE, Jina) primary; Cohere fallback.

### Items deferred to next refresh (not yet folded)

- **Gemma 4 ratings** — lab sheet timed out, need re-run.
- **GLM 5.1 ratings** — lab sheet failed permanently due to chunking issue. Need re-run with chunking guidance baked into prompt template.
- **Yi family rationalization** — 01.AI's current lineup needs verification (Yi-Lightning, Yi-1.5, Yi-2.0?).
- **Stable Video Diffusion xt-1-1** — added xt as deprecated; xt-1-1 should be its own entry next round.
- **MiniMax M2.7** — exists per version research; M2.5 may shift status.

### Authority and bias notes

- The composer (Claude Opus 4.7) drafted v1 with self-bias toward Anthropic models and against non-US labs.
- The user explicitly corrected: GLM 5.1 is frontier-class. Treat non-Western labs as peers, not foils.
- Lab reviewers (Opus, Gemini, GPT-5.5) all independently flagged Chinese ecosystem under-representation in v1.
- Lab disagreement: Gemini claimed long-context superiority over Claude; Opus self-rated 4/5 long-context (with explicit "I see my own format drift in long outputs"); both signals retained in respective `ratings:` fields.
- `verified_via:` fields now include `version_research_2026_04_29`, `gap_research_2026_04_29`, `lab_review_opus`, `lab_review_gpt55`, `user_direct_testimony` where applicable.
