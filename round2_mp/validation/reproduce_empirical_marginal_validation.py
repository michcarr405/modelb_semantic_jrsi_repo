from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.phase4 import load_map_panel
from modelb_semantic_repo.rng import ContinuationStream

CONT_ROOT = 2026100209
N_CONT = 64
OUTDIR = ROOT / "round2_mp" / "validation" / "generated_empirical"
FROZEN_SUMMARY = ROOT / "round2_mp" / "source_tables" / "empirical_marginal_summary.csv"

MAP_IDS = [
    "m000_constant",
    "m004_balanced_random_group",
    "m015_affinity_rank_group",
    "m024_contiguous_substring",
    "m027_contiguous_substring",
    "m029_contiguous_substring",
    "m033_identity",
]
MAP_LABELS = {
    "m000_constant": "MP constant",
    "m004_balanced_random_group": "MP balanced-random, 16 groups",
    "m015_affinity_rank_group": "MP affinity-rank, 64 groups",
    "m024_contiguous_substring": "MP substring start 0, length 2",
    "m027_contiguous_substring": "MP substring start 3, length 2",
    "m029_contiguous_substring": "MP substring start 1, length 3",
    "m033_identity": "MP identity",
}


def native_kernel(params):
    aff = np.asarray(params["motif_affinity_matrix"], float)
    fav = np.asarray(params["segment_favored_met"], int)
    ns, nz = len(fav), aff.shape[1]
    out = np.empty((aff.shape[0], ns, nz), float)
    for s in range(ns):
        x = aff.copy()
        x[:, fav[s]] += float(params["bias_strength"])
        x = x / float(params["temperature"])
        x -= x.max(axis=1, keepdims=True)
        e = np.exp(x)
        out[:, s, :] = e / e.sum(axis=1, keepdims=True)
    return out


def enumerate_windows(pop, nseg):
    nc, nseq, length = pop.shape
    chain = length - 4
    seglen = chain // nseg
    total = nc * nseq * chain
    motifs = np.empty(total, np.int64)
    segs = np.empty(total, np.int64)
    idx = 0
    for ci in range(nc):
        for si in range(nseq):
            seq = pop[ci, si]
            for pos in range(chain):
                m = 0
                for k in range(5):
                    m = m * 4 + int(seq[pos + k])
                s = min(pos // seglen, nseg - 1)
                motifs[idx] = m
                segs[idx] = s
                idx += 1
    return motifs, segs


def dense_labels(labels):
    _, inv = np.unique(np.asarray(labels, np.int64), return_inverse=True)
    return inv.astype(np.int64)


def mp_probabilities(native_probs, motifs, segs, labels, nseg, nz):
    groups = dense_labels(labels)[motifs]
    ng = int(groups.max()) + 1
    sums = np.zeros((ng, nseg, nz), float)
    counts = np.zeros((ng, nseg), np.int64)
    np.add.at(sums, (groups, segs), native_probs)
    np.add.at(counts, (groups, segs), 1)
    kern = np.zeros_like(sums)
    mask = counts > 0
    kern[mask] = sums[mask] / counts[mask, None]
    return kern[groups, segs]


def draw_states(probs, u):
    cdf = np.cumsum(probs, axis=1)
    states = np.sum(u[:, None] > cdf, axis=1).astype(np.int64)
    return np.minimum(states, probs.shape[1] - 1)


def state_counts(segs, states, nseg, nz):
    counts = np.zeros((nseg, nz), np.int64)
    np.add.at(counts, (segs, states), 1)
    return counts


def probs_from_counts(counts):
    return counts / counts.sum(axis=1, keepdims=True)


def mean_seg_tv(a, b):
    return float(np.mean(0.5 * np.abs(a - b).sum(axis=1)))


def max_abs(a, b):
    return float(np.max(np.abs(a - b)))


def run():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    params = default_parameters()
    kern = native_kernel(params)
    nseg, nz = kern.shape[1], kern.shape[2]
    panel = {x["map_id"]: x for x in load_map_panel(ROOT / "results" / "phase4_core" / "maps")}

    per_stream = []
    per_rep = []
    for rep in range(20):
        state_path = ROOT / "results" / "phase4_core" / "states" / "selective" / "p1.0" / f"rep_{rep:02d}.npz"
        pop = np.asarray(np.load(state_path)["population"])
        motifs, segs = enumerate_windows(pop, nseg)
        native_probs = kern[motifs, segs]
        map_probs = {
            mid: mp_probabilities(native_probs, motifs, segs, panel[mid]["labels"], nseg, nz)
            for mid in MAP_IDS
        }

        native_pool = np.zeros((nseg, nz), np.int64)
        native_first = np.zeros_like(native_pool)
        native_second = np.zeros_like(native_pool)
        map_pool = {mid: np.zeros((nseg, nz), np.int64) for mid in MAP_IDS}

        for ci in range(N_CONT):
            bid = f"selective_p1.0_r{rep:02d}"
            u = ContinuationStream(CONT_ROOT, bid, ci).observation_generator().random(len(motifs))
            st_native = draw_states(native_probs, u)
            c_native = state_counts(segs, st_native, nseg, nz)
            native_pool += c_native
            if ci < 32:
                native_first += c_native
            else:
                native_second += c_native
            p_native_stream = probs_from_counts(c_native)

            for mid in MAP_IDS:
                st_map = draw_states(map_probs[mid], u)
                c_map = state_counts(segs, st_map, nseg, nz)
                map_pool[mid] += c_map
                p_map_stream = probs_from_counts(c_map)
                per_stream.append(
                    dict(
                        replicate=rep,
                        continuation_index=ci,
                        map_id=mid,
                        map_label=MAP_LABELS[mid],
                        mean_segment_tv=mean_seg_tv(p_native_stream, p_map_stream),
                        max_abs_state_segment_diff=max_abs(p_native_stream, p_map_stream),
                    )
                )

        p_native = probs_from_counts(native_pool)
        p_first = probs_from_counts(native_first)
        p_second = probs_from_counts(native_second)
        native_split = mean_seg_tv(p_first, p_second)
        native_split_max = max_abs(p_first, p_second)

        for mid in MAP_IDS:
            p_map = probs_from_counts(map_pool[mid])
            tv = mean_seg_tv(p_native, p_map)
            per_rep.append(
                dict(
                    replicate=rep,
                    map_id=mid,
                    map_label=MAP_LABELS[mid],
                    pooled_64_mean_segment_tv=tv,
                    pooled_64_max_abs_state_segment_diff=max_abs(p_native, p_map),
                    native_split_half_mean_segment_tv=native_split,
                    native_split_half_max_abs_state_segment_diff=native_split_max,
                    ratio_to_native_split_half=(tv / native_split if native_split > 0 else np.nan),
                )
            )

    ps = pd.DataFrame(per_stream)
    pr = pd.DataFrame(per_rep)
    ps.to_csv(OUTDIR / "empirical_marginal_per_stream.csv", index=False)
    pr.to_csv(OUTDIR / "empirical_marginal_per_population.csv", index=False)

    rows = []
    for mid, g in pr.groupby("map_id", sort=False):
        gs = ps[ps.map_id == mid]
        rows.append(
            dict(
                map_id=mid,
                map_label=g.map_label.iloc[0],
                n_populations=int(len(g)),
                n_streams_per_population=N_CONT,
                mean_pooled_64_tv=float(g.pooled_64_mean_segment_tv.mean()),
                median_pooled_64_tv=float(g.pooled_64_mean_segment_tv.median()),
                max_pooled_64_tv=float(g.pooled_64_mean_segment_tv.max()),
                mean_pooled_64_max_abs=float(g.pooled_64_max_abs_state_segment_diff.mean()),
                max_pooled_64_max_abs=float(g.pooled_64_max_abs_state_segment_diff.max()),
                mean_single_stream_tv=float(gs.mean_segment_tv.mean()),
                median_single_stream_tv=float(gs.mean_segment_tv.median()),
                mean_native_split_half_tv=float(g.native_split_half_mean_segment_tv.mean()),
                median_ratio_to_native_split_half=float(g.ratio_to_native_split_half.median()),
                max_ratio_to_native_split_half=float(g.ratio_to_native_split_half.max()),
            )
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(OUTDIR / "empirical_marginal_summary.csv", index=False)

    frozen = pd.read_csv(FROZEN_SUMMARY)
    pd.testing.assert_frame_equal(
        summary.reset_index(drop=True),
        frozen.reset_index(drop=True),
        check_exact=False,
        rtol=0.0,
        atol=1e-15,
    )

    validation = {
        "continuation_root": CONT_ROOT,
        "n_populations": 20,
        "n_streams_per_population": N_CONT,
        "total_native_draws": 20 * N_CONT,
        "windows_per_draw": int(len(motifs)),
        "maps": MAP_IDS,
        "identity_pooled_tv_exact_zero": bool(
            summary.loc[summary.map_id == "m033_identity", "max_pooled_64_tv"].iloc[0] == 0.0
        ),
        "identity_single_stream_tv_exact_zero": bool(
            ps.loc[ps.map_id == "m033_identity", "mean_segment_tv"].max() == 0.0
        ),
        "max_nonidentity_mean_pooled_tv": float(
            summary.loc[summary.map_id != "m033_identity", "mean_pooled_64_tv"].max()
        ),
        "mean_native_split_half_tv": float(
            pr.drop_duplicates("replicate").native_split_half_mean_segment_tv.mean()
        ),
        "frozen_summary_match": True,
    }
    (OUTDIR / "VALIDATION.json").write_text(json.dumps(validation, indent=2))
    print("EMPIRICAL_MARGINAL_REPRODUCTION_PASS")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    run()
