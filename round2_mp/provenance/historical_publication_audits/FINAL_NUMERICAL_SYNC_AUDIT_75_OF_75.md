# Integrated main + Supplement numerical synchronization audit

Checks passed: **75/75**.

- PASS — **core delta p=0.1**: source=0.101799, main=0.101799
- PASS — **core positive p=0.1**: positive=20/20
- PASS — **core q p=0.1**: q=0.00010
- PASS — **core delta p=0.9**: source=0.723521, main=0.7235
- PASS — **core positive p=0.9**: positive=20/20
- PASS — **core q p=0.9**: q=0.00010
- PASS — **core delta p=1.0**: source=2.248146, main=2.2481
- PASS — **core positive p=1.0**: positive=20/20
- PASS — **core q p=1.0**: q=0.00010
- PASS — **core p=1 CI low**: source=1.843924, main=1.8439
- PASS — **core p=1 CI high**: source=2.640075, main=2.6401
- PASS — **first99 all reached**: reached=20/20
- PASS — **first99 identity first**: identity-first=2/20
- PASS — **first99 resolved nonidentity**: resolved nonidentity=6
- PASS — **first99 unresolved**: unresolved=14
- PASS — **causal full_minus_neutral mean**: source=1.921185, main=1.9212
- PASS — **causal full_minus_neutral CI**: source=[1.405732,2.439930], main=[1.4057,2.4399]
- PASS — **causal full_minus_neutral q**: source=0.00060, main=0.00060
- PASS — **causal full_minus_neutral support**: supported=True
- PASS — **causal full_minus_reduced mean**: source=1.023398, main=1.0234
- PASS — **causal full_minus_reduced CI**: source=[0.451405,1.597267], main=[0.4514,1.5973]
- PASS — **causal full_minus_reduced q**: source=0.00504, main=0.00504
- PASS — **causal full_minus_reduced support**: supported=True
- PASS — **causal native_minus_affinity_reassigned mean**: source=0.724592, main=0.7246
- PASS — **causal native_minus_affinity_reassigned CI**: source=[0.319521,1.184524], main=[0.3195,1.1845]
- PASS — **causal native_minus_affinity_reassigned q**: source=0.00225, main=0.00225
- PASS — **causal native_minus_affinity_reassigned support**: supported=True
- PASS — **causal native_minus_topology_mismatch mean**: source=0.341512, main=0.3415
- PASS — **causal native_minus_topology_mismatch CI**: source=[0.044105,0.658990], main=[0.0441,0.659]
- PASS — **causal native_minus_topology_mismatch q**: source=0.05010, main=0.05010
- PASS — **causal native_minus_topology_mismatch support**: supported=False
- PASS — **causal alternative_native_minus_cross mean**: source=0.813832, main=0.8138
- PASS — **causal alternative_native_minus_cross CI**: source=[0.515954,1.112170], main=[0.516,1.1122]
- PASS — **causal alternative_native_minus_cross q**: source=0.00090, main=0.00090
- PASS — **causal alternative_native_minus_cross support**: supported=True
- PASS — **causal stable_minus_unstable mean**: source=0.896173, main=0.8962
- PASS — **causal stable_minus_unstable CI**: source=[0.466481,1.289110], main=[0.4665,1.2891]
- PASS — **causal stable_minus_unstable q**: source=0.00225, main=0.00225
- PASS — **causal stable_minus_unstable support**: supported=True
- PASS — **causal 5/6 supported**: supported=5/6
- PASS — **landscape B2_default mean**: source=2.372421, main=2.3724
- PASS — **landscape B2_default CI**: source=[2.175012,2.560271], main=[2.175,2.5603]
- PASS — **landscape B2_default counts**: positive=8/8, practical=8/8
- PASS — **landscape B2_reward3 mean**: source=3.243945, main=3.2439
- PASS — **landscape B2_reward3 CI**: source=[2.923690,3.615868], main=[2.9237,3.6159]
- PASS — **landscape B2_reward3 counts**: positive=8/8, practical=8/8
- PASS — **landscape B2_stride7 mean**: source=1.549566, main=1.5496
- PASS — **landscape B2_stride7 CI**: source=[1.481238,1.622904], main=[1.4812,1.6229]
- PASS — **landscape B2_stride7 counts**: positive=8/8, practical=8/8
- PASS — **landscape A_p2_a3 mean**: source=0.224930, main=0.2249
- PASS — **landscape A_p2_a3 CI**: source=[0.081010,0.392865], main=[0.081,0.3929]
- PASS — **landscape A_p2_a3 counts**: positive=7/8, practical=3/8
- PASS — **landscape intermediate sign p**: p=0.03125
- PASS — **screen A class counts**: counts={'Viability-relevant': 10, 'Syntactic-only': 10, 'Null': 8, 'Strong-adaptation': 4}
- PASS — **screen B1 class counts**: counts={'Syntactic-only': 11, 'Null': 2, 'Boundary/uncertain': 1, 'Viability-relevant': 1, 'Strong-adaptation': 1}
- PASS — **screen B2 class counts**: counts={'Strong-adaptation': 15, 'Syntactic-only': 1, 'Viability-relevant': 1}
- PASS — **fraction normalized info**: 0.252 [0.240, 0.261]
- PASS — **fraction normalized delta**: 0.038 [0.027, 0.051]
- PASS — **fraction normalized class**: class=Syntactic-only
- PASS — **StageD A_p2_a3 delta**: source=0.484523 [0.460118,0.512749]
- PASS — **StageD A_p2_a3 8/8 positive**: positive=8/8
- PASS — **StageD A_p2_a3 median rho**: source=0.693048, main=0.693
- PASS — **StageD A_p2_a3 identity**: identity exact
- PASS — **StageD B2_reward3 delta**: source=3.502141 [2.721882,4.642223]
- PASS — **StageD B2_reward3 8/8 positive**: positive=8/8
- PASS — **StageD B2_reward3 median rho**: source=0.920856, main=0.921
- PASS — **StageD B2_reward3 identity**: identity exact
- PASS — **StageD B2_stride7 delta**: source=1.643618 [1.259788,1.980839]
- PASS — **StageD B2_stride7 8/8 positive**: positive=8/8
- PASS — **StageD B2_stride7 median rho**: source=0.934795, main=0.935
- PASS — **StageD B2_stride7 identity**: identity exact
- PASS — **StageD all 24 rho positive**: positive rho=24/24
- PASS — **MP expected one-site marginal numerical precision**: max mean TV=5.059e-14
- PASS — **realized pooled MP TV below native split-half**: max pooled TV=0.001164, split-half=0.001552
- PASS — **identity realized TV exact zero**: identity TV=0


## First-99% diagnostic reconciliation

The source record `core_p1_first_target_summary.csv` contains 20 populations: all 20 reached the mean-frontier 99% target; 6 are classified `technically_resolved_nonidentity` and 14 are classified `technically_unresolved`. Identity is first in 2/20 populations, and both identity-first cases belong to the technically-unresolved group. Thus the counts are consistent and nonexclusive in the intended way.

A stale line under a `Failures` heading in the earlier working audit incorrectly printed `resolved nonidentity=4`; that line was an audit-reporting artifact, not a discrepancy in the source data, Supplement, or main manuscript. The source CSV, Table S5, and main text all agree on 6 resolved nonidentity and 14 technically unresolved.
