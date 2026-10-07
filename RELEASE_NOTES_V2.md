# Round-2 reproducibility release candidate RC7

Round-2 analysis uses a probability-space marginal-preserving intervention as primary, with the historical pre-softmax intervention retained as a secondary comparator. The package includes recovered production drivers, seed provenance, immutable historical inputs, regenerated landscape states and full numerical validation records.

RC3 completed 68 foundation tests and the 29-table regeneration gate; 256 landscape state hashes matched, and the 15,360-row causal-specificity raw table reproduced byte-for-byte. RC4 separated publication documents from the computational repository. RC7 removes the machine-specific editable dependency path and adds release metadata and an updated CI workflow. Scientific production code and source tables are unchanged.

The MP module is a functional reconstruction, not byte-identical recovery. Core, frontier and causal specificity start from archived Round-1 states; screening, Stage C/D and independent landscapes start from deterministic initial seeds. See ROUND2_RELEASE_SCOPE.md for the full boundary.

Publication and validation from a public v2 tag remain pending. No v2 DOI is claimed.

RC7 restores all 14 current standalone figure PDFs and historical document-validation records omitted by RC4. Final-layout figure regeneration remains unvalidated; archived assets are hash-verified.

RC7 adds a validated portable final-figure build in a separate plotting environment. All 12 data figures reproduce exactly at 144 dpi; the two conceptual diagrams are archived copies. Earlier statements about an unvalidated final-layout build describe RC6 and are superseded by FIGURE_BUILD_VALIDATION.json.
