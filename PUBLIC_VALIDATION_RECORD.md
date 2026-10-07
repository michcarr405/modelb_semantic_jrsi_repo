# Public release preparation validation

Date: 2026-10-07
Tested commit: 968987512bb00556d7304d199e44bc3e8bf7a2b2
Branch: round2-release-v2.0.0
GitHub run: https://github.com/michcarr405/modelb_semantic_jrsi_repo/actions/runs/37677437249
Both jobs completed successfully.

- Numerical environment: Ubuntu 24.04, Python 3.13.5, portable pinned requirements.
- Foundation: 68 tests passed.
- Integrated evidence: current source-table and recorded scientific replay validation passed.
- Packaging: 14 checks passed.
- Figures: clean Python 3.12 plotting environment; 12 data figures rebuilt and pixel-identical at 144 dpi; 2 archived conceptual diagrams copied; report upload passed.

Before the workflow correction, the public RC7 commit 758798ae552309cc9b6752a0888f3001dfead2ef matched all 8,011 packaged files byte-for-byte. Its scientific checks passed, but figure-report upload failed because GitHub rejected a relative parent path. Commit 968987512bb00556d7304d199e44bc3e8bf7a2b2 corrected only the workflow paths and their manifest checksum. All 8,010 manifest entries then passed independent verification.

This record concerns release preparation. It does not claim the final v2 tag or Zenodo DOI has already been verified. The GitHub numerical job validates recorded full-replay outputs; it does not execute every production campaign anew. Full campaign routes and provenance limitations are recorded in ROUND2_RELEASE_SCOPE.md and round2_mp/validation/FULL_REGENERATION_STATUS.csv.
