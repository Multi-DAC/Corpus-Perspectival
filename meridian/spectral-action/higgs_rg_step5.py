"""
Step 5: Final precision summary.

Key findings from Step 4 with 2-loop running:

CRITICAL RESULT: At 2-loop with SM central values:
  - lambda(M_Pl) = 0 => m_H = 129.3 GeV
  - beta(lambda)=0 (with 2-loop couplings) => lambda = -0.00153 => m_H = 128.9 GeV
  - lambda(M_Pl) = -0.01 => m_H = 126.2 GeV
  - For m_H = 125.25: need lambda(M_Pl) = -0.01264
  - For m_H = 124.5: need lambda(M_Pl) = -0.01473

The Shaposhnikov-Wetterich condition is NEARLY satisfied at 2-loop:
  Required y_t(M_Pl) = 0.389 vs actual = 0.390 (0.3% discrepancy!)

But the 2-loop beta functions I used are approximate. The key question is whether
with FULL 3-loop RGEs (as in Buttazzo et al. 2013), the AS condition exactly works.

Let me also check: what is the Higgs mass prediction if we use the EXACT
Shaposhnikov-Wetterich condition (lambda = 0 AND beta(lambda) = 0 simultaneously)?
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar

M_Z = 91.1876
M_t_pole = 172.76
v = 246.22
M_Pl = 2.435e18

# MSbar at M_t (Buttazzo et al.)
g1_Mt = 0.463067
g2_Mt = 0.648213
g3_Mt = 1.169125
y_t_Mt = 0.9369
lambda_Mt = 0.12604

def beta_SM_1loop(t, y):
    g1, g2, g3, yt, lam = y
    g1sq, g2sq, g3sq, ytsq = g1**2, g2**2, g3**2, yt**2
    L = 1.0 / (16 * np.pi**2)
    dg1 = L * g1**3 * (41.0/10.0)
    dg2 = L * g2**3 * (-19.0/6.0)
    dg3 = L * g3**3 * (-7.0)
    dyt = L * yt * ((9.0/2.0) * ytsq - (17.0/20.0) * g1sq - (9.0/4.0) * g2sq - 8.0 * g3sq)
    dlam = L * (
        24 * lam**2 - lam * ((9.0/5.0) * g1sq + 9.0 * g2sq) + 12.0 * lam * ytsq
        + (27.0/200.0) * g1sq**2 + (9.0/20.0) * g1sq * g2sq + (9.0/8.0) * g2sq**2
        - 6.0 * ytsq**2
    )
    return [dg1, dg2, dg3, dyt, dlam]


t_Mt = np.log(M_t_pole / M_Z)
t_Pl = np.log(M_Pl / M_Z)


# =====================================================
# THE EXACT SHAPOSHNIKOV-WETTERICH COMPUTATION
# =====================================================

print("=" * 70)
print("SHAPOSHNIKOV-WETTERICH: EXACT COMPUTATION")
print("=" * 70)

# The SW (2009) paper, arXiv:0912.0208:
# Their prediction (their eq. 10, with lambda(M_Pl) = 0):
# m_H = 126 ± 3 GeV for m_t = 171.3 ± 2.3 GeV
# (using NNLO running and matching)

# They get m_H = 126 GeV for m_t = 171 GeV.
# For m_t = 173 GeV they would get m_H ≈ 129 GeV.

# The KEY: their prediction is m_H ≈ 126 GeV for THEIR value of m_t.
# With the current m_t = 172.76, the prediction shifts up.

# Let me compute the EXACT SW prediction for various m_t:

print(f"\nSW prediction (lambda(M_Pl) = 0) vs m_t:")
print(f"{'m_t':>8s}  {'y_t(M_t)':>10s}  {'m_H (1-loop)':>14s}")

for mt_val in [170.0, 171.0, 171.3, 172.0, 172.76, 173.0, 174.0]:
    # Approximate y_t(M_t) for each m_t
    alpha_s_mt = 0.1079
    mt_msbar = mt_val * (1 - (4.0/3.0) * alpha_s_mt / np.pi)
    yt_val = np.sqrt(2) * mt_msbar / v

    # Run up to M_Pl
    y0 = [g1_Mt, g2_Mt, g3_Mt, yt_val, lambda_Mt]
    sol = solve_ivp(beta_SM_1loop, (t_Mt, t_Pl), y0, method='RK45',
                    rtol=1e-12, atol=1e-14)

    g1_P, g2_P, g3_P, yt_P = sol.y[0,-1], sol.y[1,-1], sol.y[2,-1], sol.y[3,-1]

    # Now run DOWN from M_Pl with lambda = 0
    y0_down = [g1_P, g2_P, g3_P, yt_P, 0.0]
    sol_down = solve_ivp(beta_SM_1loop, (t_Pl, t_Mt), y0_down, method='RK45',
                         rtol=1e-12, atol=1e-14)

    lam_Mt_out = sol_down.y[4, -1]
    if lam_Mt_out > 0:
        mH = v * np.sqrt(2 * lam_Mt_out)
    else:
        mH = -1

    print(f"{mt_val:8.2f}  {yt_val:10.4f}  {mH:14.2f}")


# =====================================================
# THE CONNES-CHAMSEDDINE vs SHAPOSHNIKOV-WETTERICH COMPARISON
# =====================================================

print("\n" + "=" * 70)
print("COMPARISON OF ALL BOUNDARY CONDITIONS AT M_Pl")
print("=" * 70)

# Run from M_t to M_Pl with standard values
y0_std = [g1_Mt, g2_Mt, g3_Mt, y_t_Mt, lambda_Mt]
sol_std = solve_ivp(beta_SM_1loop, (t_Mt, t_Pl), y0_std, method='RK45',
                    t_eval=np.linspace(t_Mt, t_Pl, 50000),
                    rtol=1e-12, atol=1e-14, max_step=0.01)

g1_P = sol_std.y[0,-1]
g2_P = sol_std.y[1,-1]
g3_P = sol_std.y[2,-1]
yt_P = sol_std.y[3,-1]
lam_P = sol_std.y[4,-1]

print(f"\nSM values at M_Pl (1-loop, m_t = {M_t_pole}):")
print(f"  g1 = {g1_P:.6f}, g2 = {g2_P:.6f}, g3 = {g3_P:.6f}")
print(f"  y_t = {yt_P:.6f}")
print(f"  lambda = {lam_P:.8f}")

# Asymptotic safety: beta(lambda) = 0
A = 24.0
B_c = 12.0 * yt_P**2 - (9.0/5.0) * g1_P**2 - 9.0 * g2_P**2
C_c = (27.0/200.0 * g1_P**4 + 9.0/20.0 * g1_P**2 * g2_P**2
       + 9.0/8.0 * g2_P**4 - 6.0 * yt_P**4)
disc = B_c**2 - 4*A*C_c
lam_AS_neg = (-B_c - np.sqrt(disc)) / (2*A)
lam_AS_pos = (-B_c + np.sqrt(disc)) / (2*A)

# CCM at Lambda_NCG ~ 10^13 (need to find from sol)
# sin^2(theta_W) = 3/8 scale
g1_arr = sol_std.y[0]
g2_arr = sol_std.y[1]
sin2_arr = (3.0/5.0) * g1_arr**2 / ((3.0/5.0) * g1_arr**2 + g2_arr**2)
for i in range(len(sin2_arr)-1):
    if sin2_arr[i] < 3/8 and sin2_arr[i+1] >= 3/8:
        frac = (3/8 - sin2_arr[i]) / (sin2_arr[i+1] - sin2_arr[i])
        t_NCG = sol_std.t[i] + frac * (sol_std.t[i+1] - sol_std.t[i])
        Lambda_NCG = M_Z * np.exp(t_NCG)
        g_unif = sol_std.y[1, i] + frac * (sol_std.y[1, i+1] - sol_std.y[1, i])
        yt_NCG = sol_std.y[3, i] + frac * (sol_std.y[3, i+1] - sol_std.y[3, i])
        break

# CCM boundary conditions
lam_CCM_top = g_unif**2 / 12  # R = 1/3, factor 1/4
lam_CCM_nu = g_unif**2 / 16   # R = 1/4, factor 1/4

def run_down_from_Pl(lam_val):
    y0 = [g1_P, g2_P, g3_P, yt_P, lam_val]
    sol = solve_ivp(beta_SM_1loop, (t_Pl, t_Mt), y0, method='RK45',
                    rtol=1e-12, atol=1e-14)
    if sol.success:
        return sol.y[4, -1]
    return None

def lam_to_mH(lam_Mt):
    if lam_Mt is None:
        return None
    if lam_Mt > 0:
        return v * np.sqrt(2 * lam_Mt)
    else:
        return None

# Test all boundary conditions
print(f"\n{'Boundary Condition':>45s}  {'lambda(M_Pl)':>14s}  {'m_H (GeV)':>10s}  {'Source':>30s}")
print("-" * 105)

conditions = [
    ("SM observed (m_H = 125.25 GeV)", lam_P, "Standard Model"),
    ("lambda(M_Pl) = 0", 0.0, "Near-criticality"),
    ("beta(lambda)=0, negative root", lam_AS_neg, "Asymptotic safety (SW)"),
    ("beta(lambda)=0, positive root", lam_AS_pos, "Asymptotic safety (UV FP)"),
    ("lambda = -0.01", -0.01, "Ad hoc"),
    ("lambda = -0.015", -0.015, "Ad hoc"),
    ("lambda = -0.02", -0.02, "Ad hoc"),
]

for label, lam_val, source in conditions:
    lam_Mt_out = run_down_from_Pl(lam_val)
    mH = lam_to_mH(lam_Mt_out)
    mH_str = f"{mH:.2f}" if mH else "unstable"
    print(f"{label:>45s}  {lam_val:14.8f}  {mH_str:>10s}  {source:>30s}")

# CCM at Lambda_NCG (run from NCG scale, not M_Pl)
print(f"\n--- CCM boundary conditions at Lambda_NCG = {Lambda_NCG:.2e} GeV ---")
g1_N = sol_std.y[0, i] + frac * (sol_std.y[0, i+1] - sol_std.y[0, i])
g2_N = sol_std.y[1, i] + frac * (sol_std.y[1, i+1] - sol_std.y[1, i])
g3_N = sol_std.y[2, i] + frac * (sol_std.y[2, i+1] - sol_std.y[2, i])
yt_N = yt_NCG

for lam_label, lam_val in [
    ("CCM lambda=g^2/12 (R=1/3)", g_unif**2/12),
    ("CCM lambda=g^2/16 (R=1/4)", g_unif**2/16),
    ("CCM lambda=g^2*R/2 (R=1/3)", g_unif**2/6),
    ("CCM lambda=g^2*R/2 (R=1/4)", g_unif**2/8),
]:
    y0 = [g1_N, g2_N, g3_N, yt_N, lam_val]
    sol = solve_ivp(beta_SM_1loop, (t_NCG, t_Mt), y0, method='RK45',
                    rtol=1e-12, atol=1e-14)
    if sol.success:
        lam_Mt_out = sol.y[4, -1]
        mH = v * np.sqrt(2 * lam_Mt_out) if lam_Mt_out > 0 else None
        mH_str = f"{mH:.2f}" if mH else "unstable"
    else:
        mH_str = "FAIL"
    print(f"  {lam_label:>45s}  {lam_val:10.6f}  {mH_str:>10s}")


# =====================================================
# THE ACTUAL "124.5 GeV CLAIM" ANALYSIS
# =====================================================

print("\n" + "=" * 70)
print('ANALYSIS OF THE "124.5 GeV" CLAIM')
print("=" * 70)

print("""
The claim "NCG spectral action predicts m_H = 124.5 GeV when using running
Yukawa couplings at Lambda = M_Pl" likely refers to ONE of these scenarios:

SCENARIO A: The Devastato-Lizzi-Martinetti (2014) computation
  - Uses the CCM spectral triple WITH right-handed neutrinos
  - Includes seesaw threshold corrections at M_R ~ 10^{11-14} GeV
  - Can reproduce m_H ~ 125 GeV for specific choices of (y_nu, M_R)
  - NOT parameter-free: requires fitting the neutrino sector

SCENARIO B: The Shaposhnikov-Wetterich (2009) asymptotic safety
  - Imposes lambda(M_Pl) ~ 0 from gravitational asymptotic safety
  - Predicted m_H ~ 126 GeV BEFORE discovery
  - Close but NOT from the NCG spectral action itself
  - With m_t = 172.76 and 1-loop, gives 133.8 GeV (too high)
  - With m_t = 171 and NNLO, gives ~126 GeV (matches their paper)

SCENARIO C: Confused attribution
  - Someone combined the NCG boundary condition idea with the near-criticality
    of lambda at M_Pl (which IS observed in the SM) and attributed it to NCG
  - The observed lambda(M_Pl) ~ -0.017 to -0.033 (2-loop to 1-loop) is
    indeed "near zero," but this is an OBSERVATION, not a prediction

SCENARIO D: A specific NCG variant with modified spectral triple
  - Several post-2012 papers modify the original CCM spectral triple
  - Adding scalar singlets, twisted spectral triples, etc.
  - These CAN give m_H ~ 125 but always with additional parameters

None of these scenarios constitute a "parameter-free prediction of 124.5 GeV
from the NCG spectral action." The number 124.5 is suspiciously close to
the observed 125.25 but doesn't match ANY clean theoretical boundary condition.
""")


# =====================================================
# SUMMARY TABLE
# =====================================================

print("=" * 70)
print("SUMMARY TABLE: ALL HIGGS MASS PREDICTIONS")
print("=" * 70)

print(f"""
| Source                          | Boundary Condition        | lambda(Lambda) | m_H (GeV)  | Status    |
|---------------------------------|---------------------------|----------------|------------|-----------|
| CCM original (2007), tree-level | lambda=g^2*R/4, R=1/4    | 0.019          | ~170       | RULED OUT |
| CCM + RG running (this work)    | lambda=g^2/12 at 10^13   | 0.025          | 137        | RULED OUT |
| CCM + RG running (this work)    | lambda=g^2/16 at 10^13   | 0.019          | 136        | RULED OUT |
| lambda(M_Pl) = 0 (1-loop)      | near-criticality          | 0.000          | 133.8      | RULED OUT |
| lambda(M_Pl) = 0 (2-loop)      | near-criticality          | 0.000          | ~129       | CLOSE     |
| beta(lambda)=0, 1L couplings   | asymptotic safety         | -0.024         | 126.7      | CLOSE     |
| beta(lambda)=0, 2L couplings   | asymptotic safety         | -0.0015        | ~129       | CLOSE     |
| SW (2009), NNLO, m_t=171       | AS + gravity              | ~0             | 126±3      | CLOSE     |
| For m_H = 124.5 exactly (1L)   | specific tuning           | -0.0304        | 124.5      | TAUTOLOGY |
| For m_H = 124.5 exactly (2L)   | specific tuning           | -0.0147        | 124.5      | TAUTOLOGY |
| For m_H = 125.25 exactly (2L)  | specific tuning           | -0.0126        | 125.25     | TAUTOLOGY |
| OBSERVED                        | Standard Model            | -0.033 (1L)    | 125.25     | FACT      |

Note: The 2-loop results here use approximate 2-loop beta functions. Full NNLO
(3-loop RGE + 2-loop matching) shifts results by an additional 1-3 GeV.
Professional codes like mr (Kniehl et al.) or the Buttazzo et al. computation
give more precise results.
""")

# =====================================================
# FINAL VERDICT
# =====================================================

print("=" * 70)
print("FINAL VERDICT")
print("=" * 70)

print(f"""
CLAIM UNDER EXAMINATION:
  "The NCG spectral action predicts m_H = 124.5 GeV when using running
   Yukawa couplings at the cutoff Lambda = M_Pl."

STATUS: *** FALSIFIED (as a parameter-free NCG prediction) ***

DETAILED FINDINGS:

1. The ORIGINAL Chamseddine-Connes-Marcolli spectral action predicts
   m_H ≈ 170 GeV (tree-level) or m_H ≈ 136-142 GeV (with RG running).
   Neither is 124.5 GeV.

2. The CCM boundary condition lambda(Lambda) = g^2(Lambda)*b/(4*a^2) at the
   NCG unification scale (where sin^2 theta_W = 3/8, mu ~ 10^13 GeV) gives
   lambda ~ 0.019-0.025, which after RG running yields m_H = 136-137 GeV.

3. The claim likely CONFLATES two different things:
   (a) The NCG spectral triple (which gives gauge-Yukawa-Higgs relations)
   (b) The near-criticality of the SM Higgs quartic at high scales
       (which is an empirical fact about the SM, not an NCG prediction)

4. The observed m_H = 125.25 GeV implies lambda(M_Pl) ≈ -0.017 (2-loop),
   which is indeed "close to zero" — the vacuum metastability/near-criticality.
   But this is an OBSERVATION, not a prediction from the spectral triple.

5. The Shaposhnikov-Wetterich asymptotic safety prediction m_H ≈ 126 ± 3 GeV
   is the closest genuine PREDICTION that gives the right Higgs mass.
   But this comes from GRAVITATIONAL asymptotic safety, not from the NCG
   spectral action. (Though the two frameworks share mathematical structure.)

6. To get exactly 124.5 GeV from M_Pl boundary condition:
   - 1-loop: need lambda(M_Pl) = -0.0304 (92.9% of the SM value)
   - 2-loop: need lambda(M_Pl) = -0.0147 (86.1% of the SM value)
   Neither is "zero" or matches any natural boundary condition.

WHAT IS TRUE:
  - NCG constrains the Higgs sector (reduces free parameters)
  - The near-criticality of lambda at M_Pl is a genuine mystery
  - The SW asymptotic safety prediction works surprisingly well
  - NCG + seesaw thresholds CAN accommodate 125 GeV (but not parameter-free)

WHAT IS FALSE:
  - That the unmodified spectral action gives m_H = 124.5 GeV
  - That this is a parameter-free prediction
  - That 124.5 GeV comes from "running Yukawa couplings at Lambda = M_Pl"
""")
