# Figure S3 source traceability

## Figure identity

**Active number:** Figure S3  
**Title:** Complete replicate-level value-of-information and semantic-estimate distributions  
**Manuscript:** `rsif-2026-0516`  
**Production date:** 2026-08-02

## Frozen source

| Source table | Role | Rows | SHA-256 |
|---|---|---:|---|
| `core_semantic_replicates.csv` | Raw independent baseline-population values, endpoint recovery, target status, and censoring | 400 | `d8096c9e04f657337485dd2e1ffced4d04412ed2150c1319c52095e6f7c9bc69` |

## Panel-to-source mapping

| Panel | Field displayed | Records | Statistical unit | Transformation |
|---|---|---:|---|---|
| (a) | `value_of_information` | 400 | Independently evolved baseline population | Deterministic horizontal jitter only |
| (b) | `semantic_information` | 400 | Independently evolved baseline population | Deterministic horizontal jitter only |

## Frozen record

- $n=20$ populations per condition and $p$.
- 34 unique maps per population.
- Two nested continuations per map; 36-generation horizon.
- Explicit constant and identity endpoints.
- Target reached: 400/400.
- Right-censored: 0/400.
- Sequence-selective semantic estimate equals identity information: 200/200.
- Sequence-agnostic value of information and semantic estimates: numerical zero.

## Visual-production record

- Lower-case bracketed panel labels `(a)` and `(b)` are present.
- Condition is encoded by colour, marker shape, and fill.
- Raw evolved-population records remain visible; no pooled technical measurements are shown.
- No footer note is present; nested-design and censoring detail is transferred to `FIGURE_S3_FINAL_CAPTION.md`.

## Final outputs

`FIGURE_S3_PUBLICATION_GRADE.pdf`, `.svg`, `.eps`, `.png`, and `.tiff`; editable production source: `produce_supplementary_figures.py`.
