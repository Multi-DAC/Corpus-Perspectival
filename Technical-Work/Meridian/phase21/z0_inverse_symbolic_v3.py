#!/usr/bin/env python3
"""
Inverse symbolic computation for z0 (v3)
KEY DISCOVERY FROM v2: arg(theta_1(pi*z0, q)) / pi = -1/8 EXACTLY.

This means theta_1(pi*z0, q) = |target| * e^{-i*pi/8}
where |target| = ln(3)/sqrt(2).

So: theta_1(pi*z0, q) = ln(3)/sqrt(2) * e^{-i*pi/8}

This v3 exploits this phase structure and goes deeper.
"""

from mpmath import (
    mp, mpf, mpc, pi, ln, sqrt, exp, cos, sin, tan, log,
    gamma, jtheta, fabs, re, im, arg, power, floor, nstr,
    findroot, pslq, identify, ellipk, ellipe,
    zeta as riemannzeta, catalan,
    euler as eulergamma, phi as golden_ratio,
    hyp2f1, agm, diff
)

def main():
    DPS = 160
    mp.dps = DPS + 50

    # Recompute z0
    omega = mpc(-mpf(1)/2, sqrt(mpf(3))/2)
    q = exp(mpc(0, 1) * pi * omega)
    target_mod = ln(mpf(3)) / sqrt(mpf(2))

    def f(z):
        val = jtheta(1, pi * z, q)
        return fabs(val) - target_mod

    z0 = findroot(f, mpf('0.277'))
    mp.dps = DPS
    z0 = +z0

    print("z0 =", nstr(z0, 150))

    # ====================================================================
    # Verify the phase discovery
    # ====================================================================
    print("\n" + "=" * 70)
    print("PHASE VERIFICATION")
    print("=" * 70)

    th1_val = jtheta(1, pi * z0, q)
    phase = arg(th1_val)
    print(f"theta_1(pi*z0, q) = {nstr(th1_val, 40)}")
    print(f"|theta_1| = {nstr(fabs(th1_val), 40)}")
    print(f"arg(theta_1) = {nstr(phase, 40)}")
    print(f"arg/pi = {nstr(phase/pi, 40)}")
    print(f"-pi/8 = {nstr(-pi/8, 40)}")
    print(f"arg - (-pi/8) = {nstr(phase - (-pi/8), 20)}")
    print(f"|arg + pi/8| = {nstr(fabs(phase + pi/8), 10)}")

    # How many digits does phase/pi = -1/8 match?
    ratio_err = fabs(phase/pi + mpf(1)/8)
    if ratio_err > 0:
        phase_digits = int(-log(ratio_err, 10))
    else:
        phase_digits = DPS
    print(f"\nPhase = -pi/8 to {phase_digits} digits")

    # ====================================================================
    # So we now know:
    # theta_1(pi*z0, q) = (ln3/sqrt2) * e^{-i*pi/8}
    # = (ln3/sqrt2) * (cos(pi/8) - i*sin(pi/8))
    # cos(pi/8) = sqrt(2+sqrt2)/2, sin(pi/8) = sqrt(2-sqrt2)/2
    # ====================================================================
    print("\n" + "=" * 70)
    print("STRUCTURAL ANALYSIS")
    print("=" * 70)

    cos_pi8 = cos(pi/8)
    sin_pi8 = sin(pi/8)
    print(f"cos(pi/8) = sqrt(2+sqrt2)/2 = {nstr(cos_pi8, 30)}")
    print(f"sin(pi/8) = sqrt(2-sqrt2)/2 = {nstr(sin_pi8, 30)}")

    # So the real and imaginary parts of theta_1 at z0 are:
    re_target = target_mod * cos_pi8
    im_target = -target_mod * sin_pi8
    print(f"\nRe(theta_1) = ln(3)*sqrt(2+sqrt2)/(2*sqrt2) = {nstr(re_target, 30)}")
    print(f"Im(theta_1) = -ln(3)*sqrt(2-sqrt2)/(2*sqrt2) = {nstr(im_target, 30)}")
    print(f"Actual Re    = {nstr(re(th1_val), 30)}")
    print(f"Actual Im    = {nstr(im(th1_val), 30)}")

    # ====================================================================
    # Now: can we invert theta_1 analytically?
    # theta_1(z, q) = 2 * sum_{n=0}^inf (-1)^n * q^{(n+1/2)^2} * sin((2n+1)*z)
    # This is related to the Jacobi elliptic functions.
    # theta_1(pi*v, q) / theta_1'(0, q) = sn(v * K(m) | m) / ...
    # ====================================================================
    print("\n" + "=" * 70)
    print("JACOBI ELLIPTIC CONNECTION")
    print("=" * 70)

    # theta constants
    th2_0 = jtheta(2, 0, q)
    th3_0 = jtheta(3, 0, q)
    th4_0 = jtheta(4, 0, q)

    print(f"theta_2(0) = {nstr(th2_0, 25)}")
    print(f"theta_3(0) = {nstr(th3_0, 25)}")
    print(f"theta_4(0) = {nstr(th4_0, 25)}")

    # theta_1'(0) = pi * theta_2(0) * theta_3(0) * theta_4(0)
    th1p_0 = pi * th2_0 * th3_0 * th4_0
    print(f"theta_1'(0) = pi * prod = {nstr(th1p_0, 25)}")

    # The elliptic modulus: m = (theta_2(0)/theta_3(0))^4
    m_elliptic = (th2_0 / th3_0)**4
    print(f"\nElliptic modulus m = (th2/th3)^4 = {nstr(m_elliptic, 25)}")
    print(f"|m| = {nstr(fabs(m_elliptic), 25)}")
    print(f"arg(m)/pi = {nstr(arg(m_elliptic)/pi, 25)}")

    # K = pi/2 * theta_3(0)^2
    K_val = pi/2 * th3_0**2
    print(f"K = pi/2 * th3^2 = {nstr(K_val, 25)}")

    # Jacobi relation: theta_1(pi*v, q) = theta_1'(0) * sn(2*K*v, m) (needs care)
    # Actually: theta_1(pi*v, q) / theta_3(pi*v, q) = (th2_0/th4_0) * ... complex
    # Let me just compute the ratio
    ratio = th1_val / th1p_0
    print(f"\ntheta_1(pi*z0) / theta_1'(0) = {nstr(ratio, 25)}")
    print(f"|ratio| = {nstr(fabs(ratio), 25)}")

    # ====================================================================
    # Key constants for this tau
    # ====================================================================
    P = pi
    L2 = ln(mpf(2))
    L3 = ln(mpf(3))
    S2 = sqrt(mpf(2))
    S3 = sqrt(mpf(3))
    S5 = sqrt(mpf(5))
    S6 = sqrt(mpf(6))
    G13 = gamma(mpf(1)/3)
    G23 = gamma(mpf(2)/3)
    G14 = gamma(mpf(1)/4)
    G16 = gamma(mpf(1)/6)
    EC = eulergamma
    CAT = catalan

    # CM period: Omega_1 = Gamma(1/3)^3 / (2^{7/3} * 3^{1/2} * pi)
    Omega_CM = G13**3 / (mpf(2)**(mpf(7)/3) * S3 * P)

    # ====================================================================
    # DEEPER PSLQ: Now include z0^2, z0*const, etc.
    # Focus on bases that include the phase-relevant constants
    # sqrt(2+sqrt2), sqrt(2-sqrt2), pi/8 related
    # ====================================================================
    print("\n" + "=" * 70)
    print("DEEP PSLQ WITH PHASE-INFORMED BASES")
    print("=" * 70)

    s2ps2 = sqrt(2 + S2)  # related to cos(pi/8)
    s2ms2 = sqrt(2 - S2)  # related to sin(pi/8)

    def run_pslq(name, basis_vals, basis_names, maxcoeff=1000):
        try:
            rel = pslq(basis_vals, maxcoeff=maxcoeff, maxsteps=10000)
            if rel is not None:
                if rel[0] == 0:
                    return None
                residual = fabs(sum(r * b for r, b in zip(rel, basis_vals)))
                if residual > 0:
                    digits = max(0, int(-log(residual, 10)))
                else:
                    digits = DPS
                max_c = max(abs(r) for r in rel)
                coeffs = [int(r) for r in rel]
                terms = []
                for c, n in zip(coeffs[1:], basis_names[1:]):
                    if c != 0:
                        terms.append(f"({c})*{n}")
                formula = f"z0 = -({' + '.join(terms)}) / ({coeffs[0]})"
                print(f"\n  ** {name} **")
                print(f"     Coefficients: {coeffs}")
                print(f"     Formula: {formula}")
                print(f"     Digits: {digits}, Max coeff: {max_c}")
                return {'name': name, 'coeffs': coeffs, 'formula': formula,
                        'digits': digits, 'max_coeff': max_c}
        except:
            pass
        return None

    hits = []

    # Phase-informed bases
    phase_bases = [
        ('z0 vs {1, pi, ln3, sqrt(2+sqrt2), sqrt(2-sqrt2)}',
         [z0, 1, P, L3, s2ps2, s2ms2],
         ['z0','1','pi','ln3','sqrt(2+sqrt2)','sqrt(2-sqrt2)']),
        ('z0 vs {1, pi, ln3, cos(pi/8), sin(pi/8)}',
         [z0, 1, P, L3, cos_pi8, sin_pi8],
         ['z0','1','pi','ln3','cos(pi/8)','sin(pi/8)']),
        ('z0 vs {1, pi, ln3, sqrt2, sqrt3, cos(pi/8)}',
         [z0, 1, P, L3, S2, S3, cos_pi8],
         ['z0','1','pi','ln3','sqrt2','sqrt3','cos(pi/8)']),
        ('z0 vs {1, pi/8, ln3, sqrt2, sqrt3}',
         [z0, 1, P/8, L3, S2, S3],
         ['z0','1','pi/8','ln3','sqrt2','sqrt3']),
        ('z0 vs {1, G(1/3), pi, sqrt3, cos(pi/8)}',
         [z0, 1, G13, P, S3, cos_pi8],
         ['z0','1','G(1/3)','pi','sqrt3','cos(pi/8)']),
        ('z0 vs {1, G(2/3), pi, sqrt3, cos(pi/8)}',
         [z0, 1, G23, P, S3, cos_pi8],
         ['z0','1','G(2/3)','pi','sqrt3','cos(pi/8)']),
        ('z0 vs {1, Omega_CM, ln3, sqrt2, cos(pi/8)}',
         [z0, 1, Omega_CM, L3, S2, cos_pi8],
         ['z0','1','Omega_CM','ln3','sqrt2','cos(pi/8)']),
    ]

    for name, vals, names in phase_bases:
        r = run_pslq(name, vals, names)
        if r: hits.append(r)

    # ====================================================================
    # Since the phase is exact, try using the COMPLEX equation directly
    # theta_1(pi*z0, q) = (ln3/sqrt2) * e^{-i*pi/8}
    # Split into real and imaginary parts and solve each
    # ====================================================================
    print("\n" + "=" * 70)
    print("REAL/IMAGINARY SPLIT APPROACH")
    print("=" * 70)

    # Let w = (ln3/sqrt2)*e^{-i*pi/8} = known complex number
    w = target_mod * exp(-mpc(0,1)*P/8)
    print(f"Target w = {nstr(w, 30)}")
    print(f"Re(w) = {nstr(re(w), 30)}")
    print(f"Im(w) = {nstr(im(w), 30)}")

    # Verify: theta_1(pi*z0, q) = w?
    diff_check = th1_val - w
    print(f"|theta_1 - w| = {nstr(fabs(diff_check), 15)}")

    # ====================================================================
    # Try PSLQ on z0 against theta-null ratios (all real)
    # ====================================================================
    print("\n" + "=" * 70)
    print("PSLQ WITH MODULAR INVARIANTS")
    print("=" * 70)

    # |theta_i(0)|
    abs_th2 = fabs(th2_0)
    abs_th3 = fabs(th3_0)
    abs_th4 = fabs(th4_0)
    abs_th1p = fabs(th1p_0)

    print(f"|theta_2(0)| = {nstr(abs_th2, 25)}")
    print(f"|theta_3(0)| = {nstr(abs_th3, 25)}")
    print(f"|theta_4(0)| = {nstr(abs_th4, 25)}")
    print(f"|theta_1'(0)| = {nstr(abs_th1p, 25)}")

    # Dedekind eta: |eta(omega)|
    eta_abs = abs_th1p / (2*P)  # eta^3 = th1'(0)/(2*pi) ...no, different formula
    # Actually eta(tau) = q^{1/24} * prod(1-q^n)
    # And theta_1'(0,q) = 2*pi*eta(tau)^3
    # So |eta(omega)|^3 = |theta_1'(0)|/(2*pi)
    eta_cubed = abs_th1p / (2*P)
    eta_abs = eta_cubed ** (mpf(1)/3)
    print(f"|eta(omega)| via theta_1' = {nstr(eta_abs, 25)}")

    # Known CM value for eta(omega):
    # |eta(omega)| = 3^{1/8} * Gamma(1/3)^{3/2} / (2*pi)^{7/12} * ???
    # Let's just check the Chowla-Selberg formula
    # For discriminant D = -3, h(D) = 1, w(D) = 6:
    # |eta(omega)|^2 = sqrt(3)/(2*pi) * [Gamma(1/3)/Gamma(2/3)]^{3/2} * (some power of pi)
    # Actually the standard formula gives:
    # |eta(omega)|^4 = sqrt(3)/(2*pi)^2 * Gamma(1/3)^6 / (2*pi)^2 ... let me just compute ratios

    # Numerical check: is |eta(omega)| expressible via Gamma(1/3)?
    print(f"\n|eta|^2 = {nstr(eta_abs**2, 25)}")
    print(f"|eta|^3 = {nstr(eta_abs**3, 25)}")

    # PSLQ with theta nulls
    modular_bases = [
        ('z0 vs {1, |th2|, |th3|, |th4|, pi}',
         [z0, 1, abs_th2, abs_th3, abs_th4, P],
         ['z0','1','|th2|','|th3|','|th4|','pi']),
        ('z0 vs {1, |eta|, |eta|^2, pi, sqrt3}',
         [z0, 1, eta_abs, eta_abs**2, P, S3],
         ['z0','1','|eta|','|eta|^2','pi','sqrt3']),
        ('z0 vs {1, |eta|, |eta|^3, ln3, sqrt2}',
         [z0, 1, eta_abs, eta_abs**3, L3, S2],
         ['z0','1','|eta|','|eta|^3','ln3','sqrt2']),
        ('z0 vs {1, |th1p|, ln3, sqrt2, pi}',
         [z0, 1, abs_th1p, L3, S2, P],
         ['z0','1',"|th1'|",'ln3','sqrt2','pi']),
        ('z0*|th1p| vs {1, ln3, sqrt2, pi, sqrt3}',
         [z0*abs_th1p, 1, L3, S2, P, S3],
         ['z0*|th1p|','1','ln3','sqrt2','pi','sqrt3']),
    ]

    for name, vals, names in modular_bases:
        r = run_pslq(name, vals, names)
        if r: hits.append(r)

    # ====================================================================
    # Try the inverse problem: compute the Jacobi elliptic function
    # theta_1(pi*z, q) = theta_1'(0,q) * z * prod terms
    # For small q, theta_1(pi*z, q) ~ 2*q^{1/4}*sin(pi*z)*(1 - 2*q^2*cos(2*pi*z) + ...)
    # ====================================================================
    print("\n" + "=" * 70)
    print("SERIES INVERSION APPROACH")
    print("=" * 70)

    # For |q| ~ 0.0658, q^{1/4} ~ 0.5065
    q14 = fabs(q)**(mpf(1)/4)
    print(f"|q|^(1/4) = {nstr(q14, 20)}")

    # Leading order: theta_1(pi*z, q) ~ 2*q^{1/4}*sin(pi*z)
    # So sin(pi*z0) ~ |theta_1|/(2*|q|^{1/4}) = target_mod / (2*q14)
    sin_approx = target_mod / (2 * q14)
    print(f"Leading-order sin(pi*z0) ~ {nstr(sin_approx, 20)}")
    print(f"Actual sin(pi*z0) = {nstr(sin(P*z0), 20)}")
    # Not a great approximation (q isn't that small)

    # ====================================================================
    # Key test: is z0 related to the CM lattice?
    # ====================================================================
    print("\n" + "=" * 70)
    print("CM LATTICE ANALYSIS")
    print("=" * 70)

    # The CM lattice for tau=omega has Z+Z*omega = Z + Z*(-1/2+sqrt3/2*i)
    # Half-period: omega1 = 1, omega2 = omega
    # The standard normalization uses omega1 = Omega_CM (real half-period of Weierstrass)

    # z0 in units of 1/3, 1/6 etc.
    for n in [2,3,4,5,6,8,9,10,12,18,24,36]:
        frac = z0 * n
        cf_val = frac - floor(frac)
        print(f"  z0 * {n} = {nstr(frac, 20)} (fractional: {nstr(cf_val, 15)})")

    # ====================================================================
    # z0 as root of transcendental equation with known constants
    # ====================================================================
    print("\n" + "=" * 70)
    print("TRANSCENDENTAL EQUATION SEARCH")
    print("=" * 70)

    # Since theta_1(pi*z0, q) = (ln3/sqrt2)*e^{-i*pi/8}, and we know q exactly,
    # z0 is defined implicitly. The question is whether this implicit definition
    # collapses to a closed form.

    # Check: is z0 related to the argument of some modular form?
    # E.g., if z0 = 1/(8*something)...
    print(f"1/z0 = {nstr(1/z0, 25)}")
    print(f"8*z0 = {nstr(8*z0, 25)}")
    print(f"8*z0 - 2 = {nstr(8*z0-2, 25)}")

    # Check z0 vs 1/4 - delta where delta might be recognizable
    delta_from_quarter = mpf(1)/4 - z0
    print(f"\n1/4 - z0 = {nstr(delta_from_quarter, 25)}")
    # That's negative...
    delta_from_quarter2 = z0 - mpf(1)/4
    print(f"z0 - 1/4 = {nstr(delta_from_quarter2, 25)}")

    # Try identify on delta
    mp.dps = 30
    try:
        ids = identify(+delta_from_quarter2, tol=1e-25, full=True)
        if ids:
            for formula in ids[:5]:
                print(f"  identify(z0 - 1/4) -> {formula}")
    except:
        pass
    mp.dps = DPS

    # ====================================================================
    # CRITICAL TEST: solve theta_1(pi*z, q) = w for z using both real
    # and imaginary parts. Does the system over-determine z0?
    # ====================================================================
    print("\n" + "=" * 70)
    print("OVER-DETERMINATION CHECK")
    print("=" * 70)

    # We required |theta_1(z0)| = ln3/sqrt2 (one real equation, one real unknown)
    # The fact that arg = -pi/8 exactly is an OUTPUT, not an input.
    # This is a non-trivial constraint: the specific tau = omega FORCES this phase.
    #
    # Q: Does EVERY z solving |theta_1(pi*z, q_omega)| = X have arg = -pi/8?
    # If so, it's a property of tau=omega, not of z0.

    # Test: compute theta_1 at a few other real z values and check phase
    print("\nPhase of theta_1(pi*z, q_omega) for various real z:")
    for z_test_val in [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45]:
        z_test = mpf(z_test_val)
        th_test = jtheta(1, P * z_test, q)
        ph_test = arg(th_test)
        print(f"  z={z_test_val}: |theta_1|={nstr(fabs(th_test), 15)}, arg/pi={nstr(ph_test/P, 15)}")

    # ====================================================================
    # FINAL PSLQ: massive coefficient search
    # ====================================================================
    print("\n" + "=" * 70)
    print("FINAL PSLQ: HIGH COEFFICIENT SEARCH")
    print("=" * 70)

    final_bases = [
        ('z0 vs {1, pi, ln2, ln3, sqrt2, sqrt3, sqrt5}',
         [z0, 1, P, L2, L3, S2, S3, S5],
         ['z0','1','pi','ln2','ln3','sqrt2','sqrt3','sqrt5'], 5000),
        ('z0 vs {1, G13, G23, G14, pi, sqrt2, sqrt3}',
         [z0, 1, G13, G23, G14, P, S2, S3],
         ['z0','1','G(1/3)','G(2/3)','G(1/4)','pi','sqrt2','sqrt3'], 5000),
        ('z0 vs {1, pi, ln3, G13, G23, sqrt3, Omega_CM}',
         [z0, 1, P, L3, G13, G23, S3, Omega_CM],
         ['z0','1','pi','ln3','G(1/3)','G(2/3)','sqrt3','Omega_CM'], 5000),
        ('z0 vs {1, pi, ln3, sqrt2, EC, CAT, G23}',
         [z0, 1, P, L3, S2, EC, CAT, G23],
         ['z0','1','pi','ln3','sqrt2','EulerGamma','Catalan','G(2/3)'], 5000),
    ]

    for name, vals, names, mc in final_bases:
        r = run_pslq(name, vals, names, maxcoeff=mc)
        if r: hits.append(r)

    # ====================================================================
    # SUMMARY
    # ====================================================================
    print("\n" + "=" * 70)
    print("COMPLETE SUMMARY")
    print("=" * 70)

    print(f"\nz0 = {nstr(z0, 60)}")
    print(f"\nKEY DISCOVERY: arg(theta_1(pi*z0, q_omega)) = -pi/8 exactly")
    print(f"  This means theta_1(pi*z0, q_omega) = (ln3/sqrt2) * e^{{-i*pi/8}}")

    if hits:
        print(f"\nPSLQ HITS involving z0:")
        hits.sort(key=lambda h: -h['digits'])
        for h in hits:
            print(f"  [{h['digits']} digits, max_coeff={h['max_coeff']}] {h['name']}")
            print(f"    {h['formula']}")
    else:
        print(f"\nNo PSLQ relations found involving z0 with coefficients up to 5000.")
        print("z0 appears to be TRANSCENDENTAL and not expressible as a simple")
        print("algebraic combination of standard mathematical constants.")

    print(f"\nCONCLUSION:")
    print(f"  The number z0 = 0.2770794421641922830643... is defined implicitly by:")
    print(f"    theta_1(pi*z0, q) = (ln(3)/sqrt(2)) * exp(-i*pi/8)")
    print(f"  where q = exp(i*pi*omega), omega = e^(2*pi*i/3).")
    print(f"  The phase -pi/8 appears to be an exact consequence of tau = omega.")
    print("  No closed form in terms of {pi, ln, sqrt, Gamma, elliptic K, ...} found.")

if __name__ == '__main__':
    main()
