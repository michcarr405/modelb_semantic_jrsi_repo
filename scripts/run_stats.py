import argparse
from pathlib import Path
from modelb_semantic_repo.stats import (
    build_baseline_stats,
    build_viability_gap_table,
    build_robustness_table,
    build_intervention_tests,
    build_method_ablation_tests,
    build_method_summary_table,
    build_viability_definition_tests,
    build_entropy_state_definition_summary,
    build_entropy_state_definition_tests,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results-dir', required=True)
    ap.add_argument('--stats-dir', required=True)
    args = ap.parse_args()
    out = Path(args.stats_dir)
    out.mkdir(parents=True, exist_ok=True)
    build_baseline_stats(args.results_dir).to_csv(out / 'baseline_permutation_tests.csv', index=False)
    build_viability_gap_table(args.results_dir).to_csv(out / 'viability_gap_table.csv', index=False)
    build_robustness_table(args.results_dir).to_csv(out / 'robustness_table.csv', index=False)
    build_intervention_tests(args.results_dir).to_csv(out / 'intervention_selective_vs_control_tests_primary_no_kmeans.csv', index=False)
    build_method_ablation_tests(args.results_dir).to_csv(out / 'method_ablation_kmeans_vs_primary_tests.csv', index=False)
    build_method_summary_table(args.results_dir).to_csv(out / 'method_viability_summary.csv', index=False)
    build_viability_definition_tests(args.results_dir).to_csv(out / 'viability_definition_dependence_tests.csv', index=False)
    build_entropy_state_definition_summary(args.results_dir).to_csv(out / 'entropy_state_definition_summary.csv', index=False)
    build_entropy_state_definition_tests(args.results_dir).to_csv(out / 'entropy_state_definition_selective_vs_control_tests.csv', index=False)
    print(f'Wrote stats to {out}')


if __name__ == '__main__':
    main()
