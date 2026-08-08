# Figure S5 source traceability

## Figure identity

**Active number:** Figure S5  
**Title:** Raw replicate distributions across the staged generality screen  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen sources

| Source table | Role | Rows | SHA-256 |
|---|---|---:|---|
| `generality_screen_replicates.csv` | Plotted raw independent-population values | 244 | `7fa270f81c45c52103338c363b430c9aea99d76aea31d21da9dff9372e2569b4` |
| `generality_screen_summary.csv` | Deterministic setting order, frozen regime key, and design metadata; no plotted y value | 65 | `b1bc2824bbbe25109f7a8fde34ac8165a032785d91a22514b9b5203c8356c1e1` |

## Panel-to-source mapping

| Panel | Raw field displayed | Threshold |
|---|---|---:|
| (a) | `corrected_information` | 0.01 bit |
| (b) | `value_of_information` | 0.25 model-fitness unit |
| (c) | `adaptive_gain` | 1.0 model-fitness unit |

## Screen record

- Stage A: 32 settings, four populations per setting, 128 records.
- Stage B1: 16 settings, three populations per setting, 48 records.
- Stage B2: 17 settings, four populations per setting, 68 records.
- Total: 65 settings and 244 independently evolved populations.
- Setting order is written to `FIGURE_S5_SETTING_ORDER.csv`.
- Setting 61 is `B2_fraction`, the fraction-normalized fitness variant, with frozen `R1_syntactic_only` classification.
- The design is staged and non-factorial; setting-level populations are not pooled as one inferential sample.

## Visual-production record

- Lower-case bracketed panel labels `(a)`–`(c)` are present.
- Stage is encoded by background band, colour, and marker shape.
- Practical thresholds are encoded by a common dashed line style.
- No footer note is present; domain limitations and sample sizes are transferred to `FIGURE_S5_FINAL_CAPTION.md`.

## Final outputs

`FIGURE_S5_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; companion key: `FIGURE_S5_SETTING_ORDER.csv`; editable production source: `produce_supplementary_figures.py`.
