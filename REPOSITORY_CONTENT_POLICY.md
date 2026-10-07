# Repository content policy

The reproducibility repository contains simulation and analysis code, immutable state inputs, seed ledgers, numerical source tables, generated analysis outputs, environment requirements, and validation/provenance records.

Manuscript and Supplement prose, TeX/typesetting sources, compiled manuscript/Supplement PDFs, paper-page screenshots, and publication-source ZIPs are maintained separately. Historical copies of those publication assets are also excluded. Analysis figures and numerical tables remain scientific outputs; table filenames referring to the Supplement do not make them prose assets.

Changes confined to the abstract, introduction, discussion, or Supplement wording do not require a repository update or a new computational release. Changes affecting data, reported numerical results, implemented methods, analysis code, or reproducibility claims require corresponding repository changes and appropriate validation. Before submission, check numerical claims in the separately maintained paper against the source tables.

The Table S4(b) correction remains in the numerical source: substring start 3, length 2, maximum pooled TV across 20 baselines = 0.000886 at six decimals. The original compact CSV and the correction rationale are retained as numerical provenance.

RC4 supersedes RC3 for repository packaging. The code-and-data scientific evidence is unchanged. Historical manuscript-sync audits describe earlier snapshots and are not requirements to version future prose revisions here.

RC6 correction: standalone scientific figure PDFs are permitted under round2_mp/figures/. Only manuscript/Supplement document PDFs and prose/typesetting sources are excluded. RC4/RC5 inadvertently omitted the current figure folders; RC6 restores them by exact archival hash.
