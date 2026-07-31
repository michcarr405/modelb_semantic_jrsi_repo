# RESULT_FREEZE.md

## Project

**Manuscript:** `rsif-2026-0516`  
**Project:** JRSI Major Revision — Semantic Information in Model B  
**Date:** 2026-07-31  
**Phase:** Result freeze  
**Gate status:** **Gate 8 PASSED**

## 1. Scope

This phase audited the complete versioned Phase 4–6 result archive, recomputed the primary inferential records from archived machine-readable tables, created traceable figure-source tables, froze the supported claim and limitations, and decided Gate 8.

No production simulation was rerun. No model, estimator, grouping map, target rule, continuation design, inferential method, regime threshold, or archived scientific result was changed. No final publication figure was created, and no manuscript section was rewritten.

## 2. Starting provenance

- Source package: `JRSI_MAJOR_REVISION_PHASE6_GATE7_PASSED_v1`
- Starting Git commit: `f9a3030` — Close Phase 6 documentation for versioned release
- Phase 7 planning commit: `340071e`
- Preserved decisions: D16–D31
- Controlling records: `revision/REVISION_SPEC_v2.md`, approved entries in `revision/DECISIONS_LOG.md`, `revision/REVIEWER_MATRIX.md`, and `PHASE_06_HANDOFF.md`

## 3. Complete result inventory

`results/result_freeze/RESULT_INVENTORY.csv` contains one file-level record for every file under the three frozen result roots, including each self-manifest as an explicit special case.

| Archive | Files inventoried | Total bytes | Manifested files verified |
|---|---:|---:|---:|
| Phase 4 core | 1,216 | 83,793,517 | 1,215/1,215 |
| Phase 5 causal specificity | 819 | 35,447,630 | 818/818 |
| Phase 6 generality | 72 | 1,597,317 | 71/71 |
| **Total** | **2,107** | **120,838,464** | **2,104/2,104** |

The three additional files are the self-manifests, which are deliberately excluded from their own hash lists. No unmanifested scientific result file was found. Every manifested file matched its recorded size and SHA-256 hash.

## 4. Inferential record audit

`results/result_freeze/INFERENTIAL_RECORD_AUDIT.csv` contains 28 pass/fail checks. All 28 passed.

### Phase 4

Verified:

- 400 evolved baseline records;
- 28,000 continuation rows;
- 70 continuation rows per evolved baseline block;
- exact identity information and viability recovery;
- target-reaching and censoring counts;
- all 80 block-bootstrap intervals from archived draws;
- all 30 replicate-level permutation tests and BH-adjusted values;
- the Gate 4 primary records at `p = 1.0`.

### Phase 5

Verified:

- 15,400 continuation rows;
- two nested continuations per map and realization;
- exact reconstruction of seed-block control summaries from realization-level records;
- all six paired sign-randomization tests;
- all 12,000 paired-bootstrap draws and intervals;
- target-reaching and censoring records;
- exact identity recovery and the Gate 5 decision.

### Phase 6

Verified:

- all Stage A, B1, B2, and C replicate-to-summary aggregations and bootstrap intervals;
- all regime classifications from the locked practical thresholds;
- all Stage D confirmatory bootstrap intervals;
- exact identity recovery and target records;
- the Stage A and B1 positive fractions, four-family structural support, nondefault confirmations, and Gate 7 broad-generality decision.

Floating-point comparisons used exact equality where records are discrete and an absolute tolerance of at most `1e-12` for deterministic recomputation of numerical aggregates.

## 5. Figure-source freeze

Eleven machine-readable figure-source tables were created under `results/result_freeze/figure_sources/`. They contain no new model output. Each is an exact source copy, selected-column copy, row union, or deterministic wide-to-long reshape of frozen Phase 4–6 tables.

The source set includes:

- corrected core information at the independent-replicate level;
- core semantic estimates, value of information, targets, and censoring;
- all discrete replicate frontier points;
- core permutation, bootstrap, and target-reaching records;
- matched seed-block causal-control values and the six paired contrasts;
- raw and summarized generality-screen results;
- protocol sensitivity;
- nondefault confirmatory replicate and summary records.

`results/result_freeze/FIGURE_SOURCE_CATALOG.csv` records the intended evidence, derivation, source files, row count, and SHA-256 hash for each table. All 11 derivation checks passed. These tables authorize later figure construction but do not prescribe final visual layout.

## 6. Frozen scientific interpretation

The frozen claim hierarchy and mandatory limitations are recorded in `FROZEN_CLAIMS_AND_LIMITATIONS.md`.

The maximum-strength central claim is:

> Within the tested sequence-explicit, Wright–Fisher-like compositional-resampling model, inherited sequence-dependent motif–local-state information can become causally relevant to future mean model fitness. At the primary fidelity, full selection under a stable native mapping produces an additional viability-relevant component beyond built-in architectural sensitivity; this excess is reduced by the prespecified selection, affinity, topology, cross-evaluation, and temporal-instability controls and persists across multiple parameter and structural alternatives.

This claim is explicitly bounded to the implemented model and tested domain.

## 7. Gate 8 decision

Gate 8 pass criteria were evaluated as follows:

| Criterion | Result |
|---|---|
| All Phase 4–6 manifest entries exist and match size/hash | Pass |
| Archived Phase 4–6 results unchanged | Pass |
| Complete archive inventory and manifest coverage | Pass |
| Primary inferential records recompute | Pass |
| Endpoint, replicate, target, censoring, and nesting records agree | Pass |
| Figure-source tables are traceable and verified | Pass |
| Frozen claim does not exceed combined Gates 4, 5, and 7 evidence | Pass |
| No final figures or manuscript rewrite produced | Pass |

**Gate 8: PASSED.**

The Phase 4–6 scientific results, numerical records, and result-level claim boundary are now frozen. Any scientific change requires a new decision-log entry and versioned analysis release.

## 8. Work authorized after Gate 8

The next phase may begin manuscript production from this package:

1. freeze notation and operational definitions;
2. create the model-workflow and intervention schematics;
3. build final data figures exclusively from the frozen figure-source tables;
4. complete Gate 6 inheritance-scope and wording audit;
5. rewrite Methods and Results before Discussion, title, abstract, and conclusion;
6. prepare the reviewer response and final reproducibility release.

No later production step may silently change the frozen analyses or numerical results.
