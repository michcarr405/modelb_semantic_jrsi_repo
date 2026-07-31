# PHASE_07_PLAN.md

## Project

**Manuscript:** `rsif-2026-0516`  
**Project:** JRSI Major Revision — Semantic Information in Model B  
**Phase:** Result freeze and Gate 8  
**Date:** 2026-07-31

## 1. Purpose

Phase 7 converts the passed Phase 4–6 analyses into a versioned, auditable frozen-result release. It does not introduce a new model, estimator, intervention family, target rule, continuation design, inferential method, sensitivity setting, final figure, or manuscript claim.

## 2. Controlling state

The authoritative starting point is the versioned Phase 6 Gate 7 package at Git commit `f9a3030`.

The following remain fixed:

- `revision/REVISION_SPEC_v2.md`;
- approved entries in `revision/DECISIONS_LOG.md`, especially D16–D31;
- `revision/REVIEWER_MATRIX.md`;
- `PHASE_06_HANDOFF.md`;
- every archived file and manifest in `results/phase4_core/`, `results/phase5_causal_specificity/`, and `results/phase6_generality/`.

## 3. Permitted work

Phase 7 may:

1. inventory and hash the complete Phase 4–6 result archive;
2. verify manifest coverage and archive integrity;
3. recompute inferential records from archived machine-readable tables using the locked analysis code and seeds;
4. create derived figure-source tables that contain no new model output and can be traced exactly to frozen archives;
5. record the supported claim, claim strength, required caveats, and prohibited interpretations;
6. update the reviewer matrix with result-level evidence;
7. decide Gate 8 and create a versioned handoff and release package.

## 4. Prohibited work

Phase 7 must not:

- rerun or retune Phase 4–6 production simulations;
- change D16–D31;
- alter any archived Phase 4–6 result file;
- add or remove intervention maps;
- change the estimator, target, censoring rule, bootstrap, permutation test, regime thresholds, or Gate 7 criteria;
- create final publication figures;
- rewrite the manuscript, title, abstract, Discussion, Conclusion, or response letter;
- infer a chemical, historical, universal, or physical-fission conclusion not supported by the frozen analyses.

## 5. Required outputs

- `RESULT_INVENTORY.csv` — complete file-level archive inventory with manifest and hash status;
- `FIGURE_SOURCE_CATALOG.csv` and machine-readable source tables under `results/result_freeze/figure_sources/`;
- `INFERENTIAL_RECORD_AUDIT.csv` — check-level verification of all primary inferential records and Gate decisions;
- `FROZEN_CLAIMS_AND_LIMITATIONS.md` — frozen claim hierarchy, limitations, and prohibited wording;
- `RESULT_FREEZE.md` — complete audit report and Gate 8 decision;
- `VALIDATION_RESULT_FREEZE.md` and `validation/result_freeze/` records;
- `PHASE_07_HANDOFF.md`;
- a result-freeze Git commit, tag, manifest, and versioned zip package.

## 6. Gate 8 pass criteria

Gate 8 passes only if all of the following are true:

1. every Phase 4–6 result manifest entry exists and matches its recorded size and SHA-256 hash;
2. no archived Phase 4–6 result file was modified during Phase 7;
3. the archive inventory accounts for every file under the three result roots, with only each self-manifest excluded from its own hash list;
4. Phase 4, Phase 5, and Phase 6 primary inferential records recompute from archived tables within exact or documented floating-point tolerance;
5. identity endpoint, target-reach, censoring, replicate count, and nested-continuation records are internally consistent;
6. every figure-source row is traceable to an archived source row or a prespecified deterministic aggregation, and all derived-table verification checks pass;
7. the frozen claim is no stronger than the combined Gate 4, Gate 5, and Gate 7 evidence and explicitly retains the model-scope limitations;
8. no final figure or manuscript rewrite is present in the Phase 7 changeset.

Failure of any criterion blocks manuscript production and requires correction or a new versioned analysis release.

## 7. Result-freeze consequence

After Gate 8 passes, the Phase 4–6 model outputs, estimators, interventions, inferential records, and result-level claims are frozen. Any later scientific change requires:

- a new decision-log entry;
- a new versioned analysis release;
- explicit identification of invalidated outputs;
- rerunning all affected analyses and reopening the relevant gate.

Manuscript production may begin only from the Gate 8 package. Gate 6 remains a required manuscript-stage inheritance-scope and wording audit.
