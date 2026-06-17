"""resolution_confound_probe.py — isolate the RESOLUTION/MTF term of the holdout-gate confound.

GATE_CONFOUND_2026-06-17.md found the official-vs-render mean-term (band-ft = 24.44) mixes
genuine appearance-OOD with a pure resolution artifact: the official arm is real 640->64
INTER_AREA-downsampled (heavily blurred), the rendered arm is rasterized natively-sharp at 64.
This probe measures the resolution term ALONE — no official frames, no renderer refactor:

    S = render the SAME scenes natively at 64x64        (sharp; the current gate's rendered arm)
    B = render the SAME scenes at 640x640, INTER_AREA->64 (blurred to match the official MTF)

Poses are seed-matched, so S[i] and B[i] are the identical scene at two resolutions; the ONLY
difference is sharpness. FD_mean(S, B) through the band-ft encoder = how much the world-model
encoder embeds that sharp/blur difference.

  * FD_mean(S,B) large vs the committed 24.44  -> the "appearance gap" is substantially RESOLUTION
    -> greenlight the full Fix B (640x360 render -> to_training_frame, vs official) for the true
    appearance residual, and resample-matched fine-tuning as the cheap fix.
  * FD_mean(S,B) ~ the same-distribution sampling floor -> the encoder ignores resolution; the
    official gap is real appearance -> appearance-DR / obs-augmentation is the justified route.

Faithfulness note: this isolates RESOLUTION only. The band/VFoV term (already known, +131.8%) is
held identical across S and B by construction, so it does not enter FD(S,B). The official-domain
comparison (which also carries the band term) is the full Fix B, the next step if this greenlights.

Run (anakin .venv):
  .venv/Scripts/python.exe integration/resolution_confound_probe.py
"""
import math
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
ANAKIN = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(ANAKIN, "sim"))

import cv2  # noqa: E402
import torch  # noqa: E402

# reuse the EXACT gate instruments so the number is comparable to the committed run
from holdout_gate_v2 import LOGDIR, embed_frames, frechet_decomposed  # noqa: E402

import render as R  # noqa: E402
from dynamics import init_state  # noqa: E402

# same fixed course the gate's render_restyled_frames uses
GP = torch.tensor([[6.0, 0.0, 2.0], [14.0, 3.0, 2.5], [22.0, -2.0, 3.0]])
GF = torch.tensor([[-1.0, 0.0, 0.0]] * 3)

COMMITTED_OFFICIAL_GAP = 24.44  # band-ft official-vs-render mean_term (GATE_CONFOUND_2026-06-17.md)


def _set_resolution(res):
    """Point the renderer's call-time globals at a square `res` with matched HFoV intrinsics."""
    R.IMG = res
    f = (res / 2.0) / math.tan(math.radians(R.HFOV_DEG) / 2.0)
    R.FX = R.FY = float(f)
    R.CX = R.CY = res / 2.0


def render_scenes(res, n=200, seed=11, render_chunk=8):
    """Render n frames at square resolution `res`; poses fixed by `seed` (so two calls with the
    same seed give the identical scenes at different resolutions). Returns [n,res,res,3] uint8 RGB.
    add_noise=False for a clean resolution-only contrast; bg-jitter/ribbon RNG is seeded identically
    across resolutions (same number of torch.rand calls per frame regardless of res)."""
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    _set_resolution(res)
    gp = GP.to(dev).expand(1, 3, 3).contiguous()
    gf = GF.to(dev).expand(1, 3, 3).contiguous()
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    out = []
    for i in range(n):
        x = rng.uniform(-8.0, 20.0)
        y = rng.uniform(-4.0, 4.0)
        z = rng.uniform(1.2, 3.8)
        cur = torch.tensor([i % 3], dtype=torch.long, device=dev)
        s = init_state(1, dev, (float(x), float(y), float(z)))
        fr = R.render(s, gp, gf, cur, n_visible=2, add_noise=False)  # [1,res,res,3] uint8
        out.append(fr[0].cpu().numpy())
        if dev == "cuda" and (i + 1) % render_chunk == 0:
            torch.cuda.empty_cache()
    return np.stack(out)


def downsample(frames_hi, to=64):
    """INTER_AREA downsample each [H,W,3] uint8 frame to to x to — the exact op official frames get."""
    return np.stack([cv2.resize(f, (to, to), interpolation=cv2.INTER_AREA) for f in frames_hi])


def main():
    N = 200
    print(f"[probe] rendering S (native-64, sharp) and B (640->64, blurred), n={N}, matched poses...")
    S = render_scenes(64, n=N, seed=11)
    B_hi = render_scenes(640, n=N, seed=11)   # SAME seed -> same poses as S
    B = downsample(B_hi, 64)
    _set_resolution(64)                        # restore default for any later import use
    del B_hi

    ckpt = os.path.join(LOGDIR, "maneuver_band_ft", "best.pt")
    assert os.path.exists(ckpt), f"band-ft checkpoint missing: {ckpt}"
    from dreamer_pilot import DreamerPilot
    print(f"[probe] embedding through band-ft encoder: {ckpt}")
    pilot = DreamerPilot(ckpt)

    eS = embed_frames(pilot, S)
    eB = embed_frames(pilot, B)

    # pure resolution gap (matched poses, sharp vs blurred)
    res_gap = frechet_decomposed(eS, eB)
    # same-distribution sampling floor (split S in half — identical distribution, sampling-only)
    floor = frechet_decomposed(eS[: N // 2], eS[N // 2 :])

    rg = res_gap["mean_term"]
    fl = floor["mean_term"]
    print("\n========================= RESOLUTION CONFOUND PROBE =========================")
    print(f"  D (embed dim) = {res_gap['D']}   n per arm = {N}")
    print(f"  sampling floor  FD_mean(S_a, S_b)  = {fl:,.3f}   (same dist, different samples)")
    print(f"  RESOLUTION gap  FD_mean(S, B)      = {rg:,.3f}   (sharp vs 640->64 blur, MATCHED poses)")
    print(f"  committed official-vs-render gap   = {COMMITTED_OFFICIAL_GAP:,.3f}   (band-ft, GATE_CONFOUND)")
    print("  ----------------------------------------------------------------------------")
    print(f"  resolution gap / official gap      = {rg / COMMITTED_OFFICIAL_GAP:6.1%}  <-- confound share")
    print(f"  resolution gap / sampling floor    = {rg / max(fl, 1e-9):6.1f}x  (>>1 => real shift)")
    print("============================================================================")
    if rg / COMMITTED_OFFICIAL_GAP > 0.25 and rg / max(fl, 1e-9) > 3.0:
        print("VERDICT: confound CONFIRMED material — a large fraction of the 'appearance gap' is")
        print("         pure resolution. Greenlight full Fix B (640x360 render -> to_training_frame")
        print("         vs official) for the true appearance residual; cheap fix = resample-matched FT.")
    elif rg / max(fl, 1e-9) <= 3.0:
        print("VERDICT: confound NEGLIGIBLE — the encoder barely embeds resolution. The official gap")
        print("         is real appearance-OOD; appearance-DR / obs-augmentation is the justified route.")
    else:
        print("VERDICT: confound PRESENT but partial — resolution explains some of the gap, not all.")
        print("         Run full Fix B to split the residual before choosing the fix.")


if __name__ == "__main__":
    main()
