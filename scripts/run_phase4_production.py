#!/usr/bin/env python3
import argparse
import json
from modelb_semantic_repo.phase4 import Phase4Settings, run_phase4_production

parser = argparse.ArgumentParser()
parser.add_argument("--outdir", default="results/phase4_core")
parser.add_argument("--continuations", type=int, required=True)
parser.add_argument("--horizon", type=int, required=True)
parser.add_argument("--workers", type=int, default=4)
parser.add_argument("--no-resume", action="store_true")
args = parser.parse_args()
settings = Phase4Settings(
    continuation_count=args.continuations,
    intervention_horizon=args.horizon,
    workers=args.workers,
)
gate = run_phase4_production(args.outdir, settings=settings, resume=not args.no_resume)
print(json.dumps(gate, indent=2))
