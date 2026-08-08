# Figure S4 source traceability

## Figure identity

**Active number:** Figure S4  
**Title:** Matched seed-block distributions for causal-specificity controls  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen source

| Source table | Role | Rows | SHA-256 |
|---|---|---:|---|
| `causal_specificity_seed_blocks.csv` | Raw value-of-information records for 12 reference/control states across 20 matched seed blocks | 240 | `34af9be570d21034729692110a9fa5678f1d4768bfba66d8eaa6f4b0f6a255b8` |

## Panel-to-source mapping

| Panel | `control_or_reference` fields |
|---|---|
| (a) | `native_full_voi`, `selection_reduced`, `selection_neutral` |
| (b) | `native_full_voi`, `affinity_reassigned`, `topology_mismatch` |
| (c) | `alternative_a_native`, `alternative_a_cross_b` |
| (d) | `alternative_b_native`, `alternative_b_cross_a` |
| (e) | `alternative_native_mean`, `alternative_cross_mean` |
| (f) | `alternative_native_mean`, `temporally_unstable` |

## Statistical and display record

- Independent unit: matched independently evolved seed block.
- Number of blocks: 20.
- Grey lines preserve within-block pairing.
- Point jitter is deterministic and graphical only.
- No mean, interval, $p$ value, or $q$ value is recomputed in the supplementary figure.
- All control distributions remain above zero; attenuation is not depicted as elimination of built-in sensitivity.

## Visual-production record

- Lower-case bracketed panel labels `(a)`–`(f)` are present.
- Reference/control states are encoded by marker shape and colour.
- No footer note is present; causal-scope language is transferred to `FIGURE_S4_FINAL_CAPTION.md`.

## Final outputs

`FIGURE_S4_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_supplementary_figures.py`.
