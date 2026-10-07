# JRSI R2 P0 gap-closure report — 2026-10-05

## Conclusion

The two narrow P0 items identified after review of the current Supplement can now be treated as closed at the validation/provenance level.

1. **Affinity-landscape provenance:** closed. The production design did not use eight free-standing scalar affinity seeds. It used a keyed deterministic RNG: root seed `2026100211`, purpose string `affinity-landscape`, and landscape key `L = 0,...,7`. This uniquely reconstructs each 1024 x 4 standard-normal base matrix. A reader-facing L0–L7 provenance ledger has been generated with the exact SeedSequence entropy words and SHA256 hash of every base matrix. No invented scalar seed is required.
2. **Realized stochastic P(Z|S) validation:** closed by a compact prospective diagnostic frozen before outcomes. The validation used the 20 frozen selective p=1 baseline populations, the existing 64 high-continuation observation streams (root `2026100209`), and matched native-versus-MP local-state draws at the common continuation start state. It introduced no new evolutionary simulation, intervention map, threshold, or inferential claim.

## 1. Affinity-landscape provenance

The independent-landscape prespecification specifies generation of landscape `L` as a 1024 x 4 standard-normal matrix from `make_generator(2026100211, "affinity-landscape", L)`. The production script uses that exact construction. Because `make_generator` builds a NumPy `SeedSequence` from the root plus SHA256-derived purpose/key entropy, there is no separate scalar seed parameter for each landscape.

The correct provenance mapping is therefore:

`L0 -> (root=2026100211, purpose="affinity-landscape", key=0)`
through
`L7 -> (root=2026100211, purpose="affinity-landscape", key=7)`.

`R2_AFFINITY_LANDSCAPE_PROVENANCE_LEDGER_L0_L7.csv` records those keys, the exact SeedSequence entropy words, and the SHA256 of each generated base matrix. These matrix hashes provide a direct verification target for clean-room regeneration.

### Recommended Supplement/repository wording

> Eight independent affinity landscapes, labelled L0–L7, were generated deterministically from root seed 2026100211 using purpose-separated RNG keys `("affinity-landscape", L)`, with `L=0,...,7`. The complete generator-key ledger and SHA256 hash of each 1024 x 4 base matrix are provided in the reproducibility archive. Because the RNG is constructed from a root seed plus purpose/key entropy rather than a separate scalar seed for each landscape, L0–L7 and their generator keys are the controlling affinity-landscape provenance identifiers.

## 2. Realized empirical marginal-preservation validation

### Frozen design

The diagnostic was prespecified before outcomes in `R2_EMPIRICAL_MARGINAL_VALIDATION_PRESPEC_2026-10-05.md` (SHA256 `d8cbf8207b9652fc540b4201207a5dfd27880a5d4613bd0e6342a202d26d413c`).

For each of the 20 frozen p=1 selective baseline populations, the first stochastic local-state observation draw from each of 64 already-defined continuation streams was evaluated under the native kernel and the representative MP maps using the same random uniforms. This exactly mirrors the matched-common-random-number structure used by the continuation design while avoiding branch-population divergence.

Each stochastic draw contains 35,840 local-state observations. The 64 draws were pooled within each baseline population before computing empirical segment-conditioned one-site frequencies and native-versus-MP mean segment total-variation distance.

As an independent sampling-noise reference, native draws from streams 0–31 were compared with native draws from streams 32–63.

### Results

| MP map | Mean pooled 64-stream TV | Maximum pooled TV across 20 baselines | Mean single-stream TV |
|---|---:|---:|---:|
| Constant | 0.000784 | 0.001117 | 0.006256 |
| Balanced-random, 16 groups | 0.000654 | 0.001164 | 0.004988 |
| Affinity-rank, 64 groups | 0.000410 | 0.000655 | 0.003030 |
| Substring start 0, length 2 | 0.000637 | 0.000978 | 0.004963 |
| Substring start 3, length 2 | 0.000632 | 0.000886 | 0.005084 |
| Substring start 1, length 3 | 0.000470 | 0.000672 | 0.003622 |
| Identity | 0.000000 | 0.000000 | 0.000000 |

The mean native split-half TV, which estimates ordinary stochastic sampling variation with the same total number of draws, was **0.001552**. Thus every nonidentity MP map had a mean pooled native-versus-MP TV below the native sampling-noise reference; the largest was 0.000784. Identity recovered native exactly under the matched draws.

### Interpretation

The analytical result remains the substantive guarantee: the MP probability-space operator preserves expected one-site `P(Z|S)` exactly for the branch population. The realized diagnostic shows that stochastic local-state draws fluctuate around that equality at the expected sampling scale rather than exhibiting a systematic marginal shift. The diagnostic does not assert that adjacency composition or fitness are preserved; those are intentionally free to change and are already reported analytically in Table S3/Figure S9.

The check is performed at the common continuation start state deliberately. Comparing native and MP populations after propagation would confound local-state sampling with the different population compositions generated by the two branches. Because MP weights are recomputed from the current intervention-branch population, expected marginal preservation is branch-local at every generation; the present stochastic check validates realization of that construction without branch-state confounding.

### Recommended Supplement addition

A compact extension to Table S3 is sufficient; no new main figure is needed. Add columns or a small Table S3b reporting:

- analytical expected `P(Z|S)` TV (existing);
- realized pooled 64-stream native-versus-MP `P_hat(Z|S)` TV;
- maximum pooled TV across the 20 baseline populations;
- the native split-half sampling reference (`0.001552`).

Suggested caption sentence:

> A stochastic validation used the first local-state draw from each of 64 matched continuation streams for each of the 20 frozen p=1 selective populations. After pooling the 64 draws within population, mean native-versus-MP `P_hat(Z|S)` TV ranged from 0.000410 to 0.000784 across representative nonidentity MP maps, below the 0.001552 mean native split-half sampling reference; the identity map recovered native exactly. These empirical discrepancies therefore reflect finite stochastic sampling around the analytically identical expected one-site marginals.

## 3. Status change

### R1.2 marginal diagnostic
**Before:** expected/analytical preservation closed; realized stochastic validation open.

**Now:** both analytical and realized one-site marginal diagnostics are closed. Remaining work is only integration into the final Supplement and main-text cross-reference.

### R1.3a affinity generality provenance
**Before:** L0–L7 identities and inference closed; affinity-matrix seed provenance open.

**Now:** generator provenance is closed. The exact keyed RNG construction and base-matrix hashes are sufficient to reproduce and audit L0–L7. Remaining work is only inclusion of the provenance ledger in the final repository/Supplement record.

## 4. Remaining acceptance-critical item

These two P0 gaps no longer require scientific analysis. The acceptance-critical open item remains the immutable Round-2 reproducibility release, clean-install/regeneration check, published/resolving archive DOI, and synchronized Data Accessibility statement.
