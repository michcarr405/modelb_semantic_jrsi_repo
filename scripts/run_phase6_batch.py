#!/usr/bin/env python3
import argparse,json
from modelb_semantic_repo.phase6 import prepare,run_batch,prepare_c,select_d,confirm_batch,finalize
p=argparse.ArgumentParser();p.add_argument('action');p.add_argument('--outdir',default='results/phase6_generality');p.add_argument('--batch',type=int,default=20);a=p.parse_args()
if a.action=='prepare':prepare(a.outdir);r={'prepared':True}
elif a.action in ['A','B1','B2','C']:x,y=run_batch(a.action,a.outdir,a.batch);r={'completed':x,'total':y,'remaining':y-x}
elif a.action=='prepare-c':prepare_c(a.outdir);r={'prepared_c':True}
elif a.action=='select-d':select_d(a.outdir);r={'selected_d':True}
elif a.action=='D':x,y=confirm_batch(a.outdir,a.batch);r={'completed':x,'total':y,'remaining':y-x}
else:r=finalize(a.outdir)
print(json.dumps(r,indent=2))
