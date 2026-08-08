# Figure S6 source traceability

## Figure identity

**Active number:** Figure S6  
**Title:** Complete evolution-duration and intervention-horizon sensitivity  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen source

| Source table | Role | Rows | SHA-256 |
|---|---|---:|---|
| `generality_protocol_summary.csv` | Frozen means, 95% intervals, regime assignments, and identity-endpoint status for Stage C protocol variants | 12 | `fd74eac9a6b2c2c45fb0381029772e96992ba48e46a74e38c892d16abbc9286c` |

## Panel-to-source mapping

| Panel | Representative | Metric |
|---|---|---|
| (a) | `B2_default` | Corrected information |
| (b) | `A_low_3` | Corrected information |
| (c) | `B2_default` | Value of information |
| (d) | `A_low_3` | Value of information |
| (e) | `B2_default` | Adaptive gain |
| (f) | `A_low_3` | Adaptive gain |

## Protocol record

- Evolution durations: 100, 150, and 250 generations.
- Intervention horizons: 24, 36, and 60 generations.
- Independent sample size: four populations per protocol setting.
- Interval method: frozen 95% replicate-bootstrap interval from 2,000 resamples.
- Identity endpoint: exact in all 12 settings.
- Default anchor: strong-adaptation classification in 6/6 protocol variants.
- Nearest-boundary setting: four boundary/uncertain and two syntactic-only classifications.

## Display record

- Frozen means and intervals are plotted directly; no interval is recomputed.
- Lower-case bracketed panel labels `(a)`–`(f)` are present.
- Regime is encoded by colour and marker shape.
- Shared protocol-axis labels are shown on the bottom row to prevent crowding.
- No footer note is present; protocol and classification detail is transferred to `FIGURE_S6_FINAL_CAPTION.md`.

## Final outputs

`FIGURE_S6_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_supplementary_figures.py`.
