# Clean-room rerun record

**Status:** PRE-RELEASE VALIDATION PASSED (RC5). Final-tag validation remains to be run after the immutable `v1.0.0` tag is created.

## Successful external clean-room validation

A fresh GitHub-hosted Ubuntu 24.04 runner validated release candidate `jrsi-reproducibility-v1.0.0-rc5` on 2026-08-08 at commit:

`a1537a895e619173d3da24c54ff6efc0b56a9634`

The workflow completed successfully after the rendering environment was pinned and the publication font package (`fonts-croscore`, providing Arimo) was installed and recorded. The successful run completed all required steps:

1. checked out the tagged release candidate;
2. installed the publication font environment;
3. set up Python 3.13.5;
4. installed the locked dependencies;
5. recorded the clean-room environment;
6. ran the repository test suite;
7. validated the frozen result inventory;
8. verified the archived publication assets;
9. regenerated manuscript Figures 3–8 and Supplementary Figures S1–S7 from frozen source tables;
10. verified the regenerated quantitative PNG/TIFF outputs against the archived publication exports;
11. uploaded the clean-room validation records.

GitHub Actions workflow: **Reproducibility validation #2**

Artifact:

`jrsi-reproducibility-validation-jrsi-reproducibility-v1.0.0-rc5`

The prior RC4 workflow failure is retained in the repository history as provenance. It occurred only at byte-level quantitative-figure rendering verification because the external runner did not reproduce the archived publication font environment. RC5 corrected the runner/font environment without changing frozen scientific outputs, source tables, plotting logic, estimators, intervention maps, target rules, or statistical results.

## Final-tag closure

After the final annotated tag `jrsi-reproducibility-v1.0.0` is pushed, the same GitHub Actions workflow must pass on that tag. The final run should be retained on GitHub together with its validation artifact. No scientific retuning or replacement of frozen outputs is permitted.
