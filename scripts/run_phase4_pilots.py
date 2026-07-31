#!/usr/bin/env python3
import argparse
import json
from modelb_semantic_repo.phase4 import run_phase4_pilots

parser = argparse.ArgumentParser()
parser.add_argument("--outdir", default="validation/phase4_pilots")
parser.add_argument("--workers", type=int, default=4)
args = parser.parse_args()
summary = run_phase4_pilots(args.outdir, workers=args.workers)
print(json.dumps(summary, indent=2))
