"""Refined TEST 4 for the §9 correction: show N_sign (Bias-zero / dynamics-critical) and
N_struct (Phi_S fixed point) SEPARATE when symmetry is broken (asymmetric Phi_S target t).
Self-contained (no file-read, to dodge Windows cp1252 decode of unicode)."""
import numpy as np

def m_k(d, beta=1.0, h=0.0):
    p0 = np.exp(h) * (((1.0 + d) / 2.0) ** beta)
    p1 = np.exp(-h) * (((1.0 - d) / 2.0) ** beta)
    return (p0 - p1) / (p0 + p1)

def phi_s_biased(d, a=0.5, t=0.0):
    return (1 - a) * d + a * t          # fixed point at t  (= N_struct)

def combined(d, a=0.5, t=0.0, beta=2.5):
    return m_k(phi_s_biased(d, a=a, t=t), beta=beta)

def fixed_points(f, eps=1e-6):
    grid = np.linspace(-0.999999, 0.999999, 200001)
    g = np.array([f(d) for d in grid]) - grid
    out = []
    for i in range(len(grid) - 1):
        if g[i] == 0 or g[i] * g[i + 1] < 0:
            lo, hi = grid[i], grid[i + 1]
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if (f(lo) - lo) * (f(mid) - mid) <= 0: hi = mid
                else: lo = mid
            ds = 0.5 * (lo + hi)
            dv = (f(ds + eps) - f(ds - eps)) / (2 * eps)
            if not any(abs(ds - o[0]) < 1e-4 for o in out):
                out.append((ds, dv))
    return out

print("Refined TEST 4 - asymmetric Phi_S (target t = N_struct) vs symmetric super-critical M_k (beta=2.5)")
print("  N_struct = Phi_S fixed point = t ;  N_sign = interior UNSTABLE point of combined dynamics")
for t in [0.0, 0.05, 0.12, 0.20]:
    f = lambda d, t=t: combined(d, a=0.5, t=t, beta=2.5)
    fps = fixed_points(f)
    unst = [d for d, dv in fps if abs(dv) > 1.0]
    if unst:
        nsign = unst[0]; sep = abs(nsign - t)
        tag = "COINCIDE" if sep < 1e-3 else "SEPARATE - conflation exposed"
        print(f"  t(N_struct)={t:+.3f}  N_sign={nsign:+.4f}  separation={sep:.4f}  <- {tag}")
    else:
        print(f"  t(N_struct)={t:+.3f}  N_sign=(none interior)  <- neutral washed out")
