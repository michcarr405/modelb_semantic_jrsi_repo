# Public-release candidate validation

**Date:** 2026-08-08  
**Status:** PASS for candidate integrity; final clean-room validation remains open.

## Environment used for candidate verification

- Python 3.13.5
- NumPy 2.3.5
- pandas 2.2.3
- SciPy 1.17.0
- Numba 0.65.1
- Matplotlib 3.10.8
- scikit-learn 1.8.0
- Pillow 12.3.0
- pytest 9.0.2

These versions match the recorded Phase 4/6/7 production environment for the scientific stack, with Pillow recorded for the publication-figure export layer.

## Verification performed

1. `PYTHONPATH=src pytest -q` — **68 passed**.
2. `PYTHONPATH=src python scripts/validate_result_freeze.py` — **5/5 release-level checks passed**.
3. Current publication source tables were compared byte-for-byte with the Gate 8 frozen `results/result_freeze/figure_sources/` tables — **all match**.
4. Manuscript Figures 3–8 were regenerated using the archived current plotting script and frozen source tables.
5. Supplementary Figures S1–S7 were regenerated using the archived current plotting script and frozen source tables.
6. Regenerated PNG and TIFF files matched the archived current publication exports exactly by SHA-256 — **all match**.

The exact comparison is recorded in `PUBLICATION_FIGURE_REGEN_HASH_COMPARISON.csv`.

## Boundary

This verification was performed in the validated project execution environment. It is not yet the independent/fresh-environment clean-room record required for final release closure. `CLEAN_ROOM_RERUN_RECORD.md` therefore remains open.
