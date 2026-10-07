# JRSI Round-2 study-wide marginal-preserving (MP) migration — prespecification

**Status:** frozen before any new MP-migration outcome generation  
**Date:** 2026-10-02  
**Starting scientific state:** Round-1 Gate-8 frozen repository, commit `36246a86320037506beed83d0f7366c33d2c59c5`; historical scientific freeze `2c7d78694579755402c0a1896e109b29dec4d6a0`.  
**Purpose:** prospectively replace the original affinity-logit averaging intervention as the primary causal operator throughout the study with a population-frequency-weighted probability-space intervention that preserves the expected segment-conditioned one-site local-state marginal for the current intervention-branch population.

## 1. Scientific motivation

Round-2 audit showed that the original logit-space grouping operator changes `P(Z|S)` because softmax is nonlinear and evolved motif frequencies are nonuniform. The MP operator removes within-group motif-specific local-state distinctions while preserving the current expected `P(Z|S)`. The migration is designed to determine which study-wide conclusions survive this cleaner operator without retuning thresholds or selecting favorable settings after outcomes are seen.

## 2. Frozen MP operator

For native local-state kernel

`P0(z | m,s) = softmax_z[(a_mz + beta 1[z=f(s)])/Theta]`,

and grouping map `g`, the intervention kernel at generation `t` is

`Q_t(z | q,s) = sum_{m:g(m)=q} w_t(m | q,s) P0(z | m,s)`,

where `w_t(m | q,s)` is the empirical frequency of motif `m` among active motif windows in group `q` and segment `s` in the current intervention-branch population. The projection is recomputed every continuation generation.

Consequences fixed by construction:

1. motifs in the same group and segment share the same local-state kernel;
2. the expected one-site segment-conditioned marginal is preserved exactly, up to floating-point error;
3. the constant map removes motif-specific local-state dependence while preserving expected `P(Z|S)`;
4. the identity map is exactly native;
5. adjacency distributions are **not** constrained to be preserved.

For Phase-6 structural variants, the same definition is applied to the variant's motif length, active-window set, segment assignment (including jitter), local-state count, topology, fitness mode, reward/penalty parameters and floor.

## 3. Primary causal quantity and terminology

The primary causal quantity becomes

`DeltaV_MP = mean_h F_actual(h) - mean_h F_MP,constant(h)`

over the frozen intervention horizon.

Reader-facing terminology will be **marginal-preserving intervention-induced future-fitness loss** (or a shorter explicitly defined equivalent), not "value of information".

The original Round-1 logit-operator results remain a historical sensitivity analysis and are not used as the primary causal estimates after migration.

## 4. Seeds and stochastic separation

Historical baseline-evolution seeds are retained exactly wherever existing populations are extended or reconstructed.

- Round-1 Phase-4 baseline/information root: `2026073104` (unchanged).
- Round-1 Phase-6 baseline root: `2026073106` (unchanged; used to reconstruct old replicates and deterministically extend replicate indices).
- MP core continuation root: `2026100205`.
- MP Stage A/B1/B2 continuation root: `2026100206`.
- MP Stage C continuation root: `2026100207`.
- MP Stage D continuation root: `2026100208`.
- MP p=1 confirmatory frontier continuation root: `2026100209`.
- Round-2 inference/bootstrap root: `2026100210`.

No outcome-dependent seed selection is permitted.

## 5. Core compositional-coupling sweep

### Baselines
Reuse the frozen 400 Phase-4 baseline populations: 20 sequence-selective and 20 sequence-agnostic populations at each `p = 0.1,...,1.0`.

### Constant-endpoint MP analysis
- horizon: 36 generations;
- 8 new matched continuation streams per baseline;
- independently evolved baseline population remains the inferential unit;
- actual and MP branches use matched observation/propagation streams;
- sequence-agnostic MP is mathematically identical to native because `A=0`; implementation equality will be validated explicitly and all reported agnostic losses must be numerical zero.

For each `p`, report mean selective `DeltaV_MP`, 95% complete-baseline bootstrap interval (2,000 draws), positive-block count, and two-sided sign-randomization test versus the exact agnostic zero (9,999 assignments), with BH adjustment over the ten `p` values.

Corrected baseline information is unchanged by the operator and will be taken from/recomputed against the frozen Phase-4 populations using the already audited within-segment permutation correction.

## 6. Primary graded frontier after migration

The study-wide MP frontier is **not** defined by the first 99%-recovery crossing. The prior high-precision exploratory audit showed that this discrete crossing is technically unstable because the 1% recovery band is much narrower than continuation variability.

The prospective confirmatory graded frontier will therefore be evaluated only at the primary selective setting `p=1.0`:

- same 20 frozen selective populations;
- all 34 frozen grouping maps and the actual endpoint;
- corrected retained-information coordinate with 200 within-segment permutations per map;
- 64 entirely new matched continuation streams per map;
- 36-generation horizon;
- identity exact by construction.

Primary continuous frontier summaries:

1. within-population Spearman correlation between corrected retained information and mean recovery fraction across the 34 maps;
2. number of populations with positive Spearman correlation;
3. Spearman correlation across the 34 map-averaged coordinates;
4. within-family map-average monotonicity for balanced-random, affinity-rank and contiguous-substring families;
5. the constant-endpoint `DeltaV_MP` and its population-level inference.

Recovery fraction is defined as

`R(g) = [V(g)-V(constant)] / [V(actual)-V(constant)]`.

No clipping is applied. The old 99% target may be retained only as a labeled secondary descriptive diagnostic; it is not a primary semantic/minimum-information estimator and will not determine claims.

The sequence-agnostic MP frontier is analytically flat because all motif kernels are identical conditional on segment; this will be implementation-validated rather than subjected to a redundant full production campaign.

## 7. Expanded Stage A/B1/B2 domain map

All 65 prespecified settings are retained unchanged.

Independent population replication is prospectively expanded to **n=8 per setting**:

- Stage A: retain historical replicate indices 0-3 and add 4-7;
- Stage B1: retain historical replicate indices 0-2 and add 3-7;
- Stage B2: retain historical replicate indices 0-3 and add 4-7.

Because screen states were not archived, all populations will be deterministically reconstructed from the historical baseline seed law; old-cohort state hashes and non-intervention metrics will be checked against the frozen records before the expanded results are interpreted.

For every population:
- corrected sequence-specific information: same within-segment permutation correction as the historical screen (`60` permutations);
- adaptive gain: unchanged historical definition;
- MP constant-endpoint loss: 8 matched continuation streams, 36 generations.

Setting summaries use 2,000 replicate-bootstrap draws across the 8 independently evolved populations.

The historical practical thresholds remain frozen:

- corrected information `DI = 0.01 bit`;
- MP intervention loss `DV = 0.25 fitness unit`;
- adaptive gain `DF = 1.0 fitness unit`.

The historical regime-classification logic is unchanged. No threshold will be altered after MP outcomes are inspected.

**Inferential role:** Stage A/B1/B2 remain prespecified **domain-mapping / robustness screening**, not confirmatory evidence, despite the improved `n=8` replication.

## 8. Stage C protocol sensitivity

After the expanded MP Stage A/B1/B2 screen is frozen:

- default representative remains `B2_default`;
- nearest-boundary representative is selected by the same historical normalized boundary-distance rule with deterministic design-ID tie breaking;
- baseline-evolution durations remain 100, 150 and 250 generations;
- intervention horizons remain 24, 36 and 60 generations;
- each protocol setting is expanded to **n=8 independently evolved populations**;
- MP constant-endpoint analysis uses 8 matched continuation streams per population;
- classification thresholds and summary logic remain unchanged.

## 9. Stage D targeted confirmation

After Stage C completion, Stage-D representatives are selected using the unchanged historical rule:

1. deepest `R2_viability_relevant` setting by depth, deterministic design-ID tie break;
2. deepest `R3_strong_adaptation` setting;
3. nearest-boundary setting;
4. `B2_default`;
5. exact duplicate design IDs are removed.

The default confirmation uses the core `p=1.0` population block (`n=20`). Each nondefault selected representative uses `n=8` independently evolved confirmatory populations generated by the historical Phase-6 confirm seed law.

For nondefault confirmations:
- complete 34-map MP panel;
- 16 matched continuation streams per map;
- 36-generation horizon;
- corrected retained-information coordinate with 200 within-segment permutations;
- constant and identity endpoints validated exactly;
- continuous frontier summaries as in the core p=1 frontier.

A nondefault setting is called MP viability-relevant in targeted confirmation only when the 95% replicate-bootstrap lower bound of the constant-endpoint `DeltaV_MP` exceeds the unchanged `0.25` fitness-unit threshold. Frontier monotonicity is reported as mechanistic/graded support, not as an exact minimum-information threshold.

## 10. Causal-specificity control family

The already frozen prospective 64-new-continuation MP six-contrast campaign is adopted as the migrated causal-specificity analysis. It is not rerun or selectively modified. Five of six prespecified contrasts pass the frozen BH rule; the acute default topology-mismatch contrast remains borderline/inconclusive and is reported as such.

## 11. Independent affinity-landscape generality

Reviewer-1 affinity-landscape generality remains a separate required Round-2 decision. After the migrated core and Stage-D representatives are frozen, an independent-landscape MP replication will be prespecified using the final migrated primary quantities. No landscape-general claim will be made before that phase is completed; alternatively, scope must remain conditional on the fixed affinity realization.

## 12. Figure policy

No manuscript figure is regenerated until the corresponding migrated scientific block is frozen. All figures are rebuilt programmatically from source tables; no generative image editor is used.

Expected impact after scientific freeze:
- Fig. 1: unchanged scientifically;
- Fig. 2: replace logit-average intervention schematic with MP probability-space weighted aggregation;
- Fig. 3: panels a-c unchanged; panel d regenerated;
- Fig. 4: regenerated around the continuous p=1 MP frontier; discrete semantic estimate retired as primary;
- Fig. 5: use already generated high-continuation MP causal-specificity figure, subject to final manuscript synchronization;
- Figs. 6-8: regenerated after expanded MP domain map, Stage C and Stage D freeze;
- Supplementary S1-S7: redesigned/regenerated where intervention-derived quantities appear.

## 13. No-retuning / stopping rules

- No intervention threshold, information threshold, adaptive-gain threshold, parameter setting, grouping-map panel, continuation horizon, representative-selection rule, or family-level inference rule may be changed in response to migrated outcomes.
- No selective additional replication of a single disappointing setting is permitted. Any precision extension must be applied to a prospectively defined family.
- If the migrated screen materially changes representative selection, the newly selected representatives are confirmed rather than retaining historically favorable representatives.
- If an analysis fails, the result is frozen and the claim is narrowed.

