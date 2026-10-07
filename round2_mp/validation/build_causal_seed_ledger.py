"""Record final 64-new causal-specificity RNG specifications without guessing seeds."""
from pathlib import Path
import csv, hashlib, json, sys
import pandas as pd
REPO=Path(__file__).resolve().parents[2];sys.path.insert(0,str(REPO/'src'))
from modelb_semantic_repo.rng import _stable_entropy
R2=REPO/'round2_mp';OUT=R2/'provenance';raw=R2/'causal_specificity_high_continuation/results/continuation_level_results_64new.csv'
rows=[]
def add(record,kind,root,purpose,keys,count):
    spec={'root_seed':root,'purpose':purpose,'keys':keys}
    canonical=json.dumps(spec,sort_keys=True,separators=(',',':'))
    rows.append(dict(record_id=record,stream_kind=kind,root_seed=root,purpose=purpose,keys_json=json.dumps(keys),
                     seed_sequence_entropy_json=json.dumps([root&0xffffffff,*_stable_entropy(purpose,*keys)]),
                     specification_sha256=hashlib.sha256(canonical.encode()).hexdigest(),replication_count=count,
                     source='run_high_precision_campaign.py',status='RECOVERED_FINAL_PRODUCTION_SPEC'))
for r in pd.read_csv(raw).itertuples():
    record=f'{r.condition}_block{r.seed_block:02d}_realization{r.realization}_c{r.continuation_index:02d}'
    keys=[r.pairing_baseline_replicate,int(r.continuation_index)]
    add(record,'observation',2026073104,'continuation-observation',keys,36)
    add(record,'propagation',2026073104,'continuation-propagation',keys,36)
    if r.evaluation_topology_id=='temporally_unstable':
        add(record,'topology_schedule',2026073105,'phase5-unstable-topology-continuation',keys,36)
contrasts=['full_minus_neutral','full_minus_reduced','native_minus_affinity_reassigned','native_minus_topology_mismatch','alternative_native_minus_cross','stable_minus_unstable']
for c in contrasts:
    add(c,'inference_randomization',2026100202,'mp-64new-paired-randomization',[c,0],9999)
    add(c,'inference_bootstrap',2026100202,'mp-64new-paired-bootstrap',[c,0],2000)
p=OUT/'FINAL_64NEW_CAUSAL_SPECIFICITY_SEED_LEDGER.csv'
with p.open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print(len(rows),'final causal-specificity stream specifications')
