# Clean-room rerun record

**Status:** OPEN in release candidate.

The final public release requires a clean-room installation/execution record from the release contents.

Minimum closure procedure:

1. create a fresh environment from `requirements-lock.txt` or `environment-lock.yml`;
2. install the package from this repository;
3. run the frozen unit/integration test suite;
4. run `scripts/validate_result_freeze.py`;
5. run `scripts/verify_publication_figure_release.py`;
6. regenerate Figures 3–8 and S1–S7 from the frozen publication source tables;
7. record environment versions, commands, exit status, and generated-file hashes;
8. compare generated quantitative figure outputs/manifest to the archived publication exports, allowing only explicitly documented metadata-level nondeterminism if any.

No scientific retuning or replacement of frozen outputs is permitted during clean-room verification.

## Release-candidate attempt on 2026-08-08

A fresh local virtual environment was created and an install from `requirements-lock.txt` was attempted. The execution environment used for this packaging session had no package-index access, so pip could not retrieve even the pinned NumPy wheel and the isolated installation could not proceed. This was an infrastructure limitation rather than a package/test failure.

A GitHub Actions workflow is included at `.github/workflows/reproducibility.yml` specifically to perform the required fresh-environment installation, tests, result-freeze validation, and publication-figure regeneration after the final public tag is pushed.
