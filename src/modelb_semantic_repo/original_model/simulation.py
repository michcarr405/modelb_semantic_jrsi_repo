import numpy as np
from .core import compute_fitnesses_and_observations
from .mi import compute_mutual_information
from ..rng import make_generator


def init_population(n_cells, n_seqs, seq_len, rng):
    return rng.integers(0, 4, size=(n_cells, n_seqs, seq_len), dtype=np.int8)


def reproduce_with_partitioning(pop, fitnesses, mu, inherit_prob, rng):
    """Fitness-weighted compositional resampling using vectorized explicit draws.

    The stochastic law is unchanged from the audited implementation: one parent
    is sampled per daughter, each daughter slot either samples a parental
    sequence with replacement or a uniform environmental sequence, and every
    site then mutates independently. Drawing complete arrays makes production
    runs tractable while retaining explicit caller-controlled RNG streams.
    """
    fitnesses = np.maximum(np.asarray(fitnesses, dtype=float), 0)
    total = float(fitnesses.sum())
    probs = fitnesses / total if total > 0 else np.full(len(fitnesses), 1.0 / len(fitnesses))
    n_cells, n_seqs, seq_len = pop.shape

    parent_uniforms = rng.random(n_cells)
    parent_indices = np.searchsorted(np.cumsum(probs), parent_uniforms, side="right")
    parent_indices = np.minimum(parent_indices, n_cells - 1)

    inherit_mask = rng.random((n_cells, n_seqs)) < inherit_prob
    parent_sequence_indices = rng.integers(0, n_seqs, size=(n_cells, n_seqs))
    environmental = rng.integers(0, 4, size=(n_cells, n_seqs, seq_len), dtype=np.int8)
    inherited = pop[parent_indices[:, None], parent_sequence_indices]
    new_pop = np.where(inherit_mask[:, :, None], inherited, environmental).astype(np.int8, copy=False)

    mutation_mask = rng.random((n_cells, n_seqs, seq_len)) < mu
    offsets = rng.integers(1, 4, size=(n_cells, n_seqs, seq_len), dtype=np.int8)
    mutated = ((new_pop.astype(np.int16) + offsets.astype(np.int16)) % 4).astype(np.int8)
    return np.where(mutation_mask, mutated, new_pop).astype(np.int8, copy=False)


def observe_population(population, motif_affinity_matrix, params, rng=None):
    if rng is None:
        raise ValueError("observe_population requires an explicit numpy.random.Generator")
    n_cells, n_seqs, seq_len = population.shape
    n_windows = n_cells * n_seqs * (seq_len - 4)
    uniforms = rng.random(n_windows)
    return compute_fitnesses_and_observations(
        population,
        motif_affinity_matrix,
        params["segment_favored_met"],
        params["bias_strength"],
        params["productive_pairs"],
        params["anti_pairs"],
        params["reward_strength"],
        params["penalty_strength"],
        params["temperature"],
        uniforms,
    )


def run_single_sim(mu, inherit_prob, seed, motif_affinity_matrix, params, return_final_population=False):
    initialization_rng = make_generator(seed, "baseline-initialization")
    observation_rng = make_generator(seed, "baseline-observation")
    propagation_rng = make_generator(seed, "baseline-propagation")
    population = init_population(params["n_cells"], params["n_seqs"], params["seq_len"], initialization_rng)
    fitness_hist = []
    mi_hist = []
    for _ in range(params["n_gens"]):
        fitnesses, motifs, mets = observe_population(population, motif_affinity_matrix, params, observation_rng)
        fitness_hist.append(fitnesses.mean())
        mi_hist.append(compute_mutual_information(mets, motifs, params["n_metabolites"]))
        population = reproduce_with_partitioning(population, fitnesses, mu, inherit_prob, propagation_rng)
    if return_final_population:
        fitnesses, motifs, mets = observe_population(population, motif_affinity_matrix, params, observation_rng)
        state = {
            "initialization": initialization_rng.bit_generator.state,
            "observation": observation_rng.bit_generator.state,
            "propagation": propagation_rng.bit_generator.state,
        }
        return np.array(fitness_hist), np.array(mi_hist), population, fitnesses, motifs, mets, state
    return np.array(fitness_hist), np.array(mi_hist)
