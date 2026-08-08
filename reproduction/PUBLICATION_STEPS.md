# Steps to finalize the release publicly

The public GitHub repository currently exposes only a nested ZIP. The final release should expose this repository tree directly so README, code, tests, source tables, and validation records are browsable.

## 1. Resolve local release blockers

Before the final tag:

- select and add the root `LICENSE`;
- update `CITATION.cff` and `.zenodo.json` with the selected license if desired;
- archive or permanently reference the authoritative editable masters for Figures 1 and 2;
- add final standalone journal-upload exports for Figures 1 and 2 to `artwork/`;
- remove `LICENSE_PENDING.md`;
- update `CITATION.cff` from release candidate version `1.0.0-rc1` to `1.0.0`.

## 2. Publish the browsable GitHub repository

Recommended command-line workflow from a local clone of the public repository:

```bash
# Back up the existing public repository first.
git remote -v

# Copy the release-candidate repository contents into the working tree,
# preserving the scientific Git history rather than keeping a nested ZIP only.
git status

git add -A
git commit -m "Package frozen JRSI reproducibility release"
```

Record the resulting public packaging commit in `RELEASE_PROVENANCE.md` and the release notes.

## 3. Create the final tag

```bash
git tag -a jrsi-reproducibility-v1.0.0 -m "JRSI frozen reproducibility release v1.0.0"
git push origin main
git push origin jrsi-reproducibility-v1.0.0
```

The tag push triggers `.github/workflows/reproducibility.yml` on a fresh GitHub-hosted runner. Do not create the archival DOI release until the clean-room workflow passes.

## 4. Close the clean-room record

After the GitHub Actions workflow passes:

- save the workflow URL/run identifier;
- download the validation artifact;
- copy the environment, test, result-freeze, and publication-figure validation records into the final release archive if desired;
- update `CLEAN_ROOM_RERUN_RECORD.md` from OPEN to PASSED with the run identifier and date.

If the workflow reveals any scientific reproducibility defect, do not silently repair the release; reopen change control as required.

## 5. Mint the permanent DOI

A practical route is to connect the public GitHub repository to Zenodo, then create a GitHub release from the final tag. Zenodo can archive the tagged release and mint a DOI. Alternatively, upload the final release archive directly to the chosen permanent research archive.

After the DOI is minted:

- add the DOI to `CITATION.cff`;
- add it to the root README;
- add it to the final GitHub release notes;
- add it to the manuscript Data Accessibility statement;
- add it to the response-to-reviewers reproducibility response;
- regenerate the final release manifest if any archived files changed.

## 6. Final Gate 6 closure

Once the public repository is browsable, the clean-room run has passed, the DOI exists, the license is present, and Figures 1/2 masters/exports are archived or permanently referenced, rerun the short Gate 6 closure audit. No new scientific analysis is required.
