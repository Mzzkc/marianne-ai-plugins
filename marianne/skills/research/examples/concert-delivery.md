# Concrete research → consumer concert

Generate local wrappers under SCORES, artifacts under disjoint WORKSPACES. Run
this from the research resource directory after freezing its roster:

```bash
python3 scripts/concert.py wrapper \
  --parent-score /absolute/research/scores/research-b.yaml \
  --parent-workspace /absolute/WORKSPACES/request-b \
  --child-workspace /absolute/WORKSPACES/request-b-consumer \
  --input-dir /absolute/context \
  --out-dir /absolute/SCORES/request-b-chain \
  --resources /absolute/research
mzt run /absolute/SCORES/request-b-chain/parent.yaml --fresh
```

The generated parent stores input and resource paths relative to its workspace
and a frozen roster beside its YAML. Home paths in native path fields use `~/`. Its final CLI movement first
runs `research.py deliver`. Only exit 0 allows `concert.py bind` to write
`/absolute/SCORES/request-b-chain/consumer.yaml` using the ACTUAL current run ID.
Then native `on_success` resolves `consumer.yaml` beside the parent score and
submits that exact child path with `fresh: true`
and an explicit disjoint `job_workspace`. No arbitrary hook `--var` is assumed:
current manager builds `JobRequest(config_path, workspace, fresh, chain_depth)`.
The child YAML owns all input bindings. A run_job receipt proves submission only.

The wrapper example fixes the downstream consumer to `codex-cli`. Research
`roster.json` does not control this role. For a different local binding, use the
existing `concert.consumer(..., profile="your-qualified-profile")` Python argument
when generating a consumer, or adapt the generated consumer YAML before running
it. The wrapper CLI currently does not expose that argument; an automatic hook
from the unchanged wrapper uses Codex. Qualify the downstream route separately.

The consumer first runs deterministic `verify-delivery` against the expected
parent run ID, complete status, original manifest, exact original directory and
current result/report digests. Its AI stage requires the complete original
snapshot directory, current run receipt, and complete flat delivery directory.
It writes `consumer.md` addressing original constraints and remaining uncertainty.
This is explicitly selected synthesis for lab reviews, or an explanatory downstream
consumer for search. It has no authority to modify applications/adopt packages.

For a different downstream score, reuse these explicit required cadenzas and
identity gate in a locally generated wrapper. Do not rely on inherited CWD,
a global input folder, summary-only context or parent success as child completion.
Keep wrappers per request; do not overwrite an active wrapper or reuse the parent
workspace while its child is still consuming it. Historical archives and lanes
are not included in the flat delivery bucket.

Provider-free tests execute the actual deterministic gates, load the generated
native parent/child YAML, render the consumer with actual synthesized BENIGN
fixture bytes, and compare native source hashes to the parent original manifest.
No child or provider job is launched by implementation tests.
