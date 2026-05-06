"""
ρ-probe v1 — inner/outer adjunction residue on the 60.4M Anakin policy.

Theoretical frame (Coherent Structure §6.10, Anchor §1.10 + §3.8):
    The Identity-Trajectory Triple factors through an adjoint pair ι_S ⊣ ω_S.
    Residue ρ(S) := ‖coker_Inner(S)(η)‖ measures content in the inner representation
    not reducible to the outer commitment. For a PPO policy:
        Outer ω_S ≈ policy_trunk → action_net (commits obs to action distribution)
        Inner ι_S ≈ value_trunk  → value_net  (reflective state assessment)
        η ≈ the composite; residue = what value-trunk encodes that policy-trunk does not.

v1 operationalizations (all run against best_model at 60.4M steps):
    R1. Activation CV per neuron per trunk — baseline-CV KF-style signal
    R2. Linear explainability gap — regress h_vf on h_pi and vice versa; unexplained
        variance on each side IS the cokernel's first quantitative image.
    R3. Policy entropy conditional on value — high-value states with residual entropy
        indicate ρ > 0 even at commitments the agent rates confidently.

This is v1: random obs sampling within obs_space bounds. v2 will add on-distribution
rollouts and compare the two regimes (in-distribution vs off-distribution ρ).
"""

import os, sys, json, zipfile, io
import numpy as np
import torch
import torch.nn as nn

MODEL_PATH = r'C:\Users\mercu\clawd\projects\aigrandprix\sim\runs\infinite_1771733969\best\best_model.zip'
OUT_DIR = r'C:\Users\mercu\clawd\projects\aigrandprix\probes'

N_SAMPLES = 20000
SEED = 17

def load_weights(path):
    with zipfile.ZipFile(path) as z:
        with z.open('policy.pth') as f:
            sd = torch.load(io.BytesIO(f.read()), map_location='cpu', weights_only=False)
        with z.open('data') as f:
            data = json.loads(f.read().decode())
    return sd, data

def build_trunk(sd, prefix):
    # prefix = 'mlp_extractor.policy_net' or 'mlp_extractor.value_net'
    layers = []
    idx = 0
    while f'{prefix}.{idx}.weight' in sd:
        W = sd[f'{prefix}.{idx}.weight']
        b = sd[f'{prefix}.{idx}.bias']
        lin = nn.Linear(W.shape[1], W.shape[0])
        lin.weight.data = W.clone()
        lin.bias.data = b.clone()
        layers.append(lin)
        layers.append(nn.Tanh())  # SB3 default for MlpPolicy
        idx += 2
    return nn.Sequential(*layers)

def forward_with_activations(trunk, x):
    """Return list of post-activation tensors (after each Tanh)."""
    acts = []
    h = x
    for layer in trunk:
        h = layer(h)
        if isinstance(layer, nn.Tanh):
            acts.append(h.detach())
    return h, acts

def main():
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    print(f'Loading {MODEL_PATH}')
    sd, data = load_weights(MODEL_PATH)
    print(f'Model has {data["num_timesteps"]:,} training steps')

    pi_trunk = build_trunk(sd, 'mlp_extractor.policy_net')
    vf_trunk = build_trunk(sd, 'mlp_extractor.value_net')

    # Action head: 512 -> 4  (mean of Gaussian; log_std is separate)
    action_W = sd['action_net.weight']
    action_b = sd['action_net.bias']
    value_W  = sd['value_net.weight']
    value_b  = sd['value_net.bias']
    log_std  = sd['log_std']  # shape (4,) — state-independent

    # Obs space — from training env. Per convert from data serialization:
    # 30-dim Box. We'll sample uniformly in [-1, 1] as a first proxy; most obs
    # dimensions are normalized. On-distribution rollout probe comes in v2.
    obs = torch.from_numpy(
        np.random.uniform(-1.0, 1.0, size=(N_SAMPLES, 30)).astype(np.float32)
    )

    with torch.no_grad():
        pi_h_final, pi_acts = forward_with_activations(pi_trunk, obs)
        vf_h_final, vf_acts = forward_with_activations(vf_trunk, obs)
        # Action mean + value
        mu_a = pi_h_final @ action_W.t() + action_b           # (N, 4)
        v    = vf_h_final @ value_W.t()  + value_b            # (N, 1)
        std_a = torch.exp(log_std).expand_as(mu_a)            # (N, 4)
        # Gaussian entropy per sample (diag cov): sum_i 0.5*log(2πe σ²)
        ent = (0.5 * (np.log(2*np.pi*np.e) + 2*torch.log(std_a))).sum(dim=1)

    pi_hidden = pi_h_final.numpy()  # (N, 512)
    vf_hidden = vf_h_final.numpy()

    # ─── R1: activation CV per neuron per trunk ──────────────────────────────
    def cv_stats(tag, acts):
        print(f'\n=== R1: activation CV — {tag} trunk ===')
        for li, a in enumerate(acts):
            a_np = a.numpy()
            mean_abs = np.abs(a_np).mean(axis=0) + 1e-9
            std     = a_np.std(axis=0)
            cv      = std / mean_abs
            print(f'  layer {li}: CV mean={cv.mean():.3f}  median={np.median(cv):.3f}  '
                  f'p90={np.percentile(cv,90):.3f}  dead-like (CV<0.1)={int((cv<0.1).sum())}/{len(cv)}')
        return cv
    pi_cv = cv_stats('policy', pi_acts)
    vf_cv = cv_stats('value',  vf_acts)

    # ─── R2: linear explainability gap ───────────────────────────────────────
    # How much of vf_hidden is a linear function of pi_hidden? And vice versa?
    # R² = 1 - SS_res/SS_tot of least-squares fit.
    def r2_regression(X, Y):
        # Center
        Xc = X - X.mean(axis=0, keepdims=True)
        Yc = Y - Y.mean(axis=0, keepdims=True)
        # Solve Xc @ B = Yc
        B, *_ = np.linalg.lstsq(Xc, Yc, rcond=None)
        Y_hat = Xc @ B
        ss_res = ((Yc - Y_hat)**2).sum()
        ss_tot = (Yc**2).sum()
        return 1.0 - ss_res/ss_tot

    print('\n=== R2: cross-trunk linear explainability ===')
    r2_vf_from_pi = r2_regression(pi_hidden, vf_hidden)
    r2_pi_from_vf = r2_regression(vf_hidden, pi_hidden)
    print(f'  R2(vf_hidden | pi_hidden) = {r2_vf_from_pi:.4f}   -> cokernel fraction: {1-r2_vf_from_pi:.4f}')
    print(f'  R2(pi_hidden | vf_hidden) = {r2_pi_from_vf:.4f}   -> kernel fraction:   {1-r2_pi_from_vf:.4f}')

    # Also CCA-like summary: SVD of (pi, vf) cross-covariance
    Xc = pi_hidden - pi_hidden.mean(axis=0, keepdims=True)
    Yc = vf_hidden - vf_hidden.mean(axis=0, keepdims=True)
    C_xy = (Xc.T @ Yc) / (len(Xc) - 1)
    s = np.linalg.svd(C_xy, compute_uv=False)
    print(f'  cross-cov singular values — top 5: {s[:5]}')
    print(f'  spectral energy ratio top-10 / total: {(s[:10]**2).sum()/(s**2).sum():.4f}')

    # ─── R3: policy entropy vs value ─────────────────────────────────────────
    print('\n=== R3: policy entropy vs value ===')
    v_np = v.numpy().flatten()
    e_np = ent.numpy()
    # Bucket by value quantile
    qs = np.quantile(v_np, [0.1, 0.25, 0.5, 0.75, 0.9])
    print(f'  value quantiles 10/25/50/75/90: {qs}')
    print(f'  entropy mean: {e_np.mean():.4f}  std: {e_np.std():.4f}')
    # Correlation
    corr = np.corrcoef(v_np, e_np)[0,1]
    print(f'  corr(value, entropy) = {corr:+.4f}')
    # High-value + high-entropy mass (residue proxy)
    vq90 = np.quantile(v_np, 0.9)
    eq50 = np.median(e_np)
    mask = (v_np > vq90) & (e_np > eq50)
    print(f'  fraction in [value>p90 ∧ entropy>med] = {mask.mean():.4f}  '
          f'(≥0.05 meaningful; = 1% uniform expectation)')
    # log_std vector
    print(f'  log_std per action: {log_std.tolist()}  → std: {torch.exp(log_std).tolist()}')

    # ─── Save artifact ───────────────────────────────────────────────────────
    out = {
        'model_path': MODEL_PATH,
        'num_timesteps': int(data['num_timesteps']),
        'n_samples': N_SAMPLES,
        'seed': SEED,
        'obs_regime': 'uniform_[-1,1]_v1',
        'R1_policy_trunk_cv': [{'layer': i, 'mean': float(a.numpy().std(0).mean() / (np.abs(a.numpy()).mean(0)+1e-9).mean())} for i, a in enumerate(pi_acts)],
        'R2_r2_vf_from_pi': float(r2_vf_from_pi),
        'R2_r2_pi_from_vf': float(r2_pi_from_vf),
        'R2_cross_cov_top5_singular': s[:5].tolist(),
        'R3_entropy_mean': float(e_np.mean()),
        'R3_corr_value_entropy': float(corr),
        'R3_high_val_high_ent_frac': float(mask.mean()),
        'log_std': log_std.tolist(),
    }
    out_path = os.path.join(OUT_DIR, 'rho_probe_v1_results.json')
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nWrote {out_path}')

if __name__ == '__main__':
    main()
