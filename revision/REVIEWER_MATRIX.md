# REVIEWER_MATRIX.md

## Project

**Manuscript:** `rsif-2026-0516`  
**Purpose:** Track every reviewer concern from comment to completed code, analysis, figure, manuscript change, and response-letter evidence.

This matrix is subordinate to `REVISION_SPEC_v2.md`. If a proposed action conflicts with that specification, the specification controls unless the change is recorded in `DECISIONS_LOG.md`.

## Status legend

| Status | Meaning |
|---|---|
| `NOT STARTED` | No revision work completed |
| `PLANNED` | Action defined but prerequisite phase not complete |
| `IN PROGRESS` | Work is actively underway |
| `BLOCKED` | Waiting on a prerequisite, decision, or dataset |
| `PILOT PASSED` | Small-scale validation completed |
| `COMPLETE` | Analysis or manuscript change completed |
| `VERIFIED` | Completed and independently checked against code, outputs, and manuscript |
| `NOT ADOPTED` | Reviewer suggestion considered but not implemented; rationale required |

## Phase-gate status

| Gate | Status | Evidence |
|---|---|---|
| Gate 1 — code validity | `PASSED` | `PHASE_01_HANDOFF.md` |
| Gate 2 — information-measure validity | `PASSED` | `INFORMATION_MEASURE_VALIDATION.md`; `PHASE_02_HANDOFF.md` |
| Gate 3 — statistical-pipeline validity | `PASSED` | `STATISTICAL_PIPELINE_VALIDATION.md`; `PHASE_03_HANDOFF.md` |
| Gate 4 — core-result survival | `PASSED` | `CORE_RESULT_SURVIVAL.md`; `VALIDATION_PHASE4.md`; `PHASE_04_HANDOFF.md` |
| Gate 5 — causal specificity | `PASSED` | `CAUSAL_SPECIFICITY.md`; `VALIDATION_PHASE5.md`; `PHASE_05_HANDOFF.md` |

## Revision-order rule

Proceed in this order:

1. code and implementation audit;
2. corrected information measures;
3. replicate-level intervention and statistical pipeline;
4. corrected core rerun;
5. causal and circularity controls;
6. focused model-structure and parameter robustness;
7. result freeze;
8. model and intervention figures;
9. manuscript rewrite;
10. response letter and reproducibility release.

No manuscript claim should be marked `VERIFIED` until its supporting analysis has passed the relevant phase gate.

# Referee 1

## R1.1 — Novelty relative to the previous Model B paper

| Field | Entry |
|---|---|
| **Concern** | The manuscript does not clearly distinguish its contribution from the earlier Model B paper. |
| **Decision** | Concede. The sequence-agnostic condition and inheritance-fidelity effects are not new. The new contribution must be the intervention-based decomposition of syntactic and viability-relevant information. |
| **Required action** | Create an explicit novelty table comparing the prior paper with the revised manuscript. Rewrite the final Introduction paragraphs around the genuinely new analyses. |
| **Dependency** | Corrected information measures and replicate-level intervention results must be frozen first. |
| **Evidence** | Table showing which model components, controls, measures, and conclusions appeared previously and which are new. |
| **Manuscript location** | Introduction; Discussion; optional supplementary comparison table. |
| **Status** | `PLANNED` |

## R1.2 — Circularity and built-in alignment between affinity, topology, and fitness

| Field | Entry |
|---|---|
| **Concern** | Viability-relevant information may be built into the model because motif affinities affect the same metabolite states used to calculate fitness. |
| **Decision** | Treat the existence of a causal channel as built into the architecture; test whether evolution produces mapping-specific enrichment beyond that baseline. |
| **Required action** | Add selection-strength controls, complete affinity-profile reassignment, post-evolution fitness-map mismatch, alternative stable topologies, and a temporally unstable map null. |
| **Dependency** | Corrected information estimator and replicate-specific frontier pipeline. |
| **Evidence** | Phase 5 used 20 matched independently evolved seed blocks and the archived Phase 4 native/full-selection result. All six prespecified paired value-of-information contrasts were positive and survived BH correction (`q=0.0001` each): full minus neutral `6.0161`, full minus reduced `3.5161`, native minus affinity-reassigned `5.2156`, native minus topology-mismatch `1.8230`, alternative-native minus cross-evaluated `2.7761`, and stable minus temporally unstable `1.3347`. All 220 identity endpoints recovered exactly; the Phase 4 archive remained unchanged. |
| **Manuscript location** | Methods: controls; Results: causal specificity; Discussion: built-in channel versus evolved alignment. |
| **Status** | `IN PROGRESS` |

## R1.3 — Positional segment bias confounds total motif–metabolite MI

| Field | Entry |
|---|---|
| **Concern** | Total `I(M;Z)` can be generated indirectly through motif position and positional segment bias, especially in the sequence-agnostic condition. |
| **Decision** | Replace raw MI as the primary sequence-specific measure with position-conditioned MI. |
| **Required action** | Calculate `I(M;Z|S)`, permutation-correct it within segment, and report `I(M;S)`. Consider exact-position conditioning as a robustness check. |
| **Dependency** | Code validation and MI unit tests. |
| **Evidence** | Phase 4 production: 400 independent evolved baselines were analyzed with 200 within-segment permutations each. At fidelity 1.0, corrected conditional information differed by 0.25342 bits (selective minus agnostic; replicate-level permutation p=0.0001); the agnostic mean was -0.00023 bits. |
| **Manuscript location** | Analytical expectations; Methods; Results; revised baseline figure. |
| **Status** | `IN PROGRESS` |

## R1.4 — Preserved-information heuristic is not actual retained information

| Field | Entry |
|---|---|
| **Concern** | `I(M;Z) log2(K) / log2(4^5)` is a resolution heuristic, not the mutual information preserved by a grouping map. |
| **Decision** | Replace the heuristic with directly measured retained information. |
| **Required action** | Compute `I(g(M);Z|S)` for every intervention. Add constant and identity endpoints. Compare empirical and expected-channel estimates where useful. |
| **Dependency** | Corrected conditional-MI implementation and finalized grouping-map inventory. |
| **Evidence** | Phase 4 production: actual retained information was computed for every one of 34 unique maps in every baseline block; all 400 identity endpoints recovered baseline information and paired viability exactly. The strict target was reached in all blocks without imputation. |
| **Manuscript location** | Methods; Appendix; all intervention figures and tables. |
| **Status** | `IN PROGRESS` |

## R1.5 — Pseudoreplication and intervention-point statistics

| Field | Entry |
|---|---|
| **Concern** | Hundreds of intervention points are nested within a small number of independently evolved populations and cannot be treated as independent replicates. |
| **Decision** | The independently evolved baseline population is the primary inferential unit. |
| **Required action** | Build one frontier and semantic estimate per baseline replicate; use replicate-level permutation tests and block bootstrap; treat continuation seeds as technical replicates. |
| **Dependency** | Corrected intervention pipeline. |
| **Evidence** | Phase 4 production: one frontier was constructed for each of 400 independent evolved baselines. Two continuation seeds were nested within map and baseline. Inference used 2,000 complete-block bootstrap draws per fidelity and replicate-level permutation tests; no intervention point or continuation seed was counted as independent. |
| **Manuscript location** | Statistical Methods; Results; every relevant figure caption. |
| **Status** | `IN PROGRESS` |

## R1.6 — Insufficient parameter sensitivity and generality

| Field | Entry |
|---|---|
| **Concern** | Main conclusions may depend on one arbitrary default parameterization. |
| **Decision** | Use a staged sensitivity design after the corrected core result is established. |
| **Required action** | Construct a focused phase diagram over inheritance and effective affinity/noise ratios; then use a space-filling screen over major structural parameters. Apply the full semantic pipeline only to representative regions. |
| **Dependency** | Core corrected analysis and causal controls must be frozen. |
| **Evidence** | Phase map distinguishing null, syntactic-only, viability-relevant, and strong-adaptation regimes; sensitivity summary with uncertainty. |
| **Manuscript location** | Methods; Results; Discussion; supplement. |
| **Status** | `PLANNED` |

## R1.7 — Claims exceed what the model establishes

| Field | Entry |
|---|---|
| **Concern** | Terms such as “biological information,” “pre-genetic protocell,” and “semantic transition” may be interpreted as claims about historical or chemically realistic origins of life. |
| **Decision** | Narrow the claims to model-defined viability-relevant information in an abstract protocell-like compositional-resampling model. |
| **Required action** | Complete a manuscript-wide terminology audit; separate demonstration, theoretical implication, and speculation. Rewrite title and abstract last. |
| **Dependency** | Final supported result and inheritance-scope wording must be frozen. |
| **Evidence** | Consistent terminology in title, abstract, text, captions, and response letter. |
| **Manuscript location** | Entire manuscript, especially title, abstract, Introduction, Discussion, and Conclusion. |
| **Status** | `PLANNED` |

## R1.8 — Reproducibility and validation of AI-assisted code

| Field | Entry |
|---|---|
| **Concern** | Public code, seed control, dependency locking, validation, and AI-assisted-code review are insufficiently documented. |
| **Decision** | Treat reproducibility as a formal phase gate before new production runs. |
| **Required action** | Audit all RNG use; add deterministic tests, analytical checks, seed ledger, locked environment, exact commands, archived raw data, release tag, DOI, license, and clean-room rerun. |
| **Dependency** | None; this is an initial prerequisite. |
| **Evidence** | Phase 4: 57 tests pass; all states, assignments, hashes, trajectories, and seed ledgers are archived; a clean deterministic rerun reproduced one full baseline and its complete intervention block exactly. Release tag, DOI, license review, and external clean-room execution remain later release tasks. |
| **Manuscript location** | Software and reproducibility subsection; Data accessibility; AI-use statement. |
| **Status** | `IN PROGRESS` |

## R1.9 — Figure and manuscript presentation problems

| Field | Entry |
|---|---|
| **Concern** | Figures lack raw replicate information and complete caption details; submitted proof contains duplicated or inconsistent panel references and formatting artifacts. |
| **Decision** | Rebuild figures after result freeze and perform a full production audit. |
| **Required action** | Show raw independent replicates, define uncertainty and statistical unit, report target status, correct panel references, page numbering, placeholders, and author statements. |
| **Dependency** | Final frozen datasets and statistical outputs. |
| **Evidence** | Figure-source tables; caption checklist; final PDF audit record. |
| **Manuscript location** | Figures, captions, supplementary figures, front and end matter. |
| **Status** | `PLANNED` |

# Referee 2

## R2.1 — Terminology is unclear or biologically overinterpreted

| Field | Entry |
|---|---|
| **Concern** | Terms including molecular correlation, persistence, stabilization, adaptive amplification, motif–metabolite interaction, productive pairs, viability, and biological information are insufficiently defined. |
| **Decision** | Add a definition ladder and use operational, model-specific terms. |
| **Required action** | Define each state variable and process before interpretation. Replace broad terms with motif–metabolite statistical association, persistence under the specified operator, selection-driven fitness gain, fitness-promoting/reducing adjacency, and model-defined viability-relevant information. |
| **Dependency** | Model-scope and notation decisions. |
| **Evidence** | Glossary/notation table and consistent terminology audit. |
| **Manuscript location** | Model overview; Methods; Discussion; figure captions. |
| **Status** | `PLANNED` |

## R2.2 — Is this actually a protocell model?

| Field | Entry |
|---|---|
| **Concern** | The model lacks literal membrane growth, molecular production, mass conservation, and physical fission. |
| **Decision** | Retain the original operator as the principal and only inheritance model, but classify it accurately. No new inheritance simulations will be added. |
| **Required action** | Describe Model B as a Wright–Fisher-like compositional-resampling model of abstract protocell-like units. Remove claims of literal physical partitioning or fission. Add a dedicated limitations paragraph. |
| **Dependency** | Implementation audit. |
| **Evidence** | Exact algorithmic description matched to code; wording audit across manuscript and figures. |
| **Manuscript location** | Abstract; Model overview; transmission Methods; Discussion limitations; Figure 1. |
| **Status** | `PLANNED` |

## R2.3 — Some results appear deductively expected; model may be unnecessarily complicated

| Field | Entry |
|---|---|
| **Concern** | In the sequence-agnostic regime, sequence cannot causally affect metabolite sampling after conditioning on position; in the sequence-selective regime, heritable sequence effects predict stronger response with higher transmission. |
| **Decision** | Concede the qualitative direction of the baseline result and add analytical expectations. Reframe the baseline sweep as validation, not the main novelty. |
| **Required action** | Derive the reduced transition logic and explain which outcomes are expected by construction versus which require simulation: threshold sharpness, finite-population behavior, semantic frontier, mapping specificity, and parameter dependence. |
| **Dependency** | Corrected measures and final core results. |
| **Evidence** | Phase 5 separates expected architectural sensitivity from evolved mapping specificity: positive value of information persisted in disruption controls, but full selection exceeded neutral and reduced selection, native mappings exceeded profile reassignment and topology mismatch, two alternative stable topologies showed native-over-cross excess, and a stable topology exceeded the changing-topology null. The analytical expectation subsection and manuscript comparison remain to be written after result freeze. |
| **Manuscript location** | End of Introduction or start of Methods; Results framing; Discussion. |
| **Status** | `IN PROGRESS` |

## R2.4 — Add one or two visual model “life-cycle” figures

| Field | Entry |
|---|---|
| **Concern** | Readers cannot construct the complete oligomer and population update from the verbal and mathematical description alone. |
| **Decision** | Fully adopt. |
| **Required action** | Create a model-workflow figure using a short oligomer and a separate intervention schematic. Explicitly distinguish inherited sequences from transient local-state labels and depict the population update as compositional resampling, not physical fission. |
| **Dependency** | Model terminology, notation, and algorithm audit. |
| **Evidence** | Vector figure source and caption checked against implementation. |
| **Manuscript location** | Main text, early Methods. |
| **Status** | `PLANNED` |

## R2.5.1 — Why four metabolite classes?

| Field | Entry |
|---|---|
| **Concern** | The number four appears arbitrary and is not biologically justified. |
| **Decision** | State that four is a tractable, nontrivial default topology, not an empirical chemical classification. |
| **Required action** | Add rationale and parameter-table entry. Include metabolite-class number in staged structural sensitivity analysis with matched topology density and effect scale. |
| **Dependency** | Sensitivity phase. |
| **Evidence** | Results for alternative class counts or a clearly prespecified subset; normalized information diagnostic. |
| **Manuscript location** | Model overview; parameter table; sensitivity Methods and Results. |
| **Status** | `PLANNED` |

## R2.5.2 — Why does every overlapping motif sample a metabolite?

| Field | Entry |
|---|---|
| **Concern** | Fifty-six overlapping windows cannot plausibly represent simultaneously occupied, independent binding sites because of steric exclusion and physical overlap. |
| **Decision** | Reinterpret the variable accurately as a transient probabilistic local chemical-state assignment, not literal simultaneous ligand occupancy. |
| **Required action** | Rewrite all binding language. Add a model-figure note and a limitations statement. Include motif-window density or non-overlap in focused structural robustness if retained in the final scope. |
| **Dependency** | Model-structure sensitivity decision. |
| **Evidence** | Terminology audit; optional stride/non-overlap robustness results. |
| **Manuscript location** | Model overview; sampling Methods; Figure 1; Discussion limitations. |
| **Status** | `PLANNED` |

## R2.5.3 — Status of `(0,2)` and `(2,0)`

| Field | Entry |
|---|---|
| **Concern** | The manuscript does not classify the two remaining ordered adjacency pairs. |
| **Decision** | They are fitness-neutral. |
| **Required action** | Add an explicit complete adjacency table or matrix with promoting, reducing, and neutral categories. |
| **Dependency** | Implementation audit to confirm code and text match. |
| **Evidence** | Unit test and full pair table. |
| **Manuscript location** | Fitness Methods; Appendix; model figure. |
| **Status** | `PLANNED` |

## R2.5.4 — Why four segments, and where are their borders?

| Field | Entry |
|---|---|
| **Concern** | Segment count, boundaries, and favored-state ordering are not explicit or justified. |
| **Decision** | Describe them as four equal positional bins over motif-window start locations, not literal RNA domains. |
| **Required action** | Specify positions 1–14, 15–28, 29–42, and 43–56 and favored-state order `2,0,3,1`. Explain that four is a balanced default. Include segment architecture in sensitivity analysis. |
| **Dependency** | Implementation audit and sensitivity phase. |
| **Evidence** | Exact boundary test; segment-count/order robustness where included. |
| **Manuscript location** | Sampling Methods; Figure 1; parameter table. |
| **Status** | `PLANNED` |

## R2.5.5 — Meaning of the logit equation and choice of `b=2.0`

| Field | Entry |
|---|---|
| **Concern** | The indicator-function equation is hard to parse and the bias value lacks justification. |
| **Decision** | Rewrite the equation in clear indexed and piecewise form. Describe `b=2.0` as a dimensionless moderate default, not a weak empirical effect. |
| **Required action** | Quantify its consequence at the default temperature; vary `b/Theta` in the focused phase diagram. |
| **Dependency** | Notation audit and sensitivity phase. |
| **Evidence** | Probability calculation and parameter sweep. |
| **Manuscript location** | Sampling Methods; parameter table; sensitivity Results. |
| **Status** | `PLANNED` |

## R2.5.6 — Why is the softmax temperature `1.2`?

| Field | Entry |
|---|---|
| **Concern** | The parameter appears arbitrary and may be mistaken for a physically calibrated temperature. |
| **Decision** | Call it a dimensionless softmax temperature or sampling-noise scale. |
| **Required action** | Explain limiting behavior and analyze effective ratios `sigma_a/Theta` and `b/Theta`. Include temperature in sensitivity analysis. |
| **Dependency** | Sensitivity phase. |
| **Evidence** | Phase diagram or focused temperature sweep. |
| **Manuscript location** | Sampling Methods; parameter table; sensitivity Results. |
| **Status** | `PLANNED` |

## R2.5.7 — Why `F_min=0.1`, `r=2.0`, and `q=0.5`?

| Field | Entry |
|---|---|
| **Concern** | Fitness floor and reward/penalty values are unexplained; the count normalization is unclear. |
| **Decision** | Treat the floor as a numerical safeguard and the reward/penalty asymmetry as phenomenological. |
| **Required action** | Clarify that adjacency totals are mean counts per oligomer, not fractions. Report floor-hit frequency. Test floor and reward/penalty sensitivity and consider a fraction-normalized robustness formulation. |
| **Dependency** | Implementation audit and sensitivity phase. |
| **Evidence** | Floor-hit table; selected parameter robustness results. |
| **Manuscript location** | Fitness Methods; parameter table; sensitivity Results. |
| **Status** | `PLANNED` |

## R2.5.8 — Population amplification, random environmental oligomers, and inheritance

| Field | Entry |
|---|---|
| **Concern** | The original operator is difficult to interpret physically and appears to assume an unlimited environmental oligomer source and parent-correlated reconstruction. |
| **Decision** | Retain the original operator as the only inheritance model. Do not add new inheritance controls or simulations. Answer through exact description and narrowed scope. |
| **Required action** | State that parent-derived identities are sampled with replacement, non-parental identities come from an idealized uniform reservoir, and `p` is compositional coupling rather than molecular retention. Replace “division” and “physical partitioning” where misleading. |
| **Dependency** | Implementation audit only. |
| **Evidence** | Algorithm-to-manuscript comparison; manuscript-wide wording audit. |
| **Manuscript location** | Abstract; population update Methods; Figure 1; Discussion limitations. |
| **Status** | `PLANNED` |

## R2.5.9 — Prefix length and arbitrary preference for prefixes

| Field | Entry |
|---|---|
| **Concern** | Prefix length is unspecified, requested group counts do not necessarily equal actual groups, and the leading edge has no privileged status. |
| **Decision** | Correct the implementation description and remove orientation arbitrariness from the primary sequence-based intervention family. |
| **Required action** | Inventory every distinct grouping map. Add explicit constant and identity endpoints. Use leading, trailing, and internal substring maps at natural resolutions, or another prespecified orientation-neutral sequence grouping. Do not count duplicate maps as distinct interventions. |
| **Dependency** | Code audit before corrected intervention rerun. |
| **Evidence** | Phase 4 decision D16 fixed all 14 contiguous-substring maps spanning leading, trailing, and internal positions. The 34-map production panel has unique canonical hashes, explicit constant and identity endpoints, and no duplicate assignments. |
| **Manuscript location** | Intervention Methods; Appendix; supplementary method-ablation figure. |
| **Status** | `IN PROGRESS` |

## R2.6.1 — Equations are not labeled

| Field | Entry |
|---|---|
| **Concern** | Displayed equations cannot be referenced unambiguously. |
| **Decision** | Number all displayed equations. |
| **Required action** | Use sequential main-text numbers and appendix numbers such as `(A1)`, `(A2)`. Cross-reference every reused definition. |
| **Dependency** | Final notation must be frozen first. |
| **Evidence** | Equation-number audit. |
| **Manuscript location** | Entire manuscript and appendix. |
| **Status** | `PLANNED` |

## R2.6.2 — Symbol collisions and matrix notation

| Field | Entry |
|---|---|
| **Concern** | Symbols such as `M`, `G`, `H`, `T`, `A`, `P`, `R`, and `Q` are reused for unrelated concepts; matrices and elements are not typographically distinguished. |
| **Decision** | Complete a notation redesign before manuscript rewriting. |
| **Required action** | Reserve distinct symbols for motif identity, oligomer count, retained groups, gap, entropy, intervention horizon, temperature, generation count, affinity matrix, adjacency matrices, and adjacency counts. Bold matrices; use indexed nonbold symbols for elements. |
| **Dependency** | Must be frozen before equation numbering and figures. |
| **Evidence** | Complete notation table and automated/manual symbol audit. |
| **Manuscript location** | Model overview; Methods; Appendix; figure labels. |
| **Status** | `PLANNED` |

# Cross-cutting deliverables

## A. Code and validation deliverables

| Deliverable | Reviewer items supported | Status |
|---|---|---|
| RNG audit and deterministic tests | R1.8 | `VERIFIED` |
| Model implementation manifest | R2.2, R2.5.2–R2.5.9 | `VERIFIED` |
| Grouping-map inventory | R1.4, R1.5, R2.5.9 | `VERIFIED` |
| Conditional-MI validation suite | R1.3 | `VERIFIED` |
| Retained-information endpoint tests | R1.4 | `VERIFIED` |
| Replicate-frontier statistical pipeline | R1.5 | `VERIFIED` |
| Corrected core production dataset and Gate 4 test | R1.3–R1.5, R1.8, R2.5.9 | `VERIFIED` |
| Causal disruption controls | R1.2 | `VERIFIED` |
| Focused sensitivity design | R1.6, R2.5.1, R2.5.4–R2.5.7 | `IN PROGRESS` |

## B. Manuscript deliverables

| Deliverable | Reviewer items supported | Status |
|---|---|---|
| Definition and terminology table | R1.7, R2.1 | `PLANNED` |
| Notation table | R2.6.2 | `PLANNED` |
| Parameter table with basis and sensitivity range | R1.6, R2.5.1, R2.5.4–R2.5.7 | `PLANNED` |
| Model workflow figure | R2.2, R2.4, R2.5.2, R2.5.8 | `PLANNED` |
| Intervention schematic | R1.4, R2.4, R2.5.9 | `PLANNED` |
| Analytical expectations subsection | R2.3 | `PLANNED` |
| Novelty comparison table | R1.1 | `PLANNED` |
| Dedicated model-limitations subsection | R1.7, R2.2, R2.5.2, R2.5.8 | `PLANNED` |
| Numbered equations and cross-references | R2.6.1 | `PLANNED` |
| Revised abstract/title/conclusion | R1.1, R1.7, R2.2 | `BLOCKED` until result freeze |

# Reviewer-response template

For every comment, the final response letter should use:

> **Reviewer comment:**  
> [Exact or carefully shortened comment]
>
> **Response:**  
> [Direct acknowledgement and scientific answer]
>
> **Changes made:**  
> [Specific code, analysis, figure, and prose changes]
>
> **Evidence:**  
> [New figure/table/test/result]
>
> **Location:**  
> [Page, section, equation, figure, or supplementary item]

A suggestion that is not adopted must state:

1. why it was considered;
2. why it is outside the chosen revision scope;
3. what was changed instead;
4. how claims were narrowed to avoid overstating the unsupported point.

# Locked revision decision

> **The original inheritance operator will remain the principal and only inheritance model. No new without-replacement, growth–fission, finite-pool, or mass-conserving inheritance simulations will be added. The reviewer concern will be addressed through accurate classification of the operator, explicit assumptions, narrowed claims, and a dedicated limitations discussion.**

# Immediate next actions

1. Preserve D16–D25 and the archived Phase 4 and Phase 5 states.
2. Prespecify the staged, non-factorial model-structure and parameter-sensitivity design before production.
3. Use independently evolved baseline populations as the inferential unit and retain explicit censoring.
4. Do not create final figures or rewrite the manuscript until generality and result-freeze gates are decided.
5. Continue updating this matrix at every phase gate.
