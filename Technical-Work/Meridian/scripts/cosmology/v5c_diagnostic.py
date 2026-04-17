#!/usr/bin/env python3
"""Diagnostic: evaluate v5c likelihood at physical vs fitted parameters."""
import os, sys, numpy as np

os.environ['JAX_PLATFORMS'] = 'cuda'
import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp

C_KMS = 299792.458
OMEGA_GAMMA_H2 = 2.469e-5
N_EFF = 3.046
OMEGA_R_H2 = OMEGA_GAMMA_H2 * (1 + 7/8 * (4/11)**(4/3) * N_EFF)
OMBH2 = 0.02237
RD_PRIOR_MEAN = 147.09
RD_PRIOR_SIGMA = 0.26

DATA_DIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase18/data'

GL_NODES, GL_WEIGHTS = np.polynomial.legendre.leggauss(64)
GL_NODES = jnp.array(GL_NODES)
GL_WEIGHTS = jnp.array(GL_WEIGHTS)

def Ez2(z, w0, wa, Om, h):
    a = 1.0 / (1.0 + z)
    Or = OMEGA_R_H2 / h**2
    ODE = 1.0 - Om - Or
    de = a**(-3*(1 + w0 + wa)) * jnp.exp(-3*wa*(1 - a))
    return Om*(1+z)**3 + Or*(1+z)**4 + ODE*de

def comoving_distances_gauss(z_arr, w0, wa, Om, H0):
    h = H0 / 100.0
    z_eval = z_arr[:, None] * (1 + GL_NODES[None, :]) / 2
    inv_E = 1.0 / jnp.sqrt(jnp.maximum(Ez2(z_eval, w0, wa, Om, h), 1e-30))
    integral = inv_E @ GL_WEIGHTS
    return (C_KMS * z_arr) / (2 * H0) * integral

def H_of_z(z, w0, wa, Om, H0):
    return H0 * jnp.sqrt(jnp.maximum(Ez2(z, w0, wa, Om, H0/100), 1e-30))

def _compute_sh(Om, H0):
    h = H0/100; omh2 = Om*h**2; Or = OMEGA_R_H2/h**2
    b1 = 0.313*omh2**(-0.419)*(1+0.607*omh2**0.674)
    b2 = 0.238*omh2**0.223
    z_d = 1291*omh2**0.251/(1+0.659*omh2**0.828)*(1+b1*OMBH2**b2)
    g1 = 0.0783*OMBH2**(-0.238)/(1+39.5*OMBH2**0.763)
    g2 = 0.560/(1+21.1*OMBH2**1.81)
    z_s = 1048*(1+0.00124*OMBH2**(-0.738))*(1+g1*omh2**g2)
    def _sh_int(zl, zh=20000, n=1000):
        z = np.linspace(zl, zh, n)
        Rb = 3*OMBH2/(4*OMEGA_GAMMA_H2)/(1+z)
        cs = C_KMS/np.sqrt(3*(1+Rb))
        E2 = Om*(1+z)**3 + Or*(1+z)**4
        H = H0*np.sqrt(E2)
        return np.trapezoid(cs/H, z)
    rd = _sh_int(z_d)
    rs = _sh_int(z_s)
    z2 = np.linspace(0, z_s, 3000)
    E2 = Om*(1+z2)**3+Or*(1+z2)**4+(1-Om-Or)
    dc_star = np.trapezoid(C_KMS/(H0*np.sqrt(np.maximum(E2,1e-30))), z2)
    return rd, rs, z_s, dc_star

# Load data
bao_dir = os.path.join(DATA_DIR, 'desi_dr2_bao')
bao_mean = []
with open(os.path.join(bao_dir, 'desi_gaussian_bao_ALL_GCcomb_mean.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        bao_mean.append(float(line.split()[1]))
bao_mean = jnp.array(bao_mean)
bao_cov = np.loadtxt(os.path.join(bao_dir, 'desi_gaussian_bao_ALL_GCcomb_cov.txt'))
bao_cov_inv = jnp.array(np.linalg.inv(bao_cov))

sne_dir = os.path.join(DATA_DIR, 'pantheonplus')
sne_raw = np.genfromtxt(os.path.join(sne_dir, 'Pantheon+SH0ES.dat'), names=True, dtype=None, encoding='utf-8')
z_cmb_all = np.array([float(r['zHD']) for r in sne_raw])
z_hel_all = np.array([float(r['zHEL']) for r in sne_raw])
m_obs_all = np.array([float(r['m_b_corr']) for r in sne_raw])
cov_raw = np.loadtxt(os.path.join(sne_dir, 'Pantheon+SH0ES_STAT+SYS.cov'))
N_cov = int(cov_raw[0])
C_full = cov_raw[1:].reshape(N_cov, N_cov)
mask = z_cmb_all > 0.01
m_obs = jnp.array(m_obs_all[mask])
z_cmb = jnp.array(z_cmb_all[mask])
z_hel = jnp.array(z_hel_all[mask])
C = C_full[np.ix_(mask, mask)]
C_inv = np.linalg.inv(C)
ones = np.ones(int(mask.sum()))
Ci1 = C_inv @ ones
C_inv_marg = jnp.array(C_inv - np.outer(Ci1, Ci1) / (ones @ Ci1))

cmb_means = jnp.array([1.7502, 301.471, 0.02237])
cmb_sigmas = jnp.array([0.0046, 0.090, 0.00015])
cmb_corr = jnp.array([[1.0, 0.46, -0.66], [0.46, 1.0, -0.33], [-0.66, -0.33, 1.0]])
cmb_cov_inv = jnp.linalg.inv(jnp.outer(cmb_sigmas, cmb_sigmas) * cmb_corr)

def eval_chi2(w0, wa, Om, H0, label):
    rd, rs, zs, dc_star = _compute_sh(Om, H0)
    
    bao_z = jnp.array([0.295, 0.510, 0.706, 0.934, 1.321, 1.484, 2.330])
    dc_bao = comoving_distances_gauss(bao_z, w0, wa, Om, H0)
    H_bao = H_of_z(bao_z, w0, wa, Om, H0)
    
    DV_bgs = (0.295 * dc_bao[0]**2 * C_KMS / H_bao[0])**(1/3) / rd
    DM = dc_bao[1:] / rd
    DH = C_KMS / H_bao[1:] / rd
    bao_vec = jnp.array([DV_bgs, DM[0], DH[0], DM[1], DH[1], DM[2], DH[2],
                          DM[3], DH[3], DM[4], DH[4], DH[5], DM[5]])
    d_bao = bao_vec - bao_mean
    chi2_bao = float(d_bao @ bao_cov_inv @ d_bao)
    
    dc_sne = comoving_distances_gauss(z_cmb, w0, wa, Om, H0)
    dL = (1 + z_hel) * dc_sne
    mu = 5.0 * jnp.log10(jnp.maximum(dL, 1e-10)) + 25.0
    d_sne = m_obs - mu
    chi2_sne = float(d_sne @ C_inv_marg @ d_sne)
    
    R = jnp.sqrt(Om) * H0 * dc_star / C_KMS
    l_A = jnp.pi * dc_star / rs
    cmb_vec = jnp.array([R, l_A, OMBH2]) - cmb_means
    chi2_cmb = float(cmb_vec @ cmb_cov_inv @ cmb_vec)
    
    chi2_rd = float(((rd - RD_PRIOR_MEAN) / RD_PRIOR_SIGMA)**2)
    
    total = chi2_bao + chi2_sne + chi2_cmb + chi2_rd
    
    print(f"\n=== {label} ===")
    print(f"  w0={w0}, wa={wa}, Om={Om}, H0={H0}")
    print(f"  rd = {rd:.2f} Mpc")
    print(f"  R = {float(R):.4f}, l_A = {float(l_A):.3f}")
    print(f"  chi2_bao  = {chi2_bao:.2f}")
    print(f"  chi2_sne  = {chi2_sne:.2f}")
    print(f"  chi2_cmb  = {chi2_cmb:.2f}")
    print(f"  chi2_rd   = {chi2_rd:.2f}")
    print(f"  TOTAL     = {total:.2f}")
    
    # Print BAO theory vs data
    print(f"\n  BAO theory vs data:")
    for i, (t, d) in enumerate(zip(bao_vec, bao_mean)):
        print(f"    [{i:2d}] theory={float(t):.4f}  data={float(d):.4f}  diff={float(t-d):.4f}")
    
    return total

print("Loading data...", flush=True)
print(f"Platform: {jax.default_backend()}")
print(f"BAO: {len(bao_mean)} points, SNe: {mask.sum()}")
print(f"BAO data: {bao_mean}")

# Physical parameters (near v3 best-fit)
eval_chi2(-1.0, 0.0, 0.3, 67.4, "Physical (LCDM-like)")
eval_chi2(-0.93, 0.0, 0.396, 79.5, "v5c Fit A result")
eval_chi2(-1.01, 0.0, 0.302, 67.8, "Near v3 Fit A")

# CPL cases
eval_chi2(-0.56, -1.88, 0.397, 79.4, "v5c Fit B result")
eval_chi2(-0.85, -0.60, 0.305, 67.5, "Physical CPL")

print("\nDone.", flush=True)
