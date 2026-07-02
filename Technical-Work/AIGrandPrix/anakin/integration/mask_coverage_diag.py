"""mask_coverage_diag.py — does the gate-isolation rule actually fire on OFFICIAL frames? (Day 135)

The overnight gate FALSIFIED the mask route (mean-term ratio 1.153). Leading hypothesis was
encoder-overfit (gate colors match per gate_mask.py docstring, so NOT a color mismatch). But that
was asserted from the docstring, never MEASURED. This measures it on the real official harvest:
  - coverage fraction (what % of pixels survive the gate rule) at NATIVE res and at 64x64 (what the
    encoder actually sees — downsampling can dilute a thin gate rim below the R>1.55*{G,B} ratio)
  - RGB centroid of kept pixels vs the design palette core (~229,93,78) — are official gates the
    orange-red the rule was tuned for?
  - # frames where the gate effectively vanishes (coverage < 0.2%) — the worst-case failure mode:
    masking blanks the gate itself on official frames.

Uses the EXACT gate_isolate_np from sim/gate_mask.py (no reimplementation -> no drift).
Run:  .venv/Scripts/python.exe integration/mask_coverage_diag.py
"""
import os
import sys
import glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ANAKIN = os.path.dirname(HERE)
sys.path.insert(0, ANAKIN)
from sim.gate_mask import gate_isolate_np, R_MIN, RATIO  # noqa: E402

HARVEST = (r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364"
           r"\PyAIPilotExample\official_frames\manual_20260614_114130")
N = 60  # evenly-spaced sample


def kept_mask(img_uint8):
    """Recompute the keep-boolean (gate_isolate zeroes; we also want the count)."""
    a = img_uint8.astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > R_MIN) & (r * 100 > RATIO * 100 * g) & (r * 100 > RATIO * 100 * b)


def stats(name, covs, rgb_sum, rgb_n):
    covs = np.array(covs)
    print(f"\n[{name}]  n_frames={len(covs)}")
    print(f"  coverage %:  mean={covs.mean()*100:.3f}  median={np.median(covs)*100:.3f}  "
          f"min={covs.min()*100:.3f}  max={covs.max()*100:.3f}  "
          f"p10={np.percentile(covs,10)*100:.3f}  p90={np.percentile(covs,90)*100:.3f}")
    print(f"  frames with coverage < 0.2% (gate ~vanished): "
          f"{int((covs < 0.002).sum())}/{len(covs)}")
    if rgb_n > 0:
        c = rgb_sum / rgb_n
        print(f"  kept-pixel RGB centroid: ({c[0]:.0f}, {c[1]:.0f}, {c[2]:.0f})   "
              f"[design gate core ~ (229, 93, 78)]")
        print(f"  kept-pixel R/G={c[0]/max(c[1],1):.2f}  R/B={c[0]/max(c[2],1):.2f}  "
              f"(rule needs both > {RATIO})")
    else:
        print("  kept-pixel RGB centroid: (no pixels kept)")


def main():
    files = sorted(glob.glob(os.path.join(HARVEST, "*.jpg")))
    if not files:
        print(f"NO frames at {HARVEST}")
        return
    idx = np.linspace(0, len(files) - 1, min(N, len(files))).astype(int)
    sample = [files[i] for i in idx]
    print(f"harvest: {len(files)} frames; sampling {len(sample)}  (R_MIN={R_MIN}, RATIO={RATIO})")

    cov_native, cov_64 = [], []
    rgbsum_n, rgbn_n = np.zeros(3), 0
    rgbsum_64, rgbn_64 = np.zeros(3), 0

    for f in sample:
        im = Image.open(f).convert("RGB")
        a = np.asarray(im, dtype=np.uint8)
        m = kept_mask(a)
        cov_native.append(float(m.mean()))
        if m.any():
            rgbsum_n += a[m].sum(axis=0); rgbn_n += int(m.sum())

        a64 = np.asarray(im.resize((64, 64), Image.BILINEAR), dtype=np.uint8)
        m64 = kept_mask(a64)
        cov_64.append(float(m64.mean()))
        if m64.any():
            rgbsum_64 += a64[m64].sum(axis=0); rgbn_64 += int(m64.sum())

    stats("NATIVE resolution", cov_native, rgbsum_n, rgbn_n)
    stats("64x64 (encoder obs)", cov_64, rgbsum_64, rgbn_64)

    print("\n--- read ---")
    print("If NATIVE coverage is healthy (~0.5-5%) + RGB centroid ~orange-red, the rule fires on")
    print("official gates -> supports encoder/overfit (route a: gate-pixel jitter), NOT a mask bug.")
    print("If 64x64 coverage collapses vs native, downsampling dilutes the gate below the ratio ->")
    print("a RESOLUTION bug: the encoder sees a near-blank frame on BOTH domains -> rethink the mask")
    print("(dilate, or mask at native then resize). If coverage ~0 or RGB off-palette -> gate-missing.")


if __name__ == "__main__":
    main()
