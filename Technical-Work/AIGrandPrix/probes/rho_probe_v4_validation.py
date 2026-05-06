"""
rho-probe v4 - validation.

Compare v3-trained checkpoint (with F1+F2+F3) vs the 60.4M baseline, on the
same four metrics the earlier probes used:
  - R1 activation CV per trunk (off-dist + on-dist)
  - R2 cross-trunk linear explainability (cokernel fraction)
  - R3 log_std values + action saturation
  - Per-sample residue norm

Expected (framework predictions):
  - log_std[3] stays bounded (F2 working)
  - Value trunk CV on-distribution recovers (F1 working)
  - Action saturation rate drops substantially (F1 working)
  - Cokernel remains in Structural-stratum range (~0.2-0.6) - this is theoretically
    predicted to PERSIST; it's an architectural feature, not a bug
"""
import os, sys, json, io, zipfile, glob
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn

BASE = Path(r'C:\Users\mercu\clawd\projects\aigrandprix')
sys.path.insert(0, str(BASE / 'rl'))
sys.path.insert(0, str(BASE / 'sim'))

from infinite_gate_env import InfiniteGateEnv  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize  # noqa: E402
from stable_baselines3.common.monitor import Monitor  # noqa: E402

BASELINE = str(BASE / 'sim' / 'runs' / 'infinite_1771733969' / 'best' / 'best_model.zip')
OUT_DIR = str(BASE / 'probes')
N_SAMPLES_OFFDIST = 10_000
N_EPISODES_ONDIST = 8
MAX_STEPS_PER_EP = 2000
SEED = 17


def build_trunk(sd, prefix):
    layers, idx = [], 0
    while f'{prefix}.{idx}.weight' in sd:
        W = sd[f'{prefix}.{idx}.weight']; b = sd[f'{prefix}.{idx}.bias']
        lin = nn.Linear(W.shape[1], W.shape[0])
        lin.weight.data = W.clone(); lin.bias.data = b.clone()
        layers.append(lin); layers.append(nn.Tanh()); idx += 2
    return nn.Sequential(*layers)


def find_latest_v3_checkpoint(prefer_pattern='infinite_v3_*'):
    """Find the most recently modified v3 run dir matching prefer_pattern.
    Returns (model_path, vec_normalize_path).
    Picks final_model.zip if present; otherwise the latest checkpoint inside.
    """
    runs = glob.glob(str(BASE / 'sim' / 'runs' / prefer_pattern))
    if not runs:
        return None, None
    runs = sorted(runs, key=os.path.getmtime)
    run = runs[-1]
    final = os.path.join(run, 'final_model.zip')
    if os.path.exists(final):
        return final, os.path.join(run, 'vec_normalize.pkl')
    ckpts = sorted(glob.glob(os.path.join(run, 'checkpoints', 'ppo_v3_*_steps.zip')),
                   key=lambda p: int(os.path.basename(p).split('_')[2]))
    if ckpts:
        return ckpts[-1], os.path.join(run, 'vec_normalize.pkl')
    return None, None


def probe_offdist(sd):
    pi = build_trunk(sd, 'mlp_extractor.policy_net')
    vf = build_trunk(sd, 'mlp_extractor.value_net')
    np.random.seed(SEED); torch.manual_seed(SEED)
    obs = torch.from_numpy(np.random.uniform(-1, 1, size=(N_SAMPLES_OFFDIST, 30)).astype(np.float32))
    with torch.no_grad():
        h_pi = pi(obs).numpy(); h_vf = vf(obs).numpy()
    pi_cv = (h_pi.std(0) / (np.abs(h_pi).mean(0)+1e-9)).mean()
    vf_cv = (h_vf.std(0) / (np.abs(h_vf).mean(0)+1e-9)).mean()
    Xc = h_pi - h_pi.mean(0, keepdims=True); Yc = h_vf - h_vf.mean(0, keepdims=True)
    B, *_ = np.linalg.lstsq(Xc, Yc, rcond=None)
    r2 = 1 - ((Yc - Xc @ B)**2).sum() / (Yc**2).sum()
    return {'pi_cv': float(pi_cv), 'vf_cv': float(vf_cv),
            'r2_vf_from_pi': float(r2),
            'pi_hnorm': float(np.linalg.norm(h_pi, axis=1).mean()),
            'vf_hnorm': float(np.linalg.norm(h_vf, axis=1).mean())}


def probe_ondist(model_path, vec_norm_path=None):
    model = PPO.load(model_path, device='cpu')
    sd = model.policy.state_dict()
    pi = build_trunk(sd, 'mlp_extractor.policy_net')
    vf = build_trunk(sd, 'mlp_extractor.value_net')

    def _mk(seed):
        return Monitor(InfiniteGateEnv(
            gate_radius=0.75, max_steps=30000, dt=0.002, substeps=1,
            domain_rand=True, domain_rand_scale=0.15,
            adaptive_curriculum=True, seed=seed,
        ))
    raw = DummyVecEnv([lambda s=SEED+i: _mk(s) for i in range(1)])

    # Apply VecNormalize stats if provided
    if vec_norm_path and os.path.exists(vec_norm_path):
        env = VecNormalize.load(vec_norm_path, raw)
        env.training = False
        env.norm_reward = False
    else:
        env = raw

    obs_list, act_list, rewards, gates_ep = [], [], [], []
    for ep in range(N_EPISODES_ONDIST):
        obs = env.reset()
        ep_r = 0.0
        ep_gates = 0
        for t in range(MAX_STEPS_PER_EP):
            act, _ = model.predict(obs, deterministic=True)
            obs_list.append(obs[0].copy()); act_list.append(act[0].copy())
            obs, rew, done, info = env.step(act)
            ep_r += float(rew[0])
            if done[0]:
                break
        # Try to read gates passed from underlying env
        if isinstance(env, VecNormalize):
            raw_env = env.venv
        else:
            raw_env = env
        try:
            inner = raw_env.envs[0]
            while hasattr(inner, 'env'): inner = inner.env
            ep_gates = getattr(inner, 'gates_passed_total', 0)
        except Exception:
            pass
        rewards.append(ep_r); gates_ep.append(ep_gates)

    obs_arr = np.array(obs_list, dtype=np.float32)
    act_arr = np.array(act_list, dtype=np.float32)
    with torch.no_grad():
        h_pi = pi(torch.from_numpy(obs_arr)).numpy()
        h_vf = vf(torch.from_numpy(obs_arr)).numpy()

    pi_cv = (h_pi.std(0) / (np.abs(h_pi).mean(0)+1e-9))
    vf_cv = (h_vf.std(0) / (np.abs(h_vf).mean(0)+1e-9))
    Xc = h_pi - h_pi.mean(0, keepdims=True); Yc = h_vf - h_vf.mean(0, keepdims=True)
    B, *_ = np.linalg.lstsq(Xc, Yc, rcond=None)
    r2 = 1 - ((Yc - Xc @ B)**2).sum() / (Yc**2).sum()
    resid = Yc - Xc @ B
    residue_norm = np.linalg.norm(resid, axis=1)

    sat = {d: float((np.abs(act_arr[:, d]) > 0.95).mean()) for d in range(4)}
    return {
        'n_obs': int(len(obs_arr)),
        'mean_reward': float(np.mean(rewards)),
        'gates_per_ep': gates_ep,
        'pi_cv_mean': float(pi_cv.mean()),
        'vf_cv_mean': float(vf_cv.mean()),
        'pi_dead_like': int((pi_cv < 0.1).sum()),
        'vf_dead_like': int((vf_cv < 0.1).sum()),
        'r2_vf_from_pi': float(r2),
        'cokernel': float(1 - r2),
        'residue_norm_mean': float(residue_norm.mean()),
        'vf_hnorm': float(np.linalg.norm(h_vf, axis=1).mean()),
        'residue_frac': float(residue_norm.mean() / np.linalg.norm(h_vf, axis=1).mean()),
        'action_sat': sat,
        'log_std': sd['log_std'].tolist(),
    }, h_pi, h_vf


def main():
    v3_model, v3_vec = find_latest_v3_checkpoint()
    print(f'Baseline: {BASELINE}')
    print(f'v3 model: {v3_model}')
    print(f'v3 VecNormalize stats: {v3_vec}\n')

    # Baseline SD
    with zipfile.ZipFile(BASELINE) as z:
        with z.open('policy.pth') as f:
            base_sd = torch.load(io.BytesIO(f.read()), map_location='cpu', weights_only=False)

    # ---- Off-dist comparison ----
    print('=== OFF-DIST (uniform [-1,1]) ===')
    base_off = probe_offdist(base_sd)
    print(f'  BASELINE  pi_cv={base_off["pi_cv"]:.3f}  vf_cv={base_off["vf_cv"]:.3f}  '
          f'R2(vf|pi)={base_off["r2_vf_from_pi"]:.4f}  cokernel={1-base_off["r2_vf_from_pi"]:.4f}  '
          f'hnorm pi={base_off["pi_hnorm"]:.2f} vf={base_off["vf_hnorm"]:.2f}')

    v3_off_report = None
    if v3_model:
        v3_model_obj = PPO.load(v3_model, device='cpu')
        v3_sd = v3_model_obj.policy.state_dict()
        v3_off = probe_offdist(v3_sd)
        print(f'  v3 NEW    pi_cv={v3_off["pi_cv"]:.3f}  vf_cv={v3_off["vf_cv"]:.3f}  '
              f'R2(vf|pi)={v3_off["r2_vf_from_pi"]:.4f}  cokernel={1-v3_off["r2_vf_from_pi"]:.4f}  '
              f'hnorm pi={v3_off["pi_hnorm"]:.2f} vf={v3_off["vf_hnorm"]:.2f}')
        v3_off_report = v3_off
        print(f'\n  log_std baseline: {base_sd["log_std"].tolist()}')
        print(f'  log_std v3 NEW  : {v3_sd["log_std"].tolist()}')

    # ---- On-dist comparison ----
    print('\n=== ON-DIST rollouts ===')
    print('  Baseline (no VecNormalize for eval)...')
    base_on, _, _ = probe_ondist(BASELINE, vec_norm_path=None)
    print(f'    mean_reward={base_on["mean_reward"]:.1f}  gates/ep={base_on["gates_per_ep"]}')
    print(f'    pi_cv={base_on["pi_cv_mean"]:.3f}  vf_cv={base_on["vf_cv_mean"]:.3f}  '
          f'vf_dead={base_on["vf_dead_like"]}/512')
    print(f'    cokernel={base_on["cokernel"]:.4f}  residue_frac={base_on["residue_frac"]:.4f}')
    print(f'    action_sat: {base_on["action_sat"]}')

    v3_on_report = None
    if v3_model:
        print('  v3 NEW (WITH VecNormalize stats)...')
        v3_on, _, _ = probe_ondist(v3_model, vec_norm_path=v3_vec)
        print(f'    mean_reward={v3_on["mean_reward"]:.1f}  gates/ep={v3_on["gates_per_ep"]}')
        print(f'    pi_cv={v3_on["pi_cv_mean"]:.3f}  vf_cv={v3_on["vf_cv_mean"]:.3f}  '
              f'vf_dead={v3_on["vf_dead_like"]}/512')
        print(f'    cokernel={v3_on["cokernel"]:.4f}  residue_frac={v3_on["residue_frac"]:.4f}')
        print(f'    action_sat: {v3_on["action_sat"]}')
        v3_on_report = v3_on

    # ---- Save ----
    out = {
        'baseline_path': BASELINE,
        'v3_path': v3_model,
        'base_offdist': base_off, 'v3_offdist': v3_off_report,
        'base_ondist': base_on,   'v3_ondist':   v3_on_report,
    }
    out_path = os.path.join(OUT_DIR, 'rho_probe_v4_validation.json')
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nWrote {out_path}')


if __name__ == '__main__':
    main()
