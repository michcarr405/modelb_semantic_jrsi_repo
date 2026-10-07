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
# Repository content policy: publication prose/assets are outside this package.
tex=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*.tex') if p.is_file()]
add('no_packaged_tex_files', not tex, ','.join(tex))
figure_root=R2/'figures'
pdfs=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*.pdf') if p.is_file() and not p.is_relative_to(figure_root)]
add('no_manuscript_or_supplement_document_pdfs',not pdfs,','.join(pdfs))
figure_records=json.loads((figure_root/'FIGURE_PROVENANCE.json').read_text())['figures']
add('all_14_current_figures_match_archived_hashes',len(figure_records)==14 and all(hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in figure_records))
archives=list(ROOT.rglob('*.zip'))
add('no_embedded_publication_archives', not archives, ','.join(str(p.relative_to(ROOT)) for p in archives))
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
# Scientific evidence is retained independently of paper assets.
val=json.loads((R2/'validation'/'INTEGRATED_REGENERATION_VALIDATION.json').read_text())
add('integrated_evidence_passed',val.get('all_passed') is True)
val=json.loads((R2/'validation'/'RC4_SCIENTIFIC_ASSET_COMPARISON.json').read_text())
add('scientific_assets_unchanged_from_rc3',val.get('all_unchanged') is True, f"n={val.get('n_assets')}")
figure_validation=json.loads((R2/'validation'/'FIGURE_BUILD_VALIDATION.json').read_text())
add('portable_figure_build_12_regenerated_2_archived',figure_validation.get('all_passed') is True and figure_validation.get('regenerated_figures')==12 and figure_validation.get('archived_diagram_copies')==2)
report={'candidate':'jrsi-reproducibility-v2.0.0-rc7','n_checks':len(checks),'n_passed':sum(c['pass'] for c in checks),'all_passed':not fail,'checks':checks,'known_release_gate':'Code-and-data packaging checks only; complete regeneration is documented in INTEGRATED_REGENERATION_VALIDATION.json.'}
(R2/'validation'/'RC7_PACKAGED_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
sys.exit(0 if not fail else 1)
