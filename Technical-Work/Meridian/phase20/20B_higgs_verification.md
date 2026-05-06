# 20B: Verification of "NCG Predicts m_H = 124.5 GeV"

**Status: FALSIFIED** (as a parameter-free prediction from the NCG spectral action)
**Date:** 2026-03-22
**Computation:** 5-step numerical verification with 1-loop and approximate 2-loop SM RGEs

---

## The Claim

> "The NCG spectral action predicts m_H = 124.5 GeV when using running Yukawa couplings at the cutoff Lambda = M_Pl."

If true, this would be a parameter-free prediction of the Higgs mass within 0.6% accuracy. This requires rigorous verification.

---

## Method

1. Solve 1-loop SM RGEs for (g_1, g_2, g_3, y_t, lambda) from M_t to M_Pl
2. Identify the CCM unification scale where sin^2(theta_W) = 3/8
3. Compute the CCM spectral action boundary condition for lambda
4. Run lambda from the boundary condition DOWN to M_t and extract m_H
5. Compare with near-criticality and asymptotic safety boundary conditions
6. Repeat with approximate 2-loop beta functions

Inputs (Buttazzo et al. 2013 central values):
- m_t(pole) = 172.76 GeV, y_t(M_t) = 0.9369
- lambda(M_t) = 0.12604 (corresponds to m_H = 125.25 GeV)
- alpha_s(M_Z) = 0.1179, M_Z = 91.1876 GeV
- Gauge couplings in GUT normalization: g_1(M_Z) = 0.4614, g_2(M_Z) = 0.6517, g_3(M_Z) = 1.2172

---

## Key Results

### 1. SM Running from Observed Values

| Scale | g_1 | g_2 | g_3 | y_t | lambda | sin^2(theta_W) |
|-------|-----|-----|-----|-----|--------|-----------------|
| M_t = 172.76 GeV | 0.4631 | 0.6482 | 1.1691 | 0.9369 | 0.12604 | 0.231 |
| 10^6 GeV | 0.487 | 0.606 | 0.817 | 0.685 | 0.025 | 0.280 |
| 10^9 GeV | 0.509 | 0.577 | 0.688 | 0.583 | -0.008 | 0.319 |
| 10^13 GeV | 0.544 | 0.544 | 0.584 | 0.493 | -0.028 | 0.375 |
| M_Pl = 2.4e18 GeV | 0.605 | 0.508 | 0.498 | 0.412 | -0.033 | 0.459 |

**lambda crosses zero** at mu ~ 1.1 x 10^8 GeV (vacuum instability scale).

**lambda(M_Pl) = -0.0327** (1-loop) or **-0.0171** (approximate 2-loop) — NEGATIVE at the Planck scale.

### 2. The NCG Unification Scale

sin^2(theta_W) = 3/8 occurs at **Lambda_NCG ~ 1.03 x 10^13 GeV** (1-loop SM).

At this scale:
- g_1 = g_2 = 0.544 (electroweak unification)
- **g_3 = 0.584 (NOT equal to g_1, g_2 — full gauge unification does NOT occur!)**
- y_t = 0.494
- lambda_SM = -0.028 (already negative at this scale)

The SM gauge couplings do not unify at 1-loop. The NCG relation g_1 = g_2 = g_3 is not satisfied in the pure SM. This is a known issue — NCG requires either threshold corrections from new particles, or a modified desert assumption.

### 3. CCM Spectral Action Boundary Condition

The spectral action gives lambda(Lambda) = g^2(Lambda) * b/(4*a^2), where:
- a = Tr(Y^dag Y) and b = Tr((Y^dag Y)^2) are Yukawa traces
- With top-quark dominance: b/a^2 = R = 1/3
- With top + Dirac neutrino (y_nu = y_t): R = 1/4

| Boundary Condition | lambda(Lambda_NCG) | m_H (1-loop RG) |
|---|---|---|
| CCM, R = 1/3 (top only) | 0.0247 | **137.4 GeV** |
| CCM, R = 1/4 (top + nu) | 0.0185 | **136.1 GeV** |
| CCM, lambda = g^2*R/2, R = 1/3 | 0.0494 | **142.2 GeV** |
| CCM, lambda = g^2*R/2, R = 1/4 | 0.0370 | **139.9 GeV** |

**All CCM boundary conditions give m_H = 136-142 GeV.** None give 124.5 GeV.

### 4. Alternative Boundary Conditions at M_Pl

| Boundary Condition | lambda(M_Pl) | m_H (1-loop) | m_H (approx 2-loop) | Source |
|---|---|---|---|---|
| lambda = 0 | 0.000 | **133.8** | **~129** | Near-criticality |
| beta(lambda) = 0, negative root | -0.0243 | **126.7** | **~121** | Asymptotic safety |
| beta(lambda) = 0, 2L couplings | -0.00153 | — | **~129** | Asymptotic safety |
| lambda = -0.01 | -0.010 | **131.2** | **126.2** | Ad hoc |
| Needed for m_H = 124.5 | -0.0304 (1L) | **124.5** | — | Reverse-engineered |
| Needed for m_H = 124.5 | -0.0147 (2L) | — | **124.5** | Reverse-engineered |
| Needed for m_H = 125.25 | -0.0126 (2L) | — | **125.25** | Reverse-engineered |

### 5. Sensitivity to Top Mass

For the lambda(M_Pl) = 0 boundary condition (1-loop):

| m_t (GeV) | m_H prediction |
|---|---|
| 170.0 | 132.0 GeV |
| 171.0 | 133.9 GeV |
| 172.0 | 135.9 GeV |
| **172.76** | **137.4 GeV** |
| 174.0 | 139.8 GeV |

Sensitivity: dm_H/dm_t ~ 1.9 GeV/GeV (from this boundary condition, 1-loop).

### 6. The Shaposhnikov-Wetterich Connection

The Shaposhnikov-Wetterich (2009) asymptotic safety condition:
- **lambda(M_Pl) = 0 AND beta(lambda)(M_Pl) = 0**
- Requires y_t(M_Pl) = 0.3889 (from gauge couplings at M_Pl)
- Actual y_t(M_Pl) = 0.3903 (2-loop running) — **0.3% discrepancy!**
- This near-coincidence is the deepest version of the "near-criticality" mystery.

Their published prediction (NNLO, m_t = 171.3 GeV): **m_H = 126 +/- 3 GeV** — made in 2009, three years before the Higgs discovery.

---

## The Literature Record

### Chamseddine-Connes-Marcolli (2007)
Original NCG spectral action for the SM. Tree-level prediction: **m_H ~ 170 GeV**. Uses the boundary condition at the unification scale with y_nu = y_t (Dirac condition).

### Chamseddine-Connes (2012) "Resilience of the Spectral Standard Model"
Acknowledge that the original prediction gives m_H ~ 170 GeV, RULED OUT by the discovery of m_H = 125 GeV. Their solution: **add a real scalar singlet sigma** to the spectral triple (identified with the Majorana mass of right-handed neutrinos). This allows m_H = 125 GeV but introduces new parameters. The framework "survives" by MODIFYING the spectral triple.

### Devastato, Lizzi, Martinetti (2014) "Unification of Couplings, Yukawas and Higgs Self-Coupling"
Include seesaw threshold corrections from heavy Majorana neutrinos at M_R ~ 10^{11-14} GeV. CAN reproduce m_H ~ 126 GeV for specific choices of (y_nu, M_R). **NOT parameter-free**: requires fitting the neutrino sector.

### Shaposhnikov-Wetterich (2009)
Not NCG, but gravitational asymptotic safety. Predicted m_H = 126 +/- 3 GeV before the Higgs discovery. The closest genuine prediction to the observed value.

---

## Verdict

### FALSIFIED: "NCG spectral action predicts m_H = 124.5 GeV"

The claim is false as a parameter-free prediction from the unmodified NCG spectral action. Specifically:

1. **The original CCM spectral action predicts m_H ~ 170 GeV** (tree-level) or **~136-142 GeV** (with 1-loop RG running from Lambda_NCG). Both are ruled out.

2. **124.5 GeV requires lambda(M_Pl) ~ -0.015 to -0.030** (depending on loop order), which is not a natural output of the spectral action boundary condition. It is close to the SM value, making it essentially "the SM predicts the SM."

3. **No clean theoretical boundary condition** (lambda = 0, beta(lambda) = 0, or any CCM formula) gives exactly 124.5 GeV.

4. **The closest genuine prediction** is the Shaposhnikov-Wetterich asymptotic safety result (m_H = 126 +/- 3 GeV), which is a different framework from NCG.

5. **Modified NCG** (Devastato et al.) CAN accommodate 125 GeV, but only by introducing free parameters in the neutrino sector (y_nu, M_R).

### What IS true

- The NCG spectral triple constrains the Higgs sector by relating lambda to gauge and Yukawa couplings at the cutoff.
- The near-criticality of lambda(M_Pl) (close to zero, with near-vanishing beta function) is a genuine empirical mystery.
- The Shaposhnikov-Wetterich condition y_t(M_Pl) ~ y_t^{SW} is satisfied to 0.3% at 2-loop — a remarkable near-coincidence.
- NCG's structural prediction that the Higgs EXISTS as the unique scalar in the spectral triple IS confirmed.

### The honest status of the NCG Higgs mass prediction

The original prediction (170 GeV) was wrong. The framework was saved by adding a scalar singlet (Chamseddine-Connes 2012) or adjusting neutrino parameters (Devastato et al. 2014). The claim of "124.5 GeV from running Yukawas" appears to be either a misattribution of the Shaposhnikov-Wetterich result, or a post-hoc reverse-engineering of the boundary condition. The number 124.5 does not emerge naturally from any version of the NCG spectral action.

---

## Computation Files

- `higgs_rg_step1.py` — SM RG running from M_Z to M_Pl (1-loop)
- `higgs_rg_step2.py` — CCM boundary condition sweep and formula analysis
- `higgs_rg_step3.py` — Precision inverse problem (what BC gives 125.25 GeV?)
- `higgs_rg_step4.py` — 2-loop corrections and Shaposhnikov-Wetterich analysis
- `higgs_rg_step5.py` — Final summary, m_t sensitivity, and literature comparison

All computations use scipy.integrate.solve_ivp with RK45, rtol=1e-12, atol=1e-14.
