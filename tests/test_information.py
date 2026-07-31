import numpy as np
import pytest

from modelb_semantic_repo.information import (
    InformationMeasureRecord,
    canonicalize_grouping,
    conditional_mutual_information,
    constant_grouping,
    corrected_conditional_mutual_information,
    corrected_retained_information,
    grouping_hash,
    identity_grouping,
    mutual_information,
    positional_information,
    retained_information,
)
from modelb_semantic_repo.rng import PermutationStream


def test_mutual_information_perfect_binary_is_one_bit():
    x = np.array([0, 0, 1, 1])
    y = np.array([0, 0, 1, 1])
    assert mutual_information(x, y) == pytest.approx(1.0)


def test_mutual_information_independent_balanced_is_zero():
    x = np.array([0, 0, 1, 1])
    y = np.array([0, 1, 0, 1])
    assert mutual_information(x, y) == pytest.approx(0.0)


def test_conditional_mi_is_segment_weighted():
    motif = np.array([0, 0, 1, 1, 0, 0, 1, 1])
    state = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    segment = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    value, components = conditional_mutual_information(motif, state, segment, return_components=True)
    assert value == pytest.approx(0.5)
    assert sum(c["weighted_contribution"] for c in components) == pytest.approx(value)
    assert [c["n_observations"] for c in components] == [4, 4]


def test_positional_confounding_removed_by_conditioning():
    motif = np.repeat([0, 1], 100)
    segment = motif.copy()
    state = segment.copy()
    assert mutual_information(motif, state) == pytest.approx(1.0)
    assert positional_information(motif, segment) == pytest.approx(1.0)
    assert conditional_mutual_information(motif, state, segment) == pytest.approx(0.0)


def test_constant_group_retains_zero_information():
    motif = np.tile(np.arange(4), 20)
    state = motif % 2
    segment = np.tile([0, 1], 40)
    assert retained_information(motif, state, segment, constant_grouping(4)) == pytest.approx(0.0)


def test_identity_group_recovers_conditional_information():
    motif = np.tile(np.arange(4), 20)
    state = motif % 2
    segment = np.tile([0, 1], 40)
    baseline = conditional_mutual_information(motif, state, segment)
    retained = retained_information(motif, state, segment, identity_grouping(4))
    assert retained == pytest.approx(baseline)


def test_group_label_renaming_has_same_hash():
    a = np.array([0, 0, 1, 1, 2])
    b = np.array([9, 9, 4, 4, 7])
    assert grouping_hash(a) == grouping_hash(b)
    assert np.array_equal(canonicalize_grouping(a), canonicalize_grouping(b))


def test_duplicate_partitions_return_same_retained_information():
    motif = np.tile(np.arange(5), 30)
    state = motif % 3
    segment = np.tile(np.arange(3), 50)
    a = np.array([0, 0, 1, 1, 2])
    b = np.array([8, 8, 4, 4, 9])
    assert retained_information(motif, state, segment, a) == pytest.approx(
        retained_information(motif, state, segment, b)
    )


def test_mapping_object_supported():
    motif = np.array([0, 1, 2, 3] * 10)
    state = motif % 2
    segment = np.array([0, 0, 1, 1] * 10)
    grouping = {0: "a", 1: "a", 2: "b", 3: "b"}
    assert retained_information(motif, state, segment, grouping) >= 0


def test_permutation_stream_reproduces_exactly():
    rng = np.random.default_rng(22)
    motif = rng.integers(0, 20, 300)
    state = rng.integers(0, 4, 300)
    segment = rng.integers(0, 3, 300)
    stream = PermutationStream(77, "rep-A", 2)
    a = corrected_conditional_mutual_information(motif, state, segment, n_permutations=20, stream=stream)
    b = corrected_conditional_mutual_information(motif, state, segment, n_permutations=20, stream=stream)
    assert a == b


def test_different_permutation_streams_diverge():
    rng = np.random.default_rng(22)
    motif = rng.integers(0, 20, 300)
    state = rng.integers(0, 4, 300)
    segment = rng.integers(0, 3, 300)
    a = corrected_conditional_mutual_information(
        motif, state, segment, n_permutations=20, stream=PermutationStream(77, "rep-A", 2)
    )
    b = corrected_conditional_mutual_information(
        motif, state, segment, n_permutations=20, stream=PermutationStream(77, "rep-A", 3)
    )
    assert a.permutation_mean != b.permutation_mean


def test_finite_sample_bias_is_corrected_toward_zero():
    rng = np.random.default_rng(123)
    motif = rng.integers(0, 80, 240)
    state = rng.integers(0, 4, 240)
    segment = rng.integers(0, 4, 240)
    result = corrected_conditional_mutual_information(
        motif, state, segment, n_permutations=100, stream=PermutationStream(1001, "independent", 0)
    )
    assert abs(result.corrected) < result.observed


def test_corrected_retained_information_uses_grouped_motifs():
    rng = np.random.default_rng(4)
    motif = rng.integers(0, 8, 200)
    state = motif % 2
    segment = rng.integers(0, 2, 200)
    grouping = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    result = corrected_retained_information(
        motif, state, segment, grouping, n_permutations=20, stream=PermutationStream(55, "r", 0)
    )
    assert result.observed >= 0
    assert result.n_permutations == 20


def test_information_record_schema_serializes():
    record = InformationMeasureRecord(
        baseline_replicate="r1",
        observation_seed=1,
        map_hash="abc",
        permutation_root_seed=2,
        permutation_stream_index=3,
        total_information=0.2,
        positional_information=0.1,
        conditional_information=0.15,
        corrected_conditional_information=0.12,
        retained_information=0.08,
        corrected_retained_information=0.06,
    )
    assert record.to_dict()["baseline_replicate"] == "r1"


def test_empty_vectors_rejected():
    with pytest.raises(ValueError):
        mutual_information([], [])


def test_mismatched_lengths_rejected():
    with pytest.raises(ValueError):
        conditional_mutual_information([0, 1], [0], [0, 1])
