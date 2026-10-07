from __future__ import annotations

import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'src'))

from modelb_semantic_repo.information import corrected_retained_information
from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.original_model.simulation import observe_population, reproduce_with_partitioning
from modelb_semantic_repo.phase4 import load_map_panel
from modelb_semantic_repo.rng import ContinuationStream, PermutationStream

OUT = ROOT / 'round2/mp_migration/results/core_p1_frontier_64'
PHASE4 = ROOT / "results" / "phase4_core"
R1_INFO_SEED = 2026073104
EXPLORATORY_CONTINUATION_SEED = 2026100209
N_CONTINUATIONS = 64
HORIZON = 36
TARGET_EPSILON = 0.01
N_PERMUTATIONS = 200

PARAMS = None
PANEL = None
KERNEL = None


def _native_kernel(params: dict) -> np.ndarray:
    aff = np.asarray(params["motif_affinity_matrix"], dtype=np.float64)
    n_motif, n_state = aff.shape
    n_seg = len(params["segment_favored_met"])
    out = np.empty((n_motif, n_seg, n_state), dtype=np.float64)
    for s in range(n_seg):
        logits = aff.copy()
        logits[:, int(params["segment_favored_met"][s])] += params["bias_strength"]
        x = logits / params["temperature"]
        x -= x.max(axis=1, keepdims=True)
        e = np.exp(x)
        out[:, s, :] = e / e.sum(axis=1, keepdims=True)
    return out


@njit
def _observe_marginal_preserving(
    population,
    native_kernel,
    group_labels,
    productive_pairs,
    anti_pairs,
    reward_strength,
    penalty_strength,
    uniforms,
):
    n_cells, n_seqs, seq_len = population.shape
    chain_len = seq_len - 4
    n_segments = native_kernel.shape[1]
    n_states = native_kernel.shape[2]
    seg_len = chain_len // n_segments
    total_windows = n_cells * n_seqs * chain_len
    n_groups = int(group_labels.max()) + 1

    groups = np.empty(total_windows, dtype=np.int64)
    segments = np.empty(total_windows, dtype=np.int64)
    group_prob_sums = np.zeros((n_groups, n_segments, n_states), dtype=np.float64)
    group_counts = np.zeros((n_groups, n_segments), dtype=np.int64)

    idx = 0
    for ci in range(n_cells):
        for si in range(n_seqs):
            for pos in range(chain_len):
                motif = 0
                for k in range(5):
                    motif = motif * 4 + int(population[ci, si, pos + k])
                seg = pos // seg_len
                if seg >= n_segments:
                    seg = n_segments - 1
                grp = int(group_labels[motif])
                groups[idx] = grp
                segments[idx] = seg
                for z in range(n_states):
                    group_prob_sums[grp, seg, z] += native_kernel[motif, seg, z]
                group_counts[grp, seg] += 1
                idx += 1

    for g in range(n_groups):
        for s in range(n_segments):
            c = group_counts[g, s]
            if c > 0:
                inv = 1.0 / c
                for z in range(n_states):
                    group_prob_sums[g, s, z] *= inv

    fitnesses = np.empty(n_cells, dtype=np.float64)
    idx = 0
    for ci in range(n_cells):
        prod_sum = 0.0
        anti_sum = 0.0
        for si in range(n_seqs):
            prev = -1
            for pos in range(chain_len):
                grp = groups[idx]
                seg = segments[idx]
                r = uniforms[idx]
                cdf = 0.0
                chosen = n_states - 1
                for z in range(n_states):
                    cdf += group_prob_sums[grp, seg, z]
                    if r <= cdf:
                        chosen = z
                        break
                idx += 1
                if pos > 0:
                    if productive_pairs[prev, chosen]:
                        prod_sum += 1.0
                    if anti_pairs[prev, chosen]:
                        anti_sum += 1.0
                prev = chosen
        mean_prod = prod_sum / n_seqs
        mean_anti = anti_sum / n_seqs
        f = 1.0 + reward_strength * mean_prod - penalty_strength * mean_anti
        if f < 0.1:
            f = 0.1
        fitnesses[ci] = f
    return fitnesses


def _init_worker():
    global PARAMS, PANEL, KERNEL
    PARAMS = default_parameters()
    PANEL = load_map_panel(PHASE4 / "maps")
    KERNEL = _native_kernel(PARAMS)
    for item in PANEL:
        labels = np.asarray(item["labels"], dtype=np.int64)
        _, inv = np.unique(labels, return_inverse=True)
        item["labels_dense"] = inv.astype(np.int64)


def _baseline_population(rep: int) -> np.ndarray:
    p = PHASE4 / "states" / "selective" / "p1.0" / f"rep_{rep:02d}.npz"
    return np.asarray(np.load(p)["population"])


def _simulate_actual(population: np.ndarray, baseline_id: str, cont_index: int) -> float:
    stream = ContinuationStream(EXPLORATORY_CONTINUATION_SEED, baseline_id, cont_index)
    obs_rng = stream.observation_generator()
    prop_rng = stream.propagation_generator()
    pop = np.array(population, copy=True)
    vals = np.empty(HORIZON, dtype=float)
    for h in range(HORIZON):
        fitnesses, _, _ = observe_population(pop, PARAMS["motif_affinity_matrix"], PARAMS, obs_rng)
        vals[h] = float(fitnesses.mean())
        pop = reproduce_with_partitioning(pop, fitnesses, PARAMS["mutation_rate"], 1.0, prop_rng)
    return float(vals.mean())


def _simulate_map(population: np.ndarray, baseline_id: str, cont_index: int, labels: np.ndarray) -> float:
    stream = ContinuationStream(EXPLORATORY_CONTINUATION_SEED, baseline_id, cont_index)
    obs_rng = stream.observation_generator()
    prop_rng = stream.propagation_generator()
    pop = np.array(population, copy=True)
    vals = np.empty(HORIZON, dtype=float)
    n_windows = PARAMS["n_cells"] * PARAMS["n_seqs"] * (PARAMS["seq_len"] - 4)
    for h in range(HORIZON):
        uniforms = obs_rng.random(n_windows)
        fitnesses = _observe_marginal_preserving(
            pop,
            KERNEL,
            labels,
            PARAMS["productive_pairs"],
            PARAMS["anti_pairs"],
            PARAMS["reward_strength"],
            PARAMS["penalty_strength"],
            uniforms,
        )
        vals[h] = float(fitnesses.mean())
        pop = reproduce_with_partitioning(pop, fitnesses, PARAMS["mutation_rate"], 1.0, prop_rng)
    return float(vals.mean())


def _job(rep: int, cont_index: int) -> list[dict]:
    if PARAMS is None:
        _init_worker()
    baseline_id = f"selective_p1.0_r{rep:02d}"
    population = _baseline_population(rep)
    actual = _simulate_actual(population, baseline_id, cont_index)
    rows = [{
        "replicate": rep,
        "baseline_replicate": baseline_id,
        "continuation_index": cont_index,
        "map_id": "actual",
        "map_hash": "actual",
        "method": "unintervened",
        "endpoint_type": "actual",
        "actual_groups": 1024,
        "viability": actual,
    }]
    for item in PANEL:
        if item["endpoint_type"] == "identity":
            viability = actual
        else:
            viability = _simulate_map(population, baseline_id, cont_index, item["labels_dense"])
        rows.append({
            "replicate": rep,
            "baseline_replicate": baseline_id,
            "continuation_index": cont_index,
            "map_id": item["map_id"],
            "map_hash": item["map_hash"],
            "method": item["method"],
            "endpoint_type": item["endpoint_type"],
            "actual_groups": int(item["actual_groups"]),
            "viability": viability,
        })
    return rows


def _coordinate_job(rep: int) -> list[dict]:
    panel = load_map_panel(PHASE4 / "maps")
    bid = f"selective_p1.0_r{rep:02d}"
    a = np.load(PHASE4 / "states" / "selective" / "p1.0" / f"rep_{rep:02d}.npz")
    motifs = a["final_observation_motifs"]
    states = a["final_observation_states"]
    segs = a["final_observation_segments"]
    rows = []
    for item in panel:
        ci = corrected_retained_information(
            motifs,
            states,
            segs,
            item["labels"],
            n_permutations=N_PERMUTATIONS,
            stream=PermutationStream(R1_INFO_SEED, bid, 0),
        )
        rows.append({
            "replicate": rep,
            "baseline_replicate": bid,
            "map_id": item["map_id"],
            "map_hash": item["map_hash"],
            "method": item["method"],
            "endpoint_type": item["endpoint_type"],
            "actual_groups": int(item["actual_groups"]),
            "observed_retained_information": ci.observed,
            "permutation_mean": ci.permutation_mean,
            "corrected_retained_information": ci.corrected,
        })
    return rows


def compute_coordinates(workers: int):
    out = OUT / "corrected_coordinates_p1.csv"
    if out.exists():
        df = pd.read_csv(out)
        if len(df) == 20 * 34:
            return df
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_coordinate_job, rep) for rep in range(20)]
        for i, fut in enumerate(as_completed(futs), 1):
            rows.extend(fut.result())
            print(f"coordinate baselines {i}/20", flush=True)
    df = pd.DataFrame(rows).sort_values(["replicate", "map_id"])
    df.to_csv(out, index=False)
    return df


def run_continuations(workers: int, limit: int | None = None):
    blockdir = OUT / "continuation_blocks"
    blockdir.mkdir(exist_ok=True)
    jobs = []
    for rep in range(20):
        for c in range(N_CONTINUATIONS):
            path = blockdir / f"r{rep:02d}_c{c:02d}.csv"
            if not path.exists():
                jobs.append((rep, c, path))
    print(f"pending continuation blocks: {len(jobs)}", flush=True)
    if limit is not None:
        jobs = jobs[:limit]
        print(f"running this invocation: {len(jobs)}", flush=True)
    if jobs:
        t0 = time.time()
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker) as ex:
            futs = {ex.submit(_job, rep, c): (rep, c, path) for rep, c, path in jobs}
            for i, fut in enumerate(as_completed(futs), 1):
                rep, c, path = futs[fut]
                pd.DataFrame(fut.result()).to_csv(path, index=False)
                if i % 20 == 0 or i == len(futs):
                    print(f"continuation blocks {i}/{len(futs)} elapsed={time.time()-t0:.1f}s", flush=True)
    files = sorted(blockdir.glob("r*_c*.csv"))
    if len(files) != 20 * N_CONTINUATIONS:
        print(f"partial blocks: {len(files)} / {20*N_CONTINUATIONS}", flush=True)
        return None
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df.to_csv(OUT / "continuation_level_results.csv", index=False)
    return df


def _t_interval(values: np.ndarray, level: float = 0.95):
    values = np.asarray(values, dtype=float)
    n = len(values)
    mean = float(values.mean())
    sd = float(values.std(ddof=1)) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n > 0 else np.nan
    if n > 1:
        crit = float(student_t.ppf(0.5 + level / 2.0, n - 1))
        return mean, se, mean - crit * se, mean + crit * se
    return mean, se, mean, mean


def analyze(cont: pd.DataFrame, coords: pd.DataFrame):
    merged = cont.merge(
        coords[["baseline_replicate", "map_id", "corrected_retained_information"]],
        on=["baseline_replicate", "map_id"],
        how="left",
    )
    # Actual has no map coordinate; give it the identity coordinate only for bookkeeping.
    idcoord = coords[coords["endpoint_type"] == "identity"].set_index("baseline_replicate")["corrected_retained_information"].to_dict()
    merged.loc[merged["map_id"] == "actual", "corrected_retained_information"] = merged.loc[merged["map_id"] == "actual", "baseline_replicate"].map(idcoord)

    paired_rows = []
    summary_rows = []
    frontier_rows = []
    first_rows = []

    for bid, block in merged.groupby("baseline_replicate", sort=True):
        actual = block[block["map_id"] == "actual"].set_index("continuation_index")["viability"].sort_index()
        const = block[block["endpoint_type"] == "constant"].set_index("continuation_index")["viability"].sort_index()
        actual_mean = float(actual.mean())
        const_mean = float(const.mean())
        loss = actual_mean - const_mean
        target = actual_mean - TARGET_EPSILON * loss

        map_summaries = []
        for (map_id, map_hash, method, endpoint_type, actual_groups, coord), mpart in block[block["map_id"] != "actual"].groupby(
            ["map_id", "map_hash", "method", "endpoint_type", "actual_groups", "corrected_retained_information"], sort=False
        ):
            mv = mpart.set_index("continuation_index")["viability"].sort_index()
            idx = actual.index.intersection(const.index).intersection(mv.index)
            margins = mv.loc[idx].to_numpy() - (actual.loc[idx].to_numpy() - TARGET_EPSILON * (actual.loc[idx].to_numpy() - const.loc[idx].to_numpy()))
            mean_margin, se_margin, lo_margin, hi_margin = _t_interval(margins)
            viability_mean = float(mv.mean())
            recovery = (viability_mean - const_mean) / loss if abs(loss) > 1e-15 else np.nan
            for c, margin in zip(idx, margins):
                paired_rows.append({
                    "baseline_replicate": bid,
                    "map_id": map_id,
                    "continuation_index": int(c),
                    "target_margin": float(margin),
                })
            map_summaries.append({
                "baseline_replicate": bid,
                "map_id": map_id,
                "map_hash": map_hash,
                "method": method,
                "endpoint_type": endpoint_type,
                "actual_groups": int(actual_groups),
                "corrected_retained_information": float(coord),
                "viability_mean": viability_mean,
                "recovery_fraction": float(recovery),
                "target_margin_mean": mean_margin,
                "target_margin_se": se_margin,
                "target_margin_ci95_low": lo_margin,
                "target_margin_ci95_high": hi_margin,
                "continuation_target_fraction": float(np.mean(margins >= 0.0)),
            })
        ms = pd.DataFrame(map_summaries)
        summary_rows.extend(ms.to_dict("records"))

        # At tied coordinates retain best mean viability, then cumulative upper frontier.
        points = []
        for coord, part in ms.groupby("corrected_retained_information", sort=True):
            best = part.sort_values(["viability_mean", "map_hash"], ascending=[False, True]).iloc[0]
            points.append(best.to_dict())
        pts = pd.DataFrame(points).sort_values("corrected_retained_information").reset_index(drop=True)
        running_v = -np.inf
        running_source = None
        for _, row in pts.iterrows():
            if float(row["viability_mean"]) > running_v:
                running_v = float(row["viability_mean"])
                running_source = row.to_dict()
            frontier_rows.append({
                "baseline_replicate": bid,
                "corrected_retained_information": float(row["corrected_retained_information"]),
                "point_viability": float(row["viability_mean"]),
                "frontier_viability": running_v,
                "frontier_source_map_id": running_source["map_id"],
                "frontier_source_method": running_source["method"],
                "frontier_source_endpoint_type": running_source["endpoint_type"],
                "frontier_source_target_margin_mean": float(running_source["target_margin_mean"]),
                "frontier_source_target_margin_ci95_low": float(running_source["target_margin_ci95_low"]),
                "frontier_source_target_margin_ci95_high": float(running_source["target_margin_ci95_high"]),
                "target_viability": target,
                "actual_viability": actual_mean,
                "constant_viability": const_mean,
            })

        fb = pd.DataFrame([x for x in frontier_rows if x["baseline_replicate"] == bid])
        hit = fb.index[fb["frontier_viability"] >= target].to_numpy()
        if len(hit):
            h = fb.loc[int(hit[0])]
            first_map = h["frontier_source_map_id"]
            first_endpoint = h["frontier_source_endpoint_type"]
            first_method = h["frontier_source_method"]
            first_coord = float(h["corrected_retained_information"])
            first_lo = float(h["frontier_source_target_margin_ci95_low"])
            first_hi = float(h["frontier_source_target_margin_ci95_high"])
            if first_endpoint == "identity":
                nonid = ms[ms["endpoint_type"] != "identity"]
                resolved = bool((nonid["target_margin_ci95_high"] < 0).all())
                precision_class = "technically_resolved_identity" if resolved else "technically_unresolved"
            else:
                resolved = first_lo > 0
                precision_class = "technically_resolved_nonidentity" if resolved else "technically_unresolved"
            reached = True
        else:
            first_map = first_method = first_endpoint = "censored"
            first_coord = np.nan
            first_lo = first_hi = np.nan
            precision_class = "technically_unresolved"
            reached = False

        first_rows.append({
            "baseline_replicate": bid,
            "target_reached": reached,
            "actual_viability": actual_mean,
            "constant_viability": const_mean,
            "intervention_loss": loss,
            "target_viability": target,
            "target_tolerance": TARGET_EPSILON * loss,
            "first_target_map_id": first_map,
            "first_target_method": first_method,
            "first_target_endpoint_type": first_endpoint,
            "first_target_corrected_information": first_coord,
            "first_target_margin_ci95_low": first_lo,
            "first_target_margin_ci95_high": first_hi,
            "identity_required_by_mean_frontier": first_endpoint == "identity",
            "technical_precision_class": precision_class,
        })

    pd.DataFrame(paired_rows).to_csv(OUT / "paired_target_margins.csv", index=False)
    pd.DataFrame(summary_rows).to_csv(OUT / "map_summary.csv", index=False)
    pd.DataFrame(frontier_rows).to_csv(OUT / "frontier_points.csv", index=False)
    first = pd.DataFrame(first_rows)
    first.to_csv(OUT / "first_target_summary.csv", index=False)

    key = {
        "n_baselines": int(len(first)),
        "n_continuations_per_map": N_CONTINUATIONS,
        "target_reached": int(first["target_reached"].sum()),
        "identity_required_by_mean_frontier": int(first["identity_required_by_mean_frontier"].sum()),
        "technical_precision_class_counts": first["technical_precision_class"].value_counts().to_dict(),
        "first_target_method_counts": first["first_target_method"].value_counts().to_dict(),
        "mean_constant_intervention_loss": float(first["intervention_loss"].mean()),
        "median_target_tolerance": float(first["target_tolerance"].median()),
        "median_first_target_corrected_information": float(first["first_target_corrected_information"].median()),
    }
    (OUT / "KEY_RESULTS.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(json.dumps(key, indent=2), flush=True)
    return first


def main():
    workers = int(os.environ.get("HP_WORKERS", "8"))
    coords = compute_coordinates(max(1, min(workers, 8)))
    limit_env = os.environ.get('FRONTIER_LIMIT')
    limit = int(limit_env) if limit_env else None
    cont = run_continuations(workers, limit)
    if cont is not None:
        analyze(cont, coords)


if __name__ == "__main__":
    main()
