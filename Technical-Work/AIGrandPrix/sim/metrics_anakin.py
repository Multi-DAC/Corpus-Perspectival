"""
metrics_anakin.py — non-disruptive performance snapshot of the W5 vision policy.
Reads the LATEST loop checkpoint (does NOT touch the running loop), evals it on the
SAME perception-obs env it trains on, and reports gates/episode, takeoff%, per-maneuver
pass rates, reward. Appends a row to metrics_history.csv so we track development over time.

Run anytime:  python metrics_anakin.py            (default 25 eps, ground_prob 0.5)
              python metrics_anakin.py --episodes 40 --ground-prob 1.0   (VQ1 far-ground)
"""
import sys, os, glob, time, csv, argparse, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "rl"))
from infinite_gate_env import InfiniteGateEnv, ManeuverLibrary
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

TAKEOFF_ALT = 2.0


def latest_ckpt():
    cands = [z for z in glob.glob(os.path.join(HERE, "runs", "infinite_v3_vq1_vision_w5*",
             "checkpoints", "ppo_v3_*_steps.zip")) if os.path.exists(z[:-4] + "_vecnorm.pkl")]
    return max(cands, key=os.path.getmtime) if cands else None


def cumulative_steps():
    """Parse the loop log for cumulative steps (best-effort)."""
    log = os.path.join(HERE, "vq1_w5loop.log")
    if not os.path.exists(log): return None
    done = 0
    for line in open(log, encoding="utf-8", errors="ignore"):
        if "done |" in line and "/30,000,000" in line:
            try: done = int(line.split("|")[1].split("/")[0].strip().replace(",", ""))
            except Exception: pass
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=25)
    ap.add_argument("--ground-prob", type=float, default=0.5)
    ap.add_argument("--ckpt", default=None)
    args = ap.parse_args()

    ck = args.ckpt or latest_ckpt()
    if not ck:
        print("no checkpoint found"); return
    vp = ck[:-4] + "_vecnorm.pkl"
    print(f"eval checkpoint: {os.path.relpath(ck, HERE)}")

    def make(): return InfiniteGateEnv(perception_obs=True, ground_start_prob=args.ground_prob,
                                       domain_rand=True, adaptive_curriculum=True, seed=777)
    raw = DummyVecEnv([make])
    venv = VecNormalize.load(vp, raw); venv.training = False; venv.norm_reward = False
    model = PPO.load(ck, device="cpu")
    inner = venv.venv.envs[0]

    gates, rewards, lengths, took = [], [], [], 0
    for ep in range(args.episodes):
        obs = venv.reset(); done = [False]; R = 0.0; L = 0; max_h = -1e9; ep_g = 0
        while not done[0] and L < 30000:
            act, _ = model.predict(obs, deterministic=True)
            obs, r, done, info = venv.step(act)
            R += float(r[0]); L += 1
            max_h = max(max_h, float(inner._base_env.state[2]))     # z-UP training env: altitude = +z
            ep_g = max(ep_g, int(info[0].get('gates_passed', 0)))   # read from info — DummyVecEnv auto-resets env attrs on done
        gates.append(ep_g); rewards.append(R); lengths.append(L)
        took += (max_h >= TAKEOFF_ALT)

    g = np.array(gates)
    mstats = inner.get_maneuver_stats()
    print(f"\n=== Anakin @ ~{cumulative_steps() or '?':,} cumulative steps "
          f"(ground_prob={args.ground_prob}, n={args.episodes}) ===" if isinstance(cumulative_steps(), int)
          else f"\n=== Anakin (ground_prob={args.ground_prob}, n={args.episodes}) ===")
    print(f"  gates/episode : mean {g.mean():.2f}  median {np.median(g):.0f}  max {g.max()}  (>=1 gate: {(g>=1).mean()*100:.0f}%)")
    print(f"  takeoff%      : {took}/{args.episodes} = {took/args.episodes*100:.0f}%")
    print(f"  reward/episode: mean {np.mean(rewards):.0f}")
    print(f"  episode length: mean {np.mean(lengths):.0f} steps")
    print(f"  per-maneuver pass rate (this eval):")
    for m in ManeuverLibrary.MANEUVERS:
        s = mstats[m]
        if s["attempts"] > 0:
            print(f"    {m:11s} {s['successes']:>3}/{s['attempts']:<3} = {s['rate']*100:>3.0f}%")

    # append history
    hist = os.path.join(HERE, "metrics_history.csv")
    new = not os.path.exists(hist)
    with open(hist, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["time", "cumulative_steps", "ground_prob", "episodes",
                            "mean_gates", "median_gates", "max_gates", "pct_ge1_gate",
                            "takeoff_pct", "mean_reward", "mean_len", "ckpt"])
        w.writerow([time.strftime("%Y-%m-%d %H:%M"), cumulative_steps(), args.ground_prob, args.episodes,
                    round(g.mean(), 2), int(np.median(g)), int(g.max()), round((g >= 1).mean()*100, 0),
                    round(took/args.episodes*100, 0), round(np.mean(rewards), 0), round(np.mean(lengths), 0),
                    os.path.basename(ck)])
    print(f"\n-> appended to metrics_history.csv (run periodically to see the trend)")


if __name__ == "__main__":
    main()
