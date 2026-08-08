# Author actions required before final public release

The scientific analysis is frozen. The items below are release/rights/publication actions only and do not require any scientific rerun or retuning.

## 1. Repository license — CLOSED

The author selected the MIT License on 2026-08-08. The standard MIT text is present as root `LICENSE`, `CITATION.cff` records the SPDX identifier `MIT`, `.zenodo.json` records the same license, the README has been updated, and `LICENSE_PENDING.md` has been removed. No further license-selection action is required for this release candidate.

## 2. Figures 1 and 2 source artwork — CLOSED

The author supplied final editable vector masters as `artwork/masters/Figure_1.svg` and `artwork/masters/Figure_2.svg` on 2026-08-08. PDF, EPS, and 600 dpi grayscale PNG/TIFF derivatives are archived in `artwork/exports/`. The vector exports were re-rendered and visually checked against the supplied masters and the controlling revised manuscript. `artwork/ARTWORK_VALIDATION.md` and `artwork/ARTWORK_MANIFEST_SHA256.csv` record the proof and checksums. No further Figure 1/2 artwork action is required unless the author later replaces these files with newer approved masters.

## 3. Publish the repository tree to GitHub — RELEASE-CANDIDATE BRANCH CLOSED

The RC4/RC5 repository tree is publicly browsable on GitHub. The original `main` branch has intentionally not yet been replaced. Final default/current branch activation remains a post-final-tag publication step.

## 4. Run the clean-room validation on GitHub Actions — PRE-RELEASE CLOSED

Release candidate `jrsi-reproducibility-v1.0.0-rc5` at commit `a1537a895e619173d3da24c54ff6efc0b56a9634` passed the external GitHub Actions clean-room validation on 2026-08-08, including test-suite execution, result-freeze validation, archived publication-asset verification, and exact quantitative-figure regeneration/verification. The clean-room record is closed for the release candidate. The same workflow must still pass on the final `v1.0.0` tag.

## 5. Reserve a permanent DOI before the final immutable archive — CLOSED

Zenodo DOI `10.5281/zenodo.21852680` has been reserved and inserted into the final release citation/documentation metadata. The Zenodo draft must not be deleted before publication because the reserved DOI belongs to that draft. Upload the final tagged archive to this draft and publish it only after the final-tag clean-room run passes.

## 6. Create final tag and archive

After the license and artwork closures, and after DOI metadata and the clean-room record are closed:

- version metadata is now prepared as `1.0.0`;
- create the final annotated tag `jrsi-reproducibility-v1.0.0`;
- run `scripts/build_public_release_archive.sh jrsi-reproducibility-v1.0.0`;
- verify the archive and regenerate the final SHA-256 manifest;
- publish the Zenodo record;
- update the manuscript/response letter with the final DOI and repository citation.

## 7. Gate 6 closure

Run the short integrated Gate 6 closure audit. No new scientific analysis is required.
