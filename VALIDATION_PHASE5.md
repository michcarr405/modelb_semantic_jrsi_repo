# VALIDATION_PHASE5.md

## Scope

This record validates the Phase 5 causal-specificity implementation, production outputs, inferential hierarchy, and Gate 5 decision.

## Automated tests

Command:

```bash
PYTHONPATH=src pytest -q
```

Result:

- `63 passed`;
- no failures or skipped tests;
- recorded in `TEST_RESULTS_PHASE5.txt`.

New Phase 5 tests verify:

- exact neutral and full-selection endpoints of the selection-mixture law;
- equivalence of `alpha=1.0` propagation to the Phase 4 propagation law;
- equivalence of the cached Phase 5 observer to the audited Phase 4 observer for identical random streams;
- complete enumeration of the 30 matched topologies;
- fixed topology category counts, symmetry, and exclusivity;
- deterministic maximum-distance selection of alternatives A and B;
- complete affinity derangements with zero fixed points;
- reproducible unstable schedules with no immediate repeats.

## Production-structure validation

Command:

```bash
PYTHONPATH=src python scripts/validate_phase5.py
```

Result:

- `19/19` structural and deterministic checks passed.

The validator confirmed:

- all files listed in the Phase 4 archive manifest retain their original size and SHA-256 hash;
- 100 control baselines are archived;
- 220 evaluation specifications and 220 replicate-specific control frontiers are present;
- 15,400 continuation rows are present;
- every baseline/map block contains exactly two nested continuation rows;
- all 220 identity endpoints recover information and viability exactly;
- all six Gate 5 contrasts pass;
- the matched topology universe contains 30 unique hashes;
- alternatives A and B are distinct and nonnative;
- 40 complete affinity derangements are valid permutations with zero fixed points;
- every seed block has two nonnative topology mismatches;
- 60 unstable-topology schedules contain valid topology IDs and no immediate repeat;
- deterministic reruns of one baseline from each of the five evolved control modes reproduce both state and trajectory hashes;
- deterministic reruns of representative selection, affinity-reassignment, topology-mismatch, alternative-topology, and unstable-topology evaluation blocks reproduce their archived continuation tables exactly.

Machine-readable records are in `validation/phase5/`:

- `validation_summary.json`;
- `structural_checks.csv`;
- `representative_baseline_reruns.csv`;
- `representative_evaluation_reruns.csv`.

## Inferential validation

The Gate 5 table contains exactly one difference per matched evolutionary seed block. The following are nested and never enter the inferential sample size:

- disruption realization;
- grouping map;
- continuation seed;
- cell;
- oligomer;
- motif window;
- generation.

Each of the six contrasts uses 20 paired seed-block differences. Two-sided paired randomization p-values were generated from 9,999 sign randomizations because `2^20` exceeds the prespecified exact-enumeration limit. Paired-block bootstrap intervals use 2,000 resamples. Benjamini–Hochberg correction is applied once across the six prespecified contrasts.

## Censoring and endpoints

Target status is retained for every control realization. All 220 targets were reached, so no right-censored estimate occurred in this dataset. The pipeline nonetheless preserves the censoring fields and does not contain an imputation path.

Identity information and viability recovery pass for 220/220 control-realization blocks. Actual and identity continuations receive common random numbers and are exactly identical when their model inputs are identical.

## Archive integrity

`results/phase5_causal_specificity/phase4_archive_integrity_before.csv` and `phase4_archive_integrity_after.csv` independently verify the Phase 4 manifest. No Phase 4 state, continuation result, statistical output, map assignment, or seed ledger was modified.

## Validation conclusion

The Phase 5 implementation and outputs satisfy the prespecified causal-control design. The Gate 5 decision is reproducible from archived seed-block results, and no evidence of pseudoreplication, endpoint failure, hidden censoring imputation, or Phase 4 archive mutation was found.
