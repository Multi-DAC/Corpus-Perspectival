"""
Phase 2 67.5M gate-completion eval under training-matched configuration.

Motivation: G5 thrust probe ran with adaptive_curriculum=False, domain_rand=False
and saw zero gates across 10 episodes. That probe's job was thrust calibration,
not gate-completion claims — but it left an open question:

    Does Phase 2 67.5M actually clear gates under the configuration it was
    trained on (adaptive_curriculum=True, domain_rand=True with scale=0.15)?

This probe answers that. It is the gate that the perpetual-generalist + fork-
on-track-release strategy depends on. If the generalist cannot clear gates
under its training distribution, the strategy needs rework before VQ1 in May.

Outputs:
  - probes/phase2_67M_curriculum_eval.json — per-episode gate counts + planner stats
  - probes/phase2_67M_curriculum_eval.md   — human-readable summary
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "sim"))

from infinite_gate_env import InfiniteGateEnv  # noqa: E402
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

N_EPISODES = 30
MAX_STEPS_PER_EP = 30000  # 60s at 500 Hz — matches snapshots/.../eval_per_maneuver.py

OUT_JSON = BASE / "probes" / "phase2_67M_curriculum_eval.json"
OUT_MD = BASE / "probes" / "phase2_67M_curriculum_eval.md"


def make_env(seed):
    def _f():
        return InfiniteGateEnv(
            gate_radius=0.75,
            max_steps=MAX_STEPS_PER_EP,
            dt=0.002,
            substeps=1,
            domain_rand=True,
            domain_rand_scale=0.15,
            adaptive_curriculum=True,
            seed=seed,
        )
    return _f


def main():
    print(f"Loading policy: {POLICY.name}")
    print(f"Loading vecnorm: {VECNORM.name}")

    venv = DummyVecEnv([make_env(seed=42)])
    vecnorm = VecNormalize.load(str(VECNORM), venv)
    vecnorm.training = False
    vecnorm.norm_reward = False

    policy = PPO.load(str(POLICY), device="cpu")

    print()
    print("Eval config: curriculum=True, DR=True (scale=0.15), gate_radius=0.75")
    print(f"Episodes: {N_EPISODES} x up-to-{MAX_STEPS_PER_EP} steps")
    print()

    per_episode = []
    for ep in range(N_EPISODES):
        obs = vecnorm.reset()
        ep_steps = 0
        ep_gates = 0
        last_maneuver = None
        for step in range(MAX_STEPS_PER_EP):
            action, _ = policy.predict(obs, deterministic=True)
            obs, _, done, info = vecnorm.step(action)
            ep_steps += 1
            # Read gates_passed from info[0] BEFORE done triggers auto-reset.
            # episode_gates on the underlying env gets zeroed by reset().
            if "gates_passed" in info[0]:
                ep_gates = int(info[0]["gates_passed"])
            last_maneuver = venv.envs[0].current_maneuver
            if done[0]:
                break

        per_episode.append({
            "ep": ep,
            "steps": ep_steps,
            "gates": ep_gates,
            "current_maneuver": last_maneuver,
        })
        print(f"  ep {ep:2d}: {ep_steps:6d} steps, {ep_gates:3d} gates, "
              f"last maneuver={last_maneuver}")

    base = venv.envs[0]
    avg_mastery = base._get_avg_mastery() if hasattr(base, '_get_avg_mastery') else None
    planner_stats = base.sequence_planner.get_stats(avg_mastery=avg_mastery or 0.5)

    gates_arr = np.array([e["gates"] for e in per_episode])
    steps_arr = np.array([e["steps"] for e in per_episode])

    # Tier-segmented stats
    warmup = gates_arr[:10]            # planner inactive (warmup)
    early = gates_arr[10:25]           # planner active, mastery still settling
    mature = gates_arr[25:]            # planner fully exercised

    out = {
        "policy": str(POLICY.relative_to(BASE)),
        "vecnorm": str(VECNORM.relative_to(BASE)),
        "config": {
            "n_episodes": N_EPISODES,
            "max_steps_per_ep": MAX_STEPS_PER_EP,
            "gate_radius": 0.75,
            "dt": 0.002,
            "domain_rand": True,
            "domain_rand_scale": 0.15,
            "adaptive_curriculum": True,
        },
        "per_episode": per_episode,
        "stats": {
            "all": {
                "n": int(len(gates_arr)),
                "gates_mean": float(gates_arr.mean()),
                "gates_std": float(gates_arr.std()),
                "gates_min": int(gates_arr.min()),
                "gates_max": int(gates_arr.max()),
                "gates_p50": float(np.percentile(gates_arr, 50)),
                "episodes_with_zero_gates": int((gates_arr == 0).sum()),
                "episodes_with_at_least_one_gate": int((gates_arr >= 1).sum()),
                "episodes_with_at_least_five_gates": int((gates_arr >= 5).sum()),
                "steps_mean": float(steps_arr.mean()),
            },
            "warmup_eps_0_to_10": {
                "n": int(len(warmup)),
                "gates_mean": float(warmup.mean()),
                "gates_max": int(warmup.max()),
            },
            "early_eps_10_to_25": {
                "n": int(len(early)),
                "gates_mean": float(early.mean()),
                "gates_max": int(early.max()),
            },
            "mature_eps_25_plus": {
                "n": int(len(mature)),
                "gates_mean": float(mature.mean()),
                "gates_max": int(mature.max()),
            },
        },
        "final_avg_mastery": avg_mastery,
        "planner_stats": planner_stats,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {OUT_JSON.relative_to(BASE)}")
    _write_md(out)


def _write_md(out):
    s = out["stats"]
    cfg = out["config"]

    md = []
    md.append(f"# Phase 2 67.5M — Gate-Completion Eval (training-matched config)\n")
    md.append(f"**Run:** {out['timestamp']}  ")
    md.append(f"**Policy:** `{out['policy']}`  ")
    md.append(f"**VecNormalize:** `{out['vecnorm']}`  ")
    md.append(f"**Config:** curriculum={cfg['adaptive_curriculum']}, "
              f"DR={cfg['domain_rand']} (scale={cfg['domain_rand_scale']}), "
              f"gate_radius={cfg['gate_radius']}, dt={cfg['dt']}\n")

    md.append(f"## Why this eval\n")
    md.append(f"G5 thrust probe ran with curriculum=False, DR=False and saw "
              f"zero gates across 10 episodes — but that wasn't the training "
              f"configuration. This probe answers the question Phase 2's "
              f"perpetual-generalist + fork-on-track-release strategy depends "
              f"on: **does Phase 2 67.5M clear gates under its training "
              f"distribution?**\n")

    md.append(f"## Headline\n")
    a = s["all"]
    md.append(f"- Episodes run: **{a['n']}**")
    md.append(f"- Gates per episode: mean **{a['gates_mean']:.2f}**, "
              f"p50 {a['gates_p50']:.1f}, min {a['gates_min']}, max {a['gates_max']}")
    md.append(f"- Episodes with at least 1 gate: **{a['episodes_with_at_least_one_gate']}/{a['n']}**")
    md.append(f"- Episodes with at least 5 gates: **{a['episodes_with_at_least_five_gates']}/{a['n']}**")
    md.append(f"- Episodes with 0 gates: **{a['episodes_with_zero_gates']}/{a['n']}**")
    md.append(f"- Mean steps per episode: {a['steps_mean']:.0f}\n")

    md.append(f"## Curriculum tier segmentation\n")
    md.append(f"The adaptive curriculum needs warmup (>=10 episodes for planner "
              f"activation; >=50 for mastery to leave neutral default). Segmenting "
              f"shows whether early failures are warmup-mode or true policy gaps.\n")
    md.append(f"| stage | episodes | gates_mean | gates_max |")
    md.append(f"|---|---|---|---|")
    for key in ["warmup_eps_0_to_10", "early_eps_10_to_25", "mature_eps_25_plus"]:
        b = s[key]
        md.append(f"| {key} | {b['n']} | {b['gates_mean']:.2f} | {b['gates_max']} |")
    md.append("")

    md.append(f"## Final planner state\n")
    md.append(f"- Final avg mastery: **{out['final_avg_mastery']}**")
    md.append(f"- Total planner decisions: **{out['planner_stats']['total_decisions']}**")
    cd = out["planner_stats"].get("complexity_distribution", {})
    if cd:
        md.append(f"- Complexity distribution exercised:")
        for k, v in cd.items():
            md.append(f"  - {k}: {v:.2%}")
    md.append("")

    md.append(f"## Verdict\n")
    if a["gates_mean"] >= 5:
        md.append(f"**STRATEGY VALIDATED.** Phase 2 67.5M clears gates under "
                  f"training-matched config (mean {a['gates_mean']:.1f} gates/ep). "
                  f"The perpetual-generalist + fork-on-track-release plan has "
                  f"the foundation it needs. Specialization fork on VQ1 release "
                  f"can begin from this checkpoint.\n")
    elif a["gates_mean"] >= 1:
        md.append(f"**MIXED.** Phase 2 67.5M clears gates intermittently "
                  f"(mean {a['gates_mean']:.1f} gates/ep). Suggests the policy "
                  f"learned the basic skill but is fragile. Plan still viable "
                  f"but specialization fork should expect significant fine-tune "
                  f"effort. Consider extending Phase 2 training before forking.\n")
    else:
        md.append(f"**STRATEGY AT RISK.** Phase 2 67.5M does NOT reliably clear "
                  f"gates even under training-matched config. The 0-gate G5 finding "
                  f"is not a curriculum artifact — it is a real policy gap. "
                  f"Specialization fork from this checkpoint will not work. "
                  f"Action items: (a) inspect training reward curves for collapse, "
                  f"(b) verify VecNormalize stats are paired correctly, "
                  f"(c) consider regression to last known good checkpoint.\n")

    md.append(f"## Per-episode log\n")
    md.append(f"| ep | steps | gates | last maneuver |")
    md.append(f"|---|---|---|---|")
    for e in out["per_episode"]:
        md.append(f"| {e['ep']} | {e['steps']} | {e['gates']} | "
                  f"{e['current_maneuver']} |")
    md.append("")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(BASE)}")


if __name__ == "__main__":
    main()
