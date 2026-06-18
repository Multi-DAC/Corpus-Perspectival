#!/usr/bin/env python
"""Phase C — Mathieu cavity-gain map for the portal carrier sideband (2026-06-17, Clayton drive).

The wall field oscillates: sigma(x,t)=sigma_in(x) e^{i omega t}, omega ~ m_eff -> f=556 GHz. Through the
dilatonic photon coupling e^{a sigma}F^2 it is a PERIODICALLY MODULATED birefringence element. In a cavity
the intracavity field obeys a Hill/Mathieu equation:
      a'' + 2 gamma a' + omega_c^2 [1 + h cos(omega t)] a = 0 ,   gamma = omega_c/(2F)   (F = finesse)
with per-pass modulation depth  h = a_coupling * sigma_in  (dimensionless; the paper's 'a sigma_in').

Two observables fall out (reframed for the CARRIER, since the breathing mode omega_b was falsified flat):
  (1) SIDEBAND COMB (below threshold): finesse-enhanced phase-modulation index beta = F*h; first sideband
      amplitude ~ beta/2 = F*h/2. Detectable when F*h/2 > phi_noise (state-of-art cavity phase floor ~1e-10 rad).
  (2) PARAMETRIC OSCILLATION (Mathieu instability): principal tongue at omega = 2 omega_c; threshold modulation
      h_th ~ 2/F (loss = gain). Onset when F*h > ~2 — a dramatic but far harder bar (~10 orders above the comb).

This script: plug the chameleon sigma_in(rho)=phi_min(rho) and sweep the coupling a_coupling, mapping the
threshold finesse F_thresh(rho, a) for BOTH observables, vs achievable cavities (optical F~1e6, SC microwave
F~1e11). B-field enters as an O(1) birefringence enhancement of the photon channel (noted, not over-modeled).

Honest framing (matches the paper): the cavity is a BOUND on the coupling unless a is near field-natural;
even a null is a measurement. Natural units (eV).
"""
import numpy as np

eV = 1.0; meV = 1e-3
M_PL = 2.435e27          # reduced Planck mass [eV]
LAMBDA = 2.3*meV
GCM3 = 4.31e18           # eV^4 per g/cm^3
PHI_NOISE = 1e-10        # state-of-art cavity phase floor [rad]

def phi_min(rho_eV4, n=1, beta=1.0, Lam=LAMBDA):
    return (n*Lam**(4+n)*M_PL/(beta*rho_eV4))**(1.0/(n+1))   # eV  (= sigma_in scale)

# coupling a_coupling has units 1/[field] so that a*sigma is dimensionless. Sweep by the SCALE M (a=1/M):
COUPLING_SCALES = {
    "gravitational (a=1/M_Pl)":       M_PL,
    "GUT (a=1/1e25 eV)":              1e25,
    "intermediate (a=1/1e16 eV)":     1e16,
    "TeV (a=1/1e12 eV)":              1e12,
    "keV (a=1/1e3 eV)":               1e3,
    "eV (a=1/1 eV)":                  1.0,
    "field-natural (a=1/meV)":        meV,
}
ACHIEVABLE = {"optical cavity F~1e6": 1e6, "SC microwave F~1e11": 1e11}

def F_thresh(h, kind):
    if h <= 0: return np.inf
    return (2.0/h) if kind == "parametric" else (2.0*PHI_NOISE/h)  # comb: F*h/2 > phi_noise

if __name__ == "__main__":
    print("PHASE C — Mathieu cavity-gain map for the portal carrier (f=556 GHz)")
    print("="*78)
    rho0 = 4.3*GCM3                       # the unscreening / operating density (rock-ish, n=1 beta=1)
    sig = phi_min(rho0)
    print(f"operating point: rho_0~4.3 g/cm^3 (substrate-anchored wall), sigma_in = phi_min = {sig/meV:.2f} meV")
    print(f"cavity resonance: omega=2*omega_c -> omega_c = 278 GHz (or high-order comb on an optical probe)\n")

    print(f"{'coupling a=1/M':>28} {'h=a*sigma_in':>13} {'F_thresh COMB':>14} {'F_thresh PARAM':>15}")
    print("-"*78)
    for label, M in COUPLING_SCALES.items():
        h = sig / M                       # dimensionless per-pass modulation
        Fc = F_thresh(h, "comb")
        Fp = F_thresh(h, "parametric")
        print(f"{label:>28} {h:13.2e} {Fc:14.2e} {Fp:15.2e}")
    print("-"*78)
    print(f"achievable: optical F~1e6 | SC microwave F~1e11\n")

    print("VERDICT (which couplings are reachable, COMB observable = F_thresh_comb < achievable F):")
    for label, M in COUPLING_SCALES.items():
        h = sig / M
        Fc = F_thresh(h, "comb")
        best = max(ACHIEVABLE.values())
        ok = "OBSERVABLE (comb)" if Fc < best else "out of reach"
        which = "" if Fc >= best else ("optical" if Fc < ACHIEVABLE["optical cavity F~1e6"] else "SC microwave")
        print(f"   {label:>28}: comb needs F>{Fc:.1e}  -> {ok} {which}")

    print("\nDensity dependence of the comb threshold (coupling fixed at the field-natural a=1/meV, n=1):")
    print(f"   {'rho [g/cm^3]':>14} {'sigma_in':>11} {'h':>10} {'F_thresh comb':>14}")
    for rg in [2.7, 1.0, 0.3, 1.2e-3, 1.2e-6]:
        s = phi_min(rg*GCM3); h = s/meV; Fc = F_thresh(h, "comb")
        print(f"   {rg:14.1e} {s/meV:9.2f}meV {h:10.2e} {Fc:14.2e}")
    print("\n  -> comb threshold scales as F ∝ 1/sigma_in ∝ rho^{-(n+2)/(2(n+1))} : LOWER density (lighter")
    print("     field, larger sigma_in) is EASIER to see. The low-density halo is the better cavity target.")
