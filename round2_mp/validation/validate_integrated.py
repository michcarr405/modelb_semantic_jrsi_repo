"""Recompute release evidence checks and compare every current source table."""
from __future__ import annotations
import ast, csv, hashlib, inspect, json, platform, sys
from pathlib import Path
import importlib.metadata
import numpy as np
import pandas as pd

REPO=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(REPO),str(REPO/'src')]
R2=REPO/'round2_mp'; SRC=R2/'source_tables'; OUT=R2/'validation'
from modelb_semantic_repo import mp_operator
from modelb_semantic_repo.phase4 import array_sha256, load_map_panel
from modelb_semantic_repo.rng import _stable_entropy

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def compare(frozen,generated,keys):
    if not Path(generated).is_file():return dict(status='NOT_COMPLETED',rows=None)
    f=pd.read_csv(frozen,float_precision='round_trip');g=pd.read_csv(generated,float_precision='round_trip')
    if list(f.columns)!=list(g.columns) or len(f)!=len(g):
        return dict(status='FAIL',reason='columns or row count differ',frozen_rows=len(f),generated_rows=len(g))
    if keys:
        f=f.sort_values(keys).reset_index(drop=True);g=g.sort_values(keys).reset_index(drop=True)
    maxdiff=0.;bad=[];exact=True
    for col in f:
        if pd.api.types.is_numeric_dtype(f[col]) and not pd.api.types.is_bool_dtype(f[col]):
            a=f[col].to_numpy(float);b=g[col].to_numpy(float)
            d=np.abs(a-b);maxdiff=max(maxdiff,float(np.nanmax(d)) if np.any(~np.isnan(d)) else 0.)
            same=np.allclose(a,b,rtol=0,atol=1e-12,equal_nan=True)
            exact &= bool(np.array_equal(a,b,equal_nan=True))
        else:
            same=f[col].fillna('<NA>').equals(g[col].fillna('<NA>'))
            exact &= same
        if not same:bad.append(col)
    return dict(status='PASS' if not bad else 'FAIL',rows=len(f),max_abs_numeric_difference=maxdiff,
                all_cells_exact=bool(exact),byte_identical=sha(frozen)==sha(generated),mismatch_columns=bad,
                frozen_sha256=sha(frozen),generated_sha256=sha(generated))

def regenerate_reader_projections():
    """Retain frozen display labels; rebuild numerical columns from fresh tables."""
    base=REPO/'round2/mp_migration/results';dest=R2/'regenerated/reader_records';dest.mkdir(parents=True,exist_ok=True)
    cp=base/'core/core_mp_replicates.csv'
    if cp.exists():
        full=pd.read_csv(cp,float_precision='round_trip').sort_values(['condition','inherit_prob','replicate']).reset_index(drop=True)
        frozen=pd.read_csv(SRC/'core_mp_replicates.csv',float_precision='round_trip').sort_values(['condition','inherit_prob','replicate']).reset_index(drop=True)
        missing_cells=0
        for column in ['actual_viability','mp_constant_viability']:
            missing=frozen[column].isna()
            assert (frozen.loc[missing,'condition']=='control').all() and (frozen.loc[missing,'delta_mp']==0).all()
            missing_cells+=int(missing.sum())
            full.loc[missing,column]=np.nan
        full.to_csv(dest/'core_mp_replicates_archival_projection.csv',index=False)
        (dest/'CORE_ARCHIVAL_MISSINGNESS.json').write_text(json.dumps(dict(
            frozen_missing_control_viability_cells=missing_cells,
            convention='Preserve the exact frozen null/missingness footprint for archival table reproduction; complete fresh control levels remain in round2/mp_migration/results/core/core_mp_replicates.csv.',
            no_finite_frozen_value_replaced=True),indent=2))
    mappings=[('stage_c_summary_n8_mp.csv','stage_c_n8',
      ['Table_S6a_compact_reader_record.csv','Table_S7a_stageC_compact_reader_record.csv'],
      {'info_mean':'corrected_information_mean','info_low':'corrected_information_low','info_high':'corrected_information_high',
       'dv_mean':'delta_mp_mean','dv_low':'delta_mp_low','dv_high':'delta_mp_high',
       'df_mean':'adaptive_gain_mean','df_low':'adaptive_gain_low','df_high':'adaptive_gain_high','cls':'regime'}),
      ('stage_d_confirmation_summary.csv','stage_d_n8_mp_split',
       ['Table_S6b_compact_reader_record.csv','Table_S7b_stageD_compact_reader_record.csv'],
       {'dv_mean':'delta_mp_mean','dv_low':'delta_mp_low','dv_high':'delta_mp_high','median_rho':'median_within_population_spearman',
        'mean_rho':'mean_within_population_spearman','rho_low':'spearman_low','rho_high':'spearman_high','map_average_rho':'map_average_spearman',
        'positive_blocks':'positive_blocks','positive_rho_blocks':'positive_spearman_blocks','identity_exact':'identity_exact_all'})]
    for source,folder,names,cols in mappings:
        p=base/folder/source
        if not p.exists():continue
        raw=pd.read_csv(p,float_precision='round_trip')
        for n in names:
            template=pd.read_csv(SRC/n,float_precision='round_trip')
            assert len(raw)==len(template)
            if source=='stage_c_summary_n8_mp.csv':
                design_ids=[]
                for row in template.itertuples():
                    source_id='B2_default' if row.setting=='Default parameter setting' else 'B2_stride7'
                    kind='g' if row.coordinate.strip().startswith('Evolution duration') else 'h'
                    design_ids.append(f'C_{kind}{row.coordinate.strip().split()[-1]}_{source_id}')
                raw=raw.set_index('design_id').loc[design_ids].reset_index()
            for target,column in cols.items():template[target]=raw[column].to_numpy()
            template.to_csv(dest/n,index=False)
    p=base/'screen_n8/stage_ab_summary_n8_mp.csv'
    if p.exists():
        raw=pd.read_csv(p,float_precision='round_trip')
        names=['Table_S1_reader_record.csv','Table_S1_compact_reader_record.csv',
               'Table_S2_screening_full_reader_record.csv','Table_S2_screening_compact_reader_record.csv']
        cls={'R0_null':'Null','R1_syntactic_only':'Syntactic-only','R2_viability_relevant':'Viability-relevant',
             'R3_strong_adaptation':'Strong-adaptation','boundary_uncertain':'Boundary/uncertain'}
        for n in names:
            t=pd.read_csv(SRC/n,float_precision='round_trip');assert len(t)==len(raw)
            t['n']=raw['n'].to_numpy();t['stage']=raw.stage.to_numpy();t['class']=raw.regime.map(cls).to_numpy()
            for outcol,met in [('info','corrected_information'),('dv','delta_mp'),('df','adaptive_gain')]:
                def fmt(x):
                    result=f'{x:.3f}'
                    return '0.000' if result=='-0.000' else result
                sep=', ' if 'compact' in n else '--'
                t[outcol]=[f'{fmt(row[met+"_mean"])} [{fmt(row[met+"_low"])}{sep}{fmt(row[met+"_high"])}]' for _,row in raw.iterrows()]
            t.to_csv(dest/n,index=False)
    emp=R2/'cleanroom_outputs/empirical_marginal_validation/empirical_marginal_summary.csv'
    diag=R2/'cleanroom_outputs/mp_marginal_diagnostics_summary.csv'
    if emp.exists() and diag.exists():
        e=pd.read_csv(emp,float_precision='round_trip');d=pd.read_csv(diag,float_precision='round_trip').set_index('condition')
        t=pd.read_csv(SRC/'R2_SUPPLEMENT_EMPIRICAL_MARGINAL_DIAGNOSTIC_TABLE.csv',float_precision='round_trip')
        t['analytical_expected_PZ_given_S_TV']=[d.loc[mid,'mean_segment_tv'] for mid in e.map_id]
        for dst,col in [('realized_mean_pooled_64_stream_TV','mean_pooled_64_tv'),('realized_max_pooled_TV_across_20_baselines','max_pooled_64_tv'),
                        ('mean_single_stream_TV','mean_single_stream_tv'),('native_split_half_sampling_reference','mean_native_split_half_tv')]:
            t[dst]=e[col].to_numpy()
        t.to_csv(dest/'R2_SUPPLEMENT_EMPIRICAL_MARGINAL_DIAGNOSTIC_TABLE.csv',index=False)

def main():
    checks=[]
    def add(name,ok,detail=''):checks.append(dict(check=name,pass_check=bool(ok),detail=detail))
    checks_file=R2/'drivers_and_seed_ledger/seed_ledger/MP_SEED_LEDGER.csv'
    ledger=pd.read_csv(checks_file).fillna('')
    ledgerbad=[]
    for row in ledger.itertuples():
        if row.seed_sequence_entropy_json and row.root_seed!='' and row.purpose:
            got=[int(row.root_seed)&0xffffffff,*_stable_entropy(row.purpose,*json.loads(row.keys_json))]
            if got!=json.loads(row.seed_sequence_entropy_json):ledgerbad.append(row.record_id)
    add('recovered_rng_ledger_entropy_specs',not ledgerbad,f'{len(ledger)} ledger rows; {len(ledgerbad)} entropy mismatches')
    exports=['simulate_core_actual','simulate_core_grouped','simulate_phase6_grouped','simulate_core_constant','simulate_phase6_constant','expected_marginal_error_general']
    for fn in exports:add('api_'+fn,callable(getattr(mp_operator,fn,None)),str(inspect.signature(getattr(mp_operator,fn))))
    for file in (REPO/'round2/mp_migration').glob('*.py'):
        old=R2/'recovered_scientific_freeze/code'/file.name
        add('archived_driver_unmodified_'+file.name,old.exists() and sha(file)==sha(old))
    raw=R2/'causal_specificity_high_continuation/results/continuation_level_results_64new.csv'
    add('causal_raw_frozen_hash',sha(raw)=='94c01d71029606db905f9a859ae238d83b591942af9c619fa30be23f2b996df7')
    c=pd.read_csv(raw);counts=c.groupby(['condition','realization','seed_block','baseline_replicate']).size()
    add('causal_240_realizations_x64_new_streams',len(c)==15360 and len(counts)==240 and (counts==64).all() and sorted(c.continuation_index.unique())==list(range(2,66)))
    add('causal_20_inferential_seed_blocks',c.seed_block.nunique()==20)
    maps=load_map_panel(REPO/'results/phase4_core/maps');coords=pd.read_csv(SRC/'core_p1_corrected_coordinates.csv')
    lookup={x['map_id']:x for x in maps}
    for col in ['map_hash','method','endpoint_type','actual_groups']:
        add('map_panel_'+col,all(str(getattr(row,col))==str(lookup[row.map_id][col]) for row in coords.itertuples()))
    add('680_coordinates_34_maps_20_populations',len(coords)==680 and coords.map_id.nunique()==34 and coords.baseline_replicate.nunique()==20)
    add('constant_information_zero',coords.query("endpoint_type=='constant'").corrected_retained_information.abs().max()<1e-12)
    core=pd.read_csv(SRC/'core_mp_replicates.csv');ids=coords.query("endpoint_type=='identity'").merge(core.query("condition=='selective' and inherit_prob==1"),on='baseline_replicate')
    add('identity_information_matches_20_baselines',len(ids)==20 and np.allclose(ids.corrected_retained_information,ids.corrected_conditional_information,atol=1e-12,rtol=0))
    fr=pd.read_csv(SRC/'core_p1_first_target_summary.csv')
    add('first99_frozen_counts',len(fr)==20 and fr.target_reached.all() and fr.identity_required_by_mean_frontier.sum()==2 and (fr.technical_precision_class=='technically_resolved_nonidentity').sum()==6 and (fr.technical_precision_class=='technically_unresolved').sum()==14)
    inf=pd.read_csv(SRC/'causal_specificity_contrasts_64new.csv');add('five_of_six_frozen_contrasts',len(inf)==6 and inf.contrast_passed.sum()==5 and not bool(inf.loc[inf.contrast=='native_minus_topology_mismatch','contrast_passed'].iloc[0]))
    hv=pd.read_csv(OUT/'affinity_matrix_hash_verification.csv');add('eight_affinity_matrices_exact_hashes',len(hv)==8 and hv.canonical_matches_expected.all())
    regenerate_reader_projections()
    base=REPO/'round2/mp_migration/results'
    pairs={
      'core_mp_replicates.csv':(R2/'regenerated/reader_records/core_mp_replicates_archival_projection.csv',['condition','inherit_prob','replicate'],'FULL_PRODUCTION_WITH_EXPLICIT_ARCHIVAL_MISSINGNESS_MASK'),
      'core_mp_inference.csv':(base/'core/core_mp_inference.csv',['inherit_prob'],'ARCHIVED_R1_STATES_TO_FULL_R2_PRODUCTION'),
      'stage_ab_summary_n8_mp.csv':(base/'screen_n8/stage_ab_summary_n8_mp.csv',['design_id'],'INITIAL_SEEDS_TO_FULL_PRODUCTION'),
      'regime_counts_n8_mp.csv':(base/'screen_n8/regime_counts_n8_mp.csv',['stage'],'INITIAL_SEEDS_TO_FULL_PRODUCTION'),
      'stage_c_summary_n8_mp.csv':(base/'stage_c_n8/stage_c_summary_n8_mp.csv',['design_id'],'INITIAL_SEEDS_TO_FULL_PRODUCTION'),
      'stage_d_confirmation_summary.csv':(base/'stage_d_n8_mp_split/stage_d_confirmation_summary.csv',['confirm_id'],'INITIAL_SEEDS_TO_FULL_PRODUCTION'),
      'stage_d_replicate_summary.csv':(base/'stage_d_n8_mp_split/stage_d_replicate_summary.csv',['confirm_id','replicate'],'INITIAL_SEEDS_TO_FULL_PRODUCTION'),
      'stage_d_family_monotonicity.csv':(base/'stage_d_n8_mp_split/stage_d_family_monotonicity.csv',['confirm_id','method'],'INITIAL_SEEDS_TO_FULL_PRODUCTION'),
      'population_level.csv':(base/'affinity_landscape_generality/population_level.csv',['landscape','design_id','replicate'],'INITIAL_SEEDS_TO_FULL_PRODUCTION'),
      'landscape_level.csv':(base/'affinity_landscape_generality/landscape_level.csv',['landscape','design_id'],'INITIAL_SEEDS_TO_FULL_PRODUCTION'),
      'landscape_inference.csv':(base/'affinity_landscape_generality/landscape_inference.csv',['design_id'],'INITIAL_SEEDS_TO_FULL_PRODUCTION'),
      'causal_specificity_contrasts_64new.csv':(R2/'regenerated/causal_specificity/mp_operator_contrasts_64new.csv',['contrast'],'ARCHIVED_R1_STATES_TO_FULL_R2_PRODUCTION'),
      'causal_specificity_seed_blocks_64new.csv':(R2/'regenerated/causal_specificity/mp_operator_seed_block_metrics_64new.csv',['seed_block'],'ARCHIVED_R1_STATES_TO_FULL_R2_PRODUCTION'),
      'core_p1_corrected_coordinates.csv':(base/'core_p1_frontier_64/corrected_coordinates_p1.csv',['baseline_replicate','map_id'],'ARCHIVED_R1_STATES_TO_FULL_R2_PRODUCTION'),
      'core_p1_first_target_summary.csv':(base/'core_p1_frontier_64/first_target_summary.csv',['baseline_replicate'],'ARCHIVED_R1_STATES_TO_FULL_R2_PRODUCTION'),
      'core_p1_frontier_points.csv':(base/'core_p1_frontier_64/frontier_points.csv',['baseline_replicate','corrected_retained_information'],'ARCHIVED_R1_STATES_TO_FULL_R2_PRODUCTION'),
      'core_p1_map_summary.csv':(base/'core_p1_frontier_64/map_summary.csv',['baseline_replicate','map_id'],'ARCHIVED_R1_STATES_TO_FULL_R2_PRODUCTION'),
      'mp_marginal_diagnostics_replicates.csv':(R2/'cleanroom_outputs/mp_marginal_diagnostics_replicates.csv',['replicate','condition'],'ARCHIVED_R1_STATES_TO_DIAGNOSTICS'),
      'mp_marginal_diagnostics_summary.csv':(R2/'cleanroom_outputs/mp_marginal_diagnostics_summary.csv',['condition'],'ARCHIVED_R1_STATES_TO_DIAGNOSTICS'),
      'empirical_marginal_summary.csv':(R2/'cleanroom_outputs/empirical_marginal_validation/empirical_marginal_summary.csv',['map_id'],'ARCHIVED_R1_STATES_TO_DIAGNOSTICS'),
    }
    matrix=[]
    for p in sorted(SRC.glob('*.csv')):
        gen,keys,route=pairs.get(p.name,(R2/'regenerated/reader_records'/p.name,[],'REGENERATED_NUMBERS_WITH_FROZEN_DISPLAY_LABELS'))
        cmp=compare(p,gen,keys)
        matrix.append(dict(file=p.name,route=route,generated_file=str(gen.relative_to(REPO)),**cmp))
    add('all_29_current_source_tables_regenerated',len(matrix)==29 and all(x['status']=='PASS' for x in matrix))
    states=R2/'regenerated/landscape_states';frozen=pd.read_csv(SRC/'population_level.csv');match=[]
    for row in frozen.itertuples():
        p=states/f'L{row.landscape:02d}_{row.design_id}_r{row.replicate:02d}.npz'
        match.append(p.exists() and array_sha256(np.load(p)['population'])==row.state_hash)
    add('256_landscape_baseline_state_hashes',len(match)==256 and all(match),f'{sum(match)}/256')
    eqfile=states/'INDEPENDENT_FINAL_STATE_EQUIVALENCE.json'
    eq=json.loads(eqfile.read_text()) if eqfile.exists() else {}
    add('independent_final_population_hash_equivalence',eq.get('exact_final_state_match',False) and eq.get('viability_exact',False),json.dumps(eq))
    hpfull=R2/'regenerated/causal_specificity/continuation_level_results_64new.csv'
    hpcompare=compare(raw,hpfull,['condition','seed_block','realization','continuation_index'])
    add('all_15360_new_causal_continuations',hpcompare['status']=='PASS',json.dumps(hpcompare))
    env={'python':platform.python_version(),'platform':platform.platform(),**{n:importlib.metadata.version(n) for n in ['numpy','scipy','pandas','numba','pytest']}}
    report=dict(candidate='jrsi-reproducibility-v2.0.0-rc4',all_passed=all(x['pass_check'] for x in checks),
                n_checks=len(checks),n_passed=sum(x['pass_check'] for x in checks),checks=checks,source_table_matrix=matrix,
                source_byte_identity_claim=False,environment=env,absolute_numeric_tolerance=1e-12,causal_raw_comparison=hpcompare,
                stage_d_caveat='Newly generated final continuation hashes are retained. Original Stage-D final continuation hashes were not available for a direct historical comparison.',
                clean_install_scope='Fresh isolated venv; package installation and dependencies succeeded. R1 baseline states and historical nonintervention measurements were immutable inputs, not all regenerated from initial seeds.')
    (OUT/'INTEGRATED_REGENERATION_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    fields=['file','route','status','rows','max_abs_numeric_difference','all_cells_exact','byte_identical','generated_file','frozen_sha256','generated_sha256','mismatch_columns']
    with (OUT/'FULL_REGENERATION_STATUS.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(matrix)
    print(json.dumps({'n_checks':len(checks),'n_passed':report['n_passed'],'source_tables':[(x['file'],x['status'],x.get('max_abs_numeric_difference')) for x in matrix],'environment':env},indent=2))
    return 0 if report['all_passed'] else 1

if __name__=='__main__':sys.exit(main())
