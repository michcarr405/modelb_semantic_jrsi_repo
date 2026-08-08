#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "RELEASE_CANDIDATE_MANIFEST_SHA256.csv"
EXCLUDE_NAMES = {"RELEASE_CANDIDATE_MANIFEST_SHA256.csv"}
EXCLUDE_PARTS = {".git", ".pytest_cache", ".ipynb_checkpoints", "__MACOSX"}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
rows=[]
for rel in sorted(x for x in tracked if x):
    p=Path(rel)
    if p.name in EXCLUDE_NAMES or any(part in EXCLUDE_PARTS for part in p.parts) or p.name==".DS_Store":
        continue
    fp=ROOT/p
    if fp.is_file():
        rows.append((rel, fp.stat().st_size, sha256(fp)))
with OUT.open("w", newline="", encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow(["path","size_bytes","sha256"])
    w.writerows(rows)
print(f"wrote {len(rows)} entries to {OUT.name}")
