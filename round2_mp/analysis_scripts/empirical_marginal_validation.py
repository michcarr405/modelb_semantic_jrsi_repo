from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import sys

BASE = Path('/mnt/data/r2_gap_closure/JRSI_MAJOR_REVISION_PHASE7_GATE8_PASSED_v1')
sys.path.insert(0, str(BASE/'src'))
from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.phase4 import load_map_panel
from modelb_semantic_repo.rng import ContinuationStream

CONT_ROOT = 2026100209
N_CONT = 64
OUTDIR = Path('/mnt/data/r2_gap_closure/empirical_marginal_validation')
OUTDIR.mkdir(parents=True, exist_ok=True)

MAP_IDS = [
    'm000_constant',
    'm004_balanced_random_group',
    'm015_affinity_rank_group',
    'm024_contiguous_substring',
    'm027_contiguous_substring',
    'm029_contiguous_substring',
    'm033_identity',
]
MAP_LABELS = {
    'm000_constant':'MP constant',
    'm004_balanced_random_group':'MP balanced-random, 16 groups',
    'm015_affinity_rank_group':'MP affinity-rank, 64 groups',
    'm024_contiguous_substring':'MP substring start 0, length 2',
    'm027_contiguous_substring':'MP substring start 3, length 2',
    'm029_contiguous_substring':'MP substring start 1, length 3',
    'm033_identity':'MP identity',
}

def native_kernel(params):
    aff=np.asarray(params['motif_affinity_matrix'],float)
    fav=np.asarray(params['segment_favored_met'],int)
    ns=len(fav); nz=aff.shape[1]
    out=np.empty((aff.shape[0],ns,nz),float)
    for s in range(ns):
        x=aff.copy(); x[:,fav[s]] += float(params['bias_strength']); x=x/float(params['temperature']); x-=x.max(axis=1,keepdims=True)
        e=np.exp(x); out[:,s,:]=e/e.sum(axis=1,keepdims=True)
    return out

def enumerate_windows(pop,nseg):
    nc,nseq,L=pop.shape; chain=L-4; seglen=chain//nseg; total=nc*nseq*chain
    motifs=np.empty(total,np.int64); segs=np.empty(total,np.int64); idx=0
    for ci in range(nc):
        for si in range(nseq):
            seq=pop[ci,si]
            for pos in range(chain):
                m=0
                for k in range(5): m=m*4+int(seq[pos+k])
                s=pos//seglen
                if s>=nseg: s=nseg-1
                motifs[idx]=m; segs[idx]=s; idx+=1
    return motifs,segs

def dense_labels(labels):
    _,inv=np.unique(np.asarray(labels,np.int64),return_inverse=True)
    return inv.astype(np.int64)

def mp_probabilities(native_probs, motifs, segs, labels, nseg, nz):
    lab=dense_labels(labels)
    groups=lab[motifs]; ng=int(groups.max())+1
    sums=np.zeros((ng,nseg,nz),float); counts=np.zeros((ng,nseg),np.int64)
    np.add.at(sums,(groups,segs),native_probs)
    np.add.at(counts,(groups,segs),1)
    kern=np.zeros_like(sums)
    mask=counts>0
    kern[mask]=sums[mask]/counts[mask,None]
    return kern[groups,segs]

def draw_states(probs,u):
    cdf=np.cumsum(probs,axis=1)
    states=np.sum(u[:,None] > cdf,axis=1).astype(np.int64)
    states=np.minimum(states,probs.shape[1]-1)
    return states

def state_counts(segs,states,nseg,nz):
    c=np.zeros((nseg,nz),np.int64); np.add.at(c,(segs,states),1); return c

def probs_from_counts(c):
    den=c.sum(axis=1,keepdims=True)
    return c/den

def mean_seg_tv(pa,pb):
    return float(np.mean(0.5*np.abs(pa-pb).sum(axis=1)))

def max_abs(pa,pb):
    return float(np.max(np.abs(pa-pb)))

def run():
    params=default_parameters(); kern=native_kernel(params); nseg=kern.shape[1]; nz=kern.shape[2]
    panel={x['map_id']:x for x in load_map_panel(BASE/'results/phase4_core/maps')}
    per_stream=[]; per_rep=[]
    for rep in range(20):
        pop=np.asarray(np.load(BASE/f'results/phase4_core/states/selective/p1.0/rep_{rep:02d}.npz')['population'])
        motifs,segs=enumerate_windows(pop,nseg); native_probs=kern[motifs,segs]
        map_probs={mid:mp_probabilities(native_probs,motifs,segs,panel[mid]['labels'],nseg,nz) for mid in MAP_IDS}
        native_pool=np.zeros((nseg,nz),np.int64); native_first=np.zeros_like(native_pool); native_second=np.zeros_like(native_pool)
        map_pool={mid:np.zeros((nseg,nz),np.int64) for mid in MAP_IDS}
        for ci in range(N_CONT):
            bid=f'selective_p1.0_r{rep:02d}'
            u=ContinuationStream(CONT_ROOT,bid,ci).observation_generator().random(len(motifs))
            stn=draw_states(native_probs,u); cn=state_counts(segs,stn,nseg,nz); native_pool+=cn
            (native_first if ci<32 else native_second)[:] += cn
            pn=probs_from_counts(cn)
            for mid in MAP_IDS:
                stm=draw_states(map_probs[mid],u); cm=state_counts(segs,stm,nseg,nz); map_pool[mid]+=cm
                pm=probs_from_counts(cm)
                per_stream.append(dict(replicate=rep,continuation_index=ci,map_id=mid,map_label=MAP_LABELS[mid],mean_segment_tv=mean_seg_tv(pn,pm),max_abs_state_segment_diff=max_abs(pn,pm)))
        p_native=probs_from_counts(native_pool); p_first=probs_from_counts(native_first); p_second=probs_from_counts(native_second)
        native_split=mean_seg_tv(p_first,p_second); native_split_max=max_abs(p_first,p_second)
        for mid in MAP_IDS:
            pm=probs_from_counts(map_pool[mid])
            per_rep.append(dict(replicate=rep,map_id=mid,map_label=MAP_LABELS[mid],pooled_64_mean_segment_tv=mean_seg_tv(p_native,pm),pooled_64_max_abs_state_segment_diff=max_abs(p_native,pm),native_split_half_mean_segment_tv=native_split,native_split_half_max_abs_state_segment_diff=native_split_max,ratio_to_native_split_half=(mean_seg_tv(p_native,pm)/native_split if native_split>0 else np.nan)))
    ps=pd.DataFrame(per_stream); pr=pd.DataFrame(per_rep)
    ps.to_csv(OUTDIR/'empirical_marginal_per_stream.csv',index=False); pr.to_csv(OUTDIR/'empirical_marginal_per_population.csv',index=False)
    rows=[]
    for mid,g in pr.groupby('map_id',sort=False):
        gs=ps[ps.map_id==mid]
        rows.append(dict(map_id=mid,map_label=g.map_label.iloc[0],n_populations=int(len(g)),n_streams_per_population=N_CONT,
                         mean_pooled_64_tv=float(g.pooled_64_mean_segment_tv.mean()),median_pooled_64_tv=float(g.pooled_64_mean_segment_tv.median()),max_pooled_64_tv=float(g.pooled_64_mean_segment_tv.max()),
                         mean_pooled_64_max_abs=float(g.pooled_64_max_abs_state_segment_diff.mean()),max_pooled_64_max_abs=float(g.pooled_64_max_abs_state_segment_diff.max()),
                         mean_single_stream_tv=float(gs.mean_segment_tv.mean()),median_single_stream_tv=float(gs.mean_segment_tv.median()),
                         mean_native_split_half_tv=float(g.native_split_half_mean_segment_tv.mean()),median_ratio_to_native_split_half=float(g.ratio_to_native_split_half.median()),max_ratio_to_native_split_half=float(g.ratio_to_native_split_half.max())))
    sm=pd.DataFrame(rows)
    sm.to_csv(OUTDIR/'empirical_marginal_summary.csv',index=False)
    validation={
      'continuation_root':CONT_ROOT,'n_populations':20,'n_streams_per_population':N_CONT,'total_native_draws':20*N_CONT,
      'windows_per_draw':int(len(motifs)),'maps':MAP_IDS,
      'identity_pooled_tv_exact_zero':bool(sm.loc[sm.map_id=='m033_identity','max_pooled_64_tv'].iloc[0]==0.0),
      'identity_single_stream_tv_exact_zero':bool(ps.loc[ps.map_id=='m033_identity','mean_segment_tv'].max()==0.0),
      'max_nonidentity_mean_pooled_tv':float(sm.loc[sm.map_id!='m033_identity','mean_pooled_64_tv'].max()),
      'mean_native_split_half_tv':float(pr.drop_duplicates('replicate').native_split_half_mean_segment_tv.mean()),
    }
    (OUTDIR/'VALIDATION.json').write_text(json.dumps(validation,indent=2))
    print(sm.to_string(index=False))
    print(json.dumps(validation,indent=2))

if __name__=='__main__': run()
