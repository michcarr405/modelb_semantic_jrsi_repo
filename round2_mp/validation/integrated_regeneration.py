"""Portable orchestration of unchanged archived drivers; no scientific overrides."""
from __future__ import annotations
import argparse, importlib.util, json, os, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO), str(REPO / 'src')]
os.environ['JRSI_R1_ROOT'] = str(REPO)

def load_hp():
    path = REPO / 'round2_mp/causal_specificity_high_continuation/run_high_precision_campaign.py'
    spec = importlib.util.spec_from_file_location('hp_production', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.R1 = REPO
    mod.PHASE4 = REPO / 'results/phase4_core'
    mod.PHASE5 = REPO / 'results/phase5_causal_specificity'
    mod.PRIOR_R2 = REPO / 'round2_mp/causal_specificity_2cont_reference'
    mod.OUT = REPO / 'round2_mp/regenerated/causal_specificity'
    return mod

def stage_d_task(task):
    from round2.mp_migration import run_stage_d_mp_split as d
    kind, cid, rep, mid = task
    if kind == 'prep': d.prep(cid,rep)
    elif kind == 'actual': d.runactual(cid,rep)
    else: d.runmap(cid,rep,mid)
    return task

def archive_landscape_baseline(spec,li,rep):
    """Retain the unchanged driver's generated states for the candidate."""
    import numpy as np
    from round2.mp_migration import run_affinity_landscape_generality as l
    from modelb_semantic_repo.phase4 import array_sha256
    m,pop,tr,seed=l._original_baseline_custom(spec,li,rep)
    did=next(k for k,v in l.get_specs().items() if v==spec)
    out=REPO/'round2_mp/regenerated/landscape_states'
    out.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out/f'L{li:02d}_{did}_r{rep:02d}.npz',population=pop,trajectory=tr,baseline_seed=seed)
    if li==0 and did=='B2_default' and rep==0:
        from modelb_semantic_repo.mp_operator import simulate_phase6_constant
        bid='L00_B2_default_r00'
        ref,refpop=l.simulate_mp(pop,m,bid,0)
        rec,recpop=simulate_phase6_constant(pop,m,l.H,l.CONT_ROOT,bid,0,l.phase6.reproduce)
        result=dict(baseline_state_hash=array_sha256(pop),reference_viability=ref,reconstructed_viability=rec,
                    reference_final_hash=array_sha256(refpop),reconstructed_final_hash=array_sha256(recpop),
                    exact_final_state_match=bool(np.array_equal(refpop,recpop)),viability_exact=bool(ref==rec))
        (out/'INDEPENDENT_FINAL_STATE_EQUIVALENCE.json').write_text(json.dumps(result,indent=2))
    return m,pop,tr,seed

def run_stage_d(workers):
    from round2.mp_migration import run_stage_d_mp_split as d
    from modelb_semantic_repo import phase6
    prep = [('prep',cid,r,None) for cid in ['D0','D1','D2'] for r in range(8)
            if not (d.OUT/'prepared'/f'{cid}_r{r:02d}'/'meta.json').exists()]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for i,f in enumerate(as_completed([pool.submit(stage_d_task,t) for t in prep]),1):
            f.result(); print('Stage D prep',i,len(prep),flush=True)
    tasks=[]
    for cid in ['D0','D1','D2']:
        m=phase6.model(json.loads(d.getrow(cid)['spec_json']))
        mids=[it['map_id'] for it in phase6.panel(m,phase6.ROOT,cid) if it['endpoint_type'] != 'identity']
        for r in range(8):
            for mid in ['actual',*mids]:
                if not (d.OUT/'map_blocks'/f'{cid}_r{r:02d}_{mid}.csv').exists():
                    tasks.append(('actual' if mid=='actual' else 'map',cid,r,mid))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for i,f in enumerate(as_completed([pool.submit(stage_d_task,t) for t in tasks]),1):
            f.result()
            if i%20==0 or i==len(tasks): print('Stage D maps',i,len(tasks),flush=True)
    d.finalize_all()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['hp','hp-derived','stage-d','landscapes','frontier','core-controls']);ap.add_argument('--workers',type=int,default=3);a=ap.parse_args()
    if a.action=='hp': load_hp().main(a.workers)
    elif a.action=='hp-derived':
        import pandas as pd
        h=load_hp();h.OUT.mkdir(parents=True,exist_ok=True)
        c=pd.read_csv(h.ROOT/'results/continuation_level_results_64new.csv',float_precision='round_trip')
        w=h.aggregate_seed_blocks(c,'delta_mp').sort_values('seed_block')
        w.to_csv(h.OUT/'mp_operator_seed_block_metrics_64new.csv',index=False)
        h.infer_contrasts(w,'mp-64new').to_csv(h.OUT/'mp_operator_contrasts_64new.csv',index=False)
        print('Regenerated causal specificity aggregation and inference from all',len(c),'raw rows',flush=True)
    elif a.action=='core-controls':
        import pandas as pd
        from round2.mp_migration import run_core_and_screen as d
        jobs=[(p,r) for p in [round(x/10,1) for x in range(1,11)] for r in range(1,20)]
        with ProcessPoolExecutor(max_workers=a.workers) as pool:
            fs={pool.submit(d.core_job,'control',p,r):(p,r) for p,r in jobs}
            for i,f in enumerate(as_completed(fs),1):
                p,r=fs[f];pd.DataFrame(f.result()).to_csv(d.CORE_OUT/'blocks'/f'control_p{p:.1f}_r{r:02d}.csv',index=False)
                if i%20==0 or i==len(jobs):print('Control completion',i,len(jobs),flush=True)
        d.run_core(a.workers)
    elif a.action=='stage-d': run_stage_d(a.workers)
    elif a.action=='landscapes':
        from round2.mp_migration import run_affinity_landscape_generality as l
        l._original_baseline_custom=l.baseline_custom
        l.baseline_custom=archive_landscape_baseline
        l.run(a.workers)
    else:
        from round2.mp_migration import run_core_p1_frontier as f
        f.OUT.mkdir(parents=True,exist_ok=True)
        coords=f.compute_coordinates(a.workers)
        cont=f.run_continuations(a.workers)
        if cont is not None: f.analyze(cont,coords)

if __name__=='__main__':main()
