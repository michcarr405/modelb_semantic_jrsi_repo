# Round-2 marginal-preserving reproducibility candidate

Candidate: `jrsi-reproducibility-v2.0.0-rc7`. This archive supports the Round-2 analysis of causal relevance of inherited sequence distinctions in a compositional-resampling model.

The primary intervention averages native local-state probabilities using the current population's motif frequencies within each group and positional segment. It preserves the expected one-site segment-conditioned marginal while allowing relational organization and subsequent fitness to change. The pre-softmax affinity-averaging intervention is an explicitly secondary comparator.

Current numerical evidence is under `round2_mp/source_tables/`. The model/state foundation remains under `src/` and `results/`. Frozen production drivers are installed unchanged under `round2/mp_migration/`; the recovered final 64-new causal-specificity driver is under `round2_mp/causal_specificity_high_continuation/`.

Read `ROUND2_RELEASE_CANDIDATE_README.md`, `round2_mp/validation/INTEGRATED_REGENERATION_VALIDATION.json`, and `round2_mp/validation/FULL_REGENERATION_STATUS.csv` for exact validation scope.

## Install and validate

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r round2_mp/validation/requirements-validated.txt -e .
python -m pytest -q tests
python round2_mp/validation/validate_integrated.py
```

The packaged validator checks the recorded complete regeneration outputs. For a genuinely fresh production replay, choose a destination outside this repository that does not already exist:

```bash
python round2_mp/validation/run_full_cleanroom.py --destination ../fresh-round2-replay --workers 8
```

This copies immutable inputs and unmodified drivers, excludes previous Round-2 generated outputs, and regenerates every current scientific evidence family. The runner uses the Python interpreter in the environment where the package was installed. Full campaigns require sustained computation.

## Provenance

`src/modelb_semantic_repo/mp_operator.py` is a documented functional reconstruction, not byte-identical recovery of lost source. `round2_mp/SOURCE_RECOVERY.md` explains its evidence and validation. Seed provenance combines the original recovered 27,139-record MP ledger with the recovered final causal-specificity supplement; see `round2_mp/provenance/CANONICAL_SEED_PROVENANCE.md`.

Manuscript and Supplement prose, TeX sources, compiled PDFs, and publication-source ZIPs are maintained separately and are excluded from this repository. Prose-only changes do not require a repository update or a new computational release. Changes to data, numerical results, analysis code, methods implemented by the code, or reproducibility claims require the corresponding repository update. The numerical Table S4 correction remains documented under `round2_mp/reporting_corrections/`. Historical audit records describe earlier snapshots and do not control current manuscript wording. See `REPOSITORY_CONTENT_POLICY.md`.

This candidate has not been published or tagged, and no new DOI is claimed.

## Current figures

Standalone Round-2 figures are under `round2_mp/figures/main/` (Figures 1–8) and `round2_mp/figures/supplement/` (Figures S1–S6). Root `figures/paper/` contains historical outputs. The 14 current PDFs are exact recovered archived masters. A portable build regenerates the 12 data figures with rendered-pixel validation; the two conceptual diagrams are archived asset copies. See `round2_mp/figure_build/README.md`.
