"""holdout_gate.py — the P224 appearance gate: did the restyle close the domain gap?

THE measurement A150 demanded: one end anchored OUTSIDE our wall. Compares the
world model's encoder response to (a) the 20 SEALED official-sim frames
(capture_frames_HELDOUT_TESTSET — never used for tuning, by README rule) vs
(b) fresh frames from our restyled renderer, under TWO checkpoints:

                    official frames        restyled-render frames
  band-ft best.pt   [pre-restyle: far OOD] [also OOD: old model, new palette]
  restyle-ft best   [THE QUESTION]         [in-distribution by construction]

Primary metric: Fréchet distance between encoder-embedding clouds (Gaussian
approx — mean+cov). PRE-REGISTERED PASS: FD(restyle-ft: official vs restyled)
< 0.5 x FD(band-ft: official vs restyled), i.e. the restyle at least halves
the embedding-space domain gap. Secondary (best-effort): decoder reconstruction
MSE per set, if the decoder API cooperates.

Run AFTER the restyle fine-tune completes (it owns best.pt until then):
  .venv/Scripts/python.exe integration/holdout_gate.py
"""
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
N_RENDER = 20


def load_heldout_frames():
    """The sealed official policyview frames (64x64 RGB pngs)."""
    import cv2
    paths = sorted(glob.glob(os.path.join(HELDOUT, "*_policyview.png")))
    assert paths, f"no held-out policyview frames found in {HELDOUT}"
    frames = []
    for p in paths:
        img = cv2.imread(p, cv2.IMREAD_COLOR)          # BGR
        frames.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return np.stack(frames)                             # [N,64,64,3] uint8 RGB


def render_restyled_frames(n=N_RENDER, seed=11):
    """Fresh frames from the restyled renderer: varied poses on a 3-gate course."""
    import torch
    sys.path.insert(0, os.path.join(ANAKIN, "sim"))
    from render import render
    from dynamics import init_state

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(seed)
    gp = torch.tensor([[6.0, 0.0, 2.0], [14.0, 3.0, 2.5], [22.0, -2.0, 3.0]],
                      device=dev).expand(n, 3, 3).contiguous()
    gf = torch.tensor([[-1.0, 0, 0]] * 3, device=dev).expand(n, 3, 3).contiguous()
    cur = torch.zeros(n, dtype=torch.long, device=dev)
    # varied viewpoints: spread along/around the course
    xs = np.linspace(-6.0, 18.0, n)
    frames = []
    for i, x in enumerate(xs):
        s = init_state(1, dev, (float(x), float(np.sin(i) * 1.5), 2.0 + (i % 4) * 0.6))
        fr = render(s, gp[:1], gf[:1], cur[:1], n_visible=2)
        frames.append(fr[0].cpu().numpy())
    return np.stack(frames)                             # [n,64,64,3] uint8 RGB


def embed_frames(pilot, frames):
    """Encoder embeddings for a stack of 64x64 RGB frames -> [N, D] numpy."""
    import torch
    wm = pilot._agent._wm
    obs = {
        "image": frames.astype(np.float32),             # preprocess handles scaling
        "is_first": np.ones((len(frames),), dtype=bool),
        "is_terminal": np.zeros((len(frames),), dtype=bool),
    }
    with torch.no_grad():
        data = wm.preprocess(
            {k: torch.as_tensor(v, device=pilot._config.device) for k, v in obs.items()}
        )
        embed = wm.encoder(data)
    e = embed.detach().cpu().numpy()
    return e.reshape(len(frames), -1)


def frechet(a, b, eps=1e-6):
    """Fréchet distance between Gaussian fits of two embedding clouds.

    numpy-only: tr(sqrtm(Ca@Cb)) = sum of sqrt eigenvalues of Ca@Cb (clipped to
    real nonneg — Ca@Cb is a product of PSD matrices so its spectrum is real
    nonneg up to numerical noise). Avoids a scipy dependency in the anakin venv.
    """
    mu_a, mu_b = a.mean(0), b.mean(0)
    ca = np.cov(a, rowvar=False) + eps * np.eye(a.shape[1])
    cb = np.cov(b, rowvar=False) + eps * np.eye(b.shape[1])
    eig = np.linalg.eigvals(ca @ cb)
    tr_sqrt = float(np.sqrt(np.clip(eig.real, 0, None)).sum())
    return float(((mu_a - mu_b) ** 2).sum() + np.trace(ca) + np.trace(cb) - 2 * tr_sqrt)


def recon_mse(pilot, frames):
    """Best-effort decoder reconstruction MSE (secondary metric)."""
    import torch
    try:
        wm = pilot._agent._wm
        obs = {
            "image": frames.astype(np.float32),
            "is_first": np.ones((len(frames),), dtype=bool),
            "is_terminal": np.zeros((len(frames),), dtype=bool),
        }
        with torch.no_grad():
            data = wm.preprocess(
                {k: torch.as_tensor(v, device=pilot._config.device) for k, v in obs.items()}
            )
            embed = wm.encoder(data)
            latent, _ = wm.dynamics.obs_step(
                None, None, embed, torch.ones(len(frames), device=pilot._config.device).bool()
            )
            feat = wm.dynamics.get_feat(latent)
            dec = wm.heads["decoder"](feat)["image"].mode()
        target = data["image"]
        return float(((dec - target) ** 2).mean().item())
    except Exception as e:
        return f"unavailable ({type(e).__name__}: {e})"


def main():
    from dreamer_pilot import DreamerPilot

    official = load_heldout_frames()
    restyled = render_restyled_frames()
    print(f"frames: official(held-out)={len(official)}  restyled(fresh)={len(restyled)}")

    results = {}
    for name, ckpt in (("band-ft (pre-restyle)", CKPT_OLD), ("restyle-ft", CKPT_NEW)):
        pilot = DreamerPilot(ckpt)
        e_off = embed_frames(pilot, official)
        e_res = embed_frames(pilot, restyled)
        fd = frechet(e_off, e_res)
        results[name] = fd
        print(f"[{name}] FD(official <-> restyled) = {fd:,.1f}   "
              f"recon_mse: official={recon_mse(pilot, official)}  "
              f"restyled={recon_mse(pilot, restyled)}")
        del pilot
        import gc, torch
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()  # two 19M-param pilots back-to-back; free VRAM between

    old_fd, new_fd = results["band-ft (pre-restyle)"], results["restyle-ft"]
    ratio = new_fd / max(old_fd, 1e-9)
    print(f"\nGATE: FD ratio (restyle-ft / band-ft) = {ratio:.3f}")
    print("PRE-REGISTERED PASS: ratio < 0.5  (restyle at least halves the "
          "embedding-space domain gap on SEALED official frames)")
    print(f"VERDICT: {'PASS' if ratio < 0.5 else 'FAIL'}")


if __name__ == "__main__":
    main()
