"""
bc_train.py — Behavior-cloning the vision student from the distillation dataset.

Trains an SB3 PPO actor (MlpPolicy, pi=[512,512] — same family as the v3 vision policy)
to imitate the teacher's continuous CTBR action from the perception-grade observation,
via supervised MSE on the policy mean action. Saves the student as a PPO .zip + a paired
VecNormalize .pkl whose obs stats are fit from the dataset, so the normalization the
student trains under is IDENTICAL to what metrics_anakin.py applies at eval.

Output (so metrics_anakin --ckpt works directly):
    <out>/bc_student.zip
    <out>/bc_student_vecnorm.pkl

Usage:
    python bc_train.py --data runs/distill/bc_seed.npz --out runs/distill --epochs 40
"""
import os, sys, time, argparse
import numpy as np
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "rl"))

import torch
from infinite_gate_env import InfiniteGateEnv
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize


def build_student(seed):
    """A perception_obs PPO with the v3 net family — gives correct spaces + a loadable .zip."""
    def mk():
        return InfiniteGateEnv(perception_obs=True, ground_start_prob=0.5,
                               domain_rand=True, adaptive_curriculum=True, seed=seed)
    raw = DummyVecEnv([mk])
    venv = VecNormalize(raw, norm_obs=True, norm_reward=False, clip_obs=10.0)
    model = PPO(
        "MlpPolicy", venv,
        policy_kwargs=dict(net_arch=dict(pi=[512, 512], vf=[512, 512])),
        device="cpu", seed=seed, verbose=0,
    )
    return model, venv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(HERE, "runs", "distill", "bc_seed.npz"))
    ap.add_argument("--out", default=os.path.join(HERE, "runs", "distill"))
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--val-frac", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--name", default="bc_student")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    d = np.load(args.data, allow_pickle=True)
    obs = d["obs"].astype(np.float32)        # (N,30)
    act = d["act"].astype(np.float32)        # (N,4)
    N = len(obs)
    print(f"dataset: {obs.shape} obs, {act.shape} act  ({N:,} pairs)")

    # Obs normalization stats from the dataset (these go into the saved VecNormalize).
    mean = obs.mean(axis=0)
    var = obs.var(axis=0) + 1e-8
    std = np.sqrt(var)

    model, venv = build_student(args.seed)
    # Inject dataset obs stats into the env normalizer; freeze it (eval-time transform == train-time).
    venv.obs_rms.mean = mean.astype(np.float64)
    venv.obs_rms.var = var.astype(np.float64)
    venv.obs_rms.count = float(N)
    venv.training = False
    venv.norm_reward = False
    clip = float(venv.clip_obs)

    # Normalized obs for supervised training (matches VecNormalize.normalize_obs at eval).
    obs_n = np.clip((obs - mean) / std, -clip, clip).astype(np.float32)

    # train/val split
    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(N)
    n_val = int(N * args.val_frac)
    val_idx, tr_idx = idx[:n_val], idx[n_val:]
    Xtr = torch.as_tensor(obs_n[tr_idx]); Ytr = torch.as_tensor(act[tr_idx])
    Xva = torch.as_tensor(obs_n[val_idx]); Yva = torch.as_tensor(act[val_idx])
    print(f"  train {len(Xtr):,} / val {len(Xva):,}")

    policy = model.policy
    policy.train()
    opt = torch.optim.Adam(policy.parameters(), lr=args.lr)

    def forward_mean(x):
        """Policy mean action for obs batch x (SB3 ActorCriticPolicy internals)."""
        features = policy.extract_features(x)
        if policy.share_features_extractor:
            latent_pi, _ = policy.mlp_extractor(features)
        else:
            pi_feat, _ = features
            latent_pi = policy.mlp_extractor.forward_actor(pi_feat)
        return policy.action_net(latent_pi)

    n_tr = len(Xtr)
    t0 = time.time()
    best_val = float("inf")
    for ep in range(1, args.epochs + 1):
        perm = torch.randperm(n_tr)
        tot = 0.0
        for i in range(0, n_tr, args.batch):
            b = perm[i:i + args.batch]
            pred = forward_mean(Xtr[b])
            loss = torch.nn.functional.mse_loss(pred, Ytr[b])
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item() * len(b)
        tr_mse = tot / n_tr
        with torch.no_grad():
            val_mse = torch.nn.functional.mse_loss(forward_mean(Xva), Yva).item()
        best_val = min(best_val, val_mse)
        if ep % 5 == 0 or ep == 1:
            print(f"  epoch {ep:3d}  train_mse {tr_mse:.5f}  val_mse {val_mse:.5f}")

    dt = time.time() - t0
    policy.eval()
    # Sanity: deterministic predict on a few normalized obs vs teacher actions.
    with torch.no_grad():
        sample = forward_mean(Xva[:512]).numpy()
    err = np.abs(sample - Yva[:512].numpy())
    print(f"\n  trained {args.epochs} epochs in {dt:.1f}s  best_val_mse {best_val:.5f}")
    print(f"  per-action-dim MAE (val sample): {err.mean(axis=0).round(4).tolist()}")

    zip_path = out / f"{args.name}.zip"
    pkl_path = out / f"{args.name}_vecnorm.pkl"
    model.save(str(zip_path).replace(".zip", ""))
    venv.save(str(pkl_path))
    print(f"  saved student : {os.path.relpath(zip_path, HERE)}")
    print(f"  saved vecnorm : {os.path.relpath(pkl_path, HERE)}")


if __name__ == "__main__":
    main()
