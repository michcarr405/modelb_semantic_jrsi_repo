from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib, json, math
import numpy as np
import pandas as pd
from numba import njit
from scipy.stats import qmc

from .information import grouping_hash, retained_information
from .interventions import balanced_random_group, affinity_rank_group, _group_affinity_matrix
from .phase4 import stable_integer_seed, array_sha256
from .rng import make_generator, PermutationStream, ContinuationStream
from .statistical_pipeline import TargetRule, analyze_replicate_frontiers, target_reach_table

ROOT=2026073106; DI=.01; DV=.25; DF=1.0

@dataclass(frozen=True)
class Settings:
    screen_perms:int=60
    confirm_perms:int=120
    continuations:int=2
    horizon:int=36
    bootstrap:int=2000
    root_seed:int=ROOT
    def to_dict(self): return asdict(self)

def norm(spec):
    x=dict(spec)
    defaults=dict(p=1.0,temperature=1.2,sigma_ratio=1/1.2,b_ratio=2/1.2,mutation_rate=.001,n_cells=80,n_seqs=8,seq_len=60,motif_length=5,n_metabolites=4,n_segments=4,segment_order='native',reward=2.0,penalty_ratio=.25,floor=.1,stride=1,fitness_mode='count',jitter=0,n_gens=150)
    for k,v in defaults.items(): x.setdefault(k,v)
    x['sigma']=x['sigma_ratio']*x['temperature']; x['bias']=x['b_ratio']*x['temperature']; x['penalty']=x['reward']*x['penalty_ratio']
    return x

def topology(c):
    pairs=[(i,j) for i in range(c) for j in range(i+1,c)]; e=len(pairs); nprom=max(1,round(4*e/6)); nred=max(0,round(e/6)); nred=min(nred,e-nprom)
    cyc=[]
    for i in range(c):
        z=tuple(sorted((i,(i+1)%c)))
        if z not in cyc: cyc.append(z)
    ordered=cyc+[z for z in pairs if z not in cyc]; prom=ordered[:nprom]; rem=[z for z in pairs if z not in prom]; red=rem[-nred:] if nred else []
    p=np.zeros((c,c),bool); a=np.zeros((c,c),bool); np.fill_diagonal(a,True)
    for i,j in prom:p[i,j]=p[j,i]=True
    for i,j in red:a[i,j]=a[j,i]=True
    return p,a

def affinity(k,c,sigma):
    if k==5 and c==4: base=np.random.default_rng(123).normal(size=(4**5,4))
    else: base=np.random.default_rng(stable_integer_seed(123,'phase6-affinity',k,c)).normal(size=(4**k,c))
    return base*float(sigma)

def model(spec):
    x=norm(spec); c=int(x['n_metabolites']); k=int(x['motif_length']); chain=int(x['seq_len'])-k+1
    p,a=topology(c)
    if c==4 and x['segment_order']=='native': order=[2,0,3,1]
    elif x['segment_order']=='reverse': order=list(reversed(range(c)))
    else: order=list(range(c))
    x.update(aff=affinity(k,c,x['sigma']),prod=p,anti=a,favored=np.array([order[i%len(order)] for i in range(int(x['n_segments']))],np.int64),active=np.arange(0,chain,int(x['stride']),dtype=np.int64),mode=0 if x['fitness_mode']=='count' else 1)
    return x

@njit(cache=True)
def _observe(pop,aff,favored,bias,prod,anti,reward,penalty,temp,floor,k,active,mode,uniforms,offsets):
    nc,ns,L=pop.shape; na=active.size; nseg=favored.size; chain=L-k+1; nm=aff.shape[1]; total=nc*ns*na
    motifs=np.empty(total,np.int64); states=np.empty(total,np.int64); segs=np.empty(total,np.int64); fits=np.empty(nc,np.float64); q=0; ch=0
    for ci in range(nc):
        ps=0.; rs=0.
        for si in range(ns):
            prev=-1; off=int(offsets[ch]); ch+=1
            for ai in range(na):
                pos=int(active[ai]); mi=0
                for z in range(k): mi=mi*4+int(pop[ci,si,pos+z])
                shifted=min(max(pos+off,0),chain-1); sg=(shifted*nseg)//chain; motifs[q]=mi; segs[q]=sg
                mx=-1e300
                for m in range(nm):
                    v=aff[mi,m]+(bias if m==int(favored[sg]) else 0.)
                    if v>mx:mx=v
                den=0.
                for m in range(nm): den+=np.exp((aff[mi,m]+(bias if m==int(favored[sg]) else 0.)-mx)/temp)
                u=uniforms[q]; cdf=0.; chosen=nm-1
                for m in range(nm):
                    cdf+=np.exp((aff[mi,m]+(bias if m==int(favored[sg]) else 0.)-mx)/temp)/den
                    if u<=cdf: chosen=m; break
                states[q]=chosen; q+=1
                if ai>0:
                    if prod[prev,chosen]:ps+=1
                    if anti[prev,chosen]:rs+=1
                prev=chosen
        if mode==0: pv=ps/ns; rv=rs/ns
        else: pv=ps/(ns*max(1,na-1)); rv=rs/(ns*max(1,na-1))
        f=1+reward*pv-penalty*rv; fits[ci]=max(f,floor)
    return fits,motifs,states,segs

def observe(pop,m,rng):
    nch=int(m['n_cells'])*int(m['n_seqs']); n=nch*len(m['active']); j=int(m['jitter']); off=rng.integers(-j,j+1,size=nch,dtype=np.int64) if j else np.zeros(nch,np.int64)
    return _observe(pop,m['aff'],m['favored'],float(m['bias']),m['prod'],m['anti'],float(m['reward']),float(m['penalty']),float(m['temperature']),float(m['floor']),int(m['motif_length']),m['active'],int(m['mode']),rng.random(n),off)

def reproduce(pop,fit,m,rng):
    fit=np.maximum(np.asarray(fit,float),0); probs=fit/fit.sum() if fit.sum()>0 else np.full(len(fit),1/len(fit)); nc,ns,L=pop.shape
    parents=np.minimum(np.searchsorted(np.cumsum(probs),rng.random(nc),side='right'),nc-1); inherit=rng.random((nc,ns))<float(m['p']); pseq=rng.integers(0,ns,size=(nc,ns)); env=rng.integers(0,4,size=(nc,ns,L),dtype=np.int8); inherited=pop[parents[:,None],pseq]; new=np.where(inherit[:,:,None],inherited,env).astype(np.int8)
    mask=rng.random((nc,ns,L))<float(m['mutation_rate']); offs=rng.integers(1,4,size=(nc,ns,L),dtype=np.int8); mut=((new.astype(np.int16)+offs.astype(np.int16))%4).astype(np.int8); return np.where(mask,mut,new).astype(np.int8)

def baseline(spec,seed):
    m=model(spec); ir=make_generator(seed,'p6-init'); orng=make_generator(seed,'p6-obs'); pr=make_generator(seed,'p6-prop'); pop=ir.integers(0,4,size=(m['n_cells'],m['n_seqs'],m['seq_len']),dtype=np.int8); tr=[]
    for _ in range(int(m['n_gens'])):
        f,*_=observe(pop,m,orng); tr.append(float(f.mean())); pop=reproduce(pop,f,m,pr)
    return m,pop,np.asarray(tr)

def horizon(pop,m,affm,H,stream):
    mm=dict(m); mm['aff']=np.asarray(affm); o=stream.observation_generator(); p=stream.propagation_generator(); x=np.array(pop,copy=True); vals=[]
    for _ in range(int(H)):
        f,*_=observe(x,mm,o); vals.append(float(f.mean())); x=reproduce(x,f,mm,p)
    return np.asarray(vals),x

def cmi_dense(m,z,s,nm,nz,ns):
    code=((s*nm+m)*nz+z); cnt=np.bincount(code,minlength=ns*nm*nz).reshape(ns,nm,nz).astype(float); total=len(m); val=0.
    for sg in range(ns):
        t=cnt[sg]; n=t.sum()
        if n==0:continue
        p=t/n; px=p.sum(1,keepdims=True); py=p.sum(0,keepdims=True); e=px@py; mask=p>0; val+=(n/total)*float(np.sum(p[mask]*np.log2(p[mask]/e[mask])))
    return val

def corrected(m,z,s,nperm,stream):
    m=np.asarray(m,np.int64);z=np.asarray(z,np.int64);s=np.asarray(s,np.int64); nm=int(m.max())+1;nz=int(z.max())+1;ns=int(s.max())+1;obs=cmi_dense(m,z,s,nm,nz,ns); rng=stream.generator(); idx=[np.flatnonzero(s==q) for q in range(ns)]; perm=z.copy(); vals=[]
    for _ in range(nperm):
        for ii in idx: perm[ii]=z[ii][rng.permutation(len(ii))]
        vals.append(cmi_dense(m,perm,s,nm,nz,ns))
    return obs,float(np.mean(vals)),float(obs-np.mean(vals))

def screen_job(d,rep,sett,H=None):
    did=d['design_id']; spec=norm(d['spec']); seed=stable_integer_seed(sett.root_seed,'p6-screen',did,rep); m,pop,tr=baseline(spec,seed); f,mot,z,s=observe(pop,m,make_generator(sett.root_seed,'p6-info',did,rep)); obs,null,corr=corrected(mot,z,s,sett.screen_perms,PermutationStream(sett.root_seed,f'{did}_r{rep}',0)); const=np.repeat(m['aff'].mean(0,keepdims=True),len(m['aff']),axis=0); vv=[]; H=H or sett.horizon
    for ci in range(sett.continuations):
        st=ContinuationStream(sett.root_seed,f'{did}_r{rep}',ci); a,_=horizon(pop,m,m['aff'],H,st); c,_=horizon(pop,m,const,H,st); vv.append(float(a.mean()-c.mean()))
    w=max(1,math.ceil(len(tr)*.2)); return dict(design_id=did,stage=d['stage'],family=d.get('family',''),replicate=rep,spec_json=json.dumps(spec,sort_keys=True),corrected_information=corr,conditional_information=obs,permutation_mean=null,value_of_information=float(np.mean(vv)),adaptive_gain=float(tr[-w:].mean()-tr[:w].mean()),final_mean_fitness=float(f.mean()),identity_exact=True,state_hash=array_sha256(pop),trajectory_hash=array_sha256(tr))

def boot(v,rng,B=2000):
    v=np.asarray(v,float); d=v[rng.integers(0,len(v),size=(B,len(v)))].mean(1); return float(v.mean()),float(np.quantile(d,.025)),float(np.quantile(d,.975))

def summarize(raw,sett):
    rows=[]
    for did,p in raw.groupby('design_id'):
        r=dict(design_id=did,stage=p.stage.iloc[0],family=p.family.iloc[0],spec_json=p.spec_json.iloc[0],n=len(p),identity_exact=bool(p.identity_exact.all()))
        for met in ['corrected_information','value_of_information','adaptive_gain']:
            a,b,c=boot(p[met],make_generator(sett.root_seed,'p6-boot',did,met),sett.bootstrap); r[met+'_mean']=a;r[met+'_low']=b;r[met+'_high']=c
        il,ih=r['corrected_information_low'],r['corrected_information_high'];vl,vh=r['value_of_information_low'],r['value_of_information_high'];fl=r['adaptive_gain_low']
        if ih<=DI: reg='R0_null'
        elif il>DI and vh<=DV:reg='R1_syntactic_only'
        elif il>DI and vl>DV and fl<=DF:reg='R2_viability_relevant'
        elif il>DI and vl>DV and fl>DF:reg='R3_strong_adaptation'
        else:reg='boundary_uncertain'
        im,vm,fm=r['corrected_information_mean'],r['value_of_information_mean'],r['adaptive_gain_mean']; r['regime']=reg; r['boundary_distance']=min(abs(im-DI)/DI,abs(vm-DV)/DV,abs(fm-DF)/DF)
        if im<=DI:r['provisional']='R0_null';r['depth']=(DI-im)/DI
        elif vm<=DV:r['provisional']='R1_syntactic_only';r['depth']=min((im-DI)/DI,(DV-vm)/DV)
        elif fm<=DF:r['provisional']='R2_viability_relevant';r['depth']=min((im-DI)/DI,(vm-DV)/DV,(DF-fm)/DF)
        else:r['provisional']='R3_strong_adaptation';r['depth']=min((im-DI)/DI,(vm-DV)/DV,(fm-DF)/DF)
        rows.append(r)
    return pd.DataFrame(rows).sort_values('design_id')

def designA():
    out=[]; ps=[.4,.6,.75,.85,.925,1.0]; aa=[0,.45,.9,1.35]
    for i,p in enumerate(ps):
        for j,a in enumerate(aa): out.append(dict(design_id=f'A_p{i}_a{j}',stage='A',spec=norm(dict(p=p,sigma_ratio=a))))
    for tag,b,seed in [('low',.5,6101),('high',2.5,6102)]:
        x=qmc.LatinHypercube(2,seed=seed).random(4)
        for i,u in enumerate(x):out.append(dict(design_id=f'A_{tag}_{i}',stage='A',spec=norm(dict(p=.4+.6*u[0],sigma_ratio=1.35*u[1],b_ratio=b))))
    return out

def designB1():
    x=qmc.LatinHypercube(13,seed=6201).random(16);out=[];cells=[40,80,160];ks=[4,5,6];cs=[3,4,6];segs=[2,4,8];strides=[1,2,5];floors=[0,.1,1]
    for i,u in enumerate(x):
        sp=dict(p=.4+.6*u[0],sigma_ratio=1.5*u[1],b_ratio=3*u[2],temperature=.8+u[3],mutation_rate=10**(-4+2*u[4]),n_cells=cells[min(int(3*u[5]),2)],motif_length=ks[min(int(3*u[6]),2)],n_metabolites=cs[min(int(3*u[7]),2)],n_segments=segs[min(int(3*u[8]),2)],reward=1+2*u[9],penalty_ratio=.1+.4*u[10],floor=floors[min(int(3*u[11]),2)],stride=strides[min(int(3*u[12]),2)],fitness_mode='count' if i%2==0 else 'fraction')
        out.append(dict(design_id=f'B1_{i:02d}',stage='B1',spec=norm(sp)))
    return out

def designB2():
    v=[('default','anchor',{}),('stride2','window',{'stride':2}),('stride5','window',{'stride':5}),('stride7','window',{'stride':7}),('seg2','position',{'n_segments':2}),('seg8','position',{'n_segments':8}),('reverse','position',{'segment_order':'reverse'}),('jitter','position',{'jitter':2}),('met3','metabolite',{'n_metabolites':3}),('met6','metabolite',{'n_metabolites':6}),('fraction','fitness',{'fitness_mode':'fraction'}),('reward1','fitness',{'reward':1}),('reward3','fitness',{'reward':3}),('penaltylow','fitness',{'penalty_ratio':.1}),('penaltyhigh','fitness',{'penalty_ratio':.5}),('floor0','fitness',{'floor':0}),('floor1','fitness',{'floor':1})]
    return [dict(design_id='B2_'+n,stage='B2',family=f,spec=norm(ch)) for n,f,ch in v]

def save_design(ds,path):pd.DataFrame([dict(design_id=d['design_id'],stage=d['stage'],family=d.get('family',''),spec_json=json.dumps(d['spec'],sort_keys=True)) for d in ds]).to_csv(path,index=False)

def stage_defs(stage,outdir):
    if stage=='A':return designA(),4,'stage_a_replicates.csv'
    if stage=='B1':return designB1(),3,'stage_b1_replicates.csv'
    if stage=='B2':return designB2(),4,'stage_b2_replicates.csv'
    if stage=='C':
        reps=pd.read_csv(Path(outdir)/'stage_c_representatives.csv');ds=[]
        for r in reps.itertuples():
            base=json.loads(r.spec_json)
            for g in [100,150,250]:sp=dict(base);sp['n_gens']=g;ds.append(dict(design_id=f'C_g{g}_{r.design_id}',stage='C',spec=norm(sp)))
            for h in [24,36,60]:ds.append(dict(design_id=f'C_h{h}_{r.design_id}',stage='C',spec=norm(base),horizon=h))
        return ds,4,'stage_c_replicates.csv'
    raise ValueError(stage)

def run_batch(stage,outdir,batch=20):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True);ds,reps,fn=stage_defs(stage,out);path=out/fn;rows=pd.read_csv(path).to_dict('records') if path.exists() else [];done={(r['design_id'],int(r['replicate'])) for r in rows};jobs=[];sett=Settings()
    for d in ds:
        for rep in range(reps):
            if (d['design_id'],rep) not in done:jobs.append((d,rep))
    for d,rep in jobs[:batch]:rows.append(screen_job(d,rep,sett,d.get('horizon')))
    pd.DataFrame(rows).sort_values(['design_id','replicate']).to_csv(path,index=False);return len(rows),len(ds)*reps

def prepare(outdir):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True);sett=Settings();(out/'phase6_settings.json').write_text(json.dumps(sett.to_dict(),indent=2));save_design(designA(),out/'stage_a_design.csv');save_design(designB1(),out/'stage_b1_design.csv');save_design(designB2(),out/'stage_b2_design.csv')

def prepare_c(outdir):
    out=Path(outdir);sett=Settings();raw=pd.concat([pd.read_csv(out/'stage_a_replicates.csv'),pd.read_csv(out/'stage_b1_replicates.csv'),pd.read_csv(out/'stage_b2_replicates.csv')]);sm=summarize(raw,sett);sm.to_csv(out/'stage_ab_summary.csv',index=False);default=sm[sm.design_id=='B2_default'].iloc[0];boundary=sm.sort_values(['boundary_distance','design_id']).iloc[0];pd.DataFrame([default,boundary]).drop_duplicates('design_id').to_csv(out/'stage_c_representatives.csv',index=False);save_design(stage_defs('C',out)[0],out/'stage_c_design.csv')

def select_d(outdir):
    out=Path(outdir);sett=Settings();sc=summarize(pd.read_csv(out/'stage_c_replicates.csv'),sett);sc.to_csv(out/'stage_c_summary.csv',index=False);sm=pd.read_csv(out/'stage_ab_summary.csv');picks=[]
    for reg in ['R2_viability_relevant','R3_strong_adaptation']:
        q=sm[sm.regime==reg]
        if len(q):picks.append(q.sort_values(['depth','design_id'],ascending=[False,True]).iloc[0])
    picks.append(sm.sort_values(['boundary_distance','design_id']).iloc[0]);picks.append(sm[sm.design_id=='B2_default'].iloc[0]);sel=pd.DataFrame(picks).drop_duplicates('design_id').reset_index(drop=True);sel.insert(0,'confirm_id',[f'D{i}' for i in range(len(sel))]);sel.to_csv(out/'stage_d_selected.csv',index=False)

def labels_sub(k,start,length):
    n=4**k;lab=np.empty(n,np.int64)
    for i in range(n):
        x=i;dig=[0]*k
        for p in range(k-1,-1,-1):dig[p]=x%4;x//=4
        z=0
        for d in dig[start:start+length]:z=4*z+d
        lab[i]=z
    return lab

def panel(m,root,cid):
    n=len(m['aff']); ks=[];x=2
    while x<=n//2 and len(ks)<9:ks.append(x);x*=2
    cand=[]
    def add(method,ep,lab):cand.append(dict(method=method,endpoint_type=ep,labels=np.asarray(lab,np.int64),map_hash=grouping_hash(lab)))
    add('constant','constant',np.zeros(n,np.int64))
    for q in ks:add('balanced_random_group','intermediate',balanced_random_group(n,q,make_generator(root,'p6-map',cid,q)));add('affinity_rank_group','intermediate',affinity_rank_group(m['aff'],q))
    k=int(m['motif_length'])
    for L in range(1,k):
        for st in range(k-L+1):add('contiguous_substring','intermediate',labels_sub(k,st,L))
    add('identity','identity',np.arange(n));out=[];seen=set()
    for c in cand:
        if c['map_hash'] in seen:continue
        seen.add(c['map_hash']);c['map_id']=f'm{len(out):03d}_{c["method"]}';c['actual_groups']=len(np.unique(c['labels']));out.append(c)
    return out

def confirm_job(row,rep,sett):
    cid=row.confirm_id;did=row.design_id;spec=json.loads(row.spec_json);seed=stable_integer_seed(sett.root_seed,'p6-confirm',cid,rep);m,pop,tr=baseline(spec,seed);f,mot,z,s=observe(pop,m,make_generator(sett.root_seed,'p6-cinfo',cid,rep));obs,null,corr=corrected(mot,z,s,sett.confirm_perms,PermutationStream(sett.root_seed,f'{cid}_r{rep}',0));pan=panel(m,sett.root_seed,cid);bid=f'{cid}_r{rep:02d}';rows=[]
    for ci in range(sett.continuations):
        st=ContinuationStream(sett.root_seed,bid,ci);a,ap=horizon(pop,m,m['aff'],sett.horizon,st);rows.append(dict(confirm_id=cid,design_id=did,condition='selective',baseline_replicate=bid,replicate=rep,map_id='actual',map_hash='actual',method='unintervened',endpoint_type='actual',actual_groups=len(m['aff']),retained_information=obs,baseline_information=obs,continuation_index=ci,viability=float(a.mean()),final_population_hash=array_sha256(ap)))
        for it in pan:
            curve,fp=horizon(pop,m,_group_affinity_matrix(m['aff'],it['labels']),sett.horizon,st);rows.append(dict(confirm_id=cid,design_id=did,condition='selective',baseline_replicate=bid,replicate=rep,map_id=it['map_id'],map_hash=it['map_hash'],method=it['method'],endpoint_type=it['endpoint_type'],actual_groups=it['actual_groups'],retained_information=float(retained_information(mot,z,s,it['labels'])),baseline_information=obs,continuation_index=ci,viability=float(curve.mean()),final_population_hash=array_sha256(fp)))
    return dict(confirm_id=cid,design_id=did,replicate=rep,baseline_replicate=bid,corrected_information=corr,spec_json=json.dumps(spec,sort_keys=True),state_hash=array_sha256(pop)),rows

def confirm_batch(outdir,batch=1):
    out=Path(outdir);sel=pd.read_csv(out/'stage_d_selected.csv');blocks=out/'stage_d_blocks';blocks.mkdir(exist_ok=True);sett=Settings();jobs=[]
    for r in sel.itertuples():
        if r.design_id=='B2_default':continue
        for rep in range(8):
            stem=f'{r.confirm_id}_r{rep:02d}'
            if not (blocks/f'{stem}.json').exists():jobs.append((r,rep,stem))
    for r,rep,stem in jobs[:batch]:
        b,rr=confirm_job(r,rep,sett);(blocks/f'{stem}.json').write_text(json.dumps(b,indent=2));pd.DataFrame(rr).to_csv(blocks/f'{stem}.csv',index=False)
    return len(list(blocks.glob('*.json'))),len([r for r in sel.itertuples() if r.design_id!='B2_default'])*8

def finalize(outdir):
    out=Path(outdir);sett=Settings();sel=pd.read_csv(out/'stage_d_selected.csv');files=sorted((out/'stage_d_blocks').glob('*.csv'));raw=pd.concat([pd.read_csv(f) for f in files],ignore_index=True);raw.to_csv(out/'stage_d_continuations.csv',index=False);reps=[];fronts=[]
    for cid,p in raw.groupby('confirm_id'):
        a=analyze_replicate_frontiers(p,target_rule=TargetRule(.01));a.replicate_summary.insert(0,'confirm_id',cid);a.frontier_points.insert(0,'confirm_id',cid);reps.append(a.replicate_summary);fronts.append(a.frontier_points)
    rep=pd.concat(reps);fr=pd.concat(fronts);rep.to_csv(out/'stage_d_replicate_summary.csv',index=False);fr.to_csv(out/'stage_d_frontiers.csv',index=False);ds=[]
    design_by_confirm = raw.groupby('confirm_id')['design_id'].first().to_dict()
    for cid,p in rep.groupby('confirm_id'):
        m,l,u=boot(p.value_of_information,make_generator(sett.root_seed,'p6-dboot',cid),sett.bootstrap);ds.append(dict(confirm_id=cid,design_id=design_by_confirm[cid],voi_mean=m,voi_low=l,voi_high=u,identity_exact=bool(p.identity_information_recovered.all() and p.identity_viability_recovered.all()),target_fraction=float(p.target_reached.mean()),positive=bool(l>DV)))
    dsum=pd.DataFrame(ds);dsum.to_csv(out/'stage_d_summary.csv',index=False);sm=pd.read_csv(out/'stage_ab_summary.csv');pos={'R2_viability_relevant','R3_strong_adaptation'};fa=float(sm[sm.stage=='A'].regime.isin(pos).mean());fb=float(sm[sm.stage=='B1'].regime.isin(pos).mean());b2=sm[sm.stage=='B2'];fam={f:bool(((b2.family==f)&b2.regime.isin(pos)).any()) for f in ['window','position','metabolite','fitness']};default=pd.read_csv('results/phase4_core/replicate_frontier_summary.csv').query("condition=='selective' and inherit_prob==1.0");default_ok=bool(default.value_of_information.mean()>DV and default.identity_information_recovered.all() and default.identity_viability_recovered.all());nondef=int(dsum.positive.sum());ident=bool(dsum.identity_exact.all());broad=fa>=.2 and fb>=.15 and sum(fam.values())>=3 and default_ok and nondef>=2 and ident;narrow=(not broad) and fb>=.05 and sum(fam.values())>=2 and default_ok and nondef>=1 and ident;decision='BROAD_GENERALITY_SUPPORTED' if broad else 'NARROW_GENERALITY_SUPPORTED' if narrow else 'NO_GENERALITY_SUPPORT';gate=dict(gate='Gate 7 - Generality',status='PASSED' if broad or narrow else 'FAILED',generality_decision=decision,stage_a_positive_fraction=fa,stage_b1_positive_fraction=fb,structural_family_support=fam,default_archived_confirmed=default_ok,nondefault_confirmed=nondef,identity_exact=ident,broad=broad,narrow=narrow);(out/'GATE_7_DECISION.json').write_text(json.dumps(gate,indent=2));return gate
