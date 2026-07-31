#!/usr/bin/env python3
"""
Run targeted statistical tests for the Model B JRSI manuscript using cached data only.

Outputs:
  stats/paper/targeted_statistical_tests.csv
  stats/paper/targeted_statistical_tests_summary.md

Intended use from repository root:
  python scripts/run_targeted_stats.py

Or from anywhere:
  python scripts/run_targeted_stats.py --root /path/to/modelb_semantic_jsri_repo

The script does not rerun simulations. It reads cached CSV files from results/paper.
"""

from __future__ import annotations

import argparse
import itertools
import math
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats

try:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.stats.anova import anova_lm
except Exception:  # pragma: no cover
    sm = None
    smf = None
    anova_lm = None


RNG_DEFAULT = 20260509
BIOLOGICAL_DEFS = ["excess_over_control", "mean_future_fitness", "threshold_survival"]
ENTROPY_DEFS = [
    "negative_fitness_distribution_entropy",
    "negative_local_metabolite_configuration_entropy",
    "negative_adjacency_state_entropy",
    "negative_protocell_compositional_entropy",
]


def read_csv_required(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required cached data file not found: {path}")
    return pd.read_csv(path)


def bh_fdr(pvals: Sequence[float]) -> np.ndarray:
    p = np.asarray([np.nan if x is None else x for x in pvals], dtype=float)
    q = np.full_like(p, np.nan, dtype=float)
    ok = np.isfinite(p)
    if ok.sum() == 0:
        return q
    idx = np.where(ok)[0]
    order = idx[np.argsort(p[ok])]
    ranked = p[order]
    m = len(ranked)
    adj = ranked * m / np.arange(1, m + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.clip(adj, 0.0, 1.0)
    q[order] = adj
    return q


def bootstrap_ci(values: Sequence[float], n_boot: int = 5000, rng: Optional[np.random.Generator] = None) -> Tuple[float, float]:
    vals = np.asarray(values, dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return (np.nan, np.nan)
    if len(vals) == 1:
        return (float(vals[0]), float(vals[0]))
    if rng is None:
        rng = np.random.default_rng(RNG_DEFAULT)
    means = np.empty(n_boot, dtype=float)
    n = len(vals)
    for i in range(n_boot):
        means[i] = rng.choice(vals, size=n, replace=True).mean()
    return tuple(np.percentile(means, [2.5, 97.5]).astype(float))


def sign_flip_pvalue(diffs: Sequence[float], alternative: str = "two-sided") -> float:
    """Exact sign-flip p-value for paired differences when n <= 20; otherwise Monte Carlo."""
    d = np.asarray(diffs, dtype=float)
    d = d[np.isfinite(d)]
    d = d[d != 0]
    n = len(d)
    if n == 0:
        return np.nan
    obs = d.mean()
    if n <= 20:
        vals = []
        for signs in itertools.product([-1.0, 1.0], repeat=n):
            vals.append(np.mean(np.asarray(signs) * d))
        null = np.asarray(vals)
    else:
        rng = np.random.default_rng(RNG_DEFAULT)
        signs = rng.choice([-1.0, 1.0], size=(20000, n), replace=True)
        null = (signs * d).mean(axis=1)
    if alternative == "greater":
        return float((np.sum(null >= obs) + 1) / (len(null) + 1))
    if alternative == "less":
        return float((np.sum(null <= obs) + 1) / (len(null) + 1))
    return float((np.sum(np.abs(null) >= abs(obs)) + 1) / (len(null) + 1))


def permutation_mean_diff(x: Sequence[float], y: Sequence[float], n_perm: int = 20000, rng: Optional[np.random.Generator] = None) -> Tuple[float, float]:
    """Two-sided independent-label permutation test for difference in means x - y."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x = x[np.isfinite(x)]
    y = y[np.isfinite(y)]
    if len(x) == 0 or len(y) == 0:
        return (np.nan, np.nan)
    obs = float(x.mean() - y.mean())
    pooled = np.concatenate([x, y])
    nx = len(x)
    if rng is None:
        rng = np.random.default_rng(RNG_DEFAULT)
    count = 0
    for _ in range(n_perm):
        perm = rng.permutation(pooled)
        stat = perm[:nx].mean() - perm[nx:].mean()
        if abs(stat) >= abs(obs):
            count += 1
    p = (count + 1) / (n_perm + 1)
    return obs, float(p)


def load_baseline(results_dir: Path) -> pd.DataFrame:
    sel = read_csv_required(results_dir / "baseline_selective_replicate_deltas.csv").copy()
    ctl = read_csv_required(results_dir / "baseline_control_replicate_deltas.csv").copy()
    sel["condition"] = "selective"
    ctl["condition"] = "control"
    df = pd.concat([sel, ctl], ignore_index=True)
    df["inherit_prob"] = df["inherit_prob"].astype(float)
    return df


def omnibus_regime_by_fidelity_tests(baseline: pd.DataFrame, rng: np.random.Generator, n_perm: int) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    if smf is None or anova_lm is None:
        rows.append({
            "analysis": "omnibus_regime_by_fidelity",
            "metric": "delta_mi/delta_fitness",
            "condition": "all",
            "comparison": "statsmodels_unavailable",
            "statistic": np.nan,
            "effect": np.nan,
            "p_value": np.nan,
            "ci_low": np.nan,
            "ci_high": np.nan,
            "n": len(baseline),
            "notes": "Install statsmodels to run omnibus ANOVA tests.",
        })
        return rows

    df = baseline.copy()
    df["inherit_prob_cat"] = df["inherit_prob"].map(lambda v: f"{v:.1f}")

    for metric in ["delta_mi", "delta_fitness"]:
        # Categorical fidelity interaction: does condition effect vary across the fidelity sweep?
        model = smf.ols(f"{metric} ~ C(condition) * C(inherit_prob_cat)", data=df).fit()
        aov = anova_lm(model, typ=2)
        term = "C(condition):C(inherit_prob_cat)"
        f_stat = float(aov.loc[term, "F"])
        p_param = float(aov.loc[term, "PR(>F)"])

        # Permutation p-value: shuffle condition labels within each inheritance fidelity.
        perm_stats = np.empty(n_perm, dtype=float)
        for i in range(n_perm):
            tmp = df.copy()
            tmp["condition"] = tmp.groupby("inherit_prob_cat")["condition"].transform(
                lambda s: rng.permutation(s.to_numpy())
            )
            perm_model = smf.ols(f"{metric} ~ C(condition) * C(inherit_prob_cat)", data=tmp).fit()
            perm_aov = anova_lm(perm_model, typ=2)
            perm_stats[i] = float(perm_aov.loc[term, "F"])
        p_perm = float((np.sum(perm_stats >= f_stat) + 1) / (n_perm + 1))

        rows.append({
            "analysis": "omnibus_regime_by_fidelity",
            "metric": metric,
            "condition": "all",
            "comparison": "C(condition):C(inherit_prob)",
            "statistic": f_stat,
            "effect": np.nan,
            "p_value": p_perm,
            "parametric_p_value": p_param,
            "ci_low": np.nan,
            "ci_high": np.nan,
            "n": len(df),
            "notes": "Two-way OLS ANOVA interaction; permutation shuffles condition labels within fidelity.",
        })

        # Continuous slope interaction for compact reporting.
        cont = smf.ols(f"{metric} ~ C(condition) * inherit_prob", data=df).fit(cov_type="HC3")
        term2 = "C(condition)[T.selective]:inherit_prob"
        if term2 not in cont.params.index:
            term2 = [x for x in cont.params.index if ":inherit_prob" in x][0]
        rows.append({
            "analysis": "omnibus_regime_by_fidelity",
            "metric": metric,
            "condition": "all",
            "comparison": "condition_x_linear_fidelity_slope",
            "statistic": float(cont.tvalues[term2]),
            "effect": float(cont.params[term2]),
            "p_value": float(cont.pvalues[term2]),
            "parametric_p_value": float(cont.pvalues[term2]),
            "ci_low": float(cont.conf_int().loc[term2, 0]),
            "ci_high": float(cont.conf_int().loc[term2, 1]),
            "n": len(df),
            "notes": "HC3 robust OLS slope interaction; effect is selective-minus-control slope difference.",
        })
    return rows


def fit_piecewise_transition(x: Sequence[float], y: Sequence[float], grid: Optional[Sequence[float]] = None) -> Dict[str, float]:
    """Continuous two-segment linear model y = a + b*x + c*max(0, x - pc)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    x = x[ok]
    y = y[ok]
    if len(x) < 5:
        return {"transition": np.nan, "sse": np.nan, "slope_before": np.nan, "slope_after": np.nan}
    if grid is None:
        uniq = np.sort(np.unique(x))
        grid = uniq[1:-1]
    best = None
    for pc in grid:
        X = np.column_stack([np.ones_like(x), x, np.maximum(0.0, x - pc)])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X.dot(beta)
        sse = float(np.sum(resid ** 2))
        out = {
            "transition": float(pc),
            "sse": sse,
            "slope_before": float(beta[1]),
            "slope_after": float(beta[1] + beta[2]),
        }
        if best is None or sse < best["sse"]:
            best = out
    return best if best is not None else {"transition": np.nan, "sse": np.nan, "slope_before": np.nan, "slope_after": np.nan}


def transition_diagnostics(baseline: pd.DataFrame, results_dir: Path, rng: np.random.Generator, n_boot: int) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []

    # Baseline replicate deltas by condition and metric.
    for condition in ["selective", "control"]:
        sub = baseline[baseline["condition"] == condition]
        for metric in ["delta_mi", "delta_fitness"]:
            means = sub.groupby("inherit_prob", as_index=False)[metric].mean()
            fit = fit_piecewise_transition(means["inherit_prob"], means[metric])
            boots = []
            for _ in range(n_boot):
                sampled = []
                for inh, g in sub.groupby("inherit_prob"):
                    vals = g[metric].to_numpy(dtype=float)
                    sampled.append((float(inh), float(rng.choice(vals, size=len(vals), replace=True).mean())))
                boot_df = pd.DataFrame(sampled, columns=["inherit_prob", metric]).sort_values("inherit_prob")
                boots.append(fit_piecewise_transition(boot_df["inherit_prob"], boot_df[metric])["transition"])
            lo, hi = np.nanpercentile(boots, [2.5, 97.5])
            rows.append({
                "analysis": "empirical_transition_diagnostic",
                "metric": metric,
                "condition": condition,
                "comparison": "piecewise_linear_final_outcome",
                "statistic": fit["transition"],
                "effect": fit["slope_after"] - fit["slope_before"],
                "p_value": np.nan,
                "ci_low": float(lo),
                "ci_high": float(hi),
                "n": len(sub),
                "notes": "Model-specific diagnostic from cached final deltas; not a general threshold theory.",
            })

    # Semantic information transitions from summary files.
    for condition in ["selective", "control"]:
        path = results_dir / f"intervention_summary_{condition}_excess_over_control.csv"
        if not path.exists():
            continue
        summ = pd.read_csv(path).sort_values("inherit_prob")
        for metric in ["semantic_info_mean", "value_of_information_mean", "semantic_efficiency_mean"]:
            if metric not in summ.columns:
                continue
            fit = fit_piecewise_transition(summ["inherit_prob"], summ[metric])
            rows.append({
                "analysis": "empirical_transition_diagnostic",
                "metric": metric,
                "condition": condition,
                "comparison": "piecewise_linear_summary_excess_over_control",
                "statistic": fit["transition"],
                "effect": fit["slope_after"] - fit["slope_before"],
                "p_value": np.nan,
                "ci_low": np.nan,
                "ci_high": np.nan,
                "n": len(summ),
                "notes": "Summary-level transition diagnostic; no replicate bootstrap because only aggregated semantic summary is cached.",
            })
    return rows


def replicate_level_intervention_tests(results_dir: Path, rng: np.random.Generator, n_perm: int) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    sel_path = results_dir / "intervention_points_selective_excess_over_control.csv"
    ctl_path = results_dir / "intervention_points_control_excess_over_control.csv"
    if not (sel_path.exists() and ctl_path.exists()):
        return rows
    pts = pd.concat([pd.read_csv(sel_path), pd.read_csv(ctl_path)], ignore_index=True)
    pts = pts[pts.get("analysis_role", "primary") == "primary"].copy()
    if pts.empty:
        return rows

    # Aggregate intervention points to replicate-level means to avoid treating intervention points as independent runs.
    rep = (
        pts.groupby(["condition", "inherit_prob", "rep"], as_index=False)
        .agg(
            viability_mean=("viability", "mean"),
            actual_viability_mean=("actual_viability", "mean"),
            syntactic_info_mean=("syntactic_info", "mean"),
            n_points=("viability", "size"),
        )
    )

    pvals = []
    row_idx = []
    for inh, g in rep.groupby("inherit_prob"):
        x = g[g["condition"] == "selective"]["viability_mean"].to_numpy(dtype=float)
        y = g[g["condition"] == "control"]["viability_mean"].to_numpy(dtype=float)
        if len(x) == 0 or len(y) == 0:
            continue
        u = stats.mannwhitneyu(x, y, alternative="greater")
        effect, p_perm = permutation_mean_diff(x, y, n_perm=n_perm, rng=rng)
        lo, hi = bootstrap_ci([rng.choice(x, size=len(x), replace=True).mean() - rng.choice(y, size=len(y), replace=True).mean() for _ in range(2000)], n_boot=1000, rng=rng)
        rows.append({
            "analysis": "replicate_level_intervention_contrast",
            "metric": "mean_intervention_viability",
            "condition": "selective_vs_control",
            "comparison": f"inherit_prob={inh:.1f}",
            "inherit_prob": float(inh),
            "statistic": float(u.statistic),
            "effect": float(effect),
            "p_value": float(p_perm),
            "mannwhitney_p_value": float(u.pvalue),
            "ci_low": float(lo),
            "ci_high": float(hi),
            "n": int(len(x) + len(y)),
            "notes": "Replicate-level primary-intervention confirmation; effect is selective-control mean viability.",
        })
        pvals.append(p_perm)
        row_idx.append(len(rows) - 1)
    q = bh_fdr(pvals)
    for i, qi in zip(row_idx, q):
        rows[i]["q_value"] = float(qi)
    return rows


def frontier_and_ablation_tests(results_dir: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    sel_path = results_dir / "intervention_summary_selective_excess_over_control.csv"
    ctl_path = results_dir / "intervention_summary_control_excess_over_control.csv"
    if sel_path.exists() and ctl_path.exists():
        sel = pd.read_csv(sel_path).sort_values("inherit_prob")
        ctl = pd.read_csv(ctl_path).sort_values("inherit_prob")
        merged = sel.merge(ctl, on="inherit_prob", suffixes=("_selective", "_control"))
        for metric in ["frontier_max_viability", "actual_viability_mean", "value_of_information_mean"]:
            xs = merged[f"{metric}_selective"].to_numpy(float)
            ys = merged[f"{metric}_control"].to_numpy(float)
            diffs = xs - ys
            lo, hi = bootstrap_ci(diffs, n_boot=5000)
            rows.append({
                "analysis": "frontier_regime_contrast",
                "metric": metric,
                "condition": "selective_vs_control",
                "comparison": "paired_by_inheritance_fidelity",
                "statistic": float(np.mean(diffs)),
                "effect": float(np.mean(diffs)),
                "p_value": sign_flip_pvalue(diffs, alternative="two-sided"),
                "ci_low": float(lo),
                "ci_high": float(hi),
                "n": len(diffs),
                "notes": "Paired sign-flip test across inheritance fidelities; effect is selective-control.",
            })
        # Actual-minus-frontier gap, which is central to Fig. 5c.
        gap_sel = merged["actual_viability_mean_selective"] - merged["frontier_max_viability_selective"]
        gap_ctl = merged["actual_viability_mean_control"] - merged["frontier_max_viability_control"]
        diffs = (gap_sel - gap_ctl).to_numpy(float)
        lo, hi = bootstrap_ci(diffs, n_boot=5000)
        rows.append({
            "analysis": "frontier_regime_contrast",
            "metric": "actual_minus_frontier_gap",
            "condition": "selective_vs_control",
            "comparison": "paired_by_inheritance_fidelity",
            "statistic": float(np.mean(diffs)),
            "effect": float(np.mean(diffs)),
            "p_value": sign_flip_pvalue(diffs, alternative="two-sided"),
            "ci_low": float(lo),
            "ci_high": float(hi),
            "n": len(diffs),
            "notes": "Tests whether Fig. 5c gap is larger in sequence-selective runs.",
        })

    # Method ablation: primary vs all-methods and primary vs kmeans diagnostic for selective excess-over-control.
    primary_path = results_dir / "intervention_summary_selective_excess_over_control.csv"
    all_path = results_dir / "intervention_summary_selective_excess_over_control_all_methods_diagnostic.csv"
    km_path = results_dir / "intervention_summary_selective_excess_over_control_kmeans_profile_mechanistic.csv"
    comparisons = []
    if primary_path.exists() and all_path.exists():
        comparisons.append(("all_methods_diagnostic_minus_primary", pd.read_csv(all_path), pd.read_csv(primary_path)))
    if primary_path.exists() and km_path.exists():
        comparisons.append(("kmeans_profile_minus_primary", pd.read_csv(km_path), pd.read_csv(primary_path)))
    for name, a, b in comparisons:
        m = a.merge(b, on="inherit_prob", suffixes=("_a", "_primary")).sort_values("inherit_prob")
        for metric in ["semantic_info_mean", "frontier_max_viability", "semantic_efficiency_mean"]:
            ca = f"{metric}_a"
            cb = f"{metric}_primary"
            if ca not in m.columns or cb not in m.columns:
                continue
            diffs = (m[ca] - m[cb]).to_numpy(float)
            lo, hi = bootstrap_ci(diffs, n_boot=5000)
            rows.append({
                "analysis": "method_ablation_summary_contrast",
                "metric": metric,
                "condition": "selective_excess_over_control",
                "comparison": name,
                "statistic": float(np.mean(diffs)),
                "effect": float(np.mean(diffs)),
                "p_value": sign_flip_pvalue(diffs, alternative="two-sided"),
                "ci_low": float(lo),
                "ci_high": float(hi),
                "n": len(diffs),
                "notes": "Paired across inheritance fidelities; diagnostic-primary. Use as support, not as primary pooled estimate.",
            })
    return rows


def entropy_specificity_tests(results_dir: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    bio_path = results_dir / "intervention_summary_selective_excess_over_control.csv"
    if not bio_path.exists():
        return rows
    bio = pd.read_csv(bio_path)[["inherit_prob", "semantic_info_mean"]].rename(columns={"semantic_info_mean": "bio_semantic"})

    all_entropy_vals = []
    for viability_def in ENTROPY_DEFS:
        path = results_dir / f"intervention_summary_selective_{viability_def}.csv"
        if not path.exists():
            continue
        ent = pd.read_csv(path)[["inherit_prob", "semantic_info_mean"]].rename(columns={"semantic_info_mean": "entropy_semantic"})
        all_entropy_vals.extend(ent["entropy_semantic"].dropna().astype(float).tolist())
        m = bio.merge(ent, on="inherit_prob")
        diffs = (m["bio_semantic"] - m["entropy_semantic"]).to_numpy(float)
        lo, hi = bootstrap_ci(diffs, n_boot=5000)
        rows.append({
            "analysis": "entropy_state_specificity",
            "metric": "semantic_info_mean",
            "condition": "selective",
            "comparison": f"excess_over_control_minus_{viability_def}",
            "statistic": float(np.mean(diffs)),
            "effect": float(np.mean(diffs)),
            "p_value": sign_flip_pvalue(diffs, alternative="greater"),
            "ci_low": float(lo),
            "ci_high": float(hi),
            "n": len(diffs),
            "notes": "Paired across inheritance fidelities; tests biological definition gives larger semantic estimates than entropy-state control.",
        })
    if all_entropy_vals:
        vals = np.asarray(all_entropy_vals, dtype=float)
        lo, hi = bootstrap_ci(vals, n_boot=5000)
        rows.append({
            "analysis": "entropy_state_specificity",
            "metric": "semantic_info_mean",
            "condition": "selective_entropy_controls",
            "comparison": "upper_bound_across_entropy_definitions",
            "statistic": float(np.mean(vals)),
            "effect": float(np.max(vals)),
            "p_value": np.nan,
            "ci_low": float(lo),
            "ci_high": float(hi),
            "n": len(vals),
            "notes": "Mean and max entropy-state semantic estimate across cached entropy definitions and inheritance fidelities.",
        })
    return rows


def write_summary(out_csv: Path, out_md: Path, df: pd.DataFrame) -> None:
    lines = []
    lines.append("# Targeted statistical tests summary\n")
    lines.append(f"Source CSV: `{out_csv.name}`\n")
    lines.append("These tests use cached data only; no simulations were rerun.\n")

    def fmt_p(p):
        if pd.isna(p):
            return "NA"
        if p < 1e-4:
            return f"{p:.2e}"
        return f"{p:.4f}"

    def markdown_table(table: pd.DataFrame) -> str:
        try:
            return table.to_markdown(index=False)
        except ImportError:
            values = table.astype(str)
            cols = list(values.columns)
            rows = values.to_numpy().tolist()
            widths = [
                max(len(str(col)), *(len(str(row[i])) for row in rows)) if rows else len(str(col))
                for i, col in enumerate(cols)
            ]
            header = "| " + " | ".join(str(col).ljust(widths[i]) for i, col in enumerate(cols)) + " |"
            divider = "| " + " | ".join("-" * widths[i] for i in range(len(cols))) + " |"
            body = [
                "| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(cols))) + " |"
                for row in rows
            ]
            return "\n".join([header, divider, *body])

    for analysis, g in df.groupby("analysis", sort=False):
        lines.append(f"\n## {analysis}\n")
        keep_cols = [c for c in ["metric", "condition", "comparison", "inherit_prob", "effect", "statistic", "p_value", "q_value", "ci_low", "ci_high", "n"] if c in g.columns]
        tmp = g[keep_cols].copy()
        for c in ["effect", "statistic", "ci_low", "ci_high"]:
            if c in tmp.columns:
                tmp[c] = tmp[c].map(lambda x: "NA" if pd.isna(x) else f"{float(x):.6g}")
        for c in ["p_value", "q_value"]:
            if c in tmp.columns:
                tmp[c] = tmp[c].map(fmt_p)
        lines.append(markdown_table(tmp))
        lines.append("\n")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run targeted manuscript stats from cached Model B outputs.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="Repository root.")
    parser.add_argument("--results-dir", type=Path, default=None, help="Directory containing cached result CSV files.")
    parser.add_argument("--stats-dir", type=Path, default=None, help="Directory for output statistics.")
    parser.add_argument("--n-perm", type=int, default=10000, help="Permutation iterations for omnibus/intervention tests.")
    parser.add_argument("--n-boot", type=int, default=2000, help="Bootstrap iterations for transition diagnostics.")
    parser.add_argument("--seed", type=int, default=RNG_DEFAULT, help="Random seed.")
    args = parser.parse_args()

    root = args.root.resolve()
    results_dir = args.results_dir.resolve() if args.results_dir else root / "results" / "paper"
    stats_dir = args.stats_dir.resolve() if args.stats_dir else root / "stats" / "paper"
    stats_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    rows: List[Dict[str, object]] = []

    baseline = load_baseline(results_dir)
    rows.extend(omnibus_regime_by_fidelity_tests(baseline, rng, args.n_perm))
    rows.extend(transition_diagnostics(baseline, results_dir, rng, args.n_boot))
    rows.extend(replicate_level_intervention_tests(results_dir, rng, args.n_perm))
    rows.extend(frontier_and_ablation_tests(results_dir))
    rows.extend(entropy_specificity_tests(results_dir))

    out = pd.DataFrame(rows)
    if "p_value" in out.columns:
        # Global q-values are not ideal across heterogeneous tests, but useful as a conservative screen.
        out["global_q_value"] = bh_fdr(out["p_value"].to_numpy())
    if "q_value" not in out.columns:
        out["q_value"] = np.nan
    # Put common columns first.
    first = ["analysis", "metric", "condition", "comparison", "inherit_prob", "statistic", "effect", "p_value", "q_value", "global_q_value", "ci_low", "ci_high", "n", "notes"]
    cols = [c for c in first if c in out.columns] + [c for c in out.columns if c not in first]
    out = out[cols]

    out_csv = stats_dir / "targeted_statistical_tests.csv"
    out_md = stats_dir / "targeted_statistical_tests_summary.md"
    out.to_csv(out_csv, index=False)
    write_summary(out_csv, out_md, out)

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    print("Done. No simulations were rerun.")


if __name__ == "__main__":
    main()
