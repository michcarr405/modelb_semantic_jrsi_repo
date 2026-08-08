# Draft release notes — JRSI reproducibility release v1.0.0

This release archives the code, frozen analysis outputs, validation records, seed ledgers, evolved states, processed figure-source tables, and publication-figure generation materials supporting manuscript `rsif-2026-0516`, *Counterfactual interventions reveal causal relevance of inherited sequence distinctions in a compositional-resampling model*.

## Scientific freeze

The scientific results were frozen at commit:

`2c7d78694579755402c0a1896e109b29dec4d6a0`

The Gate 8 closure tag is `phase7-gate8-passed-v1` at commit `36246a86320037506beed83d0f7366c33d2c59c5`.

The RC3 public-release packaging layer changes documentation, citation/release metadata, environment locking, publication-figure reproducibility assets, and release-archive hygiene only. It does not alter frozen scientific results.

## License

This release is distributed under the MIT License. See `LICENSE`.

## Publication-figure reproducibility

The release includes the exact scripts and frozen source tables used to produce manuscript Figures 3–8 and Supplementary Figures S1–S7. Quantitative figures can be regenerated without rerunning scientific production simulations.

Figures 1 and 2 are vector schematics; their authoritative editable masters and final standalone exports are archived/referenced separately in the final release.

## Validation

- full repository test suite: 68 passed;
- result-freeze release validation: passed;
- frozen publication source-table hashes: passed;
- regenerated quantitative publication PNG/TIFF files: exact hash match to archived publication exports.

## Before publishing this draft as final

Replace the remaining release-candidate placeholders:

- final public tag/packaging commit;
- permanent archive DOI;
- Figure 1/2 editable-master references and standalone exports;
- final clean-room rerun record.
