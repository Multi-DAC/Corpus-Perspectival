"""
rho-probe v2 - on-distribution rollouts.

v1 used uniform random obs. v2 runs the best policy in its actual training
env (InfiniteGateEnv) and measures rho on realistic obs. Compares to v1.
"""

import os, sys, json, zipfile, io
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn

# Path plumbing: match train_infinite.py's sys.path setup
BASE = Path(r'C:\Users\mercu\clawd\projects\aigrandprix')
sys.path.insert(0, str(BASE / 'rl'))
sys.path.insert(0, str(BASE / 'sim'))

from infinite_gate_env import InfiniteGateEnv  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402

MODEL_PATH = str(BASE / 'sim' / 'runs' / 'infinite_1771733969' / 'best' / 'best_model.zip')
OUT_DIR = str(BASE / 'probes')
N_EPISODES = 10
MAX_STEPS_PER_EP = 3000
SEED = 17


def build_trunk(sd, prefix):
    layers, idx = [], 0
    while f'{prefix}.{idx}.weight' in sd:
        W = sd[f'{prefix}.{idx}.weight']
        b = sd[f'{prefix}.{idx}.bias']
        lin = nn.Linear(W.shape[1], W.shape[0])
        lin.weight.data = W.clone(); lin.bias.data = b.clone()
        layers.append(lin); layers.append(nn.Tanh())
        idx += 2
    return nn.Sequential(*layers)


def main():
    np.random.seed(SEED); torch.manual_seed(SEED)

    print(f'Loading policy: {MODEL_PATH}')
    model = PPO.load(MODEL_PATH, device='cpu')
    sd = model.policy.state_dict()
    pi_trunk = build_trunk(sd, 'mlp_extractor.policy_net')
    vf_trunk = build_trunk(sd, 'mlp_extractor.value_net')

    print('Building InfiniteGateEnv...')
    env = InfiniteGateEnv(seed=SEED)

    obs_buf = []
    act_buf = []
    reward_buf = []
    gates_passed = []

    for ep in range(N_EPISODES):
        obs, _ = env.reset(seed=SEED + ep)
        ep_reward = 0.0
        ep_gates_start = getattr(env, 'gates_passed_total', 0)
        for t in range(MAX_STEPS_PER_EP):
            action, _ = model.predict(obs, deterministic=True)
            obs_buf.append(obs.copy())
            act_buf.append(action.copy())
            obs, reward, terminated, truncated, info = env.step(action)
            ep_reward += float(reward)
            if terminated or truncated:
                break
        ep_gates = getattr(env, 'gates_passed_total', 0) - ep_gates_start
        reward_buf.append(ep_reward)
        gates_passed.append(ep_gates)
        print(f'  ep{ep}: {t+1:>5} steps, reward={ep_reward:>9.2f}, gates={ep_gates}')

    env.close()

    obs_arr = np.array(obs_buf, dtype=np.float32)
    act_arr = np.array(act_buf, dtype=np.float32)
    N = len(obs_arr)
    print(f'\nCollected {N:,} on-distribution observations across {N_EPISODES} episodes')
    print(f'Rewards: mean={np.mean(reward_buf):.2f}  Gates: mean={np.mean(gates_passed):.1f}')

    print('\n=== Obs statistics (real distribution) ===')
    print(f'obs mean range: [{obs_arr.mean(0).min():.3f}, {obs_arr.mean(0).max():.3f}]')
    print(f'obs std  range: [{obs_arr.std(0).min():.3f}, {obs_arr.std(0).max():.3f}]')
    print(f'obs |max| per dim (first 10): {np.abs(obs_arr).max(0)[:10]}')

    # Forward through trunks
    obs_t = torch.from_numpy(obs_arr)
    with torch.no_grad():
        h_pi = pi_trunk(obs_t).numpy()
        h_vf = vf_trunk(obs_t).numpy()

    # R1 activation CV
    print('\n=== R1 on-distribution ===')
    def cv(h, tag):
        mean_abs = np.abs(h).mean(0) + 1e-9
        c = h.std(0) / mean_abs
        dead = int((c < 0.1).sum())
        print(f'  {tag}: CV mean={c.mean():.3f}  median={np.median(c):.3f}  p90={np.percentile(c,90):.3f}  dead-like={dead}/{len(c)}')
        return c
    pi_cv = cv(h_pi, 'policy')
    vf_cv = cv(h_vf, 'value ')

    # R2 cross-trunk
    print('\n=== R2 on-distribution ===')
    Xc = h_pi - h_pi.mean(0, keepdims=True)
    Yc = h_vf - h_vf.mean(0, keepdims=True)
    B, *_ = np.linalg.lstsq(Xc, Yc, rcond=None)
    r2_vf_from_pi = 1 - ((Yc - Xc @ B)**2).sum() / (Yc**2).sum()
    B2, *_ = np.linalg.lstsq(Yc, Xc, rcond=None)
    r2_pi_from_vf = 1 - ((Xc - Yc @ B2)**2).sum() / (Xc**2).sum()
    print(f'  R2(vf|pi) on-dist: {r2_vf_from_pi:.4f}  (off-dist v1: 0.3721)  -> cokernel {1-r2_vf_from_pi:.4f}')
    print(f'  R2(pi|vf) on-dist: {r2_pi_from_vf:.4f}  (off-dist v1: 0.1383)  -> kernel   {1-r2_pi_from_vf:.4f}')

    # R3 action/entropy on real obs
    print('\n=== R3 on-distribution: action statistics ===')
    print(f'  action range per dim: {act_arr.min(0)} .. {act_arr.max(0)}')
    print(f'  action std per dim:   {act_arr.std(0)}')
    # How often does yaw (dim 3) saturate?
    yaw_sat = np.abs(act_arr[:, 3]) > 0.95
    print(f'  yaw saturation rate (|a3|>0.95): {yaw_sat.mean():.3f}')
    for d in range(4):
        sat_d = (np.abs(act_arr[:, d]) > 0.95).mean()
        print(f'  dim {d} saturation (>0.95): {sat_d:.3f}')

    # Per-sample residue: ||h_vf - P_pi(h_vf)|| (the 6.10.6.4 analogue)
    residual = Yc - Xc @ B                   # residue vectors
    per_sample_norm = np.linalg.norm(residual, axis=1)
    print(f'\n=== Per-sample residue (Def 6.10.6.4 analogue) ===')
    print(f'  ||residue|| mean: {per_sample_norm.mean():.3f}')
    print(f'  ||residue|| std : {per_sample_norm.std():.3f}')
    print(f'  ||residue|| p10/50/90: {np.percentile(per_sample_norm, [10,50,90])}')
    print(f'  ||h_vf|| mean: {np.linalg.norm(h_vf, axis=1).mean():.3f}')
    print(f'  residue fraction of h_vf: {per_sample_norm.mean() / np.linalg.norm(h_vf, axis=1).mean():.4f}')

    out = {
        'n_observations': int(N),
        'n_episodes': N_EPISODES,
        'mean_reward': float(np.mean(reward_buf)),
        'mean_gates': float(np.mean(gates_passed)),
        'r2_vf_from_pi_ondist': float(r2_vf_from_pi),
        'r2_pi_from_vf_ondist': float(r2_pi_from_vf),
        'r2_vf_from_pi_v1': 0.3721,
        'pi_cv_mean': float(pi_cv.mean()),
        'vf_cv_mean': float(vf_cv.mean()),
        'yaw_saturation_rate': float(yaw_sat.mean()),
        'per_sample_residue_mean': float(per_sample_norm.mean()),
        'per_sample_residue_std': float(per_sample_norm.std()),
        'vf_hidden_norm_mean': float(np.linalg.norm(h_vf, axis=1).mean()),
        'action_stds': act_arr.std(0).tolist(),
        'action_ranges_min': act_arr.min(0).tolist(),
        'action_ranges_max': act_arr.max(0).tolist(),
        'obs_stats': {
            'dim_means': obs_arr.mean(0).tolist(),
            'dim_stds':  obs_arr.std(0).tolist(),
            'dim_absmax': np.abs(obs_arr).max(0).tolist(),
        },
    }
    out_path = os.path.join(OUT_DIR, 'rho_probe_v2_ondist.json')
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nWrote {out_path}')


if __name__ == '__main__':
    main()
