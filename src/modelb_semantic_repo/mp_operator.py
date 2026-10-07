"""Reconstructed Round-2 marginal-preserving intervention operator.

PROVENANCE
----------
This module is a functional reconstruction, not a byte-identical recovery of the
lost Round-2 production source. It is reconstructed from the frozen Round-2
production drivers, the self-contained p=1 frontier implementation, the frozen
causal-specificity implementation, and the immutable Round-1 model source.

The public API matches the imports used by the recovered Round-2 production
scripts. Validation records should accompany any release containing this file.
"""
from __future__ import annotations

import numpy as np
from numba import njit

from .rng import ContinuationStream
from .original_model.simulation import observe_population, reproduce_with_partitioning


def _dense_labels(labels: np.ndarray) -> np.ndarray:
    labels = np.asarray(labels, dtype=np.int64)
    _, inv = np.unique(labels, return_inverse=True)
    return inv.astype(np.int64)


def _core_native_kernel(matrix: np.ndarray, params: dict) -> np.ndarray:
    aff = np.asarray(matrix, dtype=np.float64)
    favored = np.asarray(params["segment_favored_met"], dtype=np.int64)
    n_motif, n_state = aff.shape
    out = np.empty((n_motif, len(favored), n_state), dtype=np.float64)
    for s, fav in enumerate(favored):
        logits = aff.copy()
        logits[:, int(fav)] += float(params["bias_strength"])
        x = logits / float(params["temperature"])
        x -= x.max(axis=1, keepdims=True)
        e = np.exp(x)
        out[:, s, :] = e / e.sum(axis=1, keepdims=True)
    return out


def _phase6_native_kernel(m: dict) -> np.ndarray:
    aff = np.asarray(m["aff"], dtype=np.float64)
    favored = np.asarray(m["favored"], dtype=np.int64)
    n_motif, n_state = aff.shape
    out = np.empty((n_motif, len(favored), n_state), dtype=np.float64)
    for s, fav in enumerate(favored):
        logits = aff.copy()
        logits[:, int(fav)] += float(m["bias"])
        x = logits / float(m["temperature"])
        x -= x.max(axis=1, keepdims=True)
        e = np.exp(x)
        out[:, s, :] = e / e.sum(axis=1, keepdims=True)
    return out


@njit(cache=True)
def _observe_grouped(
    population,
    native_kernel,
    group_labels,
    active,
    offsets,
    productive_pairs,
    anti_pairs,
    reward_strength,
    penalty_strength,
    floor,
    motif_length,
    mode,
    uniforms,
):
    n_cells, n_seqs, seq_len = population.shape
    n_active = active.size
    n_segments = native_kernel.shape[1]
    n_states = native_kernel.shape[2]
    chain_len = seq_len - motif_length + 1
    total_windows = n_cells * n_seqs * n_active
    if uniforms.size != total_windows:
        raise ValueError("uniforms has incorrect length")
    if offsets.size != n_cells * n_seqs:
        raise ValueError("offsets has incorrect length")

    n_groups = int(group_labels.max()) + 1
    groups = np.empty(total_windows, dtype=np.int64)
    segments = np.empty(total_windows, dtype=np.int64)
    prob_sums = np.zeros((n_groups, n_segments, n_states), dtype=np.float64)
    counts = np.zeros((n_groups, n_segments), dtype=np.int64)

    idx = 0
    chain_idx = 0
    for ci in range(n_cells):
        for si in range(n_seqs):
            off = int(offsets[chain_idx])
            chain_idx += 1
            for ai in range(n_active):
                pos = int(active[ai])
                motif = 0
                for k in range(motif_length):
                    motif = motif * 4 + int(population[ci, si, pos + k])
                shifted = pos + off
                if shifted < 0:
                    shifted = 0
                elif shifted >= chain_len:
                    shifted = chain_len - 1
                seg = (shifted * n_segments) // chain_len
                if seg >= n_segments:
                    seg = n_segments - 1
                grp = int(group_labels[motif])
                groups[idx] = grp
                segments[idx] = seg
                for z in range(n_states):
                    prob_sums[grp, seg, z] += native_kernel[motif, seg, z]
                counts[grp, seg] += 1
                idx += 1

    for g in range(n_groups):
        for s in range(n_segments):
            c = counts[g, s]
            if c > 0:
                inv = 1.0 / c
                for z in range(n_states):
                    prob_sums[g, s, z] *= inv

    fits = np.empty(n_cells, dtype=np.float64)
    idx = 0
    for ci in range(n_cells):
        prod_sum = 0.0
        anti_sum = 0.0
        for si in range(n_seqs):
            prev = -1
            for ai in range(n_active):
                grp = groups[idx]
                seg = segments[idx]
                r = uniforms[idx]
                cdf = 0.0
                chosen = n_states - 1
                for z in range(n_states):
                    cdf += prob_sums[grp, seg, z]
                    if r <= cdf:
                        chosen = z
                        break
                idx += 1
                if ai > 0:
                    if productive_pairs[prev, chosen]:
                        prod_sum += 1.0
                    if anti_pairs[prev, chosen]:
                        anti_sum += 1.0
                prev = chosen
        if mode == 0:
            mean_prod = prod_sum / n_seqs
            mean_anti = anti_sum / n_seqs
        else:
            denom = n_seqs * max(1, n_active - 1)
            mean_prod = prod_sum / denom
            mean_anti = anti_sum / denom
        fit = 1.0 + reward_strength * mean_prod - penalty_strength * mean_anti
        if fit < floor:
            fit = floor
        fits[ci] = fit
    return fits


def simulate_core_actual(population, params, matrix, inherit_prob, horizon, root_seed, baseline_id, continuation_index):
    """Unintervened core continuation; API recovered from production call sites."""
    stream = ContinuationStream(root_seed, baseline_id, continuation_index)
    obs_rng = stream.observation_generator()
    prop_rng = stream.propagation_generator()
    pop = np.array(population, copy=True)
    vals = np.empty(int(horizon), dtype=np.float64)
    for h in range(int(horizon)):
        fits, _, _ = observe_population(pop, matrix, params, obs_rng)
        vals[h] = float(fits.mean())
        pop = reproduce_with_partitioning(
            pop, fits, float(params["mutation_rate"]), float(inherit_prob), prop_rng
        )
    return float(vals.mean()), pop


def simulate_core_grouped(population, params, matrix, inherit_prob, labels, horizon, root_seed, baseline_id, continuation_index):
    """Core continuation under population-frequency-weighted MP grouping."""
    labels = _dense_labels(labels)
    kernel = _core_native_kernel(matrix, params)
    stream = ContinuationStream(root_seed, baseline_id, continuation_index)
    obs_rng = stream.observation_generator()
    prop_rng = stream.propagation_generator()
    pop = np.array(population, copy=True)
    chain_len = int(params["seq_len"]) - 4
    active = np.arange(chain_len, dtype=np.int64)
    offsets = np.zeros(int(params["n_cells"]) * int(params["n_seqs"]), dtype=np.int64)
    n_windows = int(params["n_cells"]) * int(params["n_seqs"]) * chain_len
    vals = np.empty(int(horizon), dtype=np.float64)
    for h in range(int(horizon)):
        uniforms = obs_rng.random(n_windows)
        fits = _observe_grouped(
            pop, kernel, labels, active, offsets,
            np.asarray(params["productive_pairs"]), np.asarray(params["anti_pairs"]),
            float(params["reward_strength"]), float(params["penalty_strength"]),
            0.1, 5, 0, uniforms,
        )
        vals[h] = float(fits.mean())
        pop = reproduce_with_partitioning(
            pop, fits, float(params["mutation_rate"]), float(inherit_prob), prop_rng
        )
    return float(vals.mean()), pop


def simulate_core_constant(population, params, matrix, inherit_prob, horizon, root_seed, baseline_id, continuation_index):
    labels = np.zeros(np.asarray(matrix).shape[0], dtype=np.int64)
    return simulate_core_grouped(
        population, params, matrix, inherit_prob, labels, horizon,
        root_seed, baseline_id, continuation_index,
    )


def simulate_phase6_grouped(population, m, labels, horizon, root_seed, baseline_id, continuation_index, reproduce_fn):
    """Phase-6 continuation under MP grouping, preserving Phase-6 RNG draw order."""
    labels = _dense_labels(labels)
    kernel = _phase6_native_kernel(m)
    stream = ContinuationStream(root_seed, baseline_id, continuation_index)
    obs_rng = stream.observation_generator()
    prop_rng = stream.propagation_generator()
    pop = np.array(population, copy=True)
    active = np.asarray(m["active"], dtype=np.int64)
    n_chains = int(m["n_cells"]) * int(m["n_seqs"])
    n_windows = n_chains * len(active)
    jitter = int(m.get("jitter", 0))
    vals = np.empty(int(horizon), dtype=np.float64)
    for h in range(int(horizon)):
        # Must match phase6.observe draw order: offsets first, then local-state uniforms.
        offsets = (
            obs_rng.integers(-jitter, jitter + 1, size=n_chains, dtype=np.int64)
            if jitter else np.zeros(n_chains, dtype=np.int64)
        )
        uniforms = obs_rng.random(n_windows)
        fits = _observe_grouped(
            pop, kernel, labels, active, offsets,
            np.asarray(m["prod"]), np.asarray(m["anti"]),
            float(m["reward"]), float(m["penalty"]), float(m["floor"]),
            int(m["motif_length"]), int(m["mode"]), uniforms,
        )
        vals[h] = float(fits.mean())
        pop = reproduce_fn(pop, fits, m, prop_rng)
    return float(vals.mean()), pop


def simulate_phase6_constant(population, m, horizon, root_seed, baseline_id, continuation_index, reproduce_fn):
    labels = np.zeros(len(m["aff"]), dtype=np.int64)
    return simulate_phase6_grouped(
        population, m, labels, horizon, root_seed, baseline_id,
        continuation_index, reproduce_fn,
    )


def expected_marginal_error_general(population, m, labels, offsets=None):
    """Maximum absolute expected one-site P(Z|S) error induced by MP grouping.

    The two sides are accumulated independently, matching the frozen validation
    logic: native P(Z|S) is accumulated window-by-window, whereas the MP side is
    reconstructed from segment-specific motif frequencies, group frequencies,
    and the group probability kernels. Differences are therefore floating-point
    roundoff rather than an algebraically forced zero.
    """
    pop = np.asarray(population)
    labels = _dense_labels(labels)
    kernel = _phase6_native_kernel(m)
    active = np.asarray(m["active"], dtype=np.int64)
    n_cells, n_seqs, seq_len = pop.shape
    n_chains = n_cells * n_seqs
    if offsets is None:
        offsets = np.zeros(n_chains, dtype=np.int64)
    else:
        offsets = np.asarray(offsets, dtype=np.int64)
    if len(offsets) != n_chains:
        raise ValueError("offsets has incorrect length")
    k = int(m["motif_length"])
    chain_len = seq_len - k + 1
    nseg = kernel.shape[1]
    nstate = kernel.shape[2]
    nmotif = kernel.shape[0]
    ngroup = int(labels.max()) + 1

    native_sum = np.zeros((nseg, nstate), dtype=np.float64)
    seg_counts = np.zeros(nseg, dtype=np.int64)
    motif_counts = np.zeros((nseg, nmotif), dtype=np.int64)

    ch = 0
    for ci in range(n_cells):
        for si in range(n_seqs):
            off = int(offsets[ch]); ch += 1
            for pos0 in active:
                pos = int(pos0)
                motif = 0
                for kk in range(k):
                    motif = motif * 4 + int(pop[ci, si, pos + kk])
                shifted = min(max(pos + off, 0), chain_len - 1)
                seg = (shifted * nseg) // chain_len
                if seg >= nseg:
                    seg = nseg - 1
                native_sum[seg] += kernel[motif, seg]
                seg_counts[seg] += 1
                motif_counts[seg, motif] += 1

    native = np.zeros_like(native_sum)
    for s in range(nseg):
        if seg_counts[s] > 0:
            native[s] = native_sum[s] / seg_counts[s]

    reconstructed = np.zeros_like(native_sum)
    for s in range(nseg):
        total = int(seg_counts[s])
        if total <= 0:
            continue
        for g in range(ngroup):
            members = np.flatnonzero(labels == g)
            gc = int(motif_counts[s, members].sum())
            if gc <= 0:
                continue
            q = np.zeros(nstate, dtype=np.float64)
            for motif in members:
                c = int(motif_counts[s, motif])
                if c:
                    q += (c / gc) * kernel[motif, s]
            reconstructed[s] += (gc / total) * q
    return float(np.max(np.abs(native - reconstructed)))


__all__ = [
    "simulate_core_actual",
    "simulate_core_grouped",
    "simulate_phase6_grouped",
    "simulate_core_constant",
    "simulate_phase6_constant",
    "expected_marginal_error_general",
]
