# Publication handoff

Target repository: https://github.com/michcarr405/modelb_semantic_jrsi_repo
Preparation branch: round2-release-v2.0.0
Version: 2.0.0
Final tag: jrsi-reproducibility-v2.0.0

1. Preparation branch upload and clean-install validation are complete; see PUBLIC_VALIDATION_RECORD.md. Preserve v1 tags and repository history.
2. Final version strings and release date are set. RELEASE_MANIFEST_SHA256.txt covers the release files except itself; historical validation records remain unchanged.
3. Final tag and GitHub release are published at commit e6c0657af7cadf6f9b1d9e2508dee486772125e4. Final-tag CI and independent public-tag checks passed. The release ZIP was built from that tag.
4. Zenodo v2 is published as a linked new version: https://doi.org/10.5281/zenodo.23223636. Its version-family DOI is 10.5281/zenodo.21852679.
5. The verified v2 DOI is included in citation metadata in a subsequent commit; the archived tag is preserved. The separately maintained manuscript Data Accessibility statement should use the verified v2 DOI and GitHub release links.

All 14 standalone current figure PDFs are retained. The 12 data figures have a validated portable build; the two conceptual diagrams are archived asset copies. Manuscript and Supplement prose, TeX and complete document PDFs remain outside the repository. Prose-only edits do not require a computational release.
