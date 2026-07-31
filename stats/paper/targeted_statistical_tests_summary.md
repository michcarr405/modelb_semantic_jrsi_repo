# Targeted statistical tests summary

Source CSV: `targeted_statistical_tests.csv`

These tests use cached data only; no simulations were rerun.


## omnibus_regime_by_fidelity

| metric        | condition | comparison                        | inherit_prob | effect   | statistic | p_value  | q_value | ci_low    | ci_high    | n   |
| ------------- | --------- | --------------------------------- | ------------ | -------- | --------- | -------- | ------- | --------- | ---------- | --- |
| delta_mi      | all       | C(condition):C(inherit_prob)      | nan          | NA       | 193.338   | 1.00e-04 | NA      | NA        | NA         | 400 |
| delta_mi      | all       | condition_x_linear_fidelity_slope | nan          | -0.10654 | -3.24921  | 0.0012   | NA      | -0.170807 | -0.0422738 | 400 |
| delta_fitness | all       | C(condition):C(inherit_prob)      | nan          | NA       | 67.3518   | 1.00e-04 | NA      | NA        | NA         | 400 |
| delta_fitness | all       | condition_x_linear_fidelity_slope | nan          | 3.32103  | 6.95694   | 3.48e-12 | NA      | 2.3854    | 4.25666    | 400 |



## empirical_transition_diagnostic

| metric                    | condition | comparison                                   | inherit_prob | effect    | statistic | p_value | q_value | ci_low | ci_high | n   |
| ------------------------- | --------- | -------------------------------------------- | ------------ | --------- | --------- | ------- | ------- | ------ | ------- | --- |
| delta_mi                  | selective | piecewise_linear_final_outcome               | nan          | 1.05947   | 0.8       | NA      | NA      | 0.8    | 0.8     | 200 |
| delta_fitness             | selective | piecewise_linear_final_outcome               | nan          | 46.6656   | 0.9       | NA      | NA      | 0.9    | 0.9     | 200 |
| delta_mi                  | control   | piecewise_linear_final_outcome               | nan          | 1.69616   | 0.8       | NA      | NA      | 0.8    | 0.9     | 200 |
| delta_fitness             | control   | piecewise_linear_final_outcome               | nan          | 2.46752   | 0.2       | NA      | NA      | 0.2    | 0.9     | 200 |
| semantic_info_mean        | selective | piecewise_linear_summary_excess_over_control | nan          | 0.929434  | 0.8       | NA      | NA      | NA     | NA      | 10  |
| value_of_information_mean | selective | piecewise_linear_summary_excess_over_control | nan          | 54.941    | 0.9       | NA      | NA      | NA     | NA      | 10  |
| semantic_efficiency_mean  | selective | piecewise_linear_summary_excess_over_control | nan          | 0.117131  | 0.8       | NA      | NA      | NA     | NA      | 10  |
| semantic_info_mean        | control   | piecewise_linear_summary_excess_over_control | nan          | 0         | 0.2       | NA      | NA      | NA     | NA      | 10  |
| value_of_information_mean | control   | piecewise_linear_summary_excess_over_control | nan          | -0.311029 | 0.9       | NA      | NA      | NA     | NA      | 10  |
| semantic_efficiency_mean  | control   | piecewise_linear_summary_excess_over_control | nan          | 0         | 0.2       | NA      | NA      | NA     | NA      | 10  |



## replicate_level_intervention_contrast

| metric                      | condition            | comparison       | inherit_prob | effect   | statistic | p_value  | q_value  | ci_low   | ci_high  | n  |
| --------------------------- | -------------------- | ---------------- | ------------ | -------- | --------- | -------- | -------- | -------- | -------- | -- |
| mean_intervention_viability | selective_vs_control | inherit_prob=0.1 | 0.1          | 0.358847 | 144       | 1.00e-04 | 1.00e-04 | 0.357188 | 0.360154 | 24 |
| mean_intervention_viability | selective_vs_control | inherit_prob=0.2 | 0.2          | 0.353028 | 144       | 1.00e-04 | 1.00e-04 | 0.350405 | 0.353558 | 24 |
| mean_intervention_viability | selective_vs_control | inherit_prob=0.3 | 0.3          | 0.332237 | 144       | 1.00e-04 | 1.00e-04 | 0.330792 | 0.333623 | 24 |
| mean_intervention_viability | selective_vs_control | inherit_prob=0.4 | 0.4          | 0.332152 | 144       | 1.00e-04 | 1.00e-04 | 0.331139 | 0.334422 | 24 |
| mean_intervention_viability | selective_vs_control | inherit_prob=0.5 | 0.5          | 0.286353 | 142       | 1.00e-04 | 1.00e-04 | 0.284036 | 0.287098 | 24 |
| mean_intervention_viability | selective_vs_control | inherit_prob=0.6 | 0.6          | 0.365947 | 144       | 1.00e-04 | 1.00e-04 | 0.363938 | 0.366988 | 24 |
| mean_intervention_viability | selective_vs_control | inherit_prob=0.7 | 0.7          | 0.302019 | 144       | 1.00e-04 | 1.00e-04 | 0.30119  | 0.303521 | 24 |
| mean_intervention_viability | selective_vs_control | inherit_prob=0.8 | 0.8          | 0.348373 | 144       | 1.00e-04 | 1.00e-04 | 0.346047 | 0.348659 | 24 |
| mean_intervention_viability | selective_vs_control | inherit_prob=0.9 | 0.9          | 0.398178 | 144       | 1.00e-04 | 1.00e-04 | 0.396734 | 0.399594 | 24 |
| mean_intervention_viability | selective_vs_control | inherit_prob=1.0 | 1.0          | 0.566827 | 144       | 1.00e-04 | 1.00e-04 | 0.564221 | 0.568019 | 24 |



## frontier_regime_contrast

| metric                    | condition            | comparison                     | inherit_prob | effect  | statistic | p_value | q_value | ci_low  | ci_high | n  |
| ------------------------- | -------------------- | ------------------------------ | ------------ | ------- | --------- | ------- | ------- | ------- | ------- | -- |
| frontier_max_viability    | selective_vs_control | paired_by_inheritance_fidelity | nan          | 2.08539 | 2.08539   | 0.0029  | NA      | 1.77025 | 2.65108 | 10 |
| actual_viability_mean     | selective_vs_control | paired_by_inheritance_fidelity | nan          | 6.42292 | 6.42292   | 0.0029  | NA      | 5.78149 | 7.51977 | 10 |
| value_of_information_mean | selective_vs_control | paired_by_inheritance_fidelity | nan          | 6.40271 | 6.40271   | 0.0029  | NA      | 5.71115 | 7.62355 | 10 |
| actual_minus_frontier_gap | selective_vs_control | paired_by_inheritance_fidelity | nan          | 4.33752 | 4.33752   | 0.0029  | NA      | 3.98934 | 4.89222 | 10 |



## method_ablation_summary_contrast

| metric                   | condition                     | comparison                           | inherit_prob | effect     | statistic  | p_value | q_value | ci_low     | ci_high     | n  |
| ------------------------ | ----------------------------- | ------------------------------------ | ------------ | ---------- | ---------- | ------- | ------- | ---------- | ----------- | -- |
| semantic_info_mean       | selective_excess_over_control | all_methods_diagnostic_minus_primary | nan          | -0.0363228 | -0.0363228 | 0.1765  | NA      | -0.0715831 | -0.00531596 | 10 |
| frontier_max_viability   | selective_excess_over_control | all_methods_diagnostic_minus_primary | nan          | 4.21315    | 4.21315    | 0.0029  | NA      | 3.53175    | 5.22649     | 10 |
| semantic_efficiency_mean | selective_excess_over_control | all_methods_diagnostic_minus_primary | nan          | -0.092627  | -0.092627  | 0.1765  | NA      | -0.176965  | -0.0171315  | 10 |
| semantic_info_mean       | selective_excess_over_control | kmeans_profile_minus_primary         | nan          | -0.0516934 | -0.0516934 | 0.0029  | NA      | -0.0823045 | -0.0287672  | 10 |
| frontier_max_viability   | selective_excess_over_control | kmeans_profile_minus_primary         | nan          | 4.21315    | 4.21315    | 0.0029  | NA      | 3.53175    | 5.22649     | 10 |
| semantic_efficiency_mean | selective_excess_over_control | kmeans_profile_minus_primary         | nan          | -0.1507    | -0.1507    | 0.0029  | NA      | -0.20972   | -0.105756   | 10 |



## entropy_state_specificity

| metric             | condition                  | comparison                                                                | inherit_prob | effect      | statistic   | p_value | q_value | ci_low   | ci_high     | n  |
| ------------------ | -------------------------- | ------------------------------------------------------------------------- | ------------ | ----------- | ----------- | ------- | ------- | -------- | ----------- | -- |
| semantic_info_mean | selective                  | excess_over_control_minus_negative_fitness_distribution_entropy           | nan          | 0.251203    | 0.251203    | 0.0020  | NA      | 0.216582 | 0.300974    | 10 |
| semantic_info_mean | selective                  | excess_over_control_minus_negative_local_metabolite_configuration_entropy | nan          | 0.251276    | 0.251276    | 0.0020  | NA      | 0.216582 | 0.301191    | 10 |
| semantic_info_mean | selective                  | excess_over_control_minus_negative_adjacency_state_entropy                | nan          | 0.251276    | 0.251276    | 0.0020  | NA      | 0.216582 | 0.301191    | 10 |
| semantic_info_mean | selective                  | excess_over_control_minus_negative_protocell_compositional_entropy        | nan          | 0.251276    | 0.251276    | 0.0020  | NA      | 0.216582 | 0.301191    | 10 |
| semantic_info_mean | selective_entropy_controls | upper_bound_across_entropy_definitions                                    | nan          | 0.000723897 | 1.80974e-05 | NA      | NA      | 0        | 5.42923e-05 | 40 |

