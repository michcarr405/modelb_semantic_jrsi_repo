# Exact reproduction commands

Run from the repository root.

## A. Validate the frozen result archive

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/validate_result_freeze.py
python scripts/verify_publication_figure_release.py
```

## B. Regenerate manuscript Figures 3–8 from frozen source tables

```bash
python publication_figures/main/produce_publication_figures.py \
  --table-dir publication_figures/source_tables \
  --out-dir reproduction/generated_main_figures
```

## C. Regenerate Supplementary Figures S1–S7 from frozen source tables

```bash
python publication_figures/supplementary/produce_supplementary_figures.py \
  --table-dir publication_figures/source_tables \
  --out-dir reproduction/generated_supplementary_figures
```

## D. Regenerate all quantitative publication figures

```bash
bash scripts/reproduce_publication_figures.sh
```

The publication-figure commands consume frozen source tables and do not rerun scientific production simulations.

## E. Validated Phase 4 corrected core production

```bash
PYTHONPATH=src python scripts/run_phase4_pilots.py --outdir validation/phase4_pilots --workers 5
PYTHONPATH=src python scripts/run_phase4_production.py --outdir results/phase4_core --continuations 2 --horizon 36 --workers 5
PYTHONPATH=src python scripts/validate_phase4.py
PYTHONPATH=src python -m pytest -q
```

## F. Validated Phase 5 causal-specificity production

```bash
PYTHONPATH=src python scripts/run_phase5_production.py --workers 1
PYTHONPATH=src python scripts/validate_phase5.py
```

## G. Validated Phase 6 staged generality/robustness production

```bash
PYTHONPATH=src python scripts/run_phase6_batch.py A --batch 8 --outdir results/phase6_generality
PYTHONPATH=src python scripts/run_phase6_batch.py B1 --batch 8 --outdir results/phase6_generality
PYTHONPATH=src python scripts/run_phase6_batch.py B2 --batch 8 --outdir results/phase6_generality
PYTHONPATH=src python scripts/run_phase6_batch.py select-c --outdir results/phase6_generality
PYTHONPATH=src python scripts/run_phase6_batch.py C --batch 8 --outdir results/phase6_generality
PYTHONPATH=src python scripts/run_phase6_batch.py select-d --outdir results/phase6_generality
PYTHONPATH=src python scripts/run_phase6_batch.py D --batch 2 --outdir results/phase6_generality
PYTHONPATH=src python scripts/run_phase6_batch.py finalize --outdir results/phase6_generality
PYTHONPATH=src python scripts/validate_phase6.py
```

## H. Result freeze

```bash
PYTHONPATH=src python scripts/build_result_freeze.py
PYTHONPATH=src python scripts/validate_result_freeze.py
PYTHONPATH=src pytest -q tests/test_result_freeze.py
```

No production simulation should be rerun merely to regenerate manuscript figures.

## Figures 1 and 2 derivative export commands

Figures 1 and 2 are author-edited vector schematics, not quantitative plots generated from simulation data. Their archived SVG masters are converted to submission/proof formats without changing scientific content.

```bash
mkdir -p artwork/exports
for n in 1 2; do
  inkscape artwork/masters/Figure_${n}.svg \
    --export-type=pdf \
    --export-filename=artwork/exports/Figure_${n}.pdf

  inkscape artwork/masters/Figure_${n}.svg \
    --export-type=eps \
    --export-filename=artwork/exports/Figure_${n}.eps

  inkscape artwork/masters/Figure_${n}.svg \
    --export-type=png \
    --export-dpi=600 \
    --export-filename=artwork/exports/Figure_${n}_600dpi_tmp.png

  magick artwork/exports/Figure_${n}_600dpi_tmp.png \
    -alpha off -colorspace Gray -units PixelsPerInch -density 600 \
    -define png:color-type=0 \
    artwork/exports/Figure_${n}_600dpi_grayscale.png

  magick artwork/exports/Figure_${n}_600dpi_tmp.png \
    -alpha off -colorspace Gray -units PixelsPerInch -density 600 \
    -compress LZW \
    artwork/exports/Figure_${n}_600dpi_grayscale.tiff

  rm artwork/exports/Figure_${n}_600dpi_tmp.png
done
```

The final vector/raster files must be visually proofed against the archived SVG masters and the controlling manuscript; conversion alone is not the acceptance test. See `artwork/ARTWORK_VALIDATION.md`.
