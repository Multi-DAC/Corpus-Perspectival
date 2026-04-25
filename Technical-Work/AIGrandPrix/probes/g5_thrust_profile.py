"""
G5 pre-staging — log Phase 2 67.5M policy's action[0] (collective thrust)
distribution in InfiniteGateEnv so we have a SITL-day calibration target.

The training env uses a TWR_max=3.3 quadrotor:
    collective_max = 4 * T_max = 4 * (0.85 * 9.81 * 3.3 / 4) ≈ 27.52 N
    hover_collective = m * g = 0.85 * 9.801 ≈ 8.33 N
    analytical hover throttle = hover/max ≈ 0.303

If the trained policy's *empirical* throttle distribution centers near
that analytical hover ratio, the mavsdk_client thrust mapping
(action[0] -> normalized [0,1] thrust) is correctly scaled — provided
PX4 interprets "1.0 = max collective" with the same ratio.

If PX4's max collective differs, we can read off the ratio here and
apply a THRUST_SCALE factor at SITL bring-up to match.

Outputs:
  - probes/g5_thrust_profile.json — all action[0] samples + hover-mode subset
  - probes/g5_thrust_profile_findings.md — human-readable summary
"""

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "sim"))

from infinite_gate_env import InfiniteGateEnv  # noqa: E402
from drone_env_v2 import QuadParams  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize  # noqa: E402

POLICY = (
    BASE / "sim" / "runs" / "infinite_v3_phase2_60M_1777095742"
    / "checkpoints" / "ppo_phase2_67500016_steps.zip"
)
VECNORM = (
    BASE / "sim" / "runs" / "infinite_v3_phase2_60M_1777095742"
    / "checkpoints" / "ppo_phase2_67500016_steps_vecnorm.pkl"
)

N_EPISODES = 10
MAX_STEPS_PER_EP = 5000  # 10s at 500 Hz — enough to see steady-state
HOVER_SPEED_THRESHOLD = 1.0  # m/s — count as "hover-like" if speed below this

OUT_JSON = BASE / "probes" / "g5_thrust_profile.json"
OUT_MD = BASE / "probes" / "g5_thrust_profile_findings.md"


def make_env(seed):
    def _f():
        env = InfiniteGateEnv(
            gate_radius=0.75,
            max_steps=MAX_STEPS_PER_EP,
            dt=0.002,
            substeps=1,
            domain_rand=False,  # match Phase 2 baseline DR=False for clean calibration
            adaptive_curriculum=False,
            seed=seed,
        )
        return env
    return _f


def write_markdown_only():
    """Skip the rollout, regenerate the markdown from the existing JSON."""
    out = json.loads(OUT_JSON.read_text())
    params = QuadParams()
    _write_md(out, params)


def main():
    if "--md-only" in sys.argv:
        write_markdown_only()
        return
    print(f"Loading policy: {POLICY.name}")
    print(f"Loading vecnorm: {VECNORM.name}")

    venv = DummyVecEnv([make_env(seed=42)])
    vecnorm = VecNormalize.load(str(VECNORM), venv)
    vecnorm.training = False
    vecnorm.norm_reward = False

    policy = PPO.load(str(POLICY), device="cpu")

    params = QuadParams()
    collective_max = 4 * params.T_max
    hover_collective = params.mass * params.g
    analytical_hover_ratio = hover_collective / collective_max
    analytical_a_hover = 2 * analytical_hover_ratio - 1

    print()
    print(f"Quadrotor params (training):")
    print(f"  mass={params.mass} kg, g={params.g}, TWR_max=3.3")
    print(f"  collective_max = {collective_max:.3f} N")
    print(f"  hover_collective = {hover_collective:.3f} N")
    print(f"  analytical hover ratio = {analytical_hover_ratio:.4f}")
    print(f"  analytical a_hover = {analytical_a_hover:.4f}")
    print()

    all_actions0 = []
    hover_actions0 = []
    speeds = []
    gates_passed = []

    for ep in range(N_EPISODES):
        obs = venv.reset()
        ep_actions = []
        ep_hover = []
        ep_gates = 0
        for step in range(MAX_STEPS_PER_EP):
            action, _ = policy.predict(obs, deterministic=True)
            obs, _, done, info = venv.step(action)
            a0 = float(action[0, 0])
            ep_actions.append(a0)

            # Read gates from info before done triggers DummyVecEnv auto-reset
            # (which zeros venv.envs[0].episode_gates). See Mirror #21.
            if "gates_passed" in info[0]:
                ep_gates = int(info[0]["gates_passed"])

            # Pull the underlying env state for hover-classification
            base = venv.envs[0]._base_env
            vel = base.state[3:6]
            speed = float(np.linalg.norm(vel))
            speeds.append(speed)
            if speed < HOVER_SPEED_THRESHOLD:
                ep_hover.append(a0)

            if done[0]:
                break

        all_actions0.extend(ep_actions)
        hover_actions0.extend(ep_hover)
        gates = ep_gates
        gates_passed.append(gates)
        print(f"  ep {ep}: {len(ep_actions)} steps, {gates} gates, "
              f"{len(ep_hover)} hover-like steps, "
              f"action[0] mean={np.mean(ep_actions):+.3f}")

    all_a = np.array(all_actions0)
    hover_a = np.array(hover_actions0) if hover_actions0 else np.array([np.nan])

    def stats(x):
        if len(x) == 0 or np.all(np.isnan(x)):
            return {"n": 0, "mean": None, "std": None,
                    "p10": None, "p50": None, "p90": None,
                    "throttle_mean": None}
        thr = (x + 1.0) * 0.5  # convert action[0] to throttle [0,1]
        return {
            "n": int(len(x)),
            "mean": float(np.mean(x)),
            "std": float(np.std(x)),
            "p10": float(np.percentile(x, 10)),
            "p50": float(np.percentile(x, 50)),
            "p90": float(np.percentile(x, 90)),
            "throttle_mean": float(np.mean(thr)),
            "throttle_p10": float(np.percentile(thr, 10)),
            "throttle_p50": float(np.percentile(thr, 50)),
            "throttle_p90": float(np.percentile(thr, 90)),
        }

    out = {
        "policy": str(POLICY.relative_to(BASE)),
        "vecnorm": str(VECNORM.relative_to(BASE)),
        "n_episodes": N_EPISODES,
        "max_steps_per_ep": MAX_STEPS_PER_EP,
        "hover_speed_threshold_m_s": HOVER_SPEED_THRESHOLD,
        "training_quadrotor": {
            "mass_kg": params.mass,
            "g": params.g,
            "TWR_max": 3.3,
            "collective_max_N": collective_max,
            "hover_collective_N": hover_collective,
            "analytical_hover_ratio": analytical_hover_ratio,
            "analytical_a_hover": analytical_a_hover,
        },
        "all_steps": stats(all_a),
        "hover_like_steps": stats(hover_a),
        "gates_per_episode": gates_passed,
        "mean_speed_m_s": float(np.mean(speeds)) if speeds else None,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    OUT_JSON.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {OUT_JSON.relative_to(BASE)}")
    _write_md(out, params)


def _write_md(out, params):
    gates_passed = out["gates_per_episode"]
    collective_max = out["training_quadrotor"]["collective_max_N"]
    hover_collective = out["training_quadrotor"]["hover_collective_N"]
    analytical_hover_ratio = out["training_quadrotor"]["analytical_hover_ratio"]
    analytical_a_hover = out["training_quadrotor"]["analytical_a_hover"]

    md = []
    md.append(f"# G5 Thrust Profile — Phase 2 67.5M (probe run {out['timestamp']})\n")
    md.append(f"**Policy:** `{out['policy']}`  ")
    md.append(f"**VecNormalize:** `{out['vecnorm']}`  ")
    md.append(f"**Episodes:** {N_EPISODES} x up-to-{MAX_STEPS_PER_EP} steps")
    md.append(f"  (DR off, curriculum off, gate_radius=0.75, dt=0.002)\n")

    md.append(f"## Analytical target (training quadrotor)\n")
    md.append(f"- mass = {params.mass} kg, g = {params.g}, TWR_max = 3.3")
    md.append(f"- collective_max = **{collective_max:.3f} N**")
    md.append(f"- hover_collective = m*g = **{hover_collective:.3f} N**")
    md.append(f"- analytical hover throttle = **{analytical_hover_ratio:.4f}** "
              f"(action[0] = {analytical_a_hover:+.4f})\n")

    md.append(f"## Empirical action[0] distribution\n")
    md.append(f"### All steps (n={out['all_steps']['n']})\n")
    md.append(f"| stat | action[0] | throttle [0,1] |")
    md.append(f"|---|---|---|")
    md.append(f"| mean | {out['all_steps']['mean']:+.4f} | {out['all_steps']['throttle_mean']:.4f} |")
    md.append(f"| p10  | {out['all_steps']['p10']:+.4f} | {out['all_steps']['throttle_p10']:.4f} |")
    md.append(f"| p50  | {out['all_steps']['p50']:+.4f} | {out['all_steps']['throttle_p50']:.4f} |")
    md.append(f"| p90  | {out['all_steps']['p90']:+.4f} | {out['all_steps']['throttle_p90']:.4f} |")
    md.append(f"| std  | {out['all_steps']['std']:.4f} | — |\n")

    if out['hover_like_steps']['n'] > 0:
        md.append(f"### Hover-like steps (speed < {HOVER_SPEED_THRESHOLD} m/s, "
                  f"n={out['hover_like_steps']['n']})\n")
        md.append(f"| stat | action[0] | throttle [0,1] |")
        md.append(f"|---|---|---|")
        md.append(f"| mean | {out['hover_like_steps']['mean']:+.4f} | {out['hover_like_steps']['throttle_mean']:.4f} |")
        md.append(f"| p10  | {out['hover_like_steps']['p10']:+.4f} | {out['hover_like_steps']['throttle_p10']:.4f} |")
        md.append(f"| p50  | {out['hover_like_steps']['p50']:+.4f} | {out['hover_like_steps']['throttle_p50']:.4f} |")
        md.append(f"| p90  | {out['hover_like_steps']['p90']:+.4f} | {out['hover_like_steps']['throttle_p90']:.4f} |")
        md.append(f"| std  | {out['hover_like_steps']['std']:.4f} | — |\n")
    else:
        md.append(f"### Hover-like steps: NONE found\n")
        md.append(f"Policy never dropped below {HOVER_SPEED_THRESHOLD} m/s — racing-only behavior.\n")
        md.append(f"Use the all-steps median as the calibration target instead.\n")

    md.append(f"## Gates per episode\n")
    md.append(f"`{gates_passed}` (mean = {np.mean(gates_passed):.1f})\n")

    if all(g == 0 for g in gates_passed):
        md.append(f"### NOTE: zero gates across all episodes\n")
        md.append(f"This probe runs with `adaptive_curriculum=False` and "
                  f"`domain_rand=False` for clean thrust calibration. The "
                  f"curriculum-off setting falls through to uniform-random "
                  f"maneuver selection, which can start the policy on "
                  f"hairpins/spirals from a cold init. This says nothing "
                  f"about Phase 2's gate-completion rate under the "
                  f"training-matched configuration (curriculum on, DR on).\n")
        md.append(f"**Action item:** rerun with `adaptive_curriculum=True` "
                  f"and `domain_rand=True` if we want to claim gate-completion "
                  f"behavior here. For now, this probe's only deliverable is "
                  f"the throttle distribution.\n")

    md.append(f"## SITL calibration recipe\n")
    md.append(f"At SITL bring-up, hover the drone in PX4 with offboard "
              f"sending action[0] = {analytical_a_hover:+.4f} (throttle = "
              f"{analytical_hover_ratio:.4f}).\n")
    md.append(f"- If PX4 holds altitude: thrust scaling matches; THRUST_SCALE = 1.0.")
    md.append(f"- If PX4 climbs: PX4's max collective < sim's. THRUST_SCALE > 1.0 "
              f"(send action[0] commanding *more* throttle to compensate).")
    md.append(f"- If PX4 falls: PX4's max collective > sim's. THRUST_SCALE < 1.0.\n")
    md.append(f"Compare empirical p50 throttle ({out['all_steps']['throttle_p50']:.4f}) "
              f"and hover-mode mean throttle to the in-flight observation.\n")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(BASE)}")


if __name__ == "__main__":
    main()
