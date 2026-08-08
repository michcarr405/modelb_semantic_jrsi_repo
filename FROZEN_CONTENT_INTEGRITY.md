# Frozen-content integrity statement

This release candidate was built by branching from the Gate 8 closure commit `36246a86320037506beed83d0f7366c33d2c59c5`.

The frozen scientific commit remains `2c7d78694579755402c0a1896e109b29dec4d6a0`.

During release-candidate construction:

- no pre-existing file under `src/`, `results/`, `validation/`, `tests/`, or the Phase 4–7 scientific/validation records was modified;
- the existing root `README.md` was replaced with a public-facing release README, while the prior Gate 8 README was preserved verbatim as `docs/GATE8_INTERNAL_README.md`;
- new release-only files were added for publication-figure reproducibility, environment locking, citation/release metadata, artwork provenance, and public-release validation;
- `scripts/validate_result_freeze.py` still passes all release-level checks;
- the full test suite passes 68/68 tests;
- copied publication figure-source tables match the Gate 8 frozen figure sources exactly by SHA-256.

A final public packaging commit may be created only after the license, DOI, Figure 1/2 archive references, and clean-room record are closed.
