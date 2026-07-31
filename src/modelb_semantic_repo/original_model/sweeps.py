import numpy as np
from tqdm import tqdm
from .simulation import run_single_sim


def mean_sem(arr):
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1))
    sem = std / np.sqrt(len(arr))
    return mean, sem


def permutation_test_delta(deltas, n_perm=5000, rng_seed=0):
    rng = np.random.default_rng(rng_seed)
    obs = np.mean(deltas)
    n = len(deltas)
    count = 0
    for _ in range(n_perm):
        signs = rng.choice([-1, 1], size=n)
        if abs(np.mean(deltas * signs)) >= abs(obs):
            count += 1
    return obs, (count + 1) / (n_perm + 1)


def run_inheritance_sweep(inherit_probs, motif_affinity_matrix, params, label='selective', seed_offset=0, collect_final_states=False):
    fit_results = {}
    MI_results = {}
    final_states = {}
    n_reps = params['n_reps']
    mu = params['mutation_rate']
    for inh in tqdm(inherit_probs, desc=f'baseline sweep: {label}'):
        fit_histories, MI_histories = [], []
        rep_states = []
        for r in tqdm(range(n_reps), desc=f'{label} inh={inh:.1f}', leave=False):
            seed = seed_offset + 1000 + r + int(round(inh * 1000))
            out = run_single_sim(mu, inh, seed, motif_affinity_matrix, params, return_final_population=collect_final_states)
            if collect_final_states:
                fit_hist, MI_hist, population, fitnesses, motifs, mets, rng_state = out
                rep_states.append({
                    'population': population,
                    'fitnesses': fitnesses,
                    'motifs': motifs,
                    'metabolites': mets,
                    'seed': seed,
                    'rng_state': rng_state,
                    'inherit_prob': inh,
                })
            else:
                fit_hist, MI_hist = out
            fit_histories.append(fit_hist)
            MI_histories.append(MI_hist)
        fit_results[inh] = np.vstack(fit_histories)
        MI_results[inh] = np.vstack(MI_histories)
        if collect_final_states:
            final_states[inh] = rep_states
    return fit_results, MI_results, final_states
