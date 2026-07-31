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
