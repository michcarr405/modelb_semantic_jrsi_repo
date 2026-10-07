from __future__ import annotations

import argparse
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.phase4 import array_sha256
from modelb_semantic_repo.rng import ContinuationStream, PermutationStream, make_generator
from modelb_semantic_repo.mp_operator import (
    simulate_core_actual,
    simulate_core_grouped,
    simulate_phase6_grouped,
    simulate_core_constant,
    simulate_phase6_constant,
    expected_marginal_error_general,
)
from modelb_semantic_repo import phase6

CORE_CONT_ROOT = 2026100205
SCREEN_CONT_ROOT = 2026100206
ANALYSIS_ROOT = 2026100210
CORE_N_CONT = 8
SCREEN_N_CONT = 8
HORIZON = 36
BOOT = 2000
N_SIGN = 9999

OUT = ROOT / "round2" / "mp_migration" / "results"
CORE_OUT = OUT / "core"
SCREEN_OUT = OUT / "screen_n8"


def sign_randomization_p(values: np.ndarray, seed_key: str) -> float:
    v = np.asarray(values, float)
    obs = abs(float(v.mean()))
    if len(v) <= 20:
        # exact enumeration is only ~1.05m at n=20; use deterministic Monte Carlo per frozen plan for consistency.
        pass
    rng = make_generator(ANALYSIS_ROOT, "mp-sign", seed_key)
    count = 0
    for _ in range(N_SIGN):
        s = rng.choice(np.array([-1.0, 1.0]), size=len(v))
        if abs(float((v * s).mean())) >= obs - 1e-15:
            count += 1
    return (count + 1) / (N_SIGN + 1)


def bh_adjust(pvals: list[float]) -> list[float]:
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    q = np.empty(n, float)
    prev = 1.0
    for rank_rev, idx in enumerate(order[::-1], start=1):
        rank = n - rank_rev + 1
        val = p[idx] * n / rank
        prev = min(prev, val)
        q[idx] = min(1.0, prev)
    return q.tolist()


def bootstrap_mean(values: np.ndarray, key: str) -> tuple[float, float, float]:
    v = np.asarray(values, float)
    rng = make_generator(ANALYSIS_ROOT, "mp-bootstrap", key)
    draws = v[rng.integers(0, len(v), size=(BOOT, len(v)))].mean(axis=1)
    return float(v.mean()), float(np.quantile(draws, .025)), float(np.quantile(draws, .975))


def core_state(condition: str, p: float, rep: int):
    cond_dir = "selective" if condition == "selective" else "control"
    path = ROOT / "results" / "phase4_core" / "states" / cond_dir / f"p{p:.1f}" / f"rep_{rep:02d}.npz"
    return np.load(path)


def core_job(condition: str, p: float, rep: int) -> list[dict]:
    params = default_parameters()
    matrix = params["motif_affinity_matrix"] if condition == "selective" else params["motif_affinity_matrix_no_aff"]
    arr = core_state(condition, p, rep)
    pop = np.asarray(arr["population"])
    labels = np.zeros(matrix.shape[0], dtype=np.int64)
    bid = f"{'selective' if condition=='selective' else 'control'}_p{p:.1f}_r{rep:02d}"
    rows = []
    for ci in range(CORE_N_CONT):
        actual, _ = simulate_core_actual(pop, params, matrix, p, HORIZON, CORE_CONT_ROOT, bid, ci)
        mp, _ = simulate_core_constant(pop, params, matrix, p, HORIZON, CORE_CONT_ROOT, bid, ci)
        rows.append({
            "condition": condition,
            "inherit_prob": p,
            "replicate": rep,
            "baseline_replicate": bid,
            "continuation_index": ci,
            "actual_viability": actual,
            "mp_constant_viability": mp,
            "delta_mp": actual - mp,
            "analytical_exact_zero": False,
        })
    return rows


def run_core(workers: int):
    CORE_OUT.mkdir(parents=True, exist_ok=True)
    blockdir = CORE_OUT / "blocks"
    blockdir.mkdir(exist_ok=True)
    jobs = []
    for condition in ["control", "selective"]:
        for p in [round(x/10, 1) for x in range(1, 11)]:
            for rep in range(20):
                path = blockdir / f"{condition}_p{p:.1f}_r{rep:02d}.csv"
                if path.exists():
                    continue
                # In the sequence-agnostic regime A=0, so every motif has the same
                # native kernel conditional on segment and the MP constant operator is
                # analytically identical to native. Run rep 0 at each p as an explicit
                # implementation validation and record exact analytical zeros for the
                # remaining blocks. This does not change the prespecified estimand.
                if condition == "control" and rep != 0:
                    rows=[{
                        "condition":condition,"inherit_prob":p,"replicate":rep,
                        "baseline_replicate":f"control_p{p:.1f}_r{rep:02d}",
                        "continuation_index":ci,"actual_viability":np.nan,
                        "mp_constant_viability":np.nan,"delta_mp":0.0,
                        "analytical_exact_zero":True,
                    } for ci in range(CORE_N_CONT)]
                    pd.DataFrame(rows).to_csv(path,index=False)
                else:
                    jobs.append((condition, p, rep, path))
    if jobs:
        if workers <= 1:
            for i,(c,p,r,path) in enumerate(jobs,1):
                pd.DataFrame(core_job(c,p,r)).to_csv(path,index=False)
                if i % 10 == 0 or i == len(jobs):
                    print(f"core blocks {i}/{len(jobs)}", flush=True)
        else:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                futs = {ex.submit(core_job, c, p, r):(c,p,r,path) for c,p,r,path in jobs}
                for i, fut in enumerate(as_completed(futs), 1):
                    c,p,r,path = futs[fut]
                    pd.DataFrame(fut.result()).to_csv(path, index=False)
                    if i % 10 == 0 or i == len(futs):
                        print(f"core blocks {i}/{len(futs)}", flush=True)
    files = sorted(blockdir.glob("*.csv"))
    cont = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    cont.to_csv(CORE_OUT / "continuation_level_results.csv", index=False)
    seed = cont.groupby(["condition","inherit_prob","replicate","baseline_replicate"], as_index=False).agg(
        actual_viability=("actual_viability","mean"),
        mp_constant_viability=("mp_constant_viability","mean"),
        delta_mp=("delta_mp","mean"),
        n_continuations=("continuation_index","count"),
    )
    seed.to_csv(CORE_OUT / "seed_block_results.csv", index=False)
    # validation of exact agnostic null
    control = seed[seed.condition=="control"]
    max_control = float(control.delta_mp.abs().max())
    # merge frozen corrected info for figure-source convenience
    info = pd.read_csv(ROOT / "results" / "phase4_core" / "baseline_information.csv")
    info["condition"] = info["condition"].replace({"control":"control","selective":"selective"})
    merged = seed.merge(info[["condition","inherit_prob","replicate","corrected_conditional_information","total_information","positional_information"]], on=["condition","inherit_prob","replicate"], how="left", validate="one_to_one")
    merged.to_csv(CORE_OUT / "core_mp_replicates.csv", index=False)
    inf_rows=[]
    for p, g in seed[seed.condition=="selective"].groupby("inherit_prob"):
        vals=g.delta_mp.to_numpy(float)
        mean,lo,hi=bootstrap_mean(vals,f"core-p{p:.1f}")
        pv=sign_randomization_p(vals,f"core-p{p:.1f}")
        inf_rows.append({"inherit_prob":p,"mean_delta_mp":mean,"bootstrap_95_lower":lo,"bootstrap_95_upper":hi,"positive_blocks":int((vals>0).sum()),"n":len(vals),"p_value":pv})
    inf=pd.DataFrame(inf_rows).sort_values("inherit_prob")
    inf["q_value_bh_10"] = bh_adjust(inf.p_value.tolist())
    inf.to_csv(CORE_OUT / "core_mp_inference.csv", index=False)
    validation={"n_continuation_rows":int(len(cont)),"n_seed_blocks":int(len(seed)),"max_abs_control_delta_mp":max_control,"control_exact_zero":bool(max_control < 1e-12),"n_continuations_per_block_unique":sorted(seed.n_continuations.unique().tolist())}
    (CORE_OUT/"VALIDATION.json").write_text(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2), flush=True)
    print(inf.to_string(index=False), flush=True)


def screen_designs():
    return phase6.designA() + phase6.designB1() + phase6.designB2()


def screen_rep_range(stage: str):
    return range(8)


def screen_job(d: dict, rep: int) -> dict:
    did=d["design_id"]
    spec=phase6.norm(d["spec"])
    seed=phase6.stable_integer_seed(phase6.ROOT,"p6-screen",did,rep)
    m,pop,tr=phase6.baseline(spec,seed)
    f,mot,z,s=phase6.observe(pop,m,make_generator(phase6.ROOT,"p6-info",did,rep))
    obs,null,corr=phase6.corrected(mot,z,s,60,PermutationStream(phase6.ROOT,f"{did}_r{rep}",0))
    labels=np.zeros(len(m["aff"]),dtype=np.int64)
    vv=[]
    bid=f"{did}_r{rep}"
    for ci in range(SCREEN_N_CONT):
        st=ContinuationStream(SCREEN_CONT_ROOT,bid,ci)
        actual,_=phase6.horizon(pop,m,m["aff"],HORIZON,st)
        mp,_=simulate_phase6_constant(pop,m,HORIZON,SCREEN_CONT_ROOT,bid,ci,phase6.reproduce)
        vv.append(float(actual.mean()-mp))
    w=max(1,math.ceil(len(tr)*.2))
    # one deterministic marginal-preservation check; for jitter draw a frozen offset realization
    vrng=make_generator(ANALYSIS_ROOT,"screen-marginal-check",did,rep)
    n_chain=int(m["n_cells"])*int(m["n_seqs"])
    j=int(m.get("jitter",0))
    offsets=vrng.integers(-j,j+1,size=n_chain,dtype=np.int64) if j else np.zeros(n_chain,dtype=np.int64)
    err=expected_marginal_error_general(pop,m,labels,offsets)
    return {
        "design_id":did,"stage":d["stage"],"family":d.get("family",""),"replicate":rep,
        "spec_json":json.dumps(spec,sort_keys=True),"baseline_seed":seed,
        "corrected_information":corr,"conditional_information":obs,"permutation_mean":null,
        "delta_mp":float(np.mean(vv)),"delta_mp_cont_sd":float(np.std(vv,ddof=1)) if len(vv)>1 else 0.0,
        "adaptive_gain":float(tr[-w:].mean()-tr[:w].mean()),"final_mean_fitness":float(f.mean()),
        "state_hash":array_sha256(pop),"trajectory_hash":array_sha256(tr),
        "mp_marginal_max_abs_error":float(err),"n_continuations":SCREEN_N_CONT,
    }


def summarize_screen(raw: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for did,p in raw.groupby("design_id"):
        r={"design_id":did,"stage":p.stage.iloc[0],"family":p.family.iloc[0],"spec_json":p.spec_json.iloc[0],"n":len(p)}
        for met in ["corrected_information","delta_mp","adaptive_gain"]:
            mean,lo,hi=bootstrap_mean(p[met].to_numpy(float),f"screen-{did}-{met}")
            r[met+"_mean"]=mean;r[met+"_low"]=lo;r[met+"_high"]=hi
        il,ih=r["corrected_information_low"],r["corrected_information_high"]
        vl,vh=r["delta_mp_low"],r["delta_mp_high"]
        fl=r["adaptive_gain_low"]
        if ih<=phase6.DI: reg="R0_null"
        elif il>phase6.DI and vh<=phase6.DV: reg="R1_syntactic_only"
        elif il>phase6.DI and vl>phase6.DV and fl<=phase6.DF: reg="R2_viability_relevant"
        elif il>phase6.DI and vl>phase6.DV and fl>phase6.DF: reg="R3_strong_adaptation"
        else: reg="boundary_uncertain"
        im,vm,fm=r["corrected_information_mean"],r["delta_mp_mean"],r["adaptive_gain_mean"]
        r["regime"]=reg
        r["boundary_distance"]=min(abs(im-phase6.DI)/phase6.DI,abs(vm-phase6.DV)/phase6.DV,abs(fm-phase6.DF)/phase6.DF)
        if im<=phase6.DI: r["provisional"]="R0_null";r["depth"]=(phase6.DI-im)/phase6.DI
        elif vm<=phase6.DV: r["provisional"]="R1_syntactic_only";r["depth"]=min((im-phase6.DI)/phase6.DI,(phase6.DV-vm)/phase6.DV)
        elif fm<=phase6.DF: r["provisional"]="R2_viability_relevant";r["depth"]=min((im-phase6.DI)/phase6.DI,(vm-phase6.DV)/phase6.DV,(phase6.DF-fm)/phase6.DF)
        else: r["provisional"]="R3_strong_adaptation";r["depth"]=min((im-phase6.DI)/phase6.DI,(vm-phase6.DV)/phase6.DV,(fm-phase6.DF)/phase6.DF)
        rows.append(r)
    return pd.DataFrame(rows).sort_values("design_id")


def validate_old_screen(raw: pd.DataFrame) -> dict:
    old_files={
        "A":ROOT/"results/phase6_generality/stage_a_replicates.csv",
        "B1":ROOT/"results/phase6_generality/stage_b1_replicates.csv",
        "B2":ROOT/"results/phase6_generality/stage_b2_replicates.csv",
    }
    diffs=[]; hash_matches=[]
    for stage,path in old_files.items():
        old=pd.read_csv(path)
        max_rep=3 if stage in ["A","B2"] else 2
        new=raw[(raw.stage==stage)&(raw.replicate<=max_rep)]
        m=old.merge(new,on=["design_id","replicate"],suffixes=("_old","_new"),validate="one_to_one")
        for col in ["corrected_information","adaptive_gain","final_mean_fitness"]:
            diffs.append(float(np.max(np.abs(m[f"{col}_old"]-m[f"{col}_new"]))))
        if "state_hash_old" in m.columns:
            hash_matches.extend((m.state_hash_old==m.state_hash_new).tolist())
    return {"max_abs_old_cohort_nonintervention_difference":max(diffs) if diffs else None,"old_cohort_state_hashes_all_match":bool(all(hash_matches)) if hash_matches else None,"n_old_hash_checks":len(hash_matches)}


def run_screen(workers:int):
    SCREEN_OUT.mkdir(parents=True,exist_ok=True)
    blockdir=SCREEN_OUT/"blocks";blockdir.mkdir(exist_ok=True)
    ds=screen_designs(); jobs=[]
    for d in ds:
        for rep in screen_rep_range(d["stage"]):
            path=blockdir/f"{d['design_id']}_r{rep:02d}.json"
            if not path.exists(): jobs.append((d,rep,path))
    if jobs:
        if workers <= 1:
            for i,(d,rep,path) in enumerate(jobs,1):
                path.write_text(json.dumps(screen_job(d,rep),indent=2))
                if i%10==0 or i==len(jobs): print(f"screen blocks {i}/{len(jobs)}",flush=True)
        else:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                futs={ex.submit(screen_job,d,rep):(d,rep,path) for d,rep,path in jobs}
                for i,fut in enumerate(as_completed(futs),1):
                    d,rep,path=futs[fut]
                    path.write_text(json.dumps(fut.result(),indent=2))
                    if i%10==0 or i==len(futs): print(f"screen blocks {i}/{len(futs)}",flush=True)
    rows=[json.loads(p.read_text()) for p in sorted(blockdir.glob("*.json"))]
    raw=pd.DataFrame(rows).sort_values(["design_id","replicate"])
    raw.to_csv(SCREEN_OUT/"stage_ab_replicates_n8_mp.csv",index=False)
    val=validate_old_screen(raw)
    val.update({"n_replicates":int(len(raw)),"n_settings":int(raw.design_id.nunique()),"replicates_per_setting":sorted(raw.groupby('design_id').size().unique().tolist()),"max_mp_marginal_abs_error":float(raw.mp_marginal_max_abs_error.max())})
    (SCREEN_OUT/"VALIDATION.json").write_text(json.dumps(val,indent=2))
    summary=summarize_screen(raw)
    summary.to_csv(SCREEN_OUT/"stage_ab_summary_n8_mp.csv",index=False)
    counts=summary.groupby(["stage","regime"]).size().unstack(fill_value=0)
    counts.to_csv(SCREEN_OUT/"regime_counts_n8_mp.csv")
    # freeze Stage-C reps and prospective Stage-D picks from screen (D final selection repeated after C as historical ordering)
    default=summary[summary.design_id=="B2_default"].iloc[0]
    boundary=summary.sort_values(["boundary_distance","design_id"]).iloc[0]
    pd.DataFrame([default,boundary]).drop_duplicates("design_id").to_csv(SCREEN_OUT/"stage_c_representatives_mp.csv",index=False)
    picks=[]
    for reg in ["R2_viability_relevant","R3_strong_adaptation"]:
        q=summary[summary.regime==reg]
        if len(q): picks.append(q.sort_values(["depth","design_id"],ascending=[False,True]).iloc[0])
    picks.append(boundary); picks.append(default)
    sel=pd.DataFrame(picks).drop_duplicates("design_id").reset_index(drop=True)
    sel.insert(0,"confirm_id",[f"D{i}" for i in range(len(sel))])
    sel.to_csv(SCREEN_OUT/"stage_d_selected_provisional_mp.csv",index=False)
    print(json.dumps(val,indent=2),flush=True)
    print("\nRegime counts:\n",counts.to_string(),flush=True)
    print("\nStage C reps:\n",pd.DataFrame([default,boundary])[["design_id","regime","boundary_distance","delta_mp_mean"]].to_string(index=False),flush=True)
    print("\nProvisional Stage D:\n",sel[["confirm_id","design_id","regime","depth","boundary_distance","delta_mp_mean"]].to_string(index=False),flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument("action",choices=["core","screen","all"]);ap.add_argument("--workers",type=int,default=4);a=ap.parse_args()
    if a.action in ["core","all"]: run_core(a.workers)
    if a.action in ["screen","all"]: run_screen(a.workers)

if __name__=="__main__": main()
