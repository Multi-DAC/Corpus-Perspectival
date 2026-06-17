#!/usr/bin/env python
"""
Do-Be-Talk-Be-Do drive (2026-06-17 ~09:10): COMPUTE the translational pinning mode omega_pin
of the gauged Q-ball in an explicit screening gradient -- the quantitative replacement for the
BREATHING mode that last night's dream-drive FALSIFIED (it was rho-flat; see
dynamical-qball-breathing-2026-06-17.py). This is the genuine place-localization boundary-mapper
named in experience #130 and the paper's section 8 -- currently ASSERTED there, not computed.

PHYSICS (Manton rigid-soliton / collective-coordinate, leading order):
  A soliton (lump) sigma(x) in a homogeneous background has a TRANSLATIONAL ZERO MODE (Goldstone of
  broken translation): it can drift for free. That is why a free soliton is NOT pinned to a place.
  Now let the chameleon mass vary in space because the ambient density varies:
        m^2(x) = m0^2 [1 + alpha * f(x)]          (f tracks the density contrast of "a place")
  This explicitly breaks translation. Treat the soliton center X as a collective coordinate (rigid
  profile, Manton approx). The only X-dependent piece of the energy is
        V_eff(X) = (1/2) alpha m0^2 INT f(x) sigma(x-X)^2 dx        = (1/2) alpha m0^2 (f * sigma^2)(X)
  i.e. the density-contrast profile CONVOLVED with the soliton's density. The translational inertia
  (from the kinetic term (1/2)(d_t phi)^2 -> (1/2) M Xdot^2) is the standard soliton mass
        M = INT sigma'(x)^2 dx .
  Small oscillations about the minimum X0:   omega_pin^2 = V_eff''(X0) / M .

PREDICTIONS (logged 09:10, before running):
  P1 (high):      pocket f=-sech^2(x/L) pins the lump at X=0, V_eff''>0, omega_pin finite>0.
  P2 (high):      omega_pin^2 ~ alpha (linear) -> omega_pin ~ sqrt(alpha) -> 0 as contrast vanishes.
  P3 (med-high):  omega_pin -> 0 as L -> infinity (contrast spread over large scale = locally uniform).
  P4 (medium):    monotonic step f=tanh(x/L) gives NO interior minimum -> lump slides -> no pinning.
                  => place-pinning needs a density EXTREMUM (curvature), not just a gradient. (refines LC45)
  P5 (medium):    the lump localizes in the LOW-m^2 (low-density, UNSCREENED) region -> portals at
                  voids / low-density pockets (a falsifiable geological signature).
"""
import numpy as np

# ---------- soliton profile (a clean 1D lump; the scaling result is profile-independent) ----------
SIGMA_IN = 1.0
W        = 1.0                                  # soliton width
def sigma(x, X=0.0):    return SIGMA_IN / np.cosh((x - X) / W)          # sech lump
def dsigma(x, X=0.0):   return -(SIGMA_IN / W) * np.sinh((x - X)/W) / np.cosh((x - X)/W)**2

# spatial grid (wide enough that the lump + its excursions are fully captured)
x = np.linspace(-60, 60, 24001)
dx = x[1] - x[0]
M_inertia = np.trapezoid(dsigma(x)**2, dx=dx)   # translational inertia M = INT sigma'^2 dx
print(f"soliton inertia  M = INT sigma'^2 dx = {M_inertia:.6f}   (sech lump, w={W})")

# ---------- density-contrast profiles f(x) ----------
def f_pocket(xx, L):  return -1.0 / np.cosh(xx / L)**2      # low-density VOID centered at 0 (m^2 dips)
def f_step(xx, L):    return np.tanh(xx / L)                # monotonic density boundary (pure gradient)

m0 = 1.0

def Veff(X, alpha, L, fprofile):
    """X-dependent collective-coordinate potential (1/2) alpha m0^2 INT f(x) sigma(x-X)^2 dx."""
    return 0.5 * alpha * m0**2 * np.trapezoid(fprofile(x, L) * sigma(x, X)**2, dx=dx)

def omega_pin(alpha, L, fprofile, Xspan=8.0, nX=4001):
    """Find X0=argmin Veff, curvature there, and omega_pin = sqrt(Veff''/M). Returns dict."""
    Xs = np.linspace(-Xspan, Xspan, nX)
    Vs = np.array([Veff(X, alpha, L, fprofile) for X in Xs])
    i = int(np.argmin(Vs))
    interior = 0 < i < len(Xs) - 1
    # local parabola fit for X0 and curvature
    sl = slice(max(0, i-40), min(len(Xs), i+41))
    p = np.polyfit(Xs[sl], Vs[sl], 2)
    X0 = -p[1] / (2*p[0]); Vpp = 2*p[0]
    pinned = interior and Vpp > 0
    w2 = Vpp / M_inertia
    return dict(X0=X0, Vpp=Vpp, w2=w2,
                w=(np.sqrt(w2) if (pinned and w2 > 0) else float('nan')),
                pinned=pinned, Vmin=Vs[i], Xmin=Xs[i])

# ============================ P1 + P5: does a pocket pin, and WHERE? ============================
print("\n=== P1/P5: density POCKET  f=-sech^2(x/L),  alpha=0.3, L=3  (lump should pin at a LOW-m^2 spot) ===")
d = omega_pin(0.3, 3.0, f_pocket)
print(f"  X0={d['X0']:+.4f}  Veff''={d['Vpp']:+.5f}  omega_pin={d['w']:.5f}  pinned={d['pinned']}")
print(f"  m^2 at the pin (X0): {m0**2*(1+0.3*f_pocket(d['X0'],3.0)):.4f}  vs far-field m^2={m0**2:.4f}"
      f"   -> sits in {'LOW' if (1+0.3*f_pocket(d['X0'],3.0))<1 else 'HIGH'}-density region  [P5]")

# ============================ P2: omega_pin vs contrast alpha ============================
print("\n=== P2: omega_pin vs contrast alpha  (pocket, L=3)   expect omega^2 ~ alpha (slope-1 in log-log) ===")
alphas = np.array([0.02, 0.05, 0.1, 0.2, 0.4, 0.8])
w2s = []
for al in alphas:
    di = omega_pin(al, 3.0, f_pocket)
    w2s.append(di['w2'])
    print(f"  alpha={al:5.2f}  omega_pin^2={di['w2']:.6e}  omega_pin={di['w']:.5f}")
w2s = np.array(w2s)
slope = np.polyfit(np.log(alphas), np.log(w2s), 1)[0]
print(f"  log-log slope of omega_pin^2 vs alpha = {slope:.4f}   (P2 predicts 1.000: omega_pin ~ sqrt(alpha))")

# ============================ P3: omega_pin vs pocket width L (flatten the contrast) ============================
print("\n=== P3: omega_pin vs pocket width L  (alpha=0.3)   expect omega_pin -> 0 as L -> infinity ===")
Ls = np.array([1.0, 2.0, 4.0, 8.0, 16.0, 32.0])
for L in Ls:
    di = omega_pin(0.3, L, f_pocket, Xspan=min(8.0, 3*L), nX=4001)
    print(f"  L={L:5.1f}  omega_pin={di['w']:.6f}  Veff''={di['Vpp']:+.6e}")

# ============================ P4: a monotonic STEP -- does a pure gradient pin? ============================
print("\n=== P4: monotonic STEP f=tanh(x/L), alpha=0.3, L=3  (pure gradient, NO extremum) ===")
Xs = np.linspace(-30, 30, 6001)
Vs = np.array([Veff(X, 0.3, 3.0, f_step) for X in Xs])
i = int(np.argmin(Vs))
ran_to_edge = (i == 0 or i == len(Xs)-1)
print(f"  argmin at X={Xs[i]:+.2f}  ({'RAN TO BOUNDARY -> slides, NOT pinned' if ran_to_edge else 'interior min'})")
print(f"  Veff monotone? min at edge={ran_to_edge}; Veff(-30)={Vs[0]:+.4f}  Veff(+30)={Vs[-1]:+.4f}")
print(f"  => a pure gradient does NOT pin; place-localization needs a density EXTREMUM (curvature). [P4 -> sharpens LC45]")

print("\n" + "="*78)
print("SYNTHESIS: omega_pin = sqrt( Veff''(X0)/M ), Veff''(X0) = (1/2) alpha m0^2 (f*sigma^2)''(X0).")
print("It vanishes as alpha->0 (P2: ~sqrt(alpha)) OR L->inf (P3): BOTH are 'flatten the contrast'.")
print("A step does not pin (P4): the place is a density EXTREMUM, and omega_pin is set by the CURVATURE")
print("of the screening profile convolved with the soliton. This is the computed backbone of section 8.")
