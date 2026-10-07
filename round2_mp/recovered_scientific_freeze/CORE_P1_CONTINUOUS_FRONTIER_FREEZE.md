# MP migration freeze — primary p=1 continuous marginal-preserving frontier

**Status:** confirmatory migration block complete and frozen  \n**Date:** 2026-10-02

## Frozen design

- 20 frozen sequence-selective p=1.0 baseline populations.
- 34 frozen grouping maps per population plus actual endpoint.
- 64 entirely new matched continuation streams per map, continuation root 2026100209.
- 36-generation horizon.
- 200 within-segment permutations per map for corrected retained information.
- Primary frontier interpretation is continuous; the historical 99% first-crossing statistic is secondary/descriptive only.

## Primary results

- Mean within-population Spearman rho between corrected retained information and MP recovery: **0.9240**.
- Median within-population rho: **0.9429**.
- Minimum rho across the 20 independently evolved populations: **0.5859**.
- Positive rho: **20/20** populations.
- Across the 34 map-averaged coordinates, Spearman rho = **0.9905**.
- Constant-endpoint MP loss: mean **2.2858** fitness units; 95% complete-baseline bootstrap **1.9121–2.6760**; positive in **20/20**; sign-randomization p = **0.0001**.

## Intervention-family monotonicity

- affinity_rank_group: n=9, map-average Spearman rho=1.0000, nondecreasing recovery=True.
- balanced_random_group: n=9, map-average Spearman rho=1.0000, nondecreasing recovery=True.
- contiguous_substring: n=14, map-average Spearman rho=0.9429, nondecreasing recovery=False.

## Secondary historical 99% target diagnostic

The old discrete first-crossing statistic is retained only as a descriptive audit. Identity was first by the mean frontier in **2/20** populations; **6/20** had a technically resolved nonidentity crossing, and **14/20** remained technically unresolved. This confirms the migration decision to retire the first-99%-crossing semantic estimate as the primary frontier quantity.

## Scientific interpretation

The MP intervention yields a strong graded relationship between retained sequence-dependent information and recovery of future model fitness while preserving the expected one-site segment-conditioned local-state marginal. The stable object is the continuous information-recovery relationship, not an operator-independent minimum-information threshold or identity requirement.
