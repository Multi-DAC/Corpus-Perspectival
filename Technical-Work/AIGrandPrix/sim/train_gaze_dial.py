"""
train_gaze_dial.py — the A0/A2 arm from COVERAGE_ACQUISITION_TENSION_2026-06-03.md.

QUESTION: is gaze (active gate acquisition) TRAINABLE under the dead-reckon dial, with NO gaze
reward — just the gate-passing reward we already have, made instrumentally to require looking?

The morning sweep (gaze_eval.py --reckon inf,2,5,10,20) showed every existing checkpoint flies on
odometry and collapses to ~0.25 gates the instant the crutch is bounded — a CLIFF, not a curve. So
there is no gentle FIXED dial value to train under (reckon=20 is as brutal as reckon=2 for a policy
that hasn't learned to look). The fix is to make the dial a CURRICULUM: warm-start with the crutch
ON (max_reckon_steps=None, the policy flies as it always has), then tighten the dial over training
(inf -> 20 -> 10 -> 5 -> 2) so the policy is forced down the cliff GRADUALLY and has to grow gaze on
the descent, paying the acquisition debt from the gate-passing reward alone.

  A2 (the arm):   --dial-schedule "inf:0,20:0.2,10:0.4,5:0.6,2:0.8"   (default — anneal the dial)
  A0 (control):   --dial-schedule "inf:0"                              (crutch never bounded)

If A2's ACQUISITION-STRESS gates/ep (eval at reckon=2) rises above A0's, gaze is trainable via the
dial and the gaze-reward subproject stays unbuilt (P224 confirmed). If it doesn't, gaze needs reward
shaping after all (the A1/A3 arms), and we'll have learned that cheaply.

Lessons folded in from the FALSIFIED gaze1 fine-tune (GAZE_FINETUNE_RESULT_2026-06-02.md):
  - FIXED difficulty (adaptive_curriculum=False): the dial IS our curriculum; gate difficulty must
    be held constant or training-rollout gates/ep is uninterpretable (that run's "4.2 peak" was on an
    eased track and evaporated to 1.29 deterministically).
  - lr=3e-5 (not 1e-4 — "too hot for too long" drifted the policy off the warm-start basin).
  - SELECT BY DETERMINISTIC EVAL, never training rollout. Each checkpoint is eval'd in-loop at both
    the deploy setting (reckon=None) AND the acquisition-stress setting (reckon=2). Best = best stress.

Usage:
    python train_gaze_dial.py --total-steps 1000000 --tag a2            # the dial arm
    python train_gaze_dial.py --total-steps 1000000 --tag a0 --dial-schedule "inf:0"   # control
"""
import os, sys, time, argparse
import numpy as np
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, str(Path(HERE).parent / "rl"))

import torch
import gymnasium as gym
from infinite_gate_env import InfiniteGateEnv
from perception_deadreckon import DeadReckonPerceptionObsWrapper
from drone_env_v2 import quat_rotate_np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import BaseCallback

TEACHER = os.path.join(HERE, "runs", "infinite_1771556763", "checkpoints",
                       "ppo_infinite_80000000_steps.zip")
c20, s20 = np.cos(np.radians(20)), np.sin(np.radians(20))
CAM_NOSE_TILT = [c20, 0.0, s20]          # +x nose +20deg up — deploy convention (adapter.py)
DEFAULT_SCHEDULE = "inf:0,20:0.2,10:0.4,5:0.6,2:0.8"


# ---------------------------------------------------------------- dial schedule helpers
def parse_schedule(s):
    """'inf:0,20:0.2,2:0.8' -> [(None,0.0),(20,0.2),(2,0.8)] sorted by progress fraction."""
    out = []
    for tok in s.split(","):
        v, f = tok.split(":")
        val = None if v.strip().lower() in ("inf", "none") else int(v)
        out.append((val, float(f)))
    out.sort(key=lambda x: x[1])
    return out


def value_at(sched, p):
    """The dial value in effect at training progress p in [0,1] (last phase whose frac <= p)."""
    val = sched[0][0]
    for v, f in sched:
        if p >= f:
            val = v
        else:
            break
    return val


def _find_wrapper(e):
    """Descend .env until the InfiniteGateEnv that holds the perception _obs_wrapper."""
    while not hasattr(e, "_obs_wrapper") and hasattr(e, "env"):
        e = e.env
    return e if hasattr(e, "_obs_wrapper") else None


# ---------------------------------------------------------------- callbacks
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


class DialSchedule(BaseCallback):
    """Tighten max_reckon_steps on every training env as training progresses (the curriculum)."""
    _UNSET = object()
    def __init__(self, sched, total):
        super().__init__(); self.sched = sched; self.total = total; self._cur = self._UNSET
    def _set(self, val):
        n = 0
        for e in self.training_env.envs:
            w = _find_wrapper(e)
            if w is not None:
                w._obs_wrapper.max_reckon_steps = val
                n += 1
        return n
    def _on_step(self):
        p = self.num_timesteps / self.total
        val = value_at(self.sched, p)
        if val is not self._cur and val != self._cur:
            self._cur = val
            n = self._set(val)
            tag = "inf" if val is None else str(val)
            print(f"  [DIAL {self.num_timesteps:>9,} p={p:.2f}] max_reckon_steps -> {tag} "
                  f"(set on {n} envs)", flush=True)
        return True


class GatesLogger(BaseCallback):
    """Rolling gates/ep from info dict every `freq` steps (DIAGNOSTIC ONLY — not for selection)."""
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
                print(f"  [{self.num_timesteps:>9,}] train-rollout gates/ep ~{g.mean():.2f} "
                      f"(NOT a selection signal — curriculum/dial confounded)", flush=True)
        return True


class EvalGazeDial(BaseCallback):
    """At each interval: save ckpt, run DETERMINISTIC eval at deploy(inf) AND stress(reckon=2).
    Track best-by-acquisition-stress (the metric that sees the debt). Append to ledger."""
    def __init__(self, every, ckpt_dir, ledger, best_file, n_eval=8):
        super().__init__()
        self.every = every; self.dir = Path(ckpt_dir); self.ledger = ledger
        self.best_file = best_file; self.n = n_eval
        self._last = 0; self.best_stress = -1.0; self.best_path = None
    def _log(self, msg):
        print(msg, flush=True)
        with open(self.ledger, "a") as f:
            f.write(msg + "\n")
    def _on_step(self):
        if self.num_timesteps - self._last < self.every:
            return True
        self._last = self.num_timesteps
        ck = self.dir / f"gd_{self.num_timesteps}_steps"
        self.model.save(str(ck))
        try:
            from gaze_eval import run
            rd = run(self.model, max_reckon_steps=None, episodes=self.n, seed=2026)   # deploy
            rs = run(self.model, max_reckon_steps=2, episodes=self.n, seed=2026)      # stress
            ts = time.strftime("%H:%M:%S")
            self._log(f"[{ts}] {self.num_timesteps:>9,}  deploy(inf): gates={rd['gates']:.2f} "
                      f"gaze={rd['gaze']:.3f} iv={rd['inview']:.0f}%  |  stress(2): "
                      f"gates={rs['gates']:.2f} gaze={rs['gaze']:.3f} iv={rs['inview']:.0f}%")
            if rs['gates'] > self.best_stress:
                self.best_stress = rs['gates']; self.best_path = str(ck) + ".zip"
                with open(self.best_file, "w") as f:
                    f.write(f"{self.best_path}\nstress_gates={rs['gates']:.3f} "
                            f"deploy_gates={rd['gates']:.3f} step={self.num_timesteps}\n")
                self._log(f"           ^ new best-by-stress ({rs['gates']:.2f})")
        except Exception as e:
            self._log(f"           eval ERROR @ {self.num_timesteps}: {type(e).__name__}: {e}")
        return True


# ---------------------------------------------------------------- coupled gaze reward (A3)
class CoupledGazeReward(gym.Wrapper):
    """Gaze bonus that pays ONLY when looking-at-the-gate coincides with closing on it.

    A2's finding (2026-06-03): the dial grows looking but UNMOORS it from flying — the policy
    learns to point at the gate at the cost of passing it, so the control (no dial) out-flies it
    at gentle stress. Fix: reward looking *in service of progress*, not looking per se.

        bonus = weight * max(cos<cam_axis, bearing_to_gate>, 0) * max(progress_this_step, 0) * progress_scale

    Staring while stalling or veering pays nothing (progress<=0 or align<=0). Only looking WHILE
    advancing pays. weight=0.5 => a perfectly-aimed approach earns +50% of that step's progress
    reward (env progress_scale=2.0). This makes gaze instrumental to passing by construction.
    Active only when weight>0 (A3); A0/A2 leave it off and are byte-for-byte unchanged.
    """
    def __init__(self, env, weight=0.5, cam=None, progress_scale=2.0):
        super().__init__(env)
        self._base = env._base_env
        self._w = float(weight)
        c = np.asarray(cam if cam is not None else CAM_NOSE_TILT, float)
        self._cam = c / (np.linalg.norm(c) + 1e-9)
        self._psc = float(progress_scale)
        self._prev_d = None
        self._prev_g = None

    def __getattr__(self, name):
        # forward everything (incl. underscore attrs like _obs_wrapper) to the wrapped env,
        # overriding gymnasium.Wrapper's underscore-blocking so the dial hook reaches through.
        if name == "env":
            raise AttributeError(name)
        return getattr(self.env, name)

    def _cur(self):
        g = self._base.current_gate
        if g >= len(self._base.gates):
            return None, None, g
        rel = np.asarray(self._base.gates[g], float) - self._base.state[0:3]
        return float(np.linalg.norm(rel)), rel, g

    def reset(self, **kw):
        out = self.env.reset(**kw)
        self._prev_d, _, self._prev_g = self._cur()
        return out

    def step(self, action):
        obs, reward, term, trunc, info = self.env.step(action)
        if self._w > 0:
            d, rel, g = self._cur()
            if d is not None and d > 1e-6:
                if g == self._prev_g and self._prev_d is not None:
                    progress = self._prev_d - d
                    cam_w = quat_rotate_np(self._base.state[6:10], self._cam)
                    cam_w = cam_w / (np.linalg.norm(cam_w) + 1e-9)
                    align = float(np.dot(cam_w, rel / d))
                    bonus = self._w * max(align, 0.0) * max(progress, 0.0) * self._psc
                    reward = reward + bonus
                    info["gaze_bonus"] = bonus
                self._prev_d, self._prev_g = d, g
            else:
                self._prev_d, self._prev_g = d, g
        return obs, reward, term, trunc, info


# ---------------------------------------------------------------- env
def make_env(seed, ground_prob, init_reckon, gaze_reward_weight=0.0):
    def _init():
        env = InfiniteGateEnv(gate_radius=0.75, max_steps=30000, dt=0.002, substeps=1,
                              domain_rand=True, domain_rand_scale=0.15,
                              adaptive_curriculum=False,        # FIXED difficulty — dial is the curriculum
                              ground_start_prob=ground_prob, perception_obs=True, seed=seed)
        env._obs_wrapper = DeadReckonPerceptionObsWrapper(
            env._ctbr, cam_axis_body=CAM_NOSE_TILT, deadreckon=True,
            max_reckon_steps=init_reckon, randomize=True, seed=seed + 7)
        env.observation_space = env._obs_wrapper.observation_space
        if gaze_reward_weight > 0:
            env = CoupledGazeReward(env, weight=gaze_reward_weight, cam=CAM_NOSE_TILT)
        return Monitor(env)
    return _init


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--total-steps", type=int, default=1_000_000)
    p.add_argument("--n-envs", type=int, default=8)
    p.add_argument("--ground-prob", type=float, default=0.5)
    p.add_argument("--lr", type=float, default=3e-5)                 # gentle (1e-4 drifted gaze1)
    p.add_argument("--save-every", type=int, default=250_000)
    p.add_argument("--eval-episodes", type=int, default=8)
    p.add_argument("--gaze-reward-weight", type=float, default=0.0,
                   help="A3: couple looking to progress. bonus = w*max(align,0)*max(progress,0)*2.0. "
                        "0 = off (A0/A2 unchanged); 0.5 = aimed approach earns +50%% of progress reward.")
    p.add_argument("--tag", default="a2")
    p.add_argument("--dial-schedule", default=DEFAULT_SCHEDULE,
                   help="comma 'value:frac' phases; 'inf'=None. A0 control = 'inf:0'.")
    p.add_argument("--warmstart", default=TEACHER,
                   help="policy to warm-start from. DEFAULT = RAW 80M teacher (validated). A "
                        "VecNormalize-trained navigator (v3 batched) needs its obs normalized — this "
                        "RAW env would feed it unnormalized obs (mismatch); validate before trusting.")
    p.add_argument("--scratch", action="store_true", help="train from scratch (no warm-start)")
    args = p.parse_args()

    sched = parse_schedule(args.dial_schedule)
    init_reckon = value_at(sched, 0.0)

    out = Path(HERE) / "runs" / f"gaze_dial_{args.tag}_{int(time.time())}"
    (out / "checkpoints").mkdir(parents=True, exist_ok=True)
    ledger = str(out / "eval_ledger.txt")
    best_file = str(out / "BEST.txt")

    print(f"=== gaze-dial arm '{args.tag}' (corrected cam +x+20tilt, FIXED difficulty) ===")
    print(f"  out: {out}")
    print(f"  warm-start: {None if args.scratch else os.path.basename(args.warmstart)}  "
          f"lr={args.lr}  steps={args.total_steps:,}")
    print(f"  dial schedule: {sched}  (init reckon = {'inf' if init_reckon is None else init_reckon})")
    print(f"  gaze-reward-weight: {args.gaze_reward_weight}  "
          f"({'COUPLED gaze reward ON (A3)' if args.gaze_reward_weight > 0 else 'off (A0/A2)'})")
    if not args.scratch and os.path.abspath(args.warmstart) != os.path.abspath(TEACHER):
        print("  WARNING: non-default warm-start — if VecNormalize-trained, obs will MISMATCH this "
              "RAW env. Validated path is the RAW 80M teacher.", flush=True)

    venv = DummyVecEnv([make_env(seed=i * 42, ground_prob=args.ground_prob, init_reckon=init_reckon,
                                 gaze_reward_weight=args.gaze_reward_weight)
                        for i in range(args.n_envs)])

    if args.scratch:
        model = PPO("MlpPolicy", venv, learning_rate=args.lr, clip_range=0.2, ent_coef=0.01,
                    n_steps=4096, batch_size=512, n_epochs=8, gamma=0.999, gae_lambda=0.95,
                    max_grad_norm=0.5, vf_coef=0.5,
                    policy_kwargs=dict(net_arch=dict(pi=[512, 512], vf=[512, 512])),
                    device="cpu", verbose=0)
    else:
        model = PPO.load(args.warmstart, env=venv, device="cpu")
        model.learning_rate = args.lr
        model.max_grad_norm = 0.3
        print(f"  resumed {os.path.basename(args.warmstart)}; lr->{args.lr}, max_grad_norm->0.3")

    cbs = [LogStdClamp(),
           DialSchedule(sched, args.total_steps),
           GatesLogger(),
           EvalGazeDial(args.save_every, out / "checkpoints", ledger, best_file, args.eval_episodes)]

    t0 = time.time()
    model.learn(total_timesteps=args.total_steps, progress_bar=False, reset_num_timesteps=True,
                callback=cbs)
    model.save(str(out / "final_model"))
    print(f"\n  done in {(time.time()-t0)/60:.1f} min -> {out}/final_model.zip")
    if os.path.exists(best_file):
        print("  BEST (by acquisition-stress):")
        print("   ", open(best_file).read().strip().replace("\n", "\n    "))


if __name__ == "__main__":
    main()
