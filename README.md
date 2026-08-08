# Model B semantic-information analysis — JRSI frozen reproducibility release

This repository is the reproducibility release for manuscript **rsif-2026-0516**, *Counterfactual interventions reveal causal relevance of inherited sequence distinctions in a compositional-resampling model*.

## Frozen scientific provenance

The scientific results were frozen at Git commit:

`2c7d78694579755402c0a1896e109b29dec4d6a0`

The Gate 8 documentation/tag closure is:

`phase7-gate8-passed-v1` at commit `36246a86320037506beed83d0f7366c33d2c59c5`.

Files added after Gate 8 for public release, citation metadata, environment locking, and publication-figure reproducibility are **packaging/documentation only**. They do not alter the frozen simulations, estimators, intervention panel, inferential procedures, source tables, or numerical results.

## Model scope

Model B is a sequence-explicit, fitness-weighted, Wright–Fisher-like compositional-resampling model of abstract protocell-like population units. The parameter `p` is parental-composition coupling/compositional-transmission fidelity; it is not literal molecular retention. Local-state labels are transient probabilistic assignments rather than inherited molecular inventories.

## What is in this release

- `src/` — versioned scientific implementation.
- `scripts/` — production, validation, result-freeze, and release-verification commands.
- `tests/` — unit/integration tests.
- `results/phase4_core/` — frozen corrected core outputs and evolved states.
- `results/phase5_causal_specificity/` — frozen causal-specificity controls.
- `results/phase6_generality/` — frozen staged generality/robustness outputs.
- `results/result_freeze/` — result inventory, inferential audit, and the authoritative frozen figure-source tables.
- `publication_figures/` — exact scripts, frozen source data, manifests, and final quantitative exports for manuscript Figures 3–8 and Supplementary Figures S1–S7.
- `artwork/` — provenance for Figures 1 and 2; their authoritative editable vector masters and final submission exports must be archived or permanently referenced before final public release.
- `reproduction/` — exact reproduction commands and release/clean-room records.
- `requirements-lock.txt` and `environment-lock.yml` — machine-readable locked software environment.

Historical submitted/paper-mode analyses retained elsewhere in the repository are provenance only and are **not** the evidence base for the revised manuscript. The revised scientific evidence is the Gate 8 frozen Phase 4–6 archive and its result-freeze source tables.

## Environment

Validated production/result-freeze environment:

- Linux x86-64
- Python 3.13.5
- NumPy 2.3.5
- pandas 2.2.3
- SciPy 1.17.0
- Numba 0.65.1
- Matplotlib 3.10.8
- scikit-learn 1.8.0 (Phase 6)
- Pillow 12.3.0 (publication-figure export)
- pytest 9.0.2 (validation)

Create an isolated environment using the lock file appropriate to the local package manager. For a pip/venv installation:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-build-isolation
```

## Validate the frozen repository

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/validate_result_freeze.py
python scripts/verify_publication_figure_release.py
```

## Reproduce manuscript-grade quantitative figures

The plotting scripts consume the frozen figure-source CSV files; they do **not** rerun production simulations.

```bash
bash scripts/reproduce_publication_figures.sh
```

Equivalent individual commands are recorded in `reproduction/EXACT_COMMANDS.md`.

- Main Figures 3–8: `publication_figures/main/produce_publication_figures.py`
- Supplementary Figures S1–S7: `publication_figures/supplementary/produce_supplementary_figures.py`
- Frozen source data: `publication_figures/source_tables/`

## Re-run the scientific analyses

Full production reruns are computationally heavier and are not needed to verify the frozen manuscript figures. Exact validated Phase 4–7 commands and their provenance are recorded in `reproduction/EXACT_COMMANDS.md` and the phase validation files.

## Data integrity

The Gate 8 result freeze verified 2,104 manifested Phase 4–6 files, 28 inferential/structural checks, and 11 frozen figure-source tables. `results/result_freeze/FILE_MANIFEST_SHA256.csv` and the release manifest provide file-level SHA-256 checksums.

## Citation and DOI

Citation metadata are provided in `CITATION.cff`. The permanent archive DOI must be inserted into the citation metadata, Data Accessibility statement, and release notes after the public archival deposit is minted.

## License

A repository license must be selected by the author before public release. `LICENSE_PENDING.md` records this unresolved release item; do not publish the candidate as the final release until it has been replaced by the selected `LICENSE` file.

## Figures 1 and 2

Figures 1 and 2 are vector schematics rather than analytical plots. Their authoritative editable masters are the author-maintained Google Slides files described in `artwork/EDITABLE_VECTOR_ARTWORK_HANDOFF.md`. The final public release should archive those editable masters or provide stable permanent references, together with the final journal-upload exports.
