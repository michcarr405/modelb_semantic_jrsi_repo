# Phase 4 pre-production pilot and confirmatory plan

**Project:** JRSI major revision, manuscript `rsif-2026-0516`  
**Phase:** 4 — corrected core production and core-result survival  
**Date frozen:** 2026-07-31  
**Status:** Prespecified before pilot execution or production simulation

## 1. Provenance gate

Phase 4 may proceed only from the supplied Phase 3 package. Before any code change, the repository must contain:

- closure commit `c42fa82040e5d3b32105ef440c520dd6dd7c782d`;
- validated scientific implementation commit `add8a0750d9a2dc0e9d8ef5fbded6bab9175db42`;
- `PHASE_03_HANDOFF.md`;
- `STATISTICAL_PIPELINE_VALIDATION.md`;
- `revision/REVISION_SPEC_v2.md`;
- `revision/DECISIONS_LOG.md`;
- `revision/REVIEWER_MATRIX.md`.

If any item is absent, Phase 4 stops without reconstructing from an older archive.

## 2. Pilot-only scope

The pilot may use small, separately seeded diagnostic baseline populations. Pilot seeds are disjoint from production seeds. Pilot output cannot be used as confirmatory evidence for Gate 4.

Pilot conditions:

- regimes: sequence-selective and sequence-agnostic;
- inheritance probabilities: `0.5`, `0.9`, `1.0`;
- two independent pilot baselines per regime and fidelity;
- default population and molecular dimensions;
- 100 evolutionary generations;
- a fixed diagnostic subset of maps spanning constant, random, affinity-rank, contiguous-substring, and identity endpoints;
- eight nested continuation seeds;
- one maximum continuation of 36 generations, evaluated at prefixes 12, 24, and 36.

## 3. P01 candidate and decision rule

Candidate sequence family: every contiguous substring partition of a 5-symbol motif for substring lengths 1–4 and every valid start position. This produces leading, trailing, and internal maps without privileging one orientation. The length-5 map is represented only by the explicit identity endpoint.

P01 is approved if:

- all generated maps have deterministic canonical hashes;
- exact duplicate maps are removed;
- all leading, trailing, and internal positions are represented;
- constant and identity remain separate explicit endpoints.

Otherwise Phase 4 stops for a new decision.

## 4. P02 continuation-count candidates and decision rule

Candidates: `k = 1, 2, 4, 6, 8` continuation seeds.

For each block and map, the first `k` continuation means are compared with the full eight-seed mean at the candidate production horizon. Select the smallest `k` satisfying both:

- root-mean-square error no greater than `0.10` model-fitness units;
- 95th percentile absolute error no greater than `0.25` model-fitness units.

If no candidate below eight passes, use eight.

## 5. P03 horizon candidates and decision rule

Candidates: 12, 24, and 36 generations.

For each shorter horizon, compare map-level mean viability with the 36-generation mean. Select the shortest horizon satisfying all:

- Spearman rank correlation at least `0.98`;
- median absolute difference no greater than `0.10` model-fitness units;
- 95th percentile absolute difference no greater than `0.25` model-fitness units.

If neither shorter horizon passes, use 36.

## 6. P04 target tolerance and uncertainty rule

The confirmatory target rule is provisionally the submitted strict recovery standard:

\[
V_{\mathrm{target},r}=V_{\mathrm{actual},r}-0.01\left(V_{\mathrm{actual},r}-V_{\mathrm{constant},r}\right).
\]

The pilot may only verify endpoint behavior. It may not select a looser tolerance from favorable frontier outcomes. Retain `0.01` if paired actual and identity continuations recover exactly. If exact identity recovery fails, Phase 4 stops; it does not relax the target.

## 7. P05 pooling candidate and decision rule

The primary frontier will pool only prespecified neutral/conservative maps:

- balanced-random grouping;
- affinity-rank grouping;
- all contiguous-substring grouping maps from P01;
- constant and identity endpoints.

Exact duplicate assignments are collapsed by canonical hash. Affinity-profile k-means is excluded from the Phase 4 primary pool and is not run in Phase 4. The frontier is the validated discrete monotone upper envelope with no binning, smoothing, or interpolation.

P05 is approved if the pilot confirms valid unique hashes, endpoint coverage, and exact identity recovery.

## 8. Production design frozen after P01–P05 approval

Production will use:

- full inheritance-probability sweep `0.1, ..., 1.0`;
- 20 independently evolved baseline populations per regime and fidelity;
- default 150-generation evolution;
- fixed affinity matrix from the authoritative repository;
- dedicated deterministic streams for initialization, baseline observation, baseline propagation, information observation, within-segment permutations, grouping-map construction, continuations, bootstrap, and inference;
- 200 within-segment permutations per evolved baseline for corrected conditional information;
- map grid `K = 2, 4, 8, 16, 32, 64, 128, 256, 512` for balanced-random and affinity-rank maps;
- all P01 contiguous-substring maps;
- explicit constant and identity endpoints;
- one replicate-specific frontier per evolved baseline;
- 2,000 complete-block bootstrap replicates per fidelity;
- 9,999 Monte Carlo label permutations when exact enumeration is unavailable.

All final populations, trajectories, observations, map assignments, hashes, continuation rows, seed ledgers, and state hashes must be archived.

## 9. Prespecified Gate 4 test

The primary confirmatory fidelity is `p = 1.0`, where the submitted work predicted the strongest selective effect. The full sweep is reported, but the gate is not retuned from the sweep.

Gate 4 passes only if all of the following hold:

1. Every production block passes identity information and paired identity viability recovery.
2. At `p = 1.0`, replicate-level corrected conditional information is greater in the sequence-selective regime than in the sequence-agnostic regime by a two-sided replicate-level permutation test with `p < 0.05`.
3. At `p = 1.0`, replicate-level value of information is greater in the sequence-selective regime than in the sequence-agnostic regime by a two-sided replicate-level permutation test with `p < 0.05`, and the selective mean value is positive.
4. At `p = 1.0`, the sequence-selective semantic-information distribution is greater than the sequence-agnostic distribution if uncensored values are available for all blocks. If censoring prevents that test, censoring is retained and Gate 4 cannot be declared passed solely from complete cases.
5. No pooled map, continuation, motif, window, generation, or protocell observation is treated as an independent replicate.

The `p = 0.9` contrast and the remaining fidelity sweep are secondary corroborative analyses. No causal controls, broad parameter sweeps, final publication figures, or manuscript rewriting are permitted before the Gate 4 decision.
