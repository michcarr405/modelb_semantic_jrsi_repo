import argparse
from modelb_semantic_repo.pipeline import run_pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['fast', 'medium', 'paper'], default='paper')
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()
    run_pipeline(args.mode, args.outdir, args.seed)
    print(f'Wrote results to {args.outdir}')


if __name__ == '__main__':
    main()
