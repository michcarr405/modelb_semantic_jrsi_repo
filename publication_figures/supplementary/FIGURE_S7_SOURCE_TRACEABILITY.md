# Figure S7 source traceability

## Figure identity

**Active number:** Figure S7  
**Title:** Raw nondefault confirmatory endpoint and replicate records  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen sources

| Source table | Role | Rows | SHA-256 |
|---|---|---:|---|
| `generality_confirmatory_replicates.csv` | Plotted raw endpoint, value-of-information, semantic, identity, target, and censoring records | 24 | `0c5f967225f319ad7b9b371e045b39dce9f41303ac4cfc35368ca30187cf40c6` |
| `generality_confirmatory_summary.csv` | Caption-only design-ID mapping and frozen positive/non-positive designation | 3 | `4c3fa39d27e2239fb481306894e4b8c5d5b7a64102ea6f158d87d2b18f870bef` |

## Panel-to-source mapping

| Panel | Displayed records |
|---|---|
| (a) | D0 constant, target, actual, and identity viability |
| (b) | D1 constant, target, actual, and identity viability |
| (c) | D2 constant, target, actual, and identity viability |
| (d) | Raw `value_of_information` for D0–D2 |
| (e) | Raw `semantic_information` paired with `identity_information` |
| (f) | Counts from `target_reached`, `censoring`, `identity_information_recovered`, and `identity_viability_recovered` |

## Confirmatory record

- D0: `A_high_2`, viability-relevant representative, eight populations.
- D1: `B2_reward3`, strong-adaptation representative, eight populations.
- D2: `A_low_3`, boundary representative, eight populations.
- Unique maps: 34 per population.
- Nested continuations: two per map; 70 continuation rows per population.
- Intervention horizon: 36 generations.
- Target rule: strict 1% recovery target.
- Target reached: 24/24.
- Right-censored: 0/24.
- Exact identity information and identity viability recovery: 24/24.
- Semantic estimate equals identity information: D0 8/8, D1 8/8, D2 6/8.

## Provenance boundary

`generality_confirmatory_replicates.csv` does not contain map-level retained-information/viability coordinates. Accordingly, no unverified full frontier shape is reconstructed. Panels (a)–(c) show only frozen endpoint and target records, and panels (d)–(f) show raw replicate summaries and audits.

## Visual-production record

- Lower-case bracketed panel labels `(a)`–`(f)` are present.
- Endpoint types and representative classes are redundantly encoded by marker shape and colour.
- No footer note is present; nested-design and confirmation status are transferred to `FIGURE_S7_FINAL_CAPTION.md`.

## Final outputs

`FIGURE_S7_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_supplementary_figures.py`.
