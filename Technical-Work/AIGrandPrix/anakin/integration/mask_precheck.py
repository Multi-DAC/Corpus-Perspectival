"""mask_precheck.py — validate the gate-isolation transform BEFORE the retrain.

Three checks:
  (1) torch/numpy parity of gate_isolate (must be bit-identical).
  (2) segmentation quality: save official + our-renderer overlays for eyeball.
  (3) THE NUMBER: pixel-space Fréchet distance between official and our-renderer
      frame distributions, computed for RGB vs MASKED (PCA-reduced, encoder-free).
      Hypothesis: FD_masked << FD_rgb  (masking removes the domain-distinguishing
      background texture). This is the cheap proxy for "the 24.44 gap collapses."
"""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ANAKIN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ANAKIN, "sim"))
from gate_mask import gate_isolate_np, gate_isolate_t  # noqa: E402

OFFICIAL = r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364\PyAIPilotExample\official_frames\manual_20260614_114130"
OUT = os.path.join(HERE, "mask_precheck_out")
os.makedirs(OUT, exist_ok=True)
N = 200


def load_official(n):
    import cv2
    paths = sorted(glob.glob(os.path.join(OFFICIAL, "*.jpg")))
    idx = np.linspace(0, len(paths) - 1, n).astype(int)
    fr = []
    for i in idx:
        bgr = cv2.imread(paths[i], cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        fr.append(cv2.resize(rgb, (64, 64), interpolation=cv2.INTER_AREA))
    return np.stack(fr).astype(np.uint8)


def render_ours(n, seed=7):
    import torch
    sys.path.insert(0, os.path.join(ANAKIN, "sim"))
    from render import render
    from dynamics import init_state
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    rng = np.random.default_rng(seed)
    gp = torch.tensor([[6.0, 0.0, 2.0], [14.0, 3.0, 2.5], [22.0, -2.0, 3.0]],
                      device=dev).expand(1, 3, 3).contiguous()
    gf = torch.tensor([[-1.0, 0, 0]] * 3, device=dev).expand(1, 3, 3).contiguous()
    fr = []
    for i in range(n):
        x = rng.uniform(-8.0, 20.0); y = rng.uniform(-4.0, 4.0); z = rng.uniform(1.2, 3.8)
        cur = torch.tensor([i % 3], dtype=torch.long, device=dev)
        s = init_state(1, dev, (float(x), float(y), float(z)))
        f = render(s, gp, gf, cur, n_visible=2)  # [1,64,64,3] uint8 (torch or np?)
        f = f[0].detach().cpu().numpy() if hasattr(f, "detach") else np.asarray(f)[0]
        fr.append(f.astype(np.uint8))
    return np.stack(fr)


def frechet_pixels(a, b, k=40):
    """Fréchet distance between two frame sets in a shared k-dim PCA pixel space."""
    A = a.reshape(len(a), -1).astype(np.float32) / 255.0
    B = b.reshape(len(b), -1).astype(np.float32) / 255.0
    X = np.concatenate([A, B], 0)
    mu = X.mean(0, keepdims=True)
    U, S, Vt = np.linalg.svd(X - mu, full_matrices=False)
    P = Vt[:k].T                       # [D,k]
    pa, pb = (A - mu) @ P, (B - mu) @ P
    ma, mb = pa.mean(0), pb.mean(0)
    ca = np.cov(pa, rowvar=False) + 1e-6 * np.eye(k)
    cb = np.cov(pb, rowvar=False) + 1e-6 * np.eye(k)
    eig = np.linalg.eigvals(ca @ cb)
    tr_sqrt = float(np.sqrt(np.clip(eig.real, 0, None)).sum())
    mean_term = float(((ma - mb) ** 2).sum())
    cov_term = float(np.trace(ca) + np.trace(cb) - 2 * tr_sqrt)
    return mean_term, cov_term, mean_term + cov_term


def main():
    import cv2, torch
    # (1) parity
    rt = torch.randint(0, 256, (5, 64, 64, 3), dtype=torch.uint8)
    a = gate_isolate_np(rt.numpy())
    b = gate_isolate_t(rt).numpy()
    parity = bool((a == b).all())
    print(f"(1) torch/numpy parity: {'OK' if parity else 'MISMATCH!'}")

    off = load_official(N)
    ours = render_ours(N)
    off_m = gate_isolate_np(off)
    ours_m = gate_isolate_np(ours)

    # (2) overlays
    for tag, raw, msk in (("official", off, off_m), ("ours", ours, ours_m)):
        covs = (msk.reshape(len(msk), -1) > 0).mean(1)
        order = np.argsort(-covs)[:6]
        rows = []
        for i in order:
            sep_w = np.full((64, 4, 3), 255, np.uint8)
            rows.append(np.hstack([raw[i], sep_w, msk[i]]))
            rows.append(np.full((4, rows[-1].shape[1], 3), 255, np.uint8))  # h-separator
        grid = np.vstack(rows)
        cv2.imwrite(os.path.join(OUT, f"{tag}_overlays.png"), cv2.cvtColor(grid, cv2.COLOR_RGB2BGR))
        print(f"(2) {tag}: gate-coverage mean={covs.mean()*100:.2f}%  "
              f"frames-with-gate={int((covs>5e-4).sum())}/{len(covs)}  overlay saved")

    # (3) the number
    print("(3) pixel-space Fréchet distance, official <-> ours:")
    for tag, A, B in (("RGB   ", off, ours), ("MASKED", off_m, ours_m)):
        mt, ct, tot = frechet_pixels(A, B)
        print(f"    {tag}: mean_term={mt:.4f}  cov_term={ct:.4f}  total={tot:.4f}")
    print(f"overlays -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
