# GENERALITY_ANALYSIS.md

## Scope

This record reports the prespecified Phase 6 focused model-structure and parameter-robustness analysis. It applies the staged, non-factorial design frozen in `PHASE_06_PLAN.md` and decisions D26–D30. Gates 1–5, D16–D25, and all archived Phase 4 and Phase 5 states remain unchanged.

The result is a **model-domain generality decision**, not a claim of chemical realism, historical occurrence, or universality over all possible prebiotic systems.

## Regime definitions

Each design point was classified from independently evolved baseline populations using 95% replicate bootstrap intervals and fixed preproduction thresholds:

- information threshold: `0.01` bit for bias-corrected `I(M;Z|S)`;
- value-of-information threshold: `0.25` model-fitness unit;
- sustained adaptive-gain threshold: `1.0` model-fitness unit.

The prespecified classes were:

- **R0 — null:** corrected sequence-specific information does not exceed its practical null;
- **R1 — syntactic-only:** corrected information is positive, but value of information is not detectably positive;
- **R2 — viability-relevant:** corrected information and value of information are positive, without confirmed strong adaptive gain;
- **R3 — strong adaptation:** R2 plus sustained selection-driven fitness gain;
- **boundary/uncertain:** interval evidence crosses one or more practical thresholds.

Boundary points were not counted as positive evidence.

## Production design and completed sample

| Stage | Purpose | Design points | Independent populations |
|---|---|---:|---:|
| A | Focused mechanistic map plus low/high positional-ratio points | 32 | 128 |
| B1 | Global Latin-hypercube screen | 16 | 48 |
| B2 | Anchored structural controls | 17 | 68 |
| C | Duration and intervention-horizon sensitivity | 12 | 48 |
| D | Full D20-analogue semantic confirmation | 3 nondefault representatives | 24 |

Stage D additionally reused the archived 20-population Phase 4 default reference rather than rerunning it. Each nondefault Stage D population had 34 unique intervention maps, two nested continuation seeds per map, a 36-generation horizon, exact constant and identity endpoints, actual retained information, and explicit target/censoring fields.

## Stage A — focused mechanistic map

Of 32 points:

- 8 were R0;
- 0 were R1;
- 19 were R2;
- 4 were R3;
- 1 was boundary/uncertain.

Thus, `23/32 = 0.71875` were definitively R2 or R3, exceeding the prespecified broad-generality requirement of 20%.

The mechanistic map separated three behaviors. Zero affinity variance remained null across parental-composition coupling. Positive affinity/noise ratios produced viability-relevant information over a broad part of the tested plane, including at incomplete parental coupling. Strong adaptation was more restricted: at the default positional ratio it occurred at `p=1.0`, and one high-positional-ratio Latinized point reached R3 at `p≈0.904`. This supports a broad viability-relevant region but a narrower strong-adaptation region.

## Stage B1 — global space-filling screen

Of 16 Latin-hypercube points:

- 2 were R0;
- 8 were R1;
- 5 were R2;
- 1 was R3.

Thus, `6/16 = 0.375` were definitively R2 or R3, exceeding the broad-generality requirement of 15%.

The eight R1 points are scientifically important: sequence-specific statistical information was common in the sampled domain, but it did not automatically become viability-relevant. The screen therefore preserved the intended distinction between syntactic information and causal contribution to future model fitness.

## Stage B2 — anchored structural controls

The default anchor and 16 one-change controls yielded:

- 15 R3 points;
- 1 R2 point;
- 1 R1 point.

All four prespecified structural families contained at least one R2/R3 setting:

| Structural family | Positive support | Main result |
|---|---|---|
| Window density | Yes | Strides 2 and 5 remained R3; stride 7 remained R2 |
| Positional structure | Yes | 2/8 segments, reversed order, and non-heritable boundary jitter remained R3 |
| Metabolite-state count | Yes | Matched 3- and 6-state variants remained R3 |
| Fitness formulation/scale | Yes | Reward, penalty, and floor variants remained R3 |

The important exception was **fraction-normalized fitness**, which was R1 rather than R2/R3 (`VOI mean ≈0.171`). The semantic effect is therefore not invariant to every fitness normalization. Broad support means persistence across multiple nontrivial structural alternatives, not insensitivity to all formulations.

## Stage C — protocol sensitivity

The default anchor remained R3 for all tested baseline durations (`100`, `150`, `250` generations) and all tested intervention horizons (`24`, `36`, `60` generations). Its value-of-information lower interval remained far above the practical threshold in every protocol variant.

The nearest-boundary point alternated between R1 and boundary/uncertain across duration and horizon. This is expected for a point selected specifically for proximity to the decision boundary and shows that the classifier did not force marginal cases into positive regimes.

## Stage D — full semantic confirmation

The deterministic representative set contained the deepest R2 point, deepest R3 point, nearest boundary point, and archived default anchor.

| Representative | Screen class | Independent populations | VOI mean | 95% bootstrap interval | Confirmed above 0.25? |
|---|---|---:|---:|---:|---|
| `A_high_2` | R2 | 8 | 4.4637 | 4.4507–4.4778 | Yes |
| `B2_reward3` | R3 | 8 | 18.3376 | 17.3771–19.2311 | Yes |
| `A_low_3` | Boundary | 8 | 0.2220 | 0.1870–0.2527 | No |

All 24 nondefault Stage D populations recovered identity information and identity viability exactly. All targets were reached, no estimate was imputed, and no right-censored case occurred. The boundary representative correctly failed confirmatory positivity.

The archived Phase 4 default reference also remained valid: all 20 identity endpoints recovered, all targets were reached, and mean value of information was approximately `11.9072`.

## Gate 7 decision

The prespecified broad-generality criteria were evaluated without visual override:

| Criterion | Requirement | Result |
|---|---|---|
| Stage A R2/R3 fraction | at least 20% | 71.875% — pass |
| Stage B1 R2/R3 fraction | at least 15% | 37.5% — pass |
| Structural-family persistence | at least 3 of 4 | 4 of 4 — pass |
| Confirmatory semantic analysis | archived default plus at least 2 nondefault positives | default plus 2 — pass |
| Endpoint/archive/censoring integrity | no failure | pass |

**Gate 7 PASSED: BROAD GENERALITY SUPPORTED within the prespecified Model B design domain.**

## Interpretation and limits

The corrected result is not confined to one default parameter vector. Viability-relevant sequence-dependent information persisted across a substantial portion of the focused mechanistic map, a non-factorial global screen, and multiple window, positional, state-space, and fitness-scale variants. Strong selection-driven fitness gain occupied a narrower region than viability relevance.

The supported claim remains bounded:

> Within the tested sequence-explicit compositional-resampling model, selection-dependent and mapping-specific viability-relevant information persists across multiple parameter and structural alternatives, while null, syntactic-only, boundary, viability-relevant, and strong-adaptation regions remain distinguishable.

This does not establish universality, biochemical realism, a historical prebiotic transition, semantic compression, or robustness to every possible fitness formulation. In particular, the fraction-normalized variant weakened the result to syntactic-only, and the Stage C boundary point remained protocol-sensitive.
