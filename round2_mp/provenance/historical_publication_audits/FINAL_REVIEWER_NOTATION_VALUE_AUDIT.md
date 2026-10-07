# Final reviewer-specific notation/value audit

**Manuscript:** JRSI rsif-2026-0516.R1 — Major Revision #2  
**Scope:** exact current main-manuscript and Supplement LaTeX sources after main↔Supplement cross-reference synchronization  
**Audit purpose:** close the remaining Reviewer-2 notation/value gate before reproducibility-release work  
**Status:** **PASS after notation-only corrections documented below**

## 1. Audit method

The audit covered the complete main Methods, Results, main figure captions, Supplementary analytical notes, Supplementary Table S1, Tables S2–S7, and Supplementary figure captions. It checked:

1. first-use definition of every nontrivial mathematical symbol or indexed quantity in the main manuscript;
2. consistency between those definitions and Supplementary Table S1;
3. locally introduced Supplement-only notation;
4. reuse of index letters with conflicting meanings;
5. parameter-value and operational-threshold rationale;
6. reader-facing terminology and stale revision-history language;
7. successful recompilation after notation closure.

The notation table is treated as a reader aid, consistent with its caption; it does not replace first-use definitions in the main Methods.

## 2. Main-text first-use audit

All substantive notation is defined at, or immediately adjacent to, first use. The principal checks were:

| Symbol / family | First-use meaning | Audit result |
|---|---|---|
| `\mathcal X`, `N`, `n_olig`, `L`, `k` | alphabet and default structural dimensions | PASS |
| `n_win` | motif windows per oligomer | PASS |
| `i,o,t,u,v`, `x_{io\ell}`, `\ell`, `\mathcal M` | unit/slot/generation/window/within-window/sequence indices and motif universe | PASS |
| `n_S`, `s(u)` | positional-segment count and assignment | PASS |
| `M,Z,S`; `m,z,s`; `\mathcal Z` | random variables, realized values, local-state set | PASS |
| `\mathbf A=[a_{mz}]` | sequence-dependent affinity matrix | PASS |
| `\lambda_{mz}(s)`, `\mathbf 1[\cdot]`, `f(s)`, `\beta`, `\Theta`, `\sigma_a` | local-state logit, indicator, favored-state map, bias/noise/affinity scales | PASS |
| `c_{zz'}`, `n^+_{i,t}`, `n^-_{i,t}` | adjacency category and promoting/reducing counts | PASS |
| `F_{i,t}`, `\omega_+`, `\omega_-`, `F_min` | phenomenological model fitness and weights/floor | PASS |
| `\pi_{i,t}(\alpha)`, `\alpha`, `j` | source-selection probability, selection strength, denominator index | PASS |
| `source(i,t)`, `B_{io,t+1}`, `p` | selected source, slot-source indicator, parental-composition coupling | PASS |
| `X^{(0)}`, `\mathcal X_L`, `\widehat P_source`, `U(\mathcal X_L)` | pre-mutation identity and source/reservoir distributions | PASS |
| `D`, `\mu`, `T_evo` | mutation increment, mutation probability, baseline evolution duration | PASS |
| `I(X;Y)`, `I(X;Y|W)`, `P` | generic MI/CMI and empirical PMF | PASS |
| `I_tot`, `I_pos`, `I_seq`, `I_obs`, `E_perm`, `I_seq,corr` | information measures and finite-sample correction | PASS |
| `g`, `K_g`, group index `q`, `P_0`, `w_t`, `Q_t`, `P_t`, `g_identity` | grouping intervention and marginal-preserving kernel | PASS |
| replicate `r`, continuation `c`, horizon index `h`, `C`, `tau_int`, `\bar F` | future-fitness functional indices and averaging quantities | PASS |
| `V_r(g)`, `V_actual`, `V_MP,const`, `Delta V_MP`, `R_r(g)` | future-fitness outcome, MP loss, normalized recovery | PASS |
| `n` | independent inferential sample size in reported analysis | PASS |
| `Delta F`, overbar convention | sustained adaptive gain and initial/final mean-fitness windows | PASS |
| `delta_I`, `delta_V`, `delta_F` | fixed operational screening cutoffs | PASS |
| `q_BH` | Benjamini–Hochberg-adjusted p-value | PASS |
| `rho` | Spearman rank correlation coefficient | PASS; defined in context as Spearman correlation |

## 3. Notation conflicts found and closed

The exhaustive pass found four presentation-level notation inconsistencies. None affected data, equations as implemented, statistical results, or scientific interpretation.

### 3.1 Index collision: within-window `q` versus grouping-class `q`

The main motif-encoding definition had used `q` for within-window position, while Figure 2, its caption, and Supplementary Table S1 used `q` for grouping class. The MP equations in the main text used `b`, creating a three-way inconsistency.

**Closure:**
- within-window position index renamed `q -> v` in the motif-encoding definition and summation;
- grouping-class index standardized to `q` throughout the main MP-intervention equations and prose;
- Figure 2 artwork/caption and Supplementary Table S1 already used `q`, so they now agree exactly.

This is a notation-only alpha-renaming; equations and numerical content are unchanged.

### 3.2 Sequence notation in Supplementary Table S1

Table S1 listed bare `X` as an “oligomer sequence state,” whereas the main text distinguishes the alphabet `\mathcal X` and pre-/post-mutation sequence-identity variables.

**Closure:** Table S1 now uses `\mathcal X; X^(0), X` and describes the alphabet plus pre-/post-mutation sequence-identity variables.

### 3.3 Affinity-matrix typography

Table S1 used `A=(a_mz)` while the main text defines `\mathbf A=[a_mz]`.

**Closure:** Table S1 now reproduces the main definition `\mathbf A=[a_mz]`.

### 3.4 Local-state cardinality

Table S1 and the Stage-B1/B2 screening record used `|Z|` for the number of local-state classes, while the main text defines `\mathcal Z` as the local-state set and `Z` as the random variable.

**Closure:** local-state cardinality is now written `|\mathcal Z|` in Table S1 and every affected Table S2 setting. Numerical values are unchanged.

## 4. Supplement-only notation

Supplement-specific notation not carried into Table S1 was checked for local definition and is acceptable:

- `TV` is introduced explicitly as total-variation distance in Table S4;
- `\widehat P(Z|S)` is explicitly identified as the empirical realized one-site distribution in Table S4 / analytical notes;
- `rho` is identified as Spearman correlation wherever used in Table S7 and the main text;
- L0–L7 are explicitly defined as deterministic affinity-landscape generator identifiers in Table S3;
- exact `p` values and `q_BH` values are explicitly identified as inferential statistics in Tables S3 and S6.

No Supplement symbol was found to carry a meaning that conflicts with the main manuscript after the closures above.

## 5. Parameter-value and threshold rationale

Reviewer-sensitive parameter/rationale checks pass:

- `N`, `n_olig`, `L`, and `k`: explicitly identified as dimensionless Model-B design choices rather than empirically calibrated prebiotic constants;
- `n_S`: explicitly identified as a balanced design choice;
- favored-state order `2,0,3,1`: explicitly identified as a fixed reference label permutation with no intrinsic rank;
- `beta`: explicitly identified as a model-design default rather than an empirical effect size;
- `Theta`: explicitly identified as a numerical sampling-noise scale, not thermodynamic temperature;
- affinity scores: explicitly identified as dimensionless model parameters, not biochemical binding constants;
- `omega_+`, `omega_-`, `F_min`: explicitly identified as phenomenological design defaults / numerical safeguard rather than biochemical constants or biological survival threshold;
- `mu`: explicitly identified as an uncalibrated model default;
- `p`: explicitly interpreted as effective parental-composition coupling, not literal molecular retention;
- affinity-rank coefficient `0.25`: explicitly identified as a fixed prespecified map-construction constant, not a fitted parameter;
- `delta_I=0.01`, `delta_V=0.25`, `delta_F=1.0`: explicitly identified as fixed operational screening cutoffs, not biologically calibrated or universal thresholds;
- `n=20`, `n=8`, landscape-level `n=8`, continuation counts, and permutation counts: roles and inferential hierarchy are explicitly distinguished.

## 6. Reader-facing terminology scrub

The current main + Supplement sources contain no reader-facing occurrence of the deprecated/problematic phrases:

- `value of information`
- `recovery fraction`
- `historical affinity-logit`
- `submitted`
- `migrated`
- `expanded`
- `protocell-like`

No stale Supplementary Figure S7/S8/S9 cross-reference remains. Current Table S7 is intentional and valid. No old Stage A/B `n=3–4` sample-size statement remains.

## 7. Build and layout verification

After notation closure:

- main manuscript compiles to 23 pages;
- Supplement compiles to 14 pages;
- final `main.log` contains no undefined references or citations;
- final Supplement log contains no undefined references;
- Supplementary Table S1 remains on one portrait page and is visually readable;
- the MP-intervention equations now display group index `q`, matching Figure 2 and the notation table;
- scientific numbers, classifications, intervals, p/q values, and figure source data were not altered.

## 8. Freeze-gate conclusion

**Reviewer-specific notation/value audit: PASS.**

The previously remaining notation gate is closed. The only changes made during this audit are symbol/typography standardizations; there is no scientific or numerical change. The main + Supplement package can now be treated as notation-closed and can proceed to the immutable Round-2 reproducibility-release stage.
