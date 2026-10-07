# Author actions required before final Round-2 public release

The scientific analysis, manuscript/Supplement freeze, release-candidate assembly, hash verification, packaged validation, clean-room regeneration, and manuscript-repository consistency checks are closed.

## Closed before immutable release

- RC0 scientific freeze: PASS.
- RC1 Round-2 release tree assembly: PASS.
- RC2 SHA-256/provenance verification: PASS.
- RC3 packaged validation: PASS.
- RC4 external GitHub Actions clean-room validation: PASS.
- RC5 manuscript-repository consistency: PASS.
- MIT license: unchanged and valid.
- Round-2 release metadata prepared as version 2.0.0.
- Reserved DOI retained: 10.5281/zenodo.21852680.

## Remaining publication actions

1. Allow the post-metadata GitHub Actions validation to pass on the final candidate commit.
2. Lock RC6 and record the final candidate commit SHA.
3. Create immutable tag `jrsi-reproducibility-v2.0.0`.
4. Create a GitHub Release from that exact tag.
5. Upload/archive that exact tagged release to the existing Zenodo draft associated with reserved DOI `10.5281/zenodo.21852680`.
6. Publish the Zenodo record.
7. Independently verify that the DOI resolves publicly and that the archive content corresponds to the tagged GitHub release.
8. Only then replace the manuscript Data Accessibility placeholder with the verified repository release and DOI.
9. Run the final submission-package audit and response-letter closure.

Do not retune or regenerate scientific results during these publication steps. Any scientific change reopens the scientific freeze under a new version.
