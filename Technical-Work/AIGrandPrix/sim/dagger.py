"""
dagger.py — DAgger iterations to close the BC compounding-error gap (Anakin distillation).

Pure BC fails because the student visits off-distribution states the teacher never showed it.
DAgger fixes this: roll out the CURRENT STUDENT (it drives from perception obs), query the
TEACHER for the correct action at every state the student actually visits (privileged view of
the same physics state — the same dual-view trick as distill_collect, but the student's action
steps the env), aggregate those (perception_obs, teacher_action) labels, retrain. Repeat.

Warm-starts from the BC student, grows one aggregated dataset, refits obs normalization on it
each iteration, and saves a PPO .zip + paired vecnorm.pkl per iteration so metrics_anakin.py
can eval any of them directly.

Usage:
    python dagger.py --iters 4 --rollout-pairs 60000 --epochs 15
"""
import os, sys, time, argparse
import numpy as np
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "rl"))

import torch
from infinite_gate_env import InfiniteGateEnv
from perception_obs import PerceptionObsWrapper
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

TEACHER_DEFAULT = os.path.join(HERE, "runs", "infinite_1771556763",
                               "checkpoints", "ppo_infinite_80000000_steps.zip")
TAKEOFF_ALT = 2.0


def _reset_perception(perc):
    perc._reset_perception_state(); perc._sample_episode_params()
    perc.last_gate_idx = 0; perc.last_gate_time = 0.0


def forward_mean(policy, x):
    features = policy.extract_features(x)
    if policy.share_features_extractor:
        latent_pi, _ = policy.mlp_extractor(features)
    else:
        pi_feat, _ = features
        latent_pi = policy.mlp_extractor.forward_actor(pi_feat)
    return policy.action_net(latent_pi)


def normalize(obs, mean, std, clip):
    return np.clip((obs - mean) / std, -clip, clip).astype(np.float32)


def rollout_student(model, mean, std, clip, env, perc, teacher, n_pairs, ground_prob, seed):
    """Student drives; teacher labels every visited state. Returns (obs, act) + flight stats."""
    obs_buf, act_buf = [], []
    ep_gates, took, ep = [], 0, 0
    priv_obs, _ = env.reset(); _reset_perception(perc)
    L, max_h = 0, -1e9
    base = env._base_env
    while len(obs_buf) < n_pairs:
        perc_obs = perc.observation(None)                       # student input
        s_in = normalize(perc_obs[None], mean, std, clip)
        student_act, _ = model.predict(s_in, deterministic=True)
        teacher_act, _ = teacher.predict(priv_obs, deterministic=True)  # DAgger label
        obs_buf.append(np.asarray(perc_obs, dtype=np.float32))
        act_buf.append(np.asarray(teacher_act, dtype=np.float32))
        priv_obs, _r, term, trunc, info = env.step(np.asarray(student_act[0]))  # STUDENT drives
        L += 1; max_h = max(max_h, float(base.state[2]))
        if term or trunc or L >= 30000:
            ep_gates.append(int(info.get("gates_passed", 0)))
            took += (max_h >= TAKEOFF_ALT); ep += 1
            priv_obs, _ = env.reset(); _reset_perception(perc)
            L, max_h = 0, -1e9
    g = np.array(ep_gates) if ep_gates else np.array([0])
    return (np.stack(obs_buf), np.stack(act_buf),
            dict(gates_mean=float(g.mean()), gates_max=int(g.max()),
                 pct_ge1=float((g >= 1).mean() * 100), takeoff=took, eps=ep))


def train_on(policy, obs_n, act, epochs, batch, lr, seed):
    opt = torch.optim.Adam(policy.parameters(), lr=lr)
    X = torch.as_tensor(obs_n); Y = torch.as_tensor(act)
    n = len(X); policy.train()
    for ep in range(epochs):
        perm = torch.randperm(n)
        tot = 0.0
        for i in range(0, n, batch):
            b = perm[i:i + batch]
            loss = torch.nn.functional.mse_loss(forward_mean(policy, X[b]), Y[b])
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item() * len(b)
    policy.eval()
    return tot / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", default=TEACHER_DEFAULT)
    ap.add_argument("--student", default=os.path.join(HERE, "runs", "distill", "bc_student.zip"))
    ap.add_argument("--seed-data", default=os.path.join(HERE, "runs", "distill", "bc_seed.npz"))
    ap.add_argument("--out", default=os.path.join(HERE, "runs", "distill"))
    ap.add_argument("--iters", type=int, default=4)
    ap.add_argument("--rollout-pairs", type=int, default=60000)
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--batch", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--ground-prob", type=float, default=0.5)
    ap.add_argument("--eval-eps", type=int, default=15)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    teacher = PPO.load(args.teacher, device="cpu")
    model = PPO.load(args.student, device="cpu")
    policy = model.policy
    clip = 10.0

    # Aggregated dataset starts from the BC seed.
    d = np.load(args.seed_data, allow_pickle=True)
    agg_obs = d["obs"].astype(np.float32)
    agg_act = d["act"].astype(np.float32)
    print(f"seed dataset: {agg_obs.shape}")

    # Rollout env (privileged main view) + side perception view of the same base env.
    env = InfiniteGateEnv(perception_obs=False, ground_start_prob=args.ground_prob,
                          domain_rand=True, adaptive_curriculum=True, seed=args.seed + 100)
    perc = PerceptionObsWrapper(env._ctbr, randomize=True, seed=args.seed + 101)

    def fit_norm(obs):
        m = obs.mean(axis=0); v = obs.var(axis=0) + 1e-8
        return m, np.sqrt(v), v

    mean, std, var = fit_norm(agg_obs)

    for it in range(1, args.iters + 1):
        t0 = time.time()
        r_obs, r_act, stats = rollout_student(
            model, mean, std, clip, env, perc, teacher,
            args.rollout_pairs, args.ground_prob, args.seed + it)
        agg_obs = np.concatenate([agg_obs, r_obs], axis=0)
        agg_act = np.concatenate([agg_act, r_act], axis=0)
        mean, std, var = fit_norm(agg_obs)                      # refit on grown set
        obs_n = normalize(agg_obs, mean, std, clip)
        tr_mse = train_on(policy, obs_n, agg_act, args.epochs, args.batch, args.lr, args.seed)

        # Persist this iter's student + matching vecnorm.
        venv = VecNormalize(DummyVecEnv([lambda: InfiniteGateEnv(
            perception_obs=True, ground_start_prob=args.ground_prob,
            domain_rand=True, adaptive_curriculum=True, seed=args.seed)]),
            norm_obs=True, norm_reward=False, clip_obs=clip)
        venv.obs_rms.mean = mean.astype(np.float64)
        venv.obs_rms.var = var.astype(np.float64)
        venv.obs_rms.count = float(len(agg_obs))
        venv.training = False; venv.norm_reward = False
        name = f"dagger_iter{it}"
        model.save(str(out / name))
        venv.save(str(out / f"{name}_vecnorm.pkl"))
        venv.close()

        dt = time.time() - t0
        print(f"\n=== DAgger iter {it} ({dt/60:.1f} min) ===")
        print(f"  rollout (student-driven): gates/ep mean {stats['gates_mean']:.2f}  "
              f"max {stats['gates_max']}  >=1 {stats['pct_ge1']:.0f}%  "
              f"takeoff {stats['takeoff']}/{stats['eps']}")
        print(f"  aggregated dataset: {agg_obs.shape[0]:,} pairs   train_mse {tr_mse:.5f}")
        print(f"  saved: {name}.zip (+ vecnorm)")

    env.close()
    np.savez_compressed(out / "dagger_aggregated.npz", obs=agg_obs, act=agg_act)
    print(f"\nDAgger done. Final student: dagger_iter{args.iters}.zip")
    print("Eval with: python metrics_anakin.py --ckpt runs/distill/dagger_iter%d.zip --episodes 25" % args.iters)


if __name__ == "__main__":
    main()
