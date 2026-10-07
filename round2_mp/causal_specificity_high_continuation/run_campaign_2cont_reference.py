from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

# R1 scientific archive is read-only input.
R1 = Path(os.environ.get('JRSI_R1_ROOT', '/mnt/data/JRSI_R2_CTRL/JRSI_MAJOR_REVISION_PHASE7_GATE8_PASSED_v1'))
OUT = Path(__file__).resolve().parent / 'results'
PHASE4 = R1 / 'results' / 'phase4_core'
PHASE5 = R1 / 'results' / 'phase5_causal_specificity'

import sys
sys.path.insert(0, str(R1 / 'src'))

from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.phase5 import (
    enumerate_matched_topologies,
    select_alternative_topologies,
    reproduce_with_selection_strength,
    paired_sign_randomization,
    paired_bootstrap_interval,
    _bh_adjust,
)
from modelb_semantic_repo.rng import ContinuationStream, AnalysisStream

CONT_ROOT = 2026073104
ANALYSIS_ROOT = 2026100201
N_CONT = 2
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
    return out


def starting_marginal_error(population: np.ndarray, kernel: np.ndarray, params: dict) -> float:
    n_cells, n_seqs, seq_len = population.shape
    chain_len = seq_len - 4
    n_s = kernel.shape[1]
    n_z = kernel.shape[2]
    seg_len = chain_len // n_s
    native_sum = np.zeros((n_s, n_z), dtype=float)
    counts = np.zeros(n_s, dtype=int)
    # independent direct loop over windows
    for ci in range(n_cells):
        for si in range(n_seqs):
            for pos in range(chain_len):
                motif = 0
                for k in range(5):
                    motif = motif * 4 + int(population[ci, si, pos+k])
                s = min(pos // seg_len, n_s - 1)
                native_sum[s] += kernel[motif, s]
                counts[s] += 1
    native = native_sum / counts[:, None]
    # MP constant Q is exactly the empirical population-frequency weighted probability-space mean.
    q = np.zeros_like(native)
    motif_counts = np.zeros((n_s, kernel.shape[0]), dtype=int)
    for ci in range(n_cells):
        for si in range(n_seqs):
            for pos in range(chain_len):
                motif = 0
                for k in range(5):
                    motif = motif * 4 + int(population[ci, si, pos+k])
                s = min(pos // seg_len, n_s - 1)
                motif_counts[s, motif] += 1
    for s in range(n_s):
        w = motif_counts[s] / motif_counts[s].sum()
        q[s] = (w[:, None] * kernel[:, s, :]).sum(axis=0)
    return float(np.max(np.abs(native - q)))


def simulate_mp(population, matrix, params, selection_strength, pairing_id, continuation_index, fixed_topology_id, schedule):
    topologies = enumerate_matched_topologies()
    lookup = {t.topology_id: t for t in topologies}
    kernel = kernel_from_matrix(matrix, params)
    stream = ContinuationStream(CONT_ROOT, pairing_id, continuation_index)
    obs_rng = stream.observation_generator()
    prop_rng = stream.propagation_generator()
    pop = np.array(population, copy=True)
    n_windows = params['n_cells'] * params['n_seqs'] * (params['seq_len'] - 4)
    vals = np.empty(HORIZON, dtype=float)
    for h in range(HORIZON):
        topology = lookup[fixed_topology_id] if fixed_topology_id is not None else lookup[str(schedule[h])]
        uniforms = obs_rng.random(n_windows)
        fit = observe_mp_constant(
            pop, kernel, topology.productive_pairs, topology.anti_pairs,
            float(params['reward_strength']), float(params['penalty_strength']), uniforms
        )
        vals[h] = float(np.mean(fit))
        pop = reproduce_with_selection_strength(
            pop, fit, float(params['mutation_rate']), 1.0, prop_rng, float(selection_strength)
        )
    return float(vals.mean())


def load_archived_pair(block_path: Path, continuation_index: int):
    d = pd.read_csv(block_path)
    a = d[(d['map_id'] == 'actual') & (d['continuation_index'] == continuation_index)]
    c = d[(d['endpoint_type'] == 'constant') & (d['continuation_index'] == continuation_index)]
    if len(a) != 1 or len(c) != 1:
        raise RuntimeError(f'bad archived actual/constant rows: {block_path} c={continuation_index}')
    return float(a.iloc[0]['viability']), float(c.iloc[0]['viability'])


def schedule_for(spec: dict, continuation_index: int):
    if not spec['dynamic_topology']:
        return None
    p = PHASE5 / 'topology_schedules' / f"{spec['baseline_replicate']}_c{continuation_index}_schedule.json"
    if not p.exists():
        raise FileNotFoundError(p)
    schedule = json.loads(p.read_text())
    if len(schedule) != HORIZON:
        raise RuntimeError(f'bad schedule length {p}: {len(schedule)}')
    return schedule


def native_job(rep: int):
    params = default_parameters()
    topologies = enumerate_matched_topologies()
    native, _, _ = select_alternative_topologies(topologies)
    bid = f'selective_p1.0_r{rep:02d}'
    population = np.asarray(np.load(PHASE4 / 'states' / 'selective' / 'p1.0' / f'rep_{rep:02d}.npz')['population'])
    matrix = np.asarray(params['motif_affinity_matrix'])
    err = starting_marginal_error(population, kernel_from_matrix(matrix, params), params)
    rows = []
    block = PHASE4 / 'continuation_blocks' / f'{bid}.csv'
    for c in range(N_CONT):
        actual, original_const = load_archived_pair(block, c)
        mp = simulate_mp(population, matrix, params, 1.0, bid, c, native.topology_id, None)
        rows.append({
            'condition': 'native_full', 'control_family': 'native_full', 'realization': 0,
            'seed_block': rep, 'baseline_replicate': bid, 'pairing_baseline_replicate': bid,
            'continuation_index': c, 'selection_strength': 1.0, 'evaluation_topology_id': native.topology_id,
            'actual_viability': actual, 'original_constant_viability': original_const,
            'mp_constant_viability': mp, 'delta_original': actual-original_const, 'delta_mp': actual-mp,
            'starting_expected_marginal_max_abs_error': err,
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
    block = PHASE5 / 'continuation_blocks' / f"{spec['baseline_replicate']}.csv"
    rows = []
    for c in range(N_CONT):
        actual, original_const = load_archived_pair(block, c)
        schedule = schedule_for(spec, c)
        fixed = str(spec['fixed_topology_id']) if spec['fixed_topology_id'] is not None else None
        mp = simulate_mp(
            population, matrix, params, float(spec['selection_strength']),
            str(spec['pairing_baseline_replicate']), c, fixed, schedule
        )
        rows.append({
            'condition': spec['condition'], 'control_family': spec['control_family'],
            'realization': int(spec['realization']), 'seed_block': int(spec['seed_block']),
            'baseline_replicate': spec['baseline_replicate'],
            'pairing_baseline_replicate': spec['pairing_baseline_replicate'],
            'continuation_index': c, 'selection_strength': float(spec['selection_strength']),
            'evaluation_topology_id': spec['fixed_topology_id'] or 'temporally_unstable',
            'actual_viability': actual, 'original_constant_viability': original_const,
            'mp_constant_viability': mp, 'delta_original': actual-original_const, 'delta_mp': actual-mp,
            'starting_expected_marginal_max_abs_error': err,
        })
    return rows


def aggregate_seed_blocks(cont: pd.DataFrame, metric: str) -> pd.DataFrame:
    # Average continuations first within realization.
    real = cont.groupby(['condition','control_family','realization','seed_block','baseline_replicate'], as_index=False)[metric].mean()
    # Average nested disruption realizations within control family/seed block.
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


def infer_contrasts(wide: pd.DataFrame, metric_label: str) -> pd.DataFrame:
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
            vals, stream=AnalysisStream(ANALYSIS_ROOT, f'{metric_label}-paired-randomization', name),
            n_permutations=N_PERM
        )
        lo, hi, _ = paired_bootstrap_interval(
            vals, stream=AnalysisStream(ANALYSIS_ROOT, f'{metric_label}-paired-bootstrap', name),
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


def main(workers: int):
    OUT.mkdir(parents=True, exist_ok=True)
    specs = json.loads((PHASE5/'evaluation_specifications.json').read_text())
    if len(specs) != 220:
        raise RuntimeError(f'expected 220 Phase5 specs, got {len(specs)}')

    jobs=[]
    all_rows=[]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in range(20): jobs.append(ex.submit(native_job,r))
        for spec in specs: jobs.append(ex.submit(spec_job,spec))
        for i,f in enumerate(as_completed(jobs),1):
            all_rows.extend(f.result())
            if i%20==0 or i==len(jobs): print(f'MP causal-specificity jobs {i}/{len(jobs)}', flush=True)
    cont=pd.DataFrame(all_rows).sort_values(['condition','seed_block','realization','continuation_index'])
    cont.to_csv(OUT/'continuation_level_results.csv', index=False)

    # Validation and reconstruction of original Phase5 control metrics.
    mp_max_err=float(cont['starting_expected_marginal_max_abs_error'].max())
    original_wide=aggregate_seed_blocks(cont,'delta_original')
    mp_wide=aggregate_seed_blocks(cont,'delta_mp')
    original_wide.to_csv(OUT/'original_operator_seed_block_reconstruction.csv',index=False)
    mp_wide.to_csv(OUT/'mp_operator_seed_block_metrics.csv',index=False)

    archived=pd.read_csv(PHASE5/'gate5_seed_block_metrics.csv').sort_values('seed_block')
    original_wide=original_wide.sort_values('seed_block')
    mapping={
      'native_full':'native_full_voi','selection_neutral':'selection_neutral','selection_reduced':'selection_reduced',
      'affinity_reassigned':'affinity_reassigned','topology_mismatch':'topology_mismatch',
      'alternative_native_mean':'alternative_native_mean','alternative_cross_mean':'alternative_cross_mean',
      'temporally_unstable':'temporally_unstable',
      'contrast_full_minus_neutral':'contrast_full_minus_neutral','contrast_full_minus_reduced':'contrast_full_minus_reduced',
      'contrast_native_minus_affinity_reassigned':'contrast_native_minus_affinity_reassigned',
      'contrast_native_minus_topology_mismatch':'contrast_native_minus_topology_mismatch',
      'contrast_alternative_native_minus_cross':'contrast_alternative_native_minus_cross',
      'contrast_stable_minus_unstable':'contrast_stable_minus_unstable'
    }
    errs=[]
    for ours,arc in mapping.items():
        errs.extend(np.abs(original_wide[ours].to_numpy()-archived[arc].to_numpy()).tolist())
    max_reconstruction_error=float(max(errs))

    orig_inf=infer_contrasts(original_wide,'original-reconstruction')
    mp_inf=infer_contrasts(mp_wide,'mp')
    orig_inf.to_csv(OUT/'original_operator_contrasts_reconstructed.csv',index=False)
    mp_inf.to_csv(OUT/'mp_operator_contrasts.csv',index=False)

    # Condition levels and apples-to-apples comparisons.
    level_cols=['native_full','selection_neutral','selection_reduced','affinity_reassigned','topology_mismatch',
                'alternative_a_native','alternative_a_cross_b','alternative_b_native','alternative_b_cross_a','temporally_unstable',
                'alternative_native_mean','alternative_cross_mean']
    levels=[]
    for col in level_cols:
        o=original_wide[col].to_numpy(float); m=mp_wide[col].to_numpy(float)
        levels.append({'condition':col,'original_mean_loss':float(o.mean()),'mp_mean_loss':float(m.mean()),
                       'mp_over_original_ratio':float(m.mean()/o.mean()) if abs(o.mean())>1e-15 else np.nan,
                       'mean_attenuation':float((o-m).mean()),'positive_mp_seed_blocks':int((m>0).sum()),
                       'sign_concordance_fraction':float(np.mean(np.sign(o)==np.sign(m)))})
    levels=pd.DataFrame(levels)
    levels.to_csv(OUT/'condition_level_original_vs_mp.csv',index=False)

    comp=orig_inf[['contrast','mean_difference']].rename(columns={'mean_difference':'original_mean_contrast'}).merge(
        mp_inf, on='contrast', validate='one_to_one')
    comp['mp_over_original_ratio']=comp['mean_difference']/comp['original_mean_contrast']
    comp['mean_contrast_attenuation']=comp['original_mean_contrast']-comp['mean_difference']
    # seed-block sign concordance
    ccols={
      'full_minus_neutral':'contrast_full_minus_neutral','full_minus_reduced':'contrast_full_minus_reduced',
      'native_minus_affinity_reassigned':'contrast_native_minus_affinity_reassigned',
      'native_minus_topology_mismatch':'contrast_native_minus_topology_mismatch',
      'alternative_native_minus_cross':'contrast_alternative_native_minus_cross','stable_minus_unstable':'contrast_stable_minus_unstable'}
    concord=[]
    for name,col in ccols.items():
        concord.append({'contrast':name,'seed_block_sign_concordance':float(np.mean(np.sign(original_wide[col])==np.sign(mp_wide[col]))),
                        'both_positive_blocks':int(np.sum((original_wide[col]>0)&(mp_wide[col]>0)))})
    comp=comp.merge(pd.DataFrame(concord),on='contrast')
    comp.to_csv(OUT/'contrast_original_vs_mp.csv',index=False)

    validation={
      'n_phase5_specs':len(specs),'n_native_full_specs':20,'n_continuation_rows':len(cont),
      'max_starting_expected_marginal_abs_error':mp_max_err,
      'max_original_seed_block_reconstruction_abs_error':max_reconstruction_error,
      'all_six_mp_contrasts_pass':bool(mp_inf['contrast_passed'].all()),
      'n_mp_contrasts_passed':int(mp_inf['contrast_passed'].sum()),
      'continuation_root_seed_reused_for_pairing':CONT_ROOT,'round2_analysis_root_seed':ANALYSIS_ROOT,
    }
    (OUT/'VALIDATION_AND_KEY_RESULTS.json').write_text(json.dumps(validation,indent=2))
    print(json.dumps(validation,indent=2))
    print('\nMP contrasts:\n',mp_inf.to_string(index=False))
    print('\nComparison:\n',comp.to_string(index=False))

if __name__=='__main__':
    main(int(os.environ.get('R2_WORKERS','8')))
