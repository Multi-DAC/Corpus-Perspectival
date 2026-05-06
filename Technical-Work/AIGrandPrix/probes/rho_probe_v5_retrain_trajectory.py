"""
rho-probe v5 - retrain trajectory.

Measure off-distribution cokernel at each saved checkpoint in the 7.5M v3
retrain run, plus the 200K validation run, plus the 60.4M baseline. Tests
the framework prediction that rho climbs into Structural-stratum range
(~0.2-0.6) as specialization proceeds under F1+F2+F3 healthy training.

No env needed. Loads state_dict from zip, builds trunks, feeds uniform
random obs, measures R^2(vf|pi) linear fit, reports cokernel = 1 - R^2.
"""
import os, sys, io, zipfile, glob, json
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn

BASE = Path(r'C:\Users\mercu\clawd\projects\aigrandprix')
RETRAIN_DIR = BASE / 'sim' / 'runs' / 'infinite_v3_retrain10M_1777074572'
VALIDATION_DIR = BASE / 'sim' / 'runs' / 'infinite_v3_validation_1777074001'
BASELINE = BASE / 'sim' / 'runs' / 'infinite_1771733969' / 'best' / 'best_model.zip'
OUT = BASE / 'probes' / 'rho_probe_v5_retrain_trajectory.json'
N_SAMPLES = 10_000
SEED = 17


def load_sd(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        with z.open('policy.pth') as f:
            return torch.load(io.BytesIO(f.read()), map_location='cpu', weights_only=False)


def build_trunk(sd, prefix):
    layers, idx = [], 0
    while f'{prefix}.{idx}.weight' in sd:
        W = sd[f'{prefix}.{idx}.weight']; b = sd[f'{prefix}.{idx}.bias']
        lin = nn.Linear(W.shape[1], W.shape[0])
        lin.weight.data = W.clone(); lin.bias.data = b.clone()
        layers.append(lin); layers.append(nn.Tanh()); idx += 2
    return nn.Sequential(*layers)


def probe(sd, n_samples=N_SAMPLES, obs_dim=30):
    pi = build_trunk(sd, 'mlp_extractor.policy_net')
    vf = build_trunk(sd, 'mlp_extractor.value_net')
    np.random.seed(SEED); torch.manual_seed(SEED)
    obs = torch.from_numpy(np.random.uniform(-1, 1, size=(n_samples, obs_dim)).astype(np.float32))
    with torch.no_grad():
        h_pi = pi(obs).numpy(); h_vf = vf(obs).numpy()
    pi_cv = float((h_pi.std(0) / (np.abs(h_pi).mean(0)+1e-9)).mean())
    vf_cv = float((h_vf.std(0) / (np.abs(h_vf).mean(0)+1e-9)).mean())
    Xc = h_pi - h_pi.mean(0, keepdims=True); Yc = h_vf - h_vf.mean(0, keepdims=True)
    B, *_ = np.linalg.lstsq(Xc, Yc, rcond=None)
    r2 = 1 - float(((Yc - Xc @ B)**2).sum() / (Yc**2).sum())
    return {
        'pi_cv': pi_cv, 'vf_cv': vf_cv,
        'r2_vf_from_pi': r2, 'cokernel': 1 - r2,
        'pi_hnorm': float(np.linalg.norm(h_pi, axis=1).mean()),
        'vf_hnorm': float(np.linalg.norm(h_vf, axis=1).mean()),
        'log_std': sd['log_std'].tolist() if 'log_std' in sd else None,
    }


def main():
    results = []

    # 60.4M baseline (no F1/F2/F3)
    print('=== 60.4M BASELINE (no F1/F2/F3) ===')
    r = probe(load_sd(BASELINE)); r['label'] = 'baseline_60.4M'; r['step'] = 60_400_000
    print(f"  cokernel={r['cokernel']:.4f}  hnorm pi={r['pi_hnorm']:.2f} vf={r['vf_hnorm']:.2f}  "
          f"log_std={[round(x,3) for x in r['log_std']]}")
    results.append(r)

    # 200K validation (F1+F2+F3)
    print('\n=== 200K VALIDATION (F1+F2+F3) ===')
    vpath = str(VALIDATION_DIR / 'final_model.zip')
    if os.path.exists(vpath):
        r = probe(load_sd(vpath)); r['label'] = 'v3_validation_200K'; r['step'] = 200_000
        print(f"  cokernel={r['cokernel']:.4f}  hnorm pi={r['pi_hnorm']:.2f} vf={r['vf_hnorm']:.2f}  "
              f"log_std={[round(x,3) for x in r['log_std']]}")
        results.append(r)

    # Retrain checkpoints
    print('\n=== RETRAIN TRAJECTORY (F1+F2+F3) ===')
    ckpts = sorted(
        glob.glob(str(RETRAIN_DIR / 'checkpoints' / 'ppo_v3_*_steps.zip')),
        key=lambda p: int(os.path.basename(p).split('_')[2]),
    )
    print(f'  found {len(ckpts)} checkpoints')
    for ckpt in ckpts:
        step = int(os.path.basename(ckpt).split('_')[2])
        r = probe(load_sd(ckpt)); r['label'] = f'retrain_{step}'; r['step'] = step
        print(f"  step={step:>8,}  cokernel={r['cokernel']:.4f}  "
              f"hnorm pi={r['pi_hnorm']:.2f} vf={r['vf_hnorm']:.2f}  "
              f"log_std={[round(x,3) for x in r['log_std']]}")
        results.append(r)

    # Save
    with open(OUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\nWrote {OUT}')

    # Brief summary
    print('\n=== TRAJECTORY SUMMARY ===')
    retrain_only = [r for r in results if r['label'].startswith('retrain_')]
    if retrain_only:
        starts = retrain_only[0]
        ends = retrain_only[-1]
        print(f"  Retrain: cokernel {starts['cokernel']:.4f} (step {starts['step']:,}) "
              f"-> {ends['cokernel']:.4f} (step {ends['step']:,})")
        delta = ends['cokernel'] - starts['cokernel']
        print(f"  Delta: {delta:+.4f}")
        if delta > 0.1:
            print(f"  --> rho CLIMBING (M12 Structural-stratum prediction)")
        elif delta < -0.05:
            print(f"  --> rho DROPPING")
        else:
            print(f"  --> rho roughly stable")


if __name__ == '__main__':
    main()
