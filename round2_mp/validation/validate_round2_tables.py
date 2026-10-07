from pathlib import Path
import math
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"source_tables"

def close(a,b,tol=1e-6):
    return math.isclose(float(a),float(b),rel_tol=0,abs_tol=tol)

core=pd.read_csv(D/"core_mp_inference.csv")
assert len(core)==10
assert set(core["n"])=={20}
assert (core["positive_blocks"]==20).all()
assert close(core.loc[core.inherit_prob.eq(0.1),"mean_delta_mp"].iloc[0],0.10179877387152755,1e-12)
assert close(core.loc[core.inherit_prob.eq(0.9),"mean_delta_mp"].iloc[0],0.7235206434461812,1e-12)
assert close(core.loc[core.inherit_prob.eq(1.0),"mean_delta_mp"].iloc[0],2.2481462944878468,1e-12)

ft=pd.read_csv(D/"core_p1_first_target_summary.csv")
assert len(ft)==20 and bool(ft["target_reached"].all())
assert int(ft["identity_required_by_mean_frontier"].sum())==2
vc=ft["technical_precision_class"].value_counts().to_dict()
assert vc.get("technically_unresolved",0)==14
assert vc.get("technically_resolved_nonidentity",0)==6

cs=pd.read_csv(D/"causal_specificity_contrasts_64new.csv")
assert len(cs)==6
assert int(cs["contrast_passed"].sum())==5
row=cs.set_index("contrast")
assert not bool(row.loc["native_minus_topology_mismatch","contrast_passed"])
assert close(row.loc["full_minus_neutral","mean_difference"],1.921185,1e-6)
assert close(row.loc["alternative_native_minus_cross","mean_difference"],0.813832,1e-6)

ab=pd.read_csv(D/"stage_ab_summary_n8_mp.csv")
assert len(ab)==65 and set(ab["n"])=={8}
expected={
 ("A","R0_null"):8,("A","R1_syntactic_only"):10,("A","R2_viability_relevant"):10,("A","R3_strong_adaptation"):4,
 ("B1","R0_null"):2,("B1","R1_syntactic_only"):11,("B1","boundary_uncertain"):1,("B1","R2_viability_relevant"):1,("B1","R3_strong_adaptation"):1,
 ("B2","R1_syntactic_only"):1,("B2","R2_viability_relevant"):1,("B2","R3_strong_adaptation"):15,
}
assert ab.groupby(["stage","regime"]).size().to_dict()==expected

c=pd.read_csv(D/"stage_c_summary_n8_mp.csv")
assert len(c)==12 and set(c["n"])=={8}
assert c["source_design_id"].value_counts().to_dict()=={"B2_default":6,"B2_stride7":6}

d=pd.read_csv(D/"stage_d_confirmation_summary.csv").set_index("confirm_id")
assert set(d.index)=={"D0","D1","D2"} and set(d["n"])=={8}
assert (d["positive_blocks"]==8).all()
assert (d["positive_spearman_blocks"]==8).all()
assert bool(d["identity_exact_all"].all())
assert close(d.loc["D0","delta_mp_mean"],0.484523,1e-6)
assert close(d.loc["D1","delta_mp_mean"],3.502141,1e-6)
assert close(d.loc["D2","delta_mp_mean"],1.643618,1e-6)

li=pd.read_csv(D/"landscape_inference.csv").set_index("design_id")
assert set(li["n_landscapes"])=={8}
assert int(li.loc["A_p2_a3","positive_landscapes"])==7
for k in ["B2_default","B2_reward3","B2_stride7"]:
    assert int(li.loc[k,"positive_landscapes"])==8
    assert close(li.loc[k,"exact_sign_p"],0.0078125,1e-12)
assert close(li.loc["A_p2_a3","exact_sign_p"],0.03125,1e-12)

md=pd.read_csv(D/"mp_marginal_diagnostics_summary.csv").set_index("condition")
assert close(md.loc["native","mean_segment_tv"],0.0,1e-15)
assert md.loc["m000_constant","mean_segment_tv"] < 1e-12
assert md.loc["m004_balanced_random_group","mean_segment_tv"] < 1e-12
assert md.loc["m015_affinity_rank_group","mean_segment_tv"] < 1e-12
assert close(md.loc["submitted_constant","mean_segment_tv"],0.1165518,1e-6)
assert close(md.loc["m000_constant","mean_adjacency_tv"],0.014324,1e-6)

print("ROUND2_TABLE_VALIDATION_PASS")
