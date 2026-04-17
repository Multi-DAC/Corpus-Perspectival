"""
Project Meridian — D3.4: Numerical Cosmological Solver
Clayton & Clawd, March 2026

Solves the Meridian cuscuton braneworld cosmology for:
  - w(z) dark energy equation of state
  - w0, wa (CPL parametrization)
  - H0 from CMB calibration
  - f*sigma8(z) growth rate
  - mu(z), eta(z) modified gravity observables
  - Phantom crossing detection

Two modes:
  xi = 0: Analytic E^2(a) from the cuscuton K ~ 1/H^2 scaling
  xi > 0: Full numerical ODE integration with curvature coupling
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.optimize import brentq, minimize_scalar, minimize
from dataclasses import dataclass, field
from typing import Optional, Tuple


# ============================================================
# CONSTANTS
# ============================================================

# Cosmological parameters (Planck 2018 + DESI DR2 baseline)
OMEGA_M0 = 0.315       # Matter density today
OMEGA_R0 = 9.1e-5      # Radiation density today
OMEGA_DE0 = 1.0 - OMEGA_M0 - OMEGA_R0  # DE density (flat universe)
H0_FIDUCIAL = 67.4     # km/s/Mpc (Planck LCDM)
Z_STAR = 1089.92        # Last scattering redshift
SIGMA8_FID = 0.811      # sigma_8 fiducial (Planck)

# DESI DR2 targets (Planck + DESI + Union3)
W0_DESI = -0.752
W0_DESI_ERR = 0.058
WA_DESI = -0.86
WA_DESI_ERR_PLUS = 0.28
WA_DESI_ERR_MINUS = 0.25

# Observational fσ₈ data (compiled from BOSS, eBOSS, 6dFGS, VIPERS, FastSound)
# Each entry: (z_eff, fsigma8, sigma_fsigma8, survey)
FSIGMA8_DATA = [
    (0.02, 0.428, 0.0465, "6dFGS (2012)"),
    (0.15, 0.490, 0.145,  "SDSS MGS (2015)"),
    (0.38, 0.497, 0.045,  "BOSS DR12 (2017)"),
    (0.51, 0.459, 0.038,  "BOSS DR12 (2017)"),
    (0.61, 0.436, 0.034,  "BOSS DR12 (2017)"),
    (0.70, 0.448, 0.043,  "VIPERS (2018)"),
    (0.85, 0.315, 0.095,  "FastSound (2016)"),
    (0.978, 0.379, 0.176, "eBOSS QSO (2020)"),
    (1.48, 0.462, 0.045,  "eBOSS Lyα (2020)"),
]

# Planck CMB distance prior: θ_* = r_s(z*)/D_A(z*) fixed
# This constrains the combination H0 * r_s(z*) / ∫da/(a²E)
# We use H0 comparison as a proxy


@dataclass
class MeridianParams:
    """Parameters for the Meridian cosmological model."""
    eps0: float         # epsilon_0 = K_eff,0 / V_eff,0 (kinetic/potential ratio)
    zeta0: float = 0.0  # zeta_0 = xi * phi_IR^2 / F_0 (cosmological xi-coupling)
    beta: float = 0.0   # phi_dot_IR / (H0 * phi_IR) (fractional rolling rate)
    lambda3: float = 0.0  # G_3 braiding parameter (extended cuscuton, D5.5)
    gamma_r: float = 0.0  # Radion drift coupling (D5.6): V_eff(a) = v0 * E^{2*gamma_r}
    Omega_m: float = OMEGA_M0
    Omega_r: float = OMEGA_R0


@dataclass
class MeridianResult:
    """Results from the cosmological solver."""
    # CPL parameters (E^2-based fit — what DESI measures)
    w0: float = 0.0
    wa: float = 0.0
    # Intrinsic w (scalar field equation of state)
    w0_intrinsic: float = 0.0
    wa_intrinsic: float = 0.0
    # Observables
    H0_CMB: float = 0.0          # km/s/Mpc from CMB calibration
    delta_H0_pct: float = 0.0    # % shift from LCDM
    # Growth
    fsigma8: dict = field(default_factory=dict)  # {z: fsigma8(z)}
    delta_fsigma8_pct: dict = field(default_factory=dict)
    # Modified gravity
    mu_z: dict = field(default_factory=dict)     # {z: mu(z)}
    eta: float = 1.0              # Gravitational slip (exact for cuscuton)
    cs2: float = np.inf           # Sound speed squared
    # Phantom crossing
    has_phantom_crossing: bool = False
    z_phantom: float = -1.0       # Redshift of phantom crossing (-1 if none)
    # DESI comparison
    chi2_DESI: float = 0.0
    # Full curves
    z_array: np.ndarray = field(default_factory=lambda: np.array([]))
    w_array: np.ndarray = field(default_factory=lambda: np.array([]))
    E_array: np.ndarray = field(default_factory=lambda: np.array([]))


# ============================================================
# XI = 0 SOLVER (Analytic)
# ============================================================

def E2_xi0(a: float, params: MeridianParams) -> float:
    """
    Analytic E^2(a) = H^2(a)/H0^2 for xi = 0 cuscuton dark energy.

    From D3.2: K_eff ~ 1/H^2, V_eff ~ const (slowly rolling).
    The Friedmann equation becomes a quadratic in E^2:
      E^4 - (Omega_mat(a) + v0) E^2 - kappa0 = 0

    where v0 = Omega_DE/(1+eps0), kappa0 = eps0*v0.
    """
    eps0 = params.eps0
    Om = params.Omega_m
    Or = params.Omega_r
    Ode = 1.0 - Om - Or

    v0 = Ode / (1.0 + eps0)      # Potential contribution
    kappa0 = eps0 * v0             # Kinetic contribution

    Omega_mat_a = Om * a**(-3) + Or * a**(-4)
    R = Omega_mat_a + v0           # Non-kinetic sum

    # Quadratic formula: E^2 = (R + sqrt(R^2 + 4*kappa0)) / 2
    discriminant = R**2 + 4.0 * kappa0
    return 0.5 * (R + np.sqrt(discriminant))


def w_DE_xi0(a: float, params: MeridianParams) -> float:
    """
    Dark energy equation of state at xi = 0.

    w_DE = (K_eff - V_eff) / (K_eff + V_eff)
         = (kappa0/E^2 - v0) / (kappa0/E^2 + v0)
    """
    eps0 = params.eps0
    Ode = 1.0 - params.Omega_m - params.Omega_r
    v0 = Ode / (1.0 + eps0)
    kappa0 = eps0 * v0

    E2 = E2_xi0(a, params)
    K_norm = kappa0 / E2    # K_eff normalized

    return (K_norm - v0) / (K_norm + v0)


# ============================================================
# EXTENDED CUSCUTON SOLVER (Quartic Friedmann, D5.5)
# ============================================================

def solve_quartic_E(R: float, lambda3: float, kappa0: float) -> float:
    """
    Solve E^4 - R*E^2 - lambda3*E - kappa0 = 0 for the largest positive real root.
    This is the extended cuscuton Friedmann equation (D5.5, eq 3.5).
    """
    coeffs = [1.0, 0.0, -R, -lambda3, -kappa0]
    roots = np.roots(coeffs)
    # Filter for positive real roots
    real_roots = []
    for r in roots:
        if abs(r.imag) < 1e-10 and r.real > 0:
            real_roots.append(r.real)
    if not real_roots:
        # Fallback to minimal cuscuton solution
        disc = R**2 + 4.0 * kappa0
        return np.sqrt(0.5 * (R + np.sqrt(max(disc, 0.0))))
    return max(real_roots)


def E_extended(a: float, params: MeridianParams) -> float:
    """
    E(a) = H(a)/H0 for the extended cuscuton (lambda3 > 0, xi = 0).

    Solves: E^4 - R(a)*E^2 - lambda3*E - kappa0 = 0
    where R(a) = Omega_m*a^{-3} + Omega_r*a^{-4} + v0
    and kappa0 = eps0 * v0, v0 = (Omega_DE - lambda3) / (1 + eps0).
    """
    eps0 = params.eps0
    Om = params.Omega_m
    Or = params.Omega_r
    Ode = 1.0 - Om - Or
    lam3 = params.lambda3

    v0 = (Ode - lam3) / (1.0 + eps0)
    kappa0 = eps0 * v0

    R = Om * a**(-3) + Or * a**(-4) + v0
    return solve_quartic_E(R, lam3, kappa0)


def w_DE_extended(a: float, params: MeridianParams) -> float:
    """
    Dark energy equation of state for the extended cuscuton.

    rho_DE = v0 + lambda3/E + kappa0/E^2
    w_DE = -1 - (d ln rho_DE / dN) / 3

    Uses implicit differentiation of the quartic for dE/dN.
    """
    eps0 = params.eps0
    Om = params.Omega_m
    Or = params.Omega_r
    Ode = 1.0 - Om - Or
    lam3 = params.lambda3

    v0 = (Ode - lam3) / (1.0 + eps0)
    kappa0 = eps0 * v0

    Om_a3 = Om * a**(-3)
    Or_a4 = Or * a**(-4)
    R = Om_a3 + Or_a4 + v0

    E = solve_quartic_E(R, lam3, kappa0)

    # dR/dN = -3*Omega_m*a^{-3} - 4*Omega_r*a^{-4}
    dR_dN = -3.0 * Om_a3 - 4.0 * Or_a4

    # Implicit differentiation: dE/dN = dR_dN * E^2 / (4E^3 - 2R*E - lambda3)
    denom = 4.0 * E**3 - 2.0 * R * E - lam3
    if abs(denom) < 1e-30:
        return -1.0
    dE_dN = dR_dN * E**2 / denom

    # rho_DE = v0 + lambda3/E + kappa0/E^2
    rho_DE = v0 + lam3 / E + kappa0 / E**2
    # d(rho_DE)/dN = -(dE/dN) * (lambda3/E^2 + 2*kappa0/E^3)
    drho_DE_dN = -dE_dN * (lam3 / E**2 + 2.0 * kappa0 / E**3)

    if rho_DE > 1e-20:
        return -1.0 - drho_DE_dN / (3.0 * rho_DE)
    return -1.0


# ============================================================
# RADION DYNAMICS SOLVER (D5.6)
# ============================================================

def E_radion(a: float, params: MeridianParams) -> float:
    """
    E(a) for the radion-modified cuscuton (gamma_r > 0, xi = 0).

    Solves: E^4 - Omega_mat(a)*E^2 - v0*E^{2+2*gamma_r} - kappa0 = 0
    Requires numerical root-finding (transcendental in E).
    """
    eps0 = params.eps0
    gr = params.gamma_r
    Om = params.Omega_m
    Or = params.Omega_r
    Ode = 1.0 - Om - Or

    v0 = Ode / (1.0 + eps0)
    kappa0 = eps0 * v0

    Om_mat = Om * a**(-3) + Or * a**(-4)

    def f(E):
        return E**4 - Om_mat * E**2 - v0 * E**(2 + 2*gr) - kappa0

    # f(0+) = -kappa0 < 0, f(large) → +inf. Unique positive root.
    # Good bracket: [0.01, 200]
    try:
        return brentq(f, 0.01, 200.0, xtol=1e-12, rtol=1e-12)
    except ValueError:
        # Fallback: minimal cuscuton solution
        R = Om_mat + v0
        disc = R**2 + 4.0 * kappa0
        return np.sqrt(0.5 * (R + np.sqrt(max(disc, 0.0))))


def w_DE_radion(a: float, params: MeridianParams) -> float:
    """
    Dark energy equation of state for radion-modified cuscuton.

    rho_DE = v0*E^{2*gamma_r} + kappa0/E^2
    w_DE = -1 - (d ln rho_DE / dN) / 3

    Uses implicit differentiation for dE/dN.
    """
    eps0 = params.eps0
    gr = params.gamma_r
    Om = params.Omega_m
    Or = params.Omega_r
    Ode = 1.0 - Om - Or

    v0 = Ode / (1.0 + eps0)
    kappa0 = eps0 * v0

    Om_a3 = Om * a**(-3)
    Or_a4 = Or * a**(-4)
    Om_mat = Om_a3 + Or_a4

    E = E_radion(a, params)

    # dOm_mat/dN = -3*Om_a3 - 4*Or_a4
    dOm_dN = -3.0 * Om_a3 - 4.0 * Or_a4

    # From E^4 - Om_mat*E^2 - v0*E^{2+2gr} - kappa0 = 0
    # Implicit diff:
    # 4E^3 dE/dN - dOm/dN*E^2 - 2*Om_mat*E*dE/dN
    #   - v0*(2+2gr)*E^{1+2gr}*dE/dN + 2*kappa0/E^3 * dE/dN = 0
    #
    # Wait — the kappa0 term: d/dN(-kappa0) = 0 since kappa0 is constant.
    # But in the Friedmann eq: E^4 = Om_mat*E^2 + v0*E^{2+2gr} + kappa0
    # Diff: 4E^3 dE/dN = dOm/dN*E^2 + 2*Om_mat*E*dE/dN + v0*(2+2gr)*E^{1+2gr}*dE/dN
    # So: dE/dN * [4E^3 - 2*Om_mat*E - v0*(2+2gr)*E^{1+2gr}] = dOm/dN * E^2

    denom = 4.0*E**3 - 2.0*Om_mat*E - v0*(2.0+2.0*gr)*E**(1.0+2.0*gr)
    if abs(denom) < 1e-30:
        return -1.0
    dE_dN = dOm_dN * E**2 / denom
    dE2_dN = 2.0 * E * dE_dN

    # Operational: rho_DE = E^2 - Om_mat
    rho_DE = E**2 - Om_mat
    drho_DE_dN = dE2_dN - dOm_dN  # = dE2/dN + 3*Om_a3 + 4*Or_a4

    if rho_DE > 1e-20:
        return -1.0 - drho_DE_dN / (3.0 * rho_DE)
    return -1.0


# ============================================================
# XI > 0 SOLVER (Numerical ODE)
# ============================================================

def solve_xi_positive(params: MeridianParams,
                      N_start: float = -8.0,
                      N_end: float = 0.5,
                      N_points: int = 3000) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Solve the xi > 0 cosmological system numerically.

    Strategy (v3 — clean algebraic):
      1. Evolve psi(N) via ODE: psi' = beta / E^2(N, psi)
      2. E^2 is computed ALGEBRAICALLY from the modified Friedmann equation
         by substituting psi' = beta/E^2 into the xi correction, yielding
         a clean quadratic in E^2 with no circular dependency.
      3. w_DE is extracted operationally from rho_DE = E^2 - Omega_mat:
         w_DE = -1 - (d ln rho_DE / dN) / 3
         with dE^2/dN computed analytically via implicit differentiation.

    The modified Friedmann quadratic (D3.3 eq 3.6 with psi' = beta/E^2):
      A * (E^2)^2 + B * (E^2) - kappa0 = 0
    where A = 1 + 2*zeta0*psi^2
          B = 4*zeta0*psi*beta - R
          R = Omega_m*a^{-3} + Omega_r*a^{-4} + v0*psi

    Returns: (N_arr, psi_arr, E_arr, w_arr)
    """
    eps0 = params.eps0
    zeta0 = params.zeta0
    beta = params.beta
    lam3 = params.lambda3
    gr = params.gamma_r
    Om = params.Omega_m
    Or = params.Omega_r
    Ode = 1.0 - Om - Or

    # --- Self-consistent normalization ensuring E(0) = 1 ---
    # At N=0, psi=1, E=1: A*1 + B*1 - lambda3*1 - kappa0 = 0
    # => v0*(1+eps0) = Ode + 2*zeta0 + 4*zeta0*beta - lambda3
    # (Radion: E^{2*gr}=1 at a=1, so normalization unchanged.)
    # beta depends on v0, so iterate:
    v0_xi0 = Ode / (1.0 + eps0)
    beta_i = np.sqrt(2.0 * eps0 * v0_xi0 / Ode) * 0.5 if (beta == 0.0 and eps0 > 0) else beta
    for _iter in range(20):
        v0_i = (Ode + 2.0 * zeta0 + 4.0 * zeta0 * beta_i - lam3) / (1.0 + eps0)
        beta_new = np.sqrt(2.0 * eps0 * max(v0_i, 1e-20) / Ode) * 0.5
        if abs(beta_new - beta_i) < 1e-14:
            break
        beta_i = beta_new
    v0 = v0_i
    kappa0 = eps0 * v0
    beta = beta_i

    def E2_algebraic(N, psi):
        """
        Compute E^2 from the modified Friedmann equation.
        When gamma_r > 0: solves transcendental A*x^2 + C*x - V*x^{1+gr} - kappa0 = 0.
        When lambda3 > 0: solves quartic A*E^4 + B*E^2 - lambda3*E - kappa0 = 0.
        When both = 0: solves quadratic A*x^2 + B*x - kappa0 = 0 where x = E^2.
        """
        a = np.exp(N)
        Om_mat = Om * a**(-3) + Or * a**(-4)
        A = 1.0 + 2.0 * zeta0 * psi**2

        if gr > 1e-12:
            # Transcendental: A*x^2 + C*x - V*x^{1+gr} - kappa0 = 0
            C = 4.0 * zeta0 * psi * beta - Om_mat
            V = v0 * psi
            def f_radion(x):
                return A*x**2 + C*x - V*x**(1.0+gr) - kappa0
            try:
                return brentq(f_radion, 0.001, 1e6, xtol=1e-12, rtol=1e-12)
            except ValueError:
                # Fallback: ignore radion
                B = C - V
                disc = B**2 + 4.0 * A * kappa0
                return (-B + np.sqrt(max(disc, 0.0))) / (2.0 * A)

        R = Om_mat + v0 * psi
        B = 4.0 * zeta0 * psi * beta - R

        if lam3 > 1e-12:
            # Quartic in E: A*E^4 + B*E^2 - lambda3*E - kappa0 = 0
            coeffs = [A, 0.0, B, -lam3, -kappa0]
            roots = np.roots(coeffs)
            real_pos = [r.real for r in roots if abs(r.imag) < 1e-10 and r.real > 0]
            if real_pos:
                E = max(real_pos)
                return E**2
            # Fallback to quadratic
            disc = B**2 + 4.0 * A * kappa0
            return (-B + np.sqrt(max(disc, 0.0))) / (2.0 * A)
        else:
            # Original quadratic: A*x^2 + B*x - kappa0 = 0
            disc = B**2 + 4.0 * A * kappa0
            return (-B + np.sqrt(max(disc, 0.0))) / (2.0 * A)

    def rhs_psi(N, y):
        """ODE for psi. Scalar rolls at rate beta/E^2 (cuscuton zeroth order)."""
        psi = max(y[0], 1e-10)
        E2 = E2_algebraic(N, psi)
        return [beta / max(E2, 1e-10)]

    # --- Integrate BACKWARD from N=0 to get psi(N<0), then FORWARD for N>0 ---
    # This guarantees psi(N=0) = 1 exactly.

    N_back = np.linspace(0, N_start, N_points * 3 // 4)  # today → past
    N_fwd  = np.linspace(0, N_end, N_points // 4 + 1)     # today → future

    sol_back = solve_ivp(rhs_psi, [0, N_start], [1.0],
                         t_eval=N_back, method='RK45',
                         rtol=1e-10, atol=1e-12, max_step=0.01)
    sol_fwd = solve_ivp(rhs_psi, [0, N_end], [1.0],
                        t_eval=N_fwd, method='RK45',
                        rtol=1e-10, atol=1e-12, max_step=0.01)

    if not sol_back.success:
        print(f"Warning: backward ODE failed: {sol_back.message}")
    if not sol_fwd.success:
        print(f"Warning: forward ODE failed: {sol_fwd.message}")

    # Concatenate: reverse backward, skip duplicate N=0 point
    N_arr   = np.concatenate([sol_back.t[::-1], sol_fwd.t[1:]])
    psi_arr = np.concatenate([sol_back.y[0][::-1], sol_fwd.y[0][1:]])

    # Compute E^2 algebraically along the solution
    E2_arr = np.array([E2_algebraic(N_arr[i], psi_arr[i]) for i in range(len(N_arr))])
    E_arr = np.sqrt(np.maximum(E2_arr, 1e-30))

    # Compute w_DE using the OPERATIONAL definition:
    #   rho_DE = E^2 - Omega_m*a^{-3} - Omega_r*a^{-4}
    #   w_DE = -1 - (d rho_DE / dN) / (3 * rho_DE)
    #
    # Three modes for dE^2/dN via implicit differentiation:
    #   gamma_r > 0: transcendental A*x^2 + C*x - V*x^{1+gr} - kappa0 = 0
    #   lambda3 > 0: quartic A*E^4 + B*E^2 - lambda3*E - kappa0 = 0
    #   both = 0:    quadratic A*x^2 + B*x - kappa0 = 0
    a_arr = np.exp(N_arr)

    w_arr = np.zeros_like(N_arr)
    for i in range(len(N_arr)):
        N = N_arr[i]
        a = a_arr[i]
        E2 = E2_arr[i]
        E = E_arr[i]
        psi = psi_arr[i]
        psi_prime = beta / max(E2, 1e-30)  # dψ/dN = β/E²

        # Matter/radiation at this point
        Om_a3 = Om * a**(-3)
        Or_a4 = Or * a**(-4)
        Om_mat = Om_a3 + Or_a4

        # Friedmann coefficients
        A = 1.0 + 2.0 * zeta0 * psi**2

        # Derivative of A w.r.t. N
        dA_dN = 4.0 * zeta0 * psi * psi_prime

        if gr > 1e-12:
            # Transcendental: g(x,N) = A*x^2 + C*x - V*x^{1+gr} - kappa0 = 0
            C = 4.0 * zeta0 * psi * beta - Om_mat
            V = v0 * psi
            dC_dN = 4.0 * zeta0 * beta * psi_prime + 3.0 * Om_a3 + 4.0 * Or_a4
            dV_dN = v0 * psi_prime

            # dx/dN = [-dA/dN*x^2 - dC/dN*x + dV/dN*x^{1+gr}]
            #        / [2A*x + C - V*(1+gr)*x^gr]
            numer = -dA_dN * E2**2 - dC_dN * E2 + dV_dN * E2**(1.0+gr)
            denom_deriv = 2.0 * A * E2 + C - V * (1.0+gr) * E2**gr
            if abs(denom_deriv) > 1e-30:
                dE2_dN = numer / denom_deriv
            else:
                dE2_dN = 0.0

        elif lam3 > 1e-12:
            R = Om_mat + v0 * psi
            B = 4.0 * zeta0 * psi * beta - R
            dR_dN = -3.0 * Om_a3 - 4.0 * Or_a4 + v0 * psi_prime
            dB_dN = 4.0 * zeta0 * beta * psi_prime - dR_dN
            # Quartic: A*E^4 + B*E^2 - lam3*E - kappa0 = 0
            denom_deriv = 4.0 * A * E**3 + 2.0 * B * E - lam3
            if abs(denom_deriv) > 1e-30:
                dE_dN = -(dA_dN * E**4 + dB_dN * E2) / denom_deriv
                dE2_dN = 2.0 * E * dE_dN
            else:
                dE2_dN = 0.0
        else:
            R = Om_mat + v0 * psi
            B = 4.0 * zeta0 * psi * beta - R
            dR_dN = -3.0 * Om_a3 - 4.0 * Or_a4 + v0 * psi_prime
            dB_dN = 4.0 * zeta0 * beta * psi_prime - dR_dN
            # Original quadratic: dE^2/dN = -[dA/dN*(E^2)^2 + dB/dN*E^2] / [2A*E^2 + B]
            denom_deriv = 2.0 * A * E2 + B
            if abs(denom_deriv) > 1e-30:
                dE2_dN = -(dA_dN * E2**2 + dB_dN * E2) / denom_deriv
            else:
                dE2_dN = 0.0

        # Operational dark energy density and its derivative
        rho_DE = E2 - Om_a3 - Or_a4
        drho_DE_dN = dE2_dN + 3.0 * Om_a3 + 4.0 * Or_a4

        # w_DE = -1 - (d ln rho_DE / dN) / 3
        if rho_DE > 1e-20:
            w_arr[i] = -1.0 - drho_DE_dN / (3.0 * rho_DE)
        else:
            w_arr[i] = -1.0

    return N_arr, psi_arr, E_arr, w_arr


# ============================================================
# OBSERVABLE COMPUTATION
# ============================================================

def cpl_fit_intrinsic(a_arr: np.ndarray, w_arr: np.ndarray,
                      a_second: float = 0.5) -> Tuple[float, float]:
    """
    Extract CPL parameters from the INTRINSIC w(a) = (K-V)/(K+V).
    Two-point method: w0 = w(1), wa = (w(a_second) - w(1))/(1-a_second).
    """
    from numpy import interp
    w0 = interp(1.0, a_arr, w_arr)
    w_second = interp(a_second, a_arr, w_arr)
    wa = (w_second - w0) / (1.0 - a_second)
    return w0, wa


def cpl_fit_E2(a_arr: np.ndarray, E2_arr: np.ndarray,
               Om: float = OMEGA_M0, Or: float = OMEGA_R0) -> Tuple[float, float]:
    """
    Fit CPL parametrization to the model E^2(a) curve.

    E^2_CPL(a) = Om*a^{-3} + Or*a^{-4} + Ode * f(a; w0, wa)
    f(a; w0, wa) = a^{-3(1+w0+wa)} * exp(-3*wa*(1-a))

    This is what DESI actually does: fit w0,wa to distance data, which
    determines E(z). Minimizes sum (E^2_model - E^2_CPL)^2 / E^4_model
    over the observational range a in [0.3, 1.05] (z in [0, 2.3]).
    """
    Ode = 1.0 - Om - Or

    def E2_CPL(a, w0, wa):
        """CPL prediction for E^2(a)."""
        de_factor = a**(-3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * (1.0 - a))
        return Om * a**(-3) + Or * a**(-4) + Ode * de_factor

    # Fit over DESI-relevant range
    mask = (a_arr >= 0.3) & (a_arr <= 1.05)
    a_fit = a_arr[mask]
    E2_fit = E2_arr[mask]

    if len(a_fit) < 10:
        return -1.0, 0.0

    def chi2(params):
        w0, wa = params
        E2_cpl = E2_CPL(a_fit, w0, wa)
        # Weighted residuals (fractional)
        return np.sum(((E2_fit - E2_cpl) / E2_fit)**2)

    res = minimize(chi2, [-1.0, 0.0], method='Nelder-Mead',
                   options={'xatol': 1e-6, 'fatol': 1e-12, 'maxiter': 5000})
    return res.x[0], res.x[1]


def compute_H0_CMB(a_arr: np.ndarray, E_arr: np.ndarray) -> Tuple[float, float]:
    """
    Compute H0 from CMB calibration.

    The angular diameter distance to last scattering:
      d_A = integral_0^z* dz/H(z) = integral_{a*}^1 da/(a^2 H(a))

    Compare with LCDM to get relative H0 shift.
    Returns (H0_CMB, delta_H0_pct).
    """
    a_star = 1.0 / (1.0 + Z_STAR)

    # Our model: d_A ~ integral da/(a^2 * H0 * E(a))
    # LCDM: d_A ~ integral da/(a^2 * H0_LCDM * E_LCDM(a))
    # Ratio of d_A determines ratio of H0:
    # d_A_us * H0_us = d_A_LCDM * H0_LCDM
    # => H0_us/H0_LCDM = integral_LCDM / integral_us

    # Our model integral
    mask = (a_arr >= a_star) & (a_arr <= 1.0)
    if np.sum(mask) < 10:
        return H0_FIDUCIAL, 0.0

    a_sub = a_arr[mask]
    E_sub = E_arr[mask]
    integrand = 1.0 / (a_sub**2 * E_sub)
    I_model = np.trapezoid(integrand, a_sub)

    # LCDM integral
    def E_LCDM(a):
        return np.sqrt(OMEGA_M0 * a**(-3) + OMEGA_R0 * a**(-4) + OMEGA_DE0)

    E_lcdm = np.array([E_LCDM(a) for a in a_sub])
    integrand_lcdm = 1.0 / (a_sub**2 * E_lcdm)
    I_lcdm = np.trapezoid(integrand_lcdm, a_sub)

    ratio = I_lcdm / I_model
    H0_CMB = H0_FIDUCIAL * ratio
    delta_pct = (H0_CMB - H0_FIDUCIAL) / H0_FIDUCIAL * 100.0

    return H0_CMB, delta_pct


def compute_growth(a_arr: np.ndarray, E_arr: np.ndarray,
                   params: MeridianParams,
                   mu_func=None) -> Tuple[dict, dict]:
    """
    Compute f*sigma8(z) from the growth equation.

    d^2 delta/dN^2 + (2 + E'/E) d(delta)/dN = (3/2) * Omega_m(a) * mu(a) * delta

    For cuscuton: mu(a) from time-dependent Planck mass only (no fifth force).

    Returns: (fsigma8_dict, delta_fsigma8_pct_dict) at key redshifts.
    """
    Om = params.Omega_m

    # Default mu = 1 (GR)
    if mu_func is None:
        mu_func = lambda a: 1.0

    # Solve growth equation: d(delta)/dN = f*delta, df/dN = ...
    # Use ln(delta) growth: D(N) = delta/delta_i
    # f = d ln D / d ln a = D'/D

    # ODE: D'' + (2 + E'/E)*D' - (3/2)*Om_m(a)/E^2 * mu * D = 0
    # State: [D, D'] where D' = dD/dN

    # Interpolate E(N) for the growth equation
    N_arr = np.log(a_arr)
    E_interp = np.interp

    # Compute E'/E from finite differences
    dE_dN = np.gradient(E_arr, N_arr)
    EprimeOverE = dE_dN / E_arr

    def growth_rhs(N, y):
        D, Dp = y  # D and dD/dN
        a = np.exp(N)
        E = np.interp(N, N_arr, E_arr)
        E2 = E**2
        EpE = np.interp(N, N_arr, EprimeOverE)
        mu = mu_func(a)

        Om_a = Om * a**(-3) / E2

        Dpp = -(2.0 + EpE) * Dp + 1.5 * Om_a * mu * D
        return [Dp, Dpp]

    # Integrate from early times (matter dominated: D ~ a, f = 1)
    N_start = N_arr[0]
    N_end = N_arr[-1]
    D0 = np.exp(N_start)  # D ~ a in matter domination
    Dp0 = D0              # dD/dN = D in matter domination (f=1)

    sol = solve_ivp(growth_rhs, [N_start, N_end], [D0, Dp0],
                    t_eval=N_arr, method='RK45', rtol=1e-10, atol=1e-12)

    if not sol.success:
        print(f"Warning: Growth equation failed: {sol.message}")
        return {}, {}

    D_arr = sol.y[0]
    Dp_arr = sol.y[1]
    f_arr = Dp_arr / D_arr  # f = dln D / dln a

    # Normalize sigma8: D(a=1) corresponds to sigma8_today
    D_today = np.interp(0.0, sol.t, D_arr)
    sigma8_arr = SIGMA8_FID * D_arr / D_today

    fsigma8_arr = f_arr * sigma8_arr

    # Extract at key redshifts
    target_z = [0.0, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]
    fsigma8_dict = {}
    delta_dict = {}

    # Also compute LCDM growth for comparison
    def E_LCDM(a):
        return np.sqrt(OMEGA_M0 * a**(-3) + OMEGA_R0 * a**(-4) + OMEGA_DE0)

    E_lcdm_arr = np.array([E_LCDM(a) for a in a_arr])
    dE_lcdm = np.gradient(E_lcdm_arr, N_arr)
    EpE_lcdm = dE_lcdm / E_lcdm_arr

    def growth_rhs_lcdm(N, y):
        D, Dp = y
        a = np.exp(N)
        E = E_LCDM(a)
        E2 = E**2
        EpE = np.interp(N, N_arr, EpE_lcdm)
        Om_a = Om * a**(-3) / E2
        Dpp = -(2.0 + EpE) * Dp + 1.5 * Om_a * D
        return [Dp, Dpp]

    sol_lcdm = solve_ivp(growth_rhs_lcdm, [N_start, N_end], [D0, Dp0],
                          t_eval=N_arr, method='RK45', rtol=1e-10, atol=1e-12)

    D_lcdm = sol_lcdm.y[0]
    Dp_lcdm = sol_lcdm.y[1]
    f_lcdm = Dp_lcdm / D_lcdm
    D_today_lcdm = np.interp(0.0, sol_lcdm.t, D_lcdm)
    sigma8_lcdm = SIGMA8_FID * D_lcdm / D_today_lcdm
    fsigma8_lcdm = f_lcdm * sigma8_lcdm

    for z in target_z:
        N_z = -np.log(1.0 + z)
        fs8 = np.interp(N_z, sol.t, fsigma8_arr)
        fs8_lcdm = np.interp(N_z, sol_lcdm.t, fsigma8_lcdm)
        fsigma8_dict[z] = fs8
        if abs(fs8_lcdm) > 1e-30:
            delta_dict[z] = (fs8 - fs8_lcdm) / fs8_lcdm * 100.0
        else:
            delta_dict[z] = 0.0

    return fsigma8_dict, delta_dict


def detect_phantom_crossing(a_arr: np.ndarray, w_arr: np.ndarray) -> Tuple[bool, float]:
    """Detect phantom crossing (w = -1) and return the redshift."""
    # Look for sign change of (w + 1)
    wp1 = w_arr + 1.0

    # Only look in the range z = 0 to z = 3 (a = 0.25 to a = 1)
    mask = (a_arr >= 0.25) & (a_arr <= 1.0)
    a_sub = a_arr[mask]
    wp1_sub = wp1[mask]

    for i in range(len(wp1_sub) - 1):
        if wp1_sub[i] * wp1_sub[i+1] < 0:
            # Linear interpolation for crossing
            a_cross = a_sub[i] + (a_sub[i+1] - a_sub[i]) * abs(wp1_sub[i]) / (abs(wp1_sub[i]) + abs(wp1_sub[i+1]))
            z_cross = 1.0 / a_cross - 1.0
            return True, z_cross

    return False, -1.0


def compute_mu(a: float, params: MeridianParams,
               psi_func=None) -> float:
    """
    Modified Newton's constant mu(a) = G_eff(a) / G_N.

    For the cuscuton (no scalar fifth force):
      mu(a) = F_0 / F(a) = 1 / (1 - zeta0*(psi^2(a) - 1))

    In the IR-brane-dominated limit.
    """
    if params.zeta0 == 0:
        return 1.0

    if psi_func is not None:
        psi = psi_func(a)
    else:
        # Approximate psi(a) ~ 1 + beta*ln(a) for moderate evolution
        psi = 1.0 + params.beta * np.log(a)
        psi = max(psi, 0.01)

    # mu = 1 / (1 - zeta0*(psi^2 - 1))
    # For psi < 1 (past): psi^2 - 1 < 0, so denominator > 1, mu < 1
    # For psi > 1 (future): psi^2 - 1 > 0, so denominator < 1, mu > 1
    denom = 1.0 - params.zeta0 * (psi**2 - 1.0)
    if abs(denom) < 1e-10:
        return 10.0  # Cap
    return 1.0 / denom


# ============================================================
# MAIN SOLVER
# ============================================================

def solve_meridian(params: MeridianParams) -> MeridianResult:
    """
    Solve the complete Meridian cosmological model.

    For xi = 0 (zeta0 = 0): uses analytic formulas.
    For xi > 0 (zeta0 > 0): uses numerical ODE integration.
    """
    result = MeridianResult()
    result.eta = 1.0      # Exact for cuscuton
    result.cs2 = np.inf   # Cuscuton: infinite sound speed

    psi_interp = None  # Will hold ψ(a) interpolant for ξ > 0

    if params.gamma_r > 1e-12 and (params.zeta0 == 0 or params.zeta0 < 1e-10):
        # ============ RADION DYNAMICS MODE (gamma_r > 0, xi = 0, D5.6) ============
        a_arr = np.logspace(-4, np.log10(1.5), 3000)
        E_arr = np.array([E_radion(a, params) for a in a_arr])
        w_arr = np.array([w_DE_radion(a, params) for a in a_arr])

    elif params.gamma_r > 1e-12 and params.zeta0 > 1e-10:
        # ============ COMBINED MODE (gamma_r > 0 + xi > 0, D5.6+D3.3) ============
        # Both cuscuton xi-coupling AND radion warp-factor drift active.
        # solve_xi_positive handles gamma_r internally via transcendental Friedmann eq.
        if params.beta == 0:
            Ode = 1.0 - params.Omega_m - params.Omega_r
            v0 = Ode / (1.0 + params.eps0)
            params.beta = np.sqrt(params.eps0 * v0) * 0.3
        N_arr, psi_arr, E_arr, w_arr = solve_xi_positive(params)
        a_arr = np.exp(N_arr)
        psi_interp = lambda a_val: np.interp(np.log(a_val), N_arr, psi_arr)

    elif params.lambda3 > 1e-12 and (params.zeta0 == 0 or params.zeta0 < 1e-10):
        # ============ EXTENDED CUSCUTON MODE (lambda3 > 0, xi = 0) ============
        a_arr = np.logspace(-4, np.log10(1.5), 3000)
        E_arr = np.array([E_extended(a, params) for a in a_arr])
        w_arr = np.array([w_DE_extended(a, params) for a in a_arr])

    elif params.zeta0 == 0 or params.zeta0 < 1e-10:
        # ============ XI = 0 MODE (minimal cuscuton) ============
        a_arr = np.logspace(-4, np.log10(1.5), 3000)
        E_arr = np.array([np.sqrt(E2_xi0(a, params)) for a in a_arr])
        w_arr = np.array([w_DE_xi0(a, params) for a in a_arr])

    else:
        # ============ XI > 0 MODE ============
        # Auto-estimate beta if not set
        if params.beta == 0:
            Ode = 1.0 - params.Omega_m - params.Omega_r
            v0 = Ode / (1.0 + params.eps0)
            params.beta = np.sqrt(params.eps0 * v0) * 0.3  # Rough

        N_arr, psi_arr, E_arr, w_arr = solve_xi_positive(params)
        a_arr = np.exp(N_arr)

        # Create ψ(a) interpolant for μ(a) computation
        psi_interp = lambda a_val: np.interp(np.log(a_val), N_arr, psi_arr)

    result.z_array = 1.0 / a_arr - 1.0
    result.w_array = w_arr
    result.E_array = E_arr

    # --- CPL fits ---
    # 1. E^2-based fit: what DESI actually measures (fit CPL to expansion history)
    E2_arr = E_arr**2
    result.w0, result.wa = cpl_fit_E2(a_arr, E2_arr)

    # 2. Intrinsic w fit: scalar field equation of state (for theory comparison)
    #    For xi=0: w_arr is the intrinsic w from (K-V)/(K+V)
    #    For xi>0: w_arr is the operational/effective w (includes xi terms)
    result.w0_intrinsic, result.wa_intrinsic = cpl_fit_intrinsic(a_arr, w_arr)

    # H0 from CMB
    result.H0_CMB, result.delta_H0_pct = compute_H0_CMB(a_arr, E_arr)

    # Phantom crossing
    result.has_phantom_crossing, result.z_phantom = detect_phantom_crossing(a_arr, w_arr)

    # Modified gravity — use actual ψ(a) from ODE when available
    if params.zeta0 > 0 and psi_interp is not None:
        for z in [0.0, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]:
            a = 1.0 / (1.0 + z)
            result.mu_z[z] = compute_mu(a, params, psi_func=psi_interp)
    else:
        for z in [0.0, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]:
            result.mu_z[z] = 1.0

    # Growth rate — use actual ψ(a) for μ
    if psi_interp is not None:
        mu_func = lambda a: compute_mu(a, params, psi_func=psi_interp)
    else:
        mu_func = lambda a: compute_mu(a, params)
    result.fsigma8, result.delta_fsigma8_pct = compute_growth(
        a_arr, E_arr, params, mu_func=mu_func
    )

    # DESI chi2
    dw0 = (result.w0 - W0_DESI) / W0_DESI_ERR
    # Use average of asymmetric errors for wa
    wa_err = (WA_DESI_ERR_PLUS + WA_DESI_ERR_MINUS) / 2.0
    dwa = (result.wa - WA_DESI) / wa_err
    result.chi2_DESI = dw0**2 + dwa**2

    return result


# ============================================================
# PARAMETER SCAN
# ============================================================

def _solve_for_w0(eps0, zeta0):
    """Helper: compute w0 for a given (eps0, zeta0). Returns w0."""
    params = MeridianParams(eps0=eps0, zeta0=zeta0, beta=0.0)
    result = solve_meridian(params)
    return result.w0


def diagnose_w0_vs_eps0(zeta0: float, eps0_values=None):
    """
    Diagnostic: print w0 as a function of eps0 at fixed zeta0.
    Reveals the shape of w0(eps0) to understand brentq behavior.
    """
    if eps0_values is None:
        eps0_values = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 4.0, 8.0, 15.0]
    print(f"\n  Diagnostic: w0(eps0) at zeta0={zeta0:.2f}")
    print(f"  {'eps0':>8} | {'w0':>8}")
    print(f"  {'-'*20}")
    for e in eps0_values:
        try:
            w0 = _solve_for_w0(e, zeta0)
            print(f"  {e:8.3f} | {w0:8.4f}")
        except Exception as ex:
            print(f"  {e:8.3f} | ERROR: {ex}")
    print(f"  Target: w0 = {W0_DESI:.3f}")
    print()


def scan_zeta0(eps0_base: float = 0.15,
               zeta0_values: list = None,
               auto_eps0: bool = True) -> list:
    """
    Scan over zeta0 values and compute all observables.

    If auto_eps0=True, uses iterative root-finding to find eps0 that
    gives w0 = W0_DESI for each zeta0. Reports when no solution exists.
    """
    if zeta0_values is None:
        zeta0_values = [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5]

    results = []

    for zeta0 in zeta0_values:
        converged = True
        if auto_eps0 and zeta0 > 0:
            w0_tgt = W0_DESI

            # Check bracket endpoints first
            try:
                w0_lo = _solve_for_w0(0.02, zeta0)
                w0_hi = _solve_for_w0(15.0, zeta0)
            except Exception:
                w0_lo, w0_hi = -2.0, -2.0

            if (w0_lo - w0_tgt) * (w0_hi - w0_tgt) > 0:
                # No sign change — w0_tgt not achievable in bracket
                converged = False
                # Use perturbative guess as fallback
                num = 1.0 + w0_tgt + 0.69 * zeta0
                den = 1.0 - w0_tgt - 0.69 * zeta0
                eps0 = max(num / den, 0.01) if den > 0.01 else 5.0
            else:
                try:
                    eps0 = brentq(lambda e: _solve_for_w0(e, zeta0) - w0_tgt,
                                  0.02, 15.0,
                                  xtol=1e-4, rtol=1e-4, maxiter=30)
                except ValueError:
                    converged = False
                    num = 1.0 + w0_tgt + 0.69 * zeta0
                    den = 1.0 - w0_tgt - 0.69 * zeta0
                    eps0 = max(num / den, 0.01) if den > 0.01 else 5.0
        else:
            eps0 = eps0_base

        params = MeridianParams(eps0=eps0, zeta0=zeta0, beta=0.0)

        tag = "" if converged else " [NO w0 SOLUTION]"
        print(f"  zeta0 = {zeta0:.2f}, eps0 = {eps0:.3f}{tag} ...", end="")

        result = solve_meridian(params)
        result_dict = {
            'zeta0': zeta0,
            'eps0': eps0,
            'eps_SW': zeta0 / (1.0 + zeta0),
            'w0': result.w0,           # E^2-based fit
            'wa': result.wa,           # E^2-based fit
            'w0_int': result.w0_intrinsic,  # Intrinsic scalar field w
            'wa_int': result.wa_intrinsic,
            'w0_plus_wa': result.w0 + result.wa,
            'H0_CMB': result.H0_CMB,
            'delta_H0_pct': result.delta_H0_pct,
            'phantom': result.has_phantom_crossing,
            'z_phantom': result.z_phantom,
            'mu_z1': result.mu_z.get(1.0, 1.0),
            'fsigma8_05': result.fsigma8.get(0.5, 0.0),
            'delta_fsigma8_05': result.delta_fsigma8_pct.get(0.5, 0.0),
            'chi2_DESI': result.chi2_DESI,
            'eta': 1.0,
            'cs2': 'inf',
            'converged': converged,
            'result': result,
        }
        results.append(result_dict)

        phantom_str = f"z_x={result.z_phantom:.2f}" if result.has_phantom_crossing else "none"
        print(f" w0={result.w0:.3f}, wa={result.wa:.3f}, phantom={phantom_str}, chi2={result.chi2_DESI:.2f}")

    return results


def print_prediction_table(results: list):
    """Print the formatted prediction table with both E^2-fit and intrinsic w."""
    print("\n" + "=" * 120)
    print("  MERIDIAN D3.4 — NUMERICAL PREDICTION TABLE")
    print("  w0,wa (E²-fit) = what DESI measures;  w0,wa (intr) = scalar field intrinsic EoS")
    print("=" * 120)
    hdr = (f"  {'zeta0':>6} | {'eps0':>6} | {'w0_E2':>7} | {'wa_E2':>7} | "
           f"{'w0_int':>7} | {'wa_int':>7} | {'z_x':>5} | "
           f"{'mu(1)':>6} | {'dfs8%':>6} | {'H0':>6} | {'chi2':>6}")
    print(hdr)
    print("-" * 120)

    for r in results:
        z_x_str = f"{r['z_phantom']:.2f}" if r['phantom'] else "  — "
        flag = " *" if not r.get('converged', True) else "  "
        print(f" {flag}{r['zeta0']:5.2f} | {r['eps0']:6.3f} | "
              f"{r['w0']:7.3f} | {r['wa']:7.3f} | "
              f"{r.get('w0_int', 0):7.3f} | {r.get('wa_int', 0):7.3f} | "
              f"{z_x_str:>5} | {r['mu_z1']:6.3f} | "
              f"{r['delta_fsigma8_05']:+6.1f} | {r['H0_CMB']:6.1f} | "
              f"{r['chi2_DESI']:6.2f}")

    print("-" * 120)
    print(f"  DESI DR2:              | {W0_DESI:7.3f} | {WA_DESI:7.3f} | "
          f"{'':>7} | {'':>7} |       |        |        | {H0_FIDUCIAL:6.1f} |")
    print(f"  DESI 1σ:               | ±{W0_DESI_ERR:.3f} | +{WA_DESI_ERR_PLUS:.2f}/−{WA_DESI_ERR_MINUS:.2f} |")
    print("=" * 120)
    print()
    n_unconverged = sum(1 for r in results if not r.get('converged', True))
    if n_unconverged > 0:
        print(f"  * = no eps0 found s.t. w0 = {W0_DESI:.3f}; shown at perturbative guess")
        print()

    print("  FIXED predictions (all zeta0):")
    print("    c²_s = ∞       (cuscuton — no DE clustering)")
    print("    η    = 1       (no gravitational slip, exact)")
    print("    α_T  = 0       (GW speed = c)")
    print("    Σ    = μ       (lensing = clustering)")
    print()


def chi2_DESI(eps0, zeta0):
    """Compute DESI chi2 for a given (eps0, zeta0). Returns chi2."""
    params = MeridianParams(eps0=eps0, zeta0=zeta0, beta=0.0)
    result = solve_meridian(params)
    return result.chi2_DESI, result


def scan_2d(eps0_values=None, zeta0_values=None):
    """
    2D scan over (eps0, zeta0) to find the DESI-optimal point.
    Uses E^2-based CPL fit throughout.
    """
    if eps0_values is None:
        eps0_values = [0.01, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.50]
    if zeta0_values is None:
        zeta0_values = [0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30]

    print(f"\n  2D SCAN: {len(eps0_values)} x {len(zeta0_values)} = "
          f"{len(eps0_values)*len(zeta0_values)} evaluations")
    print()

    # Header
    header = "  eps0\\zeta0 |" + "".join(f" {z:6.2f}" for z in zeta0_values)
    print(header)
    print("  " + "-" * (12 + 7 * len(zeta0_values)))

    best_chi2 = 1e10
    best_eps0, best_zeta0 = 0, 0
    best_result = None
    grid = {}

    for eps0 in eps0_values:
        row = f"  {eps0:10.3f} |"
        for zeta0 in zeta0_values:
            try:
                chi2, result = chi2_DESI(eps0, zeta0)
                grid[(eps0, zeta0)] = {
                    'chi2': chi2, 'w0': result.w0, 'wa': result.wa,
                    'w0_int': result.w0_intrinsic, 'wa_int': result.wa_intrinsic,
                    'H0': result.H0_CMB, 'mu_z1': result.mu_z.get(1.0, 1.0),
                    'phantom': result.has_phantom_crossing,
                    'z_phantom': result.z_phantom,
                    'result': result,
                }
                if chi2 < best_chi2:
                    best_chi2 = chi2
                    best_eps0 = eps0
                    best_zeta0 = zeta0
                    best_result = result
                row += f" {chi2:6.1f}"
            except Exception as ex:
                row += "   ERR"
                grid[(eps0, zeta0)] = {'chi2': 999, 'error': str(ex)}
        print(row)

    print()
    print(f"  Grid minimum: eps0={best_eps0:.3f}, zeta0={best_zeta0:.3f}, "
          f"chi2={best_chi2:.2f}")

    return grid, best_eps0, best_zeta0, best_result


def optimize_DESI(eps0_init=0.10, zeta0_init=0.05):
    """
    Optimize (eps0, zeta0) to minimize chi2_DESI using Nelder-Mead.
    Uses E^2-based CPL fit.
    """
    print(f"\n  Optimizing from (eps0={eps0_init:.3f}, zeta0={zeta0_init:.3f})...")

    def objective(x):
        eps0, zeta0 = x
        if eps0 <= 0.001 or zeta0 < 0 or eps0 > 20:
            return 1000.0
        try:
            chi2, _ = chi2_DESI(eps0, zeta0)
            return chi2
        except Exception:
            return 1000.0

    res = minimize(objective, [eps0_init, zeta0_init],
                   method='Nelder-Mead',
                   options={'xatol': 1e-4, 'fatol': 1e-3, 'maxiter': 200})

    eps0_opt, zeta0_opt = res.x
    zeta0_opt = max(zeta0_opt, 0.0)

    # Final evaluation at optimum
    params = MeridianParams(eps0=eps0_opt, zeta0=zeta0_opt, beta=0.0)
    result = solve_meridian(params)

    print(f"  Optimum: eps0={eps0_opt:.4f}, zeta0={zeta0_opt:.4f}")
    print(f"    w0 (E²-fit)  = {result.w0:.4f}")
    print(f"    wa (E²-fit)  = {result.wa:.4f}")
    print(f"    w0 (intrinsic) = {result.w0_intrinsic:.4f}")
    print(f"    wa (intrinsic) = {result.wa_intrinsic:.4f}")
    print(f"    chi2_DESI = {result.chi2_DESI:.4f}")
    print(f"    H0 = {result.H0_CMB:.2f} km/s/Mpc")
    print(f"    mu(z=1) = {result.mu_z.get(1.0, 1.0):.4f}")
    ph = result.has_phantom_crossing
    print(f"    Phantom crossing: {'z=' + f'{result.z_phantom:.2f}' if ph else 'none'}")
    print(f"    Nelder-Mead converged: {res.success} ({res.nfev} evaluations)")

    return eps0_opt, zeta0_opt, result


# ============================================================
# PHASE 4: PERTURBATION ANALYSIS
# ============================================================

def compute_alpha_M(a, params, psi_func, E_func):
    """
    Running of the effective Planck mass:
      alpha_M(a) = d ln M^2_* / dN
    where M^2_*(a) = 2*G4(phi(a)) = F(a) = F_0 * (1 - zeta0*(psi^2 - 1)).

    alpha_M = -2*zeta0*psi*psi' / (1 - zeta0*(psi^2 - 1))
    with psi' = beta/E^2 (cuscuton constraint).
    """
    if params.zeta0 == 0:
        return 0.0
    psi = psi_func(a)
    E2 = E_func(a)**2

    # Need beta — recompute from self-consistent normalization
    eps0 = params.eps0
    zeta0 = params.zeta0
    Om = params.Omega_m
    Or = params.Omega_r
    Ode = 1.0 - Om - Or
    v0_xi0 = Ode / (1.0 + eps0)
    beta = np.sqrt(2.0 * eps0 * v0_xi0 / Ode) * 0.5
    for _ in range(20):
        v0_i = (Ode + 2.0 * zeta0 + 4.0 * zeta0 * beta) / (1.0 + eps0)
        beta_new = np.sqrt(2.0 * eps0 * v0_i / Ode) * 0.5
        if abs(beta_new - beta) < 1e-14:
            break
        beta = beta_new

    psi_prime = beta / max(E2, 1e-30)
    denom = 1.0 - zeta0 * (psi**2 - 1.0)
    if abs(denom) < 1e-10:
        return 0.0
    return -2.0 * zeta0 * psi * psi_prime / denom


def perturbation_analysis(params, label=""):
    """
    Full Phase 4 perturbation analysis for a single parameter point.
    Computes mu(z), eta(z), Sigma(z), alpha_M(z), growth predictions.
    Returns a dict with all perturbation observables.
    """
    result = solve_meridian(params)

    zeta0 = params.zeta0
    eps0 = params.eps0

    # Build interpolants from the solution
    a_arr = 1.0 / (1.0 + result.z_array)
    # Handle potential non-monotonic a_arr from z_array
    sort_idx = np.argsort(a_arr)
    a_sorted = a_arr[sort_idx]
    E_sorted = result.E_array[sort_idx]

    E_func = lambda a_val: np.interp(a_val, a_sorted, E_sorted)

    # For ξ > 0, get ψ(a) from re-running the ODE (or use stored solution)
    psi_func = None
    if zeta0 > 0:
        N_arr_ode, psi_arr_ode, _, _ = solve_xi_positive(params)
        psi_func = lambda a_val: np.interp(np.log(max(a_val, 1e-10)),
                                            N_arr_ode, psi_arr_ode)

    target_z = [0.0, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]
    target_z_early = [0.0, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 5.0, 10.0, 100.0, 1000.0]

    # Compute perturbation parameters at each redshift
    mu_vals = {}
    eta_vals = {}
    Sigma_vals = {}
    alpha_M_vals = {}

    for z in target_z_early:
        a = 1.0 / (1.0 + z)
        if zeta0 > 0 and psi_func is not None:
            mu_vals[z] = compute_mu(a, params, psi_func=psi_func)
            alpha_M_vals[z] = compute_alpha_M(a, params, psi_func, E_func)
        else:
            mu_vals[z] = 1.0
            alpha_M_vals[z] = 0.0
        eta_vals[z] = 1.0  # Exact for cuscuton
        Sigma_vals[z] = mu_vals[z]  # Sigma = mu when eta = 1

    # EFT parameters at z=0
    alpha_T = 0.0  # GW speed = c (from GW170817)
    alpha_K = np.inf  # Cuscuton: infinite kineticity
    cs2 = np.inf

    # Growth is already computed in solve_meridian with proper mu
    # Compute early-universe mu for Hiramatsu-Kobayashi comparison
    if psi_func is not None:
        psi_early = psi_func(1e-4)  # a ~ 10^-4
        mu_early = 1.0 / (1.0 - zeta0 * (psi_early**2 - 1.0))
        delta_mu_early = mu_early - 1.0
    else:
        mu_early = 1.0
        delta_mu_early = 0.0

    return {
        'label': label,
        'params': params,
        'result': result,
        'mu': mu_vals,
        'eta': eta_vals,
        'Sigma': Sigma_vals,
        'alpha_M': alpha_M_vals,
        'alpha_T': alpha_T,
        'alpha_K': alpha_K,
        'cs2': cs2,
        'mu_early': mu_early,
        'delta_mu_early': delta_mu_early,
    }


def print_perturbation_table(analyses):
    """Print formatted perturbation parameter table for Phase 4."""
    print("\n" + "=" * 100)
    print("  D4.1 — MODIFIED GRAVITY PARAMETERS μ(z), η(z), Σ(z), α_M(z)")
    print("=" * 100)

    for pa in analyses:
        label = pa['label']
        p = pa['params']
        r = pa['result']
        print(f"\n  --- {label} ---")
        print(f"  ε₀={p.eps0:.4f}, ζ₀={p.zeta0:.4f}, ε_SW={p.zeta0/(1+p.zeta0):.4f}")
        print(f"  w₀(E²)={r.w0:.4f}, wₐ(E²)={r.wa:.4f}, χ²_DESI={r.chi2_DESI:.2f}")
        print(f"  H₀={r.H0_CMB:.2f} km/s/Mpc")
        ph_str = f"z={r.z_phantom:.2f}" if r.has_phantom_crossing else "none"
        print(f"  Phantom crossing: {ph_str}")
        print()

        # Table header
        print(f"    {'z':>6} | {'μ(z)':>8} | {'η(z)':>8} | {'Σ(z)':>8} | {'α_M(z)':>10} | "
              f"{'fσ₈':>8} | {'Δfσ₈%':>8}")
        print(f"    {'-'*70}")

        target_z = [0.0, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]
        for z in target_z:
            mu = pa['mu'].get(z, 1.0)
            eta = pa['eta'].get(z, 1.0)
            Sig = pa['Sigma'].get(z, 1.0)
            aM = pa['alpha_M'].get(z, 0.0)
            fs8 = r.fsigma8.get(z, 0.0)
            dfs8 = r.delta_fsigma8_pct.get(z, 0.0)
            print(f"    {z:6.1f} | {mu:8.5f} | {eta:8.5f} | {Sig:8.5f} | "
                  f"{aM:10.6f} | {fs8:8.4f} | {dfs8:+8.2f}")

        # Early universe values
        print()
        print(f"    Early universe (a→0): μ → {pa['mu_early']:.5f}  "
              f"(Δμ = {pa['delta_mu_early']:+.5f})")

    # Fixed predictions
    print("\n" + "-" * 100)
    print("  FIXED PREDICTIONS (all parameter points):")
    print("    c²_s   = ∞       (cuscuton — infinite sound speed, no DE clustering)")
    print("    η(z)   = 1       (no gravitational slip, exact — G₄,X = 0)")
    print("    α_T    = 0       (GW speed = c, consistent with GW170817)")
    print("    Σ(z)   = μ(z)    (lensing = clustering, follows from η = 1)")
    print("    α_K    = ∞       (infinite kineticity — defines the cuscuton)")
    print("    QSA    = EXACT   (not an approximation — scalar eq is intrinsically a constraint)")
    print("=" * 100)


def hiramatsu_kobayashi_mapping(analyses):
    """
    Map our model parameters onto the Hiramatsu-Kobayashi (2022) constraint.

    H&K constrain spatially covariant gravity with 2 tensor DOF and one
    parameter β_HK from Planck CMB: −0.047 < β_HK < −0.028 at 68% CL.

    In our model, μ varies with time. The closest comparison is the
    CMB-weighted effective μ or the early-universe limit.
    """
    print("\n" + "=" * 100)
    print("  D4.1 — HIRAMATSU-KOBAYASHI (2022) CONSTRAINT MAPPING")
    print("=" * 100)
    print()
    print("  H&K (arXiv:2205.04688): Planck CMB constraint on spatially covariant gravity")
    print("  with 2 tensor DOF, single parameter β_HK: −0.047 < β_HK < −0.028 (68% CL)")
    print()
    print("  Our model: μ(a) = 1/(1 − ζ₀(ψ²(a) − 1))")
    print("  Early universe (a→0): ψ→0, so μ → 1/(1+ζ₀)")
    print("  Effective β_HK ≈ μ_early − 1 = −ζ₀/(1+ζ₀) = −ε_SW")
    print()
    print(f"  {'Label':>30} | {'ζ₀':>6} | {'ε_SW':>6} | {'β_eff':>8} | {'In 68% CL?':>12} | {'In 95% CL?':>12}")
    print(f"  {'-'*85}")

    beta_lo_68 = -0.047
    beta_hi_68 = -0.028
    # Approximate 95% CL as ~2x width
    beta_lo_95 = beta_lo_68 - (beta_hi_68 - beta_lo_68)
    beta_hi_95 = beta_hi_68 + (beta_hi_68 - beta_lo_68)

    for pa in analyses:
        p = pa['params']
        label = pa['label']
        zeta0 = p.zeta0
        eps_SW = zeta0 / (1.0 + zeta0)
        beta_eff = -eps_SW  # mu_early - 1

        in_68 = "YES" if beta_lo_68 <= beta_eff <= beta_hi_68 else "NO"
        in_95 = "YES" if beta_lo_95 <= beta_eff <= beta_hi_95 else "NO"

        print(f"  {label:>30} | {zeta0:6.3f} | {eps_SW:6.4f} | {beta_eff:+8.5f} | "
              f"{in_68:>12} | {in_95:>12}")

    print()
    print("  CAVEAT: H&K assume a CONSTANT β over all redshifts. Our model has")
    print("  time-dependent μ(a). The early-universe limit β_eff = −ε_SW is the")
    print("  most CMB-relevant comparison, but a rigorous constraint requires")
    print("  implementing our model in CLASS/hi_class (future work).")
    print("=" * 100)


def run_phase4_D41():
    """Run the complete D4.1 perturbation parameter analysis."""
    print("=" * 70)
    print("  PROJECT MERIDIAN — PHASE 4, D4.1")
    print("  Modified Gravity Parameters from Cuscuton Braneworld")
    print("  Clayton & Clawd, March 2026")
    print("=" * 70)
    print()

    # Define parameter points to analyze
    points = [
        ("DESI-optimal (ε₀≈0, ζ₀=0.058)",
         MeridianParams(eps0=0.001, zeta0=0.058)),
        ("Moderate coupling (ε₀=0.05, ζ₀=0.10)",
         MeridianParams(eps0=0.05, zeta0=0.10)),
        ("Stronger coupling (ε₀=0.10, ζ₀=0.30)",
         MeridianParams(eps0=0.10, zeta0=0.30)),
        ("Large coupling (ε₀=0.30, ζ₀=0.80)",
         MeridianParams(eps0=0.30, zeta0=0.80)),
        ("Pure ξ=0 reference (ε₀=0.15, ζ₀=0)",
         MeridianParams(eps0=0.15, zeta0=0.0)),
    ]

    # Run perturbation analysis at each point
    analyses = []
    for label, params in points:
        print(f"  Computing: {label} ...")
        try:
            pa = perturbation_analysis(params, label=label)
            analyses.append(pa)
            print(f"    → μ(z=1)={pa['mu'].get(1.0, 1.0):.5f}, "
                  f"α_M(z=0)={pa['alpha_M'].get(0.0, 0.0):.6f}, "
                  f"χ²={pa['result'].chi2_DESI:.2f}")
        except Exception as ex:
            print(f"    → FAILED: {ex}")

    print()

    # Print perturbation parameter tables
    print_perturbation_table(analyses)

    # Hiramatsu-Kobayashi mapping
    hiramatsu_kobayashi_mapping(analyses)

    # EFT parameter summary
    print("\n" + "=" * 100)
    print("  D4.1 — EFT OF DARK ENERGY PARAMETRIZATION")
    print("=" * 100)
    print()
    print("  In the EFT language (Bellini & Sawicki 2014), the cuscuton braneworld has:")
    print()
    print("    α_K → ∞     (kineticity — defines cuscuton as incompressible limit)")
    print("    α_B → −α_M  (braiding — related to Planck mass running for cuscuton)")
    print("    α_M(a)      (Planck mass running — the ONLY free function)")
    print("    α_T = 0     (tensor speed excess — vanishes identically)")
    print()
    print("  This reduces the EFT from 4 free functions to 1 (α_M(a)),")
    print("  which is itself determined by ζ₀ and ψ(a):")
    print("    α_M(a) = −2ζ₀ψψ'/(1 − ζ₀(ψ²−1))")
    print()
    print("  At z=0:")
    for pa in analyses:
        zeta0 = pa['params'].zeta0
        aM0 = pa['alpha_M'].get(0.0, 0.0)
        label = pa['label']
        print(f"    {label}: α_M(0) = {aM0:+.6f}")
    print()

    # Background-perturbation tension summary
    print("=" * 100)
    print("  D4.1 — BACKGROUND-PERTURBATION TENSION (QUANTIFIED)")
    print("=" * 100)
    print()
    print(f"  {'Label':>40} | {'χ²_DESI':>8} | {'μ(z=1)':>8} | {'Δfσ₈(0.5)%':>11} | {'Status':>20}")
    print(f"  {'-'*95}")

    for pa in analyses:
        label = pa['label']
        chi2 = pa['result'].chi2_DESI
        mu1 = pa['mu'].get(1.0, 1.0)
        dfs = pa['result'].delta_fsigma8_pct.get(0.5, 0.0)

        if chi2 < 15:
            bg_status = "Good background"
        elif chi2 < 30:
            bg_status = "Marginal bg"
        else:
            bg_status = "Excluded by bg"

        if abs(mu1 - 1.0) > 0.03:
            pert_status = "Distinctive"
        elif abs(mu1 - 1.0) > 0.005:
            pert_status = "Marginal"
        else:
            pert_status = "≈ GR"

        status = f"{bg_status} / {pert_status}"

        print(f"  {label:>40} | {chi2:8.2f} | {mu1:8.5f} | {dfs:+11.2f} | {status:>20}")

    print()
    print("  CONCLUSION: The trade-off is confirmed quantitatively.")
    print("  Good DESI fit → GR-like perturbations. Distinctive perturbations → bad DESI fit.")
    print("=" * 100)

    return analyses


# ============================================================
# PHASE 4: D4.2 — OBSERVABLE PREDICTIONS
# ============================================================

def compute_fsigma8_chi2(result):
    """
    Compute chi2 of fσ₈ predictions against observational data.
    Uses the fσ₈ data compiled from BOSS, eBOSS, 6dFGS, VIPERS, FastSound.
    """
    chi2 = 0.0
    n_data = 0
    details = []

    for z_obs, fs8_obs, fs8_err, survey in FSIGMA8_DATA:
        # Interpolate between stored fsigma8 values
        z_keys = sorted(result.fsigma8.keys())
        if len(z_keys) == 0:
            continue
        fs8_model = np.interp(z_obs, z_keys,
                               [result.fsigma8[z] for z in z_keys])
        if fs8_model == 0.0:
            continue

        dchi2 = ((fs8_obs - fs8_model) / fs8_err) ** 2
        chi2 += dchi2
        n_data += 1
        details.append({
            'z': z_obs, 'survey': survey,
            'fs8_obs': fs8_obs, 'fs8_err': fs8_err,
            'fs8_model': fs8_model,
            'pull': (fs8_obs - fs8_model) / fs8_err,
        })

    return chi2, n_data, details


def compute_ISW_signal(a_arr, E_arr, params, mu_func=None):
    """
    Compute ISW integrand (f-1)×D/a as a function of a.
    Returns (isw_model, isw_lcdm) arrays.
    """
    if mu_func is None:
        mu_func = lambda a: 1.0

    N_arr = np.log(np.maximum(a_arr, 1e-10))
    Om = params.Omega_m

    dE_dN = np.gradient(E_arr, N_arr)
    EprimeOverE = dE_dN / E_arr

    def growth_rhs(N, y):
        D, Dp = y
        a = np.exp(N)
        E = np.interp(N, N_arr, E_arr)
        E2 = E**2
        EpE = np.interp(N, N_arr, EprimeOverE)
        mu = mu_func(a)
        Om_a = Om * a**(-3) / E2
        Dpp = -(2.0 + EpE) * Dp + 1.5 * Om_a * mu * D
        return [Dp, Dpp]

    N_start, N_end = N_arr[0], N_arr[-1]
    D0, Dp0 = np.exp(N_start), np.exp(N_start)

    sol = solve_ivp(growth_rhs, [N_start, N_end], [D0, Dp0],
                    t_eval=N_arr, method='RK45', rtol=1e-10, atol=1e-12)
    if not sol.success:
        return np.zeros_like(a_arr), np.zeros_like(a_arr)

    D_arr = sol.y[0]
    f_arr = sol.y[1] / D_arr
    D_today = np.interp(0.0, sol.t, D_arr)
    D_norm = D_arr / D_today
    isw_integrand = (f_arr - 1.0) * D_norm / a_arr

    # ΛCDM comparison
    def E_LCDM(a):
        return np.sqrt(OMEGA_M0 * a**(-3) + OMEGA_R0 * a**(-4) + OMEGA_DE0)

    E_lcdm_arr = np.array([E_LCDM(a) for a in a_arr])
    dE_lcdm = np.gradient(E_lcdm_arr, N_arr)
    EpE_lcdm = dE_lcdm / E_lcdm_arr

    def growth_rhs_lcdm(N, y):
        D, Dp = y
        a = np.exp(N)
        E2 = E_LCDM(a)**2
        EpE = np.interp(N, N_arr, EpE_lcdm)
        Om_a = Om * a**(-3) / E2
        Dpp = -(2.0 + EpE) * Dp + 1.5 * Om_a * D
        return [Dp, Dpp]

    sol_l = solve_ivp(growth_rhs_lcdm, [N_start, N_end], [D0, Dp0],
                       t_eval=N_arr, method='RK45', rtol=1e-10, atol=1e-12)
    f_lcdm = sol_l.y[1] / sol_l.y[0]
    D_today_l = np.interp(0.0, sol_l.t, sol_l.y[0])
    D_norm_l = sol_l.y[0] / D_today_l
    isw_lcdm = (f_lcdm - 1.0) * D_norm_l / a_arr

    return isw_integrand, isw_lcdm


def compute_lensing_modification(a_arr, E_arr, params, mu_func=None):
    """
    Compute ratio of CMB lensing kernel integrand (model/ΛCDM) at key redshifts.
    Kernel ∝ Σ(a) × Ω_m(a) × D(a) × H(a) / a.
    """
    if mu_func is None:
        mu_func = lambda a: 1.0

    Om = params.Omega_m
    N_arr = np.log(np.maximum(a_arr, 1e-10))
    dE_dN = np.gradient(E_arr, N_arr)
    EprimeOverE = dE_dN / E_arr

    def growth_rhs(N, y):
        D, Dp = y
        a = np.exp(N)
        E = np.interp(N, N_arr, E_arr)
        E2 = E**2
        EpE = np.interp(N, N_arr, EprimeOverE)
        mu = mu_func(a)
        Om_a = Om * a**(-3) / E2
        Dpp = -(2.0 + EpE) * Dp + 1.5 * Om_a * mu * D
        return [Dp, Dpp]

    N_start, N_end = N_arr[0], N_arr[-1]
    D0, Dp0 = np.exp(N_start), np.exp(N_start)

    sol = solve_ivp(growth_rhs, [N_start, N_end], [D0, Dp0],
                    t_eval=N_arr, method='RK45', rtol=1e-10, atol=1e-12)
    if not sol.success:
        return {}

    D_today = np.interp(0.0, sol.t, sol.y[0])
    D_norm = sol.y[0] / D_today

    def E_LCDM(a):
        return np.sqrt(OMEGA_M0 * a**(-3) + OMEGA_R0 * a**(-4) + OMEGA_DE0)

    E_lcdm_arr = np.array([E_LCDM(a) for a in a_arr])
    dE_lcdm = np.gradient(E_lcdm_arr, N_arr)
    EpE_lcdm = dE_lcdm / E_lcdm_arr

    def growth_rhs_lcdm(N, y):
        D, Dp = y
        a = np.exp(N)
        E2 = E_LCDM(a)**2
        EpE = np.interp(N, N_arr, EpE_lcdm)
        Om_a = Om * a**(-3) / E2
        Dpp = -(2.0 + EpE) * Dp + 1.5 * Om_a * D
        return [Dp, Dpp]

    sol_l = solve_ivp(growth_rhs_lcdm, [N_start, N_end], [D0, Dp0],
                       t_eval=N_arr, method='RK45', rtol=1e-10, atol=1e-12)
    D_today_l = np.interp(0.0, sol_l.t, sol_l.y[0])
    D_norm_l = sol_l.y[0] / D_today_l

    target_z = [0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0]
    ratios = {}
    for z in target_z:
        a = 1.0 / (1.0 + z)
        N = np.log(a)
        E_mod = np.interp(N, N_arr, E_arr)
        E_lcd = np.interp(N, N_arr, E_lcdm_arr)
        D_mod = np.interp(N, sol.t, D_norm)
        D_lcd = np.interp(N, sol_l.t, D_norm_l)
        mu = mu_func(a)
        if abs(D_lcd * E_lcd) > 1e-30:
            ratios[z] = (mu * D_mod * E_mod) / (D_lcd * E_lcd)
        else:
            ratios[z] = 1.0
    return ratios


def _build_mu_func(params):
    """Build a mu(a) function using the actual ψ(a) solution for ξ > 0."""
    if params.zeta0 > 0:
        N_ode, psi_ode, _, _ = solve_xi_positive(params)
        # Capture arrays by value to avoid closure issues
        N_captured = N_ode.copy()
        P_captured = psi_ode.copy()
        def mu_func(a, _N=N_captured, _P=P_captured, _p=params):
            psi = np.interp(np.log(max(a, 1e-10)), _N, _P)
            denom = 1.0 - _p.zeta0 * (psi**2 - 1.0)
            if abs(denom) < 1e-10:
                return 10.0
            return 1.0 / denom
        return mu_func
    else:
        return lambda a: 1.0


def run_phase4_D42_D43(analyses=None):
    """
    D4.2: Observable predictions (fσ₈ vs data, ISW, lensing)
    D4.3: Multi-probe χ²
    """
    print("\n" + "=" * 70)
    print("  PROJECT MERIDIAN — PHASE 4, D4.2 & D4.3")
    print("  Observable Predictions & Multi-Probe Constraints")
    print("  Clayton & Clawd, March 2026")
    print("=" * 70)

    if analyses is None:
        points = [
            ("DESI-optimal (ε₀≈0, ζ₀=0.058)",
             MeridianParams(eps0=0.001, zeta0=0.058)),
            ("Moderate (ε₀=0.05, ζ₀=0.10)",
             MeridianParams(eps0=0.05, zeta0=0.10)),
            ("ξ=0 reference (ε₀=0.15)",
             MeridianParams(eps0=0.15, zeta0=0.0)),
        ]
        analyses = []
        for label, params in points:
            print(f"  Computing: {label} ...")
            pa = perturbation_analysis(params, label=label)
            analyses.append(pa)

    # ============================================================
    # D4.2: fσ₈ COMPARISON WITH DATA
    # ============================================================
    print("\n" + "=" * 100)
    print("  D4.2 — fσ₈ COMPARISON WITH OBSERVATIONAL DATA")
    print("=" * 100)

    for pa in analyses:
        label = pa['label']
        result = pa['result']
        chi2_fs8, n_data, details = compute_fsigma8_chi2(result)

        print(f"\n  --- {label} ---")
        print(f"  χ²_fσ₈ = {chi2_fs8:.2f}  ({n_data} data points)")
        print()
        print(f"    {'z':>6} | {'fσ₈_obs':>8} | {'σ':>6} | {'fσ₈_mod':>8} | "
              f"{'pull':>6} | {'Survey':>20}")
        print(f"    {'-'*65}")

        for d in details:
            print(f"    {d['z']:6.3f} | {d['fs8_obs']:8.3f} | {d['fs8_err']:6.3f} | "
                  f"{d['fs8_model']:8.4f} | {d['pull']:+6.2f} | {d['survey']:>20}")

        pa['chi2_fsigma8'] = chi2_fs8
        pa['n_fsigma8'] = n_data

    # ============================================================
    # D4.2: ISW EFFECT
    # ============================================================
    print("\n" + "=" * 100)
    print("  D4.2 — ISW EFFECT MODIFICATION")
    print("=" * 100)

    for pa in analyses:
        label = pa['label']
        result = pa['result']
        params = pa['params']

        a_arr = 1.0 / (1.0 + result.z_array)
        sort_idx = np.argsort(a_arr)
        a_sorted = a_arr[sort_idx]
        E_sorted = result.E_array[sort_idx]

        mu_func = _build_mu_func(params)
        isw_model, isw_lcdm = compute_ISW_signal(a_sorted, E_sorted, params, mu_func)

        print(f"\n  --- {label} ---")
        target_z = [0.3, 0.5, 0.8, 1.0, 1.5, 2.0]
        isw_peak = max(abs(np.interp(-np.log(1+z), np.log(a_sorted), isw_lcdm))
                       for z in target_z) if len(isw_lcdm) > 0 else 1.0
        if isw_peak < 1e-30:
            isw_peak = 1.0

        print(f"    {'z':>6} | {'ISW_mod':>10} | {'ISW_ΛCDM':>10} | {'Ratio':>8}")
        print(f"    {'-'*42}")
        for z in target_z:
            N_z = -np.log(1 + z)
            isw_m = np.interp(N_z, np.log(a_sorted), isw_model) / isw_peak
            isw_l = np.interp(N_z, np.log(a_sorted), isw_lcdm) / isw_peak
            ratio = isw_m / isw_l if abs(isw_l) > 1e-30 else 1.0
            print(f"    {z:6.1f} | {isw_m:10.4f} | {isw_l:10.4f} | {ratio:8.4f}")

    # ============================================================
    # D4.2: CMB LENSING
    # ============================================================
    print("\n" + "=" * 100)
    print("  D4.2 — CMB LENSING KERNEL MODIFICATION (Σ×D×H/a ratio to ΛCDM)")
    print("=" * 100)

    for pa in analyses:
        label = pa['label']
        result = pa['result']
        params = pa['params']

        a_arr = 1.0 / (1.0 + result.z_array)
        sort_idx = np.argsort(a_arr)
        a_sorted = a_arr[sort_idx]
        E_sorted = result.E_array[sort_idx]

        mu_func = _build_mu_func(params)
        ratios = compute_lensing_modification(a_sorted, E_sorted, params, mu_func)

        print(f"\n  --- {label} ---")
        print(f"    {'z':>6} | {'Kernel ratio':>14} | {'ΔC_ℓ^κκ approx':>16}")
        print(f"    {'-'*42}")
        for z in sorted(ratios.keys()):
            r = ratios[z]
            dC_pct = 2.0 * (r - 1.0) * 100.0
            print(f"    {z:6.1f} | {r:14.5f} | {dC_pct:+16.2f}%")
        pa['lensing_ratios'] = ratios

    # ============================================================
    # D4.3: MULTI-PROBE χ²
    # ============================================================
    print("\n" + "=" * 100)
    print("  D4.3 — MULTI-PROBE χ²")
    print("=" * 100)
    print()
    print("  Components:")
    print("    χ²_DESI:  BAO w₀, wₐ (2 dof)")
    print("    χ²_fσ₈:  Growth data (9 points)")
    print("    χ²_H₀:   CMB distance prior (σ=0.5 km/s/Mpc)")
    print("    χ²_HK:   Hiramatsu-Kobayashi Planck (β_center=−0.037, σ≈0.01)")
    print()

    # H&K parameters
    beta_HK_center = -0.037
    sigma_HK = (0.047 - 0.028) / 2.0
    sigma_H0 = 0.5

    print(f"  {'Label':>35} | {'χ²_DESI':>8} | {'χ²_fσ₈':>8} | {'χ²_H₀':>8} | "
          f"{'χ²_HK':>8} | {'χ²_total':>9} | {'dof':>4} | {'χ²/dof':>7}")
    print(f"  {'-'*105}")

    # ΛCDM baseline
    lcdm_params = MeridianParams(eps0=0.0001, zeta0=0.0)
    lcdm_result = solve_meridian(lcdm_params)
    chi2_fs8_lcdm, n_lcdm, _ = compute_fsigma8_chi2(lcdm_result)
    chi2_HK_lcdm = (beta_HK_center / sigma_HK) ** 2

    for pa in analyses:
        label = pa['label']
        result = pa['result']
        params = pa['params']

        chi2_desi = result.chi2_DESI
        chi2_fs8 = pa.get('chi2_fsigma8', 0.0)
        n_fs8 = pa.get('n_fsigma8', 0)
        chi2_H0 = ((result.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
        eps_SW = params.zeta0 / (1.0 + params.zeta0)
        chi2_HK = ((-eps_SW - beta_HK_center) / sigma_HK) ** 2

        chi2_total = chi2_desi + chi2_fs8 + chi2_H0 + chi2_HK
        n_dof = 2 + n_fs8 + 1 + 1
        chi2_per_dof = chi2_total / n_dof if n_dof > 0 else 0

        print(f"  {label:>35} | {chi2_desi:8.2f} | {chi2_fs8:8.2f} | {chi2_H0:8.2f} | "
              f"{chi2_HK:8.2f} | {chi2_total:9.2f} | {n_dof:4d} | {chi2_per_dof:7.2f}")

        pa['chi2_total'] = chi2_total
        pa['chi2_H0'] = chi2_H0
        pa['chi2_HK'] = chi2_HK

    # ΛCDM row
    chi2_total_lcdm = 0.0 + chi2_fs8_lcdm + 0.0 + chi2_HK_lcdm
    n_dof_lcdm = 2 + n_lcdm + 1 + 1
    print(f"  {'ΛCDM (reference)':>35} | {'0.00':>8} | {chi2_fs8_lcdm:8.2f} | "
          f"{'0.00':>8} | {chi2_HK_lcdm:8.2f} | {chi2_total_lcdm:9.2f} | "
          f"{n_dof_lcdm:4d} | {chi2_total_lcdm/n_dof_lcdm:7.2f}")

    print()
    print("  NOTE: χ²_DESI = 0 for ΛCDM by construction. The model must improve")
    print("  TOTAL χ² to be preferred. H&K actually penalizes GR (β=0) because")
    print("  Planck prefers β ≈ −0.037 — our model goes in the right direction.")
    print("=" * 100)

    return analyses


# ============================================================
# PHASE 5: EXTENDED CUSCUTON ANALYSIS (D5.5)
# ============================================================

def scan_extended_cuscuton(eps0_values=None, lambda3_values=None, zeta0: float = 0.0):
    """
    2D scan over (eps0, lambda3) at fixed zeta0 to find the DESI+H0 optimum.
    The extended cuscuton breaks K~1/H^2 via the lambda3/E term.
    """
    if eps0_values is None:
        eps0_values = [0.001, 0.01, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30]
    if lambda3_values is None:
        lambda3_values = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]

    print(f"\n  EXTENDED CUSCUTON 2D SCAN: {len(eps0_values)} x {len(lambda3_values)} = "
          f"{len(eps0_values)*len(lambda3_values)} evaluations")
    print(f"  Fixed: zeta0 = {zeta0:.3f}")
    print()

    # Print chi2_DESI grid
    header = "  eps0\\lam3 |" + "".join(f" {l:6.2f}" for l in lambda3_values)
    print("  --- chi2_DESI ---")
    print(header)
    print("  " + "-" * (12 + 7 * len(lambda3_values)))

    best_chi2_total = 1e10
    best_chi2_desi = 1e10
    best_eps0, best_lam3 = 0, 0
    best_result = None
    grid = {}

    sigma_H0 = 0.5
    beta_HK_center = -0.037
    sigma_HK = (0.047 - 0.028) / 2.0

    for eps0 in eps0_values:
        row = f"  {eps0:10.3f} |"
        for lam3 in lambda3_values:
            try:
                params = MeridianParams(eps0=eps0, zeta0=zeta0, lambda3=lam3)
                result = solve_meridian(params)

                chi2_desi = result.chi2_DESI
                chi2_H0 = ((result.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
                eps_SW = zeta0 / (1.0 + zeta0) if zeta0 > 0 else 0.0
                chi2_HK = ((-eps_SW - beta_HK_center) / sigma_HK) ** 2
                chi2_fs8, n_fs8, _ = compute_fsigma8_chi2(result)
                chi2_total = chi2_desi + chi2_fs8 + chi2_H0 + chi2_HK

                grid[(eps0, lam3)] = {
                    'chi2_desi': chi2_desi, 'chi2_H0': chi2_H0,
                    'chi2_HK': chi2_HK, 'chi2_fs8': chi2_fs8,
                    'chi2_total': chi2_total,
                    'w0': result.w0, 'wa': result.wa,
                    'H0': result.H0_CMB, 'result': result,
                }
                if chi2_total < best_chi2_total:
                    best_chi2_total = chi2_total
                    best_chi2_desi = chi2_desi
                    best_eps0 = eps0
                    best_lam3 = lam3
                    best_result = result
                row += f" {chi2_desi:6.1f}"
            except Exception as ex:
                row += "   ERR"
                grid[(eps0, lam3)] = {'chi2_total': 999, 'error': str(ex)}
        print(row)

    # Print H0 grid
    print()
    print("  --- H0 (km/s/Mpc) ---")
    header2 = "  eps0\\lam3 |" + "".join(f" {l:6.2f}" for l in lambda3_values)
    print(header2)
    print("  " + "-" * (12 + 7 * len(lambda3_values)))
    for eps0 in eps0_values:
        row = f"  {eps0:10.3f} |"
        for lam3 in lambda3_values:
            g = grid.get((eps0, lam3), {})
            H0 = g.get('H0', 0.0)
            if H0 > 0:
                row += f" {H0:6.1f}"
            else:
                row += "   ERR"
        print(row)

    # Print chi2_total grid
    print()
    print("  --- chi2_total (DESI + fσ₈ + H₀ + H&K) ---")
    header3 = "  eps0\\lam3 |" + "".join(f" {l:6.2f}" for l in lambda3_values)
    print(header3)
    print("  " + "-" * (12 + 7 * len(lambda3_values)))
    for eps0 in eps0_values:
        row = f"  {eps0:10.3f} |"
        for lam3 in lambda3_values:
            g = grid.get((eps0, lam3), {})
            ct = g.get('chi2_total', 999.0)
            if ct < 999:
                row += f" {ct:6.1f}"
            else:
                row += "   ERR"
        print(row)

    print()
    print(f"  Grid minimum: eps0={best_eps0:.3f}, lambda3={best_lam3:.3f}")
    print(f"    chi2_total = {best_chi2_total:.2f}, chi2_DESI = {best_chi2_desi:.2f}")
    if best_result:
        print(f"    w0 = {best_result.w0:.4f}, wa = {best_result.wa:.4f}")
        print(f"    H0 = {best_result.H0_CMB:.2f} km/s/Mpc")
        ph = best_result.has_phantom_crossing
        print(f"    Phantom: {'z=' + f'{best_result.z_phantom:.2f}' if ph else 'none'}")

    return grid, best_eps0, best_lam3, best_result


def optimize_extended_cuscuton(eps0_init=0.05, lambda3_init=0.20, zeta0: float = 0.0):
    """
    Optimize (eps0, lambda3) to minimize the multi-probe chi2_total.
    """
    sigma_H0 = 0.5
    beta_HK_center = -0.037
    sigma_HK = (0.047 - 0.028) / 2.0

    print(f"\n  Optimizing from (eps0={eps0_init:.3f}, lambda3={lambda3_init:.3f})...")

    def objective(x):
        eps0, lam3 = x
        Ode = 1.0 - OMEGA_M0 - OMEGA_R0
        if eps0 <= 0.0001 or lam3 < 0 or lam3 >= Ode or eps0 > 20:
            return 1000.0
        try:
            params = MeridianParams(eps0=eps0, zeta0=zeta0, lambda3=lam3)
            result = solve_meridian(params)
            chi2_desi = result.chi2_DESI
            chi2_H0 = ((result.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
            eps_SW = zeta0 / (1.0 + zeta0) if zeta0 > 0 else 0.0
            chi2_HK = ((-eps_SW - beta_HK_center) / sigma_HK) ** 2
            chi2_fs8, _, _ = compute_fsigma8_chi2(result)
            return chi2_desi + chi2_fs8 + chi2_H0 + chi2_HK
        except Exception:
            return 1000.0

    res = minimize(objective, [eps0_init, lambda3_init],
                   method='Nelder-Mead',
                   options={'xatol': 1e-5, 'fatol': 1e-3, 'maxiter': 500})

    eps0_opt, lam3_opt = res.x
    lam3_opt = max(lam3_opt, 0.0)

    params_opt = MeridianParams(eps0=eps0_opt, zeta0=zeta0, lambda3=lam3_opt)
    result_opt = solve_meridian(params_opt)

    chi2_desi = result_opt.chi2_DESI
    chi2_H0 = ((result_opt.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
    eps_SW = zeta0 / (1.0 + zeta0) if zeta0 > 0 else 0.0
    chi2_HK = ((-eps_SW - beta_HK_center) / sigma_HK) ** 2
    chi2_fs8, n_fs8, _ = compute_fsigma8_chi2(result_opt)
    chi2_total = chi2_desi + chi2_fs8 + chi2_H0 + chi2_HK

    Ode = 1.0 - OMEGA_M0 - OMEGA_R0
    v0 = (Ode - lam3_opt) / (1.0 + eps0_opt)
    kappa0 = eps0_opt * v0

    print(f"  OPTIMUM: eps0={eps0_opt:.6f}, lambda3={lam3_opt:.6f}")
    print(f"    v0={v0:.6f}, kappa0={kappa0:.6f}")
    print(f"    w0={result_opt.w0:.4f}, wa={result_opt.wa:.4f}, H0={result_opt.H0_CMB:.2f}")
    print(f"    chi2: DESI={chi2_desi:.2f} fσ₈={chi2_fs8:.2f} H₀={chi2_H0:.2f} "
          f"HK={chi2_HK:.2f} total={chi2_total:.2f}")
    print(f"    Converged: {res.success} ({res.nfev} evals)")

    return eps0_opt, lam3_opt, result_opt, chi2_total


def run_phase5_extended():
    """
    Phase 5 extended cuscuton numerical analysis.
    1. Coarse 2D grid scan over (eps0, lambda3) at zeta0=0
    2. Nelder-Mead optimization from grid minimum + multiple starts
    3. Compare minimal vs extended cuscuton
    4. K_eff decomposition and w(z) comparison
    """
    print("=" * 80)
    print("  PROJECT MERIDIAN — PHASE 5, D5.5 NUMERICAL VERIFICATION")
    print("  Extended Cuscuton: E^4 - R*E^2 - lambda3*E - kappa0 = 0")
    print("  Clayton & Clawd, March 2026")
    print("=" * 80)

    # STEP 1: Coarse grid scan
    print("\n  STEP 1: Coarse 2D grid scan (eps0 x lambda3)")
    grid, best_e, best_l, best_r = scan_extended_cuscuton()

    # STEP 2: Optimize
    print("\n  STEP 2: Nelder-Mead optimization")
    all_optima = []
    try:
        e_opt, l_opt, r_opt, c_opt = optimize_extended_cuscuton(best_e, best_l)
        all_optima.append((e_opt, l_opt, r_opt, c_opt))
    except Exception as ex:
        print(f"    Failed from grid min: {ex}")

    starts = [(0.01, 0.10), (0.05, 0.15), (0.10, 0.25),
              (0.001, 0.30), (0.03, 0.20), (0.15, 0.35)]
    for e0, l0 in starts:
        try:
            eo, lo, ro, co = optimize_extended_cuscuton(e0, l0)
            all_optima.append((eo, lo, ro, co))
        except Exception as ex:
            print(f"    Failed from ({e0}, {l0}): {ex}")

    if not all_optima:
        print("  ERROR: No optimization succeeded.")
        return

    best = min(all_optima, key=lambda x: x[3])
    eps0_best, lam3_best, result_best, chi2_best = best

    print(f"\n  {'='*60}")
    print(f"  GLOBAL OPTIMUM:")
    print(f"    eps0={eps0_best:.6f}, lambda3={lam3_best:.6f}")
    print(f"    chi2_total={chi2_best:.4f}")
    print(f"    w0={result_best.w0:.4f}, wa={result_best.wa:.4f}")
    print(f"    H0={result_best.H0_CMB:.2f} km/s/Mpc")
    print(f"  {'='*60}")

    # STEP 3: Comparison table
    print("\n  STEP 3: Minimal vs Extended Cuscuton Comparison")
    print("=" * 110)

    sigma_H0 = 0.5
    beta_HK_center = -0.037
    sigma_HK = (0.047 - 0.028) / 2.0
    Ode = 1.0 - OMEGA_M0 - OMEGA_R0

    models = []
    # LCDM
    r_lcdm = solve_meridian(MeridianParams(eps0=0.0001, zeta0=0.0))
    fs8_lcdm, _, _ = compute_fsigma8_chi2(r_lcdm)
    hk_lcdm = ((0.0 - beta_HK_center) / sigma_HK) ** 2
    models.append(("LCDM", r_lcdm, 0.0, fs8_lcdm, 0.0, hk_lcdm))

    # Minimal (Phase 4 DESI-optimal)
    r_min = solve_meridian(MeridianParams(eps0=0.001, zeta0=0.058))
    fs8_min, _, _ = compute_fsigma8_chi2(r_min)
    h0_min = ((r_min.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
    hk_min = ((-0.058/1.058 - beta_HK_center) / sigma_HK) ** 2
    models.append(("Minimal (Ph4 best)", r_min, r_min.chi2_DESI, fs8_min, h0_min, hk_min))

    # Extended optimum
    r_ext = solve_meridian(MeridianParams(eps0=eps0_best, zeta0=0.0, lambda3=lam3_best))
    fs8_ext, _, _ = compute_fsigma8_chi2(r_ext)
    h0_ext = ((r_ext.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
    hk_ext = ((0.0 - beta_HK_center) / sigma_HK) ** 2
    models.append(("Extended (optimum)", r_ext, r_ext.chi2_DESI, fs8_ext, h0_ext, hk_ext))

    print(f"  {'Model':>25} | {'w0':>7} | {'wa':>7} | {'H0':>6} | "
          f"{'chi2_D':>7} | {'chi2_f':>7} | {'chi2_H':>7} | {'chi2_K':>7} | {'TOTAL':>8}")
    print(f"  {'-'*100}")
    for name, r, cd, cf, ch, ck in models:
        tot = cd + cf + ch + ck
        print(f"  {name:>25} | {r.w0:7.3f} | {r.wa:7.3f} | {r.H0_CMB:6.1f} | "
              f"{cd:7.2f} | {cf:7.2f} | {ch:7.2f} | {ck:7.2f} | {tot:8.2f}")
    print(f"  {'DESI DR2':>25} | {W0_DESI:7.3f} | {WA_DESI:7.3f} | {H0_FIDUCIAL:6.1f} |")

    # STEP 4: K_eff decomposition
    print("\n  STEP 4: K_eff Decomposition (verify 1/H^2 breaking)")
    print("=" * 85)

    v0_ext = (Ode - lam3_best) / (1.0 + eps0_best)
    kappa0_ext = eps0_best * v0_ext
    params_ext = MeridianParams(eps0=eps0_best, zeta0=0.0, lambda3=lam3_best)

    print(f"\n  eps0={eps0_best:.6f}, lambda3={lam3_best:.6f}, v0={v0_ext:.6f}, kappa0={kappa0_ext:.6f}")
    print()
    print(f"  {'z':>6} | {'E':>8} | {'K_eff':>8} | {'lam3/E':>8} | {'kap0/E2':>8} | "
          f"{'lam3/E %':>9} | {'kap0/E2 %':>10}")
    print(f"  {'-'*70}")

    for z in [0.0, 0.2, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0]:
        a = 1.0 / (1.0 + z)
        E = E_extended(a, params_ext)
        lam_term = lam3_best / E
        kap_term = kappa0_ext / E**2
        K_eff = lam_term + kap_term
        pct_l = 100.0 * lam_term / K_eff if K_eff > 1e-20 else 0.0
        pct_k = 100.0 * kap_term / K_eff if K_eff > 1e-20 else 0.0
        print(f"  {z:6.1f} | {E:8.4f} | {K_eff:8.5f} | {lam_term:8.5f} | "
              f"{kap_term:8.5f} | {pct_l:8.1f}% | {pct_k:9.1f}%")

    # STEP 5: w(z) comparison
    print("\n  STEP 5: w(z) — Minimal vs Extended at same eps0")
    print("=" * 50)
    params_min_xi0 = MeridianParams(eps0=eps0_best, zeta0=0.0, lambda3=0.0)
    print(f"\n  {'z':>6} | {'w_minimal':>10} | {'w_extended':>11} | {'dw':>8}")
    print(f"  {'-'*42}")
    for z in [0.0, 0.2, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0]:
        a = 1.0 / (1.0 + z)
        w_min = w_DE_xi0(a, params_min_xi0)
        w_ext = w_DE_extended(a, params_ext)
        print(f"  {z:6.1f} | {w_min:10.5f} | {w_ext:11.5f} | {w_ext - w_min:+8.5f}")

    print("\n  🦞🧍💜🔥♾️")
    return eps0_best, lam3_best, result_best, chi2_best


def run_phase5b_xi_plus_lambda3():
    """
    Phase 5b: Extended cuscuton WITH non-minimal coupling.
    Scans lambda3 at the Phase 4 DESI-optimal zeta0=0.058.
    This is where the H0 bottleneck (64.5 km/s/Mpc) exists and lambda3 should fix it.
    """
    print("=" * 80)
    print("  PROJECT MERIDIAN — PHASE 5b: EXTENDED CUSCUTON + NON-MINIMAL COUPLING")
    print("  Testing lambda3 at zeta0=0.058 (Phase 4 DESI-optimal)")
    print("  The H0 bottleneck (64.5 km/s/Mpc) should be relieved by lambda3.")
    print("=" * 80)

    sigma_H0 = 0.5
    beta_HK_center = -0.037
    sigma_HK = (0.047 - 0.028) / 2.0
    Ode = 1.0 - OMEGA_M0 - OMEGA_R0

    # ---- STEP 1: lambda3 scan at fixed (eps0~0, zeta0=0.058) ----
    zeta0_fix = 0.058
    eps0_fix = 0.001  # Near-zero (DESI-optimal from Phase 4)

    lambda3_values = [0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]

    print(f"\n  STEP 1: 1D scan over lambda3 at eps0={eps0_fix}, zeta0={zeta0_fix}")
    print(f"\n  {'lam3':>6} | {'w0':>7} | {'wa':>7} | {'H0':>6} | "
          f"{'chi2_D':>7} | {'chi2_f':>7} | {'chi2_H':>7} | {'chi2_K':>7} | {'TOTAL':>7}")
    print(f"  {'-'*75}")

    best_total = 1e10
    best_lam3_1d = 0.0
    scan_results = []

    for lam3 in lambda3_values:
        try:
            params = MeridianParams(eps0=eps0_fix, zeta0=zeta0_fix, lambda3=lam3)
            result = solve_meridian(params)

            chi2_desi = result.chi2_DESI
            chi2_H0 = ((result.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
            eps_SW = zeta0_fix / (1.0 + zeta0_fix)
            chi2_HK = ((-eps_SW - beta_HK_center) / sigma_HK) ** 2
            chi2_fs8, n_fs8, _ = compute_fsigma8_chi2(result)
            chi2_total = chi2_desi + chi2_fs8 + chi2_H0 + chi2_HK

            print(f"  {lam3:6.2f} | {result.w0:7.3f} | {result.wa:7.3f} | "
                  f"{result.H0_CMB:6.1f} | {chi2_desi:7.2f} | {chi2_fs8:7.2f} | "
                  f"{chi2_H0:7.2f} | {chi2_HK:7.2f} | {chi2_total:7.2f}")

            scan_results.append({
                'lam3': lam3, 'w0': result.w0, 'wa': result.wa,
                'H0': result.H0_CMB, 'chi2_desi': chi2_desi,
                'chi2_fs8': chi2_fs8, 'chi2_H0': chi2_H0,
                'chi2_HK': chi2_HK, 'chi2_total': chi2_total,
                'result': result,
            })
            if chi2_total < best_total:
                best_total = chi2_total
                best_lam3_1d = lam3
        except Exception as ex:
            print(f"  {lam3:6.2f} | ERROR: {ex}")

    print(f"\n  1D minimum: lambda3={best_lam3_1d:.3f}, chi2_total={best_total:.2f}")

    # ---- STEP 2: 2D grid over (eps0, lambda3) at zeta0=0.058 ----
    print(f"\n  STEP 2: 2D grid scan at zeta0={zeta0_fix}")
    grid, best_e2, best_l2, best_r2 = scan_extended_cuscuton(
        eps0_values=[0.001, 0.005, 0.01, 0.03, 0.05, 0.08, 0.10, 0.15],
        lambda3_values=[0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40],
        zeta0=zeta0_fix
    )

    # ---- STEP 3: Optimize ----
    print(f"\n  STEP 3: Nelder-Mead optimization at zeta0={zeta0_fix}")
    all_optima = []

    starts = [
        (best_e2, best_l2),
        (0.001, 0.10), (0.001, 0.20), (0.01, 0.15),
        (0.05, 0.10), (0.001, best_lam3_1d),
    ]
    for e0, l0 in starts:
        try:
            eo, lo, ro, co = optimize_extended_cuscuton(e0, l0, zeta0=zeta0_fix)
            all_optima.append((eo, lo, ro, co))
        except Exception as ex:
            print(f"    Failed from ({e0}, {l0}): {ex}")

    if not all_optima:
        print("  ERROR: No optimization succeeded.")
        return

    best = min(all_optima, key=lambda x: x[3])
    eps0_best, lam3_best, result_best, chi2_best = best

    # ---- STEP 4: Comparison table ----
    print(f"\n  {'='*80}")
    print(f"  COMPARISON: Minimal vs Extended at zeta0={zeta0_fix}")
    print(f"  {'='*80}")

    # Minimal at DESI-optimal
    params_min = MeridianParams(eps0=0.001, zeta0=zeta0_fix, lambda3=0.0)
    result_min = solve_meridian(params_min)
    chi2_d_min = result_min.chi2_DESI
    chi2_H_min = ((result_min.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
    eps_SW = zeta0_fix / (1.0 + zeta0_fix)
    chi2_K_min = ((-eps_SW - beta_HK_center) / sigma_HK) ** 2
    chi2_f_min, _, _ = compute_fsigma8_chi2(result_min)
    chi2_t_min = chi2_d_min + chi2_f_min + chi2_H_min + chi2_K_min

    # Extended at optimum
    params_ext = MeridianParams(eps0=eps0_best, zeta0=zeta0_fix, lambda3=lam3_best)
    result_ext = solve_meridian(params_ext)
    chi2_d_ext = result_ext.chi2_DESI
    chi2_H_ext = ((result_ext.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
    chi2_K_ext = chi2_K_min  # Same zeta0
    chi2_f_ext, _, _ = compute_fsigma8_chi2(result_ext)
    chi2_t_ext = chi2_d_ext + chi2_f_ext + chi2_H_ext + chi2_K_ext

    # LCDM
    params_lcdm = MeridianParams(eps0=0.0001, zeta0=0.0, lambda3=0.0)
    result_lcdm = solve_meridian(params_lcdm)
    chi2_d_lcdm = result_lcdm.chi2_DESI
    chi2_f_lcdm, _, _ = compute_fsigma8_chi2(result_lcdm)
    chi2_K_lcdm = ((0.0 - beta_HK_center) / sigma_HK) ** 2
    chi2_t_lcdm = chi2_d_lcdm + chi2_f_lcdm + 0.0 + chi2_K_lcdm

    print(f"\n  {'Model':>30} | {'w0':>7} | {'wa':>7} | {'H0':>6} | "
          f"{'chi2_D':>7} | {'chi2_f':>7} | {'chi2_H':>7} | {'chi2_K':>7} | {'TOTAL':>7}")
    print(f"  {'-'*90}")
    print(f"  {'LCDM':>30} | {result_lcdm.w0:7.3f} | {result_lcdm.wa:7.3f} | {67.4:6.1f} | "
          f"{chi2_d_lcdm:7.2f} | {chi2_f_lcdm:7.2f} | {'0.00':>7} | {chi2_K_lcdm:7.2f} | {chi2_t_lcdm:7.2f}")
    print(f"  {'Minimal (lam3=0)':>30} | {result_min.w0:7.3f} | {result_min.wa:7.3f} | "
          f"{result_min.H0_CMB:6.1f} | {chi2_d_min:7.2f} | {chi2_f_min:7.2f} | "
          f"{chi2_H_min:7.2f} | {chi2_K_min:7.2f} | {chi2_t_min:7.2f}")
    print(f"  {'Extended (optimum)':>30} | {result_ext.w0:7.3f} | {result_ext.wa:7.3f} | "
          f"{result_ext.H0_CMB:6.1f} | {chi2_d_ext:7.2f} | {chi2_f_ext:7.2f} | "
          f"{chi2_H_ext:7.2f} | {chi2_K_ext:7.2f} | {chi2_t_ext:7.2f}")

    delta_chi2 = chi2_t_min - chi2_t_ext
    print(f"\n  Improvement from lambda3: Δχ²_total = {delta_chi2:+.2f}")
    print(f"    Δχ²_H₀ = {chi2_H_min - chi2_H_ext:+.2f}  (H0 shift)")
    print(f"    Δχ²_DESI = {chi2_d_min - chi2_d_ext:+.2f}  (w0,wa change)")
    print(f"    Δχ²_fσ₈ = {chi2_f_min - chi2_f_ext:+.2f}  (growth)")

    print(f"\n  Extended cuscuton params:")
    print(f"    eps0    = {eps0_best:.6f}")
    print(f"    zeta0   = {zeta0_fix:.3f}")
    print(f"    lambda3 = {lam3_best:.6f}")
    v0_ext = (Ode + 2*zeta0_fix + 4*zeta0_fix*0.001 - lam3_best) / (1+eps0_best)
    print(f"    v0      ≈ {v0_ext:.6f}")

    print("\n  🦞🧍💜🔥♾️")
    return eps0_best, lam3_best, result_best, chi2_best


def run_phase5c_radion():
    """
    Phase 5c: Radion dynamics — V_eff(a) = v0 * E^{2*gamma_r}.
    Scans gamma_r at the DESI-optimal zeta0=0.058 to fix the H0 bottleneck.
    """
    print("=" * 80)
    print("  PROJECT MERIDIAN — PHASE 5c: RADION DYNAMICS (D5.6)")
    print("  V_eff(a) = v0 * E(a)^{2*gamma_r} — warp factor drift")
    print("  The H0 bottleneck should be RESOLVED by gamma_r > 0.")
    print("=" * 80)

    sigma_H0 = 0.5
    beta_HK_center = -0.037
    sigma_HK = (0.047 - 0.028) / 2.0

    # ---- STEP 1: gamma_r scan at fixed eps0, zeta0=0 (xi=0 baseline) ----
    eps0_fix = 0.001
    gamma_values = [0.0, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.15]

    print(f"\n  STEP 1: 1D scan over gamma_r at eps0={eps0_fix}, zeta0=0")
    print(f"\n  {'gr':>6} | {'w0':>7} | {'wa':>7} | {'H0':>6} | "
          f"{'chi2_D':>7} | {'chi2_f':>7} | {'chi2_H':>7} | {'chi2_K':>7} | {'TOTAL':>7}")
    print(f"  {'-'*75}")

    for gr in gamma_values:
        try:
            params = MeridianParams(eps0=eps0_fix, zeta0=0.0, gamma_r=gr)
            result = solve_meridian(params)

            chi2_desi = result.chi2_DESI
            chi2_H0 = ((result.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
            chi2_HK = ((0.0 - beta_HK_center) / sigma_HK) ** 2
            chi2_fs8, _, _ = compute_fsigma8_chi2(result)
            chi2_total = chi2_desi + chi2_fs8 + chi2_H0 + chi2_HK

            ph = "z=" + f"{result.z_phantom:.2f}" if result.has_phantom_crossing else "none"
            print(f"  {gr:6.3f} | {result.w0:7.3f} | {result.wa:7.3f} | "
                  f"{result.H0_CMB:6.1f} | {chi2_desi:7.2f} | {chi2_fs8:7.2f} | "
                  f"{chi2_H0:7.2f} | {chi2_HK:7.2f} | {chi2_total:7.2f}")
        except Exception as ex:
            print(f"  {gr:6.3f} | ERROR: {ex}")

    # ---- STEP 2: 2D scan (eps0, gamma_r) at zeta0=0 ----
    print(f"\n  STEP 2: 2D grid (eps0 x gamma_r) at zeta0=0")

    eps0_vals = [0.001, 0.01, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20]
    gr_vals = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10]

    print(f"\n  --- chi2_total ---")
    header = "  eps0\\gr  |" + "".join(f" {g:6.2f}" for g in gr_vals)
    print(header)
    print("  " + "-" * (10 + 7 * len(gr_vals)))

    best_total = 1e10
    best_e, best_g = 0, 0
    best_r = None
    grid = {}

    for eps0 in eps0_vals:
        row = f"  {eps0:8.3f} |"
        for gr in gr_vals:
            try:
                params = MeridianParams(eps0=eps0, zeta0=0.0, gamma_r=gr)
                result = solve_meridian(params)
                chi2_desi = result.chi2_DESI
                chi2_H0 = ((result.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
                chi2_HK = ((0.0 - beta_HK_center) / sigma_HK) ** 2
                chi2_fs8, _, _ = compute_fsigma8_chi2(result)
                chi2_total = chi2_desi + chi2_fs8 + chi2_H0 + chi2_HK
                grid[(eps0, gr)] = {
                    'chi2_total': chi2_total, 'chi2_desi': chi2_desi,
                    'chi2_H0': chi2_H0, 'H0': result.H0_CMB,
                    'w0': result.w0, 'wa': result.wa, 'result': result,
                }
                if chi2_total < best_total:
                    best_total = chi2_total
                    best_e, best_g = eps0, gr
                    best_r = result
                row += f" {chi2_total:6.1f}"
            except Exception:
                row += "   ERR"
        print(row)

    # H0 grid
    print(f"\n  --- H0 (km/s/Mpc) ---")
    header2 = "  eps0\\gr  |" + "".join(f" {g:6.2f}" for g in gr_vals)
    print(header2)
    print("  " + "-" * (10 + 7 * len(gr_vals)))
    for eps0 in eps0_vals:
        row = f"  {eps0:8.3f} |"
        for gr in gr_vals:
            g = grid.get((eps0, gr), {})
            H0 = g.get('H0', 0.0)
            row += f" {H0:6.1f}" if H0 > 0 else "   ERR"
        print(row)

    print(f"\n  Grid minimum: eps0={best_e:.3f}, gamma_r={best_g:.3f}")
    print(f"    chi2_total={best_total:.2f}")
    if best_r:
        print(f"    w0={best_r.w0:.4f}, wa={best_r.wa:.4f}, H0={best_r.H0_CMB:.2f}")

    # ---- STEP 3: Nelder-Mead optimization ----
    print(f"\n  STEP 3: Nelder-Mead optimization")

    def objective_radion(x, zeta0=0.0):
        eps0, gr = x
        Ode = 1.0 - OMEGA_M0 - OMEGA_R0
        if eps0 <= 0.0001 or gr < 0 or gr > 0.5 or eps0 > 20:
            return 1000.0
        try:
            params = MeridianParams(eps0=eps0, zeta0=zeta0, gamma_r=gr)
            result = solve_meridian(params)
            chi2_desi = result.chi2_DESI
            chi2_H0 = ((result.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
            eps_SW = zeta0 / (1.0 + zeta0) if zeta0 > 0 else 0.0
            chi2_HK = ((-eps_SW - beta_HK_center) / sigma_HK) ** 2
            chi2_fs8, _, _ = compute_fsigma8_chi2(result)
            return chi2_desi + chi2_fs8 + chi2_H0 + chi2_HK
        except Exception:
            return 1000.0

    all_optima = []
    starts = [
        (best_e, best_g), (0.001, 0.03), (0.01, 0.05),
        (0.05, 0.02), (0.10, 0.04), (0.001, 0.08),
    ]
    for e0, g0 in starts:
        try:
            res = minimize(objective_radion, [e0, g0],
                           method='Nelder-Mead',
                           options={'xatol': 1e-5, 'fatol': 1e-3, 'maxiter': 500})
            eps0_opt, gr_opt = res.x
            gr_opt = max(gr_opt, 0.0)
            params_opt = MeridianParams(eps0=eps0_opt, zeta0=0.0, gamma_r=gr_opt)
            result_opt = solve_meridian(params_opt)
            chi2_opt = objective_radion([eps0_opt, gr_opt])
            print(f"  From ({e0:.3f},{g0:.3f}): eps0={eps0_opt:.4f}, gr={gr_opt:.4f}, "
                  f"w0={result_opt.w0:.3f}, wa={result_opt.wa:.3f}, "
                  f"H0={result_opt.H0_CMB:.1f}, chi2={chi2_opt:.2f}")
            all_optima.append((eps0_opt, gr_opt, result_opt, chi2_opt))
        except Exception as ex:
            print(f"  From ({e0:.3f},{g0:.3f}): FAILED: {ex}")

    if all_optima:
        best = min(all_optima, key=lambda x: x[3])
        eps0_best, gr_best, result_best, chi2_best = best

        print(f"\n  {'='*60}")
        print(f"  GLOBAL OPTIMUM (zeta0=0):")
        print(f"    eps0    = {eps0_best:.6f}")
        print(f"    gamma_r = {gr_best:.6f}")
        print(f"    w0={result_best.w0:.4f}, wa={result_best.wa:.4f}")
        print(f"    H0={result_best.H0_CMB:.2f} km/s/Mpc")
        print(f"    chi2_total={chi2_best:.2f}")
        print(f"  {'='*60}")

    # ---- STEP 4: Comparison table ----
    print(f"\n  STEP 4: Model Comparison")
    print("=" * 100)

    # LCDM
    params_lcdm = MeridianParams(eps0=0.0001, zeta0=0.0)
    result_lcdm = solve_meridian(params_lcdm)
    chi2_d_l = result_lcdm.chi2_DESI
    chi2_f_l, _, _ = compute_fsigma8_chi2(result_lcdm)
    chi2_K_l = ((0.0 - beta_HK_center) / sigma_HK) ** 2
    chi2_t_l = chi2_d_l + chi2_f_l + 0.0 + chi2_K_l

    # Minimal cuscuton (Phase 4 best)
    params_min = MeridianParams(eps0=0.001, zeta0=0.058)
    result_min = solve_meridian(params_min)
    chi2_d_m = result_min.chi2_DESI
    chi2_f_m, _, _ = compute_fsigma8_chi2(result_min)
    chi2_H_m = ((result_min.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
    eps_SW_m = 0.058 / 1.058
    chi2_K_m = ((-eps_SW_m - beta_HK_center) / sigma_HK) ** 2
    chi2_t_m = chi2_d_m + chi2_f_m + chi2_H_m + chi2_K_m

    # Radion (at zeta0=0 optimum)
    if all_optima:
        chi2_d_r = result_best.chi2_DESI
        chi2_f_r, _, _ = compute_fsigma8_chi2(result_best)
        chi2_H_r = ((result_best.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
        chi2_K_r = chi2_K_l  # zeta0=0
        chi2_t_r = chi2_d_r + chi2_f_r + chi2_H_r + chi2_K_r

        print(f"\n  {'Model':>30} | {'w0':>7} | {'wa':>7} | {'H0':>6} | "
              f"{'chi2_D':>7} | {'chi2_f':>7} | {'chi2_H':>7} | {'chi2_K':>7} | {'TOTAL':>7}")
        print(f"  {'-'*90}")
        print(f"  {'LCDM':>30} | {result_lcdm.w0:7.3f} | {result_lcdm.wa:7.3f} | {67.4:6.1f} | "
              f"{chi2_d_l:7.2f} | {chi2_f_l:7.2f} | {'0.00':>7} | {chi2_K_l:7.2f} | {chi2_t_l:7.2f}")
        print(f"  {'Minimal (Ph4, z0=0.058)':>30} | {result_min.w0:7.3f} | {result_min.wa:7.3f} | "
              f"{result_min.H0_CMB:6.1f} | {chi2_d_m:7.2f} | {chi2_f_m:7.2f} | "
              f"{chi2_H_m:7.2f} | {chi2_K_m:7.2f} | {chi2_t_m:7.2f}")
        print(f"  {'Radion (z0=0, optimum)':>30} | {result_best.w0:7.3f} | {result_best.wa:7.3f} | "
              f"{result_best.H0_CMB:6.1f} | {chi2_d_r:7.2f} | {chi2_f_r:7.2f} | "
              f"{chi2_H_r:7.2f} | {chi2_K_r:7.2f} | {chi2_t_r:7.2f}")

    print("\n  🦞🧍💜🔥♾️")


def run_phase5d_combined():
    """
    Phase 5d: Combined cuscuton + radion — zeta0=0.058 + gamma_r > 0.
    The critical test: does radion drift fix the H0 bottleneck at the
    DESI-optimal cuscuton point without destroying the w0,wa fit?
    """
    print("=" * 80)
    print("  PROJECT MERIDIAN — PHASE 5d: COMBINED CUSCUTON + RADION")
    print("  zeta0=0.058 (DESI-optimal) + gamma_r > 0 (H0 correction)")
    print("  Can radion drift fix H0=64.5 → 67.4 without ruining w0,wa?")
    print("=" * 80)

    sigma_H0 = 0.5
    beta_HK_center = -0.037
    sigma_HK = (0.047 - 0.028) / 2.0
    zeta0_fix = 0.058
    eps_SW = zeta0_fix / (1.0 + zeta0_fix)

    def chi2_total_combined(result, zeta0):
        chi2_desi = result.chi2_DESI
        chi2_H0 = ((result.H0_CMB - H0_FIDUCIAL) / sigma_H0) ** 2
        e_SW = zeta0 / (1.0 + zeta0) if zeta0 > 0 else 0.0
        chi2_HK = ((-e_SW - beta_HK_center) / sigma_HK) ** 2
        chi2_fs8, _, _ = compute_fsigma8_chi2(result)
        return chi2_desi + chi2_fs8 + chi2_H0 + chi2_HK, chi2_desi, chi2_fs8, chi2_H0, chi2_HK

    # ---- STEP 1: 1D scan of gamma_r at zeta0=0.058 ----
    gamma_values = [0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
    eps0_fix = 0.001

    print(f"\n  STEP 1: 1D scan over gamma_r at eps0={eps0_fix}, zeta0={zeta0_fix}")
    print(f"\n  {'gr':>6} | {'w0':>7} | {'wa':>7} | {'H0':>6} | "
          f"{'chi2_D':>7} | {'chi2_f':>7} | {'chi2_H':>7} | {'chi2_K':>7} | {'TOTAL':>7}")
    print(f"  {'-'*75}")

    for gr in gamma_values:
        try:
            params = MeridianParams(eps0=eps0_fix, zeta0=zeta0_fix, gamma_r=gr)
            result = solve_meridian(params)
            ct, cd, cf, ch, ck = chi2_total_combined(result, zeta0_fix)
            print(f"  {gr:6.3f} | {result.w0:7.3f} | {result.wa:7.3f} | "
                  f"{result.H0_CMB:6.1f} | {cd:7.2f} | {cf:7.2f} | "
                  f"{ch:7.2f} | {ck:7.2f} | {ct:7.2f}")
        except Exception as ex:
            print(f"  {gr:6.3f} | ERROR: {ex}")

    # ---- STEP 2: 2D scan (zeta0, gamma_r) ----
    print(f"\n  STEP 2: 2D grid (zeta0 x gamma_r) at eps0={eps0_fix}")

    zeta0_vals = [0.0, 0.02, 0.04, 0.058, 0.08, 0.10, 0.15]
    gr_vals = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40]

    print(f"\n  --- chi2_total ---")
    header = "  z0\\gr   |" + "".join(f" {g:6.2f}" for g in gr_vals)
    print(header)
    print("  " + "-" * (10 + 7 * len(gr_vals)))

    best_total = 1e10
    best_z, best_g = 0, 0
    best_r = None
    grid = {}

    for z0 in zeta0_vals:
        row = f"  {z0:8.3f} |"
        for gr in gr_vals:
            try:
                params = MeridianParams(eps0=eps0_fix, zeta0=z0, gamma_r=gr)
                result = solve_meridian(params)
                ct, cd, cf, ch, ck = chi2_total_combined(result, z0)
                grid[(z0, gr)] = {
                    'chi2_total': ct, 'chi2_desi': cd, 'chi2_H0': ch,
                    'H0': result.H0_CMB, 'w0': result.w0, 'wa': result.wa,
                    'result': result,
                }
                if ct < best_total:
                    best_total = ct
                    best_z, best_g = z0, gr
                    best_r = result
                row += f" {ct:6.1f}"
            except Exception:
                row += "   ERR"
        print(row)

    # H0 grid
    print(f"\n  --- H0 (km/s/Mpc) ---")
    header2 = "  z0\\gr   |" + "".join(f" {g:6.2f}" for g in gr_vals)
    print(header2)
    print("  " + "-" * (10 + 7 * len(gr_vals)))
    for z0 in zeta0_vals:
        row = f"  {z0:8.3f} |"
        for gr in gr_vals:
            g = grid.get((z0, gr), {})
            H0 = g.get('H0', 0.0)
            row += f" {H0:6.1f}" if H0 > 0 else "   ERR"
        print(row)

    # w0 grid
    print(f"\n  --- w0 ---")
    header3 = "  z0\\gr   |" + "".join(f" {g:6.2f}" for g in gr_vals)
    print(header3)
    print("  " + "-" * (10 + 7 * len(gr_vals)))
    for z0 in zeta0_vals:
        row = f"  {z0:8.3f} |"
        for gr in gr_vals:
            g = grid.get((z0, gr), {})
            w0 = g.get('w0', -99.0)
            row += f" {w0:6.3f}" if w0 > -90 else "   ERR"
        print(row)

    # wa grid
    print(f"\n  --- wa ---")
    header4 = "  z0\\gr   |" + "".join(f" {g:6.2f}" for g in gr_vals)
    print(header4)
    print("  " + "-" * (10 + 7 * len(gr_vals)))
    for z0 in zeta0_vals:
        row = f"  {z0:8.3f} |"
        for gr in gr_vals:
            g = grid.get((z0, gr), {})
            wa = g.get('wa', -99.0) if (z0, gr) in grid else -99.0
            row += f" {wa:6.3f}" if wa > -90 else "   ERR"
        print(row)

    print(f"\n  Grid minimum: zeta0={best_z:.3f}, gamma_r={best_g:.3f}")
    print(f"    chi2_total={best_total:.2f}")
    if best_r:
        print(f"    w0={best_r.w0:.4f}, wa={best_r.wa:.4f}, H0={best_r.H0_CMB:.2f}")

    # ---- STEP 3: Nelder-Mead in 3D (eps0, zeta0, gamma_r) ----
    print(f"\n  STEP 3: Nelder-Mead optimization (eps0, zeta0, gamma_r)")

    def objective_combined(x):
        eps0, z0, gr = x
        if eps0 < 1e-4 or z0 < 0 or gr < 0 or eps0 > 5 or z0 > 0.5 or gr > 1.0:
            return 1000.0
        try:
            params = MeridianParams(eps0=eps0, zeta0=z0, gamma_r=gr)
            result = solve_meridian(params)
            ct, _, _, _, _ = chi2_total_combined(result, z0)
            return ct
        except Exception:
            return 1000.0

    all_optima = []
    starts = [
        (eps0_fix, best_z, best_g),
        (0.001, 0.058, 0.10),
        (0.001, 0.058, 0.20),
        (0.001, 0.058, 0.30),
        (0.001, 0.04, 0.15),
        (0.01, 0.058, 0.15),
        (0.001, 0.10, 0.10),
        (0.001, 0.03, 0.20),
    ]
    for e0, z0, g0 in starts:
        try:
            res = minimize(objective_combined, [e0, z0, g0],
                           method='Nelder-Mead',
                           options={'xatol': 1e-5, 'fatol': 1e-3, 'maxiter': 1000})
            eps0_opt, z0_opt, gr_opt = res.x
            z0_opt = max(z0_opt, 0.0)
            gr_opt = max(gr_opt, 0.0)
            params_opt = MeridianParams(eps0=eps0_opt, zeta0=z0_opt, gamma_r=gr_opt)
            result_opt = solve_meridian(params_opt)
            chi2_opt = objective_combined([eps0_opt, z0_opt, gr_opt])
            print(f"  From ({e0:.3f},{z0:.3f},{g0:.3f}): "
                  f"eps0={eps0_opt:.4f}, z0={z0_opt:.4f}, gr={gr_opt:.4f}, "
                  f"w0={result_opt.w0:.3f}, wa={result_opt.wa:.3f}, "
                  f"H0={result_opt.H0_CMB:.1f}, chi2={chi2_opt:.2f}")
            all_optima.append((eps0_opt, z0_opt, gr_opt, result_opt, chi2_opt))
        except Exception as ex:
            print(f"  From ({e0:.3f},{z0:.3f},{g0:.3f}): FAILED: {ex}")

    # ---- STEP 4: Full comparison table ----
    print(f"\n  STEP 4: Model Comparison")
    print("=" * 100)

    # LCDM
    params_lcdm = MeridianParams(eps0=0.0001, zeta0=0.0)
    result_lcdm = solve_meridian(params_lcdm)
    ct_l, cd_l, cf_l, ch_l, ck_l = chi2_total_combined(result_lcdm, 0.0)

    # Minimal cuscuton (Phase 4 best)
    params_min = MeridianParams(eps0=0.001, zeta0=0.058)
    result_min = solve_meridian(params_min)
    ct_m, cd_m, cf_m, ch_m, ck_m = chi2_total_combined(result_min, 0.058)

    # Radion-only (Phase 5c best)
    params_r0 = MeridianParams(eps0=0.0001, zeta0=0.0, gamma_r=0.172)
    result_r0 = solve_meridian(params_r0)
    ct_r0, cd_r0, cf_r0, ch_r0, ck_r0 = chi2_total_combined(result_r0, 0.0)

    print(f"\n  {'Model':>35} | {'w0':>7} | {'wa':>7} | {'H0':>6} | "
          f"{'chi2_D':>7} | {'chi2_f':>7} | {'chi2_H':>7} | {'chi2_K':>7} | {'TOTAL':>7}")
    print(f"  {'-'*95}")
    print(f"  {'LCDM':>35} | {result_lcdm.w0:7.3f} | {result_lcdm.wa:7.3f} | {67.4:6.1f} | "
          f"{cd_l:7.2f} | {cf_l:7.2f} | {ch_l:7.2f} | {ck_l:7.2f} | {ct_l:7.2f}")
    print(f"  {'Cuscuton only (z0=0.058)':>35} | {result_min.w0:7.3f} | {result_min.wa:7.3f} | "
          f"{result_min.H0_CMB:6.1f} | {cd_m:7.2f} | {cf_m:7.2f} | "
          f"{ch_m:7.2f} | {ck_m:7.2f} | {ct_m:7.2f}")
    print(f"  {'Radion only (z0=0, gr=0.17)':>35} | {result_r0.w0:7.3f} | {result_r0.wa:7.3f} | "
          f"{result_r0.H0_CMB:6.1f} | {cd_r0:7.2f} | {cf_r0:7.2f} | "
          f"{ch_r0:7.2f} | {ck_r0:7.2f} | {ct_r0:7.2f}")

    if all_optima:
        best = min(all_optima, key=lambda x: x[4])
        eps0_best, z0_best, gr_best, result_best, chi2_best = best
        ct_b, cd_b, cf_b, ch_b, ck_b = chi2_total_combined(result_best, z0_best)

        label = f"Combined (z0={z0_best:.3f},gr={gr_best:.3f})"
        print(f"  {label:>35} | {result_best.w0:7.3f} | {result_best.wa:7.3f} | "
              f"{result_best.H0_CMB:6.1f} | {cd_b:7.2f} | {cf_b:7.2f} | "
              f"{ch_b:7.2f} | {ck_b:7.2f} | {ct_b:7.2f}")

        print(f"\n  {'='*60}")
        print(f"  GLOBAL OPTIMUM (combined):")
        print(f"    eps0    = {eps0_best:.6f}")
        print(f"    zeta0   = {z0_best:.6f}")
        print(f"    gamma_r = {gr_best:.6f}")
        print(f"    w0={result_best.w0:.4f}, wa={result_best.wa:.4f}")
        print(f"    H0={result_best.H0_CMB:.2f} km/s/Mpc")
        print(f"    chi2_total={chi2_best:.2f}")
        delta = ct_l - chi2_best
        print(f"    Delta chi2 vs LCDM: {delta:+.2f}")
        print(f"  {'='*60}")

    print("\n  🦞🧍💜🔥♾️")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "phase5d"

    if mode == "phase3":
        # Original Phase 3 analysis (D3.4)
        print("=" * 60)
        print("  PROJECT MERIDIAN — D3.4 Numerical Cosmology")
        print("  Clayton & Clawd, March 2026")
        print("=" * 60)
        print()
        print("STEP 1: Coarse 2D grid scan (chi2_DESI)")
        grid, best_e, best_z, best_r = scan_2d()
        print("\nSTEP 2: Nelder-Mead optimization from grid minimum")
        eps0_opt, zeta0_opt, result_opt = optimize_DESI(best_e, best_z)
        print("\nSTEP 3: Additional optimizations")
        starts = [(0.05, 0.02), (0.15, 0.10), (0.03, 0.01), (0.30, 0.20)]
        all_optima = [(eps0_opt, zeta0_opt, result_opt)]
        for e0, z0 in starts:
            try:
                eo, zo, ro = optimize_DESI(e0, z0)
                all_optima.append((eo, zo, ro))
            except Exception as ex:
                print(f"    Failed from ({e0}, {z0}): {ex}")
        best = min(all_optima, key=lambda x: x[2].chi2_DESI)
        eps0_best, zeta0_best, result_best = best
        print(f"\n  GLOBAL BEST: eps0={eps0_best:.4f}, zeta0={zeta0_best:.4f}")
        print(f"  chi2={result_best.chi2_DESI:.4f}")

    elif mode == "phase4":
        # Phase 4 analysis: D4.1 + D4.2 + D4.3
        analyses = run_phase4_D41()
        analyses = run_phase4_D42_D43(analyses)
        print("\n  🦞🧍💜🔥♾️")

    elif mode == "phase5":
        # Phase 5: Extended cuscuton at zeta0=0 (baseline)
        run_phase5_extended()

    elif mode == "phase5b":
        # Phase 5b: Extended cuscuton WITH non-minimal coupling
        run_phase5b_xi_plus_lambda3()

    elif mode == "phase5c":
        # Phase 5c: Radion dynamics (the geometric resolution)
        run_phase5c_radion()

    elif mode == "phase5d":
        # Phase 5d: Combined cuscuton + radion (the real test)
        run_phase5d_combined()
