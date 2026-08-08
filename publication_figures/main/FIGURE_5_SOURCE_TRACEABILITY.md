# Figure 5 source traceability

## Figure identity

**Active number:** Figure 5  
**Title:** Selection dependence and mapping specificity  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen source tables

| Source table | Frozen role | Rows | SHA-256 |
|---|---|---:|---|
| `causal_specificity_seed_blocks.csv` | Matched seed-block value-of-information observations | 240 | `34af9be570d21034729692110a9fa5678f1d4768bfba66d8eaa6f4b0f6a255b8` |
| `causal_specificity_contrasts.csv` | Six frozen paired contrasts, intervals, permutation tests, and adjusted values | 6 | `d825e7f63b65b26d25efb8f58c88ae16550277bfb51931357e1d859f4bc3a442` |

Every hash matches the frozen result manifest.

## Panel-to-source mapping

| Panel | Frozen contrast or role | Paired reference | Paired control | Statistical unit |
|---|---|---|---|---|
| (a) | `full_minus_neutral` | Full selection | Neutral selection | Independently evolved seed block |
| (b) | `full_minus_reduced` | Full selection | Reduced selection | Independently evolved seed block |
| (c) | `native_minus_affinity_reassigned` | Native mapping | Complete affinity-profile reassignment | Independently evolved seed block |
| (d) | `native_minus_topology_mismatch` | Native topology | Matched topology mismatch | Independently evolved seed block |
| (e) | `alternative_native_minus_cross` | Alternative native topology | Cross-evaluated topology | Independently evolved seed block |
| (f) | `stable_minus_unstable` | Stable fixed topology | Temporally unstable topology | Independently evolved seed block |
| (g) | All six frozen contrast records | — | — | Matched independently evolved seed block |
| (h) | Nonquantitative causal-interpretation boundary | — | — | Explanatory panel; no new evidence |

## Statistical-display record

- Matched seed blocks: `n=20` per contrast.
- Paired-bootstrap resamples: `2,000`.
- Paired sign-randomization permutations: `9,999`.
- Multiplicity adjustment: Benjamini–Hochberg across six prespecified contrasts.
- Frozen adjusted value: $q=0.0001$ for every contrast.
- Nested simulation realizations and continuation seeds are excluded from independent `n`.
- Inferential statistics: no recalculation.

## Visual-production record

- Every quantitative comparison has a separate lower-case bracketed panel label `(a)`–`(f)`.
- Panel (g) displays the full forest summary with unclipped labels and a dedicated adjusted-$q$ column.
- Reference/control roles use marker shape, fill, and colour redundantly.
- Panel (h) is explicitly explanatory rather than an additional result.
- No bottom-note block is present; required interpretation and statistical information are in `FIGURE_5_FINAL_CAPTION.md`.
- All controls retain nonzero architectural sensitivity; no zero-effect claim is displayed.

## Final outputs

`FIGURE_5_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_publication_figures.py`.
