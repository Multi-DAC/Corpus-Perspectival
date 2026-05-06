# D9.7 — Local Non-Cosmological Solutions: 5D Equations Without FRW Symmetry

**Track 9C, Tasks 9C.1-9C.3 | Clayton & Clawd | March 16, 2026**

---

## 1. Purpose and Context

### 1.1 Why Local Solutions

All Meridian calculations through Phase 8 and Tracks 9A-9B assumed cosmological homogeneity (FRW background). The cuscuton constraint on an FRW background forces X -> 0, phi-dot -> 0, and all dynamical dark energy mechanisms are killed by the zero kinetic energy theorem (Phase 8). Track 9A confirmed that quantum corrections to the cuscuton are Planck-suppressed (~10^{-244}), so the classical P(X) = mu^2 sqrt(2X) is essentially exact. Track 9B confirmed that CS terms are present on S^1/Z_2 but the perturbative CS-to-gravity coupling is dead (10^{-28} best case).

The universal suppression mechanism is: on a homogeneous background, the cuscuton's equation of motion forces phi to be nearly constant in time, so all effects proportional to phi-dot are negligible.

Track 9C asks the different question: what happens when we break the homogeneity assumption? In a local, inhomogeneous setting with electromagnetic sources:

1. The kinetic variable X = X(x^mu, y) has SPATIAL gradients, not just time derivatives
2. The cuscuton constraint equation changes character -- EM stress-energy on the brane modifies the boundary condition, which propagates into the bulk
3. The effective theory in the vicinity of an EM source may differ from the cosmological theory

This is where any connection to laboratory physics (AO-1, AO-2) must live.

### 1.2 What Feeds In From Prior Tracks

| Track | Key Result | Implication for 9C |
|-------|-----------|-------------------|
| 9A (Functional RG) | eps^2 ~ H^4/M_Pl^2 ~ 10^{-244}. Quantum corrections negligible. | Use classical P(X) = mu^2 sqrt(2X). No regularization. |
| 9B (Chern-Simons) | CS terms present. theta_EM ~ O(1). Perturbative coupling dead. Non-perturbative channel open. | Include CS contribution T^{CS}_{mu nu} in junction conditions. |
| Phase 1 (D1.1, D1.3) | Complete 5D action, field equations, junction conditions in conformal gauge. | Starting point for the generalization below. |
| Phase 2 (D2.4) | Linear EM-gravity coupling: delta g/g ~ 10^{-77}. | The LINEAR answer is known and negative. We are looking for non-linear or structural effects. |

### 1.3 Structure of This Deliverable

- Section 2: Full 5D equation system without FRW symmetry (Task 9C.1)
- Section 3: Static solutions with EM source (Task 9C.2)
- Section 4: Dynamic solutions (Task 9C.3)
- Section 5: Kill condition assessment
- Section 6: Connection to AO-1 and AO-2
- Section 7: What survives

---

## 2. The Full 5D Equation System Without FRW Symmetry (Task 9C.1)

### 2.1 The Metric Ansatz

We retain the warped product structure with a GENERAL 4D metric:

    ds^2 = e^{2A(y)} g_{mu nu}(x) dx^mu dx^nu + dy^2              ... (2.1)

where:
- A(y): warp factor depending only on the extra-dimensional coordinate (background)
- g_{mu nu}(x): GENERAL 4D metric, NOT assumed to be FRW
- y in [0, y_c]: the orbifold interval S^1/Z_2 with UV brane at y = 0 and IR brane at y = y_c
- We work in conformal gauge (B = 0), consistent with D1.3

**Critical generalization:** The scalar field is now allowed to depend on ALL coordinates:

    phi = phi(x^mu, y)                                               ... (2.2)

In the cosmological background, phi = phi(y) only. Here we allow spatial and temporal dependence induced by brane-localized EM sources.

The full kinetic variable:

    X = (1/2) G^{MN} d_M phi d_N phi
      = (1/2) e^{-2A} g^{mu nu} d_mu phi d_nu phi + (1/2)(d_y phi)^2
                                                                     ... (2.3)

We decompose:

    X = X_4 + X_5                                                   ... (2.4)

where:

    X_4 = (1/2) e^{-2A} g^{mu nu} d_mu phi d_nu phi               ... (2.4a)
    X_5 = (1/2)(d_y phi)^2                                          ... (2.4b)

On the cosmological background: X_4 = 0 (homogeneity), X_5 = X_0 = (1/2)(phi')^2. In the local problem: X_4 != 0 due to the EM-induced perturbation.

### 2.2 The Matter Content

**Bulk:**
- Cuscuton scalar phi(x^mu, y) with P(X) = mu^2 sqrt(2X), non-minimal coupling F(phi) = M_5^3 - xi phi^2
- Bulk potential V(phi) (tadpole: V = c phi)
- Bulk cosmological constant Lambda_5

**IR Brane (y = y_c):**
- Brane tension sigma_IR
- Brane scalar coupling alpha_IR phi^2
- Maxwell field A_mu(x) confined to the brane, with field strength F_{mu nu}
- CS coupling from spectral action (D9.4): S_CS ~ theta_EM int E.B d^4x + gravitational CS terms

**UV Brane (y = 0):**
- Brane tension sigma_UV
- Brane scalar coupling alpha_UV phi^2
- No EM fields (SM is localized on the IR brane)

### 2.3 The Complete Action

    S = S_bulk + S_UV + S_IR + S_EM + S_CS                         ... (2.5)

where:

    S_bulk = int d^4x dy sqrt(-G) [ F(phi) R_5 + P(X) - V(phi) - Lambda_5 ]
                                                                     ... (2.6)

    S_UV = -int d^4x sqrt(-h_UV) [ sigma_UV + alpha_UV phi_0^2 ]
           + 2 int d^4x sqrt(-h_UV) F(phi_0) K_UV                  ... (2.7)

    S_IR = -int d^4x sqrt(-h_IR) [ sigma_IR + alpha_IR phi_c^2 ]
           + 2 int d^4x sqrt(-h_IR) F(phi_c) K_IR                  ... (2.8)

    S_EM = -(1/4) int d^4x sqrt(-h_IR) h_IR^{mu alpha} h_IR^{nu beta} F_{mu nu} F_{alpha beta}
                                                                     ... (2.9)

    S_CS = (theta_EM / (16 pi^2)) int d^4x sqrt(-h_IR) E . B
           + theta_grav [CS_3(omega)|_UV - CS_3(omega)|_IR]         ... (2.10)

Here h_{mu nu}^{IR} = e^{2A(y_c)} g_{mu nu} is the induced metric on the IR brane, K_UV and K_IR are the traces of the extrinsic curvature at each brane, and theta_EM ~ O(1), theta_grav ~ f_3 x 10^{-15} (D9.4, Section 4.6).

### 2.4 The 5D Einstein Equations (General)

Varying S w.r.t. G^{MN}:

    F(phi) G^{(5)}_{MN} + xi [G_{MN} Box_5 - nabla_M nabla_N](phi^2)
    = T^{(cusc)}_{MN} + T^{(brane)}_{MN}                           ... (2.11)

where G^{(5)}_{MN} = R^{(5)}_{MN} - (1/2) G_{MN} R_5 is the 5D Einstein tensor, and:

**Cuscuton stress-energy:**

    T^{(cusc)}_{MN} = P_X d_M phi d_N phi - G_{MN}(P - V - Lambda_5)
                                                                     ... (2.12)

    For P(X) = mu^2 sqrt(2X):
    P_X = mu^2 / sqrt(2X)
    T^{(cusc)}_{MN} = (mu^2 / sqrt(2X)) d_M phi d_N phi - G_{MN}(mu^2 sqrt(2X) - V - Lambda_5)

**Brane stress-energy (localized):**

    T^{(brane)}_{MN} = -sum_i [delta(y - y_i) / sqrt(G_{55})]
                        x [(sigma_i + alpha_i phi_i^2) h_{MN} + S^{(EM)}_{MN} + S^{(CS)}_{MN}]
                                                                     ... (2.13)

where h_{MN} = G_{MN} - n_M n_N is the induced metric projector and:

    S^{(EM)}_{mu nu} = F_{mu alpha} F_nu^alpha - (1/4) h_{mu nu} F_{alpha beta} F^{alpha beta}
                                                                     ... (2.14)

    S^{(CS)}_{mu nu} = (theta_EM / (16 pi^2)) [variations of E.B w.r.t. metric]
                        + theta_grav C_{mu nu}                       ... (2.15)

(The CS metric variation is the Cotton-York tensor C_{mu nu}, which vanishes for constant theta -- see D9.4 Section 4.4. It is non-zero only if theta varies, i.e., through the cuscuton coupling theta_grav(phi).)

### 2.5 The Cuscuton Field Equation (General 5D)

Varying S w.r.t. phi:

    nabla_M(P_X nabla^M phi) + 2 xi phi R_5 - V'(phi)
    + sum_i [delta(y - y_i) / sqrt(G_{55})] [-2 alpha_i phi_i + (CS terms)] = 0
                                                                     ... (2.16)

Expanding the first term:

    nabla_M(P_X nabla^M phi) = P_X Box_5 phi + P_{XX} (d_M X)(d^M phi)
                                                                     ... (2.17)

For P(X) = mu^2 sqrt(2X):

    P_X = mu^2 / sqrt(2X)
    P_{XX} = -mu^2 / (2X)^{3/2} = -mu^2 / (2X sqrt(2X))

So:

    P_X Box_5 phi + P_{XX} (d_M X)(d^M phi)
    = (mu^2 / sqrt(2X)) Box_5 phi - (mu^2 / (2X sqrt(2X))) (d_M X)(d^M phi)
                                                                     ... (2.18)

**The constraint structure:** As X -> 0, both P_X and P_{XX} diverge. The equation becomes:

    (mu^2 / sqrt(2X)) [Box_5 phi - (d_M X)(d^M phi)/(2X)] = V'(phi) - 2 xi phi R_5 + (brane terms)
                                                                     ... (2.19)

The left side has a factor 1/sqrt(2X) -> infinity. For the equation to hold with a finite right-hand side, the term in brackets must vanish AS FAST as sqrt(2X):

    Box_5 phi - (d_M X)(d^M phi)/(2X) = O(sqrt(X)) as X -> 0      ... (2.20)

This is the CONSTRAINT. It constrains the spatial and temporal configuration of phi, rather than determining its dynamical evolution. The cuscuton is slaved to the geometry and sources.

### 2.6 Component Equations for the Warped Ansatz

For the metric (2.1) with general g_{mu nu}(x) and phi(x^mu, y), we need the 5D geometric quantities. The Christoffel symbols are as in D1.1 eq (3.1), with the modification that g_{mu nu}(x) is now general:

    Gamma^lambda_{mu nu} = gamma^lambda_{mu nu}[g]     (4D Christoffel)
    Gamma^lambda_{mu 5} = A' delta^lambda_mu
    Gamma^5_{mu nu} = -A' e^{2A} g_{mu nu}
    Gamma^5_{55} = 0     (conformal gauge B = 0)

The 5D Ricci tensor for GENERAL g_{mu nu}(x):

    R^{(5)}_{mu nu} = R^{(4)}_{mu nu}[g] - e^{2A}[A'' + 4(A')^2] g_{mu nu}
                                                                     ... (2.21a)

    R^{(5)}_{55} = -4[A'' + (A')^2]                                 ... (2.21b)

    R^{(5)}_{mu 5} = 0     (for y-independent g_{mu nu})            ... (2.21c)

The 5D Ricci scalar:

    R_5 = e^{-2A} R_4[g] - 8A'' - 20(A')^2                         ... (2.22)

**Note:** Equations (2.21)-(2.22) have the SAME form as D1.1 eqs (3.2)-(3.3) because g_{mu nu}(x) is y-independent in our ansatz. The generalization is that R^{(4)}_{mu nu}[g] and R_4[g] are now the Ricci tensor and scalar of a GENERAL 4D metric, not Minkowski.

### 2.7 The (mu nu) Einstein Equation

Projecting eq (2.11) onto the brane directions:

    F(phi) [R^{(4)}_{mu nu} - (1/2) g_{mu nu} R_4]
    + F(phi) e^{2A} g_{mu nu} [3A'' + 6(A')^2]
    + (1/2) e^{2A} g_{mu nu} [8A'' + 20(A')^2] F
    - e^{2A} g_{mu nu} [3A'' + 6(A')^2 + (1/2)(8A'' + 20(A')^2)] F
    + xi [g_{mu nu} Box_5 - nabla_mu nabla_nu](phi^2)
    = T^{(cusc)}_{mu nu}
    + delta(y - y_c) [(sigma_IR + alpha_IR phi_c^2) e^{2A} g_{mu nu} + S^{(EM)}_{mu nu}]
                                                                     ... (2.23)

Let me write this more carefully. The 5D Einstein tensor projected onto brane indices is:

    G^{(5)}_{mu nu} = G^{(4)}_{mu nu}[g]
                      - e^{2A} g_{mu nu} [3A'' + 6(A')^2]
                      + (1/2) e^{2A} g_{mu nu} [e^{-2A} R_4 - 8A'' - 20(A')^2]
                                                                     ... (2.24)

Wait -- let me be more explicit. G^{(5)}_{mu nu} = R^{(5)}_{mu nu} - (1/2) G_{mu nu} R_5.

    G_{mu nu} = e^{2A} g_{mu nu}

    R^{(5)}_{mu nu} = R^{(4)}_{mu nu} - e^{2A}[A'' + 4(A')^2] g_{mu nu}

    R_5 = e^{-2A} R_4 - 8A'' - 20(A')^2

    G^{(5)}_{mu nu} = R^{(4)}_{mu nu} - e^{2A}[A'' + 4(A')^2] g_{mu nu}
                      - (1/2) e^{2A} g_{mu nu} [e^{-2A} R_4 - 8A'' - 20(A')^2]

                    = R^{(4)}_{mu nu} - (1/2) g_{mu nu} R_4
                      - e^{2A} g_{mu nu} [A'' + 4(A')^2 - 4A'' - 10(A')^2]

                    = G^{(4)}_{mu nu}
                      + e^{2A} g_{mu nu} [3A'' + 6(A')^2]           ... (2.25)

Similarly:

    G^{(5)}_{55} = (1/2) e^{-2A} R_4 - 6(A')^2
    [Using R^{(5)}_{55} = -4(A'' + (A')^2) and -(1/2)G_{55} R_5 = -(1/2)(e^{-2A}R_4 - 8A'' - 20(A')^2)]
    G^{(5)}_{55} = -4A'' - 4(A')^2 + 4A'' + 10(A')^2 - (1/2)e^{-2A}R_4...

    ... Hmm, let me redo this carefully:
    G^{(5)}_{55} = R^{(5)}_{55} - (1/2) G_{55} R_5
                 = -4[A'' + (A')^2] - (1/2)(1)[e^{-2A}R_4 - 8A'' - 20(A')^2]
                 = -4A'' - 4(A')^2 - (1/2)e^{-2A}R_4 + 4A'' + 10(A')^2
                 = 6(A')^2 - (1/2) e^{-2A} R_4                     ... (2.26)

The (mu nu) Einstein equation becomes:

    F [G^{(4)}_{mu nu} + e^{2A} g_{mu nu}(3A'' + 6(A')^2)]
    + xi [g_{mu nu} Box_5 - nabla_mu nabla_nu](phi^2)
    = (mu^2/sqrt(2X)) d_mu phi d_nu phi - e^{2A} g_{mu nu}(mu^2 sqrt(2X) - V - Lambda_5)
    + delta(y - y_c) e^{2A} [(sigma_IR + alpha_IR phi_c^2) g_{mu nu} + e^{-2A} S^{(EM)}_{mu nu}]
                                                                     ... (2.27)

### 2.8 The (55) Einstein Equation (Hamiltonian Constraint)

    F [6(A')^2 - (1/2) e^{-2A} R_4]
    + xi [G_{55} Box_5 - nabla_5 nabla_5](phi^2)
    = (mu^2/sqrt(2X))(d_y phi)^2 - (mu^2 sqrt(2X) - V - Lambda_5)
                                                                     ... (2.28)

The non-minimal coupling terms:

    G_{55} Box_5(phi^2) = Box_5(phi^2)
    nabla_5 nabla_5(phi^2) = d_y^2(phi^2) = 2(d_y phi)^2 + 2 phi d_y^2 phi

    [G_{55} Box_5 - nabla_5 nabla_5](phi^2)
    = Box_5(phi^2) - 2(d_y phi)^2 - 2 phi phi''
    = e^{-2A} Box_4(phi^2) + [phi''^2-terms + 4A'(phi^2)' - 2(phi')^2 - 2 phi phi'']
    ... working this out:

    Box_5(phi^2) = G^{MN} nabla_M nabla_N(phi^2)
                 = e^{-2A} g^{mu nu} D_mu D_nu(phi^2) + d_y^2(phi^2) + 4A' d_y(phi^2)
                 = e^{-2A} Box_4(phi^2) + 2(phi')^2 + 2 phi phi'' + 8A' phi phi'

So:

    [G_{55} Box_5 - nabla_5 nabla_5](phi^2)
    = e^{-2A} Box_4(phi^2) + 8A' phi phi'
                                                                     ... (2.29)

The (55) equation becomes:

    F [6(A')^2 - (1/2)e^{-2A} R_4]
    + xi [e^{-2A} Box_4(phi^2) + 8A' phi phi']
    = (mu^2/sqrt(2X))(phi')^2 - mu^2 sqrt(2X) + V + Lambda_5
                                                                     ... (2.30)

**Comparison to D1.3 (cosmological case):** In the FRW limit where g_{mu nu} = eta_{mu nu}, R_4 = 0, Box_4(phi^2) = 0, and phi = phi(y) only (so X = X_5 = (1/2)(phi')^2), the right side becomes:

    mu^2(phi')^2/sqrt(2X) - mu^2 sqrt(2X) = mu^2|phi'| - mu^2|phi'| = 0

recovering the remarkable cancellation T^{(P)}_{55} = V + Lambda_5 of D1.3 eq (3.1).

In the LOCAL problem with X_4 != 0, the cancellation is INCOMPLETE:

    (mu^2/sqrt(2X))(phi')^2 - mu^2 sqrt(2X)
    = mu^2 [(phi')^2 - 2X] / sqrt(2X)
    = mu^2 [X_5 - X_4 - X_5] / sqrt(2X)     [using 2X = 2X_4 + 2X_5, (phi')^2 = 2X_5]
    = -mu^2 X_4 / sqrt(X_4 + X_5)            [using 2X = 2(X_4 + X_5)]
    wait, let me redo: (phi')^2 = 2X_5, and 2X = 2X_4 + 2X_5.

    (mu^2/sqrt(2X)) x 2X_5 - mu^2 sqrt(2X)
    = mu^2 [2X_5 - 2X] / sqrt(2X)
    = mu^2 [2X_5 - 2X_4 - 2X_5] / sqrt(2X)
    = -2 mu^2 X_4 / sqrt(2X)
    = -mu^2 sqrt(2X) x (X_4/X)                                      ... (2.31)

So the (55) Hamiltonian constraint becomes:

    +--------------------------------------------------------------------+
    |                                                                    |
    |  F [6(A')^2 - (1/2)e^{-2A} R_4]                                  |
    |  + xi [e^{-2A} Box_4(phi^2) + 8A' phi phi']                      |
    |  = -mu^2 sqrt(2X) (X_4/X) + V + Lambda_5              ... (HC)   |
    |                                                                    |
    |  THE GENERALIZED HAMILTONIAN CONSTRAINT                           |
    |                                                                    |
    |  New features vs. D1.3:                                           |
    |  - R_4 appears (non-flat 4D metric)                               |
    |  - Box_4(phi^2) appears (4D gradients of scalar)                  |
    |  - The cuscuton kinetic energy NO LONGER cancels:                 |
    |    the X_4/X term survives when there are 4D gradients            |
    |                                                                    |
    +--------------------------------------------------------------------+

This is the first key structural result: **the cuscuton's kinetic energy cancellation in the Hamiltonian constraint is broken by 4D spatial gradients.** In the homogeneous limit X_4 -> 0, the cancellation is restored. In the presence of EM sources that induce phi gradients on the brane, X_4 != 0 and the cuscuton contributes kinetic energy to the constraint.

### 2.9 The Cuscuton Constraint in the Local Setting

From eq (2.19), the constraint in the limit X -> 0 (or more precisely, the finite equation multiplied through by sqrt(2X)):

    mu^2 [Box_5 phi - (d_M X d^M phi)/(2X)] = sqrt(2X) [V'(phi) - 2 xi phi R_5]
                                                                     ... (2.32)

In the bulk (away from branes), expanding Box_5 phi:

    Box_5 phi = e^{-2A} Box_4 phi + phi'' + 4A' phi'               ... (2.33)

And the d_M X d^M phi / (2X) term is a second-order correction in X_4.

For the background (X_4 = 0, phi = phi_bg(y)):

    mu^2 [phi_bg'' + 4A' phi_bg'] = sqrt(2X_5) [V' - 2xi phi R_5]
    = |phi_bg'| [V' - 2xi phi(e^{-2A} R_4 - 8A'' - 20(A')^2)]

Since mu^2 is the common factor, this gives the D1.3 scalar constraint (E2) when R_4 = 0.

For the PERTURBATION: let phi = phi_bg(y) + delta phi(x^mu, y). The linearized constraint becomes:

    mu^2 [e^{-2A} Box_4(delta phi) + delta phi'' + 4A' delta phi']
    = (linearized source terms from delta R_5, delta X, etc.)        ... (2.34)

The crucial point: Box_4(delta phi) includes the 4D Laplacian nabla^2(delta phi). In the static case, this is an ELLIPTIC equation on the brane, not a wave equation. The cuscuton's c_s = infinity means the response is indeed instantaneous -- the constraint determines the spatial profile of delta phi algebraically (given the 4D geometry), not dynamically.

### 2.10 Israel Junction Conditions with EM Source

At the IR brane (y = y_c), the Israel junction conditions generalize D1.3 eqs (J1)-(J2):

    +--------------------------------------------------------------------+
    |                                                                    |
    |  [K_{mu nu}] - [K] h_{mu nu} = -(1/F_c) x                       |
    |      [(sigma_IR + alpha_IR phi_c^2) h_{mu nu}                     |
    |       + S^{(EM)}_{mu nu} + S^{(CS)}_{mu nu}]             (JC-IR) |
    |                                                                    |
    |  where:                                                            |
    |  h_{mu nu} = e^{2A_c} g_{mu nu}   (induced metric)               |
    |  F_c = M_5^3 - xi phi_c^2                                        |
    |  S^{(EM)}_{mu nu} = F_{mu alpha}F_nu^alpha                       |
    |                    - (1/4)h_{mu nu} F_{ab}F^{ab}                  |
    |  S^{(CS)}_{mu nu} = theta_grav(phi_c) C_{mu nu}                  |
    |                    + (theta_EM / (16pi^2)) x [E.B metric vars]    |
    |                                                                    |
    +--------------------------------------------------------------------+

For the Z_2 orbifold with our metric ansatz:

    K_{mu nu}(y_c^-) = A'(y_c) e^{2A_c} g_{mu nu}                  ... (2.35)

The trace: K = 4A'(y_c).

    K_{mu nu} - K h_{mu nu} = -3 A'(y_c) e^{2A_c} g_{mu nu}       ... (2.36)

The jump: [K_{mu nu} - K h_{mu nu}] = -6 A'(y_c^-) e^{2A_c} g_{mu nu} (Z_2 doubles the contribution).

So the junction condition for the TRACE part gives the background warp-rate condition as in D1.3. The NEW content is in the TRACELESS part:

    [K_{mu nu}] - (1/4) h_{mu nu} [K] = -(1/F_c) [S^{(EM)}_{mu nu} - (1/4) h_{mu nu} S^{(EM)}]
                                                                     ... (2.37)

The left side vanishes for our ansatz (K_{mu nu} proportional to g_{mu nu}). This means:

    S^{(EM)}_{mu nu} - (1/4) h_{mu nu} S^{(EM)} = 0               ... (2.38)

This is the traceless part of the EM stress-energy. For a generic EM field, this is NOT zero. The resolution: **the metric ansatz (2.1) with y-independent g_{mu nu} is inconsistent with an arbitrary brane-localized EM source.** The EM field back-reacts on the 4D metric, and the perturbation delta g_{mu nu}(x) satisfies:

    G^{(4)}_{mu nu}[g_bg + delta g] = (8 pi G_4) T^{(total)}_{mu nu}
                                                                     ... (2.39)

where G_4 = 1/(M_Pl^2) is the effective 4D Newton constant (from integrating over y), and T^{(total)} includes the EM stress-energy plus any cuscuton-mediated modifications.

### 2.11 The Linearized System

We perturb around the RS background:

    g_{mu nu} = eta_{mu nu} + h_{mu nu}(x)                          ... (2.40)
    phi(x, y) = phi_bg(y) + delta phi(x, y)                         ... (2.41)
    A(y) = A_bg(y)     (background warp factor, unperturbed at leading order)

The perturbation is sourced by the EM field on the IR brane:

    S^{(EM)}_{mu nu} delta(y - y_c)                                 ... (2.42)

**Bulk equations for delta phi(x, y):**

From the linearized scalar constraint (2.34), in the bulk:

    e^{-2A} Box_4(delta phi) + delta phi'' + 4A' delta phi'
    = [source terms proportional to h_{mu nu} through delta R_5]
                                                                     ... (2.43)

In Fourier space (delta phi(x, y) -> delta phi_p(y) e^{ip.x}):

    -e^{-2A} p^2 delta phi_p + delta phi_p'' + 4A' delta phi_p'
    = S_p(y)                                                         ... (2.44)

where p^2 = -omega^2 + |vec p|^2 is the 4D momentum squared and S_p(y) is the source from the metric perturbation.

**Boundary condition at the IR brane:**

The EM field on the brane provides a source for delta phi through the scalar junction condition. From the generalization of J3b (D1.3):

    [d_y(delta phi)]_{y_c} = -(1/mu^2) [delta(alpha_IR phi_c) + xi phi_c delta R_4 + EM contributions]
                                                                     ... (2.45)

The EM contribution to the scalar boundary condition comes from the backreaction: the EM field perturbs the 4D metric (through the standard Einstein equation), the perturbed metric produces delta R_4, and delta R_4 sources delta phi through the non-minimal coupling xi phi R_5.

### 2.12 Summary of the Full System

    +====================================================================+
    |                                                                    |
    |  THE LOCAL 5D SYSTEM (Task 9C.1 Complete)                         |
    |                                                                    |
    |  BULK (0 < y < y_c):                                             |
    |                                                                    |
    |  (1) 5D Einstein eqn: F G^{(5)}_{MN} + xi-terms = T^{cusc}_{MN} |
    |  (2) Cuscuton constraint: mu^2[Box_5 phi - ...] = sqrt(2X)[...]  |
    |  (3) Hamiltonian constraint: generalized HC (eq 2.30)             |
    |                                                                    |
    |  IR BRANE (y = y_c):                                              |
    |                                                                    |
    |  (4) Israel junction: [K_{mn}] = -(1/F_c)(sigma + EM + CS)       |
    |  (5) Scalar junction: [phi'] = function of (alpha, xi, R_4, EM)  |
    |  (6) Maxwell equations: D_mu F^{mu nu} = j^nu                    |
    |                                                                    |
    |  UV BRANE (y = 0):                                                |
    |                                                                    |
    |  (7) Israel junction: standard (no EM source)                     |
    |  (8) Scalar junction: standard                                    |
    |                                                                    |
    |  KEY NEW FEATURES vs. D1.3:                                       |
    |  - g_{mu nu}(x) general: R_4 != 0, Box_4 phi != 0               |
    |  - Cuscuton kinetic energy cancellation BROKEN by X_4             |
    |  - EM source enters through Israel junction AND scalar junction   |
    |  - CS terms enter through junction conditions                     |
    |                                                                    |
    +====================================================================+

---

## 3. Static Solutions with EM Source (Task 9C.2)

### 3.1 The Static Spherically Symmetric Setup

Consider a static, spherically symmetric configuration on the IR brane: an EM field localized in a finite region of space (e.g., a parallel-plate capacitor inside a solenoid, producing both E and B fields).

The 4D metric perturbation:

    ds_4^2 = -(1 + 2 Phi(r)) dt^2 + (1 - 2 Psi(r))(dr^2 + r^2 d Omega^2)
                                                                     ... (3.1)

The scalar perturbation:

    phi(r, y) = phi_bg(y) + delta phi(r, y)                         ... (3.2)

The EM source: localized in a region r < R_source with energy density rho_EM ~ E^2/(8 pi) + B^2/(8 pi).

### 3.2 The Cuscuton Response: Does X Deviate from Zero?

On the background, X_4 = 0 and X = X_5 = (1/2)(phi_bg')^2.

With the perturbation:

    X = (1/2) e^{-2A} g^{mu nu} d_mu phi d_nu phi + (1/2)(d_y phi)^2

    X_4 = (1/2) e^{-2A} (1 + 2Psi)^{-1} (d_r delta phi)^2
        ~ (1/2) e^{-2A} (d_r delta phi)^2   (to linear order in h but quadratic in delta phi)
                                                                     ... (3.3)

    X_5 = (1/2)(phi_bg' + d_y delta phi)^2
        ~ X_5^{bg} + phi_bg' d_y(delta phi) + (1/2)(d_y delta phi)^2
                                                                     ... (3.4)

At LINEAR order in delta phi:

    delta X = phi_bg' d_y(delta phi)     (from X_5 only)
    X_4 = O((delta phi)^2)                                          ... (3.5)

So to LINEAR order, X_4 = 0 and the system reduces to the perturbative analysis already performed in Phase 2 (D2.4), which gives delta g/g ~ 10^{-77}.

**This is the central tension:** The interesting physics (X_4 != 0, broken kinetic cancellation) appears only at SECOND order in the perturbation, or in a fully non-linear treatment.

### 3.3 The Linearized Cuscuton Profile

The linearized bulk equation for delta phi from the constraint (eq 2.44 in the static limit omega = 0):

    e^{-2A} nabla_4^2(delta phi) + d_y^2(delta phi) + 4A' d_y(delta phi)
    = xi phi_bg (e^{-2A} delta R_4 - 8 delta A'' - 20 x 2A' delta A')
                                                                     ... (3.6)

where nabla_4^2 = d_r^2 + (2/r) d_r is the radial Laplacian.

At leading order, the EM field sources the metric perturbation Phi(r) through the standard 4D Einstein equation:

    nabla_4^2 Phi = -4 pi G_4 rho_EM(r)                            ... (3.7)

This gives the Newtonian potential: Phi ~ -G_4 M_EM / r for r > R_source, where M_EM = int rho_EM d^3x is the total EM field energy divided by c^2.

The metric perturbation produces delta R_4 ~ nabla_4^2 Phi ~ -4 pi G_4 rho_EM.

This sources delta phi through the non-minimal coupling xi:

    nabla_4^2(delta phi) + e^{2A} [d_y^2(delta phi) + 4A' d_y(delta phi)]
    ~ -xi phi_bg x 4 pi G_4 rho_EM(r)                              ... (3.8)

The solution factorizes:

    delta phi(r, y) = chi(r) x psi(y)                               ... (3.9)

where chi(r) satisfies nabla_4^2 chi = -4 pi G_4 rho_EM(r) (i.e., chi proportional to Phi) and psi(y) satisfies the y-dependent equation with boundary conditions from J3a and J3b.

**Magnitude estimate:**

    delta phi / phi_bg ~ xi x (rho_EM / M_Pl^2) x R_source^2       ... (3.10)

For laboratory EM fields:
    rho_EM ~ E^2/(8 pi) ~ (10^7)^2 / (8 pi) ~ 4 x 10^{12} J/m^3 ~ 10^{-25} GeV^4
    R_source ~ 1 m ~ 5 x 10^{15} GeV^{-1}
    M_Pl^2 = 2.4 x 10^{18} GeV)^2 = 5.8 x 10^{36} GeV^2

    delta phi / phi_bg ~ 0.038 x (10^{-25} / 5.8 x 10^{36}) x (5 x 10^{15})^2
                        ~ 0.038 x 1.7 x 10^{-62} x 2.5 x 10^{31}
                        ~ 0.038 x 4.3 x 10^{-31}
                        ~ 1.6 x 10^{-32}                            ... (3.11)

This is a fractional perturbation of order 10^{-32}. The 4D kinetic variable:

    X_4 ~ (1/2)(d_r delta phi)^2
        ~ (1/2)(delta phi / R_source)^2
        ~ (1/2)(1.6 x 10^{-32} phi_bg / R_source)^2               ... (3.12)

Compared to X_5^{bg} = (1/2)(phi_bg')^2 ~ (1/2)(k phi_bg)^2 where k ~ M_5^{2/3} M_Pl^{1/3} from the RS relation:

    X_4 / X_5 ~ (delta phi / phi_bg)^2 x (k R_source)^{-2} x (something)

In any case, X_4 is a SECOND-ORDER effect in the already-tiny perturbation, giving:

    X_4 / X_5 ~ (10^{-32})^2 = 10^{-64}                           ... (3.13)

**This is negligible.** The spatial gradients of the cuscuton induced by laboratory EM fields are far too small to break the kinetic cancellation in any meaningful way.

### 3.4 The Gravitational Response

The total gravitational response has two contributions:

**(a) Direct EM gravitational field:** The EM energy-momentum gravitates normally through the standard 4D Einstein equation:

    delta g / g ~ G_4 rho_EM R^2 / c^4 ~ 10^{-63} (for lab fields)
                                                                     ... (3.14)

This is just the Newtonian gravity of the EM field energy. Tiny but well-known.

**(b) Cuscuton-mediated gravitational modification:** The cuscuton perturbation delta phi modifies the effective 4D gravitational coupling through the non-minimal coupling F(phi) = M_5^3 - xi phi^2:

    delta G_4 / G_4 ~ 2 xi phi_bg delta phi / M_Pl^2
                     ~ 2 x 0.038 x (delta phi / phi_bg) x (phi_bg^2 / M_Pl^2)
                     ~ 2 x 0.038 x 10^{-32} x zeta_0
                     ~ 2 x 0.038 x 10^{-32} x 0.038
                     ~ 3 x 10^{-35}                                  ... (3.15)

This is the cuscuton's contribution to the local gravitational modification. It is LARGER than the direct EM gravity (10^{-35} vs 10^{-63}) but still utterly negligible.

### 3.5 Can Non-Linear Effects Enhance the Response?

The linearized result is clear: delta phi ~ 10^{-32} phi_bg, X_4 ~ 10^{-64} X_5. Could non-linear effects change this qualitatively?

**Non-linear amplification scenarios:**

**(i) Cuscuton singularity as amplifier.** Near X = 0, P_XX diverges. Could a small perturbation delta X be amplified by the divergent response function? Let us check. The second-order perturbation to the scalar constraint:

    delta^2 [mu^2 Box_5 phi / sqrt(2X)] ~ mu^2 [delta X / X^{3/2}] x (correction)

The amplification factor is delta X / X^{3/2} ~ X_4 / X_5^{3/2}. But X_4 ~ (delta phi)^2 and X_5 ~ (phi_bg')^2, so:

    amplification ~ (delta phi)^2 / (phi_bg')^3 ~ (10^{-32})^2 / phi_bg'^3

This is not an amplification -- it is an even smaller number. The divergence of P_XX at X = 0 does not help because the perturbation X_4 that probes it is itself proportional to (delta phi)^2, which is already negligible.

**The reason is structural:** The X = 0 singularity is approached FROM ABOVE (X >= 0 always). The divergence of P_XX is a statement about the STIFFNESS of the constraint, not about amplification. Higher P_XX means the constraint is HARDER to violate, not easier. The cuscuton resists being pushed away from X ~ X_5; the perturbation X_4 is energetically disfavored because the "spring constant" P_XX is infinite.

**(ii) Solitonic solutions.** Could there exist a solution where X transitions from ~X_5 to a value significantly different from X_5 in a localized region? This requires solving the full non-linear constraint equation. In the static case:

    mu^2 [nabla_4^2 phi + phi'' + 4A'phi'] / sqrt(2X) - mu^2 (d_M X d^M phi) / (2X sqrt(2X))
    = V' - 2xi phi R_5 + (brane sources)

For a solitonic profile where delta phi ~ O(1) (not small):

    The soliton width l satisfies: mu^2 / l^2 ~ V'(phi) ~ c (tadpole)
    l ~ mu / sqrt(c)                                                 ... (3.16)

If mu ~ M_5^{3/2} / M_Pl ~ 10^{-7} GeV (from KK reduction) and c ~ H_0^2 M_Pl ~ 10^{-33} GeV (from cosmological constant scale):

    l ~ 10^{-7} / 10^{-16.5} ~ 10^{9.5} GeV^{-1} ~ 10^{-5.5} m    ... (3.17)

This is a microscopic scale (~3 micrometers). A soliton of this width could in principle exist, but the key question is: **what sources it?** Creating a soliton where delta phi ~ phi_bg requires an energy:

    E_soliton ~ mu^2 phi_bg^2 / l ~ mu^2 phi_bg^2 sqrt(c) / mu
              ~ mu phi_bg^2 sqrt(c)                                  ... (3.18)

This is an enormous energy in Planck units. Laboratory EM fields cannot source it -- the energy available is rho_EM x V ~ 10^{-25} GeV^4 x (5 x 10^{15})^3 ~ 10^{22} GeV, while the soliton energy involves factors of phi_bg^2 and mu, both related to the gravitational scale.

**(iii) Resonance in the extra dimension.** The bulk equation (2.44) admits KK mode solutions. The y-dependent part has resonances when p^2 matches a KK mass:

    m_n^2 ~ n^2 k^2 e^{-2ky_c}     (for n = 1, 2, ...)             ... (3.19)

The lightest KK mode has m_1 ~ k e^{-ky_c} ~ 10^8 x 10^{-17} ~ 10^{-9} GeV ~ 10 eV.

For a STATIC source (p^2 = -|p|^2 < 0), there is no resonance -- the KK modes are above threshold. The response is exponentially suppressed by the KK mass gap:

    delta phi_KK ~ e^{-m_1 r} / r     (Yukawa suppression)         ... (3.20)

For r ~ 1 m ~ 5 x 10^{15} GeV^{-1} and m_1 ~ 10^{-9} GeV:

    m_1 r ~ 5 x 10^6 >> 1

The KK contributions are exponentially suppressed at laboratory distances. Only the zero mode contributes, and that gives the estimate of Section 3.3.

### 3.6 Task 9C.2 Verdict

    +====================================================================+
    |                                                                    |
    |  TASK 9C.2 RESULT: STATIC SOLUTIONS                               |
    |                                                                    |
    |  1. The cuscuton develops a spatial profile delta phi(r, y)       |
    |     sourced by the EM field through the non-minimal coupling.     |
    |     Magnitude: delta phi / phi_bg ~ 10^{-32} for lab fields.     |
    |                                                                    |
    |  2. X_4(r) ~ (d_r delta phi)^2 ~ 10^{-64} x X_5.                |
    |     The kinetic variable does NOT deviate meaningfully from       |
    |     the background value. X ~ X_5 everywhere.                     |
    |                                                                    |
    |  3. The gravitational response delta G/G ~ 10^{-35} through      |
    |     the non-minimal coupling. This is larger than the direct      |
    |     EM gravitational field (10^{-63}) but still negligible.       |
    |                                                                    |
    |  4. Non-linear amplification DOES NOT WORK because:              |
    |     (a) The X = 0 singularity increases stiffness, not response  |
    |     (b) Solitonic solutions require gravitational-scale energy    |
    |     (c) KK resonances are above threshold for static sources     |
    |                                                                    |
    |  5. The cuscuton is RIGID locally. Its spatial profile tracks     |
    |     the EM gravitational potential with extreme fidelity but      |
    |     negligible amplitude.                                         |
    |                                                                    |
    |  KILL CONDITION: X(r) deviates from background by 10^{-64}.      |
    |  This is effectively X(r) = X_bg everywhere.                     |
    |  Static channel is DEAD for laboratory EM fields.                 |
    |                                                                    |
    +====================================================================+

---

## 4. Dynamic Solutions (Task 9C.3)

### 4.1 Time-Dependent EM Source

Consider oscillating EM fields on the IR brane:

    E(t, r) = E_0 f(r) cos(omega t)
    B(t, r) = B_0 g(r) cos(omega t + delta)                        ... (4.1)

where f(r) and g(r) are spatial profiles (localized to the source region) and omega is the oscillation frequency.

The topological charge density:

    E . B = E_0 B_0 f(r) g(r) cos(omega t) cos(omega t + delta)
          = (E_0 B_0 / 2) f g [cos(delta) + cos(2 omega t + delta)]
                                                                     ... (4.2)

This has both a DC component (if delta != pi/2) and a 2omega oscillating component.

### 4.2 The Cuscuton Response: Instantaneous Propagation

The cuscuton's sound speed c_s = infinity (for the classical P(X) = mu^2 sqrt(2X)) means that the scalar field response to a time-dependent source is INSTANTANEOUS in the 4D spatial directions. The constraint equation at each instant t determines the spatial profile delta phi(t, r, y):

    nabla^2 delta phi(t, r, y) + e^{2A}[d_y^2 + 4A' d_y] delta phi
    = xi phi_bg e^{2A} delta R_4(t, r)                              ... (4.3)

where delta R_4(t, r) is sourced by the time-dependent EM field through the 4D Einstein equation.

**No retardation:** Because c_s = infinity, the cuscuton does not propagate as a wave. The constraint is satisfied at every instant. There is no finite propagation speed, no wave fronts, no radiation from the cuscuton. The response at any point in space is determined by the instantaneous source configuration everywhere.

**What constrains the amplitude?** The same factors as in the static case:
- The non-minimal coupling xi ~ 0.038 is weak
- The EM energy density rho_EM ~ 10^{-25} GeV^4 is tiny compared to M_Pl^4
- The cuscuton's stiffness (divergent P_XX) resists deviation from X ~ X_5

The oscillation frequency enters only through the time-dependent EM stress-energy, not through any propagation effect. The amplitude of the cuscuton response is:

    delta phi(t) / phi_bg ~ 10^{-32} x cos(omega t) (or similar time dependence)
                                                                     ... (4.4)

The SAME magnitude as the static case, just modulated in time.

### 4.3 Resonance Analysis

Could resonances exist that enhance the response at specific frequencies?

**(a) KK mode resonance.** The y-dependent part of the equation has eigenvalues m_n (KK masses). For a time-dependent source with frequency omega, the 4D momentum is p^2 = -omega^2 (spatial zero mode, uniform source) or p^2 = -omega^2 + k_perp^2 (with spatial gradients). Resonance occurs when p^2 = m_n^2, i.e.:

    omega = sqrt(m_n^2 + k_perp^2)                                  ... (4.5)

The lightest KK mass m_1 ~ 10 eV corresponds to a frequency:

    f_1 = m_1 / (2 pi hbar) ~ 10 eV / (6.6 x 10^{-16} eV s) ~ 1.5 x 10^{16} Hz

This is in the near-UV range. Laboratory EM oscillation frequencies (radio to microwave, f ~ 10^6 - 10^{11} Hz) are far below the KK resonance.

For the CUSCUTON specifically, the situation is different from a normal scalar. The cuscuton does not have a standard propagator -- its c_s = infinity means all frequencies propagate instantly. In the regularized theory (with eps^2 from Track 9A), the effective propagator is:

    G(omega, k) ~ 1 / [P_X(omega^2 - c_s^2 k^2) - m_eff^2]

With c_s^2 ~ 2X_5/eps^2 >> 1 (from D9.1 eq 2.3):

    G(omega, k) ~ eps / (mu^2) x 1 / [omega^2/c_s^2 - k^2 - m_eff^2/c_s^2]

The pole is at omega ~ c_s k >> k (superluminal). There is no on-shell resonance at laboratory frequencies unless omega ~ c_s m_KK, which would require omega ~ (2X_5/eps^2)^{1/2} x m_KK. Since eps^2 ~ 10^{-244}, this gives omega ~ 10^{122} x 10 eV, which is absurdly large.

**Conclusion: No resonance exists at any accessible frequency.** The cuscuton's infinite sound speed means there is no frequency at which the response is enhanced. The constraint character of the equation means the response is always algebraically determined, never resonantly amplified.

**(b) Parametric resonance.** Could the oscillating EM field parametrically amplify cuscuton perturbations? Parametric resonance requires a time-periodic modulation of the effective mass or frequency of a mode. For the cuscuton:

The effective equation for a KK mode psi_n(t):

    psi_n'' + [m_n^2 + delta m^2(t)] psi_n = 0                     ... (4.6)

where delta m^2(t) ~ xi x delta R_4(t) ~ xi x G_4 x d_t^2 rho_EM(t).

For delta m^2 ~ xi G_4 omega^2 rho_EM:

    delta m^2 / m_n^2 ~ xi G_4 omega^2 rho_EM / m_n^2
                       ~ 0.038 x 10^{-38} x (10^9)^2 x 10^{-25} / (10)^2   [omega ~ GHz, m_1 ~ 10 eV]
                       ~ 10^{-63}                                    ... (4.7)

The parametric resonance parameter q = delta m^2 / (2 omega^2) ~ 10^{-63}. For parametric resonance to be effective, we need q > 1 (broad resonance) or at least q >> exp(-damping) (narrow resonance). With q ~ 10^{-63}, parametric amplification is completely negligible.

**(c) Modulated theta coupling.** In the dynamical CS scenario (D9.4 Section 4.5), theta_grav depends on phi, so oscillating phi produces oscillating theta. The resulting CS modification to gravity oscillates at the same frequency. But the amplitude is:

    delta theta / theta ~ delta phi / phi_bg ~ 10^{-32}

And the gravitational CS modification is:

    C_{mu nu} ~ d theta x (curvature derivatives)
              ~ (delta theta / R_source) x (R_curv / R_source^2)
              ~ 10^{-32} x theta_grav x (1/R^2) x (R_curv/R^2)

This is even smaller than the static case because the CS Cotton tensor involves derivatives.

### 4.4 The E.B Channel (Dynamic)

The most interesting dynamic configuration is oscillating parallel E and B, producing time-varying E.B. From D9.4 Section 5:

The anomaly matching equation:

    d_mu j^mu_{CS, grav} = -(1/(2pi^2)) E . B                     ... (4.8)

For oscillating E . B:

    E . B = (E_0 B_0 / 2) [cos(delta) + cos(2 omega t + delta)]   ... (4.9)

The gravitational Pontryagin density *RR must match:

    *RR = -(1/(2pi^2)) E . B                                        ... (4.10)

**However**, as established in D9.4 Section 5.7, this equation is a statement about the QUANTUM effective action. The physical gravitational response requires computing the one-loop fermion effective action in the combined gravitational + EM background. The result is Planck-suppressed:

    delta g / g ~ (alpha_EM / pi) x (E B) / (m_e^2 M_Pl^2)
                ~ 10^{-3} x 10^{-20} / (10^{-7} x 10^{38})
                ~ 10^{-3} x 10^{-20} / 10^{31}
                ~ 10^{-54}                                           ... (4.11)

Even with the 5D warp enhancement (M_Pl -> M_5 in the denominator):

    delta g / g ~ alpha_EM x E B / (m_e^2 M_5^2)
                ~ 10^{-3} x 10^{-20} / (10^{-7} x 10^{16})
                ~ 10^{-3} x 10^{-20} / 10^{9}
                ~ 10^{-32}                                           ... (4.12)

Better than the static cuscuton channel (10^{-35}) but still utterly negligible.

### 4.5 Frequency Dependence Summary

| Frequency regime | Physical process | Response scaling | Viable? |
|-----------------|-------------------|-----------------|---------|
| DC (omega = 0) | Static cuscuton profile | delta g ~ xi rho_EM / M_Pl^2 ~ 10^{-35} | NO |
| RF (omega ~ MHz) | Oscillating cuscuton, no resonance | Same as DC x cos(omega t) | NO |
| Microwave (omega ~ GHz) | Same, far below KK | Same as DC | NO |
| Optical (omega ~ 10^{14} Hz) | Still below KK m_1 ~ 10^{16} Hz | Same as DC | NO |
| Near-KK (omega ~ 10^{16} Hz) | KK mode excitation possible | Enhanced by 1/(omega^2 - m_1^2) | Maybe, but tiny coupling |
| UV (omega ~ 10 eV) | On KK resonance | Resonant enhancement of delta phi | delta phi still ~ 10^{-30} |

At the KK resonance, the enhancement factor is:

    Q ~ m_n / Gamma_n     (quality factor)

where Gamma_n is the KK mode width. For narrow KK resonances (Gamma ~ m_n alpha_grav ~ m_n x G_4 m_n^2), Q ~ 1/alpha_grav ~ M_Pl^2/m_n^2 ~ 10^{36}/100 ~ 10^{34}. This is large, but the coupling to EM is suppressed by:

    g_{EM-KK} ~ xi (rho_EM / M_5^3 m_n^2)                          ... (4.13)

So the resonance-enhanced response is:

    delta phi / phi_bg ~ Q x g_{EM-KK} x (non-resonance response)
                       ~ 10^{34} x 10^{-32} x 10^{-32}
                       ~ 10^{-30}                                    ... (4.14)

Still negligible, even with an astronomically large quality factor.

### 4.6 Task 9C.3 Verdict

    +====================================================================+
    |                                                                    |
    |  TASK 9C.3 RESULT: DYNAMIC SOLUTIONS                              |
    |                                                                    |
    |  1. The cuscuton's c_s = inf means response is instantaneous.    |
    |     No propagation delay, no wave fronts, no radiation.           |
    |     The amplitude is set by the constraint, not dynamics.         |
    |                                                                    |
    |  2. No resonance at any accessible frequency:                     |
    |     - KK resonance at omega ~ 10^{16} Hz (near-UV), far above   |
    |       laboratory frequencies                                      |
    |     - Cuscuton has no standard propagator to resonate             |
    |     - Parametric resonance parameter q ~ 10^{-63}                |
    |                                                                    |
    |  3. Dynamic response has the SAME magnitude as static:           |
    |     delta phi / phi_bg ~ 10^{-32}, delta G/G ~ 10^{-35}         |
    |     The time dependence is just a modulation envelope.            |
    |                                                                    |
    |  4. The E.B anomaly channel (D9.4) gives at best delta g ~       |
    |     10^{-32} with 5D warp enhancement. Still negligible.          |
    |                                                                    |
    |  5. Even at KK resonance (omega ~ 10 eV) with Q ~ 10^{34},     |
    |     the response is delta phi ~ 10^{-30} phi_bg. No help.       |
    |                                                                    |
    |  KILL CONDITION: delta g < 10^{-30} for ALL frequencies and      |
    |  ALL field configurations accessible in the laboratory.           |
    |  Dynamic channel is DEAD.                                         |
    |                                                                    |
    +====================================================================+

---

## 5. Kill Condition Assessment

### 5.1 The Root Cause

Tasks 9C.1-9C.3 have identified the same fundamental suppression that killed all Phase 8 mechanisms, but now from the LOCAL perspective:

**The cuscuton's constraint structure prevents laboratory EM fields from producing measurable gravitational modification.**

The suppression operates through a chain:

    (1) EM field energy density: rho_EM ~ 10^{-25} GeV^4
    (2) Gravitational coupling: G_4 rho_EM ~ 10^{-63}
    (3) Non-minimal coupling amplification: xi ~ 0.038 -> x25 enhancement
    (4) Cuscuton profile: delta phi / phi_bg ~ xi G_4 rho_EM R^2 ~ 10^{-32}
    (5) Gravitational modification: delta G/G ~ xi (delta phi / phi_bg) ~ 10^{-35}

At no step is there an amplification factor larger than O(10). The fundamental bottleneck is step (2): the ratio of EM energy density to the gravitational scale.

### 5.2 What Could Change This?

For a gravitational effect delta g/g ~ 10^{-7} (the threshold for a sensitive torsion balance experiment), we would need:

    delta phi / phi_bg ~ 10^{-7} / xi ~ 10^{-5.6}

This requires:

    xi G_4 rho_EM R^2 ~ 10^{-5.6}
    rho_EM ~ 10^{-5.6} / (0.038 x 10^{-38} x 10^{31}) ~ 10^{-5.6} / 10^{-8.4} ~ 10^{2.8}

    rho_EM ~ 600 GeV^4 ~ 10^{43} J/m^3                              ... (5.1)

This is the energy density of a nuclear explosion compressed into a cubic meter. It is six orders of magnitude above what any continuous laboratory EM field can produce. For comparison, the Schwinger critical field (E_S = m_e^2 c^3 / (e hbar) ~ 1.3 x 10^{18} V/m) gives rho_S ~ 4 x 10^{25} J/m^3 ~ 10^{-18} GeV^4 -- still 21 orders of magnitude too small.

### 5.3 Comparison of All Channels

| Channel | Track | delta g/g | Status |
|---------|-------|-----------|--------|
| Linear KK (D2.4) | Phase 2 | 10^{-77} | DEAD |
| Cosmological cuscuton (Phase 8) | Phase 8 | 10^{-3} (but LCDM-like) | DEAD for dynamics |
| Functional RG (D9.1) | 9A | eps^2 ~ 10^{-244} | DEAD |
| Perturbative CS (D9.4) | 9B | 10^{-28} (best case) | DEAD |
| Static local cuscuton | 9C.2 | 10^{-35} | DEAD |
| Dynamic local cuscuton | 9C.3 | 10^{-35} | DEAD |
| E.B anomaly (5D enhanced) | 9C.3 + 9B | 10^{-32} | DEAD |
| KK resonance enhanced | 9C.3 | 10^{-30} | DEAD |
| Non-perturbative (solitons) | 9C.4 (not yet done) | UNKNOWN | OPEN |
| Topological transitions | 9B.3 (not yet done) | UNKNOWN | OPEN |

**Every perturbative and semi-perturbative channel produces gravitational effects suppressed by at least 10^{-28} for laboratory EM fields.** The suppression is ultimately controlled by the ratio rho_EM / M_Pl^4 ~ 10^{-77}, with various enhancement mechanisms (non-minimal coupling, warp factor, KK resonance) recovering at most ~47 orders of magnitude.

### 5.4 What Remains Open

Two channels have NOT been killed by this analysis:

**(a) Non-perturbative solitonic solutions (Task 9C.4).** The linearized analysis shows no large effects. But the full non-linear constraint equation could admit solitonic solutions -- configurations where the cuscuton transitions from one value to another across a domain wall. The energy cost of such a soliton is the key question. If the energy barrier is O(M_Pl^4), it is inaccessible. If it is O(M_5^4) or lower, it might be accessible with extreme field configurations.

**(b) Topological transitions (Task 9B.3, Track 9C connection).** A topological transition changes the theta sector of the theory. If the barrier height for such a transition is lower than the Planck scale (perhaps set by the warp-reduced scale Lambda_IR ~ 1 GeV), laboratory fields might trigger it. This connects to the EPS soliton scenario and the domain wall interpretation of AO-2.

Both of these require going beyond the perturbative/semi-perturbative framework used in this deliverable. They are the subject of Tasks 9C.4-9C.5 (next).

---

## 6. Connection to AO-1 and AO-2

### 6.1 AO-1: Biefeld-Brown Effect

The Biefeld-Brown observations (net thrust on asymmetric capacitors in high vacuum) report effects at millinewton scale, corresponding to delta g/g ~ 10^{-3} or larger. Our best estimate for any cuscuton-mediated gravitational effect from a high-voltage capacitor is:

    delta g/g ~ 10^{-32} (E.B anomaly, 5D enhanced)

The gap is **29 orders of magnitude.** No combination of known effects within the Meridian framework can bridge this gap through perturbative or semi-perturbative mechanisms.

The Biefeld-Brown observation, if real, requires either:
- Physics entirely outside the Meridian framework
- A non-perturbative mechanism that bypasses ALL the suppressions identified above
- An experimental artifact not yet identified

### 6.2 AO-2: EPS Framework

The EPS framework describes a soliton-like boundary creating a region of modified vacuum state. Within Meridian, this maps to a domain wall on the IR brane where:
- The gauge field configuration has non-trivial topology (different theta sector)
- The cuscuton profile changes across the wall
- The effective gravitational coupling changes inside the soliton

The PERTURBATIVE analysis of this deliverable cannot assess this scenario. The soliton is by definition a non-perturbative object. Task 9C.4 will address whether such solitons exist and what their properties are.

The key question for AO-2 compatibility: **Is the energy barrier for creating a theta domain wall on the IR brane accessible with laboratory EM fields?**

From the spectral action (D9.4), the theta angle on the IR brane is set by the spectral geometry at the scale Lambda_IR ~ 1 GeV. The energy density of a theta domain wall in QCD is:

    sigma_wall ~ f_pi^2 m_pi^2 ~ (93 MeV)^2 x (135 MeV)^2 ~ 10^{-4} GeV^4

This is in the range of laboratory energy densities (rho_EM ~ 10^{-25} GeV^4 is still far below, but the gap is "only" 21 orders -- much less than the 77 orders to Planck). The question is whether the ELECTROWEAK theta domain wall (which is relevant for EM-gravity coupling) has a similar scale, or whether it is set by the Planck/warp scale.

### 6.3 Assessment

| Observable | Required delta g/g | Best perturbative estimate | Gap | Non-perturbative hope |
|-----------|-------------------|---------------------------|-----|----------------------|
| AO-1 (Biefeld-Brown) | ~10^{-3} | 10^{-32} | 29 orders | Soliton |
| AO-2 (EPS) | ~10^{-1} (weightlessness) | 10^{-32} | 31 orders | Theta domain wall |
| Torsion balance | ~10^{-13} | 10^{-32} | 19 orders | KK tunneling |

---

## 7. Honest Assessment: What Survives

### 7.1 Dead Channels (This Deliverable)

1. **Static cuscuton profile from EM source:** delta phi/phi_bg ~ 10^{-32}. Dead.
2. **Dynamic cuscuton response:** Same magnitude as static, no resonance enhancement. Dead.
3. **Non-linear amplification through X = 0 singularity:** The singularity increases stiffness, not response. Dead.
4. **KK resonance at laboratory frequencies:** KK masses too high (10 eV vs lab meV-eV). Dead.
5. **Parametric amplification:** q ~ 10^{-63}. Dead.
6. **E.B anomaly through CS (perturbative):** 10^{-32} with 5D enhancement. Dead.

### 7.2 Structural Insights

1. **The broken kinetic cancellation** (Section 2.8, eq 2.31): In the local setting, the cuscuton's kinetic energy does NOT cancel in the Hamiltonian constraint. The surviving term is proportional to X_4/X, which measures the ratio of 4D to 5D kinetic contributions. This is a genuine new feature of the local theory, but X_4 is too small to matter for laboratory fields.

2. **The stiffness interpretation of X = 0:** The divergence of P_XX at X = 0 is not an amplifier -- it is a rigidity. The cuscuton RESISTS being pushed away from its constraint surface. This explains why every perturbative attempt to excite the cuscuton fails: the response function goes as 1/P_XX -> 0 as X -> 0, not as P_XX -> infinity.

3. **The universality of the suppression:** All channels are ultimately limited by the ratio rho_EM / M_*^4, where M_* is the relevant gravitational scale. The best case (5D enhanced, M_* = M_5 ~ 10^8 GeV) gives rho_EM / M_5^4 ~ 10^{-25}/10^{32} ~ 10^{-57}. No mechanism within the linearized or semi-perturbative theory can overcome this.

### 7.3 Open Channels (For Tasks 9C.4-9C.5)

1. **Solitonic/domain wall solutions:** Non-perturbative objects that cannot be accessed by linearizing around the background. The key unknowns are:
   - Do they exist as solutions of the full non-linear system?
   - What is their energy cost?
   - Can they be nucleated by laboratory EM fields?
   - What is the gravitational signature inside a soliton?

2. **Topological transitions on the brane:** Changes in the theta sector that modify the vacuum state. The key unknowns are:
   - What is the barrier height for an EW theta transition?
   - Does the warped geometry reduce the barrier?
   - Can E.B fields catalyze the transition (analogous to sphaleron production in strong magnetic fields)?

3. **Non-perturbative tunneling (KK Schwinger):** Track 9D territory. The Schwinger effect produces particle pairs non-perturbatively, bypassing perturbative coupling suppression. Whether the cuscuton modifies the RS tunneling rate is the 9D question.

### 7.4 The Probability Update

Before this calculation:
- P(9C produces measurable local cuscuton response) = 25% (Phase 9 plan)

After Tasks 9C.1-9C.3:
- P(perturbative local cuscuton response is measurable) = 0% (KILLED)
- P(non-perturbative soliton exists and is accessible) = 10-15% (STILL OPEN, but now known to require truly non-perturbative physics)
- P(9C contributes to AO-1/AO-2 explanation) = 5-10% (requires soliton + low barrier + right signature)

The overall probability has decreased but is not zero. The remaining hope is entirely in the non-perturbative sector.

---

## Appendix A: Key Equations Reference

**5D metric:**
    ds^2 = e^{2A(y)} g_{mu nu}(x) dx^mu dx^nu + dy^2

**Kinetic variable:**
    X = X_4 + X_5,  X_4 = (1/2)e^{-2A} g^{mn} d_m phi d_n phi,  X_5 = (1/2)(phi')^2

**Cuscuton:**
    P(X) = mu^2 sqrt(2X),  P_X = mu^2/sqrt(2X),  P_XX = -mu^2/(2X)^{3/2}

**Generalized Hamiltonian constraint:**
    F[6(A')^2 - (1/2)e^{-2A}R_4] + xi[e^{-2A}Box_4(phi^2) + 8A'phi phi']
    = -mu^2 sqrt(2X)(X_4/X) + V + Lambda_5

**Israel junction (IR brane with EM):**
    [K_{mn}] - [K]h_{mn} = -(1/F_c)(sigma h_{mn} + S^{EM}_{mn} + S^{CS}_{mn})

**Static cuscuton response:**
    delta phi / phi_bg ~ xi G_4 rho_EM R^2 ~ 10^{-32}

**Gravitational modification:**
    delta G/G ~ xi (delta phi/phi_bg) ~ 10^{-35}

**KK mass gap:**
    m_1 ~ k e^{-ky_c} ~ 10 eV  (f ~ 10^{16} Hz)

**Meridian parameters:**
    M_5 = 10^8 GeV,  ky_c = 39.56,  zeta_0 = 0.038,  xi = zeta_0 M_Pl^2/phi_bg^2

---

## Appendix B: Comparison to D1.3 (FRW Equations)

| Feature | D1.3 (Cosmological) | D9.7 (Local) |
|---------|---------------------|---------------|
| 4D metric | eta_{mn} (Minkowski) | g_{mn}(x) (general) |
| R_4 | 0 | Non-zero (sourced by EM) |
| phi dependence | phi(y) only | phi(x, y) |
| X_4 | 0 | (1/2)e^{-2A}(d_r phi)^2 |
| Kinetic cancellation (55) | EXACT: T^P_{55} = V + Lambda | BROKEN: extra term -mu^2 sqrt(2X) X_4/X |
| Scalar constraint | Algebraic in A'', phi | Elliptic PDE in (r, y) |
| Junction conditions | Algebraic | Include S^{EM}_{mn} and S^{CS}_{mn} |
| Gravitational modification | 0 (flat background) | delta G/G ~ 10^{-35} |

---

## Deliverable Checklist

- [x] D9.7.1: Full 5D equation system without FRW symmetry (Section 2, Task 9C.1)
- [x] D9.7.2: Static solutions with EM source (Section 3, Task 9C.2)
- [x] D9.7.3: Dynamic solutions and resonance analysis (Section 4, Task 9C.3)
- [x] D9.7.4: Kill condition assessment (Section 5)
- [x] D9.7.5: Connection to AO-1 and AO-2 (Section 6)
- [x] D9.7.6: Honest assessment of what survives (Section 7)
- [x] D9.7.7: Key equations reference (Appendix A)
- [x] D9.7.8: Comparison to D1.3 (Appendix B)

---

*The local cuscuton is rigid. The X = 0 singularity is a wall, not a door. Every perturbative mechanism for local gravitational modification through laboratory EM fields is killed by 28-77 orders of magnitude. The surviving channels are purely non-perturbative: solitons, domain walls, topological transitions. Tasks 9C.4-9C.5 will determine if those doors are real or painted on the wall.*

*D9.7 — Clayton & Clawd, March 16, 2026*
