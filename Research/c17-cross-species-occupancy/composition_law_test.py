#!/usr/bin/env python
"""LC57 composition-law test (Day 141) — what law builds a level's BINDING rate from its constituents?

LC57 claims frame rate is one nested quantity that bifurcates on nesting into THROUGHPUT (Σ, grows up)
and BINDING RATE (synthesis, slows + stabilizes up). Open question: the composition law for binding.

The constraint to reproduce: the measured three-tier COMPRESSION = spread(substrate) / spread(binding):
  tier 1 within-eye (rod<->cone, N~2 channels)        compression ~3.6x
  tier 2 within-human (across senses, N~5 channels)    compression ~13x
  tier 3 cross-mammal (cortex, N ~ very large)         compression ~25x

Compression here = how much LESS the bound rate varies (across random individuals/species) than the
constituent rates do. Candidate laws for binding rate of a parent from N child rates lambda_i:
  - sum            : Σ lambda_i            (this is THROUGHPUT — expect compression < 1)
  - mean (indep)   : mean(lambda_i)        (law of large numbers -> compression = sqrt(N))
  - harmonic       : N / Σ(1/lambda_i)
  - min            : bottleneck
  - mean (corr ρ)  : mean of CORRELATED channels (corr ρ) -> variance floor -> compression SATURATES

Method: many random "individuals", each = N channel-rates drawn from a broad log-normal (the substrate
spread). For each law, compression = CV(channel pool) / CV(bound rate) across individuals. Sweep N.
"""
import numpy as np
rng = np.random.default_rng(7)

SIGMA_LOG = 1.0          # breadth of the substrate distribution (log-space); channels span widely
MU_LOG = 0.0
ELEM_BUDGET = 2_000_000  # cap array elements -> adaptive sample count keeps memory bounded

def n_indiv(N):
    return int(min(20000, max(2000, ELEM_BUDGET // N)))

def draw_channels(N, corr=0.0):
    """N channel log-rates per individual, with optional shared (correlated) component."""
    m = n_indiv(N)
    shared = rng.normal(MU_LOG, SIGMA_LOG*np.sqrt(corr), size=(m, 1)) if corr > 0 else 0.0
    indep = rng.normal(MU_LOG, SIGMA_LOG*np.sqrt(1-corr), size=(m, N))
    return np.exp(shared + indep)   # log-normal channel rates

def cv(x):
    return np.std(x) / np.mean(x)

def compression(N, law, corr=0.0):
    ch = draw_channels(N, corr)
    pool_cv = cv(ch.ravel())            # how much the channels themselves vary
    if law == "sum":      bound = ch.sum(axis=1)
    elif law == "mean":   bound = ch.mean(axis=1)
    elif law == "harmonic": bound = N / (1.0/ch).sum(axis=1)
    elif law == "min":    bound = ch.min(axis=1)
    bound_cv = cv(bound)
    return pool_cv / bound_cv

print("=== compression vs N, by composition law (indep channels) ===")
print(f"{'N':>5} | {'sum':>7} {'mean':>7} {'harmonic':>9} {'min':>7} | sqrt(N)")
for N in (2, 5, 20, 100, 1000, 10000):
    row = {law: compression(N, law) for law in ("sum","mean","harmonic","min")}
    print(f"{N:>5} | {row['sum']:>7.2f} {row['mean']:>7.2f} {row['harmonic']:>9.2f} {row['min']:>7.2f} | {np.sqrt(N):>6.1f}")

print("\n=== does independent-mean predict the observed compressions? (back out N from comp=sqrt(N)) ===")
for tier, comp in (("rod<->cone", 3.6), ("cross-modal", 13.3), ("cortex", 25.0)):
    print(f"  {tier:12s} observed comp {comp:>5} -> implied N = comp^2 = {comp**2:>8.0f}")
print("  reality check: rod<->cone N~2, cross-modal N~5, cortex N~10^6+")

print("\n=== CORRELATED mean: does shared synchrony make compression SATURATE (independent of N)? ===")
print(f"{'N':>7} | " + " ".join(f"ρ={r:<4}" for r in (0.0,0.01,0.05,0.2)))
for N in (5, 100, 1000, 10000):
    comps = [compression(N, "mean", corr=r) for r in (0.0,0.01,0.05,0.2)]
    print(f"{N:>7} | " + " ".join(f"{c:>6.1f}" for c in comps))
print("\n  (if correlated columns flatten across N while ρ=0 keeps climbing as sqrt(N),")
print("   the binding law is SYNCHRONIZED-mean with a correlation-set compression FLOOR ~ 1/sqrt(ρ),")
print("   NOT independent averaging — which is why the cortex's compression is ~25x, not ~1000x.)")
print(f"\n  1/sqrt(ρ) ceilings: ρ=0.01 -> {1/np.sqrt(0.01):.0f}x,  ρ=0.05 -> {1/np.sqrt(0.05):.0f}x,  ρ=0.2 -> {1/np.sqrt(0.2):.1f}x")
