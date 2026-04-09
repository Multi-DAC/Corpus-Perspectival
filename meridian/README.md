# Project Meridian — Computational Scripts

Five-dimensional warped-geometry framework (Randall-Sundrum orbifold x noncommutative geometry) unifying gravity and the Standard Model. 244 scripts across 26 research phases.

## Key Predictions

| Quantity | Value | Script |
|---|---|---|
| w_0 (dark energy EoS) | -0.830 | `cosmology/meridian_cosmology.py` |
| w_a (time variation) | 0 (exactly) | Derived from cuscuton constraint |
| C_GB (Gauss-Bonnet coupling) | 2/3 (derived) | `gauss-bonnet/c1_symbolic_gb_kk.py` |
| epsilon_GW | 0.275 [0.169, 0.347] 1sigma | `cosmology/` |
| Threshold | ln(3)/sqrt(2) = 0.7768 | `torsion/track_c_dkl.sage` |

## Directory Guide

### `cosmology/` — Modified Friedmann Equation & Observational Tests
Core cosmological solver with cuscuton-modified Friedmann equation. Includes MCMC parameter estimation, BAO/CMB/SNe distance fitting, growth factor integration, and DESI DR2 confrontation.

### `spectral-action/` — NCG Spectral Triple & Gauge Structure
Seeley-DeWitt expansion of the spectral action on the almost-commutative geometry M x F. Computation of a_4 coefficients, gauge coupling unification, Higgs mass prediction, Pati-Salam extension, and NCG-asymptotic safety bridge.

### `torsion/` — Analytic Torsion & Topological Invariants
The largest subdirectory (86 scripts). Analytic torsion on del Pezzo surfaces, Z3 orbifold spectral geometry, DKL (Kullback-Leibler) analysis of spectral proximity, threshold ratio computation. Includes SageMath and Wolfram/Mathematica scripts.

### `self-tuning/` — Cosmological Constant Self-Tuning
Demonstration that the 5D orbifold boundary conditions naturally tune Lambda_4 to zero (to 16 significant figures). Basin of attraction analysis, Chebyshev polynomial expansion, vacuum energy no-go theorems.

### `fermion-sector/` — Three Generations & Mass Hierarchy
Derivation of three fermion generations from the octonionic algebra J_3(O). CKM and PMNS mixing matrices, fermion mass hierarchy from warp factor localization, sterile neutrino dark matter, proton decay bounds.

### `observables/` — Experimental Predictions
Collider phenomenology (KK graviton and radion signatures at LHC), LISA gravitational wave forecasts, LiteBIRD CMB polarization predictions, DESI DR2 Fisher matrix forecasts.

### `gauss-bonnet/` — C_GB = 2/3 Derivation
The central result: the Gauss-Bonnet coupling is derived (not fitted) from the spectral action on the RS orbifold. Symbolic Kaluza-Klein reduction, junction condition computation, and cross-validation.

### `validation/` — Cross-Checks
Monograph validation scripts ensuring internal consistency across all computational claims.

### `thermal-history/` — Early Universe
Baryogenesis via leptogenesis in the KK sector, reheating temperature computation.

### `tools/` — Utilities
Prediction dashboard, Wolfram Engine library for symbolic computations.

## Requirements

- Python 3.10+ with NumPy, SciPy, SymPy, Matplotlib
- SageMath 10+ (for `torsion/*.sage` files)
- Wolfram Engine 14+ (for `*.wl` files, optional)
- CAMB (for CMB cross-validation, optional)

## Research Phases

These scripts span Phases 2-26 of the Meridian research program (February-April 2026). The original phase numbering is preserved in file naming conventions where applicable.
