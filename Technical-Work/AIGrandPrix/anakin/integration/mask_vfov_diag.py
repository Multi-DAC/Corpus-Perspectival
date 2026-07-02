"""mask_vfov_diag.py — is the official->training domain gap GEOMETRIC (tilt/vertical), not appearance? (Day 135)

The mask FALSIFY + color-match + 10x coverage drop point at GEOMETRY. to_training_frame places
official content in rows 14:50 (1/10 scale + 14px pad top/bottom). The dreamer_pilot docstring claims
training renders 20deg DOWN-tilt while the official camera is 20deg UP (Mirror #32) — a potential 40deg
vertical mismatch that would push official gates to a DIFFERENT row band than training expects. Don't
trust the docstring (Mirror #33) — MEASURE: compare the vertical (row) distribution of gate pixels in
official vs rendered policy-views, both via their real transforms.

  - official: holdout_gate_v2.load_official_frames(raw=True)  [to_training_frame 64x64]
  - rendered: holdout_gate_v2.render_restyled_frames()        [render() 64x64]
  - gate pixels = same keep-rule; report mean row + row histogram + content-band occupancy.

If official gate-rows sit systematically higher/lower than rendered (or pile at the row-14 band edge),
the gap is GEOMETRIC (tilt) — fix is the camera transform, NOT masking/color/randomization.
Run:  .venv/Scripts/python.exe integration/mask_vfov_diag.py
"""
import os
os.environ["ANAKIN_GATE_MASK"] = "0"  # unmasked; we find gate pixels ourselves
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ANAKIN = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ANAKIN)

from sim.gate_mask import R_MIN, RATIO  # noqa: E402
from holdout_gate_v2 import load_official_frames, render_restyled_frames  # noqa: E402

HARVEST = (r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364"
           r"\PyAIPilotExample\official_frames\manual_20260614_114130")
CONTENT_TOP, CONTENT_BOT = 14, 50  # to_training_frame pad rows: content lives in [14:50]


def keep_mask(a):
    a = a.astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > R_MIN) & (r * 100 > RATIO * 100 * g) & (r * 100 > RATIO * 100 * b)


def row_profile(name, frames):
    frames = np.asarray(frames)
    m = keep_mask(frames)                       # [N,64,64] bool
    rows = np.where(m)[1] if m.any() else np.array([])  # row index of every kept pixel
    print(f"\n[{name}]  frames={len(frames)}  kept_px={m.sum()}  cov={m.mean()*100:.3f}%")
    if len(rows) == 0:
        print("  (no gate pixels)"); return None
    print(f"  gate-pixel ROW: mean={rows.mean():.1f}  median={np.median(rows):.0f}  "
          f"p10={np.percentile(rows,10):.0f}  p90={np.percentile(rows,90):.0f}  "
          f"(content band = rows {CONTENT_TOP}:{CONTENT_BOT}, center={CONTENT_TOP+(CONTENT_BOT-CONTENT_TOP)/2:.0f})")
    in_band = ((rows >= CONTENT_TOP) & (rows < CONTENT_BOT)).mean()
    print(f"  fraction of gate pixels inside content band: {in_band*100:.1f}%")
    # coarse 8-bin histogram across the 64 rows
    hist, edges = np.histogram(rows, bins=8, range=(0, 64))
    bars = "  ".join(f"{int(edges[i])}-{int(edges[i+1])}:{hist[i]}" for i in range(8))
    print(f"  row hist (8 bins): {bars}")
    return rows.mean()


def main():
    print(f"R_MIN={R_MIN} RATIO={RATIO}  content band rows [{CONTENT_TOP}:{CONTENT_BOT}]")
    official = load_official_frames(HARVEST, raw=True, cap=400)
    idx = np.linspace(0, len(official) - 1, min(80, len(official))).astype(int)
    mo = row_profile("OFFICIAL (to_training_frame)", official[idx])
    mr = row_profile("RENDERED (render())", render_restyled_frames(n=80))

    print("\n--- VERDICT ---")
    if mo is not None and mr is not None:
        d = mo - mr
        print(f"  mean gate-row: official={mo:.1f}  rendered={mr:.1f}  delta={d:+.1f} rows")
        deg_per_row = 59.0 / (CONTENT_BOT - CONTENT_TOP)  # official VFOV 59deg over 36 content rows
        print(f"  => ~{abs(d)*deg_per_row:.1f} deg vertical offset (1 row ~ {deg_per_row:.1f} deg)")
        if abs(d) >= 4:
            print("  GEOMETRIC mismatch CONFIRMED: official gates sit in a different row band than")
            print("  rendered -> the domain gap is camera tilt/vertical, NOT appearance. Fix = correct")
            print("  the tilt in render.py or the pad-offset in to_training_frame; masking/color/random")
            print("  CANNOT fix a vertical-registration gap. (Ties Mirror #32 tilt-sign.)")
        else:
            print("  No major vertical mismatch (<4 rows). Gates co-located; the gap is NOT tilt.")
            print("  The 10x coverage drop is then correct angular shrinkage (official gates genuinely")
            print("  small at true 1/10 scale) -> sparsity is real; route = don't-mask / randomize.")


if __name__ == "__main__":
    main()
