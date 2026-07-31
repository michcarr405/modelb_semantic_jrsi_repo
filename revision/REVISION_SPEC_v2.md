# REVISION_SPEC.md

## Project

**Manuscript:** `rsif-2026-0516`  
**Working project title:** *JRSI Major Revision — Semantic Information in Model B*  
**Purpose of this document:** Define the scientific, analytical, statistical, computational, and interpretive rules for the revision before new simulations or manuscript rewriting begin.

This file is the controlling specification for the revision. Downstream analyses, figures, and prose should conform to it unless a change is explicitly approved and recorded in `DECISIONS_LOG.md`.

---

## 1. Revised primary scientific question

The revised manuscript will ask:

> **Which inherited motif-dependent correlations are sequence-specific and causally necessary for maintaining future model fitness under noisy compositional transmission?**

The revised paper will not primarily ask whether raw motif–metabolite mutual information rises with inheritance fidelity. That phenomenon was already established in the previous Model B study.

The revised contribution is the separation of:

1. position-mediated statistical association;
2. sequence-specific motif–metabolite information;
3. the subset of that information that is causally relevant to future model viability under intervention.

---

## 2. Core conceptual hierarchy

The revised analysis will distinguish the following quantities.

### 2.1 Total motif–metabolite association

\[
I(M;Z)
\]

where:

- \(M\) is motif identity;
- \(Z\) is sampled metabolite or local chemical-state class.

This quantity includes both direct motif-dependent association and indirect association mediated by positional structure.

### 2.2 Position-conditioned sequence-specific information

\[
I(M;Z\mid S)
\]

where \(S\) is positional segment or positional bin.

This is the primary measure of motif-specific statistical information because it controls for the sequence-agnostic positional channel.

### 2.3 Bias-corrected conditional information

\[
I_{\mathrm{corr}}(M;Z\mid S)
=
I_{\mathrm{obs}}(M;Z\mid S)
-
E_{\mathrm{perm}}\!\left[I(M;Z\mid S)\right]
\]

The permutation null must preserve positional structure by shuffling metabolite labels within segment.

### 2.4 Actual information retained by a coarse-graining

For a grouping map \(g\),

\[
I_{\mathrm{ret}}(g)
=
I(g(M);Z\mid S)
\]

This replaces the submitted heuristic based on:

\[
I(M;Z)\frac{\log_2 G}{\log_2(4^5)}.
\]

Nominal group number may be reported descriptively but will not be treated as retained mutual information.

### 2.5 Viability effect of information disruption

\[
\Delta V
=
V_{\mathrm{actual}}-V_{\mathrm{intervened}}.
\]

This measures the effect of disrupting motif-level distinctions on a prespecified future model outcome.

### 2.6 Replicate-specific semantic-information estimate

For independently evolved baseline replicate \(r\),

\[
S_r
=
\inf\left\{
R:
D_r(R)\geq V_{\mathrm{target},r}
\right\},
\]

where \(D_r(R)\) is the replicate-specific monotone information–viability frontier.

---

## 3. Primary interpretation

The strongest claim the revised manuscript may support is:

> **Within Model B, inherited sequence-dependent motif–metabolite information can become causally relevant to a prespecified future model-fitness measure under coarse-graining intervention.**

The paper may present this as:

- an intervention-based semantic decomposition;
- a model-based proof of principle;
- a theoretical possibility relevant to origins-of-life research.

The paper will not claim that the model directly demonstrates:

- an actual historical stage in abiogenesis;
- a universal pre-genetic transition;
- chemically realistic RNA–metabolite binding;
- literal protocell growth and physical fission;
- thermodynamic self-maintenance;
- a complete biological information system.

---

## 4. Terminology rules

The following terminology will be used consistently.

| Avoid or qualify | Preferred wording |
|---|---|
| molecular correlations | motif–metabolite statistical associations |
| biological information | model-defined viability-relevant information |
| biological viability | model-defined future viability or future mean fitness |
| productive pair | fitness-promoting adjacency |
| anti-productive pair | fitness-reducing adjacency |
| adaptive amplification | selection-driven fitness gain |
| physical partitioning | compositional resampling, unless a mass-conserving control is being described |
| protocell | abstract protocell-like population unit |
| inheritance fidelity | parental-composition coupling or compositional transmission fidelity, when referring to the original operator |
| metabolite binding at every motif | probabilistic local chemical-state assignment |
| merely persistent | persistent but not detectably viability-contributing under the specified test |

“Pre-genetic” will mean only that the model lacks explicit template replication, encoded catalysts, and genotype–phenotype decoding. It will not be used as a claim of historical reconstruction.

---

## 5. Model-scope statement

Model B will be described as:

> **A sequence-explicit, Wright–Fisher-like compositional-resampling model of abstract protocell-like units.**

The principal operator does not explicitly simulate:

- membrane growth;
- lipid or amphiphile production;
- oligomer synthesis chemistry;
- metabolite production or depletion;
- molecular copy-number conservation;
- literal two-daughter fission;
- steric exclusion;
- binding kinetics;
- RNA folding;
- catalytic reaction networks;
- thermodynamic coupling.

Metabolite labels are transient probabilistic local-state outcomes, not inherited molecular inventories.

The original with-replacement transmission operator must not be described as literal physical retention or mass-conserving partitioning.

### Revision decision on inheritance controls

For this revision, the original operator is retained without adding alternative inheritance simulations. Reviewer concerns about physical plausibility will be answered through precise model classification, explicit assumptions, narrowed claims, and a dedicated limitations paragraph. Alternative mass-conserving growth–fission or copy-number models are reserved for future work.

---

## 6. Primary viability definition

The primary viability function will be:

\[
V_{\mathrm{mean}}
=
\frac{1}{\tau_{\mathrm{int}}}
\sum_{t=1}^{\tau_{\mathrm{int}}}
\overline F_t,
\]

the mean population fitness over the post-intervention horizon.

Robustness definitions may include:

1. excess over a matched control;
2. threshold-survival fraction;
3. carefully justified alternative state functions.

The manuscript must distinguish:

- instantaneous protocell fitness;
- future viability function;
- semantic target.

These quantities must not be used interchangeably.

---

## 7. Statistical unit and inferential hierarchy

The primary independent unit is:

> **An independently evolved baseline simulation population.**

The hierarchy is:

| Level | Role |
|---|---|
| independently evolved baseline population | primary statistical replicate |
| intervention method and grouping map | repeated measurements nested within replicate |
| continuation seed | technical or Monte Carlo replicate |
| protocells, motifs, windows, and generations | internal simulation observations |

Pooled intervention points must not be treated as independent replicates.

For each baseline replicate, construct one:

- information–viability frontier;
- semantic estimate;
- value-of-information estimate;
- semantic-efficiency estimate;
- syntactic–semantic gap;
- target-reached indicator.

Primary inference will use replicate-level permutation tests and block bootstrap resampling of complete baseline-replicate blocks.

Mixed-effects models may be used as complementary analyses of the full intervention landscape.

---

## 8. Target attainment and censoring

The intervention set must include:

- complete scrambling;
- intermediate coarse-grainings;
- the full identity endpoint.

If the target is not reached, the result is a lower bound:

\[
S_r>I_{\max,r}.
\]

Target-not-reached cases must not be reported as ordinary point estimates.

Every relevant figure and table must report:

- number of independent replicates;
- number reaching the target;
- fraction reaching the target;
- confidence interval for that fraction;
- treatment of censored cases.

---

## 9. Required computational validation before new production runs

No revised production simulations may begin until all of the following pass.

### 9.1 Random-number control

- All stochastic draws must originate from explicitly controlled random generators.
- Same seed and same locked environment must reproduce the same trajectory.
- Different seeds must generate different stochastic trajectories.
- No hidden global random state may influence reported results.

### 9.2 Unit tests

Tests must cover:

- motif encoding;
- segment assignment;
- sampling probabilities;
- affinity and positional-logit combination;
- adjacency classification;
- fitness calculation;
- parent selection;
- inheritance and environmental replacement;
- sequence alteration;
- total MI;
- conditional MI;
- permutation correction;
- grouping endpoints;
- frontier construction;
- target detection;
- target-not-reached handling.

### 9.3 Analytical checks

The following must hold in test cases:

\[
I(M;Z\mid S)=0
\]

for the sequence-agnostic channel in the population limit;

\[
I(g_{\mathrm{constant}}(M);Z\mid S)=0;
\]

\[
I(g_{\mathrm{identity}}(M);Z\mid S)=I(M;Z\mid S).
\]

The identity intervention must reproduce the unintervened channel.

---

## 10. Intervention-family specification

The primary intervention families must be fixed before production runs.

Candidate families include:

- balanced-random grouping;
- affinity-rank grouping;
- leading-substring grouping;
- trailing-substring grouping;
- internal-substring grouping;
- Hamming-distance or another orientation-neutral sequence grouping;
- affinity-profile clustering as a diagnostic or explicitly labeled mechanistic family.

Repeated use of the same grouping map must not be counted as distinct intervention structures.

The submitted prefix implementation must be corrected because multiple requested group counts currently map to the same actual prefix partition.

All interventions must record:

- grouping-map identity;
- actual number of groups;
- method;
- retained-information value;
- baseline replicate;
- continuation seed;
- viability outcome;
- target status.

---

## 11. Core revised experiment

The core revised analysis will include:

- sequence-selective regime;
- sequence-agnostic regime;
- full inheritance-fidelity sweep;
- preferably 20 independently evolved baseline replicates per condition;
- corrected \(I(M;Z\mid S)\);
- permutation baseline;
- \(I(M;S)\);
- actual \(I(g(M);Z\mid S)\);
- replicate-specific frontiers;
- multiple continuation seeds where computationally feasible;
- identity and complete-scrambling endpoints.

The revised semantic claim may proceed only if it survives:

1. positional conditioning;
2. finite-sample correction;
3. actual retained-information measurement;
4. replicate-level inference.

---

## 12. Required circularity and specificity controls

The following controls are required before broad biological interpretation.

### 12.1 Selection-strength control

Vary selection from neutral parent sampling to full fitness-proportional propagation.

### 12.2 Affinity-profile reassignment

Permute complete affinity profiles among motif identities while preserving the affinity distribution.

### 12.3 Fitness-map mismatch

Evaluate evolved populations under matched randomized adjacency maps.

### 12.4 Alternative fixed topologies

Evolve populations under at least two alternative stable fitness topologies and test native-versus-nonnative evaluation.

### 12.5 Temporally unstable topology

Use a changing map as a null for persistent mapping-specific semantic accumulation.

The strongest acceptable interpretation requires a selection-dependent and mapping-specific semantic excess.

---

## 13. Inheritance-operator scope and description

The original inheritance operator will remain the principal and only inheritance model in this revision. No new without-replacement, growth–fission, finite-pool, or mass-conserving inheritance simulations are required.

The revision will address the reviewers' concern by describing the implemented operator accurately and narrowing the biological interpretation accordingly.

The operator must be described as:

> **A fitness-weighted, Wright–Fisher-like compositional-resampling transition over abstract protocell-like population units.**

The manuscript must state explicitly that:

- parent-derived oligomer identities are sampled with replacement from the selected parent's empirical oligomer distribution;
- non-parental oligomers are drawn from an idealized uniform environmental sequence reservoir;
- the parameter \(p\) measures parent–offspring compositional coupling, not literal retention of conserved molecular instances;
- the same parental sequence identity may occupy more than one offspring slot;
- the model does not specify the chemical production process that supplies daughter molecular material;
- metabolite labels are transient sampled local-state outcomes and are not inherited molecular inventories;
- the operator does not simulate membrane growth, molecular synthesis, mass conservation, or physical two-daughter fission.

The revision must remove or replace claims that the operator represents:

- noisy physical partitioning;
- literal protocell division;
- molecule-by-molecule retention;
- mass-conserving inheritance.

The supported conclusion is limited to information dynamics under the specified compositional-resampling operator. Physical protocell growth, production, and fission remain outside the scope of the manuscript and must be identified as future work.

---

## 14. Required model-structure controls

The revision should test whether the result depends on physically problematic or arbitrary structural choices.

### 14.1 Motif-window density

Compare:

- stride 1;
- partial overlap;
- non-overlapping windows;
- sparse active windows;
- exclusion of overlapping active windows.

### 14.2 Positional structure

Compare:

- alternative segment counts;
- alternative segment orders;
- non-heritable boundary jitter;
- optionally heritable mutable boundaries.

### 14.3 Metabolite-state count

Vary the number of abstract metabolite classes using matched topology density and effect scale.

### 14.4 Fitness formulation

Test:

- submitted count-based fitness;
- fraction-normalized adjacency fitness;
- reward/penalty variation;
- fitness-floor sensitivity.

---

## 15. Parameter-sensitivity strategy

A full factorial sweep is prohibited unless specifically justified.

Use a staged design.

### Stage A: focused mechanistic phase diagram

Primary axes:

\[
p
\quad\text{and}\quad
\frac{\sigma_a}{\Theta},
\]

with facets or secondary variation in:

\[
\frac{b}{\Theta}.
\]

### Stage B: global space-filling screen

Sample across:

- segment-bias strength;
- affinity variance;
- softmax temperature;
- mutation rate;
- population size;
- motif length;
- metabolite-class number;
- reward scale;
- penalty ratio.

### Stage C: protocol sensitivity

Treat separately:

- simulation duration;
- intervention horizon.

### Stage D: confirmatory semantic analysis

Apply the full intervention pipeline to representative parameter sets from:

- null region;
- syntactic-only region;
- viability-relevant region;
- strong-adaptation region;
- boundary region.

---

## 16. Prespecified regime definitions

The revised analysis should classify model behavior using prespecified criteria.

### Regime 0: no sequence-specific information

\[
I_{\mathrm{corr}}(M;Z\mid S)\approx0.
\]

### Regime 1: sequence-specific syntactic information

\[
I_{\mathrm{corr}}(M;Z\mid S)>0,
\qquad
\Delta V\approx0.
\]

### Regime 2: viability-relevant information

\[
I_{\mathrm{corr}}(M;Z\mid S)>0,
\qquad
\Delta V>0,
\]

with a nonzero replicate-specific semantic estimate.

### Regime 3: strong selection-driven fitness gain

Regime 2 plus a sustained increase in mean model fitness.

Threshold language should be used only if finite-size or sensitivity analysis supports a sharp transition. Otherwise use “crossover,” “transition region,” or “regime boundary.”

---

## 17. Novelty statement relative to the prior Model B paper

The previous Model B paper:

- introduced the model;
- reported inheritance-fidelity effects;
- measured raw motif–metabolite MI;
- included the no-intrinsic-affinity condition;
- reported separation between MI and fitness.

The revised JRSI manuscript is novel because it:

- treats raw MI as syntactic rather than automatically semantic;
- controls for positional mediation;
- applies counterfactual coarse-graining interventions;
- measures actual retained information;
- constructs replicate-specific information–viability frontiers;
- tests mapping specificity and causal disruption;
- uses replicate-level inference;
- maps robustness across parameter space and alternative inheritance mechanisms.

The manuscript must not claim that the sequence-agnostic condition itself is new.

---

## 18. Figure requirements

Final publication figures must not be produced until the analysis is frozen.

Required visual elements include:

1. model workflow using a short illustrative oligomer;
2. explicit distinction between inherited and transient variables;
3. accurate population-update schematic;
4. intervention schematic;
5. raw independent replicate-level information;
6. clearly defined confidence intervals;
7. target-reaching status;
8. direct display of total, position-conditioned, and viability-relevant information;
9. causal-disruption controls;
10. phase diagram or global-sensitivity summary.

Every caption must state:

- independent \(n\);
- nested intervention count where relevant;
- statistical unit;
- summary statistic;
- confidence-interval method;
- bootstrap or permutation count;
- target-reaching fraction;
- treatment of censoring.

---

## 19. Manuscript-rewrite order

Do not patch the submitted manuscript section by section before results are frozen.

Rewrite in this order:

1. model-scope statement;
2. model workflow and definitions;
3. analytical expectations;
4. corrected Methods;
5. corrected Results;
6. Discussion separating demonstration from speculation;
7. novelty table;
8. figure captions;
9. title;
10. abstract;
11. conclusion.

The title, abstract, and conclusion must be written last.

---

## 20. Reproducibility requirements

The final release must include:

- detailed README;
- exact commands for every figure and statistical result;
- locked environment;
- seed ledger;
- validation tests;
- raw outputs or archived generated datasets;
- processed figure-source data;
- evolved populations used for interventions;
- license;
- `CITATION.cff`;
- release tag;
- full Git commit hash;
- permanent DOI;
- clean-room rerun record.

AI-assisted code will be described as reviewed and validated through tests, analytical checks, deterministic reruns, and independent execution from a clean environment.

---

## 21. Phase gates

### Gate 1 — Code validity

Pass only when RNG control, unit tests, implementation audit, and intervention-map inventory are complete.

### Gate 2 — Information-measure validity

Pass only when conditional MI, permutation correction, actual retained information, and endpoint tests behave as expected.

### Gate 3 — Statistical-pipeline validity

Pass only when replicate-specific frontiers, block bootstrap, target handling, and continuation design are validated.

### Gate 4 — Core-result survival

Pass only if the corrected selective-versus-agnostic result survives the revised measures and replicate-level inference.

### Gate 5 — Causal specificity

Pass only if the selection-dependent semantic component is reduced by the relevant disruption controls.

### Gate 6 — Inheritance-scope and wording audit

Pass only when the manuscript, figures, captions, abstract, and Discussion consistently describe the original operator as compositional resampling rather than physical partitioning or mechanistic protocell fission. No additional inheritance simulations are required.

### Gate 7 — Generality

Pass only after model-structure controls and sensitivity analysis define the region in which the effect persists.

### Gate 8 — Result freeze

After this gate, no model, estimator, grouping, or inferential change is permitted without opening a new versioned analysis release.

---

## 22. Go/no-go criteria for the central semantic claim

### Strong support

The central claim is strongly supported if:

- sequence-agnostic corrected conditional MI is near its null;
- sequence-selective conditional MI is reproducibly positive;
- actual retained information produces a monotone viability frontier;
- replicate-level semantic estimates are consistently nonzero;
- the signal is reduced by affinity remapping or fitness-map mismatch;
- the result persists over a meaningful parameter region;
- the inheritance claim is explicitly restricted to the implemented compositional-resampling operator.

### Narrow support

The claim may be retained in narrower form if:

- the result survives corrected information analysis and replicate-level inference;
- but is sensitive to specific intervention or parameter choices, or remains specific to the original compositional-resampling operator.

The paper must then describe a model-specific existence result rather than a general prebiotic regime.

### No support for the current semantic claim

The claim must be abandoned or fundamentally reframed if:

- corrected sequence-specific MI disappears;
- identity endpoints fail to recover the unintervened channel;
- replicate-level semantic estimates are not reproducible;
- disruption controls do not distinguish native from scrambled mappings;
- the effect exists only because of the submitted heuristic information scale;
- the semantic effect cannot be distinguished from a direct artifact of the implemented grouping or information estimator.

Negative outcomes must be reported honestly and used to redefine the manuscript’s contribution.

---

## 23. Change-control rule

Any proposed change to the following must be recorded in `DECISIONS_LOG.md` before implementation:

- primary question;
- viability definition;
- information measure;
- intervention family;
- target rule;
- statistical unit;
- replicate count;
- model operator;
- parameter ranges;
- biological interpretation.

The log entry must state:

- proposed change;
- reason;
- analyses invalidated;
- required reruns;
- approval decision.

---

## 24. No-do-over rules

1. Do not run large parameter sweeps before the corrected information measures are validated.
2. Do not run the full intervention suite before endpoint tests pass.
3. Do not construct final figures before replicate-level statistics are frozen.
4. Do not rewrite the abstract, title, or Discussion before causal controls are known and the inheritance-operator wording has been frozen.
5. Do not create the permanent DOI release before all analyses are frozen.
6. Do not treat technical continuation seeds as independent biological or evolutionary replicates.
7. Do not introduce new intervention families after confirmatory production runs without versioning and rerunning the relevant analysis.
8. Do not preserve submitted numerical estimates merely for continuity if the corrected analysis changes them.

---

## 25. Revision success criterion

The revision succeeds if it provides a transparent and reproducible answer to:

> **What part of inherited motif–metabolite association remains after positional structure is controlled, how much of that information is preserved by each intervention, and which part causally contributes to future model fitness across independent evolutionary replicates?**

The final paper should be narrower in biological scope but stronger in information theory, causal interpretation, statistical inference, and reproducibility.
