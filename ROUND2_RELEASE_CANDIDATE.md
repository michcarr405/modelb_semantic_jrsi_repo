# Round-2 release candidate

Candidate branch: `round2-release-candidate-v2.0.0`

Historical base repository commit: `dadee39c832751fe0be21bdcf26343a3039d757c`

The candidate layers the frozen Round-2 MP-primary evidence over the validated historical repository without rewriting the Round-1/Gate-8 scientific record.

## Current gate status

- RC0 scientific freeze: **PASS**
- RC1 release-tree assembly: **PASS**
- RC2 hash/provenance verification: **PASS**
- RC3 packaged validation: **PASS**
- RC4 clean-room reproduction: **PASS**
- RC5 manuscript-repository consistency: **PASS**
- final Supplement evidence closure: **PASS**
- RC6 immutable candidate lock/tag: **READY pending one final workflow pass on this complete candidate tree**
- GitHub Release: not yet created
- Zenodo publication/DOI verification: not yet completed

## Current-evidence scope

The authoritative Round-2 evidence is under `round2_mp/`.

The release includes:
- 19 frozen MP-primary numerical source tables;
- 4 exact MP migration/diagnostic scripts;
- final Supplement Table S2 compact and full reader records;
- final empirical marginal summary and reader diagnostic table;
- empirical marginal prespecification and exact original validation script;
- a repository-native reproduction script that regenerates per-stream/per-population empirical diagnostics from archived Phase-4 states;
- the final Supplement source-record map;
- manuscript/Supplement freeze hashes and reviewer-audit records.

Historical affinity-logit primary analyses, historical S7-S9 Supplement assets, earlier 21-page/13-page working builds, and older Gate-8 publication figures remain provenance only.

## RC6 rule

After the final clean-room workflow passes on the complete candidate tree, that exact commit is the immutable release candidate. No repository file should be changed before creation of tag `jrsi-reproducibility-v2.0.0`. The public archive SHA-256 produced by that run is recorded externally with the GitHub Release/Zenodo deposit because embedding an archive hash inside the archive itself would alter the archive.
