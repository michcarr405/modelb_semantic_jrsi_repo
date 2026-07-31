import numpy as np

from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.original_model.simulation import reproduce_with_partitioning
from modelb_semantic_repo.phase5 import (
    categorical_hamming,
    complete_profile_derangement,
    enumerate_matched_topologies,
    generate_topology_schedule,
    reproduce_with_selection_strength,
    selection_probabilities,
    select_alternative_topologies,
)


def test_selection_mixture_endpoints():
    fitness = np.array([1.0, 2.0, 7.0])
    neutral = selection_probabilities(fitness, 0.0)
    full = selection_probabilities(fitness, 1.0)
    reduced = selection_probabilities(fitness, 0.25)
    assert np.allclose(neutral, np.full(3, 1 / 3))
    assert np.allclose(full, fitness / fitness.sum())
    assert np.allclose(reduced, 0.75 * np.full(3, 1 / 3) + 0.25 * fitness / fitness.sum())


def test_full_selection_reproduction_matches_phase4_law():
    rng_pop = np.random.default_rng(11)
    pop = rng_pop.integers(0, 4, size=(8, 3, 12), dtype=np.int8)
    fitness = np.linspace(0.5, 4.0, 8)
    rng_a = np.random.default_rng(991)
    rng_b = np.random.default_rng(991)
    expected = reproduce_with_partitioning(pop, fitness, 0.01, 0.8, rng_a)
    observed = reproduce_with_selection_strength(pop, fitness, 0.01, 0.8, rng_b, 1.0)
    assert np.array_equal(expected, observed)


def test_topology_universe_preserves_counts_and_selects_distant_alternatives():
    topologies = enumerate_matched_topologies()
    assert len(topologies) == 30
    assert len({t.topology_hash for t in topologies}) == 30
    assert sum(t.is_native for t in topologies) == 1
    for topology in topologies:
        assert int(topology.productive_pairs.sum()) == 8
        assert int(topology.anti_pairs.sum()) == 6
        assert np.array_equal(topology.productive_pairs, topology.productive_pairs.T)
        assert np.array_equal(topology.anti_pairs, topology.anti_pairs.T)
        assert not np.any(topology.productive_pairs & topology.anti_pairs)
    native, a, b = select_alternative_topologies(topologies)
    max_native = max(categorical_hamming(t, native) for t in topologies if not t.is_native)
    assert categorical_hamming(a, native) == max_native
    assert a.topology_id != b.topology_id
    assert not a.is_native and not b.is_native


def test_complete_profile_derangement_has_no_fixed_points_and_is_permutation():
    permutation = complete_profile_derangement(1024, np.random.default_rng(1234))
    assert np.array_equal(np.sort(permutation), np.arange(1024))
    assert not np.any(permutation == np.arange(1024))


def test_unstable_schedule_has_no_immediate_repeats_and_is_reproducible():
    topologies = enumerate_matched_topologies()
    a = generate_topology_schedule(topologies, root_seed=5, purpose="test", keys=("x",), length=200)
    b = generate_topology_schedule(topologies, root_seed=5, purpose="test", keys=("x",), length=200)
    c = generate_topology_schedule(topologies, root_seed=5, purpose="test", keys=("y",), length=200)
    assert a == b
    assert a != c
    assert all(x != y for x, y in zip(a[:-1], a[1:]))
