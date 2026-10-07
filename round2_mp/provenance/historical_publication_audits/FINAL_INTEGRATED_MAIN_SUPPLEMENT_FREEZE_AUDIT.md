# JRSI Major Revision #2 - Final integrated main + Supplement freeze audit

**Date:** 2026-10-06  
**Status:** PASS - main manuscript and Supplement are synchronized and suitable for scientific/layout freeze.  
**Controlling inputs:** the two user-provided final source ZIP files preserved in `input_zips/`.

## 1. Clean-build verification

- Main manuscript: clean `latexmk -pdf` build completed successfully; 23 A4 pages.
- Supplement: clean `latexmk -pdf` build completed successfully; 14 A4 pages.
- No undefined references or undefined citations were present in either final build.
- PDF preflight: both PDFs open normally, are unencrypted, and contain searchable text.
- Recompilation render comparison against the immediately preceding accepted builds found 0 visually changed pages in both main and Supplement at 80 dpi.

## 2. Main <-> Supplement cross-reference synchronization

Final main-text mapping is correct:

- notation summary -> Supplementary Table S1;
- MP marginal-preservation diagnostics -> Supplementary Figure S6 and Table S4;
- replicate-specific / complementary core frontier diagnostics -> Supplementary Figures S1 and S2;
- first-99%-recovery diagnostic -> Supplementary Table S5;
- alternative-topology disaggregation / six-contrast record -> Supplementary Figure S3 and Table S6;
- affinity-landscape numerical/provenance record -> Supplementary Table S3;
- 65-setting domain map -> Supplementary Table S2 and Figure S4;
- Stage C protocol sensitivity -> Supplementary Figure S5 and Table S7(a);
- Stage D full-pipeline confirmations -> Supplementary Table S7(b).

No stale Supplementary Figure S8/S9 references remain.

## 3. Supplement numbering, ordering, and layout

- `Supplementary Tables` appears before Table S1.
- Table sequence is S1-S7.
- All tables precede the supplementary figures.
- `Supplementary Figures` appears on the same page as Figure S1; the prior blank-space issue is resolved.
- Figure sequence is S1-S6.
- Figure S3 and Figure S5 have no unnecessary top-level figure title.
- Figure S6 retains the final three-panel diagnostic layout with corrected panel spacing.
- Visual render review found no clipped captions, figure/table overlap, black glyph boxes, or page-edge clipping.

## 4. Scientific source integrity

Relative to the previously audited S1-S7 Supplement package, all data-bearing table files are unchanged. The only table-source edits are layout relocation of `\\clearpage` / the `Supplementary Tables` heading into `main.tex`.

- Figures S1-S4 are byte-identical to the audited prefreeze versions.
- Figure S5 is pixel-identical to the separately audited title-removed version.
- Figure S6 is pixel-identical to the separately audited final-spacing version.

The final main source differs from the immediately preceding audited source only by two editorial corrections: a missing period after the Table S6 cross-reference and removal of duplicated wording in the Table S7(b) sentence. Neither change affects scientific content or numerical values.

## 5. Numerical synchronization

The prior source-table synchronization campaign is carried forward because the data-bearing Supplement tables are unchanged and the final main changes are editorial only. The corrected final record is `FINAL_NUMERICAL_SYNC_AUDIT_75_OF_75.md`.

Result: **75/75 targeted numerical checks pass.** These cover the core MP coupling sweep, p=1 high-continuation frontier, first-99% diagnostic, all six causal-specificity contrasts, independent affinity landscapes, 65-setting class counts, fraction-normalized boundary case, Stage D confirmations, and expected/realized MP marginal diagnostics.

The first-99% source record was explicitly rechecked during this final audit: 6/20 populations are technically resolved nonidentity and 14/20 are technically unresolved; identity is first in 2/20 and those two are within the unresolved group. A stale contradictory line in an earlier working audit was an audit-reporting artifact and is not carried into this freeze.

## 6. Terminology and scope scrub

No reader-facing occurrences remain of the deprecated/stale phrases searched for in the final TeX sources, including `value of information`, `recovery fraction`, `historical affinity-logit`, `old operator`, `migrated`, `protocell-like`, or stale S8/S9 references.

The final manuscript preserves the required scope boundaries: Model B is an abstract evolutionary/compositional-resampling model; `p` is parental-composition coupling rather than literal molecular retention; `Delta V_MP` is a model-fitness loss rather than an information-theoretic quantity; and the supported frontier claim is graded/intervention-specific rather than an operator-independent minimum representation.

## 7. Notation / first-use audit

Reviewer-sensitive notation items are in acceptable final state. In particular: `n_win` is defined when introduced; mutual-information notation is defined before the analytical expectation; `C` and `tau_int` are defined before use in the future-outcome functional; `g_identity` is explicitly defined; overbars in `Delta F` are explained; `q_BH` is defined at first reported use; and the pre-mutation sequence variable is explicitly identified. Table S1 is a reader aid and does not substitute for these main-text definitions.

## 8. Build-warning disposition

The Royal Society class emits expected underfull/overfull box warnings associated with its page geometry and float handling. One large `longtable` diagnostic is emitted at the Table S2 caption line, but render inspection confirms that the caption and table remain within the printable area with no visible clipping or overflow. These warnings are therefore classified as nonblocking layout diagnostics, not submission defects.

## 9. Freeze decision

**PASS.** No scientific inconsistency, stale cross-reference, numbering defect, or blocking visual defect was found. The main manuscript and Supplement are frozen at the exact source states contained in this package.

The next project phase is separate from this manuscript/Supplement freeze: build the immutable Round-2 reproducibility release, run the network-enabled clean-install/regeneration check, publish/verify the archival DOI, and then synchronize the final Data Accessibility statement and repository metadata.
