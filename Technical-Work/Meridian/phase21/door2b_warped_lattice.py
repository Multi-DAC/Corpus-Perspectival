#!/usr/bin/env python3
"""
Door 2B — Warped Lattice Gauge Theory: Non-perturbative test of gauge universality on RS1

Simulates SU(2) and U(1) gauge theories on a 5D warped lattice (discretized Randall-Sundrum)
using Metropolis Monte Carlo. Measures gauge coupling at each y-slice via average plaquette
and Creutz ratios, comparing SU(2) (which has instantons/confinement) against U(1) (which
does not) to detect non-perturbative gauge-dependent corrections near the IR brane.

Physics: The RS1 metric ds^2 = e^{-2ky} eta_{mu nu} dx^mu dx^nu + dy^2 discretized on a
lattice with L^3 x L_t spatial sites and N5 extra-dimension sites. Warp factor w_j = e^{-k*j*a5}
modifies the plaquette action at each y-slice.

Key prediction: if non-perturbative effects break gauge universality, the ratio
r(j) = g^2_SU(2)(j) / g^2_U(1)(j) should deviate from 1 near the IR brane (large j),
and the deviation should grow with kL.

Project Meridian Phase 21, Track 21A.4 — Computation C
"""

import numpy as np
import time
import sys
import os

# ============================================================
# CONFIGURATION
# ============================================================

class Config:
    """Simulation parameters."""
    # Lattice geometry
    L = 6              # Spatial extent (4D)
    Lt = 6             # Temporal extent
    N5 = 12            # Extra dimension sites

    # Warp parameters to scan
    kL_values = [2.0, 4.0, 6.0]  # kL = k * L_5 (total warp)

    # Coupling (inverse coupling beta_0 = 2N/g^2 for SU(N))
    beta0_su2 = 2.4    # SU(2): in the crossover region
    beta0_u1 = 1.0     # U(1): scaled for comparison

    # Monte Carlo parameters
    n_therm = 200       # Thermalization sweeps
    n_meas = 150        # Measurement sweeps
    n_skip = 5          # Sweeps between measurements
    metropolis_eps_su2 = 0.3   # SU(2) proposal width
    metropolis_eps_u1 = 0.5    # U(1) proposal width

    # Wilson loop sizes for Creutz ratios
    wilson_R_max = 3    # Max spatial extent
    wilson_T_max = 3    # Max temporal extent

    # Random seed
    seed = 42

# ============================================================
# SU(2) MATRIX OPERATIONS
# ============================================================

def random_su2_near_identity(eps, shape=None):
    """Generate random SU(2) matrix near identity.

    Parametrize as U = a0*I + i*(a1*s1 + a2*s2 + a3*s3) with |a|^2 = 1.
    Generate a1,a2,a3 uniform in [-eps, eps], compute a0 = sqrt(1 - |a_vec|^2).
    If |a_vec|^2 > 1, resample.
    """
    if shape is None:
        while True:
            a_vec = np.random.uniform(-eps, eps, size=3)
            r2 = np.sum(a_vec**2)
            if r2 < 1.0:
                a0 = np.sqrt(1.0 - r2)
                return _su2_from_quaternion(a0, a_vec)
    else:
        # Vectorized version for initialization
        total = int(np.prod(shape))
        results = np.zeros((total, 2, 2), dtype=complex)
        count = 0
        while count < total:
            batch = total - count
            a_vec = np.random.uniform(-eps, eps, size=(batch, 3))
            r2 = np.sum(a_vec**2, axis=1)
            valid = r2 < 1.0
            n_valid = np.sum(valid)
            if n_valid > 0:
                a0 = np.sqrt(1.0 - r2[valid])
                for i in range(n_valid):
                    results[count] = _su2_from_quaternion(a0[i], a_vec[valid][i])
                    count += 1
        return results.reshape(shape + (2, 2))


def _su2_from_quaternion(a0, a_vec):
    """Construct SU(2) matrix from quaternion components.

    U = ( a0 + i*a3,   a2 + i*a1 )
        ( -a2 + i*a1,  a0 - i*a3 )
    """
    a1, a2, a3 = a_vec
    return np.array([
        [a0 + 1j*a3,  a2 + 1j*a1],
        [-a2 + 1j*a1, a0 - 1j*a3]
    ], dtype=complex)


def random_su2():
    """Generate a uniformly random SU(2) matrix (for hot start)."""
    # Generate random quaternion on S^3
    a = np.random.randn(4)
    a /= np.linalg.norm(a)
    return _su2_from_quaternion(a[0], a[1:])


def su2_dagger(U):
    """Hermitian conjugate of SU(2) matrix."""
    return U.conj().T


def su2_identity():
    """Return SU(2) identity matrix."""
    return np.eye(2, dtype=complex)


def su2_trace(U):
    """Return trace of SU(2) matrix (real part for normalized plaquette)."""
    return U[0, 0] + U[1, 1]


# ============================================================
# U(1) OPERATIONS
# ============================================================

def random_u1_near_identity(eps):
    """Generate U(1) element near identity: exp(i*delta) with delta ~ Uniform(-eps, eps)."""
    return np.exp(1j * np.random.uniform(-eps, eps))


def random_u1():
    """Generate uniformly random U(1) element."""
    return np.exp(1j * np.random.uniform(0, 2*np.pi))


# ============================================================
# LATTICE CLASS
# ============================================================

class WarpedLattice:
    """5D warped lattice for gauge theory simulation.

    Dimensions: (x, y, z, t, y5) with sizes (L, L, L, Lt, N5)
    Directions: mu = 0,1,2,3 (4D), mu = 4 (extra dimension)
    Links: U[x,y,z,t,y5,mu] stores the gauge link variable.
    """

    def __init__(self, config, kL, gauge_group='SU2'):
        self.L = config.L
        self.Lt = config.Lt
        self.N5 = config.N5
        self.kL = kL
        self.gauge_group = gauge_group
        self.config = config

        # Derived
        self.k = kL / self.N5  # k*a5 per site (a5 = 1 in lattice units)
        self.dims = (self.L, self.L, self.L, self.Lt, self.N5)
        self.ndirs = 5  # 4D + extra dimension

        # Warp factor at each y5-slice
        self.warp = np.exp(-self.k * np.arange(self.N5))  # w_j = e^{-k*j}

        # Initialize links
        if gauge_group == 'SU2':
            self._init_su2()
        elif gauge_group == 'U1':
            self._init_u1()
        else:
            raise ValueError(f"Unknown gauge group: {gauge_group}")

    def _init_su2(self):
        """Initialize SU(2) link variables (cold start = identity)."""
        shape = self.dims + (self.ndirs,)
        # Cold start: all links = identity
        self.links = np.zeros(shape + (2, 2), dtype=complex)
        for idx in np.ndindex(shape):
            self.links[idx] = su2_identity()

    def _init_u1(self):
        """Initialize U(1) link variables (cold start = 1)."""
        shape = self.dims + (self.ndirs,)
        self.links = np.ones(shape, dtype=complex)

    def site_shift(self, site, mu, direction=+1):
        """Return site shifted by one step in direction mu.

        Periodic BC in 4D (mu=0,1,2,3).
        Dirichlet BC in extra dim (mu=4): clamp to boundaries.
        """
        site = list(site)
        if mu < 4:
            # Periodic BC
            sizes = [self.L, self.L, self.L, self.Lt]
            site[mu] = (site[mu] + direction) % sizes[mu]
        else:
            # Extra dimension: clamp at boundaries (Dirichlet-like)
            site[4] = site[4] + direction
            site[4] = max(0, min(self.N5 - 1, site[4]))
        return tuple(site)

    def get_link(self, site, mu):
        """Get link variable U_mu(site)."""
        return self.links[site + (mu,)]

    def set_link(self, site, mu, U):
        """Set link variable U_mu(site)."""
        self.links[site + (mu,)] = U

    def get_link_dag(self, site, mu):
        """Get U_mu^dagger(site)."""
        U = self.get_link(site, mu)
        if self.gauge_group == 'SU2':
            return su2_dagger(U)
        else:
            return np.conj(U)

    def plaquette(self, site, mu, nu):
        """Compute plaquette U_mu(x) U_nu(x+mu) U_mu^dag(x+nu) U_nu^dag(x).

        Returns the matrix (SU(2)) or complex number (U(1)).
        """
        x = site
        x_mu = self.site_shift(x, mu, +1)
        x_nu = self.site_shift(x, nu, +1)

        U1 = self.get_link(x, mu)
        U2 = self.get_link(x_mu, nu)
        U3 = self.get_link_dag(x_nu, mu)
        U4 = self.get_link_dag(x, nu)

        if self.gauge_group == 'SU2':
            return U1 @ U2 @ U3 @ U4
        else:
            return U1 * U2 * U3 * U4

    def plaquette_trace(self, site, mu, nu):
        """Real part of normalized plaquette trace.

        For SU(2): Re[Tr(P)]/2  (normalized to [0,1])
        For U(1): Re[P]         (already normalized)
        """
        P = self.plaquette(site, mu, nu)
        if self.gauge_group == 'SU2':
            return su2_trace(P).real / 2.0
        else:
            return P.real

    def staple(self, site, mu):
        """Compute the sum of staples around link U_mu(site).

        Staple for each nu != mu:
          Forward: U_nu(x+mu) U_mu^dag(x+nu) U_nu^dag(x)
          Backward: U_nu^dag(x+mu-nu) U_mu^dag(x-nu) U_nu(x-nu)

        Returns the sum over all staples (matrix for SU(2), complex for U(1)).
        """
        x = site
        x_mu = self.site_shift(x, mu, +1)

        if self.gauge_group == 'SU2':
            S = np.zeros((2, 2), dtype=complex)
        else:
            S = 0.0 + 0j

        for nu in range(self.ndirs):
            if nu == mu:
                continue

            # Forward staple
            x_nu = self.site_shift(x, nu, +1)
            x_mu_nu = self.site_shift(x_mu, nu, +1)

            U2 = self.get_link(x_mu, nu)
            U3 = self.get_link_dag(x_nu, mu)
            U4 = self.get_link_dag(x, nu)

            if self.gauge_group == 'SU2':
                S += U2 @ U3 @ U4
            else:
                S += U2 * U3 * U4

            # Backward staple
            x_nu_back = self.site_shift(x, nu, -1)
            x_mu_nu_back = self.site_shift(x_mu, nu, -1)

            U2b = self.get_link_dag(x_mu_nu_back, nu)
            U3b = self.get_link_dag(x_nu_back, mu)
            U4b = self.get_link(x_nu_back, nu)

            if self.gauge_group == 'SU2':
                S += U2b @ U3b @ U4b
            else:
                S += U2b * U3b * U4b

        return S

    def warped_beta(self, site, mu, nu):
        """Compute the warped inverse coupling for a plaquette at (site, mu, nu).

        4D plaquettes (both mu,nu < 4): beta = beta0 * w_j^4
        Mixed plaquettes (one of mu,nu = 4): beta = beta0 * w_j^2
        5-5 plaquettes: not physical (only 1 extra dim)
        """
        j = site[4]  # Position in extra dimension
        wj = self.warp[j]

        if self.gauge_group == 'SU2':
            beta0 = self.config.beta0_su2
        else:
            beta0 = self.config.beta0_u1

        if mu < 4 and nu < 4:
            return beta0 * wj**4
        elif mu == 4 or nu == 4:
            return beta0 * wj**2
        else:
            return beta0  # Shouldn't happen


# ============================================================
# MONTE CARLO UPDATE
# ============================================================

def metropolis_sweep_su2(lattice, eps):
    """Perform one Metropolis sweep over all SU(2) links.

    For each link U_mu(x):
      1. Compute staple S_mu(x)
      2. Propose U' = dU * U where dU is near-identity SU(2)
      3. Compute Delta_S = sum over plaquettes containing U
      4. Accept with probability min(1, exp(-Delta_S))

    Returns acceptance rate.
    """
    accepted = 0
    total = 0
    dims = lattice.dims
    ndirs = lattice.ndirs

    for x0 in range(dims[0]):
        for x1 in range(dims[1]):
            for x2 in range(dims[2]):
                for x3 in range(dims[3]):
                    for x4 in range(dims[4]):
                        site = (x0, x1, x2, x3, x4)
                        for mu in range(ndirs):
                            # Skip mu=4 links at boundaries
                            if mu == 4 and x4 == dims[4] - 1:
                                continue

                            total += 1
                            U_old = lattice.get_link(site, mu)
                            staple = lattice.staple(site, mu)

                            # Compute action contribution of old link
                            # S_old = -beta * Re[Tr(U_old * S)] / N
                            # For SU(2), N = 2
                            old_contrib = su2_trace(U_old @ staple).real

                            # Propose new link
                            dU = random_su2_near_identity(eps)
                            U_new = dU @ U_old

                            new_contrib = su2_trace(U_new @ staple).real

                            # The action change depends on the warped beta
                            # But since staple already sums over all plaquettes
                            # containing this link, we need the effective beta.
                            # For simplicity with warped lattice: compute the
                            # average warped beta for plaquettes touching this link.
                            # Actually, the correct approach: the staple already
                            # carries the proper weight if we weight each staple
                            # contribution by its beta.

                            # Recompute with warped staple
                            warped_staple = _warped_staple_su2(lattice, site, mu)
                            old_contrib_w = su2_trace(U_old @ warped_staple).real / 2.0
                            new_contrib_w = su2_trace(U_new @ warped_staple).real / 2.0

                            delta_S = -(new_contrib_w - old_contrib_w)

                            if delta_S < 0 or np.random.random() < np.exp(-delta_S):
                                lattice.set_link(site, mu, U_new)
                                accepted += 1

    return accepted / max(total, 1)


def _warped_staple_su2(lattice, site, mu):
    """Compute warped staple: each staple contribution weighted by the
    warped beta of the corresponding plaquette."""
    x = site
    x_mu = lattice.site_shift(x, mu, +1)
    S = np.zeros((2, 2), dtype=complex)

    for nu in range(lattice.ndirs):
        if nu == mu:
            continue

        beta_plaq = lattice.warped_beta(site, mu, nu)

        # Forward staple
        x_nu = lattice.site_shift(x, nu, +1)
        U2 = lattice.get_link(x_mu, nu)
        U3 = lattice.get_link_dag(x_nu, mu)
        U4 = lattice.get_link_dag(x, nu)
        S += beta_plaq * (U2 @ U3 @ U4)

        # Backward staple
        x_nu_back = lattice.site_shift(x, nu, -1)
        x_mu_nu_back = lattice.site_shift(x_mu, nu, -1)

        # The plaquette involving the backward staple lives at x-nu
        site_back = x_nu_back
        beta_plaq_back = lattice.warped_beta(site_back, mu, nu)

        U2b = lattice.get_link_dag(x_mu_nu_back, nu)
        U3b = lattice.get_link_dag(x_nu_back, mu)
        U4b = lattice.get_link(x_nu_back, nu)
        S += beta_plaq_back * (U2b @ U3b @ U4b)

    return S


def metropolis_sweep_u1(lattice, eps):
    """Perform one Metropolis sweep over all U(1) links."""
    accepted = 0
    total = 0
    dims = lattice.dims
    ndirs = lattice.ndirs

    for x0 in range(dims[0]):
        for x1 in range(dims[1]):
            for x2 in range(dims[2]):
                for x3 in range(dims[3]):
                    for x4 in range(dims[4]):
                        site = (x0, x1, x2, x3, x4)
                        for mu in range(ndirs):
                            if mu == 4 and x4 == dims[4] - 1:
                                continue

                            total += 1
                            U_old = lattice.get_link(site, mu)

                            # Warped staple for U(1)
                            warped_staple = _warped_staple_u1(lattice, site, mu)

                            old_contrib = (U_old * warped_staple).real
                            dU = random_u1_near_identity(eps)
                            U_new = dU * U_old
                            new_contrib = (U_new * warped_staple).real

                            delta_S = -(new_contrib - old_contrib)

                            if delta_S < 0 or np.random.random() < np.exp(-delta_S):
                                lattice.set_link(site, mu, U_new)
                                accepted += 1

    return accepted / max(total, 1)


def _warped_staple_u1(lattice, site, mu):
    """Compute warped staple for U(1) gauge theory."""
    x = site
    x_mu = lattice.site_shift(x, mu, +1)
    S = 0.0 + 0j

    for nu in range(lattice.ndirs):
        if nu == mu:
            continue

        beta_plaq = lattice.warped_beta(site, mu, nu)

        # Forward staple
        x_nu = lattice.site_shift(x, nu, +1)
        U2 = lattice.get_link(x_mu, nu)
        U3 = np.conj(lattice.get_link(x_nu, mu))
        U4 = np.conj(lattice.get_link(x, nu))
        S += beta_plaq * U2 * U3 * U4

        # Backward staple
        x_nu_back = lattice.site_shift(x, nu, -1)
        x_mu_nu_back = lattice.site_shift(x_mu, nu, -1)

        site_back = x_nu_back
        beta_plaq_back = lattice.warped_beta(site_back, mu, nu)

        U2b = np.conj(lattice.get_link(x_mu_nu_back, nu))
        U3b = np.conj(lattice.get_link(x_nu_back, mu))
        U4b = lattice.get_link(x_nu_back, nu)
        S += beta_plaq_back * U2b * U3b * U4b

    return S


# ============================================================
# MEASUREMENTS
# ============================================================

def measure_plaquette_by_slice(lattice):
    """Measure average plaquette at each y5-slice.

    Returns arrays:
      plaq_4d[j] = average of 4D plaquettes at slice j
      plaq_mixed[j] = average of mixed (mu,5) plaquettes at slice j
    """
    L, Lt, N5 = lattice.L, lattice.Lt, lattice.N5
    plaq_4d = np.zeros(N5)
    plaq_mixed = np.zeros(N5)
    count_4d = np.zeros(N5)
    count_mixed = np.zeros(N5)

    for x0 in range(L):
        for x1 in range(L):
            for x2 in range(L):
                for x3 in range(Lt):
                    for x4 in range(N5):
                        site = (x0, x1, x2, x3, x4)

                        # 4D plaquettes: 6 orientations (01,02,03,12,13,23)
                        for mu in range(4):
                            for nu in range(mu+1, 4):
                                p = lattice.plaquette_trace(site, mu, nu)
                                plaq_4d[x4] += p
                                count_4d[x4] += 1

                        # Mixed plaquettes: 4 orientations (04,14,24,34)
                        if x4 < N5 - 1:  # Only if not at boundary
                            for mu in range(4):
                                p = lattice.plaquette_trace(site, mu, 4)
                                plaq_mixed[x4] += p
                                count_mixed[x4] += 1

    # Normalize
    for j in range(N5):
        if count_4d[j] > 0:
            plaq_4d[j] /= count_4d[j]
        if count_mixed[j] > 0:
            plaq_mixed[j] /= count_mixed[j]

    return plaq_4d, plaq_mixed


def measure_wilson_loop(lattice, R, T, y_slice):
    """Measure Wilson loop W(R,T) at a specific y5-slice.

    Computed in the (0,3) plane (x-direction spatial, t-direction temporal).
    Averaged over all starting positions at the given y_slice.

    For SU(2): W = Re[Tr(loop product)]/2
    For U(1): W = Re[loop product]
    """
    L, Lt = lattice.L, lattice.Lt
    total = 0.0
    count = 0

    mu_space = 0  # spatial direction
    mu_time = 3   # temporal direction

    for x1 in range(L):
        for x2 in range(L):
            for x3 in range(Lt):
                # Starting site
                site = [0, x1, x2, x3, y_slice]

                if lattice.gauge_group == 'SU2':
                    # Build the Wilson loop as a product of link matrices
                    loop = su2_identity()

                    # Bottom edge: R links in spatial direction
                    current = list(site)
                    for r in range(R):
                        loop = loop @ lattice.get_link(tuple(current), mu_space)
                        current = list(lattice.site_shift(tuple(current), mu_space, +1))

                    # Right edge: T links in temporal direction
                    for t in range(T):
                        loop = loop @ lattice.get_link(tuple(current), mu_time)
                        current = list(lattice.site_shift(tuple(current), mu_time, +1))

                    # Top edge: R links backward in spatial direction
                    for r in range(R):
                        current = list(lattice.site_shift(tuple(current), mu_space, -1))
                        loop = loop @ lattice.get_link_dag(tuple(current), mu_space)

                    # Left edge: T links backward in temporal direction
                    for t in range(T):
                        current = list(lattice.site_shift(tuple(current), mu_time, -1))
                        loop = loop @ lattice.get_link_dag(tuple(current), mu_time)

                    total += su2_trace(loop).real / 2.0

                else:
                    # U(1) Wilson loop
                    loop = 1.0 + 0j
                    current = list(site)

                    for r in range(R):
                        loop *= lattice.get_link(tuple(current), mu_space)
                        current = list(lattice.site_shift(tuple(current), mu_space, +1))

                    for t in range(T):
                        loop *= lattice.get_link(tuple(current), mu_time)
                        current = list(lattice.site_shift(tuple(current), mu_time, +1))

                    for r in range(R):
                        current = list(lattice.site_shift(tuple(current), mu_space, -1))
                        loop *= np.conj(lattice.get_link(tuple(current), mu_space))

                    for t in range(T):
                        current = list(lattice.site_shift(tuple(current), mu_time, -1))
                        loop *= np.conj(lattice.get_link(tuple(current), mu_time))

                    total += loop.real

                count += 1

    return total / max(count, 1)


def measure_polyakov_extra_dim(lattice):
    """Measure Polyakov loop in the extra dimension at each 4D site.

    P(x) = Tr[prod_{j=0}^{N5-1} U_4(x, j)] / N

    For Dirichlet BC, this is the order parameter for 'deconfinement' along y.
    Returns average |P| over all 4D sites.
    """
    L, Lt, N5 = lattice.L, lattice.Lt, lattice.N5
    total_abs = 0.0
    count = 0

    for x0 in range(L):
        for x1 in range(L):
            for x2 in range(L):
                for x3 in range(Lt):
                    if lattice.gauge_group == 'SU2':
                        P = su2_identity()
                        for j in range(N5 - 1):
                            P = P @ lattice.get_link((x0, x1, x2, x3, j), 4)
                        total_abs += abs(su2_trace(P).real / 2.0)
                    else:
                        P = 1.0 + 0j
                        for j in range(N5 - 1):
                            P *= lattice.get_link((x0, x1, x2, x3, j), 4)
                        total_abs += abs(P.real)
                    count += 1

    return total_abs / max(count, 1)


def measure_topological_charge_su2(lattice, y_slice):
    """Estimate topological charge at a y-slice for SU(2).

    Uses the clover definition:
    Q = (1/16pi^2) sum_x sum_{mu<nu} epsilon_{mu nu rho sigma}
        Tr[F_{mu nu}(x) F_{rho sigma}(x)]

    where F_{mu nu} is approximated by the clover (average of 4 plaquettes).

    Simplified: sum over all 4D plaquettes of Im[Tr(P_{01} P_{23} - P_{02} P_{13} + P_{03} P_{12})]
    For a rough estimate, use sum of Im[Tr(plaquette)] as a proxy.
    """
    L, Lt = lattice.L, lattice.Lt
    Q = 0.0

    for x0 in range(L):
        for x1 in range(L):
            for x2 in range(L):
                for x3 in range(Lt):
                    site = (x0, x1, x2, x3, y_slice)

                    # Clover-like: F_{01} * F_{23}
                    P01 = lattice.plaquette(site, 0, 1)
                    P23 = lattice.plaquette(site, 2, 3)
                    P02 = lattice.plaquette(site, 0, 2)
                    P13 = lattice.plaquette(site, 1, 3)
                    P03 = lattice.plaquette(site, 0, 3)
                    P12 = lattice.plaquette(site, 1, 2)

                    # Q ~ Tr(F_tilde * F) = epsilon_munurhosig * Tr(F_munu F_rhosig)
                    Q += su2_trace(P01 @ P23).imag
                    Q -= su2_trace(P02 @ P13).imag
                    Q += su2_trace(P03 @ P12).imag

    return Q / (16.0 * np.pi**2)


def extract_coupling_from_plaquette(plaq_value, gauge_group):
    """Extract effective coupling g^2_eff from average plaquette.

    For weak coupling (perturbation theory):
      <P> = 1 - g^2 * C / (4N)  (leading order)

    where C is the Casimir (depends on the group representation and dimension).

    For SU(2) in d=4: <P> ~ 1 - 3/(4*beta) + ...
      so g^2 ~ 4*(1-<P>) / (3/4) = 16*(1-<P>)/3

    For U(1) in d=4: <P> ~ 1 - 1/(2*beta) + ...
      so g^2 ~ 2*(1-<P>)

    We use the simplified extraction:
      g^2_eff = c * (1 - <P>)  where c is a normalization constant.

    Since we're comparing RATIOS, the normalization cancels.
    """
    if gauge_group == 'SU2':
        # Strong coupling expansion: <P> = 1 - d*(d-1)/(4*beta^2) + ...
        # Weak coupling: <P> = 1 - (d-1)/(2*N*beta) + ...
        # For the ratio comparison, use 1 - <P> as proxy for g^2
        return 1.0 - plaq_value
    else:
        return 1.0 - plaq_value


def creutz_ratio(W, I, J):
    """Compute Creutz ratio chi(I,J) from Wilson loop data.

    chi(I,J) = -ln[W(I,J) * W(I-1,J-1) / (W(I,J-1) * W(I-1,J))]

    Returns the string tension / effective coupling proxy.
    """
    if I < 1 or J < 1:
        return None
    if W.get((I,J), 0) <= 0 or W.get((I-1,J-1), 0) <= 0:
        return None
    if W.get((I,J-1), 0) <= 0 or W.get((I-1,J), 0) <= 0:
        return None

    ratio = W[(I,J)] * W[(I-1,J-1)] / (W[(I,J-1)] * W[(I-1,J)])
    if ratio <= 0:
        return None
    return -np.log(ratio)


# ============================================================
# MAIN SIMULATION
# ============================================================

def run_simulation(config, kL, gauge_group, verbose=True):
    """Run full MC simulation for one gauge group at one kL value.

    Returns dict of measurements.
    """
    t0 = time.time()

    if verbose:
        print(f"\n{'='*60}")
        print(f"  {gauge_group} | kL = {kL:.1f} | L = {config.L} | N5 = {config.N5}")
        print(f"{'='*60}")

    lattice = WarpedLattice(config, kL, gauge_group)

    if gauge_group == 'SU2':
        eps = config.metropolis_eps_su2
        sweep_fn = lambda lat: metropolis_sweep_su2(lat, eps)
    else:
        eps = config.metropolis_eps_u1
        sweep_fn = lambda lat: metropolis_sweep_u1(lat, eps)

    # Thermalization
    if verbose:
        print(f"  Thermalizing ({config.n_therm} sweeps)...")

    acc_rates = []
    for i in range(config.n_therm):
        acc = sweep_fn(lattice)
        acc_rates.append(acc)
        if verbose and (i+1) % 50 == 0:
            print(f"    Sweep {i+1}/{config.n_therm}, acc = {np.mean(acc_rates[-50:]):.3f}")

    if verbose:
        print(f"  Thermalization done. Avg acceptance = {np.mean(acc_rates):.3f}")

    # Measurements
    if verbose:
        print(f"  Measuring ({config.n_meas} measurements, skip {config.n_skip})...")

    plaq_4d_all = []
    plaq_mixed_all = []
    polyakov_all = []
    wilson_data = []  # list of dicts: {(R,T): W_value} for each measurement
    topo_charge_all = []  # SU(2) only

    for m in range(config.n_meas):
        # Skip sweeps
        for s in range(config.n_skip):
            sweep_fn(lattice)

        # Measure plaquettes
        p4d, pmix = measure_plaquette_by_slice(lattice)
        plaq_4d_all.append(p4d.copy())
        plaq_mixed_all.append(pmix.copy())

        # Polyakov loop in extra dim
        poly = measure_polyakov_extra_dim(lattice)
        polyakov_all.append(poly)

        # Wilson loops at UV (j=0) and IR (j=N5-1) slices
        w_data = {}
        for j_slice in [0, config.N5 // 2, config.N5 - 1]:
            for R in range(1, config.wilson_R_max + 1):
                for T in range(1, config.wilson_T_max + 1):
                    w = measure_wilson_loop(lattice, R, T, j_slice)
                    w_data[(R, T, j_slice)] = w
        wilson_data.append(w_data)

        # Topological charge (SU(2) only, at 3 slices)
        if gauge_group == 'SU2':
            q_list = []
            for j_slice in [0, config.N5 // 2, config.N5 - 1]:
                q = measure_topological_charge_su2(lattice, j_slice)
                q_list.append(q)
            topo_charge_all.append(q_list)

        if verbose and (m+1) % 25 == 0:
            elapsed = time.time() - t0
            print(f"    Measurement {m+1}/{config.n_meas} ({elapsed:.0f}s)")

    elapsed = time.time() - t0
    if verbose:
        print(f"  Done in {elapsed:.1f}s")

    # Process results
    plaq_4d_arr = np.array(plaq_4d_all)   # shape: (n_meas, N5)
    plaq_mixed_arr = np.array(plaq_mixed_all)

    results = {
        'gauge_group': gauge_group,
        'kL': kL,
        'plaq_4d_mean': np.mean(plaq_4d_arr, axis=0),
        'plaq_4d_err': np.std(plaq_4d_arr, axis=0) / np.sqrt(config.n_meas),
        'plaq_mixed_mean': np.mean(plaq_mixed_arr, axis=0),
        'plaq_mixed_err': np.std(plaq_mixed_arr, axis=0) / np.sqrt(config.n_meas),
        'polyakov_mean': np.mean(polyakov_all),
        'polyakov_err': np.std(polyakov_all) / np.sqrt(config.n_meas),
        'wilson_data': wilson_data,
        'topo_charge': topo_charge_all if gauge_group == 'SU2' else None,
        'elapsed': elapsed,
        'warp_factors': lattice.warp.copy(),
    }

    return results


def analyze_results(su2_results, u1_results, config):
    """Compare SU(2) and U(1) results and extract gauge-dependent corrections."""

    kL = su2_results['kL']
    N5 = config.N5

    print(f"\n{'#'*70}")
    print(f"#  ANALYSIS: kL = {kL:.1f}")
    print(f"{'#'*70}")

    # 1. Plaquette comparison by slice
    print(f"\n--- Average 4D Plaquette by y-slice ---")
    print(f"{'j':>3} {'warp':>10} {'SU(2)':>12} {'U(1)':>12} {'g2_SU2':>10} {'g2_U1':>10} {'ratio':>10}")

    g2_su2 = np.zeros(N5)
    g2_u1 = np.zeros(N5)
    g2_ratio = np.zeros(N5)

    for j in range(N5):
        wj = su2_results['warp_factors'][j]
        p_su2 = su2_results['plaq_4d_mean'][j]
        p_u1 = u1_results['plaq_4d_mean'][j]
        e_su2 = su2_results['plaq_4d_err'][j]
        e_u1 = u1_results['plaq_4d_err'][j]

        g2_su2[j] = extract_coupling_from_plaquette(p_su2, 'SU2')
        g2_u1[j] = extract_coupling_from_plaquette(p_u1, 'U1')

        if g2_u1[j] > 1e-10:
            g2_ratio[j] = g2_su2[j] / g2_u1[j]
        else:
            g2_ratio[j] = float('nan')

        print(f"{j:3d} {wj:10.4f} {p_su2:12.6f}+/-{e_su2:.4f} {p_u1:12.6f}+/-{e_u1:.4f} "
              f"{g2_su2[j]:10.6f} {g2_u1[j]:10.6f} {g2_ratio[j]:10.4f}")

    # 2. Mixed plaquette comparison
    print(f"\n--- Average Mixed (mu,5) Plaquette by y-slice ---")
    print(f"{'j':>3} {'SU(2)':>12} {'U(1)':>12}")
    for j in range(N5 - 1):
        p_su2 = su2_results['plaq_mixed_mean'][j]
        p_u1 = u1_results['plaq_mixed_mean'][j]
        print(f"{j:3d} {p_su2:12.6f} {p_u1:12.6f}")

    # 3. Polyakov loop
    print(f"\n--- Polyakov Loop (extra dim) ---")
    print(f"  SU(2): |P| = {su2_results['polyakov_mean']:.6f} +/- {su2_results['polyakov_err']:.6f}")
    print(f"  U(1):  |P| = {u1_results['polyakov_mean']:.6f} +/- {u1_results['polyakov_err']:.6f}")

    # 4. Wilson loops and Creutz ratios
    print(f"\n--- Wilson Loops at UV (j=0) and IR (j={N5-1}) ---")
    for j_slice in [0, N5 // 2, N5 - 1]:
        print(f"\n  y-slice j = {j_slice} (warp = {su2_results['warp_factors'][j_slice]:.4f}):")

        # Average Wilson loops over measurements
        W_su2_avg = {}
        W_u1_avg = {}
        for R in range(1, config.wilson_R_max + 1):
            for T in range(1, config.wilson_T_max + 1):
                key = (R, T, j_slice)
                vals_su2 = [wd[key] for wd in su2_results['wilson_data']]
                vals_u1 = [wd[key] for wd in u1_results['wilson_data']]
                W_su2_avg[(R, T)] = np.mean(vals_su2)
                W_u1_avg[(R, T)] = np.mean(vals_u1)

        print(f"  {'(R,T)':>8} {'W_SU2':>12} {'W_U1':>12} {'ratio':>10}")
        for R in range(1, config.wilson_R_max + 1):
            for T in range(1, config.wilson_T_max + 1):
                ws = W_su2_avg[(R, T)]
                wu = W_u1_avg[(R, T)]
                ratio = ws / wu if abs(wu) > 1e-15 else float('nan')
                print(f"  ({R},{T}):  {ws:12.6f} {wu:12.6f} {ratio:10.4f}")

        # Creutz ratios
        print(f"  Creutz ratios:")
        for I in range(2, config.wilson_R_max + 1):
            for J in range(2, config.wilson_T_max + 1):
                chi_su2 = creutz_ratio(W_su2_avg, I, J)
                chi_u1 = creutz_ratio(W_u1_avg, I, J)
                if chi_su2 is not None and chi_u1 is not None:
                    ratio = chi_su2 / chi_u1 if abs(chi_u1) > 1e-15 else float('nan')
                    print(f"    chi({I},{J}): SU(2) = {chi_su2:.6f}, U(1) = {chi_u1:.6f}, ratio = {ratio:.4f}")

    # 5. Topological charge (SU(2) only)
    if su2_results['topo_charge'] is not None:
        print(f"\n--- Topological Charge Q (SU(2) only) ---")
        topo = np.array(su2_results['topo_charge'])
        for idx, j_slice in enumerate([0, N5 // 2, N5 - 1]):
            Q_vals = topo[:, idx]
            print(f"  j={j_slice}: <Q> = {np.mean(Q_vals):.4f}, <Q^2> = {np.mean(Q_vals**2):.4f}, "
                  f"std(Q) = {np.std(Q_vals):.4f}")

    # 6. Key metric: ratio profile
    print(f"\n--- KEY METRIC: g^2_SU(2) / g^2_U(1) vs y ---")
    print(f"  (Deviations from 1.0 indicate non-perturbative gauge-dependent effects)")

    # Compute with errors via bootstrap
    uv_ratio = g2_ratio[0]
    ir_ratio = g2_ratio[-1]
    mid_ratio = g2_ratio[N5 // 2]

    print(f"  UV brane (j=0):    r = {uv_ratio:.6f}")
    print(f"  Midpoint (j={N5//2}):   r = {mid_ratio:.6f}")
    print(f"  IR brane (j={N5-1}):  r = {ir_ratio:.6f}")
    print(f"  IR/UV deviation:   Delta_r = {ir_ratio - uv_ratio:.6f}")

    return {
        'kL': kL,
        'g2_su2': g2_su2.copy(),
        'g2_u1': g2_u1.copy(),
        'g2_ratio': g2_ratio.copy(),
        'uv_ratio': uv_ratio,
        'ir_ratio': ir_ratio,
        'delta_r': ir_ratio - uv_ratio,
        'polyakov_su2': su2_results['polyakov_mean'],
        'polyakov_u1': u1_results['polyakov_mean'],
    }


def main():
    """Run the full warped lattice simulation."""
    print("=" * 70)
    print("  WARPED LATTICE GAUGE THEORY — Non-perturbative test")
    print("  Project Meridian Phase 21 | Door 2B | Computation C")
    print("=" * 70)

    np.random.seed(Config.seed)

    # Check if we should use a smaller lattice for speed
    if '--fast' in sys.argv:
        print("\n  [FAST MODE: reduced lattice for testing]")
        Config.L = 4
        Config.Lt = 4
        Config.N5 = 8
        Config.n_therm = 100
        Config.n_meas = 50
        Config.n_skip = 3
        Config.wilson_R_max = 2
        Config.wilson_T_max = 2

    # Print configuration
    print(f"\n  Lattice: {Config.L}^3 x {Config.Lt} x {Config.N5}")
    print(f"  beta0(SU2) = {Config.beta0_su2}, beta0(U1) = {Config.beta0_u1}")
    print(f"  Thermalization: {Config.n_therm} sweeps")
    print(f"  Measurements: {Config.n_meas} x (every {Config.n_skip} sweeps)")
    print(f"  kL values: {Config.kL_values}")

    all_analyses = []

    for kL in Config.kL_values:
        print(f"\n\n{'*'*70}")
        print(f"  kL = {kL:.1f}  (warp factor = {np.exp(kL):.1f})")
        print(f"{'*'*70}")

        # Run SU(2)
        su2_results = run_simulation(Config, kL, 'SU2', verbose=True)

        # Run U(1)
        u1_results = run_simulation(Config, kL, 'U1', verbose=True)

        # Analyze
        analysis = analyze_results(su2_results, u1_results, Config)
        all_analyses.append(analysis)

    # Final summary
    print(f"\n\n{'='*70}")
    print(f"  FINAL SUMMARY — Gauge Universality Test")
    print(f"{'='*70}")

    print(f"\n{'kL':>6} {'warp':>8} {'r(UV)':>10} {'r(IR)':>10} {'Delta_r':>10} {'P_SU2':>10} {'P_U1':>10}")
    print("-" * 70)

    for a in all_analyses:
        warp = np.exp(a['kL'])
        print(f"{a['kL']:6.1f} {warp:8.1f} {a['uv_ratio']:10.4f} {a['ir_ratio']:10.4f} "
              f"{a['delta_r']:10.6f} {a['polyakov_su2']:10.4f} {a['polyakov_u1']:10.4f}")

    # Assess scaling
    print(f"\n  Scaling assessment:")
    if len(all_analyses) >= 2:
        delta_rs = [a['delta_r'] for a in all_analyses]
        kLs = [a['kL'] for a in all_analyses]

        # Check if delta_r grows with kL
        growing = all(delta_rs[i+1] > delta_rs[i] for i in range(len(delta_rs)-1))
        if growing:
            print(f"  Delta_r GROWS with kL: suggests non-perturbative correction amplified by warping")
        else:
            print(f"  Delta_r does NOT consistently grow with kL")

        # Fit power law delta_r ~ A * kL^p
        if all(abs(d) > 1e-12 for d in delta_rs):
            log_kL = np.log(kLs)
            log_dr = np.log(np.abs(delta_rs))
            if len(log_kL) >= 2:
                p, A = np.polyfit(log_kL, log_dr, 1)
                print(f"  Power law fit: |Delta_r| ~ kL^{p:.2f}")
                print(f"  Extrapolation to kL=35: |Delta_r| ~ {np.exp(A) * 35**p:.4f}")

    # Detailed coupling profile
    print(f"\n--- Coupling ratio g^2_SU(2)/g^2_U(1) profile for each kL ---")
    for a in all_analyses:
        print(f"\n  kL = {a['kL']:.1f}:")
        N5 = len(a['g2_ratio'])
        for j in range(N5):
            wj = np.exp(-a['kL'] * j / N5)
            bar_len = int(50 * abs(a['g2_ratio'][j] - 1.0) / max(1e-6, max(abs(r-1) for r in a['g2_ratio'])))
            bar = '#' * bar_len
            print(f"    j={j:2d} (w={wj:.4f}): r = {a['g2_ratio'][j]:.6f} {bar}")

    total_time = sum(a.get('elapsed', 0) for a_res in [] for a in all_analyses)
    print(f"\n  Total elapsed time: see individual runs above")
    print(f"\n  Script complete.")

    return all_analyses


if __name__ == '__main__':
    results = main()
