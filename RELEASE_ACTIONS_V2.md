# Publication handoff

Target repository: https://github.com/michcarr405/modelb_semantic_jrsi_repo
Preparation branch: round2-release-v2.0.0
Candidate: 2.0.0rc7
Intended final tag after release acceptance: jrsi-reproducibility-v2.0.0

1. Push the preparation branch and review the code-and-data release. Do not force-push or alter v1 tags.
2. Finalize version strings to 2.0.0, update the release date, and regenerate RELEASE_MANIFEST_SHA256.txt after any metadata change. Preserve historical RC3/RC4 validation records.
3. Create the final tag and GitHub release on the reviewed commit; use RELEASE_NOTES_V2.md and attach the verified release archive.
4. Run the release CI and independently clone the exact public tag; install the portable locked requirements, run tests and the integrated and packaging validators. Record the tag commit and output.
5. Archive the v2 release as a new version of the existing Zenodo record if that record is owned by the author; verify the actual record/version DOI. Do not reuse the v1 version DOI as the v2 DOI. If GitHub-Zenodo integration is enabled, check its result before uploading a duplicate record.
6. Insert the actual v2 DOI and final metadata in citation records, keeping archive/commit provenance explicit. Update the separately maintained manuscript Data Accessibility statement with verified public links.

No manuscript or Supplement prose/TeX/PDF files are included. Prose edits do not require a computational release.

RC7 restores all 14 current standalone figure PDFs and historical document-validation records omitted by RC4. Final-layout figure regeneration remains unvalidated; archived assets are hash-verified.

RC7 adds a validated portable final-figure build in a separate plotting environment. All 12 data figures reproduce exactly at 144 dpi; the two conceptual diagrams are archived copies. Earlier statements about an unvalidated final-layout build describe RC6 and are superseded by FIGURE_BUILD_VALIDATION.json.
