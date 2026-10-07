#!/usr/bin/env python3
"""Reproduce the eight Round-2 affinity base matrices and their canonical SHA-256 hashes.

Hash convention copied from the frozen Model-B `array_sha256` helper:
    sha256( ascii(str(dtype)) || int64_le(shape).tobytes() || contiguous_array.tobytes() )

Landscape generation convention:
    make_generator(2026100211, "affinity-landscape", L).normal(size=(1024, 4))
for L = 0,...,7.
"""
from __future__ import annotations

import csv
import hashlib
import platform
from pathlib import Path
import sys
import numpy as np

LAND_ROOT = 2026100211
PURPOSE = "affinity-landscape"
SHAPE = (4**5, 4)
OUT = Path(__file__).with_name("affinity_matrix_hash_verification.csv")

EXPECTED = {
    0: "54efeb72bbc9a140a64f4e830ab319d80d9bc9f1a961911a1e147b7c06272de0",
    1: "97fd423a74519f6c3c63bd14d46504b3ec1f1e0a8a00a53cf9970e5197d560d9",
    2: "f3cdb827f895e8194d24138c7744cf93fd958afe86074acd9f5ac507249416de",
    3: "2e7c9cafe8e2c498a4837d3e6d8ada33dddff5ab5d6a999bf1d89a2d955f2ab8",
    4: "458ae4ad8ce3d47aa8c6994b925a5bd57de5df9a7ce2ac5f0bd5b07dd8292b19",
    5: "4dc44dce0ebf2c2a4c78c78c6584e16ff21a097dec63edefcd1af539891e3477",
    6: "c03ae676535ef0e3ad378f5cfd72255e145d5ccf906370743fb9f0420335519a",
    7: "f38a7033128010c55673bccf9e3f112ac8154bb3f5fafee652b7bec659a25243",
}


def _stable_entropy(*parts: object) -> list[int]:
    payload = "\x1f".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return [int.from_bytes(digest[i : i + 4], "little") for i in range(0, 32, 4)]


def make_generator(root_seed: int, purpose: str, *keys: object) -> np.random.Generator:
    entropy = [int(root_seed) & 0xFFFFFFFF, *_stable_entropy(purpose, *keys)]
    return np.random.default_rng(np.random.SeedSequence(entropy))


def canonical_array_sha256(array: np.ndarray) -> str:
    arr = np.ascontiguousarray(array)
    h = hashlib.sha256()
    h.update(str(arr.dtype).encode("ascii"))
    h.update(np.asarray(arr.shape, dtype="<i8").tobytes())
    h.update(arr.tobytes())
    return h.hexdigest()


def raw_bytes_sha256(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def main() -> int:
    rows = []
    ok = True
    for landscape in range(8):
        arr = make_generator(LAND_ROOT, PURPOSE, landscape).normal(size=SHAPE)
        canonical = canonical_array_sha256(arr)
        raw = raw_bytes_sha256(arr)
        expected = EXPECTED[landscape]
        match = canonical == expected
        ok &= match
        rows.append({
            "landscape": landscape,
            "root_seed": LAND_ROOT,
            "purpose": PURPOSE,
            "dtype": str(arr.dtype),
            "shape": "1024x4",
            "canonical_array_sha256": canonical,
            "raw_tobytes_sha256": raw,
            "expected_canonical_sha256": expected,
            "canonical_matches_expected": match,
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
        })

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    print(f"Python {platform.python_version()} | NumPy {np.__version__}")
    print("Canonical convention: sha256(dtype_ascii || shape_int64_le || contiguous_data_bytes)")
    for row in rows:
        print(
            f"L{row['landscape']}: canonical={row['canonical_array_sha256']} "
            f"raw={row['raw_tobytes_sha256']} match={row['canonical_matches_expected']}"
        )
    print(f"Wrote {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
