# CAUSAL_SPECIFICITY.md

## Project

**Manuscript:** `rsif-2026-0516`  
**Phase:** Phase 5 — causal specificity  
**Date:** 2026-07-31  
**Gate:** **Gate 5 PASSED**

## 1. Question tested

Phase 4 showed that the corrected sequence-selective result survives position conditioning, finite-sample correction, direct retained-information measurement, identity endpoints, and replicate-level inference. It also showed that positive value of information exists even at low transmission fidelity, so part of the effect is expected from the built-in affinity-to-fitness architecture.

Phase 5 therefore asked the narrower causal question:

> Does full selection under a stable native mapping produce a reproducible excess in viability-relevant information beyond the architectural effect that remains under neutral propagation, weakened selection, reassigned affinity profiles, mismatched fitness maps, nonnative stable topologies, or a temporally changing topology?

The primary always-defined outcome was value of information,

\[
\Delta V = V_{\mathrm{actual}} - V_{\mathrm{constant}}.
\]

## 2. Prespecified design

The design was frozen in `PHASE_05_PLAN.md` and decisions D21–D25 before Phase 5 implementation or production.

All confirmatory controls used:

- transmission fidelity `p = 1.0`;
- 20 matched independently evolved seed blocks;
- the archived Phase 4 full-selection/native result as the reference;
- the unchanged 34-map D20 panel;
- two paired continuation seeds per map;
- a 36-generation intervention horizon;
- the strict discrete 1% recovery target;
- one frontier per evolved population and control realization;
- explicit target reach and censoring.

No corrected Phase 4 baseline or intervention analysis was rerun or retuned.

## 3. Controls

### 3.1 Neutral and reduced selection

Parent probabilities were varied through

\[
\pi_i(\alpha)
=
(1-\alpha)N^{-1}
+
\alpha F_i\left(\sum_jF_j\right)^{-1}.
\]

The controls were:

- neutral propagation: `alpha = 0.0`;
- reduced selection: `alpha = 0.25`;
- full selection reference: `alpha = 1.0` from the Phase 4 archive.

The same initial-population, observation, and propagation streams were used within each matched seed block.

### 3.2 Complete affinity-profile reassignment

Two complete derangements were generated per archived native population. Every one of the 1,024 four-state affinity profiles was transferred to a different motif identity; the profile multiset was preserved exactly and no motif retained its original profile.

### 3.3 Fitness-map mismatch

Two nonnative topologies were evaluated per archived native population. Each mismatch preserved the exact category counts and symmetry of the native topology: eight directed promoting edges, six directed reducing edges, and two directed neutral edges.

### 3.4 Alternative stable topologies

The complete 30-topology matched universe was enumerated. Two alternatives were chosen by the prespecified maximum-Hamming-distance rule without consulting outcomes:

- topology A: `topology_00`, category vector `NPPPPR` for unordered pairs `01,02,03,12,13,23`;
- topology B: `topology_11`, category vector `PPNRPP`;
- native topology: `topology_06`, category vector `PNPPRP`.

Twenty populations were evolved under each alternative. Each was evaluated under its native topology and the other alternative topology.

### 3.5 Temporally unstable topology null

Twenty populations were evolved while the matched topology changed every generation, with no immediate repeat. The same scheduled topology sequence was shared by actual and intervened trajectories within each continuation.

## 4. Production dataset

Phase 5 produced:

- 100 newly evolved control populations;
- 220 control-realization frontiers;
- 15,400 continuation-level rows;
- 34 unique intervention maps plus the actual trajectory per frontier;
- two continuation rows per map;
- 40 complete affinity derangements;
- 40 matched topology-mismatch evaluations;
- 60 archived unstable-topology schedules;
- six paired Gate 5 contrasts over 20 independent seed blocks.

All 220 identity endpoints recovered baseline information and paired actual viability exactly. All 220 control-realization targets were reached; no censored value was imputed. In 210/220 realizations, the strict target was first reached only at identity. The Phase 5 result therefore does not establish general semantic compression.

## 5. Value-of-information levels

| Condition | Mean value of information | SD | Independent seed blocks |
|---|---:|---:|---:|
| Native topology, full selection (Phase 4 archive) | 11.9072 | 1.3351 | 20 |
| Neutral propagation | 5.8911 | 1.4861 | 20 |
| Reduced selection (`alpha=0.25`) | 8.3911 | 1.8260 | 20 |
| Complete affinity-profile reassignment | 6.6916 | 1.9395 | 20 |
| Matched fitness-topology mismatch | 10.0842 | 1.3339 | 20 |
| Alternative topology A, native evaluation | 11.3692 | 0.9259 | 20 |
| Alternative topology A, cross-evaluated under B | 8.9207 | 1.7450 | 20 |
| Alternative topology B, native evaluation | 11.7998 | 1.5034 | 20 |
| Alternative topology B, cross-evaluated under A | 8.6961 | 1.8054 | 20 |
| Temporally unstable topology | 10.2498 | 0.6740 | 20 |

The positive values retained by neutral, reassigned, mismatched, and unstable controls confirm that a substantial architectural sensitivity is built into the model. The Gate 5 claim concerns the additional excess produced by selection and stable mapping alignment.

## 6. Prespecified paired contrasts

Two-sided paired randomization tests used one aggregate difference per matched independently evolved seed block. Benjamini–Hochberg correction was applied across all six tests.

| Prespecified contrast | Mean difference | 95% paired-block bootstrap interval | Positive seed blocks | p | BH q | Result |
|---|---:|---:|---:|---:|---:|---|
| Full selection − neutral | 6.0161 | [4.9878, 6.9431] | 20/20 | 0.0001 | 0.0001 | Pass |
| Full selection − reduced selection | 3.5161 | [2.6042, 4.4026] | 18/20 | 0.0001 | 0.0001 | Pass |
| Native mapping − affinity reassignment | 5.2156 | [4.3843, 6.1938] | 20/20 | 0.0001 | 0.0001 | Pass |
| Native topology − topology mismatch | 1.8230 | [1.1257, 2.5401] | 18/20 | 0.0001 | 0.0001 | Pass |
| Alternative native − cross-evaluated | 2.7761 | [2.0839, 3.4558] | 19/20 | 0.0001 | 0.0001 | Pass |
| Stable fixed topology − unstable topology | 1.3347 | [0.8940, 1.7830] | 18/20 | 0.0001 | 0.0001 | Pass |

All six prespecified contrasts passed.

## 7. Gate 5 decision

Gate 5 required:

1. positive full-minus-neutral and full-minus-reduced effects;
2. reduction under complete affinity-profile reassignment;
3. reduction under matched fitness-map mismatch;
4. native advantage for populations evolved under two alternative stable topologies;
5. reduction under the temporally unstable topology null;
6. positive mean differences with BH-adjusted `q < 0.05` for all six contrasts;
7. exact identity recovery;
8. explicit censoring;
9. unchanged Phase 4 archive.

Every criterion passed.

**Gate 5: PASSED.**

## 8. Supported interpretation

The strongest result supported at this stage is:

> Within Model B at the primary `p = 1.0` condition, full selection under a stable native motif-affinity/fitness mapping produces an additional viability-relevant information component beyond the nonzero sensitivity built into the architecture. This excess is reduced by weakening or removing selection, reassigning complete affinity profiles among motif identities, evaluating under a nonnative matched fitness topology, cross-evaluating populations evolved under alternative stable topologies, and removing temporal mapping stability.

The result supports selection dependence, mapping specificity, and a requirement for stable mapping identity within the implemented model.

It does **not** establish that:

- all measured value of information was produced by evolution;
- intermediate coarse-grainings generally preserve near-native viability;
- the original topology is uniquely privileged;
- the effect is general across model structure or parameter space;
- the model is a chemically mechanistic protocell-fission system;
- the result demonstrates a historical prebiotic transition.

The next analytical task is to determine generality through the staged model-structure and parameter-sensitivity design. Final figures and manuscript rewriting remain deferred.
