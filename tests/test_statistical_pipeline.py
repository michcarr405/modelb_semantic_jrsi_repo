import numpy as np
import pandas as pd
import pytest

from modelb_semantic_repo.rng import AnalysisStream
from modelb_semantic_repo.statistical_pipeline import (
    TargetRule,
    aggregate_nested_continuations,
    analyze_replicate_frontiers,
    block_bootstrap,
    construct_monotone_frontier,
    continuation_variance_diagnostic,
    detect_target,
    paired_endpoint_diagnostic,
    replicate_level_permutation_test,
    target_reach_table,
    validate_continuation_table,
)


def test_one_frontier_per_independent_replicate(synthetic_continuations):
    result = analyze_replicate_frontiers(synthetic_continuations, target_rule=TargetRule(0.1))
    assert len(result.replicate_summary) == 10
    assert result.frontier_points.groupby(["condition", "baseline_replicate"]).ngroups == 10


def test_continuations_are_aggregated_within_maps(synthetic_continuations):
    maps = aggregate_nested_continuations(synthetic_continuations)
    assert maps["n_continuations"].eq(4).all()
    assert len(maps) == 10 * 6  # actual plus five intervention maps per replicate


def test_independent_n_not_equal_to_continuation_rows(synthetic_continuations):
    result = analyze_replicate_frontiers(synthetic_continuations, target_rule=TargetRule(0.1))
    assert result.replicate_summary["n_continuation_rows"].eq(24).all()
    assert len(result.replicate_summary) == 10


def test_identity_endpoint_recovers_information_and_viability(synthetic_continuations):
    result = analyze_replicate_frontiers(synthetic_continuations, target_rule=TargetRule(0.1))
    assert result.replicate_summary["identity_information_recovered"].all()
    assert result.replicate_summary["identity_viability_recovered"].all()


def test_paired_endpoint_diagnostic_is_exact(synthetic_continuations):
    diagnostic = paired_endpoint_diagnostic(synthetic_continuations, atol=0.0)
    assert diagnostic["endpoint_recovered"].all()
    assert diagnostic["max_abs_viability_difference"].eq(0).all()


def test_selective_target_detected_at_half_bit(synthetic_continuations):
    result = analyze_replicate_frontiers(synthetic_continuations, target_rule=TargetRule(0.1))
    selective = result.replicate_summary[result.replicate_summary["condition"] == "selective"]
    assert selective["semantic_information"].eq(0.5).all()
    assert selective["target_reached"].all()


def test_control_target_detected_only_at_identity(synthetic_continuations):
    result = analyze_replicate_frontiers(synthetic_continuations, target_rule=TargetRule(0.1))
    control = result.replicate_summary[result.replicate_summary["condition"] == "control"]
    assert control["semantic_information"].eq(1.0).all()


def test_target_not_reached_is_right_censored_not_point_estimate(synthetic_continuations):
    truncated = synthetic_continuations[
        ~((synthetic_continuations["baseline_replicate"] == "control_r0") & (synthetic_continuations["endpoint_type"] == "identity"))
    ]
    result = analyze_replicate_frontiers(truncated, target_rule=TargetRule(0.1), require_identity=False)
    row = result.replicate_summary[result.replicate_summary["baseline_replicate"] == "control_r0"].iloc[0]
    assert not row["target_reached"]
    assert row["censoring"] == "right_censored"
    assert np.isnan(row["semantic_information"])
    assert row["semantic_lower_bound"] == pytest.approx(0.75)


def test_missing_identity_rejected_when_required(synthetic_continuations):
    truncated = synthetic_continuations[
        ~((synthetic_continuations["baseline_replicate"] == "control_r0") & (synthetic_continuations["endpoint_type"] == "identity"))
    ]
    with pytest.raises(ValueError, match="identity endpoint"):
        analyze_replicate_frontiers(truncated, target_rule=TargetRule(0.1), require_identity=True)


def test_identity_viability_mismatch_rejected(synthetic_continuations):
    bad = synthetic_continuations.copy()
    mask = (bad["baseline_replicate"] == "selective_r0") & (bad["endpoint_type"] == "identity")
    bad.loc[mask, "viability"] += 0.01
    with pytest.raises(ValueError, match="paired actual viability"):
        analyze_replicate_frontiers(bad, target_rule=TargetRule(0.1), viability_atol=0.0)


def test_identity_information_mismatch_rejected(synthetic_continuations):
    bad = synthetic_continuations.copy()
    mask = (bad["baseline_replicate"] == "selective_r0") & (bad["endpoint_type"] == "identity")
    bad.loc[mask, "retained_information"] = 0.99
    with pytest.raises(ValueError, match="baseline information"):
        analyze_replicate_frontiers(bad, target_rule=TargetRule(0.1))


def test_duplicate_map_alias_is_collapsed(synthetic_continuations):
    duplicate = synthetic_continuations[
        (synthetic_continuations["baseline_replicate"] == "selective_r0")
        & (synthetic_continuations["map_hash"] == "mid050")
    ].copy()
    duplicate["method"] = "alias_method"
    raw = pd.concat([synthetic_continuations, duplicate], ignore_index=True)
    validated = validate_continuation_table(raw)
    expected = len(synthetic_continuations)
    assert len(validated) == expected
    method = validated[(validated["baseline_replicate"] == "selective_r0") & (validated["map_hash"] == "mid050")]["method"].iloc[0]
    assert "alias_method" in method


def test_conflicting_duplicate_map_rejected(synthetic_continuations):
    duplicate = synthetic_continuations.iloc[[0]].copy()
    duplicate["viability"] += 1
    raw = pd.concat([synthetic_continuations, duplicate], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate viability"):
        validate_continuation_table(raw)


def test_monotone_frontier_is_cumulative_upper_envelope():
    maps = pd.DataFrame(
        {
            "condition": ["x"] * 4,
            "baseline_replicate": ["r"] * 4,
            "map_hash": ["c", "a", "b", "i"],
            "method": ["m"] * 4,
            "endpoint_type": ["constant", "intermediate", "intermediate", "identity"],
            "retained_information": [0.0, 0.3, 0.6, 1.0],
            "viability_mean": [1.0, 3.0, 2.0, 4.0],
            "n_continuations": [2] * 4,
        }
    )
    frontier = construct_monotone_frontier(maps)
    assert frontier["frontier_viability"].tolist() == [1.0, 3.0, 3.0, 4.0]


def test_target_detection_uses_discrete_tested_coordinate():
    frontier = pd.DataFrame(
        {
            "retained_information": [0.0, 0.5, 1.0],
            "frontier_viability": [0.0, 0.8, 1.0],
        }
    )
    detected = detect_target(frontier, 0.9)
    assert detected["semantic_information"] == 1.0


def test_target_reach_table_counts_censoring(synthetic_continuations):
    truncated = synthetic_continuations[
        ~((synthetic_continuations["baseline_replicate"] == "control_r0") & (synthetic_continuations["endpoint_type"] == "identity"))
    ]
    summary = analyze_replicate_frontiers(truncated, target_rule=TargetRule(0.1), require_identity=False).replicate_summary
    table = target_reach_table(summary)
    control = table[table["condition"] == "control"].iloc[0]
    assert control["n_independent_replicates"] == 5
    assert control["n_target_reached"] == 4
    assert control["n_right_censored"] == 1


def test_continuation_variance_diagnostic_tracks_seed_count(synthetic_continuations):
    diagnostic = continuation_variance_diagnostic(synthetic_continuations, absolute_tolerance=0.05)
    assert diagnostic["n_continuations"].tolist() == [1, 2, 3, 4]
    assert diagnostic.iloc[-1]["rmse_vs_full_mean"] == pytest.approx(0.0)
    assert diagnostic.iloc[-1]["fraction_within_absolute_tolerance"] == pytest.approx(1.0)


def test_block_bootstrap_reproducible(synthetic_continuations):
    kwargs = dict(
        target_rule=TargetRule(0.1),
        n_bootstrap=40,
        confidence_level=0.9,
        stream=AnalysisStream(123, "block-bootstrap", "test"),
    )
    a = block_bootstrap(synthetic_continuations, **kwargs)
    b = block_bootstrap(synthetic_continuations, **kwargs)
    pd.testing.assert_frame_equal(a[0], b[0])
    pd.testing.assert_frame_equal(a[1], b[1])


def test_block_bootstrap_preserves_condition_sample_sizes(synthetic_continuations):
    intervals, draws = block_bootstrap(
        synthetic_continuations,
        target_rule=TargetRule(0.1),
        n_bootstrap=20,
        stream=AnalysisStream(1, "block-bootstrap", "sizes"),
    )
    counts = draws.groupby(["bootstrap_index", "condition"])[["n_reached", "n_censored"]].first().sum(axis=1)
    assert counts.eq(5).all()
    assert intervals["n_independent_replicates"].eq(5).all()


def test_bootstrap_semantic_interval_is_conditional_on_reached(synthetic_continuations):
    intervals, _ = block_bootstrap(
        synthetic_continuations,
        target_rule=TargetRule(0.1),
        n_bootstrap=20,
        stream=AnalysisStream(2, "block-bootstrap", "notes"),
    )
    row = intervals[intervals["metric"] == "median_semantic_information_among_reached"].iloc[0]
    assert "censored values are not imputed" in row["note"]


def test_replicate_level_permutation_detects_known_difference(synthetic_continuations):
    summary = analyze_replicate_frontiers(synthetic_continuations, target_rule=TargetRule(0.1)).replicate_summary
    result = replicate_level_permutation_test(
        summary,
        metric="semantic_information",
        group_a="selective",
        group_b="control",
        stream=AnalysisStream(9, "replicate-permutation", "semantic"),
    )
    assert result.observed_difference == pytest.approx(-0.5)
    assert result.exact
    assert result.n_group_a == 5 and result.n_group_b == 5


def test_permutation_rejects_duplicate_replicate_rows(synthetic_continuations):
    summary = analyze_replicate_frontiers(synthetic_continuations, target_rule=TargetRule(0.1)).replicate_summary
    bad = pd.concat([summary, summary.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate baseline blocks"):
        replicate_level_permutation_test(
            bad,
            metric="value_of_information",
            group_a="selective",
            group_b="control",
            stream=AnalysisStream(9, "replicate-permutation", "dup"),
        )


def test_permutation_refuses_censored_semantic_values(synthetic_continuations):
    truncated = synthetic_continuations[
        ~((synthetic_continuations["baseline_replicate"] == "control_r0") & (synthetic_continuations["endpoint_type"] == "identity"))
    ]
    summary = analyze_replicate_frontiers(truncated, target_rule=TargetRule(0.1), require_identity=False).replicate_summary
    with pytest.raises(ValueError, match="censored/missing"):
        replicate_level_permutation_test(
            summary,
            metric="semantic_information",
            group_a="selective",
            group_b="control",
            stream=AnalysisStream(9, "replicate-permutation", "censored"),
        )


def test_permutation_can_test_target_reach_indicator(synthetic_continuations):
    truncated = synthetic_continuations[
        ~((synthetic_continuations["baseline_replicate"] == "control_r0") & (synthetic_continuations["endpoint_type"] == "identity"))
    ]
    summary = analyze_replicate_frontiers(truncated, target_rule=TargetRule(0.1), require_identity=False).replicate_summary
    result = replicate_level_permutation_test(
        summary,
        metric="target_reached",
        group_a="selective",
        group_b="control",
        stream=AnalysisStream(9, "replicate-permutation", "reach"),
    )
    assert result.observed_difference == pytest.approx(0.2)


def test_paired_replicate_permutation_uses_sign_flips():
    summary = pd.DataFrame(
        {
            "condition": ["a", "b", "a", "b", "a", "b"],
            "baseline_replicate": ["a0", "b0", "a1", "b1", "a2", "b2"],
            "pair_id": [0, 0, 1, 1, 2, 2],
            "metric": [3.0, 1.0, 4.0, 2.0, 5.0, 3.0],
        }
    )
    result = replicate_level_permutation_test(
        summary,
        metric="metric",
        group_a="a",
        group_b="b",
        paired_by="pair_id",
        stream=AnalysisStream(11, "replicate-permutation", "paired"),
    )
    assert result.paired and result.exact
    assert result.observed_difference == pytest.approx(2.0)


def test_target_rule_rejects_negative_tolerance():
    with pytest.raises(ValueError):
        TargetRule(-0.1)


def test_block_bootstrap_preserves_censored_cases_without_imputation(synthetic_continuations):
    truncated = synthetic_continuations[
        ~((synthetic_continuations["baseline_replicate"] == "control_r0") & (synthetic_continuations["endpoint_type"] == "identity"))
    ]
    intervals, draws = block_bootstrap(
        truncated,
        target_rule=TargetRule(0.1),
        n_bootstrap=30,
        stream=AnalysisStream(5, "block-bootstrap", "censored"),
        require_identity=False,
    )
    control_reach = intervals[(intervals["condition"] == "control") & (intervals["metric"] == "reach_fraction")].iloc[0]
    assert control_reach["estimate"] == pytest.approx(0.8)
    censored_metric = intervals[(intervals["condition"] == "control") & (intervals["metric"] == "median_censored_lower_bound")].iloc[0]
    assert censored_metric["estimate"] == pytest.approx(0.75)
    assert (draws.loc[draws["condition"] == "control", "n_censored"] > 0).any()
