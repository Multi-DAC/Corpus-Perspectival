#!/usr/bin/env python3
"""Volume discrepancy diagnostic: why does Vol(bal) = 4.63 != Vol(FS) = 15.19?

Test: compute the covariance formula with G = I (identity).
If the formula is correct, this should give g_FS and Vol(FS) = 15.19.
If it gives something else, the formula has a normalization error.
"""
import numpy as np
from math import pi
import sys, time
sys.stdout.reconfigure(encoding='utf-8')

# Minimal sampling
N_MC = 50000
DOMAIN_R = 5.0
BAL_K = 8
RNG_SEED = 2026
rng = np.random.default_rng(RNG_SEED)

# Sample surface
a_all_list, b_all_list, c_all_list = [], [], []
for _ in range(3):
    a_re = rng.uniform(-DOMAIN_R, DOMAIN_R, N_MC)
    a_im = rng.uniform(-DOMAIN_R, DOMAIN_R, N_MC)
    b_re = rng.uniform(-DOMAIN_R, DOMAIN_R, N_MC)
    b_im = rng.uniform(-DOMAIN_R, DOMAIN_R, N_MC)
    a = a_re + 1j * a_im
    b = b_re + 1j * b_im
    w_raw = -(a**3 + b**3 + 1)
    r = np.abs(w_raw) ** (1.0 / 3.0)
    theta = np.angle(w_raw) / 3.0
    c = r * np.exp(1j * theta)
    valid = np.abs(c**3 + a**3 + b**3 + 1) < 0.01 * (1 + np.abs(a)**3 + np.abs(b)**3)
    valid &= np.abs(c) > 0.02
    a_all_list.append(a[valid])
    b_all_list.append(b[valid])
    c_all_list.append(c[valid])

a_all = np.concatenate(a_all_list)
b_all = np.concatenate(b_all_list)
c_all = np.concatenate(c_all_list)
N_total = len(a_all)
P = 1 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2

# FS metric
dc_da = -(a_all**2) / (c_all**2)
dc_db = -(b_all**2) / (c_all**2)
dP_da = np.conj(a_all) + np.conj(c_all) * dc_da
dP_db = np.conj(b_all) + np.conj(c_all) * dc_db
dP_dab = a_all + c_all * np.conj(dc_da)
dP_dbb = b_all + c_all * np.conj(dc_db)

g_FS_11 = (P * (1 + np.abs(dc_da)**2) - np.abs(dP_da)**2) / P**2
g_FS_12 = (P * dc_db * np.conj(dc_da) - dP_db * np.conj(dP_da)) / P**2
g_FS_22 = (P * (1 + np.abs(dc_db)**2) - np.abs(dP_db)**2) / P**2

det_g_FS = np.abs(g_FS_11 * g_FS_22 - g_FS_12 * np.conj(g_FS_12))
domain_vol = (2 * DOMAIN_R)**4
weights_FS = det_g_FS * domain_vol / (3 * N_MC)
vol_FS = np.sum(weights_FS)
vol_exact = 3 * pi**2 / 2

print(f"N_total = {N_total}")
print(f"Vol(FS) = {vol_FS:.4f} (exact = {vol_exact:.4f})")

# Now: build sections at k=8 with G = IDENTITY
k = BAL_K
sec_indices = []
for j1 in range(k + 1):
    for j2 in range(k - j1 + 1):
        for j3 in range(min(k - j1 - j2, 2) + 1):
            sec_indices.append((j1, j2, j3))

N_sec = len(sec_indices)
print(f"\nN_sections = {N_sec}")

# Compute section norms for FS normalization
print("Computing section norms...")
logP = np.log(P)
P_half_k = np.exp(-0.5 * k * logP)

a_pow_b = [np.ones(N_total, dtype=complex)]
b_pow_b = [np.ones(N_total, dtype=complex)]
c_pow_b = [np.ones(N_total, dtype=complex)]
for i in range(1, k + 1):
    a_pow_b.append(a_pow_b[-1] * a_all)
    b_pow_b.append(b_pow_b[-1] * b_all)
    if i <= 2:
        c_pow_b.append(c_pow_b[-1] * c_all)

# Raw section values (before normalization)
U_raw = np.empty((N_sec, N_total), dtype=complex)
for idx, (j1, j2, j3) in enumerate(sec_indices):
    U_raw[idx] = a_pow_b[j1] * b_pow_b[j2] * c_pow_b[j3] * P_half_k

# Compute norms via MC integration
sec_norms = np.sqrt(np.sum(np.abs(U_raw)**2 * weights_FS[np.newaxis, :], axis=1))
sec_norms = np.maximum(sec_norms, 1e-30)

# Normalized sections
U = U_raw / sec_norms[:, np.newaxis]

# === TEST 1: Covariance formula with G = I ===
print("\n=== TEST 1: Covariance formula with G = Identity ===")
# V = G @ U = I @ U = U
V_test = U.copy()
rho_test = np.real(np.sum(np.conj(U) * V_test, axis=0))  # = sum |U|^2
rho_safe = np.maximum(rho_test, 1e-30)

# R_a, R_b
R_a = dP_da / P
R_b = dP_db / P

# Utilde = (D - k*R) * U
inv_a = np.where(np.abs(a_all) > 1e-30, 1.0 / a_all, 0.0)
inv_b = np.where(np.abs(b_all) > 1e-30, 1.0 / b_all, 0.0)
dc_da_over_c = dc_da / c_all
dc_db_over_c = dc_db / c_all

Utilde_a = np.empty((N_sec, N_total), dtype=complex)
Utilde_b = np.empty((N_sec, N_total), dtype=complex)
for idx, (j1, j2, j3) in enumerate(sec_indices):
    D_a = np.zeros(N_total, dtype=complex)
    D_b = np.zeros(N_total, dtype=complex)
    if j1 > 0:
        D_a += j1 * inv_a
    if j3 > 0:
        D_a += j3 * dc_da_over_c
    if j2 > 0:
        D_b += j2 * inv_b
    if j3 > 0:
        D_b += j3 * dc_db_over_c
    Utilde_a[idx] = (D_a - k * R_a) * U[idx]
    Utilde_b[idx] = (D_b - k * R_b) * U[idx]

# With G = I: W_a = Utilde_a, W_b = Utilde_b
inv_rho = 1.0 / rho_safe
inv_rho2 = inv_rho * inv_rho

UaUa = np.real(np.sum(np.conj(Utilde_a) * Utilde_a, axis=0))
UbUb = np.real(np.sum(np.conj(Utilde_b) * Utilde_b, axis=0))
UbUa = np.sum(np.conj(Utilde_b) * Utilde_a, axis=0)

VdUa = np.sum(np.conj(V_test) * Utilde_a, axis=0)
VdUb = np.sum(np.conj(V_test) * Utilde_b, axis=0)

g_cov_11 = (1.0/k) * (UaUa * inv_rho - np.abs(VdUa)**2 * inv_rho2)
g_cov_22 = (1.0/k) * (UbUb * inv_rho - np.abs(VdUb)**2 * inv_rho2)
g_cov_12 = (1.0/k) * (UbUa * inv_rho - VdUa * np.conj(VdUb) * inv_rho2)

det_g_cov = (g_cov_11 * g_cov_22 - g_cov_12 * np.conj(g_cov_12)).real
weights_cov = np.abs(det_g_cov) * domain_vol / (3 * N_MC)
vol_cov = np.sum(weights_cov)

print(f"Vol(covariance, G=I) = {vol_cov:.4f}")
print(f"Vol(FS) = {vol_FS:.4f}")
print(f"Ratio = {vol_cov / vol_FS:.4f}")
print(f"Mean det ratio = {np.mean(np.abs(det_g_cov) / det_g_FS):.4f}")

# Also check: does the covariance give g_FS component-wise?
ratio_11 = np.mean(g_cov_11.real / g_FS_11.real)
ratio_22 = np.mean(g_cov_22.real / g_FS_22.real)
print(f"Mean g_cov_11 / g_FS_11 = {ratio_11:.4f}")
print(f"Mean g_cov_22 / g_FS_22 = {ratio_22:.4f}")

# === TEST 2: Additive formula g_bal = g_FS + (1/k)*ddbar(log rho) ===
print("\n=== TEST 2: Additive formula ===")
# ddbar log rho = (d_a d_bbar rho)/rho - (d_a rho)(d_bbar rho)/rho^2
# d_a rho = V^dag Utilde_a (= sum conj(U)*Utilde_a for G=I)
# d_bbar rho = conj(V^dag Utilde_b) = conj(sum conj(U)*Utilde_b)
# d_a d_bbar rho = Utilde_b^dag G Utilde_a - k*g_FS*rho
#   (for G=I: = sum conj(Utilde_b)*Utilde_a - k*g_FS*rho)

d2_rho_11 = np.real(np.sum(np.conj(Utilde_a) * Utilde_a, axis=0)) - k * g_FS_11.real * rho_test
d2_rho_22 = np.real(np.sum(np.conj(Utilde_b) * Utilde_b, axis=0)) - k * g_FS_22.real * rho_test
d2_rho_12 = np.sum(np.conj(Utilde_b) * Utilde_a, axis=0) - k * g_FS_12 * rho_test

# ddbar log rho
ddbar_11 = d2_rho_11 / rho_test - np.abs(VdUa)**2 / rho_test**2
ddbar_22 = d2_rho_22 / rho_test - np.abs(VdUb)**2 / rho_test**2
ddbar_12 = d2_rho_12 / rho_test - VdUa * np.conj(VdUb) / rho_test**2

# g_add = g_FS + (1/k)*ddbar
g_add_11 = g_FS_11.real + (1.0/k) * ddbar_11
g_add_22 = g_FS_22.real + (1.0/k) * ddbar_22
g_add_12 = g_FS_12 + (1.0/k) * ddbar_12

det_g_add = (g_add_11 * g_add_22 - g_add_12 * np.conj(g_add_12)).real
weights_add = np.abs(det_g_add) * domain_vol / (3 * N_MC)
vol_add = np.sum(weights_add)

print(f"Vol(additive, G=I) = {vol_add:.4f}")
print(f"Vol(FS) = {vol_FS:.4f}")
print(f"Ratio = {vol_add / vol_FS:.4f}")
print(f"Mean g_add_11 / g_FS_11 = {np.mean(g_add_11 / g_FS_11.real):.4f}")
print(f"Mean g_add_22 / g_FS_22 = {np.mean(g_add_22 / g_FS_22.real):.4f}")

# Verify: covariance = additive? (they SHOULD be identical)
diff_11 = np.max(np.abs(g_cov_11 - g_add_11))
diff_22 = np.max(np.abs(g_cov_22 - g_add_22))
diff_12 = np.max(np.abs(g_cov_12 - g_add_12))
print(f"\nCovariance vs Additive max diff: 11={diff_11:.2e}, 22={diff_22:.2e}, 12={diff_12:.2e}")

# === TEST 3: Now with the actual balanced metric G from k=8 ===
print("\n=== TEST 3: Balanced metric G from k=8 ===")
bal_data = np.load('balanced_metric_k8.npz', allow_pickle=True)
N_bal = int(bal_data['N_sections'])
sec_norms_bal = bal_data['section_norms']
sections_info = bal_data['sections']

G_full = np.zeros((N_bal, N_bal), dtype=complex)
for q1 in range(3):
    for q2 in range(3):
        gk = f'G_{q1}_{q2}'
        ik = f'idx_{q1}_{q2}'
        if gk in bal_data:
            G_block = bal_data[gk]
            indices = bal_data[ik]
            for i_local, i_global in enumerate(indices):
                for j_local, j_global in enumerate(indices):
                    G_full[int(i_global), int(j_global)] = G_block[i_local, j_local]

# Build PROPERLY normalized sections using bal_data norms
U_bal = np.empty((N_bal, N_total), dtype=complex)
for idx in range(N_bal):
    j1 = int(sections_info[idx, 0])
    j2 = int(sections_info[idx, 1])
    j3 = int(sections_info[idx, 2])
    U_bal[idx] = a_pow_b[j1] * b_pow_b[j2] * c_pow_b[j3] * P_half_k / sec_norms_bal[idx]

V_bal = G_full @ U_bal
rho_bal = np.real(np.sum(np.conj(U_bal) * V_bal, axis=0))
rho_bal_safe = np.maximum(rho_bal, 1e-30)

# Additive formula: g_bal = g_FS + (1/k)*ddbar log rho_G
# d_a rho_G = V^dag Utilde_a
Utilde_a_bal = np.empty((N_bal, N_total), dtype=complex)
Utilde_b_bal = np.empty((N_bal, N_total), dtype=complex)
for idx in range(N_bal):
    j1 = int(sections_info[idx, 0])
    j2 = int(sections_info[idx, 1])
    j3 = int(sections_info[idx, 2])
    D_a = np.zeros(N_total, dtype=complex)
    D_b = np.zeros(N_total, dtype=complex)
    if j1 > 0: D_a += j1 * inv_a
    if j3 > 0: D_a += j3 * dc_da_over_c
    if j2 > 0: D_b += j2 * inv_b
    if j3 > 0: D_b += j3 * dc_db_over_c
    Utilde_a_bal[idx] = (D_a - k * R_a) * U_bal[idx]
    Utilde_b_bal[idx] = (D_b - k * R_b) * U_bal[idx]

# Covariance formula
W_a = G_full @ Utilde_a_bal
W_b = G_full @ Utilde_b_bal
UaGUa = np.real(np.sum(np.conj(Utilde_a_bal) * W_a, axis=0))
UbGUb = np.real(np.sum(np.conj(Utilde_b_bal) * W_b, axis=0))
UbGUa = np.sum(np.conj(Utilde_b_bal) * W_a, axis=0)
VdUa_bal = np.sum(np.conj(V_bal) * Utilde_a_bal, axis=0)
VdUb_bal = np.sum(np.conj(V_bal) * Utilde_b_bal, axis=0)

inv_rho_bal = 1.0 / rho_bal_safe
inv_rho2_bal = inv_rho_bal**2

g_cov_bal_11 = (1.0/k) * (UaGUa * inv_rho_bal - np.abs(VdUa_bal)**2 * inv_rho2_bal)
g_cov_bal_22 = (1.0/k) * (UbGUb * inv_rho_bal - np.abs(VdUb_bal)**2 * inv_rho2_bal)
g_cov_bal_12 = (1.0/k) * (UbGUa * inv_rho_bal - VdUa_bal * np.conj(VdUb_bal) * inv_rho2_bal)

det_cov_bal = (g_cov_bal_11 * g_cov_bal_22 - g_cov_bal_12 * np.conj(g_cov_bal_12)).real
vol_cov_bal = np.sum(np.abs(det_cov_bal) * domain_vol / (3 * N_MC))

# Additive formula with balanced G
d2_rho_bal_11 = UaGUa - k * g_FS_11.real * rho_bal
d2_rho_bal_22 = UbGUb - k * g_FS_22.real * rho_bal
d2_rho_bal_12 = UbGUa - k * g_FS_12 * rho_bal

ddbar_bal_11 = d2_rho_bal_11 / rho_bal_safe - np.abs(VdUa_bal)**2 / rho_bal_safe**2
ddbar_bal_22 = d2_rho_bal_22 / rho_bal_safe - np.abs(VdUb_bal)**2 / rho_bal_safe**2
ddbar_bal_12 = d2_rho_bal_12 / rho_bal_safe - VdUa_bal * np.conj(VdUb_bal) / rho_bal_safe**2

g_add_bal_11 = g_FS_11.real + (1.0/k) * ddbar_bal_11
g_add_bal_22 = g_FS_22.real + (1.0/k) * ddbar_bal_22
g_add_bal_12 = g_FS_12 + (1.0/k) * ddbar_bal_12

det_add_bal = (g_add_bal_11 * g_add_bal_22 - g_add_bal_12 * np.conj(g_add_bal_12)).real
vol_add_bal = np.sum(np.abs(det_add_bal) * domain_vol / (3 * N_MC))

print(f"Vol(covariance, bal G) = {vol_cov_bal:.4f}")
print(f"Vol(additive, bal G) = {vol_add_bal:.4f}")
print(f"Vol(FS) = {vol_FS:.4f}")

# Check if they agree
diff_11 = np.max(np.abs(g_cov_bal_11 - g_add_bal_11))
diff_22 = np.max(np.abs(g_cov_bal_22 - g_add_bal_22))
print(f"Covariance vs Additive max diff: 11={diff_11:.2e}, 22={diff_22:.2e}")

# KEY CHECK: does d2_rho really include the -k*g_FS*rho term?
# Verify by direct finite difference at one point
print("\n=== FINITE DIFFERENCE VERIFICATION at point 0 ===")
eps = 1e-5
p = 0  # test point index

a0, b0, c0 = a_all[p], b_all[p], c_all[p]

def compute_rho_at(a_pt, b_pt):
    c_cubed = -(a_pt**3 + b_pt**3 + 1)
    c_pt = np.abs(c_cubed)**(1./3) * np.exp(1j * np.angle(c_cubed) / 3)
    P_pt = 1 + abs(a_pt)**2 + abs(b_pt)**2 + abs(c_pt)**2
    P_hk = P_pt**(-k/2)
    u = np.zeros(N_bal, dtype=complex)
    for idx, (j1, j2, j3) in enumerate([(int(sections_info[i,0]), int(sections_info[i,1]), int(sections_info[i,2])) for i in range(N_bal)]):
        u[idx] = a_pt**j1 * b_pt**j2 * c_pt**j3 * P_hk / sec_norms_bal[idx]
    v = G_full @ u
    return np.real(np.dot(np.conj(u), v))

rho0 = compute_rho_at(a0, b0)
# d_a d_abar rho by finite difference
rho_pa = compute_rho_at(a0 + eps, b0)
rho_ma = compute_rho_at(a0 - eps, b0)
rho_pia = compute_rho_at(a0 + 1j*eps, b0)
rho_mia = compute_rho_at(a0 - 1j*eps, b0)

# d_a d_abar = (1/4)(d_x^2 + d_y^2) where a = x + iy
d2_rho_fd = (rho_pa + rho_ma + rho_pia + rho_mia - 4*rho0) / (eps**2)

# Compare with analytic formula
d2_rho_analytic = float(UaGUa[p]) - k * float(g_FS_11[p].real) * float(rho_bal[p])

print(f"rho at point = {rho0:.6f}")
print(f"d_a d_abar rho (finite diff) = {d2_rho_fd:.6f}")
print(f"d_a d_abar rho (analytic) = {d2_rho_analytic:.6f}")
print(f"Ratio = {d2_rho_fd / d2_rho_analytic:.4f}")
