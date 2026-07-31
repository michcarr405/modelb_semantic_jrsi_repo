# PHASE_05_ENVIRONMENT.md

Phase 5 was executed in the inherited Phase 4 environment.

- Python: 3.13
- Primary packages: NumPy, pandas, SciPy, Numba, pytest
- Source import: `PYTHONPATH=src`
- Test command: `PYTHONPATH=src pytest -q`
- Production command: `PYTHONPATH=src python scripts/run_phase5_production.py --workers 1`
- Validation command: `PYTHONPATH=src python scripts/validate_phase5.py`

The production runner is restartable. Baseline and evaluation blocks are written after each completed job and are reused on resume.
