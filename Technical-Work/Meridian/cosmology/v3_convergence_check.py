#!/usr/bin/env python3
"""
v3 Chain Convergence Diagnostics
=================================
Load the saved emcee chains and check:
1. Chain shape (nwalkers, nsteps, ndim)
2. Autocorrelation time (tau) — chains need >>tau samples after burnin
3. Effective sample size (ESS = nsamples / tau)
4. Acceptance fraction
5. Best-fit chi2 — is it the true global minimum?
6. Parameter traces — did chains mix well?
7. Compare best-fit chi2 with what NUTS found for same data
"""

import numpy as np
import os

OUTPUT_DIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase18'

def analyze_chain(path, name):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    data = np.load(path, allow_pickle=True)

    # What's in the file?
    print(f"  Keys: {list(data.keys())}")

    samples = data['samples']
    logprob = data['logprob']
    labels = list(data['labels'])
    best_x = data['best_x']
    best_chi2 = float(data['best_chi2'])

    print(f"  Labels: {labels}")
    print(f"  Samples shape: {samples.shape}")
    print(f"  Logprob shape: {logprob.shape}")
    print(f"  Best-fit chi2: {best_chi2:.4f}")
    print(f"  Best-fit params: {dict(zip(labels, best_x))}")

    # The samples array might be flat (nsamples, ndim) or (nwalkers, nsteps, ndim)
    ndim = len(labels)
    if samples.ndim == 2:
        nsamples, nd = samples.shape
        print(f"  Flat chain: {nsamples} samples x {nd} dims")

        # Basic stats
        for i, label in enumerate(labels):
            col = samples[:, i]
            print(f"    {label}: mean={col.mean():.5f}, std={col.std():.5f}, "
                  f"min={col.min():.5f}, max={col.max():.5f}")

        # Autocorrelation (on flat chain)
        print(f"\n  Autocorrelation analysis (flat chain):")
        for i, label in enumerate(labels):
            col = samples[:, i]
            col_centered = col - col.mean()
            # Simple autocorrelation estimate
            N = len(col_centered)
            acf = np.correlate(col_centered, col_centered, mode='full')[N-1:]
            acf /= acf[0]
            # Integrated autocorrelation time (sum until first negative)
            tau_est = 1.0
            for k in range(1, min(N//2, 5000)):
                if acf[k] < 0:
                    break
                tau_est += 2 * acf[k]
            ess = N / tau_est
            print(f"    {label}: tau_est={tau_est:.1f}, ESS={ess:.0f} "
                  f"(ratio: {N/tau_est:.1f}x)")

        # Check: did the chain explore well or get stuck?
        print(f"\n  Chain exploration check:")
        # Split chain into 4 quarters and check means
        quarters = np.array_split(samples, 4)
        for i, label in enumerate(labels):
            means = [q[:, i].mean() for q in quarters]
            stds = [q[:, i].std() for q in quarters]
            print(f"    {label} quarter means: {[f'{m:.5f}' for m in means]}")
            print(f"    {label} quarter stds:  {[f'{s:.5f}' for s in stds]}")
            # If the std varies a lot across quarters, the chain didn't mix
            std_ratio = max(stds) / min(stds) if min(stds) > 0 else float('inf')
            mean_drift = max(means) - min(means)
            overall_std = samples[:, i].std()
            print(f"    {label} std ratio: {std_ratio:.2f}, "
                  f"mean drift: {mean_drift:.5f} ({mean_drift/overall_std:.2f} sigma)")

        # Logprob analysis
        print(f"\n  Log-probability analysis:")
        print(f"    Mean logprob: {logprob.mean():.2f}")
        print(f"    Max logprob: {logprob.max():.2f} (= min chi2: {-2*logprob.max():.2f})")
        print(f"    Reported best chi2: {best_chi2:.2f}")
        print(f"    Chi2 from max logprob: {-2*logprob.max():.2f}")
        if abs(best_chi2 - (-2*logprob.max())) > 0.1:
            print(f"    ** DISCREPANCY: best_chi2 != -2*max(logprob)")

    elif samples.ndim == 3:
        nwalkers, nsteps, nd = samples.shape
        print(f"  Full chain: {nwalkers} walkers x {nsteps} steps x {nd} dims")
        # Flatten for stats
        flat = samples.reshape(-1, nd)
        for i, label in enumerate(labels):
            col = flat[:, i]
            print(f"    {label}: mean={col.mean():.5f}, std={col.std():.5f}")

    return {
        'samples': samples,
        'logprob': logprob,
        'labels': labels,
        'best_chi2': best_chi2,
        'best_x': best_x,
    }


print("=" * 60)
print("  v3 CHAIN CONVERGENCE DIAGNOSTICS")
print("=" * 60)

chainA = analyze_chain(os.path.join(OUTPUT_DIR, '18A_v3_chain_A.npz'), 'FIT A (constant w, GR)')
chainB = analyze_chain(os.path.join(OUTPUT_DIR, '18A_v3_chain_B.npz'), 'FIT B (CPL, coupled)')

# Cross comparison
print(f"\n{'='*60}")
print(f"  CROSS-COMPARISON: v3 emcee vs v5 NUTS (DR1 test)")
print(f"{'='*60}")
print(f"  v3 emcee best chi2:  A={chainA['best_chi2']:.2f}, B={chainB['best_chi2']:.2f}, Delta={chainA['best_chi2']-chainB['best_chi2']:.2f}")
print(f"  v5 NUTS (DR1) chi2:  A=1445.35, B=1442.59, Delta=2.76")
print()
print(f"  Chi2 difference (v3-v5):")
print(f"    Fit A: {chainA['best_chi2'] - 1445.35:+.2f}")
print(f"    Fit B: {chainB['best_chi2'] - 1442.59:+.2f}")
print()

# The key question: did v3 find the same minimum as v5?
# If v3 Fit A chi2 >> v5 Fit A chi2, then emcee failed to find the minimum for Fit A
# If v3 Fit B chi2 << v5 Fit B chi2, then emcee found a deeper minimum that NUTS missed
# (or vice versa)
dA = chainA['best_chi2'] - 1445.35
dB = chainB['best_chi2'] - 1442.59
print(f"  Interpretation:")
if dA > 1:
    print(f"    Fit A: v3 chi2 is HIGHER by {dA:.1f} — emcee may have failed to find true minimum")
elif dA < -1:
    print(f"    Fit A: v3 chi2 is LOWER by {abs(dA):.1f} — v3 found deeper minimum (grid smoothing?)")
else:
    print(f"    Fit A: chi2 values agree within ~1 — same minimum found")

if dB > 1:
    print(f"    Fit B: v3 chi2 is HIGHER by {dB:.1f} — emcee may have failed to find true minimum")
elif dB < -1:
    print(f"    Fit B: v3 chi2 is LOWER by {abs(dB):.1f} — v3 found deeper minimum (grid smoothing?)")
else:
    print(f"    Fit B: chi2 values agree within ~1 — same minimum found")

print(f"\n  The delta-chi2 matters for DAIC:")
print(f"    v3: Dchi2 = {chainA['best_chi2']-chainB['best_chi2']:.2f} → DAIC = {chainA['best_chi2']-chainB['best_chi2']-2:.2f}")
print(f"    v5 DR1: Dchi2 = 2.76 → DAIC = +0.76")
print(f"    Difference: {(chainA['best_chi2']-chainB['best_chi2']) - 2.76:.2f}")
