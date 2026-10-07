# Publication handoff

Target repository: https://github.com/michcarr405/modelb_semantic_jrsi_repo
Preparation branch: round2-release-v2.0.0
Version: 2.0.0
Final tag: jrsi-reproducibility-v2.0.0

1. Preparation branch upload and clean-install validation are complete; see PUBLIC_VALIDATION_RECORD.md. Preserve v1 tags and repository history.
2. Final version strings and release date are set. RELEASE_MANIFEST_SHA256.txt covers the release files except itself; historical validation records remain unchanged.
3. Create the final tag on the reviewed preparation commit. Verify its GitHub workflow and independently fetch the exact public tag before publishing the GitHub release. Use RELEASE_NOTES_V2.md and an archive built from the final tag, rather than the older RC7 ZIP.
4. Archive v2 as a new version of the existing author-owned Zenodo record. If GitHub-Zenodo integration is enabled, check its result before making a duplicate upload. Verify the actual version DOI; do not reuse the v1 version DOI as v2.
5. Add the verified DOI to citation records in a subsequent metadata commit without moving the archived tag. Maintain explicit archive/commit provenance. Update the separately maintained manuscript Data Accessibility statement with verified public links.

All 14 standalone current figure PDFs are retained. The 12 data figures have a validated portable build; the two conceptual diagrams are archived asset copies. Manuscript and Supplement prose, TeX and complete document PDFs remain outside the repository. Prose-only edits do not require a computational release.
