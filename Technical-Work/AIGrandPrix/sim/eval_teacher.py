"""
eval_teacher.py — evaluate the PRIVILEGED-STATE teacher in its OWN obs space.

metrics_anakin.py hardcodes perception_obs=True (correct for the vision student, wrong for the
teacher). The teacher was trained on privileged state (perception_obs=False), so we must eval it
there or it fails at 0%. This is the DISTILLATION-CEILING check: the student can be at best as good
as the teacher it learns from. Mirrors metrics_anakin's metrics for apples-to-apples comparison.

Usage: python eval_teacher.py [--episodes 50] [--ground-prob 0.5] [--ckpt PATH] [--vecnorm PATH]
"""
import sys, os, glob, argparse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "rl"))
from infinite_gate_env import InfiniteGateEnv, ManeuverLibrary
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

TAKEOFF_ALT = 2.0
TEACHER_DIR = os.path.join(HERE, "runs", "infinite_v3_teacher_unitdir_1780340429")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=50)
    ap.add_argument("--ground-prob", type=float, default=0.5)
    ap.add_argument("--ckpt", default=os.path.join(TEACHER_DIR, "checkpoints", "ppo_v3_40000000_steps.zip"))
    ap.add_argument("--vecnorm", default=os.path.join(TEACHER_DIR, "vec_normalize.pkl"))
    args = ap.parse_args()

    print(f"TEACHER ckpt   : {os.path.relpath(args.ckpt, HERE)}")
    print(f"TEACHER vecnorm: {os.path.relpath(args.vecnorm, HERE)}")
    print(f"obs mode       : PRIVILEGED (perception_obs=False)")

    def make(): return InfiniteGateEnv(perception_obs=False, ground_start_prob=args.ground_prob,
                                       domain_rand=True, adaptive_curriculum=True, seed=777)
    raw = DummyVecEnv([make])
    venv = VecNormalize.load(args.vecnorm, raw); venv.training = False; venv.norm_reward = False
    model = PPO.load(args.ckpt, device="cpu")
    inner = venv.venv.envs[0]

    gates, rewards, lengths, took = [], [], [], 0
    for ep in range(args.episodes):
        obs = venv.reset(); done = [False]; R = 0.0; L = 0; max_h = -1e9; ep_g = 0
        while not done[0] and L < 30000:
            act, _ = model.predict(obs, deterministic=True)
            obs, r, done, info = venv.step(act)
            R += float(r[0]); L += 1
            max_h = max(max_h, float(inner._base_env.state[2]))
            ep_g = max(ep_g, int(info[0].get('gates_passed', 0)))
        gates.append(ep_g); rewards.append(R); lengths.append(L); took += (max_h >= TAKEOFF_ALT)

    g = np.array(gates)
    mstats = inner.get_maneuver_stats()
    print(f"\n=== TEACHER (privileged) — ground_prob={args.ground_prob}, n={args.episodes} ===")
    print(f"  gates/episode : mean {g.mean():.2f}  median {np.median(g):.0f}  max {g.max()}  (>=1 gate: {(g>=1).mean()*100:.0f}%)")
    print(f"  takeoff%      : {took}/{args.episodes} = {took/args.episodes*100:.0f}%")
    print(f"  reward/episode: mean {np.mean(rewards):.0f}")
    print(f"  episode length: mean {np.mean(lengths):.0f} steps")
    print(f"  per-maneuver pass rate:")
    for m in ManeuverLibrary.MANEUVERS:
        s = mstats[m]
        if s["attempts"] > 0:
            print(f"    {m:11s} {s['successes']:>3}/{s['attempts']:<3} = {s['rate']*100:>3.0f}%")


if __name__ == "__main__":
    main()
