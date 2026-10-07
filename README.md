# Model B semantic-information analysis — JRSI Round-2 release candidate

This branch is the **Round-2 reproducibility release candidate** for manuscript **rsif-2026-0516**, *Counterfactual interventions reveal causal relevance of inherited sequence distinctions in a compositional-resampling model*.

The authoritative Round-2 evidence layer is under `round2_mp/`. The older Gate-8 / Round-1 directories retained elsewhere in this repository are **historical provenance only** and are not the evidence base for the current Round-2 manuscript.

## Candidate gates

- RC0 scientific freeze: **PASS**
- RC1 release-tree assembly: **PASS**
- RC2 provenance/hash verification: **PASS**
- RC3 packaged validation: **PASS**
- RC4 clean-room install/regeneration: **PASS**
- RC5 manuscript-repository consistency: **PASS**
- RC6 immutable lock/tag: **NEXT**
- Zenodo publication/DOI verification: pending

Clean-room validation used Ubuntu 24.04 / Python 3.13.5, verified all 23 frozen Round-2 source/script hashes, passed 68 repository tests and 5/5 historical freeze checks, and regenerated MP figures from released source tables.

No immutable Round-2 tag or GitHub Release has yet been created.

See `ROUND2_RELEASE_CANDIDATE.md` and `round2_mp/provenance/`.
