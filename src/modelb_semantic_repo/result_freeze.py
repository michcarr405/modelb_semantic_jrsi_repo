from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .phase4 import Phase4Settings, _bh_adjust as phase4_bh_adjust
from .phase5 import (
    Phase5Settings,
    _aggregate_realizations,
    _bh_adjust as phase5_bh_adjust,
    paired_bootstrap_interval,
    paired_sign_randomization,
)
from .phase6 import Settings as Phase6Settings
from .phase6 import boot as phase6_boot
from .phase6 import summarize as phase6_summarize
from .rng import AnalysisStream, make_generator
from .statistical_pipeline import replicate_level_permutation_test

PHASE_ROOTS = {
    "phase4": Path("results/phase4_core"),
    "phase5": Path("results/phase5_causal_specificity"),
    "phase6": Path("results/phase6_generality"),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _category(relative_path: str) -> str:
    name = Path(relative_path).name.lower()
    parts = Path(relative_path).parts
    if name == "file_manifest_sha256.csv":
        return "self_manifest"
    if "state" in parts or name.endswith(".npz"):
        return "archived_state_or_array"
    if "continuation" in name or "continuation_blocks" in parts or "stage_d_blocks" in parts:
        return "continuation_record"
    if "seed" in name or "ledger" in name:
        return "seed_or_provenance_record"
    if "frontier" in name:
        return "frontier_record"
    if "bootstrap" in name:
        return "bootstrap_record"
    if "permutation" in name or "contrast" in name:
        return "inferential_record"
    if "gate_" in name or name.startswith("gate"):
        return "gate_decision"
    if "manifest" in name:
        return "manifest"
    if "design" in name or "settings" in name or "specification" in name:
        return "design_or_settings"
    if "summary" in name or "counts" in name:
        return "summary_record"
    if name.endswith(".json"):
        return "json_record"
    if name.endswith(".csv"):
        return "tabular_record"
    return "other"


def _inspect_file(path: Path) -> tuple[int | None, int | None, str]:
    try:
        if path.suffix.lower() == ".csv":
            frame = pd.read_csv(path)
            return len(frame), len(frame.columns), json.dumps(list(frame.columns))
        if path.suffix.lower() == ".json":
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                return 1, len(obj), json.dumps(list(obj.keys()))
            if isinstance(obj, list):
                keys: list[str] = []
                if obj and isinstance(obj[0], dict):
                    keys = list(obj[0].keys())
                return len(obj), len(keys) if keys else None, json.dumps(keys)
    except Exception as exc:  # pragma: no cover - inventory records the exception
        return None, None, json.dumps({"inspection_error": str(exc)})
    return None, None, ""


def build_result_inventory(repo_root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for phase, rel_root in PHASE_ROOTS.items():
        root = repo_root / rel_root
        manifest_path = root / "FILE_MANIFEST_SHA256.csv"
        manifest = pd.read_csv(manifest_path)
        expected = manifest.set_index("relative_path").to_dict("index")
        actual = {
            path.relative_to(root).as_posix(): path
            for path in root.rglob("*")
            if path.is_file() and path.name != "FILE_MANIFEST_SHA256.csv"
        }
        for relative_path in sorted(set(actual) | set(expected)):
            path = actual.get(relative_path)
            exp = expected.get(relative_path)
            exists = path is not None and path.exists()
            size = path.stat().st_size if exists else None
            digest = sha256_file(path) if exists else ""
            row_count, column_count, schema = _inspect_file(path) if exists else (None, None, "")
            in_manifest = exp is not None
            rows.append(
                {
                    "phase": phase,
                    "archive_root": rel_root.as_posix(),
                    "relative_path": relative_path,
                    "category": _category(relative_path),
                    "exists": exists,
                    "in_manifest": in_manifest,
                    "expected_size_bytes": int(exp["size_bytes"]) if exp else None,
                    "actual_size_bytes": size,
                    "size_matches": bool(exists and exp and size == int(exp["size_bytes"])),
                    "expected_sha256": str(exp["sha256"]) if exp else "",
                    "actual_sha256": digest,
                    "hash_matches": bool(exists and exp and digest == str(exp["sha256"])),
                    "file_format": path.suffix.lower().lstrip(".") if exists else Path(relative_path).suffix.lower().lstrip("."),
                    "row_count": row_count,
                    "column_count": column_count,
                    "schema_or_keys_json": schema,
                }
            )
        # Self-manifest is deliberately not listed in itself.
        size = manifest_path.stat().st_size
        digest = sha256_file(manifest_path)
        row_count, column_count, schema = _inspect_file(manifest_path)
        rows.append(
            {
                "phase": phase,
                "archive_root": rel_root.as_posix(),
                "relative_path": "FILE_MANIFEST_SHA256.csv",
                "category": "self_manifest",
                "exists": True,
                "in_manifest": False,
                "expected_size_bytes": None,
                "actual_size_bytes": size,
                "size_matches": True,
                "expected_sha256": "",
                "actual_sha256": digest,
                "hash_matches": True,
                "file_format": "csv",
                "row_count": row_count,
                "column_count": column_count,
                "schema_or_keys_json": schema,
            }
        )
    inventory = pd.DataFrame(rows)
    return inventory.sort_values(["phase", "relative_path", "category"]).reset_index(drop=True)


def _write_source(frame: pd.DataFrame, path: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return {
        "table_name": path.name,
        "relative_path": path.as_posix(),
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "sha256": sha256_file(path),
    }


def build_figure_sources(repo_root: Path, outdir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    source_dir = outdir / "figure_sources"
    source_dir.mkdir(parents=True, exist_ok=True)
    catalog: list[dict[str, Any]] = []
    verification: list[dict[str, Any]] = []

    p4 = repo_root / PHASE_ROOTS["phase4"]
    p5 = repo_root / PHASE_ROOTS["phase5"]
    p6 = repo_root / PHASE_ROOTS["phase6"]

    core_info = pd.read_csv(p4 / "baseline_information.csv")
    core_info_cols = [
        "condition", "inherit_prob", "replicate", "baseline_replicate", "final_mean_fitness",
        "total_information", "positional_information", "conditional_information",
        "permutation_mean", "permutation_std", "corrected_conditional_information",
    ]
    core_info_source = core_info[core_info_cols].copy()
    core_info_source.insert(0, "source_file", "results/phase4_core/baseline_information.csv")
    meta = _write_source(core_info_source, source_dir / "core_information_replicates.csv")
    catalog.append({**meta, "intended_evidence": "Corrected information hierarchy across fidelity and regimes", "derivation": "Exact selected columns; no aggregation", "source_files": "results/phase4_core/baseline_information.csv"})
    verification.append({"table_name": meta["table_name"], "check": "exact_selected_columns", "passed": core_info_source.drop(columns="source_file").equals(core_info[core_info_cols])})

    core_frontier = pd.read_csv(p4 / "replicate_frontier_summary.csv")
    core_frontier_source = core_frontier.copy()
    core_frontier_source.insert(0, "source_file", "results/phase4_core/replicate_frontier_summary.csv")
    meta = _write_source(core_frontier_source, source_dir / "core_semantic_replicates.csv")
    catalog.append({**meta, "intended_evidence": "Replicate-specific value of information, semantic estimates, targets, and censoring", "derivation": "Exact copy with source provenance", "source_files": "results/phase4_core/replicate_frontier_summary.csv"})
    verification.append({"table_name": meta["table_name"], "check": "exact_copy", "passed": core_frontier_source.drop(columns="source_file").equals(core_frontier)})

    core_points = pd.read_csv(p4 / "replicate_frontiers.csv")
    core_points_source = core_points.copy()
    core_points_source.insert(0, "source_file", "results/phase4_core/replicate_frontiers.csv")
    meta = _write_source(core_points_source, source_dir / "core_frontier_points.csv")
    catalog.append({**meta, "intended_evidence": "Discrete monotone information-viability frontiers for raw replicate display", "derivation": "Exact copy with source provenance", "source_files": "results/phase4_core/replicate_frontiers.csv"})
    verification.append({"table_name": meta["table_name"], "check": "exact_copy", "passed": core_points_source.drop(columns="source_file").equals(core_points)})

    p4_perm = pd.read_csv(p4 / "replicate_level_permutation_results.csv")
    p4_boot = pd.read_csv(p4 / "block_bootstrap_intervals.csv")
    p4_reach = pd.read_csv(p4 / "target_reach_counts.csv")
    p4_perm.insert(0, "record_type", "replicate_permutation")
    p4_boot.insert(0, "record_type", "block_bootstrap_interval")
    p4_reach.insert(0, "record_type", "target_reach_count")
    # Preserve heterogeneous schemas in one long, analysis-ready table.
    core_inference = pd.concat([p4_perm, p4_boot, p4_reach], ignore_index=True, sort=False)
    meta = _write_source(core_inference, source_dir / "core_inference_records.csv")
    catalog.append({**meta, "intended_evidence": "Core confidence intervals, replicate-level tests, and target-reaching fractions", "derivation": "Row-wise union with record_type; values unchanged", "source_files": "results/phase4_core/replicate_level_permutation_results.csv; results/phase4_core/block_bootstrap_intervals.csv; results/phase4_core/target_reach_counts.csv"})
    verification.append({"table_name": meta["table_name"], "check": "component_row_counts", "passed": len(core_inference) == len(p4_perm) + len(p4_boot) + len(p4_reach)})

    p5_metrics = pd.read_csv(p5 / "gate5_seed_block_metrics.csv")
    metric_columns = [
        "native_full_voi", "selection_neutral", "selection_reduced", "affinity_reassigned",
        "topology_mismatch", "alternative_a_native", "alternative_a_cross_b",
        "alternative_b_native", "alternative_b_cross_a", "temporally_unstable",
        "alternative_native_mean", "alternative_cross_mean",
    ]
    causal_long = p5_metrics[["seed_block", *metric_columns]].melt(
        id_vars="seed_block", var_name="control_or_reference", value_name="value_of_information"
    )
    causal_long.insert(0, "source_file", "results/phase5_causal_specificity/gate5_seed_block_metrics.csv")
    meta = _write_source(causal_long, source_dir / "causal_specificity_seed_blocks.csv")
    catalog.append({**meta, "intended_evidence": "Matched seed-block value-of-information distributions for causal controls", "derivation": "Deterministic wide-to-long reshape", "source_files": "results/phase5_causal_specificity/gate5_seed_block_metrics.csv"})
    reconstructed = causal_long.drop(columns="source_file").pivot(index="seed_block", columns="control_or_reference", values="value_of_information").reset_index()
    verification.append({"table_name": meta["table_name"], "check": "wide_long_roundtrip", "passed": all(np.allclose(reconstructed[c], p5_metrics[c]) for c in metric_columns)})

    p5_contrasts = pd.read_csv(p5 / "gate5_paired_contrasts.csv")
    p5_contrasts_source = p5_contrasts.copy()
    p5_contrasts_source.insert(0, "source_file", "results/phase5_causal_specificity/gate5_paired_contrasts.csv")
    meta = _write_source(p5_contrasts_source, source_dir / "causal_specificity_contrasts.csv")
    catalog.append({**meta, "intended_evidence": "Six prespecified paired causal-specificity contrasts", "derivation": "Exact copy with source provenance", "source_files": "results/phase5_causal_specificity/gate5_paired_contrasts.csv"})
    verification.append({"table_name": meta["table_name"], "check": "exact_copy", "passed": p5_contrasts_source.drop(columns="source_file").equals(p5_contrasts)})

    screen_reps = pd.concat(
        [
            pd.read_csv(p6 / "stage_a_replicates.csv"),
            pd.read_csv(p6 / "stage_b1_replicates.csv"),
            pd.read_csv(p6 / "stage_b2_replicates.csv"),
        ],
        ignore_index=True,
    )
    screen_reps.insert(0, "source_file", screen_reps["stage"].map({"A": "results/phase6_generality/stage_a_replicates.csv", "B1": "results/phase6_generality/stage_b1_replicates.csv", "B2": "results/phase6_generality/stage_b2_replicates.csv"}))
    meta = _write_source(screen_reps, source_dir / "generality_screen_replicates.csv")
    catalog.append({**meta, "intended_evidence": "Raw independent replicate data for focused, global, and structural robustness", "derivation": "Exact row union with stage-specific source provenance", "source_files": "results/phase6_generality/stage_a_replicates.csv; results/phase6_generality/stage_b1_replicates.csv; results/phase6_generality/stage_b2_replicates.csv"})
    verification.append({"table_name": meta["table_name"], "check": "expected_rows", "passed": len(screen_reps) == 128 + 48 + 68})

    screen_summary = pd.read_csv(p6 / "stage_ab_summary.csv")
    screen_summary_source = screen_summary.copy()
    screen_summary_source.insert(0, "source_file", "results/phase6_generality/stage_ab_summary.csv")
    meta = _write_source(screen_summary_source, source_dir / "generality_screen_summary.csv")
    catalog.append({**meta, "intended_evidence": "Regime map and structural-family summaries with bootstrap intervals", "derivation": "Exact copy with source provenance", "source_files": "results/phase6_generality/stage_ab_summary.csv"})
    verification.append({"table_name": meta["table_name"], "check": "exact_copy", "passed": screen_summary_source.drop(columns="source_file").equals(screen_summary)})

    protocol = pd.read_csv(p6 / "stage_c_protocol_summary.csv")
    protocol_source = protocol.copy()
    protocol_source.insert(0, "source_file", "results/phase6_generality/stage_c_protocol_summary.csv")
    meta = _write_source(protocol_source, source_dir / "generality_protocol_summary.csv")
    catalog.append({**meta, "intended_evidence": "Duration and intervention-horizon sensitivity", "derivation": "Exact copy with source provenance", "source_files": "results/phase6_generality/stage_c_protocol_summary.csv"})
    verification.append({"table_name": meta["table_name"], "check": "exact_copy", "passed": protocol_source.drop(columns="source_file").equals(protocol)})

    drep = pd.read_csv(p6 / "stage_d_replicate_summary.csv")
    drep_source = drep.copy()
    drep_source.insert(0, "source_file", "results/phase6_generality/stage_d_replicate_summary.csv")
    meta = _write_source(drep_source, source_dir / "generality_confirmatory_replicates.csv")
    catalog.append({**meta, "intended_evidence": "Full semantic confirmation for nondefault representatives", "derivation": "Exact copy with source provenance", "source_files": "results/phase6_generality/stage_d_replicate_summary.csv"})
    verification.append({"table_name": meta["table_name"], "check": "exact_copy", "passed": drep_source.drop(columns="source_file").equals(drep)})

    dsum = pd.read_csv(p6 / "stage_d_summary.csv")
    dsum_source = dsum.copy()
    dsum_source.insert(0, "source_file", "results/phase6_generality/stage_d_summary.csv")
    meta = _write_source(dsum_source, source_dir / "generality_confirmatory_summary.csv")
    catalog.append({**meta, "intended_evidence": "Confirmatory value-of-information intervals and positivity decisions", "derivation": "Exact copy with source provenance", "source_files": "results/phase6_generality/stage_d_summary.csv"})
    verification.append({"table_name": meta["table_name"], "check": "exact_copy", "passed": dsum_source.drop(columns="source_file").equals(dsum)})

    catalog_frame = pd.DataFrame(catalog).sort_values("table_name").reset_index(drop=True)
    verification_frame = pd.DataFrame(verification).sort_values(["table_name", "check"]).reset_index(drop=True)
    return catalog_frame, verification_frame


def _audit_row(check_id: str, phase: str, category: str, passed: bool, expected: Any, observed: Any, source_files: str, tolerance: str = "exact") -> dict[str, Any]:
    return {
        "check_id": check_id,
        "phase": phase,
        "category": category,
        "passed": bool(passed),
        "expected": json.dumps(expected, sort_keys=True, default=str),
        "observed": json.dumps(observed, sort_keys=True, default=str),
        "tolerance": tolerance,
        "source_files": source_files,
    }


def _frames_close(left: pd.DataFrame, right: pd.DataFrame, keys: Iterable[str], numeric_atol: float = 1e-12) -> tuple[bool, str]:
    keys = list(keys)
    l = left.sort_values(keys).reset_index(drop=True)
    r = right.sort_values(keys).reset_index(drop=True)
    if list(l.columns) != list(r.columns) or len(l) != len(r):
        return False, f"shape/columns differ: {l.shape} versus {r.shape}"
    for col in l.columns:
        if pd.api.types.is_numeric_dtype(l[col]) and pd.api.types.is_numeric_dtype(r[col]):
            if not np.allclose(l[col].to_numpy(float), r[col].to_numpy(float), rtol=0, atol=numeric_atol, equal_nan=True):
                return False, f"numeric mismatch in {col}"
        else:
            if not l[col].fillna("<NA>").astype(str).equals(r[col].fillna("<NA>").astype(str)):
                return False, f"value mismatch in {col}"
    return True, "all values match"


def audit_inferential_records(repo_root: Path, validation_dir: Path) -> pd.DataFrame:
    validation_dir.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    # Archive integrity and coverage.
    inventory = build_result_inventory(repo_root)
    inventory.to_csv(validation_dir / "result_inventory_recomputed.csv", index=False)
    for phase in PHASE_ROOTS:
        part = inventory[inventory["phase"] == phase]
        nonself = part[part["relative_path"] != "FILE_MANIFEST_SHA256.csv"]
        passed = bool(nonself["exists"].all() and nonself["in_manifest"].all() and nonself["size_matches"].all() and nonself["hash_matches"].all())
        checks.append(_audit_row(f"{phase}_archive_integrity", phase, "archive", passed, "all manifested files exist and match", {"n": len(nonself), "matches": int(nonself["hash_matches"].sum())}, str(PHASE_ROOTS[phase] / "FILE_MANIFEST_SHA256.csv")))
        actual_unmanifested = part[(part["relative_path"] != "FILE_MANIFEST_SHA256.csv") & ~part["in_manifest"]]
        checks.append(_audit_row(f"{phase}_manifest_coverage", phase, "archive", actual_unmanifested.empty, 0, len(actual_unmanifested), str(PHASE_ROOTS[phase])))

    # Phase 4 counts, endpoint integrity, bootstrap, and permutation inference.
    p4 = repo_root / PHASE_ROOTS["phase4"]
    settings4 = Phase4Settings(**json.loads((p4 / "phase4_settings.json").read_text()))
    baseline = pd.read_csv(p4 / "baseline_information.csv")
    raw4 = pd.read_csv(p4 / "continuation_level_results.csv")
    rep4 = pd.read_csv(p4 / "replicate_frontier_summary.csv")
    manifest4 = pd.read_csv(p4 / "maps/grouping_map_manifest.csv")
    checks.append(_audit_row("p4_baseline_count", "phase4", "structure", len(baseline) == 400, 400, len(baseline), "results/phase4_core/baseline_information.csv"))
    checks.append(_audit_row("p4_continuation_count", "phase4", "structure", len(raw4) == 28000, 28000, len(raw4), "results/phase4_core/continuation_level_results.csv"))
    per_block = raw4.groupby("baseline_replicate").size()
    expected_per_block = (len(manifest4) + 1) * settings4.continuation_count
    checks.append(_audit_row("p4_nested_continuations", "phase4", "structure", bool(per_block.eq(expected_per_block).all()), expected_per_block, per_block.value_counts().to_dict(), "results/phase4_core/continuation_level_results.csv; results/phase4_core/maps/grouping_map_manifest.csv"))
    identity_ok = bool(rep4["identity_information_recovered"].all() and rep4["identity_viability_recovered"].all())
    checks.append(_audit_row("p4_identity_endpoints", "phase4", "endpoint", identity_ok, True, identity_ok, "results/phase4_core/replicate_frontier_summary.csv"))

    reach_stored = pd.read_csv(p4 / "target_reach_counts.csv")
    reach_calc = (
        rep4.groupby(["inherit_prob", "condition"], as_index=False)
        .agg(n_independent_replicates=("baseline_replicate", "size"), n_target_reached=("target_reached", "sum"))
    )
    reach_calc["n_right_censored"] = reach_calc["n_independent_replicates"] - reach_calc["n_target_reached"]
    reach_calc["target_reached_fraction"] = reach_calc["n_target_reached"] / reach_calc["n_independent_replicates"]
    ok, detail = _frames_close(reach_calc[reach_stored.columns], reach_stored, ["inherit_prob", "condition"])
    reach_calc.to_csv(validation_dir / "phase4_target_reach_recomputed.csv", index=False)
    checks.append(_audit_row("p4_target_censoring_records", "phase4", "censoring", ok, "stored target table", detail, "results/phase4_core/replicate_frontier_summary.csv; results/phase4_core/target_reach_counts.csv"))

    draws4 = pd.read_csv(p4 / "block_bootstrap_draws.csv")
    intervals4 = pd.read_csv(p4 / "block_bootstrap_intervals.csv")
    recomputed_intervals = []
    notes = intervals4.set_index(["inherit_prob", "condition", "metric"])["note"].to_dict()
    for (prob, condition), part in rep4.groupby(["inherit_prob", "condition"]):
        d = draws4[(np.isclose(draws4["inherit_prob"], prob)) & (draws4["condition"] == condition)]
        estimates = {
            "reach_fraction": float(part["target_reached"].mean()),
            "median_semantic_information_among_reached": float(part.loc[part["target_reached"].astype(bool), "semantic_information"].median()),
            "median_censored_lower_bound": float(part.loc[~part["target_reached"].astype(bool), "semantic_lower_bound"].median()) if (~part["target_reached"].astype(bool)).any() else np.nan,
            "mean_value_of_information": float(part["value_of_information"].mean()),
        }
        for metric, estimate in estimates.items():
            values = d[metric].dropna().to_numpy(float)
            recomputed_intervals.append({
                "inherit_prob": prob, "condition": condition, "metric": metric, "estimate": estimate,
                "confidence_level": 0.95,
                "lower": float(np.quantile(values, 0.025)) if len(values) else np.nan,
                "upper": float(np.quantile(values, 0.975)) if len(values) else np.nan,
                "n_independent_replicates": len(part), "n_bootstrap": settings4.n_bootstrap,
                "note": notes[(prob, condition, metric)],
            })
    recomputed_intervals = pd.DataFrame(recomputed_intervals)
    ok, detail = _frames_close(recomputed_intervals[intervals4.columns], intervals4, ["inherit_prob", "condition", "metric"], 1e-12)
    recomputed_intervals.to_csv(validation_dir / "phase4_bootstrap_intervals_recomputed.csv", index=False)
    checks.append(_audit_row("p4_bootstrap_intervals", "phase4", "inference", ok, "80 stored intervals", detail, "results/phase4_core/block_bootstrap_draws.csv; results/phase4_core/block_bootstrap_intervals.csv"))

    perm_rows = []
    for prob in sorted(rep4["inherit_prob"].unique()):
        info_part = baseline[np.isclose(baseline["inherit_prob"], prob)][["condition", "baseline_replicate", "corrected_conditional_information"]]
        tests = [
            replicate_level_permutation_test(info_part, metric="corrected_conditional_information", group_a="selective", group_b="control", stream=AnalysisStream(settings4.root_seed, "phase4-replicate-permutation", f"corrected-info-p{prob:.1f}"), n_permutations=settings4.n_inference_permutations),
            replicate_level_permutation_test(rep4[np.isclose(rep4["inherit_prob"], prob)], metric="value_of_information", group_a="selective", group_b="control", stream=AnalysisStream(settings4.root_seed, "phase4-replicate-permutation", f"voi-p{prob:.1f}"), n_permutations=settings4.n_inference_permutations),
            replicate_level_permutation_test(rep4[np.isclose(rep4["inherit_prob"], prob)], metric="semantic_information", group_a="selective", group_b="control", stream=AnalysisStream(settings4.root_seed, "phase4-replicate-permutation", f"semantic-p{prob:.1f}"), n_permutations=settings4.n_inference_permutations),
        ]
        perm_rows.extend({"inherit_prob": prob, **test.to_dict(), "status": "performed"} for test in tests)
    perm_calc = pd.DataFrame(perm_rows)
    for metric, idx in perm_calc.groupby("metric").groups.items():
        perm_calc.loc[idx, "q_value_bh_across_fidelities"] = phase4_bh_adjust(perm_calc.loc[idx, "p_value_two_sided"])
    perm_stored = pd.read_csv(p4 / "replicate_level_permutation_results.csv")
    perm_calc = perm_calc[perm_stored.columns]
    ok, detail = _frames_close(perm_calc, perm_stored, ["inherit_prob", "metric"], 1e-12)
    perm_calc.to_csv(validation_dir / "phase4_permutation_results_recomputed.csv", index=False)
    checks.append(_audit_row("p4_permutation_inference", "phase4", "inference", ok, "30 stored tests", detail, "results/phase4_core/baseline_information.csv; results/phase4_core/replicate_frontier_summary.csv; results/phase4_core/replicate_level_permutation_results.csv"))

    gate4 = json.loads((p4 / "GATE_4_DECISION.json").read_text())
    p1 = perm_calc[np.isclose(perm_calc["inherit_prob"], 1.0)].set_index("metric")
    gate4_recomputed = {
        "status": "PASSED" if identity_ok else "FAILED",
        "corrected_information_observed_difference_selective_minus_control": float(p1.loc["corrected_conditional_information", "observed_difference"]),
        "corrected_information_p_value": float(p1.loc["corrected_conditional_information", "p_value_two_sided"]),
        "value_of_information_observed_difference_selective_minus_control": float(p1.loc["value_of_information", "observed_difference"]),
        "value_of_information_p_value": float(p1.loc["value_of_information", "p_value_two_sided"]),
    }
    gate4_ok = all(
        gate4[k] == v if isinstance(v, str) else np.isclose(gate4[k], v, rtol=0, atol=1e-15)
        for k, v in gate4_recomputed.items()
    )
    checks.append(_audit_row("gate4_primary_records", "phase4", "gate", gate4_ok, gate4_recomputed, {k: gate4[k] for k in gate4_recomputed}, "results/phase4_core/GATE_4_DECISION.json; validation/result_freeze/phase4_permutation_results_recomputed.csv"))

    # Phase 5 aggregation, paired tests, bootstrap, target/censoring, and gate.
    p5 = repo_root / PHASE_ROOTS["phase5"]
    settings5 = Phase5Settings(**json.loads((p5 / "phase5_settings.json").read_text()))
    raw5 = pd.read_csv(p5 / "continuation_level_results.csv")
    realization5 = pd.read_csv(p5 / "realization_frontier_summary.csv")
    specs5 = pd.DataFrame(json.loads((p5 / "evaluation_specifications.json").read_text()))
    stored_agg = pd.read_csv(p5 / "seed_block_control_summary.csv")
    calc_agg = _aggregate_realizations(realization5, specs5)
    ok, detail = _frames_close(calc_agg[stored_agg.columns], stored_agg, ["control_family", "seed_block"], 1e-12)
    calc_agg.to_csv(validation_dir / "phase5_seed_block_control_summary_recomputed.csv", index=False)
    checks.append(_audit_row("p5_seed_block_aggregation", "phase5", "inference", ok, "stored seed-block aggregation", detail, "results/phase5_causal_specificity/realization_frontier_summary.csv; results/phase5_causal_specificity/evaluation_specifications.json; results/phase5_causal_specificity/seed_block_control_summary.csv"))
    checks.append(_audit_row("p5_continuation_count", "phase5", "structure", len(raw5) == 15400, 15400, len(raw5), "results/phase5_causal_specificity/continuation_level_results.csv"))
    checks.append(_audit_row("p5_nested_continuations", "phase5", "structure", bool(raw5.groupby(["baseline_replicate", "map_hash"]).size().eq(2).all()), 2, raw5.groupby(["baseline_replicate", "map_hash"]).size().value_counts().to_dict(), "results/phase5_causal_specificity/continuation_level_results.csv"))
    p5_identity = bool(realization5["identity_information_recovered"].all() and realization5["identity_viability_recovered"].all())
    checks.append(_audit_row("p5_identity_endpoints", "phase5", "endpoint", p5_identity, True, p5_identity, "results/phase5_causal_specificity/realization_frontier_summary.csv"))

    phase4_native = rep4[(rep4["condition"] == "selective") & np.isclose(rep4["inherit_prob"], 1.0)].copy()
    phase4_native["seed_block"] = phase4_native["baseline_replicate"].str.extract(r"r(\d+)$")[0].astype(int)
    native = phase4_native[["seed_block", "value_of_information", "target_reached", "semantic_information", "semantic_lower_bound"]].rename(columns={"value_of_information": "native_full_voi"})
    wide = calc_agg.pivot(index="seed_block", columns="control_family", values="mean_value_of_information").reset_index()
    metrics = native.merge(wide, on="seed_block", validate="one_to_one")
    metrics["alternative_native_mean"] = 0.5 * (metrics["alternative_a_native"] + metrics["alternative_b_native"])
    metrics["alternative_cross_mean"] = 0.5 * (metrics["alternative_a_cross_b"] + metrics["alternative_b_cross_a"])
    contrast_specs = [
        ("full_minus_neutral", "native_full_voi", "selection_neutral"),
        ("full_minus_reduced", "native_full_voi", "selection_reduced"),
        ("native_minus_affinity_reassigned", "native_full_voi", "affinity_reassigned"),
        ("native_minus_topology_mismatch", "native_full_voi", "topology_mismatch"),
        ("alternative_native_minus_cross", "alternative_native_mean", "alternative_cross_mean"),
        ("stable_minus_unstable", "alternative_native_mean", "temporally_unstable"),
    ]
    contrast_rows = []
    draw_frames = []
    for name, a, b in contrast_specs:
        diffs = (metrics[a] - metrics[b]).to_numpy(float)
        metrics[f"contrast_{name}"] = diffs
        test = paired_sign_randomization(diffs, stream=AnalysisStream(settings5.root_seed, "phase5-paired-randomization", name), n_permutations=settings5.n_inference_permutations)
        lower, upper, draws = paired_bootstrap_interval(diffs, stream=AnalysisStream(settings5.root_seed, "phase5-paired-bootstrap", name), n_bootstrap=settings5.n_bootstrap)
        contrast_rows.append({"contrast": name, **test, "bootstrap_95_lower": lower, "bootstrap_95_upper": upper, "analysis_unit": "matched independently evolved seed block"})
        draw_frames.append(pd.DataFrame({"contrast": name, "bootstrap_index": np.arange(len(draws)), "mean_difference": draws}))
    calc_contrasts = pd.DataFrame(contrast_rows)
    calc_contrasts["q_value_bh_six_contrasts"] = phase5_bh_adjust(calc_contrasts["p_value_two_sided"])
    calc_contrasts["contrast_passed"] = (calc_contrasts["mean_difference"] > 0) & (calc_contrasts["q_value_bh_six_contrasts"] < 0.05)
    stored_contrasts = pd.read_csv(p5 / "gate5_paired_contrasts.csv")
    ok, detail = _frames_close(calc_contrasts[stored_contrasts.columns], stored_contrasts, ["contrast"], 1e-15)
    calc_contrasts.to_csv(validation_dir / "phase5_paired_contrasts_recomputed.csv", index=False)
    checks.append(_audit_row("p5_paired_contrasts", "phase5", "inference", ok, "six stored paired contrasts", detail, "results/phase5_causal_specificity/gate5_seed_block_metrics.csv; results/phase5_causal_specificity/gate5_paired_contrasts.csv"))
    calc_draws = pd.concat(draw_frames, ignore_index=True)
    stored_draws = pd.read_csv(p5 / "gate5_paired_bootstrap_draws.csv")
    ok_draws, detail_draws = _frames_close(calc_draws[stored_draws.columns], stored_draws, ["contrast", "bootstrap_index"], 1e-12)
    calc_draws.to_csv(validation_dir / "phase5_bootstrap_draws_recomputed.csv", index=False)
    checks.append(_audit_row("p5_paired_bootstrap_draws", "phase5", "inference", ok_draws, "12000 stored draws", detail_draws, "results/phase5_causal_specificity/gate5_paired_bootstrap_draws.csv"))

    merged5 = realization5.merge(specs5[["condition", "baseline_replicate", "control_family", "realization", "seed_block"]].drop_duplicates(), on=["condition", "baseline_replicate"], how="left")
    reach_rows5 = []
    for family, part in merged5.groupby("control_family", sort=True):
        reach_rows5.append({"control_family": family, "n_frontier_realizations": len(part), "n_seed_blocks": part["seed_block"].nunique(), "n_target_reached": int(part["target_reached"].sum()), "n_right_censored": int((~part["target_reached"].astype(bool)).sum()), "target_reached_fraction": float(part["target_reached"].mean())})
    calc_reach5 = pd.DataFrame(reach_rows5)
    stored_reach5 = pd.read_csv(p5 / "target_reach_and_censoring.csv")
    ok, detail = _frames_close(calc_reach5[stored_reach5.columns], stored_reach5, ["control_family"], 1e-15)
    calc_reach5.to_csv(validation_dir / "phase5_target_reach_recomputed.csv", index=False)
    checks.append(_audit_row("p5_target_censoring_records", "phase5", "censoring", ok, "stored target/censoring table", detail, "results/phase5_causal_specificity/realization_frontier_summary.csv; results/phase5_causal_specificity/target_reach_and_censoring.csv"))

    gate5 = json.loads((p5 / "GATE_5_DECISION.json").read_text())
    gate5_ok = bool(len(metrics) == 20 and p5_identity and calc_contrasts["contrast_passed"].all() and gate5["status"] == "PASSED" and gate5["n_contrasts_passed"] == 6)
    checks.append(_audit_row("gate5_primary_records", "phase5", "gate", gate5_ok, {"n_seed_blocks": 20, "n_passed": 6, "identity": True}, {"n_seed_blocks": len(metrics), "n_passed": int(calc_contrasts["contrast_passed"].sum()), "identity": p5_identity, "stored_status": gate5["status"]}, "results/phase5_causal_specificity/GATE_5_DECISION.json; validation/result_freeze/phase5_paired_contrasts_recomputed.csv"))

    # Phase 6 summary intervals, regimes, Stage D inference, and Gate 7.
    p6 = repo_root / PHASE_ROOTS["phase6"]
    settings6 = Phase6Settings(**json.loads((p6 / "phase6_settings.json").read_text()))
    a6 = pd.read_csv(p6 / "stage_a_replicates.csv")
    b16 = pd.read_csv(p6 / "stage_b1_replicates.csv")
    b26 = pd.read_csv(p6 / "stage_b2_replicates.csv")
    c6 = pd.read_csv(p6 / "stage_c_replicates.csv")
    calc_ab6 = pd.concat([phase6_summarize(a6, settings6), phase6_summarize(b16, settings6), phase6_summarize(b26, settings6)], ignore_index=True).sort_values("design_id").reset_index(drop=True)
    stored_ab6 = pd.read_csv(p6 / "stage_ab_summary.csv").sort_values("design_id").reset_index(drop=True)
    ok, detail = _frames_close(calc_ab6[stored_ab6.columns], stored_ab6, ["design_id"], 1e-12)
    calc_ab6.to_csv(validation_dir / "phase6_stage_ab_summary_recomputed.csv", index=False)
    checks.append(_audit_row("p6_stage_ab_inference", "phase6", "inference", ok, "65 stored design summaries", detail, "results/phase6_generality/stage_a_replicates.csv; results/phase6_generality/stage_b1_replicates.csv; results/phase6_generality/stage_b2_replicates.csv; results/phase6_generality/stage_ab_summary.csv"))
    calc_c6 = phase6_summarize(c6, settings6).sort_values("design_id").reset_index(drop=True)
    stored_c6 = pd.read_csv(p6 / "stage_c_protocol_summary.csv").sort_values("design_id").reset_index(drop=True)
    ok, detail = _frames_close(calc_c6[stored_c6.columns], stored_c6, ["design_id"], 1e-12)
    calc_c6.to_csv(validation_dir / "phase6_stage_c_summary_recomputed.csv", index=False)
    checks.append(_audit_row("p6_stage_c_inference", "phase6", "inference", ok, "12 stored protocol summaries", detail, "results/phase6_generality/stage_c_replicates.csv; results/phase6_generality/stage_c_protocol_summary.csv"))

    drep6 = pd.read_csv(p6 / "stage_d_replicate_summary.csv")
    selected6 = pd.read_csv(p6 / "stage_d_selected.csv")
    design_by_confirm = selected6.set_index("confirm_id")["design_id"].to_dict()
    drows = []
    for cid, part in drep6.groupby("confirm_id"):
        mean, low, high = phase6_boot(part["value_of_information"], make_generator(settings6.root_seed, "p6-dboot", cid), settings6.bootstrap)
        drows.append({"confirm_id": cid, "design_id": design_by_confirm[cid], "voi_mean": mean, "voi_low": low, "voi_high": high, "identity_exact": bool(part["identity_information_recovered"].all() and part["identity_viability_recovered"].all()), "target_fraction": float(part["target_reached"].mean()), "positive": bool(low > 0.25)})
    calc_d6 = pd.DataFrame(drows)
    stored_d6 = pd.read_csv(p6 / "stage_d_summary.csv")
    ok, detail = _frames_close(calc_d6[stored_d6.columns], stored_d6, ["confirm_id"], 1e-12)
    calc_d6.to_csv(validation_dir / "phase6_stage_d_summary_recomputed.csv", index=False)
    checks.append(_audit_row("p6_stage_d_inference", "phase6", "inference", ok, "three stored confirmatory summaries", detail, "results/phase6_generality/stage_d_replicate_summary.csv; results/phase6_generality/stage_d_summary.csv"))
    checks.append(_audit_row("p6_identity_endpoints", "phase6", "endpoint", bool(drep6["identity_information_recovered"].all() and drep6["identity_viability_recovered"].all()), True, {"information": int(drep6["identity_information_recovered"].sum()), "viability": int(drep6["identity_viability_recovered"].sum()), "n": len(drep6)}, "results/phase6_generality/stage_d_replicate_summary.csv"))
    checks.append(_audit_row("p6_target_censoring_records", "phase6", "censoring", bool(drep6["target_reached"].all() and drep6["censoring"].eq("none").all()), {"reached": 24, "right_censored": 0}, {"reached": int(drep6["target_reached"].sum()), "right_censored": int((~drep6["target_reached"].astype(bool)).sum())}, "results/phase6_generality/stage_d_replicate_summary.csv"))

    positive = {"R2_viability_relevant", "R3_strong_adaptation"}
    fa = float(calc_ab6[calc_ab6["stage"] == "A"]["regime"].isin(positive).mean())
    fb = float(calc_ab6[calc_ab6["stage"] == "B1"]["regime"].isin(positive).mean())
    b2part = calc_ab6[calc_ab6["stage"] == "B2"]
    fam = {f: bool(((b2part["family"] == f) & b2part["regime"].isin(positive)).any()) for f in ["window", "position", "metabolite", "fitness"]}
    default = rep4[(rep4["condition"] == "selective") & np.isclose(rep4["inherit_prob"], 1.0)]
    default_ok = bool(default["value_of_information"].mean() > 0.25 and default["identity_information_recovered"].all() and default["identity_viability_recovered"].all())
    nondefault = int(calc_d6["positive"].sum())
    ident = bool(calc_d6["identity_exact"].all())
    broad = bool(fa >= 0.2 and fb >= 0.15 and sum(fam.values()) >= 3 and default_ok and nondefault >= 2 and ident)
    gate7 = json.loads((p6 / "GATE_7_DECISION.json").read_text())
    gate7_calc = {"stage_a_positive_fraction": fa, "stage_b1_positive_fraction": fb, "structural_family_support": fam, "default_archived_confirmed": default_ok, "nondefault_confirmed": nondefault, "identity_exact": ident, "broad": broad}
    gate7_ok = all(gate7[k] == v for k, v in gate7_calc.items()) and gate7["status"] == "PASSED" and gate7["generality_decision"] == "BROAD_GENERALITY_SUPPORTED"
    checks.append(_audit_row("gate7_primary_records", "phase6", "gate", gate7_ok, gate7_calc, {k: gate7[k] for k in gate7_calc} | {"status": gate7["status"]}, "results/phase6_generality/GATE_7_DECISION.json; validation/result_freeze/phase6_stage_ab_summary_recomputed.csv; validation/result_freeze/phase6_stage_d_summary_recomputed.csv"))

    audit = pd.DataFrame(checks).sort_values(["phase", "category", "check_id"]).reset_index(drop=True)
    return audit


def make_manifest(root: Path, *, exclude_name: str = "FILE_MANIFEST_SHA256.csv") -> pd.DataFrame:
    rows = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.name != exclude_name):
        rows.append({"relative_path": path.relative_to(root).as_posix(), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return pd.DataFrame(rows)
