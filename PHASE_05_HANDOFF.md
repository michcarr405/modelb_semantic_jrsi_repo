# PHASE_05_HANDOFF.md

## Project

**Manuscript:** `rsif-2026-0516`  
**Project:** JRSI Major Revision — Semantic Information in Model B  
**Date:** 2026-07-31  
**Completed phase:** Phase 5 — causal specificity  
**Gate status:** **Gate 5 PASSED**

## 1. Handoff purpose

This file closes Phase 5 and defines the state that may be carried into the next phase. Gates 1–4 were inherited from the versioned Phase 4 package. Phase 5 preserved D16–D20, used the archived Phase 4 core states and result as the full-selection/native reference, implemented the focused D10 controls, and decided Gate 5 before any broad sensitivity sweep, final publication figure, or manuscript rewrite.

## 2. Source provenance

Phase 5 began from the repository and Git history embedded in:

`JRSI_MAJOR_REVISION_PHASE4_GATE4_PASSED_v1(1).zip`

Verified starting points included:

- Phase 3 closure commit `c42fa82040e5d3b32105ef440c520dd6dd7c782d`;
- Phase 3 validated implementation commit `add8a0750d9a2dc0e9d8ef5fbded6bab9175db42`;
- Phase 4 scientific production commit `204010b439bcaf0921a3ed3a82a3e48468ee704e`;
- Phase 4 release tag `phase4-gate4-passed-v1`;
- `PHASE_04_HANDOFF.md` and the full Phase 4 archive manifest.

The older submitted repositories were not used.

## 3. Prespecified Phase 5 decisions

`PHASE_05_PLAN.md` and approved decisions D21–D25 fixed:

- control scope at the primary `p = 1.0` condition;
- 20 matched independently evolved seed blocks;
- neutral selection `alpha=0.0` and reduced selection `alpha=0.25`;
- two complete affinity-profile derangements per archived population;
- two matched nonnative topology evaluations per archived population;
- two objectively selected alternative stable topologies;
- a generation-changing matched-topology null;
- value of information as the primary always-defined Gate metric;
- six paired seed-block contrasts with BH correction;
- Gate 5 passage only if all six contrasts pass.

D16–D20 were not changed.

## 4. Production outputs

The versioned Phase 5 dataset contains:

- 100 newly evolved control states;
- 220 control-realization frontiers;
- 15,400 continuation rows;
- 40 complete affinity derangements;
- 40 topology-mismatch realizations;
- 30 matched topology definitions;
- 60 unstable-topology schedules;
- 2,000 paired-block bootstrap draws per Gate contrast;
- 9,999 paired sign randomizations per Gate contrast.

Primary files are under `results/phase5_causal_specificity/`.

## 5. Gate 5 result

All six prespecified effects were positive and survived BH correction (`q=0.0001` for each):

- full selection minus neutral: `6.0161`;
- full selection minus reduced selection: `3.5161`;
- native mapping minus affinity reassignment: `5.2156`;
- native topology minus matched mismatch: `1.8230`;
- alternative native minus cross-evaluated: `2.7761`;
- stable fixed topology minus unstable topology: `1.3347`.

All bootstrap intervals excluded zero. All 220 identity endpoints recovered exactly. The Phase 4 archive remained unchanged.

**Gate 5 PASSED.**

Full evidence is in `CAUSAL_SPECIFICITY.md`, `VALIDATION_PHASE5.md`, and `results/phase5_causal_specificity/GATE_5_DECISION.json`.

## 6. Interpretation carried forward

The model contains a built-in causal path from motif-dependent local-state sampling to topology-defined fitness. Phase 5 does not erase that fact: neutral, reassigned, mismatched, and unstable controls all retained positive value of information.

What Phase 5 establishes is an additional component. At `p = 1.0`, full selection under a stable native mapping produces more value of information than the relevant architectural and disruption controls. The excess is selection-dependent, mapping-specific, reproducible under two alternative stable topologies, and reduced when topology identity changes through time.

The acceptable claim remains model-specific. Phase 5 does not establish chemical realism, historical occurrence, universality, semantic compression, or generality across parameter space.

## 7. Compression and censoring caution

All 220 control-realization targets were reached, but 210/220 were first reached only at identity. The Phase 4 native selective result likewise required identity in every baseline block. The revision must not claim that a small compressed motif representation generally preserves native viability.

No censored estimate was imputed. The explicit censoring schema remains in force for later analyses.

## 8. Validation

- 63 tests pass;
- 19/19 Phase 5 structural and deterministic validation checks pass;
- one baseline from every evolved control mode reruns to identical state and trajectory hashes;
- representative evaluation blocks from all major control families rerun exactly;
- all Phase 4 archive hashes match before and after Phase 5.

## 9. Restrictions still in force

Do not yet:

- create final publication figures;
- rewrite the title, abstract, Discussion, Conclusion, or response letter;
- claim semantic compression;
- claim broad model generality;
- alter D16–D25 without a new decision entry and versioned rerun;
- treat nested maps, disruption realizations, continuation seeds, cells, motifs, windows, or generations as independent replicates.

## 10. Next work

The next analytical work should implement the staged model-structure and parameter-sensitivity design required for generality. It should remain focused rather than full factorial and should use Phase 5 as a prerequisite.

The formal Gate 6 inheritance-scope and wording audit remains a later manuscript-stage requirement. The original operator must ultimately be described consistently as a fitness-weighted, Wright–Fisher-like compositional-resampling transition rather than literal physical fission.

## 11. Recommended next opening prompt

> Begin the next analytical phase of the JRSI major revision: focused model-structure and parameter robustness leading to the generality decision. Use the versioned Phase 5 package and treat `revision/REVISION_SPEC_v2.md`, approved entries in `revision/DECISIONS_LOG.md`, `revision/REVIEWER_MATRIX.md`, and `PHASE_05_HANDOFF.md` as controlling documents. Gates 1–5 have passed. Preserve D16–D25 and all archived Phase 4 and Phase 5 states. Do not alter the core estimator or causal-control design, create final figures, or rewrite the manuscript. Prespecify a staged, non-factorial sensitivity design before production, distinguish null, syntactic-only, viability-relevant, and strong-adaptation regions, and decide generality before result freeze.
