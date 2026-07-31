# FROZEN_CLAIMS_AND_LIMITATIONS.md

## Project

**Manuscript:** `rsif-2026-0516`  
**Project:** JRSI Major Revision — Semantic Information in Model B  
**Freeze date:** 2026-07-31  
**Evidence base:** Passed Gates 4, 5, 7, and 8

## 1. Frozen claim class

The central result has **strong support within the tested Model B design domain**.

This is a model-specific causal and generality result. It is not a universality result, a chemical-realism result, or a historical reconstruction of abiogenesis.

## 2. Primary frozen claim

> **Within the tested sequence-explicit, Wright–Fisher-like compositional-resampling model, inherited sequence-dependent motif–local-state information can become causally relevant to future mean model fitness. At the primary fidelity, full selection under a stable native motif-affinity/fitness mapping produces an additional viability-relevant information component beyond the nonzero sensitivity built into the model architecture. This excess is reduced by weakening or removing selection, reassigning complete affinity profiles, evaluating under nonnative matched fitness topologies, cross-evaluating populations evolved under alternative stable topologies, and removing temporal mapping stability. The effect persists across multiple parameter and structural alternatives while null, syntactic-only, boundary, viability-relevant, and strong-adaptation regions remain distinguishable.**

This wording is the maximum-strength result-level claim authorized for manuscript production.

## 3. Evidence supporting the claim

### 3.1 Corrected core result

Phase 4 analyzed 400 independently evolved baseline populations and 28,000 continuation rows using position-conditioned information, within-segment permutation correction, actual retained information, one frontier per evolved population, two nested continuation seeds per map, and a 36-generation future-fitness horizon.

At the primary fidelity `p = 1.0`:

- corrected conditional information differed by `0.2534183` bits between selective and sequence-agnostic regimes;
- the replicate-level permutation p-value was `0.0001`;
- value of information differed by `11.9071864` model-fitness units;
- the replicate-level permutation p-value was `0.0001`;
- every identity endpoint recovered information and viability exactly;
- all 40 primary-fidelity targets were reached, with no imputed censored estimate.

### 3.2 Causal specificity

Phase 5 used 20 matched independently evolved seed blocks. Every prespecified paired value-of-information contrast was positive and survived Benjamini–Hochberg correction across the six tests (`q = 0.0001` for each):

| Contrast | Mean difference | 95% paired-bootstrap interval |
|---|---:|---:|
| Full selection minus neutral | 6.0161 | 4.9878–6.9431 |
| Full selection minus reduced | 3.5161 | 2.6042–4.4026 |
| Native minus affinity-reassigned | 5.2156 | 4.3843–6.1938 |
| Native minus topology-mismatch | 1.8230 | 1.1257–2.5401 |
| Alternative-native minus cross-evaluated | 2.7761 | 2.0839–3.4558 |
| Stable fixed topology minus unstable topology | 1.3347 | 0.8940–1.7830 |

These controls support selection dependence, mapping specificity, and a requirement for temporal stability of the mapping within the implemented model.

### 3.3 Generality within the tested domain

Phase 6 found:

- `23/32 = 71.875%` Stage A points in viability-relevant or strong-adaptation regimes;
- `6/16 = 37.5%` Stage B1 points in those regimes, with eight additional syntactic-only points;
- positive support in all four structural families: window density, positional structure, metabolite-state count, and fitness formulation/scale;
- two nondefault full semantic confirmations with value-of-information lower 95% bounds above `0.25`;
- exact identity recovery and complete target attainment for all 24 nondefault Stage D populations.

The nondefault confirmatory estimates were:

- `A_high_2`: `4.4637` (`4.4507–4.4778`);
- `B2_reward3`: `18.3376` (`17.3771–19.2311`).

The nearest-boundary representative did not confirm above the practical value-of-information threshold: `0.2220` (`0.1870–0.2527`).

## 4. Required claim distinctions

The manuscript must distinguish all of the following.

### 4.1 Statistical association versus causal contribution

- `I(M;Z)` is total motif–local-state association.
- `I(M;Z|S)` controls positional segment structure.
- the within-segment permutation-corrected quantity estimates sequence-specific association beyond finite-sample bias;
- `I(g(M);Z|S)` is actual retained information under a specific grouping map;
- value of information and the replicate-specific semantic estimate are intervention-dependent causal quantities tied to the prespecified future-fitness function.

None of these quantities may be used interchangeably.

### 4.2 Built-in causal channel versus evolved mapping-specific enrichment

The architecture contains a causal path from motif affinity to sampled local states and from local-state adjacency to fitness. The result is not that a causal channel exists. The result is that evolution under full selection and a stable native mapping produces an additional mapping-specific viability contribution relative to the prespecified disruption controls.

### 4.3 Viability relevance versus strong adaptation

Viability-relevant information occupies a broader tested region than strong sustained fitness gain. The manuscript must not equate nonzero value of information with a strong adaptive increase.

### 4.4 Model-domain breadth versus universality

“Broad generality” means that the result persists across the prespecified Model B parameter and structural alternatives. It does not mean invariance to every possible model formulation or applicability to all prebiotic systems.

## 5. Frozen limitations

The following limitations are mandatory in the manuscript and response letter.

1. **Operational semantics.** “Semantic information” means model-defined viability-relevant information under the specified counterfactual intervention and future-fitness function. It is not a claim of linguistic meaning, genetic coding, or a complete biological information system.

2. **Abstract transmission operator.** The population update is a fitness-weighted, Wright–Fisher-like compositional-resampling transition. Parent-derived oligomer identities are sampled with replacement, non-parental identities come from an idealized uniform sequence reservoir, and `p` measures parent–offspring compositional coupling. The model does not simulate literal molecular retention, mass conservation, membrane growth, synthesis chemistry, or two-daughter physical fission.

3. **Transient local-state labels.** Window-level metabolite variables are transient probabilistic local chemical-state assignments. They are not simultaneous bound ligand inventories and do not model steric exclusion, binding kinetics, copy number, metabolite production, or depletion.

4. **Built-in architecture.** A motif-affinity/local-state/fitness causal path is specified by construction. The disruption controls show selection-dependent and mapping-specific enrichment beyond that sensitivity, but they do not establish that all measured value of information was generated by evolution.

5. **Intervention dependence.** Semantic estimates depend on the D16–D20 map panel, discrete upper-frontier rule, strict one-percent target, 36-generation horizon, and mean future fitness. The primary panel is conservative and excludes affinity-profile k-means. The results do not establish a unique or universal semantic bit value.

6. **No semantic-compression claim.** A positive semantic estimate or syntactic–semantic gap does not by itself demonstrate an efficient code, minimal representation, or biological compression architecture.

7. **No universal fitness-formulation invariance.** The fraction-normalized fitness variant was classified as syntactic-only in the anchored structural analysis. The effect is therefore not invariant to every fitness normalization.

8. **Boundary sensitivity.** A representative selected near the practical regime boundary remained sensitive to baseline duration and intervention horizon and failed full positive confirmation. Marginal cases must be described as boundary or uncertain, not forced into a positive regime.

9. **No critical-threshold claim.** The frozen analyses identify fidelity-dependent changes, regime boundaries, and transition regions. They do not establish a thermodynamic critical point or universal sharp threshold.

10. **No historical or chemical reconstruction.** The model does not demonstrate an actual stage of abiogenesis, chemically realistic RNA–metabolite binding, encoded catalysts, template replication, thermodynamic self-maintenance, or an inevitable route to genetics.

11. **Inference scope.** The independently evolved baseline population is the inferential unit. Maps and continuation seeds are nested technical measurements; cells, motifs, windows, and generations are internal observations.

12. **Tested-domain scope.** The sensitivity program is staged and non-factorial. It supports persistence across a meaningful prespecified domain, not exhaustive coverage of all parameters or interactions.

13. **Inheritance-scope wording audit still required.** Gate 6 remains a manuscript-stage obligation. Final prose and figures must be checked for compositional-resampling wording before acceptance.

## 6. Authorized secondary claims

The following subordinate claims are supported when stated with model-specific qualifiers:

- position conditioning removes the sequence-agnostic positional channel as a source of primary sequence-specific information;
- total motif–local-state mutual information is not sufficient to identify viability relevance;
- actual retained information differs from nominal group-count resolution;
- replicate-level inference avoids the submitted intervention-point pseudoreplication;
- selection dependence and mapping specificity are empirically distinguishable within Model B;
- sequence-specific statistical information can occur without detectable viability relevance;
- viability relevance can occur without strong sustained adaptive gain;
- the corrected result is not restricted to the single default parameter vector.

## 7. Prohibited interpretations

The frozen results do not authorize statements that:

- Model B reproduces physical protocell growth and division;
- the analysis demonstrates the historical origin of biological meaning;
- semantic information inevitably precedes genetics in nature;
- a universal critical inheritance threshold has been found;
- all value of information is an evolved quantity;
- every fitness formulation supports the effect;
- the semantic estimate is a universal minimum number of bits;
- affinity-profile clustering establishes the primary semantic frontier;
- the model demonstrates open-ended evolution, genotype–phenotype separation, or a complete genetic code;
- biochemical realism follows from robustness within the abstract model domain.

## 8. Change control after freeze

Any stronger claim, altered limitation, new primary endpoint, changed estimator, changed intervention panel, changed inferential rule, or changed numerical result requires a new decision-log entry and a versioned rerun of every affected analysis. Editorial rephrasing is permitted only if it remains within this frozen claim boundary.
