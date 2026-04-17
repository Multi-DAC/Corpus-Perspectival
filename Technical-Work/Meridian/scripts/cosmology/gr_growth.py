#!/usr/bin/env python3
"""
Exact GR growth factor computation for Meridian Fit A.
======================================================

Solves the linear growth ODE with mu = Sigma = 1 EXACTLY:

    D''(a) + [3/a + H'(a)/H(a)] D'(a) - (3/2) Omega_m(a) / [a^2 * (aH/H0)^2] D(a) = 0

where the source term is ONLY from matter density (no DE clustering contribution).

This is the Meridian prediction: the cuscuton has zero kinetic energy, so it
does not cluster. The gravitational potentials are sourced entirely by matter.
Standard analyses (including CAMB's fluid model with c_s^2=1) include residual
DE perturbation contributions of order (1+w)(aH/ck)^2, which are ~1-2% but
nonzero. This module eliminates that contribution entirely.

Usage:
    from gr_growth import compute_fsigma8_gr
    fsigma8 = compute_fsigma8_gr(z_array, Om, H0, sigma8_0, w0)

For PRL submission: replace CAMB's get_fsigma8() in Fit A with this function.
The difference quantifies the "perturbation coupling artifact" explicitly.

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: 2026-03-19
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d


def hubble_ratio(a, Om, w0):
    """E(a) = H(a)/H0 for flat wCDM with constant w.

    H^2/H0^2 = Om * a^-3 + (1 - Om) * a^(-3(1+w))
    """
    Ode = 1.0 - Om
    return np.sqrt(Om * a**(-3) + Ode * a**(-3.0 * (1.0 + w0)))


def growth_ode(a, y, Om, w0):
    """Linear growth ODE in terms of scale factor a.

    Variables: y = [D, dD/da]

    The ODE is:
        D''(a) + A(a) D'(a) - B(a) D(a) = 0

    where:
        A(a) = 3/a + (1/H) dH/da
        B(a) = (3/2) Om_m(a) / [a^2 * E(a)^2]

    and Om_m(a) = Om * a^-3 / E(a)^2 is the matter fraction at scale factor a.

    The key: no DE perturbation source term. Only matter sources gravity.
    This is mu = Sigma = 1 exactly.
    """
    D, Dp = y  # D and dD/da

    E = hubble_ratio(a, Om, w0)
    Ode = 1.0 - Om

    # dE/da via chain rule from E^2 expression
    # d(E^2)/da = -3 Om a^-4 - 3(1+w) (1-Om) a^(-3(1+w)-1)
    dE2da = -3.0 * Om * a**(-4) - 3.0 * (1.0 + w0) * Ode * a**(-3.0 * (1.0 + w0) - 1.0)
    dEda = dE2da / (2.0 * E)

    # Friction term
    A = 3.0 / a + dEda / E

    # Source term: only matter (mu = Sigma = 1, no DE clustering)
    Omm_a = Om * a**(-3) / E**2  # matter fraction at scale factor a
    B = 1.5 * Omm_a / a**2

    # D'' = -A D' + B D
    Dpp = -A * Dp + B * D

    return [Dp, Dpp]


def compute_growth_factor(Om, w0, z_array, a_start=1e-4):
    """Compute the linear growth factor D(z) normalized so D(0) = 1.

    Uses exact GR perturbation equations (mu = Sigma = 1, matter-only source).

    Parameters
    ----------
    Om : float
        Present-day matter density parameter.
    w0 : float
        Constant dark energy equation of state.
    z_array : array-like
        Redshifts at which to evaluate D(z).
    a_start : float
        Starting scale factor for integration (deep in matter domination).

    Returns
    -------
    D_z : ndarray
        Growth factor D(z) normalized to D(z=0) = 1.
    f_z : ndarray
        Growth rate f(z) = d ln D / d ln a.
    """
    z_array = np.atleast_1d(z_array)

    # Initial conditions deep in matter domination: D ~ a, D' ~ 1
    y0 = [a_start, 1.0]

    # Integrate from a_start to a=1 (z=0)
    a_end = 1.0
    a_eval = np.sort(np.unique(np.concatenate([
        np.linspace(a_start, a_end, 2000),
        1.0 / (1.0 + z_array)  # ensure we evaluate at requested redshifts
    ])))

    sol = solve_ivp(
        growth_ode, [a_start, a_end], y0,
        args=(Om, w0),
        t_eval=a_eval,
        method='RK45',
        rtol=1e-10, atol=1e-12,
        dense_output=True
    )

    if not sol.success:
        raise RuntimeError(f"Growth ODE integration failed: {sol.message}")

    # Normalize: D(a=1) = 1
    D_of_a = sol.y[0]
    Dp_of_a = sol.y[1]
    D0 = np.interp(1.0, sol.t, D_of_a)

    D_of_a /= D0
    Dp_of_a /= D0

    # Interpolate to requested redshifts
    a_requested = 1.0 / (1.0 + z_array)

    D_z = np.interp(a_requested, sol.t, D_of_a)

    # Growth rate: f = d ln D / d ln a = (a/D) * dD/da
    Dp_z = np.interp(a_requested, sol.t, Dp_of_a)
    f_z = a_requested * Dp_z / D_z

    return D_z, f_z


def compute_fsigma8_gr(z_array, Om, H0, sigma8_0, w0):
    """Compute f*sigma8(z) using exact GR growth (mu = Sigma = 1).

    This is the Meridian prediction for Fit A: background evolves with
    constant w, but perturbations obey GR identically (cuscuton doesn't cluster).

    Parameters
    ----------
    z_array : array-like
        Redshifts.
    Om : float
        Present-day matter density.
    H0 : float
        Hubble constant in km/s/Mpc.
    sigma8_0 : float
        sigma8 at z=0 (from CAMB or measured).
    w0 : float
        Constant dark energy equation of state.

    Returns
    -------
    fsigma8 : ndarray
        f(z) * sigma8(z) at each redshift.
    """
    D_z, f_z = compute_growth_factor(Om, w0, z_array)

    sigma8_z = sigma8_0 * D_z
    fsigma8 = f_z * sigma8_z

    return fsigma8


def compare_with_camb(w0=-0.746, Om=0.315, H0=67.36):
    """Compare exact GR growth with CAMB's fluid model.

    Quantifies the residual DE perturbation effect in CAMB's c_s^2=1 fluid.
    """
    try:
        import camb
    except ImportError:
        print("CAMB not available for comparison")
        return

    z_test = np.array([0.067, 0.38, 0.51, 0.61, 0.70, 0.85, 1.48])

    # CAMB computation (fluid model, c_s^2 = 1)
    ombh2 = 0.02237
    h = H0 / 100.0
    omch2 = Om * h**2 - ombh2

    pars = camb.CAMBparams()
    pars.set_cosmology(H0=H0, ombh2=ombh2, omch2=omch2, mnu=0.06, num_massive_neutrinos=1)
    pars.set_dark_energy(w=w0, dark_energy_model='fluid')
    pars.InitPower.set_params(As=2.1e-9, ns=0.9649)
    pars.set_matter_power(redshifts=sorted(list(z_test) + [0.0]), kmax=2.0)
    pars.WantTransfer = True
    pars.NonLinear = camb.model.NonLinear_none

    results = camb.get_results(pars)

    # CAMB's fsigma8
    all_z = sorted(list(z_test) + [0.0])
    all_fs8_camb = results.get_fsigma8()
    fs8_camb = np.interp(z_test, all_z, all_fs8_camb)

    sigma8_0 = results.get_sigma8_0()

    # Exact GR computation
    fs8_gr = compute_fsigma8_gr(z_test, Om, H0, sigma8_0, w0)

    print(f"Comparison: CAMB fluid (cs2=1) vs Exact GR (mu=Sigma=1)")
    print(f"w0 = {w0}, Om = {Om}, H0 = {H0}, sigma8_0 = {sigma8_0:.4f}")
    print(f"{'z':>6s}  {'CAMB':>8s}  {'GR':>8s}  {'diff':>8s}  {'%diff':>8s}")
    for i, z in enumerate(z_test):
        diff = fs8_camb[i] - fs8_gr[i]
        pct = 100 * diff / fs8_gr[i]
        print(f"{z:6.3f}  {fs8_camb[i]:8.4f}  {fs8_gr[i]:8.4f}  {diff:+8.5f}  {pct:+8.3f}%")


if __name__ == '__main__':
    compare_with_camb()
