# PHASE_06_PACKAGE_MANIFEST.md

## Release identity

- Project: JRSI Major Revision — Semantic Information in Model B
- Completed phase: Phase 6 — focused model-structure and parameter robustness
- Gate decision: Gate 7 PASSED — BROAD GENERALITY SUPPORTED within the prespecified Model B design domain
- Scientific production and Gate 7 evidence commit: `387ce3c1e4f987b338bc363eef332d0863883f0a`
- Starting Phase 5 closure commit: `da63c52`
- Starting Phase 5 release tag: `phase5-gate5-passed-v1`
- Phase 4 release tag: `phase4-gate4-passed-v1`
- Source Phase 5 package SHA-256: `f9d3f23040e7edd85aeb89874cd5238884ca72e826d2d91b4cbfebd4a1748377`

## Controlling and handoff records

- `revision/REVISION_SPEC_v2.md`
- `revision/DECISIONS_LOG.md`, including preserved D16–D25 and approved D26–D31
- `revision/REVIEWER_MATRIX.md`
- `PHASE_05_HANDOFF.md`
- `PHASE_06_PLAN.md`
- `PHASE_06_HANDOFF.md`

## Phase 6 implementation and validation

- `src/modelb_semantic_repo/phase6.py`
- `scripts/run_phase6_batch.py`
- `scripts/validate_phase6.py`
- `tests/test_phase6.py`
- `GENERALITY_ANALYSIS.md`
- `VALIDATION_PHASE6.md`
- `PHASE_06_ENVIRONMENT.md`
- `TEST_RESULTS_PHASE6.txt`
- `validation/phase6/validation_summary.json`
- `validation/phase6/structural_checks.csv`
- Phase 4, Phase 5, and Phase 6 manifest-verification tables under `validation/phase6/`

## Archived Phase 6 result set

Root: `results/phase6_generality/`

- `GATE_7_DECISION.json`
- `phase6_settings.json`
- `regime_counts.csv`
- all Stage A, B1, B2, and C design, replicate, and summary tables
- deterministic Stage C and Stage D representative-selection records
- all 24 nondefault Stage D population blocks
- `stage_d_continuations.csv`
- `stage_d_replicate_summary.csv`
- `stage_d_frontiers.csv`
- `stage_d_summary.csv`
- `FILE_MANIFEST_SHA256.csv`

The Phase 6 result manifest hashes 71 archived result files and excludes itself.

## Validation summary

- 66 tests passed in bounded test invocations.
- 24/24 Phase 6 structural, inferential, Gate, and archive-integrity checks passed.
- All nondefault Stage D identity endpoints recovered information and viability exactly.
- All Phase 4 and Phase 5 archived files remain hash-identical to their manifests.
- Gate 7 recomputes as broad support from the archived machine-readable results.

## Restrictions carried forward

This release authorizes a model-domain generality conclusion but does not authorize final publication figures or manuscript rewriting. Gate 8 result freeze remains required. Gate 6 inheritance-scope and wording audit remains a later manuscript-stage requirement.
