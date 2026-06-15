"""gate_mask.py — gate-isolation obs transform (segmentation front-end, Day 134).

WHY: holdout_gate_v2 (n=400) showed the official<->training gap is the official sim's dense
TRON BACKGROUND texture, not gate color — our renderer already matches the measured orange-red
gate palette. Zeroing every non-gate pixel removes exactly that gap source and leaves the gate
(which both domains share). This is the SkyDreamer route: the world model learns geometry, not
photometry. See integration/SEG_ROUTE_DECISION_2026-06-14.md.

THE RULE IS IN RGB SPACE (not HSV) ON PURPOSE: the training path is batched torch on CUDA and the
inference path is single-frame numpy. An RGB-ratio rule is trivially identical in both — no cv2-vs-
torch HSV reimplementation to drift. The orange-red gate (core RGB ~229,93,78; dim ~115,46,38;
glow-blend ~98,50,45) has R strongly dominant; gray bg, white cityscape, cyan ribbon, green grid
all FAIL `R dominates G and B`.

Toggle with env var ANAKIN_GATE_MASK=1 so old (unmasked) checkpoints/tooling are untouched; the
mask-retrain and its inference set it. Output keeps 3 uint8 channels (masked RGB: gate pixels keep
their color, everything else -> 0) so NO encoder architecture change is needed.
"""
import os

R_MIN = 70      # exclude dark bg (~27) and faint noise
RATIO = 1.55    # R must exceed 1.55x both G and B (orange-red only)


def enabled() -> bool:
    return os.environ.get("ANAKIN_GATE_MASK", "0") == "1"


def gate_isolate_np(img_uint8):
    """[...,H,W,3] uint8 RGB numpy -> same shape, non-gate pixels zeroed."""
    import numpy as np
    a = img_uint8.astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    keep = (r > R_MIN) & (r * 100 > RATIO * 100 * g) & (r * 100 > RATIO * 100 * b)
    return (img_uint8 * keep[..., None]).astype(np.uint8)


def gate_isolate_t(img_uint8):
    """[...,H,W,3] uint8 RGB torch tensor -> same shape/device, non-gate pixels zeroed."""
    a = img_uint8.to(dtype=__import__("torch").int32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    keep = (r > R_MIN) & (r * 100 > int(RATIO * 100) * g) & (r * 100 > int(RATIO * 100) * b)
    return img_uint8 * keep.unsqueeze(-1).to(img_uint8.dtype)
