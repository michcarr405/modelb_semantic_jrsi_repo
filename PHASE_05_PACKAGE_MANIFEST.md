# PHASE_05_PACKAGE_MANIFEST.md

## Release identity

- Project: JRSI Major Revision — Semantic Information in Model B
- Completed phase: Phase 5 — causal specificity
- Gate decision: Gate 5 PASSED
- Scientific production and Gate 5 evidence commit: `c9bc4c1`
- Starting Phase 4 release tag: `phase4-gate4-passed-v1`
- Phase 4 scientific production commit: `204010b439bcaf0921a3ed3a82a3e48468ee704e`
- Phase 3 closure commit: `c42fa82040e5d3b32105ef440c520dd6dd7c782d`
- Phase 3 validated implementation commit: `add8a0750d9a2dc0e9d8ef5fbded6bab9175db42`

## Controlling and handoff records

- `revision/REVISION_SPEC_v2.md`
- `revision/DECISIONS_LOG.md`, including preserved D16–D20 and approved D21–D25
- `revision/REVIEWER_MATRIX.md`
- `PHASE_04_HANDOFF.md`
- `PHASE_05_PLAN.md`
- `PHASE_05_HANDOFF.md`

## Phase 5 implementation and validation

- `src/modelb_semantic_repo/phase5.py`
- `scripts/run_phase5_production.py`
- `scripts/validate_phase5.py`
- `tests/test_phase5.py`
- `CAUSAL_SPECIFICITY.md`
- `VALIDATION_PHASE5.md`
- `PHASE_05_ENVIRONMENT.md`
- `TEST_RESULTS_PHASE5.txt`
- `validation/phase5/validation_summary.json`
- `validation/phase5/structural_checks.csv`
- `validation/phase5/representative_baseline_reruns.csv`
- `validation/phase5/representative_evaluation_reruns.csv`

## Archived Phase 5 result set

Root: `results/phase5_causal_specificity/`

- `GATE_5_DECISION.json`
- `gate5_paired_contrasts.csv`
- `gate5_block_values.csv`
- `control_summary.csv`
- `target_reach_and_censoring.csv`
- `identity_endpoint_checks.csv`
- `phase4_archive_verification.csv`
- `FILE_MANIFEST_SHA256.csv`
- all evolved control states and RNG records
- all baseline blocks, intervention information, continuation rows, frontiers, topology definitions, affinity derangements, and unstable-topology schedules

The result manifest hashes 818 archived result files. The manifest excludes itself.

## Validation summary

- 63 tests passed.
- 19/19 Phase 5 validation checks passed.
- 220/220 identity endpoints recovered exactly.
- 220/220 targets were reached; no censored observation was imputed, and censoring fields remain explicit.
- All six prespecified paired Gate contrasts were positive and BH-significant.
- The archived Phase 4 files remained hash-identical.

## Restrictions carried forward

This release does not authorize broad parameter sweeps, final publication figures, manuscript rewriting, a semantic-compression claim, or a generality claim. Those remain subject to later gates and change control.
