"""
Cross-species occupancy — the WITHIN-METHOD test (Day 140 late drive).
Sourced pairs only; method-tagged to avoid the speed-correlated-method confound.

KEY DISTINCTION the data forces:
  (A) WITHIN one visual system across adaptation (human rod<->cone): lambda and tau trade
      off ~4x each -> mu CONSERVED (~1.5). Strong reciprocity. [sourced earlier]
  (B) ACROSS species at MATCHED adaptation, one method (insect light-adapted photoreceptor):
      tau ~constant (12-22 ms) while lambda spans ~4.6x -> mu TRACKS lambda. Weak/no reciprocity.

So: the reciprocity that pins texture is a WITHIN-SYSTEM ADAPTATION mechanism, NOT a cross-species
conservation law. Across species a real (if compressed) texture gradient exists.
"""
import numpy as np

# --- Insect set: SOLID sourced pairs (consistent method: light-adapted photoreceptor) ---
# lambda = CFFT (Hz), sourced; tau = light-adapted photoreceptor time-to-peak (ms), sourced
# (Howard/Blakeslee/Laughlin-lineage 8-insect impulse-response study; insect CFFT review).
insects_solid = [
    # name,        lambda_Hz, tau_ms,  notes
    ("housefly",     275.0,   12.0,  "CFFT ~250-300 (fly receptors ~200, fast fly ~300); ttp 12.0"),
    ("dragonfly",    300.0,   17.5,  "CFFT ~300 (fastest insect vision); ttp 17.5"),
    ("locust",        65.0,   21.9,  "CFFT 65 (migratory locust, sourced); ttp 21.9"),
]
# less-certain CFFT (tau sourced, lambda estimated from ecology) — shown, flagged, NOT in the fit
insects_soft = [
    ("drone-fly",    200.0,   16.5,  "ttp 16.5 sourced; CFFT est ~200 (fast hoverfly)"),
    ("mantid",        60.0,   18.1,  "ttp 18.1 sourced; CFFT est ~60 (ambush, slow) — UNCERTAIN"),
    ("cricket",       45.0,   22.1,  "ttp 22.1 sourced; CFFT est ~45 (nocturnal, slow) — UNCERTAIN"),
]

def mu(l, t): return l * t/1000.0

print("=== INSECT cross-species set (consistent method: light-adapted photoreceptor ttp) ===")
print(f"{'species':12s} {'lambda':>7s} {'tau(ms)':>8s} {'mu=lt':>7s}")
solid = []
for n,l,t,_ in insects_solid:
    m = mu(l,t); solid.append((l,t,m))
    print(f"{n:12s} {l:7.0f} {t:8.1f} {m:7.2f}   SOLID")
for n,l,t,_ in insects_soft:
    print(f"{n:12s} {l:7.0f} {t:8.1f} {mu(l,t):7.2f}   (soft, lambda est)")

lam = np.array([s[0] for s in solid]); tau = np.array([s[1] for s in solid]); muv = np.array([s[2] for s in solid])
print("\n--- SOLID insect pairs (n=3) ---")
print(f"  lambda spans {lam.min():.0f}-{lam.max():.0f} Hz  (x{lam.max()/lam.min():.1f})")
print(f"  tau    spans {tau.min():.1f}-{tau.max():.1f} ms  (x{tau.max()/tau.min():.1f})")
print(f"  mu     spans {muv.min():.2f}-{muv.max():.2f}    (x{muv.max()/muv.min():.1f})")
print(f"  => tau compresses lambda's {lam.max()/lam.min():.1f}x only to mu's {muv.max()/muv.min():.1f}x.")
# does mu track lambda? (reciprocity would make them uncorrelated / mu flat)
r = np.corrcoef(lam, muv)[0,1]
print(f"  corr(lambda, mu) = {r:+.2f}  (reciprocity-conservation would give ~0; tracking gives ~+1)")

print("\n=== CONTRAST: within-system human rod<->cone (one eye, one method) ===")
print("  rod : lambda 15, tau 100 -> mu 1.50")
print("  cone: lambda 60, tau  25 -> mu 1.50    (lambda x4 up, tau x4 down, mu CONSERVED)")

print("\n=== VERDICT ===")
print("  Reciprocity (mu conserved) is REAL but it is a WITHIN-SYSTEM ADAPTATION mechanism")
print("  (an eye trades speed<->sensitivity as it adapts, holding its OWN texture ~constant).")
print("  ACROSS species at matched adaptation, tau is ~clade-constant and mu TRACKS lambda:")
print("  a real texture gradient exists (dragonfly mu~5 >> cricket/locust mu~1).")
print("  => H-occ-1 'mu conserved across species / animals share one band' is PARTIALLY FALSIFIED.")
print("  => Defensible claim: texture = mu = lambda*tau (NOT lambda alone), and across the FULL")
print("     kingdom tau compresses the gradient (lambda ~75x -> mu maybe ~5-10x) but does NOT")
print("     erase it. The naive 'fast eyes = proportional slow-motion' is still wrong; the strong")
print("     'all animals share one now' is also wrong. Truth is the compressed middle.")
