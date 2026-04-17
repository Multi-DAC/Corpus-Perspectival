#!/usr/bin/env python3
"""
Inverse symbolic computation for z0 (v2 - deeper search)
|theta_1(z0 | omega)| = ln(3)/sqrt(2), omega = e^{2*pi*i/3}

The v1 run established z0 = 0.27707944216419228306... to 150 digits.
The PSLQ "hit" was a tautology (sqrt(3) - 3/sqrt(3) = 0, z0 coefficient = 0).
No closed form found in v1. This v2 goes deeper.
"""

import sys
from mpmath import (
    mp, mpf, mpc, pi, ln, sqrt, exp, cos, sin, tan, log,
    gamma, jtheta, fabs, re, im, arg, power, floor, nstr,
    findroot, pslq, identify, ellipk, ellipe,
    zeta as riemannzeta, catalan,
    euler as eulergamma, phi as golden_ratio,
    hyp2f1, agm, nprint
)

def main():
    DPS = 160
    mp.dps = DPS + 50

    # Recompute z0
    omega = mpc(-mpf(1)/2, sqrt(mpf(3))/2)
    q = exp(mpc(0, 1) * pi * omega)
    target = ln(mpf(3)) / sqrt(mpf(2))

    def f(z):
        val = jtheta(1, pi * z, q)
        return fabs(val) - target

    z0 = findroot(f, mpf('0.277'))
    mp.dps = DPS
    z0 = +z0

    print("z0 =", nstr(z0, 150))
    print()

    # ====================================================================
    # Key constants
    # ====================================================================
    P = pi
    L2 = ln(mpf(2))
    L3 = ln(mpf(3))
    S2 = sqrt(mpf(2))
    S3 = sqrt(mpf(3))
    S5 = sqrt(mpf(5))
    S6 = sqrt(mpf(6))
    S7 = sqrt(mpf(7))
    G13 = gamma(mpf(1)/3)
    G23 = gamma(mpf(2)/3)
    G14 = gamma(mpf(1)/4)
    G34 = gamma(mpf(3)/4)
    G16 = gamma(mpf(1)/6)
    G56 = gamma(mpf(5)/6)
    EC = eulergamma
    CAT = catalan
    PHI = golden_ratio

    # Chowla-Selberg: for tau = omega (CM discriminant -3)
    # |eta(omega)|^2 = sqrt(3)/(4*pi) * Gamma(1/3)^3 / (2*pi)
    # Actually: |eta(omega)| = 3^{1/8} * Gamma(1/3)^{3/2} / (2*pi)^{7/12} * ...
    # Let me just define useful combos
    eta_mod_sq = S3 * G13**3 / (4 * P * (2*P))  # a known identity form

    # Weierstrass invariants at tau = omega
    # g2(omega) = 0, g3(omega) = 140 * G(1/3)^18 / (2^4 * 3^3 * pi^6) ... complex
    # Better: the key CM period is Omega = Gamma(1/3)^3 / (2^{7/3} * 3^{1/2} * pi)
    Omega_CM = G13**3 / (mpf(2)**(mpf(7)/3) * S3 * P)
    print(f"CM half-period Omega = Gamma(1/3)^3/(2^(7/3)*sqrt(3)*pi) = {nstr(Omega_CM, 25)}")
    print(f"z0 / Omega_CM = {nstr(z0 / Omega_CM, 25)}")
    print(f"z0 * Omega_CM = {nstr(z0 * Omega_CM, 25)}")

    # Also: (2*pi)^{2/3} / Gamma(1/3)^2 is the inverse key
    inv_key = (2*P)**(mpf(2)/3) / G13**2
    print(f"(2pi)^(2/3)/Gamma(1/3)^2 = {nstr(inv_key, 25)}")
    print(f"z0 / inv_key = {nstr(z0 / inv_key, 25)}")

    print()
    print("=" * 70)
    print("PSLQ SEARCHES (v2 - excluding trivial relations)")
    print("=" * 70)

    def run_pslq(name, basis_vals, basis_names, maxcoeff=1000):
        """Run PSLQ and only report if z0 coefficient is nonzero."""
        try:
            rel = pslq(basis_vals, maxcoeff=maxcoeff, maxsteps=10000)
            if rel is not None:
                # Check z0 coefficient (first element)
                if rel[0] == 0:
                    # This is a relation among the constants, not involving z0
                    return None
                residual = fabs(sum(r * b for r, b in zip(rel, basis_vals)))
                if residual > 0:
                    digits = max(0, int(-log(residual, 10)))
                else:
                    digits = DPS
                max_c = max(abs(r) for r in rel)
                coeffs = [int(r) for r in rel]

                # Reconstruct formula: rel[0]*z0 + rel[1]*b1 + ... = 0
                # => z0 = -(rel[1]*b1 + ...)/rel[0]
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
        except Exception as e:
            pass
        return None

    hits = []

    # ------------------------------------------------------------------
    # Group 1: z0 vs basic constants (linear)
    # ------------------------------------------------------------------
    print("\n--- Group 1: Linear in basic constants ---")

    bases_g1 = [
        ('1,pi,ln2,ln3,sqrt2,sqrt3',
         [z0, 1, P, L2, L3, S2, S3],
         ['z0', '1', 'pi', 'ln2', 'ln3', 'sqrt2', 'sqrt3']),
        ('1,pi,ln3,sqrt2,sqrt3,sqrt5',
         [z0, 1, P, L3, S2, S3, S5],
         ['z0', '1', 'pi', 'ln3', 'sqrt2', 'sqrt3', 'sqrt5']),
        ('1,pi,ln2,ln3,EC,Catalan',
         [z0, 1, P, L2, L3, EC, CAT],
         ['z0', '1', 'pi', 'ln2', 'ln3', 'EulerGamma', 'Catalan']),
        ('1,pi,pi^2,ln3,sqrt3',
         [z0, 1, P, P**2, L3, S3],
         ['z0', '1', 'pi', 'pi^2', 'ln3', 'sqrt3']),
        ('1,pi,ln3,sqrt2,sqrt3,phi',
         [z0, 1, P, L3, S2, S3, PHI],
         ['z0', '1', 'pi', 'ln3', 'sqrt2', 'sqrt3', 'phi']),
    ]

    for name, vals, names in bases_g1:
        r = run_pslq(name, vals, names)
        if r: hits.append(r)

    # ------------------------------------------------------------------
    # Group 2: z0 vs Gamma values
    # ------------------------------------------------------------------
    print("\n--- Group 2: Gamma function values ---")

    bases_g2 = [
        ('1,G(1/3),G(2/3),pi,sqrt3',
         [z0, 1, G13, G23, P, S3],
         ['z0', '1', 'G(1/3)', 'G(2/3)', 'pi', 'sqrt3']),
        ('1,G(1/3),G(1/3)^2,pi,pi^2',
         [z0, 1, G13, G13**2, P, P**2],
         ['z0', '1', 'G(1/3)', 'G(1/3)^2', 'pi', 'pi^2']),
        ('1,G(2/3),G(2/3)^2,pi,sqrt3',
         [z0, 1, G23, G23**2, P, S3],
         ['z0', '1', 'G(2/3)', 'G(2/3)^2', 'pi', 'sqrt3']),
        ('1,G(1/3)^3/(2pi),pi,sqrt3',
         [z0, 1, G13**3/(2*P), P, S3],
         ['z0', '1', 'G(1/3)^3/(2pi)', 'pi', 'sqrt3']),
        ('1,Omega_CM,pi,sqrt3,ln3',
         [z0, 1, Omega_CM, P, S3, L3],
         ['z0', '1', 'Omega_CM', 'pi', 'sqrt3', 'ln3']),
        ('1,G(1/3),G(2/3),G(1/4),pi',
         [z0, 1, G13, G23, G14, P],
         ['z0', '1', 'G(1/3)', 'G(2/3)', 'G(1/4)', 'pi']),
        ('1,G(1/6),G(1/3),pi,sqrt3',
         [z0, 1, G16, G13, P, S3],
         ['z0', '1', 'G(1/6)', 'G(1/3)', 'pi', 'sqrt3']),
    ]

    for name, vals, names in bases_g2:
        r = run_pslq(name, vals, names)
        if r: hits.append(r)

    # ------------------------------------------------------------------
    # Group 3: z0 vs products/ratios of constants
    # ------------------------------------------------------------------
    print("\n--- Group 3: Products and ratios ---")

    bases_g3 = [
        ('1,pi*ln3,pi*sqrt3,ln3*sqrt3,pi,ln3,sqrt3',
         [z0, 1, P*L3, P*S3, L3*S3, P, L3, S3],
         ['z0','1','pi*ln3','pi*sqrt3','ln3*sqrt3','pi','ln3','sqrt3']),
        ('1,G13/pi,G23/pi,sqrt3/pi,G13*G23/pi^2',
         [z0, 1, G13/P, G23/P, S3/P, G13*G23/P**2],
         ['z0','1','G(1/3)/pi','G(2/3)/pi','sqrt3/pi','G(1/3)*G(2/3)/pi^2']),
        ('1,ln3/sqrt2,pi/sqrt3,sqrt2*sqrt3,ln3*sqrt3',
         [z0, 1, L3/S2, P/S3, S2*S3, L3*S3],
         ['z0','1','ln3/sqrt2','pi/sqrt3','sqrt2*sqrt3','ln3*sqrt3']),
        ('1,G13^3/pi^2,pi/G13^3,sqrt3',
         [z0, 1, G13**3/P**2, P/G13**3, S3],
         ['z0','1','G(1/3)^3/pi^2','pi/G(1/3)^3','sqrt3']),
    ]

    for name, vals, names in bases_g3:
        r = run_pslq(name, vals, names)
        if r: hits.append(r)

    # ------------------------------------------------------------------
    # Group 4: z0 vs elliptic/hypergeometric
    # ------------------------------------------------------------------
    print("\n--- Group 4: Elliptic integrals ---")

    K_half = ellipk(mpf(1)/2)
    K_quart = ellipk(mpf(1)/4)
    K_third = ellipk(mpf(1)/3)
    AGM_val = agm(1, S2)  # = pi/(2*K(1/2))

    bases_g4 = [
        ('1,K(1/2),pi,sqrt2',
         [z0, 1, K_half, P, S2],
         ['z0','1','K(1/2)','pi','sqrt2']),
        ('1,K(1/3),pi,sqrt3',
         [z0, 1, K_third, P, S3],
         ['z0','1','K(1/3)','pi','sqrt3']),
        ('1,K(1/4),pi,sqrt2,sqrt3',
         [z0, 1, K_quart, P, S2, S3],
         ['z0','1','K(1/4)','pi','sqrt2','sqrt3']),
        ('1,K(1/2)/pi,K(1/3)/pi,sqrt3',
         [z0, 1, K_half/P, K_third/P, S3],
         ['z0','1','K(1/2)/pi','K(1/3)/pi','sqrt3']),
    ]

    for name, vals, names in bases_g4:
        r = run_pslq(name, vals, names)
        if r: hits.append(r)

    # ------------------------------------------------------------------
    # Group 5: Minimal polynomial (is z0 algebraic?)
    # ------------------------------------------------------------------
    print("\n--- Group 5: Minimal polynomial search ---")

    for deg in range(2, 13):
        basis = [z0**k for k in range(deg + 1)]
        try:
            rel = pslq(basis, maxcoeff=100000, maxsteps=20000)
            if rel is not None:
                residual = fabs(sum(r * b for r, b in zip(rel, basis)))
                if residual > 0:
                    digits = max(0, int(-log(residual, 10)))
                else:
                    digits = DPS
                max_c = max(abs(r) for r in rel)
                coeffs = [int(r) for r in rel]
                if digits >= 20 and max_c <= 100000:
                    print(f"  *** Degree {deg}: {coeffs}, {digits} digits, max_coeff={max_c}")
                elif digits >= 10:
                    print(f"  (near) Degree {deg}: {coeffs}, {digits} digits, max_coeff={max_c}")
        except:
            pass

    # ------------------------------------------------------------------
    # Group 6: PSLQ on transforms of z0
    # ------------------------------------------------------------------
    print("\n--- Group 6: PSLQ on transformed z0 ---")

    transforms = {
        '1/z0': 1/z0,
        'z0*18': z0*18,
        'z0*36': z0*36,
        'z0*12': z0*12,
        'z0*6': z0*6,
        'z0*3': z0*3,
        'z0*pi': z0*P,
        'z0*2pi': z0*2*P,
        'sin(pi*z0)': sin(P*z0),
        'cos(pi*z0)': cos(P*z0),
        'tan(pi*z0)': tan(P*z0),
        'z0^2': z0**2,
        'sqrt(z0)': sqrt(z0),
        'ln(z0)': ln(z0),
        'exp(z0)': exp(z0),
        'z0*G(1/3)': z0*G13,
        'z0*G(2/3)': z0*G23,
        'z0*pi*sqrt3': z0*P*S3,
        'z0*G(1/3)^3/pi^2': z0*G13**3/P**2,
    }

    base_consts = [1, P, L2, L3, S2, S3]
    base_names = ['1', 'pi', 'ln2', 'ln3', 'sqrt2', 'sqrt3']

    for tname, tval in transforms.items():
        basis = [tval] + base_consts
        bnames = [tname] + base_names
        r = run_pslq(f"transform:{tname}", basis, bnames)
        if r: hits.append(r)

    # ------------------------------------------------------------------
    # Group 7: PSLQ on transforms with Gamma
    # ------------------------------------------------------------------
    print("\n--- Group 7: Transforms with Gamma ---")

    gamma_consts = [1, G13, G23, P, S3]
    gamma_names = ['1', 'G(1/3)', 'G(2/3)', 'pi', 'sqrt3']

    for tname, tval in transforms.items():
        basis = [tval] + gamma_consts
        bnames = [tname] + gamma_names
        r = run_pslq(f"transform+G:{tname}", basis, bnames, maxcoeff=500)
        if r: hits.append(r)

    # ------------------------------------------------------------------
    # Group 8: Bilinear: z0*const vs other constants
    # ------------------------------------------------------------------
    print("\n--- Group 8: Bilinear relations ---")

    # z0*pi vs {1, ln3, sqrt3, G(1/3), ...}
    bilinear = [
        ('z0*pi', z0*P, [1, L3, S3, G13, G23]),
        ('z0*sqrt3', z0*S3, [1, P, L3, G13, G23]),
        ('z0*ln3', z0*L3, [1, P, S3, S2, G13]),
        ('z0*G(1/3)', z0*G13, [1, P, S3, L3, G23]),
        ('z0*G(2/3)', z0*G23, [1, P, S3, L3, G13]),
        ('z0*pi^2', z0*P**2, [1, P, S3, L3, G13]),
        ('z0*pi*sqrt3', z0*P*S3, [1, P, S3, L3, G13, G23]),
    ]

    for bname, bval, consts in bilinear:
        names_list = ['1', 'c1', 'c2', 'c3', 'c4'] + (['c5','c6'][:len(consts)-4] if len(consts)>4 else [])
        full_basis = [bval] + consts
        full_names = [bname] + [str(c)[:10] for c in consts]
        r = run_pslq(f"bilinear:{bname}", full_basis, full_names, maxcoeff=500)
        if r: hits.append(r)

    # ------------------------------------------------------------------
    # Group 9: Two-constant products in PSLQ
    # ------------------------------------------------------------------
    print("\n--- Group 9: Quadratic PSLQ (z0 + products of 2 constants) ---")

    # z0 vs {1, c_i, c_i*c_j} for pairs from {pi, ln3, sqrt3, G(1/3), G(2/3)}
    const_pool = [('pi',P), ('ln3',L3), ('sqrt3',S3), ('G13',G13), ('G23',G23), ('sqrt2',S2)]
    for i in range(len(const_pool)):
        for j in range(i, len(const_pool)):
            ni, ci = const_pool[i]
            nj, cj = const_pool[j]
            basis = [z0, 1, ci, cj, ci*cj]
            bnames = ['z0', '1', ni, nj, f'{ni}*{nj}']
            r = run_pslq(f"quad:{ni},{nj}", basis, bnames, maxcoeff=500)
            if r: hits.append(r)

    # ------------------------------------------------------------------
    # Group 10: identify() with extended constants
    # ------------------------------------------------------------------
    print("\n--- Group 10: mpmath identify() extended ---")

    for tname, tval in [('z0', z0), ('1/z0', 1/z0), ('z0*pi', z0*P),
                         ('z0*sqrt3', z0*S3), ('z0*12', z0*12),
                         ('z0*G(1/3)', z0*G13), ('z0*G(2/3)', z0*G23),
                         ('z0*pi*sqrt3', z0*P*S3),
                         ('z0*2^(7/3)*sqrt3*pi/G13^3', z0 * mpf(2)**(mpf(7)/3) * S3 * P / G13**3),
                         ('z0*G13^3/(2pi)', z0*G13**3/(2*P)),
                         ('sin(pi*z0)', sin(P*z0)), ('cos(pi*z0)', cos(P*z0)),
                         ('3*z0', 3*z0), ('6*z0', 6*z0),
                         ('z0^2*pi', z0**2*P),
                         ('(1-3*z0)', 1-3*z0)]:
        try:
            mp.dps = 30  # identify works better at lower precision
            val_low = +tval
            ids = identify(val_low, tol=1e-25, full=True)
            if ids:
                for formula in ids[:5]:
                    print(f"  identify({tname}): {formula}")
            mp.dps = DPS
        except Exception as e:
            mp.dps = DPS
            pass

    # ------------------------------------------------------------------
    # Group 11: Deep algebraic (higher maxcoeff)
    # ------------------------------------------------------------------
    print("\n--- Group 11: Deep minimal polynomial (maxcoeff 10^6) ---")
    mp.dps = DPS

    for deg in [3, 4, 5, 6, 8, 10, 12]:
        basis = [z0**k for k in range(deg + 1)]
        try:
            rel = pslq(basis, maxcoeff=1000000, maxsteps=50000)
            if rel is not None:
                residual = fabs(sum(r * b for r, b in zip(rel, basis)))
                if residual > 0:
                    digits = max(0, int(-log(residual, 10)))
                else:
                    digits = DPS
                max_c = max(abs(r) for r in rel)
                coeffs = [int(r) for r in rel]
                if digits >= 30:
                    print(f"  *** Degree {deg}: {coeffs}, {digits} digits, max_coeff={max_c}")
                elif digits >= 15:
                    print(f"  (near) Degree {deg}: {coeffs}, {digits} digits, max_coeff={max_c}")
        except:
            pass

    # ------------------------------------------------------------------
    # Group 12: The theta function itself - inversion approach
    # ------------------------------------------------------------------
    print("\n--- Group 12: Direct theta inversion ---")

    # We know theta_1(pi*z0, q) has modulus = ln(3)/sqrt(2)
    # What is its argument (phase)?
    th1_val = jtheta(1, pi * z0, q)
    print(f"  theta_1(pi*z0, q) = {nstr(th1_val, 30)}")
    print(f"  |theta_1| = {nstr(fabs(th1_val), 30)}")
    print(f"  arg(theta_1) = {nstr(arg(th1_val), 30)}")
    print(f"  arg(theta_1)/pi = {nstr(arg(th1_val)/P, 30)}")

    # The phase of theta_1 at z0
    phase = arg(th1_val)
    print(f"\n  Phase = {nstr(phase, 30)}")
    print(f"  Phase/pi = {nstr(phase/P, 30)}")

    # Is the phase a simple rational multiple of pi?
    phase_over_pi = phase / P
    print(f"\n  Testing phase/pi for rationality:")
    for q_den in range(1, 200):
        for p_num in range(-200, 200):
            frac = mpf(p_num) / q_den
            if fabs(phase_over_pi - frac) < mpf(10)**(-20):
                print(f"    phase/pi = {p_num}/{q_den} ({int(-log(fabs(phase_over_pi - frac), 10))} digits)")

    # PSLQ on phase
    print(f"\n  PSLQ on phase:")
    for name, basis, bnames in [
        ('phase vs {1,pi,sqrt3,ln3}',
         [phase, 1, P, S3, L3],
         ['phase','1','pi','sqrt3','ln3']),
        ('phase vs {1,pi,pi^2,sqrt3}',
         [phase, 1, P, P**2, S3],
         ['phase','1','pi','pi^2','sqrt3']),
    ]:
        r = run_pslq(name, basis, bnames)
        if r: hits.append(r)

    # ------------------------------------------------------------------
    # Group 13: theta_1 derivative / Jacobi relation approach
    # ------------------------------------------------------------------
    print("\n--- Group 13: Using theta_1'(0) and Jacobi identities ---")

    # theta_1'(0, q) = pi * theta_2(0,q) * theta_3(0,q) * theta_4(0,q)
    th2_0 = jtheta(2, 0, q)
    th3_0 = jtheta(3, 0, q)
    th4_0 = jtheta(4, 0, q)
    th1p_0 = P * th2_0 * th3_0 * th4_0

    print(f"  theta_2(0,q) = {nstr(th2_0, 25)}")
    print(f"  theta_3(0,q) = {nstr(th3_0, 25)}")
    print(f"  theta_4(0,q) = {nstr(th4_0, 25)}")
    print(f"  theta_1'(0,q) = {nstr(th1p_0, 25)}")
    print(f"  |theta_1'(0,q)| = {nstr(fabs(th1p_0), 25)}")

    # The ratio theta_1(pi*z0, q) / theta_1'(0, q) relates to sn() etc.
    ratio = th1_val / th1p_0
    print(f"\n  theta_1(pi*z0)/theta_1'(0) = {nstr(ratio, 25)}")
    print(f"  |ratio| = {nstr(fabs(ratio), 25)}")

    # ------------------------------------------------------------------
    # Group 14: Exhaustive small-height search a/b + c/d * X for constants X
    # ------------------------------------------------------------------
    print("\n--- Group 14: Exhaustive a/b + c/d * X search ---")

    special_consts = [
        ('pi', P), ('ln2', L2), ('ln3', L3), ('sqrt2', S2), ('sqrt3', S3),
        ('G(1/3)', G13), ('G(2/3)', G23), ('1/pi', 1/P), ('pi^2', P**2),
        ('ln3/pi', L3/P), ('pi/sqrt3', P/S3), ('sqrt3/pi', S3/P),
        ('G(1/3)/pi', G13/P), ('G(2/3)/pi', G23/P),
        ('G(1/3)^3/(2pi)^2', G13**3/(4*P**2)),
        ('Omega_CM', Omega_CM),
        ('K(1/3)', ellipk(mpf(1)/3)),
        ('K(1/2)', ellipk(mpf(1)/2)),
        ('K(1/3)/pi', ellipk(mpf(1)/3)/P),
        ('sqrt(3)/pi^2', S3/P**2),
        ('G(1/3)*G(2/3)/pi', G13*G23/P),
        ('EulerGamma', EC),
        ('Catalan', CAT),
    ]

    best_match = (0, '', '')
    for xname, xval in special_consts:
        for b in range(1, 51):
            for a in range(-50, 51):
                for d in range(1, 51):
                    for c in [-3,-2,-1,1,2,3]:
                        candidate = mpf(a)/b + (mpf(c)/d) * xval
                        diff = fabs(candidate - z0)
                        if diff > 0 and diff < mpf('1e-8'):
                            digits = int(-log(diff, 10))
                            if digits > best_match[0]:
                                best_match = (digits, f"{a}/{b} + ({c}/{d})*{xname}", nstr(candidate, 25))
                                if digits >= 10:
                                    print(f"    {digits} digits: z0 = {a}/{b} + ({c}/{d})*{xname}")

    if best_match[0] >= 5:
        print(f"  Best: {best_match[0]} digits: {best_match[1]} = {best_match[2]}")

    # ------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUMMARY OF ALL PSLQ HITS (z0 coefficient nonzero)")
    print("=" * 70)

    if hits:
        hits.sort(key=lambda h: -h['digits'])
        for h in hits:
            print(f"\n  [{h['digits']} digits, max_coeff={h['max_coeff']}]")
            print(f"  Basis: {h['name']}")
            print(f"  Coefficients: {h['coeffs']}")
            print(f"  Formula: {h['formula']}")
    else:
        print("\n  No PSLQ relations found involving z0.")

    print("\n  z0 =", nstr(z0, 50))
    print("\n  CONCLUSION: If no hits above, z0 likely has no simple closed form")
    print("  in terms of standard mathematical constants.")

if __name__ == '__main__':
    main()
