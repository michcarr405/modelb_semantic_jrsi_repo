# JRSI major-revision validation branch

**Current gate:** Phase 3 statistical-pipeline validity passed.

The submitted paper-mode outputs and the legacy `run_pipeline.py` workflow below are retained only for provenance. They are **not** the corrected revision production pipeline and must not be used to generate revised scientific claims. The corrected production rerun remains blocked until the pre-production choices in `PHASE_03_HANDOFF.md` are frozen.

Validated Phase 3 commands:

```bash
python -m pytest -q
python scripts/validate_statistical_pipeline.py
```

These commands use unit tests, synthetic continuation tables, and one tiny identity-endpoint diagnostic only. See `STATISTICAL_PIPELINE_VALIDATION.md`.

---

# Model B Semantic Information: JSRI-ready standalone analysis repo

This repository reruns the **full original Model B implementation** and adds an end-to-end intervention-based semantic-information analysis designed for a manuscript targeting **J. R. Soc. Interface**.

The package contains no placeholder data. Simulations, intervention points, statistics, and figures are generated from the included Model B implementation. The archive also includes the current paper-mode outputs available at package-build time under `results/paper`, `stats/paper`, and `figures/paper`.

## Scientific framing

The analysis follows a three-layer JSRI strategy:

1. **Main biological decomposition**: `excess_over_control` is the primary viability definition. It asks whether preserved motif information supports adaptive viability beyond the matched non-selective/control baseline.
2. **Biological robustness decomposition**: `mean_future_fitness` and `threshold_survival` test whether the syntactic-semantic separation survives permissive and strict biological viability definitions.
3. **Physics/entropy diagnostics**: entropy-based viability definitions are kept in a separate figure and stats table rather than pooled into the main biological Figure 4. This avoids treating a generic entropy proxy as equivalent to the Model B fitness mechanism.

## Entropy-based viability definitions

The current revision replaces the single broad `negative_shannon_entropy` display with three explicit entropy diagnostics:

- `negative_local_metabolite_configuration_entropy`  
  Negative entropy of local metabolite-configuration states, by default adjacent metabolite pairs. This is best aligned with the semantic variable because the model asks whether motifs predict local metabolite configurations.

- `negative_adjacency_state_entropy`  
  Negative entropy of productive/anti-productive/neutral adjacency classes. This is best aligned with the Model B fitness mechanism because growth depends on productive and anti-productive metabolite adjacencies.

- `negative_protocell_compositional_entropy`  
  Negative entropy of coarse-grained protocell compositional states based on nucleotide composition across inherited oligomers. This is a broad global-composition null/reference, not the preferred mechanistic physics measure.

A legacy `negative_fitness_distribution_entropy` is retained in the code as an optional diagnostic of the binned future-fitness distribution, but it is not plotted in the revised main Figure 4.

## Important method choice: kmeans_profile is not pooled into the primary frontier

The primary pooled frontier uses only conservative/neutral coarse-graining interventions:

- `balanced_random_group`
- `affinity_rank_group`
- `prefix_group`

`kmeans_profile` is retained, but only as a separate **function-preserving diagnostic / mechanistic analysis**. It groups motifs by affinity-profile similarity, so it can preserve functional equivalence classes and dominate the upper envelope in selective runs. The pipeline therefore writes:

- primary no-kmeans summaries used for main figures
- all-methods pooled diagnostic summaries
- kmeans-only mechanistic summaries
- method-ablation statistical tests

## Main figure order

The figure scripts generate the following main-text sequence:

1. `figure_1_baseline_vs_adaptive_gain.png`  
   Original Model B baseline: syntactic MI vs adaptive gain.
2. `figure_2_intervention_schematic.png`  
   Intervention framework schematic: syntactic information, semantic information, value of information, and frontier logic.
3. `figure_3_main_decomposition_excess_over_control.png`  
   Main biological decomposition using `excess_over_control`.
4. `figure_4_viability_definition_comparison.png` and `figure_4_gap_widening.png`  
   Biological viability-definition comparison only: `excess_over_control`, `mean_future_fitness`, and `threshold_survival`. Entropy curves are intentionally excluded.
5. `figure_4b_entropy_state_definitions.png`  
   New entropy-diagnostic figure comparing local metabolite-configuration entropy, productive/anti-productive adjacency-state entropy, and protocell compositional entropy.
6. `figure_5_frontiers_and_robustness.png`  
   Frontier examples and threshold/smoothing robustness.

Supplements include:

- `supplement_threshold_survival.png`
- `supplement_method_ablation_no_kmeans_sensitivity.png`
- `supplement_frontiers.png`
- `supplement_method_diagnostics.png`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Run a quick validation:

```bash
python scripts/run_pipeline.py --mode fast --outdir results/fast
python scripts/run_stats.py --results-dir results/fast --stats-dir stats/fast
python scripts/make_figures.py --results-dir results/fast --figures-dir figures/fast
```

Run a larger check:

```bash
python scripts/run_pipeline.py --mode medium --outdir results/medium
python scripts/run_stats.py --results-dir results/medium --stats-dir stats/medium
python scripts/make_figures.py --results-dir results/medium --figures-dir figures/medium
```

Run the paper analysis:

```bash
python scripts/run_pipeline.py --mode paper --outdir results/paper
python scripts/run_stats.py --results-dir results/paper --stats-dir stats/paper
python scripts/make_figures.py --results-dir results/paper --figures-dir figures/paper
```

## Output CSVs

For each viability definition and condition, the pipeline writes:

- `intervention_points_<condition>_<viability>.csv`  
  All intervention points, including `analysis_role = primary` or `diagnostic_function_preserving`.
- `intervention_summary_<condition>_<viability>.csv`  
  Primary no-kmeans summary used in main figures.
- `intervention_summary_<condition>_<viability>_all_methods_diagnostic.csv`  
  All-methods pooled diagnostic summary.
- `intervention_summary_<condition>_<viability>_kmeans_profile_mechanistic.csv`  
  kmeans-only function-preserving diagnostic summary.
- `threshold_sensitivity_<condition>_<viability>.csv`  
  Primary no-kmeans threshold/smoothing sensitivity grid.

The stats script writes:

- `baseline_permutation_tests.csv`
- `viability_gap_table.csv`
- `robustness_table.csv`
- `intervention_selective_vs_control_tests_primary_no_kmeans.csv`
- `method_ablation_kmeans_vs_primary_tests.csv`
- `method_viability_summary.csv`
- `viability_definition_dependence_tests.csv`
- `entropy_state_definition_summary.csv`
- `entropy_state_definition_selective_vs_control_tests.csv`

## Viability definitions

Biological definitions:

- `excess_over_control`: mean future fitness minus matched control mean future fitness.
- `mean_future_fitness`: mean fitness over the intervention horizon.
- `threshold_survival`: fraction of future generations whose mean fitness exceeds `mean_fitness_threshold`.

Entropy diagnostics:

- `negative_local_metabolite_configuration_entropy`: negative entropy of local metabolite-configuration states.
- `negative_adjacency_state_entropy`: negative entropy of productive/anti-productive adjacency-state classes.
- `negative_protocell_compositional_entropy`: negative entropy of coarse-grained protocell composition.
- `negative_fitness_distribution_entropy`: optional legacy entropy of the discretized short-horizon cell-fitness distribution.

## Notes

- Fast mode is for smoke testing.
- Medium mode is for checking qualitative patterns.
- Paper mode is intended for manuscript-scale outputs.
- Entropy diagnostics require rerunning `run_pipeline.py` with this revision because they depend on short-horizon state observations that were not stored in earlier output CSVs.
