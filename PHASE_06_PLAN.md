# PHASE_06_PLAN.md

## Scope and immutable prerequisites

Phase 6 is the focused model-structure and parameter-robustness phase leading to Gate 7 (Generality). It begins from the checksum-verified Phase 5 release. Gates 1–5 and D16–D25 remain locked. Phase 4 and Phase 5 states and outputs are read-only. The validated conditional-information estimator, actual retained-information coordinate, independently evolved baseline as the inferential unit, two nested continuations, 36-generation primary horizon, strict one-percent target, explicit censoring, and D20 conservative pooled frontier are unchanged. No final figures or manuscript rewrite are permitted.

## Prespecified evidence quantities

Each independently evolved baseline population yields:

- bias-corrected position-conditioned information, `I_corr(M;Z|S)`;
- paired value of information, `VOI = V_actual - V_constant`, using common random numbers;
- sustained adaptive gain, final 20% minus initial 20% of the baseline mean-fitness trajectory.

Practical thresholds are fixed before production:

- `delta_I = 0.01` bit;
- `delta_V = 0.25` model-fitness unit;
- `delta_F = 1.0` model-fitness unit.

Point-level 95% bootstrap intervals define:

- **R0 null:** upper information interval `<= delta_I`;
- **R1 syntactic-only:** lower information interval `> delta_I`, upper VOI interval `<= delta_V`;
- **R2 viability-relevant:** lower information and VOI intervals exceed thresholds, but lower adaptive-gain interval `<= delta_F`;
- **R3 strong adaptation:** lower intervals exceed all three thresholds;
- all other points are **boundary/uncertain** and do not count as positive evidence.

## Staged non-factorial design

### Stage A — focused mechanistic map

Evaluate a 6-by-4 plane at the default positional ratio:

- `p = 0.40, 0.60, 0.75, 0.85, 0.925, 1.00`;
- `sigma_a/Theta = 0.00, 0.45, 0.90, 1.35`.

Add eight Latinized points split between `b/Theta = 0.50` and `2.50`; do not run the full three-factor cube. Use four independent baseline replicates per point.

### Stage B1 — global space-filling screen

Use a deterministic 16-point Latin-hypercube design with three independent replicates per point over parental coupling, affinity/noise, positional-bias/noise, temperature, mutation rate, population size, motif length, metabolite-state count, segment count, reward scale, penalty ratio, fitness floor, window stride, and count versus fraction-normalized fitness.

### Stage B2 — anchored structural controls

At the default strong setting, use one-change-at-a-time controls for:

- window density: stride 1, 2, 5, and 7;
- positional structure: 2 and 8 segments, reversed order, and non-heritable boundary jitter;
- metabolite-state count: 3 and 6 with matched topology density and effect scale;
- fitness formulation/scale: fraction-normalized fitness, low/high reward, low/high penalty ratio, and floor 0/1.

Use four independent replicates per setting. The default anchor is included once.

### Stage C — protocol sensitivity

At the default anchor and the deterministic nearest-boundary point, vary baseline duration over 100/150/250 generations and intervention horizon over 24/36/60 generations. Use four independent replicates per setting. The primary Gate decision remains tied to the D18 36-generation horizon.

### Stage D — full semantic confirmation

Select deterministically after screening:

1. the deepest observed R2 point;
2. the deepest observed R3 point;
3. the nearest boundary point;
4. the unchanged default anchor, using the archived Phase 4 result rather than rerunning it.

Ties are resolved by design ID. For each nondefault representative, run the full D20-analogue map panel with eight independently evolved populations, two nested continuations, the 36-generation horizon, strict one-percent target, and explicit censoring. Structural variants use the exact D16/D20 combinatorial analogue over their motif universe; the archived five-symbol core panel is unchanged.

## Gate 7 decision

**Broad generality** requires:

1. at least 20% of Stage A and 15% of Stage B1 points are definitively R2/R3;
2. R2/R3 persists in at least three of four structural families: window density, positional structure, metabolite-state count, and fitness formulation/scale;
3. the archived default plus at least two nondefault Stage D representatives have VOI lower 95% bounds above `delta_V` and exact identity recovery;
4. no archive-integrity, endpoint, estimator, or censoring failure.

**Narrow generality** applies if broad support fails but at least 5% of Stage B1 points are R2/R3, at least two structural families persist, and the default plus one nondefault Stage D representative confirm.

Otherwise Gate 7 fails and the central result remains a default-setting existence result. Design-domain fractions are not probabilities over possible prebiotic systems.
