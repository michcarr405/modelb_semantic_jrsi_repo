# Portable final-figure build

Use a separate plotting environment. The scientific simulation environment intentionally has different dependency pins.

```bash
python3.12 -m venv .venv-figures
. .venv-figures/bin/activate
python -m pip install -r round2_mp/figure_build/requirements-figures.txt
python round2_mp/figure_build/build_figures.py --output ../round2-figure-replay
python round2_mp/figure_build/verify_figures.py --generated ../round2-figure-replay
```

No network or machine-specific path is needed after dependency installation. Arimo font files and their redistribution license are bundled. Plotting uses Matplotlib 3.10.8, matching the archived rendering environment.

Figures 3–8 and S1–S6 are regenerated from recovered plotting code and numerical inputs. Figures 1 and 2 are conceptual diagrams copied from their exact archived masters; no numerical regeneration is claimed for those diagrams. The verifier compares rendered RGB pixels at 144 dpi, rather than requiring identical PDF metadata or serialization.

## Recovery details

The adapter routes historical file references to current source tables. The historical p=1 frontier display uses retained reconstruction/derived plotting inputs under historical_plot_inputs/. These are immutable plotting dependencies; the full scientific regeneration record remains separately documented in ROUND2_RELEASE_SCOPE.md.

Original main plotting scripts are retained under historical_source/. Supplement plot sections were extracted from frozen prefreeze scripts, excluding unrelated manuscript/table authoring. The final Figure 4 ylabel overlays and Figure 8 short tick labels, 4.1 top axis limit and 12-degree tick-label rotation were reconstructed from the final PDF masters. Those adaptations are explicit in build_figures.py and are validated by rendered-pixel equivalence. The plotting adapter is a documented reconstruction of the final build, not a recovered byte-identical final build script.

The six Figure 5 forest summaries are rounded constants retained in the archived source; all dot/paired-line values are read from the controlling 64-new-stream seed-block table. The scientific inference table remains the numerical authority.

Historical sources with /mnt/data strings are archival inputs only. The portable entry point rewrites their routing in memory and does not execute them as standalone commands. It creates no manuscript or Supplement documents.
