# Round-2 high-continuation marginal-preserving causal-specificity replication

**Manuscript:** rsif-2026-0516.R1  
**Date:** 2026-10-02  
**Primary design:** 20 independent seed blocks; all six historical contrasts; 64 entirely new continuation streams per evaluation realization (indices 2–65); 36 generations; marginal-preserving probability-space, population-frequency-weighted constant intervention.  
**Status:** **5/6 contrasts pass the unchanged historical criterion; the native-topology vs matched-topology-mismatch contrast remains borderline and does not pass.**

## 1. Prospective design

The campaign was frozen before any of the 64 new continuation outcomes were generated. Because the earlier two-continuation marginal-preserving results were already known, this is a prospectively specified **precision/replication campaign**, not an outcome-naive first confirmatory test. All six contrasts were rerun together; there was no contrast-specific continuation count or stopping rule. Historical continuation indices 0–1 were excluded from the primary analysis.

The primary campaign used continuation indices 2–65 under the historical continuation root seed `2026073104`. Temporally unstable schedules were generated with the historical Phase-5 schedule protocol and root seed `2026073105`. The independent evolved seed block remained the inferential unit (`n=20`); the 64 continuations are nested technical replicates and do not increase inferential n.

## 2. Validation

- 220/220 archived Phase-5 evaluation specifications and 20/20 native/full baseline states resolved.
- Primary continuation rows: **15,360** (= 240 evaluation realizations × 64 new continuations).
- Every evaluation realization contains exactly 64 new continuations.
- Maximum starting-state expected-marginal preservation error: **4.219e-14**.
- Actual and marginal-preserving branches used identical continuation keys; unstable pairs shared the same prospectively generated topology schedule.

## 3. Primary 64-new-continuation results

| Contrast | 2-cont MP mean | 64-new MP mean | 95% bootstrap CI | Positive blocks | BH q | Frozen criterion |
|---|---:|---:|---:|---:|---:|---|
| Full selection − neutral | 1.6775 | **1.9212** | [1.4057, 2.4399] | 18/20 | 0.00060 | **Pass** |
| Full selection − reduced | 0.9772 | **1.0234** | [0.4514, 1.5973] | 15/20 | 0.00504 | **Pass** |
| Native mapping − affinity reassignment | 0.5530 | **0.7246** | [0.3195, 1.1845] | 17/20 | 0.00225 | **Pass** |
| Native topology − topology mismatch | 0.2048 | **0.3415** | [0.0441, 0.6590] | 13/20 | 0.05010 | **Does not pass** |
| Alternative native − cross-evaluated | 0.8693 | **0.8138** | [0.5160, 1.1122] | 17/20 | 0.00090 | **Pass** |
| Stable fixed − temporally unstable | 0.9622 | **0.8962** | [0.4665, 1.2891] | 17/20 | 0.00225 | **Pass** |

Five contrasts reproduce decisively. The topology-mismatch contrast moves in the positive direction with higher technical precision, but under the **prespecified randomization-plus-BH criterion** it still does not pass: mean `+0.3415`, 13/20 seed blocks positive, two-sided paired sign-randomization `p = 0.0501`, BH `q = 0.0501`. The paired-bootstrap interval is positive (`0.0441–0.6590`), so this result is best described as **borderline/inconclusive under the frozen primary inferential rule**, not as evidence of no effect.

## 4. Condition-level marginal-preserving losses

| Condition | Mean MP loss | Positive seed blocks |
|---|---:|---:|
| Native/full selection | 2.2737 | 20/20 |
| Neutral selection | 0.3525 | 15/20 |
| Reduced selection | 1.2503 | 19/20 |
| Affinity reassigned | 1.5491 | 20/20 |
| Topology mismatch | 1.9322 | 20/20 |
| Alternative A native | 2.8669 | 20/20 |
| A evaluated under B | 2.0010 | 20/20 |
| Alternative B native | 2.2765 | 20/20 |
| B evaluated under A | 1.5147 | 20/20 |
| Temporally unstable | 1.6755 | 20/20 |
| Alternative native mean | 2.5717 | 20/20 |
| Alternative cross mean | 1.7578 | 20/20 |

The selection ordering remains clear: full selection `2.2737` > reduced selection `1.2503` > neutral selection `0.3525`. Historical topology alignment also remains visible: alternative-native mean `2.5717` > alternative-cross mean `1.7578`.

## 5. Technical precision gained

The median technical standard error of a 64-continuation seed-block contrast mean is approximately:

| Contrast | Median technical SE |
|---|---:|
| Alternative native − cross-evaluated | 0.0657 |
| Full selection − neutral | 0.0709 |
| Full selection − reduced | 0.0971 |
| Native mapping − affinity reassignment | 0.0947 |
| Native topology − topology mismatch | 0.0830 |
| Stable fixed − temporally unstable | 0.0714 |

Thus the higher-continuation campaign substantially reduces technical continuation noise. Remaining uncertainty in the six paired tests is now dominated much more by heterogeneity among the 20 independently evolved seed blocks than by the two-continuation Monte Carlo estimate.

## 6. Relation to the original Round-1 operator

| Contrast | Original operator mean | 64-new MP mean | Fraction retained |
|---|---:|---:|---:|
| Full selection − neutral | 6.0161 | 1.9212 | 31.9% |
| Full selection − reduced | 3.5161 | 1.0234 | 29.1% |
| Native mapping − affinity reassignment | 5.2156 | 0.7246 | 13.9% |
| Native topology − topology mismatch | 1.8230 | 0.3415 | 18.7% |
| Alternative native − cross-evaluated | 2.7761 | 0.8138 | 29.3% |
| Stable fixed − temporally unstable | 1.3347 | 0.8962 | 67.1% |

The original operator amplified most control contrasts through the one-site marginal changes that the Round-2 intervention removes. Temporal stability remains the most operator-robust contrast proportionally, retaining about 67% of the original contrast magnitude.

## 7. Prespecified combined-66 sensitivity analysis

The secondary analysis combining the two already-observed historical continuations with the 64 new continuations gives the same qualitative result: **5/6 pass**, and native topology minus topology mismatch remains just outside the frozen criterion (`mean = 0.3374`, 12/20 positive, `q = 0.0523`). This sensitivity analysis therefore does not change the primary conclusion.

## 8. Scientific interpretation

The higher-continuation rerun stabilizes the Round-2 causal-specificity picture. Under the marginal-preserving intervention, the residual motif-dependent future-fitness effect is reproducibly stronger after full selection than after neutral or reduced selection; it is reduced by complete affinity-profile reassignment; it is larger when populations evolved under alternative stable fitness topologies are evaluated under their own historical topology rather than cross-evaluated; and it is reduced when the topology is temporally unstable.

The direct default native-topology versus matched-topology-mismatch contrast should remain **separate and qualified**. Higher continuation precision makes its mean more clearly positive, but the distribution across independent evolved seed blocks is heterogeneous (13 positive, 7 negative), and it narrowly fails the prespecified paired-randomization/BH threshold. It should not be promoted to an independently confirmed marginal-preserving specificity result.

Accordingly, the stable interpretation remains: **five components of the historical control architecture survive the cleaner intervention; the default acute topology-mismatch control remains borderline/operator-sensitive.**

## 9. Frozen decision

**High-continuation marginal-preserving causal-specificity campaign: PARTIAL PASS (5/6).** No retuning, selective extension, or alternative significance rule is warranted. The topology-mismatch contrast should be reported transparently as borderline under higher-continuation replication and non-passing under the frozen primary criterion.
