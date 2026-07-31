from copy import deepcopy
from .original_model.config import default_parameters


def get_mode_parameters(mode: str):
    """Return reproducible run parameters for fast, medium, and paper modes.

    The paper mode reruns the full original Model B inheritance sweep and then
    performs the JSRI-oriented intervention analysis. The primary pooled frontier
    intentionally excludes kmeans_profile; kmeans_profile is kept as a separate
    function-preserving diagnostic/mechanistic analysis.
    """
    base = default_parameters()
    params = deepcopy(base)

    if mode == 'fast':
        params['n_cells'] = 40
        params['n_gens'] = 60
        params['n_reps'] = 4
        params['intervention_reps'] = 4
        params['intervention_horizon'] = 12
        params['frontier_bins'] = 12
        params['kmeans_restarts'] = 8
        params['bootstrap_reps'] = 300
    elif mode == 'medium':
        params['n_cells'] = 60
        params['n_gens'] = 100
        params['n_reps'] = 8
        params['intervention_reps'] = 8
        params['intervention_horizon'] = 20
        params['frontier_bins'] = 18
        params['kmeans_restarts'] = 12
        params['bootstrap_reps'] = 600
    elif mode == 'paper':
        params['n_cells'] = 80
        params['n_gens'] = 150
        params['n_reps'] = 20
        # Intervention re-running is the expensive step; use enough independent
        # final populations for stable paper figures while keeping runtime practical.
        params['intervention_reps'] = 12
        params['intervention_horizon'] = 24
        params['frontier_bins'] = 24
        params['kmeans_restarts'] = 16
        params['bootstrap_reps'] = 1000
    else:
        raise ValueError(f'Unknown mode: {mode}')

    params['tolerances'] = [0.01, 0.025, 0.05]
    params['smoothing_windows'] = [1, 2, 3] if mode == 'fast' else [1, 2, 3, 5]
    params['k_grid'] = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128]

    # Primary estimates use conservative/neutral coarse-grainings. kmeans_profile
    # is not pooled into the primary frontier because it preserves affinity-profile
    # classes and can dominate the upper envelope in selective runs.
    params['primary_intervention_methods'] = [
        'balanced_random_group',
        'affinity_rank_group',
        'prefix_group',
    ]
    params['diagnostic_intervention_methods'] = ['kmeans_profile']
    params['intervention_methods'] = params['primary_intervention_methods'] + params['diagnostic_intervention_methods']

    params['min_bin_support'] = 3 if mode == 'fast' else (4 if mode == 'medium' else 5)
    params['profile_diversity_threshold'] = 0.08
    params['mean_fitness_threshold'] = 30.0

    # Entropy-based physics diagnostics. These are deliberately separated from
    # the main biological Figure 4 viability comparison.
    params['fitness_entropy_bin_width'] = 0.5
    params['local_configuration_window'] = 2
    params['composition_entropy_bin_width'] = 8
    return params
