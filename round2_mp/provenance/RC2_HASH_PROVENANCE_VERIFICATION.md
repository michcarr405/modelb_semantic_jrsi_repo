# RC2 hash and provenance verification

Status: **PASS**

Validated on GitHub Actions run **37608812728** at commit `d3811eab2ed3d7d8edc5fea8c75d8ad4bb2212e6`.

- all 23 Round-2 MP source/script files matched the SHA-256 values from the frozen MP migration manifest;
- the files comprise 19 frozen source tables and 4 exact MP migration/diagnostic scripts;
- no source-hash mismatch was detected;
- the historical Gate-8 repository remained intact and separately validated.

The authoritative expected hashes are in `RC1_SOURCE_SHA256.txt`.
