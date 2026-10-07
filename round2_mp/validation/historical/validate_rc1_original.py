from pathlib import Path
import csv, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[2]
R2=ROOT/'round2_mp'
fail=[]; checks=[]
def add(name, ok, detail=''):
    checks.append({'check':name,'pass':bool(ok),'detail':detail})
    if not ok: fail.append(name)
# original MP hashes
vf=R2/'provenance'/'MP_ORIGINAL_HASH_VERIFICATION.csv'
rows=list(csv.DictReader(vf.open()))
add('original_mp_hashes_24_of_24', len(rows)==24 and all(r['status']=='PASS' for r in rows), f"n={len(rows)}")
# current publication surface
pub=list((R2/'publication').rglob('*'))
old=[p.name for p in pub if p.is_file() and any(f'Figure_S{i}' in p.name for i in (7,8,9))]
add('no_current_s7_s9_publication_files', not old, ','.join(old))
for f in ['JRSI_R2_MAIN_NOTATION_CLOSED_2026-10-06.pdf','JRSI_R2_SUPPLEMENT_NOTATION_CLOSED_2026-10-06.pdf']:
    p=next((x for x in (R2/'publication').rglob(f)),None)
    add(f'present_{f}', p is not None and p.stat().st_size>0)
# exact deterministic diagnostic regeneration
pairs=[
 ('mp_marginal_diagnostics_replicates.csv',R2/'cleanroom_outputs'/'mp_marginal_diagnostics_replicates.csv'),
 ('mp_marginal_diagnostics_summary.csv',R2/'cleanroom_outputs'/'mp_marginal_diagnostics_summary.csv'),
 ('empirical_marginal_summary.csv',R2/'cleanroom_outputs'/'empirical_marginal_validation'/'empirical_marginal_summary.csv'),
]
for name, regen in pairs:
    frozen=R2/'source_tables'/name
    ok=regen.exists() and frozen.exists() and hashlib.sha256(regen.read_bytes()).digest()==hashlib.sha256(frozen.read_bytes()).digest()
    add(f'exact_regeneration_{name}',ok)
# empirical validation identity
val=json.loads((R2/'cleanroom_outputs'/'empirical_marginal_validation'/'VALIDATION.json').read_text())
add('empirical_identity_pooled_tv_zero',val.get('identity_pooled_tv_exact_zero') is True)
add('empirical_identity_single_stream_tv_zero',val.get('identity_single_stream_tv_exact_zero') is True)
add('empirical_mp_below_native_split_reference',float(val['max_nonidentity_mean_pooled_tv']) < float(val['mean_native_split_half_tv']),f"{val['max_nonidentity_mean_pooled_tv']} < {val['mean_native_split_half_tv']}")
# final audits
for f in ['FINAL_INTEGRATED_MAIN_SUPPLEMENT_FREEZE_AUDIT.md','FINAL_NUMERICAL_SYNC_AUDIT_75_OF_75.md','FINAL_REVIEWER_NOTATION_VALUE_AUDIT.md']:
    add(f'present_{f}',(R2/'publication'/'qc'/f).exists())
report={'candidate':'jrsi-reproducibility-v2.0.0-rc1','n_checks':len(checks),'n_passed':sum(c['pass'] for c in checks),'all_passed':not fail,'checks':checks,'known_release_gate':'MP production driver for every MP-primary source table remains unlocated; this validator does not claim full production regeneration.'}
(R2/'validation'/'RC1_PACKAGED_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
sys.exit(0 if not fail else 1)
