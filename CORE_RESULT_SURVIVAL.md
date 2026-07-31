# Phase 4 corrected core result and Gate 4 survival test

**Project:** JRSI major revision, manuscript `rsif-2026-0516`  
**Date:** 2026-07-31  
**Phase:** 4 — corrected core production and core-result survival  
**Gate status:** **PASSED**

## 1. Scope and provenance

Phase 4 was run only from the repository contained in `JRSI_MAJOR_REVISION_PHASE3_GATE3_PASSED(1).zip`. Before code changes, the repository was verified to have:

- Phase 3 closure commit `c42fa82040e5d3b32105ef440c520dd6dd7c782d` as `HEAD`;
- validated Phase 3 implementation commit `add8a0750d9a2dc0e9d8ef5fbded6bab9175db42` in its Git history;
- all expected controlling and validation files.

No source was reconstructed from either older repository archive.

## 2. Frozen production settings

The prespecified pilots and approved decisions D16–D20 fixed:

- sequence family: all 14 contiguous-substring maps of lengths 1–4 at every valid position;
- primary map pool: balanced-random, affinity-rank, contiguous-substring, constant, and identity maps;
- unique primary map count: 34;
- continuation seeds per map: 2;
- intervention horizon: 36 generations;
- target tolerance: 0.01, corresponding to 99% recovery of the actual-minus-constant viability range;
- frontier: discrete monotone upper envelope without binning, smoothing, or interpolation;
- primary viability: mean future population fitness;
- affinity-profile k-means: excluded from Phase 4.

## 3. Production inventory

- 2 regimes: sequence-selective and sequence-agnostic;
- 10 transmission fidelities: 0.1–1.0;
- 20 independently evolved baseline populations per regime and fidelity;
- 400 independent baseline blocks total;
- 150 evolutionary generations per baseline;
- 200 within-segment permutations per baseline information estimate;
- 28,000 continuation-level rows;
- 2,000 complete-block bootstrap draws per fidelity;
- 9,999 replicate-level permutation draws where exact enumeration was unavailable;
- every evolved final state, state hash, observation, map assignment, map hash, continuation trajectory, final continuation hash, and seed ledger archived.

## 4. Prespecified Gate 4 result at fidelity 1.0

All 400 production blocks recovered the identity endpoint exactly in both retained information and paired continuation viability. Full 36-generation actual and identity trajectories and final populations also matched exactly.

At the prespecified primary fidelity `p = 1.0`:

| Quantity | Sequence-selective result | Sequence-agnostic result | Replicate-level contrast |
|---|---:|---:|---:|
| Corrected conditional information | mean 0.25319 bits | mean -0.00023 bits | difference 0.25342 bits, permutation `p = 0.0001` |
| Value of information | mean 11.90719, 95% block-bootstrap CI [11.33189, 12.43681] | exactly 0 | difference 11.90719, permutation `p = 0.0001` |
| Semantic information | median 0.28296 bits, 95% block-bootstrap CI [0.27587, 0.29287] | median 0 bits | mean difference 0.28363 bits, permutation `p = 0.0001` |
| Target reached | 20/20 | 20/20 | no censoring |

The corrected selective-versus-agnostic core therefore satisfies every prespecified Gate 4 criterion.

## 5. Full fidelity sweep

|   p |   Icorr selective |   Icorr agnostic |   VOI selective |   VOI agnostic |   S median selective |   S median agnostic | reach selective   |
|----:|------------------:|-----------------:|----------------:|---------------:|---------------------:|--------------------:|:------------------|
| 0.1 |            0.2165 |           0.0001 |           5.718 |              0 |               0.5036 |                   0 | 20/20             |
| 0.2 |            0.2167 |          -0.0002 |           5.735 |              0 |               0.5044 |                   0 | 20/20             |
| 0.3 |            0.2139 |           0.0003 |           5.732 |              0 |               0.5019 |                   0 | 20/20             |
| 0.4 |            0.2149 |           0.0011 |           5.749 |              0 |               0.5016 |                   0 | 20/20             |
| 0.5 |            0.2174 |          -0.0011 |           5.76  |              0 |               0.5044 |                   0 | 20/20             |
| 0.6 |            0.2167 |           0      |           5.762 |              0 |               0.4989 |                   0 | 20/20             |
| 0.7 |            0.2168 |          -0      |           5.816 |              0 |               0.4966 |                   0 | 20/20             |
| 0.8 |            0.2177 |          -0.0004 |           5.939 |              0 |               0.4862 |                   0 | 20/20             |
| 0.9 |            0.222  |           0.0001 |           6.484 |              0 |               0.4529 |                   0 | 20/20             |
| 1   |            0.2532 |          -0.0002 |          11.907 |              0 |               0.283  |                   0 | 20/20             |

## 6. What survived—and what did not

### Survived

1. **Positional conditioning removed the agnostic signal.** Corrected `I(M;Z|S)` remained near zero in the sequence-agnostic regime across the full sweep, while the sequence-selective regime remained reproducibly positive.
2. **The sequence-selective channel had a large intervention effect.** Coarse-graining to the constant endpoint reduced future mean fitness, whereas all sequence-agnostic affinity matrices were identical under every grouping and therefore had zero value of information.
3. **Replicate-level inference was decisive.** The primary contrasts used 20 independently evolved populations per regime, not intervention points or continuation seeds.
4. **Endpoint and censoring requirements were satisfied.** All identity endpoints recovered exactly and all targets were reached, so no censored point estimates were silently imputed.

### Important narrowing

For every one of the 200 sequence-selective production blocks, the first map reaching the strict 99% viability target was the full identity endpoint. Consequently, the semantic estimate equaled the full observed conditional information for every selective replicate. None of the tested intermediate coarse-grainings recovered 99% of the actual-minus-constant viability range.

Thus Gate 4 supports a **sequence-specific, viability-relevant information effect**, but it does **not** demonstrate semantic compression under the present strict target and map panel. The corrected result is stronger statistically yet narrower conceptually than the submitted pooled frontier claim.

A second limitation remains intentionally unresolved at Gate 4: positive value of information occurred throughout the selective sweep, including low transmission fidelity. This can arise from the model's built-in affinity-to-fitness causal architecture and cannot yet be interpreted as selection-dependent mapping specificity. That question is reserved for Phase 5 causal controls.

## 7. Gate decision

**Gate 4 PASSED.** The corrected selective-versus-agnostic result survives positional conditioning, permutation correction, actual retained information, independent evolved replicates, identity endpoints, explicit censoring rules, block bootstrap, and replicate-level permutation inference.

The supported Phase 4 conclusion is limited to:

> Within Model B, sequence-dependent motif–local-state information is reproducibly positive and viability-relevant under the specified coarse-graining interventions, whereas the sequence-agnostic channel is removed by positional conditioning and has zero intervention value.

Claims that this effect is selection-dependent, mapping-specific, broadly general, chemically realistic, or semantically compressed remain blocked until later gates.

## 8. Prohibited work respected

Phase 4 did not run causal disruption controls, broad parameter sweeps, final publication figures, or manuscript rewriting.
