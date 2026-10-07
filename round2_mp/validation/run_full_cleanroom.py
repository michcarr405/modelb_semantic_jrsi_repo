"""Replay every Round-2 scientific evidence family in a new copied tree.

The frozen R1 foundation, final Stage-D design selection, and publication display
templates are immutable inputs. Existing R2 regeneration outputs are excluded.
"""
from __future__ import annotations
import argparse, os, shutil, subprocess, sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination',type=Path,required=True);ap.add_argument('--workers',type=int,default=8);a=ap.parse_args()
    target=a.destination.resolve()
    if target.exists():raise SystemExit('Destination must not exist; existing files are never overwritten.')
    if target.is_relative_to(REPO):raise SystemExit('Destination must be outside the source repository.')
    def exclude(directory,names):
        relative=Path(directory).relative_to(REPO)
        blocked={'.git','__pycache__','.pytest_cache','.venv'}
        if relative==Path('round2/mp_migration'):blocked.add('results')
        if relative==Path('round2_mp'):blocked.update({'regenerated','cleanroom_outputs'})
        return [n for n in names if n in blocked]
    shutil.copytree(REPO,target,ignore=exclude)
    (target/'round2_mp/cleanroom_outputs').mkdir()
    selection=target/'round2/mp_migration/results/stage_c_n8';selection.mkdir(parents=True)
    shutil.copy2(target/'round2_mp/recovered_scientific_freeze/results/stage_c/stage_d_selected_final_mp.csv',selection/'stage_d_selected_final_mp.csv')
    logdir=target/'round2_mp/validation/fresh_run_logs';logdir.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env['OPENBLAS_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1'
    runner='round2_mp/validation/integrated_regeneration.py'
    commands=[
      ('foundation',[sys.executable,'-m','pytest','-q','tests']),
      ('core',[sys.executable,'round2/mp_migration/run_core_and_screen.py','core','--workers',str(a.workers)]),
      ('control_levels',[sys.executable,runner,'core-controls','--workers',str(a.workers)]),
      ('screen',[sys.executable,'round2/mp_migration/run_core_and_screen.py','screen','--workers',str(a.workers)]),
      ('stage_c',[sys.executable,'round2/mp_migration/run_stage_c.py','run','--workers',str(a.workers),'--limit','100']),
      ('stage_c_finalize',[sys.executable,'round2/mp_migration/run_stage_c.py','finalize']),
      ('stage_d',[sys.executable,runner,'stage-d','--workers',str(a.workers)]),
      ('frontier',[sys.executable,runner,'frontier','--workers',str(a.workers)]),
      ('landscapes',[sys.executable,runner,'landscapes','--workers',str(a.workers)]),
      ('causal_specificity',[sys.executable,runner,'hp','--workers',str(a.workers)]),
      ('expected_marginals',[sys.executable,'round2_mp/cleanroom_scripts/make_marginal_diagnostics_rc.py']),
      ('empirical_marginals',[sys.executable,'round2_mp/cleanroom_scripts/empirical_marginal_validation_rc.py']),
      ('affinity_hashes',[sys.executable,'round2_mp/validation/verify_affinity_matrix_hashes.py']),
      ('final_causal_seed_ledger',[sys.executable,'round2_mp/validation/build_causal_seed_ledger.py']),
      ('integrated_validation',[sys.executable,'round2_mp/validation/validate_integrated.py']),
    ]
    for name,command in commands:
        print('Running',name,flush=True)
        with (logdir/f'{name}.log').open('w') as f:
            result=subprocess.run(command,cwd=target,env=env,stdout=f,stderr=subprocess.STDOUT)
        if result.returncode:raise SystemExit(f'{name} failed ({result.returncode}); see {logdir/name}.log')
    print('Complete integrated regeneration:',target,flush=True)

if __name__=='__main__':main()
