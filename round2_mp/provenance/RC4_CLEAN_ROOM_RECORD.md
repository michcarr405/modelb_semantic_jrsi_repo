# RC4 clean-room reproduction record

Status: **PASS**

GitHub Actions run: **37608812728**
Validated commit: `d3811eab2ed3d7d8edc5fea8c75d8ad4bb2212e6`
Runner: Ubuntu 24.04
Python: 3.13.5

Clean-room sequence:
1. fresh GitHub-hosted checkout;
2. install only `requirements-lock.txt` plus editable package;
3. verify all Round-2 source hashes;
4. validate frozen Round-2 numerical records;
5. run complete repository tests;
6. validate historical result freeze;
7. compile Round-2 scripts;
8. regenerate MP publication figures from the released frozen source tables.

Results:
- exact source hashes: PASS, 23/23;
- Round-2 numerical record validation: PASS;
- test suite: 68/68 passed;
- historical freeze validation: 5/5 passed;
- representative MP figure regeneration: PASS.

GitHub Actions artifact:
- artifact ID: **11475782371**
- artifact archive SHA-256: `6f782c27ee19535a726edf4f5a2f8544788b4f909d54048b2799f2d1945f33ea`
- artifact contains clean-room records and regenerated PDFs.

Warnings were rendering-only (PostScript transparency and Matplotlib unfilled-marker warnings) and did not affect successful regeneration.
