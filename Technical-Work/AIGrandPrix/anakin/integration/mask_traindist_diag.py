"""mask_traindist_diag.py — the CLEAN confound-free test (Day 135): official vs ACTUAL TRAINING obs.

Every prior official-comparison used render_restyled_frames' synthetic wide-pose sampling = the WRONG
reference (confounds coverage + vertical position). This uses the real thing: saved training episodes
from the 10M-step scale run (maneuver_scale_2/train_eps/*.npz, unmasked render() obs at the true
training pose distribution). Question: does the official domain genuinely differ from what the policy
TRAINED on (not from synthetic poses)?

Rigor: official frames (via to_training_frame) are padded — content in rows [14:50] = 59deg VFOV;
training render() frames are full 64 rows = 90deg VFOV. Raw row indices conflate padding/FOV with real
elevation, so we convert row -> angular ELEVATION per each domain's own VFOV (shared 20deg up-tilt
cancels). Report coverage (distance/approach signal) + gate angular elevation (geometric registration).

Run:  .venv/Scripts/python.exe integration/mask_traindist_diag.py
"""
import os
os.environ["ANAKIN_GATE_MASK"] = "0"
import sys
import glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ANAKIN = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ANAKIN)
from sim.gate_mask import R_MIN, RATIO  # noqa: E402
from holdout_gate_v2 import load_official_frames  # noqa: E402

# Default official source = the (biased, human-flown) manual harvest. After flight #3, point this at
# the runner's flight_frames/ (on-line policy-view PNGs = the UNBIASED official reference) via:
#   ANAKIN_OFFICIAL_DIR="...\PyAIPilotExample\flight_frames" ANAKIN_OFFICIAL_RAW=0  (policyviews are 64x64)
HARVEST = os.environ.get("ANAKIN_OFFICIAL_DIR",
                         r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364"
                         r"\PyAIPilotExample\official_frames\manual_20260614_114130")
OFFICIAL_RAW = os.environ.get("ANAKIN_OFFICIAL_RAW", "1") == "1"
# NOTE (Day 135): scale_2 + band_ft predate the Day-131 orange-red restyle (their gates are the OLD
# gray/blue-white color -> 0% match the current rule). The valid post-restyle reference is restyle_ft
# (orange-red, unmasked, real training poses). This is itself the headline finding: the 10M-step
# backbone trained on a DIFFERENT gate color than the official sim uses.
TRAIN_EPS = os.path.join(ANAKIN, "third_party", "dreamerv3-torch", "logdir",
                         os.environ.get("ANAKIN_TRAIN_REF", "maneuver_restyle_ft"), "train_eps")

OFF_VFOV, OFF_TOP, OFF_BOT = 59.0, 14, 50   # official content band + its VFOV
TRAIN_VFOV = 90.0                            # render() full-frame VFOV


def keep_mask(a):
    a = a.astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > R_MIN) & (r * 100 > RATIO * 100 * g) & (r * 100 > RATIO * 100 * b)


def load_train_frames(n=80, per_ep=10):
    files = sorted(glob.glob(os.path.join(TRAIN_EPS, "*.npz")))
    assert files, f"no train eps in {TRAIN_EPS}"
    # sample episodes spread across the run
    idx = np.linspace(0, len(files) - 1, max(1, n // per_ep)).astype(int)
    frames = []
    key = None
    for i in idx:
        d = np.load(files[i])
        if key is None:
            key = "image" if "image" in d.files else [k for k in d.files if d[k].ndim == 4][0]
            print(f"  (npz keys={d.files}; using '{key}', shape {d[key].shape})")
        img = d[key]  # [T,64,64,3] uint8
        t = np.linspace(0, len(img) - 1, min(per_ep, len(img))).astype(int)
        frames.append(img[t])
    return np.concatenate(frames)[:n]


def profile(name, frames, vfov, top, bot):
    frames = np.asarray(frames)
    m = keep_mask(frames)
    cov = m.mean()
    rows = np.where(m)[1] if m.any() else np.array([])
    print(f"\n[{name}]  frames={len(frames)}  kept_px={int(m.sum())}  cov={cov*100:.3f}%")
    if len(rows) == 0:
        print("  (no gate pixels)"); return None
    # row -> elevation: center of the content band is 0deg (level); +deg = up (lower row)
    center = (top + bot) / 2.0 if bot else 32.0
    span_rows = (bot - top) if bot else 64.0
    deg_per_row = vfov / span_rows
    elev = -(rows - center) * deg_per_row   # lower row (higher in image) -> +elevation
    print(f"  gate-pixel row: mean={rows.mean():.1f} median={np.median(rows):.0f}")
    print(f"  gate ANGULAR ELEVATION: mean={elev.mean():+.1f}deg  median={np.median(elev):+.1f}deg  "
          f"p10={np.percentile(elev,10):+.1f}  p90={np.percentile(elev,90):+.1f}  "
          f"(deg/row={deg_per_row:.2f})")
    return elev.mean()


def main():
    print(f"R_MIN={R_MIN} RATIO={RATIO}")
    print("OFFICIAL (to_training_frame, padded rows 14:50 = 59deg VFOV):")
    official = load_official_frames(HARVEST, raw=OFFICIAL_RAW, cap=400)
    oi = np.linspace(0, len(official) - 1, 80).astype(int)
    eo = profile("OFFICIAL", official[oi], OFF_VFOV, OFF_TOP, OFF_BOT)
    print("\nTRAINING (scale-run obs, full 64 rows = 90deg VFOV):")
    train = load_train_frames(n=80)
    et = profile("TRAINING (scale_2 obs)", train, TRAIN_VFOV, 0, 64)

    print("\n--- VERDICT ---")
    if eo is not None and et is not None:
        d = eo - et
        print(f"  gate mean ELEVATION: official={eo:+.1f}deg  training={et:+.1f}deg  delta={d:+.1f}deg")
        if abs(d) >= 6:
            print(f"  REAL geometric gap: official gates sit ~{abs(d):.0f}deg "
                  f"{'higher' if d>0 else 'lower'} than what the policy trained on. The policy looks")
            print("  where training put gates; official puts them elsewhere -> it misses. Fix = align the")
            print("  vertical registration (pad-offset in to_training_frame, or a pose/elevation prior),")
            print("  NOT masking/color. This is the official-vs-TRAINING gap (confound-free).")
        else:
            print("  Elevations MATCH (<6deg) -> no vertical-registration gap vs the real training dist.")
            print("  The mask FALSIFY is then NOT geometric: likely masking-small-gates-to-black is too")
            print("  aggressive (coverage starves the encoder), or it's an encoder-capacity issue.")
            print("  Compare coverage: if official cov << training cov, gates are just smaller/farther in")
            print("  the official flight -> masking leaves official obs near-blank.")


if __name__ == "__main__":
    main()
