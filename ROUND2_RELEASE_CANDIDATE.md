# Round-2 release candidate

Candidate branch: `round2-release-candidate-v2.0.0`

Base repository commit: `dadee39c832751fe0be21bdcf26343a3039d757c`

This candidate layers the frozen Round-2 MP-primary evidence over the validated historical repository without mutating the Round-1 release state.

## Current-evidence scope

Included:
- frozen MP-primary source tables;
- MP migration/diagnostic scripts;
- exact MP migration SHA-256 provenance;
- final manuscript/Supplement freeze hashes;
- explicit supersession documentation.

Not current evidence:
- historical affinity-logit primary analyses;
- historical Supplementary Figures S7-S9;
- earlier 21-page main / 13-page Supplement builds;
- older Gate-8 publication-figure outputs.

Those remain historical provenance only.
