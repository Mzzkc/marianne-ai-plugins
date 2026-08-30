---
name: marianne-model-profile-refresh
description: Use when users ask to "update Marianne models", "refresh instrument profiles", "upgrade musician profiles", "audit stale model IDs", or "run the Marianne model updater".
---

# Marianne model/profile refresh

## Contract

Run one bounded model-definition update transaction. Inventory first, establish
scope, research current facts, back up every accepted target, apply updates,
commission the result, compensate on failure, and write an exact receipt. There
is no approval pause after invocation.

Treat this capability as updates only. Never install a client, provider,
plugin, model, credential, or authentication flow. Use only already-integrated
Marianne and client surfaces. Keep credentials and secret-bearing values out of
inventory, manifests, backup reports, and receipts.

Instrument/model identity is not agent identity. A profile refresh may update
verified routing facts and capability evidence; it must not edit an agent's
portable seed, L1-L4 data, lifecycle debt, relationships, or cadenza
associations. Read `${CLAUDE_PLUGIN_ROOT}/docs/ref/modern-agents.md` when the
refresh will feed a persistent-agent score.

## Modes

- **Direct-agent mode:** perform the entire contract directly with the bundled
  deterministic runtime. Route through `TASK-MAP.md` and use
  `score/run_refresh.py` when Marianne is available. The runner captures and
  restores the exact prior technique on every runner exit. Its temporary mode
  is separate from the explicit persistent `install-technique` command.
  Without Marianne, execute the same ordered stages directly and use
  `score/scripts/refreshctl.py` for deterministic inventory, authority
  validation, backup, commissioning, restore, receipt, and lock operations;
  never install Marianne to complete a refresh.
- **Marianne musician mode:** follow the bounded research or apply assignment
  injected by the score. Treat `score/technique/SKILL.md` as the score-safe
  projection and keep deterministic backup, validation, commissioning, and
  compensation under the score runtime's custody.

Apply the same authority in both modes. A targeted refresh stays within its
named provider/family and active downstream references. A broad refresh
requires a full active-state census and current official-web research before
mutation.

## Invariants

Classify every candidate before editing. Preserve pinned, frozen, retired,
historical, and unknown-authority references unless the request explicitly
names an eligible pinned or frozen target. Search matches do not grant mutation
authority.

Require an accepted manifest and transactional backup before the first target
mutation. Its protected transaction state binds recovery and manifest
digests, transaction, exact paths, resolved scope, pre-apply parent-chain
identity, and caller authority; the public index alone is not recovery
authority. Keep the observed change set identical to the accepted target
ledger. Stop on a required gate failure and perform deterministic compensation
in reverse order. Treat an unproved restore as compensation failure and
preserve recovery state.

Keep configured, parsed, integrated, and live-smoked evidence distinct. The
bounded Google adapter uses only an installed Gemini CLI and supported existing
authentication. Unsupported, unauthenticated, or failed live access remains
unverified rather than being promoted to success.

## Route

Read `TASK-MAP.md`, then load only the references named for the current mode or
decision. Run the bundled scripts instead of recreating byte-level backup,
restore, redaction, manifest, or release-lock behavior.
