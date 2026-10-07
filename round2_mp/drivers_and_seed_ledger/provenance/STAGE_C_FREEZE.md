# MP migration Stage C freeze

**Status:** Stage C protocol-sensitivity expansion complete and frozen before Stage-D outcome generation.

The migrated Stage-C design used the two representatives selected prospectively from the expanded n=8 MP domain screen: `B2_default` and `B2_stride7`. Each of the six historical protocol variants (baseline evolution duration 100, 150, 250 generations; intervention horizon 24, 36, 60 generations) was evaluated with n=8 independently evolved populations and 8 matched MP continuation streams per population. Historical thresholds and classification logic were unchanged.

Validation:
- 96 population-level records; 12 protocol settings; n=8 each.
- maximum numerical MP marginal-preservation error: 1.40e-13.
- reconstructed historical default-cohort state hashes: all matched.
- maximum reconstructed historical non-intervention difference: 8.88e-16.

Default `B2_default` remained `R3_strong_adaptation` under all six protocol variants.

`B2_stride7` was `R2_viability_relevant` at evolution durations 100 and 250 and horizon 60, and `R3_strong_adaptation` at evolution duration 150 and horizons 24 and 36. It remained MP viability-relevant under every protocol variant; no Stage-C setting reverted to syntactic-only or boundary/uncertain.

The Stage-D representatives are therefore finalized exactly as selected by the frozen rule from the expanded MP screen:
- D0: `A_p2_a3` — deepest R2 viability-relevant setting;
- D1: `B2_reward3` — deepest R3 strong-adaptation setting;
- D2: `B2_stride7` — nearest-boundary setting;
- D3: `B2_default` — default reference.

No representative was changed in response to Stage-C outcomes.
