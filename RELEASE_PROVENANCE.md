# Release provenance

## Frozen scientific commit

`2c7d78694579755402c0a1896e109b29dec4d6a0` — *Freeze Phase 4-6 results and pass Gate 8*.

This commit fixes the scientific outputs and result-level claim boundary used by the revised manuscript.

## Gate 8 closure/tag

- internal tag: `phase7-gate8-passed-v1`
- closure commit: `36246a86320037506beed83d0f7366c33d2c59c5`

The closure commit adds phase documentation around the already frozen science.

## Public-release packaging layer

The public reproducibility release may add only documentation/packaging items such as:

- public README;
- license and citation metadata;
- environment lock files;
- publication-grade plotting scripts and frozen source tables;
- final figure exports;
- release manifest and archival DOI metadata;
- clean-room verification records.

These additions must not alter any frozen scientific result, estimator, intervention map, target rule, statistical method, or Phase 4–6 archive content.


## Release candidate RC2 packaging commit

`105b62e` and its immediate packaging-only predecessors add the safer public-release workflow, a Git-tracked archive builder, and transient-file exclusions. The RC2 tag is `jrsi-reproducibility-v1.0.0-rc2`. These changes are packaging/documentation only and do not alter the frozen scientific commit or Gate 8 results.

## Recommended final public tag

After the author inserts the DOI, archives Figures 1/2 masters/exports, and closes clean-room validation, create a final public tag such as:

`jrsi-reproducibility-v1.0.0`

The public release notes should state both the frozen scientific commit and the later packaging/tag commit.

## Release candidate RC3 packaging commit

RC3 records the author's MIT License selection and synchronizes the root `LICENSE`, `CITATION.cff`, `.zenodo.json`, README, checklist, release notes, and publication instructions. These are rights/metadata/package changes only. No frozen scientific result, estimator, intervention map, target rule, statistical method, figure-source table, or Phase 4–6 archive content is altered.
