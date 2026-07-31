# Phase 3 validation commands

Run from the repository root.

## Install

```bash
python -m pip install -e . --no-build-isolation
```

## Full test suite

```bash
python -m pytest -q
```

Expected result:

```text
53 passed
```

## Statistical-pipeline validation

```bash
python scripts/validate_statistical_pipeline.py
```

The script uses synthetic continuation data and one tiny identity-endpoint model diagnostic. It does not run the baseline fidelity sweep or production intervention suite. Outputs are written to `validation/phase3/`.

## Hidden global RNG scan

```bash
grep -R "np\.random\.random\|np\.random\.rand\|np\.random\.choice\|np\.random\.shuffle" -n src
```

Expected result: no matches.

## Git record

```bash
git status --short
git rev-parse HEAD
git log --oneline -3
```
