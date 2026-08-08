# Public reproducibility release checklist

## Completed in this release candidate

- [x] Frozen scientific commit explicitly recorded.
- [x] Gate 8 closure/tag explicitly recorded.
- [x] Full frozen Phase 4–6 outputs retained.
- [x] Evolved states retained.
- [x] Seed ledgers retained.
- [x] Result-freeze integrity manifests retained.
- [x] Frozen figure-source tables retained and copied into publication-figure workspace.
- [x] Exact current plotting script for manuscript Figures 3–8 archived.
- [x] Exact current plotting script for Supplementary Figures S1–S7 archived.
- [x] Current quantitative figure exports archived.
- [x] Exact figure-generation commands documented.
- [x] Machine-readable environment lock files added.
- [x] Public-facing README drafted.
- [x] Citation metadata drafted.
- [x] Release provenance documented.
- [x] Quantitative Figures 3–8 and S1–S7 regenerated from frozen source tables in the validated environment; PNG/TIFF hashes match archived publication outputs exactly.
- [x] Clean Git-tracked release-archive builder added; it excludes local caches and hidden transient files.

## Must be closed before final public release

- [x] Author selected MIT License and root `LICENSE` is present.
- [x] `CITATION.cff` and `.zenodo.json` license metadata updated to `MIT`.
- [x] Author-supplied final editable SVG masters for Figures 1 and 2 archived in `artwork/masters/`.
- [x] Final standalone PDF/EPS and 600 dpi grayscale PNG/TIFF exports for Figures 1 and 2 archived and visually checked against the controlling revised manuscript.
- [x] Release-candidate clean-room rerun completed on RC5 and `reproduction/CLEAN_ROOM_RERUN_RECORD.md` closed for pre-release validation.
- [x] Release-candidate repository tree published and browsable on GitHub (RC4/RC5 branches); final default/current branch activation remains pending.
- [ ] Final public Git tag/release created.
- [x] Permanent archive DOI reserved: `10.5281/zenodo.21852680`.
- [ ] Zenodo record published so the reserved DOI is registered/resolvable.
- [x] Reserved DOI added to `CITATION.cff`, README, release notes, and prepared Data Accessibility text.
- [ ] Final release manifest generated after all above changes.
