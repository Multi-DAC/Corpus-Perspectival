"""edge_precheck.py — verify edge_filter np/torch parity BEFORE any fine-tune (Day 135).

A train(torch)/infer(numpy) obs mismatch silently kills transfer. This asserts edge_np and edge_t are
BIT-identical on random + real frames, and sanity-checks the edge output (not all-zero / all-saturated).
Run: .venv/Scripts/python.exe integration/edge_precheck.py
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ANAKIN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ANAKIN, "sim"))
sys.path.insert(0, HERE)
from edge_filter import edge_np, edge_t  # noqa: E402
import torch  # noqa: E402

HARVEST = (r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364"
           r"\PyAIPilotExample\official_frames\manual_20260614_114130")


def check(name, img):
    a = edge_np(img)                                  # [H,W,3] uint8
    b = edge_t(torch.from_numpy(img[None])).numpy()[0]  # [H,W,3] uint8
    identical = np.array_equal(a, b)
    cov = (a[..., 0] > 0).mean()
    print(f"[{name}] np==torch: {'BIT-IDENTICAL' if identical else 'MISMATCH!!'}  "
          f"max_diff={int(np.abs(a.astype(int)-b.astype(int)).max())}  "
          f"edge-pixels>0: {cov*100:.1f}%  mean={a[...,0].mean():.1f} max={int(a.max())}")
    return identical


def main():
    ok = True
    rng = np.random.default_rng(7)
    ok &= check("random", rng.integers(0, 256, (64, 64, 3), dtype=np.uint8))
    # a flat frame -> should be near-zero edges
    ok &= check("flat-gray", np.full((64, 64, 3), 27, dtype=np.uint8))
    # a real official frame (resized to 64x64) if available
    import glob
    fs = sorted(glob.glob(os.path.join(HARVEST, "*.jpg")))
    if fs:
        from PIL import Image
        im = np.asarray(Image.open(fs[len(fs) // 2]).convert("RGB").resize((64, 64)), dtype=np.uint8)
        ok &= check("official(64x64)", im)
    print("\nPARITY", "OK — safe to fine-tune." if ok else "FAILED — DO NOT fine-tune; fix edge_filter.")


if __name__ == "__main__":
    main()
