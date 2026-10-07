# Canonical seed provenance

Use both the exact recovered `round2_mp/drivers_and_seed_ledger/seed_ledger/MP_SEED_LEDGER.csv` (27,139 rows) and `round2_mp/provenance/FINAL_64NEW_CAUSAL_SPECIFICITY_SEED_LEDGER.csv` (32,012 rows). The former's historical missing-causal-campaign status statements are superseded by the latter and the recovered production driver. Every nonempty recovered SeedSequence entropy specification is checked against the historical RNG law.

The final causal ledger has 30,720 observation/propagation records, 1,280 topology-schedule records, and 12 primary inference records. Repeated pairing keys across evaluations deliberately share common random numbers; ledger records are not independent scientific replicates.

Primary causal-specificity continuation root: 2026073104, indices 2 through 65. Dynamic topology root: 2026073105. Primary inference root: 2026100202. Six contrasts use 9,999 sign randomizations and 2,000 bootstrap resamples. The 20 independently evolved seed blocks remain the inferential units.

The complete Round-1 baseline/control state and selection specifications are inherited immutable dependencies under `results/phase4_core/` and `results/phase5_causal_specificity/`. The MP registry records the later core/screen/Stage C/Stage D/frontier and landscape roots. Landscape matrices use root 2026100211 with the purpose/key tuple (affinity-landscape, L), L=0..7; no scalar landscape seed is invented.

For the supplemental causal ledger, specification_sha256 means SHA256 of UTF-8 compact sorted-key JSON of root_seed, purpose and keys. The entropy formula is root_seed & 0xffffffff followed by eight little-endian words from SHA256 of the separator-joined purpose and keys; the included rng.py is authoritative.
