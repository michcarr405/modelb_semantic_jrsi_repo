# Figure S2 source traceability

## Figure identity

**Active number:** Figure S2  
**Title:** Complete inferential, target-attainment, and censoring record  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen source

| Source table | Role | Rows | SHA-256 |
|---|---|---:|---|
| `core_inference_records.csv` | Frozen complete-block bootstrap intervals, replicate-level permutation tests, adjusted values, target counts, and censoring counts | 130 | `0bc30784704e210ad2da076c344b1a244bfbe3b1415b1ab3a84c5b7f454a16e5` |

## Panel-to-source mapping

| Panel | Record filter | Frozen fields displayed | Transformation |
|---|---|---|---|
| (a) | `record_type=block_bootstrap_interval`, `metric=mean_value_of_information` | `estimate`, `lower`, `upper` | Ordered by condition and $p$ |
| (b) | `record_type=block_bootstrap_interval`, `metric=median_semantic_information_among_reached` | `estimate`, `lower`, `upper` | Ordered by condition and $p$ |
| (c) | `record_type=target_reach_count` | `n_target_reached`, `n_right_censored` | Categorical count matrix |
| (d) | `record_type=replicate_permutation`, corrected-information metric | `observed_difference` | Ordered by $p$ |
| (e) | `record_type=replicate_permutation`, value-of-information metric | `observed_difference` | Ordered by $p$ |
| (f) | `record_type=replicate_permutation`, semantic-information metric | `observed_difference` | Ordered by $p$ |

## Inferential record

- Independent unit: independently evolved baseline population.
- Independent sample size: 20 per regime and $p$.
- Bootstrap: 2,000 complete-block resamples; 95% intervals.
- Permutation inference: 9,999 two-sided permutations.
- Multiplicity: Benjamini–Hochberg correction across ten $p$ values separately by metric.
- Adjusted results: every displayed metric–$p$ comparison has $q=0.0001$.
- Target reaching: 20/20 in every regime–$p$ cell.
- Right censoring: 0 in every regime–$p$ cell.

## Visual-production record

- Lower-case bracketed panel labels `(a)`–`(f)` are present.
- Complete count labels remain inside the figure boundary.
- No pooled intervention points are displayed as independent observations.
- No footer note is present; inferential detail is transferred to `FIGURE_S2_FINAL_CAPTION.md`.

## Final outputs

`FIGURE_S2_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_supplementary_figures.py`.
