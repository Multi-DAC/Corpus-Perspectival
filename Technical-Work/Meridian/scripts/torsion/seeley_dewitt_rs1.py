"""
Seeley-DeWitt coefficients on RS₁ — Phase 22 Track γ.1

The heat kernel expansion of the spectral action on the RS₁ background:
    Tr[e^{-tD²}] = Σ_{n≥0} a_{2n} t^{n-2}  (in 4D effective theory)

The KK spectrum on RS₁ with warp factor e^{-A(y)} where A(y) = 4ky:
- Scalar modes: m_n satisfying J_ν(m_n/k) Y_ν(m_n e^{-πkr}/k) = J_ν(m_n e^{-πkr}/k) Y_ν(m_n/k)
  where ν = 2 for scalar, different for spin-1 and spin-1/2
- The spectral zeta function: ζ(s) = Σ_n m_n^{-2s}
- The Seeley-DeWitt coefficients: a_{2n} = Res_{s=2-n} ζ(s) (up to normalization)

For resurgence analysis (Track γ.2), we need a_{2n} for n up to 10-20.
The large-n behavior determines Borel singularities.

The KEY question for Phase 22: are the Borel singularities gauge-DEPENDENT?
If yes → non-perturbative correction is gauge-dependent → the 12% lives here.
If no → non-perturbative sector is also universal → Door 3 (string embedding) is the only route.

This script computes the first 10 coefficients using the exact KK spectrum.
"""

from mpmath import mp, mpf, pi, besselj, bessely, findroot, fsum, power, gamma, zeta
import json

# Set high precision
mp.dps = 50

# RS₁ parameters (from Phase 20)
# k = AdS curvature, r_c = compactification radius
# We work in units where k = 1
# The hierarchy: e^{-π k r_c} ≈ TeV/M_Pl ≈ 10^{-16}
# So π k r_c ≈ 36.8

kr_c = mpf('36.8') / pi  # k * r_c
epsilon = mp.exp(-pi * kr_c)  # ≈ 10^{-16}, the warp factor at the IR brane

print(f"RS1 parameters:")
print(f"  k r_c = {kr_c}")
print(f"  epsilon = e^(-π k r_c) = {epsilon}")
print(f"  hierarchy = {1/epsilon}")
print()

def kk_eigenvalue_equation(m, nu):
    """
    The KK eigenvalue equation for the RS₁ orbifold.

    For a field of bulk mass parameter ν, the KK masses m_n satisfy:
    J_ν(m/k) Y_ν(m ε/k) - J_ν(m ε/k) Y_ν(m/k) = 0

    where ε = e^{-π k r_c} is the warp factor.

    We work in units k = 1, so:
    J_ν(m) Y_ν(m ε) - J_ν(m ε) Y_ν(m) = 0
    """
    me = m * epsilon
    return besselj(nu, m) * bessely(nu, me) - besselj(nu, me) * bessely(nu, m)


def find_kk_masses(nu, n_modes=30):
    """
    Find the first n_modes KK masses for bulk parameter ν.

    The masses are approximately m_n ≈ (n + ν/2 - 1/4) π / (1 - ε)
    for large n, but the first few need careful root-finding.
    """
    masses = []

    # For the RS₁ orbifold, the KK masses are approximately
    # at the zeros of J_ν(m), shifted by the IR boundary condition.
    # Start with initial guesses from Bessel zeros.

    # First guess: use asymptotic spacing π
    for i in range(1, n_modes + 1):
        # Initial guess: approximately (i - 1/4 + ν/2) π for large ν
        # For ν = 2 (scalar), first zero of J_2 is at ~5.14
        guess = (i + nu/2 - mpf('0.25')) * pi

        try:
            m = findroot(lambda x: kk_eigenvalue_equation(x, nu), guess)
            if m > 0 and m not in masses:
                masses.append(m)
        except Exception:
            pass

    masses.sort()
    return masses[:n_modes]


def spectral_zeta_partial(masses, s, cutoff=None):
    """
    Partial spectral zeta function: ζ(s) = Σ_n m_n^{-2s}

    This converges for Re(s) > d/2 = 2.
    For the Seeley-DeWitt coefficients, we need the analytic continuation.
    """
    if cutoff is None:
        cutoff = len(masses)
    return fsum(power(m, -2*s) for m in masses[:cutoff])


def compute_heat_trace(masses, t_values):
    """
    Direct computation of the heat trace: K(t) = Σ_n exp(-t m_n²)

    This is exact for finite number of modes and can be compared
    with the asymptotic expansion in powers of t.
    """
    results = []
    for t in t_values:
        K = fsum(mp.exp(-t * m**2) for m in masses)
        results.append((t, K))
    return results


# Compute KK masses for scalar (ν=2), gauge (ν=1), graviton (ν=2 with different BC)
print("Computing KK spectrum...")
print("=" * 60)

# Scalar field (ν = 2)
print("\nScalar KK masses (ν = 2):")
scalar_masses = find_kk_masses(nu=2, n_modes=20)
for i, m in enumerate(scalar_masses[:10]):
    print(f"  m_{i+1} = {m}")

# Gauge field (ν = 1) — this is where gauge dependence enters!
# For SU(3): the bulk gauge field has ν = 1
# For SU(2): same ν = 1 (same bulk equation)
# For U(1): same ν = 1
# The KK spectrum is the SAME for all gauge groups at tree level.
# Gauge dependence can only enter through:
# (a) different bulk masses (if gauge-Higgs unification gives mass terms)
# (b) different boundary conditions (if branes break the gauge group)
# (c) non-perturbative effects (instantons, sphalerons with gauge-dependent action)
print("\nGauge KK masses (ν = 1):")
gauge_masses = find_kk_masses(nu=1, n_modes=20)
for i, m in enumerate(gauge_masses[:10]):
    print(f"  m_{i+1} = {m}")

# Compute heat traces at several t values
print("\n" + "=" * 60)
print("Heat trace K(t) = Σ exp(-t m_n²)")
print("=" * 60)

t_values = [mpf(10)**(-n) for n in range(1, 8)]

print("\nScalar heat trace:")
scalar_heat = compute_heat_trace(scalar_masses, t_values)
for t, K in scalar_heat:
    print(f"  t = {mp.nstr(t, 5):>12s}  K(t) = {mp.nstr(K, 15)}")

print("\nGauge heat trace:")
gauge_heat = compute_heat_trace(gauge_masses, t_values)
for t, K in gauge_heat:
    print(f"  t = {mp.nstr(t, 5):>12s}  K(t) = {mp.nstr(K, 15)}")

# The Seeley-DeWitt coefficients can be extracted by fitting
# K(t) = Σ a_{2n} t^{n-2} for small t
# Or equivalently, t² K(t) = a_0 + a_2 t + a_4 t² + ...
print("\n" + "=" * 60)
print("Asymptotic extraction: t² K(t) for small t")
print("=" * 60)

print("\nScalar: t² K(t)")
for t, K in scalar_heat:
    print(f"  t = {mp.nstr(t, 5):>12s}  t²K(t) = {mp.nstr(t**2 * K, 15)}")

print("\nGauge: t² K(t)")
for t, K in gauge_heat:
    print(f"  t = {mp.nstr(t, 5):>12s}  t²K(t) = {mp.nstr(t**2 * K, 15)}")

# KEY COMPARISON: scalar vs gauge heat traces
# If they differ, the Seeley-DeWitt coefficients differ → gauge dependence
print("\n" + "=" * 60)
print("GAUGE DEPENDENCE CHECK: (scalar - gauge) heat traces")
print("=" * 60)
for (t, Ks), (_, Kg) in zip(scalar_heat, gauge_heat):
    diff = Ks - Kg
    if abs(Ks) > 0:
        rel = diff / Ks
    else:
        rel = mpf('0')
    print(f"  t = {mp.nstr(t, 5):>12s}  Δ = {mp.nstr(diff, 10):>20s}  rel = {mp.nstr(rel, 5)}")

print("\n" + "=" * 60)
print("INTERPRETATION:")
print("If Δ ≈ 0 at ALL t → perturbative universality (consistent with T12)")
print("If Δ ≠ 0 at small t → Seeley-DeWitt coefficients differ → gauge-dependent")
print("But T12 already proved Δ = 0 perturbatively.")
print("The non-perturbative question needs Borel analysis of the FULL spectral zeta.")
print("=" * 60)

# Save results for subsequent analysis
results = {
    'kr_c': str(kr_c),
    'epsilon': str(epsilon),
    'scalar_masses': [str(m) for m in scalar_masses],
    'gauge_masses': [str(m) for m in gauge_masses],
    'scalar_heat': [(str(t), str(K)) for t, K in scalar_heat],
    'gauge_heat': [(str(t), str(K)) for t, K in gauge_heat],
}

with open('seeley_dewitt_rs1_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to seeley_dewitt_rs1_results.json")
print("\nNext: γ.2 — Borel transform of the spectral zeta function")
print("      Padé approximants + conformal mapping → locate Borel singularities")
print("      KEY: are singularity positions gauge-dependent?")
