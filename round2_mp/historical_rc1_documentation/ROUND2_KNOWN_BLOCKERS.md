# Known blockers after RC1

## B1 - exact MP production-driver provenance

**Severity:** release-gating for a claim of full end-to-end production regeneration.

The recovered Round-2 materials include frozen source tables, figure-generation scripts, marginal-diagnostic scripts, empirical P(Z|S) validation code, and the Gate-8 implementation/evolved states. A single exact archived production driver (or complete set of drivers) that produced every MP-primary source table has not yet been found.

This is not a manuscript numerical inconsistency. The frozen source tables have independent manuscript/Supplement synchronization audits and 24/24 original-hash verification for the principal tables/scripts.

### Next test

Run packaged validation and clean-room diagnostic regeneration from RC1. This will distinguish:

- components already reproducible from archived states/code;
- components reproducible from frozen source tables only;
- any remaining production-only provenance exception requiring documentation or recovery.

## B2 - public release metadata

GitHub default branch/README and public release metadata still describe the earlier v1.0.0/Gate-8 release. Do not update DOI/Data Accessibility or create an immutable v2 tag until RC2-RC5 pass.
