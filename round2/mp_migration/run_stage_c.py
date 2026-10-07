from __future__ import annotations
import argparse,json,math,sys,time,multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from modelb_semantic_repo import phase6
from modelb_semantic_repo.phase4 import array_sha256
from modelb_semantic_repo.rng import ContinuationStream,PermutationStream,make_generator
from modelb_semantic_repo.mp_operator import simulate_phase6_constant,expected_marginal_error_general
from round2.mp_migration.run_core_and_screen import bootstrap_mean

OUT=ROOT/'round2/mp_migration/results/stage_c_n8'
SCREEN=ROOT/'round2/mp_migration/results/screen_n8'
CONT_ROOT=2026100207
NCONT=8
BOOT=2000

def stage_c_designs():
    reps=pd.read_csv(SCREEN/'stage_c_representatives_mp.csv')
    ds=[]
    for r in reps.itertuples():
        base=json.loads(r.spec_json)
        for g in [100,150,250]:
            sp=dict(base);sp['n_gens']=g
            ds.append(dict(design_id=f'C_g{g}_{r.design_id}',stage='C',source_design_id=r.design_id,spec=phase6.norm(sp),horizon=36))
        for h in [24,36,60]:
            ds.append(dict(design_id=f'C_h{h}_{r.design_id}',stage='C',source_design_id=r.design_id,spec=phase6.norm(base),horizon=h))
    return ds

def job(d,rep):
    did=d['design_id'];spec=d['spec'];H=int(d['horizon'])
    seed=phase6.stable_integer_seed(phase6.ROOT,'p6-screen',did,rep)
    m,pop,tr=phase6.baseline(spec,seed)
    f,mot,z,s=phase6.observe(pop,m,make_generator(phase6.ROOT,'p6-info',did,rep))
    obs,null,corr=phase6.corrected(mot,z,s,60,PermutationStream(phase6.ROOT,f'{did}_r{rep}',0))
    bid=f'{did}_r{rep}'; vv=[]
    for ci in range(NCONT):
        st=ContinuationStream(CONT_ROOT,bid,ci)
        actual,_=phase6.horizon(pop,m,m['aff'],H,st)
        mpv,_=simulate_phase6_constant(pop,m,H,CONT_ROOT,bid,ci,phase6.reproduce)
        vv.append(float(actual.mean()-mpv))
    w=max(1,math.ceil(len(tr)*.2))
    vr=make_generator(2026100210,'stage-c-marginal',did,rep);nc=int(m['n_cells'])*int(m['n_seqs']);j=int(m.get('jitter',0));offs=vr.integers(-j,j+1,size=nc,dtype=np.int64) if j else np.zeros(nc,np.int64)
    return dict(design_id=did,source_design_id=d['source_design_id'],stage='C',replicate=rep,spec_json=json.dumps(spec,sort_keys=True),horizon=H,baseline_seed=seed,corrected_information=corr,conditional_information=obs,permutation_mean=null,delta_mp=float(np.mean(vv)),delta_mp_cont_sd=float(np.std(vv,ddof=1)),adaptive_gain=float(tr[-w:].mean()-tr[:w].mean()),final_mean_fitness=float(f.mean()),state_hash=array_sha256(pop),trajectory_hash=array_sha256(tr),mp_marginal_max_abs_error=float(expected_marginal_error_general(pop,m,np.zeros(len(m['aff']),np.int64),offs)),n_continuations=NCONT)

def worker(x):
    d,r=x;return d['design_id'],r,job(d,r)

def summarize(raw):
    rows=[]
    for did,p in raw.groupby('design_id'):
        r=dict(design_id=did,source_design_id=p.source_design_id.iloc[0],n=len(p),horizon=int(p.horizon.iloc[0]),spec_json=p.spec_json.iloc[0])
        for met in ['corrected_information','delta_mp','adaptive_gain']:
            a,b,c=bootstrap_mean(p[met].to_numpy(float),f'stage-c-{did}-{met}');r[met+'_mean']=a;r[met+'_low']=b;r[met+'_high']=c
        il,ih=r['corrected_information_low'],r['corrected_information_high'];vl,vh=r['delta_mp_low'],r['delta_mp_high'];fl=r['adaptive_gain_low']
        if ih<=phase6.DI:reg='R0_null'
        elif il>phase6.DI and vh<=phase6.DV:reg='R1_syntactic_only'
        elif il>phase6.DI and vl>phase6.DV and fl<=phase6.DF:reg='R2_viability_relevant'
        elif il>phase6.DI and vl>phase6.DV and fl>phase6.DF:reg='R3_strong_adaptation'
        else:reg='boundary_uncertain'
        r['regime']=reg;rows.append(r)
    return pd.DataFrame(rows).sort_values('design_id')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['run','finalize']);ap.add_argument('--workers',type=int,default=4);ap.add_argument('--limit',type=int,default=20);a=ap.parse_args();OUT.mkdir(parents=True,exist_ok=True);b=OUT/'blocks';b.mkdir(exist_ok=True)
    if a.action=='run':
        miss=[]
        for d in stage_c_designs():
            for r in range(8):
                p=b/f"{d['design_id']}_r{r:02d}.json"
                if not p.exists():miss.append((d,r))
        miss=miss[:a.limit];print(json.dumps({'jobs':len(miss)}),flush=True);t=time.time();ctx=mp.get_context('spawn')
        with ctx.Pool(a.workers) as pool:
            for i,(did,r,res) in enumerate(pool.imap_unordered(worker,miss,chunksize=1),1):
                (b/f'{did}_r{r:02d}.json').write_text(json.dumps(res,indent=2))
                if i%10==0 or i==len(miss):print(json.dumps({'done':i,'elapsed':round(time.time()-t,1)}),flush=True)
    else:
        rows=[json.loads(p.read_text()) for p in sorted(b.glob('*.json'))];raw=pd.DataFrame(rows).sort_values(['design_id','replicate']);raw.to_csv(OUT/'stage_c_replicates_n8_mp.csv',index=False)
        sm=summarize(raw);sm.to_csv(OUT/'stage_c_summary_n8_mp.csv',index=False)
        # Validate reconstructed historical default cohort where design IDs overlap.
        old=pd.read_csv(ROOT/'results/phase6_generality/stage_c_replicates.csv'); old=old[old.design_id.str.contains('B2_default')]
        nw=raw[(raw.source_design_id=='B2_default') & (raw.replicate<4)]
        m=old.merge(nw,on=['design_id','replicate'],suffixes=('_old','_new'),validate='one_to_one')
        val={'n_rows':len(raw),'n_designs':raw.design_id.nunique(),'n_per_design':sorted(raw.groupby('design_id').size().unique().tolist()),'max_mp_marginal_abs_error':float(raw.mp_marginal_max_abs_error.max()),'default_old_state_hashes_all_match':bool((m.state_hash_old==m.state_hash_new).all()),'max_abs_default_old_nonintervention_diff':float(max(np.max(np.abs(m.corrected_information_old-m.corrected_information_new)),np.max(np.abs(m.adaptive_gain_old-m.adaptive_gain_new)),np.max(np.abs(m.final_mean_fitness_old-m.final_mean_fitness_new))))}
        (OUT/'VALIDATION.json').write_text(json.dumps(val,indent=2));print(json.dumps(val,indent=2));print(sm[['design_id','source_design_id','delta_mp_mean','delta_mp_low','delta_mp_high','corrected_information_mean','adaptive_gain_mean','regime']].to_string(index=False))
if __name__=='__main__':main()
