# JRSI Major Revision #2 reproducibility release candidate

Candidate identifier: `jrsi-reproducibility-v2.0.0-rc1`
Date assembled: 2026-10-07
Status: **RC1 assembled; HOLD before RC2/RC3 promotion until the declared MP-production-code provenance gap is resolved or explicitly bounded.**

## Scientific state

The Round-2 manuscript and Supplement are scientifically frozen and notation-closed. The current evidence surface uses the population-frequency-weighted probability-space marginal-preserving (MP) intervention. The reader-facing Supplement ends at Figure S6.

The repository root is the frozen Gate-8 Model B code/evidence foundation. The current Round-2 evidence is isolated under `round2_mp/` so historical analyses remain preserved rather than overwritten.

## Round-2 evidence layer

- `round2_mp/source_tables/` — frozen MP-primary source tables and compact reader records.
- `round2_mp/analysis_scripts/` — recovered MP migration/diagnostic/figure scripts and empirical marginal-validation code.
- `round2_mp/publication/final_main/` — notation-closed final main manuscript PDF, editable source ZIP/source tree, and Figures 1-8.
- `round2_mp/publication/final_supplement/` — notation-closed final Supplement PDF, editable source ZIP/source tree, and Figures S1-S6.
- `round2_mp/publication/qc/` — final numerical, integrated, and Reviewer-2 notation/value audits plus the source-table map.
- `round2_mp/provenance/` — original MP migration SHA256 record, hash verification, landscape provenance, and synchronization records.

## Historical material

Gate-8/round-1 scientific material at repository root is retained as historical/foundation provenance. It is not the current Round-2 evidence surface. Transitional Supplementary Figures S7-S9 are deliberately excluded from `round2_mp/publication/`; the final Supplement ends at S6.

## Current release gate

The frozen MP source tables and recovered migration scripts hash-match the original MP migration SHA256 record. However, the materials presently assembled do not contain a single archived production driver that regenerates every MP-primary source table from the Gate-8 evolved states. This gap blocks a claim of full end-to-end Round-2 production regeneration until it is resolved or the release scope is explicitly documented as archived-output verification plus deterministic diagnostic regeneration.

Do not create an immutable tag or publish the Zenodo record from this RC1 state.
