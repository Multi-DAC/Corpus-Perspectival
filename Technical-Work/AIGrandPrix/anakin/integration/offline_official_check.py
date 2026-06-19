"""
Offline official-frame check — feed the REAL official frames captured during a live/dry flight
straight through a checkpoint and log the commanded rates. The cheap gate that replaces
guess-and-fly: if the policy saturates roll (~-15) on these frames, it's appearance-OOD;
after an appearance-DR fine-tune, re-run the SAME frames and check the saturation clears.

Usage (anakin venv):
  PY integration/offline_official_check.py --ckpt <best.pt> --tag 112559
  (tag = the run_tag prefix of the saved frames in integration/flight_frames/)
"""
import os, sys, glob, argparse
import numpy as np
import cv2

ANAKIN = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin"
sys.path.insert(0, os.path.join(ANAKIN, "integration"))
from dreamer_pilot import DreamerPilot, to_competition_action  # noqa: E402

FRAME_DIR = os.path.join(ANAKIN, "integration", "flight_frames")
DEFAULT_CKPT = os.path.join(ANAKIN, "third_party", "dreamerv3-torch", "logdir", "maneuver_rate_ft", "best.pt")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=DEFAULT_CKPT)
    ap.add_argument("--tag", default="112559", help="run_tag prefix of saved raw frames")
    args = ap.parse_args()

    raws = sorted(glob.glob(os.path.join(FRAME_DIR, f"{args.tag}_s*_raw.jpg")))
    if not raws:
        print(f"NO frames for tag {args.tag} in {FRAME_DIR}"); return
    print(f"Loading pilot from {os.path.basename(os.path.dirname(args.ckpt))}/best.pt ...", flush=True)
    pilot = DreamerPilot(args.ckpt)
    print(f"Replaying {len(raws)} official frames (stateful, in order)...\n", flush=True)

    OMEGA_XY = 15.0
    rolls, pitches, yaws, thrs = [], [], [], []
    for i, f in enumerate(raws):
        img = cv2.imread(f)            # BGR 640x360 (the official feed)
        a = pilot.act(img)            # stateful RSSM
        ca = to_competition_action(a)
        rolls.append(ca.roll_rate_rad_s); pitches.append(ca.pitch_rate_rad_s)
        yaws.append(ca.yaw_rate_rad_s); thrs.append(ca.throttle)
        if i % 10 == 0:
            print(f"  f{i:3d} thr={ca.throttle:.2f} r/p/y=({ca.roll_rate_rad_s:+6.2f},"
                  f"{ca.pitch_rate_rad_s:+6.2f},{ca.yaw_rate_rad_s:+5.2f})", flush=True)

    r = np.array(rolls)
    sat = np.mean(np.abs(r) > 0.95 * OMEGA_XY)     # fraction roll-saturated
    print("\n=== SUMMARY ===")
    print(f"frames={len(r)}")
    print(f"roll:  mean={r.mean():+.2f}  std={r.std():.2f}  |roll|>14 (saturated) = {100*sat:.0f}% of frames")
    print(f"pitch: mean={np.mean(pitches):+.2f}  std={np.std(pitches):.2f}")
    print(f"yaw:   mean={np.mean(yaws):+.2f}  throttle mean={np.mean(thrs):.2f}")
    verdict = "APPEARANCE-OOD (roll saturated)" if sat > 0.4 else "looks sane (not saturating)"
    print(f"VERDICT: {verdict}")

if __name__ == "__main__":
    main()
