"""Replicate-level information--viability frontier and inference pipeline.

The independently evolved baseline population is the only inferential unit.
Grouping maps and continuation seeds are nested technical measurements.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations, product
import math
from typing import Any, Callable, Iterable, Sequence

import numpy as np
import pandas as pd

from .rng import AnalysisStream


REQUIRED_CONTINUATION_COLUMNS = {
    "condition",
    "baseline_replicate",
    "map_hash",
    "method",
    "endpoint_type",
    "retained_information",
    "continuation_index",
    "viability",
}


@dataclass(frozen=True)
class TargetRule:
    """Configurable target rule; the final tolerance remains a pending decision."""

    tolerance: float

    def __post_init__(self):
        if not np.isfinite(self.tolerance) or self.tolerance < 0:
            raise ValueError("target tolerance must be finite and non-negative")

    def target(self, actual_viability: float, constant_viability: float) -> float:
        value = actual_viability - constant_viability
        return float(actual_viability - self.tolerance * value)


@dataclass(frozen=True)
class ReplicateFrontierRecord:
    condition: str
    baseline_replicate: str
    target_tolerance: float
    actual_viability: float
    constant_viability: float
    identity_viability: float
    value_of_information: float
    target_viability: float
    target_reached: bool
    censoring: str
    semantic_information: float
    semantic_lower_bound: float
    max_retained_information: float
    baseline_information: float
    identity_information: float
    identity_information_recovered: bool
    identity_viability_recovered: bool
    n_unique_maps: int
    n_continuation_rows: int
    min_continuations_per_map: int
    max_continuations_per_map: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FrontierAnalysis:
    replicate_summary: pd.DataFrame
    frontier_points: pd.DataFrame
    map_summary: pd.DataFrame
    continuation_summary: pd.DataFrame


@dataclass(frozen=True)
class PermutationResult:
    metric: str
    statistic: str
    observed_difference: float
    p_value_two_sided: float
    group_a: str
    group_b: str
    n_group_a: int
    n_group_b: int
    n_permutations: int
    exact: bool
    paired: bool
    analysis_unit: str = "independently evolved baseline replicate"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BootstrapInterval:
    metric: str
    estimate: float
    confidence_level: float
    lower: float
    upper: float
    n_independent_replicates: int
    n_bootstrap: int
    note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = sorted(set(columns).difference(df.columns))
    if missing:
        raise ValueError(f"missing required columns: {missing}")


def _finite_scalar(values: pd.Series, label: str, *, atol: float = 1e-12) -> float:
    arr = values.to_numpy(dtype=float)
    if arr.size == 0 or not np.all(np.isfinite(arr)):
        raise ValueError(f"{label} must contain finite values")
    if float(np.max(arr) - np.min(arr)) > atol:
        raise ValueError(f"{label} must be constant within a nested map block")
    return float(arr[0])


def validate_continuation_table(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate and canonicalize continuation-level data without pooling blocks."""
    _require_columns(raw, REQUIRED_CONTINUATION_COLUMNS)
    df = raw.copy()
    if df.empty:
        raise ValueError("continuation table must not be empty")
    for col in ("condition", "baseline_replicate", "map_hash", "method", "endpoint_type"):
        if df[col].isna().any():
            raise ValueError(f"{col} contains missing values")
        df[col] = df[col].astype(str)
    df["continuation_index"] = pd.to_numeric(df["continuation_index"], errors="raise").astype(int)
    if (df["continuation_index"] < 0).any():
        raise ValueError("continuation_index must be non-negative")
    for col in ("retained_information", "viability"):
        df[col] = pd.to_numeric(df[col], errors="raise").astype(float)
        if not np.isfinite(df[col]).all():
            raise ValueError(f"{col} contains non-finite values")
    if (df["retained_information"] < -1e-12).any():
        raise ValueError("retained_information must be non-negative")

    key = ["condition", "baseline_replicate", "map_hash", "continuation_index"]
    duplicated = df.duplicated(key, keep=False)
    if duplicated.any():
        # Duplicate map aliases are legal only when every scientific value agrees.
        collapsed = []
        for _, part in df.groupby(key, sort=False, dropna=False):
            if len(part) == 1:
                collapsed.append(part.iloc[0].to_dict())
                continue
            _finite_scalar(part["retained_information"], "duplicate retained_information")
            _finite_scalar(part["viability"], "duplicate viability")
            if part["endpoint_type"].nunique() != 1:
                raise ValueError("duplicate map rows disagree on endpoint_type")
            row = part.iloc[0].to_dict()
            row["method"] = "|".join(sorted(set(part["method"].astype(str))))
            collapsed.append(row)
        df = pd.DataFrame(collapsed)

    # A map is a nested repeated measure and must have one information coordinate.
    for _, part in df.groupby(["condition", "baseline_replicate", "map_hash"], sort=False):
        _finite_scalar(part["retained_information"], "retained_information")
        if part["endpoint_type"].nunique() != 1:
            raise ValueError("one map_hash has multiple endpoint types")
    return df.sort_values(key).reset_index(drop=True)


def aggregate_nested_continuations(raw: pd.DataFrame) -> pd.DataFrame:
    """Average continuation seeds within each map, never across baseline replicates."""
    df = validate_continuation_table(raw)
    rows = []
    group_cols = ["condition", "baseline_replicate", "map_hash"]
    for keys, part in df.groupby(group_cols, sort=True):
        methods = "|".join(sorted(set(part["method"])))
        rows.append(
            {
                "condition": keys[0],
                "baseline_replicate": keys[1],
                "map_hash": keys[2],
                "method": methods,
                "endpoint_type": part["endpoint_type"].iloc[0],
                "retained_information": _finite_scalar(part["retained_information"], "retained_information"),
                "viability_mean": float(part["viability"].mean()),
                "viability_sd": float(part["viability"].std(ddof=1)) if len(part) > 1 else 0.0,
                "viability_se": float(part["viability"].std(ddof=1) / math.sqrt(len(part))) if len(part) > 1 else 0.0,
                "n_continuations": int(len(part)),
                "continuation_indices": "|".join(str(x) for x in sorted(part["continuation_index"].unique())),
            }
        )
    return pd.DataFrame(rows)


def paired_endpoint_diagnostic(
    raw: pd.DataFrame,
    *,
    endpoint_a: str = "actual",
    endpoint_b: str = "identity",
    atol: float = 0.0,
) -> pd.DataFrame:
    """Check common-random-number pairing for two endpoint trajectories."""
    df = validate_continuation_table(raw)
    rows = []
    for (condition, baseline), block in df.groupby(["condition", "baseline_replicate"], sort=True):
        a = block[block["endpoint_type"] == endpoint_a]
        b = block[block["endpoint_type"] == endpoint_b]
        if a.empty or b.empty:
            rows.append(
                {
                    "condition": condition,
                    "baseline_replicate": baseline,
                    "endpoint_a": endpoint_a,
                    "endpoint_b": endpoint_b,
                    "paired": False,
                    "same_continuation_indices": False,
                    "max_abs_viability_difference": np.nan,
                    "endpoint_recovered": False,
                    "reason": "missing endpoint",
                }
            )
            continue
        if a["map_hash"].nunique() != 1 or b["map_hash"].nunique() != 1:
            raise ValueError("actual and identity endpoints must each have one map per baseline")
        am = a.set_index("continuation_index")["viability"]
        bm = b.set_index("continuation_index")["viability"]
        same = am.index.equals(bm.index)
        if same:
            maxdiff = float(np.max(np.abs(am.to_numpy() - bm.to_numpy())))
            recovered = bool(maxdiff <= atol)
        else:
            maxdiff = np.nan
            recovered = False
        rows.append(
            {
                "condition": condition,
                "baseline_replicate": baseline,
                "endpoint_a": endpoint_a,
                "endpoint_b": endpoint_b,
                "paired": same,
                "same_continuation_indices": same,
                "max_abs_viability_difference": maxdiff,
                "endpoint_recovered": recovered,
                "reason": "ok" if recovered else ("continuation indices differ" if not same else "viability differs"),
            }
        )
    return pd.DataFrame(rows)


def _single_endpoint(map_block: pd.DataFrame, endpoint: str) -> pd.Series:
    part = map_block[map_block["endpoint_type"] == endpoint]
    if len(part) != 1:
        raise ValueError(f"expected exactly one {endpoint!r} map in each baseline block; found {len(part)}")
    return part.iloc[0]


def construct_monotone_frontier(map_block: pd.DataFrame) -> pd.DataFrame:
    """Construct a discrete upper envelope from one baseline replicate only."""
    if map_block[["condition", "baseline_replicate"]].drop_duplicates().shape[0] != 1:
        raise ValueError("construct_monotone_frontier requires exactly one baseline block")
    candidates = map_block[map_block["endpoint_type"] != "actual"].copy()
    if candidates.empty:
        raise ValueError("frontier has no intervention maps")
    candidates = candidates.sort_values(["retained_information", "viability_mean", "map_hash"], ascending=[True, False, True])

    # At an identical information coordinate, retain the best observed map.
    exact_rows = []
    for x, part in candidates.groupby("retained_information", sort=True):
        best = part.sort_values(["viability_mean", "map_hash"], ascending=[False, True]).iloc[0]
        exact_rows.append(
            {
                "retained_information": float(x),
                "point_viability": float(best["viability_mean"]),
                "point_map_hash": best["map_hash"],
                "point_method": best["method"],
                "point_endpoint_type": best["endpoint_type"],
                "n_maps_at_coordinate": int(len(part)),
            }
        )
    frontier = pd.DataFrame(exact_rows).sort_values("retained_information").reset_index(drop=True)
    running_value = -np.inf
    running_hash = None
    running_method = None
    running_endpoint = None
    values = []
    hashes = []
    methods = []
    endpoints = []
    for row in frontier.itertuples(index=False):
        if row.point_viability > running_value:
            running_value = float(row.point_viability)
            running_hash = row.point_map_hash
            running_method = row.point_method
            running_endpoint = row.point_endpoint_type
        values.append(running_value)
        hashes.append(running_hash)
        methods.append(running_method)
        endpoints.append(running_endpoint)
    frontier["frontier_viability"] = values
    frontier["frontier_source_map_hash"] = hashes
    frontier["frontier_source_method"] = methods
    frontier["frontier_source_endpoint_type"] = endpoints
    return frontier


def detect_target(frontier: pd.DataFrame, target: float) -> dict[str, Any]:
    """Detect the first tested retained-information coordinate reaching target.

    No interpolation is used: an untested information level is never reported as
    an observed semantic estimate.
    """
    if frontier.empty or not np.isfinite(target):
        raise ValueError("frontier and target must be finite")
    hit = frontier.index[frontier["frontier_viability"] >= target].to_numpy()
    max_info = float(frontier["retained_information"].max())
    if hit.size == 0:
        return {
            "target_reached": False,
            "censoring": "right_censored",
            "semantic_information": np.nan,
            "semantic_lower_bound": max_info,
        }
    x = float(frontier.loc[int(hit[0]), "retained_information"])
    return {
        "target_reached": True,
        "censoring": "none",
        "semantic_information": x,
        "semantic_lower_bound": np.nan,
    }


def analyze_replicate_frontiers(
    raw: pd.DataFrame,
    *,
    target_rule: TargetRule,
    information_atol: float = 1e-12,
    viability_atol: float = 1e-12,
    require_identity: bool = True,
) -> FrontierAnalysis:
    """Build exactly one frontier and semantic record per baseline replicate."""
    continuation = validate_continuation_table(raw)
    map_summary = aggregate_nested_continuations(continuation)
    endpoint_diag = paired_endpoint_diagnostic(continuation, atol=viability_atol)
    summary_rows = []
    frontier_frames = []

    for (condition, baseline), block in map_summary.groupby(["condition", "baseline_replicate"], sort=True):
        actual = _single_endpoint(block, "actual")
        constant = _single_endpoint(block, "constant")
        identity_part = block[block["endpoint_type"] == "identity"]
        if require_identity and len(identity_part) != 1:
            raise ValueError(f"baseline {baseline} lacks exactly one identity endpoint")
        identity = identity_part.iloc[0] if len(identity_part) == 1 else None

        frontier = construct_monotone_frontier(block)
        frontier["condition"] = condition
        frontier["baseline_replicate"] = baseline
        target = target_rule.target(float(actual["viability_mean"]), float(constant["viability_mean"]))
        detected = detect_target(frontier, target)

        if "baseline_information" in continuation.columns:
            raw_block = continuation[(continuation["condition"] == condition) & (continuation["baseline_replicate"] == baseline)]
            baseline_info = _finite_scalar(raw_block["baseline_information"], "baseline_information", atol=information_atol)
        else:
            baseline_info = float(actual["retained_information"])

        identity_info = float(identity["retained_information"]) if identity is not None else np.nan
        identity_info_ok = bool(np.isfinite(identity_info) and abs(identity_info - baseline_info) <= information_atol)
        diag = endpoint_diag[(endpoint_diag["condition"] == condition) & (endpoint_diag["baseline_replicate"] == baseline)]
        identity_viability_ok = bool(len(diag) == 1 and diag.iloc[0]["endpoint_recovered"])

        if require_identity and not identity_info_ok:
            raise ValueError(f"identity endpoint does not recover baseline information for {baseline}")
        if require_identity and not identity_viability_ok:
            raise ValueError(f"identity endpoint does not recover paired actual viability for {baseline}")

        counts = block["n_continuations"].astype(int)
        record = ReplicateFrontierRecord(
            condition=condition,
            baseline_replicate=baseline,
            target_tolerance=float(target_rule.tolerance),
            actual_viability=float(actual["viability_mean"]),
            constant_viability=float(constant["viability_mean"]),
            identity_viability=float(identity["viability_mean"]) if identity is not None else np.nan,
            value_of_information=float(actual["viability_mean"] - constant["viability_mean"]),
            target_viability=float(target),
            target_reached=bool(detected["target_reached"]),
            censoring=str(detected["censoring"]),
            semantic_information=float(detected["semantic_information"]),
            semantic_lower_bound=float(detected["semantic_lower_bound"]),
            max_retained_information=float(frontier["retained_information"].max()),
            baseline_information=float(baseline_info),
            identity_information=float(identity_info),
            identity_information_recovered=identity_info_ok,
            identity_viability_recovered=identity_viability_ok,
            n_unique_maps=int(len(block[block["endpoint_type"] != "actual"])),
            n_continuation_rows=int(
                len(continuation[(continuation["condition"] == condition) & (continuation["baseline_replicate"] == baseline)])
            ),
            min_continuations_per_map=int(counts.min()),
            max_continuations_per_map=int(counts.max()),
        )
        summary_rows.append(record.to_dict())
        frontier["target_viability"] = target
        frontier["target_reached"] = detected["target_reached"]
        frontier_frames.append(frontier)

    summary = pd.DataFrame(summary_rows)
    frontiers = pd.concat(frontier_frames, ignore_index=True) if frontier_frames else pd.DataFrame()
    return FrontierAnalysis(
        replicate_summary=summary,
        frontier_points=frontiers,
        map_summary=map_summary,
        continuation_summary=continuation,
    )


def target_reach_table(replicate_summary: pd.DataFrame) -> pd.DataFrame:
    """Machine-readable counts and fractions without imputing censored estimates."""
    _require_columns(replicate_summary, {"condition", "target_reached", "censoring"})
    rows = []
    for condition, part in replicate_summary.groupby("condition", sort=True):
        n = int(len(part))
        reached = int(part["target_reached"].astype(bool).sum())
        rows.append(
            {
                "condition": condition,
                "n_independent_replicates": n,
                "n_target_reached": reached,
                "n_right_censored": int(n - reached),
                "target_reached_fraction": float(reached / n) if n else np.nan,
            }
        )
    return pd.DataFrame(rows)


def continuation_variance_diagnostic(raw: pd.DataFrame, *, absolute_tolerance: float = 0.1) -> pd.DataFrame:
    """Quantify stabilization as continuation seeds are nested within each map."""
    if absolute_tolerance < 0:
        raise ValueError("absolute_tolerance must be non-negative")
    df = validate_continuation_table(raw)
    rows = []
    max_k = int(df.groupby(["condition", "baseline_replicate", "map_hash"]).size().min())
    if max_k < 1:
        return pd.DataFrame()
    full_means = df.groupby(["condition", "baseline_replicate", "map_hash"])["viability"].mean()
    for k in range(1, max_k + 1):
        errors = []
        ses = []
        for keys, part in df.groupby(["condition", "baseline_replicate", "map_hash"], sort=False):
            part = part.sort_values("continuation_index").iloc[:k]
            estimate = float(part["viability"].mean())
            errors.append(estimate - float(full_means.loc[keys]))
            ses.append(float(part["viability"].std(ddof=1) / math.sqrt(k)) if k > 1 else np.nan)
        errors = np.asarray(errors, dtype=float)
        ses_arr = np.asarray(ses, dtype=float)
        rows.append(
            {
                "n_continuations": k,
                "n_map_blocks": int(len(errors)),
                "rmse_vs_full_mean": float(np.sqrt(np.mean(errors**2))),
                "median_absolute_error_vs_full_mean": float(np.median(np.abs(errors))),
                "max_absolute_error_vs_full_mean": float(np.max(np.abs(errors))),
                "mean_monte_carlo_se": float(np.nanmean(ses_arr)) if np.isfinite(ses_arr).any() else np.nan,
                "fraction_within_absolute_tolerance": float(np.mean(np.abs(errors) <= absolute_tolerance)),
                "absolute_tolerance": float(absolute_tolerance),
            }
        )
    return pd.DataFrame(rows)


def _summaries_from_resampled_blocks(
    raw: pd.DataFrame,
    selected: Sequence[tuple[str, str]],
    target_rule: TargetRule,
    *,
    require_identity: bool,
) -> pd.DataFrame:
    pieces = []
    for draw_index, (condition, baseline) in enumerate(selected):
        block = raw[(raw["condition"] == condition) & (raw["baseline_replicate"] == baseline)].copy()
        block["baseline_replicate"] = f"bootstrap_{draw_index:05d}:{baseline}"
        pieces.append(block)
    sampled = pd.concat(pieces, ignore_index=True)
    return analyze_replicate_frontiers(
        sampled, target_rule=target_rule, require_identity=require_identity
    ).replicate_summary


def block_bootstrap(
    raw: pd.DataFrame,
    *,
    target_rule: TargetRule,
    n_bootstrap: int,
    stream: AnalysisStream,
    confidence_level: float = 0.95,
    require_identity: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Resample complete evolved-replicate blocks and recompute frontiers."""
    if n_bootstrap < 1:
        raise ValueError("n_bootstrap must be positive")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must lie in (0,1)")
    df = validate_continuation_table(raw)
    unique_blocks = df[["condition", "baseline_replicate"]].drop_duplicates()
    blocks_by_condition = {
        condition: list(part[["condition", "baseline_replicate"]].itertuples(index=False, name=None))
        for condition, part in unique_blocks.groupby("condition", sort=True)
    }
    observed = analyze_replicate_frontiers(
        df, target_rule=target_rule, require_identity=require_identity
    ).replicate_summary
    rng = stream.generator()
    draws = []
    for b in range(n_bootstrap):
        selected = []
        for condition, blocks in blocks_by_condition.items():
            choice = rng.integers(0, len(blocks), size=len(blocks))
            selected.extend(blocks[i] for i in choice)
        summaries = _summaries_from_resampled_blocks(
            df, selected, target_rule, require_identity=require_identity
        )
        for condition, part in summaries.groupby("condition", sort=True):
            reached = part[part["target_reached"]]
            censored = part[~part["target_reached"]]
            draws.append(
                {
                    "bootstrap_index": b,
                    "condition": condition,
                    "reach_fraction": float(part["target_reached"].mean()),
                    "median_semantic_information_among_reached": float(reached["semantic_information"].median()) if len(reached) else np.nan,
                    "median_censored_lower_bound": float(censored["semantic_lower_bound"].median()) if len(censored) else np.nan,
                    "mean_value_of_information": float(part["value_of_information"].mean()),
                    "n_reached": int(len(reached)),
                    "n_censored": int(len(censored)),
                }
            )
    draws_df = pd.DataFrame(draws)
    alpha = (1.0 - confidence_level) / 2.0
    interval_rows = []
    metric_specs = {
        "reach_fraction": "All independent replicates; censoring retained as target_reached=False.",
        "median_semantic_information_among_reached": "Conditional on target-reached replicates; censored values are not imputed.",
        "median_censored_lower_bound": "Conditional on right-censored replicates; reports their tested lower bounds.",
        "mean_value_of_information": "Defined for every independent replicate.",
    }
    for condition, observed_part in observed.groupby("condition", sort=True):
        obs_reached = observed_part[observed_part["target_reached"]]
        obs_censored = observed_part[~observed_part["target_reached"]]
        observed_metrics = {
            "reach_fraction": float(observed_part["target_reached"].mean()),
            "median_semantic_information_among_reached": float(obs_reached["semantic_information"].median()) if len(obs_reached) else np.nan,
            "median_censored_lower_bound": float(obs_censored["semantic_lower_bound"].median()) if len(obs_censored) else np.nan,
            "mean_value_of_information": float(observed_part["value_of_information"].mean()),
        }
        part_draws = draws_df[draws_df["condition"] == condition]
        for metric, note in metric_specs.items():
            vals = part_draws[metric].dropna().to_numpy(dtype=float)
            lower = float(np.quantile(vals, alpha)) if len(vals) else np.nan
            upper = float(np.quantile(vals, 1 - alpha)) if len(vals) else np.nan
            interval_rows.append(
                {
                    "condition": condition,
                    **BootstrapInterval(
                        metric=metric,
                        estimate=observed_metrics[metric],
                        confidence_level=float(confidence_level),
                        lower=lower,
                        upper=upper,
                        n_independent_replicates=int(len(observed_part)),
                        n_bootstrap=int(n_bootstrap),
                        note=note,
                    ).to_dict(),
                }
            )
    return pd.DataFrame(interval_rows), draws_df


def _statistic(values_a: np.ndarray, values_b: np.ndarray, name: str) -> float:
    if name == "mean_difference":
        return float(np.mean(values_a) - np.mean(values_b))
    if name == "median_difference":
        return float(np.median(values_a) - np.median(values_b))
    raise ValueError(f"unknown statistic: {name}")


def replicate_level_permutation_test(
    replicate_summary: pd.DataFrame,
    *,
    metric: str,
    group_a: str,
    group_b: str,
    stream: AnalysisStream,
    statistic: str = "mean_difference",
    n_permutations: int = 9999,
    paired_by: str | None = None,
    max_exact_assignments: int = 100_000,
) -> PermutationResult:
    """Permute only replicate-level values; nested map/seed rows are forbidden."""
    _require_columns(replicate_summary, {"condition", "baseline_replicate", metric})
    if replicate_summary.duplicated(["condition", "baseline_replicate"]).any():
        raise ValueError("replicate-level permutation input has duplicate baseline blocks")
    work = replicate_summary[replicate_summary["condition"].isin([group_a, group_b])].copy()
    if work[metric].isna().any():
        raise ValueError(
            f"metric {metric!r} contains censored/missing values; test target_reached or an always-defined metric instead"
        )
    work[metric] = work[metric].astype(float)
    rng = stream.generator()

    if paired_by is not None:
        _require_columns(work, {paired_by})
        pivot = work.pivot(index=paired_by, columns="condition", values=metric)
        if group_a not in pivot or group_b not in pivot or pivot[[group_a, group_b]].isna().any().any():
            raise ValueError("paired permutation requires complete one-to-one pairs")
        diffs = (pivot[group_a] - pivot[group_b]).to_numpy(dtype=float)
        observed = float(np.mean(diffs)) if statistic == "mean_difference" else float(np.median(diffs))
        n = len(diffs)
        exact_count = 2**n
        if exact_count <= max_exact_assignments:
            permuted = np.asarray([
                np.mean(diffs * np.asarray(signs)) if statistic == "mean_difference" else np.median(diffs * np.asarray(signs))
                for signs in product([-1.0, 1.0], repeat=n)
            ])
            exact = True
        else:
            signs = rng.choice(np.array([-1.0, 1.0]), size=(n_permutations, n))
            permuted = np.mean(signs * diffs, axis=1) if statistic == "mean_difference" else np.median(signs * diffs, axis=1)
            exact = False
        p = float(np.mean(np.abs(permuted) >= abs(observed))) if exact else float((1 + np.sum(np.abs(permuted) >= abs(observed))) / (len(permuted) + 1))
        return PermutationResult(
            metric=metric,
            statistic=statistic,
            observed_difference=observed,
            p_value_two_sided=p,
            group_a=group_a,
            group_b=group_b,
            n_group_a=n,
            n_group_b=n,
            n_permutations=int(len(permuted)),
            exact=exact,
            paired=True,
        )

    a = work.loc[work["condition"] == group_a, metric].to_numpy(dtype=float)
    b = work.loc[work["condition"] == group_b, metric].to_numpy(dtype=float)
    if len(a) < 1 or len(b) < 1:
        raise ValueError("both groups require at least one independent replicate")
    observed = _statistic(a, b, statistic)
    pooled = np.concatenate([a, b])
    n_a = len(a)
    assignments = math.comb(len(pooled), n_a)
    if assignments <= max_exact_assignments:
        vals = []
        all_idx = np.arange(len(pooled))
        for idx_a in combinations(all_idx, n_a):
            mask = np.zeros(len(pooled), dtype=bool)
            mask[list(idx_a)] = True
            vals.append(_statistic(pooled[mask], pooled[~mask], statistic))
        permuted = np.asarray(vals, dtype=float)
        exact = True
        p = float(np.mean(np.abs(permuted) >= abs(observed)))
    else:
        permuted = np.empty(n_permutations, dtype=float)
        for i in range(n_permutations):
            order = rng.permutation(len(pooled))
            permuted[i] = _statistic(pooled[order[:n_a]], pooled[order[n_a:]], statistic)
        exact = False
        p = float((1 + np.sum(np.abs(permuted) >= abs(observed))) / (n_permutations + 1))
    return PermutationResult(
        metric=metric,
        statistic=statistic,
        observed_difference=observed,
        p_value_two_sided=p,
        group_a=group_a,
        group_b=group_b,
        n_group_a=int(len(a)),
        n_group_b=int(len(b)),
        n_permutations=int(len(permuted)),
        exact=exact,
        paired=False,
    )
