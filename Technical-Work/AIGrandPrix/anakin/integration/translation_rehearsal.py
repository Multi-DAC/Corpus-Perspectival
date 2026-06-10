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


def run_episodes(pilot, condition, seeds, max_steps, device):
    sys.path.insert(0, str(_HERE.parent / "sim"))
    from maneuver_env import AnakinManeuverEnv as ManeuverEnv

    returns, gates = [], []
    for seed in seeds:
        env = ManeuverEnv(max_steps=max_steps, device=device, seed=seed)
        obs, _ = env.reset(seed=seed)
        pilot.reset()
        ep_ret, t = 0.0, 0
        while True:
            if condition == "direct":
                action = pilot.act_training_frame(obs)
            elif condition == "band":
                action = pilot.act_training_frame(band_only(obs))
            elif condition == "blur":
                action = pilot.act_training_frame(blur_only(obs))
            else:
                action = pilot.act(to_competition_feed(obs))
            obs, r, term, trunc, info = env.step(action)
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
    args = ap.parse_args()

    pilot = DreamerPilot(args.checkpoint)
    seeds = list(range(1000, 1000 + args.episodes))

    results = {}
    for cond in ["direct", "band", "blur", "roundtrip"]:
        print(f"\n=== {cond} ({args.episodes} eps) ===", flush=True)
        results[cond] = run_episodes(pilot, cond, seeds, args.max_steps, args.env_device)

    print("\n=== TRANSLATION REHEARSAL SUMMARY ===")
    print("(direct = training-eval anchor; band = VFoV crop only; blur = resample only; "
          "roundtrip = full adapter path. Training-run best batch metric: +256.28)")
    base = results["direct"][0].mean()
    for cond in ["direct", "band", "blur", "roundtrip"]:
        r, g = results[cond]
        rel = (r.mean() - base) / abs(base) * 100 if base else float("nan")
        print(f"{cond:9s}: return {r.mean():+8.2f} +/- {r.std():6.2f}   "
              f"gates {g.mean():5.1f}   delta-vs-direct {rel:+6.1f}%")


if __name__ == "__main__":
    main()
