# DECISIONS_LOG.md

## Project

**Manuscript:** `rsif-2026-0516`  
**Project:** *JRSI Major Revision — Semantic Information in Model B*  
**Purpose:** Record decisions that constrain downstream code, analyses, figures, manuscript text, and reviewer responses.

This file is a change-control record. It is not a general notebook. Only decisions that affect the scientific interpretation, analytical pipeline, revision scope, or reproducibility should be entered here.

The controlling documents are:

1. `REVISION_SPEC_v2.md`
2. `REVIEWER_MATRIX.md`
3. `DECISIONS_LOG.md`
4. the current phase handoff

If a later proposal conflicts with a logged decision, the conflict must be resolved through a new decision entry before implementation.

---

## Entry template

Copy this template for every new decision.

```markdown
## DXX — Short decision title

**Date:** YYYY-MM-DD  
**Status:** PROPOSED | APPROVED | SUPERSEDED | REJECTED  
**Requested by:**  
**Phase:**  
**Reviewer items affected:**  

### Decision

[Exact decision.]

### Rationale

[Why this choice was made.]

### Alternatives considered

- Alternative 1
- Alternative 2

### Consequences

**Code affected:**  
**Analyses affected:**  
**Figures affected:**  
**Manuscript sections affected:**  
**Previously generated outputs invalidated:**  

### Verification required

[What must be checked before the decision is considered implemented.]

### Supersedes

[Earlier decision ID, if any.]
```

---

# Approved decisions

## D01 — Revised primary scientific question

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Author and revision planning process  
**Phase:** Project setup  
**Reviewer items affected:** R1.1, R1.3, R1.4, R1.7, R2.1, R2.3

### Decision

The revised manuscript will primarily ask:

> **Which inherited motif-dependent correlations are sequence-specific and causally necessary for maintaining future model fitness under noisy compositional transmission?**

The revised paper will not be centered on the observation that raw motif–metabolite mutual information rises with inheritance fidelity.

### Rationale

The previous Model B paper already reported inheritance-dependent raw mutual information and fitness behavior. The revised paper’s distinct contribution is the intervention-based separation of positional association, sequence-specific information, and viability-relevant information.

### Alternatives considered

- Retain the original emphasis on a semantic-stabilization threshold.
- Present raw mutual information accumulation as the main discovery.
- Focus entirely on the inheritance-fidelity fitness transition.

### Consequences

**Code affected:** Conditional-MI and intervention analyses become central.  
**Analyses affected:** Raw MI becomes descriptive rather than the primary semantic measure.  
**Figures affected:** Main results must show the information hierarchy.  
**Manuscript sections affected:** Title, abstract, Introduction, Results, Discussion, Conclusion.  
**Previously generated outputs invalidated:** Submitted semantic estimates are provisional until the corrected pipeline is complete.

### Verification required

The final manuscript must consistently distinguish the prior Model B findings from the revised intervention-based contribution.

### Supersedes

None.

---

## D02 — Position-conditioned mutual information is the primary sequence-specific association measure

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Reviewer-response planning  
**Phase:** Corrected information measures  
**Reviewer items affected:** R1.3, R2.3

### Decision

The primary sequence-specific statistical-information measure will be:

\[
I(M;Z\mid S),
\]

with finite-sample correction based on permutations that preserve positional segment structure.

The revision will also report:

\[
I(M;Z)
\]

and:

\[
I(M;S)
\]

to show how total association decomposes.

### Rationale

In the sequence-agnostic regime, metabolite state depends on segment rather than motif identity. Total \(I(M;Z)\) may therefore arise through the pathway \(M\leftrightarrow S\rightarrow Z\). Conditioning on segment is required to isolate motif-dependent association.

### Alternatives considered

- Retain total \(I(M;Z)\) as the primary semantic quantity.
- Remove the sequence-agnostic condition.
- Condition on exact window position only.

### Consequences

**Code affected:** Add conditional-MI and within-segment permutation functions.  
**Analyses affected:** All baseline information results must be recalculated.  
**Figures affected:** Baseline figure must show total, positional, and conditional information.  
**Manuscript sections affected:** Analytical expectations, Methods, Results, Discussion.  
**Previously generated outputs invalidated:** Any conclusion equating total MI with sequence-specific information.

### Verification required

Analytical and simulation tests must show that sequence-agnostic \(I(M;Z\mid S)\) approaches its null expectation.

### Supersedes

None.

---

## D03 — Actual retained information replaces the nominal group-count heuristic

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Reviewer-response planning  
**Phase:** Corrected information measures  
**Reviewer items affected:** R1.4, R2.5.9

### Decision

For every coarse-graining map \(g\), retained information will be measured directly as:

\[
I_{\mathrm{ret}}(g)=I(g(M);Z\mid S).
\]

The submitted approximation:

\[
I(M;Z)\frac{\log_2 K}{\log_2(4^5)}
\]

will not be used as the primary information coordinate.

### Rationale

Nominal resolution does not determine how much motif–metabolite information a specific grouping preserves. Different grouping methods with the same number of groups can retain very different information.

### Alternatives considered

- Retain the heuristic and label it an approximation.
- Use only group number on the x-axis.
- Use affinity-profile variance as the information coordinate.

### Consequences

**Code affected:** Every intervention must calculate actual retained information.  
**Analyses affected:** Frontiers, semantic estimates, efficiencies, and gaps must be recomputed.  
**Figures affected:** All information–viability figures change.  
**Manuscript sections affected:** Intervention Methods, Results, Appendix, captions.  
**Previously generated outputs invalidated:** Submitted semantic bit values and frontier x-coordinates.

### Verification required

Constant and identity grouping endpoints must satisfy the expected information limits.

### Supersedes

None.

---

## D04 — Independent evolved population is the primary statistical unit

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Reviewer-response planning  
**Phase:** Statistical pipeline  
**Reviewer items affected:** R1.5

### Decision

The independently evolved baseline population is the primary inferential unit.

Intervention maps and continuation seeds are nested repeated measurements. They will not be treated as independent evolutionary replicates.

### Rationale

Intervention outcomes derived from the same evolved population share evolutionary history and are statistically dependent. Treating hundreds of intervention points as independent inflates precision.

### Alternatives considered

- Continue using pooled intervention-point Mann–Whitney tests.
- Treat continuation seeds as independent replicates.
- Average all populations before constructing one frontier.

### Consequences

**Code affected:** Construct one frontier and semantic estimate per evolved replicate.  
**Analyses affected:** Use replicate-level permutation tests and block bootstrap.  
**Figures affected:** Display raw independent replicate points and target status.  
**Manuscript sections affected:** Statistical Methods, Results, figure captions.  
**Previously generated outputs invalidated:** Submitted pooled-point p-values as primary inferential evidence.

### Verification required

Every reported \(n\) must distinguish evolved replicates, intervention maps, and continuation seeds.

### Supersedes

None.

---

## D05 — Primary viability definition is mean future model fitness

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Revision planning  
**Phase:** Intervention design  
**Reviewer items affected:** R1.2, R1.4, R2.1

### Decision

The primary intervention viability function will be the mean population model fitness over the prespecified intervention horizon:

\[
V_{\mathrm{mean}}
=
\frac{1}{\tau_{\mathrm{int}}}
\sum_{t=1}^{\tau_{\mathrm{int}}}\overline F_t.
\]

Excess over matched control and threshold survival may be used as robustness measures.

### Rationale

Mean future fitness is directly interpretable within the model and avoids making the sequence-agnostic control part of the primary viability definition. It also separates the model’s instantaneous fitness score from the future viability functional.

### Alternatives considered

- Excess over sequence-agnostic control as the primary viability definition.
- Threshold survival as the primary definition.
- Negative entropy as the primary viability definition.

### Consequences

**Code affected:** Standardize future-fitness calculation and horizon handling.  
**Analyses affected:** Recompute primary frontiers and semantic estimates.  
**Figures affected:** Primary intervention plots will use mean future fitness.  
**Manuscript sections affected:** Methods, Results, semantic-framework explanation.  
**Previously generated outputs invalidated:** Primary status of the excess-over-control analysis.

### Verification required

The primary and robustness viability measures must be clearly distinguished in all outputs.

### Supersedes

None.

---

## D06 — The original inheritance operator remains the principal and only inheritance model

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Author  
**Phase:** Revision scope  
**Reviewer items affected:** R2.2, R2.5.8, R1.7

### Decision

The original inheritance operator will remain the principal and only inheritance model in this revision.

No new:

- without-replacement inheritance simulations;
- growth–fission simulations;
- finite environmental-pool simulations;
- mass-conserving partition simulations;
- explicit copy-number models

will be required for the revision.

### Rationale

The manuscript’s central purpose is to analyze information dynamics under the existing abstract operator, not to replace Model B with a chemically mechanistic protocell model. The reviewer’s concern will be addressed by accurately classifying the operator and limiting the claims to what it implements.

### Alternatives considered

- Add a without-replacement control.
- Add an explicit two-daughter growth–fission model.
- Replace the original operator entirely.
- Convert the model to explicit molecular copy numbers.

### Consequences

**Code affected:** No new inheritance model is required.  
**Analyses affected:** Existing operator remains the basis of all revised analyses.  
**Figures affected:** Model schematic must depict compositional resampling, not physical fission.  
**Manuscript sections affected:** Abstract, Model overview, transmission Methods, Discussion limitations, Conclusion.  
**Previously generated outputs invalidated:** None solely because of this decision.

### Required wording

The operator will be described as:

> **A fitness-weighted, Wright–Fisher-like compositional-resampling transition over abstract protocell-like population units.**

The manuscript must state that:

- parent-derived oligomer identities are sampled with replacement;
- non-parental oligomers are drawn from an idealized environmental sequence reservoir;
- \(p\) measures parent–offspring compositional coupling;
- \(p\) is not literal retention of conserved molecular instances;
- the same parental sequence identity may occupy multiple offspring slots;
- the model does not specify molecular production, membrane growth, mass conservation, or literal two-daughter fission.

### Verification required

A manuscript-wide wording audit must confirm that “physical partitioning,” “literal division,” and equivalent mechanistic claims are removed or explicitly qualified.

### Supersedes

The earlier revision-plan proposal to require additional inheritance controls.

---

## D07 — Metabolite-window states are not literal simultaneous bound molecules

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Reviewer-response planning  
**Phase:** Model description  
**Reviewer items affected:** R2.4, R2.5.2

### Decision

Each motif window will be described as receiving a transient probabilistic local chemical-state label.

The model will not describe all 56 overlapping windows as simultaneously occupied metabolite-binding sites.

### Rationale

The implementation does not model steric exclusion, occupancy, ligand copy number, association/dissociation kinetics, or RNA folding. Literal simultaneous binding is therefore not supported.

### Alternatives considered

- Defend every window as an independent physical binding site.
- Reinterpret labels as metabolite concentrations.
- Add a mechanistic ligand-occupancy model.

### Consequences

**Code affected:** None required for the terminology change.  
**Analyses affected:** Optional window-density robustness remains a separate scope decision.  
**Figures affected:** Figure 1 must label the variables as transient local-state outcomes.  
**Manuscript sections affected:** Model overview, sampling Methods, limitations.  
**Previously generated outputs invalidated:** None numerically.

### Verification required

Search the manuscript for “bind,” “bound,” “occupancy,” and similar terms and verify that each use is accurate.

### Supersedes

None.

---

## D08 — “Productive” and “anti-productive” will be replaced

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Reviewer-response planning  
**Phase:** Terminology and notation  
**Reviewer items affected:** R2.1, R2.5.3, R2.5.7

### Decision

Use:

- **fitness-promoting adjacency**
- **fitness-reducing adjacency**
- **fitness-neutral adjacency**

instead of “productive” and “anti-productive.”

The pairs \((0,2)\) and \((2,0)\) will be explicitly identified as neutral.

### Rationale

The model does not simulate chemical products or reaction inhibition. The revised terms describe the actual mathematical role of the pair categories.

### Alternatives considered

- Retain the original terminology with a disclaimer.
- Use beneficial and deleterious pairs.
- Use positive and negative reaction pairs.

### Consequences

**Code affected:** Variable names may be updated where practical, but numerical behavior need not change.  
**Analyses affected:** None numerically.  
**Figures affected:** Pair classification and model schematic labels.  
**Manuscript sections affected:** Entire manuscript and Appendix.  
**Previously generated outputs invalidated:** None.

### Verification required

Complete terminology audit and full ordered-pair table.

### Supersedes

None.

---

## D09 — Prefix grouping will not remain an unexplained privileged sequence intervention

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Reviewer-response planning  
**Phase:** Intervention audit  
**Reviewer items affected:** R1.4, R1.5, R2.5.9

### Decision

The submitted prefix-grouping implementation will be audited and corrected.

Repeated requested group counts that produce the same actual grouping map will not be treated as distinct intervention structures.

The revised sequence-based intervention set will include either:

1. leading, trailing, and internal substring maps at natural resolutions; or
2. a prespecified orientation-neutral sequence grouping method.

The exact final family will be frozen after the Phase 1 grouping-map audit.

### Rationale

The first motif position has no privileged role in Model B, and the submitted implementation maps several requested group counts to identical partitions.

### Alternatives considered

- Retain prefix grouping unchanged.
- Remove all sequence-based grouping methods.
- Make k-means-profile grouping the only structured method.

### Consequences

**Code affected:** Grouping functions and grouping manifest.  
**Analyses affected:** All revised interventions and frontiers.  
**Figures affected:** Method-ablation and intervention schematic.  
**Manuscript sections affected:** Intervention Methods and Appendix.  
**Previously generated outputs invalidated:** Submitted prefix-family intervention counts and pooled-point interpretation.

### Verification required

Produce a map-level manifest listing method, parameters, exact assignment hash, and actual group count.

### Supersedes

None.

---

## D10 — Causal specificity controls are required

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Reviewer-response planning  
**Phase:** Post-core causal controls  
**Reviewer items affected:** R1.2, R2.3

### Decision

The revision will test whether the semantic signal is selection-dependent and mapping-specific using a focused set of disruption controls.

Planned controls include:

- neutral or reduced selection;
- complete affinity-profile reassignment;
- fitness-map mismatch;
- alternative stable fitness topologies;
- a temporally unstable topology null.

### Rationale

A causal path from motif identity to fitness exists by design in the sequence-selective architecture. The nontrivial question is whether evolution produces stable, mapping-specific enrichment beyond architectural sensitivity.

### Alternatives considered

- Rely only on the sequence-agnostic control.
- Treat any intervention-induced fitness loss as evidence of evolved semantics.
- Remove the semantic interpretation.

### Consequences

**Code affected:** Add prespecified disruption modes.  
**Analyses affected:** Replicate-level value-of-information and semantic-excess comparisons.  
**Figures affected:** Dedicated specificity-control figure.  
**Manuscript sections affected:** Methods, Results, Discussion.  
**Previously generated outputs invalidated:** None until the controls are run, but strong evolutionary claims remain blocked.

### Verification required

The reviewer response must distinguish built-in causal architecture from selection-dependent mapping specificity.

### Supersedes

None.

---

## D11 — Parameter values will be described as dimensionless defaults unless empirically supported

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Reviewer-response planning  
**Phase:** Model description and sensitivity  
**Reviewer items affected:** R1.6, R2.5.1, R2.5.4–R2.5.7

### Decision

The following defaults will not be presented as empirically calibrated prebiotic constants:

- four metabolite classes;
- four positional bins;
- segment-bias strength \(b=2.0\);
- softmax temperature \(\Theta=1.2\);
- reward \(r=2.0\);
- penalty \(q=0.5\);
- fitness floor \(F_{\min}=0.1\).

They will be described as dimensionless model-design choices with stated computational roles.

### Rationale

The submitted manuscript does not provide experimental calibration for these values. Inventing retrospective biochemical justifications would weaken trust.

### Alternatives considered

- Defend the defaults as chemically realistic.
- Remove the parameter discussion.
- Fit the parameters to unrelated empirical data.

### Consequences

**Code affected:** Focused sensitivity analyses and parameter reporting.  
**Analyses affected:** Phase diagram and selected robustness tests.  
**Figures affected:** Parameter-sensitivity figure or supplement.  
**Manuscript sections affected:** Parameter table, Methods, Discussion limitations.  
**Previously generated outputs invalidated:** None solely from the wording decision.

### Verification required

Every default in the final parameter table must include meaning, basis, and sensitivity range.

### Supersedes

None.

---

## D12 — Baseline trends will be framed as analytical expectations, not the main discovery

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Reviewer-response planning  
**Phase:** Manuscript architecture  
**Reviewer items affected:** R2.3, R1.1

### Decision

The qualitative baseline expectations will be stated analytically:

- in the sequence-agnostic regime, motif identity should not influence metabolite state after conditioning on position;
- in the sequence-selective regime, stronger parent–offspring compositional coupling should increase the persistence of selectable sequence effects.

The baseline sweep will be presented as validation and calibration. The main novelty will be the corrected intervention and causal-specificity analysis.

### Rationale

The reviewer is correct that the direction of the baseline effects is largely expected from the model architecture.

### Alternatives considered

- Continue presenting the baseline fidelity sweep as the headline discovery.
- Remove the baseline sweep entirely.
- Replace the agent-based model with only an analytical model.

### Consequences

**Code affected:** None directly.  
**Analyses affected:** Reduced-model derivation and comparison.  
**Figures affected:** Baseline figure may be simplified or moved earlier.  
**Manuscript sections affected:** Introduction, analytical expectations, Results framing, Discussion.  
**Previously generated outputs invalidated:** None numerically.

### Verification required

The revised manuscript must identify which findings are deductive, quantitative, intervention-dependent, and genuinely new.

### Supersedes

None.

---

## D13 — Final figures and manuscript prose will be produced only after result freeze

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Revision planning  
**Phase:** Workflow control  
**Reviewer items affected:** All

### Decision

Only rough diagnostic plots and schematic drafts may be produced before the corrected analyses and controls are frozen.

Final data figures, captions, title, abstract, Discussion, and Conclusion will be created after the result-freeze gate.

### Rationale

Changes to information measurement, statistical unit, grouping maps, or causal controls would otherwise force repeated revisions of figures and prose.

### Alternatives considered

- Rewrite the manuscript in parallel with code changes.
- Modify the submitted figures incrementally.
- Finalize the title and abstract first.

### Consequences

**Code affected:** None.  
**Analyses affected:** Encourages explicit phase gates.  
**Figures affected:** Final figure generation is deferred.  
**Manuscript sections affected:** All.  
**Previously generated outputs invalidated:** None.

### Verification required

The master project chat must record that Gate 8 has passed before final figure and manuscript production begins.

### Supersedes

None.

---

## D14 — Threshold language requires evidence of sharpness

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Revision planning  
**Phase:** Sensitivity and interpretation  
**Reviewer items affected:** R1.6, R1.7, R2.3

### Decision

The terms “threshold” and “critical” will be used only if finite-size, replicate-variance, or parameter-resolution analysis supports a sharp transition.

Otherwise the paper will use:

- transition region;
- crossover;
- regime boundary;
- fidelity-dependent change.

### Rationale

A nonlinear response in one finite simulation does not by itself establish a critical threshold.

### Alternatives considered

- Retain threshold terminology because the curves appear abrupt.
- Avoid all transition terminology.
- Define threshold only by statistical significance.

### Consequences

**Code affected:** Potential finite-size and refined-grid analyses.  
**Analyses affected:** Threshold characterization.  
**Figures affected:** Phase diagram and transition plots.  
**Manuscript sections affected:** Title, abstract, Results, Discussion, Conclusion.  
**Previously generated outputs invalidated:** Any unqualified submitted claim of a critical threshold.

### Verification required

The final terminology must follow the evidence in the frozen results.

### Supersedes

None.

---

## D15 — Equation and notation redesign precedes manuscript rewrite

**Date:** 2026-07-30  
**Status:** APPROVED  
**Requested by:** Reviewer-response planning  
**Phase:** Methods redesign  
**Reviewer items affected:** R2.6.1, R2.6.2

### Decision

A complete notation table will be frozen before the revised Methods and figures are written.

Matrices will be bold. Elements will use nonbold indexed symbols. The same core symbol will not represent unrelated concepts.

All displayed equations will be numbered and cross-referenced.

### Rationale

The submitted notation reuses several symbols for unrelated variables, which makes the model difficult to follow and increases the risk of errors during revision.

### Alternatives considered

- Retain the existing notation and add explanations.
- Change only the most obvious collisions.
- Put all equations in the Appendix.

### Consequences

**Code affected:** Optional variable-name cleanup; mathematical outputs may need relabeling.  
**Analyses affected:** None numerically.  
**Figures affected:** All mathematical figure labels.  
**Manuscript sections affected:** Entire Methods and Appendix.  
**Previously generated outputs invalidated:** None numerically.

### Verification required

Complete symbol audit before equation numbering is finalized.

### Supersedes

None.

---

# Decisions pending after prerequisite phases

These are not yet approved and should not be implemented as confirmatory choices until their prerequisites are complete.

## P01 — Final sequence-based grouping family

**Prerequisite:** Phase 1 grouping-map audit.  
**Decision needed:** Leading/trailing/internal substrings versus orientation-neutral Hamming-based grouping, or a combination.

## P02 — Number of continuation seeds per intervention

**Prerequisite:** Runtime benchmark and variance pilot.  
**Decision needed:** Minimum technical repetitions for stable replicate-level viability estimates.

## P03 — Final intervention horizon

**Prerequisite:** Horizon-sensitivity pilot.  
**Decision needed:** Fixed \(\tau_{\mathrm{int}}\) for confirmatory runs.

## P04 — Semantic target tolerance

**Prerequisite:** Corrected frontier pilot with identity endpoints.  
**Decision needed:** Exact target rule and treatment of Monte Carlo uncertainty.

## P05 — Primary intervention-family pooling rule

**Prerequisite:** Actual retained-information pilot and method-ablation results.  
**Decision needed:** Whether the primary frontier pools prespecified families or reports family-specific frontiers.

## P06 — Role of affinity-profile clustering

**Prerequisite:** Actual retained-information analysis.  
**Decision needed:** Primary family, diagnostic family, or supplementary mechanistic upper bound.

## P07 — Exact structural-sensitivity subset

**Prerequisite:** Core corrected result.  
**Decision needed:** Which among metabolite-class number, segment count, window stride, fitness normalization, and parameter ratios enter confirmatory robustness analysis.

## P08 — Final title and use of “semantic-stabilization”

**Prerequisite:** Result freeze and threshold assessment.  
**Decision needed:** Whether semantic-stabilization remains scientifically justified in the title.

---

# Rejected or out-of-scope proposals

## X01 — Add a new physical inheritance model during this revision

**Date:** 2026-07-30  
**Status:** REJECTED  
**Reason:** The revision will retain the original abstract compositional-resampling operator and narrow the claims rather than redesigning the model. Mechanistic mass-conserving growth–fission and copy-number models remain future work.

## X02 — Defend arbitrary defaults as empirically calibrated chemistry

**Date:** 2026-07-30  
**Status:** REJECTED  
**Reason:** The current defaults were not estimated from a specific prebiotic system. They will be treated transparently as model-design choices and tested through focused sensitivity analysis.

## X03 — Preserve submitted semantic bit values for continuity

**Date:** 2026-07-30  
**Status:** REJECTED  
**Reason:** The retained-information heuristic must be replaced. Revised bit values will be reported even if they differ substantially from the submitted manuscript.

## X04 — Use pooled intervention points as the main inferential sample

**Date:** 2026-07-30  
**Status:** REJECTED  
**Reason:** Intervention points are nested within evolved populations. The evolved replicate is the primary independent unit.

---

# Change-control procedure

Before changing any approved decision:

1. Add a new proposed decision entry.
2. Identify the approved decision it would supersede.
3. State why the current decision is inadequate.
4. List all code, analyses, figures, and prose invalidated by the change.
5. Decide whether previously completed phase gates must be reopened.
6. Obtain explicit author approval.
7. Update `REVISION_SPEC_v2.md` and `REVIEWER_MATRIX.md`.
8. Version all rerun outputs separately.

No approved decision should be silently changed in a phase-specific chat.

---

# Current lock summary

As of 2026-07-30, the following are locked:

- revised primary scientific question;
- position-conditioned MI as the primary sequence-specific measure;
- direct retained-information measurement;
- evolved population as the primary statistical unit;
- mean future fitness as the primary viability function;
- original inheritance operator retained without new inheritance simulations;
- compositional-resampling interpretation of that operator;
- local-state rather than literal simultaneous-binding interpretation;
- revised adjacency terminology;
- need to correct the sequence-grouping intervention family;
- causal disruption controls;
- model defaults described as dimensionless design choices;
- baseline trends framed as analytical expectations;
- final writing and figures deferred until result freeze;
- threshold language conditional on evidence;
- notation redesign and equation numbering required.


# Phase 4 approved pre-production decisions

## D16 — P01 final sequence-based grouping family

**Date:** 2026-07-31  
**Status:** APPROVED  
**Requested by:** Phase 4 pre-production freeze  
**Phase:** Corrected core production  
**Reviewer items affected:** R1.4, R1.5, R2.5.9

### Decision

The Phase 4 primary sequence-based intervention family consists of every contiguous substring partition of a five-symbol motif for substring lengths 1–4 and every valid start position. This gives 14 deterministic maps spanning leading, trailing, and internal motif positions. The length-five partition is represented only by the explicit identity endpoint.

### Rationale

This family removes the unexplained privilege of the leading motif edge while retaining a transparent sequence-based coarse-graining. It introduces no distance metric or clustering hyperparameter. The prespecified pilot generated 14 unique canonical assignment hashes and retained separate constant and identity endpoints.

### Alternatives considered

- Leading-prefix maps only.
- A Hamming-distance clustering family.
- Leading, trailing, and one hand-selected internal map.

### Consequences

**Code affected:** Phase 4 map-panel construction.  
**Analyses affected:** Corrected core intervention frontiers.  
**Figures affected:** None in Phase 4.  
**Manuscript sections affected:** Future intervention Methods and Appendix.  
**Previously generated outputs invalidated:** Submitted prefix-family intervention results remain non-confirmatory.

### Verification required

Save every assignment, canonical hash, substring start, substring length, and actual group count. Collapse exact aliases before frontier construction.

### Supersedes

Resolves P01 and implements D09.

---

## D17 — P02 two continuation seeds per intervention

**Date:** 2026-07-31  
**Status:** APPROVED  
**Requested by:** Phase 4 pre-production freeze  
**Phase:** Corrected core production  
**Reviewer items affected:** R1.5, R1.8

### Decision

Use two paired continuation seeds per actual trajectory and intervention map.

### Rationale

In the prespecified eight-seed pilot, one seed already met the numerical stability thresholds (RMSE 0.08898 and 95th-percentile absolute error 0.12372 model-fitness units relative to the eight-seed mean). Two seeds improved these values to RMSE 0.06029 and 95th-percentile absolute error 0.10857. Two is selected rather than one because the controlling specification calls for nested continuation seeds where feasible and because at least two seeds preserve an estimable within-map technical variance.

### Alternatives considered

- One seed, the smallest candidate satisfying the numerical pilot thresholds.
- Four, six, or eight seeds.

### Consequences

**Code affected:** Phase 4 production settings only.  
**Analyses affected:** Map-level viability is the mean of two nested technical continuations.  
**Figures affected:** None in Phase 4.  
**Manuscript sections affected:** Future Statistical Methods and captions.  
**Previously generated outputs invalidated:** None; pilot outputs are diagnostic only.

### Verification required

Continuation indices must remain nested within map and evolved baseline. They must never be counted as independent replicates. Common-random-number stream keys must exclude map identity.

### Supersedes

Resolves P02.

---

## D18 — P03 36-generation intervention horizon

**Date:** 2026-07-31  
**Status:** APPROVED  
**Requested by:** Phase 4 pre-production freeze  
**Phase:** Corrected core production  
**Reviewer items affected:** R1.2, R1.4, R1.6

### Decision

Use a fixed intervention horizon of 36 generations for the corrected core analysis.

### Rationale

Against the prespecified 36-generation reference, the 12-generation horizon failed the rank-stability rule (Spearman 0.9041), and the 24-generation horizon also failed the prespecified rank threshold (Spearman 0.9666 < 0.98), despite small absolute differences. Therefore the longest prespecified horizon is required.

### Alternatives considered

- 12 generations.
- 24 generations.

### Consequences

**Code affected:** Phase 4 production settings only.  
**Analyses affected:** Primary mean-future-fitness viability is averaged over 36 generations.  
**Figures affected:** None in Phase 4.  
**Manuscript sections affected:** Future intervention Methods.  
**Previously generated outputs invalidated:** Submitted 24-generation intervention estimates remain non-confirmatory.

### Verification required

Every continuation row must record the 36-point mean-fitness trajectory and the fixed horizon.

### Supersedes

Resolves P03.

---

## D19 — P04 strict one-percent recovery target

**Date:** 2026-07-31  
**Status:** APPROVED  
**Requested by:** Phase 4 pre-production freeze  
**Phase:** Corrected core production  
**Reviewer items affected:** R1.4, R1.5

### Decision

Use

\[
V_{\mathrm{target},r}
=
V_{\mathrm{actual},r}
-0.01\left(V_{\mathrm{actual},r}-V_{\mathrm{constant},r}\right).
\]

No interpolation is permitted. The semantic estimate is the smallest tested retained-information coordinate whose discrete monotone frontier reaches the target. Target failures remain right-censored lower bounds.

### Rationale

The one-percent target preserves the submitted strict recovery standard rather than loosening it after observing corrected outcomes. In the prespecified pilot, paired actual and identity continuations recovered exactly, with maximum absolute trajectory difference zero, so Monte Carlo endpoint noise does not require a relaxed tolerance.

### Alternatives considered

- 2.5% recovery tolerance.
- 5% recovery tolerance.
- A tolerance selected from favorable production frontiers.

### Consequences

**Code affected:** Phase 4 target rule.  
**Analyses affected:** Replicate-specific target detection and censoring.  
**Figures affected:** None in Phase 4.  
**Manuscript sections affected:** Future intervention and statistical Methods.  
**Previously generated outputs invalidated:** Submitted interpolated and ordinary lower-bound estimates.

### Verification required

Identity recovery must pass for every production block. Censored values must remain missing point estimates with explicit lower bounds.

### Supersedes

Resolves P04.

---

## D20 — P05 conservative pooled primary frontier

**Date:** 2026-07-31  
**Status:** APPROVED  
**Requested by:** Phase 4 pre-production freeze  
**Phase:** Corrected core production  
**Reviewer items affected:** R1.4, R1.5, R2.5.9

### Decision

For each independently evolved baseline replicate, construct one primary discrete monotone upper frontier pooling unique maps from:

- balanced-random grouping;
- affinity-rank grouping;
- the D16 contiguous-substring family;
- the constant endpoint;
- the identity endpoint.

Collapse exact duplicate assignments by canonical hash. Do not bin, smooth, or interpolate. Affinity-profile k-means is excluded from Phase 4 production and from the primary frontier.

### Rationale

The pooled neutral/conservative family samples multiple forms of information loss without allowing the function-preserving k-means diagnostic to dominate the upper envelope. The prespecified map panel contains 34 unique maps with complete constant-to-identity coverage.

### Alternatives considered

- Family-specific primary frontiers only.
- All methods including affinity-profile k-means.
- A prefix-only frontier.

### Consequences

**Code affected:** Phase 4 map panel and frontier input.  
**Analyses affected:** All Gate 4 semantic estimates.  
**Figures affected:** None in Phase 4.  
**Manuscript sections affected:** Future intervention Methods and method-ablation supplement.  
**Previously generated outputs invalidated:** Submitted binned, smoothed, interpolated, and k-means-sensitive primary frontiers.

### Verification required

Save the fixed panel before production, require unique hashes, and record method membership for every map-level point.

### Supersedes

Resolves P05. P06 remains deferred because affinity-profile clustering is not run in Phase 4.
