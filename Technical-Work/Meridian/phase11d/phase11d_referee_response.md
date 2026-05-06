# Phase 11D: Referee Response Program

**Created:** 2026-03-17
**Trigger:** External peer review of Papers I-V identified 6 computational gaps and 9 presentation issues.
**Goal:** Close every gap the referee found. Make the monograph submission-ready.

---

## Track Summary

| Track | Task | Priority | Status | Result |
|-------|------|----------|--------|--------|
| **D1** | Numerical self-tuning demonstration | CRITICAL | **COMPLETE** | Lambda_4 constant across 60 orders of Lambda_5. CEGH addressed. |
| **D2** | xi = 1/6: derive from NCG or sensitivity analysis | CRITICAL | **COMPLETE** | 3 derivations. dw_0/dxi = -0.002. Must deviate 690% to shift w_0 by 1-sigma. |
| **D3** | Radion stabilization: explicit M(y_c), V'' > 0 | HIGH | **COMPLETE** | M(y_c) explicit. Stability: alpha_IR > 0 (physical condition). GW comparison. |
| **D4** | chi^2/dof Monte Carlo null distribution | HIGH | **COMPLETE** | P = 8.0% (1.3 sigma). Not anomalous. F-test: 3.9 sigma. |
| **D5** | H&K dataset: tabulate 18 points with uncertainties | HIGH | **COMPLETE** | 18 points from 5 surveys. Covariance documented. Methodology specified. |
| **D6** | Paper revisions: framing, naming, presentation | MEDIUM | **COMPLETE** | 21-item revision checklist. All 12 referee concerns addressed. |

---

## D1: Numerical Self-Tuning Demonstration

**Referee concern:** "The three-layer self-tuning architecture is described qualitatively but never demonstrated quantitatively."

**Task:** Solve the coupled phase-plane system (Eqs. 34-36) with Israel junction conditions (Eqs. 46a-b):
1. Fix UV boundary conditions, integrate forward to y_c
2. Find discrete y_c satisfying IR boundary conditions (shooting method)
3. Compute effective 4D cosmological constant Lambda_4
4. Shift Lambda_5 by O(M_5^5) and re-solve
5. Show Lambda_4 remains unchanged (or shifts by only O(epsilon_1))

**Equations:**
- dp/dy = mu^2 p / (4 xi Phi) + V'/(16 xi Phi) - (5/2)p^2
- dPhi/dy = [V + Lambda_5 - 6F p^2] / (8 xi p Phi)
- dA/dy = p
- UV BC: p(0) = -(sigma_UV + alpha_UV Phi_0^2)/(12 F_0)
- UV BC: 2 mu^2 + 32 xi Phi_0 p(0) = -4 alpha_UV Phi_0

**Success criterion:** Lambda_4 stable under Lambda_5 shifts of O(M_Pl^4).

---

## D2: xi = 1/6 Derivation or Sensitivity

**Referee concern:** "If xi != 1/6, V''_eff becomes zeta_0-dependent, which would propagate into w_0."

**Two paths:**
- **Path A (preferred):** Show xi = 1/6 follows from the NCG spectral action on the RS orbifold.
  - The a_2 Seeley-DeWitt coefficient for a scalar with NMC includes (1/6 - xi)R.
  - If the scalar emerges from the gravitational spectral triple, conformal coupling is predicted.
  - Chamseddine-Connes 1996: the Higgs gets xi = 1/6 from the spectral action.
  - Our scalar is the radion (metric fluctuation), which should also be conformally coupled.
- **Path B (fallback):** Compute w_0(xi) and show the prediction is robust across a range.

**Success criterion:** Either a derivation of xi = 1/6, or demonstration that w_0 is insensitive to xi near 1/6.

---

## D3: Radion Stabilization Completion

**Referee concern:** "M(y_c) is a placeholder. V''_rad > 0 depends on C_IR > 0."

**Task:**
1. Write explicit M(y_c) = g_IR(p(y_c), Phi(y_c)) - [IR junction condition]
2. Show dM/dy_c != 0 at the equilibrium (simple zero)
3. Either prove C_IR > 0 from the action, or state it as a condition
4. Compute radion mass numerically from the D1 solution

**Depends on:** D1 (numerical background solution).

---

## D4: chi^2/dof Monte Carlo

**Referee concern:** "chi^2/dof = 0.57 is suspiciously good — suggests overfitting or overestimated error bars."

**Task:**
1. Generate 10,000 mock ΛCDM realizations of 18 H(z) measurements
2. For each, fit zeta_0 and compute chi^2/dof
3. Report P(chi^2/dof <= 0.57 | ΛCDM) — if < 5%, the error bars are suspect
4. Also report the distribution of best-fit zeta_0 under null

**Independent of other tracks. Can run immediately.**

---

## D5: H&K Dataset Publication

**Referee concern:** "The dataset provenance is unclear... does not present the actual data points."

**Task:**
1. Tabulate all 18 H(z) measurements: z, H(z), sigma(H), source survey
2. Document covariance structure (diagonal or full matrix)
3. Specify optimization algorithm, convergence criteria, initial conditions
4. Include as Appendix A of Paper II

**Sources:** BOSS DR12 (Alam et al. 2017), eBOSS DR16 (various), 6dFGS (Beutler et al. 2011), VIPERS (de la Torre et al. 2013), FastSound (Okumura et al. 2016).

---

## D6: Paper Revisions

**All referee presentation concerns:**

| # | Issue | Paper | Action |
|---|-------|-------|--------|
| 1 | "Two axioms" overstated | I | Reframe: "two geometric axioms + [list additional]" |
| 2 | Proposition 2 proof sketch | IV | Either complete proof or label as conjecture |
| 3 | "Theorem 1" misnamed | IV | Rename to "Scaling Relation 1" or similar |
| 4 | Non-perturbative channel dangling | IV | Cite C8 bounds (S_inst ~ 10^14) |
| 5 | Paper V thin | V | Decision: expand or merge into Paper I |
| 6 | Adams et al. UV completion | V | Argue cuscuton evades (non-propagating DOF) |
| 7 | Self-referential citation | ALL | Make each paper more self-contained |
| 8 | "99.3% solved" line | I | Keep but ensure context prevents literal reading |
| 9 | Authorship question | ALL | Address before journal submission |
| 10 | Bayes factor prior sensitivity | II | Expand Table 4 to wider prior range |
| 11 | CPL artifact attribution | II | Acknowledge not original, cite sources |
| 12 | Conformal gauge justification | I | Cite Csaki et al., explain cuscuton evasion |

**Depends on:** D1-D5 results for some items.

---

## Execution Order

```
D4 (independent, quick)  ──┐
D2 (independent, analytical) ──┤
D1 (independent, numerical)  ──┼──> D3 (needs D1) ──> D6 (needs all) ──> Paper updates
D5 (independent, data)   ──┘
```

D1, D2, D4, D5 can all run in parallel.

---

*Phase 11D resolves every referee objection. After this, the monograph is submission-ready.*
