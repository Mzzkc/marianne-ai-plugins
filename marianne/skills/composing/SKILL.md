---
name: composing
description: Use when the user wants to compose a Marianne score from a goal, turn an idea into a multi-stage AI workflow, or design orchestration YAML. Triggered by /marianne:compose or when the user describes work that would benefit from multi-stage, multi-agent orchestration.
---

# Score Composition

Composition turns a goal into a score — a program that coordinates intelligences through staged work. You are the composer. The score is played by agents you will never meet on work you will never see. Every structural choice you make now shapes whether that work succeeds.

This skill covers the cognitive work of composition: understanding the goal, recognizing the forces at play, and arranging stages so the structure serves the work. The score-authoring skill covers YAML syntax. The command skill covers execution. This skill is about the shape between them.

Scope: **Marianne orchestration.** The concrete apparatus — instruments, validation types, workspace safety, `mzt` commands — assumes Marianne. The methodology (forces, decomposition, pattern composition) transfers elsewhere; the apparatus does not. If a user asks for composition outside Marianne, say so and adapt.

---

## Preflight

Composition needs corpus vocabulary in working memory. But dumping the whole corpus upfront buries the user's goal under abstract theory. Read in tiers, tied to when you actually need each file.

**Tier 1 — before you analyze forces:**

1. `scores/rosetta-corpus/INDEX.md` — the full pattern catalog, by scale, with problems and signals.
2. `scores/rosetta-corpus/forces.md` — the ten forces and their generators.

**Tier 2 — just-in-time, as you select patterns:**

3. `scores/rosetta-corpus/selection-guide.md` — the section matching your problem type.
4. `scores/rosetta-corpus/patterns/<name>.md` — the full file for each candidate pattern. Not a summary. Not from memory. The file itself. Pattern files carry the shape you are about to implement.

**Tier 2.5 — before you select instruments:**

5. `plugins/marianne/docs/ref/instrument-catalog.md` — the catalog of instruments and musicians with capability, capacity, tags, ratings, and use-case chains. The YAML at `plugins/marianne/docs/ref/instrument-catalog.yaml` is authoritative; the MD is the readable view. Without this, instrument selection is name recognition rather than tag-driven matching. The catalog encodes the open-source-first ladder: open weights primary, opencode/free fallback, subscription/premier as last resort. If your stage's use-case chain isn't obvious from the catalog, search the use-case chains section by your stage's task.

**Tier 3 — on demand:**

- `examples/` and `examples/patterns/` — proof scores, as reference for shape.
- `scores/rosetta-corpus/glossary.md` — when terminology is unclear.

Tiered reading is not permission to skip. What it buys is **attention preservation**: the user's goal stays fresh through the moment of composition. Pattern files must be read before you claim their patterns; that is the one rule here worth being rigid about, because the rest of this skill assumes you have the shape in hand.

---

## Principle Zero

The user is the authority. You propose; they decide. Present reasoning, offer alternatives, get approval before generating YAML.

---

## Phase 0 — Decide Whether to Compose

Not every request warrants a score. Orchestration machinery pays for itself when there is real coordination; when there isn't, it's pure overhead. Answer this before anything else.

A score is the right tool when **two or more** apply:

- The work decomposes into distinct stages with different artifacts or capabilities.
- Independent units benefit from parallel execution — fan-out over files, sources, perspectives.
- Different stages want different instruments.
- Validation between stages matters — contamination downstream costs more than catching it here.
- The work is long-running, retryable, or needs recovery.
- The score will be run again, by someone else, or in different contexts.

A score is **not** the right tool when:

- The user wants a single piece of output one good prompt could produce.
- The user wants one command run with reasoning — that's a CLI invocation.
- The user is exploring and premature structure would freeze the wrong shape.
- The user has the answer and just needs it typed out.
- The score's overhead exceeds the work itself.

**At Phase 0:**

1. Say in one sentence what the user wants.
2. Say in one sentence what serves it — a score, a prompt, a command, a conversation.
3. If it's not a score, say so and recommend the simpler path. If the user wants help with the simpler path, help them with it directly — don't abandon them to navigate without you. If they want the score anyway, they get to overrule you; note the concern and proceed.
4. If it is a score, name the criteria that apply, then continue.

Over-composition is a failure mode of this skill. Under-composition is a failure mode of neglect. The gate sits between them.

---

## Vocabulary

A **score** is a YAML configuration declaring what work to do, which instruments to use, how to validate, and how to recover.

A **sheet** is one agent performing one task — the atomic unit of execution. A **stage** is a logical phase that may fan out into multiple sheets — parallel instances of related work over different data. A fan-out can use one movement-level instrument, a complete `instrument_map`, or deliberate `per_sheet_instruments`; mixed-instrument fan-out is valid when the architecture needs it, but partial concrete coverage should be fixed or documented because validation will warn on ambiguity. In YAML, stages are declared via `movements:` and `sheet.total_items`; the `stage` template variable gives each sheet its phase number.

An **instrument** is any CLI tool or API endpoint wrapped as a plugin profile, with specific capabilities and cost profile. `mzt instruments list` shows what's registered.

**Preludes** inject shared context into every sheet. **Cadenzas** inject per-sheet context. Injection is how you give an agent what it needs. Telling an agent to "read a file" is unreliable; injecting the file is not.

A **concert** chains scores via `on_success`. The **workspace** is shared memory between sheets. The **conductor** is the daemon.

The musical vocabulary is load-bearing, not decoration. When a name feels forced, the architecture may be wrong.

### Forces

Every coordination problem has a force profile. Forces drive pattern selection.

| Force | The question it asks |
|-------|---------------------|
| **Information Asymmetry** | Do different agents need to know different things? |
| **Finite Resources** | Does the work exceed what one agent can handle well? |
| **Partial Failure** | Can components fail independently? |
| **Exponential Defect Cost** | Do problems found late cost more than problems found early? |
| **Producer-Consumer Mismatch** | Do stages produce in formats the next can't directly consume? |
| **Instrument-Task Fit** | Do different tasks need fundamentally different capabilities? |
| **Convergence Imperative** | Does iterative work need domain-specific stopping criteria? |
| **Accumulated Signal** | Must evidence build to a threshold before triggering change? |
| **Structured Disagreement** | Are single perspectives unreliable for this problem? |
| **Progressive Commitment** | Is full commitment before validation risky? |

`scores/rosetta-corpus/forces.md` maps forces to generators and generators to patterns.

### The Rosetta Corpus

The corpus is a growing catalog of coordination patterns organized by scale — within-stage, score-level, concert-level, and cross-cutting. Each pattern file carries: problem, signals, forces, generators, stages (the shape), composes-with, core dynamic, failure mode, and a YAML sketch. New patterns land as novel shapes recur enough to name; the INDEX is the source of truth for what exists today.

Patterns are structural moves, not templates. They name shapes that exist because coordination requires them. Composing multiple patterns creates a shape none of them have alone.

**The corpus is reference, not scripture.** It captures recurring shapes observed to date, not all valid shapes. When honest force analysis finds no pattern matching more than a signal or two, composing from first principles is not a fallback — it's the right move. See *Select Patterns* below.

---

## The Workflow

```
DECIDE → UNDERSTAND → QUESTION → DESIGN GATE → COMPOSE → REVIEW → OFFER
```

Phase 0 is above. The rest assume composition is right.

### Phase 1 — Understand

Study the goal:

- What did the user say they want?
- What do they probably need but didn't articulate?
- What would make the output wrong?

**Offer to investigate the project** before designing. Conventions discovered now prevent validation failures later. The user may already have the context, or the goal may not need project-specific knowledge.

Two investigation dimensions matter:

1. **Venue context** — structure, spec corpus at `.marianne/spec/`, project docs, available instruments.
2. **Codebase analysis** (code goals only) — relevant files, test commands, build/lint commands, integration points.

If your platform supports subagents, `venue-explorer` and `codebase-analyzer` run these in parallel. If not, do it yourself.

### Phase 2 — Question

Ask at least one question. Even when the goal seems clear, confirm your read. Focus on what the user hasn't considered — missing validation strategies, unclear decomposition, unstated constraints. One question per message, multiple choice where possible. Skip only if explicitly told to.

### Phase 3 — Design Gate

Present the architecture before generating YAML. The gate is structural: the design must land as a reviewable artifact — and be reviewed — before any YAML is produced. In an interactive session that means a turn boundary: design, stop, wait for the user, then compose. In an orchestrated compose-system run it means a stage boundary: the design is written as a workspace artifact and a downstream stage (or the user) validates it before composition begins. Either way, if design and YAML collapse into the same response or the same stage, the gate is gone.

Show:

- The forces you identified and why they are active.
- The pattern(s) you selected (or that no pattern fit, and the structure was derived from first principles — name the forces that shaped it).
- How stages decompose: roughly what each does, what depends on what.
- Which instruments serve each stage.
- Where the workspace lives.
- How validations prove the outcome.

Concise for straightforward compositions, fuller for complex ones. Wait for approval.

### Phase 4 — Compose

Generate the YAML. Before writing, load the score-authoring reference — invoke `marianne:score-authoring` or read the tiered docs in this plugin's `docs/ref/`:

- `essentials.md` — syntax, validation types, config, common pitfalls.
- `patterns.md` — fan-out, multi-stage, Jinja, prompt engineering.
- `advanced.md` — concerts, self-chaining, isolation, stale detection.

### Phase 5 — Review

Review adversarially. Dispatch `score-reviewer` if available, or review yourself assuming the score is wrong until proven otherwise. Check workspace safety, YAML correctness, validation quality, first-run safety. Fix critical and important issues before presenting.

### Phase 6 — Offer

Present the score. Show where it saves, what it does, what the review caught. If the conductor is running, offer to submit it. If not, show the run command.

Save location by context:

- Ongoing development → `scores-internal/`
- Project operations → `scores/`
- Documentation examples → `examples/`
- Unclear → ask.

---

## The Composition Methodology

This is the heart of Phase 4: how to move from approved design to correct score.

Composition is judgment. The steps below structure that judgment; they are not a rigid order. Decomposition can reveal wrong pattern selection. Force analysis can reframe the goal. Move fluidly.

### Define the Work

Before touching patterns or YAML:

- What is the input — data, files, state?
- What is the output — what must exist when the score completes?
- What are the units of work? Can they run independently?
- What makes output wrong? What distinguishes done from done well?
- What varies across units? What must be shared?
- What depends on what?

These answers determine everything that follows.

### Analyze Forces

Walk the ten forces. For each, is it active here? Note the evidence — a sentence or two on what makes it active or not. Evidence grounds pattern selection. Without it, pattern choice collapses into name recognition.

`scores/rosetta-corpus/selection-guide.md` organizes patterns by problem type. Start there when the force profile matches a known problem type.

### Select Patterns

Active forces point to candidate patterns. **For each candidate, read the pattern file** at `scores/rosetta-corpus/patterns/<name>.md`. Not a summary. Not from memory. The file itself. Pattern files carry the structural shape — stages, instrument guidance, dependency topology — that you need in the next step. Without the file open, you cannot derive structure; you can only name the pattern.

For each candidate, hold in mind:

- The pattern's `problem` statement and how well it matches yours.
- Which signals match (two or more suggests fit; fewer suggests forcing).
- The minimum stage list and what each stage does.
- The instrument guidance per stage.
- The `composes_with` list — next-round candidates.
- The `Failure Mode` section — this is how the pattern breaks when structure is degraded.

Before committing:

- Why this pattern and not an alternative addressing the same forces?
- If composing: what structural property does the composition create that neither pattern has alone?
- Could any pattern be removed without losing a necessary property?
- Could the problem be served by sequential stages with good validations and no named pattern at all?

**When no pattern fits**, compose from first principles. This is a peer path, not a fallback:

1. Derive stages from the work's dependency graph — what inputs, what outputs, what must precede what.
2. Use the forces framework to justify each boundary — why one stage ends here and the next begins there.
3. At the Design Gate, tell the user explicitly: "No Rosetta pattern matched; I derived the structure from forces and dependencies." Name the forces you applied.
4. Append one line to `docs/technique-ideas.md` describing the shape and why existing patterns didn't cover it. Novel shapes are how the corpus grows.

First-principles composition is the same work as pattern composition with a different input. You still derive stages, place boundaries, select instruments, design injections and validations. What you give up is the vocabulary that lets you borrow structural commitments from prior art. What you gain is fit.

### Derive the Structure

Walk each selected pattern's `stages:` field. For each, know the purpose, the instrument capability, and the dependencies. Compose: sometimes patterns chain sequentially (one's output feeds the next), sometimes they nest (one's single stage expands into another's full shape), sometimes they run in parallel with a convergence point.

Patterns have *core* stages — the distinctive cognitive work — and *bookend* stages like setup, ingestion, and consolidation that naturally overlap across patterns. Bookends can merge when a single stage genuinely serves both patterns. A merge is honest when the merged stage carries every validation from both source stages, every dependency from both source stages, operates on the same artifact, and uses an instrument capable of both stages' work. A merge that drops a validation, decouples a dependency, or collapses distinct artifacts isn't a merge; it is removing structure. If you can't explain what each pattern's core stages are doing in your composition, the pattern is not implemented.

Place a stage boundary where:

- The output format changes.
- The instrument should change.
- Work must be verified before it feeds downstream.
- Parallelism begins or ends.
- Context would exceed useful limits.

Don't place a boundary where:

- Work is naturally atomic.
- Splitting would lose necessary context.
- The boundary is symmetric, not cognitive.

### Select Instruments via Tag Intersection

Different instruments — and different models within them — were built for different work. The catalog at `plugins/marianne/docs/ref/instrument-catalog.{yaml,md}` is the source of truth. Marianne distinguishes:

- **Instrument** — the execution framework, a plugin profile (capabilities: tool use, file edit, shell, vision, MCP). Examples: `claude-code`, `gemini-cli`, `opencode`, `ollama`, `cli`.
- **Musician** — the model played by the instrument (capacity: context, cost, speed, reasoning quality). Identified by a model id; common shapes include `vendor/model`, `local-model:size`, and `openrouter/vendor/model:free`.

For each stage, compute its tag intersection along four dimensions:

- **Tier**: `quick` / `standard` / `heavy` / `max` — how much intelligence the work warrants.
- **Task**: `code`, `code-translation`, `classification`, `synthesis`, `runner`, etc. — what the work IS.
- **Modality**: `text`, `vision`, `image-gen`, `audio-in`, `embedding`, etc. — what it consumes/produces.
- **Constraint**: `cheap`, `fast`, `offline`, `no-rate-limit`, `free`, `open-weights` — what's required.

Then look up the matching use-case chain in the catalog. The chain gives ranked primaries → fallbacks. **Adopt them in order.** A typical stage's `instrument:` and `instrument_fallbacks:` come straight from a chain.

#### The open-source-first ladder

The catalog's chains are designed around Marianne's open-source-first vision:

1. **Primary picks favor open weights and free tier** — a local/open code model for translation, an unlimited-plan open model for runners, a free-tier open model for code generation. The catalog's chains name the current best picks.
2. **Fallback is opencode-routed free or low-cost subscription** — a cheap fast model for classification, a mid-tier frontier model for code work that genuinely needs more capability.
3. **Premier frontier models are the last resort** — reserved for stages where the catalog ratings genuinely warrant the cost (deep synthesis, frontier reasoning, adversarial review).

Reaching for premier when the chain says open weights would suffice needs justification. Open-default reaching for premier doesn't.

#### Cross-vendor verification (subtle)

When a stage produces work that downstream stages will trust as ground truth, consider routing the verification step through a **different vendor lineage** than the producing step. Different training corpora produce different blind spots; correlated models share them. The catalog's `cross_vendor_review` chain enumerates typical pairs.

Use sparingly. Cross-vendor diversity is leverage when verification matters. Overusing it dilutes the signal and slows iteration.

For full multi-perspective review, the `scores/prep/thinking-lab.yaml` score fans out to several frontier reviewers in parallel — one per vendor family, a mix of paid and free/open-weight — producing independent reviews. The lab uses directory-cadenza injection of `scores/prep/thinking-lab-input/` so reviewers see the prompt and context without orchestration overhead. A calling score can chain to it via `on_success` and read the reviews to synthesize.

#### Practical reminders

- Every assignment needs a fallback chain (`instrument_fallbacks:`) so rate limits or outages don't halt the score. The catalog's chains already provide one — copy it.
- Deterministic work — running tests, building, file moves, structural greps — is `cli`, not an AI. Per The Tool Chain pattern.
- `mzt doctor` shows what is actually installed on this conductor. A score referencing an uninstalled instrument fails at runtime, not at `mzt validate`. Prefer instruments verified over instruments remembered.
- The catalog is refreshed by `scores/instrument-catalog-refresh.yaml`. If a musician's `last_verified` is more than 90 days old, treat its ratings with appropriate skepticism.

### Map the Context Flow (load-bearing)

Patterns are the **scaffolding** of a score. Context flow is the **muscle**. Pattern selection gets the structure right; context flow determines whether the right model receives the right inputs to do good work. A score with correct patterns and wrong context flow produces structurally-clean output that misses the point.

Before designing injections, map every load-bearing piece of context the work depends on. For each, answer four questions:

| Context | Source | Lands at | Mechanism |
|---|---|---|---|

- **Context** — the thing the work needs (channel voice, full transcript, prior-stage output, etc.)
- **Source** — where it comes from (corpus directory, upstream stage's artifact, score variable, score variable composed with stage data)
- **Lands at** — which sheet(s) need it (every sheet via prelude, one specific stage via cadenza, just the stage that produces the next artifact via cross_sheet)
- **Mechanism** — `prelude` (every sheet), `cadenza` per-stage (specific sheet), file path the agent loads via Read (when content is large or per-instance unique), template variable from `prompt.variables` (small static values)

If a load-bearing context piece has no row, that's the structural gap that produces bad output. If two pieces share a row, you have a choice to make about how they combine.

**Match instrument capacity to what the context enables.** A 7B local model cannot carry distinctive brand voice from a corpus, however well that corpus is injected. The instrument must be capable of USING the context you route to it. Pattern selection often has to revise after this step: a stage that needs full-document context for high-stakes synthesis routes to a frontier model, not a `quick`-tier one — even when the catalog's default chain for that task tier suggested otherwise.

This is especially important for **brand-stake / livelihood-stake** work. For high-stakes synthesis stages, spend disproportionately on context-flow design and model capability. Defaults that are sensible for "ship fast, iterate" are wrong for "this can't fail." Cross-vendor verification, deterministic post-checks (red-line linters), and corpus-richness gates earn their keep here.

### Design Injections

Injections are the implementation of the context-flow map. If an agent needs content to do its work, inject it — don't tell agents to "read this file." Telling is unreliable; injection is not.

- **Preludes** — shared context for every sheet. Conventions, standards, the spec passage, the glossary, the channel voice corpus. A score without preludes leaves each agent to find context independently; they will find it differently, or not at all.
- **Cadenzas** — per-sheet context for specific sheets. The pattern file for this stage, the upstream output to review, the per-instance data for fan-out specialization. Both `file:` and `directory:` modes are supported; directory mode globs all files in the directory and is ideal for evolving corpora the composer maintains by hand.
- **Read tool** — when context is per-instance and large enough that injection would balloon every fan-out instance's prompt, instruct the agent to read specific files directly. Trade-off: less reliable than injection (agent may forget); more flexible.
- **Template variables** — `prompt.variables` for small static values (paths, thresholds, names) referenced via Jinja in templates AND via Python format in validation paths/commands.

Preludes establish the substrate. Cadenzas specialize each stage. Together they implement the rows of your context-flow map.

### Design Validations

Three questions, in order:

1. **Can the agent pass all my validations without achieving this goal?** If yes, the validations are decorative. Add one that proves the goal.
2. **If the work is done but done poorly, do my validations catch that?** Completion and quality are different. A file can exist and contain nothing useful. Code can pass tests and be unmaintainable. Distinguish adequate from inadequate, not just present from absent.
3. **When a stage produces bad output, what happens?** If the answer is "it flows downstream and contaminates everything after it," the score has a structural gap. Catching problems early is itself work that belongs in the structure.

Validations prove outcomes, not process. Layer coarse to fine — existence first, structure second, behavior third. Skip fine checks when coarse checks fail.

For fan-out, validate each instance independently. For synthesis stages, validate the output reflects integration, not concatenation.

**Negative-test your validations.** Ask: if the agent wrote an empty file, a one-line placeholder, or a refusal, would this validation catch it? Every markdown artifact stage should have a word-count or structural-marker check alongside `file_exists` — `file_exists` alone is the most common decorative validation.

### Self-Review

Step back from the structural work and ask: **does this score still serve the user's goal?** Structural perfection for the wrong problem is still wrong. The patterns are vocabulary; the destination is intent.

Then, with that alignment held, consider each stage:

- Can this instrument do this work with quality? If "probably," decompose further or strengthen the instrument.
- Is every required input injected, not just referenced?
- Can the agent pass validations without doing the work?
- Are dependencies declared for everything that needs them?
- For fan-out: `parallel.enabled: true`? Dependencies right?
- Does `mzt validate` pass?
- For concerts: absolute `job_path`? `fresh: true` for self-chaining?
- Would each validation catch an empty or placeholder output?
- Are all referenced instruments registered?

Self-review is reflection, not a checklist you race through. If you are moving fast enough to not notice which stage fails a question, you are moving too fast.

---

## Workspace Safety

**Never** set workspace to the project root. If `workspace_lifecycle.archive_on_fresh` triggers, the workspace is archived or wiped. If workspace is the project root, the project is destroyed.

**Default:** `./workspaces/{job-name}-workspace`

For scores that modify source code, use a dual-path pattern: workspace for artifacts and state, a `project_root` variable for the codebase. Agents work in `project_root` and write artifacts to `workspace`.

Always:

- Confirm the workspace path with the user.
- Verify the path doesn't contain `.git/`, `pyproject.toml`, or other project-root markers at its root.
- Use `{{ workspace }}` in templates, `{workspace}` in validations — mixing these is the most common syntax error.

---

## References

| Purpose | Where |
|---------|-------|
| YAML syntax, validation types, config structure, common pitfalls | `marianne:score-authoring` |
| Running, monitoring, debugging, recovering jobs | `marianne:command` |
| Full pattern catalog by scale, with problems and signals | `scores/rosetta-corpus/INDEX.md` |
| Individual pattern shapes, stages, composition edges | `scores/rosetta-corpus/patterns/<name>.md` |
| Forces → generators → patterns mapping | `scores/rosetta-corpus/forces.md` |
| Problem type → pattern composition mapping | `scores/rosetta-corpus/selection-guide.md` |
| Marianne terminology | `scores/rosetta-corpus/glossary.md` |
| Proof scores (how patterns become YAML) | `examples/patterns/` |
| Score archetypes and real examples | `examples/` |
| Complete score YAML reference | `docs/score-writing-guide.md` |
