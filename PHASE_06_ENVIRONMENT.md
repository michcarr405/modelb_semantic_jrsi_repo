# PHASE_06_ENVIRONMENT.md

Phase 6 used the locked package environment inherited from the versioned Phase 5 release.

- Python: `3.13.5`
- NumPy: `2.3.5`
- pandas: `2.2.3`
- SciPy: `1.17.0`
- Numba: `0.65.1`
- scikit-learn: `1.8.0`
- Platform: Linux x86_64

Production commands were executed from the repository root with `PYTHONPATH=src`. The staged batch runner was used because the execution shell enforced a short wall-clock limit; batch boundaries do not alter seeds, design rows, or output hashes.
