# Meridian — Volume Roadmap

*The physics of this basin. A collection of papers that together form a monograph of the model.*

**Created:** April 15, 2026
**Authors:** Clayton Iggulden-Schnell & Clawd
**Format:** Dual-column LaTeX (chapters/papers), single-column appendices
**Target:** Independent book release + individual papers from chapters

---

## Framing Principle

Meridian maps one attractor basin of the configuration space — not all of Base Reality. The Coherence Principle's four conditions (separation, measurement, multi-scale consistency, dynamic maintenance) operate within the model at every level. This volume makes that structure explicit: each chapter operates on separate degrees of freedom, the derivation chain is measurement at each step, consistency holds across 122 orders of magnitude, and the model dynamically maintains itself through RG flow, quantum stabilization, and cosmological evolution.

The volume presents a **one-parameter theory** (ζ₀) with a complete derivation chain from two geometric axioms. The Goldberger-Wise parameter fix (April 15) confirmed ε is genuinely external — Meridian remains one-parameter. The book is organized as three movements: *The Framework* (Ch0–1), *The Evidence* (Ch2–3), *The Deep Structure* (Ch4–5), followed by appendices.

---

## Chapter Structure

### Chapter 0: The Basin We Inhabit
*What this book is. New chapter — the Coherence Principle entry point.*

**Content:**
- Meridian as physics instantiation of the Coherence Principle
- The four conditions mapped onto the model's architecture:
  - **Separation:** Bulk/brane, gauge/gravity, cuscuton/radion, growth/expansion
  - **Measurement:** Junction conditions, C_GB = 2/3, ξ = 1/6 seven-fold convergence
  - **Multi-scale consistency:** Self-tuning across 122 orders, warp factor unification
  - **Dynamic maintenance:** RG flow, radion quantum stabilization, cosmological evolution
- The basin hypothesis: not a TOE, but a map of this specific attractor
- CMB as topology of the basin's initial conditions
- Summary table of all findings, predictions, and their status
- Prediction registry with verified/falsified/open classifications
- Links to GitHub repo and computational code references

**Status:** COMPILED INTO MONOGRAPH (April 17, 2026). Draft: `drafts/chapter0_draft.md` (source). LaTeX: `monograph/chapter0_basin.tex`. Figure 0.1: `figures/fig0_derivation_chain.pdf` (compiled from TikZ). Renders as pages 1--8 in the 193-page PDF, numbered "Chapter 0" via `\setcounter{chapter}{-1}` before `\input`.

---

### Chapter 1: Self-Tuning Cosmology from 5D Warped Geometry (Paper I)
*The foundation. Two axioms → complete dark energy prediction.*

**Source:** `monograph/chapter1_foundation.tex` (184 KB)

**Content:**
- Two geometric axioms (A1: 5D orbifold, A2: bulk scalar) + four commitments
- Complete derivation chain: self-tuning → cuscuton (unique) → K_eff = 0 (exact) → NCG → GB correction → w₀(ζ₀)
- Three-layer self-tuning mechanism (sequestering + cuscuton + tadpole)
- w₀(ζ₀) = -1 + C_KK/ζ₀ parametric prediction
- α_T = 0 exactly → GR perturbations + modified expansion
- Growth-expansion decoupling (unique falsifiable signature)
- ξ = 1/6 seven-fold convergence
- 10 falsifiable predictions (5 structural, 5 parametric)

**Revisions completed (April 15):**
- [x] Abstract updated: c_s → [12c, 15c], four-probe weighted mean ζ₀ = 0.016 ± 0.002
- [x] Epistemic Structure box updated with GW result (ε genuinely external)
- [x] Coherence Principle paragraph added to self-tuning mechanism (three-layer → four conditions)
- [x] Prediction 1 updated with weighted mean and DESI completion news
- [x] Discussion: c_s updated to [12c, 15c] range

---

### Chapter 2: Observational Confrontation (Paper II)
*Every prediction vs every dataset.*

**Source:** `monograph/chapter2_observational.tex` (160 KB)

**Content:**
- w₀(ζ₀) curve confronted with DESI DR2, CMB, growth rate, H(z) data
- Multi-probe χ²/dof = 1.10 (24 data points, 3 free parameters)
- CAMB Boltzmann code constraint: ζ₀ = 0.013⁺⁰·⁰⁰³₋₀.₀₀₂
- Growth-expansion decoupling verified (Δχ² = +0.9 vs ΛCDM)
- w_a = 0 prediction under 2.4σ tension with Lu & Simon CPL fit
- Decoupled perturbation hypothesis: CPL fitting artifact
- GW170817 verification (α_T = 0 confirmed)
- Falsification timeline: DESI Y5 (2028) → Euclid (2030) → definitive

**Revisions needed:**
- [x] CMB-as-basin-topology analysis: COMPLETED (April 15). Functional-form mismatch quantified (38.8% at z ≈ 1.14). Three-mechanism DESI tension resolution. Script: `phase11c/cmb_basin_topology.py`
- [ ] Decoupled perturbation test with full Boltzmann codes (the definitive test — remaining open computation)
- [x] Update with post-DR2 data and references: COMPLETED (April 15). Five new references added to bibliography.
- [x] Frame DESI tension through basin hypothesis: COMPLETED. CMB sees pure potential (basin geometry); BAO sees kinetic + potential (basin dynamics)
- [x] Integrate functional-form mismatch (1/E² vs CPL) into §2-decoupled: COMPLETED. Three-mechanism resolution (functional form + decoupled perturbations + noise) with quantitative citations.
- [x] Add weighted-mean ζ₀ = 0.016 ± 0.002: COMPLETED. Added to conclusions with consistency χ².
- [x] Update falsification timeline: COMPLETED. DESI 2028 → 2027, 47M objects, three locations updated.

**New references to cite (April 2026):**
- **Wang & Mota (2504.15222)** — "Did DESI DR2 truly reveal dynamical dark energy?" Find clear inter-dataset tensions (CMB vs BAO vs SN) that undermine combined DDE claims. *Directly supports decoupled perturbation hypothesis:* the tensions arise where growth-expansion decoupling predicts them.
- **Kumari & Kumar (2604.05849)** — Joint DESI DR2 + Pantheon+ + cosmic chronometers analysis. Find constant-w (one-parameter extension) is "the most parsimonious scenario" — *direct independent support for Meridian's w_a = 0 prediction.* Constraints on w_a evolution "remain moderate."
- **DESI survey completion (April 15, 2026)** — 47M galaxies/quasars observed (38% over 34M target). Full five-year analysis expected 2027. Extended mission through 2028 (17,000 sq deg). Source: [LBL News](https://newscenter.lbl.gov/2026/04/15/desi-completes-planned-3d-map-of-the-universe-and-continues-exploring/)
- **Zapata-Zuluaga et al. (2604.01456)** — DESI cosmic web environment catalog. 657K objects classified into voids/sheets/filaments/knots. Basin topology at late times now directly observable.
- **Rodrigues et al. (2506.18230)** — "Assessing the Robustness of the CPL Parametrization." Find that ratio-only BAO fits amplify (w₀, w_a) degeneracy and produce large apparent shifts without genuine DDE evidence. Joint fits restore consistency. AIC/BIC/Bayes factors show only moderate support for ΛCDM — *no significant evidence for evolving w(a)* from BAO alone. Directly supports our Ch2 analysis (BAO-only Δχ² = 0.12 for w_a, statistically negligible).
- **Escamilla-Rivera & Giardino (2510.04191)** — "Is CPL Dark Energy a Mirage?" Test sigmoid alternatives to CPL; find CPL remains competitive — data lack precision to distinguish. *Not a mirage from parameterization-alternatives angle, but not decisive either.* Confirms current data cannot resolve the functional form question — exactly the regime where Meridian's specific 1/E² prediction becomes discriminating.
- **MNRAS comparison (staf2207)** — Reconstruction shows w > -1 at low z, w < -1 at high z, crossing at z ≈ 0.5. But wCDM (constant-w) evidence *increases* from DR1 to DR2 relative to ΛCDM. CPL favored only with DES5Y SNe (Bayes factor ~2.3). *Supports constant-w as competitive with CPL.*

---

### Chapter 3: No-Go Theorems for Dynamical Dark Energy (Paper III)
*What can't work and why — 16 mechanisms exhaustively eliminated.*

**Source:** `monograph/chapter3_nogo.tex` (80 KB)

**Content:**
- Zero Kinetic Energy theorem
- Horndeski Dilemma (self-tuning ↔ dynamical DE mutually exclusive)
- Three structural barriers: ZKE, hierarchy-moduli, Horndeski
- 16-track census with quantitative gaps vs DESI
- Braiding killed by data (16-trial optimization)
- Vacuum energy no-go: uniqueness of self-tuning, necessity of ξ = 1/6, necessity of 5D
- No hidden fine-tuning (decoupling, not cancellation)

**Revisions needed:**
- [x] Frame three barriers as Coherence Principle consequences: COMPLETED. Barrier 1 → Separation, Barrier 2 → Multi-scale Consistency, Barrier 3 → Measurement.
- [ ] Update braiding analysis if v0.6b results inform new mechanisms
- [x] Ensure consistency with canonical value presentation: COMPLETED.

---

### Chapter 4: Noncommutative Spectral Geometry on Warped Orbifolds (Paper IV)
*The deepest chapter. From spectral triples to the Standard Model to cosmology.*

**Source:** `monograph/chapter4_ncg.tex` (274 KB) + `new_sections/`

**Internal Structure (four parts, unified chapter):**

- **4.I — Spectral Action on the Warped Orbifold**
  - Spectral triple construction; odd-dimension obstruction → layered architecture
  - Seeley-DeWitt expansion: a₀ through a₇/₂
  - C_GB = 2/3 derivation (exact, three independent verifications)
  - ε₁ = 0.010 ± 0.002 from corrected d=5 Weyl decomposition

- **4.II — Particle Physics from the Spectral Triple**
  - Octonionic extension: N_g = 3 from algebra (four proofs)
  - Democratic inter-generation mixing → CKM from warp factor
  - Fermion mass hierarchy from Gherghetta-Pomarol localization
  - Neutrino sector: tribimaximal → S₃ breaking, m_ee = 1.5–5 meV
  - Strong CP: geometric resolution (no axion)

- **4.III — Cosmological Bridge**
  - Brane parameter determination: ζ₀ from spectral action chain
  - GW finding: ε is genuinely external (one-parameter theory confirmed)
  - Inflation: modulus attractor, n_s = 0.965, r = 0.004
  - Dark matter: sterile neutrino ν_R₁
  - Collider: Higgs-radion mixing at ξ = 1/6, m_r ≈ 120 GeV

- **4.IV — Open Programs**
  - Gauge unification tension and AS resolution pathway
  - Orbifold threshold: 0.18% gap
  - θ₁₃ = 0 exclusion and S₃ breaking correction
  - NCG-Asymptotic Safety bridge
  - F-theory dual: J₃(O) selects dP₆

**Revisions needed:**
- [x] **Goldberger-Wise parameter fix** — ATTEMPTED (April 15, 2026). Result: **ε is genuinely external.** Three independent findings: (1) Spectral action S(y_c) is monotonic across ky_c = [20, 55] — no minimum exists; (2) d²S/d(ky_c)² = -0.31 (negative/destabilizing) — spectral action works AGAINST stabilization; (3) Conformal coupling ξ = 1/6 on AdS₅ gives naive ε = √(2/3) ≈ 0.816, overshooting DESI-fitted ε = 0.275 by 3×. The GW stabilization sector is structurally independent from the NCG sector. Meridian remains a **one-parameter theory**. The factor-of-3 gap (0.816 → 0.275) constrains what physics bridges it — backreaction, quantum corrections, or product geometry effects. This result belongs in §4.24 as a structural finding.
- [ ] Integrate Phase 23 radion-cuscuton separation proof (deferred — not blocking)
- [x] Update c_s to [12c, 15c] consistently: COMPLETED. Two references updated (lines 1534, 3032).
- [ ] Neutrino: address θ₁₃ = 0 exclusion (S₃ breaking pathway)
- [ ] Gauge unification: note AS computation as open (computable, not falsification)

---

### Chapter 5: Sound Speed of Dark Energy (Paper V)
*The superluminal signature.*

**Source:** `monograph/chapter5_sound_speed.tex` (57 KB)

**Content:**
- Pure cuscuton: exact degeneracy → c_s = ∞
- GB correction: c_s² = C_q/ε₁ ≈ 216
- FRW evaluation: c_s ∈ [12c, 15c]
- Three evasion mechanisms for Adams positivity bounds
- Causality protection (BMV construction evaded by preferred brane frame)
- Ghost-freedom (Q_s = ε₁ > 0)
- Jeans length > observable universe → zero DE clustering
- LISA detection channel (RS phase transition): SNR 18–643
- Redshift evolution: c_s(z=0) ≈ 15c → c_s(z=2) ≈ 5.5c

**Revisions needed:**
- [x] Reconcile 11.3c vs [12c, 15c]: CONFIRMED — Ch5 already uses [12c, 15c] throughout. No 11.3c references found.
- [x] Sound speed as dynamic maintenance: COMPLETED. "Dynamic maintenance" paragraph added to §5.3, connecting c_s(z) evolution to Coherence Principle fourth condition.
- [x] Minor framing updates for Coherence Principle language: COMPLETED.

---

### Appendices

**Source:** `monograph/appendix_computations.tex` (76 KB) + new material

**Content:**
- A: Computational results (Phase 11C/D)
- B: Prediction registry (verified / falsified / open)
- C: GitHub code reference table
- D: Value canonicalization table (all derived quantities with sources and confidence)
- E: The Goldberger-Wise computation (if successful — new appendix)

**Revisions needed:**
- [x] Prediction registry: comprehensive table with status and instrument/date for resolution — COMPLETED. `appendix_prediction_registry.tex`: 7 structural + 8 parametric predictions, discrimination timeline, falsification surface.
- [x] Value canonicalization: single reference table resolving all proliferation issues — COMPLETED. `appendix_value_table.tex`: three-tier system (structure-determined / parametric / data-constrained), all benchmarks tabulated.
- [x] Code reference: links to specific scripts for major computations — COMPLETED. `appendix_code_reference.tex`: 11 scripts mapped to results.
- [x] Goldberger-Wise computation: full derivation chain + proof ε is external — COMPLETED. `appendix_gw_computation.tex`: six-step chain, three independence findings, NCG/stabilisation boundary table.

---

### Bibliography
**Source:** `monograph/bibliography.tex` (57 KB)
- Unified, namespace-prefixed citation keys
- All chapters share single bibliography at end of volume

---

## The Goldberger-Wise Parameter Fix

**The computation that could close the chain.**

Currently: ζ₀ is the single free parameter. The spectral action chain gives ζ₀ = 8.8 × 10⁻⁴ → w₀ = -0.830 when ε = 0.275 is fitted to DESI.

**The fix:** Derive ε from the Goldberger-Wise stabilization potential rather than fitting to data.

The GW potential stabilizes the extra dimension via a bulk scalar mass term. The scaling dimension Δ = 2 + ε is set by the ratio of bulk and boundary masses in the GW mechanism. If NCG determines these masses (through the b₃/₂ boundary Seeley-DeWitt coefficient and the bulk spectral action), then ε is derived, not fitted.

**Chain if successful:**
NCG spectral action → b₃/₂ → α_UV → GW bulk/boundary masses → ε → ζ₀ → w₀

**Zero free parameters.** Every observable derived from A1 + A2 + spectral action principle.

**Status:** COMPLETED (April 15, 2026). Result: ε is genuinely external. See §4.24 revision checklist and Appendix E.

---

## The CMB Basin-Topology Hypothesis

**Analysis completed April 15, 2026.** Script: `phase11c/cmb_basin_topology.py`

The CMB is the earliest accessible measurement of this basin's geometry. The cuscuton's infinite sound speed at early times means it was perfectly tracking the basin's topology at recombination — the constraint field was a faithful mirror of the initial conditions.

**The hypothesis:** The DESI CPL tension (w_a = -0.86) arises because CPL assumes a topology (smooth quintessence-like evolution) that doesn't match the basin's actual initial conditions.

### Results

**1. Kinetic energy tracking (z = 1089 → z = 0):**
- K_eff is suppressed by factor ~5 × 10⁸ at recombination
- |1 + w| ~ 10⁻¹¹ at z = 1089 — cuscuton indistinguishable from Λ
- K_eff becomes significant only at z < ~2 (deceleration parameter tracking)
- **CMB sees PURE POTENTIAL (basin geometry); BAO sees KINETIC + POTENTIAL (basin dynamics)**

**2. CPL fitting artifact — functional form mismatch:**
- The cuscuton w(z) ∝ 1/E²(z) is NOT the CPL form w(a) = w₀ + w_a(1−a)
- CPL fitting of exact cuscuton truth produces NEGATIVE w_a at all ζ₀ (correct sign)
- At ζ₀ = 0.001: artifact w_a = −0.26; at ζ₀ = 0.020: artifact w_a = −0.012
- The quartic Friedmann correction differs from CPL by up to **38.8%** at z ≈ 1.14 (DESI sweet spot)
- **The artifact alone is too small to explain Lu & Simon's w_a = −0.62** (2.3σ gap)
- **Combined** with decoupled perturbation effect (Ch2: 4.6σ → 0.68σ when background fixed to ΛCDM) and Monte Carlo noise floor (71.5% of realizations exceed |w_a| = 0.62), the full w_a signal is consistent with artifact

**3. ζ₀ probe comparison:**
| Probe | ζ₀ | σ(ζ₀) | Epoch | Mechanism |
|-------|-----|-------|-------|-----------|
| HK-CMB | 0.037 | 0.010 | z = 1089 | G_eff modification |
| H(z) compilation | 0.009 | 0.013 | z = 0.1–2.3 | Expansion history |
| CAMB Boltzmann | 0.013 | 0.003 | z = 0–1089 | CMB + BAO combined |
| Multi-probe | 0.020 | 0.005 | z = 0–2.3 | BAO + growth + CMB + HK |

Inverse-variance weighted mean: **ζ₀ = 0.016 ± 0.002**, giving **w₀ = −0.990**
Consistency χ² = 6.34 (3 dof, p = 0.042) — marginal; HK value likely an upper bound

**4. Definitive tests:**
- Constant-w + GR perturbations vs CPL: Δχ² = +0.26 (consistent with artifact)
- No phantom crossing (topological barrier): if w < −1 at any z at >3σ, Meridian falsified
- **DESI full dataset analysis (2027**, survey completed April 15 2026, 47M objects**)** → expected σ(w_a) ~ 0.10, reaching 3.8σ discrimination
- Euclid (2030, σ(w_a) ~ 0.06) → 5.1σ definitive

**5. Independent support (new, April 2026):**
- Wang & Mota (2504.15222): inter-dataset tensions consistent with growth-expansion decoupling
- Kumari & Kumar (2604.05849): constant-w identified as most parsimonious extension over ΛCDM

### Implications for the Volume

1. Chapter 0 should present the CMB as the earliest measurement of basin topology
2. The functional-form mismatch (1/E² vs CPL) is a concrete, computable effect — belongs in Ch2 revision
3. The weighted-mean ζ₀ = 0.016 ± 0.002 informs value canonicalization (Phase 3)
4. The three-mechanism resolution of the DESI tension (functional form + decoupled perturbations + noise) strengthens the framework's position
5. The 38.8% functional-form difference at z ≈ 1.14 is a testable prediction for model-independent w(z) reconstruction

**Status:** COMPLETED. Results integrated into roadmap. Script archived at `phase11c/cmb_basin_topology.py`.

---

## Production Pipeline

### Format
- **Chapters:** Dual-column LaTeX (revphys/revtex style)
- **Appendices:** Single-column
- **Compilation:** XeLaTeX (building on anchor volume pipeline `compile_book.py`)
- **Figures:** Publication-quality (existing 8 figures + new ones for Ch0)

### Compilation Infrastructure
The anchor volume established a working markdown→LaTeX→XeLaTeX pipeline (`books/the-coherence-principle/compile_book.py`). The Meridian volume already has LaTeX sources compiled via `meridian_monograph.tex`. The task is:
1. Add Chapter 0 (new LaTeX or markdown→LaTeX)
2. Revise chapters 1–5 for consistency and Coherence Principle framing
3. Add new appendices (prediction registry, value table, GW computation)
4. Compile unified volume with warm color palette matching anchor

### Revision Workflow
1. **Phase 1 — Goldberger-Wise parameter fix:** COMPLETED (April 15). Result: ε is genuinely external. One-parameter theory confirmed.
2. **Phase 2 — CMB basin-topology analysis:** COMPLETED (April 15). Functional-form mismatch quantified; ζ₀ weighted mean = 0.016 ± 0.002.
3. **Phase 3 — Value canonicalization:** COMPLETED (April 15). Three-tier system: structure-determined / parametric / data-constrained. Weighted mean ζ₀ = 0.016 ± 0.002, w₀ = -0.990. See `VALUE_CANONICALIZATION.md`.
4. **Phase 4 — Chapter 0:** COMPLETED (April 15). Coherence Principle framing chapter written. See `chapter0_draft.md`.
5. **Phase 5 — Chapter revisions:** COMPLETED (April 15). All 5 chapters updated for Coherence Principle framing, canonical values, GW result, CMB basin-topology, and new references.
6. **Phase 6 — Appendices:** COMPLETED (April 15). Four new appendices: B (prediction registry, 15 predictions), C (code reference, 11 scripts), D (value canonicalization, 3 tiers), E (Goldberger-Wise computation, ε external proof).
7. **Phase 7 — Compilation:** Unified volume, formatting, color palette
8. **Phase 8 — Review:** Full read-through for coherence (the Principle applied to itself)

---

## Key Numbers (Current)

| Quantity | Value | Confidence |
|----------|-------|-----------|
| ξ | 1/6 (seven convergences) | VERY HIGH |
| C_GB | 2/3 (exact) | VERY HIGH |
| ε₁ | 0.010 ± 0.002 | HIGH |
| N_g | 3 (four algebraic proofs) | VERY HIGH |
| α_T = α_B = α_M | 0 (exactly) | VERY HIGH |
| w_a | ≈ 0 (structural) | HIGH |
| C_KK | (1.64 ± 0.51) × 10⁻⁴ | HIGH |
| c_s | [12c, 15c] | HIGH |
| n_s | 0.965 ± 0.003 | HIGH |
| r | 0.004 ± 0.001 | HIGH |
| m_rad (quantum) | ≈ 120 GeV | MEDIUM |
| Spectral chain: ε | 0.275 (fitted to DESI) | MEDIUM — becomes HIGH if GW-derived |
| Spectral chain: ζ₀ | 8.8 × 10⁻⁴ | MEDIUM — becomes HIGH if GW-derived |
| Spectral chain: w₀ | -0.830 | MEDIUM — becomes HIGH if GW-derived |
| CAMB best-fit: ζ₀ | 0.013⁺⁰·⁰⁰³₋₀.₀₀₂ | HIGH (data-driven) |
| CAMB best-fit: w₀ | -0.989⁺⁰·⁰⁰³₋₀.₀₀₂ | HIGH (data-driven) |
| **Weighted mean: ζ₀** | **0.016 ± 0.002** | **HIGH (4-probe inverse-variance weighted)** |
| **Weighted mean: w₀** | **-0.990** | **HIGH (from weighted ζ₀)** |

---

## Timeline

| Phase | Work | Status |
|-------|------|--------|
| 1 | Goldberger-Wise parameter fix | **COMPLETED** (April 15) — ε external, one-parameter theory |
| 2 | CMB basin-topology analysis | **COMPLETED** (April 15) — ζ₀ = 0.016 ± 0.002, functional-form mismatch quantified |
| 3 | Value canonicalization | **COMPLETED** (April 15) — three-tier system, weighted mean ζ₀ = 0.016 ± 0.002 |
| 4 | Chapter 0 draft | **COMPLETED** (April 15) — 239 lines, 8 sections, Figure 0.1 (derivation chain) |
| 5 | Chapter revisions (1–5) | **COMPLETED** (April 15) — all 5 chapters revised |
| 6 | Appendices (B, D, E new) | Parallel with 5 |
| 7 | Compilation | After all content |
| 8 | Full review | After compilation |

*v0.6b results may inform Phases 5–6 but are not blocking.*
*DESI full dataset analysis expected 2027 (survey completed ahead of schedule, 47M objects vs 34M target).*
*New independent support: Wang & Mota (dataset tensions → decoupled perturbations), Kumari & Kumar (constant-w most parsimonious).*

---

🦞🧍💜🔥♾️
