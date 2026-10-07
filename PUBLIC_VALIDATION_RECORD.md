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

## Final public tag and archive verification

Final tag: jrsi-reproducibility-v2.0.0
Tag commit: e6c0657af7cadf6f9b1d9e2508dee486772125e4
Final-tag GitHub run: https://github.com/michcarr405/modelb_semantic_jrsi_repo/actions/runs/37678229103
Both jobs passed, including figure report upload. An independent fresh public-tag clone and Python 3.12 installation passed 68 tests, 29 integrated checks, and 14 packaging checks. All 8,011 manifest entries were independently verified.

GitHub release: https://github.com/michcarr405/modelb_semantic_jrsi_repo/releases/tag/jrsi-reproducibility-v2.0.0
Zenodo version DOI: https://doi.org/10.5281/zenodo.23223636
Zenodo record: https://zenodo.org/records/23223636
Version-family DOI: https://doi.org/10.5281/zenodo.21852679
The public Zenodo metadata links this record to the same version family as v1.

Archive filename: JRSI_R2_REPRODUCIBILITY_v2.0.0.zip
Archive size: 74409593 bytes
SHA256: 341ed6a56d4efd3ad9ff5c5b87dfd73197b194a8d1717693683b42346cdae24f
The published GitHub ZIP contains 8,012 repository files and matches the tagged file bytes. The public Zenodo ZIP was independently downloaded without authentication: its SHA256 matches the GitHub release ZIP exactly. All 8,011 manifest entries and all 14 figure PDFs were verified.

This DOI/citation metadata is a subsequent commit. The final release tag and its published ZIP are preserved unchanged.
