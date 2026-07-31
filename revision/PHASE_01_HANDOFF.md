# PHASE_01_HANDOFF.md

## Project

**Manuscript:** `rsif-2026-0516`
**Project:** JRSI Major Revision — Semantic Information in Model B
**Date:** 2026-07-30
**Completed phase:** Phase 1 — code, implementation, and reproducibility audit
**Gate status:** **Gate 1 PASSED**

## 1. Handoff purpose

This file closes the amended Phase 1 audit after recovery of `modelb_semantic_jrsi_repo.zip` and defines the permitted opening state for Phase 2.

The initial Phase 1 audit was blocked because the semantic-intervention implementation appeared absent. The recovered archive supplied the missing intervention, frontier, statistics, figure, notebook, and processed-output code. The audit was reopened, all relevant findings were incorporated, and the Gate 1 result was superseded from blocked to passed.

## 2. What Phase 1 established

### Repository and implementation

- Both submitted code archives are inventoried and hashed.
- The implemented baseline model was compared systematically with the submitted manuscript.
- The recovered semantic pipeline was traced from baseline evolution through grouping interventions, continuation, viability, frontier construction, statistics, and figure production.
- The code confirms a fitness-weighted, with-replacement compositional-resampling transition, not literal mass-conserving fission.

### RNG

- One hidden historical source was identified: `np.random.random()` in the compiled local-state sampler.
- Identical submitted seeds do not reproduce trajectories.
- The authoritative branch now uses explicit controlled generators for all draws.
- Same-seed determinism passes within and across processes; different seeds diverge.
- Purpose-separated continuation stream scaffolding exists.

### Intervention maps

- All 13,440 submitted map-generation instances were replayed from exact recovered source and seed order.
- Constant and identity revision endpoints were added, producing 13,442 manifest rows total.
- There are 4,708 distinct canonical assignment hashes and 8,734 duplicate rows.
- All 3,360 cached k-means metadata entries match the replay.
- The submitted prefix grid yields only four distinct leading-prefix partitions: 4, 16, 64, and 256 groups.
- The submitted intervention set lacks a full 1,024-group identity endpoint.

### Tests and environment

- 42 tests pass.
- The audit environment and direct dependency versions are recorded.
- A static random-source manifest, source-hash records, exact validation commands, and seed-ledger template are present.

## 3. Important findings carried forward

These are not Phase 1 blockers, but they constrain later work:

1. **Submitted scientific outputs are provisional.** The revision specification supersedes the raw-MI measure, heuristic retained-information coordinate, pooled-point statistics, and ordinary treatment of censored lower bounds.
2. **Selective target recovery was poor.** Cached submitted frontiers reached the target in 0/10 fidelities for excess-over-control, 0/10 for mean future fitness, and 1/10 for threshold survival.
3. **Final evolved populations are not archived.** New deterministic baseline populations will be required for the corrected production rerun after Gates 2 and 3.
4. **Assignments were not saved.** Submitted maps can be replayed from code and seed order, but future production must save assignments and hashes directly.
5. **Viability-definition runs re-observed the baseline state.** The revised pipeline should calculate and store baseline information once per evolved replicate.
6. **The submitted map/continuation RNG was call-order coupled.** The revised pipeline must use purpose-separated streams.
7. **The final sequence-based grouping family remains pending.** Phase 1 provides evidence but does not silently resolve P01.

## 4. Required Phase 1 deliverables

| Deliverable | Status |
|---|---|
| `IMPLEMENTATION_AUDIT.md` | Complete |
| `RNG_AUDIT.md` | Complete |
| `RNG_SOURCE_MANIFEST.csv` | Complete |
| `GROUPING_MAP_MANIFEST.csv` | Complete |
| `GROUPING_MAP_UNIQUE.csv` | Complete |
| explicit constant and identity endpoints | Complete |
| `VALIDATION.md` | Complete |
| `ENVIRONMENT.md` and lock | Complete for audit environment |
| seed-ledger format | Complete |
| test results | 42 passed |
| updated reviewer matrix | Complete at Phase 1 level |
| Git commit hash | Recorded at close |

## 5. Gate 1 decision

Gate 1 requires RNG control, unit tests, implementation audit, and intervention-map inventory.

| Gate criterion | Result |
|---|---|
| Repository structure and execution path documented | Pass |
| Algorithm compared with manuscript | Pass |
| All random sources inventoried | Pass |
| Hidden RNG repaired | Pass |
| Same-seed reproducibility | Pass |
| Grouping maps and duplicates inventoried | Pass |
| Constant and identity endpoints specified | Pass |
| Core tests pass | Pass |
| No ambiguity blocks conditional-MI implementation | Pass |

**Gate 1: PASSED.**

## 6. Phase 2 objective

**Phase title:** Information-measure validity

Phase 2 must implement and validate:

\[
I(M;Z\mid S),
\]

within-segment permutation correction,

\[
I_{\mathrm{corr}}(M;Z\mid S)
=
I_{\mathrm{obs}}(M;Z\mid S)-E_{\mathrm{perm}}[I(M;Z\mid S)],
\]

and actual retained information,

\[
I(g(M);Z\mid S).
\]

## 7. Required Phase 2 tests

At minimum:

- conditional-MI agreement with hand-computable distributions;
- segment-weighted decomposition correctness;
- sequence-agnostic population-limit conditional MI equals zero;
- finite-sample conditional MI is corrected toward its null;
- permutations shuffle metabolite/local-state labels within segment only;
- permutation results are reproducible from a dedicated stream;
- constant grouping gives zero retained conditional information;
- identity grouping reproduces baseline conditional information exactly;
- grouping-label renaming leaves retained information invariant;
- duplicate grouping maps yield identical retained information on the same observations;
- total MI, conditional MI, positional MI, and corrected MI are not conflated;
- estimator input/output schema records baseline replicate, observation seed, map hash, and permutation seed.

## 8. Phase 2 restrictions

Do not during Phase 2:

- run the full baseline fidelity sweep;
- run the full intervention suite;
- generate production semantic estimates;
- perform parameter sweeps;
- decide the final target tolerance or continuation count without the required pilots;
- rewrite the manuscript or final figures.

Small synthetic, analytical, and diagnostic simulations are permitted only to validate estimators and endpoints.

## 9. Pending decisions

Phase 1 informs but does not resolve:

- **P01:** final sequence-based grouping family;
- **P02:** continuation seeds per intervention;
- **P03:** final intervention horizon;
- **P04:** target tolerance;
- **P05:** pooling versus family-specific frontiers;
- **P06:** role of k-means-profile clustering.

P01 should be resolved before confirmatory intervention production, but it does not block implementation of map-agnostic information estimators in Phase 2.

## 10. Recommended Phase 2 opening prompt

> Begin Phase 2 of the JRSI major revision: information-measure validity. Treat `REVISION_SPEC_v2.md`, `DECISIONS_LOG.md`, `REVIEWER_MATRIX.md`, and `PHASE_01_HANDOFF.md` as controlling documents. Gate 1 has passed. Do not run production simulations or rewrite the manuscript. Implement and validate position-conditioned mutual information, within-segment permutation correction, and actual retained information for arbitrary grouping maps. Require constant and identity endpoint tests, dedicated permutation RNG streams, analytical checks, and a Phase 2 handoff before any replicate-level frontier work begins.
