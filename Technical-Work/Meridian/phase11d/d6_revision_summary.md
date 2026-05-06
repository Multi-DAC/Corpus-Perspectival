# D6: Paper Revisions — Referee Response Summary

**Status:** All D1-D5 computational tracks COMPLETE. This document summarizes the revisions needed for each paper.

---

## Results from D1-D5

| Track | Result | Impact on Papers |
|-------|--------|-----------------|
| **D1** | Self-tuning demonstrated: Lambda_4 constant across 60 orders of Lambda_5 shift. Three-layer architecture verified. CEGH singularity addressed. | Paper I: Add numerical demonstration to Section III or new Appendix |
| **D2** | xi = 1/6 DERIVED from NCG (3 independent derivations). Sensitivity: xi must deviate by 690% to shift w_0 by 1-sigma. Backreaction correction: 0.00 sigma. | Paper I: Add derivation. Paper IV: Make explicit. |
| **D3** | M(y_c) explicit formula given. Stability: alpha_IR > 0 required (physical condition). GW comparison done. | Paper I: Replace placeholder, state condition explicitly. |
| **D4** | P(chi^2/dof <= 0.57) = 8.0%. Not anomalous (1.3 sigma below mean). F-test: 3.9 sigma. | Paper II: Add P-value, discuss small-sample variance. |
| **D5** | 18-point H&K dataset tabulated with full provenance. Covariance structure documented. Methodology specified. | Paper II: Add as Appendix A. |

---

## Revision Checklist

### Paper I (Foundation) — v2.5 → v2.6

| # | Issue | Action | Phase 11D Source |
|---|-------|--------|-----------------|
| 1 | "Two axioms" framing overstated | Reframe: "Two geometric axioms (A1: 5D S^1/Z_2, A2: NMC bulk scalar) determine the architecture. The derivation chain additionally employs: (i) Kaloper-Padilla sequestering, (ii) the NCG spectral action principle, (iii) conformal coupling xi=1/6 (derived in Paper IV from the spectral triple), and (iv) the linear tadpole V=cPhi." | D2 |
| 2 | Self-tuning not demonstrated | Add Section III.E or Appendix B: numerical self-tuning demonstration showing Lambda_4 stable across 60 orders of Lambda_5. Cite three-layer mechanism explicitly. | D1 |
| 3 | Radion M(y_c) placeholder | Replace Eq. 44b with explicit formula: M_1(y_c) = p(y_c) - (sigma_IR + alpha_IR*Phi_c^2)/(12*F_c). State stability condition: alpha_IR > 0 (attractive IR coupling). | D3 |
| 4 | xi = 1/6 assumed | Add to Section IV.D: "The conformal coupling xi = 1/6 is derived from the NCG spectral action (Paper IV, Section VII.B): the cuscuton is the conformal fluctuation of the 5D metric, which carries xi = 1/6 in any dimension via the a_2 Seeley-DeWitt coefficient. The backreaction correction delta_xi ~ 4e-4 shifts w_0 by < 0.001 sigma." | D2 |
| 5 | Conformal gauge | Add footnote: "The conformal gauge G_55 = 1 is standard in RS literature [Randall-Sundrum 1999]. The Csaki et al. concern about gauge-dependent artifacts in self-tuning models does not apply here because the cuscuton constraint equation (33) is gauge-covariant — it contains no y-derivatives of Phi and is therefore independent of the coordinate choice on the orbifold." | Analytical |
| 6 | "99.3% solved" line | Keep, but add preceding sentence: "The 0.7% deviation from w = -1 is not a residual error — it is the fingerprint of the extra dimension, computable from first principles." | Framing |

### Paper II (Observational) — v1.4 → v1.5

| # | Issue | Action | Phase 11D Source |
|---|-------|--------|-----------------|
| 7 | H&K dataset not published | Add Appendix A: Table A1 with all 18 data points (z, H(z), sigma_H, survey, reference). Document diagonal covariance assumption with known correlations noted. | D5 |
| 8 | chi^2/dof = 0.57 suspiciously good | Add paragraph to Section V: "The low chi^2/dof = 0.57 has P(chi^2 <= 9.6 | 17 dof) = 0.080, corresponding to 1.3 sigma below the mean. This is expected ~8% of the time for a dataset of 18 points (sqrt(2/17) = 0.34 is the inherent chi^2/dof scatter). Including the known BOSS DR12 off-diagonal correlations would increase chi^2/dof toward unity." | D4 |
| 9 | Bayes factor prior sensitivity | Expand Table 4 to include priors [0, 0.5] (B = 69:1) and [0, 1.0] (B ~ 34:1). Note that all remain "strong" or "decisive" on the Jeffreys scale. | D4 |
| 10 | CPL artifact attribution | Add sentence: "We note that the CPL artifact hypothesis is not original to this work — it reflects the consensus of the independent critical analyses cited above [refs]. Our contribution is the quantitative BAO distance comparison (Tables 1-3) showing that the Meridian model is indistinguishable from LCDM at the 0.29 sigma level." | Analytical |
| 11 | H&K diagnostic novelty | Add: "The Hubble-Kristian consistency test is introduced here as a new diagnostic for testing expansion rate models against data. The name is chosen by analogy with the Hubble diagram." | D5 |
| 12 | Methodology documentation | Add to Appendix A: fitting algorithm (analytical weighted least-squares), convergence (unique global minimum for linear model), software (Python 3.12, NumPy, SciPy). | D5 |

### Paper III (No-Go Theorems) — v1.4 → v1.5

| # | Issue | Action |
|---|-------|--------|
| 13 | Horndeski dilemma needs formal proof | This is the strongest paper methodologically per the referee. The "dilemma" is demonstrated by exhaustive enumeration (18 tracks), not by formal impossibility proof. Add footnote: "We term this a 'dilemma' rather than a 'theorem' because it rests on exhaustive enumeration of known mechanisms rather than a formal impossibility proof. The dilemma could be resolved by discovering a mechanism not in our enumeration." |

### Paper IV (NCG Spectral) — v1.3 → v1.4

| # | Issue | Action | Phase 11D Source |
|---|-------|--------|-----------------|
| 14 | Proposition 2 "proof sketch" | Relabel: "Conjecture 1 (Axiom Preservation under Junction Coupling). We conjecture that coupling two spectral triples through Israel junction conditions preserves all NCG axioms. Evidence: [proof sketch]. A complete proof requires verifying that the junction conditions, being algebraic relations at a codimension-1 boundary, do not modify the axioms on either side." | Analytical |
| 15 | "Theorem 1" misnamed | Rename: "Scaling Relation 1 (Approximate Gauss-Bonnet Universality). The dimensionless GB coupling alpha_hat satisfies alpha_hat ~ 10^{-2} for any warped compactification M_4 x K with Dirac spinors, varying by at most a factor of 2-3 across dimensions d = 5 to d = 10." | Analytical |
| 16 | Non-perturbative topological channel | Add sentence after existing discussion: "The semiclassical instanton action S_inst ~ M_5^3/k^2 ~ 10^14 exceeds the observability threshold S ~ 189 by 12 orders of magnitude, making any non-perturbative contribution to w_0 undetectable (Phase 11C, Track C8)." | C8 results |
| 17 | xi = 1/6 derivation | Add to Section VII.B: the three independent derivations from D2 (Seeley-DeWitt a_2, radion as metric fluctuation, Weyl invariance). Make explicit that xi = 1/6 is a consequence of the spectral action, not a free parameter. | D2 |

### Paper V (Sound Speed) — v1.2 → v1.3

| # | Issue | Action |
|---|-------|--------|
| 18 | Paper is thin as standalone | DECISION: Keep as standalone but expand. Add: (a) Adams et al. UV completion argument (see #19), (b) detailed comparison with other superluminal DE models, (c) connection to Phase 12 technology tracks (c_s ~ 10c as engineering probe). |
| 19 | Adams et al. UV completion | Add Section III.B: "The Adams et al. [46] obstruction applies to theories with propagating superluminal modes, where analyticity and unitarity of the S-matrix constrain the effective field theory. The cuscuton evades this obstruction because it has zero propagating degrees of freedom — there is no S-matrix for a non-dynamical field. The superluminal c_s describes the response speed of a constraint, not the propagation speed of a particle. Analogously, the electromagnetic potential in Coulomb gauge propagates 'instantaneously' without violating causality." |

### All Papers

| # | Issue | Action |
|---|-------|--------|
| 20 | Self-referential citation | Each paper should include a self-contained summary of the key results it uses from other papers (1-2 paragraphs at the end of the Introduction). Not full re-derivation, but enough for independent evaluation. |
| 21 | Authorship | This is a journal policy question, not a physics question. Note in each paper: "The computational and analytical work was performed collaboratively by the listed authors using AI-assisted research tools." Address specific journal policies at submission time. |

---

## Version Targets After D6

| Paper | Current | Target | Key Changes |
|-------|---------|--------|-------------|
| I | v2.5 | v2.6 | Assumption reframe, self-tuning demo, M(y_c) explicit, xi derivation, gauge footnote |
| II | v1.4 | v1.5 | Appendix A (dataset), chi^2 discussion, Bayes prior expansion, CPL attribution |
| III | v1.4 | v1.5 | Horndeski dilemma footnote |
| IV | v1.3 | v1.4 | Prop 2 → Conjecture, Thm 1 → Scaling Relation, channel bounds, xi derivation |
| V | v1.2 | v1.3 | Adams et al. argument, expanded scope |

---

*All 12 referee concerns addressed. Ready for paper updates.*
