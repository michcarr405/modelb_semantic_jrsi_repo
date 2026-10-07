# Round-2 confirmatory campaign — marginal-preserving causal-specificity controls

**Manuscript:** rsif-2026-0516.R1  
**Campaign:** R2 marginal-preserving rerun of all six frozen Phase-5 causal-specificity contrasts  
**Prespecification date:** 2026-10-02  
**Status:** frozen before outcome generation

## 1. Question

Round 1 used one affinity-logit grouping operator for all Phase-5 causal-specificity controls. Round-2 audit R2.2 showed that this operator changes segment-conditioned one-site local-state marginals as well as motif-specific dependence. This campaign asks whether the six historically prespecified Phase-5 contrasts survive when the constant-endpoint intervention is replaced by a population-frequency-weighted probability-space operator that preserves expected `P(Z|S)` for the current population.

The campaign is confirmatory with respect to the six historical contrast definitions. It does not redesign the control architecture after inspecting marginal-preserving outcomes.

## 2. Frozen historical inputs

Read-only inputs come from the Gate-8 Phase-5 archive and Phase-4 primary-fidelity archive.

Retain unchanged:

- primary parental-composition coupling `p = 1.0`;
- 20 matched independently evolved seed blocks;
- archived evolved populations for native/full selection, neutral selection, reduced selection, alternative topology A, alternative topology B, and temporally unstable topology;
- the two archived complete affinity-profile derangements per native population;
- the two archived topology-mismatch realizations per native population;
- the fixed alternative topologies A and B;
- the archived temporally unstable topology schedules;
- selection strengths used in the corresponding Round-1 continuations;
- two continuation indices per evaluation;
- 36-generation continuation horizon;
- independently evolved seed block as the inferential unit.

No population evolution is rerun and no control realization is regenerated.

## 3. Marginal-preserving constant intervention

For the evaluation affinity matrix used in a given control realization, define the native local-state kernel

`P0(z|m,s) = softmax((a_mz + beta 1[z=f(s)]) / Theta)`.

At each continuation generation `t`, for the current population and segment `s`, the complete-group marginal-preserving kernel is

`Q_t(z|s) = sum_m w_t(m|s) P0(z|m,s)`,

where `w_t(m|s)` is the empirical current frequency of motif identity `m` among motif windows in segment `s`.

Every motif window in segment `s` is sampled from the same `Q_t(.|s)`. Thus motif-specific local-state dependence is removed at the constant endpoint while expected `P(Z|S)` for that current population is preserved by construction.

For affinity-reassignment controls, `P0` is computed from the exact archived deranged affinity matrix. For topology controls, the exact archived evaluation topology is used. For the temporally unstable condition, the exact archived generation-specific topology schedule is used.

## 4. Pairing and random streams

The marginal-preserving continuation uses the same Round-1 continuation stream key as the corresponding archived actual continuation:

- continuation root seed: `2026073104`;
- pairing key: the archived `pairing_baseline_replicate`;
- continuation indices: `0` and `1`.

This preserves the Round-1 matched-random-number design. The archived actual viability is the paired reference. No new simulation random stream is introduced for the primary rerun.

For Round-2 bootstrap and paired-randomization summaries only, use analysis root seed `2026100201` with purpose-separated streams.

## 5. Six frozen contrasts

The six contrasts are unchanged from `PHASE_05_PLAN.md`:

1. full selection minus neutral selection;
2. full selection minus reduced selection;
3. native mapping minus complete affinity-profile reassignment;
4. native topology minus matched topology mismatch;
5. alternative stable-topology native evaluation minus cross-evaluation;
6. stable fixed-topology native evaluation minus temporally unstable topology.

For the two-realization affinity-reassignment and topology-mismatch controls, compute each realization separately and average only after obtaining one marginal-preserving intervention loss per realization, matching the historical hierarchy.

For the alternative-topology contrast, average the A-native and B-native intervention losses within seed block and compare with the within-seed mean of A-cross-B and B-cross-A. For stable-versus-unstable, use the same stable fixed reference: the within-seed mean of A-native and B-native.

## 6. Outcome and inference

For each evaluation realization and seed block:

`DeltaV_MP = V_actual - V_MP,constant`,

where both terms are 36-generation mean population fitness and `V_actual` is the exact archived matched actual continuation average.

Primary inference for each of the six contrasts:

- one contrast difference per matched independent seed block (`n=20`);
- mean difference;
- 95% paired complete-seed-block bootstrap interval from 2,000 resamples;
- two-sided paired sign-randomization with 9,999 randomizations;
- Benjamini-Hochberg adjustment across the six tests;
- number of positive seed-block differences.

A marginal-preserving contrast is classified as surviving the historical Gate-5 criterion only if its mean difference is positive and BH-adjusted `q < 0.05`.

## 7. Validation requirements

Before interpretation:

1. every requested archived state/specification must resolve;
2. archived actual records must contain exactly two continuations per realization;
3. the marginal-preserving expected `P(Z|S)` identity must be numerically validated on every starting state/evaluation kernel;
4. the sequence-independent kernel limit must yield no motif-specific dependence;
5. topology schedules for unstable evaluations must be read from the archived schedule files rather than regenerated if available;
6. Round-1 files remain unchanged.

## 8. Comparison with Round 1

Report side by side for every condition and every contrast:

- Round-1 original-operator mean intervention loss / mean contrast;
- Round-2 marginal-preserving mean intervention loss / mean contrast;
- marginal-preserving-to-original ratio when the original value is nonzero;
- sign concordance across seed blocks.

The comparison is descriptive; the primary inferential question is whether each of the six marginal-preserving contrasts is positive with BH-adjusted `q < 0.05`.

## 9. Interpretation rules

- If all six survive: the selection-, mapping-, topology-, and temporal-stability architecture remains supported after removing one-site marginal shifts as an explanation of the constant-endpoint loss.
- If only a subset survives: retain only those specific marginal-preserving causal-specificity claims; describe the remaining Round-1 contrasts as operator-specific sensitivity results.
- If none survive: the central marginal-preserving endpoint result may still stand, but the Round-1 control architecture cannot be used as evidence that the residual relational effect is selection/mapping specific.

No manuscript rewriting occurs until this campaign is frozen.
