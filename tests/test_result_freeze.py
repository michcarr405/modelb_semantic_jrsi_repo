from pathlib import Path

import pandas as pd

from modelb_semantic_repo.result_freeze import _category, build_result_inventory


def test_result_category_classification():
    assert _category("continuation_blocks/selective_p1.0_r00.csv") == "continuation_record"
    assert _category("GATE_7_DECISION.json") == "gate_decision"
    assert _category("states/selective/rep_00.npz") == "archived_state_or_array"


def test_inventory_covers_phase_manifests():
    root = Path(__file__).resolve().parents[1]
    inventory = build_result_inventory(root)
    assert set(inventory["phase"]) == {"phase4", "phase5", "phase6"}
    for phase, part in inventory.groupby("phase"):
        self_rows = part[part["relative_path"] == "FILE_MANIFEST_SHA256.csv"]
        assert len(self_rows) == 1
        nonself = part[part["relative_path"] != "FILE_MANIFEST_SHA256.csv"]
        assert nonself["exists"].all()
        assert nonself["in_manifest"].all()
        assert nonself["size_matches"].all()
        assert nonself["hash_matches"].all()
