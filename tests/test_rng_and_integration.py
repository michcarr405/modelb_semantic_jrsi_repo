import numpy as np
import pytest

from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.original_model.simulation import (
    init_population,
    observe_population,
    reproduce_with_partitioning,
    run_single_sim,
)
from modelb_semantic_repo.rng import AnalysisStream, ContinuationStream, make_generator


def tiny_params():
    params = default_parameters()
    params["n_cells"] = 5
    params["n_seqs"] = 2
    params["seq_len"] = 12
    params["n_gens"] = 4
    return params


def test_observer_requires_explicit_generator():
    params = tiny_params()
    pop = np.zeros((5, 2, 12), dtype=np.int8)
    with pytest.raises(ValueError):
        observe_population(pop, params["motif_affinity_matrix"], params)


def test_observer_same_seed_reproduces():
    params = tiny_params()
    pop = np.zeros((5, 2, 12), dtype=np.int8)
    a = observe_population(pop, params["motif_affinity_matrix"], params, np.random.default_rng(8))
    b = observe_population(pop, params["motif_affinity_matrix"], params, np.random.default_rng(8))
    for x, y in zip(a, b):
        assert np.array_equal(x, y)


def test_observer_different_seed_diverges():
    params = tiny_params()
    pop = np.zeros((5, 2, 12), dtype=np.int8)
    a = observe_population(pop, params["motif_affinity_matrix"], params, np.random.default_rng(8))
    b = observe_population(pop, params["motif_affinity_matrix"], params, np.random.default_rng(9))
    assert not np.array_equal(a[2], b[2])


def test_run_single_sim_same_seed_reproduces():
    params = tiny_params()
    a = run_single_sim(params["mutation_rate"], 0.8, 42, params["motif_affinity_matrix"], params)
    b = run_single_sim(params["mutation_rate"], 0.8, 42, params["motif_affinity_matrix"], params)
    assert np.array_equal(a[0], b[0])
    assert np.array_equal(a[1], b[1])


def test_run_single_sim_different_seed_diverges():
    params = tiny_params()
    a = run_single_sim(params["mutation_rate"], 0.8, 42, params["motif_affinity_matrix"], params)
    b = run_single_sim(params["mutation_rate"], 0.8, 43, params["motif_affinity_matrix"], params)
    assert not np.array_equal(a[0], b[0])


def simulate_continuation(pop, affinity, params, stream, horizon=4):
    pop = pop.copy()
    obs_rng = stream.observation_generator()
    prop_rng = stream.propagation_generator()
    means = []
    for _ in range(horizon):
        fitness, _, _ = observe_population(pop, affinity, params, obs_rng)
        means.append(float(fitness.mean()))
        pop = reproduce_with_partitioning(pop, fitness, params["mutation_rate"], 0.8, prop_rng)
    return np.array(means), pop


def test_actual_and_identity_continuations_are_exactly_paired():
    params = tiny_params()
    init_rng = make_generator(99, "identity-test-initial")
    pop = init_population(params["n_cells"], params["n_seqs"], params["seq_len"], init_rng)
    stream_a = ContinuationStream(20260731, "baseline-0", 0)
    stream_b = ContinuationStream(20260731, "baseline-0", 0)
    a = simulate_continuation(pop, params["motif_affinity_matrix"], params, stream_a)
    b = simulate_continuation(pop, params["motif_affinity_matrix"].copy(), params, stream_b)
    assert np.array_equal(a[0], b[0])
    assert np.array_equal(a[1], b[1])


def test_continuation_index_changes_stream():
    a = ContinuationStream(1, "r", 0).observation_generator().random(5)
    b = ContinuationStream(1, "r", 1).observation_generator().random(5)
    assert not np.array_equal(a, b)


def test_analysis_purposes_are_separated():
    a = AnalysisStream(5, "bootstrap", "x").generator().random(5)
    b = AnalysisStream(5, "replicate-permutation", "x").generator().random(5)
    assert not np.array_equal(a, b)


def test_stable_generator_reconstructs():
    a = make_generator(2, "purpose", "a", 1).integers(0, 100, 10)
    b = make_generator(2, "purpose", "a", 1).integers(0, 100, 10)
    assert np.array_equal(a, b)


def test_public_paired_horizon_runner_recovers_identity():
    from modelb_semantic_repo.interventions import simulate_horizon_with_stream

    params = tiny_params()
    pop = init_population(
        params["n_cells"], params["n_seqs"], params["seq_len"], make_generator(12, "paired-runner-init")
    )
    stream = ContinuationStream(901, "baseline-public", 2)
    actual = simulate_horizon_with_stream(pop, params["motif_affinity_matrix"], params, 0.8, 3, stream)
    identity = simulate_horizon_with_stream(pop, params["motif_affinity_matrix"].copy(), params, 0.8, 3, stream)
    assert np.array_equal(actual["mean_fitness"], identity["mean_fitness"])
    assert np.array_equal(actual["final_population"], identity["final_population"])


def test_vectorized_reproduction_extreme_parent_and_environment_cases():
    from modelb_semantic_repo.original_model.simulation import reproduce_with_partitioning
    pop = np.zeros((3, 2, 6), dtype=np.int8)
    pop[0, 0] = 1
    pop[0, 1] = 2
    pop[1] = 3
    fitness = np.array([1.0, 0.0, 0.0])
    inherited = reproduce_with_partitioning(pop, fitness, 0.0, 1.0, np.random.default_rng(44))
    assert set(np.unique(inherited)).issubset({1, 2})
    environmental = reproduce_with_partitioning(pop, fitness, 0.0, 0.0, np.random.default_rng(44))
    assert environmental.shape == pop.shape
    assert environmental.min() >= 0 and environmental.max() <= 3
