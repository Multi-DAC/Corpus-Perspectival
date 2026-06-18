#!/usr/bin/env python
"""Close Gap 1 — does the carrier drive outrun the FULL decoherence spectrum? (2026-06-17, Clayton)

The coherence-threshold result showed omega(556GHz) >> nu_ei (e-i collisions). But collisions are the
dominant, not the only, decoherence channel. Race the drive against ALL of them:
  - collisional       nu_ei  = 2.91e-6 n_e lnL T^{-1.5}                       [Spitzer/NRL]
  - bremsstrahlung    nu_br  ~ 7.1e-14 n_e T^{-0.5}  (radiative cooling rate)
  - recombination     nu_rec = 2.7e-13 T^{-0.75} n_e (radiative recomb)
  - turbulent/Alfven  nu_A   = v_A / L,  v_A=2.18e11 B[G]/sqrt(n_i)  cm/s
Drive: omega = 2*pi*556 GHz = 3.49e12 rad/s. Gap 1 closes if omega >> every channel.
(n_e cm^-3, T_e eV, B Gauss, L cm.)
"""
import numpy as np

omega = 2*np.pi*556e9
lnL = 10.0

def rates(n_e, T, B=10.0, L=1e5):     # L=1km=1e5 cm
    nu_ei  = 2.91e-6 * n_e * lnL * T**(-1.5)
    nu_br  = 7.1e-14 * n_e * T**(-0.5)
    nu_rec = 2.7e-13 * T**(-0.75) * n_e
    v_A    = 2.18e11 * B / np.sqrt(max(n_e,1.0))   # cm/s (n_i~n_e, H)
    nu_A   = v_A / L
    return {"collisional": nu_ei, "bremsstrahlung": nu_br, "recombination": nu_rec, "turbulent/Alfven": nu_A}

if __name__ == "__main__":
    print("GAP 1 — drive vs the FULL decoherence spectrum (omega = 3.49e12 rad/s)")
    print("="*74)
    cases = [("Hessdalen-class luminous", 1e13, 1.0),
             ("rarefied halo",           1e8,  1.0),
             ("lab spheromak (R10)",     1e15, 50.0),
             ("lightning channel",       1e17, 3.0)]
    for name, ne, Te in cases:
        r = rates(ne, Te)
        fastest = max(r.values())
        print(f"\n{name}  (n_e={ne:.0e} cm^-3, T_e={Te} eV):")
        for ch, v in r.items():
            print(f"   {ch:>18}: {v:10.2e} s^-1   omega/rate = {omega/v:8.1e}")
        print(f"   {'-> FASTEST channel':>18}: {fastest:10.2e} s^-1   DRIVE MARGIN = {omega/fastest:.1e}x  "
              f"{'(DRIVE WINS)' if omega>fastest else '(decoherence wins)'}")

    print("\n" + "="*74)
    print("READ: if the drive margin > 1 for the FASTEST channel in each regime, the carrier drive outruns")
    print("the ENTIRE decoherence spectrum, not just collisions -> Gap 1 closed across natural plasma regimes")
    print("(it reopens only at near-solid density, the classical substrate wall).")
