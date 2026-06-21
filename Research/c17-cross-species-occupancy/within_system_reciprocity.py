"""
C17 reciprocity — WITHIN-SYSTEM test (human rod <-> cone). Day 140 (2026-06-20).

Why within-system: the cross-species fit fails for a sourcing reason, not a model reason —
the comparative literature reports CFF and integration time SEPARATELY, "no species with both"
(Temporal vision: measures/mechanisms/meaning, J Exp Biol 224:jeb222679, 2021). So we test the
SAME hinge (is occupancy mu=lambda*tau invariant when lambda changes?) inside ONE well-
characterized system where both axes are measured in the same eye: the human rod->cone shift.

SOURCED numbers (NCBI Webvision, 'Temporal Resolution', Bookshelf NBK11559; corroborated by the
PLOS-One systematic review on CFF, 2023):
  lambda (CFF):   rod/scotopic ~15 Hz   ;  cone/photopic ~60 Hz   (4x rise)
  tau (Bloch critical duration): rod ~100 ms ; cone ~10-50 ms (fast cones 10-15 ms,
       L-cone ~50 ms; classic photopic Bloch ~20-50 ms)
"""
import numpy as np

def mu(lam_hz, tau_ms): return lam_hz * (tau_ms/1000.0)
def gap(m): return np.exp(-m)

# Rod (scotopic): well-agreed values
rod_lam, rod_tau = 15.0, 100.0          # Hz, ms
# Cone (photopic): lambda well-agreed; tau has a real spread across cone types
cone_lam = 60.0
cone_tau_lo, cone_tau_mid, cone_tau_hi = 15.0, 25.0, 50.0   # ms

rod_mu = mu(rod_lam, rod_tau)
cone_mu_lo, cone_mu_mid, cone_mu_hi = (mu(cone_lam, t) for t in (cone_tau_lo, cone_tau_mid, cone_tau_hi))

print("=== Human rod -> cone reciprocity (within one retina) ===")
print(f"{'':8s} {'lambda(Hz)':>10s} {'tau(ms)':>10s} {'mu=lam*tau':>12s} {'gap=e^-mu':>10s}")
print(f"{'ROD':8s} {rod_lam:10.0f} {rod_tau:10.0f} {rod_mu:12.2f} {gap(rod_mu):10.3f}")
print(f"{'CONE':8s} {cone_lam:10.0f} {cone_tau_mid:7.0f} (15-50) {cone_mu_mid:9.2f} {gap(cone_mu_mid):10.3f}"
      f"   [mu range {cone_mu_lo:.2f}-{cone_mu_hi:.2f}]")

print("\n--- the hinge ---")
print(f"  lambda changes {cone_lam/rod_lam:.0f}x  (15 -> 60 Hz)")
print(f"  tau changes    {rod_tau/cone_tau_mid:.0f}x the other way (100 -> 25 ms, central)")
print(f"  => mu (central): rod {rod_mu:.2f}  vs  cone {cone_mu_mid:.2f}   ratio {cone_mu_mid/rod_mu:.2f}")
print(f"  => mu stays O(1) across the transition; with the honest cone-tau spread,")
print(f"     cone mu in [{cone_mu_lo:.2f}, {cone_mu_hi:.2f}] BRACKETS rod {rod_mu:.2f}.")
print(f"  NAIVE expectation (texture tracks lambda): cone vision {cone_lam/rod_lam:.0f}x finer than rod.")
print(f"  C17 (texture tracks mu=lambda*tau): essentially UNCHANGED ({cone_mu_mid/rod_mu:.1f}x).")

print("\n--- honest grade ---")
print("  SOURCED, within-system, n=2 regimes of one eye. Rod mu (1.5) is tight; cone mu spreads")
print("  0.9-3.0 with cone-type (which tau is 'the' binding window is a real modeling choice).")
print("  CLAIM EARNED: occupancy stays O(1) while lambda swings 4x -> the reciprocity is real in")
print("  the one system where both axes are co-measured. CLAIM NOT EARNED: cross-species conservation")
print("  (needs paired data the field hasn't compiled) or a precise conserved constant.")
