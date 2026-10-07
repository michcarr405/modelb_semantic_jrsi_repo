# Model B semantic-information analysis — JRSI Round-2 reproducibility release candidate

This repository contains the reproducibility record for manuscript **rsif-2026-0516**, *Counterfactual interventions reveal causal relevance of inherited sequence distinctions in a compositional-resampling model*.

## Current Round-2 evidence

The authoritative Round-2 evidence layer is under `round2_mp/`.

It contains frozen source tables for the MP core sweep, corrected retained-information frontiers, first-99 diagnostic, six causal-specificity contrasts, independent affinity-landscape replication, expected/empirical marginal diagnostics, the complete 65-setting screen, Stage C protocol sensitivity, and Stage D targeted confirmations.

The older Gate-8 / Round-1 directories retained elsewhere in the repository are **historical provenance only** and are not the current evidence base.

## Validation status

- RC0 scientific freeze: **PASS**
- RC1 release-tree assembly: **PASS**
- RC2 provenance/hash verification: **PASS**
- RC3 packaged validation: **PASS**
- RC4 clean-room install/regeneration: **PASS**
- RC5 manuscript-repository consistency: **PASS**
- RC6 immutable lock/tag: pending final post-metadata validation

External GitHub Actions validation used Ubuntu 24.04 / Python 3.13.5, verified all 23 frozen Round-2 source/script hashes, passed 68 repository tests and 5/5 historical freeze checks, and regenerated MP figures from released source tables.

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
python round2_mp/validation/validate_round2_tables.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/validate_result_freeze.py
```

See `ROUND2_RELEASE_CANDIDATE.md`, `RELEASE_NOTES_DRAFT.md`, and `round2_mp/provenance/`.
