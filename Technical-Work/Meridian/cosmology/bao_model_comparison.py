"""
BAO Distance Comparison: Meridian (w=-0.993) vs ΛCDM vs CPL

Computes D_M/r_d and D_H/r_d at DESI DR2 effective redshifts for three models:
1. ΛCDM (w = -1)
2. Meridian prediction (w = -0.993, constant)
3. CPL best-fit (w0 = -0.75, wa = -0.86)

Shows fractional differences to assess whether current data can distinguish models.

Author: Clawd
Date: 2026-03-16
"""

import numpy as np
from scipy.integrate import quad

# ============================================================
# Cosmological parameters (Planck 2018 + DESI fiducial)
# ============================================================
c = 299792.458  # km/s
H0 = 67.36      # km/s/Mpc
Omega_m = 0.3153
Omega_DE = 1.0 - Omega_m  # flat universe
r_d = 147.09    # Mpc (fiducial Planck sound horizon)

# DESI DR2 effective redshifts
tracers = ['BGS', 'LRG1', 'LRG2', 'LRG3+ELG1', 'ELG2', 'QSO', 'Lya']
z_eff = np.array([0.295, 0.510, 0.706, 0.934, 1.321, 1.484, 2.330])

# Approximate DESI DR2 fractional precision on DM/rd and DH/rd (%)
# From: "uncertainties ranging from 1.54% for QSO down to 0.45% for LRG3+ELG1"
sigma_DM_pct = np.array([1.5, 0.95, 0.56, 0.46, 0.76, 1.56, 1.16])  # approximate
sigma_DH_pct = np.array([2.0, 1.72, 1.25, 0.95, 1.52, 2.64, 1.17])  # approximate

# ============================================================
# Hubble parameter for different dark energy models
# ============================================================
def H_wCDM(z, w):
    """Hubble parameter for constant w dark energy."""
    return H0 * np.sqrt(Omega_m * (1+z)**3 + Omega_DE * (1+z)**(3*(1+w)))

def H_CPL(z, w0, wa):
    """Hubble parameter for CPL parameterization: w(a) = w0 + wa*(1-a)."""
    a = 1.0 / (1.0 + z)
    # DE density: rho_DE/rho_DE0 = a^(-3(1+w0+wa)) * exp(-3*wa*(1-a))
    DE_factor = a**(-3*(1+w0+wa)) * np.exp(-3*wa*(1-a))
    return H0 * np.sqrt(Omega_m * (1+z)**3 + Omega_DE * DE_factor)

# ============================================================
# Distance measures
# ============================================================
def compute_DH(z, H_func, *args):
    """D_H(z) = c/H(z) in Mpc."""
    return c / H_func(z, *args)

def compute_DM(z, H_func, *args):
    """D_M(z) = c * integral_0^z dz'/H(z') in Mpc."""
    integrand = lambda zp: c / H_func(zp, *args)
    result, _ = quad(integrand, 0, z)
    return result

def compute_DV(z, DM, DH):
    """D_V(z) = [z * DM^2 * DH]^(1/3)."""
    return (z * DM**2 * DH)**(1.0/3.0)

# ============================================================
# Compute all distances
# ============================================================
models = {
    'LCDM':    {'func': H_wCDM, 'args': (-1.0,),       'label': 'ΛCDM (w=-1)'},
    'Meridian':{'func': H_wCDM, 'args': (-0.993,),      'label': 'Meridian (w=-0.993)'},
    'CPL':     {'func': H_CPL,  'args': (-0.75, -0.86), 'label': 'CPL (w₀=-0.75, wₐ=-0.86)'},
}

results = {}
for name, model in models.items():
    DM_over_rd = []
    DH_over_rd = []
    DV_over_rd = []
    for z in z_eff:
        DH = compute_DH(z, model['func'], *model['args'])
        DM = compute_DM(z, model['func'], *model['args'])
        DV = compute_DV(z, DM, DH)
        DM_over_rd.append(DM / r_d)
        DH_over_rd.append(DH / r_d)
        DV_over_rd.append(DV / r_d)
    results[name] = {
        'DM_rd': np.array(DM_over_rd),
        'DH_rd': np.array(DH_over_rd),
        'DV_rd': np.array(DV_over_rd),
    }

# ============================================================
# Output
# ============================================================
output = []
output.append("=" * 80)
output.append("BAO DISTANCE COMPARISON: Meridian vs ΛCDM vs CPL at DESI DR2 Redshifts")
output.append("=" * 80)
output.append("")

# Table 1: Absolute values
output.append("TABLE 1: D_M/r_d at DESI DR2 effective redshifts")
output.append("-" * 75)
header = f"{'Tracer':<12} {'z_eff':>5} {'ΛCDM':>10} {'Meridian':>10} {'CPL':>10}"
output.append(header)
output.append("-" * 75)
for i, (t, z) in enumerate(zip(tracers, z_eff)):
    output.append(f"{t:<12} {z:>5.3f} {results['LCDM']['DM_rd'][i]:>10.4f} "
                  f"{results['Meridian']['DM_rd'][i]:>10.4f} {results['CPL']['DM_rd'][i]:>10.4f}")
output.append("")

output.append("TABLE 2: D_H/r_d at DESI DR2 effective redshifts")
output.append("-" * 75)
output.append(header)
output.append("-" * 75)
for i, (t, z) in enumerate(zip(tracers, z_eff)):
    output.append(f"{t:<12} {z:>5.3f} {results['LCDM']['DH_rd'][i]:>10.4f} "
                  f"{results['Meridian']['DH_rd'][i]:>10.4f} {results['CPL']['DH_rd'][i]:>10.4f}")
output.append("")

# Table 3: Fractional differences from ΛCDM (the key table)
output.append("TABLE 3: FRACTIONAL DIFFERENCE FROM ΛCDM (%)")
output.append("  δ(D_M/r_d) = (Model - ΛCDM) / ΛCDM × 100")
output.append("  Compared to approximate DESI DR2 measurement precision σ(%)")
output.append("-" * 85)
header3 = (f"{'Tracer':<12} {'z':>5} {'Merid δDM%':>10} {'CPL δDM%':>10} "
           f"{'σ_DM%':>7} {'Merid δDH%':>10} {'CPL δDH%':>10} {'σ_DH%':>7}")
output.append(header3)
output.append("-" * 85)

for i, (t, z) in enumerate(zip(tracers, z_eff)):
    dDM_merid = (results['Meridian']['DM_rd'][i] / results['LCDM']['DM_rd'][i] - 1) * 100
    dDM_cpl   = (results['CPL']['DM_rd'][i]      / results['LCDM']['DM_rd'][i] - 1) * 100
    dDH_merid = (results['Meridian']['DH_rd'][i] / results['LCDM']['DH_rd'][i] - 1) * 100
    dDH_cpl   = (results['CPL']['DH_rd'][i]      / results['LCDM']['DH_rd'][i] - 1) * 100

    output.append(f"{t:<12} {z:>5.3f} {dDM_merid:>+10.4f} {dDM_cpl:>+10.4f} "
                  f"{sigma_DM_pct[i]:>7.2f} {dDH_merid:>+10.4f} {dDH_cpl:>+10.4f} {sigma_DH_pct[i]:>7.2f}")

output.append("")
output.append("-" * 85)

# Summary statistics
dDM_merid_all = (results['Meridian']['DM_rd'] / results['LCDM']['DM_rd'] - 1) * 100
dDM_cpl_all   = (results['CPL']['DM_rd']      / results['LCDM']['DM_rd'] - 1) * 100
dDH_merid_all = (results['Meridian']['DH_rd'] / results['LCDM']['DH_rd'] - 1) * 100
dDH_cpl_all   = (results['CPL']['DH_rd']      / results['LCDM']['DH_rd'] - 1) * 100

output.append("")
output.append("SUMMARY:")
output.append(f"  Meridian max |δD_M|: {np.max(np.abs(dDM_merid_all)):.4f}%")
output.append(f"  Meridian max |δD_H|: {np.max(np.abs(dDH_merid_all)):.4f}%")
output.append(f"  CPL max |δD_M|:      {np.max(np.abs(dDM_cpl_all)):.4f}%")
output.append(f"  CPL max |δD_H|:      {np.max(np.abs(dDH_cpl_all)):.4f}%")
output.append(f"  Min DESI σ_DM:       {np.min(sigma_DM_pct):.2f}%")
output.append(f"  Min DESI σ_DH:       {np.min(sigma_DH_pct):.2f}%")
output.append("")

# Detection significance: |δ|/σ for each measurement
output.append("TABLE 4: DETECTION SIGNIFICANCE |δ/σ| (number of sigma)")
output.append("-" * 75)
header4 = f"{'Tracer':<12} {'z':>5} {'Merid DM':>9} {'CPL DM':>9} {'Merid DH':>9} {'CPL DH':>9}"
output.append(header4)
output.append("-" * 75)

merid_chi2_DM = 0
merid_chi2_DH = 0
cpl_chi2_DM = 0
cpl_chi2_DH = 0

for i, (t, z) in enumerate(zip(tracers, z_eff)):
    sig_merid_DM = abs(dDM_merid_all[i]) / sigma_DM_pct[i]
    sig_cpl_DM   = abs(dDM_cpl_all[i])   / sigma_DM_pct[i]
    sig_merid_DH = abs(dDH_merid_all[i]) / sigma_DH_pct[i]
    sig_cpl_DH   = abs(dDH_cpl_all[i])   / sigma_DH_pct[i]

    merid_chi2_DM += sig_merid_DM**2
    merid_chi2_DH += sig_merid_DH**2
    cpl_chi2_DM += sig_cpl_DM**2
    cpl_chi2_DH += sig_cpl_DH**2

    output.append(f"{t:<12} {z:>5.3f} {sig_merid_DM:>9.3f}σ {sig_cpl_DM:>9.3f}σ "
                  f"{sig_merid_DH:>9.3f}σ {sig_cpl_DH:>9.3f}σ")

output.append("")
output.append(f"  Approx Σ(δ/σ)² for Meridian: DM={merid_chi2_DM:.3f}, DH={merid_chi2_DH:.3f}")
output.append(f"  Approx Σ(δ/σ)² for CPL:      DM={cpl_chi2_DM:.3f}, DH={cpl_chi2_DH:.3f}")
output.append("")

# Interpretation
output.append("=" * 80)
output.append("INTERPRETATION")
output.append("=" * 80)
output.append("")
output.append("If Meridian |δ/σ| << 1 at all redshifts:")
output.append("  → Our model is INDISTINGUISHABLE from ΛCDM with current DESI precision.")
output.append("  → The 'tension' is not between our model and data,")
output.append("    but between our model and the CPL parameterization.")
output.append("")
output.append("If CPL |δ/σ| > 1 at some redshifts:")
output.append("  → CPL IS distinguishable from ΛCDM — that's where the statistical preference comes from.")
output.append("  → But if model-independent analyses (cosmographic, pivoted w_p)")
output.append("    don't show this preference, CPL is forcing an artifact.")
output.append("")
output.append("Our prediction w₀ = -0.993 is falsifiable by Euclid/Rubin/Roman")
output.append("when σ(w₀) drops below ~0.007 (current precision: ~0.07).")
output.append("")

# Write to file
text = "\n".join(output)
with open("bao_comparison_results.txt", "w", encoding="utf-8") as f:
    f.write(text)
import builtins
builtins.print(text.encode('ascii', 'replace').decode('ascii'))
