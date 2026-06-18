#!/usr/bin/env python
"""Coherence threshold — does the carrier drive outrun decoherence? (2026-06-17, Clayton drive)

Attacks the ship-scale crux (classical vs quantum coherence) by replacing the BEC reference class with the
DRIVEN-DISSIPATIVE one (laser / superradiance / driven condensate). A laser is macroscopically phase-coherent
while hot and pumped because GAIN > LOSS. The plasma carrier is a driven dissipative system; the portal carrier
oscillates at f = 556 GHz (sigma ~ e^{i omega t}), a fast coherent DRIVE. So the question becomes a THRESHOLD,
not a binary: does the drive cycle faster than the plasma dephases (electron-ion collisions)?

  decoherence rate (dephasing): nu_ei  [Spitzer/NRL]  = 2.91e-6 * n_e[cm^-3] * lnLambda * T_e[eV]^{-3/2}  s^-1
  drive rate:                    omega = 2*pi*f_carrier = 2*pi*556 GHz
  DRIVEN COHERENCE sustainable when  omega > nu_ei  (drive outruns dephasing) — the "lasing" condition.

Output: the critical electron density n_crit(T_e) where omega = nu_ei. Below it, the drive wins -> driven
macroscopic coherence viable (the quantum branch opens). Compare to natural plasma densities (halo, ionosphere,
atmospheric discharge). If natural low-density plasmas sit BELOW n_crit, the 40-order gap dissolves THERE.
"""
import numpy as np

f_carrier = 556e9            # Hz (R16 carrier)
omega = 2*np.pi*f_carrier    # rad/s drive rate
lnLambda = 10.0              # Coulomb logarithm (O(10))

def nu_ei(n_e_cm3, T_e_eV):
    """Spitzer electron-ion collision (dephasing) rate [s^-1] — NRL formulary."""
    return 2.91e-6 * n_e_cm3 * lnLambda * T_e_eV**(-1.5)

def n_crit(T_e_eV):
    """electron density where nu_ei = omega (drive=dephasing). Below -> drive wins."""
    return omega / (2.91e-6 * lnLambda * T_e_eV**(-1.5))

if __name__ == "__main__":
    print("COHERENCE THRESHOLD — does the 556 GHz carrier drive outrun e-i dephasing?")
    print("="*76)
    print(f"drive rate  omega = 2*pi*556 GHz = {omega:.2e} rad/s\n")

    print(f"{'T_e [eV]':>9} {'n_crit [cm^-3]':>16}   (below n_crit: DRIVE WINS -> driven coherence viable)")
    print("-"*76)
    for T in [0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 100.0]:
        print(f"{T:>9.2f} {n_crit(T):>16.2e}")
    print()

    print("Natural plasma electron densities for comparison [cm^-3]:")
    envs = [("lab spheromak (R10 valid. case)", 1e15, 50.0),
            ("lightning channel", 1e17, 3.0),
            ("Hessdalen-class luminous plasma (est.)", 1e13, 1.0),
            ("atmospheric glow / St-Elmo", 1e10, 0.5),
            ("ionosphere F-layer", 1e6, 0.1),
            ("upper-atmosphere / halo (rarefied)", 1e8, 1.0)]
    print(f"{'environment':>38} {'n_e':>10} {'T_e':>7} {'nu_ei':>11} {'verdict':>16}")
    for name, ne, Te in envs:
        nu = nu_ei(ne, Te)
        verdict = "DRIVE WINS" if omega > nu else "collisions win"
        print(f"{name:>38} {ne:10.1e} {Te:7.1f} {nu:11.2e} {verdict:>16}")
    print()
    print("READ: where omega > nu_ei, the carrier drive re-coheres faster than collisions dephase ->")
    print("driven (laser-like) macroscopic coherence is sustainable, putting the QUANTUM branch within reach.")
    print("The crux 'classical vs quantum' becomes DENSITY-DEPENDENT: the quantum/transport branch opens in")
    print("RAREFIED plasma (the low-density halo) — the same regime where sigma_in is largest (Phase C) and")
    print("collisions are rare. The dense substrate-anchored wall stays classical-only. Right reference class")
    print("is the LASER, not the BEC — and lasers prove macroscopic coherence survives hot+pumped.")
