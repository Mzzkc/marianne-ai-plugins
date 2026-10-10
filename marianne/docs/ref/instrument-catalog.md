# Instrument Catalog

**Generated:** 2026-04-29 (v1.1 fact-fold) from `instrument-catalog.yaml`; current instrument/model corrections applied through 2026-09-26.
**Refresh policy:** every 30 days; per-musician staleness flagged at 90 days. Run `scores/instrument-catalog-refresh.yaml`.
**Changelog:** `CHANGELOG-instrument-catalog.md` records every fact change.

> **Model-profile refresh 2026-09-26:** broad provider research added 29
> catalog entries from official-source evidence: Claude Opus 5.5 / Fable 5.1 /
> Sonnet 5 and GPT-6 Astra / Sol / Luna (Opus 5.5 also joined the active
> Claude Code profiles; GPT-6 Sol/Luna joined codex-cli); `gemini-3.8-flash`
> joined the `gemini-cli` runs list while its profile `default_model` stays
> `gemini-3.7-flash`; `deepseek-v4-pro` reached GA and `deepseek-v4.1-flash`
> (API ID `deepseek-flash`) superseded V4 Flash; `mistral-large-3` and 21
> further creator releases (Yi-Lightning, BGE-M3, FLUX.2 Pro, Seedream 5.0
> Pro, Command A+, Jais 2, distil-large-v3.5, Ideogram 4.0, Jina reranker
> v3.5 / embeddings v5, LTX-2, Llama 4 Maverick, Nemotron 3.5 Lightning,
> MiniCPM-V 4.6, Recraft V4.1, voyage-4-large, nomic-embed-text-v2-moe,
> HiDream O1 Image, eleven_v3_conversational, Trinity-Large-Thinking,
> Hermes-4-405B) were added as catalog-only entries without new routes. All
> default models were preserved exactly.

> **Gemini correction 2026-08-17:** stable / GA `gemini-3.7-flash` was released
> 2026-08-13 with a 1,048,576-token input limit, 65,536-token output limit,
> text/image/video/audio/PDF input, text output, and low/medium/high thinking.
> `minimal` is unsupported and returns an error. Current Flash chains use 3.7;
> the older `gemini-3-flash-preview` entry remains historical only.

> **Codex correction 2026-07-16:** GPT-5.6 Sol, Terra, Luna, and their `[1m]`
> variants are models played through `codex-cli`. There is no separate
> `gpt-5.6` instrument, and Marianne does not set a Codex default model.

> The YAML is authoritative. This markdown is a human view — read the YAML when scripting against the catalog.

---

## How to Read This

Marianne distinguishes **instruments** from **musicians**:

- **Instrument** = the execution framework (a plugin profile). Determines *capabilities* — tool use, file editing, shell access, vision, MCP.
- **Musician** = the model played by the instrument. Determines *capacity* — context window, cost, speed, reasoning quality.

A score may name a **capability class** such as `strong` or `writing` in an
instrument position. The class is an installation-specific ordered chain of
instrument profiles, defined by the packaged default and optional user/venue
`classes.yaml` layers. It is a routing configuration, not a new instrument or
musician. `mzt instruments classes show --json` displays the effective chain
and source hashes; `mzt instruments classes check` tests configuration and
current route availability. The chain is frozen into each job's checkpoint.

Composers select tag intersections (`tier × task × modality × constraint`) and the catalog maps the intersection to ranked model chains. **Open-source-first by default**; subscription and premier as fallbacks where open models genuinely don't suffice. Frontier means capability tier, not vendor origin.

---

## Tag Dimensions

| Dimension | Tags |
|---|---|
| **Tier** | `quick`, `standard`, `heavy`, `max` |
| **Task** | `code`, `code-translation`, `code-review`, `review`, `research`, `writing`, `transform`, `design`, `classification`, `synthesis`, `planning`, `reasoning`, `math`, `tool-use`, `agent`, `careful-long-running`, `multilingual`, `regional`, `retrieval-augmented`, `transcription`, `streaming`, `conversational`, `routing`, `general`, `vision` |
| **Modality** | `text`, `vision`, `image-gen`, `audio-in`, `speech-out`, `video-gen`, `audio-gen`, `embedding`, `reranking`, `multimodal` |
| **Constraint** | `cheap`, `fast`, `thorough`, `offline`, `no-rate-limit`, `free`, `open-weights`, `subscription`, `premier`, `oss-default`, `deprecated`, `sunset` |

---

## Instruments

| Instrument | Auth | Capabilities | Notes |
|---|---|---|---|
| `claude-code` | Anthropic sub or API | tool_use, file_edit, shell, web_fetch, MCP, vision | Full agentic capability |
| `gemini-cli` | Google sub or API | tool_use, file_edit, shell, vision, MCP, structured_output, thinking | Runs `gemini-3.8-flash` (added 2026-09-26; profile `default_model` stays `gemini-3.7-flash`); catalog presence does not prove local configuration or live execution |
| `antigravity` | existing Google account/API configuration | tool_use, file_edit, shell, MCP, session_resume, thinking | Profile-selected models; configuration and dispatch compatibility require separate checks |
| `codex-cli` | OpenAI Plus or API | tool_use, file_edit, shell, vision, MCP, thinking | Plays GPT-6 Sol/Luna/Astra and GPT-5.6 Sol/Terra/Luna; model remains client-selected unless a score overrides it |
| `opencode` | per-provider | tool_use, file_edit, shell, multi_provider | Best route to OpenRouter free tier and Z.AI Coding Plan |
| `aider` | per-provider | tool_use, file_edit, git, shell, multi_provider | Strong git integration |
| `goose` | per-provider | tool_use, file_edit, shell, MCP, multi_provider | Block.xyz; MCP-strong |
| `crush` | per-provider | tool_use, terminal_ui, multi_provider | Charm.land TUI |
| `ollama` | none | local, offline, no_rate_limit, structured_output | OpenAI-compatible text/structured-output profile; no file or shell tools |
| `cli` | none | shell, deterministic | Plain bash; cheapest option per The Tool Chain |

---

## Musicians by Family

### Anthropic — Claude

| Model | Context | Cost in/out (per 1M) | Tags | Status |
|---|---:|---|---|---|
| `claude-opus-5-5` | **1M** | $4 / $20 | max, premier | current Opus-line release (added 2026-09-26; joined Claude Code profiles) |
| `claude-fable-5-1` | **1M** | $10 / $50 | max, premier | current flagship (catalog entry added 2026-09-26) |
| `claude-sonnet-5` | **1M** | $2 / $10 | heavy, standard | current Sonnet, native 1M window (catalog entry added 2026-09-26) |
| `claude-opus-4-7` | **1M** (released 2026-04-16) | $15 / $75 | max, premier | current |
| `claude-sonnet-4-6` | 200K (1M beta) | $3 / $15 | heavy, standard | current |
| `claude-haiku-4-5-20251001` | 200K | $0.80 / $4 | quick, fast | current |

### OpenAI

| Model | Context | Cost in/out | Tags | Status |
|---|---:|---|---|---|
| `gpt-6-astra` | 1.05M | $10 / $50 | max, premier | GPT-6 hard-work tier (catalog entry added 2026-09-26) |
| `gpt-6-sol` | 1.05M | $2 / $10 | heavy, standard | GPT-6 balanced tier (added 2026-09-26; joined codex-cli) |
| `gpt-6-luna` | 1.05M | $0.1 / $0.5 | quick, fast | GPT-6 high-volume tier (added 2026-09-26; joined codex-cli) |
| `gpt-5.6-sol` | 272K (1.05M variant) | $5 / $30 | max, premier | current flagship |
| `gpt-5.6-terra` | 272K (1.05M variant) | $2.50 / $15 | heavy, standard | current balanced tier |
| `gpt-5.6-luna` | 272K (1.05M variant) | $1 / $6 | quick, fast | current throughput tier |
| `gpt-5.5` | 256K | $5 / $25 | max, premier, **deprecated** | superseded by GPT-5.6 |
| `gpt-5` | 200K | $2.50 / $10 | heavy, **deprecated** | retired from ChatGPT 2026-02-13 |
| `o4-mini` | 128K | $1.10 / $4.40 | reasoning, **deprecated** | fully deprecated |

### Google — Gemini 3

| Model | Context | Cost in/out | Tags | Status |
|---|---:|---|---|---|
| **`gemini-3.8-flash`** | **1,048,576 input / 65,536 output** | $0.75 / $3.75 per 1M (through 2026-12-31) | quick, standard, heavy | **stable / GA; current Flash release; served via `antigravity` and `gemini-cli`; ratings provisional pending independent evaluation** |
| `gemini-3.7-flash` | 1,048,576 input / 65,536 output | not recorded | quick, standard, heavy | historical fallback; released 2026-08-13; successor 3.8; gemini-cli profile `default_model` remains 3.7 |
| `gemini-3.1-pro-preview` | 2M | $2.50 / $10 | max | preview |
| `gemini-3-flash-preview` | 1M | $0.30 / $1.20 | quick, fast | historical fallback/reference only; current chains use 3.8 |
| `gemini-2.5-pro` | 2M | $1.25 / $5 | heavy, **deprecating** | deprecates 2026-06-17 (API), 2026-10-16 (Vertex) |

Gemini 3.7 Flash accepts text, image, video, audio, and PDF input and produces
text. Google documents caching, code execution, preview computer use, file
search, function calling, Google Maps grounding, search grounding, structured
output, thinking, and URL context. Use only low, medium, or high thinking.

Official evidence: [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash),
[models index](https://ai.google.dev/gemini-api/docs/models), and
[Gemini API changelog](https://ai.google.dev/gemini-api/docs/changelog).
Catalog availability through `gemini-cli` and `antigravity` is not proof of a
configured local profile, dispatch compatibility, authentication, or a live
model execution; this catalog refresh performed no live probe.

### Z.AI — GLM (frontier-class, MIT-licensed for 5.1)

| Model | Context | Cost | Tags | Status |
|---|---:|---|---|---|
| **`glm-5.3`** | **1M** | Coding Plan subscription | **max, heavy, premier** | **current; use high/max reasoning for well-bounded work. Composer-calibrated at Fable 5-level on that scope and preferred for authorized defensive vulnerability discovery through specialized scores.** |
| **`glm-5.1`** | **200K** | free (MIT) | **max, premier, open-weights, oss-default** | **frontier — SWE-Bench Pro 58.4 beats GPT-5.4, Opus 4.6, Gemini 3.1 Pro.** Released 2026-04-07. **Trusted by user over Gemini for careful long-running analysis.** ⚠ Quirk: must chunk tool calls. |
| `glm-5` | 128K | hosted | heavy, premier | Z.AI flagship hosted |
| `glm-5v-turbo` | 128K | hosted | heavy | Vision variant of GLM 5 (released 2026-04-01) |
| `zai-coding-plan/glm-5-turbo` | 131K | free (Coding Plan) | standard, no-rate-limit | ⚠ Quirk: chunk tool calls |
| `zai-coding-plan/glm-4.7-flash` | 131K | free (Coding Plan) | quick, fast | ⚠ Quirk: chunk tool calls |
| `openrouter/z-ai/glm-4.5-air:free` | 131K | free OR | standard, open-weights | ⚠ Quirk: chunk tool calls |

> **Historical GLM tool-call chunking quirk:** older GLM releases failed on
> overly large single tool calls. Do not project that behavior onto GLM 5.3 as
> a fact without a fresh probe; still bound outputs and validate tool results.

### Alibaba — Qwen3 family (the biggest 2026 catalog gap, now filled)

| Model | Context | License | Notes |
|---|---:|---|---|
| `qwen3-coder-480b-a35b-instruct` | **256K** | Apache-2.0 | Strongest open-weight code model. **New primary** in code generation/translation chains. |
| `qwen3-235b-a22b` | 131K | Apache-2.0 | Flagship general MoE. |
| `qwen3.6-27b` | 262K → 1M YaRN | Apache-2.0 | Released 2026-04-22, dense, single-GPU friendly. |
| `qwen3.6-35b-a3b` | 262K | Apache-2.0 | Released 2026-04-16, MoE 3B-active, runs on consumer hardware. |
| `qwen3-32b` | 32K | Apache-2.0 | Practical local Qwen3. |
| `qwq-32b` | 32K | Apache-2.0 | Open-weight reasoning (o1-style). |
| `qwen2.5-coder:32b` | 131K | Apache-2.0 | Local code specialist (legacy after Qwen3-Coder). |

### DeepSeek

| Model | Context | License | Status |
|---|---:|---|---|
| `deepseek-v4-pro` | **1M** | DeepSeek license | **GA** (was preview; confirmed 2026-09-26); 1.6T MoE / 49B active |
| `deepseek-v4.1-flash` | pending fold | — | current Flash; API ID `deepseek-flash`; multimodal; superseded V4 Flash (added 2026-09-26) |
| `deepseek-v4-flash` | 1M | DeepSeek license | **superseded** by V4.1 Flash at API ID `deepseek-flash`; 284B / 13B active |
| `deepseek-v3` | 128K | open-weight | **deprecating** — endpoints retire 2026-07-24 |
| `deepseek-r1` | 128K | MIT | open-weight reasoning |

### Mistral

| Model | Context | License | Notes |
|---|---:|---|---|
| `mistral-small-4` | 128K | Apache-2.0 | Released 2026-03-16, 119B/6B-active, multimodal — merges Magistral+Pixtral+Devstral |
| `mistral-nemo-12b` | 128K | Apache-2.0 | Cheap local generalist |
| `mistral-large-3` | 256K | open-weight | GA multimodal successor to Large 2 (added 2026-09-26) |
| `mistral-large-2` | 128K | proprietary | Mistral hosted flagship |
| `codestral:22b` | 32K | open | Code specialist |

### Microsoft — Phi-4

| Model | Context | License | Notes |
|---|---:|---|---|
| `phi-4-reasoning` | 32K | MIT | 14B with thinking blocks, 75.3% AIME 2024 |
| `phi-4-multimodal` | 32K | MIT | 5.6B unified speech+vision+text |
| `phi-4:14b` | 16K | MIT | Base 14B model |

### Other notable LLMs

| Model | Context | Notes |
|---|---:|---|
| `cohere-command-r-plus` | 128K | RAG-optimized with citation grounding (CC-BY-NC-4.0) |
| `command-a-plus-05-2026` | 128K / 64K out | Cohere Command A+ enterprise text/vision (added 2026-09-26) |
| `llama3.3:70b` | 128K | Legacy local/open fallback |
| `meta-llama/Llama-4-Maverick-17B-128E-Instruct` | — | Llama 4 Maverick, natively multimodal successor line (added 2026-09-26) |
| `openrouter/google/gemma-4-31b-it:free` | 262K | Free OR |
| `openrouter/minimax/minimax-m2.5:free` | 196K | SWE-Bench Verified 80.2%; M2.7 successor exists |
| `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | 262K | Free OR |
| `nemotron-3.5-lightning-30b-a3b` | — | NVIDIA's newest announced Nemotron LLM (added 2026-09-26; no broker slug) |
| `jais-30b-chat` | 8K | Arabic-specialized |
| `jais-2` | 70B | Arabic open-weight successor to Jais-30B (added 2026-09-26) |
| `tiny-aya` | 32K | Cohere, 70+ languages |
| `yi-large` | 32K | **deprecated** as flagship — Yi-Lightning replaced 2024-10-16 |
| `yi-lightning` | — | 01.AI MoE flagship that replaced yi-large (catalog entry added 2026-09-26) |
| `arcee-ai/Trinity-Large-Thinking` | — | Released successor behind the inventoried OpenCode free route (added 2026-09-26) |
| `NousResearch/Hermes-4-405B` | — | Hermes 4, successor behind the inventoried Hermes 3 free route (added 2026-09-26) |
| `openrouter/free` | meta | OpenRouter auto-router for free models (released 2026-02-01) |

### Multimodal (text + vision)

| Model | License | Notes |
|---|---|---|
| `llava-onevision-qwen2-72b` | Apache-2.0 | Open multimodal at 72B |
| `minicpm-v-2.6` | Apache-2.0 | Edge-class, 8B, real-time video understanding |
| `openbmb/MiniCPM-V-4.6` | Apache-2.0 | Newer small vision model; 2.6 retained (added 2026-09-26) |

### Embeddings

| Model | License | Notes |
|---|---|---|
| `stella-en-1.5b-v5` | MIT | Top of MTEB at size class |
| `mixedbread-ai/mxbai-embed-large-v1` | Apache-2.0 | Binary quantization support |
| `bge-large-en-v1.5` | open | English baseline |
| `bge-m3` | open | Multilingual multigranular embedding (added 2026-09-26) |
| `nomic-embed-text-v1.5` | Apache-2.0 | Long-context emphasis |
| `nomic-ai/nomic-embed-text-v2-moe` | Apache-2.0 | Multilingual MoE text embedding (added 2026-09-26) |
| `nomic-embed-vision-v1.5` | Apache-2.0 | Multimodal |
| `jina-embeddings-v3` | CC-BY-NC-4.0 | Task-specific LoRAs |
| `jina-embeddings-v5-text-small` | — | Jina's current embedding; v3 retained (added 2026-09-26) |
| `cohere-embed-v4` | proprietary | Multimodal, 128K context |
| `voyage-3` | proprietary | Domain variants |
| `voyage-4-large` | proprietary | Current MoE embedding (added 2026-09-26) |
| `text-embedding-3-large` | proprietary | OpenAI flagship |

### Reranking

| Model | License | Notes |
|---|---|---|
| `bge-reranker-v2-m3` | open | Multilingual |
| `jina-reranker-v2-base-multilingual` | Apache-2.0 | Open multilingual |
| `jina-reranker-v3.5` | — | Jina's current reranker; v2 retained (added 2026-09-26) |
| `cohere-rerank-3.5` | proprietary | Premier managed |

### Speech (audio-in)

| Model | License | Notes |
|---|---|---|
| `whisper-large-v3` | open | Canonical batch ASR |
| `distil-whisper-large-v3` | open | Fast English variant |
| `distil-whisper/distil-large-v3.5` | open | Newer official distil-whisper release; v3 retained (added 2026-09-26) |
| `nvidia-canary-1b` | CC-BY-NC-4.0 | Multilingual ASR + translation |
| `nvidia-parakeet-tdt-0.6b-v2` | CC-BY-4.0 | Streaming-capable |
| `facebook/seamless-m4t-v2-large` | CC-BY-NC-4.0 | Speech-to-speech translation |

### Speech (speech-out)

| Model | License | Notes |
|---|---|---|
| `kokoro-tts` | open | Fast small open TTS |
| `f5-tts` | MIT | Voice cloning, flow-matching |
| `sesame-csm` | Apache-2.0 | Conversational, 24kHz, in HF Transformers (released March 2025) |
| `openvoice-v2` | MIT | Voice cloning, 9 + zero-shot languages |
| `xtts-v2` | Coqui Public Model License | 17 languages |
| `bark` | MIT | Generative audio + speech + sound effects |
| `elevenlabs-v3` | proprietary | Premier commercial TTS |
| `eleven_v3_conversational` | proprietary | Expressive low-latency conversational speech (added 2026-09-26) |

### Image generation

| Model | License | Notes |
|---|---|---|
| `flux-1-pro` | proprietary | Premier |
| `flux-2-pro` | proprietary | Current FLUX.2 Pro commercial image gen (added 2026-09-26) |
| `flux-1-dev`, `flux-schnell` | open-weight | Open Flux variants |
| `stable-diffusion-3.5-large` | open | Stability flagship |
| `pixart-sigma` | CreativeML OpenRAIL++-M | 512/1024/2K resolutions |
| `sdxl-lightning` | CreativeML OpenRAIL++-M | 1/2/4/8-step variants |
| `seedream-5.0-pro` | proprietary | ByteDance Seed current image gen, supersedes 4.5 (added 2026-09-26) |
| `hidream-i1-full` | open-weight | Multi-LLM text encoder |
| `hidream-o1-image` | open-weight | HiDream's current unified image model (added 2026-09-26) |
| `ideogram-v3` | proprietary | Text rendering specialist |
| `ideogram-4.0` | open weights + API | Succeeds v3 (added 2026-09-26) |
| `recraft-v3` | proprietary | Vector/design |
| `recraft-v4.1` | proprietary | Current Recraft release (added 2026-09-26) |
| `imagen-3` | proprietary | **sunset** — migrate by 2026-06-30 |

### Video generation

| Model | License | Notes |
|---|---|---|
| `wan2.1-t2v-14b` | Apache-2.0 | Open T2V |
| `mochi-1` | Apache-2.0 | Open T2V |
| `cogvideox-5b` | CogVideoX license | 720x480 / 8fps / 6s |
| `hunyuan-video` | open-weight | Open T2V |
| `ltx-video` | open-weight | Fast open video |
| `ltx-2` | open-weight | Synchronized audio/video generation (added 2026-09-26) |
| `stable-video-diffusion-img2vid-xt` | Stability community | **deprecated** (xt-1-1 successor) |
| `veo-3` | proprietary | Google premier |
| `sora-2` | proprietary | OpenAI premier |

---

## Use-Case Chains

Open-source-first ranking. `→` = fallback ladder.

### Code generation
1. `qwen3-coder-480b-a35b-instruct` (Apache-2.0, 256K)
2. `openrouter/minimax/minimax-m2.5:free` (SWE-Bench 80.2%)
3. `qwen2.5-coder:32b` (local)
→ `claude-sonnet-4-6`, `mistral-small-4`, `openrouter/google/gemma-4-31b-it:free`
→ last resort: `claude-opus-4-7`, `gpt-5.6-sol`, `glm-5.3`

### Code translation (port-toolkit-style)
1. `qwen3-coder-480b-a35b-instruct`, `openrouter/minimax/minimax-m2.5:free`, `qwen2.5-coder:32b`, `deepseek-v4-pro`
→ `claude-sonnet-4-6`, `mistral-small-4`
→ last resort: `claude-opus-4-7`, `glm-5.3`

### Reasoning verification
1. `deepseek-r1`, `qwq-32b`, `phi-4-reasoning`
→ `claude-opus-4-7`, `gemini-3.1-pro-preview`, `glm-5.3`

### **Careful long-running analysis** (NEW chain)
1. **`glm-5.3`** — primary for well-bounded work at high/max reasoning per composer operational calibration
→ `claude-opus-4-7`
→ last resort: `gpt-5.6-sol`

### Long-document synthesis (>200K tokens)
1. `gemini-3.8-flash` (1,048,576), `claude-opus-4-7` (1M), `deepseek-v4-pro` (1M)
→ `gemini-3.1-pro-preview` (2M)

### Classification
1. `zai-coding-plan/glm-4.7-flash`, `phi-4:14b`
→ `gemini-3.8-flash`, `claude-haiku-4-5-20251001`

### Cross-vendor review (subtle)

Use `skills/research/scores/thinking-lab.yaml` for independent review with the configured distinct-family roster; see the research skill for isolated input and concert binding. Typical pairs:

- `claude-opus-4-7` ↔ `gpt-5.6-terra`, `gemini-3.1-pro-preview`, **`glm-5.3`**
- `gpt-5.6-terra` ↔ `claude-opus-4-7`, `glm-5.3`
- `glm-5.3` ↔ `claude-opus-4-7`
- `qwen3-coder-480b-a35b-instruct` ↔ `claude-sonnet-4-6`

> GLM-as-reviewer needs chunking guidance in prompt.

### Agent loops
1. `openrouter/nvidia/nemotron-3-super-120b-a12b:free`, `claude-sonnet-4-6`
→ `claude-opus-4-7`, `gpt-5.6-terra`

### Runner stage (mostly deterministic)
1. **`cli`** — the actual default
2. `zai-coding-plan/glm-4.7-flash` — if some LLM judgment needed
→ `phi-4:14b`, `claude-haiku-4-5-20251001`

### Open-default general
1. `qwen3-235b-a22b`, `qwen3.6-27b`, `qwen3-coder-480b-a35b-instruct`, `glm-5.3`
→ `openrouter/minimax/minimax-m2.5:free`, `openrouter/google/gemma-4-31b-it:free`, `mistral-small-4`, `llama3.3:70b` (legacy)
→ last resort: `claude-sonnet-4-6`

### Speech transcription
Primary: `whisper-large-v3`, `nvidia-parakeet-tdt-0.6b-v2`
Fallback: `distil-whisper-large-v3`, `nvidia-canary-1b`, `facebook/seamless-m4t-v2-large` (translation pipelines)

### Speech synthesis
Primary: `kokoro-tts`, `f5-tts`, `sesame-csm`
Fallback: `openvoice-v2`, `xtts-v2`, `bark`
Last resort: `elevenlabs-v3`

### Image generation
Primary: `flux-schnell`, `flux-1-dev`, `sdxl-lightning`
Fallback: `stable-diffusion-3.5-large`, `pixart-sigma`, `hidream-i1-full`
Last resort: `flux-1-pro`, `ideogram-v3`, `recraft-v3`

### Video generation
Primary: `wan2.1-t2v-14b`, `ltx-video`, `mochi-1`, `hunyuan-video`
Fallback: `cogvideox-5b`
Last resort: `veo-3`, `sora-2`

### Text embeddings
Primary: `stella-en-1.5b-v5`, `mixedbread-ai/mxbai-embed-large-v1`, `bge-large-en-v1.5`, `nomic-embed-text-v1.5`
Fallback: `jina-embeddings-v3`, `cohere-embed-v4`, `voyage-3`, `text-embedding-3-large`
Multimodal: `nomic-embed-vision-v1.5`, `cohere-embed-v4`

### Reranking
Primary: `bge-reranker-v2-m3`, `jina-reranker-v2-base-multilingual`
Fallback: `cohere-rerank-3.5`

---

## Composer Workflow

1. **Identify the stage's task** — code translation, classification, synthesis, runner, etc.
2. **Identify hard constraints** — must-be-offline? long-context? rate-limit-proof? large output (mind GLM chunking)?
3. **Look up the matching use-case chain.** The chain gives ranked primaries → fallbacks.
4. **Map to YAML** — set `instrument:` to the recommended primary's instrument; set `instrument_config.model:` to the musician id; set `instrument_fallbacks:` to the fallback chain.
5. **Justify any deviation.** If reaching for premier when the chain says open weights would suffice, document why. Marianne's open-source-first ethos puts the burden of proof on premier picks.
6. **For GLM-routed stages**, add chunking guidance: "Write your output in chunks of ~50–100 lines per Write/Edit; multiple small tool calls succeed where single large ones fail."

---

## Refresh

The catalog is a snapshot. Run `scores/instrument-catalog-refresh.yaml`:

1. Probe currently-installed instruments (`mzt doctor`)
2. Web-research vendor releases since `last_verified`
3. Scan OpenRouter / Hugging Face for new free-tier models
4. Run research independent-review mode on the changeset with the configured qualified roster and complete original context
5. Diff against current catalog
6. Write a versioned update with citations

Recommended cadence: monthly. Auto-staleness flag at 90 days per musician.

## v1.1 deferred items

- **Gemma 4 + GLM 5.1 ratings** — lab pass deferred (Gemma timed out, GLM hit chunking quirk). Re-run with chunking guidance baked in.
- **Yi family rationalization** — Yi-Lightning vs Yi-1.5/2.0 etc.
- **stable-video-diffusion-img2vid-xt-1-1** — successor entry not yet drafted.
- **MiniMax M2.7** — exists per version research; M2.5 may shift.
