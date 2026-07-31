#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from modelb_semantic_repo.result_freeze import audit_inferential_records, build_result_inventory, sha256_file


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "results" / "result_freeze"
    val = root / "validation" / "result_freeze"
    val.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": json.dumps(detail, default=str, sort_keys=True)})

    stored_inventory = pd.read_csv(out / "RESULT_INVENTORY.csv")
    current_inventory = build_result_inventory(root)
    inventory_equal = stored_inventory.fillna("").astype(str).equals(current_inventory.fillna("").astype(str))
    check("result_inventory_recomputes", inventory_equal, {"stored": len(stored_inventory), "current": len(current_inventory)})

    manifest = pd.read_csv(out / "FILE_MANIFEST_SHA256.csv")
    manifest_rows = []
    for row in manifest.itertuples(index=False):
        path = out / row.relative_path
        exists = path.exists()
        size_ok = exists and path.stat().st_size == int(row.size_bytes)
        hash_ok = exists and sha256_file(path) == row.sha256
        manifest_rows.append({"relative_path": row.relative_path, "exists": exists, "size_matches": size_ok, "hash_matches": hash_ok})
    manifest_check = pd.DataFrame(manifest_rows)
    manifest_check.to_csv(val / "result_freeze_manifest_verification.csv", index=False)
    check("result_freeze_manifest_integrity", bool(manifest_check[["exists", "size_matches", "hash_matches"]].all().all()), {"matches": int(manifest_check["hash_matches"].sum()), "n": len(manifest_check)})

    source_checks = pd.read_csv(val / "figure_source_verification.csv")
    check("figure_source_tables_verified", bool(source_checks["passed"].all()), {"passed": int(source_checks["passed"].sum()), "n": len(source_checks)})

    recomputed_audit = audit_inferential_records(root, val / "rerun")
    stored_audit = pd.read_csv(out / "INFERENTIAL_RECORD_AUDIT.csv")
    audit_equal = stored_audit.fillna("<NA>").astype(str).equals(recomputed_audit.fillna("<NA>").astype(str))
    check("inferential_audit_recomputes", audit_equal and bool(recomputed_audit["passed"].all()), {"equal": audit_equal, "passed": int(recomputed_audit["passed"].sum()), "n": len(recomputed_audit)})

    gate = json.loads((out / "GATE_8_DECISION.json").read_text())
    check("gate8_record", gate["status"] == "PASSED" and not gate["final_publication_figures_created"] and not gate["manuscript_rewritten"] and not gate["scientific_outputs_changed"], gate)

    frame = pd.DataFrame(checks)
    frame.to_csv(val / "structural_checks.csv", index=False)
    summary = {"n_checks": len(frame), "n_passed": int(frame["passed"].sum()), "all_passed": bool(frame["passed"].all())}
    (val / "validation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not summary["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
