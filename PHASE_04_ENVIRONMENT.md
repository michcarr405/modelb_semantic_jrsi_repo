# Phase 4 environment

- Date: 2026-07-31
- Python: 3.13.5
- Platform: Linux-6.12.13-x86_64-with-glibc2.41
- NumPy: 2.3.5
- pandas: 2.2.3
- SciPy: 1.17.0
- Numba: 0.65.1
- Matplotlib: 3.10.8
- Production workers: 5
- Production root seed: 2026073104

The authoritative dependency declarations remain `requirements.txt` and `pyproject.toml`. Commands use `PYTHONPATH=src` so the package is imported from the versioned repository source.
