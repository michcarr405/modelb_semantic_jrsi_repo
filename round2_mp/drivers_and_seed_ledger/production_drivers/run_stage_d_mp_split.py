from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from modelb_semantic_repo import phase6
from modelb_semantic_repo.phase4 import array_sha256
from modelb_semantic_repo.rng import ContinuationStream,PermutationStream,make_generator
from modelb_semantic_repo.mp_operator import simulate_phase6_grouped,expected_marginal_error_general

SEL=ROOT/'round2/mp_migration/results/stage_c_n8/stage_d_selected_final_mp.csv';OUT=ROOT/'round2/mp_migration/results/stage_d_n8_mp_split';CONT_ROOT=2026100208;INFO_ROOT=2026073106;NCONT=16;H=36;NPERM=200

def sels(): return pd.read_csv(SEL).query("design_id != 'B2_default'").to_dict('records')
def getrow(cid): return next(r for r in sels() if r['confirm_id']==cid)
def prep(cid,rep):
 r=getrow(cid);spec=json.loads(r['spec_json']);seed=phase6.stable_integer_seed(phase6.ROOT,'p6-confirm',cid,rep);m,pop,tr=phase6.baseline(spec,seed);f,mot,z,s=phase6.observe(pop,m,make_generator(phase6.ROOT,'p6-cinfo',cid,rep));bid=f'{cid}_r{rep:02d}';pan=phase6.panel(m,phase6.ROOT,cid);rows=[]
 for it in pan:
  gm=np.asarray(it['labels'],np.int64)[mot];obs,null,corr=phase6.corrected(gm,z,s,NPERM,PermutationStream(INFO_ROOT,bid,0));rows.append(dict(map_id=it['map_id'],map_hash=it['map_hash'],method=it['method'],endpoint_type=it['endpoint_type'],actual_groups=int(it['actual_groups']),observed_retained_information=obs,permutation_mean=null,corrected_retained_information=corr))
 d=OUT/'prepared'/bid;d.mkdir(parents=True,exist_ok=True);np.save(d/'population.npy',pop);pd.DataFrame(rows).to_csv(d/'coords.csv',index=False);meta=dict(confirm_id=cid,design_id=r['design_id'],replicate=rep,baseline_replicate=bid,baseline_seed=seed,spec_json=json.dumps(spec,sort_keys=True),state_hash=array_sha256(pop),trajectory_hash=array_sha256(tr),baseline_corrected_information=float(pd.DataFrame(rows).query("endpoint_type=='identity'").corrected_retained_information.iloc[0]),max_mp_marginal_abs_error=float(expected_marginal_error_general(pop,m,next(it['labels'] for it in pan if it['endpoint_type']=='constant'))),n_continuations=NCONT,horizon=H);(d/'meta.json').write_text(json.dumps(meta,indent=2))
def runmap(cid,rep,map_id):
 r=getrow(cid);bid=f'{cid}_r{rep:02d}';d=OUT/'prepared'/bid;spec=json.loads(r['spec_json']);m=phase6.model(spec);pop=np.load(d/'population.npy');pan=phase6.panel(m,phase6.ROOT,cid);it=next(x for x in pan if x['map_id']==map_id);coords=pd.read_csv(d/'coords.csv');coord=float(coords.loc[coords.map_id==map_id,'corrected_retained_information'].iloc[0]);rows=[]
 for ci in range(NCONT):
  if it['endpoint_type']=='identity': raise RuntimeError('identity generated from actual in finalize')
  v,fp=simulate_phase6_grouped(pop,m,it['labels'],H,CONT_ROOT,bid,ci,phase6.reproduce);rows.append(dict(confirm_id=cid,design_id=r['design_id'],replicate=rep,baseline_replicate=bid,continuation_index=ci,map_id=map_id,map_hash=it['map_hash'],method=it['method'],endpoint_type=it['endpoint_type'],actual_groups=int(it['actual_groups']),corrected_retained_information=coord,viability=float(v),final_population_hash=array_sha256(fp)))
 od=OUT/'map_blocks';od.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows).to_csv(od/f'{bid}_{map_id}.csv',index=False)
def runactual(cid,rep):
 r=getrow(cid);bid=f'{cid}_r{rep:02d}';d=OUT/'prepared'/bid;spec=json.loads(r['spec_json']);m=phase6.model(spec);pop=np.load(d/'population.npy');coord=json.loads((d/'meta.json').read_text())['baseline_corrected_information'];rows=[]
 for ci in range(NCONT):
  st=ContinuationStream(CONT_ROOT,bid,ci);curve,fp=phase6.horizon(pop,m,m['aff'],H,st);rows.append(dict(confirm_id=cid,design_id=r['design_id'],replicate=rep,baseline_replicate=bid,continuation_index=ci,map_id='actual',map_hash='actual',method='unintervened',endpoint_type='actual',actual_groups=len(m['aff']),corrected_retained_information=coord,viability=float(curve.mean()),final_population_hash=array_sha256(fp)))
 od=OUT/'map_blocks';od.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows).to_csv(od/f'{bid}_actual.csv',index=False)
def runmaps(cid,rep,map_ids):
 for mid in map_ids:
  runmap(cid,rep,mid)


def finalize_all():
 from scipy.stats import spearmanr
 from round2.mp_migration.run_core_and_screen import bootstrap_mean
 block=OUT/'map_blocks'; metas=[]; coords=[]; cont=[]
 for cid in ['D0','D1','D2']:
  for rep in range(8):
   bid=f'{cid}_r{rep:02d}';d=OUT/'prepared'/bid
   metas.append(json.loads((d/'meta.json').read_text()))
   cc=pd.read_csv(d/'coords.csv');cc.insert(0,'replicate',rep);cc.insert(0,'confirm_id',cid);coords.append(cc)
   a=pd.read_csv(block/f'{bid}_actual.csv');cont.append(a)
   for f in sorted(block.glob(f'{bid}_m*.csv')): cont.append(pd.read_csv(f))
   # identity is exact native; create from actual rows using identity metadata
   ir=cc[cc.endpoint_type=='identity'].iloc[0]
   ident=a.copy();ident['map_id']=ir.map_id;ident['map_hash']=ir.map_hash;ident['method']=ir.method;ident['endpoint_type']='identity';ident['actual_groups']=int(ir.actual_groups);ident['corrected_retained_information']=float(ir.corrected_retained_information);cont.append(ident)
 meta=pd.DataFrame(metas).sort_values(['confirm_id','replicate']);co=pd.concat(coords,ignore_index=True);ct=pd.concat(cont,ignore_index=True)
 meta.to_csv(OUT/'stage_d_rep_metadata.csv',index=False);co.to_csv(OUT/'stage_d_corrected_coordinates.csv',index=False);ct.to_csv(OUT/'stage_d_continuation_level.csv',index=False)
 reps=[];maps=[]
 for (cid,rep),p in ct.groupby(['confirm_id','replicate']):
  actual=p[p.map_id=='actual'].set_index('continuation_index').viability.sort_index();const=p[p.endpoint_type=='constant'].set_index('continuation_index').viability.sort_index();am=float(actual.mean());cm=float(const.mean());loss=am-cm;local=[]
  for keys,q in p[p.map_id!='actual'].groupby(['map_id','method','endpoint_type','actual_groups','corrected_retained_information']):
   mid,method,ep,ng,info=keys;vm=float(q.viability.mean());rec=(vm-cm)/loss if abs(loss)>1e-15 else np.nan;local.append(dict(confirm_id=cid,replicate=rep,map_id=mid,method=method,endpoint_type=ep,actual_groups=int(ng),corrected_retained_information=float(info),mean_viability=vm,recovery_fraction=float(rec)))
  lm=pd.DataFrame(local);maps.extend(local);rho=float(spearmanr(lm.corrected_retained_information,lm.recovery_fraction).statistic);idv=float(lm[lm.endpoint_type=='identity'].mean_viability.iloc[0]);reps.append(dict(confirm_id=cid,design_id=p.design_id.iloc[0],replicate=rep,actual_mean=am,constant_mean=cm,delta_mp=loss,spearman_info_recovery=rho,identity_exact=abs(idv-am)<1e-12))
 repdf=pd.DataFrame(reps).sort_values(['confirm_id','replicate']);mapdf=pd.DataFrame(maps).sort_values(['confirm_id','replicate','corrected_retained_information','map_id']);repdf.to_csv(OUT/'stage_d_replicate_summary.csv',index=False);mapdf.to_csv(OUT/'stage_d_map_summary.csv',index=False)
 sums=[];fams=[]
 for cid,p in repdf.groupby('confirm_id'):
  mean,lo,hi=bootstrap_mean(p.delta_mp.to_numpy(float),f'stage-d-{cid}-delta');spm,spl,sph=bootstrap_mean(p.spearman_info_recovery.to_numpy(float),f'stage-d-{cid}-spearman');mm=mapdf[mapdf.confirm_id==cid];ma=mm.groupby(['map_id','method','endpoint_type'],as_index=False).agg(mean_info=('corrected_retained_information','mean'),mean_recovery=('recovery_fraction','mean'));rho=float(spearmanr(ma.mean_info,ma.mean_recovery).statistic);ma.to_csv(OUT/f'{cid}_map_across_replicate_summary.csv',index=False)
  for method,q in ma[ma.endpoint_type=='intermediate'].groupby('method'):
   fams.append(dict(confirm_id=cid,method=method,n_maps=len(q),spearman_map_average=float(spearmanr(q.mean_info,q.mean_recovery).statistic) if len(q)>1 else np.nan))
  sums.append(dict(confirm_id=cid,design_id=p.design_id.iloc[0],n=len(p),delta_mp_mean=mean,delta_mp_low=lo,delta_mp_high=hi,positive_confirmed=bool(lo>0.25),positive_blocks=int((p.delta_mp>0).sum()),median_within_population_spearman=float(p.spearman_info_recovery.median()),mean_within_population_spearman=spm,spearman_low=spl,spearman_high=sph,positive_spearman_blocks=int((p.spearman_info_recovery>0).sum()),map_average_spearman=rho,identity_exact_all=bool(p.identity_exact.all())))
 sm=pd.DataFrame(sums).sort_values('confirm_id');sm.to_csv(OUT/'stage_d_confirmation_summary.csv',index=False);pd.DataFrame(fams).to_csv(OUT/'stage_d_family_monotonicity.csv',index=False)
 val=dict(n_nondefault_confirmations=int(sm.confirm_id.nunique()),n_replicates=int(len(repdf)),n_per_confirm=sorted(repdf.groupby('confirm_id').size().unique().tolist()),n_continuations=NCONT,max_mp_marginal_abs_error=float(meta.max_mp_marginal_abs_error.max()),identity_exact_all=bool(sm.identity_exact_all.all()),expected_map_block_files=3*8*34,observed_map_block_files=len(list(block.glob('D*_*.csv'))))
 (OUT/'VALIDATION.json').write_text(json.dumps(val,indent=2));print(json.dumps(val,indent=2));print(sm.to_string(index=False))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prep','map','maps','actual','finalize']);ap.add_argument('cid');ap.add_argument('rep',type=int);ap.add_argument('map_id',nargs='?');a=ap.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if a.action=='finalize':finalize_all();return
 if a.action=='prep':prep(a.cid,a.rep)
 elif a.action=='actual':runactual(a.cid,a.rep)
 elif a.action=='maps':runmaps(a.cid,a.rep,[x for x in (a.map_id or '').split(',') if x])
 else:runmap(a.cid,a.rep,a.map_id)
if __name__=='__main__':main()
