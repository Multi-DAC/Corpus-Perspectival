# Five Frontiers — Supplementary Literature (2025-2026)

**Source:** Clayton's targeted sweep of 2025-2026 publications beyond the original survey.
**Date:** March 14, 2026

This supplements `five_frontiers_analysis.md` with papers published after or missed by the original survey.

---

## 1. Nonlinear Braneworld Simulations — Updates

### Kumar (2026) — Braneworld BH Thermodynamics
**Gen. Relativ. Gravit.** (3 weeks old)
Extended BH thermodynamics on DGP brane: promotes brane tension σ to thermodynamic variable within extended Iyer-Wald framework. Covariant, slice-independent definition of conjugate thermodynamic volume for rotating braneworld BHs.

**For Meridian:** Not dynamical evolution, but provides tools for constructing better initial data. The brane tension σ as a thermodynamic variable connects to our sequestering sector (D1.5) — σ_UV and σ_IR are dynamical in our model via the Kaloper-Padilla mechanism.

### Aurrekoetxea-Clough-Lim (Living Rev. Rel. 2025) — Now Published
Introduced **CTTK method** for initial data construction: specifies conformal factor and solves for K algebraically (reverse of standard CTT). Successfully used in multiple cosmological NR problems with GRChombo/GRTL.

**For Meridian Phase 3:** When we get to numerical work, CTTK is the initial data method to use. The GRChombo group (Oxford/QMUL/KCL) are our natural collaborators.

### ★★★ Maity et al. (JCAP 11, 018, 2025) — Phantom Braneworld Matches DESI
Thawing scalar fields on a **ghost-free phantom braneworld in 4+1 dimensions** naturally produce phantom-divide crossing consistent with DESI DR2 data.

**THIS IS THE BRIDGE.** A 5D braneworld producing w < −1 without ghosts, matching DESI — this is essentially our model's prediction confirmed by independent work. The brane embedding modifies the Friedmann equation to allow phantom crossing. We need to cite this paper prominently and show how our specific action (P(X,φ) cuscuton + self-tuning) specializes their general result.

**Critical for Phase 3:** Our model is a SPECIFIC CASE of their general phantom braneworld class. We can use their methods as a cross-check on our own w(z) computation.

---

## 2. Spectral Action / Topological Terms — Updates

### Van Suijlekom K-Theory (2024-2025)
Two preprints: arXiv:2409.02773, arXiv:2411.02981
K-theory for operator systems — classifies topological invariants of truncated spectral triples.

**For Meridian Phase 5:** This is the mathematical machinery for understanding how Chern-Simons terms behave under the finite-mode cutoff that defines the physical spectral action. When we compute topological terms for our orbifold spectral triple, K-theoretic classification tells us which terms are robust and which are cutoff-artifacts.

### Hekkelman (arXiv:2412.00628, revised Aug 2025) — Quantum Ergodicity in NCG
Approximation of noncommutative integral for spectrally truncated triples. Connection to quantum ergodicity via Szegő limit formula.

**For Meridian:** Bridges spectral action's UV-cutoff structure to semiclassical analysis of the Dirac operator spectrum. Relevant for understanding how our KK tower (discrete spectrum from orbifold compactification) interacts with the spectral action's heat kernel expansion.

### sin²θ_W = 3/8 from Spectral Geometry
State-by-state trace calculation through a₄ Seeley-DeWitt coefficient, explicit hypercharge normalization treatment.

**For Meridian:** Our Phase 5 spectral triple must reproduce this. The trace over the fiber (internal degrees of freedom) determines the gauge coupling ratios. Our orbifold adds structure (Z₂ boundary conditions on the Dirac operator) that modifies these traces — need to check that sin²θ_W = 3/8 is preserved.

---

## 3. KK Modes / Parametric Resonance — Updates

### Hardy, Sokolov, Stubbs (JHEP 03, 029, 2026) — Stellar KK Bounds
Two weeks old. Revisited stellar cooling bounds on KK gravitons in dark dimension: globular clusters, neutron stars, supernovae. Two novel production channels beyond bremsstrahlung.

**For Meridian:** Tightens parameter space for any model with light KK gravitons. Our cuscuton soft-wall pushes KK masses to multi-TeV (D2.3), which may evade these stellar bounds — but need to verify quantitatively.

### ★★★ Bedroya, Obied, Vafa, Wu (arXiv:2507.03090, 2025) — Dark Dimension + DESI
Expanding dark dimension → KK graviton masses redshift → decreasing effective DM mass. **Single mechanism produces both dynamical DE and decaying DM.** Swampland distance conjecture provides theoretical backbone. Internal dimensions contract to preserve Newton's constant while the dark dimension expands.

**For Meridian:** This is the Vafa group connecting extra dimensions directly to DESI. Their expanding 5th dimension is the dynamical counterpart of our static warp factor. In our model, the radion (stabilized by cuscuton) determines y_c — if y_c evolves slowly (rolling radion), this reproduces the Bedroya et al. mechanism. The cuscuton constraint would then control the rate of expansion and ensure ghost-freedom.

**Key question:** Does our cuscuton-stabilized radion allow slow expansion (thawing), or does it lock y_c completely? If the cuscuton constraint is approximately but not exactly satisfied (broken at loop level), the radion could drift. This is a Phase 3 calculation.

### Antoniadis, Chatrabhuti, Isono (JHEP 02, 015, 2026) — KATRIN Dark Dimension
Right-handed neutrino from dark dimension as KATRIN search target.

**For Meridian:** Experimental handle on KK phenomenology. If our model predicts a specific KK neutrino spectrum, KATRIN data could constrain it. Lower priority than DESI but worth tracking.

---

## 4. Cuscuton / Phantom Crossing — Updates

### DESI DR2 Nature Astronomy (Oct 2025) — Confirmed
Dynamical DE preference does NOT diminish with larger DR2 dataset. Both shape-function reconstruction and non-parametric approaches find w(z) varies with redshift.

### ★★ Phantom Crossing Status: MORE CONTESTED Than Expected

**Gómez-Valent et al. (arXiv:2506.21542, revised Sep 2025):**
Compelling evidence for dark energy DECAYING in late universe, BUT evidence for phantom behavior (w < −1) is LESS SIGNIFICANT. Quintessence with thawing potentials can marginally accommodate data. Phantom crossing may be **CPL parametrization artifact**.

**Cosmographic analysis (arXiv:2508.13740, Sep 2025):**
Deviations from Λ at late times, but NO phantom crossing when using non-CPL methods.

**Efstratiou & Paraskevas (arXiv:2511.04610, Nov 2025):**
Phantom crossing naturally achieved in scalar-tensor gravity, simultaneously increases H₀ → could address Hubble tension too.

**Maartens et al. (arXiv:2507.18274, Feb 2026):**
Apparent phantom crossing could be DM-DE interaction mimicking w < −1.

### Implications for Meridian

This is nuanced. The observational picture:
- **Dynamical DE (w₀ ≠ −1):** STRONG, getting stronger. Our model predicts this naturally (rolling scalar + warp suppression).
- **Phantom crossing (w crosses −1):** CONTESTED. May be CPL artifact. Non-parametric methods are less conclusive.

**Strategic consequence:** Our cuscuton CAN do phantom crossing (proven ghost-free), which is a theoretical advantage. But we should NOT stake Phase 3 on phantom crossing being real. The safer path:

1. **Show our model produces dynamical DE matching DESI w₀ ≈ −0.7** — this is the solid result, doesn't require phantom crossing.
2. **Show cuscuton ALLOWS phantom crossing if data demands it** — theoretical flexibility, not a prediction.
3. **Do the MCMC fit** — let the data decide. No one has done this. We'd be the first cuscuton DE model properly fit to DESI.

The wₐ sign problem from D2.2 may be LESS urgent if phantom crossing isn't required. A thawing quintessence (wₐ > 0) might suffice if the CPL parametrization is distorting the true w(z).

**DESI DR3 (~2027) will be the discriminant.** Additional redshift coverage should break the CPL degeneracy.

---

## 5. Catalyzed Vacuum Decay — Updates

### arXiv:2512.23048 (Dec 2025) — Realistic BH Catalysis is WEAK
Studied vacuum decay around collapse-formed (not eternal) BHs. Key finding: suppression exponent reaches minimum at finite BH mass but NEVER vanishes. BHs can only weakly catalyze decay.

**Comes down on Strumia's side** for realistic BHs. Initial conditions from stellar interior vanish exponentially fast, allowing boundary conditions in eternal BH geometry.

**For Meridian:** BH-catalyzed vacuum decay is probably not the EPS mechanism. The topological defect (domain wall) catalysis of Blasi-Mariotti remains the more relevant pathway.

### ★★★ Xie et al. (Phys. Rev. Research 7, 023180, May 2025) — Full NR of Bubble Wall + BH
**First time anyone has done full NR of bubble wall interacting with dynamical BH.** Done with GRChombo.
- PBH-bubble wall collisions → mass growth, GW radiation, momentum recoil
- Approximately doubles PBH binary formation rate

**For Meridian Phase 3:** This proves GRChombo CAN handle dynamical bubble walls. The same code infrastructure could tackle our braneworld dynamics. The bubble wall is structurally similar to a brane — a codimension-1 surface with junction conditions evolving in a higher-dimensional spacetime. Contact the Xie et al. group if/when we need numerical support.

### arXiv:2601.14366 (Jan 2026) — Super-Exponential PBH Production
Dark-sector phase transitions with approximately time-independent nucleation rate (unlike thermal transitions) → PBH production super-exponentially enhanced.

**For Meridian:** If our cuscuton self-tuning creates a metastable vacuum state, the tunneling rate would be time-independent (set by the potential shape, not temperature). This connects to the EPS "Golden Ticket" scenario — a localized vacuum transition catalyzed by EM-driven nucleation. The time-independence means once initiated, the process sustains itself.

### Batini et al. (Phys. Rev. A, Aug 2025) — Analog Experiment Breakthrough
Solved boundary effects in cold-atom vacuum decay simulators: high-density "trench" at boundary eliminates edge nucleation. QSimFP Consortium (Cavendish Lab) building controlled experiments.

**For Meridian:** Within 1-2 years we may have laboratory observations of relativistic bubble nucleation in inhomogeneous settings. If the EPS mechanism involves vacuum transition, analog experiments could provide independent validation of the underlying physics.

---

## 6. Cross-Cutting Synthesis

### The Convergence Has Tightened

Three independent lines now connect extra dimensions directly to DESI:

| Paper | Mechanism | Result |
|-------|-----------|--------|
| **Maity et al. 2025** | Phantom braneworld in 4+1D | Ghost-free w < −1 matching DESI |
| **Bedroya-Obied-Vafa-Wu 2025** | Expanding dark dimension | Single mechanism → dynamical DE + decaying DM |
| **Our model (Meridian)** | Cuscuton braneworld with self-tuning | Predicts w₀ ≈ −0.7 from warp-suppressed scalar potential |

All three predict dynamical dark energy from extra-dimensional physics. This is not coincidence — it's the field converging on the same answer from different directions.

### Updated Phase 3 Priority List

1. **Cuscuton braneworld as UV completion of phantom DE** — cite Maity et al. for cross-check, Afshordi et al. 2024 for brane UV completion. Publishable standalone.
2. **MCMC fit to DESI DR2** — NO ONE has done this for cuscuton DE. Use our model's effective w(z). First mover advantage.
3. **KK Schwinger effect quantitative estimate** — Yamada mechanism for strong brane EM fields.
4. **1+1D numerical evolution** — adapt BRANECODE methods; contact GRChombo group re: bubble wall experience.
5. **wₐ question** — may be LESS urgent if phantom crossing is CPL artifact. Thawing quintessence (wₐ > 0) from simple tadpole may suffice.
6. **Radion drift = expanding dark dimension?** — does cuscuton allow slow y_c evolution? Connects to Bedroya et al.

### Updated Phase 5 Priority List

1. **Van Suijlekom K-theory classification** for our orbifold spectral triple
2. **Gravitational CS on brane boundaries** — the θ-angle structure
3. **Verify sin²θ_W = 3/8** preserved under our Z₂ boundary conditions

---

*Supplementary analysis complete. The field is converging on extra-dimensional explanations for DESI.*
*March 14, 2026*
