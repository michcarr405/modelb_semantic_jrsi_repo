# RC2 hash and provenance verification

Status: **PASS**

The Round-2 release carries two frozen-source hash sets.

## MP migration evidence

`RC1_SOURCE_SHA256.txt` verifies:
- 19 frozen MP-primary source tables;
- 4 exact MP migration/diagnostic scripts.

All 23 matched the SHA-256 values from the frozen MP migration manifest.

## Final Supplement evidence

`RC5_SUPPLEMENT_EVIDENCE_SHA256.txt` verifies seven additional exact final-Supplement evidence artifacts:
- final Supplement source-record map;
- empirical marginal-preservation prespecification;
- empirical marginal reader diagnostic table;
- empirical marginal frozen summary;
- Table S2 compact reader record;
- Table S2 full reader record;
- exact original empirical marginal validation script.

These hashes were taken from the controlling final-Supplement evidence package and are checked in the clean-room workflow.

The repository-native empirical reproduction script is new release packaging code and is validated by execution rather than represented as a frozen pre-existing source artifact.
