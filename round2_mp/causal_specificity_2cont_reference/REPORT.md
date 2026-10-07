# Round-2 confirmatory marginal-preserving causal-specificity campaign

**Manuscript:** rsif-2026-0516.R1  
**Date:** 2026-10-02  
**Historical comparison:** Phase 5 / Gate 5 six prespecified causal-specificity contrasts  
**Status:** **5/6 contrasts survive the marginal-preserving operator; native-topology vs topology-mismatch does not pass**

## 1. Purpose

Round 1 tested six causal-specificity contrasts with the same affinity-logit grouping operator. Round-2 audit R2.2 showed that the original operator changes one-site segment-conditioned local-state marginals `P(Z|S)` as well as motif-specific dependence. This campaign therefore reran all six historical contrasts with a population-frequency-weighted probability-space **marginal-preserving constant intervention**, while leaving the historical evolved states, control realizations, topology schedules, pairing structure, continuation streams, horizon, and inferential hierarchy unchanged.

The design was frozen in `PRESPECIFICATION.md` before outcome generation. No contrast definition, control realization, threshold, or multiplicity rule was changed after results were observed.

## 2. Exact apples-to-apples design

The campaign retained:

- `p = 1.0`;
- 20 matched independently evolved seed blocks;
- the exact archived Phase-4 native/full-selection states;
- exact archived Phase-5 neutral, reduced-selection, alternative-A, alternative-B, and temporally unstable states;
- both archived affinity-profile derangements per native state;
- both archived topology-mismatch realizations per native state;
- exact archived fixed topologies A/B and unstable continuation schedules;
- the historical continuation root seed `2026073104`;
- continuation indices 0 and 1;
- 36 continuation generations;
- historical selection strength in each condition;
- independently evolved seed block as the sole inferential unit.

The only substantive intervention change was the constant endpoint.

For the evaluation affinity matrix in each realization, the native local-state kernel is

`P0(z|m,s)`.

At continuation generation `t`, the new constant intervention uses

`Q_t(z|s) = sum_m w_t(m|s) P0(z|m,s)`,

where `w_t(m|s)` is the current empirical motif frequency in segment `s`. Every motif in segment `s` samples from the same `Q_t`, removing motif-specific local-state dependence while preserving the expected `P(Z|S)` of the current population.

The outcome remains a model-fitness loss:

`DeltaV_MP = V_actual - V_MP,constant`.

## 3. Validation

All validation gates passed.

- Phase-5 evaluation specifications recovered: **220/220**.
- Native/full-selection baseline specifications added: **20/20**.
- Continuation-level matched observations: **480** (240 evaluation realizations × 2 continuations).
- Maximum starting-state expected-marginal preservation error: **4.21885e-14**.
- The original-operator seed-block metrics reconstructed from archived actual and constant rows with maximum absolute discrepancy **7.10543e-15** from the frozen Gate-5 metrics.
- Round-1 archive inputs were read only.

This establishes that the comparison below uses the exact historical control architecture.

## 4. Intervention-loss levels by condition

| Condition | Original operator mean loss | Marginal-preserving mean loss | MP / original | MP-positive seed blocks |
|---|---:|---:|---:|---:|
| Native/full selection | 11.9072 | **2.0911** | 0.176 | 20/20 |
| Neutral selection | 5.8911 | **0.4136** | 0.070 | 16/20 |
| Reduced selection | 8.3911 | **1.1139** | 0.133 | 18/20 |
| Affinity reassigned | 6.6916 | **1.5381** | 0.230 | 19/20 |
| Topology mismatch | 10.0842 | **1.8863** | 0.187 | 20/20 |
| Alternative topology A, native evaluation | 11.3692 | **2.8882** | 0.254 | 20/20 |
| Alternative topology A, cross-evaluated under B | 8.9207 | **1.8943** | 0.212 | 19/20 |
| Alternative topology B, native evaluation | 11.7998 | **2.3189** | 0.197 | 20/20 |
| Alternative topology B, cross-evaluated under A | 8.6961 | **1.5743** | 0.181 | 19/20 |
| Alternative stable native mean | 11.5845 | **2.6035** | 0.225 | 20/20 |
| Alternative cross-evaluated mean | 8.8084 | **1.7343** | 0.197 | 20/20 |
| Temporally unstable topology | 10.2498 | **1.6414** | 0.160 | 20/20 |

The absolute intervention losses attenuate substantially under marginal preservation, as expected from R2.2. The important question for the control architecture is whether the **matched differences among conditions** remain positive and inferentially supported.

## 5. Six historical contrasts under the marginal-preserving operator

| Contrast | Original mean contrast | MP mean contrast | 95% paired bootstrap interval | Positive blocks | p | BH q | Historical criterion |
|---|---:|---:|---:|---:|---:|---:|---|
| Full selection − neutral | 6.0161 | **1.6775** | **[1.2467, 2.0915]** | 18/20 | 0.0001 | 0.0003 | **Pass** |
| Full selection − reduced | 3.5161 | **0.9772** | **[0.3561, 1.6260]** | 16/20 | 0.0045 | 0.00675 | **Pass** |
| Native mapping − affinity reassignment | 5.2156 | **0.5530** | **[0.1370, 1.0102]** | 14/20 | 0.0167 | 0.02004 | **Pass** |
| Native topology − topology mismatch | 1.8230 | **0.2048** | **[-0.1406, 0.5489]** | 11/20 | 0.2706 | 0.2706 | **Does not pass** |
| Alternative native − cross-evaluated | 2.7761 | **0.8693** | **[0.5214, 1.2266]** | 17/20 | 0.0001 | 0.0003 | **Pass** |
| Stable fixed topology − unstable topology | 1.3347 | **0.9622** | **[0.5363, 1.3838]** | 14/20 | 0.0008 | 0.0016 | **Pass** |

**Five of the six historically prespecified contrasts survive the marginal-preserving intervention under the unchanged Gate-5 criterion.**

The single exception is the direct **native-topology minus matched-topology-mismatch** contrast. Its mean remains positive (`+0.2048` fitness units), but the interval crosses zero, only 11/20 seed blocks are positive, and the BH-adjusted value is `q = 0.2706`.

## 6. How much of each historical contrast remains?

The marginal-preserving contrast as a fraction of the original contrast is:

- full minus neutral: **27.9%**;
- full minus reduced: **27.8%**;
- native minus affinity reassignment: **10.6%**;
- native topology minus topology mismatch: **11.2%**;
- alternative native minus cross-evaluated: **31.3%**;
- stable fixed minus unstable: **72.1%**.

Thus the original operator amplified most contrast magnitudes through its one-site marginal effects. The stable-versus-unstable contrast is the least attenuated and remains especially strong under marginal preservation.

## 7. Scientific interpretation

### 7.1 Selection dependence survives

The marginal-preserving losses show a clear mean ordering:

`full selection = 2.0911 > reduced selection = 1.1139 > neutral selection = 0.4136`.

Both prespecified selection contrasts pass after BH correction. Therefore the residual sequence-dependent relational fitness effect is not merely an architectural consequence of having motif-specific affinities; sustained selection increases that effect even after expected `P(Z|S)` shifts are removed from the intervention.

### 7.2 Affinity-mapping specificity survives, but is strongly attenuated

Reassigning complete affinity profiles lowers the marginal-preserving loss from 2.0911 to 1.5381 units. The matched contrast is positive in 14/20 seed blocks and remains significant after six-test BH correction (`q = 0.02004`). This supports a residual dependence on the evolved motif-to-affinity assignment, although the contrast is only about 11% as large as under the original operator.

### 7.3 The direct matched topology-mismatch result does not survive

Under the original operator, native evaluation exceeded topology mismatch by 1.8230 units. Under the marginal-preserving operator the difference falls to 0.2048 units and does not pass inference.

Accordingly, the Round-1 topology-mismatch contrast should **not** be used in the revision as independent evidence that the residual marginal-preserving relational effect specifically depends on the native default topology. Its original effect was largely associated with components removed by marginal preservation, including the interaction between intervention-induced local-state marginal shifts and the changed fitness topology.

This does not mean that topology alignment is irrelevant in general, because the independently evolved alternative-topology test gives a different result.

### 7.4 Historical topology alignment survives in the alternative-topology cross-evaluation

For populations evolved under the two prespecified alternative stable topologies, the mean marginal-preserving loss is 2.6035 under their native evaluation and 1.7343 under cross-evaluation. The native-minus-cross contrast is +0.8693 units, positive in 17/20 blocks, with `q = 0.0003`.

This is stronger evidence for **history-dependent topology alignment** than the default-state topology-mismatch test because it asks whether populations evolved under different stable topologies are more dependent on the topology under which they evolved.

### 7.5 Temporal stability survives strongly

The alternative-stable native mean is 2.6035 units versus 1.6414 under the temporally unstable topology condition. The contrast is +0.9622 units with `q = 0.0016` and retains approximately 72% of its original magnitude. Temporal stability is therefore the most operator-robust of the six historical causal-specificity contrasts by proportional retention.

## 8. Revised status of the Round-1 control architecture

The control architecture remains scientifically relevant, but it should no longer be summarized as “all six controls independently confirm the same information-specific effect.” The marginal-preserving rerun supports a more precise structure:

**Supported under the marginal-preserving operator:**

1. selection dependence — full > neutral;
2. selection dependence — full > reduced;
3. motif-to-affinity mapping specificity — native > complete affinity reassignment;
4. historical topology alignment — alternative native > cross-evaluated;
5. temporal mapping stability — stable > unstable.

**Not supported under the marginal-preserving operator:**

6. default native topology > matched topology mismatch.

Thus the broad claim that **selection and stable historically matched mappings strengthen the residual sequence-dependent relational fitness effect** remains supported, but the direct default-topology-mismatch comparison must be reported as operator-sensitive rather than as an independently surviving line of evidence.

## 9. Manuscript implication

The strongest defensible Round-2 causal-specificity statement is now:

> At the primary fidelity, the future-fitness consequence of removing motif-specific local-state dependence persisted under a population-frequency-weighted probability-space intervention that preserves expected segment-conditioned local-state marginals. The residual effect was larger after full than weakened or neutral selection, was reduced by complete affinity-profile reassignment, was larger when populations evolved under alternative stable topologies were evaluated under their own rather than a cross-evaluated topology, and was reduced under temporally unstable topology. A separate matched default-topology mismatch contrast did not remain distinguishable from zero under the marginal-preserving intervention.

This statement preserves the positive evidence while explicitly retaining the one failed historical contrast.

## 10. Decision

**Round-2 marginal-preserving causal-specificity campaign: PARTIAL PASS (5/6 historical contrasts).**

No retuning is warranted. The failed topology-mismatch result should be carried forward as a genuine limitation and used to narrow the revised causal-specificity wording.
