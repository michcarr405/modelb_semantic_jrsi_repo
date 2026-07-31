#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import tempfile

import numpy as np
import pandas as pd

from modelb_semantic_repo.phase4 import (
    Phase4Settings,
    _baseline_job,
    _intervention_job,
)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    results = root / "results" / "phase4_core"
    outdir = root / "validation" / "phase4"
    outdir.mkdir(parents=True, exist_ok=True)

    settings = Phase4Settings(**json.loads((results / "phase4_settings.json").read_text()))
    baseline = pd.read_csv(results / "baseline_information.csv")
    raw = pd.read_csv(results / "continuation_level_results.csv")
    replicate = pd.read_csv(results / "replicate_frontier_summary.csv")
    manifest = pd.read_csv(results / "maps" / "grouping_map_manifest.csv")
    gate = json.loads((results / "GATE_4_DECISION.json").read_text())

    expected_blocks = 2 * 10 * settings.n_baseline_replicates
    expected_rows_per_block = (len(manifest) + 1) * settings.continuation_count
    block_sizes = raw.groupby("baseline_replicate").size()

    actual = raw[raw["endpoint_type"] == "actual"][
        ["baseline_replicate", "continuation_index", "viability", "mean_fitness_trajectory_json", "final_population_hash"]
    ].rename(
        columns={
            "viability": "actual_viability",
            "mean_fitness_trajectory_json": "actual_trajectory",
            "final_population_hash": "actual_final_hash",
        }
    )
    identity = raw[raw["endpoint_type"] == "identity"][
        ["baseline_replicate", "continuation_index", "viability", "mean_fitness_trajectory_json", "final_population_hash"]
    ].rename(
        columns={
            "viability": "identity_viability",
            "mean_fitness_trajectory_json": "identity_trajectory",
            "final_population_hash": "identity_final_hash",
        }
    )
    paired = actual.merge(identity, on=["baseline_replicate", "continuation_index"], validate="one_to_one")
    paired["viability_exact"] = paired["actual_viability"] == paired["identity_viability"]
    paired["trajectory_exact"] = paired["actual_trajectory"] == paired["identity_trajectory"]
    paired["final_population_exact"] = paired["actual_final_hash"] == paired["identity_final_hash"]
    paired.to_csv(outdir / "actual_identity_full_trajectory_check.csv", index=False)

    chosen = baseline[(baseline["condition"] == "selective") & np.isclose(baseline["inherit_prob"], 1.0) & (baseline["replicate"] == 0)].iloc[0]
    with tempfile.TemporaryDirectory(prefix="phase4_baseline_rerun_") as temp:
        rerun = _baseline_job(
            {
                "condition": str(chosen["condition"]),
                "inherit_prob": float(chosen["inherit_prob"]),
                "replicate": int(chosen["replicate"]),
                "root_seed": settings.root_seed,
                "n_information_permutations": settings.n_information_permutations,
                "state_dir": temp,
            }
        )
    baseline_checks = {
        "baseline_replicate": chosen["baseline_replicate"],
        "state_hash_equal": rerun["state_hash"] == chosen["state_hash"],
        "trajectory_hash_equal": rerun["trajectory_hash"] == chosen["trajectory_hash"],
        "corrected_information_equal": bool(np.isclose(rerun["corrected_conditional_information"], chosen["corrected_conditional_information"], rtol=0, atol=1e-15)),
        "conditional_information_equal": bool(np.isclose(rerun["conditional_information"], chosen["conditional_information"], rtol=0, atol=1e-15)),
        "final_mean_fitness_equal": bool(np.isclose(rerun["final_mean_fitness"], chosen["final_mean_fitness"], rtol=0, atol=1e-15)),
    }
    pd.DataFrame([baseline_checks]).to_csv(outdir / "deterministic_baseline_rerun.csv", index=False)

    with tempfile.TemporaryDirectory(prefix="phase4_intervention_rerun_") as temp:
        path = _intervention_job(
            {
                "base": chosen.to_dict(),
                "settings": settings.to_dict(),
                "map_dir": str(results / "maps"),
                "block_dir": temp,
            }
        )
        rerun_block = pd.read_csv(path)
    original_block = raw[raw["baseline_replicate"] == chosen["baseline_replicate"]].copy()
    sort_cols = ["map_id", "continuation_index"]
    original_block = original_block.sort_values(sort_cols).reset_index(drop=True)
    rerun_block = rerun_block.sort_values(sort_cols).reset_index(drop=True)
    numeric_cols = ["retained_information", "baseline_information", "viability"]
    string_cols = ["map_hash", "method", "endpoint_type", "mean_fitness_trajectory_json", "final_population_hash", "continuation_stream_key"]
    intervention_checks = {
        "baseline_replicate": chosen["baseline_replicate"],
        "row_count_equal": len(original_block) == len(rerun_block),
        "numeric_values_equal": bool(np.allclose(original_block[numeric_cols], rerun_block[numeric_cols], rtol=0, atol=1e-14)),
        "string_values_equal": bool((original_block[string_cols].astype(str).to_numpy() == rerun_block[string_cols].astype(str).to_numpy()).all()),
    }
    pd.DataFrame([intervention_checks]).to_csv(outdir / "deterministic_intervention_rerun.csv", index=False)

    summary = {
        "gate4_status": gate["status"],
        "n_baseline_blocks": int(len(baseline)),
        "expected_baseline_blocks": int(expected_blocks),
        "n_continuation_rows": int(len(raw)),
        "expected_rows_per_block": int(expected_rows_per_block),
        "all_block_sizes_correct": bool((block_sizes == expected_rows_per_block).all()),
        "n_unique_maps": int(len(manifest)),
        "map_hashes_unique": bool(manifest["map_hash"].is_unique),
        "all_identity_information_recovered": bool(replicate["identity_information_recovered"].all()),
        "all_identity_viability_recovered": bool(replicate["identity_viability_recovered"].all()),
        "all_actual_identity_viabilities_exact": bool(paired["viability_exact"].all()),
        "all_actual_identity_trajectories_exact": bool(paired["trajectory_exact"].all()),
        "all_actual_identity_final_populations_exact": bool(paired["final_population_exact"].all()),
        "n_right_censored": int((~replicate["target_reached"].astype(bool)).sum()),
        "baseline_deterministic_rerun": baseline_checks,
        "intervention_deterministic_rerun": intervention_checks,
        "production_figures_generated": False,
        "manuscript_rewritten": False,
        "causal_controls_run": False,
        "broad_parameter_sweeps_run": False,
    }
    (outdir / "phase4_validation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
