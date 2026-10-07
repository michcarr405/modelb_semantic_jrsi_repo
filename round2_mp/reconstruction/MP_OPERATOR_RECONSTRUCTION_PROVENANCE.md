# Round-2 `mp_operator.py` functional reconstruction and validation

**Date:** 2026-10-07  
**Manuscript:** `rsif-2026-0516.R1`  
**Status:** **FUNCTIONAL RECONSTRUCTION VALIDATED IN LAYERS**

## Provenance statement

The file `src/modelb_semantic_repo/mp_operator.py` in this package is **not claimed to be a byte-identical recovery of the lost Round-2 production source**. It was reconstructed from frozen production evidence:

1. `JRSI_R2_MP_DRIVERS_AND_SEED_LEDGER_2026-10-07.zip` — exact integrated production call sites and deterministic seed specifications;
2. `JRSI_R2_MP_MIGRATION_SCIENTIFIC_FREEZE_2026-10-02.zip` — frozen production drivers, self-contained p=1 frontier implementation, frozen summaries and prespecification/freeze records;
3. `JRSI_R2_MP_CAUSAL_SPECIFICITY_2026-10-02.zip` — independently frozen standalone marginal-preserving constant implementation and retained continuation-level results;
4. immutable Round-1 Gate-8 source/state archive — historical simulation, reproduction and RNG implementations on which the Round-2 drivers depend.

The reconstruction deliberately preserves the recovered public API and stochastic stream ordering. The reconstructed file SHA256 is:

`cd01290a16234700898e7c5040abc33a72fc620aac8221100250d151d2ee7ccc`

## Recovered API

All six names imported by the recovered production drivers are supplied without changing the call sites:

- `simulate_core_actual`
- `simulate_core_grouped`
- `simulate_phase6_grouped`
- `simulate_core_constant`
- `simulate_phase6_constant`
- `expected_marginal_error_general`

This closes the API-level blocker in the recovered integrated drivers.

## Reconstruction basis

The core grouped observer is anchored directly to the frozen self-contained `run_core_p1_frontier.py` implementation. That file specifies the population-frequency-weighted probability-space group kernel, use of matched observation/propagation streams, and the exact local-state sampling/fitness path.

The Phase-6 constant implementation is anchored independently to `run_affinity_landscape_generality.py`, including the critical observation-stream draw order: jitter offsets are drawn first, followed by local-state uniforms, after which the unchanged Phase-6 reproduction function consumes the matched propagation stream.

The causal-specificity package supplies a third independent implementation of the constant MP construction and a retained continuation-level numerical reference.

## Validation results

### 1. API equivalence — PASS

Every recovered production-driver import resolves with the expected positional signature. No production call site was modified.

### 2. Marginal-preservation equivalence — PASS

Representative independently computed maximum expected one-site marginal errors were:

- B2 default, replicate 0: `1.2545520178264269e-14`
- B2 jitter, replicate 0: `1.2878587085651816e-14`
- B2 stride-7, replicate 0: `6.494804694057166e-15`
- Stage D D0 replicate 0: `4.163336342344337e-15`

These are at floating-point roundoff and comfortably inside the frozen campaign maxima (`<=3.3e-13` screen, `1.40e-13` Stage C, `1.29e-13` Stage D).

### 3. Continuation equivalence — PASS where an exact retained/self-contained reference exists

For p=1, replicate 0, continuation 3, four representative map families were evaluated both by the frozen self-contained frontier implementation and by the reconstructed module:

- constant, 1 group: difference `0.0`
- balanced-random, 16 groups: difference `0.0`
- affinity-rank, 64 groups: difference `0.0`
- contiguous-substring, 16 groups: difference `0.0`

For the integrated core driver, p=1 replicate 0 averaged over all eight Round-2 MP continuation streams reproduced the frozen values exactly at CSV precision:

- actual viability: `39.28175998263889`
- MP constant viability: `37.68868272569445`
- `DeltaV_MP`: `1.5930772569444436`

The retained causal-specificity package was also rerun for native/full seed block 0. Both archived continuations reproduced with maximum differences of exactly `0.0` for actual viability, MP viability, `DeltaV_MP`, and the starting marginal diagnostic.

### 4. State equivalence — PASS against an independent self-contained Phase-6 production reference

The frozen independent-affinity driver was used as an independent state-level reference. For landscape L0, B2-default, replicate 0, continuation 0:

- frozen baseline seed: `2642101240`
- regenerated baseline state hash matched the frozen `population_level.csv` state hash;
- self-contained MP viability: `36.59750434027778`
- reconstructed-module MP viability: `36.59750434027778`
- self-contained final-population hash: `4ea046ebde5f4f020b136ddb1f95200c4d0446758c49178248eb12e1a4e66926`
- reconstructed final-population hash: `4ea046ebde5f4f020b136ddb1f95200c4d0446758c49178248eb12e1a4e66926`

This is an exact full stochastic-path match, not merely a summary-statistic match.

**Stage-D limitation:** the three supplied recovery archives do not contain the original Stage-D continuation-level `final_population_hash` table. Consequently, direct comparison of a reconstructed Stage-D final-population hash to an archived Stage-D final hash cannot be performed from these materials alone. The reconstructed Stage-D run does emit final-population hashes, and the independent Phase-6 state-equivalence test above establishes exact stochastic-path equivalence for the same reconstructed Phase-6 constant operator.

### 5. Campaign equivalence — strong partial regeneration PASS

The following campaign-level checks were executed from the recovered drivers rather than by transforming frozen summary tables:

- **Core MP sweep:** 60 complete selective seed blocks covering p = 0.1, 0.2 and 0.3 (20 populations each, eight continuations each). Relative to the frozen replicate table, maximum absolute differences were `7.11e-15` for actual viability, `7.11e-15` for MP viability and `9.71e-17` for `DeltaV_MP`.
- **Stage A/B screening:** the complete n=8 `B2_default` setting was regenerated. The generated `DeltaV_MP` mean was `2.5889387342664922` versus frozen `2.588938734266492`; corrected-information intervals, adaptive-gain intervals, regime, provisional class, depth and boundary distance matched exactly or to floating roundoff.
- **Stage C:** the complete n=8 `C_g150_B2_default` setting was regenerated. Generated `DeltaV_MP = 2.485701158311632 [1.8135600195990675, 3.3215505133734817]`, matching the frozen table; all checked information/adaptive-gain summary fields and the strong-adaptation classification matched.
- **Stage D:** a complete D0 replicate (`D0_r00`) was regenerated across the full 34-map panel and all 16 continuation streams. Generated `actual_mean = 37.65237223307292`, `constant_mean = 37.21698133680556`, `DeltaV_MP = 0.43539089626735716`, and within-population Spearman `0.40840336134453775`; the frozen replicate row is identical to floating roundoff. Identity recovery was exact.
- **p=1 frontier:** representative maps from every major grouping family checked above were exact at the continuation level against the frozen self-contained driver. The full 20 x 64 x 34 campaign was not rerun in this recovery pass because it is computationally large and its production driver is already self-contained.
- **Affinity-landscape campaign:** state and continuation equivalence were checked against its independent self-contained implementation as described above. The recovered audit separately records successful regeneration of all 256 frozen baseline-state hashes.

These tests cover the core operator, constant and grouped endpoints, core and generalized Phase-6 paths, jitter/stride parameterization, full-map Stage-D behavior, and exact stochastic propagation.

## Release interpretation

The evidence supports treating this file as the **canonical reconstructed Round-2 reproducibility implementation**, provided the release states explicitly that:

> The original Round-2 `mp_operator.py` source file was not recovered byte-for-byte. The implementation distributed here was reconstructed from frozen production drivers, independently frozen operator implementations, immutable historical model source, deterministic seed ledgers and frozen numerical outputs. It was validated by exact continuation-level reproduction, campaign-level source-table reproduction, machine-precision marginal-preservation checks, and an exact final-population SHA256 match against an independent self-contained Phase-6 production implementation.

The release should **not** state or imply that this is the original file or that its SHA256 is the historical production-file SHA256.

## Remaining provenance issue unrelated to this module

The driver/seed-ledger audit separately identifies the final high-continuation causal-specificity campaign as lacking its exact 64-new-stream production archive/root/raw table. Reconstruction of `mp_operator.py` does not by itself close that separate provenance item. The older two-continuation causal-specificity package is useful as an independent operator-validation reference but is not a substitute for the final 64-new-stream campaign archive.
