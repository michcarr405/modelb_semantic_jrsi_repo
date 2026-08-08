# Figure 7 source traceability

## Figure identity

**Active number:** Figure 7  
**Title:** Structural-family support within the tested Model B design domain  
**Former location:** middle row of the former composite Figure 6  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen source tables

| Source table | Frozen role | Rows | SHA-256 |
|---|---|---:|---|
| `generality_screen_replicates.csv` | Raw Stage B2 independent replicate values | 244 | `7fa270f81c45c52103338c363b430c9aea99d76aea31d21da9dff9372e2569b4` |
| `generality_screen_summary.csv` | Stage B2 means, 95% intervals, and frozen regime assignments | 65 | `b1bc2824bbbe25109f7a8fde34ac8165a032785d91a22514b9b5203c8356c1e1` |

Every hash matches the frozen result manifest.

## Panel-to-source mapping

| Panel | Stage B2 family | Displayed settings | Independent replicate count |
|---|---|---|---:|
| (a) | `window` | Strides 2, 5, and 7 | 4 per setting |
| (b) | `position` | 2/8 segments, reversed order, and non-heritable boundary jitter | 4 per setting |
| (c) | `metabolite` | Matched 3- and 6-local-state variants | 4 per setting |
| (d) | `fitness` | Reward, penalty-ratio, floor, and fraction-normalized variants | 4 per setting |

## Statistical-display record

- Small grey points: raw independent populations.
- Large regime symbol: frozen mean value of information.
- Horizontal interval: frozen 95% replicate-bootstrap interval, `2,000` resamples.
- Dashed vertical line: prespecified positivity threshold, `0.25` model-fitness unit.
- Dotted vertical line: frozen default-anchor mean.
- Structural-family support: `4/4` families contain R2/R3 settings.
- Fraction-normalized fitness: frozen R1 syntactic-only limitation.

## Visual-production record

- Figure 7 is a standalone full-width figure, allowing complete setting labels and visible raw replicates.
- Panels are labeled `(a)`–`(d)`.
- Regimes use colour-plus-shape redundancy and remain interpretable in grayscale proofing.
- No bottom-note block is present; statistical and limitation text is in `FIGURE_7_FINAL_CAPTION.md`.

## Final outputs

`FIGURE_7_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_publication_figures.py`.
