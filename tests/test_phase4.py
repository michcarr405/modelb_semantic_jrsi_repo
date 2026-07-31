import numpy as np
from modelb_semantic_repo.phase4 import (
    build_phase4_map_panel,
    contiguous_substring_grouping,
)
from modelb_semantic_repo.information import grouping_hash


def test_contiguous_substring_group_counts_and_orientation():
    left = contiguous_substring_grouping(start=0, length=2)
    right = contiguous_substring_grouping(start=3, length=2)
    middle = contiguous_substring_grouping(start=1, length=3)
    assert len(np.unique(left)) == 16
    assert len(np.unique(right)) == 16
    assert len(np.unique(middle)) == 64
    assert grouping_hash(left) != grouping_hash(right)


def test_phase4_map_panel_is_unique_and_has_expected_coverage():
    panel = build_phase4_map_panel()
    assert len(panel) == 34
    assert len({x["map_hash"] for x in panel}) == 34
    assert sum(x["method"] == "contiguous_substring" for x in panel) == 14
    assert sum(x["endpoint_type"] == "constant" for x in panel) == 1
    assert sum(x["endpoint_type"] == "identity" for x in panel) == 1
    assert all(x["method"] != "kmeans_profile" for x in panel)


def test_fast_block_bootstrap_preserves_independent_block_counts_and_censoring():
    import pandas as pd
    from modelb_semantic_repo.phase4 import fast_block_bootstrap_from_replicate_summary
    from modelb_semantic_repo.rng import AnalysisStream
    rows = []
    for condition in ("selective", "control"):
        for i in range(4):
            reached = not (condition == "control" and i == 0)
            rows.append({
                "condition": condition,
                "baseline_replicate": f"{condition}_{i}",
                "target_reached": reached,
                "semantic_information": 0.5 if reached else np.nan,
                "semantic_lower_bound": np.nan if reached else 0.8,
                "value_of_information": 1.0 if condition == "selective" else 0.0,
            })
    intervals, draws = fast_block_bootstrap_from_replicate_summary(
        pd.DataFrame(rows), n_bootstrap=20, stream=AnalysisStream(4, "test-fast-bootstrap")
    )
    assert set(intervals["n_independent_replicates"]) == {4}
    assert len(draws) == 40
    control_reach = intervals[(intervals.condition == "control") & (intervals.metric == "reach_fraction")]
    assert float(control_reach.estimate.iloc[0]) == 0.75
