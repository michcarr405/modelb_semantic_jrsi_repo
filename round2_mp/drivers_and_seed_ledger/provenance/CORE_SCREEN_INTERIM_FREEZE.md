# MP migration interim freeze — core and expanded domain screen

**Status:** core constant-endpoint MP sweep and Stage A/B1/B2 expanded n=8 domain screen complete; Stage C/D not yet run.  
**Prespecification commit:** `522db2cab60ca83df708457961dd389c112e7a78`.

## Core MP sweep

All 20 selective blocks were positive at every compositional-coupling value. The agnostic/control MP loss was exactly zero by construction and implementation validation. Mean MP intervention-induced future-fitness loss increased strongly with p:

| p | mean DeltaV_MP | 95% bootstrap interval |
|---:|---:|---:|
| 0.1 | 0.101799 | 0.092131–0.111204 |
| 0.2 | 0.098298 | 0.086011–0.110472 |
| 0.3 | 0.114799 | 0.101563–0.127731 |
| 0.4 | 0.119315 | 0.107709–0.132162 |
| 0.5 | 0.134553 | 0.125162–0.143699 |
| 0.6 | 0.167113 | 0.155468–0.178115 |
| 0.7 | 0.210428 | 0.193744–0.227695 |
| 0.8 | 0.308062 | 0.279192–0.336986 |
| 0.9 | 0.723521 | 0.663137–0.785602 |
| 1.0 | 2.248146 | 1.843924–2.640075 |

All ten two-sided sign-randomization tests versus the exact agnostic zero have BH-adjusted q=0.0001. The effect is small at low p (~0.10 fitness unit) and rises to ~2.25 units at p=1.0.

## Expanded n=8 Stage A/B1/B2 screen

The historical 65 settings were retained unchanged and every setting was expanded to eight independently evolved populations. Deterministic reconstruction of all 244 historical screen populations reproduced the frozen state hashes exactly and non-intervention metrics to <=3.6e-15. The MP marginal-preservation numerical error was <=3.3e-13.

New regime counts:

| stage   |   R0_null |   R1_syntactic_only |   R2_viability_relevant |   R3_strong_adaptation |   boundary_uncertain |
|:--------|----------:|--------------------:|------------------------:|-----------------------:|---------------------:|
| A       |         8 |                  10 |                      10 |                      4 |                    0 |
| B1      |         2 |                  11 |                       1 |                      1 |                    1 |
| B2      |         0 |                   1 |                       1 |                     15 |                    0 |

The migrated classification differs from Round 1 at **16 of 65 settings**. The dominant change is attenuation of the original viability-relevant class to syntactic-only under the marginal-preserving operator. This is a substantive scientific result, not a plotting change.

The ten Stage-A settings that move from R2 viability-relevant to R1 syntactic-only include the former Stage-D viability representative `A_high_2`. In B1, four historical viability-relevant settings move to syntactic-only. B2 is much more stable: 15/17 settings remain strong-adaptation, one viability-relevant and one syntactic-only.

The migrated Stage-C representatives selected by the frozen rule are:

- default: `B2_default` (R3 strong-adaptation; mean DeltaV_MP=2.588939);
- nearest boundary: `B2_stride7` (R2 viability-relevant; mean DeltaV_MP=1.386929).

The provisional Stage-D selection under the unchanged historical rule is:

- D0: `A_p2_a3` — deepest R2 viability-relevant setting;
- D1: `B2_reward3` — deepest R3 strong-adaptation setting;
- D2: `B2_stride7` — nearest boundary setting;
- D3: `B2_default` — default reference.

Round-1 `A_high_2` and `A_low_3` are therefore **not retained by the migrated selection rule**. They will not be privileged post hoc.

## Next frozen step

Run Stage C at n=8 for `B2_default` and `B2_stride7` under the unchanged six protocol variants, then finalize Stage-D selection and run the complete 34-map MP confirmation on the selected nondefault settings. The p=1 64-continuation confirmatory continuous frontier remains outstanding.
