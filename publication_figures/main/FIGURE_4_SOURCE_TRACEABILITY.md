# Figure 4 source traceability

## Figure identity

**Active number:** Figure 4  
**Title:** Replicate-specific information–fitness frontiers and semantic estimates  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen source tables

| Source table | Frozen role | Rows | SHA-256 |
|---|---|---:|---|
| `core_frontier_points.csv` | Discrete intervention points and cumulative upper frontiers | 13,600 | `d301e23271ca087481fbfa1f3d8b4d909f58f0f78194667cc258e0f10bc7a251` |
| `core_semantic_replicates.csv` | Actual viability, target, semantic estimate, endpoint recovery, and censoring | 400 | `d8096c9e04f657337485dd2e1ffced4d04412ed2150c1319c52095e6f7c9bc69` |
| `core_inference_records.csv` | Frozen bootstrap intervals and target-reaching records | 130 | `0bc30784704e210ad2da076c344b1a244bfbe3b1415b1ab3a84c5b7f454a16e5` |

Every hash matches the frozen result manifest.

## Panel-to-source mapping

| Panel | Displayed content | Frozen selection | Statistical unit | Display transformation |
|---|---|---|---|---|
| (a) | Sequence-selective discrete intervention points and cumulative upper frontier | `selective_p1.0_r00` | One independently evolved baseline population | Sort by directly measured retained information; step connection through frozen frontier coordinates only |
| (b) | Sequence-agnostic discrete intervention points and cumulative upper frontier | `control_p1.0_r00` | One independently evolved baseline population | Same graphical grammar and scale as panel (a) |
| (c) | Value of information at $p=1.0$ | All 20 baseline populations per regime | Independently evolved baseline population | Raw points plus frozen mean and 95% complete-block bootstrap interval |
| (d) | Replicate-specific semantic estimate at $p=1.0$ | All 20 baseline populations per regime | Independently evolved baseline population | Raw points plus frozen median among target-reaching populations and 95% complete-block bootstrap interval |

## Frontier and endpoint record

- Retained-information coordinate: $I(g(M);Z\mid S)$.
- Unique maps: `34` per baseline population.
- Nested continuations: `2` per map.
- Intervention horizon: `36` generations.
- Target: strict `1%` viability-loss target.
- Endpoints: constant and identity included.
- Target reaching at $p=1.0$: `20/20` in each regime.
- Right censoring at $p=1.0$: `0` in each regime.
- Native sequence-selective target: identity endpoint required.
- Smoothing/interpolation: none.
- Representative selection: archived replicate `r00`, selected by index rather than outcome.

## Visual-production record

- Panel labels: `(a)`–`(d)`; each quantitative axis has its own label.
- Intervention family is encoded by marker shape and colour.
- Frontier, actual endpoint, target, and target-reaching coordinate are encoded by distinct line styles as well as colour.
- No bottom-note block is present; all statistical and censoring details are in `FIGURE_4_FINAL_CAPTION.md`.
- No semantic-compression implication is permitted.

## Final outputs

`FIGURE_4_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_publication_figures.py`.
