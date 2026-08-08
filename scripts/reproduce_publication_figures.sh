#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
rm -rf reproduction/generated_main_figures reproduction/generated_supplementary_figures
mkdir -p reproduction/generated_main_figures reproduction/generated_supplementary_figures
python publication_figures/main/produce_publication_figures.py \
  --table-dir publication_figures/source_tables \
  --out-dir reproduction/generated_main_figures
python publication_figures/supplementary/produce_supplementary_figures.py \
  --table-dir publication_figures/source_tables \
  --out-dir reproduction/generated_supplementary_figures
python scripts/verify_publication_figure_release.py --generated
