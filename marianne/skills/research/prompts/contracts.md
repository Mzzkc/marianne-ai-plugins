# Research artifact contracts v1

All JSON is an object with `schema_version: 1`, `kind` below and `run_id`
copied from the current required run receipt. Never substitute a job/session ID.
Write actual JSON, without fences. IDs are stable within this run. Text must be
nonempty. Empty arrays mean none, not omitted fields. Never fabricate retrievals.
The helper checks structural joins; it cannot prove relevance or source truth.

## strategy.json — kind research-strategy

- `requirements`: [{`id`: "R1", `text`: original constraint/preference,
  `mandatory`: true/false}]. Preserve all original constraints.
- `questions`: [{`id`: "Q1", `text`: question, `requirement_ids`: ["R1"],
  `mandatory`: true/false, `evidence_goal`: what evidence settles it,
  `queries`: [suggested query/angle], `priority`: "high"/"medium"/"low"}].
- `assignments`: object keyed by exactly every configured `search-N` seat;
  values are nonempty arrays of question IDs. Every question needs an owner.
  Dynamic question count is separate from the fixed, preconfigured native seats.
- Optional `constraint_conflicts`: original constraints in conflict and how to
  ask/condition the recommendation without silently waiving either.
- B additionally requires `cross_component`: boolean,
  `integration_question_ids`: [IDs shared by at least two seats if cross-component],
  `verification_plan`: [{`question_ids`: ["Q1"], `primary_evidence`: locations,
  `different_source_type`: structural source check, `blind_spot`: plausible missed
  formulation/option class}]. This plans evidence checks, not an extra discovery loop.

## search-N.json — kind research-search

- `seat`: "search-N"; `status`: "complete"/"partial"/"no_web".
- `scope`: where/how far searched, limits, honest zero-match explanation.
- `tool_evidence`: actual search and retrieval tools used and observed failures.
- `queries`: [{`query`: actual query, `tool`: actual tool name}].
- `sources`: source objects described below; local IDs such as "S1".
- `candidates`: candidate objects below, IDs prefixed `search-N:`.
- `question_accounts`: [{`id`: assigned Q ID, `status`: "answered"/"unknown",
  `finding`: result or uncertainty, `candidate_ids`: [local candidate IDs],
  `source_ids`: [local source IDs]}]. Exactly account for your assignment;
  answered questions need evidence. Unknown questions may have empty joins.
- `rejected_alternatives`: attractive alternatives and concrete reasons/unknowns.
- `uncovered_questions`: [unresolved Q IDs].
- `reason`: required for partial/no_web. no_web has no sources/candidates and all
  accounts unknown. A malformed response must not be relabeled no_web.

A source object: {`id`, `title`, `url`: real HTTP(S) source URL,
`accessed_at`: actual ISO timestamp with timezone, `source_type`: docs/code/release/
issue/etc., `supported_claim`: exact specific claim supported by inspected source}.
Search snippets are leads. Retrieve primary evidence before claiming support.
Two models citing the same document are one source, not independent corroboration.

A candidate object: {`id`, `name`, `canonical_identity`: canonical project URL or
stable project identity used for cross-seat deduplication, `integration`:
concrete boundary/API work, `remaining_custom_work`: explicit residual effort,
`fit`: {every R ID: {`status`: "supported"/"contradicted"/"unknown", `reason`:
criterion-specific explanation, `source_ids`: [local IDs]}}}.
Supported AND contradicted fits need source evidence. Unknown fits may have none.
This is a candidate/requirement join, not a generic summary with unrelated links.

## challenge.json — kind research-challenge (B only)

`status`: complete/partial/no_web; `summary`: evidence outcome or honest no-targets
reason; `reason` required unless complete; `sources`: source objects;
`new_candidates`: candidate objects with `challenge:` IDs and ALL requirement fits;
`targets`: zero to THREE [{`id`: "T1", `question_ids`: [Q IDs], `candidate_ids`:
[discovery or new candidate IDs], `reason`: why decision-changing,
`source_type_rationale`: why these fresh evidence types,
`disposition`: "confirmed"/"corrected"/"unresolved", `source_ids`: [challenge-local
IDs], `decision_consequence`: eligibility/rank/confidence/conditional conclusion}].
Confirmed/corrected targets require sources. New candidates need a target and
same mandatory criteria as discoveries. No invented concern to justify a call.

## synthesis.json — kind research-synthesis

`status`: complete/partial; `recommendation`: reuse/adapt/build/undetermined;
`summary`; `ranking_rationale`; `strongest_alternative`; `remaining_custom_work`;
`unresolved_gaps`: array; `contradictions`: [{`claim`, `candidate_ids`: [IDs],
`source_ids`: [qualified source IDs], `resolution`: resolved evidence or explicit
conditional conclusion}]; `ranked_approaches`: ordered array of {
`id`: "A1", `candidate_ids`: [IDs of component candidates], `rationale`,
`counterarguments`, `integration`, `remaining_custom_work`, `constraint_matrix`:
{every R ID: {`status`: supported/contradicted/unknown, `reason`, `source_ids`:
[qualified IDs]}}}.

Synthesis source IDs are qualified as `search-N:S1` or `challenge:S1`; candidate
IDs are already qualified. Merge same canonical projects before ranking; one
approach may combine several projects. Unknowns remain conditional. An empty
ranking requires undetermined; do not infer build from absence of discovered
candidates. Incomplete required seat/challenge coverage MUST be partial.
B adds `challenge_effect`: eligibility/ranking/confidence/none/unresolved and
`challenge_dispositions`: {every T ID: explicit evidence-based disposition}.
The deterministic renderer adds URLs from the same validated source joins.

## Independent lab

Write review-N.md (independent supplied-context analysis) and review-N.json:
{`schema_version`:1, `kind`: "research-review", `run_id`: current receipt ID,
`review`: "review-N", `sha256`: computed SHA256 of exact review-N.md bytes}.
No forced web search or automatic implementation. Caller owns synthesis unless
an explicitly configured downstream consumer is commissioned.
