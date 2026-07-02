"""Translation-exam rehearsal: best.pt through the FULL competition adapter path,
closed-loop against our own sim (sim-to-sim, before the official VQ-sim exists locally).

Two paired conditions on IDENTICAL episode sequences (same env seed per episode):

  direct    : sim 64x64 frame -> agent                (training-eval interface; sanity anchor)
  roundtrip : sim 64x64 -> synthetic competition feed -> DreamerPilot.act -> action
              The synthetic feed inverts to_training_frame: crop the 36 rows the
              competition camera's ~59deg VFOV would see (rows 14:50), upscale x10
              to 640x360, RGB->BGR. So `roundtrip - direct` isolates the real
              translation cost: narrower vertical FoV + resample losses.

What this CANNOT test (live-checklist items, see dreamer_pilot.py docstring):
camera tilt sign vs the official sim, body-frame handedness, thrust calibration.

Usage:
    .venv/Scripts/python.exe integration/translation_rehearsal.py --episodes 10
"""

import argparse
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from dreamer_pilot import DreamerPilot, IMG, FEED_W, FEED_H  # noqa: E402


def to_competition_feed(img64: np.ndarray) -> np.ndarray:
    """Inverse of to_training_frame: what the competition camera would have shown.
    Crop the central 36 rows (the 59deg VFOV band), upscale x10, RGB->BGR."""
    import cv2

    band = img64[(IMG - 36) // 2:(IMG - 36) // 2 + 36]          # 36x64x3
    big = cv2.resize(band, (FEED_W, FEED_H), interpolation=cv2.INTER_LINEAR)
    return cv2.cvtColor(big, cv2.COLOR_RGB2BGR)


def band_only(img64: np.ndarray) -> np.ndarray:
    """Ablation: the VFoV crop alone — gray out the rows the competition camera
    can't see, but keep the native 64x64 pixels (no resampling)."""
    from dreamer_pilot import BG_UINT8

    out = img64.copy()
    top = (IMG - 36) // 2
    out[:top] = BG_UINT8
    out[top + 36:] = BG_UINT8
    return out


def blur_only(img64: np.ndarray) -> np.ndarray:
    """Ablation: the resample round-trip alone — full frame up x10 and back,
    no FoV loss."""
    import cv2

    big = cv2.resize(img64, (IMG * 10, IMG * 10), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(big, (IMG, IMG), interpolation=cv2.INTER_AREA)


def band_resampled(img64: np.ndarray) -> np.ndarray:
    """Ablation (added 2026-06-17): the band content put through the EXACT roundtrip
    resample (36 -> 360 up, INTER_LINEAR; -> 36 down, INTER_AREA) with gray margins,
    fed via act_training_frame. Isolates the band-resample blur from the rest of the
    act() path (color round-trip is a no-op; this skips any _gm/_ef content transform).
    Discriminator: band_resampled ~ roundtrip  => the resample is the -47% killer;
                   band_resampled ~ band_only   => the resample is innocent, look in act()."""
    import cv2
    from dreamer_pilot import BG_UINT8

    top = (IMG - 36) // 2
    band = img64[top:top + 36]                                              # 36x64 native band
    big = cv2.resize(band, (FEED_W, FEED_H), interpolation=cv2.INTER_LINEAR)  # 36->360, 64->640
    small = cv2.resize(big, (IMG, FEED_H * IMG // FEED_W),
                       interpolation=cv2.INTER_AREA)                        # -> 64x36 (exact to_training_frame)
    out = np.full((IMG, IMG, 3), BG_UINT8, dtype=np.uint8)
    out[top:top + small.shape[0]] = small
    return out


def run_episodes(pilot, condition, seeds, max_steps, device):
    sys.path.insert(0, str(_HERE.parent / "sim"))
    from maneuver_env import AnakinManeuverEnv as ManeuverEnv
    from dynamics import imu_from_state  # training-frame IMU [gyro3 rad/s, accel3 m/s^2], body
    import torch

    use_imu = getattr(pilot, "_use_imu", False)

    def _imu(env, action_np):
        # IMU that pairs with the CURRENT obs: from env's live state + the action that produced it,
        # exactly as the batched training env builds obs["imu"] (noise-free for a clean gate).
        if not use_imu:
            return None
        a = torch.as_tensor(action_np, dtype=torch.float32, device=env._state.device).reshape(1, -1)
        return imu_from_state(env._state, a, noise_std=0.0)[0].detach().cpu().numpy()

    returns, gates = [], []
    for seed in seeds:
        env = ManeuverEnv(max_steps=max_steps, device=device, seed=seed)
        obs, _ = env.reset(seed=seed)
        pilot.reset()
        imu = _imu(env, np.zeros(4, dtype=np.float32))   # is_first frame (no prior action)
        ep_ret, t = 0.0, 0
        while True:
            if condition == "direct":
                action = pilot.act_training_frame(obs, imu=imu)
            elif condition == "band":
                action = pilot.act_training_frame(band_only(obs), imu=imu)
            elif condition == "blur":
                action = pilot.act_training_frame(blur_only(obs), imu=imu)
            elif condition == "band_resampled":
                action = pilot.act_training_frame(band_resampled(obs), imu=imu)
            else:
                action = pilot.act(to_competition_feed(obs), imu=imu)
            obs, r, term, trunc, info = env.step(action)
            imu = _imu(env, action)          # pair IMU with the new obs
            ep_ret += float(r)
            t += 1
            if term or trunc:
                break
        returns.append(ep_ret)
        gates.append(int(info.get("gates_passed", env._cur)))
        print(f"  [{condition}] seed={seed}  return={ep_ret:+8.2f}  "
              f"gates={gates[-1]}  steps={t}", flush=True)
    return np.array(returns), np.array(gates)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=str(
        _HERE.parent / "third_party" / "dreamerv3-torch" / "logdir" /
        "maneuver_scale_2" / "best.pt"))
    ap.add_argument("--episodes", type=int, default=10)
    ap.add_argument("--max-steps", type=int, default=1200)
    ap.add_argument("--env-device", default="cuda")
    ap.add_argument("--imu", action="store_true",
                    help="build the IMU encoder (anakin_imu checkpoints, e.g. maneuver_imu_stability)")
    args = ap.parse_args()

    configs = ("anakin_maneuver", "anakin_imu") if args.imu else ("anakin_maneuver",)
    pilot = DreamerPilot(args.checkpoint, configs=configs)
    seeds = list(range(1000, 1000 + args.episodes))

    results = {}
    for cond in ["direct", "band", "blur", "band_resampled", "roundtrip"]:
        print(f"\n=== {cond} ({args.episodes} eps) ===", flush=True)
        results[cond] = run_episodes(pilot, cond, seeds, args.max_steps, args.env_device)

    print("\n=== TRANSLATION REHEARSAL SUMMARY ===")
    print("(direct = training-eval anchor; band = VFoV crop only; blur = resample only; "
          "roundtrip = full adapter path. Training-run best batch metric: +256.28)")
    base = results["direct"][0].mean()
    for cond in ["direct", "band", "blur", "band_resampled", "roundtrip"]:
        r, g = results[cond]
        rel = (r.mean() - base) / abs(base) * 100 if base else float("nan")
        print(f"{cond:9s}: return {r.mean():+8.2f} +/- {r.std():6.2f}   "
              f"gates {g.mean():5.1f}   delta-vs-direct {rel:+6.1f}%")


if __name__ == "__main__":
    main()
