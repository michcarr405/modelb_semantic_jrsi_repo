from pathlib import Path
import sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'src'))
from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.phase4 import load_map_panel
OUT=Path(__file__).resolve().parents[1]/'cleanroom_outputs'
P=default_parameters(); PANEL=load_map_panel(ROOT/'results/phase4_core/maps'); MAP={x['map_id']:x for x in PANEL}
SELECT=['m000_constant','m004_balanced_random_group','m015_affinity_rank_group','m024_contiguous_substring','m027_contiguous_substring','m029_contiguous_substring','m033_identity']
LABEL={'native':'Actual/native','submitted_constant':'Submitted constant (logit average)','m000_constant':'MP constant','m004_balanced_random_group':'MP balanced-random, 16 groups','m015_affinity_rank_group':'MP affinity-rank, 64 groups','m024_contiguous_substring':'MP substring start 0, length 2','m027_contiguous_substring':'MP substring start 3, length 2','m029_contiguous_substring':'MP substring start 1, length 3','m033_identity':'MP identity'}
A=np.asarray(P['motif_affinity_matrix'],float); favored=np.asarray(P['segment_favored_met'],int); S=len(favored); Z=A.shape[1]
def sm(x): x=x-x.max(axis=-1,keepdims=True); e=np.exp(x); return e/e.sum(axis=-1,keepdims=True)
NK=np.empty((A.shape[0],S,Z))
for s in range(S):
    x=A.copy(); x[:,favored[s]]+=P['bias_strength']; NK[:,s]=sm(x/P['temperature'])
prod=np.asarray(P['productive_pairs'],float); anti=np.asarray(P['anti_pairs'],float); neutral=1-prod-anti
chain=P['seq_len']-4; seglen=chain//S; segs=np.minimum(np.arange(chain)//seglen,S-1)
def motifs_of(pop):
    # encode length-5 base-4 windows vectorized over cells/sequences
    nc,ns,L=pop.shape; out=np.zeros((nc,ns,chain),dtype=np.int64)
    for k in range(5): out=out*4+pop[:,:,k:k+chain].astype(np.int64)
    return out
def calc(probs):
    # probs nc,ns,chain,Z
    marg=np.vstack([probs[:,:,segs==s,:].reshape(-1,Z).mean(axis=0) for s in range(S)])
    p0=probs[:,:,:-1,:]; p1=probs[:,:,1:,:]
    ep=np.einsum('...i,...j,ij->...',p0,p1,prod); ea=np.einsum('...i,...j,ij->...',p0,p1,anti); en=1-ep-ea
    cat=np.array([ep.mean(),ea.mean(),en.mean()])
    cell_prod=ep.sum(axis=(1,2))/P['n_seqs']; cell_anti=ea.sum(axis=(1,2))/P['n_seqs']
    fit=np.maximum(0.1,1+P['reward_strength']*cell_prod-P['penalty_strength']*cell_anti).mean()
    return marg,cat,float(fit)
def tv(a,b): return float(0.5*np.abs(a-b).sum(axis=1).mean())
rows=[]
for rep in range(20):
    pop=np.asarray(np.load(ROOT/f'results/phase4_core/states/selective/p1.0/rep_{rep:02d}.npz')['population'])
    motifs=motifs_of(pop); seg_grid=np.broadcast_to(segs,(pop.shape[0],pop.shape[1],chain))
    native_probs=NK[motifs,seg_grid]
    nm,nc,nf=calc(native_probs)
    rows.append([rep,'native',LABEL['native'],0,0,*nc,nf])
    # submitted constant: unweighted average logits across all motifs
    avg=A.mean(axis=0); ok=np.empty((S,Z))
    for s in range(S):
        x=avg.copy(); x[favored[s]]+=P['bias_strength']; ok[s]=sm((x/P['temperature'])[None,:])[0]
    old_probs=ok[seg_grid]
    om,oc,of=calc(old_probs)
    rows.append([rep,'submitted_constant',LABEL['submitted_constant'],tv(nm,om),0.5*np.abs(nc-oc).sum(),*oc,of])
    for mid in SELECT:
        item=MAP[mid]
        labels=np.asarray(item['labels'],dtype=np.int64); _,dense=np.unique(labels,return_inverse=True)
        if item['endpoint_type']=='identity': probs=native_probs
        else:
            groups=dense[motifs]; G=int(dense.max())+1
            sums=np.zeros((G,S,Z)); counts=np.zeros((G,S),dtype=np.int64)
            gf=groups.ravel(); sf=seg_grid.ravel(); pf=native_probs.reshape(-1,Z)
            np.add.at(sums,(gf,sf),pf); np.add.at(counts,(gf,sf),1)
            q=np.zeros_like(sums); mask=counts>0; q[mask]=sums[mask]/counts[mask,None]
            probs=q[groups,seg_grid]
        mm,mc,mf=calc(probs)
        rows.append([rep,mid,LABEL[mid],tv(nm,mm),0.5*np.abs(nc-mc).sum(),*mc,mf])
cols=['replicate','condition','label','segment_tv','adjacency_tv','promoting','reducing','neutral','expected_initial_fitness']
df=pd.DataFrame(rows,columns=cols); df.to_csv(OUT/'mp_marginal_diagnostics_replicates.csv',index=False)
summary=df.groupby(['condition','label'],sort=False).agg(n=('replicate','size'),mean_segment_tv=('segment_tv','mean'),max_segment_tv=('segment_tv','max'),mean_adjacency_tv=('adjacency_tv','mean'),mean_promoting=('promoting','mean'),mean_reducing=('reducing','mean'),mean_neutral=('neutral','mean'),mean_expected_initial_fitness=('expected_initial_fitness','mean')).reset_index()
summary.to_csv(OUT/'mp_marginal_diagnostics_summary.csv',index=False)
print(summary.to_string(index=False))
