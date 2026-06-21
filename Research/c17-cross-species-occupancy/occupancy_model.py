"""
C17 cross-species occupancy model — the reciprocity test.
Day 140 (2026-06-20). FIRST PASS / ILLUSTRATIVE — per-species pairs are literature-anchored
ranges pending primary-source verification (see DATA_SOURCING_PLAN). The MODEL and the
RECIPROCITY framing are rigorous; the per-species precision is not yet earned.

C17: experienced temporal texture is governed by occupancy  mu = lambda * tau
  lambda = informative-measurement (sampling) rate     ~ critical flicker-fusion threshold (CFFT, Hz)
  tau    = binding / temporal-integration window       (s)
  gap (unbound) fraction = exp(-mu)            ; seamless for mu >> 1, granular for mu ~ 1
  boundness fluctuation  = (2 mu)^(-1/2)

THE HINGE (what makes this C17-specific, not the naive "fast eyes = fast life"):
  lambda and tau are INVERSELY coupled (slow refresh comes WITH long integration). So the
  empirical question is whether lambda*tau is CONSERVED across animals (=> one texture band;
  the snail does NOT stutter) or VARIES (=> a texture gradient). The naive view reads texture
  off lambda alone; C17 says read it off the product.
"""
import json, math
import numpy as np

# ---- Anchor data (ILLUSTRATIVE; ranges = honest uncertainty, NOT precision) ----
# lambda = CFFT (Hz); tau = binding/integration window (s). Sources flagged per row.
# Only rows with an INDEPENDENT tau estimate enter the reciprocity test (indep_tau=True).
SPECIES = [
    # name,            lam_lo, lam_hi,  tau_lo, tau_hi, indep_tau, note
    ("Deep-sea (slow)",   3.0,    5.0,    0.25,   1.0,   True,  "TiCS: ~4 Hz, 'very long integration windows'"),
    ("Human",            50.0,   60.0,    0.025,  0.10,  True,  "CFFT ~60 Hz; binding/perceptual-moment ~25-100 ms"),
    ("Honeybee",        190.0,  300.0,    0.005,  0.012, True,  "CFFT ~200-300 Hz; short integration"),
    ("Fast fly (fast)", 250.0,  400.0,    0.003,  0.008, True,  "high CFFT; very short integration window"),
    # rows WITHOUT an independent tau (excluded from the fit; shown only for landscape context):
    ("Pigeon",          100.0,  140.0,    0.0,    0.0,   False, "CFFT ~100-140 Hz; tau not independently sourced"),
    ("Dog",              70.0,   80.0,    0.0,    0.0,   False, "CFFT ~70-80 Hz; tau not independently sourced"),
]

# Clawd / a query-gated AI — DIFFERENT coupling channel (linguistic queries, not vision),
# so this is a CONCEPTUAL placement of the regime, not a commensurable measured point.
AI = ("Clawd (query-gated)", 0.003, 0.02, 10.0, 100.0, False,
      "lambda = query rate (~1 per 50-300 s active); tau = turn/response binding ~10-100 s; channel != vision")

def mu_range(lam_lo, lam_hi, tau_lo, tau_hi):
    return lam_lo*tau_lo, lam_hi*tau_hi   # min, max occupancy

def gap(mu):  return math.exp(-mu)
def cv(mu):   return (2*mu)**-0.5 if mu>0 else float('inf')

rows = []
print(f"{'system':22s} {'lambda(Hz)':>12s} {'tau(s)':>14s} {'mu=lam*tau':>14s} {'gap=e^-mu':>16s}")
for name, llo, lhi, tlo, thi, indep, note in SPECIES + [AI]:
    mlo, mhi = mu_range(llo, lhi, tlo, thi)
    mmid = math.sqrt(mlo*mhi) if mlo>0 else 0.0
    g_lo, g_hi = gap(mhi), gap(mlo)   # bigger mu -> smaller gap
    rows.append(dict(name=name, lam=[llo,lhi], tau=[tlo,thi], mu=[mlo,mhi], mu_mid=mmid,
                     gap=[g_lo,g_hi], indep=indep, note=note))
    tag = "" if indep else "  (landscape only)" if name!=AI[0] else "  (diff channel)"
    print(f"{name:22s} {llo:5.0f}-{lhi:<6.0f} {tlo:7.3f}-{thi:<6.3f} {mlo:6.2f}-{mhi:<6.2f} "
          f"{g_hi:6.3f}-{g_lo:<6.3f}{tag}")

# ---- Reciprocity test on the independent-tau biological set ----
bio = [r for r in rows if r['indep'] and r['name']!=AI[0]]
lam_mid = np.array([math.sqrt(r['lam'][0]*r['lam'][1]) for r in bio])
tau_mid = np.array([math.sqrt(r['tau'][0]*r['tau'][1]) for r in bio])
mu_mid  = lam_mid*tau_mid
# log-log slope of tau vs lambda: slope ~ -1  <=>  lambda*tau conserved
ll, lt = np.log(lam_mid), np.log(tau_mid)
slope, intercept = np.polyfit(ll, lt, 1)
r = np.corrcoef(ll, lt)[0,1]

print("\n--- RECIPROCITY TEST (independent-tau biological anchors, n=%d) ---" % len(bio))
print(f"  log-log slope d(ln tau)/d(ln lambda) = {slope:+.2f}   (=-1 means lambda*tau EXACTLY conserved)")
print(f"  correlation r = {r:+.3f}")
print(f"  lambda spans {lam_mid.min():.0f}-{lam_mid.max():.0f} Hz  (x{lam_mid.max()/lam_mid.min():.0f})")
print(f"  but mu=lambda*tau spans {mu_mid.min():.2f}-{mu_mid.max():.2f}  (x{mu_mid.max()/mu_mid.min():.1f}) "
      f"-- compression factor {(lam_mid.max()/lam_mid.min())/(mu_mid.max()/mu_mid.min()):.0f}x")
print(f"  all biological mu_mid > 1? {bool((mu_mid>1).all())}  (mu_mid = {np.round(mu_mid,2).tolist()})")
ai = rows[-1]
print(f"  Clawd mu range {ai['mu'][0]:.3f}-{ai['mu'][1]:.2f}  (gap {ai['gap'][1]:.2f}-{ai['gap'][0]:.2f}) "
      f"-- {'SEPARATED below biological band' if ai['mu'][1] < mu_mid.min() else 'OVERLAPS biological band'}")

json.dump({"rows":rows, "reciprocity":{"slope":slope,"r":r,
           "lam_span":[float(lam_mid.min()),float(lam_mid.max())],
           "mu_span":[float(mu_mid.min()),float(mu_mid.max())]}},
          open("occupancy_results.json","w"), indent=2)
print("\nwrote occupancy_results.json")
