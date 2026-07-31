from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, kruskal
from .interventions import VIABILITY_DEFS, BIOLOGICAL_VIABILITY_DEFS, ENTROPY_VIABILITY_DEFS
from .original_model.sweeps import permutation_test_delta


def _load(results_dir: Path, name: str):
    path = results_dir / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _safe_kruskal(*groups):
    """Return a neutral Kruskal result when all observed values are identical."""
    arrays = [np.asarray(g, dtype=float) for g in groups if len(g) > 0]
    if len(arrays) < 2:
        return np.nan, np.nan
    combined = np.concatenate(arrays)
    finite = combined[np.isfinite(combined)]
    if finite.size == 0:
        return np.nan, np.nan
    if np.all(finite == finite[0]):
        return 0.0, 1.0
    return kruskal(*arrays)


def _bh_fdr(p_values):
    p = np.asarray(p_values, dtype=float)
    out = np.full_like(p, np.nan, dtype=float)
    finite = np.isfinite(p)
    idx = np.where(finite)[0]
    if idx.size == 0:
        return out
    order = idx[np.argsort(p[idx])]
    ranked = p[order]
    m = len(ranked)
    adj = ranked * m / np.arange(1, m + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out[order] = np.minimum(adj, 1.0)
    return out


def add_fdr(df, p_col='p_value', group_cols=None):
    df = df.copy()
    if group_cols is None:
        df['p_fdr_bh'] = _bh_fdr(df[p_col].to_numpy())
    else:
        df['p_fdr_bh'] = np.nan
        for _, idx in df.groupby(group_cols).groups.items():
            idx = list(idx)
            df.loc[idx, 'p_fdr_bh'] = _bh_fdr(df.loc[idx, p_col].to_numpy())
    return df


def build_baseline_stats(results_dir: str):
    results_dir = Path(results_dir)
    rows = []
    for cond in ['selective', 'control']:
        fit = _load(results_dir, f'baseline_{cond}_replicate_deltas.csv')
        for inh, part in fit.groupby('inherit_prob'):
            dfit = part['delta_fitness'].to_numpy()
            dmi = part['delta_mi'].to_numpy()
            _, pfit = permutation_test_delta(dfit)
            _, pmi = permutation_test_delta(dmi)
            rows.append({
                'condition': cond, 'inherit_prob': inh, 'metric': 'delta_fitness',
                'n': len(dfit), 'mean': float(np.mean(dfit)), 'median': float(np.median(dfit)),
                'sem': float(np.std(dfit, ddof=1) / np.sqrt(len(dfit))) if len(dfit) > 1 else np.nan,
                'p_value': float(pfit), 'test': 'sign-randomization permutation against zero',
            })
            rows.append({
                'condition': cond, 'inherit_prob': inh, 'metric': 'delta_mi',
                'n': len(dmi), 'mean': float(np.mean(dmi)), 'median': float(np.median(dmi)),
                'sem': float(np.std(dmi, ddof=1) / np.sqrt(len(dmi))) if len(dmi) > 1 else np.nan,
                'p_value': float(pmi), 'test': 'sign-randomization permutation against zero',
            })
    return add_fdr(pd.DataFrame(rows), group_cols=['condition', 'metric'])


def build_viability_gap_table(results_dir: str):
    results_dir = Path(results_dir)
    frames = []
    for v in VIABILITY_DEFS:
        if not (results_dir / f'intervention_summary_selective_{v}.csv').exists() or not (results_dir / f'intervention_summary_control_{v}.csv').exists():
            continue
        sel = _load(results_dir, f'intervention_summary_selective_{v}.csv')
        ctl = _load(results_dir, f'intervention_summary_control_{v}.csv')
        merged = sel.merge(ctl, on='inherit_prob', suffixes=('_selective', '_control'))
        merged['viability_def'] = v
        merged['syntactic_semantic_gap_selective'] = merged['syntactic_info_mean_selective'] - merged['semantic_info_mean_selective']
        merged['syntactic_semantic_gap_control'] = merged['syntactic_info_mean_control'] - merged['semantic_info_mean_control']
        merged['semantic_info_selective_minus_control'] = merged['semantic_info_mean_selective'] - merged['semantic_info_mean_control']
        merged['value_of_information_selective_minus_control'] = merged['value_of_information_mean_selective'] - merged['value_of_information_mean_control']
        frames.append(merged)
    return pd.concat(frames, ignore_index=True)


def build_robustness_table(results_dir: str):
    results_dir = Path(results_dir)
    rows = []
    for v in VIABILITY_DEFS:
        for cond in ['selective', 'control']:
            if not (results_dir / f'threshold_sensitivity_{cond}_{v}.csv').exists():
                continue
            df = _load(results_dir, f'threshold_sensitivity_{cond}_{v}.csv')
            tab = df.groupby('inherit_prob')['semantic_info'].agg(['min', 'median', 'max', 'mean', 'std']).reset_index()
            tab['condition'] = cond
            tab['viability_def'] = v
            rows.append(tab)
    return pd.concat(rows, ignore_index=True)


def build_intervention_tests(results_dir: str):
    """Selective vs control tests using primary no-kmeans intervention points."""
    results_dir = Path(results_dir)
    rows = []
    for v in VIABILITY_DEFS:
        if not (results_dir / f'intervention_points_selective_{v}.csv').exists() or not (results_dir / f'intervention_points_control_{v}.csv').exists():
            continue
        sel = _load(results_dir, f'intervention_points_selective_{v}.csv')
        ctl = _load(results_dir, f'intervention_points_control_{v}.csv')
        sel = sel[sel['analysis_role'] == 'primary']
        ctl = ctl[ctl['analysis_role'] == 'primary']
        for inh in sorted(set(sel['inherit_prob']).intersection(set(ctl['inherit_prob']))):
            a = sel.loc[sel['inherit_prob'] == inh, 'viability'].dropna().to_numpy()
            b = ctl.loc[ctl['inherit_prob'] == inh, 'viability'].dropna().to_numpy()
            if len(a) and len(b):
                stat, p = mannwhitneyu(a, b, alternative='two-sided')
                rows.append({
                    'viability_def': v, 'inherit_prob': inh,
                    'selective_n': len(a), 'control_n': len(b),
                    'u': float(stat), 'p_value': float(p),
                    'selective_median': float(np.median(a)),
                    'control_median': float(np.median(b)),
                    'median_difference': float(np.median(a) - np.median(b)),
                    'test': 'Mann-Whitney U, primary no-kmeans intervention points',
                })
    return add_fdr(pd.DataFrame(rows), group_cols=['viability_def'])


def build_method_ablation_tests(results_dir: str):
    """Tests whether kmeans_profile has a different viability distribution from primary methods."""
    results_dir = Path(results_dir)
    rows = []
    for v in VIABILITY_DEFS:
        for cond in ['selective', 'control']:
            if not (results_dir / f'intervention_points_{cond}_{v}.csv').exists():
                continue
            df = _load(results_dir, f'intervention_points_{cond}_{v}.csv')
            for inh, part in df.groupby('inherit_prob'):
                primary = part.loc[part['analysis_role'] == 'primary', 'viability'].dropna().to_numpy()
                kmeans = part.loc[part['method'] == 'kmeans_profile', 'viability'].dropna().to_numpy()
                if len(primary) and len(kmeans):
                    stat, p = mannwhitneyu(kmeans, primary, alternative='two-sided')
                    rows.append({
                        'condition': cond, 'viability_def': v, 'inherit_prob': inh,
                        'primary_n': len(primary), 'kmeans_n': len(kmeans),
                        'u': float(stat), 'p_value': float(p),
                        'primary_median': float(np.median(primary)),
                        'kmeans_median': float(np.median(kmeans)),
                        'kmeans_minus_primary_median': float(np.median(kmeans) - np.median(primary)),
                        'test': 'Mann-Whitney U, kmeans_profile vs pooled primary methods',
                    })
    return add_fdr(pd.DataFrame(rows), group_cols=['condition', 'viability_def'])


def build_method_summary_table(results_dir: str):
    results_dir = Path(results_dir)
    rows = []
    for v in VIABILITY_DEFS:
        for cond in ['selective', 'control']:
            if not (results_dir / f'intervention_points_{cond}_{v}.csv').exists():
                continue
            df = _load(results_dir, f'intervention_points_{cond}_{v}.csv')
            tab = (df.groupby(['condition', 'viability_def', 'inherit_prob', 'method', 'analysis_role'])['viability']
                     .agg(['count', 'mean', 'median', 'std', 'min', 'max'])
                     .reset_index())
            rows.append(tab)
    return pd.concat(rows, ignore_index=True)


def build_viability_definition_tests(results_dir: str):
    """Kruskal-Wallis tests asking whether semantic estimates differ by viability definition."""
    results_dir = Path(results_dir)
    rows = []
    for cond in ['selective', 'control']:
        sens_frames = []
        for v in VIABILITY_DEFS:
            if not (results_dir / f'threshold_sensitivity_{cond}_{v}.csv').exists():
                continue
            df = _load(results_dir, f'threshold_sensitivity_{cond}_{v}.csv')
            df['viability_def'] = v
            sens_frames.append(df)
        if not sens_frames:
            continue
        sens = pd.concat(sens_frames, ignore_index=True)
        for inh, part in sens.groupby('inherit_prob'):
            groups = [g['semantic_info'].dropna().to_numpy() for _, g in part.groupby('viability_def')]
            groups = [g for g in groups if len(g) > 0]
            if len(groups) >= 2:
                stat, p = _safe_kruskal(*groups)
                rows.append({
                    'condition': cond, 'inherit_prob': inh,
                    'h': float(stat), 'p_value': float(p),
                    'test': 'Kruskal-Wallis across viability definitions using threshold/smoothing grid',
                })
    return add_fdr(pd.DataFrame(rows), group_cols=['condition'])


def build_entropy_state_definition_summary(results_dir: str):
    """Summarize entropy-based viability diagnostics over Model-B state variables."""
    results_dir = Path(results_dir)
    rows = []
    for v in ENTROPY_VIABILITY_DEFS:
        for cond in ['selective', 'control']:
            path = results_dir / f'intervention_summary_{cond}_{v}.csv'
            if not path.exists():
                continue
            df = pd.read_csv(path).copy()
            df['condition'] = cond
            df['entropy_viability_def'] = v
            df['syntactic_semantic_gap'] = df['syntactic_info_mean'] - df['semantic_info_mean']
            rows.append(df)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def build_entropy_state_definition_tests(results_dir: str):
    """Selective-vs-control tests for each entropy-based viability diagnostic."""
    results_dir = Path(results_dir)
    rows = []
    for v in ENTROPY_VIABILITY_DEFS:
        sel_path = results_dir / f'intervention_points_selective_{v}.csv'
        ctl_path = results_dir / f'intervention_points_control_{v}.csv'
        if not sel_path.exists() or not ctl_path.exists():
            continue
        sel = pd.read_csv(sel_path)
        ctl = pd.read_csv(ctl_path)
        sel = sel[sel['analysis_role'] == 'primary']
        ctl = ctl[ctl['analysis_role'] == 'primary']
        for inh in sorted(set(sel['inherit_prob']).intersection(set(ctl['inherit_prob']))):
            a = sel.loc[sel['inherit_prob'] == inh, 'viability'].dropna().to_numpy()
            b = ctl.loc[ctl['inherit_prob'] == inh, 'viability'].dropna().to_numpy()
            if len(a) and len(b):
                stat, p = mannwhitneyu(a, b, alternative='two-sided')
                rows.append({
                    'entropy_viability_def': v,
                    'inherit_prob': inh,
                    'selective_n': len(a),
                    'control_n': len(b),
                    'u': float(stat),
                    'p_value': float(p),
                    'selective_median': float(np.median(a)),
                    'control_median': float(np.median(b)),
                    'median_difference': float(np.median(a) - np.median(b)),
                    'test': 'Mann-Whitney U, entropy viability, primary no-kmeans intervention points',
                })
    return add_fdr(pd.DataFrame(rows), group_cols=['entropy_viability_def']) if rows else pd.DataFrame()
