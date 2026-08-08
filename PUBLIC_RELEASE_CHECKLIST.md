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
- [ ] Authoritative editable masters for Figures 1 and 2 archived or permanently referenced.
- [ ] Final standalone journal-upload exports for Figures 1 and 2 archived and checked.
- [ ] Clean-room rerun completed and `reproduction/CLEAN_ROOM_RERUN_RECORD.md` closed.
- [ ] Public repository made browsable (not a single nested ZIP only).
- [ ] Final public Git tag/release created.
- [ ] Permanent archive DOI minted.
- [ ] DOI added to `CITATION.cff`, README, release notes, and manuscript Data Accessibility text.
- [ ] Final release manifest generated after all above changes.
