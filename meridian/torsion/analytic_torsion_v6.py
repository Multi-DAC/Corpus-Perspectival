#!/usr/bin/env python3
"""
Analytic Torsion on the Fermat Cubic dP_6 — Version 6
======================================================
Phase 26 — Section-product basis.

Key insight: the correct L²(S, O(n)) basis uses products of GLOBAL holomorphic
sections, which are smooth everywhere on the compact surface S:

  φ_{α,β} = s_α(z) · conj(s_β(z)) / P^{(a₁+a₂)/2}

where s_α ∈ H⁰(S, O(a₁)), s_β ∈ H⁰(S, O(a₂)), and a₁ - a₂ = n.

For O(0): a₁ = a₂ = a, basis = {s_α · conj(s_β) / P^a}
For O(5): (a₁, a₂) ∈ {(5,0), (6,1), ...}, and a₁ = a₂ + 5
For O(-5): (a₁, a₂) ∈ {(0,5), (1,6), ...}, and a₂ = a₁ + 5

These functions:
  - Are smooth on all of S (products of global sections, P-normalized)
  - Are in H¹(S, O(n)) — finite Dirichlet energy
  - Break spurious holomorphicity (∂̄(s·t̄/P^a) ≠ 0 due to P)
  - Have bounded integrands for MC integration

Predictions:
  - O(0): exactly 1 zero mode (the constant function)
  - O(-5): all eigenvalues ≥ 10 (Weitzenböck bound)
"""

import numpy as np
from scipy.linalg import eigh
from math import pi, log, sqrt
import json, sys, time

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC = 100000
DOMAIN_R = 4.0
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.05
SEC_MAX = 2       # Max section degree for O(0)
# For O(±5): use levels (0,5) and (1,6)

rng = np.random.default_rng(RNG_SEED)

print("=" * 72)
print("ANALYTIC TORSION ON dP_6 — VERSION 6")
print("Section-product basis (globally smooth)")
print("=" * 72)


# ============================================================
# STAGE 1: SURFACE SAMPLING
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 1: SURFACE SAMPLING")
print("=" * 72)

t0 = time.time()
u = rng.uniform(-DOMAIN_R, DOMAIN_R, (4, N_MC))
a_raw = u[0] + 1j * u[1]
b_raw = u[2] + 1j * u[3]
w_raw = -1.0 - a_raw**3 - b_raw**3
valid = np.abs(w_raw) > 1e-8
a_base, b_base, w_base = a_raw[valid], b_raw[valid], w_raw[valid]

c_principal = np.abs(w_base)**(1/3) * np.exp(1j * np.angle(w_base) / 3)
a_all = np.tile(a_base, 3)
b_all = np.tile(b_base, 3)
c_all = np.concatenate([c_principal, ZETA3*c_principal, ZETA3**2*c_principal])

mask = np.abs(c_all) > C_FLOOR
a_all, b_all, c_all = a_all[mask], b_all[mask], c_all[mask]
N_total = len(a_all)
print(f"  N_MC={N_MC}, total points: {N_total}")


# ============================================================
# STAGE 2: METRIC
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 2: METRIC")
print("=" * 72)

ab, bb, cb = np.conj(a_all), np.conj(b_all), np.conj(c_all)
P = np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2 + 1.0

dc_da = -a_all**2 / c_all**2
dc_db = -b_all**2 / c_all**2
dcb_dab = -ab**2 / cb**2
dcb_dbb = -bb**2 / cb**2

# dP/da = ā + c̄·dc/da, dP/dā = a + c·dc̄/dā, etc.
dP_da = ab + cb * dc_da
dP_dab = a_all + c_all * dcb_dab
dP_db = bb + cb * dc_db
dP_dbb = b_all + c_all * dcb_dbb

JdJ_11 = 1.0 + np.abs(dc_da)**2
JdJ_12 = np.conj(dc_da) * dc_db
JdJ_22 = 1.0 + np.abs(dc_db)**2
P2 = P**2

JdXb_1 = ab + np.conj(dc_da) * cb
JdXb_2 = bb + np.conj(dc_db) * cb
XJ_1 = a_all + c_all * dc_da
XJ_2 = b_all + c_all * dc_db

g11 = JdJ_11/P - JdXb_1*XJ_1/P2
g12 = JdJ_12/P - JdXb_1*XJ_2/P2
g21 = np.conj(g12)
g22 = JdJ_22/P - JdXb_2*XJ_2/P2
det_g = (g11*g22 - g12*g21).real

good = (det_g > 1e-15) & (g11.real > 0) & np.isfinite(det_g)
for nm in ['a_all','b_all','c_all','ab','bb','cb','P','P2','det_g',
           'g11','g12','g21','g22','dc_da','dc_db','dcb_dab','dcb_dbb',
           'dP_da','dP_dab','dP_db','dP_dbb']:
    exec(f"{nm}={nm}[good]")
N_total = len(a_all)

ds = np.where(det_g > 1e-20, det_g, 1.0)
ginv11 = (g22/ds).real; ginv12 = -g12/ds
ginv21 = -g21/ds; ginv22 = (g11/ds).real

domain_vol = (2*DOMAIN_R)**4
weights = det_g * domain_vol / (3*N_MC)
vol_est = np.sum(weights)
vol_exact = 3*pi**2/2
print(f"  Points: {N_total}, Vol={vol_est:.4f} (exact {vol_exact:.4f}, ratio {vol_est/vol_exact:.4f})")


# ============================================================
# STAGE 3: BUILD SECTION BASES
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 3: SECTION BASES H⁰(S, O(a))")
print("=" * 72)

t1 = time.time()

def build_section_basis(a_max):
    """Build monomials for H⁰(S, O(a)): a^i b^j c^l, i+j+l ≤ a, l ∈ {0,1,2}."""
    sections = {}
    for a_deg in range(a_max + 1):
        idx_list = []
        for i in range(a_deg + 1):
            for j in range(a_deg - i + 1):
                for l in range(min(a_deg - i - j, 2) + 1):
                    idx_list.append((i, j, l))
        sections[a_deg] = idx_list
    return sections


# Precompute powers
max_deg = 6
a_pow = [np.ones(N_total, dtype=complex)]
b_pow = [np.ones(N_total, dtype=complex)]
c_pow = [np.ones(N_total, dtype=complex)]
ab_pow = [np.ones(N_total, dtype=complex)]
bb_pow = [np.ones(N_total, dtype=complex)]
cb_pow = [np.ones(N_total, dtype=complex)]
for k in range(1, max_deg + 1):
    a_pow.append(a_pow[-1] * a_all)
    b_pow.append(b_pow[-1] * b_all)
    c_pow.append(c_pow[-1] * c_all)
    ab_pow.append(ab_pow[-1] * ab)
    bb_pow.append(bb_pow[-1] * bb)
    cb_pow.append(cb_pow[-1] * cb)


def eval_sections(idx_list, holomorphic=True):
    """Evaluate sections at MC points. Returns (N_sec, N_total) array."""
    N_sec = len(idx_list)
    S = np.zeros((N_sec, N_total), dtype=complex)
    for n, (i, j, l) in enumerate(idx_list):
        if holomorphic:
            S[n] = a_pow[i] * b_pow[j] * c_pow[l]
        else:
            S[n] = ab_pow[i] * bb_pow[j] * cb_pow[l]
    return S


def eval_section_derivs(idx_list, holomorphic=True):
    """
    Compute ∂s/∂a and ∂s/∂b for holomorphic sections,
    or ∂s̄/∂ā and ∂s̄/∂b̄ for antiholomorphic sections.
    """
    N_sec = len(idx_list)
    Da = np.zeros((N_sec, N_total), dtype=complex)
    Db = np.zeros((N_sec, N_total), dtype=complex)

    for n, (i, j, l) in enumerate(idx_list):
        if holomorphic:
            # ∂s/∂a = i·a^{i-1}·b^j·c^l + l·a^i·b^j·c^{l-1}·dc/da
            if i > 0:
                Da[n] += i * a_pow[i-1] * b_pow[j] * c_pow[l]
            if l > 0:
                Da[n] += l * a_pow[i] * b_pow[j] * c_pow[l-1] * dc_da
            # ∂s/∂b = j·a^i·b^{j-1}·c^l + l·a^i·b^j·c^{l-1}·dc/db
            if j > 0:
                Db[n] += j * a_pow[i] * b_pow[j-1] * c_pow[l]
            if l > 0:
                Db[n] += l * a_pow[i] * b_pow[j] * c_pow[l-1] * dc_db
        else:
            # ∂s̄/∂ā = i·ā^{i-1}·b̄^j·c̄^l + l·ā^i·b̄^j·c̄^{l-1}·dc̄/dā
            if i > 0:
                Da[n] += i * ab_pow[i-1] * bb_pow[j] * cb_pow[l]
            if l > 0:
                Da[n] += l * ab_pow[i] * bb_pow[j] * cb_pow[l-1] * dcb_dab
            # ∂s̄/∂b̄ = j·ā^i·b̄^{j-1}·c̄^l + l·ā^i·b̄^j·c̄^{l-1}·dc̄/db̄
            if j > 0:
                Db[n] += j * ab_pow[i] * bb_pow[j-1] * cb_pow[l]
            if l > 0:
                Db[n] += l * ab_pow[i] * bb_pow[j] * cb_pow[l-1] * dcb_dbb
    return Da, Db


# Build all needed section bases
sections = build_section_basis(max_deg)
for a_deg, idx_list in sections.items():
    print(f"  H⁰(S, O({a_deg})): dim = {len(idx_list)}")


# ============================================================
# STAGE 4: BUILD PRODUCT BASIS FOR EACH TWIST
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 4: PRODUCT BASIS ASSEMBLY")
print("=" * 72)


def build_product_basis(n_twist, level_pairs):
    """
    Build product basis for O(n_twist).

    level_pairs: list of (a1, a2) with a1-a2 = n_twist.
    Basis: {s_α · conj(s_β) / P^{(a1+a2)/2}}

    Returns F, F_abar, F_bbar (basis values and antiholomorphic derivatives),
           and F_a_conj, F_b_conj (holomorphic derivatives of conjugate).
    """
    all_F = []
    all_Fabar = []
    all_Fbbar = []
    all_Fa_conj = []  # ∂(φ̄)/∂a
    all_Fb_conj = []

    for a1, a2 in level_pairs:
        idx1 = sections[a1]
        idx2 = sections[a2]
        d1, d2 = len(idx1), len(idx2)
        k = (a1 + a2) / 2.0  # P-normalization power

        # Evaluate holomorphic sections s_α ∈ H⁰(O(a1)) and their ∂/∂a, ∂/∂b derivs
        S1 = eval_sections(idx1, holomorphic=True)      # (d1, N)
        S1_da, S1_db = eval_section_derivs(idx1, holomorphic=True)  # holomorphic derivs

        # Evaluate antiholomorphic sections conj(s_β) for s_β ∈ H⁰(O(a2))
        Sb2 = eval_sections(idx2, holomorphic=False)     # (d2, N) = ā^i b̄^j c̄^l
        Sb2_dab, Sb2_dbb = eval_section_derivs(idx2, holomorphic=False)  # ∂s̄/∂ā, ∂s̄/∂b̄

        # P-normalization factor
        Pk = P ** (-k)  # (N,)
        dPk_dab = -k * P**(-k-1) * dP_dab  # ∂(P^{-k})/∂ā
        dPk_dbb = -k * P**(-k-1) * dP_dbb
        dPk_da  = -k * P**(-k-1) * dP_da   # ∂(P^{-k})/∂a
        dPk_db  = -k * P**(-k-1) * dP_db

        # For each (α, β) pair: φ_{αβ} = S1[α] · Sb2[β] · P^{-k}
        for alpha in range(d1):
            for beta in range(d2):
                s = S1[alpha]    # holomorphic section value
                sb = Sb2[beta]   # antiholomorphic section value
                f = s * sb * Pk
                all_F.append(f)

                # ∂φ/∂ā = s · [∂s̄/∂ā · P^{-k} + s̄ · ∂P^{-k}/∂ā]
                # (since ∂s/∂ā = 0 for holomorphic s)
                fabar = s * (Sb2_dab[beta] * Pk + sb * dPk_dab)
                all_Fabar.append(fabar)

                # ∂φ/∂b̄ = s · [∂s̄/∂b̄ · P^{-k} + s̄ · ∂P^{-k}/∂b̄]
                fbbar = s * (Sb2_dbb[beta] * Pk + sb * dPk_dbb)
                all_Fbbar.append(fbbar)

                # ∂(φ̄)/∂a: φ̄ = s̄ · s_β · P^{-k}  (conjugate)
                # ∂φ̄/∂a = s̄ · [∂s_β/∂a · P^{-k} + s_β · ∂P^{-k}/∂a]
                # (since ∂s̄/∂a = 0 for antiholomorphic s̄)
                # BUT: we need the conjugate basis, which swaps α↔β roles.
                # For φ_{αβ} = s_α · conj(s_β) / P^k:
                # conj(φ_{αβ}) = conj(s_α) · s_β / P^k
                # ∂(conj(φ_{αβ}))/∂a = conj(s_α) · [∂s_β/∂a] / P^k + conj(s_α) · s_β · ∂(P^{-k})/∂a
                # Here s_β refers to the holomorphic version (not conjugated).
                #
                # We need the holomorphic section s_β ∈ H⁰(O(a2)) and its derivs.
                # These come from the a2 section basis.
                pass  # Will compute below

        # We also need the holomorphic section evaluations for β index (for ∂φ̄/∂a)
        S2 = eval_sections(idx2, holomorphic=True)       # s_β holomorphic
        S2_da, S2_db = eval_section_derivs(idx2, holomorphic=True)

        # And the antiholomorphic evaluations for α index
        Sb1 = eval_sections(idx1, holomorphic=False)     # conj(s_α)

        # Now compute ∂(conj(φ_{αβ}))/∂a and /∂b
        for alpha in range(d1):
            for beta in range(d2):
                sbar_alpha = Sb1[alpha]   # conj(s_α)
                s_beta = S2[beta]         # s_β (holomorphic)

                # ∂(φ̄)/∂a = conj(s_α) · [∂s_β/∂a · P^{-k} + s_β · ∂P^{-k}/∂a]
                fa_c = sbar_alpha * (S2_da[beta] * Pk + s_beta * dPk_da)
                all_Fa_conj.append(fa_c)

                # ∂(φ̄)/∂b = conj(s_α) · [∂s_β/∂b · P^{-k} + s_β · ∂P^{-k}/∂b]
                fb_c = sbar_alpha * (S2_db[beta] * Pk + s_beta * dPk_db)
                all_Fb_conj.append(fb_c)

    F = np.array(all_F)
    Fabar = np.array(all_Fabar)
    Fbbar = np.array(all_Fbbar)
    Fa_conj = np.array(all_Fa_conj)
    Fb_conj = np.array(all_Fb_conj)

    return F, Fabar, Fbbar, Fa_conj, Fb_conj


# Define level pairs for each twist
# O(0): (a, a) for a = 0, 1, 2
o0_pairs = [(a, a) for a in range(SEC_MAX + 1)]
# O(5): (a+5, a) for a = 0, 1
o5_pairs = [(5, 0), (6, 1)]
# O(-5): (a, a+5) for a = 0, 1
om5_pairs = [(0, 5), (1, 6)]

print(f"  Building O(0) basis: levels {o0_pairs}")
F0, F0_abar, F0_bbar, F0_a_c, F0_b_c = build_product_basis(0, o0_pairs)
n0 = F0.shape[0]
print(f"    N_basis = {n0}, memory = {5*F0.nbytes/1e9:.2f} GiB")

print(f"  Building O(5) basis: levels {o5_pairs}")
F5, F5_abar, F5_bbar, F5_a_c, F5_b_c = build_product_basis(5, o5_pairs)
n5 = F5.shape[0]
print(f"    N_basis = {n5}, memory = {5*F5.nbytes/1e9:.2f} GiB")

print(f"  Building O(-5) basis: levels {om5_pairs}")
Fm5, Fm5_abar, Fm5_bbar, Fm5_a_c, Fm5_b_c = build_product_basis(-5, om5_pairs)
nm5 = Fm5.shape[0]
print(f"    N_basis = {nm5}, memory = {5*Fm5.nbytes/1e9:.2f} GiB")

print(f"  Time: {time.time()-t1:.1f}s")


# ============================================================
# STAGE 5: ASSEMBLE Q AND M
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 5: MATRIX ASSEMBLY")
print("=" * 72)


def assemble(n_twist, F, Fabar, Fbbar, Fa_c, Fb_c):
    """Assemble Q and M matrices."""
    t0 = time.time()
    h = P ** (-n_twist)
    w = h * weights

    # Q[i,j] = ∫ g^{αβ̄} (∂φ̄_i/∂z^α)(∂φ_j/∂z̄^β) P^{-n} dV
    Q = np.zeros((F.shape[0], F.shape[0]), dtype=complex)
    for (Dh, Da, gv) in [(Fa_c, Fabar, ginv11), (Fa_c, Fbbar, ginv12),
                          (Fb_c, Fabar, ginv21), (Fb_c, Fbbar, ginv22)]:
        Dw = Dh * (w * gv)[np.newaxis, :]
        Q += Dw @ Da.T

    # M[i,j] = ∫ conj(φ_i) φ_j P^{-n} dV
    Fw = np.conj(F) * w[np.newaxis, :]
    M = Fw @ F.T

    Q = 0.5 * (Q + Q.T.conj())
    M = 0.5 * (M + M.T.conj())
    print(f"    Assembled in {time.time()-t0:.1f}s")
    return Q, M


QM = {}
for label, nt, F_arr, Fab, Fbb, Fac, Fbc in [
    ("O(0)", 0, F0, F0_abar, F0_bbar, F0_a_c, F0_b_c),
    ("O(5)", 5, F5, F5_abar, F5_bbar, F5_a_c, F5_b_c),
    ("O(-5)", -5, Fm5, Fm5_abar, Fm5_bbar, Fm5_a_c, Fm5_b_c),
]:
    print(f"  {label} (n_twist={nt}, N_basis={F_arr.shape[0]}):")
    Q, M = assemble(nt, F_arr, Fab, Fbb, Fac, Fbc)
    qi = np.max(np.abs(Q.imag)); qr = np.max(np.abs(Q.real))
    mi = np.max(np.abs(M.imag)); mr = np.max(np.abs(M.real))
    print(f"    Q im/re={qi/max(qr,1e-30):.2e}, M im/re={mi/max(mr,1e-30):.2e}")
    QM[label] = (Q, M, nt)


# ============================================================
# STAGE 6: EIGENVALUES
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 6: EIGENVALUES")
print("=" * 72)

all_eigs = {}
for label, (Q, M, nt) in QM.items():
    N = M.shape[0]
    Qr = Q.real; Mr = M.real

    eigM = np.linalg.eigvalsh(Mr)
    Mmax = eigM[-1]
    rank = np.sum(eigM > 1e-8 * Mmax)

    Mr_reg = Mr + 1e-8 * Mmax * np.eye(N)

    try:
        eigvals = eigh(Qr, Mr_reg, eigvals_only=True)
        eigvals = np.sort(eigvals)
    except Exception as e:
        print(f"  {label}: ERROR {e}")
        all_eigs[label] = None
        continue

    n_neg = np.sum(eigvals < -0.5)
    n_zero = np.sum(np.abs(eigvals) < 0.5)
    n_pos = np.sum(eigvals > 0.5)
    pos = eigvals[eigvals > 0.5]

    print(f"\n  {label}: rank={rank}/{N}")
    print(f"    Neg: {n_neg}, Zero: {n_zero}, Pos: {n_pos}")
    if len(pos) > 0:
        print(f"    Min pos: {pos[0]:.4f}, Max: {pos[-1]:.1f}")
        print(f"    First 8: {pos[:8].round(3)}")

    if nt == 0:
        print(f"    ZERO MODE CHECK: {n_zero} (expect 1)")
        if n_zero == 1:
            print("    PERFECT")
        elif n_zero <= 3:
            print("    GOOD — close to expected")
        else:
            print("    ISSUE — too many zero modes")

    if nt == -5 and len(pos) > 0:
        print(f"    WEITZENBOCK: min λ = {pos[0]:.4f} (expect ≥ 10)")
        if pos[0] > 8:
            print("    PASSED")
        elif pos[0] > 5:
            print("    PARTIAL")
        else:
            print("    FAILED")

    all_eigs[label] = eigvals


# ============================================================
# STAGE 7: TORSION AND THRESHOLD
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 7: TORSION")
print("=" * 72)

results = {}
for label, eigs in all_eigs.items():
    if eigs is None:
        continue
    pos = eigs[eigs > 0.5]
    if len(pos) == 0:
        continue
    zp = -np.sum(np.log(pos))
    L = pos[-1]
    C = vol_est / (8*pi**2)
    N_w = vol_est * L**2 / (16*pi**2)
    tail = C * (-L**2*log(L)/2 + L**2/4)
    total = zp + tail
    r = abs(tail/zp) if abs(zp) > 1e-10 else float('inf')
    print(f"  {label}: N_eigs={len(pos)}, ζ'(comp)={zp:.4f}, tail={tail:.4f}, total={total:.4f}, |tail/comp|={r:.1f}")
    results[label] = {'total': total, 'computed': zp, 'tail': tail, 'N_eigs': len(pos), 'N_weyl': N_w}

target = log(3)/sqrt(2)
print(f"\n  Target: ln(3)/√2 = {target:.10f}")

if all(k in results for k in ["O(0)", "O(5)", "O(-5)"]):
    f0 = results["O(0)"]['total']
    f5 = results["O(5)"]['total']
    fm5 = results["O(-5)"]['total']
    threshold = f0 + (5/12)*(f5 + fm5)
    print(f"  f(O)={f0:.4f}, f(L⁵)={f5:.4f}, f(L⁻⁵)={fm5:.4f}")
    print(f"  Threshold = {threshold:.6f}")
    print(f"  f(L⁻⁵) - f(L⁵) = {fm5-f5:.4f}")

# Save
output = {'version': 6, 'basis': 'section_product', 'K_MAX': SEC_MAX,
          'N_MC': N_MC, 'N_total': N_total, 'domain_R': DOMAIN_R,
          'vol_est': float(vol_est), 'vol_exact': float(vol_exact),
          'target': float(target)}
for label, eigs in all_eigs.items():
    key = label.replace("(","").replace(")","").replace("-","m")
    if eigs is not None:
        pos = eigs[eigs > 0.5]
        output[f'{key}_N_basis'] = len(eigs)
        output[f'{key}_N_pos'] = int(len(pos))
        output[f'{key}_N_zero'] = int(np.sum(np.abs(eigs) < 0.5))
        if len(pos) > 0:
            output[f'{key}_min'] = float(pos[0])
            output[f'{key}_first10'] = pos[:10].tolist()
for k, v in results.items():
    key = k.replace("(","").replace(")","").replace("-","m")
    output[f'zeta_{key}'] = v

with open('analytic_torsion_v6_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n  Saved to analytic_torsion_v6_results.json")
print(f"{'=' * 72}")
print("COMPLETE")
print(f"{'=' * 72}")
