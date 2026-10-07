# JRSI Round-2 MP reproducibility recovery package — 2026-10-07

## Purpose
This package collects the exact Round-2 MP-migration drivers currently recoverable from the scientific freeze, a deterministic MP seed/stream ledger for those drivers, and regenerated evolved states for the independent-affinity-landscape campaign.

## Bottom line
**This package is not yet sufficient to make the blanket claim that every MP-primary source table can be regenerated end-to-end from the archived production state.** It materially closes the affinity-landscape state gap, but two exact-production gaps remain:

1. `modelb_semantic_repo/mp_operator.py`, imported by `run_core_and_screen.py`, `run_stage_c.py`, and `run_stage_d_mp_split.py`, is not present in the compact Round-2 scientific freeze, the transferred Round-1 source, or the currently mounted public-repository state.
2. The exact production driver and continuation-root specification for the separately frozen 64-new-continuation MP causal-specificity campaign are not present in the currently mounted archives. The campaign metadata are known (20 seed blocks, 64 new streams/evaluation, indices 2–65, 36 generations, 15,360 continuation-level evaluations; prespec commit `a00e82002fd60774927e32ad8658692c243edfa8`; result commit `2af49c5c8a9ae491928439dc056bfb1f65368102`), and downstream recovered Figure-5 source/QC files are included, but that is not equivalent to the original production driver + seed root + raw table.

Do not describe the Round-2 public release as fully end-to-end regenerable until those gaps are closed and a clean regeneration comparison is run.

## Recovered exact production drivers
- `production_drivers/run_core_and_screen.py`
- `production_drivers/run_stage_c.py`
- `production_drivers/run_stage_d_mp_split.py`
- `production_drivers/run_core_p1_frontier.py`
- `production_drivers/run_affinity_landscape_generality.py`

These are byte-for-byte copies from the 2026-10-02 integrated MP scientific freeze.

## Seed ledger
- `seed_ledger/MP_SEED_ROOT_REGISTRY.csv` — the frozen root-seed registry currently recoverable.
- `seed_ledger/MP_SEED_LEDGER.csv` — expanded deterministic stream specifications for core MP, Stage A/B, Stage C, Stage D, p=1 frontier, and affinity-landscape analyses. It records the SHA-256-derived SeedSequence entropy vector for every recovered keyed stream specification, plus exact baseline integer seeds where the driver first derives a 32-bit seed.
- The unresolved 64-new causal-specificity production stream is explicitly marked `BLOCKED_MISSING_EXACT_DRIVER_AND_ROOT`; no seed was invented.

## Independent-landscape evolved states
`independent_landscape_evolved_states/` contains:
- all 256 regenerated evolved population states (8 landscapes × 4 settings × 8 populations), compressed as NPZ;
- the eight regenerated base affinity matrices;
- `EVOLVED_STATE_MANIFEST.csv` and `AFFINITY_LANDSCAPE_MANIFEST.csv`;
- `VALIDATION.json`.

Validation succeeded for **256/256** states: reconstructed baseline seeds and canonical population state hashes match the frozen `population_level.csv` records. This closes the evolved-state archival gap for the independent-landscape campaign.

## Dependencies and frozen tables
- `dependencies/05_ROUND1_GATE8_FROZEN_SCIENTIFIC_EVIDENCE.zip` preserves the exact historical engine and R1 core states/maps used as inputs by R2 analyses.
- `provenance/JRSI_R2_MP_MIGRATION_SCIENTIFIC_FREEZE_2026-10-02.zip` preserves the compact R2 science freeze.
- `frozen_source_tables/scientific_freeze_results/` exposes the tables copied from that freeze.

## Causal-specificity recovery
`causal_specificity_recovered/` contains the currently retained Figure-5 recovered seed-block table, numerical QC, visual recovery audit, and plotting scripts. These are downstream evidence/source artifacts. They do **not** substitute for the missing high-continuation production driver/root/raw 15,360-row table.

## Required closure before a full regeneration claim
1. Recover the exact `mp_operator.py` from the Round-2 production worktree/commit or an independently checksummed archive.
2. Recover the exact `JRSI_R2_HIGH_CONTINUATION_MP_CAUSAL_SPECIFICITY_2026-10-02.zip` (or equivalent exact production driver + seed root + raw source table).
3. Restore scripts to their production path `round2/mp_migration/` so `ROOT = Path(__file__).resolve().parents[2]` resolves correctly.
4. From a clean environment, regenerate all raw and summary tables into an empty results tree.
5. Compare regenerated raw tables/hashes/numerical summaries to the frozen source tables and record the comparison.
6. Only then label the public Round-2 release as supporting full end-to-end regeneration of every MP-primary source table.
