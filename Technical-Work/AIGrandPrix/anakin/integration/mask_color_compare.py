"""mask_color_compare.py — APPLES-TO-APPLES gate-color check (Day 135, confound fix).

mask_coverage_diag.py compared official kept-pixel centroid (post-selection) to the renderer's
BASE constant GATE_BRIGHT (pre-selection) — confounded, because the keep-rule (R>1.55*{G,B}) itself
biases toward low G,B. This applies the SAME pipeline + SAME rule to BOTH domains and compares
kept-pixel centroids directly:
  - official: holdout_gate_v2.load_official_frames(raw=True)  [the exact to_training_frame 64x64 view]
  - rendered: holdout_gate_v2.render_restyled_frames()        [the exact render() 64x64 view]
  - frames UNMASKED (ANAKIN_GATE_MASK=0) so we read true gate color; we apply the keep-rule ourselves.

If rendered kept-centroid B is far above official's (~24) -> real color mismatch (conclusion stands).
If rendered kept-centroid B ~ official's -> the apparent mismatch was selection-rule bias -> WALK BACK.
Run:  .venv/Scripts/python.exe integration/mask_color_compare.py
"""
import os
os.environ["ANAKIN_GATE_MASK"] = "0"  # we want UNMASKED frames; we apply the rule ourselves
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ANAKIN = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ANAKIN)

from sim.gate_mask import R_MIN, RATIO  # noqa: E402
from holdout_gate_v2 import load_official_frames, render_restyled_frames  # noqa: E402

GATE_BRIGHT_255 = (229, 92, 79)  # render.py:54 GATE_BRIGHT=(0.90,0.36,0.31), for reference only

HARVEST = (r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364"
           r"\PyAIPilotExample\official_frames\manual_20260614_114130")


def keep_mask(a):
    a = a.astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > R_MIN) & (r * 100 > RATIO * 100 * g) & (r * 100 > RATIO * 100 * b)


def summarize(name, frames):
    frames = np.asarray(frames)
    m = keep_mask(frames)
    cov = m.reshape(len(frames), -1).mean(axis=1)
    kept = frames[m]
    print(f"\n[{name}]  frames={len(frames)}  shape={frames.shape[1:]}")
    print(f"  coverage %: mean={cov.mean()*100:.3f} median={np.median(cov)*100:.3f} "
          f"p90={np.percentile(cov,90)*100:.3f}")
    if len(kept):
        c = kept.mean(axis=0)
        print(f"  KEPT-pixel centroid: ({c[0]:.0f}, {c[1]:.0f}, {c[2]:.0f})  "
              f"R/G={c[0]/max(c[1],1):.2f} R/B={c[0]/max(c[2],1):.2f}")
        return c
    print("  (no kept pixels)")
    return None


def main():
    n = 60
    print(f"R_MIN={R_MIN} RATIO={RATIO}  GATE_BRIGHT base (render.py:54) = {GATE_BRIGHT_255}")
    official = load_official_frames(HARVEST, raw=True, cap=400)
    # evenly subsample official to n
    idx = np.linspace(0, len(official) - 1, min(n, len(official))).astype(int)
    co = summarize("OFFICIAL (to_training_frame, unmasked)", official[idx])
    rendered = render_restyled_frames(n=n)
    cr = summarize("RENDERED (render(), unmasked)", rendered)

    print("\n--- VERDICT ---")
    if co is not None and cr is not None:
        db = abs(co[2] - cr[2]); dg = abs(co[1] - cr[1]); dr = abs(co[0] - cr[0])
        print(f"  centroid delta (official - rendered): "
              f"dR={co[0]-cr[0]:+.0f} dG={co[1]-cr[1]:+.0f} dB={co[2]-cr[2]:+.0f}")
        if db > 25 or dg > 25:
            print("  => REAL color mismatch survives the apples-to-apples test (conclusion STANDS).")
        else:
            print("  => mismatch DISSOLVES under same-rule comparison; the apparent gap was selection")
            print("     bias. WALK BACK the 'color mismatch root cause' claim. The FALSIFY mechanism")
            print("     is something else (re-open: blank-frame distribution? encoder-overfit after all?).")


if __name__ == "__main__":
    main()
