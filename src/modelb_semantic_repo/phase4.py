"""Phase 4 corrected core production for the JRSI major revision.

This module uses the Phase 3 validated information and statistical pipelines.
It intentionally contains no causal controls, broad parameter sweeps, figure
production, or manuscript-writing logic.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .information import (
    conditional_mutual_information,
    corrected_conditional_mutual_information,
    grouping_hash,
    identity_grouping,
    constant_grouping,
    mutual_information,
    positional_information,
    retained_information,
)
from .interventions import (
    _group_affinity_matrix,
    affinity_rank_group,
    balanced_random_group,
    segment_indices_for_observations,
    simulate_horizon_with_stream,
)
from .original_model.config import default_parameters
from .original_model.simulation import observe_population, run_single_sim
from .rng import AnalysisStream, ContinuationStream, PermutationStream, make_generator
from .statistical_pipeline import (
    TargetRule,
    analyze_replicate_frontiers,
    block_bootstrap,
    replicate_level_permutation_test,
    target_reach_table,
)


PRODUCTION_ROOT_SEED = 2026073104
PILOT_ROOT_SEED = 2026073199
PRODUCTION_FIDELITIES = tuple(round(x / 10, 1) for x in range(1, 11))
MAP_K_GRID = (2, 4, 8, 16, 32, 64, 128, 256, 512)


@dataclass(frozen=True)
class Phase4Settings:
    continuation_count: int
    intervention_horizon: int
    target_tolerance: float = 0.01
    n_baseline_replicates: int = 20
    n_information_permutations: int = 200
    n_bootstrap: int = 2000
    n_inference_permutations: int = 9999
    root_seed: int = PRODUCTION_ROOT_SEED
    workers: int = 4

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(v) for v in value]
    return value


def stable_integer_seed(root_seed: int, purpose: str, *keys: Any) -> int:
    rng = make_generator(root_seed, purpose, *keys)
    return int(rng.integers(0, 2**32, dtype=np.uint32))


def array_sha256(array: np.ndarray) -> str:
    arr = np.ascontiguousarray(array)
    h = hashlib.sha256()
    h.update(str(arr.dtype).encode("ascii"))
    h.update(np.asarray(arr.shape, dtype="<i8").tobytes())
    h.update(arr.tobytes())
    return h.hexdigest()


def baseline_id(condition: str, inherit_prob: float, replicate: int) -> str:
    return f"{condition}_p{inherit_prob:.1f}_r{replicate:02d}"


def motif_digits(index: int, motif_length: int = 5) -> np.ndarray:
    digits = np.empty(motif_length, dtype=np.int64)
    x = int(index)
    for pos in range(motif_length - 1, -1, -1):
        digits[pos] = x % 4
        x //= 4
    return digits


def contiguous_substring_grouping(
    *, start: int, length: int, motif_length: int = 5
) -> np.ndarray:
    """Group motifs by one contiguous substring at an explicitly stated position."""
    if length < 1 or length > motif_length:
        raise ValueError("substring length is outside motif")
    if start < 0 or start + length > motif_length:
        raise ValueError("substring start is outside motif")
    n = 4**motif_length
    labels = np.empty(n, dtype=np.int64)
    for idx in range(n):
        digits = motif_digits(idx, motif_length)
        label = 0
        for digit in digits[start : start + length]:
            label = 4 * label + int(digit)
        labels[idx] = label
    return labels


def build_phase4_map_panel(
    *, root_seed: int = PRODUCTION_ROOT_SEED, motif_affinity_matrix: np.ndarray | None = None
) -> list[dict[str, Any]]:
    """Build the fixed primary intervention panel and collapse exact aliases."""
    params = default_parameters()
    profiles = (
        np.asarray(motif_affinity_matrix)
        if motif_affinity_matrix is not None
        else np.asarray(params["motif_affinity_matrix"])
    )
    candidates: list[dict[str, Any]] = []

    def add(method: str, endpoint_type: str, labels: np.ndarray, parameters: dict[str, Any]):
        labels = np.asarray(labels, dtype=np.int64)
        candidates.append(
            {
                "method": method,
                "endpoint_type": endpoint_type,
                "parameters": parameters,
                "labels": labels,
                "map_hash": grouping_hash(labels),
                "actual_groups": int(np.unique(labels).size),
            }
        )

    add("constant", "constant", constant_grouping(), {})
    for k in MAP_K_GRID:
        rng = make_generator(root_seed, "phase4-balanced-random-map", k, 0)
        add(
            "balanced_random_group",
            "intermediate",
            balanced_random_group(4**5, k, rng),
            {"requested_groups": k, "map_index": 0},
        )
    for k in MAP_K_GRID:
        add(
            "affinity_rank_group",
            "intermediate",
            affinity_rank_group(profiles, k),
            {"requested_groups": k, "reference_profiles": "fixed_selective_affinity_matrix"},
        )
    for length in range(1, 5):
        for start in range(0, 5 - length + 1):
            add(
                "contiguous_substring",
                "intermediate",
                contiguous_substring_grouping(start=start, length=length),
                {"start_zero_based": start, "length": length},
            )
    add("identity", "identity", identity_grouping(), {})

    unique: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for candidate in candidates:
        digest = candidate["map_hash"]
        if digest in seen:
            continue
        map_id = f"m{len(unique):03d}_{candidate['method']}"
        seen[digest] = map_id
        unique.append({**candidate, "map_id": map_id})
    return unique


def save_map_panel(panel: list[dict[str, Any]], outdir: Path) -> pd.DataFrame:
    outdir.mkdir(parents=True, exist_ok=True)
    metadata = []
    arrays = {}
    for item in panel:
        arrays[item["map_id"]] = np.asarray(item["labels"], dtype=np.int64)
        metadata.append(
            {
                "map_id": item["map_id"],
                "map_hash": item["map_hash"],
                "method": item["method"],
                "endpoint_type": item["endpoint_type"],
                "actual_groups": item["actual_groups"],
                "parameters_json": json.dumps(item["parameters"], sort_keys=True),
            }
        )
    np.savez_compressed(outdir / "grouping_assignments.npz", **arrays)
    df = pd.DataFrame(metadata)
    df.to_csv(outdir / "grouping_map_manifest.csv", index=False)
    return df


def load_map_panel(map_dir: Path) -> list[dict[str, Any]]:
    manifest = pd.read_csv(map_dir / "grouping_map_manifest.csv")
    arrays = np.load(map_dir / "grouping_assignments.npz")
    panel = []
    for row in manifest.itertuples(index=False):
        panel.append(
            {
                "map_id": row.map_id,
                "map_hash": row.map_hash,
                "method": row.method,
                "endpoint_type": row.endpoint_type,
                "actual_groups": int(row.actual_groups),
                "parameters": json.loads(row.parameters_json),
                "labels": np.asarray(arrays[row.map_id], dtype=np.int64),
            }
        )
    return panel


def _run_pilot_baseline(job: tuple[str, float, int, Path]) -> dict[str, Any]:
    condition, inherit_prob, replicate, outdir = job
    params = default_parameters()
    params["n_gens"] = 100
    matrix = (
        params["motif_affinity_matrix"]
        if condition == "selective"
        else params["motif_affinity_matrix_no_aff"]
    )
    bid = baseline_id(condition, inherit_prob, replicate)
    seed = stable_integer_seed(PILOT_ROOT_SEED, "phase4-pilot-baseline", bid)
    fit, legacy_mi, population, *_ = run_single_sim(
        params["mutation_rate"],
        inherit_prob,
        seed,
        matrix,
        params,
        return_final_population=True,
    )
    path = outdir / f"{bid}.npz"
    np.savez_compressed(path, population=population, fitness_trajectory=fit, legacy_mi=legacy_mi)
    return {
        "condition": condition,
        "inherit_prob": inherit_prob,
        "replicate": replicate,
        "baseline_replicate": bid,
        "baseline_seed": seed,
        "state_path": str(path),
        "state_hash": array_sha256(population),
    }



def _pilot_continuation_job(job: dict[str, Any]) -> tuple[list[dict[str, Any]], list[float]]:
    base = job["base"]
    selected_items = job["selected_items"]
    params = default_parameters()
    population = np.load(base["state_path"])["population"]
    matrix = (
        params["motif_affinity_matrix"]
        if base["condition"] == "selective"
        else params["motif_affinity_matrix_no_aff"]
    )
    rows: list[dict[str, Any]] = []
    identity_differences: list[float] = []
    for continuation_index in range(8):
        stream = ContinuationStream(PILOT_ROOT_SEED, base["baseline_replicate"], continuation_index)
        actual = simulate_horizon_with_stream(
            population, matrix, params, float(base["inherit_prob"]), 36, stream
        )
        actual_curve = np.asarray(actual["mean_fitness"], dtype=float)
        for horizon in (12, 24, 36):
            rows.append(
                {
                    "condition": base["condition"],
                    "inherit_prob": float(base["inherit_prob"]),
                    "baseline_replicate": base["baseline_replicate"],
                    "map_id": "actual",
                    "map_hash": "actual",
                    "method": "unintervened",
                    "endpoint_type": "actual",
                    "continuation_index": continuation_index,
                    "horizon": horizon,
                    "viability": float(actual_curve[:horizon].mean()),
                }
            )
        for item in selected_items:
            labels = np.asarray(item["labels"], dtype=np.int64)
            grouped = _group_affinity_matrix(matrix, labels)
            result = simulate_horizon_with_stream(
                population, grouped, params, float(base["inherit_prob"]), 36, stream
            )
            curve = np.asarray(result["mean_fitness"], dtype=float)
            if item["endpoint_type"] == "identity":
                identity_differences.append(float(np.max(np.abs(curve - actual_curve))))
            for horizon in (12, 24, 36):
                rows.append(
                    {
                        "condition": base["condition"],
                        "inherit_prob": float(base["inherit_prob"]),
                        "baseline_replicate": base["baseline_replicate"],
                        "map_id": item["map_id"],
                        "map_hash": item["map_hash"],
                        "method": item["method"],
                        "endpoint_type": item["endpoint_type"],
                        "continuation_index": continuation_index,
                        "horizon": horizon,
                        "viability": float(curve[:horizon].mean()),
                    }
                )
    return rows, identity_differences

def run_phase4_pilots(outdir: str | Path, *, workers: int = 4) -> dict[str, Any]:
    """Run the prespecified small pilot and return P01--P05 evidence."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    state_dir = outdir / "states"
    state_dir.mkdir(exist_ok=True)

    full_panel = build_phase4_map_panel(root_seed=PRODUCTION_ROOT_SEED)
    manifest = save_map_panel(full_panel, outdir / "maps")
    substring = manifest[manifest["method"] == "contiguous_substring"]
    p01_pass = bool(
        len(substring) == 14
        and manifest["map_hash"].is_unique
        and set(manifest["endpoint_type"]) >= {"constant", "identity"}
    )

    jobs = [
        (condition, p, rep, state_dir)
        for condition in ("selective", "control")
        for p in (0.5, 0.9, 1.0)
        for rep in range(2)
    ]
    rows: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=min(workers, len(jobs))) as executor:
        futures = [executor.submit(_run_pilot_baseline, job) for job in jobs]
        for future in as_completed(futures):
            rows.append(future.result())
    baselines = pd.DataFrame(rows).sort_values(["condition", "inherit_prob", "replicate"])
    baselines.to_csv(outdir / "pilot_baselines.csv", index=False)

    # Fixed diagnostic subset, selected by method/endpoints rather than outcomes.
    panel_by_id = {item["map_id"]: item for item in full_panel}
    selected_items: list[dict[str, Any]] = []
    for endpoint in ("constant", "identity"):
        selected_items.append(next(x for x in full_panel if x["endpoint_type"] == endpoint))
    selected_items.append(next(x for x in full_panel if x["method"] == "balanced_random_group" and x["actual_groups"] == 16))
    selected_items.append(next(x for x in full_panel if x["method"] == "affinity_rank_group" and x["actual_groups"] == 64))
    substring_candidates = [x for x in full_panel if x["method"] == "contiguous_substring"]
    for wanted in ({"start_zero_based": 0, "length": 2}, {"start_zero_based": 3, "length": 2}, {"start_zero_based": 1, "length": 3}):
        selected_items.append(next(x for x in substring_candidates if x["parameters"] == wanted))

    continuation_rows: list[dict[str, Any]] = []
    identity_differences: list[float] = []
    continuation_jobs = [
        {
            "base": row._asdict(),
            "selected_items": selected_items,
        }
        for row in baselines.itertuples(index=False)
    ]
    with ProcessPoolExecutor(max_workers=min(workers, len(continuation_jobs))) as executor:
        futures = [executor.submit(_pilot_continuation_job, job) for job in continuation_jobs]
        for future in as_completed(futures):
            part_rows, part_differences = future.result()
            continuation_rows.extend(part_rows)
            identity_differences.extend(part_differences)
    continuation = pd.DataFrame(continuation_rows)
    continuation.to_csv(outdir / "pilot_continuations.csv", index=False)

    map_means = (
        continuation.groupby(
            ["condition", "inherit_prob", "baseline_replicate", "map_id", "horizon"],
            as_index=False,
        )["viability"]
        .mean()
    )
    ref = map_means[map_means["horizon"] == 36].rename(columns={"viability": "viability_36"})
    horizon_rows = []
    key = ["condition", "inherit_prob", "baseline_replicate", "map_id"]
    for horizon in (12, 24):
        short = map_means[map_means["horizon"] == horizon]
        merged = short.merge(ref[key + ["viability_36"]], on=key)
        errors = np.abs(merged["viability"] - merged["viability_36"]).to_numpy()
        rho = float(spearmanr(merged["viability"], merged["viability_36"]).statistic)
        horizon_rows.append(
            {
                "horizon": horizon,
                "spearman_vs_36": rho,
                "median_abs_difference": float(np.median(errors)),
                "p95_abs_difference": float(np.quantile(errors, 0.95)),
                "passes": bool(rho >= 0.98 and np.median(errors) <= 0.10 and np.quantile(errors, 0.95) <= 0.25),
            }
        )
    horizon_df = pd.DataFrame(horizon_rows)
    passing_horizons = horizon_df.loc[horizon_df["passes"], "horizon"].tolist()
    selected_horizon = int(min(passing_horizons)) if passing_horizons else 36
    horizon_df.to_csv(outdir / "horizon_sensitivity.csv", index=False)

    horizon_data = continuation[continuation["horizon"] == selected_horizon]
    full_means = horizon_data.groupby(key)["viability"].mean()
    count_rows = []
    for k in (1, 2, 4, 6, 8):
        errors = []
        for keys, part in horizon_data.groupby(key, sort=False):
            estimate = float(part.sort_values("continuation_index").iloc[:k]["viability"].mean())
            errors.append(estimate - float(full_means.loc[keys]))
        abs_err = np.abs(np.asarray(errors, dtype=float))
        count_rows.append(
            {
                "continuation_count": k,
                "rmse_vs_8": float(np.sqrt(np.mean(np.square(errors)))),
                "p95_abs_error_vs_8": float(np.quantile(abs_err, 0.95)),
                "passes": bool(np.sqrt(np.mean(np.square(errors))) <= 0.10 and np.quantile(abs_err, 0.95) <= 0.25),
            }
        )
    count_df = pd.DataFrame(count_rows)
    passing_counts = count_df.loc[count_df["passes"], "continuation_count"].tolist()
    selected_count = int(min(passing_counts)) if passing_counts else 8
    count_df.to_csv(outdir / "continuation_count_sensitivity.csv", index=False)

    identity_max_difference = float(max(identity_differences, default=np.inf))
    p04_pass = bool(identity_max_difference == 0.0)
    summary = {
        "pilot_only": True,
        "production_seeds_used": False,
        "p01": {
            "approved": p01_pass,
            "sequence_family": "all contiguous substring maps of lengths 1-4 at every valid start position",
            "n_contiguous_substring_maps": int(len(substring)),
        },
        "p02": {"approved_continuation_count": selected_count},
        "p03": {"approved_intervention_horizon": selected_horizon},
        "p04": {
            "approved_target_tolerance": 0.01 if p04_pass else None,
            "paired_identity_max_abs_difference": identity_max_difference,
            "approved": p04_pass,
        },
        "p05": {
            "approved": bool(p01_pass and p04_pass),
            "pooling_rule": "unique balanced-random, affinity-rank, contiguous-substring, constant, and identity maps; no k-means",
            "n_unique_primary_maps": int(len(manifest)),
        },
    }
    (outdir / "pilot_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _baseline_job(job: dict[str, Any]) -> dict[str, Any]:
    params = default_parameters()
    condition = job["condition"]
    p = float(job["inherit_prob"])
    replicate = int(job["replicate"])
    root_seed = int(job["root_seed"])
    n_permutations = int(job["n_information_permutations"])
    state_dir = Path(job["state_dir"])
    bid = baseline_id(condition, p, replicate)
    matrix = params["motif_affinity_matrix"] if condition == "selective" else params["motif_affinity_matrix_no_aff"]
    run_seed = stable_integer_seed(root_seed, "phase4-production-baseline", condition, p, replicate)
    fit, legacy_mi, population, _, _, _, rng_state = run_single_sim(
        params["mutation_rate"], p, run_seed, matrix, params, return_final_population=True
    )
    observation_seed = stable_integer_seed(root_seed, "phase4-information-observation-seed", bid)
    observation_rng = make_generator(root_seed, "phase4-information-observation", bid)
    fitnesses, motifs, states = observe_population(population, matrix, params, observation_rng)
    segments = segment_indices_for_observations(params)
    corrected = corrected_conditional_mutual_information(
        motifs,
        states,
        segments,
        n_permutations=n_permutations,
        stream=PermutationStream(root_seed, bid, 0),
    )
    state_path = state_dir / condition / f"p{p:.1f}" / f"rep_{replicate:02d}.npz"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        state_path,
        population=population,
        fitness_trajectory=fit,
        legacy_total_mi_trajectory=legacy_mi,
        final_observation_fitnesses=fitnesses,
        final_observation_motifs=motifs,
        final_observation_states=states,
        final_observation_segments=segments,
    )
    rng_path = state_path.with_suffix(".rng.json")
    rng_path.write_text(json.dumps(_json_ready(rng_state), indent=2), encoding="utf-8")
    return {
        "condition": condition,
        "inherit_prob": p,
        "replicate": replicate,
        "baseline_replicate": bid,
        "baseline_run_seed": run_seed,
        "information_observation_seed": observation_seed,
        "permutation_root_seed": root_seed,
        "permutation_stream_index": 0,
        "n_information_permutations": n_permutations,
        "state_path": str(state_path),
        "rng_state_path": str(rng_path),
        "state_hash": array_sha256(population),
        "trajectory_hash": array_sha256(np.asarray(fit)),
        "final_mean_fitness": float(np.mean(fitnesses)),
        "total_information": mutual_information(motifs, states),
        "positional_information": positional_information(motifs, segments),
        "conditional_information": corrected.observed,
        "permutation_mean": corrected.permutation_mean,
        "permutation_std": corrected.permutation_std,
        "corrected_conditional_information": corrected.corrected,
    }


def run_production_baselines(outdir: Path, settings: Phase4Settings) -> pd.DataFrame:
    state_dir = outdir / "states"
    jobs = [
        {
            "condition": condition,
            "inherit_prob": p,
            "replicate": replicate,
            "root_seed": settings.root_seed,
            "n_information_permutations": settings.n_information_permutations,
            "state_dir": str(state_dir),
        }
        for condition in ("selective", "control")
        for p in PRODUCTION_FIDELITIES
        for replicate in range(settings.n_baseline_replicates)
    ]
    rows = []
    with ProcessPoolExecutor(max_workers=settings.workers) as executor:
        futures = [executor.submit(_baseline_job, job) for job in jobs]
        for index, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if index % 20 == 0 or index == len(futures):
                print(f"baseline production: {index}/{len(futures)}", flush=True)
    df = pd.DataFrame(rows).sort_values(["condition", "inherit_prob", "replicate"])
    df.to_csv(outdir / "baseline_information.csv", index=False)
    return df


def _intervention_job(job: dict[str, Any]) -> str:
    base = job["base"]
    settings = Phase4Settings(**job["settings"])
    map_dir = Path(job["map_dir"])
    block_dir = Path(job["block_dir"])
    panel = load_map_panel(map_dir)
    params = default_parameters()
    condition = base["condition"]
    matrix = params["motif_affinity_matrix"] if condition == "selective" else params["motif_affinity_matrix_no_aff"]
    loaded = np.load(base["state_path"])
    population = np.asarray(loaded["population"])
    motifs = np.asarray(loaded["final_observation_motifs"])
    states = np.asarray(loaded["final_observation_states"])
    segments = np.asarray(loaded["final_observation_segments"])
    baseline_information = float(base["conditional_information"])
    rows = []
    for continuation_index in range(settings.continuation_count):
        stream = ContinuationStream(settings.root_seed, base["baseline_replicate"], continuation_index)
        actual = simulate_horizon_with_stream(
            population,
            matrix,
            params,
            float(base["inherit_prob"]),
            settings.intervention_horizon,
            stream,
        )
        actual_curve = np.asarray(actual["mean_fitness"], dtype=float)
        rows.append(
            {
                "condition": condition,
                "inherit_prob": float(base["inherit_prob"]),
                "replicate": int(base["replicate"]),
                "baseline_replicate": base["baseline_replicate"],
                "map_id": "actual",
                "map_hash": "actual",
                "method": "unintervened",
                "endpoint_type": "actual",
                "actual_groups": 1024,
                "retained_information": baseline_information,
                "baseline_information": baseline_information,
                "continuation_index": continuation_index,
                "viability": float(actual_curve.mean()),
                "mean_fitness_trajectory_json": json.dumps(actual_curve.tolist()),
                "final_population_hash": array_sha256(actual["final_population"]),
                "continuation_root_seed": settings.root_seed,
                "continuation_stream_key": f"{base['baseline_replicate']}|{continuation_index}",
            }
        )
        for item in panel:
            grouped_matrix = _group_affinity_matrix(matrix, item["labels"])
            result = simulate_horizon_with_stream(
                population,
                grouped_matrix,
                params,
                float(base["inherit_prob"]),
                settings.intervention_horizon,
                stream,
            )
            curve = np.asarray(result["mean_fitness"], dtype=float)
            rows.append(
                {
                    "condition": condition,
                    "inherit_prob": float(base["inherit_prob"]),
                    "replicate": int(base["replicate"]),
                    "baseline_replicate": base["baseline_replicate"],
                    "map_id": item["map_id"],
                    "map_hash": item["map_hash"],
                    "method": item["method"],
                    "endpoint_type": item["endpoint_type"],
                    "actual_groups": item["actual_groups"],
                    "retained_information": float(retained_information(motifs, states, segments, item["labels"])),
                    "baseline_information": baseline_information,
                    "continuation_index": continuation_index,
                    "viability": float(curve.mean()),
                    "mean_fitness_trajectory_json": json.dumps(curve.tolist()),
                    "final_population_hash": array_sha256(result["final_population"]),
                    "continuation_root_seed": settings.root_seed,
                    "continuation_stream_key": f"{base['baseline_replicate']}|{continuation_index}",
                }
            )
    block_dir.mkdir(parents=True, exist_ok=True)
    path = block_dir / f"{base['baseline_replicate']}.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return str(path)


def run_production_interventions(
    outdir: Path, settings: Phase4Settings, baselines: pd.DataFrame
) -> pd.DataFrame:
    map_dir = outdir / "maps"
    block_dir = outdir / "continuation_blocks"
    jobs = [
        {
            "base": row._asdict(),
            "settings": settings.to_dict(),
            "map_dir": str(map_dir),
            "block_dir": str(block_dir),
        }
        for row in baselines.itertuples(index=False)
    ]
    paths = []
    with ProcessPoolExecutor(max_workers=settings.workers) as executor:
        futures = [executor.submit(_intervention_job, job) for job in jobs]
        for index, future in enumerate(as_completed(futures), start=1):
            paths.append(future.result())
            if index % 10 == 0 or index == len(futures):
                print(f"intervention production: {index}/{len(futures)}", flush=True)
    frames = [pd.read_csv(path) for path in sorted(paths)]
    raw = pd.concat(frames, ignore_index=True)
    raw.to_csv(outdir / "continuation_level_results.csv", index=False)
    return raw



def fast_block_bootstrap_from_replicate_summary(
    replicate_summary: pd.DataFrame,
    *,
    n_bootstrap: int,
    stream: AnalysisStream,
    confidence_level: float = 0.95,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Resample complete evolved-replicate summary blocks, stratified by condition.

    Each frontier is constructed before this function is called, so resampling the
    one-row-per-baseline summary is mathematically identical to resampling raw
    nested rows and reconstructing the same independent frontiers. Censored
    semantic values are never imputed.
    """
    required = {
        "condition", "baseline_replicate", "target_reached",
        "semantic_information", "semantic_lower_bound", "value_of_information",
    }
    missing = required.difference(replicate_summary.columns)
    if missing:
        raise ValueError(f"missing replicate-summary columns: {sorted(missing)}")
    if replicate_summary.duplicated(["condition", "baseline_replicate"]).any():
        raise ValueError("replicate summary contains duplicate independent blocks")
    if n_bootstrap < 1:
        raise ValueError("n_bootstrap must be positive")
    rng = stream.generator()
    draws: list[dict[str, Any]] = []
    by_condition = {c: part.reset_index(drop=True) for c, part in replicate_summary.groupby("condition", sort=True)}
    for b in range(n_bootstrap):
        for condition, part in by_condition.items():
            sampled = part.iloc[rng.integers(0, len(part), size=len(part))]
            reached = sampled[sampled["target_reached"].astype(bool)]
            censored = sampled[~sampled["target_reached"].astype(bool)]
            draws.append(
                {
                    "bootstrap_index": b,
                    "condition": condition,
                    "reach_fraction": float(sampled["target_reached"].mean()),
                    "median_semantic_information_among_reached": float(reached["semantic_information"].median()) if len(reached) else np.nan,
                    "median_censored_lower_bound": float(censored["semantic_lower_bound"].median()) if len(censored) else np.nan,
                    "mean_value_of_information": float(sampled["value_of_information"].mean()),
                    "n_reached": int(len(reached)),
                    "n_censored": int(len(censored)),
                }
            )
    draws_df = pd.DataFrame(draws)
    alpha = (1.0 - confidence_level) / 2.0
    rows: list[dict[str, Any]] = []
    notes = {
        "reach_fraction": "All independent replicates; censoring retained as target_reached=False.",
        "median_semantic_information_among_reached": "Conditional on target-reached replicates; censored values are not imputed.",
        "median_censored_lower_bound": "Conditional on right-censored replicates; reports their tested lower bounds.",
        "mean_value_of_information": "Defined for every independent replicate.",
    }
    for condition, part in replicate_summary.groupby("condition", sort=True):
        reached = part[part["target_reached"].astype(bool)]
        censored = part[~part["target_reached"].astype(bool)]
        observed = {
            "reach_fraction": float(part["target_reached"].mean()),
            "median_semantic_information_among_reached": float(reached["semantic_information"].median()) if len(reached) else np.nan,
            "median_censored_lower_bound": float(censored["semantic_lower_bound"].median()) if len(censored) else np.nan,
            "mean_value_of_information": float(part["value_of_information"].mean()),
        }
        condition_draws = draws_df[draws_df["condition"] == condition]
        for metric, note in notes.items():
            vals = condition_draws[metric].dropna().to_numpy(dtype=float)
            rows.append(
                {
                    "condition": condition,
                    "metric": metric,
                    "estimate": observed[metric],
                    "confidence_level": confidence_level,
                    "lower": float(np.quantile(vals, alpha)) if len(vals) else np.nan,
                    "upper": float(np.quantile(vals, 1 - alpha)) if len(vals) else np.nan,
                    "n_independent_replicates": int(len(part)),
                    "n_bootstrap": int(n_bootstrap),
                    "note": note,
                }
            )
    return pd.DataFrame(rows), draws_df

def _bh_adjust(pvalues: Iterable[float]) -> np.ndarray:
    p = np.asarray(list(pvalues), dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = np.minimum.accumulate((ranked * len(p) / np.arange(1, len(p) + 1))[::-1])[::-1]
    adjusted = np.minimum(adjusted, 1.0)
    out = np.empty_like(adjusted)
    out[order] = adjusted
    return out


def analyze_phase4_results(
    outdir: Path,
    settings: Phase4Settings,
    baselines: pd.DataFrame,
    raw: pd.DataFrame,
) -> dict[str, Any]:
    all_replicates = []
    all_frontiers = []
    all_maps = []
    all_reach = []
    all_bootstrap_intervals = []
    all_bootstrap_draws = []
    inference_rows: list[dict[str, Any]] = []
    target_rule = TargetRule(settings.target_tolerance)

    for p in PRODUCTION_FIDELITIES:
        part = raw[np.isclose(raw["inherit_prob"], p)].copy()
        analysis = analyze_replicate_frontiers(part, target_rule=target_rule)
        for frame in (analysis.replicate_summary, analysis.frontier_points, analysis.map_summary):
            frame.insert(0, "inherit_prob", p)
        reach = target_reach_table(analysis.replicate_summary)
        reach.insert(0, "inherit_prob", p)
        intervals, draws = fast_block_bootstrap_from_replicate_summary(
            analysis.replicate_summary,
            n_bootstrap=settings.n_bootstrap,
            stream=AnalysisStream(settings.root_seed, "phase4-block-bootstrap", f"p{p:.1f}"),
            confidence_level=0.95,
        )
        intervals.insert(0, "inherit_prob", p)
        draws.insert(0, "inherit_prob", p)
        all_replicates.append(analysis.replicate_summary)
        all_frontiers.append(analysis.frontier_points)
        all_maps.append(analysis.map_summary)
        all_reach.append(reach)
        all_bootstrap_intervals.append(intervals)
        all_bootstrap_draws.append(draws)

        info_part = baselines[np.isclose(baselines["inherit_prob"], p)][
            ["condition", "baseline_replicate", "corrected_conditional_information"]
        ].copy()
        info_test = replicate_level_permutation_test(
            info_part,
            metric="corrected_conditional_information",
            group_a="selective",
            group_b="control",
            stream=AnalysisStream(settings.root_seed, "phase4-replicate-permutation", f"corrected-info-p{p:.1f}"),
            n_permutations=settings.n_inference_permutations,
        )
        inference_rows.append({"inherit_prob": p, **info_test.to_dict(), "status": "performed"})

        voi_test = replicate_level_permutation_test(
            analysis.replicate_summary,
            metric="value_of_information",
            group_a="selective",
            group_b="control",
            stream=AnalysisStream(settings.root_seed, "phase4-replicate-permutation", f"voi-p{p:.1f}"),
            n_permutations=settings.n_inference_permutations,
        )
        inference_rows.append({"inherit_prob": p, **voi_test.to_dict(), "status": "performed"})

        if analysis.replicate_summary["semantic_information"].notna().all():
            semantic_test = replicate_level_permutation_test(
                analysis.replicate_summary,
                metric="semantic_information",
                group_a="selective",
                group_b="control",
                stream=AnalysisStream(settings.root_seed, "phase4-replicate-permutation", f"semantic-p{p:.1f}"),
                n_permutations=settings.n_inference_permutations,
            )
            inference_rows.append({"inherit_prob": p, **semantic_test.to_dict(), "status": "performed"})
        else:
            inference_rows.append(
                {
                    "inherit_prob": p,
                    "metric": "semantic_information",
                    "status": "not_performed_due_to_censoring",
                    "analysis_unit": "independently evolved baseline replicate",
                }
            )

    replicate_summary = pd.concat(all_replicates, ignore_index=True)
    frontier_points = pd.concat(all_frontiers, ignore_index=True)
    map_summary = pd.concat(all_maps, ignore_index=True)
    reach_counts = pd.concat(all_reach, ignore_index=True)
    bootstrap_intervals = pd.concat(all_bootstrap_intervals, ignore_index=True)
    bootstrap_draws = pd.concat(all_bootstrap_draws, ignore_index=True)
    inference = pd.DataFrame(inference_rows)
    for metric, idx in inference[inference["status"] == "performed"].groupby("metric").groups.items():
        inference.loc[idx, "q_value_bh_across_fidelities"] = _bh_adjust(
            inference.loc[idx, "p_value_two_sided"].astype(float)
        )

    replicate_summary.to_csv(outdir / "replicate_frontier_summary.csv", index=False)
    frontier_points.to_csv(outdir / "replicate_frontiers.csv", index=False)
    map_summary.to_csv(outdir / "map_level_nested_summary.csv", index=False)
    reach_counts.to_csv(outdir / "target_reach_counts.csv", index=False)
    bootstrap_intervals.to_csv(outdir / "block_bootstrap_intervals.csv", index=False)
    bootstrap_draws.to_csv(outdir / "block_bootstrap_draws.csv", index=False)
    inference.to_csv(outdir / "replicate_level_permutation_results.csv", index=False)

    primary_p = 1.0
    primary_rep = replicate_summary[np.isclose(replicate_summary["inherit_prob"], primary_p)]
    primary_inf = inference[np.isclose(inference["inherit_prob"], primary_p)]
    info_row = primary_inf[(primary_inf["metric"] == "corrected_conditional_information") & (primary_inf["status"] == "performed")].iloc[0]
    voi_row = primary_inf[(primary_inf["metric"] == "value_of_information") & (primary_inf["status"] == "performed")].iloc[0]
    semantic_rows = primary_inf[(primary_inf["metric"] == "semantic_information") & (primary_inf["status"] == "performed")]
    selective_voi_mean = float(primary_rep.loc[primary_rep["condition"] == "selective", "value_of_information"].mean())
    identity_ok = bool(
        replicate_summary["identity_information_recovered"].all()
        and replicate_summary["identity_viability_recovered"].all()
    )
    semantic_available = bool(len(semantic_rows) == 1)
    semantic_pass = bool(
        semantic_available
        and float(semantic_rows.iloc[0]["p_value_two_sided"]) < 0.05
        and float(semantic_rows.iloc[0]["observed_difference"]) > 0
    )
    gate_pass = bool(
        identity_ok
        and float(info_row["p_value_two_sided"]) < 0.05
        and float(info_row["observed_difference"]) > 0
        and float(voi_row["p_value_two_sided"]) < 0.05
        and float(voi_row["observed_difference"]) > 0
        and selective_voi_mean > 0
        and semantic_pass
    )
    gate = {
        "gate": "Gate 4 - core-result survival",
        "status": "PASSED" if gate_pass else "FAILED",
        "primary_fidelity": primary_p,
        "identity_endpoints_all_recovered": identity_ok,
        "corrected_information_observed_difference_selective_minus_control": float(info_row["observed_difference"]),
        "corrected_information_p_value": float(info_row["p_value_two_sided"]),
        "value_of_information_observed_difference_selective_minus_control": float(voi_row["observed_difference"]),
        "value_of_information_p_value": float(voi_row["p_value_two_sided"]),
        "selective_mean_value_of_information": selective_voi_mean,
        "semantic_test_available_without_censoring": semantic_available,
        "semantic_test_passed": semantic_pass,
        "n_production_baseline_blocks": int(len(baselines)),
        "n_continuation_rows": int(len(raw)),
    }
    (outdir / "GATE_4_DECISION.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    return gate


def run_phase4_production(
    outdir: str | Path,
    *,
    settings: Phase4Settings,
    resume: bool = True,
) -> dict[str, Any]:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "phase4_settings.json").write_text(json.dumps(settings.to_dict(), indent=2), encoding="utf-8")
    params = default_parameters()
    panel = build_phase4_map_panel(root_seed=settings.root_seed, motif_affinity_matrix=params["motif_affinity_matrix"])
    manifest = save_map_panel(panel, outdir / "maps")
    if len(manifest) != 34 or not manifest["map_hash"].is_unique:
        raise RuntimeError("unexpected Phase 4 map panel; production stopped")

    baseline_path = outdir / "baseline_information.csv"
    if resume and baseline_path.exists():
        baselines = pd.read_csv(baseline_path)
    else:
        baselines = run_production_baselines(outdir, settings)

    continuation_path = outdir / "continuation_level_results.csv"
    if resume and continuation_path.exists():
        raw = pd.read_csv(continuation_path)
    else:
        raw = run_production_interventions(outdir, settings, baselines)

    seed_ledger_cols = [
        "condition",
        "inherit_prob",
        "replicate",
        "baseline_replicate",
        "baseline_run_seed",
        "information_observation_seed",
        "permutation_root_seed",
        "permutation_stream_index",
    ]
    baselines[seed_ledger_cols].to_csv(outdir / "baseline_seed_ledger.csv", index=False)
    raw[
        [
            "condition",
            "inherit_prob",
            "replicate",
            "baseline_replicate",
            "map_id",
            "map_hash",
            "continuation_index",
            "continuation_root_seed",
            "continuation_stream_key",
        ]
    ].to_csv(outdir / "continuation_seed_ledger.csv", index=False)
    return analyze_phase4_results(outdir, settings, baselines, raw)
