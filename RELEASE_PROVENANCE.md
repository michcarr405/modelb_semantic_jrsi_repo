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

## Permanent archive DOI

Zenodo DOI `10.5281/zenodo.21852680` was reserved on 2026-08-08 before final archive publication so that the DOI could be embedded in the release metadata and files. The DOI becomes publicly registered/resolvable when the Zenodo record is published.

## Final public tag

The final public tag is to be:

`jrsi-reproducibility-v1.0.0`

The public release notes state both the frozen scientific commit and the later packaging/tag commit.

## Release candidate RC3 packaging commit

RC3 records the author's MIT License selection and synchronizes the root `LICENSE`, `CITATION.cff`, `.zenodo.json`, README, checklist, release notes, and publication instructions. These are rights/metadata/package changes only. No frozen scientific result, estimator, intervention map, target rule, statistical method, figure-source table, or Phase 4–6 archive content is altered.

## Release candidate RC4 artwork closure

RC4 archives the author-supplied final editable SVG masters for Figures 1 and 2, adds PDF/EPS and 600 dpi grayscale PNG/TIFF derivative exports, records an artwork-specific SHA-256 manifest, and adds a final scientific-content/export validation record. It also advances release-candidate metadata from `1.0.0-rc3` to `1.0.0-rc4`. These are artwork-preservation, documentation, and packaging changes only. No frozen scientific result, estimator, intervention map, target rule, statistical method, quantitative figure-source table, or Phase 4–6 archive content is altered.

## Release candidate RC5 clean-room rendering closure

The first RC4 GitHub Actions clean-room run reached quantitative-figure regeneration after the repository test suite, result-freeze validation, and archived publication-asset verification had passed. The run then failed because regenerated PNG/TIFF files differed byte-for-byte from the archived publication exports. The publication scripts prefer Arimo, and the archived vector outputs record Arimo as the resolved text face. RC5 therefore pins the runner to Ubuntu 24.04, installs Ubuntu's `fonts-croscore` package before rendering, records the resolved font/package environment, and uploads clean-room diagnostic records even if a later step fails. This is a reproducibility-workflow correction only; no frozen scientific output, source table, plotting logic, estimator, intervention map, target rule, or statistical result is changed.

## RC5 external clean-room validation

Release candidate `jrsi-reproducibility-v1.0.0-rc5` at commit `a1537a895e619173d3da24c54ff6efc0b56a9634` passed the GitHub Actions clean-room validation on 2026-08-08. The successful run installed the locked Python dependencies and publication font environment on Ubuntu 24.04, ran the full test suite, validated the result freeze, verified archived publication assets, regenerated Figures 3–8 and S1–S7 from frozen source tables, and verified exact publication-output hashes. The uploaded validation artifact is `jrsi-reproducibility-validation-jrsi-reproducibility-v1.0.0-rc5`.
