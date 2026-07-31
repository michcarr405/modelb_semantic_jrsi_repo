#!/usr/bin/env python3
"""Phase 3 validation using synthetic data and a tiny identity-endpoint run only."""
from __future__ import annotations

import json
from pathlib import Path
import platform

import numpy as np
import pandas as pd

from modelb_semantic_repo.interventions import simulate_horizon_with_stream
from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.original_model.simulation import init_population
from modelb_semantic_repo.rng import AnalysisStream, ContinuationStream, make_generator
from modelb_semantic_repo.statistical_pipeline import (
    TargetRule,
    analyze_replicate_frontiers,
    block_bootstrap,
    continuation_variance_diagnostic,
    paired_endpoint_diagnostic,
    replicate_level_permutation_test,
    target_reach_table,
)


def synthetic_continuations(n_replicates: int = 6) -> pd.DataFrame:
    rows = []
    continuation_noise = np.array([-0.12, 0.04, 0.09, -0.01])
    for condition in ["selective", "control"]:
        for rep in range(n_replicates):
            baseline = f"{condition}_r{rep}"
            actual_base = 10.0 + 0.1 * rep
            if condition == "selective":
                values = {
                    "constant": (0.0, 6.0 + 0.1 * rep),
                    "mid025": (0.25, 7.4 + 0.1 * rep),
                    "mid050": (0.50, 9.75 + 0.1 * rep),
                    "mid075": (0.75, 9.85 + 0.1 * rep),
                    "identity": (1.0, actual_base),
                }
            else:
                values = {
                    "constant": (0.0, 9.0 + 0.1 * rep),
                    "mid025": (0.25, 9.15 + 0.1 * rep),
                    "mid050": (0.50, 9.35 + 0.1 * rep),
                    "mid075": (0.75, 9.60 + 0.1 * rep),
                    "identity": (1.0, actual_base),
                }
            for continuation_index, noise in enumerate(continuation_noise):
                rows.append(
                    {
                        "condition": condition,
                        "baseline_replicate": baseline,
                        "map_hash": "actual",
                        "method": "unintervened",
                        "endpoint_type": "actual",
                        "retained_information": 1.0,
                        "baseline_information": 1.0,
                        "continuation_index": continuation_index,
                        "viability": actual_base + noise,
                    }
                )
                for map_hash, (information, base) in values.items():
                    endpoint = map_hash if map_hash in {"constant", "identity"} else "intermediate"
                    rows.append(
                        {
                            "condition": condition,
                            "baseline_replicate": baseline,
                            "map_hash": map_hash,
                            "method": "endpoint" if endpoint != "intermediate" else "synthetic_family",
                            "endpoint_type": endpoint,
                            "retained_information": information,
                            "baseline_information": 1.0,
                            "continuation_index": continuation_index,
                            "viability": base + noise,
                        }
                    )
    return pd.DataFrame(rows)


def tiny_identity_diagnostic() -> dict:
    params = default_parameters()
    params["n_cells"] = 5
    params["n_seqs"] = 2
    params["seq_len"] = 12
    pop = init_population(
        params["n_cells"],
        params["n_seqs"],
        params["seq_len"],
        make_generator(20260731, "phase3-identity-initialization"),
    )
    stream = ContinuationStream(20260731, "tiny-baseline", 0)
    actual = simulate_horizon_with_stream(
        pop, params["motif_affinity_matrix"], params, 0.8, 4, stream
    )
    identity = simulate_horizon_with_stream(
        pop, params["motif_affinity_matrix"].copy(), params, 0.8, 4, stream
    )
    return {
        "mean_fitness_equal": bool(np.array_equal(actual["mean_fitness"], identity["mean_fitness"])),
        "final_population_equal": bool(np.array_equal(actual["final_population"], identity["final_population"])),
        "max_abs_mean_fitness_difference": float(
            np.max(np.abs(actual["mean_fitness"] - identity["mean_fitness"]))
        ),
        "horizon": 4,
        "n_cells": params["n_cells"],
        "n_seqs": params["n_seqs"],
        "seq_len": params["seq_len"],
        "production_run": False,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    outdir = root / "validation" / "phase3"
    outdir.mkdir(parents=True, exist_ok=True)

    raw = synthetic_continuations()
    rule = TargetRule(0.1)  # synthetic validation value only; P04 remains unresolved.
    analysis = analyze_replicate_frontiers(raw, target_rule=rule)
    paired = paired_endpoint_diagnostic(raw, atol=0.0)
    reach = target_reach_table(analysis.replicate_summary)
    variance = continuation_variance_diagnostic(raw, absolute_tolerance=0.05)
    intervals, draws = block_bootstrap(
        raw,
        target_rule=rule,
        n_bootstrap=80,
        stream=AnalysisStream(20260731, "block-bootstrap", "phase3-validation"),
        confidence_level=0.95,
    )
    perm_semantic = replicate_level_permutation_test(
        analysis.replicate_summary,
        metric="semantic_information",
        group_a="selective",
        group_b="control",
        stream=AnalysisStream(20260731, "replicate-permutation", "semantic-information"),
    )
    perm_value = replicate_level_permutation_test(
        analysis.replicate_summary,
        metric="value_of_information",
        group_a="selective",
        group_b="control",
        stream=AnalysisStream(20260731, "replicate-permutation", "value-of-information"),
    )

    # Explicit target-not-reached diagnostic on a deliberately truncated map set.
    truncated = raw[
        ~((raw["baseline_replicate"] == "control_r0") & (raw["endpoint_type"] == "identity"))
    ].copy()
    censored_analysis = analyze_replicate_frontiers(
        truncated, target_rule=rule, require_identity=False
    )
    censored_intervals, censored_draws = block_bootstrap(
        truncated,
        target_rule=rule,
        n_bootstrap=80,
        stream=AnalysisStream(20260731, "block-bootstrap", "phase3-censoring-validation"),
        confidence_level=0.95,
        require_identity=False,
    )
    censored_row = censored_analysis.replicate_summary[
        censored_analysis.replicate_summary["baseline_replicate"] == "control_r0"
    ].iloc[0]

    raw.to_csv(outdir / "synthetic_continuations.csv", index=False)
    analysis.continuation_summary.to_csv(outdir / "validated_continuations.csv", index=False)
    analysis.map_summary.to_csv(outdir / "map_level_nested_summary.csv", index=False)
    analysis.frontier_points.to_csv(outdir / "replicate_frontiers.csv", index=False)
    analysis.replicate_summary.to_csv(outdir / "replicate_frontier_summary.csv", index=False)
    paired.to_csv(outdir / "paired_identity_diagnostic.csv", index=False)
    reach.to_csv(outdir / "target_reach_counts.csv", index=False)
    variance.to_csv(outdir / "continuation_variance_diagnostic.csv", index=False)
    intervals.to_csv(outdir / "block_bootstrap_intervals.csv", index=False)
    draws.to_csv(outdir / "block_bootstrap_draws.csv", index=False)
    censored_analysis.replicate_summary.to_csv(outdir / "censoring_diagnostic_summary.csv", index=False)
    censored_intervals.to_csv(outdir / "censoring_block_bootstrap_intervals.csv", index=False)
    censored_draws.to_csv(outdir / "censoring_block_bootstrap_draws.csv", index=False)

    permutation_rows = [perm_semantic.to_dict(), perm_value.to_dict()]
    pd.DataFrame(permutation_rows).to_csv(outdir / "replicate_level_permutation_results.csv", index=False)
    identity = tiny_identity_diagnostic()
    (outdir / "identity_model_diagnostic.json").write_text(json.dumps(identity, indent=2), encoding="utf-8")

    summary = {
        "scope": "synthetic and tiny diagnostic data only",
        "production_simulations_run": False,
        "manuscript_rewritten": False,
        "n_independent_replicates": int(len(analysis.replicate_summary)),
        "n_raw_continuation_rows": int(len(raw)),
        "n_map_level_rows": int(len(analysis.map_summary)),
        "one_frontier_per_replicate": bool(
            analysis.frontier_points.groupby(["condition", "baseline_replicate"]).ngroups
            == len(analysis.replicate_summary)
        ),
        "identity_information_recovered_all": bool(
            analysis.replicate_summary["identity_information_recovered"].all()
        ),
        "identity_viability_recovered_all": bool(
            analysis.replicate_summary["identity_viability_recovered"].all()
        ),
        "paired_identity_max_abs_difference": float(
            paired["max_abs_viability_difference"].max()
        ),
        "selective_semantic_information_values": sorted(
            analysis.replicate_summary.loc[
                analysis.replicate_summary["condition"] == "selective",
                "semantic_information",
            ].unique().tolist()
        ),
        "control_semantic_information_values": sorted(
            analysis.replicate_summary.loc[
                analysis.replicate_summary["condition"] == "control",
                "semantic_information",
            ].unique().tolist()
        ),
        "censoring_test": {
            "target_reached": bool(censored_row["target_reached"]),
            "censoring": str(censored_row["censoring"]),
            "semantic_information_is_nan": bool(pd.isna(censored_row["semantic_information"])),
            "semantic_lower_bound": float(censored_row["semantic_lower_bound"]),
            "bootstrap_reach_fraction_estimate": float(
                censored_intervals.loc[
                    (censored_intervals["condition"] == "control")
                    & (censored_intervals["metric"] == "reach_fraction"),
                    "estimate",
                ].iloc[0]
            ),
            "bootstrap_censored_lower_bound_estimate": float(
                censored_intervals.loc[
                    (censored_intervals["condition"] == "control")
                    & (censored_intervals["metric"] == "median_censored_lower_bound"),
                    "estimate",
                ].iloc[0]
            ),
        },
        "block_bootstrap_replicates": 80,
        "permutation_results": permutation_rows,
        "tiny_identity_model_diagnostic": identity,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
    }
    (outdir / "phase3_validation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
