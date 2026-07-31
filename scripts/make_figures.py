import argparse
from modelb_semantic_repo.figures import make_all_figures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results-dir', required=True)
    ap.add_argument('--figures-dir', required=True)
    args = ap.parse_args()
    make_all_figures(args.results_dir, args.figures_dir)
    print(f'Wrote figures to {args.figures_dir}')


if __name__ == '__main__':
    main()
