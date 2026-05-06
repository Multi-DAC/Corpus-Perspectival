"""
C_GB from First Principles — Symbolic Tensor Computation
=========================================================

Physical chain:
  5D Gauss-Bonnet term
  → Davis (2002) modified junction conditions on RS₁ brane
  → Anisotropic correction at O(H²) on FRW brane
  → K_eff breaking in cuscuton sector
  → C_GB = ε₁/α̂

Every tensor contraction computed symbolically with sympy.

References:
  - Davis (2002), hep-th/0208205 — GB junction conditions
  - Charmousis & Dufaux (2002), hep-th/0202107 — GB cosmology in RS
  - Gravanis & Willison (2003), gr-qc/0306029 — GB Israel conditions
"""

import sympy as sp
from sympy import Rational, sqrt, expand, factor, symbols, Matrix, simplify
from itertools import product as iterproduct

# ============================================================
# CONVENTIONS
# ============================================================
# Signature: (−,+,+,+) on the brane (orthonormal frame)
# Extrinsic curvature: K_μν = −½ £_n h_μν (outward normal)
# Static RS: K^μ_ν = −k δ^μ_ν
# Z₂ orbifold: [K_μν] = 2 K_μν^+

# ============================================================
# SYMBOLS
# ============================================================
k = sp.Symbol('k', positive=True)
H = sp.Symbol('H', positive=True)
Hdot = sp.Symbol('Hdot', real=True)
w = sp.Symbol('w', real=True)
alpha = sp.Symbol('alpha', positive=True)  # α_GB (5D coupling, dimension length²)

# Extrinsic curvature: K^0_0 = a, K^i_j = b δ^i_j
a_sym, b_sym = sp.symbols('a b')

# Perturbation parameters
beta_s, gamma_s = sp.symbols('beta gamma')

# Flat metric in orthonormal frame
eta = {}
for mu in range(4):
    for nu in range(4):
        eta[(mu, nu)] = sp.Integer(-1) if mu == nu == 0 else (sp.Integer(1) if mu == nu else sp.Integer(0))

print("=" * 70)
print("C_GB FROM FIRST PRINCIPLES")
print("=" * 70)

# ============================================================
# PART 1: THIRD FUNDAMENTAL FORM J_μν
# ============================================================
# J_μν = (1/3)(2K K_μρ K^ρ_ν + K_ρσ K^ρσ K_μν
#              − 2 K_μρ K^ρσ K_σν − K² K_μν)
#
# For diagonal K^μ_ν = diag(a, b, b, b):
#   K = a + 3b
#   K_ρσ K^ρσ = a² + 3b²
#   (K³)^0_0 = a³, (K³)^i_j = b³

K_tr = a_sym + 3*b_sym
K_sq_tr = a_sym**2 + 3*b_sym**2

# K_μν (lower): K_{00} = η_{00} a = -a, K_{ij} = η_{ii} b = b
# K^μν (upper): same as K_μν for diagonal with η (K^{00} = -a, K^{ii} = b)
# K_μρ K^ρ_ν = (K²)^μ_ν: diagonal with entries a², b²

# J^μ_ν (mixed) for diagonal K:
# J^μ_ν = (1/3)(2K (K²)^μ_ν + K_ρσK^ρσ K^μ_ν - 2(K³)^μ_ν - K² K^μ_ν)

J_00 = Rational(1, 3) * (2*K_tr*a_sym**2 + K_sq_tr*a_sym - 2*a_sym**3 - K_tr**2 * a_sym)
J_ii = Rational(1, 3) * (2*K_tr*b_sym**2 + K_sq_tr*b_sym - 2*b_sym**3 - K_tr**2 * b_sym)

J_00 = expand(J_00)
J_ii = expand(J_ii)
J_trace = expand(J_00 + 3*J_ii)

print("\nPART 1: Third fundamental form J^μ_ν (diagonal K)")
print(f"  J^0_0 = {J_00}")
print(f"  J^i_j = {J_ii}")
print(f"  tr(J) = {J_trace}")

# Isotropic check: a = b = -k
J00_iso = expand(J_00.subs([(a_sym, -k), (b_sym, -k)]))
Jii_iso = expand(J_ii.subs([(a_sym, -k), (b_sym, -k)]))
print(f"\n  Isotropic check (a=b=-k):")
print(f"    J^0_0 = {J00_iso}   (expect 2k³)")
print(f"    J^i_j = {Jii_iso}   (expect 2k³)")
assert J00_iso == 2*k**3, f"FAIL: J^0_0 isotropic = {J00_iso}"
assert Jii_iso == 2*k**3, f"FAIL: J^i_j isotropic = {Jii_iso}"
print("    ✓ PASSED")

# ============================================================
# PART 2: (3J − J h) COMBINATION
# ============================================================
GB_J00 = expand(3*J_00 - J_trace)
GB_Jii = expand(3*J_ii - J_trace)

print(f"\nPART 2: (3J - Jh)^μ_ν")
print(f"  (3J-Jh)^0_0 = {GB_J00}")
print(f"  (3J-Jh)^i_j = {GB_Jii}")

# Isotropic check
GB_J00_iso = expand(GB_J00.subs([(a_sym, -k), (b_sym, -k)]))
GB_Jii_iso = expand(GB_Jii.subs([(a_sym, -k), (b_sym, -k)]))
print(f"\n  Isotropic check:")
print(f"    (3J-Jh)^0_0 = {GB_J00_iso}   (expect -2k³)")
print(f"    (3J-Jh)^i_j = {GB_Jii_iso}   (expect -2k³)")
# Monograph confirms: 3J=6k³h, Jh=8k³h → 3J-Jh = -2k³h
assert GB_J00_iso == -2*k**3, f"FAIL: {GB_J00_iso}"
assert GB_Jii_iso == -2*k**3, f"FAIL: {GB_Jii_iso}"
print("    ✓ PASSED")

# ============================================================
# PART 3: LINEARIZE (3J-Jh) AROUND STATIC RS
# ============================================================
# a = -(k + β), b = -(k + γ) where β, γ ~ O(H²/k)
# Expand to first order in β, γ

GB_J00_full = GB_J00.subs([(a_sym, -k - beta_s), (b_sym, -k - gamma_s)])
GB_Jii_full = GB_Jii.subs([(a_sym, -k - beta_s), (b_sym, -k - gamma_s)])

# O(1) part
GB_J00_0 = expand(GB_J00_full.subs([(beta_s, 0), (gamma_s, 0)]))
GB_Jii_0 = expand(GB_Jii_full.subs([(beta_s, 0), (gamma_s, 0)]))

# Linear coefficients
dGBJ00_db = expand(sp.diff(GB_J00_full, beta_s).subs([(beta_s, 0), (gamma_s, 0)]))
dGBJ00_dg = expand(sp.diff(GB_J00_full, gamma_s).subs([(beta_s, 0), (gamma_s, 0)]))
dGBJ_ii_db = expand(sp.diff(GB_Jii_full, beta_s).subs([(beta_s, 0), (gamma_s, 0)]))
dGBJ_ii_dg = expand(sp.diff(GB_Jii_full, gamma_s).subs([(beta_s, 0), (gamma_s, 0)]))

print(f"\nPART 3: Linearization around RS background")
print(f"  (3J-Jh)^0_0: O(1) = {GB_J00_0}")
print(f"    ∂/∂β = {dGBJ00_db}")
print(f"    ∂/∂γ = {dGBJ00_dg}")
print(f"  (3J-Jh)^i_j: O(1) = {GB_Jii_0}")
print(f"    ∂/∂β = {dGBJ_ii_db}")
print(f"    ∂/∂γ = {dGBJ_ii_dg}")

# ============================================================
# PART 4: INTRINSIC FRW CURVATURE
# ============================================================
# Orthonormal frame, all-lower Riemann:
# R̂_{0i0j} = (Ḣ+H²)δ_{ij}
# R̂_{ijkl} = H²(δ_{ik}δ_{jl} - δ_{il}δ_{jk})
# Plus all components from Riemann symmetries.

def build_FRW_Riemann():
    """Build R̂_{μρνσ} for FRW in orthonormal frame."""
    R = {}
    for mu, rho, nu, sig in iterproduct(range(4), repeat=4):
        R[(mu, rho, nu, sig)] = sp.Integer(0)

    HdH2 = Hdot + H**2  # = -ä/a in FRW

    for i in range(1, 4):
        for j in range(1, 4):
            dij = sp.Integer(1) if i == j else sp.Integer(0)
            # R̂_{0i0j} and symmetry-related
            R[(0, i, 0, j)] = HdH2 * dij
            R[(i, 0, 0, j)] = -HdH2 * dij
            R[(0, i, j, 0)] = -HdH2 * dij
            R[(i, 0, j, 0)] = HdH2 * dij

            for kk in range(1, 4):
                for l in range(1, 4):
                    dik = sp.Integer(1) if i == kk else sp.Integer(0)
                    djl = sp.Integer(1) if j == l else sp.Integer(0)
                    dil = sp.Integer(1) if i == l else sp.Integer(0)
                    djk = sp.Integer(1) if j == kk else sp.Integer(0)
                    R[(i, j, kk, l)] = H**2 * (dik * djl - dil * djk)
    return R

R_hat = build_FRW_Riemann()

# Ricci tensor (lower): R̂_{μν} = Σ_ρ η^{ρρ} R̂_{ρμρν}
def Ricci_lower(mu, nu):
    return sum(eta[(rho, rho)] * R_hat[(rho, mu, rho, nu)] for rho in range(4))

R_scalar = sum(eta[(mu, mu)] * Ricci_lower(mu, mu) for mu in range(4))

print(f"\nPART 4: FRW intrinsic curvature")
print(f"  R̂_{{00}} = {expand(Ricci_lower(0, 0))}")
print(f"  R̂_{{11}} = {expand(Ricci_lower(1, 1))}")
print(f"  R̂ = {expand(R_scalar)}")
print(f"  Expected: R̂_00 = 3(Ḣ+H²), R̂_ii = -(Ḣ+3H²), R̂ = -6Ḣ-12H²")

# ============================================================
# PART 5: P TENSOR AND P·K CONTRACTION
# ============================================================
# P_{μανβ} = R̂_{μανβ}
#   + (R̂_{μβ}η_{αν} - R̂_{μν}η_{αβ} + R̂_{αν}η_{μβ} - R̂_{αβ}η_{μν})
#   + (R̂/2)(η_{μν}η_{αβ} - η_{μβ}η_{αν})

def P_lower(mu, al, nu, be):
    """P_{μανβ} from Davis (2002)."""
    t1 = R_hat[(mu, al, nu, be)]
    t2 = (Ricci_lower(mu, be) * eta[(al, nu)]
          - Ricci_lower(mu, nu) * eta[(al, be)]
          + Ricci_lower(al, nu) * eta[(mu, be)]
          - Ricci_lower(al, be) * eta[(mu, nu)])
    t3 = Rational(1, 2) * R_scalar * (
        eta[(mu, nu)] * eta[(al, be)] - eta[(mu, be)] * eta[(al, nu)])
    return t1 + t2 + t3

# K^{ρσ} in orthonormal frame for diagonal K^μ_ν = diag(a, b, b, b):
# K_{ρσ} = η_{ρρ} K^ρ_σ → K_{00} = -a, K_{ii} = b
# K^{ρσ} = η^{ρρ}η^{σσ} K_{ρσ} → K^{00} = -a, K^{ii} = b
def K_upper_comp(rho, sig):
    if rho != sig:
        return sp.Integer(0)
    return -a_sym if rho == 0 else b_sym

# (P·K)_{μν} = Σ_{ρσ} P_{μρνσ} K^{ρσ}
def PK_lower(mu, nu):
    val = sp.Integer(0)
    for rho in range(4):
        # K^{ρσ} is diagonal
        val += P_lower(mu, rho, nu, rho) * K_upper_comp(rho, rho)
    return expand(val)

# Compute P·K in lower indices
PK_00_low = PK_lower(0, 0)
PK_11_low = PK_lower(1, 1)

# Convert to mixed: (P·K)^μ_ν = η^{μμ} (P·K)_{μν}
PK_00_mix = expand(eta[(0, 0)] * PK_00_low)  # = -(P·K)_{00}
PK_ii_mix = expand(eta[(1, 1)] * PK_11_low)  # = (P·K)_{11}

print(f"\nPART 5: P·K contraction (general K)")
print(f"  (P·K)^0_0 = {PK_00_mix}")
print(f"  (P·K)^i_j = {PK_ii_mix}")

# Isotropic de Sitter check: a = b = -k, Ḣ = 0
PK_00_iso = expand(PK_00_mix.subs([(a_sym, -k), (b_sym, -k), (Hdot, 0)]))
PK_ii_iso = expand(PK_ii_mix.subs([(a_sym, -k), (b_sym, -k), (Hdot, 0)]))
print(f"\n  Isotropic de Sitter check (a=b=-k, Ḣ=0):")
print(f"    (P·K)^0_0 = {PK_00_iso}   (expect 3kH²)")
print(f"    (P·K)^i_j = {PK_ii_iso}   (expect 3kH²)")

# CRITICAL CHECK: does the monograph's P·K = -3k³ h for flat brane (H=0) hold?
PK_00_flat = expand(PK_00_mix.subs([(H, 0), (Hdot, 0)]))
PK_ii_flat = expand(PK_ii_mix.subs([(H, 0), (Hdot, 0)]))
print(f"\n  Flat brane check (H=0, Ḣ=0):")
print(f"    (P·K)^0_0 = {PK_00_flat}   (expect 0 — R̂=0 for flat brane)")
print(f"    (P·K)^i_j = {PK_ii_flat}   (expect 0)")
print(f"    NOTE: Davis P uses intrinsic R̂. For FLAT brane, R̂=0 → P=0 → P·K=0.")
print(f"    The monograph's P·K = -3k³h (line 570) uses P=K⊗K, NOT Davis definition.")

# ============================================================
# PART 6: P·K AT LEADING ORDER K = -k (for FRW brane)
# ============================================================
# P is O(H², Ḣ) from intrinsic curvature.
# K at leading order is -k δ^μ_ν.
# So P·K at leading order uses K₀ = -k:

PK_00_lead = expand(PK_00_mix.subs([(a_sym, -k), (b_sym, -k)]))
PK_ii_lead = expand(PK_ii_mix.subs([(a_sym, -k), (b_sym, -k)]))

print(f"\nPART 6: P·K at leading-order K (a=b=-k, general H,Ḣ)")
print(f"  (P·K)^0_0 = {PK_00_lead}")
print(f"  (P·K)^i_j = {PK_ii_lead}")

# Substitute Ḣ = -(3/2)(1+w)H² (Friedmann relation for perfect fluid)
PK_00_FRW = expand(PK_00_lead.subs(Hdot, -Rational(3, 2)*(1+w)*H**2))
PK_ii_FRW = expand(PK_ii_lead.subs(Hdot, -Rational(3, 2)*(1+w)*H**2))
print(f"\n  With Ḣ = -(3/2)(1+w)H²:")
print(f"    (P·K)^0_0 = {PK_00_FRW}")
print(f"    (P·K)^i_j = {PK_ii_FRW}")

# de Sitter (w=-1, Ḣ=0):
PK_00_dS = expand(PK_00_FRW.subs(w, -1))
PK_ii_dS = expand(PK_ii_FRW.subs(w, -1))
print(f"\n  de Sitter (w=-1):")
print(f"    (P·K)^0_0 = {PK_00_dS}")
print(f"    (P·K)^i_j = {PK_ii_dS}")

# Matter (w=0):
PK_00_mat = expand(PK_00_FRW.subs(w, 0))
PK_ii_mat = expand(PK_ii_FRW.subs(w, 0))
print(f"\n  Matter (w=0):")
print(f"    (P·K)^0_0 = {PK_00_mat}")
print(f"    (P·K)^i_j = {PK_ii_mat}")

# ============================================================
# PART 7: FULL JUNCTION CONDITION AT O(H²)
# ============================================================
# Davis junction (Z₂, mixed indices):
#   K^μ_ν - K δ^μ_ν + 2α[(3J-Jh)^μ_ν + 2(P·K)^μ_ν] = -(κ₅²/2) S^μ_ν
#
# K^0_0 = -(k+β), K^i_j = -(k+γ), K = -(4k+β+3γ)
# S^0_0 = -(σ+ρ), S^i_j = (-σ+p)  [tension + perfect fluid]
#
# 00: K^0_0 - K = 3k + 3γ
# ij: K^i_j - K = 3k + β + 2γ
#
# At O(1): 3k + 2α(-4k³) = (κ₅²/2)σ  → fine-tuning
# At O(H²): subtract O(1) equation

print(f"\n{'='*70}")
print(f"PART 7: Junction conditions at O(H²)")
print(f"{'='*70}")

# Standard part (no GB) at O(H²):
# 00: 3γ = (κ₅²/2)ρ
# ij: β + 2γ = -(κ₅²/2)p

# GB correction at O(H²) has two sources:
# A) Linearized (3J-Jh) in β, γ
# B) P·K at leading K

# GB 00 correction:
GB_corr_00 = 2*alpha*(dGBJ00_db*beta_s + dGBJ00_dg*gamma_s + 2*PK_00_lead)
GB_corr_ii = 2*alpha*(dGBJ_ii_db*beta_s + dGBJ_ii_dg*gamma_s + 2*PK_ii_lead)

print(f"\n  GB correction to 00 equation:")
print(f"    2α[∂(3J-Jh)₀₀/∂β · β + ∂(3J-Jh)₀₀/∂γ · γ + 2(P·K)₀₀]")
print(f"    = 2α[({dGBJ00_db})β + ({dGBJ00_dg})γ + 2({PK_00_lead})]")
print(f"\n  GB correction to ij equation:")
print(f"    = 2α[({dGBJ_ii_db})β + ({dGBJ_ii_dg})γ + 2({PK_ii_lead})]")

# Full O(H²) equations:
# (I)  3γ + 2α[(dGBJ00_db)β + (dGBJ00_dg)γ + 2·PK_00_lead] = (κ₅²/2)ρ
# (II) β + 2γ + 2α[(dGBJ_ii_db)β + (dGBJ_ii_dg)γ + 2·PK_ii_lead] = -(κ₅²/2)p

# Solve for β, γ in terms of ρ, p (linear system):
kappa5sq = sp.Symbol('kappa5sq', positive=True)
rho, p_var = sp.symbols('rho p', real=True)

# Coefficient matrix for [β, γ]:
A11 = 2*alpha*dGBJ00_db
A12 = sp.Integer(3) + 2*alpha*dGBJ00_dg
A21 = sp.Integer(1) + 2*alpha*dGBJ_ii_db
A22 = sp.Integer(2) + 2*alpha*dGBJ_ii_dg

# RHS:
b1 = kappa5sq/2 * rho - 4*alpha*PK_00_lead
b2 = -kappa5sq/2 * p_var - 4*alpha*PK_ii_lead

print(f"\n  Linear system for [β, γ]:")
print(f"    [{A11}]β + [{A12}]γ = (κ₅²/2)ρ - 4α({PK_00_lead})")
print(f"    [{A21}]β + [{A22}]γ = -(κ₅²/2)p - 4α({PK_ii_lead})")

# Solve symbolically
M = sp.Matrix([[A11, A12], [A21, A22]])
rhs_vec = sp.Matrix([b1, b2])
det_M = expand(M.det())
print(f"\n  Determinant = {det_M}")

# Solve by Cramer's rule (cleaner for display)
beta_sol = expand((A22*b1 - A12*b2) / det_M)
gamma_sol = expand((A11*b2 - A21*b1) / det_M)

# This is getting complex. Let's work to O(α) — drop α² terms.
# At O(α⁰): β₀ = -(κ₅²/2)(2ρ/3 + p), γ₀ = (κ₅²/6)ρ
# At O(α¹): corrections from GB

# Standard (α=0):
beta_0 = expand((-kappa5sq/2 * p_var * 3 - kappa5sq/2 * rho * 2) / 3)
gamma_0 = expand(kappa5sq * rho / 6)

# Wait, let me solve the α=0 system properly:
# 3γ = (κ₅²/2)ρ → γ₀ = κ₅²ρ/6
# β + 2γ = -(κ₅²/2)p → β₀ = -(κ₅²/2)p - 2γ₀ = -(κ₅²/2)p - κ₅²ρ/3
gamma_0 = kappa5sq * rho / 6
beta_0 = -kappa5sq * p_var / 2 - kappa5sq * rho / 3

print(f"\n  Standard RS (α=0):")
print(f"    γ₀ = {gamma_0}")
print(f"    β₀ = {beta_0}")

# Verify with p = wρ:
gamma_0w = gamma_0.subs(p_var, w*rho)
beta_0w = expand(beta_0.subs(p_var, w*rho))
print(f"    With p=wρ: γ₀ = {gamma_0w}, β₀ = {beta_0w}")

# Friedmann: γ₀ = H²/(2k) requires κ₅²ρ/6 = H²/(2k), so ρ = 3H²/(κ₅²k) = 3M₅³H²/k
# And β₀ = -(2+3w)κ₅²ρ/6 = -(2+3w)H²/(2k) ✓

# ============================================================
# PART 8: GB CORRECTION TO FRIEDMANN EQUATION
# ============================================================
# At O(α), the correction to γ (→ Friedmann) and β (→ Raychaudhuri) are:
#
# From eq (I) at O(α):
# 3·δγ + 2α[(dGBJ00_db)·β₀ + (dGBJ00_dg)·γ₀ + 2·PK_00] = 0
# → δγ = -(2α/3)[(dGBJ00_db)·β₀ + (dGBJ00_dg)·γ₀ + 2·PK_00]
#
# From eq (II) at O(α):
# δβ + 2·δγ + 2α[(dGBJ_ii_db)·β₀ + (dGBJ_ii_dg)·γ₀ + 2·PK_ii] = 0
# → δβ = -2·δγ - 2α[(dGBJ_ii_db)·β₀ + (dGBJ_ii_dg)·γ₀ + 2·PK_ii]

print(f"\n{'='*70}")
print(f"PART 8: GB correction at O(α)")
print(f"{'='*70}")

# Substitute β₀, γ₀ into the GB terms
# Use p = wρ and ρ = 3H²/(κ₅²k) (from Friedmann)
rho_H = 3*H**2 / (kappa5sq * k)

beta_0_H = expand(beta_0.subs([(p_var, w*rho), (rho, rho_H)]))
gamma_0_H = expand(gamma_0.subs(rho, rho_H))

print(f"\n  β₀ = {beta_0_H}")
print(f"  γ₀ = {gamma_0_H}")

# (3J-Jh) linearization coefficients (already computed):
print(f"\n  Linearization coefficients:")
print(f"    ∂(3J-Jh)₀₀/∂β = {dGBJ00_db}")
print(f"    ∂(3J-Jh)₀₀/∂γ = {dGBJ00_dg}")
print(f"    ∂(3J-Jh)ᵢⱼ/∂β = {dGBJ_ii_db}")
print(f"    ∂(3J-Jh)ᵢⱼ/∂γ = {dGBJ_ii_dg}")

# GB source for 00 equation:
src_00 = expand(dGBJ00_db * beta_0_H + dGBJ00_dg * gamma_0_H + 2*PK_00_lead)
src_ii = expand(dGBJ_ii_db * beta_0_H + dGBJ_ii_dg * gamma_0_H + 2*PK_ii_lead)

# Substitute Ḣ = -(3/2)(1+w)H²
src_00_FRW = expand(src_00.subs(Hdot, -Rational(3, 2)*(1+w)*H**2))
src_ii_FRW = expand(src_ii.subs(Hdot, -Rational(3, 2)*(1+w)*H**2))

print(f"\n  GB source terms (with Ḣ = -(3/2)(1+w)H²):")
print(f"    S₀₀ = {src_00_FRW}")
print(f"    Sᵢⱼ = {src_ii_FRW}")

# Factor out H²:
src_00_coeff = expand(src_00_FRW / H**2)
src_ii_coeff = expand(src_ii_FRW / H**2)
print(f"\n    S₀₀/H² = {src_00_coeff}")
print(f"    Sᵢⱼ/H² = {src_ii_coeff}")

# δγ = -(2α/3) · S₀₀
# Since γ₀ = H²/(2k), the fractional correction is:
# δγ/γ₀ = -(2α/3)(S₀₀/H²) × (2k) = -(4αk/3)(S₀₀/H²)

delta_gamma_over_gamma = expand(-Rational(4,1) * alpha * k / 3 * src_00_coeff)
print(f"\n  δγ/γ₀ = {delta_gamma_over_gamma}")

# The modified Friedmann equation:
# γ = γ₀ + δγ = γ₀(1 + δγ/γ₀)
# H² = 2kγ = 2k·γ₀·(1 + δγ/γ₀)
# So: H²_modified / H²_standard = 1 + δγ/γ₀

# For de Sitter (w=-1):
dg_dS = expand(delta_gamma_over_gamma.subs(w, -1))
print(f"\n  de Sitter (w=-1): δγ/γ₀ = {dg_dS}")
print(f"    → δH²/H² = {dg_dS}")
print(f"    Expected from literature: -(4/3)αk² [Charmousis-Dufaux 2002]")

# For matter (w=0):
dg_mat = expand(delta_gamma_over_gamma.subs(w, 0))
print(f"\n  Matter (w=0): δγ/γ₀ = {dg_mat}")

# ============================================================
# PART 9: EXTRACT THE ANISOTROPY → K_eff
# ============================================================
print(f"\n{'='*70}")
print(f"PART 9: Anisotropy and K_eff extraction")
print(f"{'='*70}")

# The standard RS has β₀ ≠ γ₀ (anisotropic K even without GB).
# The GB adds δβ ≠ δγ, modifying the anisotropy.
#
# The cuscuton K_eff comes from the DIFFERENCE between what the
# Friedmann equation predicts and what the Raychaudhuri equation gives.
#
# Standard: Friedmann gives H², Raychaudhuri gives Ḣ = -(3/2)(1+w)H².
# These are consistent (K_eff = 0).
#
# With GB: the 00 and ij junction conditions give DIFFERENT modifications
# to H² and Ḣ. The inconsistency = K_eff ≠ 0.
#
# The anisotropy in the GB source: ΔS = S₀₀ - Sᵢⱼ
# This is what produces K_eff.

Delta_S = expand(src_00_FRW - src_ii_FRW)
Delta_S_coeff = expand(Delta_S / H**2)

print(f"\n  GB source anisotropy: ΔS = S₀₀ - Sᵢⱼ")
print(f"    ΔS = {Delta_S}")
print(f"    ΔS/H² = {Delta_S_coeff}")

# For de Sitter (w=-1):
DS_dS = expand(Delta_S_coeff.subs(w, -1))
print(f"\n  de Sitter: ΔS/H² = {DS_dS}")

# For matter (w=0):
DS_mat = expand(Delta_S_coeff.subs(w, 0))
print(f"\n  Matter: ΔS/H² = {DS_mat}")

# General w:
print(f"\n  General w: ΔS/H² = {Delta_S_coeff}")

# ============================================================
# PART 10: FROM ANISOTROPY TO C_GB
# ============================================================
print(f"\n{'='*70}")
print(f"PART 10: C_GB extraction")
print(f"{'='*70}")

# The effective K_eff in the 4D theory:
# K_eff = ε₁ X where X = Φ̇²/2
#
# The GB-induced anisotropy acts as an effective ρ+p:
# δ(ρ+p)_eff = -2·(δβ - δγ) / κ₅²  [from the junction conditions]
#
# But δβ - δγ comes from the anisotropy in the GB source.
# From the junction equations:
# δγ = -(2α/3)S₀₀
# δβ = -2δγ - 2α·Sᵢⱼ = (4α/3)S₀₀ - 2α·Sᵢⱼ
# δβ - δγ = (4α/3)S₀₀ - 2α·Sᵢⱼ + (2α/3)S₀₀ = 2α·S₀₀ - 2α·Sᵢⱼ = 2α·ΔS
#
# So: δ(ρ+p)_eff = -4α·ΔS/κ₅²

# For the cuscuton, ρ+p = K_eff = ε₁X.
# Also, X = Φ̇²/2 is related to H through the cuscuton constraint:
# Φ̇ = μ²/(2kζ₀) [schematic — from the constraint equation]
# This is model-dependent. But the RATIO that gives C_GB is:
#
# ε₁ = α̂ × C_GB
# where α̂ = α_GB × k² (dimensionless from spectral action)
#
# The GB modification to the Friedmann equation:
# δH²/H² = (2α/3)(S₀₀/H²) [with sign from our convention]
#
# In the literature (Charmousis-Dufaux), for de Sitter:
# δH²/H² = -(4/3)α_GB k²
# This is the ISOTROPIC part.
#
# The ANISOTROPIC part (ΔS) is what produces K_eff.

# Let me compute the Friedmann modification coefficient:
# δH²/H² = -(4α/3) × (S₀₀/H²)

print("\n  Checking Friedmann modification against literature...")

# The modification should be a known expression.
# For de Sitter: δH²/H² = -(4/3)αk² [Charmousis-Dufaux]
# Our S₀₀/H² at de Sitter:
S00_dS = expand(src_00_coeff.subs(w, -1))
friedmann_mod_dS = expand(-Rational(4, 3) * alpha * S00_dS)
# But this should equal -(4/3)αk², so S₀₀/H² should be k.
# Let me check:
print(f"    S₀₀/H² at de Sitter = {S00_dS}")
print(f"    → δH²/H² = -(4α/3)×{S00_dS} = {friedmann_mod_dS}")
print(f"    Literature: -(4/3)α·k²")

# ============================================================
# PART 11: DIRECT KK REDUCTION APPROACH
# ============================================================
print(f"\n{'='*70}")
print(f"PART 11: KK reduction — direct C_GB computation")
print(f"{'='*70}")

# The GB invariant in 5D: G₅ = R² - 4R_{MN}R^{MN} + R_{MNPQ}R^{MNPQ}
# On the RS background with FRW brane:
# ds² = e^{2A(y)}(-dt² + a²(t)δ_{ij}dx^idx^j) + dy²
# A(y) = -k|y|
#
# The 5D Riemann has contributions from:
# (a) The warp factor: R_{y0y0} = A''δ(y) - A'², etc.
# (b) The FRW expansion: R_{0i0j} ~ ä/a, R_{ijkl} ~ H², etc.
#
# After KK reduction:
# ∫₀^{y_c} dy e^{4A} G₅ → 4D terms including kinetic correction
#
# The kinetic correction to the cuscuton comes from cross-terms
# between warp-factor curvature and FRW curvature in G₅.
# Specifically: terms like R_{5D}² that mix A' with H give
# contributions to the 4D effective action of the form ε₁ X.
#
# The coefficient C_GB arises from the y-integral:
# C_GB = [∫₀^{y_c} dy e^{4A} × (GB cross-term)] / [∫₀^{y_c} dy e^{2A} × (standard)]

# KK integrals:
y_c = sp.Symbol('y_c', positive=True)

# I_n = ∫₀^{y_c} e^{nA} dy = ∫₀^{y_c} e^{-nky} dy = (1-e^{-nky_c})/(nk)
# In hierarchy limit (ky_c >> 1): I_n ≈ 1/(nk)
I2 = 1/(2*k)
I4 = 1/(4*k)
I_ratio = I4/I2

print(f"\n  KK integrals (hierarchy limit):")
print(f"    I₂ = 1/(2k) = {I2}")
print(f"    I₄ = 1/(4k) = {I4}")
print(f"    I₄/I₂ = {I_ratio} = {sp.Rational(1,2)}")

# The monograph's factorization:
# C_GB = (I₄/I₂) × (2k²/(A')²) × f_P
#       = (1/2)  ×    2        × f_P
#       = f_P

# So C_GB = f_P, and we need to determine f_P.

# f_P is defined as the fraction of the GB junction correction that
# comes from the P tensor, relative to the total.
# From Part 2: at static RS, (3J-Jh) = -4k³ h
# This is ISOTROPIC. It contributes to fine-tuning, not to K_eff.
#
# From Part 5: P·K at leading order is O(H²), and it's ANISOTROPIC.
# The anisotropy IS the K_eff source.
#
# So f_P should come from the P·K anisotropy.

# From the junction condition, the GB contributes to the effective
# stress-energy through:
# δ(effective stuff) = 2α × [3J-Jh + 2P·K]
#
# At O(H²), the 3J-Jh part contributes through β₀, γ₀ (already known
# from standard RS). The P·K part is the NEW contribution.
#
# The total anisotropy ΔS = S₀₀ - Sᵢⱼ has two pieces:
# ΔS_J = linearized (3J-Jh) anisotropy
# ΔS_P = P·K anisotropy

# Let me separate these:
DS_J = expand((dGBJ00_db*beta_0_H + dGBJ00_dg*gamma_0_H)
              - (dGBJ_ii_db*beta_0_H + dGBJ_ii_dg*gamma_0_H))
DS_J_FRW = expand(DS_J.subs(Hdot, -Rational(3, 2)*(1+w)*H**2))

DS_P = expand(2*PK_00_lead - 2*PK_ii_lead)
DS_P_FRW = expand(DS_P.subs(Hdot, -Rational(3, 2)*(1+w)*H**2))

print(f"\n  Anisotropy decomposition:")
print(f"    ΔS_J (from linearized J) = {DS_J_FRW}")
print(f"    ΔS_P (from P·K)          = {DS_P_FRW}")
print(f"    ΔS_total                  = {expand(DS_J_FRW + DS_P_FRW)}")
print(f"    Check: matches ΔS? {expand(DS_J_FRW + DS_P_FRW - Delta_S.subs(Hdot, -Rational(3,2)*(1+w)*H**2)) == 0}")

# f_P = ΔS_P / ΔS_total
DS_J_coeff = expand(DS_J_FRW / H**2)
DS_P_coeff = expand(DS_P_FRW / H**2)
DS_total_coeff = expand(DS_J_coeff + DS_P_coeff)

print(f"\n    ΔS_J/H² = {DS_J_coeff}")
print(f"    ΔS_P/H² = {DS_P_coeff}")
print(f"    ΔS_total/H² = {DS_total_coeff}")

# For de Sitter:
DS_J_dS = expand(DS_J_coeff.subs(w, -1))
DS_P_dS = expand(DS_P_coeff.subs(w, -1))
DS_tot_dS = expand(DS_total_coeff.subs(w, -1))
print(f"\n  de Sitter values:")
print(f"    ΔS_J/H² = {DS_J_dS}")
print(f"    ΔS_P/H² = {DS_P_dS}")
print(f"    ΔS_total/H² = {DS_tot_dS}")
if DS_tot_dS != 0:
    print(f"    f_P = ΔS_P/ΔS_total = {expand(DS_P_dS / DS_tot_dS)}")

# For matter:
DS_J_mat = expand(DS_J_coeff.subs(w, 0))
DS_P_mat = expand(DS_P_coeff.subs(w, 0))
DS_tot_mat = expand(DS_total_coeff.subs(w, 0))
print(f"\n  Matter values:")
print(f"    ΔS_J/H² = {DS_J_mat}")
print(f"    ΔS_P/H² = {DS_P_mat}")
print(f"    ΔS_total/H² = {DS_tot_mat}")
if DS_tot_mat != 0:
    print(f"    f_P = ΔS_P/ΔS_total = {expand(DS_P_mat / DS_tot_mat)}")

# ============================================================
# PART 12: C_GB NUMERICAL VALUE
# ============================================================
print(f"\n{'='*70}")
print(f"PART 12: C_GB numerical result")
print(f"{'='*70}")

# C_GB = (I₄/I₂) × 2 × f_P(w)
# where f_P(w) may depend on equation of state.
#
# If f_P is NOT 2/3, this is a correction to the monograph.
# If f_P IS 2/3, the monograph is confirmed.
#
# For a dark-energy-dominated universe (w ≈ -1):

# Actually, let me reconsider. The monograph claims C_GB = 2/3 is EXACT,
# independent of w. Let me check whether the total anisotropy / H² is
# proportional to k with a universal coefficient.

# The full C_GB should be:
# ε₁ = α̂ × C_GB
# where α̂ = α × k² (dimensionless)
# and ε₁ is determined by the anisotropy.
#
# The anisotropy gives δ(ρ+p) = 4α × ΔS
# The cuscuton K_eff = ε₁ X = ε₁ Φ̇²/2
# Matching: ε₁ Φ̇²/2 = 4α × ΔS
#
# But Φ̇ depends on the specific cuscuton dynamics.
# The approach: ε₁ modifies the Friedmann equation as
# H² → H²(1 + C_iso × α k²) and
# Ḣ → Ḣ(1 + C_aniso × α k²)
# The DIFFERENCE C_aniso - C_iso = C_GB

# From the junction equations:
# Friedmann: δH²/H² = (coefficient from 00 equation) × α
# Raychaudhuri: δḢ/Ḣ = (coefficient from ij equation) × α
#
# If they were the same, K_eff = 0 would be preserved.
# The difference is C_GB.

# From our computation:
# 00 equation: 3(γ₀+δγ) = (κ₅²/2)ρ - 2α·S₀₀_total
# → γ = γ₀ - (2α/3)S₀₀
# → H² = 2kγ = H₀²(1 - (4αk/3)(S₀₀/H²))

# ij equation: (β₀+δβ) + 2(γ₀+δγ) = -(κ₅²/2)p - 2α·Sᵢⱼ_total
# This determines the Raychaudhuri equation (Ḣ relation).

# The standard Raychaudhuri: Ḣ = -(1+w)κ₅²kρ/4 = -(3/2)(1+w)H²
# With GB: Ḣ = -(3/2)(1+w)H²(1 + correction)

# The correction difference between Friedmann and Raychaudhuri is C_GB × α̂.

# Let me compute this difference explicitly for de Sitter and matter.

# For de Sitter (w=-1, Ḣ=0, p=-ρ):
# The Friedmann modification is:
# δH²/H² = -(4α/3)(S₀₀/H²)_dS
print(f"\n  Friedmann modification (de Sitter): δH²/H² = -(4α/3) × ({S00_dS})")
print(f"    = {expand(-Rational(4,3)*alpha*S00_dS)}")

# For de Sitter, Ḣ=0 so the Raychaudhuri gives:
# 0 = -(3/2)(1+w)H² at w=-1, which is trivially satisfied.
# The anisotropy doesn't contribute to a Ḣ correction for de Sitter.
# Instead, it contributes to the effective w₀:
# w_eff = -1 + δw where δw comes from the pressure anisotropy.

# The effective equation of state:
# w_eff = p_eff/ρ_eff = (p + δp_GB)/(ρ + δρ_GB)
# At O(α): δw = (δp/ρ - w·δρ/ρ) = (1/ρ)(δp - w·δρ)

# From the junction conditions:
# δρ = (4α/κ₅²)·S₀₀  [00 modification]
# δ(ρ+p) = (4α/κ₅²)·(S₀₀ + Sᵢⱼ)  [combined]
# Wait, I need to be more careful.

# The junction gives:
# 3γ + 2α·(J+P part)₀₀ = (κ₅²/2)ρ
# Rearranging: (κ₅²/2)ρ_eff = 3γ + 2α·(...)₀₀
# At standard: (κ₅²/2)ρ = 3γ₀
# So: ρ_eff = ρ + (4α/κ₅²)·S₀₀ = ρ(1 + (4α/κ₅²ρ)·S₀₀)

# And: -(κ₅²/2)p_eff = β + 2γ + 2α·(...)ᵢⱼ
# At standard: -(κ₅²/2)p = β₀ + 2γ₀
# So: p_eff = p - (4α/κ₅²)·Sᵢⱼ

# The effective K_eff ∝ ρ_eff + p_eff:
# ρ + p + (4α/κ₅²)(S₀₀ - Sᵢⱼ) = (ρ+p)(1 + (4α/κ₅²(ρ+p))·ΔS)

# For the cuscuton: ρ+p = K_eff = ε₁X (which is what we're computing).
# This is circular UNLESS we recognize that the GB correction CREATES
# the ρ+p where previously there was none (cuscuton has ρ+p = 0 at α=0).

# So: ε₁X = (4α/κ₅²)·ΔS = (4α/κ₅²)·(S₀₀-Sᵢⱼ)

# Now, X = Φ̇²/2 and Φ̇ is determined by the cuscuton constraint.
# For the cuscuton P = μ²√(2X): the constraint gives Φ̇ through the
# modified Friedmann equation. Schematically:
# Φ̇² ∝ H² × (geometric factors)

# But we don't need Φ̇ to get C_GB! We need the RATIO:
# C_GB = ε₁/α̂ where α̂ = α·k²
# and ε₁ = (4α/κ₅²)·ΔS / X

# Hmm, but we still need X. Unless we define things differently.

# ALTERNATIVE APPROACH: C_GB from the modification of the Friedmann equation
# and Raychaudhuri equation DIRECTLY.

# The standard RS gives:
# Friedmann: H² = ρ/(3M₄²)
# Raychaudhuri: Ḣ = -(ρ+p)/(2M₄²)
# Continuity: ρ̇ = -3H(ρ+p)
# These three are consistent: Ḣ = -(3/2)(1+w)H²

# With GB:
# Friedmann: H² = ρ/(3M₄²) × (1 + c_F · αk²)
# Raychaudhuri: Ḣ = -(ρ+p)/(2M₄²) × (1 + c_R · αk²)
# If c_F ≠ c_R, the continuity equation is violated UNLESS there's
# an additional component (the cuscuton with K_eff ≠ 0).

# The cuscuton fills the gap: its K_eff = ε₁X provides the
# additional ρ+p to restore consistency.

# The mismatch:
# Ḣ_GB = -(3/2)(1+w)H²_GB × (1 + c_R · αk²)/(1 + c_F · αk²)
# ≈ -(3/2)(1+w)H² × (1 + (c_R - c_F)αk²)
# The "missing" Ḣ is: δḢ = -(3/2)(1+w)H² × (c_R - c_F)αk²
# This comes from ε₁X via: Ḣ_cusc = -(ε₁X)/(2M₄²)
# → ε₁X = 3(1+w)H²M₄² × (c_R - c_F)αk²

# And X ∝ H² (from the cuscuton constraint on the FRW background),
# specifically X = Φ̇²/2 = (μ²/(2ζ₀k))² / 2 or similar.

# Actually, this approach also requires knowing X. Let me try the most
# direct route: compare the GB-modified Friedmann equation with the
# literature and extract C_GB from the known result.

# Davis (2002) and Charmousis-Dufaux (2002) give the GB-modified Friedmann:
# H² + k²[1 + (4/3)αk²] = κ₅⁴ρ²/36 + ... (high-energy regime)
# In the low-energy RS regime:
# H² = ρ/(3M₄²) × 1/(1 + (4/3)αk²)
# ≈ ρ/(3M₄²) × (1 - (4/3)αk²)

# So c_F = -4/3.

# The Raychaudhuri equation gets a DIFFERENT correction.
# Let me compute c_R from our equations.

# From the ij junction condition:
# β + 2γ = -(κ₅²/2)p at standard
# Ḣ + 3H² = -(β+2γ)×k at standard [relating to actual Friedmann]
# Hmm, I need to be more careful.

# Actually: β = -(2+3w)H²/(2k) and γ = H²/(2k) at standard.
# β + 2γ = [-(2+3w) + 2]H²/(2k) = -(3w)H²/(2k) = (κ₅²/2)×(-p) → -(κ₅²/2)×wρ
# Check: -(κ₅²/2)wρ = -(κ₅²/2)w × 3H²/(κ₅²k) = -3wH²/(2k) ✓

# With GB:
# β_GB + 2γ_GB = -(3w)H²/(2k) - 2α·Sᵢⱼ
# γ_GB = H²/(2k) - (2α/3)·S₀₀
# β_GB = -(3w)H²/(2k) - 2α·Sᵢⱼ - H²/k + (4α/3)·S₀₀
#       = -(2+3w)H²/(2k) + α(4S₀₀/3 - 2Sᵢⱼ)

# The Raychaudhuri equation comes from Ḣ = -(β_GB + γ_GB)×k
# (in the low-energy RS regime, Ḣ ≈ -(β+γ)k)
# Hmm, actually this isn't quite right. Let me use the actual relation.

# In the RS model: Ḣ = -kβ - kγ - 2H² (schematic)
# Actually: from the bulk equations, H² = kγ (approximately)
# and Ḣ = -k(β+γ) (approximately)

# Let me just check: Ḣ = -(3/2)(1+w)H² at standard.
# β+γ = [-(2+3w) + 1]H²/(2k) = -(1+3w)H²/(2k)
# k(β+γ) = -(1+3w)H²/2
# -(β+γ)k = (1+3w)H²/2
# But Ḣ = -(3/2)(1+w)H² = -(3+3w)H²/2
# So -(β+γ)k ≠ Ḣ in general. The relation is more subtle.

# Let me try: from H² = 2kγ (linear RS regime):
# 2HḢ = 2k γ̇
# γ̇ relates to β through the 5D Bianchi identity / conservation.
# This is getting complicated. Let me just compute numerically.

print(f"\n  Moving to numerical verification...")

# ============================================================
# NUMERICAL COMPUTATION
# ============================================================
import numpy as np

# Set k=1, κ₅²=1 (M₅³=1), α=0.01 (small)
k_val = 1.0
kappa_val = 1.0  # κ₅²
H_val = 0.01     # H << k (low energy)
alpha_val = 0.01  # small GB coupling

def compute_junction(w_val, alpha_val, H_val, k_val=1.0, kappa_val=1.0):
    """
    Compute the GB-modified junction conditions numerically.
    Returns β, γ (extrinsic curvature perturbations).
    """
    # Ḣ from standard Friedmann:
    Hdot_val = -1.5 * (1 + w_val) * H_val**2

    # Standard (α=0) solution:
    rho_val = 3 * H_val**2 / (kappa_val * k_val)
    p_val = w_val * rho_val
    gamma_0 = kappa_val * rho_val / 6  # = H²/(2k)
    beta_0 = -kappa_val * p_val / 2 - kappa_val * rho_val / 3

    # Numerical evaluation of sympy expressions
    subs_dict = {k: k_val, H: H_val, Hdot: Hdot_val,
                 alpha: alpha_val, kappa5sq: kappa_val, w: w_val}

    # Linearization coefficients (from sympy)
    A11_val = float(dGBJ00_db.subs(subs_dict))
    A12_val = float(dGBJ00_dg.subs(subs_dict))
    A21_val = float(dGBJ_ii_db.subs(subs_dict))
    A22_val = float(dGBJ_ii_dg.subs(subs_dict))

    PK00_val = float(PK_00_lead.subs(subs_dict))
    PKii_val = float(PK_ii_lead.subs(subs_dict))

    # Full O(H²) junction equations with GB:
    # (I)  (3 + 2α·A12)γ + (2α·A11)β = (κ₅²/2)ρ - 4α·PK00
    # (II) (2 + 2α·A22)γ + (1 + 2α·A21)β = -(κ₅²/2)p - 4α·PKii

    M_mat = np.array([
        [2*alpha_val*A11_val, 3 + 2*alpha_val*A12_val],
        [1 + 2*alpha_val*A21_val, 2 + 2*alpha_val*A22_val]
    ])

    rhs = np.array([
        kappa_val/2 * rho_val - 4*alpha_val*PK00_val,
        -kappa_val/2 * p_val - 4*alpha_val*PKii_val
    ])

    sol = np.linalg.solve(M_mat, rhs)
    beta_GB = sol[0]
    gamma_GB = sol[1]

    return {
        'beta_0': beta_0, 'gamma_0': gamma_0,
        'beta_GB': beta_GB, 'gamma_GB': gamma_GB,
        'delta_beta': beta_GB - beta_0, 'delta_gamma': gamma_GB - gamma_0,
        'rho': rho_val, 'p': p_val, 'Hdot': Hdot_val,
        'PK00': PK00_val, 'PKii': PKii_val,
        'A11': A11_val, 'A12': A12_val, 'A21': A21_val, 'A22': A22_val,
        'H2_standard': 2*k_val*gamma_0,
        'H2_GB': 2*k_val*gamma_GB,
    }

print(f"\n  Parameters: k={k_val}, κ₅²={kappa_val}, H={H_val}, α={alpha_val}")
print(f"  H/k = {H_val/k_val} (low-energy regime)")

for w_test in [-1.0, -0.5, 0.0, 0.5, 1.0/3]:
    res = compute_junction(w_test, alpha_val, H_val)

    # Friedmann modification:
    dH2_frac = (res['H2_GB'] - res['H2_standard']) / res['H2_standard']

    # Anisotropy:
    aniso = res['delta_beta'] - res['delta_gamma']

    print(f"\n  w = {w_test:+.2f}:")
    print(f"    γ₀ = {res['gamma_0']:.6e}, γ_GB = {res['gamma_GB']:.6e}")
    print(f"    β₀ = {res['beta_0']:.6e}, β_GB = {res['beta_GB']:.6e}")
    print(f"    δH²/H² = {dH2_frac:.6e}")
    print(f"    δH²/H²/(αk²) = {dH2_frac/(alpha_val*k_val**2):.6f}")
    print(f"    δβ-δγ = {aniso:.6e}")
    print(f"    (δβ-δγ)/(αH²/k) = {aniso/(alpha_val*H_val**2/k_val):.6f}")

# ============================================================
# PART 13: FINAL C_GB EXTRACTION
# ============================================================
print(f"\n{'='*70}")
print(f"PART 13: C_GB from anisotropy")
print(f"{'='*70}")

# C_GB comes from the TOTAL modification to the effective equation of state.
# The cuscuton with P_eff = μ²√(2X) + ε₁X has:
# w_eff = -1 + ε₁X / (something involving μ² and the expansion)
#
# But more directly: C_GB can be extracted from the ratio of the
# GB modification to the Friedmann and Raychaudhuri equations.
#
# The key insight: the (4/3) factor in the GB fine-tuning comes from
# the Davis junction condition. C_GB is a DIFFERENT quantity — it's
# about the ANISOTROPY of the GB correction on the FRW brane.
#
# Let me compute C_GB by a different, more direct route:
#
# The GB correction modifies the effective 4D Newton's constant differently
# for the Friedmann and Raychaudhuri equations. The difference is:
# δG_F/G - δG_R/G = C_GB × αk²
#
# From our numerical results:
# Friedmann: δH²/H² = c_F × αk²
# The ij junction gives the Raychaudhuri modification.

# Let me extract c_F and the Raychaudhuri coefficient.

print(f"\n  Extracting C_GB from junction condition modifications:")
print(f"  {'w':>6s}  {'c_F':>10s}  {'c_R':>10s}  {'c_F-c_R':>10s}  {'→ C_GB':>10s}")
print(f"  {'-'*55}")

for w_test in [-1.0, -0.9, -0.5, 0.0, 0.5, 1.0/3]:
    res = compute_junction(w_test, alpha_val, H_val)

    # c_F from Friedmann modification
    c_F = (res['H2_GB'] - res['H2_standard']) / (res['H2_standard'] * alpha_val * k_val**2)

    # For c_R, we need how the ij equation modifies.
    # The ij equation gives: β + 2γ = -(κ₅²/2)p + GB_correction
    # Standard: β₀ + 2γ₀ = -(κ₅²/2)p₀
    # GB: β_GB + 2γ_GB = -(κ₅²/2)p₀ + δ(GB)
    # So: (δβ + 2δγ) = δ(GB from ij)
    # The "Raychaudhuri coefficient" c_R:
    # In standard RS: Ḣ comes from the combination kβ + kγ (schematic).
    # More precisely, from the conservation equation:
    # ρ̇ + 3H(ρ+p) = 0 → using ρ = 3M₄²H²: 6M₄²HḢ = -3H(ρ+p)
    # → Ḣ = -(ρ+p)/(2M₄²) = -(1+w)ρ/(2M₄²) = -(3/2)(1+w)H²
    # With GB: ρ_eff ≠ ρ, and the modification to ρ+p comes from anisotropy.

    # The effective ρ+p from GB:
    # δ(ρ+p) from the junction = (2/κ₅²)(δβ + 2δγ + 3δγ) - ...
    # Actually, let me use:
    # ρ_eff = 6γ_GB/κ₅² [from 00 equation]
    # p_eff = -(2β_GB + 4γ_GB)/κ₅² [from ij equation]
    # ρ_eff + p_eff = (6γ_GB - 2β_GB - 4γ_GB)/κ₅² = (2γ_GB - 2β_GB)/κ₅²

    rho_eff = 6*res['gamma_GB']/kappa_val
    p_eff = -(2*res['beta_GB'] + 4*res['gamma_GB'])/kappa_val
    rho_p_eff = rho_eff + p_eff

    rho_std = 6*res['gamma_0']/kappa_val
    p_std = -(2*res['beta_0'] + 4*res['gamma_0'])/kappa_val
    rho_p_std = rho_std + p_std

    # c_R: modification to ρ+p
    if abs(rho_p_std) > 1e-20:
        c_R = (rho_p_eff - rho_p_std) / (rho_p_std * alpha_val * k_val**2)
        delta_c = c_F - c_R
    elif abs(w_test + 1) < 0.01:
        # de Sitter: ρ+p = 0, need different approach
        c_R = float('nan')
        # For de Sitter, the anisotropy IS the entire ρ+p
        # ε₁X = ρ+p from GB = (2γ_GB - 2β_GB)/κ₅² - (2γ₀ - 2β₀)/κ₅²
        delta_rho_p = rho_p_eff - rho_p_std
        # Normalize: ε₁ = δ(ρ+p) / (X × something)
        # For now, report the raw anisotropy
        delta_c = delta_rho_p / (alpha_val * k_val**2 * res['rho'])
    else:
        c_R = float('nan')
        delta_c = float('nan')

    print(f"  {w_test:+6.2f}  {c_F:10.6f}  {c_R:10.6f}  {delta_c:10.6f}  {delta_c:10.6f}")

# ============================================================
# PART 14: ALTERNATIVE — DIRECT FROM GB FINE-TUNING STRUCTURE
# ============================================================
print(f"\n{'='*70}")
print(f"PART 14: C_GB from the fine-tuning structure")
print(f"{'='*70}")

# The monograph's approach: C_GB = (I₄/I₂)(2k²/A'²) × f_P
# Let me compute f_P directly from the junction condition.
#
# At static RS: the GB assembled term is -16αk³ h (with P·K from monograph)
# or -8αk³ h (with P=0 for flat brane from Davis).
#
# The difference: the P·K term contributes -6αk³ h at isotropic K.
# The 3J-Jh contributes -4αk³×2 = -8αk³ h.
# Wait: 3J-Jh = -4k³ h (from Part 2), so 2α(3J-Jh) = -8αk³ h.
# 2α(2P·K) = 4α(P·K).
# If P·K = -3k³h (monograph), then 4α(-3k³h) = -12αk³h.
# Total: -8αk³ - 12αk³ = -20αk³?? That's wrong.
# The monograph says -16αk³. Let me recheck.
#
# From eq 4-gb-assembled: 2α[6k³ - 8k³ - 6k³] = 2α(-8k³) = -16αk³.
# Where: 3J = 6k³, J·h = 8k³, 2P·K = -6k³.
# So: 3J - J·h = -2k³, plus 2P·K = -6k³.
# Total inside brackets: -2k³ + (-6k³) = -8k³.
# ×2α: -16αk³.
#
# But from our computation: 3J - J·h = -4k³ at isotropic, and P·K = 0 for flat brane.
# So our total: -4k³, ×2α: -8αk³.
#
# DISCREPANCY: -16αk³ (monograph) vs -8αk³ (our computation with Davis P).

# This is the P tensor definition issue. Let me check both cases.

# Case A: P from Davis (intrinsic R̂). For flat brane: P = 0, P·K = 0.
# Total GB = 2α(3J-Jh) = 2α(-4k³) = -8αk³
# Fine-tuning: σ = 2(3k - 8αk³)/κ₅² = 6M₅³k(1 - (8/3)αk²)

# Case B: P from K⊗K (monograph). P_{μρνσ} = K_{μν}K_{ρσ} - K_{μσ}K_{ρν}.
# For isotropic K=-k: P_{μρνσ}K^{ρσ} = k²(h_{μν}h_{ρσ} - h_{μσ}h_{ρν})(-kh^{ρσ})
# = k²(-4k·h_{μν} - (-k)h_{μν}·4 + k·h_{μν}) ... let me compute carefully.
#
# P_{μρνσ}K^{ρσ} = Σ_{ρσ} (K_{μν}K_{ρσ} - K_{μσ}K_{ρν}) K^{ρσ}
# = K_{μν} K_{ρσ}K^{ρσ} - K_{μσ}K_{ρν}K^{ρσ}
# = K_{μν} × 4k² - (-k h_{μσ})(-k h_{ρν})(-k h^{ρσ})
# = 4k² × (-k h_{μν}) - k² h_{μσ} h_{ρν} (-k h^{ρσ})
# = -4k³ h_{μν} - k² (-k) h_{μσ} δ^{σ}_{ν} ... hmm wrong
# = -4k³ h_{μν} + k³ h_{μν} × (trace?)

# Let me be careful. With K_{μν} = -k h_{μν}:
# P_{μρνσ} K^{ρσ} = Σ_{ρ,σ} [K_{μν}K_{ρσ} - K_{μσ}K_{ρν}] K^{ρσ}
# = K_{μν} Σ_{ρσ} K_{ρσ}K^{ρσ} - Σ_{ρσ} K_{μσ}K_{ρν}K^{ρσ}
# = K_{μν} × K_{αβ}K^{αβ} - K_{μσ}(K_{ρν}K^{ρσ})
# = K_{μν} × 4k² - K_{μσ} × k² δ^{σ}_{ν}
# = -k h_{μν} × 4k² - (-k h_{μσ}) × k² δ^{σ}_{ν}
# = -4k³ h_{μν} + k³ h_{μν}
# = -3k³ h_{μν} ✓ — matches monograph!

# So the monograph uses P_{μρνσ} = K_{μν}K_{ρσ} - K_{μσ}K_{ρν}
# NOT the Davis P from intrinsic curvature R̂.

print(f"\n  KEY FINDING:")
print(f"  The monograph's P tensor = K⊗K - K⊗K (extrinsic curvature)")
print(f"  Davis's P tensor = function of intrinsic R̂")
print(f"  These are DIFFERENT on a flat brane (K⊗K ≠ 0 but R̂ = 0)")
print(f"")
print(f"  For the Gauss-Codazzi equation: R̂_{μρνσ} = R_{μρνσ} + K_{μν}K_{ρσ} - K_{μσ}K_{ρν}")
print(f"  (where R is the ambient 5D Riemann restricted to brane)")
print(f"")
print(f"  So: P(K⊗K) = P(R̂) - P(R_ambient)")
print(f"  For AdS₅ bulk: R_ambient = -k²(g_{ac}g_{bd} - g_{ad}g_{bc})")
print(f"  On the brane: restricted ambient Riemann = -k²(h_{μν}h_{ρσ} - h_{μσ}h_{ρν})")

# The Gauss-Codazzi relation tells us:
# R̂_{μρνσ} = R̃_{μρνσ} + K_{μν}K_{ρσ} - K_{μσ}K_{ρν}
# where R̃ = ambient Riemann projected to brane
# For AdS₅: R̃_{μρνσ} = -k²(h_{μν}h_{ρσ} - h_{μσ}h_{ρν})

# So for flat brane (R̂ = 0):
# 0 = -k²(hh-hh) + k²(hh-hh) [K=-kh]
# = -k²(hh-hh) + k²(hh-hh) ✓

# The Davis P uses the FULL Gauss-Codazzi-related tensor.
# Let me check: what does Davis actually write?

print(f"\n  Checking Davis (2002) definition of P...")
print(f"  Davis eq (21): P_{{μανβ}} is the 'divergence-free part of")
print(f"  the Riemann tensor of the induced metric h'")
print(f"  This IS the intrinsic R̂, built from R̂_{{μρνσ}}.")
print(f"")
print(f"  For a FLAT brane (Minkowski): R̂ = 0 → P = 0 → P·K = 0")
print(f"  For RS brane (also flat at H=0): R̂ = 0 → P·K = 0")
print(f"")
print(f"  But the monograph uses P_{μρνσ} = K_{μν}K_{ρσ} - K_{μσ}K_{ρν}")
print(f"  which gives P·K = -3k³h ≠ 0 on flat brane.")

# RESOLUTION: There might be an alternative form of the junction conditions
# where P is defined differently. Let me check Gravanis-Willison (2003)
# and other references.

# Actually, I think the issue is that different authors use different
# conventions for the junction conditions. Some write:
# [K_μν - Kh + 2α(3J - Jh + 2P·K)] = -κ₅²S
# where P uses R̂ (intrinsic), while others write:
# [K_μν - Kh + 2α(something with K³ terms)] = -κ₅²S
# and the "P" they use already absorbs the K⊗K structure.

# The KEY QUESTION: which form gives the CORRECT physics?
# Let's check by computing the GB fine-tuning correction and comparing
# with the known result.

# Known result (many papers): the GB-modified RS fine-tuning is
# σ = 6M₅³k(1 + (4/3)αk²) or σ = 6M₅³k(1 - (4/3)αk²)
# depending on sign conventions.

# With Davis P (R̂), P·K = 0 on flat brane:
# Junction gives: 3k + 2α(-4k³) = (κ₅²/2)σ
# → σ = (6k - 16αk³)/κ₅² = 6M₅³k(1 - (8/3)αk²)
# Hmm, coefficient is 8/3, not 4/3.

# With monograph P (K⊗K), P·K = -3k³h:
# Junction gives: 3k + 2α(-4k³ - 6k³) = (κ₅²/2)σ
# Wait: 2α(3J-Jh + 2P·K) = 2α(-4k³ + 2(-3k³)) = 2α(-10k³) = -20αk³
# Hmm that gives 3k - 20αk³ = (κ₅²/2)σ. Coefficient would be 20/3.

# Let me recompute from the monograph:
# 2α[3J - Jh + 2P·K] = 2α[6k³ - 8k³ + 2(-3k³)] = 2α[-8k³] = -16αk³
# So 3k - 16αk³ = (κ₅²/2)σ → σ = 6M₅³k(1 - (16/3)αk²)

# But the LITERATURE says 4/3, not 8/3 or 16/3.
# The discrepancy factor: the Davis junction has [K], which for Z₂ is 2K.
# So the FULL junction condition is:
# 2K_μν - 2Kh + 2α[6J - 2Jh + 4P·K] = -κ₅²S  (after Z₂)
# 2(3k) + 2α(2)(-4k³) + ... hmm no. Let me be very careful.

# Davis eq (15): [K_μν - Kh + 2α(3J-Jh+2P·K)] = -κ₅²/2 S
# The [·] means JUMP. For Z₂: [X] = X⁺ - X⁻ = 2X⁺.
# So: 2(K_μν - Kh) + 4α(3J-Jh+2P·K) = -κ₅²/2 S
# Wait no. The [·] applies to the whole expression:
# [K_μν - Kh + 2α(3J-Jh+2P·K)] = [K_μν] - [K]h + 2α([3J]-[J]h+2[P·K])
# For Z₂: [K] = 2K⁺, [J] depends on K...
# Since J is cubic in K, and K⁻ = -K⁺: J⁻ = -J⁺ (cubic odd).
# So [J] = 2J⁺.
# P depends on R̂ (intrinsic, same on both sides) and K (which flips sign).
# P·K: K flips sign, P doesn't (if P uses R̂) → [P·K] = 2P·K⁺.

# So: 2(K-Kh) + 2α(6J-2Jh+4P·K) = -κ₅²/2 S evaluated at + side.

# OK I realize the factor of 2 from Z₂ applies uniformly since everything
# is ODD in K (K, J=K³, P·K = R̂·K all flip sign).

# With the factor: 2 × [standard + 2α(GB)] = -κ₅²/2 S
# Standard: 2(K^μ_ν - Kδ^μ_ν)|_iso = 2(-k - (-4k)) = 2(3k) = 6k
# This gives: 6k = (κ₅²/2)σ → σ = 12k/κ₅² = 12M₅³k

# But the RS fine-tuning is σ = 6M₅³k. There's a factor of 2 wrong.

# I think the issue is that some references include the Z₂ factor in the
# junction condition definition and others don't.
# Let me use the convention where the junction condition is:
# K_μν - Kh + 2α(3J-Jh+2P·K) = -κ₅²/2 S  (single-sided, no factor of 2)
# Then: 3k + 2α(GB) = (κ₅²/2)σ → 3k = (κ₅²/2)σ → σ = 6k/κ₅² = 6M₅³k ✓

# This is the SINGLE-SIDED convention. The Z₂ is already accounted for
# by using K⁺ only.

# With this convention and Davis P (R̂=0 for flat brane):
# 3k + 2α(-4k³) = (κ₅²/2)σ
# σ = (6k - 16αk³)/κ₅² = 6M₅³k - 16M₅³αk³ = 6M₅³k(1 - (8/3)αk²)

# Literature check: Charmousis-Dufaux (2002) eq (2.8):
# σ = 6M₅³k(1 + (4/3)αk²)
#
# The sign difference (+ vs -) depends on the sign convention for α.
# If α > 0 in C-D corresponds to α < 0 in our convention, or if the
# coefficient is different.
#
# The MAGNITUDE: 8/3 ≠ 4/3. Factor of 2 off.
# This suggests we're double-counting somewhere.

# Let me check: perhaps the Davis junction (eq 15) already includes the Z₂,
# and the single-sided version is:
# K_μν - Kh + 2α(3J-Jh+2P·K) = -(κ₅²/4) S  [single-sided, halved RHS]

# Then: 3k - 8αk³ = (κ₅²/4)σ → σ = 4(3k - 8αk³)/κ₅² = 12M₅³k(1 - (8/3)αk²)

# That's even worse. Let me try the other way:
# If [·] = 2×(single side), then the junction IS:
# 2(3k) + 4α(-4k³) = -(κ₅²/2)S⁰₀ = (κ₅²/2)σ  [for tension]
# 6k - 16αk³ = (κ₅²/2)σ
# σ = (12k - 32αk³)/κ₅² = 12M₅³k(1 - (8/3)αk²)

# Standard RS has σ = 6M₅³k. So maybe κ₅² = 1/(2M₅³)?
# With κ₅² = 1/(2M₅³): σ = (12k - 32αk³) × 2M₅³ = 24M₅³k(1-(8/3)αk²)
# Still wrong.

# I think the convention confusion is the main obstacle. Let me just
# use NUMERICAL consistency: pick conventions, compute, and check against
# the known Friedmann equation modification.

# KNOWN: GB-modified Friedmann on RS brane (e.g., Maeda-Torii 2003):
# H² = (κ₅⁴/36)ρ² + (1/3)(Λ₄ + (1/2)κ₅²λρ) + ...
# where λ is the effective tension and Λ₄ includes GB corrections.
# In the low-energy limit: H² ≈ ρ/(3M₄²) with M₄² modified by GB.

# The simplest check: numerically solve the full junction condition
# and compare H² with and without α for the same ρ.

print(f"\n  ═══════════════════════════════════════════")
print(f"  NUMERICAL CROSS-CHECK: GB Friedmann modification")
print(f"  ═══════════════════════════════════════════")

# Work in units k=1, κ₅²=1.
# Full junction condition (single-sided, mixed indices):
#   K^μ_ν - K δ^μ_ν + 2α(3J^μ_ν - J δ^μ_ν + 2(P·K)^μ_ν) = -(κ₅²/2) S^μ_ν
#
# For FRW: K^0_0 = a = -(k+β), K^i_j = b = -(k+γ)
# S^0_0 = -(σ+ρ), S^i_j = (-σ+p)
# where σ is the brane tension.

# Fine-tuning at H=0: σ chosen so β=γ=0.
# → 3k + 2α(3J₀ - J₀·h + 2P₀·K₀) = (κ₅²/2)σ  [P₀·K₀ depends on convention]

# Let me do this fully numerically without P, and then WITH P.

# NUMERICAL: solve the FULL nonlinear junction for β, γ given ρ, p, σ, α.

def solve_junction_full(w_val, alpha_val, H_val_target, k_val=1.0, kappa_val=1.0,
                        use_davis_P=True):
    """
    Solve the full GB junction condition to find β, γ.

    First find σ from fine-tuning (H=0, ρ=0).
    Then solve for β, γ given matter content.

    use_davis_P: True = Davis definition (intrinsic R̂), False = K⊗K.
    """
    from scipy.optimize import fsolve

    # Step 1: Find σ from fine-tuning condition (β=γ=0)
    a0 = -k_val
    b0 = -k_val

    # J at isotropic:
    K_tr0 = a0 + 3*b0
    K_sq0 = a0**2 + 3*b0**2
    J0_00 = (1/3)*(2*K_tr0*a0**2 + K_sq0*a0 - 2*a0**3 - K_tr0**2*a0)
    J0_ii = (1/3)*(2*K_tr0*b0**2 + K_sq0*b0 - 2*b0**3 - K_tr0**2*b0)
    J0_tr = J0_00 + 3*J0_ii

    GB_J0_00 = 3*J0_00 - J0_tr  # (3J-Jh)^0_0

    # P·K at isotropic, flat brane:
    if use_davis_P:
        PK0_00 = 0.0  # R̂ = 0 for flat brane
    else:
        # K⊗K: P·K = -3k³h, so (P·K)^0_0 = -3k³ × (-1) = 3k³
        # Wait: h_{μν} = η_{μν}, so (P·K)_{00} = -3k³ × η_{00} = -3k³(-1) = 3k³
        # (P·K)^0_0 = η^{00}(P·K)_{00} = -3k³
        PK0_00 = -3*k_val**3

    # Junction 00: a - K + 2α(GB_J + 2PK) = -(κ/2)(-(σ+ρ))
    # a0 - K0 = 3k, σ contribution:
    # 3k + 2α(GB_J0_00 + 2*PK0_00) = (κ/2)σ
    sigma = 2*(3*k_val + 2*alpha_val*(GB_J0_00 + 2*PK0_00)) / kappa_val

    # Step 2: For given H, find ρ from the standard Friedmann
    # ρ = 3M₄²H² = 3H²/(κk) in our conventions
    rho_val = 3*H_val_target**2 / (kappa_val * k_val)
    p_val = w_val * rho_val
    Hdot_val = -1.5*(1+w_val)*H_val_target**2

    def junction_eqs(params):
        beta_v, gamma_v = params
        a_v = -(k_val + beta_v)
        b_v = -(k_val + gamma_v)

        # K trace and K²
        K_tr_v = a_v + 3*b_v
        K_sq_v = a_v**2 + 3*b_v**2

        # J components (mixed)
        J_00_v = (1/3)*(2*K_tr_v*a_v**2 + K_sq_v*a_v - 2*a_v**3 - K_tr_v**2*a_v)
        J_ii_v = (1/3)*(2*K_tr_v*b_v**2 + K_sq_v*b_v - 2*b_v**3 - K_tr_v**2*b_v)
        J_tr_v = J_00_v + 3*J_ii_v

        GB_J_00_v = 3*J_00_v - J_tr_v
        GB_J_ii_v = 3*J_ii_v - J_tr_v

        # P·K (depends on definition)
        if use_davis_P:
            # Use the sympy expressions evaluated numerically
            # P depends on intrinsic R̂ which depends on H, Ḣ
            # PK_00_lead and PK_ii_lead are at a=b=-k
            # For the full nonlinear, we should use actual a, b
            # But P is O(H²) and the K-dependence of P·K at O(H²) uses K₀=-k
            # So to O(H²), P·K_full ≈ P·K|_{K₀=-k}
            PK_00_v = float(PK_00_mix.subs([(a_sym, a_v), (b_sym, b_v),
                                             (H, H_val_target), (Hdot, Hdot_val),
                                             (k, k_val)]))
            PK_ii_v = float(PK_ii_mix.subs([(a_sym, a_v), (b_sym, b_v),
                                             (H, H_val_target), (Hdot, Hdot_val),
                                             (k, k_val)]))
        else:
            # K⊗K: P_{μρνσ}K^{ρσ} = K_{μν}K_{ρσ}K^{ρσ} - K_{μσ}K^{ρσ}K_{ρν}
            # In mixed indices for diagonal K:
            # (P·K)^μ_ν = K^μ_ν × K_αβK^αβ - (K²)^μ_ρ K^ρ_ν... hmm
            # All-lower: P_{μρνσ}K^{ρσ} = K_{μν}K_{αβ}K^{αβ} - K_{μσ}(K²)^σ_ν
            # K_{μν} = η_{μα}K^α_ν, K_{00} = -a_v, K_{ii} = b_v
            # K^{ρσ} = diag(-a_v, b_v, b_v, b_v)
            # K_{αβ}K^{αβ} = K_sq_v
            # (P·K)_{00} = K_{00} × K_sq_v - K_{0σ}(K²)^σ_0
            #            = (-a_v) × K_sq_v - (-a_v)(a_v²)
            #            = -a_v × K_sq_v + a_v³
            PK_00_lower = -a_v * K_sq_v + a_v**3
            PK_ii_lower = b_v * K_sq_v - b_v**3
            # Mixed: multiply by η^{μμ}
            PK_00_v = -PK_00_lower  # η^{00} = -1
            PK_ii_v = PK_ii_lower   # η^{ii} = 1

        # Full junction equations (mixed indices):
        # K^μ_ν - K δ^μ_ν + 2α(GB_J^μ_ν + 2(P·K)^μ_ν) = -(κ/2)S^μ_ν
        # S^0_0 = -(σ+ρ), S^i_j = (-σ+p)

        lhs_00 = a_v - K_tr_v + 2*alpha_val*(GB_J_00_v + 2*PK_00_v)
        rhs_00 = -kappa_val/2 * (-(sigma + rho_val))

        lhs_ii = b_v - K_tr_v + 2*alpha_val*(GB_J_ii_v + 2*PK_ii_v)
        rhs_ii = -kappa_val/2 * (-sigma + p_val)

        return [lhs_00 - rhs_00, lhs_ii - rhs_ii]

    # Solve with initial guess from standard RS
    gamma_guess = H_val_target**2 / (2*k_val)
    beta_guess = -(2+3*w_val)*H_val_target**2 / (2*k_val)

    sol = fsolve(junction_eqs, [beta_guess, gamma_guess], full_output=True)
    beta_sol, gamma_sol = sol[0]
    info = sol[1]

    H2_eff = 2*k_val*gamma_sol

    return {
        'sigma': sigma,
        'beta': beta_sol, 'gamma': gamma_sol,
        'H2_eff': H2_eff,
        'H2_target': H_val_target**2,
        'delta_H2_frac': (H2_eff - H_val_target**2) / H_val_target**2,
        'rho': rho_val, 'p': p_val,
    }

print(f"\n  Comparing Davis P (intrinsic R̂) vs K⊗K P:")
print(f"  H = {H_val}, k = {k_val}, α = {alpha_val}")
print(f"  {'w':>6s}  {'Davis δH²/H²':>14s}  {'K⊗K δH²/H²':>14s}  {'Davis/(αk²)':>12s}  {'K⊗K/(αk²)':>12s}")
print(f"  {'-'*65}")

for w_test in [-1.0, -0.5, 0.0, 1.0/3]:
    try:
        res_davis = solve_junction_full(w_test, alpha_val, H_val, use_davis_P=True)
        res_KK = solve_junction_full(w_test, alpha_val, H_val, use_davis_P=False)

        c_davis = res_davis['delta_H2_frac'] / (alpha_val * k_val**2)
        c_KK = res_KK['delta_H2_frac'] / (alpha_val * k_val**2)

        print(f"  {w_test:+6.2f}  {res_davis['delta_H2_frac']:14.6e}  {res_KK['delta_H2_frac']:14.6e}  {c_davis:12.6f}  {c_KK:12.6f}")
    except Exception as e:
        print(f"  {w_test:+6.2f}  ERROR: {e}")

# Literature value: δH²/H² = -(4/3)αk² for de Sitter.
print(f"\n  Literature: δH²/H²/(αk²) = -4/3 ≈ -1.333333 (de Sitter, Charmousis-Dufaux)")
print(f"  Which convention matches?")

# ============================================================
# PART 15: FINAL RESULT
# ============================================================
print(f"\n{'='*70}")
print(f"PART 15: FINAL C_GB DETERMINATION")
print(f"{'='*70}")

# Now extract C_GB from the anisotropy between Friedmann and Raychaudhuri.
# Use whichever P definition matches the literature.

print(f"\n  C_GB extraction from w-dependent modification:")
print(f"  (Using the P convention that matches literature)")

# For each w, compute:
# c_F(w) = δH²/H² / (αk²) — Friedmann modification
# c_R(w) = δ(ρ+p)/(ρ+p) / (αk²) — Raychaudhuri modification
# C_GB-related = c_F(w) - c_R(w)

# Or alternatively: compute the modification for w=-1 and w=-1+δ,
# and extract the w-derivative which encodes the anisotropy.

alpha_test = 0.001  # Use smaller α for better linearity

for use_davis in [True, False]:
    label = "Davis" if use_davis else "K⊗K"
    print(f"\n  --- {label} P convention ---")

    # Compute for a range of w values
    results = {}
    for w_test in [-1.0, -0.99, -0.9, -0.5, 0.0, 1.0/3]:
        try:
            res = solve_junction_full(w_test, alpha_test, 0.01, use_davis_P=use_davis)
            results[w_test] = res
            c_val = res['delta_H2_frac'] / (alpha_test * k_val**2) if alpha_test > 0 else 0

            # Also compute ρ+p modification
            rho_eff = 6*res['gamma']/kappa_val
            p_eff = -(2*res['beta'] + 4*res['gamma'])/kappa_val
            rho_p_eff = rho_eff + p_eff
            rho_p_std = res['rho'] + res['p']

            if abs(rho_p_std) > 1e-20:
                c_rp = (rho_p_eff - rho_p_std) / (rho_p_std * alpha_test)
            else:
                c_rp = float('nan')

            print(f"    w={w_test:+6.3f}: δH²/H²/(αk²) = {c_val:10.6f}, δ(ρ+p)/(ρ+p)/α = {c_rp:10.6f}")
        except Exception as e:
            print(f"    w={w_test:+6.3f}: ERROR: {e}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print(f"SUMMARY")
print(f"{'='*70}")
print(f"""
This computation determines C_GB from first principles by:
1. Computing the third fundamental form J_μν symbolically for anisotropic K
2. Computing the Davis P tensor from intrinsic FRW curvature R̂
3. Assembling the full GB junction condition at O(H²/k²)
4. Solving for the extrinsic curvature perturbations β, γ
5. Extracting the Friedmann modification and anisotropy

KEY FINDINGS:
- The monograph's P·K = -3k³h (line 570) uses P = K⊗K, NOT Davis's P(R̂)
- For Davis P: P·K = 0 on flat brane (R̂ = 0)
- For K⊗K P: P·K = -3k³h on flat brane (matches monograph)
- The correct P convention is determined by matching to known literature:
  δH²/H² = -(4/3)αk² for de Sitter [Charmousis-Dufaux 2002]
- C_GB depends on which convention matches.

The numerical results above determine which P gives the correct physics
and what C_GB actually equals.
""")
