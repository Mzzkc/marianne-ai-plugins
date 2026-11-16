# Instrument catalog v2

One YAML file per model family, plus `index.yaml`. Schema: `src/marianne/core/config/catalog.py`
(`CatalogModel`, `CatalogFile`, `CatalogIndex`); every field carries its description there.

- **Tier** is capability, not price: `frontier` (Opus-class), `balanced` (Sonnet-class),
  `light` (Haiku-class), per reasoning effort (`minimal` .. `max`) or under `default`.
  `tier_status.provisional: true` means the tier was derived from v1 price-band tags and
  is a guess; do not cite it as evidence.
- **Routes** say which instrument profile (or hosting service) reaches the model, under which
  model name, and whether it is paid by `subscription`, `free`, `metered` or `local` use.
- `legacy` holds v1 fields with no v2 home (ratings, tags, task_tags, prices, notes). Nothing
  reads it at runtime.
- `index.yaml` lists every family file and `unmatched_routes`: routes a profile lists for a
  model v1 had no entry for.

Generated from `../instrument-catalog.yaml` (v1, kept because the model-profile refresh score
still reads it) with `mzt instruments catalog convert <v1.yaml> <dir>`; check a directory with
`mzt instruments catalog check <dir>`. Nothing in Marianne reads the catalog at runtime yet.

**Refreshed 16 Nov 2026 (MC1b):** claude, gpt, glm, gemini, qwen, nemotron and gemma were re-checked against vendor
pages, the local `codex`, `agy` and `opencode` model lists, and Artificial Analysis / Vals per-effort tables.
Where `tier_status.provisional` is `false`, the tier follows the rule written in `tier_status.reason`
(Intelligence Index and Terminal-Bench 4.0 per effort). Routes that `opencode models` or the OpenRouter API
no longer list are flagged in `quirks`. Other families are unchanged and still provisional.
