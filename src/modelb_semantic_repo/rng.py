"""Purpose-separated random streams for reproducible revision analyses.

Streams are derived from stable SHA-256 labels rather than Python's randomized
``hash`` function.  The same specification reproduces exactly across processes;
different purposes cannot consume one another's state.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any

import numpy as np


def _stable_entropy(*parts: Any) -> list[int]:
    payload = "\x1f".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return [int.from_bytes(digest[i : i + 4], "little") for i in range(0, 32, 4)]


def make_generator(root_seed: int, purpose: str, *keys: Any) -> np.random.Generator:
    """Return a generator keyed by root seed, purpose, and immutable identifiers."""
    entropy = [int(root_seed) & 0xFFFFFFFF, *_stable_entropy(purpose, *keys)]
    return np.random.default_rng(np.random.SeedSequence(entropy))


@dataclass(frozen=True)
class PermutationStream:
    root_seed: int
    baseline_replicate: str
    stream_index: int = 0

    def generator(self) -> np.random.Generator:
        return make_generator(
            self.root_seed,
            "within-segment-permutation",
            self.baseline_replicate,
            self.stream_index,
        )


@dataclass(frozen=True)
class ContinuationStream:
    """Common-random-number streams shared across maps within one baseline block.

    Map identity is deliberately absent from the key.  Actual, identity, and
    coarse-grained continuations with the same baseline and continuation index
    therefore receive matched observation and propagation streams.
    """

    root_seed: int
    baseline_replicate: str
    continuation_index: int

    def observation_generator(self) -> np.random.Generator:
        return make_generator(
            self.root_seed,
            "continuation-observation",
            self.baseline_replicate,
            self.continuation_index,
        )

    def propagation_generator(self) -> np.random.Generator:
        return make_generator(
            self.root_seed,
            "continuation-propagation",
            self.baseline_replicate,
            self.continuation_index,
        )


@dataclass(frozen=True)
class AnalysisStream:
    root_seed: int
    purpose: str
    analysis_id: str = "default"
    stream_index: int = 0

    def generator(self) -> np.random.Generator:
        return make_generator(
            self.root_seed,
            self.purpose,
            self.analysis_id,
            self.stream_index,
        )
