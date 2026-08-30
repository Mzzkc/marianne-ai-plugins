# Modern persistent agents

Use this reference whenever Marianne work could benefit from a person who
returns, remembers, develops judgment, or maintains relationships across
engagements. Modern agents are composed people; they are not model aliases and
they are not the legacy prompt helpers in `plugins/marianne/agents/`.

## Decide before casting

1. Reuse an existing persistent agent when the identity, relationships, and
   accumulated judgment fit the work. Read the registry before selecting.
2. Construct a new persistent agent only for a durable recurring gap whose
   future learning has value. Give it a seed, personal data authority,
   techniques, lifecycle scores, and a discoverable registry entry.
3. Use an ephemeral worker for bounded work with no useful future identity or
   memory. Do not manufacture persistence around a disposable commission.
4. A short engagement for a persistent person may defer consolidation,
   reflection, and resurrection, but it must record visible lifecycle debt.
   Deferred integration is recovery debt, not completion.

Never select or generalize from a `musician-XXXX` profile. Those profiles are
DJ-project instruments, not Marianne's reusable agent cast.

## What composes a person

The portable seed carries the core that may travel: semantic name, voice,
focus, role, values, relationships, growth axes, and technique declarations.
On a box, the agent owns exactly one writable data tree:

```text
~/.marianne/agents/<agent>/
├── identity.md                         L1: core self
├── profile.yaml                        L2: structured self and lifecycle state
├── recent.md                           L3: current lived memory
├── growth.md                           L4: development and reflection
├── archive/                            older personal memory
├── cadenzas/personal/active/           four-file personal coordination surface
├── scores/                             installed engagement scores
├── workspaces/                         per-shape run state and artifacts
└── .marianne/                          baselines, debt, conflicts, and receipts
```

`~/.marianne/agents` is the public default, not a universal physical location.
A box may point it at another canonical root, such as a Projects-level AGENTS
registry. Follow the resolved path and never create a second writable copy.

The agent has final semantic authority over all four identity/memory layers.
The compiler may initialize missing data, three-way-merge an unchanged seed,
or propose a conflict. A compiler, composer, or conductor must never silently
replace lived divergence. Only an agent-authored adjudication can close seed
conflict debt.

Techniques are composable methods and capability surfaces. Roles describe
responsibility. Cadenzas coordinate a cohort or engagement. Instruments are
phase performers. Scores arrange all of them over time. None of those is the
agent's identity.

## Construction and portable updates

The plugin ships generated packages under `agent-scores/`: one seed and three
scores per released persistent agent. It includes Keystone. Runtime remains a
local cycle-zero seed until lived development justifies propagation.

Before changing box-local data, preview installation:

```bash
marianne-agents install-package "${CLAUDE_PLUGIN_ROOT}/agent-scores" \
  --techniques-source "${CLAUDE_PLUGIN_ROOT}/techniques" \
  --dry-run
```

With explicit authority, rerun without `--dry-run`. Installation reconciles
seeds, adds the personal cadenza and ready-to-bind scores, and synchronizes
technique documents. It updates a managed asset only when the installed bytes still
match their prior baseline; local divergence is preserved as explicit conflict
debt. The roster binds the seed version and digest of every packaged seed,
cadenza, and score; installation rejects a torn or modified package before
touching identity. Supplying custom `--agents-dir` and `--techniques-dir`
values also localizes every installed score to those resolved box paths and
creates each score's workspace parent. If `marianne-agents` is unavailable,
the compiler containing this agent lifecycle release is not installed—do not
compensate by hand-copying over identity or memory.

Installed `agents/<agent>/scores/` files are distribution-managed entry-point
templates attached to that person, not the canonical source of a newly authored
campaign. On this box, keep authored score sources and their design/runbook
context under `/home/emzi/Projects/SCORES`, and keep bound run scores,
workspaces, and artifacts under `/home/emzi/Projects/WORSKPACES`. Other boxes
may override those roots through their own instructions. Never turn a run
workspace snapshot into canonical score or memory authority merely because it
is newer.

For a single seed, use `marianne-agents reconcile SEED --dry-run` before the
authorized reconciliation. Close a pending seed conflict only with an
agent-authored resolution document and `marianne-agents acknowledge`; the
acknowledgement command records authority and never edits L1-L4 itself.

Use `marianne-agents census` for a read-only memory census. Classify results as
canonical, symlink aliases, workspace snapshots, or unknown/partial trees.
Never merge memory merely because two paths contain the same agent name.

## Three engagement scores

- `full-lifecycle.yaml`: ordinary durable work through all twelve phases.
- `targeted-work.yaml`: bounded recon/plan/work/integration/inspect/AAR with an
  immediate recent-memory update and explicit pending lifecycle debt.
- `lifecycle-integration.yaml`: processes pending engagements and seed
  conflicts through consolidation, reflection, resurrection, and later recall.

Prefer the full lifecycle. Use targeted work when timing or scope makes the
full cycle disproportionate, then schedule lifecycle integration before the
debt becomes the agent's normal condition.

The shipped targeted score captures canonical `recent.md` at recon, requires a
real before/after transition, and hashes every workspace evidence file named in
the debt. The integration score snapshots the exact pending debt and seed
conflicts before processing, requires typed later recall bound to source
evidence, verifies any agent-owned seed-resolution receipt, and closes the
canonical debt against the exact integration receipt. A plausible paragraph or
an all-zero placeholder digest is not lifecycle proof.

The lifecycle is construction → performance → AAR → consolidation → reflection
→ resurrection → demonstrated later recall. A run is not persistent merely
because it writes a file. Persistence is established when later judgment can
recall and apply grounded learning from the canonical memory tree.

## Cadenza attachment and delivery proof

Registry or cadenza membership means eligibility only. It does not attach
context. Inspect the exact score and require explicit `prelude`/`cadenzas`
entries for the intended identity, profile, recent memory, growth, techniques,
and active cadenza. Modern generated attachments use `required: true`; a
missing source must fail before performance rather than disappear as a warning.

The default personal active cadenza contains exactly:

- `01-task-board.md`
- `02-status.md`
- `03-urgent-directives.md`
- `04-handoffs.md`

A directory cadenza is immediate-files-only and reread for each sheet. Urgent
directives are controlling. Keep task claims owner-scoped, status in its
existing form, and handoffs grounded in artifact evidence.

At dispatch, current runtimes write a hash-only receipt below
`<workspace>/.marianne/context-receipts/<job>/`. The receipt binds job, sheet,
attempt, actual instrument, final prompt digest, and each delivered source,
category, resolved path, byte count, and digest. It does not copy private
memory. Use the receipt together with terminal sheet evidence to prove delivery;
a registry name or prompt claim is not proof.

## Instrument routing

Select instruments from current runtime evidence, then bind them to semantic
phase requirements. Confirm profile availability, provider, exact model,
entitlement, invocation contract, capabilities, context/output limits, and
evidence time. Keep the routing receipt.

GLM 5.3 Flash is valid only through live-verified Z.AI routing. A historical
local alias such as `opencode-ox-alpha` is not a public contract and must never
be described as a free OpenRouter route. Free or subscription-included token
metering does not erase queues, latency, quotas, rate limits, reliability, or
human waiting time. Supplementary lanes may expand capacity; they must not
become the sole load-bearing route merely because token price is zero.

Use `marianne-agents bind-score-routes INSTALLED_SCORE INVENTORY --output
BOUND_RUN_SCORE` to materialize routes and receipts in a separate run artifact.
Binding also replaces the package's `REQUIRES-LIVE-BINDING-*` workspace with a
fresh run workspace beside `BOUND_RUN_SCORE`; `--workspace` can select another
fresh engagement root. Binding refuses a workspace that already contains
`cycle-state` evidence. Put every bound score in a new engagement directory so
later runs cannot collide with earlier snapshots. Never overwrite the installed
managed score: package updates reconcile that source by hash, while route
binding is intentionally per-run evidence.
`bind-routes CONFIG ...` remains available for semantic compiler input before
compilation. Reject stale evidence, unavailable profiles, missing capabilities,
DJ-only profiles, and unverified entitlement or invocation contracts.

## Conductor acceptance

Before dispatch, record why this is reuse, new persistence, or ephemeral work;
resolve the canonical data root; preview any seed update; validate the score;
verify explicit required attachments; and inspect live routing evidence.

During and after performance, keep the runtime `job_id`, context-delivery
receipt, artifacts, terminal/validation evidence, AAR, memory before/after
digests, open lifecycle debt, and agent-authored conflict resolutions distinct.
When persistence was chosen, later run lifecycle integration and demonstrate
recall in a subsequent engagement. Without that loop, the agent was only named,
not maintained.
