# Phase 3 statistical-pipeline validation

## Project

**Manuscript:** `rsif-2026-0516`  
**Phase:** 3 — statistical-pipeline validity  
**Date:** 2026-07-31  
**Scope:** synthetic continuation tables, analytical edge cases, and one tiny identity-endpoint model diagnostic only

## 1. Controlling requirements

Phase 3 validates the inferential hierarchy fixed in `REVISION_SPEC_v2.md` and `DECISIONS_LOG.md`:

- the independently evolved baseline population is the primary statistical unit;
- grouping maps are repeated measurements nested within baseline replicate;
- continuation seeds are technical Monte Carlo replicates nested within map and baseline replicate;
- one information–viability frontier is constructed per baseline replicate;
- target-not-reached cases are right-censored lower bounds rather than ordinary semantic estimates;
- uncertainty is obtained by resampling complete baseline-replicate blocks;
- permutation inference operates on replicate-level summaries only.

No production baseline sweep, production intervention suite, parameter sweep, causal control, final figure, or manuscript rewrite was performed.

## 2. Source-provenance note

The uploaded `modelb_semantic_jrsi_repo.zip` was the recovered submitted semantic repository and did not contain the locally created Phase 2 Git history or Phase 2 source additions named in `PHASE_02_HANDOFF.md`. The Phase 2 requirements were therefore reconstructed and revalidated in this working branch before Phase 3 code was added. The resulting branch reproduces the documented conditional-MI, permutation-correction, retained-information, endpoint, and explicit-RNG behaviors, but it is not a byte-for-byte checkout of Phase 2 commit `69a7df8efea3cd78a0712778a8831983b7dc62fe`.

## 3. Implemented statistical architecture

Primary implementation:

- `src/modelb_semantic_repo/statistical_pipeline.py`
- `src/modelb_semantic_repo/rng.py`
- `src/modelb_semantic_repo/interventions.py::simulate_horizon_with_stream`

### 3.1 Continuation-level schema and nesting

Every continuation row records:

- `condition`;
- `baseline_replicate`;
- `map_hash`;
- `method`;
- `endpoint_type`;
- `retained_information`;
- `continuation_index`;
- `viability`;
- optional `baseline_information`.

The validator rejects missing values, non-finite information or viability, inconsistent map coordinates, conflicting duplicate map rows, and multiple endpoint classifications for one map hash. Exact aliases of the same map are collapsed rather than counted as independent interventions.

Continuation seeds are averaged within map and baseline replicate. The resulting map-level table preserves the continuation count, standard deviation, standard error, and continuation-index ledger. It never pools across evolved replicates.

### 3.2 Paired continuation streams

`ContinuationStream` derives separate observation and propagation generators from:

- a root continuation seed;
- baseline-replicate identifier;
- continuation index;
- a fixed purpose label.

Map identity is intentionally absent from the stream key. Actual, identity, and coarse-grained continuations at the same baseline replicate and continuation index therefore use common random numbers. Observation and propagation streams cannot consume each other's state.

A tiny model diagnostic confirmed exact actual–identity recovery over four continuation generations: mean-fitness trajectories and final populations were bitwise identical.

### 3.3 Replicate-specific frontier

For each evolved baseline replicate:

1. continuation outcomes are averaged within each map;
2. the unintervened actual endpoint sets actual viability;
3. the constant endpoint supplies complete-scrambling viability;
4. the identity endpoint must reproduce baseline retained information and paired actual viability;
5. intervention points are sorted by measured retained information;
6. at duplicate information coordinates, the highest map viability is retained;
7. a cumulative upper envelope creates a discrete monotone frontier.

No binning, smoothing, or interpolation is used in the validated primary implementation. The semantic estimate is the smallest **tested** retained-information coordinate whose frontier reaches the target.

### 3.4 Configurable target rule

The target implementation is configurable:

\[
V_{\mathrm{target},r}
=
V_{\mathrm{actual},r}
-
\epsilon\left(V_{\mathrm{actual},r}-V_{\mathrm{constant},r}\right).
\]

The synthetic validation used `epsilon = 0.1` solely to exercise the code. It does not resolve pending decision P04 and is not a confirmatory production setting.

### 3.5 Censoring

When no tested frontier point reaches the target:

- `target_reached = false`;
- `censoring = right_censored`;
- `semantic_information = NaN`;
- `semantic_lower_bound = max_retained_information`.

The pipeline never substitutes the largest tested information value as an ordinary semantic point estimate.

### 3.6 Block bootstrap

The block bootstrap:

- resamples complete evolved-replicate blocks;
- is stratified by condition so independent sample sizes remain fixed;
- reconstructs every selected replicate frontier;
- retains censoring status;
- reports target-reaching fraction;
- reports semantic information only conditional on reached cases;
- reports lower bounds separately for censored cases;
- never imputes censored semantic estimates.

The number of validation bootstrap draws is intentionally small and diagnostic. The production bootstrap count remains to be frozen before confirmatory runs.

### 3.7 Replicate-level permutation inference

The permutation implementation accepts one row per condition and evolved replicate. Duplicate replicate rows are rejected.

Supported modes:

- unpaired label permutation for independently evolved groups;
- paired sign-flip permutation when a valid pairing key is supplied;
- exact enumeration when the assignment space is small;
- reproducible Monte Carlo permutation otherwise.

A censored semantic-information column containing `NaN` is rejected. In that setting, inference must use an always-defined replicate-level quantity such as target-reached status or value of information, rather than silently dropping censored replicates.

Bootstrap and permutation generators use distinct purpose-separated analysis streams.

## 4. Validation results

### 4.1 Test suite

`53` tests pass.

Coverage includes:

- reconstructed Phase 2 information estimators and endpoint identities;
- explicit observer RNG control;
- actual–identity continuation pairing;
- one frontier per baseline replicate;
- technical-seed aggregation within maps;
- duplicate-map collapse and conflict rejection;
- discrete monotone upper-envelope construction;
- exact target detection;
- explicit right censoring;
- machine-readable target counts;
- continuation-count variance diagnostics;
- stratified complete-block bootstrap;
- bootstrap handling of censored cases without imputation;
- exact unpaired replicate-level permutation;
- paired sign-flip permutation;
- rejection of pseudoreplicated and censored-invalid inference input.

### 4.2 Synthetic frontier recovery

The validation dataset contained:

- 12 independent synthetic baseline replicates;
- 2 conditions;
- 6 baseline replicates per condition;
- 6 map states per baseline block, including actual, constant, and identity;
- 4 continuation seeds per map;
- 288 continuation-level rows;
- 72 map-level rows.

The pipeline produced exactly 12 replicate-specific frontiers. The selective synthetic condition recovered a known semantic coordinate of `0.5`; the control condition recovered `1.0`. These values are validation targets, not Model B scientific results.

### 4.3 Identity recovery

Across all synthetic baseline blocks:

- identity retained information equalled baseline information;
- paired identity viability equalled actual viability;
- maximum absolute actual–identity viability difference was `0.0`.

The tiny model run also gave a maximum actual–identity mean-fitness difference of `0.0` and identical final populations.

### 4.4 Target-not-reached behavior

A deliberately truncated diagnostic removed the identity map from one control baseline block. The pipeline returned:

- `target_reached = false`;
- `censoring = right_censored`;
- `semantic_information = NaN`;
- `semantic_lower_bound = 0.75`.

The censored block bootstrap preserved this case and reported the target-reaching fraction and censored lower bound separately.

### 4.5 Continuation variance diagnostic

The synthetic diagnostic compared estimates based on the first `k` continuation seeds with each map's full four-seed mean. RMSE decreased from `0.12` at one continuation to numerical zero at four continuations. This validates the diagnostic required to inform P02; it does not choose the final continuation count.

### 4.6 Replicate-level permutation diagnostic

With six independent replicates per synthetic condition, exact label enumeration used all `924` assignments. The deliberately constructed condition differences were recovered for both semantic information and value of information. These p-values validate the inference machinery only and are not manuscript results.

## 5. Machine-readable evidence

Evidence is stored in `validation/phase3/`, including:

- `phase3_validation_summary.json`;
- `synthetic_continuations.csv`;
- `validated_continuations.csv`;
- `map_level_nested_summary.csv`;
- `replicate_frontiers.csv`;
- `replicate_frontier_summary.csv`;
- `paired_identity_diagnostic.csv`;
- `target_reach_counts.csv`;
- `continuation_variance_diagnostic.csv`;
- `block_bootstrap_intervals.csv`;
- `censoring_block_bootstrap_intervals.csv`;
- `replicate_level_permutation_results.csv`;
- `identity_model_diagnostic.json`;
- `pytest_stdout.txt`.

## 6. Decisions intentionally not made

Phase 3 does not resolve:

- P01 — final sequence-based grouping family;
- P02 — final number of continuation seeds;
- P03 — final intervention horizon;
- P04 — final target tolerance;
- P05 — final intervention-family pooling rule;
- P06 — final role of affinity-profile clustering.

The continuation-variance machinery now exists to support P02. Target handling is configurable to support P04. No confirmatory value was selected from production data.

## 7. Gate assessment

| Gate 3 criterion | Result |
|---|---|
| One frontier per independent evolved replicate | Pass |
| Map and continuation nesting enforced | Pass |
| Paired continuation streams implemented | Pass |
| Continuation-variance diagnostic implemented | Pass |
| Target detection validated | Pass |
| Target-not-reached represented as censoring | Pass |
| Identity information endpoint recovered | Pass |
| Identity continuation viability recovered | Pass |
| Complete-block bootstrap validated | Pass |
| Replicate-level permutation inference validated | Pass |
| Target counts and fractions machine-readable | Pass |
| No production simulations or manuscript rewrite | Pass |

**Gate 3: PASSED.**
