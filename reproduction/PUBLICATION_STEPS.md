# Steps to finalize the release publicly

The public GitHub repository currently exposes only a nested ZIP. The final release should expose this repository tree directly so README, code, tests, source tables, and validation records are browsable.

## 1. Resolve local release blockers

Before the final tag:

- select and add the root `LICENSE`;
- update `CITATION.cff` **and `.zenodo.json`** with the selected license;
- archive or permanently reference the authoritative editable masters for Figures 1 and 2;
- add final standalone journal-upload exports for Figures 1 and 2 to `artwork/`;
- remove `LICENSE_PENDING.md`;
- complete a release-candidate clean-room validation run.

Note: when both `.zenodo.json` and `CITATION.cff` are present, Zenodo's GitHub integration uses `.zenodo.json` for the Zenodo record metadata. Keep both files consistent.

## 2. Publish the browsable GitHub repository safely

The existing public GitHub repository has a separate one-commit history containing only the old nested ZIP. Do **not** overwrite `main` first. Publish the frozen repository history to a new branch, inspect it, and only then make it the default/current branch.

Recommended workflow using the supplied Git bundle:

```bash
# Keep a separate backup clone of the current public repository.
git clone https://github.com/michcarr405/modelb_semantic_jrsi_repo.git public-repo-backup

# Clone the supplied frozen-history bundle.
git clone modelb_semantic_jrsi_reproducibility_release_rc2.bundle jrsi-release
cd jrsi-release

# Add the existing GitHub repository as the publication remote.
git remote rename origin bundle-origin
git remote add origin https://github.com/michcarr405/modelb_semantic_jrsi_repo.git

# Publish to a new branch first; this is non-destructive.
git push -u origin public-reproducibility-release-candidate-v2:jrsi-reproducibility-release
```

Then inspect the new branch on GitHub. Once verified, use GitHub repository settings to make `jrsi-reproducibility-release` the default branch (or rename it to `main` through the normal branch-management workflow). Keep the original one-commit branch as a historical submitted-code snapshot until final release verification is complete. Avoid a force-push unless there is an explicit backup and a deliberate decision to replace the old branch history.

Record the public branch/commit in `RELEASE_PROVENANCE.md` and the release notes.

## 3. Run clean-room validation on an RC tag

Create a release-candidate tag before the final DOI-bearing tag:

```bash
git tag -a jrsi-reproducibility-v1.0.0-rc2 -m "JRSI reproducibility release candidate rc2"
git push origin jrsi-reproducibility-v1.0.0-rc2
```

The tag push triggers `.github/workflows/reproducibility.yml` on a fresh GitHub-hosted runner. After the workflow passes:

- save the workflow URL/run identifier;
- download the validation artifact;
- update `reproduction/CLEAN_ROOM_RERUN_RECORD.md` from OPEN to PASSED with the run identifier and date.

If the workflow reveals a scientific reproducibility defect, do not silently repair the release; reopen change control as required.

## 4. Reserve the permanent DOI before the final immutable archive

Recommended workflow: create a **Zenodo draft** and reserve its DOI before publishing the final software record. Insert the reserved DOI into:

- `CITATION.cff`;
- root `README.md`;
- `RELEASE_NOTES_DRAFT.md` (renamed/finalized as appropriate);
- the manuscript Data Accessibility statement;
- the response-to-reviewers reproducibility response.

Then update version metadata from `1.0.0-rc1` to `1.0.0` and commit these packaging-only changes.

This ordering allows the DOI to be embedded in the exact final archived files before the Zenodo record becomes immutable.

## 5. Create the final tag and validate it

```bash
git tag -a jrsi-reproducibility-v1.0.0 -m "JRSI frozen reproducibility release v1.0.0"
git push origin main
git push origin jrsi-reproducibility-v1.0.0
```

Confirm that the clean-room GitHub Actions workflow also passes on the final tag. Record that final run in the release documentation.

## 6. Build the archival ZIP from Git-tracked content

Use the included builder rather than zipping the working directory. It excludes `.git`, `.pytest_cache`, `.DS_Store`, notebook checkpoints, and other untracked local artifacts.

```bash
bash scripts/build_public_release_archive.sh jrsi-reproducibility-v1.0.0
```

Upload the resulting ZIP to the reserved Zenodo draft (or use another permanent research archive), verify the metadata/license, and then publish the record.

## 7. Final metadata and Gate 6 closure

After the DOI resolves publicly:

- confirm the DOI in `CITATION.cff`, README, release notes, manuscript Data Accessibility statement, and reviewer response;
- generate the final release manifest/checksums;
- verify the final standalone Figure 1/2 exports;
- run the short Gate 6 closure audit.

No new scientific analysis is required.
