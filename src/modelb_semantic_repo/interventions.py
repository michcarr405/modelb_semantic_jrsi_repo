import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.cluster.vq import kmeans2
from tqdm import tqdm

from .original_model.simulation import observe_population, reproduce_with_partitioning
from .original_model.mi import compute_mutual_information


# Ordered for the JSRI strategy: main biological, canonical physics, permissive
# reference, strict robustness.
BIOLOGICAL_VIABILITY_DEFS = [
    'excess_over_control',
    'mean_future_fitness',
    'threshold_survival',
]

ENTROPY_VIABILITY_DEFS = [
    'negative_fitness_distribution_entropy',
    'negative_local_metabolite_configuration_entropy',
    'negative_adjacency_state_entropy',
    'negative_protocell_compositional_entropy',
]

# Backward-compatible alias used by pipeline/statistics.
VIABILITY_DEFS = BIOLOGICAL_VIABILITY_DEFS + ENTROPY_VIABILITY_DEFS


def _normalize_labels(labels):
    mapping = {}
    out = []
    nxt = 0
    for x in labels:
        x = int(x)
        if x not in mapping:
            mapping[x] = nxt
            nxt += 1
        out.append(mapping[x])
    return np.asarray(out, dtype=int)


def balanced_random_group(n_items, k, rng):
    k = max(1, min(int(k), n_items))
    labels = np.arange(n_items) % k
    rng.shuffle(labels)
    return _normalize_labels(labels)


def prefix_group(strings, k):
    if not strings:
        return np.array([], dtype=int)
    prefix_len = max(1, min(len(strings[0]), int(np.ceil(np.log(max(int(k), 2)) / np.log(4)))))
    labels = []
    groups = {}
    nxt = 0
    for s in strings:
        key = s[:prefix_len]
        if key not in groups:
            groups[key] = nxt
            nxt += 1
        labels.append(groups[key])
    return _normalize_labels(labels)


def affinity_rank_group(profiles, k):
    n = profiles.shape[0]
    k = max(1, min(int(k), n))
    scores = profiles.mean(axis=1) + 0.25 * profiles.std(axis=1)
    order = np.argsort(scores)
    labels = np.zeros(n, dtype=int)
    for i, idx in enumerate(order):
        labels[idx] = min(k - 1, (i * k) // n)
    return _normalize_labels(labels)


def profile_diversity(profiles):
    if profiles.size == 0:
        return 0.0
    uniq = np.unique(np.round(profiles, 10), axis=0)
    if len(uniq) <= 1:
        return 0.0
    return float(np.mean(np.std(uniq, axis=0)))


def kmeans_profile_groups(profiles, k, rng, restarts=8, diversity_threshold=0.08):
    """Function-preserving profile coarse-graining.

    This method is retained as a diagnostic/mechanistic probe, not as a neutral
    member of the primary pooled frontier. It can preserve affinity-profile
    classes and therefore recover much higher viability in selective runs.
    """
    n_items = int(profiles.shape[0])
    if n_items == 0:
        return np.array([], dtype=int), {'status': 'empty_input', 'k_used': 0}
    div = profile_diversity(profiles)
    if div < diversity_threshold:
        return np.zeros(n_items, dtype=int), {'status': 'disabled_low_diversity', 'k_used': 1, 'diversity': div}
    uniq = np.unique(np.round(profiles, 12), axis=0)
    max_valid_k = max(1, min(int(k), len(uniq), n_items))
    if max_valid_k <= 1:
        return np.zeros(n_items, dtype=int), {'status': 'fallback_single_group', 'k_used': 1, 'diversity': div}
    best_labels, best_inertia = None, None
    for _ in range(max(1, int(restarts))):
        seed_idx = rng.choice(n_items, size=max_valid_k, replace=False)
        init = profiles[seed_idx]
        try:
            centroids, labels = kmeans2(profiles, init, minit='matrix', missing='warn')
        except Exception:
            continue
        labels = np.asarray(labels, dtype=int)
        if len(np.unique(labels)) < max_valid_k:
            continue
        inertia = float(((profiles - centroids[labels]) ** 2).sum())
        if best_inertia is None or inertia < best_inertia:
            best_inertia = inertia
            best_labels = labels.copy()
    if best_labels is None:
        return np.zeros(n_items, dtype=int), {'status': 'fallback_failed_kmeans', 'k_used': 1, 'diversity': div}
    return _normalize_labels(best_labels), {'status': 'ok', 'k_used': int(max_valid_k), 'diversity': div, 'inertia': float(best_inertia)}


def _motif_index_to_string(idx):
    alphabet = 'ACGU'
    chars = []
    x = int(idx)
    for _ in range(5):
        chars.append(alphabet[x % 4])
        x //= 4
    return ''.join(reversed(chars))


def _group_affinity_matrix(original_aff, labels):
    labels = np.asarray(labels, dtype=int)
    out = np.empty_like(original_aff)
    for g in np.unique(labels):
        members = np.where(labels == g)[0]
        mean_profile = original_aff[members].mean(axis=0)
        out[members] = mean_profile
    return out


def _simulate_horizon(population, motif_affinity_matrix, params, inherit_prob, horizon, rng):
    """Rerun a final population for a short horizon after an intervention.

    In addition to future fitnesses, retain coarse-grainable state observations
    needed by the entropy-based viability definitions. These are generated from
    the same stochastic observations used to compute fitness, so the entropy
    diagnostics are derived from real simulation trajectories rather than
    placeholder or post-hoc synthetic data.
    """
    pop = np.array(population, copy=True)
    future_means = []
    cell_fitnesses = []
    metabolite_observations = []
    populations = []
    for _ in range(horizon):
        populations.append(np.array(pop, copy=True))
        fitnesses, motifs, mets = observe_population(pop, motif_affinity_matrix, params)
        future_means.append(float(np.mean(fitnesses)))
        cell_fitnesses.append(np.asarray(fitnesses, dtype=float))
        metabolite_observations.append(np.asarray(mets, dtype=np.int64))
        pop = reproduce_with_partitioning(pop, fitnesses, params['mutation_rate'], inherit_prob, rng)
    return {
        'mean_fitness': np.asarray(future_means, dtype=float),
        'cell_fitnesses': np.asarray(cell_fitnesses, dtype=float),
        'metabolite_observations': metabolite_observations,
        'populations': populations,
    }


def _negative_shannon_entropy(cell_fitnesses, bin_width=0.5):
    """Negative Shannon entropy of a discretized future cell-fitness distribution.

    The canonical Kolchinsky-Wolpert viability is negative entropy of the system
    state distribution. For this Model B implementation, the short-horizon cell
    fitness distribution is used as the coarse-grained system-state proxy.
    """
    values = np.asarray(cell_fitnesses, dtype=float).ravel()
    values = values[np.isfinite(values)]
    if values.size == 0:
        return np.nan
    width = float(bin_width)
    if width <= 0:
        raise ValueError('fitness_entropy_bin_width must be positive')
    bins = np.floor(values / width).astype(int)
    _, counts = np.unique(bins, return_counts=True)
    probs = counts.astype(float) / float(counts.sum())
    entropy = -float(np.sum(probs * np.log2(probs)))
    return -entropy


def _negative_entropy_from_integer_states(states):
    states = np.asarray(states, dtype=np.int64).ravel()
    if states.size == 0:
        return np.nan
    _, counts = np.unique(states, return_counts=True)
    probs = counts.astype(float) / float(counts.sum())
    entropy = -float(np.sum(probs * np.log2(probs)))
    return -entropy


def _reshape_metabolite_observations(mets, params):
    n_cells = int(params['n_cells'])
    n_seqs = int(params['n_seqs'])
    chain_len = int(params['seq_len']) - 4
    return np.asarray(mets, dtype=np.int64).reshape(n_cells, n_seqs, chain_len)


def _negative_local_metabolite_configuration_entropy(future, params):
    """Negative entropy over local metabolite configuration states.

    This is the entropy-based viability definition best aligned with the
    semantic variable in the paper: motifs are analyzed by the local metabolite
    configurations that they help predict. By default a local configuration is a
    neighboring metabolite pair; set local_configuration_window=3 for triplets.
    """
    n_met = int(params['n_metabolites'])
    window = int(params.get('local_configuration_window', 2))
    if window < 1:
        raise ValueError('local_configuration_window must be >= 1')
    labels = []
    for mets in future.get('metabolite_observations', []):
        arr = _reshape_metabolite_observations(mets, params)
        if window == 1:
            labels.append(arr.ravel())
            continue
        if arr.shape[2] < window:
            continue
        code = np.zeros(arr[:, :, :arr.shape[2] - window + 1].shape, dtype=np.int64)
        for j in range(window):
            code = code * n_met + arr[:, :, j:j + code.shape[2]]
        labels.append(code.ravel())
    if not labels:
        return np.nan
    return _negative_entropy_from_integer_states(np.concatenate(labels))


def _negative_adjacency_state_entropy(future, params):
    """Negative entropy over productive/anti-productive adjacency classes.

    Each adjacent metabolite pair is classified as neutral, productive,
    anti-productive, or both. This is the entropy diagnostic most directly
    aligned with the Model B fitness mechanism.
    """
    prod = np.asarray(params['productive_pairs'], dtype=bool)
    anti = np.asarray(params['anti_pairs'], dtype=bool)
    labels = []
    for mets in future.get('metabolite_observations', []):
        arr = _reshape_metabolite_observations(mets, params)
        a = arr[:, :, :-1]
        b = arr[:, :, 1:]
        state = prod[a, b].astype(np.int64) + 2 * anti[a, b].astype(np.int64)
        labels.append(state.ravel())
    if not labels:
        return np.nan
    return _negative_entropy_from_integer_states(np.concatenate(labels))


def _negative_protocell_compositional_entropy(future, params):
    """Negative entropy over coarse-grained protocell compositional states.

    Each protocell is represented by its global nucleotide composition across all
    inherited oligomers, binned to avoid treating every finite-sample count vector
    as a distinct microstate. This is a broad compositional null/reference rather
    than the preferred Model B semantic or fitness-mechanism entropy measure.
    """
    width = int(params.get('composition_entropy_bin_width', 8))
    if width <= 0:
        raise ValueError('composition_entropy_bin_width must be positive')
    labels = []
    base = max(1, int(params['n_seqs']) * int(params['seq_len']) // width + 2)
    for pop in future.get('populations', []):
        pop = np.asarray(pop, dtype=np.int64)
        counts = np.stack([(pop == b).sum(axis=(1, 2)) for b in range(4)], axis=1)
        bins = counts // width
        code = (((bins[:, 0] * base + bins[:, 1]) * base + bins[:, 2]) * base + bins[:, 3])
        labels.append(code.astype(np.int64))
    if not labels:
        return np.nan
    return _negative_entropy_from_integer_states(np.concatenate(labels))


def compute_viability(future, matched_control_future, kind, threshold, params):
    if kind == 'mean_future_fitness':
        return float(np.mean(future['mean_fitness']))
    if kind == 'excess_over_control':
        return float(np.mean(future['mean_fitness']) - np.mean(matched_control_future['mean_fitness']))
    if kind == 'threshold_survival':
        return float(np.mean(future['mean_fitness'] >= threshold))
    if kind in ('negative_shannon_entropy', 'negative_fitness_distribution_entropy'):
        return float(_negative_shannon_entropy(future['cell_fitnesses'], params.get('fitness_entropy_bin_width', 0.5)))
    if kind == 'negative_local_metabolite_configuration_entropy':
        return float(_negative_local_metabolite_configuration_entropy(future, params))
    if kind == 'negative_adjacency_state_entropy':
        return float(_negative_adjacency_state_entropy(future, params))
    if kind == 'negative_protocell_compositional_entropy':
        return float(_negative_protocell_compositional_entropy(future, params))
    raise ValueError(kind)


def build_frontier(df, frontier_bins=16, min_bin_support=3):
    if df.empty:
        return pd.DataFrame(columns=['preserved_info_bin', 'frontier_viability', 'support', 'method'])
    lo = float(df['preserved_info'].min())
    hi = float(df['preserved_info'].max())
    if not np.isfinite(lo) or not np.isfinite(hi) or lo == hi:
        return pd.DataFrame(columns=['preserved_info_bin', 'frontier_viability', 'support', 'method'])
    bins = np.linspace(lo, hi, frontier_bins + 1)
    work = df.copy()
    work['bin'] = pd.cut(work['preserved_info'], bins=bins, include_lowest=True, duplicates='drop')
    grouped = (work.groupby(['bin', 'method'], observed=True)
                 .agg(preserved_info_bin=('preserved_info', 'mean'),
                      frontier_viability=('viability', 'max'),
                      support=('viability', 'size'))
                 .reset_index())
    grouped = grouped[grouped['support'] >= min_bin_support].copy()
    if grouped.empty:
        return pd.DataFrame(columns=['preserved_info_bin', 'frontier_viability', 'support', 'method'])
    grouped = grouped.sort_values(['preserved_info_bin', 'frontier_viability'], ascending=[True, False])
    frontier = grouped.groupby('preserved_info_bin', as_index=False).first()
    frontier = frontier[['preserved_info_bin', 'frontier_viability', 'support', 'method']].sort_values('preserved_info_bin')
    # The information-viability frontier is an upper envelope. Enforce monotonicity
    # here so sparse-bin dropouts are not interpreted as biology.
    frontier['frontier_viability'] = frontier['frontier_viability'].cummax()
    return frontier


def smooth_frontier(frontier, window=1):
    frontier = frontier.sort_values('preserved_info_bin').copy()
    if frontier.empty:
        frontier['frontier_viability_smooth'] = []
        return frontier
    if window <= 1:
        frontier['frontier_viability_smooth'] = frontier['frontier_viability'].cummax()
        return frontier
    vals = frontier['frontier_viability'].to_numpy()
    sm = []
    n = len(vals)
    for i in range(n):
        lo = max(0, i - window + 1)
        hi = min(n, i + window)
        sm.append(np.max(vals[lo:hi]))
    frontier['frontier_viability_smooth'] = np.maximum.accumulate(np.asarray(sm, dtype=float))
    return frontier


def interpolated_threshold(frontier, target):
    if frontier.empty or not np.isfinite(target):
        return np.nan, False
    x = frontier['preserved_info_bin'].to_numpy()
    y = frontier['frontier_viability_smooth'].to_numpy()
    hit = np.where(y >= target)[0]
    if len(hit) == 0:
        return float(x[-1]), False
    i = int(hit[0])
    if i == 0:
        return float(x[0]), True
    x0, x1 = float(x[i - 1]), float(x[i])
    y0, y1 = float(y[i - 1]), float(y[i])
    if y1 == y0:
        return float(x1), True
    frac = (target - y0) / (y1 - y0)
    frac = min(1.0, max(0.0, frac))
    return float(x0 + frac * (x1 - x0)), True


def _labels_for_method(method, profiles, motif_strings, k, rng, params):
    if method == 'balanced_random_group':
        return balanced_random_group(4**5, k, rng), {'status': 'ok'}
    if method == 'affinity_rank_group':
        return affinity_rank_group(profiles, k), {'status': 'ok'}
    if method == 'prefix_group':
        return prefix_group(motif_strings, k), {'status': 'ok'}
    if method == 'kmeans_profile':
        return kmeans_profile_groups(profiles, k, rng, params['kmeans_restarts'], params['profile_diversity_threshold'])
    raise ValueError(method)


def _summarize_method_subset(df_inh, actual_vals, syn_vals, params, condition_name, viability_kind, inh, subset_name, methods):
    method_df = df_inh[df_inh['method'].isin(methods)].copy()
    frontier = build_frontier(method_df, params['frontier_bins'], params['min_bin_support'])
    full_scramble = float(method_df['viability'].min()) if not method_df.empty else np.nan
    actual_mean = float(np.mean(actual_vals)) if actual_vals else np.nan
    total_syntactic_mean = float(np.mean(syn_vals)) if syn_vals else np.nan
    value_of_information = actual_mean - full_scramble if np.isfinite(actual_mean) and np.isfinite(full_scramble) else np.nan

    sensitivity = []
    semantic_estimates = []
    reach_flags = []
    for window in params['smoothing_windows']:
        sf = smooth_frontier(frontier, window=window)
        for tol in params['tolerances']:
            target = actual_mean - tol * value_of_information if np.isfinite(value_of_information) else np.nan
            thr, reached = interpolated_threshold(sf, target)
            sensitivity.append({
                'condition': condition_name,
                'viability_def': viability_kind,
                'inherit_prob': inh,
                'analysis_set': subset_name,
                'tolerance': tol,
                'smoothing_window': window,
                'semantic_info': thr,
                'target_reached': bool(reached),
            })
            if tol == params['tolerances'][0] and window == params['smoothing_windows'][0]:
                semantic_estimates.append(thr)
                reach_flags.append(bool(reached))
    semantic_mean = float(np.nanmean(semantic_estimates)) if semantic_estimates else np.nan
    target_reached_primary = bool(all(reach_flags)) if reach_flags else False
    summary = {
        'condition': condition_name,
        'viability_def': viability_kind,
        'inherit_prob': inh,
        'analysis_set': subset_name,
        'methods': '|'.join(methods),
        'syntactic_info_mean': total_syntactic_mean,
        'semantic_info_mean': semantic_mean,
        'semantic_efficiency_mean': semantic_mean / total_syntactic_mean if total_syntactic_mean and np.isfinite(semantic_mean) else np.nan,
        'value_of_information_mean': value_of_information,
        'actual_viability_mean': actual_mean,
        'frontier_max_viability': float(frontier['frontier_viability'].max()) if not frontier.empty else np.nan,
        'frontier_reaches_target': target_reached_primary,
        'n_intervention_points': int(len(method_df)),
    }
    return summary, pd.DataFrame(sensitivity), frontier


def analyze_condition(final_states, matched_control_states, motif_affinity_matrix, params, condition_name, outdir, viability_kind):
    outdir = Path(outdir)
    rows = []
    primary_summaries = []
    all_summaries = []
    kmeans_summaries = []
    primary_sensitivity = []
    all_sensitivity = []
    kmeans_sensitivity = []
    threshold = params['mean_fitness_threshold']
    motif_strings = [_motif_index_to_string(i) for i in range(4**5)]
    primary_methods = params['primary_intervention_methods']
    all_methods = params['intervention_methods']
    kmeans_methods = params['diagnostic_intervention_methods']

    for inh, reps in tqdm(final_states.items(), desc=f'interventions {condition_name} {viability_kind}'):
        actual_vals = []
        syn_vals = []
        matched_controls = matched_control_states[inh]
        for rep_idx, rep_state in enumerate(tqdm(reps[:params['intervention_reps']], desc=f'{condition_name} inh={inh:.1f}', leave=False)):
            pop = rep_state['population']
            seed = rep_state['seed'] + 700000 + rep_idx
            rng = np.random.default_rng(seed)
            profiles = motif_affinity_matrix.copy()
            control_rep = matched_controls[min(rep_idx, len(matched_controls) - 1)]
            control_pop = control_rep['population']

            actual_future = _simulate_horizon(pop, motif_affinity_matrix, params, inh, params['intervention_horizon'], rng)
            control_future = _simulate_horizon(control_pop, params['motif_affinity_matrix_no_aff'], params, inh, params['intervention_horizon'], np.random.default_rng(seed + 1))
            fitnesses, motifs, mets = observe_population(pop, motif_affinity_matrix, params)
            total_syntactic = compute_mutual_information(mets, motifs, params['n_metabolites'])
            actual_viability = compute_viability(actual_future, control_future, viability_kind, threshold, params)
            syn_vals.append(total_syntactic)
            actual_vals.append(actual_viability)

            for method in all_methods:
                for k in params['k_grid']:
                    labels, meta = _labels_for_method(method, profiles, motif_strings, k, rng, params)
                    grouped_aff = _group_affinity_matrix(motif_affinity_matrix, labels)
                    preserved_groups = max(1, int(len(np.unique(labels))))
                    preserved_ratio = np.log2(preserved_groups) / np.log2(4**5)
                    preserved_info = float(total_syntactic * preserved_ratio)
                    future = _simulate_horizon(pop, grouped_aff, params, inh, params['intervention_horizon'], np.random.default_rng(seed + 33 + k))
                    viability = compute_viability(future, control_future, viability_kind, threshold, params)
                    rows.append({
                        'condition': condition_name,
                        'viability_def': viability_kind,
                        'inherit_prob': inh,
                        'rep': rep_idx,
                        'method': method,
                        'analysis_role': 'primary' if method in primary_methods else 'diagnostic_function_preserving',
                        'k': k,
                        'preserved_info': preserved_info,
                        'viability': viability,
                        'actual_viability': actual_viability,
                        'syntactic_info': total_syntactic,
                        'meta': json.dumps(meta, sort_keys=True),
                    })

        df_inh = pd.DataFrame([r for r in rows if r['condition'] == condition_name and r['viability_def'] == viability_kind and r['inherit_prob'] == inh])

        # Primary: no kmeans_profile.
        summary, sens, frontier = _summarize_method_subset(df_inh, actual_vals, syn_vals, params, condition_name, viability_kind, inh, 'primary_no_kmeans', primary_methods)
        primary_summaries.append(summary)
        primary_sensitivity.append(sens)
        for window in params['smoothing_windows']:
            sf = smooth_frontier(frontier, window=window)
            if not sf.empty:
                sf.to_csv(outdir / f'frontier_debug_{condition_name}_{viability_kind}_primary_no_kmeans_inh_{inh:.1f}_smooth{window}.csv', index=False)
                if window == params['smoothing_windows'][0]:
                    # Backward-compatible primary file name.
                    sf.to_csv(outdir / f'frontier_debug_{condition_name}_{viability_kind}_inh_{inh:.1f}_smooth{window}.csv', index=False)

        # All methods pooled: diagnostic only, for transparency.
        summary_all, sens_all, frontier_all = _summarize_method_subset(df_inh, actual_vals, syn_vals, params, condition_name, viability_kind, inh, 'all_methods_pooled_diagnostic', all_methods)
        all_summaries.append(summary_all)
        all_sensitivity.append(sens_all)
        for window in params['smoothing_windows']:
            sf_all = smooth_frontier(frontier_all, window=window)
            if not sf_all.empty:
                sf_all.to_csv(outdir / f'frontier_debug_{condition_name}_{viability_kind}_all_methods_inh_{inh:.1f}_smooth{window}.csv', index=False)

        # kmeans_profile only: mechanistic/function-preserving diagnostic.
        summary_k, sens_k, frontier_k = _summarize_method_subset(df_inh, actual_vals, syn_vals, params, condition_name, viability_kind, inh, 'kmeans_profile_only_mechanistic', kmeans_methods)
        kmeans_summaries.append(summary_k)
        kmeans_sensitivity.append(sens_k)
        for window in params['smoothing_windows']:
            sf_k = smooth_frontier(frontier_k, window=window)
            if not sf_k.empty:
                sf_k.to_csv(outdir / f'frontier_debug_{condition_name}_{viability_kind}_kmeans_profile_inh_{inh:.1f}_smooth{window}.csv', index=False)

    points = pd.DataFrame(rows)
    summary = pd.DataFrame(primary_summaries)
    sens = pd.concat(primary_sensitivity, ignore_index=True) if primary_sensitivity else pd.DataFrame()
    all_summary = pd.DataFrame(all_summaries)
    all_sens = pd.concat(all_sensitivity, ignore_index=True) if all_sensitivity else pd.DataFrame()
    kmeans_summary = pd.DataFrame(kmeans_summaries)
    kmeans_sens = pd.concat(kmeans_sensitivity, ignore_index=True) if kmeans_sensitivity else pd.DataFrame()

    points.to_csv(outdir / f'intervention_points_{condition_name}_{viability_kind}.csv', index=False)
    summary.to_csv(outdir / f'intervention_summary_{condition_name}_{viability_kind}.csv', index=False)
    sens.to_csv(outdir / f'threshold_sensitivity_{condition_name}_{viability_kind}.csv', index=False)
    all_summary.to_csv(outdir / f'intervention_summary_{condition_name}_{viability_kind}_all_methods_diagnostic.csv', index=False)
    all_sens.to_csv(outdir / f'threshold_sensitivity_{condition_name}_{viability_kind}_all_methods_diagnostic.csv', index=False)
    kmeans_summary.to_csv(outdir / f'intervention_summary_{condition_name}_{viability_kind}_kmeans_profile_mechanistic.csv', index=False)
    kmeans_sens.to_csv(outdir / f'threshold_sensitivity_{condition_name}_{viability_kind}_kmeans_profile_mechanistic.csv', index=False)
    return summary, sens, points
