# R2 empirical marginal-preservation validation prespecification

Date: 2026-10-05
Status: frozen before diagnostic outcomes were generated.
Purpose: close the residual reporting gap for a realized stochastic validation of the marginal-preserving (MP) grouping operator. This is a validation analysis only; it does not change any primary estimand, intervention, population, map, threshold, or inferential claim.

## Frozen inputs
- The 20 previously evolved selective p=1.0 Model-B baseline populations from the Round-1 frozen Phase-4 archive.
- The final Round-2 MP probability-space operator.
- The existing 34-map frozen grouping panel; the empirical diagnostic reports the same representative MP maps already used in Table S3 / Figure S9: constant, balanced-random 16 groups, affinity-rank 64 groups, contiguous-substring start 0 length 2, start 3 length 2, start 1 length 3, and identity.
- The existing high-continuation observation stream root 2026100209 and continuation indices 0..63. No new outcome-dependent seed selection is permitted.

## Diagnostic design
For each of the 20 frozen p=1 selective baseline populations and each of 64 frozen continuation observation streams:
1. Generate the first local-state stochastic observation draw from the continuation start population.
2. Use the same uniform random numbers for the native kernel and each MP representative map (matched stochastic draws).
3. Compute empirical segment-conditioned one-site frequencies P_hat(Z|S) for native and MP.
4. Record the mean segment total-variation (TV) distance between native and MP P_hat(Z|S).

For each baseline population and map, pool the 64 observation draws and compute the pooled native-versus-MP mean segment TV. As a sampling-noise reference, compare native P_hat(Z|S) pooled over continuation streams 0..31 with native P_hat(Z|S) pooled over streams 32..63.

## Interpretation rule
- Analytical expected marginal preservation remains the primary mathematical guarantee.
- Realized native-versus-MP empirical TV need not be exactly zero because local-state assignments are stochastic.
- The empirical validation is considered consistent with the analytical guarantee if pooled native-versus-MP discrepancies are small and of the same order as the native split-half sampling-noise reference, with identity recovering native exactly under matched uniforms.
- No p-value or new primary inferential claim is created from this validation.

## Scope
This diagnostic is intentionally performed at the common continuation start state. Comparing native and MP trajectories after propagation would mix stochastic marginal realization with branch-population divergence. The MP operator's expected P(Z|S) preservation is branch-local and is recomputed from the current branch population; the present check validates stochastic realization of that property without introducing branch-state confounding.
