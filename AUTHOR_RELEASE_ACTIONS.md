# Author actions required before final public release

The scientific analysis is frozen. The items below are release/rights/publication actions only and do not require any scientific rerun or retuning.

## 1. Repository license — CLOSED

The author selected the MIT License on 2026-08-08. The standard MIT text is present as root `LICENSE`, `CITATION.cff` records the SPDX identifier `MIT`, `.zenodo.json` records the same license, the README has been updated, and `LICENSE_PENDING.md` has been removed. No further license-selection action is required for this release candidate.

## 2. Figures 1 and 2 source artwork — CLOSED

The author supplied final editable vector masters as `artwork/masters/Figure_1.svg` and `artwork/masters/Figure_2.svg` on 2026-08-08. PDF, EPS, and 600 dpi grayscale PNG/TIFF derivatives are archived in `artwork/exports/`. The vector exports were re-rendered and visually checked against the supplied masters and the controlling revised manuscript. `artwork/ARTWORK_VALIDATION.md` and `artwork/ARTWORK_MANIFEST_SHA256.csv` record the proof and checksums. No further Figure 1/2 artwork action is required unless the author later replaces these files with newer approved masters.

## 3. Publish the repository tree to GitHub

The public GitHub repository should expose the actual repository tree instead of only a nested ZIP. Preserve the frozen scientific Git history and the Gate 8 commits/tags.

## 4. Run the clean-room validation on GitHub Actions

Push a release-candidate tag first. The included workflow installs from the lock file on a fresh runner, runs the tests, validates the result freeze, verifies publication assets, and regenerates Figures 3–8 and S1–S7.

Record the successful run identifier in `reproduction/CLEAN_ROOM_RERUN_RECORD.md`.

## 5. Reserve a permanent DOI before the final immutable archive

Recommended workflow: create a Zenodo draft and reserve its DOI before the final tag/archive. Insert the reserved DOI into `CITATION.cff`, README, release notes, and the manuscript Data Accessibility text before creating the final v1.0.0 tag. Upload the final tagged archive to the Zenodo draft and publish it only after the final clean-room run passes.

This ordering avoids publishing an immutable archive that lacks its own DOI in the bundled citation metadata.

## 6. Create final tag and archive

After the license and artwork closures, and after DOI metadata and the clean-room record are closed:

- update version metadata from `1.0.0-rc5` to `1.0.0`;
- create the final annotated tag `jrsi-reproducibility-v1.0.0`;
- run `scripts/build_public_release_archive.sh jrsi-reproducibility-v1.0.0`;
- verify the archive and regenerate the final SHA-256 manifest;
- publish the Zenodo record;
- update the manuscript/response letter with the final DOI and repository citation.

## 7. Gate 6 closure

Run the short integrated Gate 6 closure audit. No new scientific analysis is required.
