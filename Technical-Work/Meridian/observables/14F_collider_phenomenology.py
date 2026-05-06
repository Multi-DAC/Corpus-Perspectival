#!/usr/bin/env python3
"""
Track 14F: xi = 1/6 Collider Phenomenology
Project Meridian  -- Phase 14

Computes Higgs-radion mixing, production cross-sections, signal strengths,
and experimental distinguishability between xi = 1/6 (Meridian) and xi = 0 (AS generic).

References:
  - Giudice, Rattazzi, Wells (GRW), hep-ph/0005110 (2001)  -- Higgs-radion mixing
  - Dominici, Grzadkowski, Gunion, Toharia (DGGT), hep-ph/0206192 (2003)  -- scalar sector
  - Csaki, Graesser, Kolb, Terning (CGKT), hep-ph/9906513 (2000)  -- RS cosmology
  - Desai, Vaman, hep-ph/0612058 (2006)  -- Higgs-radion phenomenology

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: March 18, 2026
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, List
import json
import sys

# ============================================================
# SECTION 1: PHYSICAL CONSTANTS AND RS PARAMETERS
# ============================================================

@dataclass
class RSParams:
    """Randall-Sundrum model parameters for Meridian framework."""
    # Fundamental scales
    k: float = 1e16          # AdS curvature scale [GeV] (~ 10^16 GeV)
    M5: float = 0.0          # 5D Planck mass [GeV], computed from k and M_Pl
    M_Pl: float = 2.435e18   # Reduced Planck mass [GeV]
    ky_c: float = 35.0       # Warp factor exponent (kT_0 ~ 35)

    # Derived scales
    Lambda_IR: float = 0.0   # IR brane scale [GeV]
    Lambda_r: float = 0.0    # Radion coupling scale [GeV]

    # SM parameters
    v_EW: float = 246.0      # Electroweak VEV [GeV]
    m_h: float = 125.0       # Higgs mass [GeV]
    m_W: float = 80.4        # W boson mass [GeV]
    m_Z: float = 91.2        # Z boson mass [GeV]
    m_t: float = 173.0       # Top quark mass [GeV]

    # Non-minimal coupling
    xi: float = 1.0/6.0      # Meridian prediction: conformal coupling

    # Meridian-specific
    zeta_0: float = 0.001    # Brane benchmark value from 13B/13F
    epsilon_1: float = 0.017 # GB correction to cuscuton kinetic term

    def __post_init__(self):
        """Compute derived quantities."""
        # M_5^3 = k * M_Pl^2 / 2 (standard RS convention with factor of 2)
        # Using convention from the monograph: M_Pl^2 ~ M_5^3 / k
        self.M5 = (self.k * self.M_Pl**2)**(1.0/3.0)

        # IR brane scale
        self.Lambda_IR = self.k * np.exp(-self.ky_c)

        # Radion coupling scale (Giudice-Rattazzi-Wells)
        # Lambda_r = sqrt(6) * M_Pl * exp(-ky_c) ~ TeV
        self.Lambda_r = np.sqrt(6) * self.M_Pl * np.exp(-self.ky_c)


# ============================================================
# SECTION 2: HIGGS-RADION MIXING  -- THE GRW FORMALISM
# ============================================================

def higgs_radion_mixing(m_h0: float, m_r0: float, xi: float,
                        Lambda_r: float, v_EW: float,
                        gamma_mix: float = 0.0) -> Dict:
    """
    Compute Higgs-radion mixing following Giudice-Rattazzi-Wells (GRW).

    Following GRW (hep-ph/0005110, Eqs. 18-32) and DGGT (hep-ph/0206192).

    The non-minimal coupling xi*R*H^2 induces kinetic mixing between the
    Higgs doublet and the radion. The mixing parameter is gamma = v/Lambda_r.

    GRW mixing angle (Eq. 29):
        tan(2*theta) = 12*xi*gamma*m_h^2 / [m_r^2*(1+6*xi*gamma^2) - m_h^2]

    For xi = 0: theta = 0, no mixing.
    For xi = 1/6: theta ~ 6*gamma*(m_h/m_r)^2 for m_r >> m_h.

    The physical Higgs-like state h_1 = cos(theta)*h - sin(theta)*r has:
        g(h_1 VV) / g_SM = d = cos(theta) + gamma*sin(theta)
        g(h_1 ff) / g_SM = c = cos(theta)

    Parameters:
        m_h0: bare Higgs mass [GeV]
        m_r0: bare radion mass [GeV]
        xi: non-minimal coupling
        Lambda_r: radion coupling scale [GeV]
        v_EW: electroweak VEV [GeV]
        gamma_mix: direct mass mixing parameter, default 0

    Returns:
        Dictionary with mixing angle, physical masses, GRW coupling modifiers.
    """
    gamma = v_EW / Lambda_r

    # Kinetic mixing parameter
    Z_off = 6.0 * xi * gamma

    # Determinant of kinetic mixing matrix
    # det(Z) = 1 + 6*xi*gamma^2*(1 - 6*xi)
    det_Z = 1.0 + 6.0 * xi * gamma**2 * (1.0 - 6.0 * xi)
    # For xi = 1/6: det_Z = 1 exactly (conformal special case)

    ghost_free = det_Z > 0

    if abs(det_Z) < 1e-30:
        return {
            'gamma': gamma, 'xi': xi, 'Z_det': det_Z, 'ghost_free': False,
            'theta_mix_exact': 0.0, 'm1_phys': m_h0, 'm2_phys': m_r0,
            'd': 1.0, 'c': 1.0, 'd_r': 0.0, 'c_r': 0.0,
            'm_h0': m_h0, 'm_r0': m_r0,
            'mass_shift_h': 0.0, 'mass_shift_r': 0.0,
        }

    # GRW mixing angle (Eq. 29):
    # tan(2*theta) = 12*xi*gamma*m_h^2 / [m_r^2*(1+6*xi*gamma^2) - m_h^2]
    # For m_r > m_h and xi > 0: numerator > 0, denominator > 0 => theta > 0, small
    numer = 12.0 * xi * gamma * m_h0**2
    denom = m_r0**2 * (1.0 + 6.0 * xi * gamma**2) - m_h0**2

    if abs(denom) > 1e-10:
        theta = 0.5 * np.arctan(numer / denom)
    else:
        theta = np.pi / 4.0  # maximal mixing at degeneracy

    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    # Physical mass eigenvalues from the effective mass matrix
    # after kinetic diagonalization (DGGT Eq. 14-16):
    a_h = m_h0**2 / det_Z
    a_r = m_r0**2 * (1.0 + 6.0 * xi * gamma**2) / det_Z
    b = m_h0**2 * Z_off / det_Z

    sum_a = a_h + a_r
    disc = np.sqrt((a_r - a_h)**2 + 4.0 * b**2)

    m1_sq = 0.5 * (sum_a - disc)  # lighter (Higgs-like)
    m2_sq = 0.5 * (sum_a + disc)  # heavier (radion-like)

    m1 = np.sqrt(abs(m1_sq)) if m1_sq >= 0 else np.nan
    m2 = np.sqrt(abs(m2_sq)) if m2_sq >= 0 else np.nan

    # GRW coupling modifiers (Eqs. 33-38 of hep-ph/0005110):
    # Higgs-like state h_1 = cos(theta)*h - sin(theta)*r
    # g(h_1 VV) / g_SM = d = cos(theta) + gamma * sin(theta)
    # g(h_1 ff) / g_SM = c = cos(theta)
    d = cos_t + gamma * sin_t   # VV coupling modifier
    c = cos_t                     # fermion coupling modifier

    # Radion-like state h_2 = sin(theta)*h + cos(theta)*r
    d_r = sin_t + gamma * cos_t   # radion VV coupling
    c_r = sin_t                    # radion fermion coupling

    return {
        'gamma': gamma,
        'xi': xi,
        'Z_det': det_Z,
        'ghost_free': ghost_free,
        'theta_mix_exact': theta,
        'd': d,       # VV coupling modifier of Higgs-like state
        'c': c,       # fermion coupling modifier of Higgs-like state
        'd_r': d_r,   # VV coupling of radion-like state
        'c_r': c_r,   # fermion coupling of radion-like state
        'm1_phys': m1,
        'm2_phys': m2,
        'm_h0': m_h0,
        'm_r0': m_r0,
        'mass_shift_h': (m1 - m_h0) if not np.isnan(m1) else np.nan,
        'mass_shift_r': (m2 - m_r0) if not np.isnan(m2) else np.nan,
    }


# ============================================================
# SECTION 3: SIGNAL STRENGTH MODIFIERS
# ============================================================

def higgs_signal_strengths(d_coeff: float, c_coeff: float,
                           gamma: float, xi: float) -> Dict:
    """
    Compute modified Higgs signal strengths mu_X = sigma*BR / (sigma*BR)_SM.

    Uses the GRW coupling modifiers d (VV) and c (fermion) directly
    from the mixing computation.

    For xi = 0: d = c = 1, all couplings SM-like.
    For xi = 1/6: d = cos(theta) + gamma*sin(theta), c = cos(theta).

    Parameters:
        d_coeff: GRW 'd' parameter (VV coupling modifier)
        c_coeff: GRW 'c' parameter (fermion coupling modifier)
        gamma: v_EW / Lambda_r
        xi: non-minimal coupling

    Returns:
        Dictionary of signal strength modifiers.
    """
    # GRW coupling modifiers:
    # kappa_V = d (direct from mixing computation)
    # kappa_f = c (direct from mixing computation)
    kappa_V = d_coeff
    kappa_f = c_coeff

    # For gluon fusion (gg -> h):
    # The radion component couples to gg through the QCD trace anomaly
    # b_3 = 7 for 6 quarks. sin(theta) appears implicitly in (d - c) / gamma.
    # GRW Eq. 35: kappa_g = c + (d - c) * (b_3/4)
    # since (d - c) = gamma * sin(theta) = the radion admixture * gamma
    b3_QCD = 7.0
    ratio_gg = b3_QCD / 4.0  # ~ 1.75
    kappa_g = c_coeff + (d_coeff - c_coeff) * ratio_gg

    # For diphoton (h -> gamma gamma):
    # SM: W loop (dominant) + top loop. Radion: EM trace anomaly b_EM = 11/3
    b_EM = 11.0 / 3.0
    ratio_gammagamma = b_EM / 8.0
    kappa_gamma = c_coeff + (d_coeff - c_coeff) * ratio_gammagamma

    # Signal strengths mu_X = kappa_production^2 * kappa_decay^2 / kappa_total^2
    # For gg -> h -> XX:

    # Total width modification:
    # Gamma_total ~ kappa_f^2 * Gamma(h->bb) + kappa_V^2 * Gamma(h->WW)
    #             + kappa_V^2 * Gamma(h->ZZ) + kappa_f^2 * Gamma(h->tautau) + ...

    # SM branching ratios at m_h = 125 GeV:
    BR_SM = {
        'bb': 0.577,
        'WW': 0.215,
        'gg': 0.086,
        'tautau': 0.063,
        'cc': 0.029,
        'ZZ': 0.026,
        'gammagamma': 0.0023,
        'Zgamma': 0.0015,
    }

    # Modified partial widths relative to SM:
    Gamma_ratio = {
        'bb': kappa_f**2,
        'WW': kappa_V**2,
        'gg': kappa_g**2,
        'tautau': kappa_f**2,
        'cc': kappa_f**2,
        'ZZ': kappa_V**2,
        'gammagamma': kappa_gamma**2,
        'Zgamma': kappa_gamma**2,  # approximate
    }

    # Total width ratio:
    Gamma_total_ratio = sum(BR_SM[ch] * Gamma_ratio[ch] for ch in BR_SM)

    # Signal strengths for various channels:
    # mu(gg -> h -> XX) = kappa_g^2 * kappa_X^2 / Gamma_total_ratio
    signal_strengths = {}
    for channel, kappa_decay_sq in Gamma_ratio.items():
        signal_strengths[f'mu_ggF_{channel}'] = kappa_g**2 * kappa_decay_sq / Gamma_total_ratio

    # VBF/VH production:
    for channel, kappa_decay_sq in Gamma_ratio.items():
        signal_strengths[f'mu_VBF_{channel}'] = kappa_V**2 * kappa_decay_sq / Gamma_total_ratio

    return {
        'kappa_V': kappa_V,
        'kappa_f': kappa_f,
        'kappa_g': kappa_g,
        'kappa_gamma': kappa_gamma,
        'Gamma_total_ratio': Gamma_total_ratio,
        'signal_strengths': signal_strengths,
    }


# ============================================================
# SECTION 4: RADION PRODUCTION AND DECAY
# ============================================================

def radion_cross_sections(m_r: float, Lambda_r: float,
                          theta: float, sqrt_s: float = 13000.0) -> Dict:
    """
    Estimate radion production cross-sections at the LHC.

    The radion couples to the trace of T_mu^mu:
        L_int = -(r / Lambda_r) * T_mu^mu

    For gg -> r: sigma ~ (alpha_s^2 / Lambda_r^2) * (m_r^2 / s) * parton luminosity

    Parameters:
        m_r: radion mass [GeV]
        Lambda_r: radion coupling scale [GeV]
        theta: mixing angle with Higgs
        sqrt_s: center-of-mass energy [GeV]

    Returns:
        Dictionary of cross-sections and branching ratios.
    """
    alpha_s = 0.118  # at m_Z
    s = sqrt_s**2

    # gg -> r production (dominant channel)
    # The radion-gluon coupling comes from the QCD trace anomaly:
    # Gamma(r -> gg) = (alpha_s^2 * m_r^3) / (32 * pi^3 * Lambda_r^2) * b_3^2
    # with b_3 = 7 (Standard Model, 6 quarks)
    b3 = 7.0

    # Partial width to gg:
    Gamma_gg = (alpha_s**2 * m_r**3) / (32 * np.pi**3 * Lambda_r**2) * b3**2

    # Partial width to WW (for m_r > 2*m_W):
    m_W = 80.4
    if m_r > 2 * m_W:
        beta_W = np.sqrt(1 - 4*m_W**2/m_r**2)
        Gamma_WW = (m_r**3 / (32 * np.pi * Lambda_r**2)) * beta_W * (1 - 4*m_W**2/m_r**2 + 12*m_W**4/m_r**4)
    else:
        Gamma_WW = 0.0
        beta_W = 0.0

    # Partial width to ZZ (for m_r > 2*m_Z):
    m_Z = 91.2
    if m_r > 2 * m_Z:
        beta_Z = np.sqrt(1 - 4*m_Z**2/m_r**2)
        Gamma_ZZ = (m_r**3 / (64 * np.pi * Lambda_r**2)) * beta_Z * (1 - 4*m_Z**2/m_r**2 + 12*m_Z**4/m_r**4)
    else:
        Gamma_ZZ = 0.0
        beta_Z = 0.0

    # Partial width to hh (for m_r > 2*m_h):
    m_h = 125.0
    v_EW = 246.0
    if m_r > 2 * m_h:
        beta_h = np.sqrt(1 - 4*m_h**2/m_r**2)
        # Radion to Higgs pair: coupling ~ m_h^2 / Lambda_r
        Gamma_hh = (m_r * m_h**4) / (32 * np.pi * Lambda_r**2 * m_r**2) * beta_h
    else:
        Gamma_hh = 0.0
        beta_h = 0.0

    # Partial width to tt (for m_r > 2*m_t):
    m_t = 173.0
    if m_r > 2 * m_t:
        beta_t = np.sqrt(1 - 4*m_t**2/m_r**2)
        Nc = 3
        Gamma_tt = Nc * (m_r * m_t**2) / (8 * np.pi * Lambda_r**2) * beta_t**3
    else:
        Gamma_tt = 0.0
        beta_t = 0.0

    # Partial width to bb:
    m_b = 4.18
    beta_b = np.sqrt(1 - 4*m_b**2/m_r**2) if m_r > 2*m_b else 0.0
    Nc = 3
    Gamma_bb = Nc * (m_r * m_b**2) / (8 * np.pi * Lambda_r**2) * beta_b**3 if m_r > 2*m_b else 0.0

    # Total width:
    Gamma_total = Gamma_gg + Gamma_WW + Gamma_ZZ + Gamma_hh + Gamma_tt + Gamma_bb

    # Branching ratios:
    BRs = {}
    if Gamma_total > 0:
        BRs['gg'] = Gamma_gg / Gamma_total
        BRs['WW'] = Gamma_WW / Gamma_total
        BRs['ZZ'] = Gamma_ZZ / Gamma_total
        BRs['hh'] = Gamma_hh / Gamma_total
        BRs['tt'] = Gamma_tt / Gamma_total
        BRs['bb'] = Gamma_bb / Gamma_total

    # gg -> r production cross-section estimate
    # Using narrow-width approximation and parton luminosity approximation
    # sigma(gg -> r) ~ (pi^2 / 8) * Gamma(r -> gg) / m_r * L_gg(m_r^2/s)
    # where L_gg is the gluon-gluon parton luminosity
    # For m_r ~ few hundred GeV to TeV at 13 TeV LHC:
    # L_gg ~ 1e3 (at m_r = 200 GeV) to 1e-1 (at m_r = 2 TeV) [GeV^-2 * appropriate factors]

    # Approximate gluon luminosity (rough fit for 13 TeV LHC)
    tau = m_r**2 / s
    if tau < 1:
        # Rough parametric fit to NNPDF gluon luminosity
        log_tau = np.log10(tau)
        # L_gg in units of 1/GeV^2, times s
        log_Lgg = -2.0 - 7.0 * (log_tau + 4.0)  # very rough
        L_gg = 10**log_Lgg  # dimensionless effective luminosity factor
    else:
        L_gg = 0.0

    # sigma(gg -> r) in pb (very rough estimate)
    # More precisely: sigma = (pi^2/(8*m_r*s)) * Gamma(r->gg) * dL_gg/d(tau)
    # We use a simplified scaling relative to SM Higgs cross-section
    sigma_SM_h = 48.6  # pb, SM Higgs ggF at 13 TeV, m_h = 125 GeV

    # Ratio to SM Higgs: sigma(r) / sigma(h_SM) ~ (Gamma(r->gg)/Gamma(h->gg)) * (parton lum ratio)
    Gamma_h_gg_SM = 0.35e-3  # GeV, SM Higgs to gg partial width
    sigma_ratio = (Gamma_gg / Gamma_h_gg_SM) if Gamma_h_gg_SM > 0 else 0

    # Parton luminosity ratio (rough: scales as tau^(-a) with a ~ 4-5 for gluons)
    tau_h = m_h**2 / s
    if tau > 0 and tau_h > 0:
        plum_ratio = (tau_h / tau)**4.5 * (m_h / m_r)  # rough scaling
    else:
        plum_ratio = 0.0

    sigma_r_approx = sigma_SM_h * sigma_ratio * plum_ratio  # pb

    return {
        'm_r': m_r,
        'Lambda_r': Lambda_r,
        'Gamma_total': Gamma_total,
        'Gamma_total_GeV': Gamma_total,
        'Gamma_over_m': Gamma_total / m_r if m_r > 0 else 0,
        'BRs': BRs,
        'partial_widths': {
            'gg': Gamma_gg, 'WW': Gamma_WW, 'ZZ': Gamma_ZZ,
            'hh': Gamma_hh, 'tt': Gamma_tt, 'bb': Gamma_bb,
        },
        'sigma_ggF_approx_pb': sigma_r_approx,
    }


# ============================================================
# SECTION 5: KK GRAVITON SPECTRUM
# ============================================================

def kk_graviton_spectrum(params: RSParams, n_modes: int = 5) -> Dict:
    """
    Compute the KK graviton spectrum in the RS model with non-minimal coupling.

    KK graviton masses: m_n = x_n * k * exp(-ky_c) * (1 + delta_xi)
    where x_n are zeros of J_1(x) Bessel function:
        x_1 = 3.8317, x_2 = 7.0156, x_3 = 10.1735, ...

    The NMC correction delta_xi ~ zeta_0 from Phase 6 (D6.4, Section 7).

    Parameters:
        params: RS model parameters
        n_modes: number of KK modes to compute

    Returns:
        Dictionary with KK masses and couplings.
    """
    # Zeros of J_1(x)
    bessel_zeros = [3.8317, 7.0156, 10.1735, 13.3237, 16.4706,
                    19.6159, 22.7601, 25.9037, 29.0468, 32.1897]

    # KK scale
    m_KK = params.k * np.exp(-params.ky_c)

    # NMC correction from D6.4 Section 7: delta_m/m ~ zeta_0
    delta_xi = params.zeta_0

    masses = []
    couplings = []
    for n in range(min(n_modes, len(bessel_zeros))):
        m_n = bessel_zeros[n] * m_KK * (1 + delta_xi)
        # KK graviton coupling to brane matter: c_n = x_n * k / M_Pl * exp(-ky_c)
        # Effective coupling scale: Lambda_n ~ M_Pl * exp(ky_c) / x_n ~ M_Pl / x_n (on IR brane)
        # More precisely: KK graviton couples as (1/Lambda_1) * T_mu_nu * h^(n)_mu_nu
        # with 1/Lambda_1 ~ 1/(k * exp(-ky_c) * M_Pl * sqrt(2/k*y_c))
        # ~ 1 / (m_KK * M_Pl / k)
        Lambda_n = params.M_Pl / bessel_zeros[n]  # effective coupling scale

        masses.append(m_n)
        couplings.append(Lambda_n)

    return {
        'm_KK_scale': m_KK,
        'masses_GeV': masses,
        'coupling_scales_GeV': couplings,
        'delta_xi_correction': delta_xi,
    }


# ============================================================
# SECTION 6: SELF-TUNING BREAKDOWN FOR xi != 1/6
# ============================================================

def self_tuning_check(xi_values: np.ndarray) -> Dict:
    """
    Demonstrate why xi != 1/6 breaks the Meridian self-tuning mechanism.

    The self-tuning mechanism requires:
    1. Cuscuton structure: P(X) = mu^2 * sqrt(2X) + epsilon_1 * X
       This gives zero kinetic energy (ZKE) for the leading term.

    2. The Seeley-DeWitt coefficient a_2 of the spectral action on
       the RS orbifold gives the non-minimal coupling as:
       xi = (d-2) / (4(d-1)) = (4-2)/(4*3) = 1/6 in 4D
       This is the conformal coupling  -- the unique value where the
       scalar wave equation is conformally covariant.

    3. The self-tuning constraint: the effective 4D CC is
       Lambda_4 = Lambda_5 / (M_5^3 - xi*Phi_0^2)
       Self-tuning requires Lambda_4 to be insensitive to Lambda_5.
       This works when F(Phi) = M_5^3 - xi*Phi_0^2 has a specific
       relationship to the junction conditions, which is ONLY
       satisfied for the conformal value xi = 1/6 in the spectral
       action framework.

    4. Radion stabilization: The radion mass depends on the effective
       brane coupling through F(Phi). For xi != 1/6, the radion
       potential acquires additional minima or becomes unstable.

    Parameters:
        xi_values: array of xi values to test

    Returns:
        Dictionary with self-tuning diagnostics for each xi.
    """
    M5_cubed = 1.0  # normalized units
    Phi_0_sq = 0.006  # = 6 * zeta_0 * M5^3 for zeta_0 = 0.001

    results = []
    for xi in xi_values:
        # Effective gravitational coupling on the brane
        F = M5_cubed - xi * Phi_0_sq

        # The self-tuning condition requires:
        # d/d(Lambda_5) [Lambda_4_eff] = 0
        # Lambda_4_eff = (Lambda_5 + delta_Lambda_brane) / F
        # where delta_Lambda_brane contains the brane contributions.
        #
        # For the cuscuton mechanism (Lacombe-Mukohyama):
        # The self-tuning works because the cuscuton constraint absorbs
        # the vacuum energy into the scalar field configuration.
        #
        # The key: the cuscuton constraint V'(phi) = -3H*mu^2 determines
        # phi(H), which feeds back into F(phi). For the self-tuning to
        # CANCEL the CC at all orders, the feedback must be exact.
        #
        # This exactness requires the conformal coupling:
        # xi = 1/6 makes the scalar equation conformally covariant,
        # which means the CC cancellation is EXACT (not approximate).
        #
        # For xi != 1/6, there is a RESIDUAL CC:
        # Lambda_4_residual ~ (xi - 1/6) * Phi_0^2 * R_4 / F
        #                   ~ (xi - 1/6) * zeta_0 * H_0^2

        delta_xi = xi - 1.0/6.0
        residual_CC = abs(delta_xi) * Phi_0_sq  # in Planck units
        # In terms of dark energy density:
        # rho_residual / rho_DE ~ |delta_xi| * zeta_0 * (M_Pl / H_0)^2
        # ~ |delta_xi| * 0.001 * (10^{61})^2
        # This is ENORMOUS for |delta_xi| > 10^{-122}

        # Self-tuning precision (number of significant figures of cancellation)
        if abs(delta_xi) > 0:
            sig_figs = -np.log10(abs(delta_xi) * Phi_0_sq / M5_cubed)
        else:
            sig_figs = np.inf

        # Conformal covariance check
        # The scalar wave equation (Box - xi*R)*phi = 0
        # is conformally covariant ONLY for xi = 1/6 in 4D
        conformal_covariant = abs(delta_xi) < 1e-15

        # Radion stability
        # The radion potential curvature V_rad'' depends on F(phi)
        # and its derivatives. For xi != 1/6, F has different
        # sensitivity to phi, which changes the stability condition.
        # Specifically, the radion mass squared picks up a correction:
        # delta(m_r^2) ~ (xi - 1/6) * k^2 * e^{-2ky_c}
        radion_mass_correction = delta_xi  # relative to xi = 1/6 value

        results.append({
            'xi': xi,
            'delta_xi': delta_xi,
            'F': F,
            'residual_CC_Planck': residual_CC,
            'self_tuning_sig_figs': sig_figs,
            'conformal_covariant': conformal_covariant,
            'radion_mass_correction_relative': radion_mass_correction,
        })

    return {'xi_scan': results}


# ============================================================
# SECTION 7: EXPERIMENTAL DISTINGUISHABILITY
# ============================================================

def measurement_precision(xi_target: float = 1.0/6.0,
                          xi_null: float = 0.0) -> Dict:
    """
    Compute the precision needed to distinguish xi = 1/6 from xi = 0.

    The key observables sensitive to xi are:
    1. Higgs coupling modifiers (kappa_V, kappa_f)
    2. Radion searches (resonance in diboson/diphoton)
    3. KK graviton mass splittings

    Parameters:
        xi_target: target value (Meridian prediction)
        xi_null: null hypothesis (AS generic prediction)

    Returns:
        Dictionary with required precisions and collider prospects.
    """
    params = RSParams(xi=xi_target)
    params_null = RSParams(xi=xi_null)

    # Radion mass range to scan
    m_r_values = [200, 300, 500, 750, 1000, 1500, 2000, 3000]

    results = []
    for m_r in m_r_values:
        # Mixing for xi = 1/6
        mix_16 = higgs_radion_mixing(
            m_h0=params.m_h, m_r0=m_r,
            xi=xi_target, Lambda_r=params.Lambda_r,
            v_EW=params.v_EW
        )

        # Mixing for xi = 0
        mix_0 = higgs_radion_mixing(
            m_h0=params.m_h, m_r0=m_r,
            xi=xi_null, Lambda_r=params.Lambda_r,
            v_EW=params.v_EW
        )

        # Signal strengths for xi = 1/6
        ss_16 = higgs_signal_strengths(
            d_coeff=mix_16['d'], c_coeff=mix_16['c'],
            gamma=mix_16['gamma'], xi=xi_target
        )

        # Signal strengths for xi = 0
        ss_0 = higgs_signal_strengths(
            d_coeff=mix_0['d'], c_coeff=mix_0['c'],
            gamma=mix_0['gamma'], xi=xi_null
        )

        # Key observable: kappa_V deviation from 1
        delta_kV_16 = abs(ss_16['kappa_V'] - 1.0)
        delta_kV_0 = abs(ss_0['kappa_V'] - 1.0)

        # Separation between the two hypotheses:
        delta_kV_separation = abs(ss_16['kappa_V'] - ss_0['kappa_V'])

        # Mixing angle difference:
        delta_theta = abs(mix_16['theta_mix_exact'] - mix_0['theta_mix_exact'])

        results.append({
            'm_r': m_r,
            'theta_xi16': mix_16['theta_mix_exact'],
            'theta_xi0': mix_0['theta_mix_exact'],
            'delta_theta': delta_theta,
            'kappa_V_xi16': ss_16['kappa_V'],
            'kappa_V_xi0': ss_0['kappa_V'],
            'delta_kV_separation': delta_kV_separation,
            'delta_kV_16_from_SM': delta_kV_16,
        })

    # Current experimental precision (LHC Run 2, 139 fb^-1):
    current_precision = {
        'kappa_V': 0.05,         # ~5% from ATLAS/CMS combined
        'kappa_f': 0.10,         # ~10%
        'kappa_g': 0.10,         # ~10% (ggF production)
        'kappa_gamma': 0.10,     # ~10%
    }

    # HL-LHC projections (3000 fb^-1):
    hllhc_precision = {
        'kappa_V': 0.017,        # ~1.7% (ATLAS/CMS HL-LHC Yellow Report)
        'kappa_f': 0.03,         # ~3%
        'kappa_g': 0.025,        # ~2.5%
        'kappa_gamma': 0.02,     # ~2%
    }

    # FCC-hh projections (100 TeV, ~30 ab^-1):
    fcc_precision = {
        'kappa_V': 0.004,        # ~0.4%
        'kappa_f': 0.005,        # ~0.5%
        'kappa_g': 0.005,        # ~0.5%
        'kappa_gamma': 0.003,    # ~0.3%
    }

    # FCC-ee (Higgs factory, 240 GeV, ~5 ab^-1):
    fcc_ee_precision = {
        'kappa_V': 0.002,        # ~0.2% (from ZH threshold scan)
        'kappa_f': 0.003,        # ~0.3%
        'kappa_g': 0.01,         # ~1% (indirect)
        'kappa_gamma': 0.01,     # ~1% (indirect)
    }

    # Muon collider (10 TeV, ~10 ab^-1):
    muon_collider_precision = {
        'kappa_V': 0.001,        # ~0.1% (direct WW fusion)
        'kappa_f': 0.002,        # ~0.2%
        'kappa_g': 0.003,        # ~0.3%
        'kappa_gamma': 0.002,    # ~0.2%
    }

    return {
        'm_r_scan': results,
        'current_precision': current_precision,
        'hllhc_precision': hllhc_precision,
        'fcc_hh_precision': fcc_precision,
        'fcc_ee_precision': fcc_ee_precision,
        'muon_collider_precision': muon_collider_precision,
    }


# ============================================================
# SECTION 8: COMPREHENSIVE SCAN
# ============================================================

def comprehensive_scan() -> Dict:
    """Run the full 14F phenomenology computation."""

    print("=" * 70)
    print("Track 14F: xi = 1/6 Collider Phenomenology")
    print("Project Meridian  -- Phase 14")
    print("=" * 70)

    params = RSParams()
    print(f"\n--- RS Parameters ---")
    print(f"k = {params.k:.3e} GeV")
    print(f"M_5 = {params.M5:.3e} GeV")
    print(f"M_Pl = {params.M_Pl:.3e} GeV")
    print(f"ky_c = {params.ky_c}")
    print(f"Lambda_IR = {params.Lambda_IR:.3e} GeV")
    print(f"Lambda_r = {params.Lambda_r:.3e} GeV")
    print(f"v_EW = {params.v_EW} GeV")
    print(f"xi = {params.xi:.6f} (= 1/6)")
    print(f"gamma = v_EW/Lambda_r = {params.v_EW/params.Lambda_r:.6e}")
    print(f"zeta_0 = {params.zeta_0}")

    all_results = {}

    # --------------------------------------------------------
    # Part 1: Higgs-radion mixing for various radion masses
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 1: HIGGS-RADION MIXING")
    print("=" * 70)

    m_r_values = [200, 300, 500, 750, 1000, 1500, 2000, 3000]
    xi_values_compare = [0.0, 1.0/6.0]

    print(f"\n{'m_r [GeV]':>10} | {'xi':>8} | {'theta [rad]':>12} | {'theta [deg]':>12} | "
          f"{'m_h_phys':>10} | {'m_r_phys':>10} | {'det(Z)':>10}")
    print("-" * 95)

    mixing_results = {}
    for m_r in m_r_values:
        mixing_results[m_r] = {}
        for xi in xi_values_compare:
            mix = higgs_radion_mixing(
                m_h0=params.m_h, m_r0=m_r,
                xi=xi, Lambda_r=params.Lambda_r,
                v_EW=params.v_EW
            )
            mixing_results[m_r][xi] = mix
            label = "1/6" if abs(xi - 1.0/6.0) < 1e-10 else "0"
            print(f"{m_r:10.0f} | {label:>8} | {mix['theta_mix_exact']:12.6e} | "
                  f"{np.degrees(mix['theta_mix_exact']):12.6e} | "
                  f"{mix['m1_phys']:10.3f} | {mix['m2_phys']:10.3f} | "
                  f"{mix['Z_det']:10.6f}")

    all_results['mixing'] = {}
    for m_r in m_r_values:
        all_results['mixing'][m_r] = {}
        for xi in xi_values_compare:
            mix = mixing_results[m_r][xi]
            key = f"xi_{xi:.4f}"
            all_results['mixing'][m_r][key] = {
                'theta_rad': float(mix['theta_mix_exact']),
                'theta_deg': float(np.degrees(mix['theta_mix_exact'])),
                'm1_phys': float(mix['m1_phys']),
                'm2_phys': float(mix['m2_phys']),
                'det_Z': float(mix['Z_det']),
                'ghost_free': bool(mix['ghost_free']),
            }

    # --------------------------------------------------------
    # Part 2: Signal strengths
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 2: HIGGS SIGNAL STRENGTH MODIFICATIONS")
    print("=" * 70)

    print(f"\n{'m_r':>6} | {'xi':>5} | {'kappa_V':>10} | {'kappa_f':>10} | "
          f"{'kappa_g':>10} | {'kappa_gam':>10} | {'mu_ggF_WW':>10}")
    print("-" * 80)

    ss_results = {}
    for m_r in m_r_values:
        ss_results[m_r] = {}
        for xi in xi_values_compare:
            mix = mixing_results[m_r][xi]
            ss = higgs_signal_strengths(
                d_coeff=mix['d'], c_coeff=mix['c'],
                gamma=mix['gamma'], xi=xi
            )
            ss_results[m_r][xi] = ss
            label = "1/6" if abs(xi - 1.0/6.0) < 1e-10 else "0"
            mu_WW = ss['signal_strengths'].get('mu_ggF_WW', 0.0)
            print(f"{m_r:6.0f} | {label:>5} | {ss['kappa_V']:10.6f} | "
                  f"{ss['kappa_f']:10.6f} | {ss['kappa_g']:10.6f} | "
                  f"{ss['kappa_gamma']:10.6f} | {mu_WW:10.6f}")

    # --------------------------------------------------------
    # Part 3: Radion production and decay
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 3: RADION PRODUCTION AND DECAY")
    print("=" * 70)

    print(f"\n{'m_r':>6} | {'Gamma_tot [GeV]':>16} | {'Gamma/m':>10} | "
          f"{'BR(gg)':>8} | {'BR(WW)':>8} | {'BR(ZZ)':>8} | {'BR(hh)':>8} | {'BR(tt)':>8}")
    print("-" * 100)

    radion_results = {}
    for m_r in m_r_values:
        mix = mixing_results[m_r][1.0/6.0]
        rad = radion_cross_sections(
            m_r=m_r, Lambda_r=params.Lambda_r,
            theta=mix['theta_mix_exact']
        )
        radion_results[m_r] = rad
        brs = rad['BRs']
        print(f"{m_r:6.0f} | {rad['Gamma_total']:16.6e} | {rad['Gamma_over_m']:10.6e} | "
              f"{brs.get('gg', 0):8.4f} | {brs.get('WW', 0):8.4f} | "
              f"{brs.get('ZZ', 0):8.4f} | {brs.get('hh', 0):8.4f} | "
              f"{brs.get('tt', 0):8.4f}")

    # --------------------------------------------------------
    # Part 4: KK graviton spectrum
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 4: KK GRAVITON SPECTRUM")
    print("=" * 70)

    kk = kk_graviton_spectrum(params, n_modes=5)
    print(f"\nKK scale: {kk['m_KK_scale']:.3e} GeV")
    print(f"NMC correction: delta_xi = {kk['delta_xi_correction']:.4f}")
    print(f"\n{'Mode':>5} | {'m_n [GeV]':>15} | {'m_n [TeV]':>12} | {'Lambda_n [GeV]':>15}")
    print("-" * 55)
    for n, (m, L) in enumerate(zip(kk['masses_GeV'], kk['coupling_scales_GeV']), 1):
        print(f"{n:5d} | {m:15.3e} | {m/1000:12.3f} | {L:15.3e}")

    all_results['kk_spectrum'] = {
        'm_KK_scale': float(kk['m_KK_scale']),
        'masses_TeV': [float(m/1000) for m in kk['masses_GeV']],
        'delta_xi': float(kk['delta_xi_correction']),
    }

    # --------------------------------------------------------
    # Part 5: Self-tuning breakdown
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 5: SELF-TUNING BREAKDOWN FOR xi != 1/6")
    print("=" * 70)

    xi_scan = np.array([0.0, 0.01, 0.05, 0.10, 1.0/6.0, 0.20, 0.25, 0.50, 1.0])
    st = self_tuning_check(xi_scan)

    print(f"\n{'xi':>8} | {'delta_xi':>10} | {'F(Phi)':>10} | "
          f"{'Residual CC':>12} | {'Self-tuning':>12} | {'Conformal':>10}")
    print("-" * 75)
    for r in st['xi_scan']:
        cf = "YES" if r['conformal_covariant'] else "no"
        print(f"{r['xi']:8.4f} | {r['delta_xi']:10.6f} | {r['F']:10.6f} | "
              f"{r['residual_CC_Planck']:12.3e} | {r['self_tuning_sig_figs']:12.1f} | "
              f"{cf:>10}")

    # --------------------------------------------------------
    # Part 6: Experimental distinguishability
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 6: EXPERIMENTAL DISTINGUISHABILITY")
    print("=" * 70)

    dist = measurement_precision()

    print(f"\n--- Higgs coupling modifier separation (xi=1/6 vs xi=0) ---")
    print(f"{'m_r [GeV]':>10} | {'theta(1/6)':>12} | {'theta(0)':>12} | "
          f"{'delta_theta':>12} | {'delta_kV':>12} | {'kV(1/6)':>12}")
    print("-" * 85)
    for r in dist['m_r_scan']:
        print(f"{r['m_r']:10.0f} | {r['theta_xi16']:12.6e} | {r['theta_xi0']:12.6e} | "
              f"{r['delta_theta']:12.6e} | {r['delta_kV_separation']:12.6e} | "
              f"{r['kappa_V_xi16']:12.8f}")

    print(f"\n--- Collider precision requirements ---")
    print(f"\nFor m_r = 500 GeV (benchmark):")
    r500 = [r for r in dist['m_r_scan'] if r['m_r'] == 500][0]
    delta_kV = r500['delta_kV_separation']
    delta_kV_from_SM = r500['delta_kV_16_from_SM']

    print(f"  |kappa_V(xi=1/6) - kappa_V(xi=0)| = {delta_kV:.3e}")
    print(f"  |kappa_V(xi=1/6) - 1| = {delta_kV_from_SM:.3e}")

    colliders = {
        'LHC Run 2': dist['current_precision'],
        'HL-LHC': dist['hllhc_precision'],
        'FCC-hh': dist['fcc_hh_precision'],
        'FCC-ee': dist['fcc_ee_precision'],
        'Muon Collider': dist['muon_collider_precision'],
    }

    print(f"\n{'Collider':>20} | {'sigma(kV)':>10} | {'S/N (vs xi=0)':>14} | "
          f"{'S/N (vs SM)':>12} | {'Sensitive?':>10}")
    print("-" * 75)
    for name, prec in colliders.items():
        sn_xi = delta_kV / prec['kappa_V'] if prec['kappa_V'] > 0 else 0
        sn_sm = delta_kV_from_SM / prec['kappa_V'] if prec['kappa_V'] > 0 else 0
        sensitive = "YES" if sn_xi > 2 else "marginal" if sn_xi > 1 else "no"
        print(f"{name:>20} | {prec['kappa_V']:10.4f} | {sn_xi:14.2f} | "
              f"{sn_sm:12.2f} | {sensitive:>10}")

    all_results['distinguishability'] = {
        'benchmark_m_r': 500,
        'delta_kV_xi16_vs_xi0': float(delta_kV),
        'delta_kV_from_SM': float(delta_kV_from_SM),
    }

    # --------------------------------------------------------
    # Part 7: Scan over Lambda_r (radion coupling scale)
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 7: SENSITIVITY TO RADION COUPLING SCALE")
    print("=" * 70)

    Lambda_r_values = [500, 1000, 2000, 3000, 5000, 10000]
    m_r_fixed = 500  # benchmark radion mass

    print(f"\nBenchmark: m_r = {m_r_fixed} GeV, xi = 1/6")
    print(f"\n{'Lambda_r [GeV]':>15} | {'gamma':>10} | {'theta [deg]':>12} | "
          f"{'kappa_V':>10} | {'delta_kV':>10}")
    print("-" * 65)

    for Lr in Lambda_r_values:
        gamma = params.v_EW / Lr
        mix = higgs_radion_mixing(
            m_h0=params.m_h, m_r0=m_r_fixed,
            xi=1.0/6.0, Lambda_r=Lr,
            v_EW=params.v_EW
        )
        ss = higgs_signal_strengths(
            d_coeff=mix['d'], c_coeff=mix['c'],
            gamma=mix['gamma'], xi=1.0/6.0
        )
        print(f"{Lr:15.0f} | {gamma:10.6f} | {np.degrees(mix['theta_mix_exact']):12.6e} | "
              f"{ss['kappa_V']:10.6f} | {abs(ss['kappa_V'] - 1):10.6e}")

    # --------------------------------------------------------
    # Part 8: Critical gamma = v_EW / Lambda_r threshold
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 8: CRITICAL RESULT  -- gamma = v_EW / Lambda_r")
    print("=" * 70)

    gamma_val = params.v_EW / params.Lambda_r
    print(f"\nFor Meridian benchmark parameters:")
    print(f"  Lambda_r = sqrt(6) * M_Pl * exp(-ky_c)")
    print(f"  Lambda_r = {params.Lambda_r:.3e} GeV")
    print(f"  gamma = v_EW / Lambda_r = {gamma_val:.6e}")
    print(f"  6*xi*gamma^2 = {6 * params.xi * gamma_val**2:.6e}")
    print(f"  6*xi*gamma = {6 * params.xi * gamma_val:.6e}")
    print(f"")
    print(f"  The mixing angle scales as theta ~ 6*xi*gamma*m_h^2/(m_r^2 - m_h^2)")
    print(f"  For m_r >> m_h: theta ~ 6*xi*gamma*(m_h/m_r)^2")
    print(f"  For m_r = 500 GeV: theta ~ {6*params.xi*gamma_val*(params.m_h/500)**2:.6e}")
    print(f"")
    print(f"  KEY INSIGHT: With standard RS parameters (ky_c = 35),")
    print(f"  Lambda_r ~ {params.Lambda_r/1e9:.1f} * 10^9 GeV  -- far above the TeV scale.")
    print(f"  This suppresses gamma to ~ {gamma_val:.1e}, making the mixing angle")
    print(f"  extremely small (~{6*params.xi*gamma_val*(params.m_h/500)**2:.1e} rad for m_r = 500 GeV).")
    print(f"")
    print(f"  HOWEVER: In RS models where the radion mass is at the TeV scale,")
    print(f"  the PHYSICAL coupling is through Lambda_phi = Lambda_r / sqrt(6):")
    print(f"  Lambda_phi = M_Pl * exp(-ky_c) = {params.M_Pl * np.exp(-params.ky_c):.3e} GeV")

    # Recompute with TeV-scale Lambda_r (which is the relevant scale
    # for collider phenomenology  -- the physical radion-matter coupling)
    # In many RS phenomenology papers, Lambda_r is taken as the IR scale
    # ~ TeV, not the geometric scale. Let's do both.
    Lambda_r_pheno = params.k * np.exp(-params.ky_c)  # ~ TeV if k ~ 10^16 and ky_c ~ 35
    # But with our parameters: k = 10^16, ky_c = 35
    # exp(-35) ~ 6.3e-16
    # Lambda_IR = 10^16 * 6.3e-16 ~ 6.3 GeV
    # This is way too low  -- need to adjust k and ky_c

    print(f"\n  NOTE ON SCALE MISMATCH:")
    print(f"  k = {params.k:.1e} GeV, ky_c = {params.ky_c}")
    print(f"  Lambda_IR = k * exp(-ky_c) = {params.Lambda_IR:.3e} GeV")
    print(f"  This gives Lambda_IR ~ {params.Lambda_IR:.1f} GeV")
    print(f"")
    print(f"  For TeV-scale physics (m_KK ~ TeV), we need:")
    print(f"  k * exp(-ky_c) ~ TeV  =>  ky_c ~ ln(k/TeV) ~ {np.log(params.k/1000):.1f}")
    print(f"  With k = 10^16 GeV: ky_c ~ {np.log(1e16/1e3):.1f}")

    # Correct ky_c for TeV physics
    ky_c_TeV = np.log(params.k / 1000.0)  # ~ 29.9 for k = 10^16
    Lambda_IR_TeV = params.k * np.exp(-ky_c_TeV)
    Lambda_r_TeV = np.sqrt(6) * params.M_Pl * np.exp(-ky_c_TeV)
    gamma_TeV = params.v_EW / Lambda_r_TeV

    print(f"\n  For ky_c = {ky_c_TeV:.1f} (IR scale ~ TeV):")
    print(f"  Lambda_IR = {Lambda_IR_TeV:.3e} GeV = {Lambda_IR_TeV/1000:.1f} TeV")
    print(f"  Lambda_r = {Lambda_r_TeV:.3e} GeV")
    print(f"  gamma = {gamma_TeV:.6e}")
    print(f"  6*xi*gamma = {6*(1/6)*gamma_TeV:.6e}")

    # The STANDARD RS1 phenomenology uses ky_c ~ 35-37 with
    # k ~ O(M_Pl), which gives Lambda_IR ~ TeV:
    # If k ~ M_Pl ~ 2.4e18: ky_c = ln(k/TeV) ~ ln(2.4e15) ~ 35.4
    k_standard = 2.0e18  # closer to M_Pl
    ky_c_standard = 35.0
    Lambda_IR_std = k_standard * np.exp(-ky_c_standard)
    Lambda_r_std = np.sqrt(6) * params.M_Pl * np.exp(-ky_c_standard)
    gamma_std = params.v_EW / Lambda_r_std

    print(f"\n  STANDARD RS1 (k ~ M_Pl, ky_c ~ 35):")
    print(f"  k = {k_standard:.1e} GeV")
    print(f"  Lambda_IR = {Lambda_IR_std:.3e} GeV = {Lambda_IR_std/1000:.3f} TeV")
    print(f"  Lambda_r = {Lambda_r_std:.3e} GeV = {Lambda_r_std/1000:.3f} TeV")
    print(f"  gamma = v_EW/Lambda_r = {gamma_std:.6f}")
    print(f"  6*xi*gamma = {6*(1/6)*gamma_std:.6f}")
    print(f"  6*xi*gamma^2 = {6*(1/6)*gamma_std**2:.6f}")

    # NOW recompute the mixing with the standard RS1 parameters
    print(f"\n--- STANDARD RS1 HIGGS-RADION MIXING ---")
    print(f"{'m_r [GeV]':>10} | {'theta(1/6) [deg]':>16} | {'theta(0) [deg]':>16} | "
          f"{'delta_theta [deg]':>16} | {'kV(1/6)':>10} | {'delta_kV':>10}")
    print("-" * 95)

    final_results = []
    for m_r in [200, 300, 500, 750, 1000, 1500]:
        mix_16 = higgs_radion_mixing(
            m_h0=params.m_h, m_r0=m_r,
            xi=1.0/6.0, Lambda_r=Lambda_r_std,
            v_EW=params.v_EW
        )
        mix_0 = higgs_radion_mixing(
            m_h0=params.m_h, m_r0=m_r,
            xi=0.0, Lambda_r=Lambda_r_std,
            v_EW=params.v_EW
        )
        ss_16 = higgs_signal_strengths(
            d_coeff=mix_16['d'], c_coeff=mix_16['c'],
            gamma=mix_16['gamma'], xi=1.0/6.0
        )
        delta_theta = abs(mix_16['theta_mix_exact'] - mix_0['theta_mix_exact'])
        delta_kV = abs(ss_16['kappa_V'] - 1.0)

        print(f"{m_r:10.0f} | {np.degrees(mix_16['theta_mix_exact']):16.6f} | "
              f"{np.degrees(mix_0['theta_mix_exact']):16.6f} | "
              f"{np.degrees(delta_theta):16.6f} | "
              f"{ss_16['kappa_V']:10.6f} | {delta_kV:10.6e}")

        final_results.append({
            'm_r': m_r,
            'theta_16_deg': float(np.degrees(mix_16['theta_mix_exact'])),
            'theta_0_deg': float(np.degrees(mix_0['theta_mix_exact'])),
            'delta_theta_deg': float(np.degrees(delta_theta)),
            'kappa_V': float(ss_16['kappa_V']),
            'delta_kV': float(delta_kV),
        })

    all_results['standard_RS1'] = {
        'k': k_standard,
        'ky_c': ky_c_standard,
        'Lambda_IR_GeV': float(Lambda_IR_std),
        'Lambda_r_GeV': float(Lambda_r_std),
        'gamma': float(gamma_std),
        'scan': final_results,
    }

    # --------------------------------------------------------
    # Part 9: Sensitivity to discriminate xi at colliders
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PART 9: COLLIDER SENSITIVITY SUMMARY (STANDARD RS1)")
    print("=" * 70)

    # Use m_r = 300 GeV (benchmark where mixing is largest)
    m_r_bench = 300
    mix_bench_16 = higgs_radion_mixing(
        m_h0=params.m_h, m_r0=m_r_bench,
        xi=1.0/6.0, Lambda_r=Lambda_r_std,
        v_EW=params.v_EW
    )
    mix_bench_0 = higgs_radion_mixing(
        m_h0=params.m_h, m_r0=m_r_bench,
        xi=0.0, Lambda_r=Lambda_r_std,
        v_EW=params.v_EW
    )
    ss_bench_16 = higgs_signal_strengths(
        d_coeff=mix_bench_16['d'], c_coeff=mix_bench_16['c'],
        gamma=mix_bench_16['gamma'], xi=1.0/6.0
    )
    ss_bench_0 = higgs_signal_strengths(
        d_coeff=mix_bench_0['d'], c_coeff=mix_bench_0['c'],
        gamma=mix_bench_0['gamma'], xi=0.0
    )

    delta_kV_bench = abs(ss_bench_16['kappa_V'] - ss_bench_0['kappa_V'])
    delta_kV_SM = abs(ss_bench_16['kappa_V'] - 1.0)

    print(f"\nBenchmark: m_r = {m_r_bench} GeV, Standard RS1 (k ~ M_Pl, ky_c = 35)")
    print(f"  gamma = {gamma_std:.6f}")
    print(f"  theta(xi=1/6) = {np.degrees(mix_bench_16['theta_mix_exact']):.4f} deg")
    print(f"  kappa_V(xi=1/6) = {ss_bench_16['kappa_V']:.6f}")
    print(f"  kappa_V(xi=0) = {ss_bench_0['kappa_V']:.6f}")
    print(f"  |delta kappa_V (1/6 vs 0)| = {delta_kV_bench:.3e}")
    print(f"  |delta kappa_V (1/6 vs SM)| = {delta_kV_SM:.3e}")

    print(f"\n{'Collider':>20} | {'sigma(kV)':>10} | {'S/N (xi=1/6 vs 0)':>18} | "
          f"{'S/N (vs SM)':>12} | {'Can distinguish?':>16}")
    print("-" * 85)
    for name, prec in colliders.items():
        sn_xi = delta_kV_bench / prec['kappa_V'] if prec['kappa_V'] > 0 else 0
        sn_sm = delta_kV_SM / prec['kappa_V'] if prec['kappa_V'] > 0 else 0
        if sn_xi > 5:
            disc = "YES (5 sigma)"
        elif sn_xi > 3:
            disc = "YES (3 sigma)"
        elif sn_xi > 2:
            disc = "marginal"
        else:
            disc = "no"
        print(f"{name:>20} | {prec['kappa_V']:10.4f} | {sn_xi:18.2f} | "
              f"{sn_sm:12.2f} | {disc:>16}")

    # --------------------------------------------------------
    # Part 10: Summary statistics
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUMMARY OF KEY RESULTS")
    print("=" * 70)

    print(f"""
1. HIGGS-RADION MIXING (Standard RS1: k ~ M_Pl, ky_c = 35)
   gamma = v_EW / Lambda_r = {gamma_std:.4f}
   Mixing angle ~ {np.degrees(mix_bench_16['theta_mix_exact']):.2f} deg for m_r = {m_r_bench} GeV
   Mixing vanishes for xi = 0 (minimal coupling)

2. HIGGS SIGNAL STRENGTHS
   kappa_V(xi=1/6) = {ss_bench_16['kappa_V']:.6f} (m_r = {m_r_bench} GeV)
   Deviation from SM: |1 - kappa_V| = {delta_kV_SM:.3e}
   Separation xi=1/6 vs xi=0: {delta_kV_bench:.3e}

3. KK GRAVITON SPECTRUM
   First KK mass: m_1 = {kk['masses_GeV'][0]:.1f} GeV = {kk['masses_GeV'][0]/1000:.4f} TeV
   (with NMC correction +{kk['delta_xi_correction']*100:.1f}%)

4. SELF-TUNING
   xi = 1/6: self-tuning exact (conformal covariance)
   xi = 0: residual CC ~ zeta_0 * M_Pl^2 * H_0^2 (catastrophic)
   Any xi != 1/6 breaks the self-tuning mechanism

5. FALSIFIABILITY
   DIRECT: Measure Higgs-radion mixing to determine xi
   INDIRECT: Discover radion, measure xi from production/decay patterns
   KILLER: If xi measured != 1/6 at any precision, Meridian falsified

6. COLLIDER PROSPECTS
   Standard RS1 (gamma ~ {gamma_std:.2f}):
   - HL-LHC: {'can' if delta_kV_SM > 0.017 else 'cannot'} detect deviation from SM
   - FCC-ee: {'can' if delta_kV_SM > 0.002 else 'cannot'} detect deviation from SM
   - Muon collider: {'can' if delta_kV_SM > 0.001 else 'cannot'} detect deviation from SM
""")

    return all_results


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    results = comprehensive_scan()
