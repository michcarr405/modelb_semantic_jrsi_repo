# PHASE_07_PACKAGE_MANIFEST.md

## Release identity

- Project: JRSI Major Revision — Semantic Information in Model B
- Completed phase: Result freeze
- Gate decision: Gate 8 PASSED
- Result-freeze scientific and validation commit: `2c7d78694579755402c0a1896e109b29dec4d6a0`
- Phase 7 planning commit: `340071ebd6a2a2c67edb4bbc35cbef4a50ba1cf8`
- Phase 7 implementation commit: `8fd57af71eefe0220ae0cd3b708000a8ebdfe0e1`
- Starting Phase 6 closure commit: `f9a3030`
- Starting Phase 6 release tag: `phase6-gate7-passed-v1`
- Result-freeze release tag: `phase7-gate8-passed-v1`
- Source Phase 6 package SHA-256: `0f47504026815148241210121b96492a92476b9db47f83dcf95ae24cf65b7dfa`

The release tag resolves the documentation-only closure commit containing this manifest.

## Controlling records

- `revision/REVISION_SPEC_v2.md`
- `revision/DECISIONS_LOG.md`, including preserved D16–D31 and approved D32–D33
- `revision/REVIEWER_MATRIX.md`
- `PHASE_06_HANDOFF.md`
- `PHASE_07_PLAN.md`
- `FROZEN_CLAIMS_AND_LIMITATIONS.md`
- `RESULT_FREEZE.md`
- `PHASE_07_HANDOFF.md`

## Result-freeze implementation

- `src/modelb_semantic_repo/result_freeze.py`
- `scripts/build_result_freeze.py`
- `scripts/validate_result_freeze.py`
- `tests/test_result_freeze.py`

## Frozen result-freeze dataset

Root: `results/result_freeze/`

- `RESULT_INVENTORY.csv`
- `INFERENTIAL_RECORD_AUDIT.csv`
- `FIGURE_SOURCE_CATALOG.csv`
- 11 machine-readable source tables under `figure_sources/`
- `GATE_8_DECISION.json`
- `FILE_MANIFEST_SHA256.csv`

The result-freeze manifest hashes 15 files and excludes itself.

## Validation records

- `VALIDATION_RESULT_FREEZE.md`
- `PHASE_07_ENVIRONMENT.md`
- `TEST_RESULTS_PHASE7.txt`
- `validation/result_freeze/structural_checks.csv`
- `validation/result_freeze/validation_summary.json`
- `validation/result_freeze/figure_source_verification.csv`
- recomputed Phase 4–6 inferential tables under `validation/result_freeze/`

## Validation summary

- Full repository test suite: 68 passed
- Phase 4–6 result inventory: 2,107 files
- Manifested files verified: 2,104/2,104
- Inferential and structural audit checks: 28/28 passed
- Figure-source derivation checks: 11/11 passed
- Final result-freeze structural checks: 5/5 passed
- Final publication figures created: no
- Manuscript rewritten: no
- Scientific output changed: no

## Frozen interpretation

The package authorizes manuscript production only within the claim and limitation boundary in `FROZEN_CLAIMS_AND_LIMITATIONS.md`.

It does not authorize claims of universality, biochemical realism, historical reconstruction, literal protocell fission, semantic compression, a universal critical threshold, or robustness to every fitness formulation.

## Next-stage restriction

Final figures must be built only from the frozen source tables or directly traceable archived Phase 4–6 records. Any scientific change requires a new decision-log entry, a new versioned analysis release, and reopening every affected gate. Gate 6 remains a required manuscript-stage wording audit.
