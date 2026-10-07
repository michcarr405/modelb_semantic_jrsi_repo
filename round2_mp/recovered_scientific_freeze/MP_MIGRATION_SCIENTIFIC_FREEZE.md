# JRSI Round-2 study-wide MP migration — integrated scientific freeze

**Status:** study-wide scientific migration complete; ready for figure/manuscript regeneration  
**Date:** 2026-10-02  
**Primary intervention:** population-frequency-weighted probability-space grouping intervention preserving expected one-site `P(Z|S)` for the current intervention-branch population.

## 1. Core compositional-coupling sweep

Using the 400 frozen Round-1 baseline populations, the MP constant-endpoint intervention-induced future-fitness loss is positive in all 20 selective populations at every `p=0.1,...,1.0`, while the agnostic condition is an exact analytical zero. Mean selective `DeltaV_MP` rises from 0.1018 at p=0.1 to 2.2481 at p=1.0; all ten tests have BH q=0.0001.

**Frozen interpretation:** motif-specific dependence has a reproducible causal future-fitness effect across the full tested coupling sweep after expected one-site segment-conditioned local-state marginals are preserved.

## 2. Primary continuous p=1 MP frontier

The prospective 64-new-continuation, 34-map p=1 frontier shows a strong graded relationship between corrected retained information and fitness recovery:

- positive within-population information-recovery Spearman correlation in 20/20 independently evolved populations;
- mean rho = 0.9240, median rho = 0.9429, minimum rho = 0.5859;
- map-averaged rho across the 34 coordinates = 0.9905;
- balanced-random and affinity-rank families are perfectly monotonic at the map-average level; contiguous-substring remains strongly monotonic (rho=0.9429) but not strictly nondecreasing;
- constant-endpoint MP loss = 2.2858 fitness units, 95% complete-baseline bootstrap 1.9121–2.6760, positive in 20/20, sign-randomization p=0.0001.

The old first-99%-recovery semantic estimate is retired as a primary quantity. As a secondary audit, identity is first by the mean frontier in only 2/20 populations, six populations have a technically resolved nonidentity crossing, and fourteen are technically unresolved.

**Frozen interpretation:** the stable object is a continuous graded information-recovery relation, not an operator-independent identity requirement or exact minimum-information threshold.

## 3. Expanded n=8 domain map

All 65 historical Stage A/B1/B2 settings were retained and prospectively expanded to eight independently evolved populations per setting (520 total). Historical states reproduce for the old cohort. Migrated classifications are:

- Stage A: 8 null, 10 syntactic-only, 10 viability-relevant, 4 strong-adaptation;
- Stage B1: 2 null, 11 syntactic-only, 1 viability-relevant, 1 strong-adaptation, 1 boundary/uncertain;
- Stage B2: 0 null, 1 syntactic-only, 1 viability-relevant, 15 strong-adaptation.

Sixteen of 65 settings change classification relative to Round 1, predominantly because effects previously called viability-relevant become syntactic-only under the cleaner MP operator.

**Frozen interpretation:** broad domain coverage remains, but the MP migration materially narrows the region in which sequence-dependent organization is viability-relevant. Stage A/B1/B2 remain domain-mapping/robustness screens, not confirmatory tests.

## 4. Stage C protocol sensitivity at n=8

The MP-selected representatives are B2_default and B2_stride7. Across all six frozen evolution-duration/intervention-horizon variants:

- B2_default remains strong-adaptation in all six;
- B2_stride7 remains viability-relevant in all six and alternates between viability-relevant and strong-adaptation.

**Frozen interpretation:** the default MP result is protocol robust, and the migrated near-boundary/viability representative remains on the positive side of the practical intervention threshold across the tested protocol variations.

## 5. Stage D targeted MP confirmation

Final nondefault representatives selected by the unchanged historical rule:

- D0 A_p2_a3: DeltaV_MP=0.4845, 95% CI 0.4601–0.5127, 8/8 positive, median within-population rho=0.693;
- D1 B2_reward3: DeltaV_MP=3.5021, 95% CI 2.7219–4.6422, 8/8 positive, median rho=0.921;
- D2 B2_stride7: DeltaV_MP=1.6436, 95% CI 1.2598–1.9808, 8/8 positive, median rho=0.935.

Identity recovery is exact in all 24 nondefault confirmation populations. The MP marginal-preservation audit is at numerical precision.

## 6. Causal-specificity architecture under MP

The already frozen prospective 64-new-continuation six-contrast campaign is adopted unchanged. Five of six historical contrasts survive the MP operator:

- full minus neutral selection: survives;
- full minus reduced selection: survives;
- native affinity mapping minus reassigned: survives;
- default native topology minus acute matched mismatch: borderline/inconclusive under frozen q<0.05 rule;
- alternative-native minus cross-evaluated topology: survives;
- stable fixed minus temporally unstable topology: survives.

**Frozen interpretation:** selection dependence, affinity-mapping specificity, historical topology alignment and temporal stability survive marginal preservation. The acute default topology-mismatch contrast is not independently confirmed and should not carry the historical-mapping claim.

## 7. Independent affinity-landscape generality

Eight new independent affinity landscapes were tested, with eight independently evolved populations nested within each landscape-setting cell. The affinity landscape is the inferential unit.

- B2_default: mean DeltaV_MP=2.3724, landscape-bootstrap 95% CI 2.1750–2.5603; 8/8 positive landscapes; practical 0.25 lower-bound criterion met in 8/8 landscapes.
- B2_reward3: mean 3.2439, CI 2.9237–3.6159; 8/8 positive; practical criterion 8/8.
- B2_stride7: mean 1.5496, CI 1.4812–1.6229; 8/8 positive; practical criterion 8/8.
- A_p2_a3: mean 0.2249, CI 0.0810–0.3929; 7/8 positive landscape means; exact landscape sign-randomization p=0.03125; only 3/8 landscape cells have nested-population lower bounds above the unchanged 0.25 practical threshold.

**Frozen interpretation:** the primary default, strong-adaptation, and stride-7 positive regimes generalize strongly across independent affinity landscapes. A_p2_a3 has a positive across-landscape causal effect but its stronger practical viability-relevant classification is landscape sensitive and must not be presented as landscape-general.

## 8. Claim matrix after migration

### Strongly supported

1. Corrected sequence-specific information distinguishes selective from agnostic organization after position conditioning.
2. Removing motif-specific local-state distinctions reduces future model fitness even while expected `P(Z|S)` is preserved.
3. The MP causal effect is positive across the full tested compositional-coupling sweep in the selective regime and exactly zero in the agnostic regime.
4. Retained corrected information and MP fitness recovery show a strong graded relationship at the primary p=1 setting.
5. Full selection strengthens the MP causal effect relative to neutral and reduced selection.
6. Affinity mapping, historical stable topology, and temporal stability contribute to the MP causal effect.
7. The default, reward3 and stride7 results replicate across eight independent affinity landscapes.

### Supported with explicit narrowing

1. Broad parameter/structural coverage persists, but the MP operator narrows the viability-relevant region relative to Round 1.
2. A_p2_a3 is a valid confirmation in the historical landscape and has a positive across-landscape mean causal effect, but its practical viability-relevant classification is not landscape invariant.
3. The default acute topology-mismatch contrast is borderline/inconclusive under MP; historical topology specificity should rely on the alternative-topology cross-evaluation result.

### Retired as primary claims

1. The full original logit-operator loss as a pure "value of information".
2. An operator-independent identity requirement.
3. A precise first-99%-recovery semantic/minimum-information estimate.
4. A universal compression threshold inferred from the tested grouping maps.

## 9. Production consequences

The scientific analysis is now sufficiently frozen to begin programmatic regeneration of Figures 2–8 and affected Supplementary Figures S1–S7. Figure 1 remains scientifically unchanged. The original Round-1 operator should be retained only as a historical/sensitivity analysis, not as the primary causal operator.
