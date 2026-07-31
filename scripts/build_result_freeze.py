#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from modelb_semantic_repo.result_freeze import (
    audit_inferential_records,
    build_figure_sources,
    build_result_inventory,
    make_manifest,
)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "results" / "result_freeze"
    validation = root / "validation" / "result_freeze"
    out.mkdir(parents=True, exist_ok=True)
    validation.mkdir(parents=True, exist_ok=True)

    inventory = build_result_inventory(root)
    inventory.to_csv(out / "RESULT_INVENTORY.csv", index=False)

    catalog, source_checks = build_figure_sources(root, out)
    catalog.to_csv(out / "FIGURE_SOURCE_CATALOG.csv", index=False)
    source_checks.to_csv(validation / "figure_source_verification.csv", index=False)

    audit = audit_inferential_records(root, validation)
    audit.to_csv(out / "INFERENTIAL_RECORD_AUDIT.csv", index=False)

    archive_ok = bool(
        inventory.loc[inventory["relative_path"] != "FILE_MANIFEST_SHA256.csv", ["exists", "in_manifest", "size_matches", "hash_matches"]]
        .all()
        .all()
    )
    source_ok = bool(source_checks["passed"].all())
    inference_ok = bool(audit["passed"].all())
    gate = {
        "gate": "Gate 8 - Result freeze",
        "status": "PASSED" if archive_ok and source_ok and inference_ok else "FAILED",
        "starting_commit": "f9a3030",
        "preserved_decisions": "D16-D31",
        "archive_integrity": archive_ok,
        "figure_source_verification": source_ok,
        "inferential_record_verification": inference_ok,
        "n_inventory_rows": int(len(inventory)),
        "n_figure_source_tables": int(len(catalog)),
        "n_inferential_checks": int(len(audit)),
        "n_inferential_checks_passed": int(audit["passed"].sum()),
        "final_publication_figures_created": False,
        "manuscript_rewritten": False,
        "scientific_outputs_changed": False,
    }
    (out / "GATE_8_DECISION.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")

    manifest = make_manifest(out)
    manifest.to_csv(out / "FILE_MANIFEST_SHA256.csv", index=False)
    print(json.dumps(gate, indent=2))
    if gate["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
