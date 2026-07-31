from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .interventions import (
    VIABILITY_DEFS,
    BIOLOGICAL_VIABILITY_DEFS,
    ENTROPY_VIABILITY_DEFS,
    _summarize_method_subset,
)


def _load(results_dir: Path, name: str):
    path = results_dir / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


PALETTE = {
    'baseline': '#332288',
    'tac_s025': '#9BD4F0',
    'tac_s05': '#63B8AA',
    'tac_s075': '#117733',
    'tac_s10': '#999933',
    'pb_c05': '#DDCC77',
    'pb_c10': '#CC6677',
    'ar_s05': '#882255',
    'ar_s10': '#AA4499',
}

METHOD_COLORS = {
    'balanced_random_group': PALETTE['tac_s025'],
    'affinity_rank_group': PALETTE['tac_s05'],
    'prefix_group': PALETTE['tac_s075'],
    'kmeans_profile': PALETTE['tac_s10'],
}

CONDITION_COLORS = {
    'selective': PALETTE['tac_s075'],
    'control': PALETTE['pb_c10'],
}

SERIES_COLORS = {
    'syntactic': PALETTE['baseline'],
    'semantic': PALETTE['tac_s10'],
    'gap': PALETTE['ar_s05'],
    'value': PALETTE['tac_s05'],
}


VIABILITY_LABELS = {
    'excess_over_control': 'Excess over control',
    'negative_shannon_entropy': 'Negative fitness-distribution entropy (legacy)',
    'negative_fitness_distribution_entropy': 'Negative fitness-distribution entropy',
    'negative_local_metabolite_configuration_entropy': 'Negative local configuration entropy',
    'negative_adjacency_state_entropy': 'Negative adjacency-state entropy',
    'negative_protocell_compositional_entropy': 'Negative compositional entropy',
    'mean_future_fitness': 'Mean future fitness',
    'threshold_survival': 'Threshold survival',
}

VIABILITY_COLORS = {
    'excess_over_control': PALETTE['baseline'],
    'mean_future_fitness': PALETTE['tac_s05'],
    'threshold_survival': PALETTE['pb_c05'],
    'negative_shannon_entropy': PALETTE['ar_s10'],
    'negative_fitness_distribution_entropy': PALETTE['ar_s05'],
    'negative_local_metabolite_configuration_entropy': PALETTE['tac_s025'],
    'negative_adjacency_state_entropy': PALETTE['tac_s075'],
    'negative_protocell_compositional_entropy': PALETTE['pb_c10'],
}


def _monotone_upper_envelope(df: pd.DataFrame):
    if df.empty:
        return pd.DataFrame(columns=['preserved_info', 'viability'])
    envelope = (df.groupby('preserved_info', as_index=False)['viability']
                  .max()
                  .sort_values('preserved_info')
                  .reset_index(drop=True))
    envelope['viability'] = envelope['viability'].cummax()
    return envelope


def _series_color(name: str, default: str = '#777777'):
    return SERIES_COLORS.get(name, default)


def _condition_color(name: str, default: str = '#777777'):
    return CONDITION_COLORS.get(name, default)


def _viability_color(name: str, default: str = '#777777'):
    return VIABILITY_COLORS.get(name, default)


def _plot_method_diagnostic_panel(
    ax,
    df: pd.DataFrame,
    actual_viability: float,
    semantic_info: float,
    title: str,
    envelope_color: str | None = None,
    ref_color: str | None = None,
    method_colors: dict | None = None,
    method_label_map: dict | None = None,
):
    for method, method_df in df.groupby('method'):
        ax.scatter(
            method_df['preserved_info'],
            method_df['viability'],
            s=34,
            alpha=0.30,
            color=(method_colors or METHOD_COLORS).get(method, '#777777'),
            edgecolors='none',
            label=(method_label_map or {}).get(method, method.replace('_', ' ')),
        )
    envelope = _monotone_upper_envelope(df)
    if not envelope.empty:
        ax.plot(
            envelope['preserved_info'],
            envelope['viability'],
            color=envelope_color or 'black',
            lw=3.0,
            marker='o',
            ms=6.5,
            label='Monotone upper envelope',
        )
    if np.isfinite(actual_viability):
        ax.axhline(actual_viability, color=ref_color or 'black', lw=1.5, ls='--', label='Actual viability')
    if np.isfinite(semantic_info):
        ax.axvline(semantic_info, color=ref_color or 'black', lw=1.5, ls=(0, (5, 3)), label='Estimated semantic information')
    ax.set_title(title)
    ax.set_xlabel('Preserved information')
    ax.set_ylabel('Viability')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def _plot_with_ci(ax, x, mean, sem, *, color, marker, label):
    ci95 = 1.96 * sem
    ax.plot(x, mean, marker=marker, color=color, label=label, lw=2.8, ms=7.5)
    ax.fill_between(x, mean - ci95, mean + ci95, color=color, alpha=0.18, linewidth=0)


def _plot_with_band(ax, x, y, ylo, yhi, *, color, label, ls='-', lw=2.8, ms=7.5):
    ax.plot(x, y, marker='o', color=color, label=label, ls=ls, lw=lw, ms=ms)
    ax.fill_between(x, ylo, yhi, color=color, alpha=0.16, linewidth=0)


def _load_run_params(results_dir: Path):
    metadata = json.loads((results_dir / 'run_metadata.json').read_text())
    return metadata['parameters']


def _bootstrap_main_decomposition_cis(results_dir: Path, condition: str, viability_def: str, n_boot: int = 250, seed: int = 7):
    params = _load_run_params(results_dir)
    points = _load(results_dir, f'intervention_points_{condition}_{viability_def}.csv')
    points = points[points['analysis_role'] == 'primary'].copy()
    primary_methods = params['primary_intervention_methods']
    rng = np.random.default_rng(seed)
    rows = []
    for inh, df_inh in points.groupby('inherit_prob'):
        rep_ids = np.sort(df_inh['rep'].unique())
        if len(rep_ids) == 0:
            continue
        boot_rows = []
        for _ in range(n_boot):
            sampled = rng.choice(rep_ids, size=len(rep_ids), replace=True)
            sampled_frames = []
            actual_vals = []
            syn_vals = []
            for new_rep, rep_id in enumerate(sampled):
                rep_df = df_inh[df_inh['rep'] == rep_id].copy()
                rep_df['rep'] = new_rep
                sampled_frames.append(rep_df)
                actual_vals.append(float(rep_df['actual_viability'].iloc[0]))
                syn_vals.append(float(rep_df['syntactic_info'].iloc[0]))
            sampled_df = pd.concat(sampled_frames, ignore_index=True)
            summary, _, _ = _summarize_method_subset(
                sampled_df, actual_vals, syn_vals, params, condition, viability_def, inh, 'primary_no_kmeans', primary_methods
            )
            boot_rows.append(summary)
        boot = pd.DataFrame(boot_rows)
        row = {'inherit_prob': inh}
        for metric in [
            'syntactic_info_mean',
            'semantic_info_mean',
            'semantic_efficiency_mean',
            'value_of_information_mean',
        ]:
            vals = boot[metric].dropna().to_numpy()
            row[f'{metric}_lo'] = float(np.quantile(vals, 0.025)) if len(vals) else np.nan
            row[f'{metric}_hi'] = float(np.quantile(vals, 0.975)) if len(vals) else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values('inherit_prob').reset_index(drop=True)


def _bootstrap_summary_metrics_cis(results_dir: Path, condition: str, viability_def: str, n_boot: int = 250, seed: int = 7):
    params = _load_run_params(results_dir)
    points = _load(results_dir, f'intervention_points_{condition}_{viability_def}.csv')
    points = points[points['analysis_role'] == 'primary'].copy()
    primary_methods = params['primary_intervention_methods']
    rng = np.random.default_rng(seed)
    rows = []
    for inh, df_inh in points.groupby('inherit_prob'):
        rep_ids = np.sort(df_inh['rep'].unique())
        if len(rep_ids) == 0:
            continue
        boot_rows = []
        for _ in range(n_boot):
            sampled = rng.choice(rep_ids, size=len(rep_ids), replace=True)
            sampled_frames = []
            actual_vals = []
            syn_vals = []
            for new_rep, rep_id in enumerate(sampled):
                rep_df = df_inh[df_inh['rep'] == rep_id].copy()
                rep_df['rep'] = new_rep
                sampled_frames.append(rep_df)
                actual_vals.append(float(rep_df['actual_viability'].iloc[0]))
                syn_vals.append(float(rep_df['syntactic_info'].iloc[0]))
            sampled_df = pd.concat(sampled_frames, ignore_index=True)
            summary, _, _ = _summarize_method_subset(
                sampled_df, actual_vals, syn_vals, params, condition, viability_def, inh, 'primary_no_kmeans', primary_methods
            )
            boot_rows.append(summary)
        boot = pd.DataFrame(boot_rows)
        row = {'inherit_prob': inh}
        for metric in [
            'syntactic_info_mean',
            'semantic_info_mean',
            'semantic_efficiency_mean',
            'value_of_information_mean',
        ]:
            vals = boot[metric].dropna().to_numpy()
            row[f'{metric}_lo'] = float(np.quantile(vals, 0.025)) if len(vals) else np.nan
            row[f'{metric}_hi'] = float(np.quantile(vals, 0.975)) if len(vals) else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values('inherit_prob').reset_index(drop=True)


def figure_1_baseline(results_dir: Path, figures_dir: Path):
    sel = _load(results_dir, 'baseline_selective_summary.csv')
    ctl = _load(results_dir, 'baseline_control_summary.csv')
    fit_sel_color = PALETTE['tac_s025']
    fit_ctl_color = PALETTE['ar_s10']
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 5.2))
    _plot_with_ci(
        ax1, sel['inherit_prob'], sel['delta_mi_mean'], sel['delta_mi_sem'],
        color=fit_sel_color, marker='o', label='Sequence-selective',
    )
    _plot_with_ci(
        ax1, ctl['inherit_prob'], ctl['delta_mi_mean'], ctl['delta_mi_sem'],
        color=fit_ctl_color, marker='o', label='Sequence-agnostic',
    )
    ax1.set_xlabel('Inheritance fidelity')
    ax1.set_ylabel('Change in syntactic information (bits)')
    ax1.legend(frameon=False)
    ax1.text(-0.16, 1.03, r'$\mathit{(a)}$', transform=ax1.transAxes, fontsize=12, va='bottom', ha='left')
    _plot_with_ci(
        ax2, sel['inherit_prob'], sel['delta_fitness_mean'], sel['delta_fitness_sem'],
        color=fit_sel_color, marker='o', label='Sequence-selective',
    )
    _plot_with_ci(
        ax2, ctl['inherit_prob'], ctl['delta_fitness_mean'], ctl['delta_fitness_sem'],
        color=fit_ctl_color, marker='o', label='Sequence-agnostic',
    )
    ax2.set_xlabel('Inheritance fidelity')
    ax2.set_ylabel('Adaptive gain')
    ax2.text(-0.16, 1.03, r'$\mathit{(b)}$', transform=ax2.transAxes, fontsize=12, va='bottom', ha='left')
    for ax in (ax1, ax2):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    fig.tight_layout()
    fig.savefig(figures_dir / 'figure_1_baseline_vs_adaptive_gain.png', dpi=600)
    plt.close(fig)


def figure_2_schematic(figures_dir: Path):
    fig = plt.figure(figsize=(12, 4.8))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_axis_off()
    ax.text(0.03, 0.78, 'Original Model B\nfinal populations', fontsize=12, ha='center')
    ax.text(0.28, 0.78, 'Coarse-grain\nmotif identities', fontsize=12, ha='center')
    ax.text(0.52, 0.78, 'Rerun\nshort horizon', fontsize=12, ha='center')
    ax.text(0.78, 0.78, 'Information-viability\nfrontier', fontsize=12, ha='center')
    ax.annotate('', xy=(0.20, 0.80), xytext=(0.10, 0.80), arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate('', xy=(0.44, 0.80), xytext=(0.34, 0.80), arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate('', xy=(0.69, 0.80), xytext=(0.58, 0.80), arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(0.05, 0.48, 'Primary pooled frontier:', fontsize=12, fontweight='bold')
    ax.text(0.05, 0.38, 'balanced_random_group + affinity_rank_group + prefix_group', fontsize=11)
    ax.text(0.05, 0.28, 'kmeans_profile retained separately as function-preserving mechanistic diagnostic', fontsize=11)
    ax.text(0.56, 0.48, 'Three-layer JSRI framing:', fontsize=12, fontweight='bold')
    ax.text(0.56, 0.38, '1. Main biological: excess over control', fontsize=11)
    ax.text(0.56, 0.28, '2. Physics diagnostics: state-space entropy', fontsize=11)
    ax.text(0.56, 0.18, '3. Robustness: threshold survival and method ablations', fontsize=11)
    ax.set_title('Intervention-based semantic decomposition with alternative viability definitions')
    fig.tight_layout()
    fig.savefig(figures_dir / 'figure_2_intervention_schematic.png', dpi=600)
    plt.close(fig)


def figure_3_main_decomposition(results_dir: Path, figures_dir: Path):
    v = 'excess_over_control'
    sel = _load(results_dir, f'intervention_summary_selective_{v}.csv')
    ctl = _load(results_dir, f'intervention_summary_control_{v}.csv')
    sel_ci = _bootstrap_main_decomposition_cis(results_dir, 'selective', v, n_boot=100, seed=17)
    ctl_ci = _bootstrap_main_decomposition_cis(results_dir, 'control', v, n_boot=100, seed=29)
    sel = sel.merge(sel_ci, on='inherit_prob', how='left')
    ctl = ctl.merge(ctl_ci, on='inherit_prob', how='left')
    fig = plt.figure(figsize=(13, 10))
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)

    syn_sel_color = PALETTE['baseline']
    syn_ctl_color = PALETTE['pb_c10']
    sem_sel_color = PALETTE['tac_s075']
    sem_ctl_color = PALETTE['ar_s05']
    gap_sel_color = PALETTE['tac_s025']
    gap_ctl_color = PALETTE['ar_s10']
    voi_sel_color = gap_sel_color
    voi_ctl_color = gap_ctl_color

    for ax in (ax1, ax2, ax3, ax4):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    _plot_with_band(ax1, sel['inherit_prob'], sel['syntactic_info_mean'], sel['syntactic_info_mean_lo'], sel['syntactic_info_mean_hi'], color=syn_sel_color, label='Sequence-selective syntactic')
    _plot_with_band(ax1, sel['inherit_prob'], sel['semantic_info_mean'], sel['semantic_info_mean_lo'], sel['semantic_info_mean_hi'], color=sem_sel_color, label='Sequence-selective semantic')
    _plot_with_band(ax1, ctl['inherit_prob'], ctl['syntactic_info_mean'], ctl['syntactic_info_mean_lo'], ctl['syntactic_info_mean_hi'], color=syn_ctl_color, label='Sequence-agnostic syntactic')
    _plot_with_band(ax1, ctl['inherit_prob'], ctl['semantic_info_mean'], ctl['semantic_info_mean_lo'], ctl['semantic_info_mean_hi'], color=sem_ctl_color, label='Sequence-agnostic semantic')
    ax1.set_xlabel('Inheritance fidelity')
    ax1.set_ylabel('Information (bits)')
    ax1.legend(fontsize=8, frameon=False)
    ax1.text(-0.16, 1.03, r'$\mathit{(a)}$', transform=ax1.transAxes, fontsize=12, va='bottom', ha='left')

    _plot_with_band(
        ax2,
        sel['inherit_prob'],
        sel['syntactic_info_mean'] - sel['semantic_info_mean'],
        sel['syntactic_info_mean_lo'] - sel['semantic_info_mean_hi'],
        sel['syntactic_info_mean_hi'] - sel['semantic_info_mean_lo'],
        color=gap_sel_color,
        label='Sequence-selective',
    )
    _plot_with_band(
        ax2,
        ctl['inherit_prob'],
        ctl['syntactic_info_mean'] - ctl['semantic_info_mean'],
        ctl['syntactic_info_mean_lo'] - ctl['semantic_info_mean_hi'],
        ctl['syntactic_info_mean_hi'] - ctl['semantic_info_mean_lo'],
        color=gap_ctl_color,
        label='Sequence-agnostic',
    )
    ax2.set_xlabel('Inheritance fidelity')
    ax2.set_ylabel('Gap (bits)')
    ax2.legend(fontsize=8, frameon=False)
    ax2.text(-0.16, 1.03, r'$\mathit{(b)}$', transform=ax2.transAxes, fontsize=12, va='bottom', ha='left')

    _plot_with_band(ax3, sel['inherit_prob'], sel['semantic_efficiency_mean'], sel['semantic_efficiency_mean_lo'], sel['semantic_efficiency_mean_hi'], color=gap_sel_color, label='Sequence-selective')
    _plot_with_band(ax3, ctl['inherit_prob'], ctl['semantic_efficiency_mean'], ctl['semantic_efficiency_mean_lo'], ctl['semantic_efficiency_mean_hi'], color=gap_ctl_color, label='Sequence-agnostic')
    ax3.set_xlabel('Inheritance fidelity')
    ax3.set_ylabel('Semantic / syntactic')
    ax3.legend(fontsize=8, frameon=False)
    ax3.text(-0.16, 1.03, r'$\mathit{(c)}$', transform=ax3.transAxes, fontsize=12, va='bottom', ha='left')

    _plot_with_band(ax4, sel['inherit_prob'], sel['value_of_information_mean'], sel['value_of_information_mean_lo'], sel['value_of_information_mean_hi'], color=voi_sel_color, label='Sequence-selective')
    _plot_with_band(ax4, ctl['inherit_prob'], ctl['value_of_information_mean'], ctl['value_of_information_mean_lo'], ctl['value_of_information_mean_hi'], color=voi_ctl_color, label='Sequence-agnostic')
    ax4.set_xlabel('Inheritance fidelity')
    ax4.set_ylabel('Actual - full-scrambled viability')
    ax4.legend(fontsize=8, frameon=False)
    ax4.text(-0.16, 1.03, r'$\mathit{(d)}$', transform=ax4.transAxes, fontsize=12, va='bottom', ha='left')

    fig.tight_layout()
    fig.savefig(figures_dir / 'figure_3_main_decomposition_excess_over_control.png', dpi=600)
    plt.close(fig)


def figure_4_viability_definition_comparison(results_dir: Path, figures_dir: Path):
    """Biological viability-definition comparison only.

    Entropy-based diagnostics are intentionally excluded from this main panel and
    plotted separately by figure_4b_entropy_state_definitions.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 5.2))
    colors = {
        'excess_over_control': PALETTE['baseline'],
        'mean_future_fitness': PALETTE['tac_s075'],
        'threshold_survival': PALETTE['pb_c10'],
    }
    for ax in (ax1, ax2):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    seed_map = {
        'excess_over_control': 41,
        'mean_future_fitness': 43,
        'threshold_survival': 47,
    }
    for v in BIOLOGICAL_VIABILITY_DEFS:
        path = results_dir / f'intervention_summary_selective_{v}.csv'
        if not path.exists():
            continue
        sel = _load(results_dir, f'intervention_summary_selective_{v}.csv')
        sel_ci = _bootstrap_summary_metrics_cis(results_dir, 'selective', v, n_boot=100, seed=seed_map.get(v, 7))
        sel = sel.merge(sel_ci, on='inherit_prob', how='left')
        color = colors.get(v, _viability_color(v))
        _plot_with_band(
            ax1,
            sel['inherit_prob'],
            sel['semantic_info_mean'],
            sel['semantic_info_mean_lo'],
            sel['semantic_info_mean_hi'],
            color=color,
            label=VIABILITY_LABELS.get(v, v),
        )
        gap = sel['syntactic_info_mean'] - sel['semantic_info_mean']
        _plot_with_band(
            ax2,
            sel['inherit_prob'],
            gap,
            sel['syntactic_info_mean_lo'] - sel['semantic_info_mean_hi'],
            sel['syntactic_info_mean_hi'] - sel['semantic_info_mean_lo'],
            color=color,
            label=VIABILITY_LABELS.get(v, v),
        )
    ax1.set_xlabel('Inheritance fidelity')
    ax1.set_ylabel('Semantic information (bits)')
    ax1.legend(fontsize=8, frameon=False)
    ax1.text(-0.16, 1.03, r'$\mathit{(a)}$', transform=ax1.transAxes, fontsize=12, va='bottom', ha='left')
    ax2.set_xlabel('Inheritance fidelity')
    ax2.set_ylabel('Gap (bits)')
    ax2.text(-0.16, 1.03, r'$\mathit{(b)}$', transform=ax2.transAxes, fontsize=12, va='bottom', ha='left')
    ymin = min(ax1.get_ylim()[0], ax2.get_ylim()[0])
    ymax = max(ax1.get_ylim()[1], ax2.get_ylim()[1])
    ax1.set_ylim(ymin, ymax)
    ax2.set_ylim(ymin, ymax)
    fig.tight_layout()
    fig.savefig(figures_dir / 'figure_4_viability_definition_comparison.png', dpi=600)
    # Backwards-compatible filename requested during manuscript iteration; now no entropy curves.
    fig.savefig(figures_dir / 'figure_4_gap_widening.png', dpi=600)
    plt.close(fig)


def figure_4b_entropy_state_definitions(results_dir: Path, figures_dir: Path):
    """Entropy-based physics diagnostics over Model-B-relevant state spaces."""
    available = [v for v in ENTROPY_VIABILITY_DEFS if (results_dir / f'intervention_summary_selective_{v}.csv').exists()]
    if not available:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 5.2))
    for ax in (ax1, ax2):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    seed_map = {
        'negative_fitness_distribution_entropy': 53,
        'negative_local_metabolite_configuration_entropy': 59,
        'negative_adjacency_state_entropy': 61,
        'negative_protocell_compositional_entropy': 67,
    }
    for v in available:
        sel = _load(results_dir, f'intervention_summary_selective_{v}.csv')
        sel_ci = _bootstrap_summary_metrics_cis(results_dir, 'selective', v, n_boot=100, seed=seed_map.get(v, 7))
        sel = sel.merge(sel_ci, on='inherit_prob', how='left')
        color = _viability_color(v)
        _plot_with_band(
            ax1,
            sel['inherit_prob'],
            sel['semantic_info_mean'],
            sel['semantic_info_mean_lo'],
            sel['semantic_info_mean_hi'],
            color=color,
            label=VIABILITY_LABELS.get(v, v),
        )
        gap = sel['syntactic_info_mean'] - sel['semantic_info_mean']
        _plot_with_band(
            ax2,
            sel['inherit_prob'],
            gap,
            sel['syntactic_info_mean_lo'] - sel['semantic_info_mean_hi'],
            sel['syntactic_info_mean_hi'] - sel['semantic_info_mean_lo'],
            color=color,
            label=VIABILITY_LABELS.get(v, v),
        )
    ax1.set_xlabel('Inheritance fidelity')
    ax1.set_ylabel('Semantic information (bits)')
    ax1.legend(fontsize=8, frameon=False, loc='upper left', bbox_to_anchor=(0.02, 0.98), borderaxespad=0.0)
    ax1.text(-0.16, 1.03, r'$\mathit{(a)}$', transform=ax1.transAxes, fontsize=12, va='bottom', ha='left')
    ax2.set_xlabel('Inheritance fidelity')
    ax2.set_ylabel('Gap (bits)')
    ax2.text(-0.16, 1.03, r'$\mathit{(b)}$', transform=ax2.transAxes, fontsize=12, va='bottom', ha='left')
    ymin = min(ax1.get_ylim()[0], ax2.get_ylim()[0])
    ymax = max(ax1.get_ylim()[1], ax2.get_ylim()[1])
    ax1.set_ylim(ymin, ymax)
    ax2.set_ylim(ymin, ymax)
    fig.tight_layout()
    fig.savefig(figures_dir / 'figure_4b_entropy_state_definitions.png', dpi=600)
    plt.close(fig)


def figure_5_frontiers_and_robustness(results_dir: Path, figures_dir: Path):
    fig = plt.figure(figsize=(14.5, 4.9))
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)
    intervention_methods = ['balanced_random_group', 'affinity_rank_group', 'prefix_group']
    intervention_colors = {
        'balanced_random_group': '#4C78A8',
        'affinity_rank_group': '#2A9D8F',
        'prefix_group': '#E76F51',
    }
    reference_gray = '#8a8a8a'
    intervention_labels = {
        'balanced_random_group': 'Balanced random grouping',
        'affinity_rank_group': 'Affinity-rank grouping',
        'prefix_group': 'Prefix grouping',
    }

    examples = [
        ('selective', 'excess_over_control', 0.9, ax1, PALETTE['tac_s025']),
        ('control', 'excess_over_control', 0.9, ax2, PALETTE['ar_s10']),
    ]
    for cond, v, inh, ax, panel_color in examples:
        points = _load(results_dir, f'intervention_points_{cond}_{v}.csv')
        summary = _load(results_dir, f'intervention_summary_{cond}_{v}.csv')
        part = points[(np.isclose(points['inherit_prob'], inh)) & (points['analysis_role'] == 'primary')].copy()
        row = summary.loc[np.isclose(summary['inherit_prob'], inh)].iloc[0]
        _plot_method_diagnostic_panel(
            ax,
            part,
            float(row['actual_viability_mean']),
            float(row['semantic_info_mean']),
            '',
            envelope_color=panel_color,
            ref_color=reference_gray,
            method_colors=intervention_colors,
        )
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    ymin = min(ax1.get_ylim()[0], ax2.get_ylim()[0])
    ymax = max(ax1.get_ylim()[1], ax2.get_ylim()[1])
    ax1.set_ylim(ymin, ymax)
    ax2.set_ylim(ymin, ymax)
    intervention_handles = [
        plt.Line2D(
            [0],
            [0],
            marker='o',
            linestyle='none',
            markerfacecolor=intervention_colors[method],
            markeredgecolor='none',
            markersize=6,
            alpha=0.7,
            label=intervention_labels[method],
        )
        for method in intervention_methods
    ]
    selective_handle = plt.Line2D(
        [0],
        [0],
        color=PALETTE['tac_s025'],
        lw=3.0,
        marker='o',
        ms=6.5,
        label='Sequence-selective',
    )
    agnostic_handle = plt.Line2D(
        [0],
        [0],
        color=PALETTE['ar_s10'],
        lw=3.0,
        marker='o',
        ms=6.5,
        label='Sequence-agnostic',
    )
    ax1_frontier_legend = ax1.legend(
        handles=[selective_handle],
        loc='upper left',
        bbox_to_anchor=(0.02, 0.96),
        fontsize=8,
        frameon=False,
        handletextpad=0.5,
    )
    ax1_family_legend = ax1.legend(
        handles=intervention_handles,
        title='Intervention family',
        loc='upper left',
        bbox_to_anchor=(0.02, 0.78),
        fontsize=8,
        title_fontsize=8,
        frameon=False,
        handletextpad=0.4,
    )
    ax1.add_artist(ax1_frontier_legend)
    ax1.add_artist(ax1_family_legend)
    ax2_frontier_legend = ax2.legend(
        handles=[agnostic_handle],
        loc='upper left',
        bbox_to_anchor=(0.08, 0.96),
        fontsize=8,
        frameon=False,
        handletextpad=0.5,
    )
    ax2_family_legend = ax2.legend(
        handles=intervention_handles,
        title='Intervention family',
        loc='upper left',
        bbox_to_anchor=(0.08, 0.78),
        fontsize=8,
        title_fontsize=8,
        frameon=False,
        handletextpad=0.4,
    )
    ax2.add_artist(ax2_frontier_legend)
    ax2.add_artist(ax2_family_legend)
    ax1.text(-0.16, 1.03, r'$\mathit{(a)}$', transform=ax1.transAxes, fontsize=12, va='bottom', ha='left')
    ax2.text(-0.16, 1.03, r'$\mathit{(b)}$', transform=ax2.transAxes, fontsize=12, va='bottom', ha='left')

    sel = _load(results_dir, 'intervention_summary_selective_excess_over_control.csv').copy()
    ctl = _load(results_dir, 'intervention_summary_control_excess_over_control.csv').copy()
    sel['gap'] = sel['actual_viability_mean'] - sel['frontier_max_viability']
    ctl['gap'] = ctl['actual_viability_mean'] - ctl['frontier_max_viability']
    ax3.plot(
        sel['inherit_prob'],
        sel['gap'],
        marker='o',
        ms=7.5,
        lw=2.8,
        color=PALETTE['tac_s025'],
        label='Sequence-selective',
    )
    ax3.plot(
        ctl['inherit_prob'],
        ctl['gap'],
        marker='o',
        ms=7.5,
        lw=2.8,
        color=PALETTE['ar_s10'],
        label='Sequence-agnostic',
    )
    ax3.axhline(0.0, color=reference_gray, lw=1.4, ls='--')
    ax3.set_xlabel('Inheritance fidelity')
    ax3.set_ylabel('Actual viability mean - frontier max viability')
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.legend(fontsize=8, frameon=False)
    ax3.text(-0.16, 1.03, r'$\mathit{(c)}$', transform=ax3.transAxes, fontsize=12, va='bottom', ha='left')

    fig.tight_layout()
    fig.savefig(figures_dir / 'figure_5_frontiers_and_robustness.png', dpi=600)
    plt.close(fig)


def supplement_threshold_survival(results_dir: Path, figures_dir: Path):
    sel = _load(results_dir, 'intervention_summary_selective_threshold_survival.csv')
    ctl = _load(results_dir, 'intervention_summary_control_threshold_survival.csv')
    sel_ci = _bootstrap_summary_metrics_cis(results_dir, 'selective', 'threshold_survival', n_boot=100)
    ctl_ci = _bootstrap_summary_metrics_cis(results_dir, 'control', 'threshold_survival', n_boot=100)
    sel = sel.merge(sel_ci, on='inherit_prob', how='left')
    ctl = ctl.merge(ctl_ci, on='inherit_prob', how='left')
    fig = plt.figure(figsize=(5.1, 5.2))
    ax = fig.add_subplot(1, 1, 1)
    _plot_with_band(
        ax,
        sel['inherit_prob'],
        sel['syntactic_info_mean'],
        sel['syntactic_info_mean_lo'],
        sel['syntactic_info_mean_hi'],
        color=PALETTE['baseline'],
        label='Sequence-selective syntactic',
    )
    _plot_with_band(
        ax,
        sel['inherit_prob'],
        sel['semantic_info_mean'],
        sel['semantic_info_mean_lo'],
        sel['semantic_info_mean_hi'],
        color=PALETTE['tac_s075'],
        label='Sequence-selective semantic',
    )
    _plot_with_band(
        ax,
        ctl['inherit_prob'],
        ctl['semantic_info_mean'],
        ctl['semantic_info_mean_lo'],
        ctl['semantic_info_mean_hi'],
        color=PALETTE['pb_c10'],
        label='Sequence-agnostic semantic',
    )
    ax.set_xlabel('Inheritance fidelity')
    ax.set_ylabel('Information (bits)')
    ax.set_title('Supplement: strict threshold-survival decomposition')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(figures_dir / 'supplement_threshold_survival.png', dpi=600)
    plt.close(fig)


def supplement_method_ablation(results_dir: Path, figures_dir: Path):
    v = 'excess_over_control'
    fig = plt.figure(figsize=(10.2, 5.2))
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    regime_colors = {
        'selective': PALETTE['tac_s025'],
        'control': PALETTE['ar_s10'],
    }
    method_styles = {
        'primary': {'ls': '-', 'marker': 'o'},
        'pooled': {'ls': '--', 'marker': 's'},
        'kmeans': {'ls': ':', 'marker': '^'},
    }
    for cond in ['selective', 'control']:
        primary = _load(results_dir, f'intervention_summary_{cond}_{v}.csv')
        pooled = _load(results_dir, f'intervention_summary_{cond}_{v}_all_methods_diagnostic.csv')
        kmeans = _load(results_dir, f'intervention_summary_{cond}_{v}_kmeans_profile_mechanistic.csv')
        color = regime_colors[cond]
        ax1.plot(
            primary['inherit_prob'],
            primary['semantic_info_mean'],
            ls=method_styles['primary']['ls'],
            marker=method_styles['primary']['marker'],
            ms=7.5,
            lw=2.8,
            color=color,
        )
        ax1.plot(
            pooled['inherit_prob'],
            pooled['semantic_info_mean'],
            ls=method_styles['pooled']['ls'],
            marker=method_styles['pooled']['marker'],
            ms=7.5,
            lw=2.8,
            color=color,
        )
        ax1.plot(
            kmeans['inherit_prob'],
            kmeans['semantic_info_mean'],
            ls=method_styles['kmeans']['ls'],
            marker=method_styles['kmeans']['marker'],
            ms=7.5,
            lw=2.8,
            color=color,
        )
        ax2.plot(
            primary['inherit_prob'],
            primary['frontier_max_viability'],
            ls=method_styles['primary']['ls'],
            marker=method_styles['primary']['marker'],
            ms=7.5,
            lw=2.8,
            color=color,
        )
        ax2.plot(
            kmeans['inherit_prob'],
            kmeans['frontier_max_viability'],
            ls=method_styles['kmeans']['ls'],
            marker=method_styles['kmeans']['marker'],
            ms=7.5,
            lw=2.8,
            color=color,
        )
    ax1.set_title('Method ablation: semantic estimates')
    ax1.set_ylabel('Semantic information (bits)')
    ax1.set_xlabel('Inheritance fidelity')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.text(-0.16, 1.03, r'$\mathit{(a)}$', transform=ax1.transAxes, fontsize=12, va='bottom', ha='left')
    ax2.set_title('Method ablation: maximum frontier viability')
    ax2.set_xlabel('Inheritance fidelity')
    ax2.set_ylabel('Frontier max viability')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.text(-0.16, 1.03, r'$\mathit{(b)}$', transform=ax2.transAxes, fontsize=12, va='bottom', ha='left')
    regime_handles = [
        plt.Line2D([0], [0], color=regime_colors['selective'], lw=2.8, ls='-', label='Sequence-selective'),
        plt.Line2D([0], [0], color=regime_colors['control'], lw=2.8, ls='-', label='Sequence-agnostic control'),
    ]
    method_handles = [
        plt.Line2D([0], [0], color='#777777', lw=2.8, ls=method_styles['primary']['ls'], marker=method_styles['primary']['marker'], ms=7.5, label='Primary frontier, no k-means'),
        plt.Line2D([0], [0], color='#777777', lw=2.8, ls=method_styles['pooled']['ls'], marker=method_styles['pooled']['marker'], ms=7.5, label='All-pooled diagnostic'),
        plt.Line2D([0], [0], color='#777777', lw=2.8, ls=method_styles['kmeans']['ls'], marker=method_styles['kmeans']['marker'], ms=7.5, label='k-means-profile diagnostic'),
    ]
    regime_legend = ax1.legend(
        handles=regime_handles,
        title='Regime',
        loc='upper left',
        bbox_to_anchor=(0.02, 0.98),
        fontsize=8,
        title_fontsize=8,
        frameon=False,
        ncol=1,
    )
    method_legend = ax1.legend(
        handles=method_handles,
        title='Method (style only)',
        loc='upper left',
        bbox_to_anchor=(0.02, 0.80),
        fontsize=8,
        title_fontsize=8,
        frameon=False,
        ncol=1,
    )
    fig.add_artist(regime_legend)
    ax1.add_artist(method_legend)
    fig.tight_layout()
    fig.savefig(figures_dir / 'supplement_method_ablation_no_kmeans_sensitivity.png', dpi=600)
    plt.close(fig)


def supplement_frontiers(results_dir: Path, figures_dir: Path):
    wanted = [
        ('selective', 'excess_over_control', 0.9),
        ('selective', 'negative_local_metabolite_configuration_entropy', 0.9),
        ('selective', 'threshold_survival', 1.0),
        ('control', 'excess_over_control', 1.0),
    ]
    fig = plt.figure(figsize=(12, 8))
    axes = []
    for i, (cond, v, inh) in enumerate(wanted, start=1):
        ax = fig.add_subplot(2, 2, i)
        axes.append(ax)
        path = results_dir / f'frontier_debug_{cond}_{v}_primary_no_kmeans_inh_{inh:.1f}_smooth1.csv'
        if not path.exists():
            path = results_dir / f'frontier_debug_{cond}_{v}_inh_{inh:.1f}_smooth1.csv'
        if path.exists():
            df = pd.read_csv(path)
            if not df.empty:
                ax.plot(
                    df['preserved_info_bin'],
                    df['frontier_viability'],
                    marker='o',
                    ms=7.5,
                    lw=2.8,
                    color=PALETTE['baseline'],
                    label='Monotone frontier',
                )
                if 'frontier_viability_smooth' in df.columns:
                    ax.plot(
                        df['preserved_info_bin'],
                        df['frontier_viability_smooth'],
                        marker='o',
                        ms=7.5,
                        lw=2.8,
                        color=PALETTE['pb_c10'],
                        label='Smoothed frontier',
                    )
        ax.set_title(f'{cond} | {VIABILITY_LABELS.get(v, v)} | inh={inh:.1f}')
        ax.set_xlabel('Preserved info')
        ax.set_ylabel('Viability')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    shared_axes = [axes[0], axes[2], axes[3]]
    ymax_shared = max(ax.get_ylim()[1] for ax in shared_axes)
    for ax in shared_axes:
        ax.set_ylim(0, ymax_shared)
    axes[1].set_ylabel('Negative entropy viability')
    axes[1].set_ylim(-3.8789, -3.8776)
    axes[1].set_yticks([-3.8788, -3.8784, -3.8780, -3.8776])
    for label, ax in zip(['a', 'b', 'c', 'd'], axes):
        ax.text(-0.16, 1.03, rf'$\mathit{{({label})}}$', transform=ax.transAxes, fontsize=12, va='bottom', ha='left')
    fig.tight_layout()
    fig.savefig(figures_dir / 'supplement_frontiers.png', dpi=600)
    plt.close(fig)


def supplement_method_diagnostics(results_dir: Path, figures_dir: Path):
    viability = 'mean_future_fitness'
    points = _load(results_dir, f'intervention_points_selective_{viability}.csv')
    summary = _load(results_dir, f'intervention_summary_selective_{viability}.csv')
    inherit_prob = 0.8
    points = points[points['inherit_prob'] == inherit_prob].copy()
    summary_row = summary.loc[np.isclose(summary['inherit_prob'], inherit_prob)].iloc[0]

    fig = plt.figure(figsize=(10.8, 5.2))
    ax_all = fig.add_subplot(1, 2, 1)
    ax_no_kmeans = fig.add_subplot(1, 2, 2)
    method_colors = {
        'balanced_random_group': '#8ecae6',
        'affinity_rank_group': '#a8dadc',
        'prefix_group': '#74c69d',
        'kmeans_profile': '#c9c784',
    }
    method_label_map = {
        'affinity_rank_group': 'affinity rank group',
        'balanced_random_group': 'balanced random group',
        'kmeans_profile': 'k-means-profile diagnostic',
        'prefix_group': 'prefix group',
    }
    line_gray = '#8a8a8a'

    actual_viability = float(summary_row['actual_viability_mean'])
    semantic_info = float(summary_row['semantic_info_mean'])

    _plot_method_diagnostic_panel(
        ax_all,
        points,
        actual_viability,
        semantic_info,
        'All-methods pooled diagnostic',
        envelope_color=line_gray,
        ref_color=line_gray,
        method_colors=method_colors,
        method_label_map=method_label_map,
    )
    _plot_method_diagnostic_panel(
        ax_no_kmeans,
        points[points['method'] != 'kmeans_profile'].copy(),
        actual_viability,
        semantic_info,
        'Primary frontier excluding k-means-profile',
        envelope_color=line_gray,
        ref_color=line_gray,
        method_colors=method_colors,
        method_label_map=method_label_map,
    )
    ax_all.text(-0.16, 1.03, r'$\mathit{(a)}$', transform=ax_all.transAxes, fontsize=12, va='bottom', ha='left')
    ax_no_kmeans.text(-0.16, 1.03, r'$\mathit{(b)}$', transform=ax_no_kmeans.transAxes, fontsize=12, va='bottom', ha='left')

    handles, labels = ax_all.get_legend_handles_labels()
    label_to_handle = {}
    for handle, label in zip(handles, labels):
        label_to_handle.setdefault(label, handle)
    ordered_labels = [
        'affinity rank group',
        'balanced random group',
        'k-means-profile diagnostic',
        'prefix group',
        'Monotone upper envelope',
        'Actual viability',
        'Estimated semantic information',
    ]
    dedup_labels = [label for label in ordered_labels if label in label_to_handle]
    dedup_handles = [label_to_handle[label] for label in dedup_labels]
    ax_no_kmeans.legend(
        dedup_handles,
        dedup_labels,
        loc='upper left',
        bbox_to_anchor=(0.0, 0.84),
        frameon=False,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(figures_dir / 'supplement_method_diagnostics.png', dpi=600)
    plt.close(fig)


def make_all_figures(results_dir: str, figures_dir: str):
    results_dir = Path(results_dir)
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    figure_1_baseline(results_dir, figures_dir)
    figure_2_schematic(figures_dir)
    figure_3_main_decomposition(results_dir, figures_dir)
    figure_4_viability_definition_comparison(results_dir, figures_dir)
    figure_4b_entropy_state_definitions(results_dir, figures_dir)
    figure_5_frontiers_and_robustness(results_dir, figures_dir)
    supplement_threshold_survival(results_dir, figures_dir)
    supplement_method_ablation(results_dir, figures_dir)
    supplement_frontiers(results_dir, figures_dir)
    supplement_method_diagnostics(results_dir, figures_dir)
