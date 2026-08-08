# Figure 8 source traceability

## Figure identity

**Active number:** Figure 8  
**Title:** Full semantic confirmations and protocol sensitivity  
**Former location:** bottom row of the former composite Figure 6  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen source tables

| Source table | Frozen role | Rows | SHA-256 |
|---|---|---:|---|
| `core_semantic_replicates.csv` | Archived default confirmation replicates | 400 | `d8096c9e04f657337485dd2e1ffced4d04412ed2150c1319c52095e6f7c9bc69` |
| `core_inference_records.csv` | Archived default complete-block bootstrap interval and target records | 130 | `0bc30784704e210ad2da076c344b1a244bfbe3b1415b1ab3a84c5b7f454a16e5` |
| `generality_confirmatory_replicates.csv` | Three nondefault full-pipeline confirmation replicate sets | 24 | `0c5f967225f319ad7b9b371e045b39dce9f41303ac4cfc35368ca30187cf40c6` |
| `generality_confirmatory_summary.csv` | Nondefault confirmation means, intervals, endpoint checks, and positivity decisions | 3 | `4c3fa39d27e2239fb481306894e4b8c5d5b7a64102ea6f158d87d2b18f870bef` |
| `generality_protocol_summary.csv` | Evolution-duration and intervention-horizon sensitivity | 12 | `fd74eac9a6b2c2c45fb0381029772e96992ba48e46a74e38c892d16abbc9286c` |

Every hash matches the frozen result manifest.

## Panel-to-source mapping

| Panel | Displayed content | Frozen source | Independent replicate count |
|---|---|---|---:|
| (a) | Default plus `A_high_2`, `B2_reward3`, and `A_low_3` full confirmations | Core semantic/inference tables and confirmatory replicate/summary tables | Default: 20; each nondefault: 8 |
| (b) | Default-anchor evolution-duration and horizon sensitivity | `generality_protocol_summary.csv`, `B2_default` suffix | 4 per setting |
| (c) | Nearest-boundary evolution-duration and horizon sensitivity | `generality_protocol_summary.csv`, `A_low_3` suffix | 4 per setting |

## Frozen confirmation and protocol record

- Positivity threshold: `0.25` model-fitness unit.
- `A_high_2`: positive R2 confirmation.
- `B2_reward3`: positive R3 confirmation.
- `A_low_3`: boundary confirmation not positive.
- Identity information and viability: exact in all 24 nondefault populations and all 20 archived default populations.
- Target-reaching fraction: `1.0`; right-censored cases: `0`.
- Full-pipeline map count: `34`; nested continuations: `2`; primary horizon: `36` generations; strict target: `1%`.
- Protocol intervals: 95% replicate bootstrap, `2,000` resamples.
- Default protocol settings remain R3; nearest-boundary settings alternate between R1 and boundary/uncertain.

## Visual-production record

- Figure 8 is a standalone figure with one full-width confirmation panel and two separate protocol panels.
- Panels are labeled `(a)`–`(c)`.
- Raw replicates and interval summaries remain visible without crowding.
- No bottom-note block is present; endpoint, target, censoring, and protocol details are in `FIGURE_8_FINAL_CAPTION.md`.

## Final outputs

`FIGURE_8_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_publication_figures.py`.
