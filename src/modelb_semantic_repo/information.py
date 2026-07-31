"""Validated information measures for the JRSI major revision."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from collections.abc import Mapping
from typing import Any

import numpy as np

from .rng import PermutationStream


def _vectors(*arrays: Any) -> list[np.ndarray]:
    out = [np.asarray(a).reshape(-1) for a in arrays]
    if not out:
        raise ValueError("at least one vector is required")
    n = len(out[0])
    if any(len(a) != n for a in out):
        raise ValueError("all vectors must have equal length")
    if n == 0:
        raise ValueError("vectors must not be empty")
    return out


def mutual_information(x: Any, y: Any) -> float:
    x, y = _vectors(x, y)
    _, xi = np.unique(x, return_inverse=True)
    _, yi = np.unique(y, return_inverse=True)
    counts = np.zeros((xi.max() + 1, yi.max() + 1), dtype=float)
    np.add.at(counts, (xi, yi), 1.0)
    pxy = counts / counts.sum()
    px = pxy.sum(axis=1, keepdims=True)
    py = pxy.sum(axis=0, keepdims=True)
    expected = px @ py
    mask = pxy > 0
    return float(np.sum(pxy[mask] * np.log2(pxy[mask] / expected[mask])))


def conditional_mutual_information(motif: Any, state: Any, segment: Any, *, return_components: bool = False):
    motif, state, segment = _vectors(motif, state, segment)
    total = len(motif)
    components = []
    value = 0.0
    for seg in np.unique(segment):
        mask = segment == seg
        n = int(mask.sum())
        weight = n / total
        mi = mutual_information(motif[mask], state[mask])
        contribution = weight * mi
        value += contribution
        components.append(
            {
                "segment": int(seg) if np.issubdtype(np.asarray(seg).dtype, np.integer) else str(seg),
                "n_observations": n,
                "weight": float(weight),
                "within_segment_mi": float(mi),
                "weighted_contribution": float(contribution),
            }
        )
    return (float(value), components) if return_components else float(value)


def positional_information(motif: Any, segment: Any) -> float:
    return mutual_information(motif, segment)


def _permute_within_segment(state: np.ndarray, segment: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    permuted = np.array(state, copy=True)
    for seg in np.unique(segment):
        idx = np.flatnonzero(segment == seg)
        permuted[idx] = state[idx][rng.permutation(len(idx))]
    return permuted


@dataclass(frozen=True)
class CorrectedInformation:
    observed: float
    permutation_mean: float
    corrected: float
    permutation_std: float
    n_permutations: int


def corrected_conditional_mutual_information(
    motif: Any,
    state: Any,
    segment: Any,
    *,
    n_permutations: int,
    stream: PermutationStream,
) -> CorrectedInformation:
    if n_permutations < 1:
        raise ValueError("n_permutations must be positive")
    motif, state, segment = _vectors(motif, state, segment)
    observed = conditional_mutual_information(motif, state, segment)
    rng = stream.generator()
    null = np.empty(n_permutations, dtype=float)
    for i in range(n_permutations):
        null[i] = conditional_mutual_information(motif, _permute_within_segment(state, segment, rng), segment)
    mean = float(null.mean())
    return CorrectedInformation(
        observed=float(observed),
        permutation_mean=mean,
        corrected=float(observed - mean),
        permutation_std=float(null.std(ddof=1)) if n_permutations > 1 else 0.0,
        n_permutations=int(n_permutations),
    )


def constant_grouping(n_motifs: int = 4**5) -> np.ndarray:
    return np.zeros(int(n_motifs), dtype=np.int64)


def identity_grouping(n_motifs: int = 4**5) -> np.ndarray:
    return np.arange(int(n_motifs), dtype=np.int64)


def _assignment_array(grouping: Any, motifs: np.ndarray | None = None) -> np.ndarray:
    if isinstance(grouping, Mapping):
        if motifs is None:
            keys = sorted(int(k) for k in grouping)
            if keys != list(range(len(keys))):
                raise ValueError("mapping keys must form a dense 0..n-1 motif domain when motifs are omitted")
            return np.asarray([grouping[k] for k in keys])
        try:
            return np.asarray([grouping[int(m)] for m in motifs])
        except KeyError as exc:
            raise ValueError(f"grouping map lacks motif {exc.args[0]}") from exc
    assignment = np.asarray(grouping).reshape(-1)
    if motifs is None:
        return assignment
    motif_int = np.asarray(motifs, dtype=np.int64)
    if motif_int.min() < 0 or motif_int.max() >= len(assignment):
        raise ValueError("motif outside grouping assignment domain")
    return assignment[motif_int]


def canonicalize_grouping(grouping: Any) -> np.ndarray:
    assignment = _assignment_array(grouping)
    mapping = {}
    next_label = 0
    canonical = np.empty(len(assignment), dtype=np.int64)
    for i, label in enumerate(assignment.tolist()):
        key = str(label)
        if key not in mapping:
            mapping[key] = next_label
            next_label += 1
        canonical[i] = mapping[key]
    return canonical


def grouping_hash(grouping: Any) -> str:
    canonical = canonicalize_grouping(grouping).astype("<i8", copy=False)
    return hashlib.sha256(canonical.tobytes()).hexdigest()


def retained_information(motif: Any, state: Any, segment: Any, grouping: Any) -> float:
    motif, state, segment = _vectors(motif, state, segment)
    grouped = _assignment_array(grouping, np.asarray(motif, dtype=np.int64))
    return conditional_mutual_information(grouped, state, segment)


def corrected_retained_information(
    motif: Any,
    state: Any,
    segment: Any,
    grouping: Any,
    *,
    n_permutations: int,
    stream: PermutationStream,
) -> CorrectedInformation:
    motif, state, segment = _vectors(motif, state, segment)
    grouped = _assignment_array(grouping, np.asarray(motif, dtype=np.int64))
    return corrected_conditional_mutual_information(
        grouped,
        state,
        segment,
        n_permutations=n_permutations,
        stream=stream,
    )


@dataclass(frozen=True)
class InformationMeasureRecord:
    baseline_replicate: str
    observation_seed: int
    map_hash: str
    permutation_root_seed: int
    permutation_stream_index: int
    total_information: float
    positional_information: float
    conditional_information: float
    corrected_conditional_information: float
    retained_information: float | None = None
    corrected_retained_information: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
