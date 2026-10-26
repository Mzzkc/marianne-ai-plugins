# Concept to Completion

The default route for a new commission, from a rough concept to a finished,
handed-over result. Follow the six movements in order. Each one ends at a
named artifact, and the next one consumes it. Use the two shipped scores
wherever they fit: they encode movements 2 and 4 so you do not rebuild them.

| Movement | Ends with | Shipped machinery |
|---|---|---|
| 1. Intake | the problem, limits, deeper needs, tempo | `spec-forge.yaml` sheets 1-2 |
| 2. Breakdown | approved specs, parts, integration docs | `spec-forge.yaml` (holds for approval) |
| 3. Casting and review | a team and a review method per part | `design-to-orchestra.yaml` sheets 1-2 |
| 4. Scores and concerts | a validated, reviewed, locked fleet | `design-to-orchestra.yaml` |
| 5. Performance | parts solved, integrated, in people's hands | the fleet; persistent-agent engagements |
| 6. Polish | a recorded backlog worked down from real use | `quality-continuous`, `issue-triage` → `issue-solver` |

Both scores live in `examples/engineering/`. A part a score cannot express
goes to a persistent agent's lifecycle; neither score replaces judgment.

## 1. Intake

State what actually needs solving, in the stakeholders' words. Then find what
is underneath it: ask the probing questions, read their context, and record
each deeper need as stated or inferred. Record every limit (time, money,
people, skills, platforms, data, law, maintenance) as hard or soft; limits
move, so note which might.

Set the **tempo** before anything else. A fast commission tolerates more minor
faults in the first cut, recorded for later; it never tolerates faults that
lose data, expose people or miss the stated need. Tempo decides when the
first thing reaches human hands, what may ship deferred, and how many repair
passes the scores you commission get (rapid 2, standard 3, thorough 5). The
two shipped scores read tempo for triage and the prototype cut; their own
review loops are fixed at three passes, and `max_iterations` is the edit for
a commission that needs a different number.

Look at the problem across domains at once (COMP, SCI, CULT, EXP, META).
`spec-forge` does this as five blind parallel lenses; their convergence is the
shape of the solution and their conflicts are the decisions to make.

Questions only a stakeholder can answer never block the work. Ask them once,
together, each with the assumption you will proceed on, and continue. Hold
only an irreversible step that depends on the answer.

This applies to every domain. A grant, a campaign or a curriculum has parts,
contracts, reviews and a prototype the same way software does.

## 2. Breakdown

Build specs and designs that every worker and every reviewer reads. Design for
change: modular parts with explicit interfaces, so humans can maintain one part
without holding the whole. Bake quality in at the spec: each part names its
review method and acceptance checks before anyone builds it.

Each part gets its own spec and an integration document saying what it
consumes, what consumes it, and which checks prove the joins. Put parts in
waves. Most parts build in parallel against each other's contracts; a later
wave is only for a part that needs another part's finished output.

Lay the design out for the stakeholders against their deeper needs, not the
spec's structure, and get their approval. The approval is theirs or the
composer's, never the conductor's: "take it from here" delegates the work,
not the stakeholders' judgment. When stakeholder time is scarce, size the
brief to the time they have; if even that is out of reach, the composer
approves on their behalf and the stakeholders' first look is the prototype.
`spec-forge` does all of this and stops in a FERMATA on its last sheet with
`07-stakeholder-brief.md`:

```bash
mzt run examples/engineering/spec-forge.yaml \
  --var concept_file=/abs/concept.md --var context_dir=/abs/context --var tempo=standard
# read 07-stakeholder-brief.md, then:
mzt resolve spec-forge <sheet> accept
```

**Existing project.** Take full inventory before designing. Run
`examples/engineering/project-roadmap.yaml` with `venue_context_dir` pointing
at everything you know that the code cannot tell it (stakeholders, customers,
constraints, team, what to stop doing). Feed its roadmap and atlas to
`spec-forge` as the context directory and set `project_root`.

## 3. Casting and review

For each part decide who builds, who tests, who reviews, and how long they
get. Most parts need a team; one worker can serve several parts at once.

**Split by context, not by problem type.** On a frontier model, one
long-running agent that holds a whole part in one context usually beats a
relay of recon → plan → work sheets that lose context at each handoff. Give
it hours. Use separate sheets where a separate context is the point: tests
written blind to the implementation, reviewers on other model families,
independent research paths, parallel parts, deterministic checks. When it is
unclear how to break a part into sheets, cast a persistent agent's lifecycle
to loop on it through its cadenza directory (see 4).

Cast in this order: existing persistent agents whose role fits
(`plugins/marianne/agent-scores/roster.yaml`; `marianne-agents census` shows
who is installed), then capability classes over existing profiles. Never a
new profile for a new subject, model or timeout.

Choose the review method per part, usually a mix: deterministic (tests, lint,
types, schema), semantic review, adversarial review, fuzzing, human review.
For code the default is TDD by a sheet or agent separate from the builder,
coverage above 90% and clean static analysis, unless the composer says
otherwise.

**Review is repair.** Every review feeds a bounded repair loop and a
re-review. Triage findings by the cross-section of model families:

- **Blocker** — CRITICAL or HIGH and raised by two or more families, or a
  single-family finding you confirmed in the artifact. Fixed before release.
- **Deferred** — real, but not blocking the first usable version at this
  tempo. Recorded in a `deferred.md` the polish phase consumes.
- **Discarded** — a single-family finding nobody can confirm. One line why.

Mutual finds across families are evidence; outliers are mostly one model's
blind spot. Do not try to fix everything before people can use it.

## 4. Scores and concerts

Write the orchestra with Marianne, not by hand at the podium. Commission
`design-to-orchestra` on the approved specs. It surveys the repertoire,
casts each part, writes one build score per part plus an integration score
and a fleet, and gates every generated score before it hands over `RUN.md`:
`mzt validate` with no errors or warnings (V311, an instrument this machine
lacks, is reported but tolerated), the composing release checker with a
lock, a fleet whose members all exist and all passed, and a verdict across
two model families. `RUN.md` re-verifies each lock at start, so a score
edited after review refuses to start:

```bash
mzt run examples/engineering/design-to-orchestra.yaml \
  --var specs_dir=$HOME/workspaces/spec-forge/specs \
  --var project_root=/abs/project --var tempo=standard
```

Whoever writes scores reads the repertoire first: `examples/README.md` and
the category READMEs, `scores/rosetta-corpus/INDEX.md` and the full file of
each selected pattern, the primitives in the corpus's "Real Dialect" section
and `docs/configuration-reference.md`, and the technique library in
`plugins/marianne/techniques/`. Research existing skills on the web that could
become techniques when a part needs a method Marianne does not have.

Use the primitives. A score with no loop, no fan-out, no independent review
and no technique is a script, not an orchestra:

| Need | Primitive |
|---|---|
| Repair until good, but bounded | `sheet.loops` span with `until: file(...)` and `max_iterations` from tempo |
| Independent voices | fan-out with one alias, `select: [spread, balance]` |
| Skip empty slots or finished work at no cost | `skip_when` per stage |
| A human decision mid-score | `triggers: {N: {on_success: [escalate: ...]}}`, then `mzt resolve` |
| Parts in parallel, integration after | a `type: fleet` with dependent groups |
| Keep going until done | `triggers` → `concert` self-chain, `concert.max_chain_depth` |
| Deterministic gate | `instrument: cli` with `per_sheet_fallbacks: {N: []}` |
| A person on the work | `techniques` (mateship, coordination, specialist) on persistent agents |

Every work, review and research sheet gets the specs, designs and integration
plans as `prelude` items with `required: true`.

Gates fit the medium. Code gets tests, coverage and static analysis. A
document gets deterministic checks on what it states (figures that agree
across sections, limits met, required sections present, every claim traced
to a source) plus reviewers who read it as its audience will. Never pass a
document through a code gate it cannot fail.

**Budgets are generous.** A sheet that runs a full test suite gets an hour or
more; a long build sheet gets several hours; a persistent agent's work cycle
on an unclear part can run a day or more. Enable `stale_detection` with
`idle_timeout_seconds` of at least 1800 so silent test runs survive and a hung
sheet is caught within half an hour instead of stalling for hours. Count queue
time inside any wall clock. A cap copied from an old score is not a budget.

**Agent lifecycles on a part.** Put the part's spec, integration doc and
acceptance checks in the agent's cadenza directory, then engage:

```bash
marianne-agents engage AGENT --purpose PART --inventory INVENTORY --runs-dir RUNS
```

Their memory and mateship let them pick up loose work beside their peers.

## 5. Performance

Start only when every score is validated and reviewed, every lifecycle is
engaged with its cadenza in place, and `RUN.md` names the commands. Then run
everything resource limits allow at once and let the conductor order it.
Do not use clone conductors to get around limits; clones are for development.

Your job now is to keep it moving:

- **Watch with a sentinel, not by polling.** Arm one monitor on job states
  and on a silence threshold (no new artifact or transcript output for 30
  minutes on a running sheet). A FAILED, FERMATA or silent sheet wakes you.
  Re-arm it when it expires.
- **Classify a failure before repairing.** Venue (instrument, quota, path,
  environment) goes to the venue owner; product goes back to its part's
  repair loop. Most early failures are venue.
- **Two failed successors on one outcome stop the repetition.** Change the
  premise, the method or the casting.
- **Adapt the orchestra to new requests** with `mzt modify` or a new part
  through the same two scores; never by hand-editing a running prompt.

Put something in people's hands early. The prototype cut of each part and
the integration score's `handoff.md` exist so stakeholders touch the work
while the rest is still being built. Their feedback is input, not an
interruption.

An orchestra is not meant to play for long. When every score has finished,
or looping lifecycles report their part complete, present the result to the
stakeholders with the evidence and the polish backlog, and move to polish.

## 6. Polish

Run continuous quality and issue solving against the delivered result:
`examples/engineering/quality-continuous.yaml`, and
`issue-triage.yaml` → `issue-solver.yaml` for the backlog. Seed them with the
`deferred.md` files and the integration `polish-backlog.md`. Every new ask
from users or stakeholders goes back through movements 1-5 at the size it
deserves: a sentence of intake and one agent for a small fix, the full route
for a new capability.

## Terminal conditions

A commission is done when:

1. every part's acceptance checks pass on the integrated result;
2. the integration score's review accepted it, by families other than the
   builders';
3. the people it was for have used it;
4. the deferred findings are recorded where the polish phase reads them.

Report what is done and what is deferred separately. Do not hold delivery for
deferred findings, and do not call deferred findings fixed.

## Where commissions lose days

| Symptom | What went wrong | Move |
|---|---|---|
| Workers start before specs exist | breakdown skipped | `spec-forge` first |
| A plan with no loops, fan-out, review or techniques | primitives unused | `design-to-orchestra`; the table in 4 |
| Sheets time out mid-work, successors follow | under-sized budgets | hours, idle ≥ 1800 s, queue inside the wall |
| A job stalls for hours unnoticed | no sentinel, or it expired | one armed monitor with a silence threshold |
| Every finding becomes a repair | no triage | family cross-section; defer the rest |
| Lanes read for an hour before acting | orientation bloat | the commission is the context |
| Venue errors reworked as product | no classification | classify before repairing |
| Parts built in sequence for no reason | waves not used | parallel against contracts |
| Nobody sees anything until the end | no prototype cut | hand over the first usable cut early |
