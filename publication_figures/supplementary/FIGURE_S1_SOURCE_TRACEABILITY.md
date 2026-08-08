# Figure S1 source traceability

## Figure identity

**Active number:** Figure S1  
**Title:** Representative replicate-specific information–fitness frontiers across compositional coupling  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen sources

| Source table | Role | Rows | SHA-256 |
|---|---|---:|---|
| `core_frontier_points.csv` | Plotted discrete grouping-map coordinates, point viability, cumulative upper frontier, target, method, and endpoint type | 13,600 | `d301e23271ca087481fbfa1f3d8b4d909f58f0f78194667cc258e0f10bc7a251` |
| `core_semantic_replicates.csv` | Caption-level cross-check of map count, continuation nesting, target reaching, identity recovery, and censoring | 400 | `d8096c9e04f657337485dd2e1ffced4d04412ed2150c1319c52095e6f7c9bc69` |

## Panel-to-source mapping

| Panels | Frozen selection | Statistical unit | Display transformation |
|---|---|---|---|
| (a)–(j) | `selective_p0.1_r00` through `selective_p1.0_r00` | One independently evolved baseline population per panel | Sort by measured retained information; draw frozen cumulative upper-frontier steps only |
| (k)–(t) | `control_p0.1_r00` through `control_p1.0_r00` | One independently evolved baseline population per panel | Same graphical grammar as panels (a)–(j), with a compressed sequence-agnostic y scale |

## Frozen intervention record

- Representative selection: archived replicate `r00`, selected by index and not by outcome.
- Primary map panel: 34 unique maps per baseline population.
- Families: balanced-random, affinity-rank, contiguous-substring, constant endpoint, and identity endpoint.
- Nested continuation count: two per tested map and two for the actual continuation; 70 rows per block.
- Intervention horizon: 36 generations.
- Target rule: strict 1% recovery target.
- Interpolation, smoothing, and binning: none.
- Sequence-selective first target-reaching endpoint: identity in all 10 displayed panels.
- Sequence-agnostic first target-reaching endpoint: constant in all 10 displayed panels because $\Delta V=0$.

## Visual-production record

- Lower-case bracketed panel labels `(a)`–`(t)` are present.
- Marker shape and colour redundantly encode intervention family and endpoint.
- Line style redundantly distinguishes frontier, actual endpoint, target, and first target-reaching coordinate.
- No footer note is present; statistical and interpretive detail is transferred to `FIGURE_S1_FINAL_CAPTION.md`.
- No semantic-compression implication is permitted.

## Final outputs

`FIGURE_S1_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_supplementary_figures.py`.
