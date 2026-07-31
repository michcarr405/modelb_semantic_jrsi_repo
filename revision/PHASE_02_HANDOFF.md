# PHASE_02_HANDOFF.md

## Project

**Manuscript:** `rsif-2026-0516`  
**Project:** JRSI Major Revision — Semantic Information in Model B  
**Date:** 2026-07-31  
**Completed phase:** Phase 2 — information-measure validity  
**Gate status:** **Gate 2 PASSED**

## 1. Handoff purpose

This file closes Phase 2 and defines the permitted opening state for Phase 3. Gate 1 was accepted from `PHASE_01_HANDOFF.md`; no production simulations or manuscript rewriting were performed in Phase 2.

## 1.1 Source-provenance note

The supplied `modelb_semantic_jrsi_repo.zip` did not contain Git metadata or the Phase 1 audit/test files. This working repository was therefore initialized locally from that archive, and the controlling revision documents were copied into `revision/`. Gate 1 status was accepted from the supplied `PHASE_01_HANDOFF.md`.

The supplied source still contained the historical global local-state random draw described in the Phase 1 handoff. The explicit-generator repair was reinstated in this working branch and verified by same-seed, different-seed, and missing-generator tests. This does not represent a new scientific decision; it restores the passed Gate 1 requirement in the reconstructed source tree.

## 2. Implemented estimators

The revision branch now provides:

1. total motif–local-state mutual information, \(I(M;Z)\);
2. positional association, \(I(M;S)\);
3. position-conditioned information, \(I(M;Z\mid S)\);
4. segment-weighted decomposition of conditional MI;
5. within-segment permutation correction;
6. actual retained information, \(I(g(M);Z\mid S)\), for dense arrays and mapping objects;
7. corrected retained-information diagnostics;
8. constant and full-identity endpoint constructors;
9. label-renaming-invariant grouping-map hashes;
10. a provenance schema recording replicate, observation seed, map hash, and permutation stream.

The submitted heuristic

\[
I(M;Z)\frac{\log_2 G}{\log_2(4^5)}
\]

is not used by the revised retained-information implementation.

## 3. Validation status

- `31` unit and integration tests pass.
- `6/6` scripted analytical and endpoint checks pass.
- A sequence-agnostic confounding construction has positive total and positional MI but zero conditional MI.
- The finite-sample independent diagnostic is corrected from `0.63765` bits to `0.04053` bits after subtraction of a `0.59711`-bit within-segment permutation mean.
- Constant retained information is exactly zero.
- Identity retained information exactly reproduces baseline conditional information.
- Same permutation stream reproduces exactly; different streams diverge.
- Group-label renaming and duplicate partitions leave retained information unchanged.

Detailed evidence is in `INFORMATION_MEASURE_VALIDATION.md` and `validation/phase2/`.

## 4. RNG status relevant to Phase 2

Permutation nulls use a dedicated stream keyed by root seed, baseline replicate, and stream index. No global random state is used in the estimator.

The reconstructed branch also passes explicit-RNG observer tests: the same population and generator seed reproduce the same local-state observations, different seeds diverge, and a missing generator is rejected.

## 5. Phase 2 outputs

| Deliverable | Status |
|---|---|
| `src/modelb_semantic_repo/information.py` | Complete |
| compatibility wrappers in `original_model/mi.py` | Complete |
| actual retained-information integration | Complete |
| constant and identity endpoints | Complete |
| dedicated permutation streams | Complete |
| `tests/test_information.py` | Complete |
| `tests/test_rng_and_integration.py` | Complete |
| `scripts/validate_information_measures.py` | Complete |
| `validation/phase2/*` | Complete |
| `INFORMATION_MEASURE_VALIDATION.md` | Complete |
| updated `REVIEWER_MATRIX.md` | Complete at Phase 2 level |
| test-results record | Complete |
| versioned Git content commit | `69a7df8efea3cd78a0712778a8831983b7dc62fe` |
| `PHASE_02_ENVIRONMENT.md` | Complete |


## 5.1 Git record

- Source import commit: `55aa592cb874a85da66d664eeb47dd2557a0d8e6`
- Phase 2 scientific-code and validation commit: `69a7df8efea3cd78a0712778a8831983b7dc62fe`

The final package may include a later documentation-only closure commit; the scientific implementation validated for Gate 2 is the Phase 2 content commit above.

## 6. Gate 2 decision

Gate 2 requires conditional MI, permutation correction, actual retained information, and correct endpoints.

| Gate criterion | Result |
|---|---|
| Conditional MI agrees with analytical distributions | Pass |
| Segment weighting is correct | Pass |
| Sequence-agnostic population-limit conditional MI is zero | Pass |
| Permutation null preserves segment structure | Pass |
| Finite-sample correction behaves as intended | Pass |
| Permutation RNG is dedicated and reproducible | Pass |
| Constant endpoint is zero | Pass |
| Identity endpoint reproduces baseline | Pass |
| Arbitrary grouping maps are supported | Pass |
| Map renaming and duplicates are invariant | Pass |
| Schema records required provenance | Pass |

**Gate 2: PASSED.**

## 7. Restrictions still in force

Do not yet:

- run the full baseline fidelity sweep;
- run the full intervention suite;
- report revised semantic frontiers;
- treat continuation seeds as independent replicates;
- choose target tolerance from confirmatory results;
- pool intervention families without a prespecified rule;
- run parameter or causal-control sweeps;
- make final figures;
- rewrite the manuscript.

## 8. Phase 3 objective

**Phase title:** Statistical-pipeline validity

Phase 3 must validate, using synthetic or small diagnostic data only:

- one frontier per independently evolved baseline replicate;
- nested intervention-map and continuation-seed handling;
- paired actual/intervened continuation streams where feasible;
- continuation-variance diagnostics needed to resolve P02;
- target detection and explicit lower-bound censoring;
- identity endpoint recovery;
- block bootstrap over complete evolved-replicate blocks;
- replicate-level permutation inference;
- machine-readable target-reached counts and fractions.

No corrected production result should be generated until Gate 3 passes.

## 9. Recommended Phase 3 opening prompt

> Begin Phase 3 of the JRSI major revision: statistical-pipeline validity. Treat `REVISION_SPEC_v2.md`, `DECISIONS_LOG.md`, `REVIEWER_MATRIX.md`, and `PHASE_02_HANDOFF.md` as controlling documents. Gates 1 and 2 have passed. Do not run production simulations or rewrite the manuscript. Validate one information–viability frontier per independently evolved baseline replicate, nested continuation handling, target detection, target-not-reached censoring, block bootstrap, and replicate-level permutation inference. Require identity-endpoint recovery and a Phase 3 handoff before corrected core production runs.
