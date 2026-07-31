# VALIDATION_RESULT_FREEZE.md

## Summary

The result-freeze pipeline completed successfully.

- Result inventory rows: 2,107
- Manifested Phase 4–6 files verified: 2,104/2,104
- Figure-source tables: 11
- Figure-source derivation checks: 11/11 passed
- Inferential checks: 28/28 passed
- Final structural validation checks: 5/5 passed
- Gate 8 status: PASSED

## Commands

```bash
PYTHONPATH=src python scripts/build_result_freeze.py
PYTHONPATH=src python scripts/validate_result_freeze.py
PYTHONPATH=src pytest -q tests/test_result_freeze.py
```

The full repository test suite was also run before release closure.

## Validation records

Primary generated records are:

- `results/result_freeze/RESULT_INVENTORY.csv`
- `results/result_freeze/INFERENTIAL_RECORD_AUDIT.csv`
- `results/result_freeze/FIGURE_SOURCE_CATALOG.csv`
- `results/result_freeze/GATE_8_DECISION.json`
- `results/result_freeze/FILE_MANIFEST_SHA256.csv`
- `validation/result_freeze/figure_source_verification.csv`
- `validation/result_freeze/structural_checks.csv`
- `validation/result_freeze/validation_summary.json`
- recomputed Phase 4–6 inferential tables under `validation/result_freeze/`

## Interpretation

This validation confirms that the versioned archive is internally consistent and that the frozen numerical claims can be reproduced from archived machine-readable tables using the locked statistical code and seeds. It does not add new scientific evidence or authorize claims beyond `FROZEN_CLAIMS_AND_LIMITATIONS.md`.
