"""edge_filter.py — edge/pencil obs transform (appearance-invariant front-end, Day 135).

WHY (the corrected segmentation route): the Day-134 color-mask route FALSIFIED + flight #3 confirmed
appearance-OOD is the wall. Literature (PencilNet arXiv 2207.14131; Loquercio TRO-2019) shows the
PROVEN sim-to-real path keys invariance on EDGES, not color — edges survive the color/illumination
shift that our old-color-trained backbone chokes on. This replaces gate_mask's brittle RGB-COLOR
threshold with a Sobel EDGE magnitude: the gate (high-contrast rectangle) produces strong, consistent
edges in BOTH the rendered and official domains; raw color/texture (the OOD axis) is discarded.

CAVEAT (pre-registered): a pure edge filter ALSO passes background-texture edges (the official TRON bg
is edge-dense; the renderer's gray bg is edge-sparse). So edges fix the GATE-appearance axis but not the
background-density mismatch. This is the clean first experiment (isolate the edge variable). If the
holdout gate's mean-term improves but transfer is only partial, the residual is background edges →
NEXT step adds background randomization (APPEARANCE_RANDOMIZATION_SPEC). One variable at a time.

PARITY IS LOAD-BEARING: training (render, torch) and inference (dreamer_pilot, numpy) must produce
BIT-IDENTICAL output, or the policy trains on one obs and flies another (the silent transfer-killer).
So Sobel is computed in pure INTEGER shifted-slice arithmetic (no cv2, no float conv2d) — identical in
numpy and torch. Verify with integration/edge_precheck.py before any fine-tune.

Output: 3-channel uint8, edge magnitude replicated across channels (encoder (64,64,3) shape unchanged,
no architecture change). Toggle with env var ANAKIN_EDGE=1 (orthogonal to ANAKIN_GATE_MASK).
"""
import os

# luminance weights (sum=256 -> exact >>8); Sobel L1 magnitude scaled by >>3 (max |Gx|+|Gy|=2040 -> 255)
_LR, _LG, _LB = 77, 150, 29
_MAG_SHIFT = 3


def enabled() -> bool:
    return os.environ.get("ANAKIN_EDGE", "0") == "1"


def _sobel_mag_np(lum):
    """lum [H,W] int -> edge magnitude [H,W] uint8, zero-padded borders. Pure integer."""
    import numpy as np
    p = np.pad(lum.astype(np.int32), 1, mode="constant")
    # Gx = right Sobel - left Sobel ; Gy = bottom Sobel - top Sobel (3x3, integer)
    gx = ((p[0:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:])
          - (p[0:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2]))
    gy = ((p[2:, 0:-2] + 2 * p[2:, 1:-1] + p[2:, 2:])
          - (p[0:-2, 0:-2] + 2 * p[0:-2, 1:-1] + p[0:-2, 2:]))
    mag = (np.abs(gx) + np.abs(gy)) >> _MAG_SHIFT
    return np.minimum(mag, 255).astype(np.uint8)


def edge_np(img_uint8):
    """[H,W,3] uint8 RGB -> [H,W,3] uint8 edge-magnitude (3ch replicate). numpy/inference path."""
    import numpy as np
    a = img_uint8.astype(np.int32)
    lum = (_LR * a[..., 0] + _LG * a[..., 1] + _LB * a[..., 2]) >> 8   # [H,W] in [0,255]
    e = _sobel_mag_np(lum)                                            # [H,W] uint8
    return np.repeat(e[..., None], 3, axis=-1)


def edge_t(img_uint8):
    """[N,H,W,3] uint8 RGB torch -> same shape uint8 edge-magnitude (3ch). render/training path.
    Pure integer (int32) shifted-slice Sobel — bit-identical to edge_np."""
    import torch
    a = img_uint8.to(torch.int32)
    lum = (_LR * a[..., 0] + _LG * a[..., 1] + _LB * a[..., 2]) >> 8   # [N,H,W]
    p = torch.nn.functional.pad(lum, (1, 1, 1, 1))                     # zero-pad H,W -> [N,H+2,W+2]
    gx = ((p[:, 0:-2, 2:] + 2 * p[:, 1:-1, 2:] + p[:, 2:, 2:])
          - (p[:, 0:-2, :-2] + 2 * p[:, 1:-1, :-2] + p[:, 2:, :-2]))
    gy = ((p[:, 2:, 0:-2] + 2 * p[:, 2:, 1:-1] + p[:, 2:, 2:])
          - (p[:, 0:-2, 0:-2] + 2 * p[:, 0:-2, 1:-1] + p[:, 0:-2, 2:]))
    mag = (torch.abs(gx) + torch.abs(gy)) >> _MAG_SHIFT               # [N,H,W]
    e = torch.clamp(mag, max=255).to(torch.uint8)
    return e.unsqueeze(-1).repeat(1, 1, 1, 3)
