"""
gaze_eval.py — does the policy LOOK at the gate, and how much does it lean on the dead-reckon crutch?

Built 2026-06-03 Day 123 morning drive to TEST the predictions in
COVERAGE_ACQUISITION_TENSION_2026-06-03.md on EXISTING checkpoints — CPU only, no retrain.

Two instruments (the legibility metrics P224 flagged as CPU-runnable pre-work):
  gaze_score   = mean over steps of cos< cam_axis_world , bearing-to-current-target-gate >.
                 +1 = camera pointed straight at the gate; < cos(45deg)=0.707 => gate is OUTSIDE the FoV cone.
  in_view%     = fraction of steps the current target gate sits inside the ~90deg FoV cone.
  acquisition-stress = re-run with max_reckon_steps=2 (odometry crutch nearly removed). A policy that
                 flies by LOOKING holds up; one that leans on unbounded dead-reckon collapses toward the
                 detection-only cliff.

Geometry is GROUND TRUTH (env.gates[current] - pos, true quat), not the noisy detector estimate — this
measures where the nose ACTUALLY points vs where the gate ACTUALLY is. Harness mirrors nose_axis_test.run
exactly (same env flags, ALL_W3 error model, deterministic) so gates/ep stays comparable to its refs:
    frozen Anakin +x+20tilt deploy reckon = 1.42-1.96 | clean omniscient ceiling = 4.83 | no-reckon cliff ~0.08
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "rl"))
from infinite_gate_env import InfiniteGateEnv
from perception_deadreckon import DeadReckonPerceptionObsWrapper
from drone_env_v2 import quat_rotate_np
from stable_baselines3 import PPO

TEACHER = os.path.join(HERE, "runs", "infinite_1771556763", "checkpoints",
                       "ppo_infinite_80000000_steps.zip")
RUN = os.path.join(HERE, "runs", "vision_corrected_gaze1_1780465000")
TAKEOFF = 2.0
c20, s20 = np.cos(np.radians(20)), np.sin(np.radians(20))
CAM = [c20, 0.0, s20]                       # +x nose +20deg up — deploy + training camera axis
FOV_HALF = 0.785                            # ~45deg cone half-angle; cos => in-view threshold
ALL_W3 = dict(range_sigma_frac=0.19, bearing_sigma_rad=0.018, dropout_prob=0.05,
              fov_halfangle_rad=0.785, max_range_m=28.0, latency_steps=2, next_gate_extra_dropout=0.5)


def run(model, cam=CAM, max_reckon_steps=None, episodes=12, max_steps=15000, seed=2026):
    env = InfiniteGateEnv(perception_obs=True, ground_start_prob=0.5,
                          domain_rand=True, adaptive_curriculum=True, seed=seed)
    env._obs_wrapper = DeadReckonPerceptionObsWrapper(
        env._ctbr, cam_axis_body=cam, deadreckon=True, max_reckon_steps=max_reckon_steps,
        randomize=False, seed=seed + 5)
    env.observation_space = env._obs_wrapper.observation_space
    env._obs_wrapper.error_model.update(ALL_W3); env._obs_wrapper.randomize = False
    base = env._base_env
    cam_b = np.asarray(cam, float); cam_b = cam_b / np.linalg.norm(cam_b)
    cos_fov = float(np.cos(FOV_HALF))
    gates, took, gaze_ep, inview_ep = [], 0, [], []
    for _ in range(episodes):
        obs, _ = env.reset(); done = False; L = 0; mh = -1e9; g = 0
        ep_cos, ep_in, ep_n = 0.0, 0, 0
        while not done and L < max_steps:
            act, _ = model.predict(obs, deterministic=True)
            obs, _r, term, trunc, info = env.step(act)
            L += 1; mh = max(mh, float(base.state[2])); g = max(g, int(info.get("gates_passed", 0)))
            cur = base.current_gate
            if cur < len(base.gates):
                st = base.state
                rel = np.asarray(base.gates[cur], float) - st[0:3]
                rn = float(np.linalg.norm(rel))
                if rn > 1e-6:
                    cam_w = quat_rotate_np(st[6:10], cam_b)
                    cw = cam_w / (np.linalg.norm(cam_w) + 1e-9)
                    c = float(np.dot(cw, rel / rn))
                    ep_cos += c; ep_in += (c > cos_fov); ep_n += 1
            done = term or trunc
        gates.append(g); took += (mh >= TAKEOFF)
        if ep_n > 0:
            gaze_ep.append(ep_cos / ep_n); inview_ep.append(100.0 * ep_in / ep_n)
    env.close()
    a = np.array(gates)
    gz = float(np.mean(gaze_ep)) if gaze_ep else float("nan")
    iv = float(np.mean(inview_ep)) if inview_ep else float("nan")
    return dict(gates=float(a.mean()), mx=int(a.max()), ge1=float((a >= 1).mean()*100),
                took=took, ep=episodes, gaze=gz, inview=iv)


def run_vn(ckpt, vecnorm_path, cam=CAM, max_reckon_steps=None, episodes=8, max_steps=15000, seed=2026):
    """Vecnorm-aware variant for VecNormalize-trained policies (the v3 batched navigators).
    Mirrors eval_teacher.py's load pattern (DummyVecEnv -> VecNormalize.load, training=False) but
    deploys through the perception wrapper so we can measure gaze + acquisition-stress. Obs shapes
    match because the v3 navigators are privileged-trained (perception_obs=False), same vector layout
    as the perception wrapper's output (confirmed: frozen Anakin, also privileged, runs here)."""
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
    def make():
        e = InfiniteGateEnv(perception_obs=True, ground_start_prob=0.5,
                            domain_rand=True, adaptive_curriculum=True, seed=seed)
        e._obs_wrapper = DeadReckonPerceptionObsWrapper(
            e._ctbr, cam_axis_body=cam, deadreckon=True, max_reckon_steps=max_reckon_steps,
            randomize=False, seed=seed + 5)
        e.observation_space = e._obs_wrapper.observation_space
        e._obs_wrapper.error_model.update(ALL_W3); e._obs_wrapper.randomize = False
        return e
    raw = DummyVecEnv([make])
    venv = VecNormalize.load(vecnorm_path, raw); venv.training = False; venv.norm_reward = False
    model = PPO.load(ckpt, device="cpu")
    base = venv.venv.envs[0]._base_env
    cam_b = np.asarray(cam, float); cam_b = cam_b / np.linalg.norm(cam_b)
    cos_fov = float(np.cos(FOV_HALF))
    gates, took, gaze_ep, inview_ep = [], 0, [], []
    for _ in range(episodes):
        obs = venv.reset(); done = [False]; L = 0; mh = -1e9; g = 0
        ep_cos, ep_in, ep_n = 0.0, 0, 0
        while not done[0] and L < max_steps:
            act, _ = model.predict(obs, deterministic=True)
            obs, _r, done, info = venv.step(act)
            L += 1; mh = max(mh, float(base.state[2])); g = max(g, int(info[0].get("gates_passed", 0)))
            cur = base.current_gate
            if cur < len(base.gates):
                st = base.state
                rel = np.asarray(base.gates[cur], float) - st[0:3]
                rn = float(np.linalg.norm(rel))
                if rn > 1e-6:
                    cam_w = quat_rotate_np(st[6:10], cam_b)
                    cw = cam_w / (np.linalg.norm(cam_w) + 1e-9)
                    c = float(np.dot(cw, rel / rn))
                    ep_cos += c; ep_in += (c > cos_fov); ep_n += 1
        gates.append(g); took += (mh >= TAKEOFF)
        if ep_n > 0:
            gaze_ep.append(ep_cos / ep_n); inview_ep.append(100.0 * ep_in / ep_n)
    venv.close()
    a = np.array(gates)
    gz = float(np.mean(gaze_ep)) if gaze_ep else float("nan")
    iv = float(np.mean(inview_ep)) if inview_ep else float("nan")
    return dict(gates=float(a.mean()), mx=int(a.max()), ge1=float((a >= 1).mean()*100),
                took=took, ep=episodes, gaze=gz, inview=iv)


CKPTS = [
    ("frozen Anakin", TEACHER),
    ("gaze1 500k", os.path.join(RUN, "checkpoints", "vc_500000_steps.zip")),
    ("gaze1 final", os.path.join(RUN, "final_model.zip")),
]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=12)
    ap.add_argument("--max-steps", type=int, default=15000)
    ap.add_argument("--reckon", type=str, default="inf,2",
                    help="comma-sep max_reckon_steps values; 'inf'=None=unbounded. "
                         "e.g. 'inf,2,5,10,20' traces the coverage-acquisition curve")
    ap.add_argument("--ckpt", type=str, default=None, help="eval a single arbitrary checkpoint path")
    ap.add_argument("--vecnorm", type=str, default=None,
                    help="vec_normalize.pkl for the ckpt (REQUIRED if the policy was vecnorm-trained, "
                         "e.g. the v3 batched navigators); omit for raw policies like frozen Anakin")
    ap.add_argument("--label", type=str, default="ckpt")
    ap.add_argument("--smoke", action="store_true", help="n=1, single ckpt, short — correctness check")
    args = ap.parse_args()
    reckons = [None if t.strip().lower() in ("inf", "none") else int(t) for t in args.reckon.split(",")]

    if args.smoke:
        print("SMOKE: frozen Anakin, reckon=None, n=1, max_steps=2500", flush=True)
        m = PPO.load(TEACHER, device="cpu")
        r = run(m, max_reckon_steps=None, episodes=1, max_steps=2500)
        print(f"  gates={r['gates']:.2f} gaze={r['gaze']:.3f} inview={r['inview']:.0f}% "
              f"took={r['took']}/{r['ep']}", flush=True)
        return

    if args.ckpt:
        vn = bool(args.vecnorm)
        print(f"GAZE + ACQUISITION-STRESS — single ckpt: {args.label} "
              f"(vecnorm={'ON' if vn else 'OFF'}, +x+20tilt cam, all-W3, n={args.episodes})", flush=True)
        print(f"  refs: frozen deploy=1.42-2.0 | omniscient-ceiling=4.83 | no-reckon cliff~0.08", flush=True)
        print(f"  {'reckon':>6} {'gates/ep':>9} {'max':>4} {'gaze':>6} {'inview%':>8} {'takeoff':>8}", flush=True)
        t0 = time.time()
        for mrs in reckons:
            if vn:
                r = run_vn(args.ckpt, args.vecnorm, max_reckon_steps=mrs,
                           episodes=args.episodes, max_steps=args.max_steps)
            else:
                r = run(PPO.load(args.ckpt, device="cpu"), max_reckon_steps=mrs,
                        episodes=args.episodes, max_steps=args.max_steps)
            tag = "inf" if mrs is None else str(mrs)
            print(f"  {tag:>6} {r['gates']:>9.2f} {r['mx']:>4d} {r['gaze']:>6.3f} "
                  f"{r['inview']:>7.0f}% {r['took']:>4d}/{r['ep']:<3d}", flush=True)
        print(f"\n  done in {(time.time()-t0)/60:.1f} min", flush=True)
        return

    print(f"GAZE + ACQUISITION-STRESS EVAL  (+x+20tilt cam, all-W3, n={args.episodes})", flush=True)
    print(f"  refs: frozen deploy=1.42-1.96 | ceiling=4.83 | no-reckon cliff~0.08", flush=True)
    print(f"  PREDICT: gaze1 gaze-score ~= frozen (fine-tune taught no looking);", flush=True)
    print(f"           reckon=2 collapses BOTH toward cliff (flight carried by odometry, not gaze)\n", flush=True)
    hdr = f"  {'checkpoint':>16} {'reckon':>6} {'gates/ep':>9} {'max':>4} {'gaze':>6} {'inview%':>8} {'takeoff':>8}"
    print(hdr, flush=True)
    t0 = time.time()
    for label, path in CKPTS:
        if not os.path.exists(path):
            print(f"  {label:>16}  MISSING {path}", flush=True); continue
        model = PPO.load(path, device="cpu")
        for mrs in reckons:
            r = run(model, max_reckon_steps=mrs, episodes=args.episodes, max_steps=args.max_steps)
            tag = "inf" if mrs is None else str(mrs)
            print(f"  {label:>16} {tag:>6} {r['gates']:>9.2f} {r['mx']:>4d} {r['gaze']:>6.3f} "
                  f"{r['inview']:>7.0f}% {r['took']:>4d}/{r['ep']:<3d}", flush=True)
    print(f"\n  done in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
