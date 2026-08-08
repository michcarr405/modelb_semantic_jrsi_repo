from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "publication_figures"
FROZEN = ROOT / "results" / "result_freeze" / "figure_sources"
SRC = PUB / "source_tables"
MAIN_ARCHIVE = PUB / "exports" / "main"
SUPP_ARCHIVE = PUB / "exports" / "supplementary"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_sources() -> list[str]:
    errors: list[str] = []
    frozen_names = sorted(p.name for p in FROZEN.glob("*.csv"))
    src_names = sorted(p.name for p in SRC.glob("*.csv"))
    if frozen_names != src_names:
        errors.append(f"source-table filename mismatch: frozen={frozen_names}, publication={src_names}")
        return errors
    for name in frozen_names:
        a, b = FROZEN / name, SRC / name
        if sha256(a) != sha256(b):
            errors.append(f"source-table hash mismatch: {name}")
    return errors


def check_archived_exports() -> list[str]:
    errors: list[str] = []
    for n in range(3, 9):
        stem = f"FIGURE_{n}_PUBLICATION_GRADE"
        for ext in ("pdf", "svg", "eps", "png", "tiff"):
            if not (MAIN_ARCHIVE / f"{stem}.{ext}").is_file():
                errors.append(f"missing archived main export: {stem}.{ext}")
    for n in range(1, 8):
        stem = f"FIGURE_S{n}_PUBLICATION_GRADE"
        for ext in ("pdf", "svg", "eps", "png", "tiff"):
            if not (SUPP_ARCHIVE / f"{stem}.{ext}").is_file():
                errors.append(f"missing archived supplementary export: {stem}.{ext}")
    return errors


def check_generated() -> tuple[list[str], list[tuple[str, str, str]]]:
    errors: list[str] = []
    comparisons: list[tuple[str, str, str]] = []
    generated_main = ROOT / "reproduction" / "generated_main_figures"
    generated_supp = ROOT / "reproduction" / "generated_supplementary_figures"
    # PNG and TIFF should be byte-stable in the locked environment; vector formats
    # can contain backend metadata that is not guaranteed byte-stable.
    for n in range(3, 9):
        stem = f"FIGURE_{n}_PUBLICATION_GRADE"
        for ext in ("png", "tiff"):
            expected, got = MAIN_ARCHIVE / f"{stem}.{ext}", generated_main / f"{stem}.{ext}"
            if not got.is_file():
                errors.append(f"missing generated main export: {got.relative_to(ROOT)}")
                continue
            eh, gh = sha256(expected), sha256(got)
            comparisons.append((f"main/{stem}.{ext}", eh, gh))
            if eh != gh:
                errors.append(f"generated hash mismatch: main/{stem}.{ext}")
    for n in range(1, 8):
        stem = f"FIGURE_S{n}_PUBLICATION_GRADE"
        for ext in ("png", "tiff"):
            expected, got = SUPP_ARCHIVE / f"{stem}.{ext}", generated_supp / f"{stem}.{ext}"
            if not got.is_file():
                errors.append(f"missing generated supplementary export: {got.relative_to(ROOT)}")
                continue
            eh, gh = sha256(expected), sha256(got)
            comparisons.append((f"supplementary/{stem}.{ext}", eh, gh))
            if eh != gh:
                errors.append(f"generated hash mismatch: supplementary/{stem}.{ext}")
    if comparisons:
        out = ROOT / "reproduction" / "PUBLICATION_FIGURE_REGEN_HASH_COMPARISON.csv"
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["file", "archived_sha256", "generated_sha256", "exact_match"])
            writer.writerows((name, a, b, a == b) for name, a, b in comparisons)
    return errors, comparisons


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify frozen source tables and publication figure release assets.")
    parser.add_argument("--generated", action="store_true", help="Also verify regenerated PNG/TIFF exports.")
    args = parser.parse_args()

    errors = check_sources() + check_archived_exports()
    if args.generated:
        generated_errors, _ = check_generated()
        errors.extend(generated_errors)

    if errors:
        print("PUBLICATION FIGURE RELEASE VERIFICATION: FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print("PUBLICATION FIGURE RELEASE VERIFICATION: PASS")
    print("- publication source tables match the Gate 8 frozen figure sources exactly")
    print("- required archived quantitative figure exports are present")
    if args.generated:
        print("- regenerated PNG/TIFF exports match archived publication exports exactly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
