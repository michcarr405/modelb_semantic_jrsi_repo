# JRSI Round-2 MP migration — independent affinity-landscape generality prespecification

**Status:** frozen before generation of any independent-landscape outcomes  
**Date:** 2026-10-02  
**Purpose:** address Referee 1's concern that the original core populations share one fixed 1024 x 4 motif-affinity matrix by testing the final migrated marginal-preserving (MP) causal quantities across independently generated affinity landscapes.

## 1. Inferential hierarchy

The independent affinity **landscape**, not the nested evolved population, is the primary inferential unit for this phase. Population replicates are nested technical/biological repetitions used to estimate each landscape-level mean and do not inflate landscape-level n.

Primary campaign: **8 entirely new independent affinity landscapes**, each with **8 independently evolved populations per tested setting**. The historical fixed affinity landscape is retained only as an external reference and is excluded from primary across-landscape inference.

## 2. Landscape generation

For landscape index `L=0,...,7`, generate a 1024 x 4 standard-normal base matrix using a deterministic landscape seed derived from root **2026100211** and key `("affinity-landscape", L)`. The same base landscape is used across the four tested settings within a landscape so that setting differences are not confounded with landscape identity.

For setting-specific affinity magnitude `sigma`, use

`A_L(setting) = sigma(setting) * A_L(base)`.

No matrix is selected, rejected, resampled, or reordered based on outcomes. All four selected settings have motif length 5 and four local-state classes, so no dimension-changing landscape construction is required.

## 3. Tested settings

The final MP-migrated settings frozen before this phase are:

1. `B2_default` — primary default/core setting, p=1.0;
2. `A_p2_a3` — MP-selected viability-relevant Stage-D representative, p=0.75, sigma=1.62;
3. `B2_reward3` — MP-selected strong-adaptation Stage-D representative;
4. `B2_stride7` — MP-selected nearest-boundary/viability-relevant Stage-D representative.

No setting substitution is permitted after outcomes are seen.

## 4. Population evolution

For each landscape x setting combination, evolve **8 independent populations** for the setting's frozen baseline duration (150 generations) and all other frozen setting parameters. Population initialization/observation/propagation seeds are deterministically derived from root **2026100212**, landscape index, setting ID and population replicate index.

## 5. Primary quantities

For every evolved population measure:

- permutation-corrected `I(M;Z|S)` using 200 within-segment permutations;
- adaptive gain using the migrated study definition;
- MP constant-endpoint intervention-induced future-fitness loss `DeltaV_MP` over 36 generations using **8 matched continuation streams**;
- maximum analytical one-site marginal-preservation error for the MP constant operator.

Continuation root: **2026100213**.  
Permutation root: **2026100214**.  
Across-landscape inference/bootstrap root: **2026100215**.

The MP operator and all thresholds are exactly those frozen in `MP_MIGRATION_PRESPECIFICATION.md`.

## 6. Primary generality tests

For each of the four settings:

1. average each quantity across the 8 nested evolved populations within a landscape;
2. report all 8 landscape-level means;
3. report the number of landscapes with positive mean `DeltaV_MP`;
4. report the across-landscape arithmetic mean and a 95% nonparametric bootstrap interval resampling the **8 landscapes**;
5. test landscape-level `DeltaV_MP > 0` using the exact two-sided sign-randomization distribution over all 2^8 sign assignments;
6. report corrected-information and adaptive-gain landscape distributions descriptively and against their frozen practical thresholds where relevant.

No pooling of the 64 population replicates as if they were 64 independent affinity landscapes is permitted.

## 7. Generality decision rule

The setting is considered replicated across affinity landscapes for the MP causal effect only if:

- all 8 landscape-level mean `DeltaV_MP` values are positive **or** the exact landscape-level sign-randomization test is significant at two-sided p<0.05; and
- the 95% landscape-bootstrap interval for the mean `DeltaV_MP` excludes zero.

The practical `0.25` fitness-unit threshold remains a regime-classification threshold, not a requirement for declaring the causal effect nonzero across landscapes. For Stage-D regime persistence, report how many landscapes' nested-population bootstrap lower bounds exceed `0.25`; do not redefine the threshold.

## 8. Historical-landscape comparison

The original fixed affinity realization is plotted/reported as a labeled historical reference. It is not included in the n=8 landscape inference and is not used to tune the campaign.

## 9. No-retuning and stopping rule

- Exactly 8 new landscapes and 8 populations per landscape-setting combination are run.
- No early stopping.
- No selective extension of a landscape, setting or failed result.
- No replacement of an unfavorable landscape.
- No change to MP operator, continuation horizon, thresholds, selected settings, or statistical rule after outcomes are observed.
- Any failure is frozen and the manuscript scope is narrowed accordingly.
