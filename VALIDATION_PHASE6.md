# VALIDATION_PHASE6.md

## Scope

This record validates the Phase 6 focused robustness implementation, production structure, regime classification, Stage D confirmatory analysis, archive integrity, and Gate 7 decision.

## Automated tests

The existing Phase 2–5 tests and new Phase 6 tests were run in bounded groups because the execution shell has a short wall-clock limit. The aggregate result was:

- `66 passed`;
- `0 failed`;
- `0 skipped`.

The exact commands and per-group results are recorded in `TEST_RESULTS_PHASE6.txt`.

New Phase 6 tests verify:

- deterministic observation under fixed streams;
- unique constant and identity structural endpoints;
- reproducible corrected information under the dedicated permutation stream.

## Structural validator

Command:

```bash
PYTHONPATH=src python scripts/validate_phase6.py
```

Result:

- `24/24` checks passed.

The validator confirmed:

- 32 Stage A designs and 128 independent populations;
- 16 Stage B1 designs and 48 independent populations;
- 17 Stage B2 designs and 68 independent populations;
- 12 Stage C designs and 48 independent populations;
- exact identity recovery in all screen and protocol populations;
- four deterministically selected Stage D representatives, including the archived default;
- 24 nondefault Stage D independent populations;
- 1,680 Stage D continuation rows;
- exactly two nested continuations for every baseline/map block;
- exact identity information and viability recovery in all 24 nondefault confirmatory populations;
- explicit censoring fields and no imputation;
- exactly two nondefault representatives with VOI lower bounds above `0.25`;
- exact recomputation of Stage A and Stage B1 support fractions;
- exact recomputation of the four structural-family support indicators;
- an unambiguous broad-generality Gate 7 pass;
- all files in the archived Phase 4 and Phase 5 result manifests retain their original sizes and SHA-256 hashes.

Machine-readable validation records are in `validation/phase6/`.

## Inferential hierarchy

The independently evolved baseline population remains the inferential unit. Screening replicates, structural-control replicates, and Stage D populations were independently evolved. Intervention maps and continuation seeds are nested repeated measurements and never increase independent `n`.

Stage-level regime intervals use complete-population replicate blocks. Stage D uses one frontier per independently evolved population. No map-level or continuation-level row is treated as an independent biological/evolutionary replicate.

## Estimator and intervention preservation

Phase 6 did not change:

- the position-conditioned information target;
- within-segment permutation correction;
- direct retained information `I(g(M);Z|S)`;
- the strict one-percent target rule;
- explicit right-censoring semantics;
- the D16/D20 intervention-family logic;
- common-random-number actual/identity continuations;
- the archived Phase 4 or Phase 5 results.

Structural variants use the exact combinatorial analogue over their motif/state universe. Constant and identity endpoints are mandatory and were recovered exactly.

## Gate-decision validation

`results/phase6_generality/GATE_7_DECISION.json` evaluates each criterion separately. The broad decision follows mechanically from:

- Stage A positive fraction `0.71875`;
- Stage B1 positive fraction `0.375`;
- positive support in all four structural families;
- archived default confirmation;
- two nondefault Stage D confirmations;
- exact identity recovery;
- intact Phase 4 and Phase 5 archives.

The decision was not altered by plot inspection, and no final publication figure was generated.
