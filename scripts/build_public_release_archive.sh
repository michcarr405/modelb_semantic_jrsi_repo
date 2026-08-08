#!/usr/bin/env bash
set -euo pipefail

ref="${1:-HEAD}"
root_name="modelb_semantic_jrsi_reproducibility_release_v1.0.0"
out="${2:-${root_name}.zip}"

# Build only from Git-tracked content at the requested ref. This excludes
# .git metadata, pytest caches, .DS_Store files, notebooks checkpoints, and
# any other untracked/ignored local artifacts.
git rev-parse --verify "${ref}^{commit}" >/dev/null
git archive --format=zip --prefix="${root_name}/" -o "$out" "$ref"

python - "$out" <<'PY'
import sys, zipfile
p=sys.argv[1]
forbidden=("/.git/","/.pytest_cache/","/.DS_Store","/__MACOSX/","/.ipynb_checkpoints/")
with zipfile.ZipFile(p) as z:
    names=z.namelist()
    bad=[n for n in names if any(tok in n for tok in forbidden)]
    if bad:
        raise SystemExit("Forbidden transient files found in archive:\n"+"\n".join(bad[:30]))
print(f"archive_ok: {p} ({len(names)} entries)")
PY

sha256sum "$out"
