---
name: thinking-lab
description: Compatibility entry for independent supplied-context expert reviews with review-N.md outputs and caller-owned synthesis. Use the research skill's independent review mode.
---

Use [research — independent review mode](../research/SKILL.md). This preserves
independent reviews of supplied code/design/context and caller-owned synthesis;
it does not force web research or automatically begin implementation.

The bundled authoritative score is `../research/scores/thinking-lab.yaml`.
Plugin-relative `scores/prep/thinking-lab.yaml` and `scores/thinking-lab.yaml`
resolve to it. Legacy input default remains `~/workspaces/thinking-lab-input`;
pass `--var input_dir=/absolute/flat/context` for isolated requests and `--fresh`
with a dedicated workspace. Outputs remain `review-N.md`, one per configured
reviewer, now with run-bound hash sidecars. Configure the roster through research's
single generator surface. For optional automated synthesis/concert reuse, select
the documented downstream consumer explicitly; it also receives all originals.
A later collaborative build round requires separate implementation authorization.
