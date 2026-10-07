from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/"round2_mp"/"source_tables"

compact=pd.read_csv(D/"Table_S2_screening_compact_reader_record.csv")
full=pd.read_csv(D/"Table_S2_screening_full_reader_record.csv")
assert len(compact)==65
assert len(full)==65
assert compact["index"].tolist()==list(range(1,66))
assert full["index"].tolist()==list(range(1,66))
assert compact["stage"].value_counts().to_dict()=={"A":32,"B1":16,"B2":17}
assert full["stage"].value_counts().to_dict()=={"A":32,"B1":16,"B2":17}
assert compact["class"].value_counts().to_dict()==full["class"].value_counts().to_dict()

s=pd.read_csv(D/"empirical_marginal_summary.csv")
assert len(s)==7
assert set(s["n_populations"])=={20}
assert set(s["n_streams_per_population"])=={64}
identity=s[s.map_id=="m033_identity"].iloc[0]
assert identity.mean_pooled_64_tv==0
assert identity.mean_single_stream_tv==0
assert abs(s["mean_native_split_half_tv"].mean()-0.0015523856026785738)<1e-15
non=s[s.map_id!="m033_identity"]
assert non["mean_pooled_64_tv"].max()<s["mean_native_split_half_tv"].min()
assert non["max_ratio_to_native_split_half"].max()<1

d=pd.read_csv(D/"R2_SUPPLEMENT_EMPIRICAL_MARGINAL_DIAGNOSTIC_TABLE.csv")
assert len(d)==7
mp=d[d.condition!="MP identity"]
assert mp["analytical_expected_PZ_given_S_TV"].max()<1e-12
assert mp["realized_max_pooled_TV_across_20_baselines"].max()<mp["native_split_half_sampling_reference"].min()
ident=d[d.condition=="MP identity"].iloc[0]
assert ident.realized_mean_pooled_64_stream_TV==0
assert ident.realized_max_pooled_TV_across_20_baselines==0
assert ident.mean_single_stream_TV==0

source_map=(ROOT/"round2_mp"/"provenance"/"FINAL_SOURCE_TABLE_MAP.md").read_text()
for name in [
 "Table_S2_screening_compact_reader_record.csv",
 "Table_S2_screening_full_reader_record.csv",
 "stage_ab_summary_n8_mp.csv",
 "landscape_inference.csv",
 "mp_marginal_diagnostics_summary.csv",
 "empirical_marginal_summary.csv",
 "R2_SUPPLEMENT_EMPIRICAL_MARGINAL_DIAGNOSTIC_TABLE.csv",
 "core_p1_first_target_summary.csv",
 "core_p1_map_summary.csv",
 "causal_specificity_contrasts_64new.csv",
 "causal_specificity_seed_blocks_64new.csv",
 "stage_c_summary_n8_mp.csv",
 "stage_d_confirmation_summary.csv",
 "stage_d_replicate_summary.csv",
 "stage_d_family_monotonicity.csv",
]:
    assert name in source_map

print("ROUND2_SUPPLEMENT_EVIDENCE_VALIDATION_PASS")
