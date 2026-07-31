"""Phase 5 focused causal-specificity controls for the JRSI revision.

The Phase 4 core archive is read-only.  This module applies the prespecified
selection, mapping, stable-topology, and unstable-topology controls at p=1.0.
The independently evolved matched seed block remains the inferential unit.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd

from .information import (
    corrected_conditional_mutual_information,
    mutual_information,
    positional_information,
    retained_information,
)
from .interventions import _group_affinity_matrix, segment_indices_for_observations
from .original_model.config import default_parameters
from .original_model.simulation import init_population, observe_population
from .phase4 import (
    PRODUCTION_ROOT_SEED as PHASE4_ROOT_SEED,
    Phase4Settings,
    array_sha256,
    load_map_panel,
    stable_integer_seed,
)
from .rng import AnalysisStream, ContinuationStream, PermutationStream, make_generator
from .statistical_pipeline import TargetRule, analyze_replicate_frontiers


PHASE5_ROOT_SEED = 2026073105
PRIMARY_FIDELITY = 1.0
SELECTION_NEUTRAL = 0.0
SELECTION_REDUCED = 0.25
SELECTION_FULL = 1.0
N_DISRUPTION_REALIZATIONS = 2


@dataclass(frozen=True)
class Phase5Settings:
    n_baseline_replicates: int = 20
    continuation_count: int = 2
    intervention_horizon: int = 36
    target_tolerance: float = 0.01
    n_information_permutations: int = 200
    n_bootstrap: int = 2000
    n_inference_permutations: int = 9999
    root_seed: int = PHASE5_ROOT_SEED
    phase4_root_seed: int = PHASE4_ROOT_SEED
    workers: int = 4

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FitnessTopology:
    topology_id: str
    categories: tuple[str, ...]
    productive_pairs: np.ndarray
    anti_pairs: np.ndarray
    topology_hash: str
    is_native: bool


OFF_DIAGONAL_PAIRS = tuple(combinations(range(4), 2))


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


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_phase4_manifest(phase4_dir: Path) -> pd.DataFrame:
    """Verify every file listed in the archived Phase 4 manifest."""
    manifest = pd.read_csv(phase4_dir / "FILE_MANIFEST_SHA256.csv")
    rows = []
    for row in manifest.itertuples(index=False):
        path = phase4_dir / str(row.relative_path)
        exists = path.is_file()
        actual_size = int(path.stat().st_size) if exists else -1
        actual_hash = _file_sha256(path) if exists else "missing"
        rows.append(
            {
                "relative_path": str(row.relative_path),
                "expected_size_bytes": int(row.size_bytes),
                "actual_size_bytes": actual_size,
                "expected_sha256": str(row.sha256),
                "actual_sha256": actual_hash,
                "matches": bool(exists and actual_size == int(row.size_bytes) and actual_hash == str(row.sha256)),
            }
        )
    return pd.DataFrame(rows)


def _topology_hash(productive: np.ndarray, anti: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(productive, dtype=np.uint8).tobytes())
    h.update(np.ascontiguousarray(anti, dtype=np.uint8).tobytes())
    return h.hexdigest()


def topology_categories(productive: np.ndarray, anti: np.ndarray) -> tuple[str, ...]:
    categories = []
    for a, b in OFF_DIAGONAL_PAIRS:
        if productive[a, b]:
            categories.append("P")
        elif anti[a, b]:
            categories.append("R")
        else:
            categories.append("N")
    return tuple(categories)


def enumerate_matched_topologies() -> list[FitnessTopology]:
    """Enumerate all 30 symmetric topologies with native category counts."""
    params = default_parameters()
    native_categories = topology_categories(params["productive_pairs"], params["anti_pairs"])
    category_vectors = []
    for reducing_idx in range(len(OFF_DIAGONAL_PAIRS)):
        for neutral_idx in range(len(OFF_DIAGONAL_PAIRS)):
            if neutral_idx == reducing_idx:
                continue
            categories = tuple(
                "R" if i == reducing_idx else "N" if i == neutral_idx else "P"
                for i in range(len(OFF_DIAGONAL_PAIRS))
            )
            category_vectors.append(categories)
    category_vectors = sorted(set(category_vectors))
    topologies = []
    for index, categories in enumerate(category_vectors):
        productive = np.zeros((4, 4), dtype=np.bool_)
        anti = np.zeros((4, 4), dtype=np.bool_)
        np.fill_diagonal(anti, True)
        for category, (a, b) in zip(categories, OFF_DIAGONAL_PAIRS):
            if category == "P":
                productive[a, b] = productive[b, a] = True
            elif category == "R":
                anti[a, b] = anti[b, a] = True
        topologies.append(
            FitnessTopology(
                topology_id=f"topology_{index:02d}",
                categories=categories,
                productive_pairs=productive,
                anti_pairs=anti,
                topology_hash=_topology_hash(productive, anti),
                is_native=categories == native_categories,
            )
        )
    if len(topologies) != 30 or sum(t.is_native for t in topologies) != 1:
        raise RuntimeError("matched topology enumeration failed")
    return topologies


def categorical_hamming(a: FitnessTopology, b: FitnessTopology) -> int:
    return int(sum(x != y for x, y in zip(a.categories, b.categories)))


def select_alternative_topologies(topologies: Sequence[FitnessTopology]) -> tuple[FitnessTopology, FitnessTopology, FitnessTopology]:
    native = next(t for t in topologies if t.is_native)
    nonnative = [t for t in topologies if not t.is_native]
    max_native = max(categorical_hamming(t, native) for t in nonnative)
    topology_a = min(
        (t for t in nonnative if categorical_hamming(t, native) == max_native),
        key=lambda t: (t.categories, t.topology_id),
    )
    scores = {
        t.topology_id: min(categorical_hamming(t, native), categorical_hamming(t, topology_a))
        for t in nonnative
        if t.topology_id != topology_a.topology_id
    }
    max_score = max(scores.values())
    topology_b = min(
        (t for t in nonnative if t.topology_id != topology_a.topology_id and scores[t.topology_id] == max_score),
        key=lambda t: (t.categories, t.topology_id),
    )
    return native, topology_a, topology_b


def save_topology_manifest(topologies: Sequence[FitnessTopology], outdir: Path) -> pd.DataFrame:
    outdir.mkdir(parents=True, exist_ok=True)
    native, topology_a, topology_b = select_alternative_topologies(topologies)
    rows = []
    arrays: dict[str, np.ndarray] = {}
    for topology in topologies:
        arrays[f"{topology.topology_id}_productive"] = topology.productive_pairs.astype(np.uint8)
        arrays[f"{topology.topology_id}_anti"] = topology.anti_pairs.astype(np.uint8)
        rows.append(
            {
                "topology_id": topology.topology_id,
                "topology_hash": topology.topology_hash,
                "categories_for_pairs_01_02_03_12_13_23": "".join(topology.categories),
                "is_native": topology.is_native,
                "is_alternative_a": topology.topology_id == topology_a.topology_id,
                "is_alternative_b": topology.topology_id == topology_b.topology_id,
                "distance_from_native": categorical_hamming(topology, native),
                "distance_from_a": categorical_hamming(topology, topology_a),
                "distance_from_b": categorical_hamming(topology, topology_b),
                "n_promoting_directed": int(topology.productive_pairs.sum()),
                "n_reducing_directed": int(topology.anti_pairs.sum()),
                "n_neutral_directed": int(16 - topology.productive_pairs.sum() - topology.anti_pairs.sum()),
            }
        )
    np.savez_compressed(outdir / "topology_matrices.npz", **arrays)
    frame = pd.DataFrame(rows).sort_values("topology_id")
    frame.to_csv(outdir / "topology_manifest.csv", index=False)
    return frame


def apply_topology(params: dict[str, Any], topology: FitnessTopology) -> dict[str, Any]:
    out = dict(params)
    out["productive_pairs"] = np.asarray(topology.productive_pairs, dtype=np.bool_)
    out["anti_pairs"] = np.asarray(topology.anti_pairs, dtype=np.bool_)
    return out


def selection_probabilities(fitnesses: np.ndarray, selection_strength: float) -> np.ndarray:
    alpha = float(selection_strength)
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("selection_strength must lie in [0,1]")
    fitnesses = np.maximum(np.asarray(fitnesses, dtype=float), 0.0)
    n = len(fitnesses)
    total = float(fitnesses.sum())
    fitness_probs = fitnesses / total if total > 0 else np.full(n, 1.0 / n)
    probs = (1.0 - alpha) * np.full(n, 1.0 / n) + alpha * fitness_probs
    return probs / probs.sum()


def reproduce_with_selection_strength(
    pop: np.ndarray,
    fitnesses: np.ndarray,
    mu: float,
    inherit_prob: float,
    rng: np.random.Generator,
    selection_strength: float,
) -> np.ndarray:
    """Phase 4 propagation law with only parent-selection strength varied."""
    probs = selection_probabilities(fitnesses, selection_strength)
    n_cells, n_seqs, seq_len = pop.shape
    parent_uniforms = rng.random(n_cells)
    parent_indices = np.searchsorted(np.cumsum(probs), parent_uniforms, side="right")
    parent_indices = np.minimum(parent_indices, n_cells - 1)
    inherit_mask = rng.random((n_cells, n_seqs)) < inherit_prob
    parent_sequence_indices = rng.integers(0, n_seqs, size=(n_cells, n_seqs))
    environmental = rng.integers(0, 4, size=(n_cells, n_seqs, seq_len), dtype=np.int8)
    inherited = pop[parent_indices[:, None], parent_sequence_indices]
    new_pop = np.where(inherit_mask[:, :, None], inherited, environmental).astype(np.int8, copy=False)
    mutation_mask = rng.random((n_cells, n_seqs, seq_len)) < mu
    offsets = rng.integers(1, 4, size=(n_cells, n_seqs, seq_len), dtype=np.int8)
    mutated = ((new_pop.astype(np.int16) + offsets.astype(np.int16)) % 4).astype(np.int8)
    return np.where(mutation_mask, mutated, new_pop).astype(np.int8, copy=False)


def generate_topology_schedule(
    topologies: Sequence[FitnessTopology],
    *,
    root_seed: int,
    purpose: str,
    keys: Sequence[Any],
    length: int,
) -> list[str]:
    if length < 1:
        raise ValueError("topology schedule length must be positive")
    rng = make_generator(root_seed, purpose, *keys)
    ids = [t.topology_id for t in topologies]
    schedule: list[str] = []
    previous: str | None = None
    for _ in range(length):
        choices = ids if previous is None else [x for x in ids if x != previous]
        selected = str(choices[int(rng.integers(0, len(choices)))])
        schedule.append(selected)
        previous = selected
    return schedule


def run_control_evolution(
    *,
    run_seed: int,
    motif_affinity_matrix: np.ndarray,
    params: dict[str, Any],
    inherit_prob: float,
    selection_strength: float,
    fixed_topology: FitnessTopology | None = None,
    topology_schedule: Sequence[str] | None = None,
    topology_lookup: dict[str, FitnessTopology] | None = None,
) -> dict[str, Any]:
    """Evolve one matched baseline under a fixed or changing fitness topology."""
    if (fixed_topology is None) == (topology_schedule is None):
        raise ValueError("provide exactly one of fixed_topology or topology_schedule")
    if topology_schedule is not None and len(topology_schedule) != int(params["n_gens"]) + 1:
        raise ValueError("dynamic baseline schedule must include n_gens plus final observation topology")
    initialization_rng = make_generator(run_seed, "baseline-initialization")
    observation_rng = make_generator(run_seed, "baseline-observation")
    propagation_rng = make_generator(run_seed, "baseline-propagation")
    population = init_population(params["n_cells"], params["n_seqs"], params["seq_len"], initialization_rng)
    fitness_history = []
    for generation in range(int(params["n_gens"])):
        topology = fixed_topology if fixed_topology is not None else topology_lookup[str(topology_schedule[generation])]
        step_params = apply_topology(params, topology)
        fitnesses, _, _ = observe_population(population, motif_affinity_matrix, step_params, observation_rng)
        fitness_history.append(float(np.mean(fitnesses)))
        population = reproduce_with_selection_strength(
            population,
            fitnesses,
            params["mutation_rate"],
            inherit_prob,
            propagation_rng,
            selection_strength,
        )
    final_topology = fixed_topology if fixed_topology is not None else topology_lookup[str(topology_schedule[-1])]
    final_params = apply_topology(params, final_topology)
    final_fitnesses, final_motifs, final_states = observe_population(
        population, motif_affinity_matrix, final_params, observation_rng
    )
    return {
        "population": np.asarray(population),
        "fitness_trajectory": np.asarray(fitness_history, dtype=float),
        "final_fitnesses": np.asarray(final_fitnesses, dtype=float),
        "final_motifs": np.asarray(final_motifs, dtype=np.int64),
        "final_states": np.asarray(final_states, dtype=np.int64),
        "final_topology_id": final_topology.topology_id,
        "rng_state": {
            "initialization": initialization_rng.bit_generator.state,
            "observation": observation_rng.bit_generator.state,
            "propagation": propagation_rng.bit_generator.state,
        },
    }


def simulate_control_horizon(
    *,
    population: np.ndarray,
    motif_affinity_matrix: np.ndarray,
    params: dict[str, Any],
    inherit_prob: float,
    horizon: int,
    selection_strength: float,
    stream: ContinuationStream,
    fixed_topology: FitnessTopology | None = None,
    topology_schedule: Sequence[str] | None = None,
    topology_lookup: dict[str, FitnessTopology] | None = None,
) -> dict[str, Any]:
    if (fixed_topology is None) == (topology_schedule is None):
        raise ValueError("provide exactly one of fixed_topology or topology_schedule")
    if topology_schedule is not None and len(topology_schedule) != int(horizon):
        raise ValueError("dynamic continuation schedule must match horizon")
    observation_rng = stream.observation_generator()
    propagation_rng = stream.propagation_generator()
    pop = np.array(population, copy=True)
    means = []
    for generation in range(int(horizon)):
        topology = fixed_topology if fixed_topology is not None else topology_lookup[str(topology_schedule[generation])]
        step_params = apply_topology(params, topology)
        fitnesses, _, _ = observe_population(pop, motif_affinity_matrix, step_params, observation_rng)
        means.append(float(np.mean(fitnesses)))
        pop = reproduce_with_selection_strength(
            pop,
            fitnesses,
            params["mutation_rate"],
            inherit_prob,
            propagation_rng,
            selection_strength,
        )
    return {
        "mean_fitness": np.asarray(means, dtype=float),
        "final_population": np.asarray(pop),
    }


def complete_profile_derangement(n_items: int, rng: np.random.Generator) -> np.ndarray:
    if n_items < 2:
        raise ValueError("derangement requires at least two items")
    for _ in range(10000):
        permutation = rng.permutation(n_items)
        if not np.any(permutation == np.arange(n_items)):
            return permutation.astype(np.int64)
    raise RuntimeError("failed to generate complete profile derangement")


def _observe_information(
    *,
    population: np.ndarray,
    matrix: np.ndarray,
    params: dict[str, Any],
    topology: FitnessTopology,
    root_seed: int,
    observation_key: str,
    permutation_key: str,
    n_permutations: int,
) -> dict[str, Any]:
    observation_rng = make_generator(root_seed, "phase5-information-observation", observation_key)
    fitnesses, motifs, states = observe_population(population, matrix, apply_topology(params, topology), observation_rng)
    segments = segment_indices_for_observations(params)
    corrected = corrected_conditional_mutual_information(
        motifs,
        states,
        segments,
        n_permutations=n_permutations,
        stream=PermutationStream(root_seed, permutation_key, 0),
    )
    return {
        "fitnesses": fitnesses,
        "motifs": motifs,
        "states": states,
        "segments": segments,
        "total_information": mutual_information(motifs, states),
        "positional_information": positional_information(motifs, segments),
        "conditional_information": corrected.observed,
        "permutation_mean": corrected.permutation_mean,
        "permutation_std": corrected.permutation_std,
        "corrected_conditional_information": corrected.corrected,
    }


def _save_state(path: Path, result: dict[str, Any], information: dict[str, Any], schedule: Sequence[str] | None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "population": result["population"],
        "fitness_trajectory": result["fitness_trajectory"],
        "final_observation_fitnesses": information["fitnesses"],
        "final_observation_motifs": information["motifs"],
        "final_observation_states": information["states"],
        "final_observation_segments": information["segments"],
    }
    if schedule is not None:
        payload["topology_schedule"] = np.asarray(schedule, dtype="U16")
    np.savez_compressed(path, **payload)
    path.with_suffix(".rng.json").write_text(
        json.dumps(_json_ready(result["rng_state"]), indent=2), encoding="utf-8"
    )


def _baseline_job(job: dict[str, Any]) -> dict[str, Any]:
    settings = Phase5Settings(**job["settings"])
    params = default_parameters()
    topologies = enumerate_matched_topologies()
    lookup = {t.topology_id: t for t in topologies}
    native, topology_a, topology_b = select_alternative_topologies(topologies)
    topology_by_mode = {"selection_neutral": native, "selection_reduced": native, "alternative_a": topology_a, "alternative_b": topology_b}
    alpha_by_mode = {"selection_neutral": SELECTION_NEUTRAL, "selection_reduced": SELECTION_REDUCED, "alternative_a": SELECTION_FULL, "alternative_b": SELECTION_FULL, "temporally_unstable": SELECTION_FULL}
    mode = str(job["mode"])
    replicate = int(job["replicate"])
    phase4_row = job["phase4_row"]
    pair_id = str(phase4_row["baseline_replicate"])
    run_seed = int(phase4_row["baseline_run_seed"])
    schedule = None
    fixed_topology = topology_by_mode.get(mode)
    if mode == "temporally_unstable":
        schedule = generate_topology_schedule(
            topologies,
            root_seed=settings.root_seed,
            purpose="phase5-unstable-topology-baseline",
            keys=(pair_id,),
            length=int(params["n_gens"]) + 1,
        )
    result = run_control_evolution(
        run_seed=run_seed,
        motif_affinity_matrix=params["motif_affinity_matrix"],
        params=params,
        inherit_prob=PRIMARY_FIDELITY,
        selection_strength=alpha_by_mode[mode],
        fixed_topology=fixed_topology,
        topology_schedule=schedule,
        topology_lookup=lookup,
    )
    information_topology = fixed_topology if fixed_topology is not None else lookup[result["final_topology_id"]]
    baseline_id = f"{mode}_p1.0_r{replicate:02d}"
    information = _observe_information(
        population=result["population"],
        matrix=params["motif_affinity_matrix"],
        params=params,
        topology=information_topology,
        root_seed=settings.root_seed,
        observation_key=baseline_id,
        permutation_key=baseline_id,
        n_permutations=settings.n_information_permutations,
    )
    state_path = Path(job["state_dir"]) / mode / f"rep_{replicate:02d}.npz"
    _save_state(state_path, result, information, schedule)
    schedule_path = ""
    if schedule is not None:
        schedule_file = Path(job["schedule_dir"]) / f"{baseline_id}_baseline_schedule.json"
        schedule_file.parent.mkdir(parents=True, exist_ok=True)
        schedule_file.write_text(json.dumps(schedule, indent=2), encoding="utf-8")
        schedule_path = str(schedule_file)
    return {
        "mode": mode,
        "condition": mode,
        "replicate": replicate,
        "seed_block": replicate,
        "pairing_baseline_replicate": pair_id,
        "baseline_replicate": baseline_id,
        "baseline_run_seed": run_seed,
        "selection_strength": alpha_by_mode[mode],
        "evolution_topology_id": fixed_topology.topology_id if fixed_topology is not None else "temporally_unstable",
        "final_topology_id": result["final_topology_id"],
        "state_path": str(state_path),
        "schedule_path": schedule_path,
        "state_hash": array_sha256(result["population"]),
        "trajectory_hash": array_sha256(result["fitness_trajectory"]),
        "final_mean_fitness": float(np.mean(information["fitnesses"])),
        "total_information": information["total_information"],
        "positional_information": information["positional_information"],
        "conditional_information": information["conditional_information"],
        "permutation_mean": information["permutation_mean"],
        "permutation_std": information["permutation_std"],
        "corrected_conditional_information": information["corrected_conditional_information"],
    }


def run_control_baselines(
    outdir: Path,
    settings: Phase5Settings,
    phase4_baselines: pd.DataFrame,
    *,
    resume: bool = True,
) -> pd.DataFrame:
    path = outdir / "control_baseline_information.csv"
    if resume and path.exists():
        return pd.read_csv(path)
    state_dir = outdir / "states"
    schedule_dir = outdir / "topology_schedules"
    p1 = phase4_baselines[(phase4_baselines["condition"] == "selective") & np.isclose(phase4_baselines["inherit_prob"], PRIMARY_FIDELITY)].sort_values("replicate")
    if len(p1) != settings.n_baseline_replicates:
        raise RuntimeError("Phase 4 archive lacks the required 20 selective p=1.0 baselines")
    jobs = []
    for mode in ("selection_neutral", "selection_reduced", "alternative_a", "alternative_b", "temporally_unstable"):
        for row in p1.itertuples(index=False):
            jobs.append(
                {
                    "mode": mode,
                    "replicate": int(row.replicate),
                    "phase4_row": row._asdict(),
                    "settings": settings.to_dict(),
                    "state_dir": str(state_dir),
                    "schedule_dir": str(schedule_dir),
                }
            )
    rows = []
    with ProcessPoolExecutor(max_workers=settings.workers) as executor:
        futures = [executor.submit(_baseline_job, job) for job in jobs]
        for index, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if index % 10 == 0 or index == len(futures):
                print(f"Phase 5 baseline controls: {index}/{len(futures)}", flush=True)
    frame = pd.DataFrame(rows).sort_values(["mode", "replicate"])
    frame.to_csv(path, index=False)
    return frame


def _make_evaluation_specs(
    *,
    settings: Phase5Settings,
    phase4_dir: Path,
    phase4_baselines: pd.DataFrame,
    control_baselines: pd.DataFrame,
) -> list[dict[str, Any]]:
    params = default_parameters()
    topologies = enumerate_matched_topologies()
    lookup = {t.topology_id: t for t in topologies}
    native, topology_a, topology_b = select_alternative_topologies(topologies)
    p1 = phase4_baselines[(phase4_baselines["condition"] == "selective") & np.isclose(phase4_baselines["inherit_prob"], PRIMARY_FIDELITY)].sort_values("replicate")
    specs: list[dict[str, Any]] = []

    for row in control_baselines.itertuples(index=False):
        mode = str(row.mode)
        if mode == "selection_neutral":
            evaluations = [("selection_neutral", native, SELECTION_NEUTRAL, None)]
        elif mode == "selection_reduced":
            evaluations = [("selection_reduced", native, SELECTION_REDUCED, None)]
        elif mode == "alternative_a":
            evaluations = [
                ("alternative_a_native", topology_a, SELECTION_FULL, None),
                ("alternative_a_cross_b", topology_b, SELECTION_FULL, None),
            ]
        elif mode == "alternative_b":
            evaluations = [
                ("alternative_b_native", topology_b, SELECTION_FULL, None),
                ("alternative_b_cross_a", topology_a, SELECTION_FULL, None),
            ]
        elif mode == "temporally_unstable":
            evaluations = [("temporally_unstable", None, SELECTION_FULL, "dynamic")]
        else:
            raise ValueError(f"unknown baseline mode: {mode}")
        for condition, topology, alpha, dynamic in evaluations:
            specs.append(
                {
                    "condition": condition,
                    "control_family": condition,
                    "realization": 0,
                    "seed_block": int(row.seed_block),
                    "pairing_baseline_replicate": str(row.pairing_baseline_replicate),
                    "baseline_replicate": f"{condition}_p1.0_r{int(row.replicate):02d}",
                    "state_path": str(row.state_path),
                    "affinity_mode": "native",
                    "affinity_permutation": None,
                    "fixed_topology_id": topology.topology_id if topology is not None else None,
                    "dynamic_topology": dynamic is not None,
                    "selection_strength": alpha,
                    "baseline_information_source": "control_state",
                    "source_baseline_id": str(row.baseline_replicate),
                }
            )

    for row in p1.itertuples(index=False):
        replicate = int(row.replicate)
        pair_id = str(row.baseline_replicate)
        for realization in range(N_DISRUPTION_REALIZATIONS):
            rng = make_generator(settings.root_seed, "phase5-affinity-derangement", pair_id, realization)
            permutation = complete_profile_derangement(4**5, rng)
            specs.append(
                {
                    "condition": "affinity_reassigned",
                    "control_family": "affinity_reassigned",
                    "realization": realization,
                    "seed_block": replicate,
                    "pairing_baseline_replicate": pair_id,
                    "baseline_replicate": f"affinity_reassigned_p1.0_r{replicate:02d}_q{realization}",
                    "state_path": str(row.state_path),
                    "affinity_mode": "deranged",
                    "affinity_permutation": permutation.tolist(),
                    "fixed_topology_id": native.topology_id,
                    "dynamic_topology": False,
                    "selection_strength": SELECTION_FULL,
                    "baseline_information_source": "reobserve",
                    "source_baseline_id": pair_id,
                }
            )
        mismatch_rng = make_generator(settings.root_seed, "phase5-topology-mismatch", pair_id)
        candidates = [t for t in topologies if not t.is_native]
        chosen = mismatch_rng.choice(len(candidates), size=N_DISRUPTION_REALIZATIONS, replace=False)
        for realization, choice in enumerate(chosen):
            topology = candidates[int(choice)]
            specs.append(
                {
                    "condition": "topology_mismatch",
                    "control_family": "topology_mismatch",
                    "realization": realization,
                    "seed_block": replicate,
                    "pairing_baseline_replicate": pair_id,
                    "baseline_replicate": f"topology_mismatch_p1.0_r{replicate:02d}_q{realization}",
                    "state_path": str(row.state_path),
                    "affinity_mode": "native",
                    "affinity_permutation": None,
                    "fixed_topology_id": topology.topology_id,
                    "dynamic_topology": False,
                    "selection_strength": SELECTION_FULL,
                    "baseline_information_source": "phase4_archive",
                    "source_baseline_id": pair_id,
                }
            )
    return specs


def _evaluation_job(job: dict[str, Any]) -> str:
    settings = Phase5Settings(**job["settings"])
    spec = job["spec"]
    outdir = Path(job["outdir"])
    panel = load_map_panel(Path(job["map_dir"]))
    params = default_parameters()
    topologies = enumerate_matched_topologies()
    lookup = {t.topology_id: t for t in topologies}
    native, _, _ = select_alternative_topologies(topologies)
    loaded = np.load(spec["state_path"])
    population = np.asarray(loaded["population"])
    matrix = np.asarray(params["motif_affinity_matrix"])
    if spec["affinity_mode"] == "deranged":
        permutation = np.asarray(spec["affinity_permutation"], dtype=np.int64)
        matrix = matrix[permutation]
    fixed_topology = lookup[str(spec["fixed_topology_id"])] if spec["fixed_topology_id"] is not None else None
    information_topology = fixed_topology if fixed_topology is not None else native
    if spec["baseline_information_source"] == "phase4_archive":
        motifs = np.asarray(loaded["final_observation_motifs"])
        states = np.asarray(loaded["final_observation_states"])
        segments = np.asarray(loaded["final_observation_segments"])
        baseline_information = float(job["phase4_conditional_information"])
        info_record = None
    elif spec["baseline_information_source"] == "control_state":
        motifs = np.asarray(loaded["final_observation_motifs"])
        states = np.asarray(loaded["final_observation_states"])
        segments = np.asarray(loaded["final_observation_segments"])
        baseline_information = float(job["control_conditional_information"])
        info_record = None
    else:
        info_record = _observe_information(
            population=population,
            matrix=matrix,
            params=params,
            topology=information_topology,
            root_seed=settings.root_seed,
            observation_key=spec["baseline_replicate"],
            permutation_key=spec["baseline_replicate"],
            n_permutations=settings.n_information_permutations,
        )
        motifs = info_record["motifs"]
        states = info_record["states"]
        segments = info_record["segments"]
        baseline_information = float(info_record["conditional_information"])
    info_row = {
        "condition": spec["condition"],
        "control_family": spec["control_family"],
        "realization": int(spec["realization"]),
        "seed_block": int(spec["seed_block"]),
        "baseline_replicate": spec["baseline_replicate"],
        "source_baseline_id": spec["source_baseline_id"],
        "affinity_mode": spec["affinity_mode"],
        "fixed_topology_id": spec["fixed_topology_id"] or "temporally_unstable",
        "selection_strength": float(spec["selection_strength"]),
        "conditional_information": baseline_information,
        "corrected_conditional_information": float(info_record["corrected_conditional_information"]) if info_record is not None else np.nan,
        "profile_permutation_hash": array_sha256(np.asarray(spec["affinity_permutation"], dtype=np.int64)) if spec["affinity_permutation"] is not None else "",
        "n_profile_fixed_points": int(np.sum(np.asarray(spec["affinity_permutation"]) == np.arange(4**5))) if spec["affinity_permutation"] is not None else np.nan,
    }
    info_dir = outdir / "evaluation_information_blocks"
    info_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([info_row]).to_csv(info_dir / f"{spec['baseline_replicate']}.csv", index=False)

    rows = []
    schedule_dir = outdir / "topology_schedules"
    for continuation_index in range(settings.continuation_count):
        stream = ContinuationStream(settings.phase4_root_seed, spec["pairing_baseline_replicate"], continuation_index)
        schedule = None
        if spec["dynamic_topology"]:
            schedule = generate_topology_schedule(
                topologies,
                root_seed=settings.root_seed,
                purpose="phase5-unstable-topology-continuation",
                keys=(spec["pairing_baseline_replicate"], continuation_index),
                length=settings.intervention_horizon,
            )
            schedule_file = schedule_dir / f"{spec['baseline_replicate']}_c{continuation_index}_schedule.json"
            schedule_file.parent.mkdir(parents=True, exist_ok=True)
            schedule_file.write_text(json.dumps(schedule, indent=2), encoding="utf-8")
        actual = simulate_control_horizon(
            population=population,
            motif_affinity_matrix=matrix,
            params=params,
            inherit_prob=PRIMARY_FIDELITY,
            horizon=settings.intervention_horizon,
            selection_strength=float(spec["selection_strength"]),
            stream=stream,
            fixed_topology=fixed_topology,
            topology_schedule=schedule,
            topology_lookup=lookup,
        )
        actual_curve = np.asarray(actual["mean_fitness"], dtype=float)
        common = {
            "condition": spec["condition"],
            "control_family": spec["control_family"],
            "realization": int(spec["realization"]),
            "seed_block": int(spec["seed_block"]),
            "source_baseline_id": spec["source_baseline_id"],
            "pairing_baseline_replicate": spec["pairing_baseline_replicate"],
            "baseline_replicate": spec["baseline_replicate"],
            "selection_strength": float(spec["selection_strength"]),
            "evaluation_topology_id": spec["fixed_topology_id"] or "temporally_unstable",
            "continuation_root_seed": settings.phase4_root_seed,
            "continuation_stream_key": f"{spec['pairing_baseline_replicate']}|{continuation_index}",
        }
        rows.append(
            {
                **common,
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
            }
        )
        for item in panel:
            grouped = _group_affinity_matrix(matrix, item["labels"])
            result = simulate_control_horizon(
                population=population,
                motif_affinity_matrix=grouped,
                params=params,
                inherit_prob=PRIMARY_FIDELITY,
                horizon=settings.intervention_horizon,
                selection_strength=float(spec["selection_strength"]),
                stream=stream,
                fixed_topology=fixed_topology,
                topology_schedule=schedule,
                topology_lookup=lookup,
            )
            curve = np.asarray(result["mean_fitness"], dtype=float)
            rows.append(
                {
                    **common,
                    "map_id": item["map_id"],
                    "map_hash": item["map_hash"],
                    "method": item["method"],
                    "endpoint_type": item["endpoint_type"],
                    "actual_groups": int(item["actual_groups"]),
                    "retained_information": float(retained_information(motifs, states, segments, item["labels"])),
                    "baseline_information": baseline_information,
                    "continuation_index": continuation_index,
                    "viability": float(curve.mean()),
                    "mean_fitness_trajectory_json": json.dumps(curve.tolist()),
                    "final_population_hash": array_sha256(result["final_population"]),
                }
            )
    block_dir = outdir / "continuation_blocks"
    block_dir.mkdir(parents=True, exist_ok=True)
    path = block_dir / f"{spec['baseline_replicate']}.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return str(path)


def run_control_evaluations(
    outdir: Path,
    settings: Phase5Settings,
    phase4_dir: Path,
    phase4_baselines: pd.DataFrame,
    control_baselines: pd.DataFrame,
    *,
    resume: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw_path = outdir / "continuation_level_results.csv"
    info_path = outdir / "evaluation_information.csv"
    spec_path = outdir / "evaluation_specifications.json"
    specs = _make_evaluation_specs(
        settings=settings,
        phase4_dir=phase4_dir,
        phase4_baselines=phase4_baselines,
        control_baselines=control_baselines,
    )
    spec_path.write_text(json.dumps(_json_ready(specs), indent=2), encoding="utf-8")
    if resume and raw_path.exists() and info_path.exists():
        return pd.read_csv(raw_path), pd.read_csv(info_path), pd.DataFrame(specs)
    phase4_info = phase4_baselines.set_index("baseline_replicate")["conditional_information"].to_dict()
    control_info = control_baselines.set_index("baseline_replicate")["conditional_information"].to_dict()
    jobs = []
    for spec in specs:
        jobs.append(
            {
                "settings": settings.to_dict(),
                "spec": spec,
                "outdir": str(outdir),
                "map_dir": str(phase4_dir / "maps"),
                "phase4_conditional_information": phase4_info.get(spec["source_baseline_id"], np.nan),
                "control_conditional_information": control_info.get(spec["source_baseline_id"], np.nan),
            }
        )
    paths = []
    with ProcessPoolExecutor(max_workers=settings.workers) as executor:
        futures = [executor.submit(_evaluation_job, job) for job in jobs]
        for index, future in enumerate(as_completed(futures), start=1):
            paths.append(future.result())
            if index % 10 == 0 or index == len(futures):
                print(f"Phase 5 control evaluations: {index}/{len(futures)}", flush=True)
    raw = pd.concat([pd.read_csv(path) for path in sorted(paths)], ignore_index=True)
    raw.to_csv(raw_path, index=False)
    info_files = sorted((outdir / "evaluation_information_blocks").glob("*.csv"))
    info = pd.concat([pd.read_csv(path) for path in info_files], ignore_index=True)
    info.to_csv(info_path, index=False)
    return raw, info, pd.DataFrame(specs)


def _bh_adjust(pvalues: Iterable[float]) -> np.ndarray:
    p = np.asarray(list(pvalues), dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = np.minimum.accumulate((ranked * len(p) / np.arange(1, len(p) + 1))[::-1])[::-1]
    adjusted = np.minimum(adjusted, 1.0)
    out = np.empty_like(adjusted)
    out[order] = adjusted
    return out


def paired_sign_randomization(
    differences: np.ndarray,
    *,
    stream: AnalysisStream,
    n_permutations: int,
) -> dict[str, Any]:
    diffs = np.asarray(differences, dtype=float)
    if diffs.ndim != 1 or len(diffs) < 1 or not np.isfinite(diffs).all():
        raise ValueError("paired differences must be a finite one-dimensional array")
    observed = float(np.mean(diffs))
    exact_count = 2 ** len(diffs)
    if exact_count <= 100_000:
        permuted = np.asarray([np.mean(diffs * np.asarray(signs)) for signs in product([-1.0, 1.0], repeat=len(diffs))])
        p_value = float(np.mean(np.abs(permuted) >= abs(observed)))
        exact = True
    else:
        rng = stream.generator()
        signs = rng.choice(np.asarray([-1.0, 1.0]), size=(n_permutations, len(diffs)))
        permuted = np.mean(signs * diffs, axis=1)
        p_value = float((1 + np.sum(np.abs(permuted) >= abs(observed))) / (n_permutations + 1))
        exact = False
    return {
        "mean_difference": observed,
        "median_difference": float(np.median(diffs)),
        "p_value_two_sided": p_value,
        "n_seed_blocks": int(len(diffs)),
        "n_permutations": int(len(permuted)),
        "exact": exact,
        "fraction_positive": float(np.mean(diffs > 0)),
    }


def paired_bootstrap_interval(
    differences: np.ndarray,
    *,
    stream: AnalysisStream,
    n_bootstrap: int,
) -> tuple[float, float, np.ndarray]:
    diffs = np.asarray(differences, dtype=float)
    rng = stream.generator()
    indices = rng.integers(0, len(diffs), size=(n_bootstrap, len(diffs)))
    draws = diffs[indices].mean(axis=1)
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975)), draws


def _aggregate_realizations(summary: pd.DataFrame, spec_frame: pd.DataFrame) -> pd.DataFrame:
    meta = spec_frame[["condition", "baseline_replicate", "control_family", "realization", "seed_block", "source_baseline_id"]].drop_duplicates()
    merged = summary.merge(meta, on=["condition", "baseline_replicate"], how="left", validate="one_to_one")
    rows = []
    for (family, seed_block), part in merged.groupby(["control_family", "seed_block"], sort=True):
        all_reached = bool(part["target_reached"].astype(bool).all())
        rows.append(
            {
                "control_family": family,
                "seed_block": int(seed_block),
                "n_realizations": int(len(part)),
                "mean_value_of_information": float(part["value_of_information"].mean()),
                "mean_actual_viability": float(part["actual_viability"].mean()),
                "mean_constant_viability": float(part["constant_viability"].mean()),
                "n_target_reached": int(part["target_reached"].astype(bool).sum()),
                "all_target_reached": all_reached,
                "semantic_information_if_all_reached": float(part["semantic_information"].mean()) if all_reached else np.nan,
                "mean_semantic_lower_bound_among_censored": float(part.loc[~part["target_reached"].astype(bool), "semantic_lower_bound"].mean()) if not all_reached else np.nan,
                "all_identity_information_recovered": bool(part["identity_information_recovered"].all()),
                "all_identity_viability_recovered": bool(part["identity_viability_recovered"].all()),
            }
        )
    return pd.DataFrame(rows)


def analyze_phase5_results(
    outdir: Path,
    settings: Phase5Settings,
    phase4_dir: Path,
    raw: pd.DataFrame,
    spec_frame: pd.DataFrame,
) -> dict[str, Any]:
    analysis = analyze_replicate_frontiers(raw, target_rule=TargetRule(settings.target_tolerance))
    realization_summary = analysis.replicate_summary
    realization_summary.to_csv(outdir / "realization_frontier_summary.csv", index=False)
    analysis.frontier_points.to_csv(outdir / "realization_frontiers.csv", index=False)
    analysis.map_summary.to_csv(outdir / "realization_map_level_summary.csv", index=False)
    aggregated = _aggregate_realizations(realization_summary, spec_frame)
    aggregated.to_csv(outdir / "seed_block_control_summary.csv", index=False)

    phase4_summary = pd.read_csv(phase4_dir / "replicate_frontier_summary.csv")
    native = phase4_summary[(phase4_summary["condition"] == "selective") & np.isclose(phase4_summary["inherit_prob"], PRIMARY_FIDELITY)].copy()
    native["seed_block"] = native["baseline_replicate"].str.extract(r"r(\d+)$").astype(int)
    native = native[["seed_block", "value_of_information", "target_reached", "semantic_information", "semantic_lower_bound"]].rename(
        columns={"value_of_information": "native_full_voi"}
    )
    wide = aggregated.pivot(index="seed_block", columns="control_family", values="mean_value_of_information").reset_index()
    metrics = native.merge(wide, on="seed_block", how="inner", validate="one_to_one")
    required = {
        "selection_neutral", "selection_reduced", "affinity_reassigned", "topology_mismatch",
        "alternative_a_native", "alternative_a_cross_b", "alternative_b_native", "alternative_b_cross_a",
        "temporally_unstable",
    }
    missing = required.difference(metrics.columns)
    if missing:
        raise RuntimeError(f"missing Phase 5 control metrics: {sorted(missing)}")
    metrics["alternative_native_mean"] = 0.5 * (metrics["alternative_a_native"] + metrics["alternative_b_native"])
    metrics["alternative_cross_mean"] = 0.5 * (metrics["alternative_a_cross_b"] + metrics["alternative_b_cross_a"])
    metrics["contrast_full_minus_neutral"] = metrics["native_full_voi"] - metrics["selection_neutral"]
    metrics["contrast_full_minus_reduced"] = metrics["native_full_voi"] - metrics["selection_reduced"]
    metrics["contrast_native_minus_affinity_reassigned"] = metrics["native_full_voi"] - metrics["affinity_reassigned"]
    metrics["contrast_native_minus_topology_mismatch"] = metrics["native_full_voi"] - metrics["topology_mismatch"]
    metrics["contrast_alternative_native_minus_cross"] = metrics["alternative_native_mean"] - metrics["alternative_cross_mean"]
    metrics["contrast_stable_minus_unstable"] = metrics["alternative_native_mean"] - metrics["temporally_unstable"]
    metrics.to_csv(outdir / "gate5_seed_block_metrics.csv", index=False)

    contrast_specs = [
        ("full_minus_neutral", "contrast_full_minus_neutral"),
        ("full_minus_reduced", "contrast_full_minus_reduced"),
        ("native_minus_affinity_reassigned", "contrast_native_minus_affinity_reassigned"),
        ("native_minus_topology_mismatch", "contrast_native_minus_topology_mismatch"),
        ("alternative_native_minus_cross", "contrast_alternative_native_minus_cross"),
        ("stable_minus_unstable", "contrast_stable_minus_unstable"),
    ]
    rows = []
    draw_frames = []
    for contrast_name, column in contrast_specs:
        diffs = metrics[column].to_numpy(dtype=float)
        test = paired_sign_randomization(
            diffs,
            stream=AnalysisStream(settings.root_seed, "phase5-paired-randomization", contrast_name),
            n_permutations=settings.n_inference_permutations,
        )
        lower, upper, draws = paired_bootstrap_interval(
            diffs,
            stream=AnalysisStream(settings.root_seed, "phase5-paired-bootstrap", contrast_name),
            n_bootstrap=settings.n_bootstrap,
        )
        rows.append(
            {
                "contrast": contrast_name,
                **test,
                "bootstrap_95_lower": lower,
                "bootstrap_95_upper": upper,
                "analysis_unit": "matched independently evolved seed block",
            }
        )
        draw_frames.append(pd.DataFrame({"contrast": contrast_name, "bootstrap_index": np.arange(len(draws)), "mean_difference": draws}))
    contrasts = pd.DataFrame(rows)
    contrasts["q_value_bh_six_contrasts"] = _bh_adjust(contrasts["p_value_two_sided"])
    contrasts["contrast_passed"] = (contrasts["mean_difference"] > 0) & (contrasts["q_value_bh_six_contrasts"] < 0.05)
    contrasts.to_csv(outdir / "gate5_paired_contrasts.csv", index=False)
    pd.concat(draw_frames, ignore_index=True).to_csv(outdir / "gate5_paired_bootstrap_draws.csv", index=False)

    reach_rows = []
    merged = realization_summary.merge(
        spec_frame[["condition", "baseline_replicate", "control_family", "realization", "seed_block"]].drop_duplicates(),
        on=["condition", "baseline_replicate"],
        how="left",
    )
    for family, part in merged.groupby("control_family", sort=True):
        reach_rows.append(
            {
                "control_family": family,
                "n_frontier_realizations": int(len(part)),
                "n_seed_blocks": int(part["seed_block"].nunique()),
                "n_target_reached": int(part["target_reached"].astype(bool).sum()),
                "n_right_censored": int((~part["target_reached"].astype(bool)).sum()),
                "target_reached_fraction": float(part["target_reached"].astype(bool).mean()),
            }
        )
    pd.DataFrame(reach_rows).to_csv(outdir / "target_reach_and_censoring.csv", index=False)

    identity_ok = bool(realization_summary["identity_information_recovered"].all() and realization_summary["identity_viability_recovered"].all())
    archive_check = verify_phase4_manifest(phase4_dir)
    archive_check.to_csv(outdir / "phase4_archive_integrity_after.csv", index=False)
    archive_ok = bool(archive_check["matches"].all())
    gate_pass = bool(identity_ok and archive_ok and contrasts["contrast_passed"].all() and len(metrics) == settings.n_baseline_replicates)
    gate = {
        "gate": "Gate 5 - causal specificity",
        "status": "PASSED" if gate_pass else "FAILED",
        "primary_fidelity": PRIMARY_FIDELITY,
        "n_independent_seed_blocks": int(len(metrics)),
        "n_prespecified_contrasts": int(len(contrasts)),
        "n_contrasts_passed": int(contrasts["contrast_passed"].sum()),
        "all_six_contrasts_passed": bool(contrasts["contrast_passed"].all()),
        "all_identity_endpoints_recovered": identity_ok,
        "phase4_archive_unchanged": archive_ok,
        "censoring_retained": True,
        "primary_metric": "value_of_information",
        "multiple_testing": "Benjamini-Hochberg across six prespecified paired contrasts",
    }
    (outdir / "GATE_5_DECISION.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    return gate


def run_phase5_production(
    outdir: str | Path,
    *,
    phase4_dir: str | Path = "results/phase4_core",
    settings: Phase5Settings | None = None,
    resume: bool = True,
) -> dict[str, Any]:
    settings = settings or Phase5Settings()
    outdir = Path(outdir)
    phase4_dir = Path(phase4_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "phase5_settings.json").write_text(json.dumps(settings.to_dict(), indent=2), encoding="utf-8")
    before = verify_phase4_manifest(phase4_dir)
    before.to_csv(outdir / "phase4_archive_integrity_before.csv", index=False)
    if not before["matches"].all():
        raise RuntimeError("Phase 4 archive integrity check failed before Phase 5")
    topologies = enumerate_matched_topologies()
    topology_manifest = save_topology_manifest(topologies, outdir / "topologies")
    if len(topology_manifest) != 30:
        raise RuntimeError("unexpected topology universe")
    phase4_baselines = pd.read_csv(phase4_dir / "baseline_information.csv")
    control_baselines = run_control_baselines(outdir, settings, phase4_baselines, resume=resume)
    raw, information, specs = run_control_evaluations(
        outdir,
        settings,
        phase4_dir,
        phase4_baselines,
        control_baselines,
        resume=resume,
    )
    return analyze_phase5_results(outdir, settings, phase4_dir, raw, specs)
