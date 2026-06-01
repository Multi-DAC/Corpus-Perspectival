#
# Bounded distance encoding for the gate-relative observation dims (AIGP VQ1, Day 121).
#
# WHY: the obs encoded RAW UNBOUNDED gate-relative distance. VecNormalize stats are
# dominated by the common near-gate regime (0-10m), so a far gate (VQ1 start = 23m) is a
# ~6-sigma outlier that clips at +/-10 -> the policy saturates. Far-start *training* could
# not fix it (FALSIFIED 2026-06-01: 95M worse than 80M) because it's a normalization-
# statistics problem, not a data problem. FIX = bound the distance at the source.
#
# SINGLE SOURCE OF TRUTH: imported by BOTH vision/adapter.build_observation (deploy) and
# rl/train_ppo.ImprovedObsWrapper (training). They MUST encode identically or the live obs
# diverges from training (its own L17-trap). Sharing one function makes that true by
# construction; test_obs_encoding.py verifies the wiring.
#
# DESIGN: preserve DIRECTION always (matters most when far -> turn toward gate); squash
# MAGNITUDE via tanh so near-gate discrimination is kept (matters most when close -> precise
# pass) and far gates saturate gracefully instead of blowing up. Bounded to [0,1) by
# construction, so no value can ever be a multi-sigma outlier regardless of VecNormalize.
#
import numpy as np

DIST_SCALE = 10.0  # meters. near regime 3-10m -> tanh 0.3-0.76; VQ1 23m -> 0.98; 100m -> ~1.0


def unit_dir(v):
    """Pure unit direction (A150 fix). Each component in [-1,1] with NATURAL per-component
    variance across varied gate angles — unlike bound_vec, which multiplied by tanh(|v|) and so
    crushed the lateral components of mostly-ahead gates to tiny-variance -> VecNormalize then
    over-normalized them (the 5.65-sigma residual at the far rest-start). DECOUPLES direction from
    magnitude: direction goes here, magnitude is carried separately by bound_scalar(dist). Zero in
    -> zero out (no gate)."""
    v = np.asarray(v, dtype=float)
    n = float(np.linalg.norm(v))
    if n < 1e-9:
        return np.zeros(3)
    return v / n


def bound_vec(v):
    """[DEPRECATED for gate dirs — see A150/unit_dir] Bounded position: unit-dir * tanh(|v|/SCALE).
    Kept for reference / any non-gate use. Couples dir+magnitude (the lateral over-normalization)."""
    v = np.asarray(v, dtype=float)
    n = float(np.linalg.norm(v))
    if n < 1e-9:
        return np.zeros(3)
    return (v / n) * np.tanh(n / DIST_SCALE)


def bound_scalar(d):
    """Bounded distance scalar: tanh(d/SCALE) in [0,1). Carries the current-gate magnitude."""
    return float(np.tanh(float(d) / DIST_SCALE))


if __name__ == "__main__":
    # Offline verification: bounded, monotonic, near-discrimination preserved, far saturates.
    print("=== bound_scalar(dist) ===")
    for d in (0, 3, 5, 10, 15, 23, 50, 100):
        print(f"  dist={d:4d}m -> {bound_scalar(d):.4f}")
    print("=== bound_vec direction preserved, magnitude bounded ===")
    for d in (5, 23, 100):
        v = np.array([d * 0.96, -d * 0.02, d * 0.31])  # roughly the VQ1 gate-0 direction
        bv = bound_vec(v)
        raw_unit = v / np.linalg.norm(v)
        bv_unit = bv / (np.linalg.norm(bv) + 1e-12)
        cos = float(np.dot(raw_unit, bv_unit))
        print(f"  |v|={d:4d}m -> |bv|={np.linalg.norm(bv):.4f}  dir-cos={cos:.6f} (1.0=preserved)")
    # Assertions
    assert 0 <= bound_scalar(1000) <= 1.0, "scalar must stay in [0,1] (tanh saturates to exactly 1.0)"
    assert bound_scalar(5) < bound_scalar(10) < bound_scalar(23), "must be monotonic"
    assert np.linalg.norm(bound_vec([100, 0, 0])) <= 1.0, "vec magnitude must stay <=1"
    assert abs(np.dot(bound_vec([3, 4, 0]) / np.linalg.norm(bound_vec([3, 4, 0])),
                      np.array([0.6, 0.8, 0.0])) - 1.0) < 1e-9, "direction must be preserved"
    print("\nOK: bounded, monotonic, direction-preserving. Max possible magnitude < 1 -> no sigma blowup.")
