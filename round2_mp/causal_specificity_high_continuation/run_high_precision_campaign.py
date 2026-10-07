from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

R1 = Path(os.environ.get('JRSI_R1_ROOT', '/mnt/data/JRSI_R2_CTRL/JRSI_MAJOR_REVISION_PHASE7_GATE8_PASSED_v1'))
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
PHASE4 = R1 / 'results' / 'phase4_core'
PHASE5 = R1 / 'results' / 'phase5_causal_specificity'
PRIOR_R2 = Path('/mnt/data/JRSI_R2_MP_CONTROLS')

import sys
sys.path.insert(0, str(R1 / 'src'))

from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.phase5 import (
    enumerate_matched_topologies,
    select_alternative_topologies,
    reproduce_with_selection_strength,
    precompute_state_cdf,
    observe_population_cached,
    generate_topology_schedule,
    paired_sign_randomization,
    paired_bootstrap_interval,
    _bh_adjust,
)
from modelb_semantic_repo.rng import ContinuationStream, AnalysisStream

CONT_ROOT = 2026073104
TOPOLOGY_ROOT = 2026073105
ANALYSIS_ROOT = 2026100202
CONT_INDICES = tuple(range(2, 66))
N_CONT = len(CONT_INDICES)
HORIZON = 36
N_BOOT = 2000
N_PERM = 9999


@njit(cache=True)
def observe_mp_constant(population, native_kernel, productive, anti, reward, penalty, uniforms):
    n_cells, n_seqs, seq_len = population.shape
    chain_len = seq_len - 4
    n_segments = native_kernel.shape[1]
    n_states = native_kernel.shape[2]
    seg_len = chain_len // n_segments
    total = n_cells * n_seqs * chain_len

    segments = np.empty(total, dtype=np.int64)
    sums = np.zeros((n_segments, n_states), dtype=np.float64)
    counts = np.zeros(n_segments, dtype=np.int64)
    idx = 0
    for ci in range(n_cells):
        for si in range(n_seqs):
            for pos in range(chain_len):
                motif = 0
                for k in range(5):
                    motif = motif * 4 + int(population[ci, si, pos + k])
                seg = pos // seg_len
                if seg >= n_segments:
                    seg = n_segments - 1
                segments[idx] = seg
                for z in range(n_states):
                    sums[seg, z] += native_kernel[motif, seg, z]
                counts[seg] += 1
                idx += 1
    for s in range(n_segments):
        if counts[s] > 0:
            inv = 1.0 / counts[s]
            for z in range(n_states):
                sums[s, z] *= inv

    fitness = np.empty(n_cells, dtype=np.float64)
    idx = 0
    for ci in range(n_cells):
        prod_count = 0.0
        anti_count = 0.0
        for si in range(n_seqs):
            prev = -1
            for pos in range(chain_len):
                seg = segments[idx]
                r = uniforms[idx]
                cdf = 0.0
                chosen = n_states - 1
                for z in range(n_states):
                    cdf += sums[seg, z]
                    if r <= cdf:
                        chosen = z
                        break
                idx += 1
                if pos > 0:
                    if productive[prev, chosen]:
                        prod_count += 1.0
                    if anti[prev, chosen]:
                        anti_count += 1.0
                prev = chosen
        f = 1.0 + reward * (prod_count / n_seqs) - penalty * (anti_count / n_seqs)
        if f < 0.1:
            f = 0.1
        fitness[ci] = f
    return fitness


def kernel_from_matrix(matrix: np.ndarray, params: dict) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float64)
    n_m, n_z = matrix.shape
    n_s = len(params['segment_favored_met'])
    out = np.empty((n_m, n_s, n_z), dtype=np.float64)
    for s in range(n_s):
        logits = matrix.copy()
        logits[:, int(params['segment_favored_met'][s])] += float(params['bias_strength'])
        x = logits / float(params['temperature'])
        x -= x.max(axis=1, keepdims=True)
        e = np.exp(x)
        out[:, s, :] = e / e.sum(axis=1, keepdims=True)
    return np.ascontiguousarray(out, dtype=np.float64)


def starting_marginal_error(population: np.ndarray, kernel: np.ndarray, params: dict) -> float:
    n_cells, n_seqs, seq_len = population.shape
    chain_len = seq_len - 4
    n_s = kernel.shape[1]
    n_z = kernel.shape[2]
    seg_len = chain_len // n_s
    native_sum = np.zeros((n_s, n_z), dtype=float)
    counts = np.zeros(n_s, dtype=int)
    motif_counts = np.zeros((n_s, kernel.shape[0]), dtype=int)
    for ci in range(n_cells):
        for si in range(n_seqs):
            for pos in range(chain_len):
                motif = 0
                for k in range(5):
                    motif = motif * 4 + int(population[ci, si, pos + k])
                s = min(pos // seg_len, n_s - 1)
                native_sum[s] += kernel[motif, s]
                counts[s] += 1
                motif_counts[s, motif] += 1
    native = native_sum / counts[:, None]
    q = np.zeros_like(native)
    for s in range(n_s):
        w = motif_counts[s] / motif_counts[s].sum()
        q[s] = (w[:, None] * kernel[:, s, :]).sum(axis=0)
    return float(np.max(np.abs(native - q)))


def pair_simulation(population, matrix, params, selection_strength, pairing_id, continuation_index,
                    fixed_topology_id, schedule):
    topologies = enumerate_matched_topologies()
    lookup = {t.topology_id: t for t in topologies}
    native_cdf = precompute_state_cdf(matrix, params)
    native_kernel = kernel_from_matrix(matrix, params)

    # Separate stream objects with identical keys guarantee common random numbers.
    actual_stream = ContinuationStream(CONT_ROOT, pairing_id, continuation_index)
    mp_stream = ContinuationStream(CONT_ROOT, pairing_id, continuation_index)
    actual_obs_rng = actual_stream.observation_generator()
    actual_prop_rng = actual_stream.propagation_generator()
    mp_obs_rng = mp_stream.observation_generator()
    mp_prop_rng = mp_stream.propagation_generator()

    pop_a = np.array(population, copy=True)
    pop_m = np.array(population, copy=True)
    n_windows = params['n_cells'] * params['n_seqs'] * (params['seq_len'] - 4)
    actual_vals = np.empty(HORIZON, dtype=float)
    mp_vals = np.empty(HORIZON, dtype=float)

    for h in range(HORIZON):
        topology = lookup[fixed_topology_id] if fixed_topology_id is not None else lookup[str(schedule[h])]
        fit_a, _, _ = observe_population_cached(pop_a, native_cdf, params, topology, actual_obs_rng)
        uniforms_m = mp_obs_rng.random(n_windows)
        fit_m = observe_mp_constant(
            pop_m, native_kernel, topology.productive_pairs, topology.anti_pairs,
            float(params['reward_strength']), float(params['penalty_strength']), uniforms_m
        )
        actual_vals[h] = float(np.mean(fit_a))
        mp_vals[h] = float(np.mean(fit_m))
        pop_a = reproduce_with_selection_strength(
            pop_a, fit_a, float(params['mutation_rate']), 1.0, actual_prop_rng, float(selection_strength)
        )
        pop_m = reproduce_with_selection_strength(
            pop_m, fit_m, float(params['mutation_rate']), 1.0, mp_prop_rng, float(selection_strength)
        )
    return float(actual_vals.mean()), float(mp_vals.mean())


def new_schedule(pairing_id: str, continuation_index: int):
    topologies = enumerate_matched_topologies()
    return generate_topology_schedule(
        topologies,
        root_seed=TOPOLOGY_ROOT,
        purpose='phase5-unstable-topology-continuation',
        keys=(pairing_id, continuation_index),
        length=HORIZON,
    )


def native_job(rep: int):
    params = default_parameters()
    topologies = enumerate_matched_topologies()
    native, _, _ = select_alternative_topologies(topologies)
    bid = f'selective_p1.0_r{rep:02d}'
    population = np.asarray(np.load(PHASE4 / 'states' / 'selective' / 'p1.0' / f'rep_{rep:02d}.npz')['population'])
    matrix = np.asarray(params['motif_affinity_matrix'])
    err = starting_marginal_error(population, kernel_from_matrix(matrix, params), params)
    rows = []
    for c in CONT_INDICES:
        actual, mp = pair_simulation(population, matrix, params, 1.0, bid, c, native.topology_id, None)
        rows.append({
            'condition': 'native_full', 'control_family': 'native_full', 'realization': 0,
            'seed_block': rep, 'baseline_replicate': bid, 'pairing_baseline_replicate': bid,
            'continuation_index': c, 'selection_strength': 1.0,
            'evaluation_topology_id': native.topology_id,
            'actual_viability': actual, 'mp_constant_viability': mp,
            'delta_mp': actual-mp, 'starting_expected_marginal_max_abs_error': err,
        })
    return rows


def spec_job(spec: dict):
    params = default_parameters()
    state_path = R1 / spec['state_path']
    if not state_path.exists():
        raise FileNotFoundError(state_path)
    population = np.asarray(np.load(state_path)['population'])
    matrix = np.asarray(params['motif_affinity_matrix'])
    if spec['affinity_mode'] == 'deranged':
        matrix = matrix[np.asarray(spec['affinity_permutation'], dtype=np.int64)]
    err = starting_marginal_error(population, kernel_from_matrix(matrix, params), params)
    fixed = str(spec['fixed_topology_id']) if spec['fixed_topology_id'] is not None else None
    pairing_id = str(spec['pairing_baseline_replicate'])
    rows = []
    for c in CONT_INDICES:
        schedule = new_schedule(pairing_id, c) if spec['dynamic_topology'] else None
        actual, mp = pair_simulation(
            population, matrix, params, float(spec['selection_strength']),
            pairing_id, c, fixed, schedule
        )
        rows.append({
            'condition': spec['condition'], 'control_family': spec['control_family'],
            'realization': int(spec['realization']), 'seed_block': int(spec['seed_block']),
            'baseline_replicate': spec['baseline_replicate'],
            'pairing_baseline_replicate': pairing_id,
            'continuation_index': c, 'selection_strength': float(spec['selection_strength']),
            'evaluation_topology_id': spec['fixed_topology_id'] or 'temporally_unstable',
            'actual_viability': actual, 'mp_constant_viability': mp,
            'delta_mp': actual-mp, 'starting_expected_marginal_max_abs_error': err,
        })
    return rows


def aggregate_seed_blocks(cont: pd.DataFrame, metric: str) -> pd.DataFrame:
    real = cont.groupby(
        ['condition','control_family','realization','seed_block','baseline_replicate'], as_index=False
    )[metric].mean()
    fam = real.groupby(['control_family','seed_block'], as_index=False)[metric].mean()
    wide = fam.pivot(index='seed_block', columns='control_family', values=metric).reset_index()
    required = {
        'native_full','selection_neutral','selection_reduced','affinity_reassigned','topology_mismatch',
        'alternative_a_native','alternative_a_cross_b','alternative_b_native','alternative_b_cross_a','temporally_unstable'
    }
    miss = required.difference(wide.columns)
    if miss:
        raise RuntimeError(f'missing families for {metric}: {sorted(miss)}')
    wide['alternative_native_mean'] = 0.5*(wide['alternative_a_native']+wide['alternative_b_native'])
    wide['alternative_cross_mean'] = 0.5*(wide['alternative_a_cross_b']+wide['alternative_b_cross_a'])
    wide['contrast_full_minus_neutral'] = wide['native_full'] - wide['selection_neutral']
    wide['contrast_full_minus_reduced'] = wide['native_full'] - wide['selection_reduced']
    wide['contrast_native_minus_affinity_reassigned'] = wide['native_full'] - wide['affinity_reassigned']
    wide['contrast_native_minus_topology_mismatch'] = wide['native_full'] - wide['topology_mismatch']
    wide['contrast_alternative_native_minus_cross'] = wide['alternative_native_mean'] - wide['alternative_cross_mean']
    wide['contrast_stable_minus_unstable'] = wide['alternative_native_mean'] - wide['temporally_unstable']
    return wide


def infer_contrasts(wide: pd.DataFrame, metric_label: str, analysis_root: int = ANALYSIS_ROOT) -> pd.DataFrame:
    specs = [
        ('full_minus_neutral','contrast_full_minus_neutral'),
        ('full_minus_reduced','contrast_full_minus_reduced'),
        ('native_minus_affinity_reassigned','contrast_native_minus_affinity_reassigned'),
        ('native_minus_topology_mismatch','contrast_native_minus_topology_mismatch'),
        ('alternative_native_minus_cross','contrast_alternative_native_minus_cross'),
        ('stable_minus_unstable','contrast_stable_minus_unstable'),
    ]
    rows=[]
    for name,col in specs:
        vals = wide[col].to_numpy(dtype=float)
        test = paired_sign_randomization(
            vals, stream=AnalysisStream(analysis_root, f'{metric_label}-paired-randomization', name),
            n_permutations=N_PERM
        )
        lo, hi, _ = paired_bootstrap_interval(
            vals, stream=AnalysisStream(analysis_root, f'{metric_label}-paired-bootstrap', name),
            n_bootstrap=N_BOOT
        )
        rows.append({
            'contrast': name, 'mean_difference': float(test['mean_difference']),
            'median_difference': float(test['median_difference']),
            'bootstrap_95_lower': lo, 'bootstrap_95_upper': hi,
            'positive_seed_blocks': int(np.sum(vals>0)), 'negative_seed_blocks': int(np.sum(vals<0)),
            'p_value_two_sided': float(test['p_value_two_sided']), 'n_seed_blocks': len(vals)
        })
    out=pd.DataFrame(rows)
    out['q_value_bh_six_contrasts'] = _bh_adjust(out['p_value_two_sided'])
    out['contrast_passed'] = (out['mean_difference']>0)&(out['q_value_bh_six_contrasts']<0.05)
    return out


def technical_precision(cont: pd.DataFrame) -> pd.DataFrame:
    # Continuation-level variation of DeltaV_MP within each evaluation realization.
    r = cont.groupby(
        ['condition','control_family','realization','seed_block','baseline_replicate'], as_index=False
    )['delta_mp'].agg(['mean','std','count']).reset_index()
    r['se_of_continuation_mean'] = r['std'] / np.sqrt(r['count'])
    return r


def main(workers: int):
    OUT.mkdir(parents=True, exist_ok=True)
    specs = json.loads((PHASE5/'evaluation_specifications.json').read_text())
    if len(specs) != 220:
        raise RuntimeError(f'expected 220 Phase5 specs, got {len(specs)}')
    if CONT_INDICES != tuple(range(2,66)):
        raise RuntimeError('continuation index set changed from prespecification')

    jobs=[]
    all_rows=[]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in range(20):
            jobs.append(ex.submit(native_job,r))
        for spec in specs:
            jobs.append(ex.submit(spec_job,spec))
        for i,f in enumerate(as_completed(jobs),1):
            all_rows.extend(f.result())
            if i%10==0 or i==len(jobs):
                print(f'HP MP causal-specificity jobs {i}/{len(jobs)}', flush=True)

    cont=pd.DataFrame(all_rows).sort_values(['condition','seed_block','realization','continuation_index'])
    expected_rows = 240*N_CONT
    if len(cont) != expected_rows:
        raise RuntimeError(f'expected {expected_rows} continuation rows, got {len(cont)}')
    per_eval = cont.groupby(['condition','control_family','realization','seed_block','baseline_replicate']).size()
    if not np.all(per_eval.to_numpy()==N_CONT):
        raise RuntimeError('not every evaluation realization has exactly 64 new continuations')
    cont.to_csv(OUT/'continuation_level_results_64new.csv', index=False)

    mp_max_err=float(cont['starting_expected_marginal_max_abs_error'].max())
    wide64=aggregate_seed_blocks(cont,'delta_mp').sort_values('seed_block')
    wide64.to_csv(OUT/'mp_operator_seed_block_metrics_64new.csv',index=False)
    inf64=infer_contrasts(wide64,'mp-64new')
    inf64.to_csv(OUT/'mp_operator_contrasts_64new.csv',index=False)
    technical_precision(cont).to_csv(OUT/'technical_precision_by_realization_64new.csv',index=False)

    # Condition levels for the primary 64-new campaign.
    level_cols=['native_full','selection_neutral','selection_reduced','affinity_reassigned','topology_mismatch',
                'alternative_a_native','alternative_a_cross_b','alternative_b_native','alternative_b_cross_a',
                'temporally_unstable','alternative_native_mean','alternative_cross_mean']
    levels=[]
    for col in level_cols:
        vals=wide64[col].to_numpy(float)
        levels.append({'condition':col,'mean_mp_loss_64new':float(vals.mean()),
                       'median_mp_loss_64new':float(np.median(vals)),
                       'positive_seed_blocks':int(np.sum(vals>0))})
    pd.DataFrame(levels).to_csv(OUT/'condition_levels_64new.csv',index=False)

    # Compare prospectively new 64 with the frozen two-continuation estimates.
    prior_wide=pd.read_csv(PRIOR_R2/'results'/'mp_operator_seed_block_metrics.csv').sort_values('seed_block')
    prior_inf=pd.read_csv(PRIOR_R2/'results'/'mp_operator_contrasts.csv')
    comp=prior_inf[['contrast','mean_difference','bootstrap_95_lower','bootstrap_95_upper','positive_seed_blocks','q_value_bh_six_contrasts','contrast_passed']].rename(columns={
        'mean_difference':'mean_difference_2cont','bootstrap_95_lower':'ci_lower_2cont','bootstrap_95_upper':'ci_upper_2cont',
        'positive_seed_blocks':'positive_blocks_2cont','q_value_bh_six_contrasts':'q_2cont','contrast_passed':'passed_2cont'})
    comp=comp.merge(inf64,on='contrast',validate='one_to_one',suffixes=('','_64new'))
    comp=comp.rename(columns={
        'mean_difference':'mean_difference_64new','bootstrap_95_lower':'ci_lower_64new','bootstrap_95_upper':'ci_upper_64new',
        'positive_seed_blocks':'positive_blocks_64new','q_value_bh_six_contrasts':'q_64new','contrast_passed':'passed_64new'})
    ccols={
      'full_minus_neutral':'contrast_full_minus_neutral','full_minus_reduced':'contrast_full_minus_reduced',
      'native_minus_affinity_reassigned':'contrast_native_minus_affinity_reassigned',
      'native_minus_topology_mismatch':'contrast_native_minus_topology_mismatch',
      'alternative_native_minus_cross':'contrast_alternative_native_minus_cross','stable_minus_unstable':'contrast_stable_minus_unstable'}
    conc=[]
    for name,col in ccols.items():
        a=prior_wide[col].to_numpy(float); b=wide64[col].to_numpy(float)
        conc.append({'contrast':name,'seed_block_sign_concordance_2_vs_64':float(np.mean(np.sign(a)==np.sign(b))),
                     'positive_both':int(np.sum((a>0)&(b>0)))})
    comp=comp.merge(pd.DataFrame(conc),on='contrast')
    comp.to_csv(OUT/'comparison_2cont_vs_64new.csv',index=False)

    # Prespecified secondary combined 66-continuation sensitivity.
    prior_cont=pd.read_csv(PRIOR_R2/'results'/'continuation_level_results.csv')
    cols=['condition','control_family','realization','seed_block','baseline_replicate','pairing_baseline_replicate',
          'continuation_index','selection_strength','evaluation_topology_id','actual_viability','mp_constant_viability',
          'delta_mp','starting_expected_marginal_max_abs_error']
    combined=pd.concat([prior_cont[cols],cont[cols]],ignore_index=True)
    counts=combined.groupby(['condition','control_family','realization','seed_block','baseline_replicate']).size()
    if not np.all(counts.to_numpy()==66):
        raise RuntimeError('combined sensitivity does not contain exactly 66 continuations per realization')
    wide66=aggregate_seed_blocks(combined,'delta_mp').sort_values('seed_block')
    wide66.to_csv(OUT/'mp_operator_seed_block_metrics_66combined_secondary.csv',index=False)
    inf66=infer_contrasts(wide66,'mp-66combined-secondary',analysis_root=2026100203)
    inf66.to_csv(OUT/'mp_operator_contrasts_66combined_secondary.csv',index=False)

    validation={
      'n_phase5_specs':len(specs),'n_native_full_specs':20,
      'continuation_indices_primary':[min(CONT_INDICES),max(CONT_INDICES)],
      'n_new_continuations_per_evaluation':N_CONT,
      'n_primary_continuation_rows':len(cont),
      'max_starting_expected_marginal_abs_error':mp_max_err,
      'all_six_64new_contrasts_pass':bool(inf64['contrast_passed'].all()),
      'n_64new_contrasts_passed':int(inf64['contrast_passed'].sum()),
      'continuation_root_seed':CONT_ROOT,'topology_schedule_root_seed':TOPOLOGY_ROOT,
      'analysis_root_seed_primary':ANALYSIS_ROOT,
    }
    (OUT/'VALIDATION_AND_KEY_RESULTS.json').write_text(json.dumps(validation,indent=2))
    print(json.dumps(validation,indent=2))
    print('\nPRIMARY 64-new contrasts:\n',inf64.to_string(index=False))
    print('\nComparison 2-cont vs 64-new:\n',comp.to_string(index=False))
    print('\nSECONDARY combined-66 contrasts:\n',inf66.to_string(index=False))


if __name__=='__main__':
    main(int(os.environ.get('R2_WORKERS','5')))
