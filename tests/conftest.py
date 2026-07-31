import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def synthetic_continuations():
    rows = []
    continuation_noise = np.array([-0.12, 0.04, 0.09, -0.01])
    for condition in ["selective", "control"]:
        for rep in range(5):
            baseline = f"{condition}_r{rep}"
            actual_base = 10.0 + 0.1 * rep
            if condition == "selective":
                constant_base = 6.0 + 0.1 * rep
                map_values = {
                    "constant": (0.0, constant_base),
                    "mid025": (0.25, 7.4 + 0.1 * rep),
                    "mid050": (0.50, 9.75 + 0.1 * rep),
                    "mid075": (0.75, 9.85 + 0.1 * rep),
                    "identity": (1.0, actual_base),
                }
            else:
                constant_base = 9.0 + 0.1 * rep
                map_values = {
                    "constant": (0.0, constant_base),
                    "mid025": (0.25, 9.15 + 0.1 * rep),
                    "mid050": (0.50, 9.35 + 0.1 * rep),
                    "mid075": (0.75, 9.60 + 0.1 * rep),
                    "identity": (1.0, actual_base),
                }
            for ci, noise in enumerate(continuation_noise):
                rows.append(
                    {
                        "condition": condition,
                        "baseline_replicate": baseline,
                        "map_hash": "actual",
                        "method": "unintervened",
                        "endpoint_type": "actual",
                        "retained_information": 1.0,
                        "baseline_information": 1.0,
                        "continuation_index": ci,
                        "viability": actual_base + noise,
                    }
                )
                for map_hash, (info, base) in map_values.items():
                    endpoint = map_hash if map_hash in {"constant", "identity"} else "intermediate"
                    # Common random noise is shared across maps. Actual and identity are exact.
                    rows.append(
                        {
                            "condition": condition,
                            "baseline_replicate": baseline,
                            "map_hash": map_hash,
                            "method": "endpoint" if endpoint != "intermediate" else "synthetic_family",
                            "endpoint_type": endpoint,
                            "retained_information": info,
                            "baseline_information": 1.0,
                            "continuation_index": ci,
                            "viability": base + noise,
                        }
                    )
    return pd.DataFrame(rows)
