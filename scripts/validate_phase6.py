import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results' / 'phase6_generality'
VAL = ROOT / 'validation' / 'phase6'
VAL.mkdir(parents=True, exist_ok=True)

checks = []
def check(name, passed, detail):
    checks.append({'check': name, 'passed': bool(passed), 'detail': str(detail)})

def verify_manifest(root: Path):
    manifest = pd.read_csv(root / 'FILE_MANIFEST_SHA256.csv')
    rows = []
    for r in manifest.itertuples(index=False):
        path = root / r.relative_path
        exists = path.exists()
        size = path.stat().st_size if exists else -1
        sha = hashlib.sha256(path.read_bytes()).hexdigest() if exists else ''
        rows.append({'relative_path': r.relative_path, 'exists': exists,
                     'size_matches': exists and size == int(r.size_bytes),
                     'hash_matches': exists and sha == r.sha256})
    return pd.DataFrame(rows)

settings = json.loads((OUT / 'phase6_settings.json').read_text())
a_design = pd.read_csv(OUT / 'stage_a_design.csv')
b1_design = pd.read_csv(OUT / 'stage_b1_design.csv')
b2_design = pd.read_csv(OUT / 'stage_b2_design.csv')
a = pd.read_csv(OUT / 'stage_a_replicates.csv')
b1 = pd.read_csv(OUT / 'stage_b1_replicates.csv')
b2 = pd.read_csv(OUT / 'stage_b2_replicates.csv')
c_design = pd.read_csv(OUT / 'stage_c_design.csv')
c = pd.read_csv(OUT / 'stage_c_replicates.csv')
summary = pd.read_csv(OUT / 'stage_ab_summary.csv')
selected = pd.read_csv(OUT / 'stage_d_selected.csv')
draw = pd.read_csv(OUT / 'stage_d_continuations.csv')
drep = pd.read_csv(OUT / 'stage_d_replicate_summary.csv')
dsum = pd.read_csv(OUT / 'stage_d_summary.csv')
gate = json.loads((OUT / 'GATE_7_DECISION.json').read_text())

check('stage_a_design_count', len(a_design) == 32, len(a_design))
check('stage_a_replicate_count', len(a) == 128 and a.groupby('design_id').size().eq(4).all(), len(a))
check('stage_b1_design_count', len(b1_design) == 16, len(b1_design))
check('stage_b1_replicate_count', len(b1) == 48 and b1.groupby('design_id').size().eq(3).all(), len(b1))
check('stage_b2_design_count', len(b2_design) == 17, len(b2_design))
check('stage_b2_replicate_count', len(b2) == 68 and b2.groupby('design_id').size().eq(4).all(), len(b2))
check('stage_c_design_count', len(c_design) == 12, len(c_design))
check('stage_c_replicate_count', len(c) == 48 and c.groupby('design_id').size().eq(4).all(), len(c))
check('screen_identity_exact', bool(pd.concat([a,b1,b2,c]).identity_exact.all()), int(pd.concat([a,b1,b2,c]).identity_exact.sum()))
check('stage_d_selection_count', len(selected) == 4 and selected.design_id.eq('B2_default').sum() == 1, selected.design_id.tolist())
check('stage_d_nondefault_replicates', len(drep) == 24 and drep.groupby('confirm_id').size().eq(8).all(), len(drep))
check('stage_d_continuation_rows', len(draw) == 1680, len(draw))
check('stage_d_two_continuations_per_map', draw.groupby(['baseline_replicate','map_hash']).size().eq(settings['continuations']).all(), draw.groupby(['baseline_replicate','map_hash']).size().value_counts().to_dict())
check('stage_d_identity_information', drep.identity_information_recovered.all(), int(drep.identity_information_recovered.sum()))
check('stage_d_identity_viability', drep.identity_viability_recovered.all(), int(drep.identity_viability_recovered.sum()))
check('stage_d_censoring_explicit', set(drep.censoring.dropna().unique()) <= {'none','right'}, drep.censoring.value_counts(dropna=False).to_dict())
check('stage_d_two_nondefault_positive', int(dsum.positive.sum()) == 2, dsum[['design_id','positive']].to_dict('records'))

positive = {'R2_viability_relevant','R3_strong_adaptation'}
fa = float(summary[summary.stage.eq('A')].regime.isin(positive).mean())
fb = float(summary[summary.stage.eq('B1')].regime.isin(positive).mean())
b2s = summary[summary.stage.eq('B2')]
fam = {f: bool(((b2s.family == f) & b2s.regime.isin(positive)).any()) for f in ['window','position','metabolite','fitness']}
check('gate_stage_a_fraction_recomputes', abs(fa - gate['stage_a_positive_fraction']) < 1e-12, fa)
check('gate_stage_b1_fraction_recomputes', abs(fb - gate['stage_b1_positive_fraction']) < 1e-12, fb)
check('gate_structural_families_recompute', fam == gate['structural_family_support'], fam)
check('gate7_broad_pass', gate['status'] == 'PASSED' and gate['generality_decision'] == 'BROAD_GENERALITY_SUPPORTED' and gate['broad'], gate)

p4 = verify_manifest(ROOT / 'results' / 'phase4_core')
p5 = verify_manifest(ROOT / 'results' / 'phase5_causal_specificity')
p6 = verify_manifest(ROOT / 'results' / 'phase6_generality')
p4.to_csv(VAL / 'phase4_archive_verification.csv', index=False)
p5.to_csv(VAL / 'phase5_archive_verification.csv', index=False)
p6.to_csv(VAL / 'phase6_result_verification.csv', index=False)
check('phase4_archive_integrity', p4[['exists','size_matches','hash_matches']].all().all(), f"{p4.hash_matches.sum()}/{len(p4)}")
check('phase5_archive_integrity', p5[['exists','size_matches','hash_matches']].all().all(), f"{p5.hash_matches.sum()}/{len(p5)}")
check('phase6_result_integrity', p6[['exists','size_matches','hash_matches']].all().all(), f"{p6.hash_matches.sum()}/{len(p6)}")

pd.DataFrame(checks).to_csv(VAL / 'structural_checks.csv', index=False)
result = {'n_checks': len(checks), 'n_passed': int(sum(x['passed'] for x in checks)), 'all_passed': bool(all(x['passed'] for x in checks))}
(VAL / 'validation_summary.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
if not result['all_passed']:
    raise SystemExit(1)
