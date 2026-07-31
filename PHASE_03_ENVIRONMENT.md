# Phase 3 validation environment

**Capture date:** 2026-07-31  
**Purpose:** Statistical-pipeline validation only; this is not yet the frozen production environment.

| Item | Value |
|---|---|
| Operating system | Linux 6.12.13, x86_64, glibc 2.41 |
| Python | 3.13.5 |
| NumPy | 2.3.5 |
| SciPy | 1.17.0 |
| pandas | 2.2.3 |
| Numba | 0.65.1 |
| Matplotlib | 3.10.8 |
| pytest | 9.0.2 |

Installation used:

```bash
python -m pip install -e . --no-build-isolation
```

The revised production release still requires a frozen clean-room environment and artifact hashes before Phase 4 production runs are accepted.
