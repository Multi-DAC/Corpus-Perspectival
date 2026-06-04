"""
train_vision_corrected.py — Gaze-aware fine-tune of Anakin under the CORRECTED perception model.

Tonight's finding: the sim perception model aimed the FoV cone up the thrust axis (body-z), so the
vision policy never saw gates (W5 = 0.23). Fixed: FoV cone around the deploy camera axis (+x nose +
20deg tilt, matching vision/adapter.py::_cam_to_body_with_tilt) + ego-motion dead-reckon for the
out-of-frame gaps. Frozen omniscient Anakin CRABS, so it doesn't keep gates in a nose camera; this
fine-tune (warm-started from the 80M pilot) teaches it gaze-aware nose-forward flight — the only way
a body-mounted forward camera stays pointed at the next gate.

Trains RAW (no VecNormalize — matches the 80M's original regime; only the obs CONTENT changes,
privileged -> corrected-perception). F2 log_std clamp prevents the yaw-log_std divergence the
original run suffered. Checkpoints saved per interval; eval with metrics under the same corrected cam.

Usage:
    python train_vision_corrected.py --total-steps 3000000 --n-envs 8 --tag gaze1
"""
import os, sys, time, argparse
import numpy as np
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, str(Path(HERE).parent / "rl"))

import torch
from infinite_gate_env import InfiniteGateEnv
from perception_deadreckon import DeadReckonPerceptionObsWrapper
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import BaseCallback

TEACHER = os.path.join(HERE, "runs", "infinite_1771556763", "checkpoints",
                       "ppo_infinite_80000000_steps.zip")
c20, s20 = np.cos(np.radians(20)), np.sin(np.radians(20))
CAM_NOSE_TILT = [c20, 0.0, s20]          # +x nose + 20deg up, deploy convention (adapter.py)


class LogStdClamp(BaseCallback):
    """F2: clamp policy log_std to [log0.1, log1.0] before each rollout (yaw-divergence guard)."""
    def __init__(self, lo=0.1, hi=1.0):
        super().__init__()
        self.lo, self.hi = float(np.log(lo)), float(np.log(hi))
    def _on_step(self):
        return True
    def _on_rollout_start(self):
        with torch.no_grad():
            self.model.policy.log_std.data.clamp_(self.lo, self.hi)


class GatesLogger(BaseCallback):
    """Print rolling gates/ep from info dict every `freq` steps."""
    def __init__(self, freq=100_000):
        super().__init__(); self.freq = freq; self._last = 0; self._g = []
    def _on_step(self):
        for info in self.locals.get("infos", []):
            if "episode" in info:
                self._g.append(info.get("gates_passed", 0))
        if self.num_timesteps - self._last >= self.freq:
            self._last = self.num_timesteps
            if self._g:
                g = np.array(self._g[-200:])
                print(f"  [{self.num_timesteps:>9,}] gates/ep ~{g.mean():.2f} "
                      f"(max {g.max()}, >=1 {100*(g>=1).mean():.0f}%, n={len(g)})", flush=True)
        return True


def make_env(seed, ground_prob):
    def _init():
        env = InfiniteGateEnv(gate_radius=0.75, max_steps=30000, dt=0.002, substeps=1,
                              domain_rand=True, domain_rand_scale=0.15, adaptive_curriculum=True,
                              ground_start_prob=ground_prob, perception_obs=True, seed=seed)
        # swap stock perception wrapper for corrected-camera + dead-reckon
        env._obs_wrapper = DeadReckonPerceptionObsWrapper(
            env._ctbr, cam_axis_body=CAM_NOSE_TILT, deadreckon=True, randomize=True, seed=seed + 7)
        env.observation_space = env._obs_wrapper.observation_space
        return Monitor(env)
    return _init


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--total-steps", type=int, default=3_000_000)
    p.add_argument("--n-envs", type=int, default=8)
    p.add_argument("--ground-prob", type=float, default=0.5)
    p.add_argument("--lr", type=float, default=1e-4)        # fine-tune LR (gentle)
    p.add_argument("--save-every", type=int, default=500_000)
    p.add_argument("--tag", default="gaze1")
    p.add_argument("--scratch", action="store_true", help="train from scratch instead of warm-start")
    args = p.parse_args()

    out = Path(HERE) / "runs" / f"vision_corrected_{args.tag}_{int(time.time())}"
    (out / "checkpoints").mkdir(parents=True, exist_ok=True)
    print(f"=== Gaze-aware fine-tune (corrected camera +x+20tilt, dead-reckon) ===")
    print(f"  out: {out}\n  warm-start: {not args.scratch}  lr={args.lr}  steps={args.total_steps:,}")

    venv = DummyVecEnv([make_env(seed=i * 42, ground_prob=args.ground_prob)
                        for i in range(args.n_envs)])

    if args.scratch:
        model = PPO("MlpPolicy", venv, learning_rate=args.lr, clip_range=0.2, ent_coef=0.01,
                    n_steps=4096, batch_size=512, n_epochs=8, gamma=0.999, gae_lambda=0.95,
                    max_grad_norm=0.5, vf_coef=0.5,
                    policy_kwargs=dict(net_arch=dict(pi=[512, 512], vf=[512, 512])),
                    device="cpu", verbose=0)
    else:
        model = PPO.load(TEACHER, env=venv, device="cpu")
        model.learning_rate = args.lr
        model.max_grad_norm = 0.3
        print(f"  resumed 80M Anakin; lr->{args.lr}, max_grad_norm->0.3")

    class Ckpt(BaseCallback):
        def __init__(self, every, path):
            super().__init__(); self.every = every; self.path = Path(path); self._last = 0
        def _on_step(self):
            if self.num_timesteps - self._last >= self.every:
                self._last = self.num_timesteps
                self.model.save(str(self.path / f"vc_{self.num_timesteps}_steps"))
            return True

    t0 = time.time()
    model.learn(total_timesteps=args.total_steps, progress_bar=False, reset_num_timesteps=True,
                callback=[LogStdClamp(), GatesLogger(), Ckpt(args.save_every, out / "checkpoints")])
    model.save(str(out / "final_model"))
    print(f"\n  done in {(time.time()-t0)/60:.1f} min -> {out}/final_model.zip")


if __name__ == "__main__":
    main()
