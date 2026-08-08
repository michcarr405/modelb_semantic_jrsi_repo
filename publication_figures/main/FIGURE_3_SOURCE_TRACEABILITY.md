# Figure 3 source traceability

## Figure identity

**Active number:** Figure 3  
**Title:** Corrected information hierarchy across parental-composition coupling  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen source tables

| Source table | Frozen role | Rows | SHA-256 |
|---|---|---:|---|
| `core_information_replicates.csv` | Replicate-level total, positional, and corrected position-conditioned information | 400 | `4c4f9810188d206884cdb9aff95c7b5e1fcfa2da3adc79c83e878ba68b13b7a8` |
| `core_semantic_replicates.csv` | Replicate-level future-fitness effect of the constant endpoint | 400 | `d8096c9e04f657337485dd2e1ffced4d04412ed2150c1319c52095e6f7c9bc69` |
| `core_inference_records.csv` | Frozen complete-block bootstrap intervals for panel (d) | 130 | `0bc30784704e210ad2da076c344b1a244bfbe3b1415b1ab3a84c5b7f454a16e5` |

Every hash matches `results/result_freeze/FILE_MANIFEST_SHA256.csv`.

## Panel-to-source mapping

| Panel | Displayed quantity | Source field or frozen record | Filtering | Statistical unit | Display transformation |
|---|---|---|---|---|---|
| (a) | Total motif–local-state association, $I(M;Z)$ | `total_information` | Both regimes; $p=0.1,\ldots,1.0$ | Independently evolved population | Raw points plus arithmetic mean |
| (b) | Motif–position association, $I(M;S)$ | `positional_information` | Both regimes; full $p$ sweep | Independently evolved population | Raw points plus arithmetic mean |
| (c) | Corrected position-conditioned sequence-specific information | `corrected_conditional_information` | Both regimes; full $p$ sweep | Independently evolved population | Raw points plus arithmetic mean |
| (d) | Value of information, $\Delta V$ | `value_of_information`; frozen `mean_value_of_information` interval | Both regimes; full $p$ sweep | Independently evolved population | Raw points, frozen mean, and frozen 95% complete-block bootstrap interval |

## Statistical-display record

- Independent replicate count: `n=20` per regime and $p$ value.
- Panel (d) interval: complete-block bootstrap, `2,000` resamples.
- Point offsets: deterministic display jitter only.
- Units: bits for information quantities; model-fitness units for $\Delta V$.
- Inferential statistics: no recalculation.

## Visual-production record

- Panel labels: lower-case letters in brackets, `(a)`–`(d)`.
- Colour is redundant with marker shape, fill, and line style.
- No bottom-note block is present; statistical details are carried by `FIGURE_3_FINAL_CAPTION.md`.
- Total association, positional association, corrected sequence-specific information, and future-fitness effect remain visually distinct.

## Final outputs

`FIGURE_3_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_publication_figures.py`.
