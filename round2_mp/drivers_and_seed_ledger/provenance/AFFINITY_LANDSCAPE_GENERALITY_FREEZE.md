# MP migration freeze — independent affinity-landscape generality

**Status:** prospective independent-landscape campaign complete and frozen  \n**Date:** 2026-10-02

## Frozen design

- 8 entirely new independent 1024 x 4 standard-normal affinity landscapes.
- 8 independently evolved populations nested within every landscape x setting cell.
- Four settings fixed before outcomes: B2_default, A_p2_a3, B2_reward3, B2_stride7.
- 8 matched MP constant-endpoint continuation streams per population; 36-generation horizon.
- Landscape is the inferential unit; nested populations do not inflate n.
- Historical fixed landscape excluded from primary n=8 landscape inference.

## Results

### A_p2_a3

- Mean landscape-level DeltaV_MP: **0.2249** fitness units.
- 95% landscape-bootstrap interval: **0.0810–0.3929**.
- Positive landscape means: **7/8**.
- Exact two-sided landscape sign-randomization p: **0.03125**.
- Replicated across landscapes by frozen rule: **True**.
- Landscapes whose nested-population 95% lower bound exceeded the unchanged 0.25 practical threshold: **3/8**.
- Mean corrected information across landscapes: **0.4670 bits**.
- Mean adaptive gain across landscapes: **0.0473 fitness units**.

### B2_default

- Mean landscape-level DeltaV_MP: **2.3724** fitness units.
- 95% landscape-bootstrap interval: **2.1750–2.5603**.
- Positive landscape means: **8/8**.
- Exact two-sided landscape sign-randomization p: **0.00781**.
- Replicated across landscapes by frozen rule: **True**.
- Landscapes whose nested-population 95% lower bound exceeded the unchanged 0.25 practical threshold: **8/8**.
- Mean corrected information across landscapes: **0.2547 bits**.
- Mean adaptive gain across landscapes: **4.3275 fitness units**.

### B2_reward3

- Mean landscape-level DeltaV_MP: **3.2439** fitness units.
- 95% landscape-bootstrap interval: **2.9237–3.6159**.
- Positive landscape means: **8/8**.
- Exact two-sided landscape sign-randomization p: **0.00781**.
- Replicated across landscapes by frozen rule: **True**.
- Landscapes whose nested-population 95% lower bound exceeded the unchanged 0.25 practical threshold: **8/8**.
- Mean corrected information across landscapes: **0.2510 bits**.
- Mean adaptive gain across landscapes: **6.1208 fitness units**.

### B2_stride7

- Mean landscape-level DeltaV_MP: **1.5496** fitness units.
- 95% landscape-bootstrap interval: **1.4812–1.6229**.
- Positive landscape means: **8/8**.
- Exact two-sided landscape sign-randomization p: **0.00781**.
- Replicated across landscapes by frozen rule: **True**.
- Landscapes whose nested-population 95% lower bound exceeded the unchanged 0.25 practical threshold: **8/8**.
- Mean corrected information across landscapes: **0.2450 bits**.
- Mean adaptive gain across landscapes: **1.2703 fitness units**.

## Interpretation

The primary default, strong-adaptation B2_reward3, and stride-7 Stage-D setting generalize strongly across all eight new affinity landscapes: their MP causal effects are positive in 8/8 landscapes and their practical intervention threshold is exceeded in 8/8 landscape cells.

A_p2_a3 is more landscape-sensitive. Its across-landscape mean MP causal effect is positive and passes the frozen landscape-level replication rule, but only 3/8 landscape cells have nested-population lower bounds above the 0.25 practical threshold, and one landscape has a negative mean effect. Therefore the causal effect has cross-landscape support, but the stronger claim that A_p2_a3 is consistently viability-relevant by the study's practical classification threshold does not generalize across affinity landscapes. This distinction must be preserved in the manuscript.
