# PHASE_04_HANDOFF.md

## Project

**Manuscript:** `rsif-2026-0516`  
**Project:** JRSI Major Revision — Semantic Information in Model B  
**Date:** 2026-07-31  
**Completed phase:** Phase 4 — corrected core production and core-result survival  
**Gate status:** **Gate 4 PASSED**

## 1. Handoff purpose

This file closes Phase 4 and defines the permitted opening state for Phase 5. Gates 1–3 were inherited from the authoritative Phase 3 package. Phase 4 froze P01–P05 before production, generated the corrected core dataset, validated deterministic reruns, and applied the prespecified Gate 4 survival test.

No causal disruption controls, broad parameter sweeps, final publication figures, or manuscript rewriting were performed.

## 2. Source provenance

The sole Phase 4 starting repository was the repository embedded in `JRSI_MAJOR_REVISION_PHASE3_GATE3_PASSED(1).zip`.

Verified before modification:

- Phase 3 closure commit: `c42fa82040e5d3b32105ef440c520dd6dd7c782d`;
- Phase 3 validated scientific implementation commit: `add8a0750d9a2dc0e9d8ef5fbded6bab9175db42`;
- expected Phase 3 controlling documents, source, tests, validation records, and Git history.

The older `modelb_semantic_jrsi_repo.zip` and `03_SUBMITTED_CODE_REPOSITORY.zip` were not used.

## 3. Frozen pre-production decisions

Approved entries D16–D20 in `revision/DECISIONS_LOG.md` resolve P01–P05:

- **P01:** 14 unique contiguous-substring maps spanning every leading, trailing, and internal position at lengths 1–4;
- **P02:** two nested paired continuation seeds per map;
- **P03:** 36-generation intervention horizon;
- **P04:** strict 1% target tolerance with no interpolation;
- **P05:** one pooled primary frontier per baseline from unique balanced-random, affinity-rank, contiguous-substring, constant, and identity maps; k-means excluded.

## 4. Production dataset

The corrected core run contains:

- 2 regimes;
- 10 transmission fidelities;
- 20 independently evolved baseline populations per regime and fidelity;
- 400 independent baseline blocks;
- 34 unique intervention maps plus the actual trajectory;
- 2 continuations per map;
- 28,000 continuation rows;
- 200 within-segment information permutations per baseline;
- 2,000 complete-block bootstrap draws per fidelity;
- replicate-level permutation inference.

Archived materials include every evolved state and hash, baseline information observation, map assignment and hash, complete continuation trajectory, final continuation hash, and seed ledger.

## 5. Gate 4 result

At the prespecified primary fidelity `p = 1.0`:

- corrected conditional information difference, selective minus agnostic: `0.253418` bits, permutation `p = 0.0001`;
- value-of-information difference: `11.907186` model-fitness units, permutation `p = 0.0001`;
- semantic-information difference: `0.283632` bits, permutation `p = 0.0001`;
- target reached: 20/20 in each regime;
- identity information and viability recovery: 400/400 production blocks.

**Gate 4 PASSED.** Full evidence is in `CORE_RESULT_SURVIVAL.md`.

## 6. Critical interpretation carried forward

The corrected selective-versus-agnostic result survives, but the interpretation must remain narrow.

For all 200 sequence-selective baseline blocks, the strict 99% target was first reached only at the full identity endpoint. The semantic estimate therefore equaled the full observed conditional information. The tested intermediate coarse-grainings did not demonstrate semantic compression.

Positive value of information also occurred at low transmission fidelity. This is compatible with the built-in affinity-to-fitness causal architecture and is not yet evidence of selection-dependent mapping specificity. Phase 5 must decide whether evolution adds a native, selection-dependent component beyond that architectural effect.

## 7. Phase 4 validation

- 57 tests pass;
- all output counts and hashes validate;
- every actual–identity 36-generation trajectory and final population matches exactly;
- a clean baseline rerun and complete intervention-block rerun reproduce archived production results;
- no censored production estimates were imputed.

See `VALIDATION_PHASE4.md` and `validation/phase4/`.

## 8. Restrictions still in force

Do not yet:

- rewrite the manuscript, abstract, title, Discussion, or Conclusion;
- create final publication figures;
- claim selection-dependent or mapping-specific semantics;
- claim semantic compression;
- run broad parameter or structural sweeps;
- alter D16–D20 from causal-control outcomes without opening a new versioned analysis;
- treat maps, continuation seeds, protocells, motifs, windows, or generations as independent replicates.

## 9. Next permitted phase

**Phase 5 — causal specificity and Gate 5**

Phase 5 should use the archived Phase 4 states and fixed core estimator to test the focused controls required by D10 and reviewer item R1.2:

1. neutral and reduced selection;
2. complete affinity-profile reassignment;
3. post-evolution fitness-map mismatch;
4. alternative stable fitness topologies;
5. temporally unstable topology null.

The primary question is whether a selection-dependent, mapping-specific semantic excess remains after the built-in architectural channel is separated from evolved enrichment.

## 10. Recommended Phase 5 opening prompt

> Begin Phase 5 of the JRSI major revision: causal specificity and Gate 5. Use the versioned Phase 4 package and treat `revision/REVISION_SPEC_v2.md`, approved entries in `revision/DECISIONS_LOG.md`, `revision/REVIEWER_MATRIX.md`, and `PHASE_04_HANDOFF.md` as controlling documents. Gates 1–4 have passed. Preserve D16–D20 and the archived Phase 4 core states. Do not rerun or retune the corrected core analysis. Implement the prespecified focused controls for neutral/reduced selection, complete affinity-profile reassignment, fitness-map mismatch, alternative stable topologies, and a temporally unstable topology null. Use independently evolved baseline populations as the inferential unit, retain explicit censoring, and decide Gate 5 before any broad sensitivity sweep, final figure, or manuscript rewrite.
