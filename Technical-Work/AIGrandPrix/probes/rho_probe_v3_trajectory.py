"""
rho-probe v3 - trajectory across training checkpoints.

Core question (M12 strata test at training-dynamics register):
  Does the inner/outer cokernel approach zero (Strong stratum),
  decay slowly (Convergent), or persist (Structural)?

Also: log_std trajectory per action dim. When did yaw diverge?
"""

import os, re, json, zipfile, io
import numpy as np
import torch
import torch.nn as nn

RUN_DIR = r'C:\Users\mercu\clawd\projects\aigrandprix\sim\runs\infinite_1771733969\checkpoints'
BEST_PATH = r'C:\Users\mercu\clawd\projects\aigrandprix\sim\runs\infinite_1771733969\best\best_model.zip'
OUT_DIR = r'C:\Users\mercu\clawd\projects\aigrandprix\probes'
N_SAMPLES = 10000
SEED = 17

# Sample checkpoints covering early / mid-growth / plateau-approach / plateau / post-plateau
SELECTED = [500_000, 2_000_000, 5_000_000, 10_000_000, 15_000_000, 20_000_000,
            30_000_000, 40_000_000, 50_000_000, 55_000_000, 60_000_000,
            60_500_000, 65_000_000, 68_000_000]


def load_weights(path):
    with zipfile.ZipFile(path) as z:
        with z.open('policy.pth') as f:
            sd = torch.load(io.BytesIO(f.read()), map_location='cpu', weights_only=False)
    return sd


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


def probe_checkpoint(path, obs):
    sd = load_weights(path)
    pi_trunk = build_trunk(sd, 'mlp_extractor.policy_net')
    vf_trunk = build_trunk(sd, 'mlp_extractor.value_net')
    with torch.no_grad():
        h_pi = pi_trunk(obs).numpy()
        h_vf = vf_trunk(obs).numpy()
    # Linear R2: vf from pi
    Xc = h_pi - h_pi.mean(0, keepdims=True)
    Yc = h_vf - h_vf.mean(0, keepdims=True)
    B, *_ = np.linalg.lstsq(Xc, Yc, rcond=None)
    Y_hat = Xc @ B
    ss_res = ((Yc - Y_hat)**2).sum(); ss_tot = (Yc**2).sum()
    r2_vf_from_pi = 1.0 - ss_res/ss_tot
    # Reverse
    B2, *_ = np.linalg.lstsq(Yc, Xc, rcond=None)
    X_hat = Yc @ B2
    ss_res2 = ((Xc - X_hat)**2).sum(); ss_tot2 = (Xc**2).sum()
    r2_pi_from_vf = 1.0 - ss_res2/ss_tot2
    log_std = sd['log_std'].tolist()
    # Hidden statistics
    pi_cv_l1 = (h_pi.std(0) / (np.abs(h_pi).mean(0)+1e-9)).mean()
    vf_cv_l1 = (h_vf.std(0) / (np.abs(h_vf).mean(0)+1e-9)).mean()
    # Mean activation magnitude
    pi_h_norm = np.linalg.norm(h_pi, axis=1).mean()
    vf_h_norm = np.linalg.norm(h_vf, axis=1).mean()
    return {
        'r2_vf_from_pi': float(r2_vf_from_pi),
        'r2_pi_from_vf': float(r2_pi_from_vf),
        'log_std': [float(x) for x in log_std],
        'pi_final_cv': float(pi_cv_l1),
        'vf_final_cv': float(vf_cv_l1),
        'pi_hidden_norm': float(pi_h_norm),
        'vf_hidden_norm': float(vf_h_norm),
    }


def main():
    torch.manual_seed(SEED); np.random.seed(SEED)
    obs = torch.from_numpy(np.random.uniform(-1.0, 1.0, size=(N_SAMPLES, 30)).astype(np.float32))

    paths = []
    for s in SELECTED:
        # Snap to available checkpoint
        fname = f'ppo_infinite_{s}_steps.zip'
        p = os.path.join(RUN_DIR, fname)
        if os.path.exists(p):
            paths.append((s, p))
        else:
            print(f'  WARN: {fname} not found, skipping')
    # Also include best
    paths.append(('best_60400000', BEST_PATH))

    print(f'\nProbing {len(paths)} checkpoints...\n')
    print(f'{"steps":>14} {"R2(vf|pi)":>10} {"R2(pi|vf)":>10} {"logstd[0]":>10} {"[1]":>8} {"[2]":>8} {"[3]":>10} {"pi_norm":>9} {"vf_norm":>9}')
    results = []
    for step, path in paths:
        r = probe_checkpoint(path, obs)
        r['step'] = step
        results.append(r)
        ls = r['log_std']
        step_str = f'{step:>14,}' if isinstance(step, int) else f'{step:>14}'
        print(f'{step_str} {r["r2_vf_from_pi"]:>10.4f} {r["r2_pi_from_vf"]:>10.4f} '
              f'{ls[0]:>10.3f} {ls[1]:>8.3f} {ls[2]:>8.3f} {ls[3]:>10.3f} '
              f'{r["pi_hidden_norm"]:>9.2f} {r["vf_hidden_norm"]:>9.2f}')

    out_path = os.path.join(OUT_DIR, 'rho_probe_v3_trajectory.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\nWrote {out_path}')


if __name__ == '__main__':
    main()
