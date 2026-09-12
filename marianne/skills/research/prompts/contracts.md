# Research artifact contracts v1

All JSON is an object with `schema_version: 1`, `kind` below and `run_id`
copied from the current required run receipt. Never substitute a job/session ID.
Write actual JSON, without fences. IDs are stable within this run. Text must be
nonempty. Empty arrays mean none, not omitted fields. Never fabricate retrievals.
The helper checks structural joins; it cannot prove relevance, source truth, or semantic entailment.

## Atomic citation statements

Every narrative field named below is one atomic statement or a nonempty array:
{`kind`: fact/inference/recommendation/requirement/proposal/unknown, `text`,
`source_ids`: [], `requirement_ids`: []}. Facts, inferences and recommendations
need source IDs. Unknowns and proposals have no external citations and remain
labelled. Requirement statements have no external citations and join original
requirement IDs. The helper checks source linkage, not whether a citation entails
the prose; reviewers must assess semantic grounding.

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

`finding`, candidate `identity`/`integration`/`remaining_custom_work`, candidate
fit `reason`, rejected-alternative `statement`, and partial/no_web `reason` use
atomic citation statement(s). Do not use duplicate outer source-ID fields for a
question finding or fit reason: the statement owns its citations. Supported and
contradicted fits require cited statement kinds; unknown fits require unknown
statement kinds.

- `seat`: "search-N"; `status`: "complete"/"partial"/"no_web".
- `scope`: where/how far searched, limits, honest zero-match explanation.
- `tool_evidence`: actual search and retrieval tools used and observed failures.
- `queries`: [{`query`: actual query, `tool`: actual tool name}].
- `sources`: source objects described below; local IDs such as "S1".
- `candidates`: candidate objects below, IDs prefixed `search-N:`.
- `question_accounts`: [{`id`: assigned Q ID, `status`: "answered"/"unknown",
  `finding`: atomic statement(s), `candidate_ids`: [local candidate IDs]}].
  Exactly account for your assignment. Answered findings require cited statement
  kinds; unknown findings require unknown statement kinds.
- `rejected_alternatives`: [{`statement`: atomic statement(s)}].
- `uncovered_questions`: [unresolved Q IDs].
- `reason`: required for partial/no_web. no_web has no sources/candidates and all
  accounts unknown. A malformed response must not be relabeled no_web.

A source object: {`id`, `title`, `url`: real HTTP(S) source URL,
`accessed_at`: actual ISO timestamp with timezone, `source_type`: docs/code/release/
issue/etc., `supported_claim`: exact specific claim supported by inspected source}.
Search snippets are leads. Retrieve primary evidence before claiming support.
Two models citing the same document are one source, not independent corroboration.

Small valid no-web shape (replace `RUN`, `Q1`, and `R1` with current IDs):

```json
{"schema_version":1,"kind":"research-search","run_id":"RUN","seat":"search-1","status":"no_web","scope":"No retrieval completed","tool_evidence":"Tool unavailable","queries":[],"sources":[],"candidates":[],"question_accounts":[{"id":"Q1","status":"unknown","finding":{"kind":"unknown","text":"No evidence retrieved","source_ids":[],"requirement_ids":[]},"candidate_ids":[]}],"rejected_alternatives":[],"uncovered_questions":["Q1"],"reason":{"kind":"unknown","text":"Tool unavailable","source_ids":[],"requirement_ids":[]}}
```

A candidate object: {`id`, `name`, `canonical_identity`: canonical project URL or
stable project identity used for cross-seat deduplication, `identity`: atomic
statement(s), `integration`: atomic statement(s), `remaining_custom_work`:
atomic statement(s), `fit`: {every R ID: {`status`:
"supported"/"contradicted"/"unknown", `reason`: atomic statement(s)}}}.
Supported and contradicted fits require cited statement kinds; unknown fits require
unknown statement kinds. Do not add outer `source_ids` to a question account or fit.
This is a candidate/requirement join, not a generic summary with unrelated links.

## challenge.json — kind research-challenge (B only)

`summary`, optional `reason`, and each target's `reason`,
`source_type_rationale`, and `decision_consequence` use atomic citation
statement(s). Target source IDs retain the bounded target join; the narrative
statement itself supplies inline evidence.

`status`: complete/partial/no_web; `summary`: atomic statement(s); `reason`:
atomic statement(s), required unless complete; `sources`: source objects;
`new_candidates`: candidate objects with `challenge:` IDs and ALL requirement fits;
`targets`: zero to THREE [{`id`: "T1", `question_ids`: [Q IDs], `candidate_ids`:
[discovery or new candidate IDs], `reason`: why decision-changing,
`source_type_rationale`: why these fresh evidence types,
`disposition`: "confirmed"/"corrected"/"unresolved", `source_ids`: [challenge-local
IDs], `decision_consequence`: eligibility/rank/confidence/conditional conclusion}].
Confirmed/corrected targets require sources. New candidates need a target and
same mandatory criteria as discoveries. No invented concern to justify a call.

## synthesis.json — kind research-synthesis

`summary`, `ranking_rationale`, `strongest_alternative`,
`remaining_custom_work`, every ranked-approach narrative field, every matrix
`reason`, contradiction `claim`/`resolution`, unresolved gap, and every B
`challenge_dispositions` value use atomic citation statement(s). Matrix cells
do not carry duplicate outer source IDs. Supported/contradicted matrix reasons
require cited statement kinds; unknown rows require unknown statement kinds.

`status`: complete/partial; `recommendation`: reuse/adapt/build/undetermined;
`summary`, `ranking_rationale`, `strongest_alternative`, and
`remaining_custom_work`: atomic statement(s); `unresolved_gaps`: unknown
statement(s); `contradictions`: [{`claim`: statement(s), `candidate_ids`: [IDs],
`resolution`: statement(s)}]; `ranked_approaches`: ordered array of {`id`: "A1",
`candidate_ids`: [IDs], `rationale`, `counterarguments`, `integration`, and
`remaining_custom_work`: statement(s), `constraint_matrix`: {every R ID:
{`status`: supported/contradicted/unknown, `reason`: statement(s)}}}.

Synthesis source IDs are qualified as `search-N:S1` or `challenge:S1`; candidate
IDs are already qualified. Merge same canonical projects before ranking; one
approach may combine several projects. Unknowns remain conditional. An empty
ranking requires undetermined; do not infer build from absence of discovered
candidates. Incomplete required seat/challenge coverage MUST be partial.
B adds `challenge_effect`: eligibility/ranking/confidence/none/unresolved and
`challenge_dispositions`: {every T ID: explicit evidence-based disposition}.
The deterministic renderer adds URLs from the same validated source joins.

Small valid no-evidence synthesis shape (replace `RUN` with the current ID):

```json
{"schema_version":1,"kind":"research-synthesis","run_id":"RUN","status":"partial","recommendation":"undetermined","summary":{"kind":"unknown","text":"No complete evidence","source_ids":[],"requirement_ids":[]},"ranking_rationale":{"kind":"unknown","text":"No ranking","source_ids":[],"requirement_ids":[]},"strongest_alternative":{"kind":"unknown","text":"No alternative established","source_ids":[],"requirement_ids":[]},"remaining_custom_work":{"kind":"proposal","text":"Gather evidence","source_ids":[],"requirement_ids":[]},"unresolved_gaps":[{"kind":"unknown","text":"Primary evidence missing","source_ids":[],"requirement_ids":[]}],"contradictions":[],"ranked_approaches":[]}
```

The provider-free fixtures in `tests/test_research.py` validate these no-web and
partial shapes against a current receipt and strategy; they are not live research.

## Independent lab

Write review-N.md (independent supplied-context analysis) and review-N.json:
{`schema_version`:1, `kind`: "research-review", `run_id`: current receipt ID,
`review`: "review-N", `sha256`: computed SHA256 of exact review-N.md bytes}.
No forced web search or automatic implementation. Caller owns synthesis unless
an explicitly configured downstream consumer is commissioned.
