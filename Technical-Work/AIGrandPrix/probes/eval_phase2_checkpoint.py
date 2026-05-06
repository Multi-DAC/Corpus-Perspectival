"""Evaluate a single Phase 2 checkpoint.

Designed to be called per-checkpoint so the P96 gate-eval discipline
holds: do 22.5M, write decision, only then look at later checkpoints.

Usage:
    python eval_phase2_checkpoint.py --step 22500016
    python eval_phase2_checkpoint.py --step 30000016
    ...
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / 'sim'))

from infinite_gate_env import InfiniteGateEnv, ManeuverLibrary
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

# Platform-aware base path: WSL uses /mnt/c/, Windows uses C:\
if os.path.exists('/mnt/c/Users/mercu/clawd/projects/aigrandprix'):
    BASE = Path('/mnt/c/Users/mercu/clawd/projects/aigrandprix')
else:
    BASE = Path(r'C:\Users\mercu\clawd\projects\aigrandprix')
RUN  = BASE / 'sim' / 'runs' / 'infinite_v3_phase2_60M_1777095742'
CKPT = RUN / 'checkpoints'
OUT_DIR = BASE / 'probes' / 'phase2_trajectory'
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_EPISODES_PER_MANEUVER = 8
MAX_STEPS_PER_EP = 30000
SEED_BASE = 42


class ForceManeuverEnv(InfiniteGateEnv):
    def __init__(self, force_maneuver, **kwargs):
        kwargs.setdefault('adaptive_curriculum', False)
        super().__init__(**kwargs)
        assert force_maneuver in ManeuverLibrary.MANEUVERS
        self.force_maneuver = force_maneuver

    def _choose_maneuver(self):
        return self.force_maneuver


def make_force_env(maneuver, seed):
    return ForceManeuverEnv(
        force_maneuver=maneuver,
        gate_radius=0.75, max_steps=MAX_STEPS_PER_EP, dt=0.002, substeps=1,
        domain_rand=True, domain_rand_scale=0.15, seed=seed,
    )


def make_curriculum_env(seed):
    return InfiniteGateEnv(
        gate_radius=0.75, max_steps=MAX_STEPS_PER_EP, dt=0.002, substeps=1,
        domain_rand=True, domain_rand_scale=0.15, adaptive_curriculum=True, seed=seed,
    )


def run_eval(model, vec_norm_path, env_factory, n_episodes, seed_base):
    raw = DummyVecEnv([lambda s=seed_base + i: env_factory(s) for i in range(1)])
    env = VecNormalize.load(str(vec_norm_path), raw)
    env.training = False
    env.norm_reward = False

    rewards, gates, ep_lens, crashed = [], [], [], []
    for ep in range(n_episodes):
        obs = env.reset()
        ep_r, ep_len, ep_gates, last_term = 0.0, 0, 0, False
        for t in range(MAX_STEPS_PER_EP):
            act, _ = model.predict(obs, deterministic=True)
            obs, rew, done, info = env.step(act)
            ep_r += float(rew[0]); ep_len += 1
            if 'gates_passed' in info[0]:
                ep_gates = int(info[0]['gates_passed'])
            if done[0]:
                last_term = not bool(info[0].get('TimeLimit.truncated', False))
                break
        rewards.append(ep_r); gates.append(ep_gates); ep_lens.append(ep_len); crashed.append(last_term)
    env.close()
    return {
        'n_episodes': n_episodes,
        'reward_mean': float(np.mean(rewards)),
        'reward_std':  float(np.std(rewards)),
        'gates_mean':  float(np.mean(gates)),
        'gates_std':   float(np.std(gates)),
        'gates_max':   int(np.max(gates)),
        'gates_total': int(sum(gates)),
        'ep_len_mean': float(np.mean(ep_lens)),
        'crash_rate':  float(np.mean(crashed)),
        'rewards': rewards,
        'gates': gates,
    }


def evaluate_checkpoint(step):
    model_path = CKPT / f'ppo_phase2_{step}_steps.zip'
    vec_path   = CKPT / f'ppo_phase2_{step}_steps_vecnorm.pkl'
    assert model_path.exists(), f'missing {model_path}'
    assert vec_path.exists(),   f'missing {vec_path}'

    print(f'=== Phase 2 checkpoint eval — step {step:,} ===')
    t_load = time.time()
    model = PPO.load(str(model_path), device='cpu')
    print(f'  loaded model in {time.time() - t_load:.1f}s')

    out = {'step': step, 'config': {
        'n_episodes_per_maneuver': N_EPISODES_PER_MANEUVER,
        'max_steps_per_ep': MAX_STEPS_PER_EP,
        'seed_base': SEED_BASE,
        'maneuvers': ManeuverLibrary.MANEUVERS,
    }}

    # Curriculum eval (apples-to-apples with historical 85.5% baseline)
    t0 = time.time()
    cur = run_eval(model, vec_path, make_curriculum_env,
                   N_EPISODES_PER_MANEUVER, SEED_BASE)
    print(f'  [curriculum]  reward={cur["reward_mean"]:7.1f}±{cur["reward_std"]:5.1f}  '
          f'gates_mean={cur["gates_mean"]:5.2f}  gates_max={cur["gates_max"]:3d}  '
          f'crash={cur["crash_rate"]*100:4.0f}%  ({time.time()-t0:.1f}s)')
    out['curriculum'] = cur

    # Per-maneuver eval
    per_maneuver = {}
    for mi, m in enumerate(ManeuverLibrary.MANEUVERS):
        t0 = time.time()
        s = run_eval(model, vec_path, lambda seed, mm=m: make_force_env(mm, seed),
                     N_EPISODES_PER_MANEUVER, SEED_BASE + mi*100)
        s['maneuver'] = m
        per_maneuver[m] = s
        print(f'  {m:14s}  reward={s["reward_mean"]:7.1f}±{s["reward_std"]:5.1f}  '
              f'gates={s["gates_mean"]:5.2f}±{s["gates_std"]:4.2f}  '
              f'crash={s["crash_rate"]*100:4.0f}%  ({time.time()-t0:.1f}s)')
    out['per_maneuver'] = per_maneuver

    # Aggregates
    g = [per_maneuver[m]['gates_mean'] for m in ManeuverLibrary.MANEUVERS]
    r = [per_maneuver[m]['reward_mean'] for m in ManeuverLibrary.MANEUVERS]
    c = [per_maneuver[m]['crash_rate']  for m in ManeuverLibrary.MANEUVERS]
    out['aggregate'] = {
        'mean_gates_across_maneuvers': float(np.mean(g)),
        'std_gates_across_maneuvers':  float(np.std(g)),
        'mean_reward_across_maneuvers': float(np.mean(r)),
        'std_reward_across_maneuvers':  float(np.std(r)),
        'mean_crash_rate':              float(np.mean(c)),
    }

    out_path = OUT_DIR / f'eval_step_{step}.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'  AGG: gates {out["aggregate"]["mean_gates_across_maneuvers"]:.2f} ± '
          f'{out["aggregate"]["std_gates_across_maneuvers"]:.2f}  crash '
          f'{out["aggregate"]["mean_crash_rate"]*100:.0f}%')
    print(f'  wrote {out_path}')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--step', type=int, required=True)
    args = ap.parse_args()
    evaluate_checkpoint(args.step)
