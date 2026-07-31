import json
from pathlib import Path
import shutil
import tempfile

import numpy as np
import pandas as pd

from modelb_semantic_repo.phase5 import (
    N_DISRUPTION_REALIZATIONS,
    Phase5Settings,
    _baseline_job,
    _evaluation_job,
    _make_evaluation_specs,
    enumerate_matched_topologies,
    select_alternative_topologies,
    verify_phase4_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
PHASE4 = ROOT / "results" / "phase4_core"
PHASE5 = ROOT / "results" / "phase5_causal_specificity"
OUT = ROOT / "validation" / "phase5"
OUT.mkdir(parents=True, exist_ok=True)
settings = Phase5Settings(workers=1)

checks = []

def check(name, passed, detail):
    checks.append({"check": name, "passed": bool(passed), "detail": str(detail)})

# Archive and production counts.
archive = verify_phase4_manifest(PHASE4)
check("phase4_archive_integrity", archive["matches"].all(), f"{archive['matches'].sum()}/{len(archive)} files match")
phase4_baselines = pd.read_csv(PHASE4 / "baseline_information.csv")
controls = pd.read_csv(PHASE5 / "control_baseline_information.csv")
raw = pd.read_csv(PHASE5 / "continuation_level_results.csv")
realization = pd.read_csv(PHASE5 / "realization_frontier_summary.csv")
contrasts = pd.read_csv(PHASE5 / "gate5_paired_contrasts.csv")
info = pd.read_csv(PHASE5 / "evaluation_information.csv")
specs = pd.DataFrame(json.loads((PHASE5 / "evaluation_specifications.json").read_text()))
check("control_baseline_count", len(controls) == 100, len(controls))
check("evaluation_specification_count", len(specs) == 220, len(specs))
check("continuation_row_count", len(raw) == 15400, len(raw))
check("frontier_realization_count", len(realization) == 220, len(realization))
check("two_continuations_per_map", raw.groupby(["baseline_replicate", "map_hash"]).size().eq(2).all(), raw.groupby(["baseline_replicate", "map_hash"]).size().value_counts().to_dict())
check("identity_information_recovery", realization["identity_information_recovered"].all(), int(realization["identity_information_recovered"].sum()))
check("identity_viability_recovery", realization["identity_viability_recovered"].all(), int(realization["identity_viability_recovered"].sum()))
check("six_gate_contrasts", len(contrasts) == 6, len(contrasts))
check("all_gate_contrasts_pass", contrasts["contrast_passed"].all(), int(contrasts["contrast_passed"].sum()))

# Topology and derangement structure.
topologies = enumerate_matched_topologies()
native, topology_a, topology_b = select_alternative_topologies(topologies)
check("matched_topology_universe", len(topologies) == 30 and len({t.topology_hash for t in topologies}) == 30, len(topologies))
check("alternative_topologies_nonnative", not topology_a.is_native and not topology_b.is_native and topology_a.topology_id != topology_b.topology_id, f"A={topology_a.topology_id}, B={topology_b.topology_id}")
deranged = specs[specs["affinity_mode"] == "deranged"]
fixed_points = []
valid_permutations = []
for permutation in deranged["affinity_permutation"]:
    p = np.asarray(permutation, dtype=int)
    fixed_points.append(int(np.sum(p == np.arange(len(p)))))
    valid_permutations.append(bool(np.array_equal(np.sort(p), np.arange(len(p)))))
check("complete_affinity_derangements", len(deranged) == 40 and max(fixed_points, default=1) == 0 and all(valid_permutations), f"n={len(deranged)}, max_fixed={max(fixed_points, default=-1)}")
mismatch = specs[specs["condition"] == "topology_mismatch"]
check("two_topology_mismatches_per_seed", len(mismatch) == 40 and mismatch.groupby("seed_block").size().eq(N_DISRUPTION_REALIZATIONS).all(), len(mismatch))
check("mismatches_exclude_native", not mismatch["fixed_topology_id"].eq(native.topology_id).any(), native.topology_id)

# Unstable schedules.
schedule_files = sorted((PHASE5 / "topology_schedules").glob("*.json"))
no_repeats = True
valid_ids = {t.topology_id for t in topologies}
for path in schedule_files:
    schedule = json.loads(path.read_text())
    no_repeats &= all(x in valid_ids for x in schedule)
    no_repeats &= all(x != y for x, y in zip(schedule[:-1], schedule[1:]))
check("unstable_schedule_count", len(schedule_files) == 60, len(schedule_files))
check("unstable_schedules_no_immediate_repeat", no_repeats, len(schedule_files))

# Representative deterministic reruns of all five evolved control modes.
baseline_reruns = []
with tempfile.TemporaryDirectory(prefix="phase5_validation_", dir=OUT) as tmp:
    tmp = Path(tmp)
    p1 = phase4_baselines[(phase4_baselines["condition"] == "selective") & np.isclose(phase4_baselines["inherit_prob"], 1.0)].set_index("replicate")
    for mode in ["selection_neutral", "selection_reduced", "alternative_a", "alternative_b", "temporally_unstable"]:
        archived = controls[(controls["mode"] == mode) & (controls["replicate"] == 0)].iloc[0]
        job = {
            "mode": mode,
            "replicate": 0,
            "phase4_row": p1.loc[0].to_dict(),
            "settings": settings.to_dict(),
            "state_dir": str(tmp / "states"),
            "schedule_dir": str(tmp / "schedules"),
            "baseline_block_dir": str(tmp / "baseline_blocks"),
        }
        rerun = _baseline_job(job)
        same_state = rerun["state_hash"] == archived["state_hash"]
        same_trajectory = rerun["trajectory_hash"] == archived["trajectory_hash"]
        baseline_reruns.append({"mode": mode, "same_state_hash": same_state, "same_trajectory_hash": same_trajectory})
    check("representative_baseline_reruns", all(x["same_state_hash"] and x["same_trajectory_hash"] for x in baseline_reruns), baseline_reruns)

    # Representative evaluation reruns span selection, both mapping disruptions,
    # alternative topology, and the temporally unstable schedule.
    phase4_info = phase4_baselines.set_index("baseline_replicate")["conditional_information"].to_dict()
    control_info = controls.set_index("baseline_replicate")["conditional_information"].to_dict()
    representatives = [
        ("selection_neutral", 0),
        ("affinity_reassigned", 0),
        ("topology_mismatch", 0),
        ("alternative_a_native", 0),
        ("temporally_unstable", 0),
    ]
    evaluation_reruns = []
    for condition, seed_block in representatives:
        spec = specs[(specs["condition"] == condition) & (specs["seed_block"] == seed_block)].sort_values("realization").iloc[0].to_dict()
        job = {
            "settings": settings.to_dict(),
            "spec": spec,
            "outdir": str(tmp / "evaluations" / spec["baseline_replicate"]),
            "map_dir": str(PHASE4 / "maps"),
            "phase4_conditional_information": phase4_info.get(spec["source_baseline_id"], np.nan),
            "control_conditional_information": control_info.get(spec["source_baseline_id"], np.nan),
        }
        rerun_path = Path(_evaluation_job(job))
        archived_path = PHASE5 / "continuation_blocks" / f"{spec['baseline_replicate']}.csv"
        a = pd.read_csv(archived_path).sort_values(["map_hash", "continuation_index"]).reset_index(drop=True)
        b = pd.read_csv(rerun_path).sort_values(["map_hash", "continuation_index"]).reset_index(drop=True)
        same = a.equals(b)
        evaluation_reruns.append({"condition": condition, "baseline_replicate": spec["baseline_replicate"], "exact_table_match": same})
    check("representative_evaluation_reruns", all(x["exact_table_match"] for x in evaluation_reruns), evaluation_reruns)

pd.DataFrame(checks).to_csv(OUT / "structural_checks.csv", index=False)
pd.DataFrame(baseline_reruns).to_csv(OUT / "representative_baseline_reruns.csv", index=False)
pd.DataFrame(evaluation_reruns).to_csv(OUT / "representative_evaluation_reruns.csv", index=False)
summary = {
    "n_checks": len(checks),
    "n_passed": int(sum(x["passed"] for x in checks)),
    "all_passed": bool(all(x["passed"] for x in checks)),
}
(OUT / "validation_summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
if not summary["all_passed"]:
    raise SystemExit(1)
