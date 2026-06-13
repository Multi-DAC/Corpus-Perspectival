"""holdout_gate_v2.py — the P224 appearance gate, hardened (Day 133, 2026-06-13).

WHY v2 (from the Day-132 dream-drive caveat on anomaly I):
  v1 ran at n=20 frames. In the world model's high-D embedding space the COVARIANCE
  term of the Fréchet distance is then noise-dominated (you cannot estimate a DxD
  covariance from 20 samples), so v1's verdict was only robust as "no detectable
  closure," never as an exact FD. v2 fixes exactly that:

    (1) render 200 frames (cheap), and accept a large official-frame harvest;
    (2) DECOMPOSE the Fréchet distance and report its two pieces SEPARATELY:
          mean_term = ||mu_a - mu_b||^2                         (well-estimated even at low n)
          cov_term  = tr(Ca) + tr(Cb) - 2 tr(sqrt(Ca Cb))       (needs n > D to trust)
        The PASS verdict rests on the MEAN-TERM ratio (robust); the cov-term and the
        total are reported as secondary, flagged unreliable when n <= D.

This is the gate the post-flight-#2 appearance-adaptation loop runs through. Flight #2
spun out as v1's FAIL predicted (anomaly I -> branch a, gate validated). v2 is the
instrument for measuring whether a new adaptation (domain randomization / renderer
restyle toward official textures / encoder fine-tune) actually moves the official gap.

USAGE (anakin .venv):
  # default: sealed 20 held-out official policyviews vs 200 fresh restyled renders
  python integration/holdout_gate_v2.py
  # use a manual-harvest dir of RAW jpgs as the official set (converted to policyview):
  python integration/holdout_gate_v2.py --official-dir official_frames/manual_20260613_xxxx --official-raw
  # compare a specific pair of checkpoints
  python integration/holdout_gate_v2.py --ckpt-old <band.pt> --ckpt-new <adapted.pt>
"""
import argparse
import glob
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

ANAKIN = os.path.dirname(_HERE)
LOGDIR = os.path.join(ANAKIN, "third_party", "dreamerv3-torch", "logdir")
CKPT_OLD = os.path.join(LOGDIR, "maneuver_band_ft", "best.pt")
CKPT_NEW = os.path.join(LOGDIR, "maneuver_restyle_ft", "best.pt")
HELDOUT = r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364\PyAIPilotExample\capture_frames_HELDOUT_TESTSET"
N_RENDER = 200


def load_official_frames(directory, raw=False, cap=400):
    """Official-domain frames -> [N,64,64,3] uint8 RGB.

    raw=False: directory holds *_policyview.png (already 64x64) — v1's sealed set.
    raw=True : directory holds full-res *.jpg (the manual harvest) — convert each to
               the 64x64 policy view via dreamer_pilot.to_training_frame (the exact
               transform the policy sees), so the comparison is apples-to-apples.
    """
    import cv2
    if raw:
        from dreamer_pilot import to_training_frame
        paths = sorted(glob.glob(os.path.join(directory, "*.jpg")))[:cap]
        assert paths, f"no raw *.jpg frames in {directory}"
        frames = [to_training_frame(cv2.imread(p, cv2.IMREAD_COLOR)) for p in paths]  # RGB 64x64
        return np.stack(frames)
    paths = sorted(glob.glob(os.path.join(directory, "*_policyview.png")))[:cap]
    assert paths, f"no *_policyview.png frames in {directory}"
    frames = [cv2.cvtColor(cv2.imread(p, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB) for p in paths]
    return np.stack(frames)


def render_restyled_frames(n=N_RENDER, seed=11):
    """Fresh restyled-renderer frames with WIDE pose variation (better cov estimate)."""
    import torch
    sys.path.insert(0, os.path.join(ANAKIN, "sim"))
    from render import render
    from dynamics import init_state

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    gp = torch.tensor([[6.0, 0.0, 2.0], [14.0, 3.0, 2.5], [22.0, -2.0, 3.0]],
                      device=dev).expand(1, 3, 3).contiguous()
    gf = torch.tensor([[-1.0, 0, 0]] * 3, device=dev).expand(1, 3, 3).contiguous()
    frames = []
    for i in range(n):
        # wide, varied viewpoints along+around the course (the cov-term wants spread)
        x = rng.uniform(-8.0, 20.0)
        y = rng.uniform(-4.0, 4.0)
        z = rng.uniform(1.2, 3.8)
        cur = torch.tensor([i % 3], dtype=torch.long, device=dev)
        s = init_state(1, dev, (float(x), float(y), float(z)))
        fr = render(s, gp, gf, cur, n_visible=2)
        frames.append(fr[0].cpu().numpy())
    return np.stack(frames)


def embed_frames(pilot, frames, batch=64):
    """Encoder embeddings for a stack of 64x64 RGB frames -> [N, D] numpy (batched)."""
    import torch
    wm = pilot._agent._wm
    out = []
    for i in range(0, len(frames), batch):
        chunk = frames[i:i + batch]
        obs = {
            "image": chunk.astype(np.float32),
            "is_first": np.ones((len(chunk),), dtype=bool),
            "is_terminal": np.zeros((len(chunk),), dtype=bool),
        }
        with torch.no_grad():
            data = wm.preprocess(
                {k: torch.as_tensor(v, device=pilot._config.device) for k, v in obs.items()}
            )
            embed = wm.encoder(data)
        out.append(embed.detach().cpu().numpy().reshape(len(chunk), -1))
    return np.concatenate(out, 0)


def frechet_decomposed(a, b, eps=1e-6):
    """Fréchet distance between Gaussian fits, RETURNED AS ITS TWO TERMS.

    Returns dict: mean_term = ||mu_a-mu_b||^2 (trustworthy at any n),
                  cov_term  = tr(Ca)+tr(Cb)-2 tr(sqrt(Ca Cb)) (needs n>D),
                  total     = mean_term + cov_term,
                  n, D, rank_ok (n > D, i.e. covariance is full-rank).
    numpy-only sqrtm-trace via eigenvalues of Ca@Cb (real nonneg up to noise).
    """
    n, D = a.shape
    mu_a, mu_b = a.mean(0), b.mean(0)
    mean_term = float(((mu_a - mu_b) ** 2).sum())
    ca = np.cov(a, rowvar=False) + eps * np.eye(D)
    cb = np.cov(b, rowvar=False) + eps * np.eye(D)
    eig = np.linalg.eigvals(ca @ cb)
    tr_sqrt = float(np.sqrt(np.clip(eig.real, 0, None)).sum())
    cov_term = float(np.trace(ca) + np.trace(cb) - 2 * tr_sqrt)
    return {"mean_term": mean_term, "cov_term": cov_term,
            "total": mean_term + cov_term, "n": n, "D": D,
            "rank_ok": min(len(a), len(b)) > D}


def _fd_for(pilot, official, restyled):
    e_off = embed_frames(pilot, official)
    e_res = embed_frames(pilot, restyled)
    return frechet_decomposed(e_off, e_res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--official-dir", default=HELDOUT)
    ap.add_argument("--official-raw", action="store_true",
                    help="official-dir holds raw *.jpg (manual harvest) not *_policyview.png")
    ap.add_argument("--n-render", type=int, default=N_RENDER)
    ap.add_argument("--ckpt-old", default=CKPT_OLD)
    ap.add_argument("--ckpt-new", default=CKPT_NEW)
    args = ap.parse_args()

    from dreamer_pilot import DreamerPilot

    official = load_official_frames(args.official_dir, raw=args.official_raw)
    restyled = render_restyled_frames(args.n_render)
    print(f"frames: official={len(official)}  restyled(fresh)={len(restyled)}")

    res = {}
    for name, ckpt in (("band-ft (pre-adapt)", args.ckpt_old), ("adapted", args.ckpt_new)):
        if not os.path.exists(ckpt):
            print(f"[{name}] checkpoint missing: {ckpt} — skipping")
            continue
        pilot = DreamerPilot(ckpt)
        d = _fd_for(pilot, official, restyled)
        res[name] = d
        flag = "" if d["rank_ok"] else "  ⚠ n<=D: cov-term UNRELIABLE"
        print(f"[{name}] n={d['n']} D={d['D']}{flag}\n"
              f"    mean_term = {d['mean_term']:,.2f}   (trust at any n)\n"
              f"    cov_term  = {d['cov_term']:,.2f}\n"
              f"    total     = {d['total']:,.2f}")
        del pilot
        import gc, torch
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    if len(res) == 2:
        old, new = res["band-ft (pre-adapt)"], res["adapted"]
        mean_ratio = new["mean_term"] / max(old["mean_term"], 1e-9)
        total_ratio = new["total"] / max(old["total"], 1e-9)
        print(f"\nGATE v2 — decomposed:")
        print(f"  MEAN-TERM ratio (adapted/band-ft) = {mean_ratio:.3f}   <-- PRIMARY (robust)")
        print(f"  total ratio                       = {total_ratio:.3f}   (secondary; "
              f"{'cov full-rank' if new['rank_ok'] else 'cov-term noisy, n<=D'})")
        print("PRE-REGISTERED PASS: MEAN-TERM ratio < 0.5 "
              "(adaptation at least halves the official-domain gap on the trustworthy term)")
        print(f"VERDICT: {'PASS' if mean_ratio < 0.5 else 'FAIL'}")


if __name__ == "__main__":
    main()
