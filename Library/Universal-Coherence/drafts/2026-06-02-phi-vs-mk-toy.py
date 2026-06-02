"""
Toy verification of the §9 correction (A144) for the diagonal-irrecoverability draft.

Question: in the ℤ/2-swap model the Companion uses (§3.4.2, §7.4.3), is the midnight §9 claim
("Φ_S repelling at 0, Morse dichotomy on σ_struct") backwards? The dream-drive argument says:
  - Φ_S (push_struct) is C-AVERAGING → ATTRACTS toward the symmetric/uniform state (σ_struct max).
  - The 0→± repulsion is MEASUREMENT M_k, not Φ_S.
  - The right statement is a Φ_S-vs-M_k COMPETITION with a quantitative threshold, recovering
    einselection (M_k wins) vs decoherence-free/metastable (Φ_S wins) — NOT a Morse condition on σ_struct.
  - N_sign (Bias sign=0) and N_struct (Φ_S-harmonic) coincide under symmetry, separate when broken.

State space: distributions over {0,1}, parametrized by d = p0 - p1 ∈ [-1, 1].
  d = 0  : uniform / symmetric / superposed  (the "neutral 0")
  d = ±1 : definite / pointer states
"""
import numpy as np

# ---------------------------------------------------------------------------
# Operators on the difference coordinate d = p0 - p1
# ---------------------------------------------------------------------------

def phi_s(d, a=1.0):
    """Φ_S = C-average over the swap, strength a∈[0,1] (a=1 = full Companion push_struct(δ0)=uniform).
    C-average of [p0,p1] over {id, swap} = uniform; partial-strength contracts d toward 0."""
    return (1.0 - a) * d           # d -> (1-a) d  ; fixed point d=0 (uniform), contraction rate (1-a)

def m_k(d, beta=1.0, h=0.0):
    """Measurement / sharpening with inverse-temperature beta>=1 and optional bias h (broken symmetry).
    p_i ∝ exp(h*x_i) * p_i^beta, x_0=+1, x_1=-1.  beta>1 sharpens toward a definite pointer state."""
    p0 = (1.0 + d) / 2.0
    p1 = (1.0 - d) / 2.0
    p0 = np.exp(h) * (p0 ** beta)
    p1 = np.exp(-h) * (p1 ** beta)
    Z = p0 + p1
    return (p0 - p1) / Z

def iterate(f, d0, n=2000):
    d = d0
    for _ in range(n):
        d = f(d)
    return d

def fixed_points_and_stability(f, eps=1e-6, grid=None):
    """Find fixed points on [-1,1] by scanning sign changes of f(d)-d, classify by |f'| via finite diff."""
    if grid is None:
        grid = np.linspace(-0.999999, 0.999999, 200001)
    g = np.array([f(d) for d in grid]) - grid
    fps = []
    for i in range(len(grid) - 1):
        if g[i] == 0 or g[i] * g[i + 1] < 0:
            # bisect
            lo, hi = grid[i], grid[i + 1]
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if (f(lo) - lo) * (f(mid) - mid) <= 0:
                    hi = mid
                else:
                    lo = mid
            d_star = 0.5 * (lo + hi)
            deriv = (f(d_star + eps) - f(d_star - eps)) / (2 * eps)
            fps.append((d_star, deriv))
    # dedup
    uniq = []
    for d_star, deriv in fps:
        if not any(abs(d_star - u[0]) < 1e-4 for u in uniq):
            uniq.append((d_star, deriv))
    return uniq

def classify(deriv):
    if abs(abs(deriv) - 1.0) < 1e-3: return "MARGINAL"
    return "ATTRACTING (stable)" if abs(deriv) < 1.0 else "REPELLING (unstable)"

print("=" * 78)
print("TEST 1 — Φ_S alone (C-averaging). Prediction: uniform d=0 ATTRACTS.")
print("=" * 78)
for a in [0.3, 0.6, 1.0]:
    f = lambda d, a=a: phi_s(d, a=a)
    fps = fixed_points_and_stability(f)
    print(f"  a={a}:  d=0 derivative f'(0) = {(f(1e-6)-f(-1e-6))/(2e-6):+.4f}  -> {classify((f(1e-6)-f(-1e-6))/(2e-6))}")
    # where does a definite start go?
    print(f"        start d=0.9 -> after 50 steps: {iterate(f,0.9,50):+.6f}  (toward 0 = toward uniform)")

print()
print("=" * 78)
print("TEST 2 — M_k alone (measurement/sharpening, beta>1). Prediction: uniform REPELS, ±1 ATTRACT.")
print("=" * 78)
for beta in [1.5, 2.0, 3.0]:
    f = lambda d, b=beta: m_k(d, beta=b)
    d0deriv = (f(1e-6) - f(-1e-6)) / (2e-6)
    print(f"  beta={beta}: f'(0) = {d0deriv:+.4f} -> {classify(d0deriv)};  start d=0.01 -> {iterate(f,0.01,200):+.6f} (toward ±1 = definite)")

print()
print("=" * 78)
print("TEST 3 — COMPETITION Φ_S∘M_k. Prediction: threshold beta*(1-a)=1 separates")
print("         einselection (uniform repels) from decoherence-free (uniform attracts).")
print("=" * 78)
for a in [0.5]:
    print(f"  Φ_S strength a={a} -> predicted critical beta* = 1/(1-a) = {1/(1-a):.3f}")
    for beta in [1.5, 2.0, 2.001, 2.5, 4.0]:
        f = lambda d, b=beta, a=a: m_k(phi_s(d, a=a), beta=b)
        d0deriv = (f(1e-6) - f(-1e-6)) / (2e-6)
        end = iterate(f, 0.001, 4000)
        regime = "EINSELECTION (-> definite)" if abs(end) > 0.5 else "DECOHERENCE-FREE (-> uniform)"
        print(f"    beta={beta:5.3f}: f'(0)={d0deriv:+.4f} [{classify(d0deriv):24s}]  d:0.001->{end:+.5f}  {regime}")

print()
print("=" * 78)
print("TEST 4 — N_sign vs N_struct. Prediction: coincide (d=0) when symmetric; separate when h≠0.")
print("=" * 78)
# N_struct = Φ_S fixed point. N_sign = critical point of the COMBINED dynamics (net pull = 0).
def net_flow(d, a=0.5, beta=2.0, h=0.0):
    return m_k(phi_s(d, a=a), beta=beta, h=h) - d   # >0 pulls right, <0 pulls left; =0 at critical pt
for h in [0.0, 0.3, 0.8]:
    # N_struct: Φ_S fixed point (independent of M_k). Φ_S(d)=（1-a)d -> d=0 always (symmetric averaging).
    nstruct = 0.0
    # N_sign: zero of net_flow nearest the interior unstable point
    f = lambda d, h=h: m_k(phi_s(d, a=0.5), beta=2.0, h=h)
    fps = fixed_points_and_stability(f)
    unstable = [d for d, dv in fps if abs(dv) > 1.0]
    nsign = unstable[0] if unstable else float('nan')
    sep = abs(nsign - nstruct)
    print(f"  h={h}: N_struct(Φ_S-harmonic)={nstruct:+.4f}  N_sign(dynamics-critical)={nsign:+.4f}  separation={sep:.4f}"
          + ("  <- COINCIDE" if sep < 1e-3 else "  <- SEPARATE (conflation exposed)"))
