# Figure 6 source traceability

## Figure identity

**Active number:** Figure 6  
**Title:** Prespecified regime map across the tested Model B parameter domain  
**Former location:** top row of the former composite Figure 6  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen source tables

| Source table | Frozen role | Rows | SHA-256 |
|---|---|---:|---|
| `generality_screen_summary.csv` | Stage A/B1 setting specifications, 95% intervals, and frozen regime assignments | 65 | `b1bc2824bbbe25109f7a8fde34ac8165a032785d91a22514b9b5203c8356c1e1` |
| `generality_screen_replicates.csv` | Supporting independent replicate records used to produce the frozen summaries | 244 | `7fa270f81c45c52103338c363b430c9aea99d76aea31d21da9dff9372e2569b4` |

The rendered panels read only the frozen summary table; the replicate table is retained as the provenance source for the displayed classifications and independent sample sizes. Both hashes match the frozen manifest.

## Panel-to-source mapping

| Panel | Displayed content | Frozen selection | Independent replicate count |
|---|---|---|---:|
| (a) | Stage A settings with $\beta/\Theta=0.5$ | `stage == A`, ratio 0.5 | 4 per setting |
| (b) | Stage A settings at the default $\beta/\Theta\approx1.7$ | `stage == A`, default ratio | 4 per setting |
| (c) | Stage A settings with $\beta/\Theta=2.5$ | `stage == A`, ratio 2.5 | 4 per setting |
| (d) | Regime-count composition of Stage A and Stage B1 | Frozen `regime` field | Stage A: 4 per setting; Stage B1: 3 per setting |

## Frozen regime record

- Stage A: `8` null, `0` syntactic-only, `1` boundary/uncertain, `19` viability-relevant, and `4` strong-adaptation settings; `23/32` are R2/R3.
- Stage B1: `2` null, `8` syntactic-only, `0` boundary/uncertain, `5` viability-relevant, and `1` strong-adaptation setting; `6/16` are R2/R3.
- Classification thresholds: `0.01` bit corrected information, `0.25` fitness unit value of information, and `1.0` fitness unit sustained adaptive gain.
- Intervals: 95% replicate bootstrap, `2,000` resamples.
- Boundary settings are not positive evidence.

## Visual-production record

- Figure 6 is a standalone full-width figure, removing the density of the former three-row composite.
- Panels are labeled `(a)`–`(d)` and all axes remain separated from panel labels.
- Regimes use accessible colour and distinct marker shapes; interpretation does not depend on colour alone.
- No bottom-note block is present; the staged/non-factorial and non-universality limitations are in `FIGURE_6_FINAL_CAPTION.md`.

## Final outputs

`FIGURE_6_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_publication_figures.py`.
