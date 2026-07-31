import argparse
import json

from modelb_semantic_repo.phase5 import Phase5Settings, run_phase5_production

parser = argparse.ArgumentParser(description="Run prespecified Phase 5 causal-specificity controls")
parser.add_argument("--outdir", default="results/phase5_causal_specificity")
parser.add_argument("--phase4-dir", default="results/phase4_core")
parser.add_argument("--workers", type=int, default=4)
parser.add_argument("--no-resume", action="store_true")
args = parser.parse_args()

settings = Phase5Settings(workers=args.workers)
gate = run_phase5_production(
    args.outdir,
    phase4_dir=args.phase4_dir,
    settings=settings,
    resume=not args.no_resume,
)
print(json.dumps(gate, indent=2))
