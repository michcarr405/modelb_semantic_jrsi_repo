# Final Figures 1 and 2 artwork validation

**Date:** 2026-08-08  
**Status:** PASSED for reproducibility-release artwork archiving  
**Scope:** production/export validation only; no frozen scientific result was changed.

## Source files

The author supplied:

- `artwork/masters/Figure_1.svg`
- `artwork/masters/Figure_2.svg`

Both are editable SVG vector files. Derivative exports were produced without changing visible labels, equations, endpoint definitions, intervention membership, or model logic.

## Export set

For each master, the release contains:

- PDF vector export;
- EPS vector export;
- 600 dpi grayscale PNG proof;
- 600 dpi grayscale TIFF proof.

Export tooling used for this release-candidate proof:

- Inkscape 1.4;
- ImageMagick 7.1.2-1.

The 600 dpi raster files are 4252 x 2953 pixels. TIFF exports record 600 x 600 pixels/inch and use LZW compression. PNG exports contain the equivalent 600 dpi density metadata and grayscale image data.

## Figure 1 scientific-content proof

The final artwork was visually inspected at full-size and rendered-PDF proof size. It contains four lower-case labelled panels and preserves the required model-scope distinctions:

- **(a)** fixed model-unit oligomer slots, overlapping sequence windows, four positional bins, and explicit distinction between sequence identities and transient local-state labels;
- **(b)** transient local-state assignment is described as re-sampled during observation and *not a transmitted inventory*;
- **(c)** the adjacency-category matrix distinguishes fitness-promoting, fitness-reducing, and fitness-neutral pairs, including `(0,2)` and `(2,0)` as neutral; model fitness is explicitly a phenomenological score and not protocell growth chemistry;
- **(d)** population updating is shown as fitness-weighted source selection plus independent slot-level compositional resampling and point mutation; the parent-derived branch explicitly states **sample with replacement**; the alternative branch samples from the idealized uniform sequence reservoir; `p` is labelled parental-composition coupling/compositional-transmission fidelity.

No daughter-pair fission, membrane cleavage, conserved-molecule transfer, molecular synthesis, or physical partitioning is depicted.

## Figure 2 scientific-content proof

The final artwork was visually inspected at full-size and rendered-PDF proof size. It preserves the current intervention definition:

- grouping changes sequence-dependent affinity profiles used for local-state assignment while motif identities and listed model components remain unchanged;
- within-group affinity-profile distinctions are removed and between-group distinctions remain;
- the internal label is **“Intervention families:”**, not “Primary intervention families”;
- the displayed active families are balanced-random grouping, affinity-rank grouping, and contiguous-substring grouping;
- constant and identity endpoints are present with the validated limiting relations;
- actual retained information is stated directly as `I_ret,r(g) = I(g(M); Z | S)` and is explicitly not inferred from group count or a logarithmic resolution heuristic.

No affinity-profile k-means family or semantic-compression claim is shown.

## Render/export proof

The PDF exports were re-rendered at 200 dpi using the project PDF verification workflow and visually compared with the supplied SVG masters. No clipping, missing arrowheads, displaced labels, panel loss, or scientific-content differences were observed. The grayscale raster proofs remain legible and preserve all categorical distinctions without reliance on color.

## Controlling-manuscript comparison

The author-supplied Figure 1 and Figure 2 artwork matches the corresponding rendered figures in the controlling revised manuscript PDF used for the final integrated Gate 6 audit. Figure 2 retains the already-corrected “Intervention families” wording.

**Decision:** the Figure 1/2 artwork archiving and standalone-export requirement is closed for RC4, subject only to replacement if a newer author-approved master is intentionally introduced before final release.
