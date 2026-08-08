# EDITABLE_VECTOR_ARTWORK_HANDOFF.md

## Project state

**Project:** JRSI Major Revision—Semantic Information in Model B  
**Manuscript:** `rsif-2026-0516`  
**Phase completed:** editable master artwork for Figure 1 and Figure 3A  
**Scientific evidence base:** `JRSI_MAJOR_REVISION_PHASE7_GATE8_PASSED_v1(1).zip` only  
**Controlling manuscript-production package:** `JRSI_MANUSCRIPT_PRODUCTION_PLANNING_V1(1).zip`  
**Controlling schematic package:** `JRSI_SCHEMATIC_SPECIFICATION_V1.zip`  
**Gate 8:** remains passed and unchanged  
**Gate 6:** not passed

## 1. Handoff purpose

This handoff closes the editable-artwork construction phase for the two non-quantitative manuscript schematics:

- **Figure 1:** Model B workflow—model unit and sequence windows, transient local-state assignment, model fitness, and population update.
- **Figure 3A:** Counterfactual grouping intervention.

The author created the editable masters in Google Slides using the frozen vector specifications, label dictionary, implementation-traceability record, and the reviewed grayscale visual guides. This handoff records the scientific content that must remain fixed during caption drafting, manuscript placement, and final export.

No analysis, estimator, grouping map, intervention family, target rule, statistical unit, or inferential result was rerun, retuned, reinterpreted, or replaced during artwork construction.

## 2. Controlling hierarchy preserved

The artwork remains subordinate to the following documents, in order:

1. `FROZEN_CLAIMS_AND_LIMITATIONS.md`
2. `RESULT_FREEZE.md`
3. approved entries D16–D31 in `revision/DECISIONS_LOG.md`
4. `revision/REVIEWER_MATRIX.md`
5. `PHASE_07_HANDOFF.md`
6. `01_TERMINOLOGY_AND_NOTATION_FREEZE.md`
7. `02_FIGURE_SOURCE_AND_SECTION_MAP.md`
8. `03_GATE6_COMPOSITIONAL_RESAMPLING_WORDING_AUDIT.md`
9. `05_GATE6_FINAL_ACCEPTANCE_CHECKLIST.md`
10. `FIGURE_1_VECTOR_SPEC.md`
11. `FIGURE_3A_VECTOR_SPEC.md`
12. `SCHEMATIC_LABEL_DICTIONARY.csv`
13. `SCHEMATIC_IMPLEMENTATION_TRACEABILITY.md`
14. `SCHEMATIC_SPEC_HANDOFF.md`

## 3. Completed artwork

### 3.1 Figure 1 master

The Figure 1 master contains four panels:

- **A. Model unit and sequence windows**
- **B. Transient local-state assignment**
- **C. Model fitness**
- **D. Population update**

The master uses an abstract four-symbol oligomer representation and does not depict literal RNA structure, membranes, molecular occupancy, or physical cell division.

### 3.2 Figure 3A master

The Figure 3A master presents the grouping intervention as a simplified left-to-right transformation:

1. original motif identities and sequence-dependent affinity profiles;
2. assignment of motif identities through the grouping map `g`;
3. component-wise group-average affinity-profile replacement;
4. unchanged motif identities carrying their assigned group-average profiles;
5. constant and identity endpoint cards;
6. the direct retained-information definition;
7. the frozen primary intervention-family statement and k-means exclusion.

Decorative people and snowflake icons were removed. The final visual grammar is algorithmic rather than biological or chemical.

## 4. Figure 1 scientific-content lock

The Figure 1 artwork must retain the following content without semantic alteration.

### Panel A—model unit and sequence windows

- one abstract **model unit** with fixed oligomer slots;
- short illustrative sequence strings rather than the full sequence length;
- overlapping length-five motif windows;
- four equal positional bins over motif-window start positions;
- segment ranges `u = 1–14`, `15–28`, `29–42`, and `43–56` when displayed;
- default favored local-state order by segment: `2, 0, 3, 1`;
- explicit separation of oligomer sequence identities from transient local-state labels.

A window crossing a displayed segment boundary is assigned wholly by its start index `u`; an individual motif window is not divided between segments.

### Panel B—transient local-state assignment

The three inputs converge on **Softmax probability over local-state classes**:

- motif identity `M=m` supplies the sequence-dependent affinity score `a_mz`;
- positional segment supplies the sequence-agnostic positional bias;
- the dimensionless softmax sampling-noise scale `Theta` supplies probability-scale control.

The softmax probability vector is followed by a probabilistic draw and a transient local-state assignment `Z=z`.

Required scope statement:

> **Re-sampled during observation; not a transmitted inventory.**

The arrow from `Theta` points to the softmax-probability operation, not directly to the stochastic draw or final label.

### Panel C—model fitness

- ordered neighboring local-state labels generate ordered adjacency pairs;
- every ordered pair is classified as fitness-promoting, fitness-reducing, or fitness-neutral;
- the complete adjacency-category matrix is present or explicitly referenced;
- `(0,2)` and `(2,0)` are fitness-neutral;
- neutral adjacencies enter neither the promoting nor reducing count;
- there is no separate “neutral adjacency score”;
- model fitness is identified as a model-defined phenomenological score.

Required scope statement:

> **Model-defined phenomenological score; not protocell growth chemistry.**

### Panel D—population update

The population-update flow remains:

1. select one source model unit according to model fitness;
2. read the selected source unit’s empirical oligomer distribution;
3. for each new-unit slot independently:
   - with probability `p`, sample a parent-derived sequence identity **with replacement** from the selected source unit’s empirical oligomer distribution;
   - with probability `1-p`, sample from the idealized uniform sequence reservoir;
4. apply point mutation after sequence assignment;
5. assemble the new model unit.

`p` is parental-composition coupling or compositional-transmission fidelity, not literal molecular retention. The same source sequence identity may occupy more than one new-unit slot.

## 5. Figure 3A scientific-content lock

### 5.1 Grouping transformation

The grouping map is written as:

\[
g:\mathcal{M}\rightarrow\{1,\ldots,K_g\}.
\]

Here, `M` is the motif-identity random variable and `\mathcal{M}` is the set of motif identities. Every illustrated motif identity is assigned by `g`; no motif string changes during the intervention.

For each group, the sequence-dependent affinity profiles are averaged component by component. The same group-average profile is assigned to every motif identity in that group. Therefore:

- within-group affinity-profile distinctions are removed;
- between-group affinity-profile distinctions remain;
- starting population, motif sequence identities, positional segments, adjacency categories, and the population-update rule remain unchanged.

### 5.2 Affinity-profile axes

Each symbolic profile has four components indexed by local-state class:

\[
z\in\{0,1,2,3\}.
\]

The profile x-axis is **Local-state class `z`**, not positional segment. The glyphs are symbolic affinity profiles and are not histograms or quantitative data plots.

### 5.3 Illustrative profile geometry

The following normalized display heights were supplied for consistent construction. They are artwork geometry only and do not represent measured affinity values. They may be scaled uniformly in Google Slides while preserving the component-wise relationships.

| Profile | `z=0` | `z=1` | `z=2` | `z=3` |
|---|---:|---:|---:|---:|
| `AABDC` | 0.15 | 0.45 | 0.85 | 0.35 |
| `CDABA` | 0.55 | 0.75 | 0.65 | 0.15 |
| **Group 1 average** | **0.35** | **0.60** | **0.75** | **0.25** |
| `AACBD` | 0.85 | 0.15 | 0.45 | 0.65 |
| `DABCD` | 0.65 | 0.45 | 0.15 | 0.85 |
| **Group 2 average** | **0.75** | **0.30** | **0.30** | **0.75** |

The intervened rows must therefore show:

- `AABDC` and `CDABA` with the identical Group 1 average profile;
- `AACBD` and `DABCD` with the identical Group 2 average profile;
- visibly distinct Group 1 and Group 2 average-profile shapes.

### 5.4 Endpoint treatment

**Constant endpoint**

- all motif identities are placed in one group;
- `K_g=1`;
- one global average affinity profile is assigned to every motif identity;
- `I(g(M);Z|S)=0`.

**Identity endpoint**

- every motif identity remains distinct;
- `K_g=|\mathcal{M}|`;
- every singleton group retains its original affinity profile;
- `I(g(M);Z|S)=I(M;Z|S)`.

### 5.5 Primary families and retained information

The frozen primary intervention panel includes:

- balanced-random grouping;
- affinity-rank grouping;
- contiguous-substring grouping;
- constant endpoint;
- identity endpoint.

Affinity-profile k-means grouping remains a diagnostic method and is excluded from the primary intervention panel.

Actual retained information is defined only as:

\[
I_{\mathrm{ret},r}(g)=I(g(M);Z\mid S).
\]

It is measured for the specific grouping map `g` and is not inferred from `K_g`, nominal group count, or a logarithmic resolution heuristic.

Required interpretive boundary:

> **Frozen native selective target required the identity endpoint.**

The artwork must not imply semantic compression.

## 6. Artwork quality-control record

### 6.1 Scientific labels and notation

| Check | Status |
|---|---|
| Figure 1 panel headings and main process labels use frozen terminology | Complete at master-artwork stage |
| Figure 1 local-state labels are distinct from sequence identities | Complete at master-artwork stage |
| Figure 1 uses compositional-resampling rather than physical-fission wording | Complete at master-artwork stage |
| Figure 1 explicitly includes “with replacement” on the parent-derived branch | Required in final master and proof |
| Figure 1 matrix classifies `(0,2)` and `(2,0)` as neutral | Required in final master and proof |
| Figure 3A profile axis uses local-state class `z=0,1,2,3` | Complete at master-artwork stage |
| Figure 3A uses `g:\mathcal{M}\rightarrow\{1,\ldots,K_g\}` | Complete at master-artwork stage |
| Figure 3A uses `K_g=|\mathcal{M}|` at the identity endpoint | Complete at master-artwork stage |
| Figure 3A uses `I_ret,r(g)=I(g(M);Z|S)` | Complete at master-artwork stage |
| Figure 3A states k-means exclusion from the primary panel | Complete at master-artwork stage |

### 6.2 Arrow semantics

- Figure 1 arrows represent calculation, stochastic choice, source selection, or explanatory enlargement; none represent physical molecular transport.
- Figure 1D does not show a source unit splitting into daughters.
- Figure 3A arrows represent grouping, arithmetic averaging, and parameter-profile reassignment; none represent movement, deletion, or synthesis of motif sequences.
- Every illustrated motif identity is included in the grouping transformation.

### 6.3 Accessibility and grayscale

The masters were designed in grayscale with meaning redundantly encoded by text, shape, profile geometry, enclosure, and line structure rather than color alone.

Before final journal export, the following proof checks remain mandatory:

- export each master as a grayscale PDF;
- export a 600 dpi grayscale PNG or TIFF proof;
- inspect at intended manuscript display size;
- confirm minimum text size and mathematical-symbol legibility;
- confirm that local-state classes, adjacency categories, segment boundaries, and grouping distinctions remain interpretable without color;
- run color-vision-deficiency checks if any color is added later;
- reopen the PDF/EPS export and compare it with the editable master for font, subscript, symbol, arrowhead, and clipping errors.

### 6.4 Editable-source status

The authoritative editable sources are the author’s Google Slides master artwork. The Google Slides files should be preserved unchanged as the editable source of record. Submission-format PDF/EPS/PNG/TIFF files are derivative exports and must not replace the editable masters.

The actual Google Slides source files and final exports were not bundled into this handoff document. Their filenames, stable links, or archived copies should be entered in the project manifest when the manuscript package is assembled.

## 7. Gate 6 compliance findings

### Figure 1

- compatible with the required fitness-weighted, Wright–Fisher-like compositional-resampling classification;
- no membrane cleavage, daughter-pair, division plane, conserved-molecule transfer, molecular synthesis, or mass-balance imagery is permitted;
- transient local-state assignments are not depicted as simultaneous ligand occupancy;
- model fitness is not depicted as protocell growth chemistry;
- `p` is compositional coupling, and the parent-derived branch is with replacement.

### Figure 3A

- the intervention changes only the sequence-dependent affinity profiles used in local-state assignment;
- motif identities remain unchanged;
- group averages are arithmetic profile averages;
- constant and identity endpoints use the validated limiting relations;
- retained information is directly measured as `I(g(M);Z|S)`;
- k-means is excluded from the frozen primary panel;
- the figure does not claim semantic compression.

### Formal status

These findings do **not** pass Gate 6. Formal Gate 6 remains blocked until the complete revised manuscript, figure text, captions, supplementary material, abstract, Discussion, Conclusion, and response letter are audited together using `05_GATE6_FINAL_ACCEPTANCE_CHECKLIST.md`.

## 8. Remaining production actions that do not affect scientific meaning

The following actions may be completed without reopening the scientific freeze:

- final alignment, spacing, and line-break refinement;
- consistent font embedding and subscript rendering;
- final grayscale and color-vision proofing;
- export to PDF and 600 dpi PNG/TIFF;
- EPS export if required by the journal workflow;
- insertion of stable artwork filenames and links into the production manifest;
- minor proportional scaling of symbolic profile bars, provided every within-group average and between-group distinction is preserved;
- placement within the manuscript layout without changing visible labels or arrow meaning.

Any change to labels, equations, endpoint definitions, intervention-family membership, map logic, population-update logic, or interpretive scope requires review against the controlling specifications before implementation.

## 9. Readiness decision

### Caption drafting

**READY TO PROCEED.**

The scientific content and visual grammar of Figure 1 and Figure 3A are sufficiently fixed to draft final captions against the masters and the traceability record. Captions must not introduce physical-fission, molecular-retention, simultaneous-binding, semantic-compression, or chemical-realism interpretations absent from the artwork and frozen evidence.

### Manuscript placement

**READY FOR PROVISIONAL MANUSCRIPT PLACEMENT.**

The editable masters may be placed into the working manuscript for layout and caption integration. Final publication placement and submission export remain conditional on the grayscale, font, clipping, and accessibility proof checks listed above.

### Gate status

This readiness decision does not mark Gate 6 as passed and does not alter Gate 8.

## 10. Permitted next phase

The next phase may:

- draft the final Figure 1 and Figure 3 captions;
- place the schematics in the working manuscript;
- cross-reference the schematics from the model-overview and intervention Methods sections;
- perform integrated caption–artwork terminology and notation checks.

The next phase must not:

- alter frozen analyses or inferential results;
- convert illustrative profile geometry into quantitative claims;
- add unsupported biological or chemical mechanisms;
- claim physical inheritance, literal fission, or mass conservation;
- claim semantic compression;
- mark Gate 6 as passed before the complete integrated audit.

## 11. Handoff summary

Editable master artwork now exists for Figure 1 and Figure 3A. The scientific transformations, terminology, notation, endpoint logic, intervention-family scope, retained-information definition, and compositional-resampling interpretation are fixed. The artwork is ready for caption drafting and provisional manuscript placement, with final journal export pending routine production proofing and the later integrated Gate 6 audit.
