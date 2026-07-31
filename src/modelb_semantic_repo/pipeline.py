import json
from pathlib import Path
import pandas as pd
import numpy as np
from .modes import get_mode_parameters
from .original_model.sweeps import run_inheritance_sweep, mean_sem
from .interventions import analyze_condition, VIABILITY_DEFS


def _json_ready(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_ready(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _summarize_baseline(fit_results, mi_results, inherit_probs):
    rows = []
    replicate_rows = []
    for inh in inherit_probs:
        fits = fit_results[inh]
        mis = mi_results[inh]
        dfit = fits[:, -1] - fits[:, 0]
        dmi = mis[:, -1] - mis[:, 0]
        mean_dfit, sem_dfit = mean_sem(dfit)
        mean_dmi, sem_dmi = mean_sem(dmi)
        rows.append({
            'inherit_prob': inh,
            'delta_fitness_mean': mean_dfit,
            'delta_fitness_sem': sem_dfit,
            'delta_mi_mean': mean_dmi,
            'delta_mi_sem': sem_dmi,
            'mi_final_mean': float(np.mean(mis[:, -1])),
            'fitness_final_mean': float(np.mean(fits[:, -1])),
        })
        for rep_idx in range(len(dfit)):
            replicate_rows.append({'inherit_prob': inh, 'rep': rep_idx, 'delta_fitness': float(dfit[rep_idx]), 'delta_mi': float(dmi[rep_idx])})
    return pd.DataFrame(rows), pd.DataFrame(replicate_rows)


def run_pipeline(mode: str, outdir: str, seed: int = 7):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    params = get_mode_parameters(mode)
    metadata = {'mode': mode, 'parameters': _json_ready(params), 'seed': seed}
    (outdir / 'run_metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')

    inherit_probs = params['inherit_probs']
    fit_sel, mi_sel, final_sel = run_inheritance_sweep(inherit_probs, params['motif_affinity_matrix'], params, label='selective', seed_offset=seed * 100, collect_final_states=True)
    fit_ctl, mi_ctl, final_ctl = run_inheritance_sweep(inherit_probs, params['motif_affinity_matrix_no_aff'], params, label='control', seed_offset=seed * 200, collect_final_states=True)

    sel_summary, sel_reps = _summarize_baseline(fit_sel, mi_sel, inherit_probs)
    ctl_summary, ctl_reps = _summarize_baseline(fit_ctl, mi_ctl, inherit_probs)
    sel_summary.to_csv(outdir / 'baseline_selective_summary.csv', index=False)
    ctl_summary.to_csv(outdir / 'baseline_control_summary.csv', index=False)
    sel_reps.to_csv(outdir / 'baseline_selective_replicate_deltas.csv', index=False)
    ctl_reps.to_csv(outdir / 'baseline_control_replicate_deltas.csv', index=False)

    for v in VIABILITY_DEFS:
        analyze_condition(final_sel, final_ctl, params['motif_affinity_matrix'], params, 'selective', outdir, v)
        analyze_condition(final_ctl, final_ctl, params['motif_affinity_matrix_no_aff'], params, 'control', outdir, v)
    return outdir
