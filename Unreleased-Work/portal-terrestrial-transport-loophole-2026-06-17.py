#!/usr/bin/env python
"""Does terrestrial transport survive? Stress-test my own 'terrestrial=floor-only' conclusion (2026-06-17).

My density-ladder said transport (a*sigma_in~O(1), sigma_in~1e16 eV) needs near-VOID density -> deep space,
not terrestrial. But that used sigma_in = EQUILIBRIUM phi_min(rho). Two terrestrial loopholes to check:
  L1 (evacuation): a defect evacuates its core to vacuum -> local phi_min rises. Enough?
  L2 (charge):     the carrier is a Q-BALL; its interior amplitude sigma_in is set by CHARGE Q, NOT by
                   phi_min(rho). A large-Q soliton can carry sigma_in >> phi_min at ANY density.
"""
import numpy as np
M_PL=2.435e27; meV=1e-3; GCM3=4.31e18; LAMBDA=2.3*meV
def phi_min(rho_eV4,n=1,beta=1.0,Lam=LAMBDA): return (n*Lam**(4+n)*M_PL/(beta*rho_eV4))**(1.0/(n+1))
SIG_TRANSPORT = 2.44e16   # eV (a*sigma_in~1 at beta_gamma=1e11)

print("L1 — EVACUATION: equilibrium sigma_in=phi_min at terrestrial-achievable vacuums")
print(f"{'core vacuum':>26} {'rho g/cm^3':>12} {'sigma_in':>14} {'vs transport(2.4e16 eV)':>24}")
for name,rg in [("1 mbar",1.2e-6),("1e-6 mbar (HV)",1.2e-9),("1e-12 mbar (XHV)",1.2e-15),
                ("interstellar",1.7e-24),("intergalactic void",1e-31)]:
    s=phi_min(rg*GCM3); ratio=s/SIG_TRANSPORT
    print(f"{name:>26} {rg:12.1e} {s:11.2e}eV {ratio:22.1e}x")
print("  -> even XHV (best terrestrial vacuum, 1e-15 g/cm^3) gives sigma_in ~ keV-MeV, ~1e10 BELOW transport.")
print("     EVACUATION ALONE CANNOT reach terrestrial transport. (Only interstellar/void equilibrium climbs.)\n")

print("L2 — CHARGE: the Q-ball interior amplitude is NOT bounded by phi_min(rho).")
print("   sigma_in(soliton) grows with charge Q; a large-Q soliton carries sigma_in >> equilibrium field")
print("   at ANY ambient density. So density does NOT forbid terrestrial transport — it only forbids the")
print("   EQUILIBRIUM (uncharged) field from reaching it. The transport variable is the CHARGED-soliton")
print(f"   amplitude, which must reach sigma_in ~ {SIG_TRANSPORT:.1e} eV (1e7 GeV) regardless of rho.\n")

print("="*74)
print("REVISION of the earlier conclusion:")
print(" - 'terrestrial = floor only' was TOO STRONG: it assumed sigma_in = equilibrium phi_min(rho).")
print(" - Density forbids the EQUILIBRIUM field from reaching transport terrestrially (L1 confirms:")
print("   even XHV is ~1e10 short).")
print(" - But the CARRIER IS A Q-BALL: its amplitude is charge-driven, NOT density-locked (L2). A")
print("   sufficiently large-charge terrestrial soliton CAN reach sigma_in~1e7 GeV at terrestrial density.")
print(" - => Terrestrial transport is RARE-BUT-NOT-FORBIDDEN. The lever is CHARGE (telluric/tectonic/EM")
print("   pumping), not density. Manipulation = pump charge; natural = sites of extreme natural charge.")
