#!/usr/bin/env python
"""Quantitative carrier-blueshift densitometer — REAL chameleon, not the toy (2026-06-17, Clayton drive).

Replaces the toy m^2 = m0^2(1+rho/rho*) of portal-fixedQ-carrier with the ACTUAL screened-scalar physics
the portal paper identifies: a CHAMELEON at the dark-energy scale Lambda = (rho_Lambda)^{1/4} = 2.3 meV
(Khoury-Weltman). Goal: publishable numbers for the densitometer + find the unscreening density rho_0.

Chameleon: V(phi) = Lambda^{4+n}/phi^n  +  beta*rho*phi/M_Pl   (runaway + matter coupling)
  field minimum:   phi_min(rho) = ( n Lambda^{4+n} M_Pl / (beta rho) )^{1/(n+1)}
  effective mass:  m_eff^2(rho) = V''(phi_min) = n(n+1) Lambda^{4+n} / phi_min^{n+2}
  => m_eff(rho) ∝ rho^{(n+2)/(2(n+1))}   -> the densitometer EXPONENT S = (n+2)/(2(n+1)) (exact, parameter-free)

Carrier (Q-ball internal rotation, omega ~ m_eff):  f = m_eff c^2 / h.  At m_eff = 2.3 meV -> f = 556 GHz.
Densitometer: f(rho) ∝ rho^S near the operating point; S in [0.5,0.75]. The portal exists (macroscopic
0.085 mm wall) only where m_eff <~ 2.3 meV, i.e. where the field is UNSCREENED -> rho <~ rho_0.

Everything in natural units (eV). Honest caveat: absolute rho_0 depends on O(1) choices (n, beta, Lambda
convention); the EXPONENT S and the qualitative threshold are robust; absolute rho_0 is order-of-magnitude.
"""
import numpy as np

# --- constants (natural units, eV) ---
eV = 1.0
meV = 1e-3
M_PL = 2.435e27          # reduced Planck mass [eV]
LAMBDA = 2.3 * meV       # dark-energy scale (rho_Lambda)^{1/4} [eV]
H_EV_S = 4.135667696e-15 # Planck constant [eV*s]  (f = E/h)
GHZ = 1e9

# density conversion: 1 g/cm^3 = 4.31e18 eV^4
GCM3 = 4.31e18           # eV^4 per (g/cm^3)

def f_of_meff(m_eV):
    """carrier frequency f = m c^2 / h for m in eV -> Hz."""
    return m_eV / H_EV_S

def chameleon(rho_eV4, n=1, beta=1.0, Lam=LAMBDA):
    """Return (phi_min, m_eff) in eV for matter density rho [eV^4]."""
    Lam_pow = Lam**(4 + n)                                   # eV^{4+n}
    phi_min = (n * Lam_pow * M_PL / (beta * rho_eV4))**(1.0/(n+1))   # eV
    m_eff2 = n*(n+1) * Lam_pow / phi_min**(n+2)              # eV^2
    return phi_min, np.sqrt(m_eff2)

def S_exponent(n):
    return (n+2)/(2*(n+1))

def find_rho0(n=1, beta=1.0, Lam=LAMBDA, target=2.3*meV):
    """density rho_0 [g/cm^3] at which m_eff = target (the unscreening threshold)."""
    # m_eff ∝ rho^S, so solve directly from one evaluation
    rho_ref = 1.0 * GCM3                                     # 1 g/cm^3 reference
    _, m_ref = chameleon(rho_ref, n, beta, Lam)
    S = S_exponent(n)
    rho0_eV4 = rho_ref * (target/m_ref)**(1.0/S)
    return rho0_eV4 / GCM3

if __name__ == "__main__":
    print("QUANTITATIVE CHAMELEON DENSITOMETER (Lambda = 2.3 meV dark-energy scale)")
    print("="*76)
    print(f"carrier at m_eff=2.3 meV:  f = {f_of_meff(2.3*meV)/GHZ:.1f} GHz  (paper's R16 = 556 GHz)\n")

    print("Densitometer sensitivity  S = dln f / dln rho = (n+2)/(2(n+1)):")
    for n in (1,2,4,10):
        print(f"   n={n:2d}:  S = {S_exponent(n):.3f}")
    print("   (toy m^2∝(1+rho/rho*) gave S≈0.3–0.45 — it UNDER-estimated; real chameleon is stiffer→more sensitive)\n")

    print("Unscreening density rho_0 (where m_eff falls to 2.3 meV → macroscopic portal turns on):")
    for n in (1,2,4):
        for beta in (1.0, 10.0):
            r0 = find_rho0(n=n, beta=beta)
            print(f"   n={n}, beta={beta:4.0f}:  rho_0 = {r0:.2e} g/cm^3")
    print()

    print(f"{'environment':>22} {'rho [g/cm^3]':>13} {'m_eff':>12} {'f carrier':>12}  (n=1, beta=1)")
    print("-"*76)
    envs = [("rock", 2.7), ("water", 1.0), ("sea-level air", 1.2e-3),
            ("rough vacuum 1 mbar", 1.2e-6), ("high vac 1e-6 mbar", 1.2e-9),
            ("ISM (~1 H/cc)", 1.7e-24), ("cosmic mean", 9.5e-30)]
    for name, rg in envs:
        _, m = chameleon(rg*GCM3, n=1, beta=1.0)
        fc = f_of_meff(m)
        # human-readable mass + freq
        mstr = f"{m/meV:.2e} meV" if m < 1 else f"{m:.2e} eV"
        fstr = f"{fc/GHZ:.2e} GHz"
        print(f"{name:>22} {rg:13.1e} {mstr:>12} {fstr:>12}")

    print("\nDensitometer at the operating point (near rho_0, n=1, S=0.75):")
    print("   a 10% local density change -> 0.75*10% = 7.5% carrier shift = ~42 GHz at 556 GHz")
    print("   trivially resolved by a sub-mm spectrometer (GHz resolution).")
