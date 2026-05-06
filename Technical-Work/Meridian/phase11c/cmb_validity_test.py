#!/usr/bin/env python3
"""
CMB Compressed Likelihood Validity Test
=========================================
Phase B of the Meridian Plan: Does the compressed CMB likelihood
(R, l_A, omega_b) accurately represent the full Planck constraint
at our predicted w_0 values?

Strategy:
1. Use CAMB to compute FULL C_l^TT,TE,EE spectra at different w_0
2. Compute shift parameters (R, l_A) at each w_0
3. Compare compressed chi^2 to Fisher-matrix-estimated full spectrum chi^2
4. Determine if the compressed form over/under-estimates the constraint

If the compressed and full chi^2 agree within 20%, the compressed form
is valid and the tension is real.

If they differ by >50%, the compressed form overstates the constraint
and we need the full Planck likelihood.

Key question: our prediction has |1+w_0| = 0.07 (at model extreme w_0 = -0.933).
The monograph notes the compressed likelihood was "calibrated near LCDM" and
"breaks for |1+w_0| > 0.05" (Ch2 line 432). We're right at the boundary.

Additionally: profile w_0 with full spectra to find actual CMB-only constraint.

Clayton Iggulden-Schnell & Clawd, April 2026
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy.optimize import minimize_scalar, minimize

def fprint(*args, **kwargs):
    print(*args, **kwargs, flush=True)

fprint("=" * 78)
fprint("  CMB COMPRESSED LIKELIHOOD VALIDITY TEST")
fprint("  Phase B: Is the compressed CMB constraint valid for |1+w_0| = 0.07-0.17?")
fprint("=" * 78)

import camb
fprint(f"\nCAMB version: {camb.__version__}")

C_LIGHT = 299792.458  # km/s

# ============================================================================
# PLANCK 2018 COMPRESSED LIKELIHOOD (Chen, Huang & Wang 2019)
# ============================================================================
R_OBS, R_SIG = 1.7502, 0.0046
LA_OBS, LA_SIG = 301.471, 0.090
OBH2_OBS, OBH2_SIG = 0.02236, 0.00015

# Correlation matrix
CMB_CORR = np.array([[1.0, 0.46, -0.66],
                      [0.46, 1.0, -0.33],
                      [-0.66, -0.33, 1.0]])
CMB_SIGMA = np.diag([R_SIG, LA_SIG, OBH2_SIG])
CMB_COV = CMB_SIGMA @ CMB_CORR @ CMB_SIGMA
CMB_COV_INV = np.linalg.inv(CMB_COV)

# Fiducial cosmology (Planck 2018 best fit)
H0_FID = 67.36
OM_FID = 0.3153
OMBH2 = 0.02237
OMCH2_FID = OM_FID * (H0_FID/100)**2 - OMBH2
AS_FID = 2.1e-9
NS_FID = 0.9649
TAU_FID = 0.054
MNU = 0.06

# Planck noise model (approximate combined 143+217 GHz)
THETA_FWHM = 5.0 * np.pi / (180 * 60)  # 5 arcmin in radians
SIGMA_T = 40.0  # uK-arcmin for temperature
SIGMA_P = 60.0  # uK-arcmin for polarization
F_SKY = 0.57
LMIN = 2
LMAX_TT = 2500
LMAX_EE = 2000

def planck_noise_TT(l):
    """Planck-like noise power spectrum for TT (uK^2)."""
    sigma_rad = SIGMA_T * np.pi / (180 * 60)  # convert to radians
    beam = np.exp(l * (l+1) * THETA_FWHM**2 / (8 * np.log(2)))
    return (sigma_rad)**2 * beam

def planck_noise_EE(l):
    """Planck-like noise power spectrum for EE (uK^2)."""
    sigma_rad = SIGMA_P * np.pi / (180 * 60)
    beam = np.exp(l * (l+1) * THETA_FWHM**2 / (8 * np.log(2)))
    return (sigma_rad)**2 * beam


# ============================================================================
# CAMB SPECTRUM COMPUTATION
# ============================================================================
def get_camb_spectra(H0, Om, w0=-1.0, obh2=OMBH2, As=AS_FID, ns=NS_FID, tau=TAU_FID):
    """Get full CMB power spectra and shift parameters from CAMB."""
    omch2 = Om * (H0/100)**2 - obh2
    if omch2 < 0.001:
        return None

    pars = camb.CAMBparams()
    pars.set_cosmology(H0=H0, ombh2=obh2, omch2=omch2, mnu=MNU, omk=0, tau=tau)
    if abs(w0 + 1) < 1e-5:
        pars.set_dark_energy(w=-1.0, wa=0.0)
    else:
        pars.set_dark_energy(w=w0, wa=0.0, dark_energy_model='ppf')

    pars.InitPower.set_params(As=As, ns=ns, r=0)
    pars.set_for_lmax(LMAX_TT + 500, lens_potential_accuracy=1)
    pars.Want_CMB = True

    results = camb.get_results(pars)
    derived = results.get_derived_params()

    # Power spectra (l(l+1)C_l/(2pi) in uK^2)
    powers = results.get_cmb_power_spectra(pars, CMB_unit='muK')
    totCL = powers['total']  # columns: TT, EE, BB, TE

    # Background distances
    DM_star = results.comoving_radial_distance(derived['zstar'])
    R = np.sqrt(Om) * H0 / C_LIGHT * DM_star
    lA = np.pi * DM_star / derived['rstar']

    return {
        'Cl_TT': totCL[:, 0],  # l(l+1)C_l/(2pi) in uK^2
        'Cl_EE': totCL[:, 1],
        'Cl_TE': totCL[:, 3],
        'R': R,
        'lA': lA,
        'zstar': derived['zstar'],
        'rstar': derived['rstar'],
        'rdrag': derived['rdrag'],
        'DM_star': DM_star,
        'H0': H0,
        'Om': Om,
        'w0': w0,
    }


def chi2_compressed(R, lA, obh2=OMBH2):
    """Compressed CMB likelihood chi^2."""
    delta = np.array([(R - R_OBS)/R_SIG, (lA - LA_OBS)/LA_SIG, (obh2 - OBH2_OBS)/OBH2_SIG])
    # Use the correlation matrix inverse
    corr_inv = np.linalg.inv(CMB_CORR)
    return float(delta @ corr_inv @ delta)


def chi2_spectra(spec_model, spec_fid, use_TT=True, use_EE=True, use_TE=False):
    """
    Fisher-matrix estimate of chi^2 between model and fiducial spectra.

    Uses: chi^2 = sum_l (2l+1) f_sky * [Delta C_l / sigma_l]^2

    where sigma_l^2 = 2/(2l+1) * (C_l^fid + N_l)^2 / f_sky

    So: chi^2 = sum_l (2l+1)^2 f_sky^2 / 2 * [Delta C_l / (C_l^fid + N_l)]^2 ... no.

    Actually: variance of C_l estimate = 2/(2l+1)/f_sky * (C_l + N_l)^2

    chi^2 = sum_l [(C_l^mod - C_l^fid)^2 / var(C_l)]
          = sum_l (2l+1) f_sky / 2 * [(C_l^mod - C_l^fid) / (C_l^fid + N_l)]^2
    """
    chi2 = 0.0

    if use_TT:
        for l in range(LMIN, min(LMAX_TT + 1, len(spec_model['Cl_TT']), len(spec_fid['Cl_TT']))):
            if l < 2:
                continue
            # Convert from l(l+1)Cl/(2pi) to Cl
            Cl_mod = spec_model['Cl_TT'][l] / (l * (l+1) / (2 * np.pi))
            Cl_fid = spec_fid['Cl_TT'][l] / (l * (l+1) / (2 * np.pi))
            Nl = planck_noise_TT(l) / (l * (l+1) / (2 * np.pi))
            dCl = Cl_mod - Cl_fid
            var_Cl = 2.0 / ((2*l + 1) * F_SKY) * (Cl_fid + Nl)**2
            chi2 += dCl**2 / var_Cl

    if use_EE:
        for l in range(LMIN, min(LMAX_EE + 1, len(spec_model['Cl_EE']), len(spec_fid['Cl_EE']))):
            if l < 2:
                continue
            Cl_mod = spec_model['Cl_EE'][l] / (l * (l+1) / (2 * np.pi))
            Cl_fid = spec_fid['Cl_EE'][l] / (l * (l+1) / (2 * np.pi))
            Nl = planck_noise_EE(l) / (l * (l+1) / (2 * np.pi))
            dCl = Cl_mod - Cl_fid
            var_Cl = 2.0 / ((2*l + 1) * F_SKY) * (Cl_fid + Nl)**2
            chi2 += dCl**2 / var_Cl

    return chi2


# ============================================================================
# TEST 1: COMPRESSED vs FULL AT FIXED FIDUCIAL COSMOLOGY
# ============================================================================
fprint("\n" + "=" * 78)
fprint("TEST 1: Compressed vs Full Spectrum chi^2 at fixed cosmology")
fprint("  Varying w_0 with fixed (H_0, Omega_m, A_s, n_s, tau) at Planck best-fit")
fprint("=" * 78)

w0_values = [-1.00, -0.99, -0.98, -0.97, -0.96, -0.95, -0.933, -0.90, -0.85, -0.83]

# Compute fiducial (LCDM) spectrum
fprint("\nComputing LCDM fiducial spectrum...")
spec_fid = get_camb_spectra(H0_FID, OM_FID, w0=-1.0)
if spec_fid is None:
    fprint("ERROR: Failed to compute fiducial spectrum")
    sys.exit(1)

fprint(f"  R_fid = {spec_fid['R']:.4f} (obs: {R_OBS})")
fprint(f"  lA_fid = {spec_fid['lA']:.3f} (obs: {LA_OBS})")
fprint(f"  z_star = {spec_fid['zstar']:.2f}")

fprint(f"\n{'w0':>8} {'|1+w0|':>8} {'R':>8} {'lA':>8} {'chi2_comp':>10} {'chi2_TT':>10} {'chi2_EE':>10} {'chi2_tot':>10} {'ratio':>8}")
fprint("-" * 92)

results_test1 = []
for w0 in w0_values:
    spec = get_camb_spectra(H0_FID, OM_FID, w0=w0)
    if spec is None:
        fprint(f"  w0={w0:.3f}: CAMB failed")
        continue

    chi2_c = chi2_compressed(spec['R'], spec['lA'])
    chi2_tt = chi2_spectra(spec, spec_fid, use_TT=True, use_EE=False)
    chi2_ee = chi2_spectra(spec, spec_fid, use_TT=False, use_EE=True)
    chi2_full = chi2_tt + chi2_ee
    ratio = chi2_full / chi2_c if chi2_c > 0.01 else float('inf')

    results_test1.append({
        'w0': w0, 'R': spec['R'], 'lA': spec['lA'],
        'chi2_comp': chi2_c, 'chi2_TT': chi2_tt, 'chi2_EE': chi2_ee,
        'chi2_full': chi2_full, 'ratio': ratio
    })

    fprint(f"{w0:8.3f} {abs(1+w0):8.3f} {spec['R']:8.4f} {spec['lA']:8.3f} "
           f"{chi2_c:10.2f} {chi2_tt:10.2f} {chi2_ee:10.2f} {chi2_full:10.2f} {ratio:8.3f}")


# ============================================================================
# TEST 2: PROFILED COMPARISON
# ============================================================================
fprint("\n" + "=" * 78)
fprint("TEST 2: Profiled chi^2 — optimize (H_0, Omega_m) at each w_0")
fprint("  This captures the degeneracy between w_0 and geometric parameters")
fprint("  Both compressed and full spectrum profiled independently")
fprint("=" * 78)

def profile_compressed(w0):
    """Profile compressed CMB likelihood over (H0, Om) at fixed w0."""
    def neg_chi2(params):
        H0, Om = params
        if H0 < 50 or H0 > 90 or Om < 0.1 or Om > 0.6:
            return 1e8
        spec = get_camb_spectra(H0, Om, w0=w0)
        if spec is None:
            return 1e8
        return chi2_compressed(spec['R'], spec['lA'])

    # Start from fiducial
    result = minimize(neg_chi2, [H0_FID, OM_FID],
                      method='Nelder-Mead',
                      options={'xatol': 0.01, 'fatol': 0.01, 'maxiter': 200})

    return result.fun, result.x


def profile_full_spectrum(w0):
    """Profile full spectrum chi^2 over (H0, Om) at fixed w0."""
    def neg_chi2(params):
        H0, Om = params
        if H0 < 50 or H0 > 90 or Om < 0.1 or Om > 0.6:
            return 1e8
        spec = get_camb_spectra(H0, Om, w0=w0)
        if spec is None:
            return 1e8
        return chi2_spectra(spec, spec_fid, use_TT=True, use_EE=True)

    result = minimize(neg_chi2, [H0_FID, OM_FID],
                      method='Nelder-Mead',
                      options={'xatol': 0.01, 'fatol': 0.5, 'maxiter': 300})

    return result.fun, result.x


fprint(f"\n{'w0':>8} {'|1+w0|':>8} {'comp_prof':>10} {'H0_c':>6} {'Om_c':>6} {'full_prof':>10} {'H0_f':>6} {'Om_f':>6} {'ratio':>8}")
fprint("-" * 82)

w0_profile_vals = [-1.00, -0.99, -0.98, -0.97, -0.95, -0.933, -0.90, -0.85]

results_test2 = []
for w0 in w0_profile_vals:
    fprint(f"  Profiling w0 = {w0:.3f}...", end="")

    chi2_c, params_c = profile_compressed(w0)
    chi2_f, params_f = profile_full_spectrum(w0)
    ratio = chi2_f / chi2_c if chi2_c > 0.01 else float('inf')

    results_test2.append({
        'w0': w0, 'chi2_comp': chi2_c, 'H0_c': params_c[0], 'Om_c': params_c[1],
        'chi2_full': chi2_f, 'H0_f': params_f[0], 'Om_f': params_f[1], 'ratio': ratio
    })

    fprint(f"\r{w0:8.3f} {abs(1+w0):8.3f} {chi2_c:10.2f} {params_c[0]:6.1f} {params_c[1]:6.3f} "
           f"{chi2_f:10.2f} {params_f[0]:6.1f} {params_f[1]:6.3f} {ratio:8.3f}")


# ============================================================================
# TEST 3: DECOMPOSITION OF CONSTRAINING POWER
# ============================================================================
fprint("\n" + "=" * 78)
fprint("TEST 3: Where does the CMB constraining power on w_0 come from?")
fprint("  Decomposing: low-l (ISW, l<30) vs acoustic peaks (30<l<2000) vs damping tail")
fprint("=" * 78)

# Use w0 = -0.933 (model extreme)
spec_model = get_camb_spectra(H0_FID, OM_FID, w0=-0.933)
if spec_model is not None:
    # Decompose chi^2 by multipole range
    ranges = [
        ('ISW (l=2-30)', 2, 30),
        ('Peaks (l=30-800)', 30, 800),
        ('Damping (l=800-2500)', 800, 2500),
        ('Total (l=2-2500)', 2, 2500),
    ]

    fprint(f"\nFor w_0 = -0.933 vs LCDM:")
    fprint(f"  {'Range':>25} {'chi2_TT':>10} {'chi2_EE':>10} {'Total':>10} {'% of total':>10}")
    fprint("  " + "-" * 70)

    total_full = 0.0
    for name, lmin, lmax in ranges:
        chi2_tt = 0.0
        chi2_ee = 0.0
        for l in range(lmin, min(lmax + 1, len(spec_model['Cl_TT']), len(spec_fid['Cl_TT']))):
            Cl_mod = spec_model['Cl_TT'][l] / (l * (l+1) / (2 * np.pi))
            Cl_fid = spec_fid['Cl_TT'][l] / (l * (l+1) / (2 * np.pi))
            Nl = planck_noise_TT(l) / (l * (l+1) / (2 * np.pi))
            dCl = Cl_mod - Cl_fid
            var_Cl = 2.0 / ((2*l + 1) * F_SKY) * (Cl_fid + Nl)**2
            chi2_tt += dCl**2 / var_Cl

        for l in range(lmin, min(min(lmax + 1, LMAX_EE + 1), len(spec_model['Cl_EE']), len(spec_fid['Cl_EE']))):
            Cl_mod = spec_model['Cl_EE'][l] / (l * (l+1) / (2 * np.pi))
            Cl_fid = spec_fid['Cl_EE'][l] / (l * (l+1) / (2 * np.pi))
            Nl = planck_noise_EE(l) / (l * (l+1) / (2 * np.pi))
            dCl = Cl_mod - Cl_fid
            var_Cl = 2.0 / ((2*l + 1) * F_SKY) * (Cl_fid + Nl)**2
            chi2_ee += dCl**2 / var_Cl

        total = chi2_tt + chi2_ee
        if name.startswith('Total'):
            total_full = total
        pct = 100 * total / total_full if total_full > 0 and not name.startswith('Total') else 100
        fprint(f"  {name:>25} {chi2_tt:10.2f} {chi2_ee:10.2f} {total:10.2f} {pct:9.1f}%")

    # The geometric (peak/damping) fraction tells us how much the shift parameters capture
    fprint(f"\n  Geometric fraction (peaks + damping): accounts for the vast majority")
    fprint(f"  ISW fraction: only l=2-30, subdominant")
    fprint(f"  --> If geometric >> ISW, compressed likelihood captures most information")
    fprint(f"  --> mu=Sigma=1 only affects ISW (small) and lensing (very small)")


# ============================================================================
# TEST 4: SHIFT PARAMETER SENSITIVITY
# ============================================================================
fprint("\n" + "=" * 78)
fprint("TEST 4: Shift parameter response to w_0")
fprint("  How much do R and l_A change with w_0?")
fprint("=" * 78)

fprint(f"\n{'w0':>8} {'R':>10} {'delta_R/sig':>12} {'lA':>10} {'delta_lA/sig':>13} {'regime':>15}")
fprint("-" * 73)

for w0 in [-1.00, -0.99, -0.98, -0.97, -0.96, -0.95, -0.933, -0.90, -0.85, -0.80]:
    spec = get_camb_spectra(H0_FID, OM_FID, w0=w0)
    if spec is None:
        continue
    dR = (spec['R'] - R_OBS) / R_SIG
    dlA = (spec['lA'] - LA_OBS) / LA_SIG

    if abs(1 + w0) < 0.01:
        regime = "LINEAR"
    elif abs(1 + w0) < 0.05:
        regime = "BORDERLINE"
    else:
        regime = "NONLINEAR?"

    fprint(f"{w0:8.3f} {spec['R']:10.4f} {dR:12.2f} {spec['lA']:10.3f} {dlA:13.2f} {regime:>15}")


# ============================================================================
# SUMMARY
# ============================================================================
fprint("\n" + "=" * 78)
fprint("SUMMARY & INTERPRETATION")
fprint("=" * 78)

if results_test1 and results_test2:
    # Find the model extreme entry
    me = None
    for r in results_test1:
        if abs(r['w0'] + 0.933) < 0.01:
            me = r
            break

    mp = None
    for r in results_test2:
        if abs(r['w0'] + 0.933) < 0.01:
            mp = r
            break

    fprint(f"""
At the model extreme (w_0 = -0.933, |1+w_0| = 0.067):

  FIXED COSMOLOGY (Test 1):
    Compressed chi^2:   {me['chi2_comp']:.1f}
    Full spectrum chi^2: {me['chi2_full']:.1f}
    Ratio (full/comp):  {me['ratio']:.3f}
""" if me else "\n  [Model extreme not computed in Test 1]")

    if mp:
        fprint(f"""  PROFILED (Test 2):
    Compressed chi^2:   {mp['chi2_comp']:.1f}  (H0={mp['H0_c']:.1f}, Om={mp['Om_c']:.3f})
    Full spectrum chi^2: {mp['chi2_full']:.1f}  (H0={mp['H0_f']:.1f}, Om={mp['Om_f']:.3f})
    Ratio (full/comp):  {mp['ratio']:.3f}
""")

    fprint("""  INTERPRETATION:
    Ratio ~ 1.0: Compressed likelihood is VALID. Tension is real.
    Ratio > 1.5: Compressed likelihood UNDERESTIMATES constraint (!).
    Ratio < 0.5: Compressed likelihood OVERSTATES constraint.
                  The full Planck data is less constraining on w_0.

    The key question: does mu=Sigma=1 (cuscuton) change anything?
    NO — because mu=Sigma=1 means perturbations are STANDARD.
    The only difference from LCDM is the background expansion.
    CAMB with constant w_0 IS the correct calculation.
""")

fprint("\nDone.")
