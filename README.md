# Model B semantic-information analysis — JRSI Round-2 reproducibility release candidate

This repository contains the reproducibility record for manuscript **rsif-2026-0516**, *Counterfactual interventions reveal causal relevance of inherited sequence distinctions in a compositional-resampling model*.

## Current Round-2 evidence

The authoritative Round-2 evidence layer is under `round2_mp/`.

It contains frozen source tables for the MP core sweep, corrected retained-information frontiers, first-99 diagnostic, six causal-specificity contrasts, independent affinity-landscape replication, expected and realized marginal diagnostics, the complete 65-setting screen, Stage C protocol sensitivity, and Stage D targeted confirmations.

The final Supplement source map and reader-facing Table S2 records are archived explicitly. The empirical marginal-preservation diagnostic is reproducible from the archived Phase-4 states, grouping maps, fixed continuation root, and repository-native validation script. Per-stream and per-population diagnostic tables are regenerated in the clean-room workflow rather than duplicated as tracked derivative data.

The older Gate-8 / Round-1 directories retained elsewhere in the repository are **historical provenance only** and are not the current evidence base.

## Validation status

- RC0 scientific freeze: **PASS**
- RC1 release-tree assembly: **PASS**
- RC2 provenance/hash verification: **PASS**
- RC3 packaged validation: **PASS**
- RC4 clean-room install/regeneration: **PASS**
- RC5 manuscript-repository consistency: **PASS**
- final Supplement evidence closure: **PASS**
- RC6 immutable lock/tag: **READY after the final candidate workflow passes**

External GitHub Actions validation uses Ubuntu 24.04 / Python 3.13.5. It verifies the original 23 frozen MP source/script hashes plus seven final-Supplement evidence hashes, validates the numerical records, runs the repository tests and historical freeze audit, reproduces the empirical marginal diagnostic from archived states, regenerates MP figures, and builds the public v2.0.0 archive.

## Version and archive

Prepared Round-2 release version: **2.0.0**

Planned immutable tag: `jrsi-reproducibility-v2.0.0`

Reserved archive DOI: **10.5281/zenodo.21852680**

The DOI is reserved but must not be described as publicly resolvable until the Zenodo record is published and independently verified.

Repository: https://github.com/michcarr405/modelb_semantic_jrsi_repo

## Environment

The validated environment is recorded in `requirements-lock.txt` and `environment-lock.yml`.

For a pip/venv installation:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-build-isolation
```

Round-2 validation:

```bash
sha256sum -c round2_mp/provenance/RC1_SOURCE_SHA256.txt
sha256sum -c round2_mp/provenance/RC5_SUPPLEMENT_EVIDENCE_SHA256.txt
python round2_mp/validation/validate_round2_tables.py
python round2_mp/validation/validate_supplement_evidence.py
python round2_mp/validation/reproduce_empirical_marginal_validation.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/validate_result_freeze.py
```

See `ROUND2_RELEASE_CANDIDATE.md`, `RELEASE_NOTES_DRAFT.md`, and `round2_mp/provenance/`.
