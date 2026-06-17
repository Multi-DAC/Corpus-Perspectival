"""
Portal gauged-soliton existence test (the R4 gap).
Day 136 creative drive. Does the dilatonic radion + confined-charge system admit a
LOCALIZED energy minimum at fixed charge Q — an actual exhibited soliton scale — or does
it collapse/disperse? R4 proved only the virial NECESSARY condition by scaling; this tests
sufficiency with real radial integrals and real Gauss's law (dilatonic e^{a sigma}).

Model (dimensionless; radion mass m=1 sets the scale, lengths in 1/m, energies in m):
  - Radion bubble profile:  sigma(r) = sigma0 * 0.5*(1 - tanh((r-R)/w))   (depth sigma0, radius R, wall w)
  - Radion potential energy: E_pot = INT 0.5 m^2 sigma^2 * 4 pi r^2 dr     (displaced from vacuum, POSITIVE)
  - Radion gradient energy:  E_grad = INT 0.5 (sigma')^2 * 4 pi r^2 dr     (wall tension)
  - Charge Q confined uniformly in r<R; Gauss with dilatonic coupling:
        e^{a sigma} E * 4 pi r^2 = Q_enc(r)  ->  E(r) = Q_enc/(4 pi r^2 e^{a sigma})
        E_EM = INT 0.5 e^{a sigma} E^2 * 4 pi r^2 dr = (1/8pi) INT Q_enc^2/(r^2 e^{a sigma}) dr
  Minimize E_tot(R, sigma0, w; Q, a) over (R, sigma0, w). Finite interior minimum => soliton exists.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad

m = 1.0  # radion mass (sets units)

def profile(r, sigma0, R, w):
    return sigma0 * 0.5 * (1.0 - np.tanh((r - R) / w))

def dprofile(r, sigma0, R, w):
    # d/dr of the tanh bubble
    return sigma0 * 0.5 * (-1.0 / w) * (1.0 / np.cosh((r - R) / w) ** 2)

def energies(R, sigma0, w, Q, a):
    rmax = R + 12.0 * w + 5.0
    # radion gradient + potential (numerical radial integrals)
    Eg = quad(lambda r: 0.5 * dprofile(r, sigma0, R, w) ** 2 * 4 * np.pi * r ** 2, 0, rmax, limit=200)[0]
    Ep = quad(lambda r: 0.5 * m ** 2 * profile(r, sigma0, R, w) ** 2 * 4 * np.pi * r ** 2, 0, rmax, limit=200)[0]
    # enclosed charge: uniform density inside R
    def Qenc(r):
        return Q * min(1.0, (r / R) ** 3)
    # EM energy with dilatonic coupling (Gauss solved for fixed charge)
    def emdens(r):
        s = profile(r, sigma0, R, w)
        return (Qenc(r) ** 2) / (8 * np.pi * r ** 2 * np.exp(a * s))
    Eem = quad(emdens, 1e-6, rmax, limit=400)[0]
    return Eg, Ep, Eem

def Etot(params, Q, a):
    R, sigma0, w = params
    if R <= 0.05 or w <= 0.02 or w > R * 4:
        return 1e9
    Eg, Ep, Eem = energies(R, sigma0, w, Q, a)
    return Eg + Ep + Eem

def find_soliton(Q, a, x0=(2.0, 1.0, 0.5)):
    res = minimize(Etot, x0, args=(Q, a), method="Nelder-Mead",
                   options=dict(xatol=1e-4, fatol=1e-6, maxiter=4000))
    R, sigma0, w = res.x
    Eg, Ep, Eem = energies(R, sigma0, w, Q, a)
    virial_lhs = Eem
    virial_rhs = Eg + 3 * Ep
    return dict(R=R, sigma0=sigma0, w=w, Eg=Eg, Ep=Ep, Eem=Eem, Etot=res.x.size and (Eg+Ep+Eem),
                virial_lhs=virial_lhs, virial_rhs=virial_rhs,
                virial_resid=(virial_lhs - virial_rhs) / (abs(virial_rhs) + 1e-9), ok=res.success)

if __name__ == "__main__":
    print("Gauged-soliton existence — dilatonic radion + confined charge")
    print("=" * 74)
    # 1) scan E(R) at fixed (sigma0,w,Q,a) to see the shape (collapse? minimum? spread?)
    print("\n[1] E(R) shape at sigma0=1, w=0.5, Q=10, a=0.5 (look for interior minimum):")
    for R in [0.3, 0.5, 1, 1.5, 2, 3, 4, 6, 9]:
        Eg, Ep, Eem = energies(R, 1.0, 0.5, 10.0, 0.5)
        print(f"   R={R:4.1f}  Eg={Eg:8.2f} Ep={Ep:9.2f} Eem={Eem:8.2f}  Etot={Eg+Ep+Eem:9.2f}")
    # 2) full minimization for several charges, check virial + size scaling
    print("\n[2] Minimized soliton vs charge Q (a=0.5):")
    print(f"   {'Q':>5} {'R*':>7} {'sigma0':>7} {'w':>6} {'Eg':>8} {'Ep':>8} {'Eem':>8} {'virial resid':>12}")
    Qs = [5, 10, 20, 40, 80]
    Rs = []
    for Q in Qs:
        d = find_soliton(Q, 0.5)
        Rs.append(d["R"])
        print(f"   {Q:5.0f} {d['R']:7.3f} {d['sigma0']:7.3f} {d['w']:6.3f} "
              f"{d['Eg']:8.2f} {d['Ep']:8.2f} {d['Eem']:8.2f} {d['virial_resid']:12.2e}")
    # size scaling exponent R* ~ Q^p
    lnQ = np.log(Qs); lnR = np.log(Rs)
    p = np.polyfit(lnQ, lnR, 1)[0]
    print(f"\n   size scaling  R* ~ Q^{p:.3f}   (thin-wall gauged soliton expectation ~ Q^(1/3)=0.333)")
    # 3) dilatonic coupling dependence
    print("\n[3] Dilatonic coupling a-dependence (Q=20):")
    for a in [-1.0, -0.5, 0.0, 0.5, 1.0, 2.0]:
        d = find_soliton(20.0, a)
        print(f"   a={a:+4.1f}  R*={d['R']:6.3f}  sigma0={d['sigma0']:+6.3f}  Etot={d['Eg']+d['Ep']+d['Eem']:8.2f}"
              f"  virial_resid={d['virial_resid']:9.2e}")
