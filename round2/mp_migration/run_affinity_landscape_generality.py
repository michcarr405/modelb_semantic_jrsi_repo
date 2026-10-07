from __future__ import annotations
import argparse, itertools, json, math, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from modelb_semantic_repo import phase6
from modelb_semantic_repo.rng import make_generator, ContinuationStream, PermutationStream
from modelb_semantic_repo.phase4 import array_sha256, stable_integer_seed

OUT=ROOT/'round2/mp_migration/results/affinity_landscape_generality'
SEL=ROOT/'round2/mp_migration/results/stage_c_n8/stage_d_selected_final_mp.csv'
LAND_ROOT=2026100211; POP_ROOT=2026100212; CONT_ROOT=2026100213; PERM_ROOT=2026100214; INF_ROOT=2026100215
N_LAND=8; N_POP=8; N_CONT=8; H=36; N_PERM=200; BOOT=2000
SETTINGS=['B2_default','A_p2_a3','B2_reward3','B2_stride7']

@njit(cache=True)
def _mp_constant_observe(pop,aff,favored,bias,prod,anti,reward,penalty,temp,floor,k,active,mode,uniforms,offsets):
    nc,ns,L=pop.shape; na=active.size; nseg=favored.size; chain=L-k+1; nz=aff.shape[1]
    qsum=np.zeros((nseg,nz),np.float64); cnt=np.zeros(nseg,np.int64)
    # build population-frequency-weighted probability-space marginal by segment
    ch=0
    for ci in range(nc):
        for si in range(ns):
            off=int(offsets[ch]); ch+=1
            for ai in range(na):
                pos=int(active[ai]); mi=0
                for kk in range(k): mi=mi*4+int(pop[ci,si,pos+kk])
                shifted=min(max(pos+off,0),chain-1); sg=(shifted*nseg)//chain
                mx=-1e300
                for z in range(nz):
                    v=aff[mi,z]+(bias if z==int(favored[sg]) else 0.0)
                    if v>mx: mx=v
                den=0.0
                for z in range(nz): den+=np.exp((aff[mi,z]+(bias if z==int(favored[sg]) else 0.0)-mx)/temp)
                for z in range(nz): qsum[sg,z]+=np.exp((aff[mi,z]+(bias if z==int(favored[sg]) else 0.0)-mx)/temp)/den
                cnt[sg]+=1
    for sg in range(nseg):
        if cnt[sg]>0:
            for z in range(nz): qsum[sg,z]/=cnt[sg]
    fits=np.empty(nc,np.float64); q=0; ch=0
    for ci in range(nc):
        ps=0.0; rs=0.0
        for si in range(ns):
            prev=-1; off=int(offsets[ch]); ch+=1
            for ai in range(na):
                pos=int(active[ai]); shifted=min(max(pos+off,0),chain-1); sg=(shifted*nseg)//chain
                u=uniforms[q]; q+=1; cdf=0.0; chosen=nz-1
                for z in range(nz):
                    cdf+=qsum[sg,z]
                    if u<=cdf: chosen=z; break
                if ai>0:
                    if prod[prev,chosen]: ps+=1.0
                    if anti[prev,chosen]: rs+=1.0
                prev=chosen
        if mode==0: pv=ps/ns; rv=rs/ns
        else: pv=ps/(ns*max(1,na-1)); rv=rs/(ns*max(1,na-1))
        f=1.0+reward*pv-penalty*rv; fits[ci]=max(f,floor)
    return fits

def landscape_base(li:int)->np.ndarray:
    return make_generator(LAND_ROOT,'affinity-landscape',li).normal(size=(4**5,4))

def get_specs():
    sel=pd.read_csv(SEL)
    specs={r.design_id:json.loads(r.spec_json) for r in sel.itertuples()}
    if 'B2_default' not in specs:
        d=next(d for d in phase6.designB2() if d['design_id']=='B2_default'); specs['B2_default']=phase6.norm(d['spec'])
    return {k:specs[k] for k in SETTINGS}

def model_custom(spec,li):
    m=phase6.model(spec); base=landscape_base(li); m['aff']=base*float(m['sigma']); return m

def baseline_custom(spec,li,rep):
    m=model_custom(spec,li); seed=stable_integer_seed(POP_ROOT,'landscape-pop',li, next(k for k,v in get_specs().items() if v==spec), rep)
    ir=make_generator(seed,'init'); orng=make_generator(seed,'obs'); pr=make_generator(seed,'prop')
    pop=ir.integers(0,4,size=(m['n_cells'],m['n_seqs'],m['seq_len']),dtype=np.int8); tr=[]
    for _ in range(int(m['n_gens'])):
        f,*_=phase6.observe(pop,m,orng); tr.append(float(f.mean())); pop=phase6.reproduce(pop,f,m,pr)
    return m,pop,np.asarray(tr),seed

def simulate_actual(pop,m,bid,ci):
    st=ContinuationStream(CONT_ROOT,bid,ci); curve,fp=phase6.horizon(pop,m,m['aff'],H,st); return float(curve.mean()),fp

def simulate_mp(pop,m,bid,ci):
    st=ContinuationStream(CONT_ROOT,bid,ci); o=st.observation_generator(); p=st.propagation_generator(); x=np.array(pop,copy=True); vals=[]
    nch=int(m['n_cells'])*int(m['n_seqs']); n=nch*len(m['active']); j=int(m.get('jitter',0))
    for _ in range(H):
        off=o.integers(-j,j+1,size=nch,dtype=np.int64) if j else np.zeros(nch,np.int64)
        uniforms=o.random(n)
        f=_mp_constant_observe(x,m['aff'],m['favored'],float(m['bias']),m['prod'],m['anti'],float(m['reward']),float(m['penalty']),float(m['temperature']),float(m['floor']),int(m['motif_length']),m['active'],int(m['mode']),uniforms,off)
        vals.append(float(f.mean())); x=phase6.reproduce(x,f,m,p)
    return float(np.mean(vals)),x

def expected_marginal_error(pop,m):
    # analytical comparison of native expected P(Z|S) to MP Q(Z|S)
    nc,ns,L=pop.shape; k=int(m['motif_length']); chain=L-k+1; active=np.asarray(m['active']); nseg=len(m['favored']); nz=m['aff'].shape[1]
    off=np.zeros(nc*ns,dtype=np.int64); j=int(m.get('jitter',0))
    if j: off=make_generator(INF_ROOT,'marginal-check').integers(-j,j+1,size=nc*ns,dtype=np.int64)
    sums=np.zeros((nseg,nz)); cnt=np.zeros(nseg); ch=0
    for ci in range(nc):
      for si in range(ns):
        oo=int(off[ch]); ch+=1
        for pos in active:
          pos=int(pos); mi=0
          for kk in range(k): mi=mi*4+int(pop[ci,si,pos+kk])
          sg=(min(max(pos+oo,0),chain-1)*nseg)//chain
          logits=np.asarray(m['aff'][mi],float).copy(); logits[int(m['favored'][sg])]+=float(m['bias']); x=logits/float(m['temperature']); x-=x.max(); pr=np.exp(x);pr/=pr.sum(); sums[sg]+=pr;cnt[sg]+=1
    native=sums/cnt[:,None]
    # Reconstruct the marginal implied by the constant MP projection independently:
    # every window in segment s samples the same Q_s, where Q_s is the empirical
    # population-frequency-weighted average of native motif kernels in that segment.
    q=sums/cnt[:,None]
    recon=np.zeros_like(native)
    for sg in range(nseg):
        if cnt[sg]>0:
            recon[sg]=q[sg]  # sum_q P(q|s)Q(q,s) with one constant group
    return float(np.max(np.abs(native-recon)))

def job(li,did,rep):
    specs=get_specs();spec=specs[did];m,pop,tr,seed=baseline_custom(spec,li,rep); bid=f'L{li:02d}_{did}_r{rep:02d}'
    f,mot,z,s=phase6.observe(pop,m,make_generator(POP_ROOT,'landscape-info-observe',li,did,rep))
    obs,null,corr=phase6.corrected(mot,z,s,N_PERM,PermutationStream(PERM_ROOT,bid,0))
    av=[];mv=[]
    for ci in range(N_CONT):
        a,_=simulate_actual(pop,m,bid,ci); q,_=simulate_mp(pop,m,bid,ci); av.append(a);mv.append(q)
    w=max(1,math.ceil(len(tr)*.2)); gain=float(tr[-w:].mean()-tr[:w].mean())
    return dict(landscape=li,design_id=did,replicate=rep,baseline_seed=seed,state_hash=array_sha256(pop),corrected_information=corr,conditional_information=obs,permutation_mean=null,adaptive_gain=gain,actual_viability=float(np.mean(av)),mp_constant_viability=float(np.mean(mv)),delta_mp=float(np.mean(np.asarray(av)-np.asarray(mv))),delta_mp_cont_sd=float(np.std(np.asarray(av)-np.asarray(mv),ddof=1)),n_continuations=N_CONT,mp_marginal_max_abs_error=expected_marginal_error(pop,m))

def bootstrap(v,key):
    v=np.asarray(v,float); rng=make_generator(INF_ROOT,'landscape-bootstrap',key); d=v[rng.integers(0,len(v),size=(BOOT,len(v)))].mean(1); return float(v.mean()),float(np.quantile(d,.025)),float(np.quantile(d,.975))

def exact_sign_p(v):
    v=np.asarray(v,float); obs=abs(v.mean()); vals=[]
    for signs in itertools.product([-1.0,1.0],repeat=len(v)): vals.append(abs(np.mean(v*np.asarray(signs))))
    vals=np.asarray(vals); return float(np.mean(vals>=obs-1e-15))

def run(workers):
    OUT.mkdir(parents=True,exist_ok=True); bd=OUT/'blocks';bd.mkdir(exist_ok=True);jobs=[]
    for li in range(N_LAND):
      for did in SETTINGS:
       for rep in range(N_POP):
        p=bd/f'L{li:02d}_{did}_r{rep:02d}.json'
        if not p.exists(): jobs.append((li,did,rep,p))
    print('pending',len(jobs),flush=True);t=time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
      futs={ex.submit(job,li,did,rep):(li,did,rep,p) for li,did,rep,p in jobs}
      for i,fut in enumerate(as_completed(futs),1):
        li,did,rep,p=futs[fut];p.write_text(json.dumps(fut.result(),indent=2))
        if i%8==0 or i==len(futs): print(f'blocks {i}/{len(futs)} elapsed={time.time()-t:.1f}s',flush=True)
    finalize()

def finalize():
    rows=[json.loads(p.read_text()) for p in sorted((OUT/'blocks').glob('*.json'))]; raw=pd.DataFrame(rows).sort_values(['design_id','landscape','replicate']);raw.to_csv(OUT/'population_level.csv',index=False)
    lr=[]
    for (did,li),g in raw.groupby(['design_id','landscape']):
      dm=g.delta_mp.to_numpy(float); im=g.corrected_information.to_numpy(float); ag=g.adaptive_gain.to_numpy(float); rng=make_generator(INF_ROOT,'nested-pop-bootstrap',did,li); draws=dm[rng.integers(0,len(dm),size=(BOOT,len(dm)))].mean(1)
      lr.append(dict(design_id=did,landscape=li,n_pop=len(g),mean_delta_mp=float(dm.mean()),delta_mp_pop_boot_low=float(np.quantile(draws,.025)),delta_mp_pop_boot_high=float(np.quantile(draws,.975)),regime_lower_gt_0p25=bool(np.quantile(draws,.025)>.25),mean_corrected_information=float(im.mean()),mean_adaptive_gain=float(ag.mean()),positive_population_blocks=int((dm>0).sum())))
    land=pd.DataFrame(lr).sort_values(['design_id','landscape']);land.to_csv(OUT/'landscape_level.csv',index=False)
    sr=[]
    for did,g in land.groupby('design_id'):
      v=g.mean_delta_mp.to_numpy(float);mean,lo,hi=bootstrap(v,did);sr.append(dict(design_id=did,n_landscapes=len(g),mean_delta_mp=mean,landscape_boot_95_low=lo,landscape_boot_95_high=hi,positive_landscapes=int((v>0).sum()),exact_sign_p=exact_sign_p(v),replicated_across_landscapes=bool((lo>0) and (((v>0).sum()==len(v)) or exact_sign_p(v)<.05)),landscapes_regime_lower_gt_0p25=int(g.regime_lower_gt_0p25.sum()),mean_corrected_information=float(g.mean_corrected_information.mean()),mean_adaptive_gain=float(g.mean_adaptive_gain.mean())))
    sm=pd.DataFrame(sr).sort_values('design_id');sm.to_csv(OUT/'landscape_inference.csv',index=False)
    val=dict(n_population_rows=len(raw),n_landscapes=N_LAND,n_pop_per_landscape_setting=N_POP,n_settings=len(SETTINGS),max_mp_marginal_abs_error=float(raw.mp_marginal_max_abs_error.max()),all_landscape_setting_cells_complete=bool((raw.groupby(['design_id','landscape']).size()==N_POP).all()))
    (OUT/'VALIDATION.json').write_text(json.dumps(val,indent=2));print(json.dumps(val,indent=2));print(sm.to_string(index=False))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=8);a=ap.parse_args();run(a.workers)
if __name__=='__main__':main()
