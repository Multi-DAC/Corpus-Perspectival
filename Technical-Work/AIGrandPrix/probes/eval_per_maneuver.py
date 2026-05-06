"""Per-maneuver deterministic eval harness — Phase 1 of the Day 83 ROADMAP.

Loads a (policy, vec_normalize) pair, forces InfiniteGateEnv to use one
maneuver type at a time, runs N deterministic episodes per maneuver, and
reports per-maneuver mean reward / variance / gate completion rate / mean
episode length / crash rate.

Designed for three-way comparison: v3 7.5M (healthy) vs baseline 60.4M
(wrong-attractor) vs v3 200K (control).

Usage:
    python eval_per_maneuver.py
"""

import os
import sys
import json
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / 'sim'))

from infinite_gate_env import InfiniteGateEnv, ManeuverLibrary
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

BASE = Path(r'C:\Users\mercu\clawd\projects\aigrandprix')
RUNS = BASE / 'sim' / 'runs'

POLICIES = [
    {
        'name': 'v3_7.5M_healthy',
        'model': RUNS / 'infinite_v3_retrain10M_1777074572' / 'checkpoints' / 'ppo_v3_7500000_steps.zip',
        'vec_norm': RUNS / 'infinite_v3_retrain10M_1777074572' / 'vec_normalize_reconstructed.pkl',
    },
    {
        'name': 'baseline_60.4M_wrong_attractor',
        'model': RUNS / 'infinite_1771733969' / 'best' / 'best_model.zip',
        'vec_norm': None,  # baseline trained without VecNormalize
    },
    {
        'name': 'v3_200K_control',
        'model': RUNS / 'infinite_v3_validation_1777074001' / 'final_model.zip',
        'vec_norm': RUNS / 'infinite_v3_validation_1777074001' / 'vec_normalize.pkl',
    },
]

N_EPISODES_PER_MANEUVER = 8
MAX_STEPS_PER_EP = 30000
SEED_BASE = 42

OUT = BASE / 'probes' / 'eval_per_maneuver_results.json'


class ForceManeuverEnv(InfiniteGateEnv):
    """InfiniteGateEnv that always uses a specified maneuver type.

    Bypasses curriculum sequencing — every gate transition uses force_maneuver.
    Used for per-maneuver capability isolation.
    """
    def __init__(self, force_maneuver: str, **kwargs):
        kwargs.setdefault('adaptive_curriculum', False)
        super().__init__(**kwargs)
        assert force_maneuver in ManeuverLibrary.MANEUVERS, \
            f'unknown maneuver {force_maneuver!r}'
        self.force_maneuver = force_maneuver

    def _choose_maneuver(self):
        return self.force_maneuver


def make_env(force_maneuver: str, seed: int):
    return ForceManeuverEnv(
        force_maneuver=force_maneuver,
        gate_radius=0.75,
        max_steps=MAX_STEPS_PER_EP,
        dt=0.002,
        substeps=1,
        domain_rand=True,
        domain_rand_scale=0.15,
        seed=seed,
    )


def make_curriculum_env(seed: int):
    """Standard V2-curriculum env (mixed maneuvers via SequencePlanner).

    Apples-to-apples with historical 85.5%-completion measurements.
    """
    return InfiniteGateEnv(
        gate_radius=0.75,
        max_steps=MAX_STEPS_PER_EP,
        dt=0.002,
        substeps=1,
        domain_rand=True,
        domain_rand_scale=0.15,
        adaptive_curriculum=True,
        seed=seed,
    )


def evaluate_policy_curriculum(model, vec_norm_path, n_episodes: int, seed_base: int):
    """Run n_episodes deterministic rollouts under standard V2 curriculum."""
    raw = DummyVecEnv([
        lambda s=seed_base + i: make_curriculum_env(s) for i in range(1)
    ])
    if vec_norm_path is not None and os.path.exists(vec_norm_path):
        env = VecNormalize.load(str(vec_norm_path), raw)
        env.training = False
        env.norm_reward = False
    else:
        env = raw

    rewards, gates, ep_lens, crashed = [], [], [], []
    for ep in range(n_episodes):
        obs = env.reset()
        ep_r = 0.0
        ep_len = 0
        ep_gates = 0
        last_term = False
        for t in range(MAX_STEPS_PER_EP):
            act, _ = model.predict(obs, deterministic=True)
            obs, rew, done, info = env.step(act)
            ep_r += float(rew[0])
            ep_len += 1
            if 'gates_passed' in info[0]:
                ep_gates = int(info[0]['gates_passed'])
            if done[0]:
                last_term = not bool(info[0].get('TimeLimit.truncated', False))
                break
        rewards.append(ep_r)
        gates.append(ep_gates)
        ep_lens.append(ep_len)
        crashed.append(last_term)
    env.close()
    return {
        'mode': 'standard_curriculum',
        'n_episodes': n_episodes,
        'reward_mean': float(np.mean(rewards)),
        'reward_std': float(np.std(rewards)),
        'gates_mean': float(np.mean(gates)),
        'gates_std': float(np.std(gates)),
        'gates_max': int(np.max(gates)),
        'gates_total': int(sum(gates)),
        'ep_len_mean': float(np.mean(ep_lens)),
        'crash_rate': float(np.mean(crashed)),
        'rewards': rewards,
        'gates': gates,
    }


def evaluate_policy_on_maneuver(model, vec_norm_path, maneuver: str,
                                  n_episodes: int, seed_base: int):
    """Run n_episodes deterministic rollouts of `model` on `maneuver`.

    Returns dict with reward stats, gate stats, episode-length stats, crash rate.
    """
    raw = DummyVecEnv([
        lambda s=seed_base + i: make_env(maneuver, s) for i in range(1)
    ])

    if vec_norm_path is not None and os.path.exists(vec_norm_path):
        env = VecNormalize.load(str(vec_norm_path), raw)
        env.training = False
        env.norm_reward = False
    else:
        env = raw

    rewards, gates, ep_lens, crashed = [], [], [], []
    for ep in range(n_episodes):
        obs = env.reset()
        ep_r = 0.0
        ep_len = 0
        ep_gates = 0
        last_term = False
        for t in range(MAX_STEPS_PER_EP):
            act, _ = model.predict(obs, deterministic=True)
            obs, rew, done, info = env.step(act)
            ep_r += float(rew[0])
            ep_len += 1
            # Capture gates_passed from info BEFORE done-triggered auto-reset
            if 'gates_passed' in info[0]:
                ep_gates = int(info[0]['gates_passed'])
            if done[0]:
                # 'TimeLimit.truncated' in info[0] when truncated; else terminated (crash).
                last_term = not bool(info[0].get('TimeLimit.truncated', False))
                break
        rewards.append(ep_r)
        gates.append(ep_gates)
        ep_lens.append(ep_len)
        crashed.append(last_term)

    env.close()
    return {
        'maneuver': maneuver,
        'n_episodes': n_episodes,
        'reward_mean': float(np.mean(rewards)),
        'reward_std': float(np.std(rewards)),
        'reward_min': float(np.min(rewards)),
        'reward_max': float(np.max(rewards)),
        'gates_mean': float(np.mean(gates)),
        'gates_std': float(np.std(gates)),
        'gates_total': int(sum(gates)),
        'ep_len_mean': float(np.mean(ep_lens)),
        'crash_rate': float(np.mean(crashed)),
        'rewards': rewards,
        'gates': gates,
    }


def main():
    print('=' * 80)
    print('Per-Maneuver Eval — Phase 1 of Day 83 ROADMAP')
    print(f'Episodes per (policy, maneuver): {N_EPISODES_PER_MANEUVER}')
    print(f'Max steps per episode:           {MAX_STEPS_PER_EP}')
    print('=' * 80)

    results = {'config': {
        'n_episodes_per_maneuver': N_EPISODES_PER_MANEUVER,
        'max_steps_per_ep': MAX_STEPS_PER_EP,
        'seed_base': SEED_BASE,
        'maneuvers': ManeuverLibrary.MANEUVERS,
        'policies': [p['name'] for p in POLICIES],
    }, 'by_policy': {}}

    for pol in POLICIES:
        print(f'\n--- Policy: {pol["name"]} ---')
        if not os.path.exists(pol['model']):
            print(f'  SKIP — missing {pol["model"]}')
            results['by_policy'][pol['name']] = {'skipped': str(pol['model'])}
            continue
        t_load = time.time()
        model = PPO.load(str(pol['model']), device='cpu')
        print(f'  loaded model in {time.time() - t_load:.1f}s')

        # 1) Standard V2 curriculum eval (apples-to-apples with historical numbers)
        t0 = time.time()
        cur_stats = evaluate_policy_curriculum(
            model, pol['vec_norm'], N_EPISODES_PER_MANEUVER, SEED_BASE,
        )
        dt_cur = time.time() - t0
        print(f'  [curriculum]   reward={cur_stats["reward_mean"]:7.1f}±{cur_stats["reward_std"]:5.1f}  '
              f'gates_mean={cur_stats["gates_mean"]:5.2f}  gates_max={cur_stats["gates_max"]:3d}  '
              f'crash={cur_stats["crash_rate"]*100:4.0f}%  ep_len={cur_stats["ep_len_mean"]:6.0f}  ({dt_cur:.1f}s)')

        per_maneuver = {}
        for mi, m in enumerate(ManeuverLibrary.MANEUVERS):
            t0 = time.time()
            stats = evaluate_policy_on_maneuver(
                model, pol['vec_norm'], m,
                N_EPISODES_PER_MANEUVER, SEED_BASE + mi * 100,
            )
            dt = time.time() - t0
            per_maneuver[m] = stats
            print(f'  {m:14s}  reward={stats["reward_mean"]:7.1f}±{stats["reward_std"]:5.1f}  '
                  f'gates={stats["gates_mean"]:5.2f}±{stats["gates_std"]:4.2f}  '
                  f'crash={stats["crash_rate"]*100:4.0f}%  '
                  f'ep_len={stats["ep_len_mean"]:6.0f}  ({dt:.1f}s)')

        # Aggregate across maneuvers
        all_reward_means = [per_maneuver[m]['reward_mean'] for m in ManeuverLibrary.MANEUVERS]
        all_gate_means = [per_maneuver[m]['gates_mean'] for m in ManeuverLibrary.MANEUVERS]
        all_crash_rates = [per_maneuver[m]['crash_rate'] for m in ManeuverLibrary.MANEUVERS]

        agg = {
            'mean_reward_across_maneuvers': float(np.mean(all_reward_means)),
            'std_reward_across_maneuvers': float(np.std(all_reward_means)),
            'mean_gates_across_maneuvers': float(np.mean(all_gate_means)),
            'std_gates_across_maneuvers': float(np.std(all_gate_means)),
            'mean_crash_rate': float(np.mean(all_crash_rates)),
            'reward_cv_across_maneuvers': float(np.std(all_reward_means) /
                                                 (abs(np.mean(all_reward_means)) + 1e-6)),
        }
        print(f'  AGGREGATE: reward {agg["mean_reward_across_maneuvers"]:.1f} ± '
              f'{agg["std_reward_across_maneuvers"]:.1f}  '
              f'gates {agg["mean_gates_across_maneuvers"]:.2f} ± '
              f'{agg["std_gates_across_maneuvers"]:.2f}  '
              f'crash {agg["mean_crash_rate"]*100:.0f}%  '
              f'reward CV {agg["reward_cv_across_maneuvers"]:.3f}')

        results['by_policy'][pol['name']] = {
            'curriculum': cur_stats,
            'per_maneuver': per_maneuver,
            'aggregate': agg,
        }

    with open(OUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\nWrote {OUT}')

    # Three-way comparison summary
    print('\n' + '=' * 80)
    print('THREE-WAY COMPARISON — DECISION GATE')
    print('=' * 80)
    print(f'{"maneuver":<14s} {"v3_7.5M":>12s} {"baseline_60M":>14s} {"v3_200K":>12s}')
    for m in ManeuverLibrary.MANEUVERS:
        cells = []
        for pol in POLICIES:
            d = results['by_policy'].get(pol['name'], {})
            if 'per_maneuver' not in d:
                cells.append('  --  ')
            else:
                s = d['per_maneuver'][m]
                cells.append(f'{s["gates_mean"]:5.2f}/{s["crash_rate"]*100:3.0f}%')
        print(f'{m:<14s} {cells[0]:>12s} {cells[1]:>14s} {cells[2]:>12s}')


if __name__ == '__main__':
    main()
