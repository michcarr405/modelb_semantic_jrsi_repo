# PHASE_07_ENVIRONMENT.md

## Purpose

Record the execution environment used for the result-freeze inventory, inferential recomputation, source-table construction, and Gate 8 validation.

## Runtime

- Platform: `Linux-6.12.13-x86_64-with-glibc2.41`
- Python: `3.13.5` (GCC 14.2.0)
- NumPy: `2.3.5`
- pandas: `2.2.3`
- SciPy: `1.17.0`
- Numba: `0.65.1`
- Project dependency records: `requirements.txt` and `pyproject.toml`
- Source import path for validation: `PYTHONPATH=src`

## Phase 7 commands

```bash
PYTHONPATH=src python scripts/build_result_freeze.py
PYTHONPATH=src python scripts/validate_result_freeze.py
PYTHONPATH=src pytest -q tests/test_result_freeze.py
```

No production simulation command was run in Phase 7.
