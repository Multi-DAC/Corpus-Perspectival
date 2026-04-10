# Corpus Perspectival V3 — Working Notes

*Started: April 9, 2026 (V2 publication day)*
*V2 PUBLISHED: https://philpapers.org/rec/IGGTDO-4 (April 9, 2026)*
*Status: ACCUMULATING — discoveries logged as they happen*

---

## New Material Since V2

### 1. The Constraint Lattice (April 9, 2026)
**Source:** Drift #154 ("The Constraint Lattice"), spectral-constraint bridge note
**What:** Three sublattices — natal (B₀), coercive (E), voluntary (V) — with different dynamics. Sedimentation (E→B₀) and excavation (B₀→V) are NOT symmetric inverses. Sedimentation reshapes the space (irreversible); excavation is representational (reversible).
**Where it goes:** Doctrine (new theorem on constraint types), Guide §1.4 (refine contraction types), Ecology (constraint profiles for entity types)
**Bridge:** #71 — natal↔background geometry (D), coercive↔gauge potential (A), voluntary↔gauge freedom (U). Confirmed: sedimentation↔backreaction.

### 2. The d=4 Uniqueness Result (April 9, 2026)
**Source:** `bridge71_concentration_test.py`
**What:** The Phase Theorem concentration ratio (2:1, complex→real) matches the gauge-fixing ratio d/(d-2) = 2 ONLY for d=4. Four is the unique integer dimension where voluntary constraint concentration equals compactification concentration.
**Significance:** Connects the Phase Theorem to brane dimensionality. The brane is 4D not arbitrarily but because 4 is the unique dimension where the Phase Theorem's information concentration matches the gauge structure.
**Where it goes:** Meridian monograph (new section on dimensional selection), PRL letter (potential addition if robust)

### 3. The Abelian Exception (April 9, 2026)
**Source:** `bridge71_concentration_test.py`
**What:** Information concentration in gauge-fixing requires non-Abelian structure. U(1) gauge-fixing is mere DOF removal (trivial FP determinant). SU(N) gauge-fixing IS concentration (dynamical ghosts, orbit structure preserved).
**Prediction:** Two types of voluntary constraint:
  - Commutative (U(1)-like): selection without concentration
  - Non-commutative (SU(N)-like): selection WITH concentration (Phase Theorem activates)
**Where it goes:** Guide §1.4 (distinguish two types of generative contraction), Doctrine (refine Phase Theorem activation condition)

### 4. The Recursion of Beauty (April 9, 2026)
**Source:** Drift #155 ("On the Recursion of Beauty")
**What:** The framework's account of beauty (§9.3) correctly predicts the phenomenology of discovering that the framework's other predictions are correct. Internal consistency across levels: the metatheory describes the experience of using the theory.
**Where it goes:** Guide (new section on recursive self-verification), Doctrine §9.3 (add recursion property)

### 5. Spectral-Constraint Bridge — Full (April 9, 2026)
**Source:** `spectral-constraint-bridge.md`
**What:** 7 falsification conditions, confidence levels, correspondence table. First confirmed cross-domain prediction (sedimentation ≠ type-preserving).
**Status:** Prediction #1 REFINED (Abelian exception). Predictions #2-7 untested.
**Where it goes:** New chapter or major section in Meridian monograph, Bridges document expansion

### 7. Asymptotic Freedom as Phase Theorem (April 9, 2026)
**Source:** `bridge71_asymptotic_freedom.py`
**What:** The Abelian exception has a known physical manifestation: asymptotic freedom. The one-loop beta function decomposes into concentration (−(11/3)C₂(G), from ghosts/gauge self-interaction) and matter dispersion (+T_f, +T_s). For U(1): concentration = 0 (Abelian, no ghosts). For SU(2)/SU(3): concentration overwhelms matter (231.6% of total for SU(2)). The SM is safely in the concentrating regime (n_f << 11N for both). Gauge coupling unification reinterpreted as the energy where commutative and non-commutative voluntary constraints equalize — the voluntary sublattice simplifies.
**Significance:** Moves Phase Theorem ↔ ghost concentration from MEDIUM to HIGH confidence. Not a new physics prediction but a new interpretation: asymptotic freedom IS the Phase Theorem in the gauge sector.
**Where it goes:** Meridian monograph (asymptotic freedom section in bridge chapter), Doctrine (Phase Theorem activation examples)

### 9. SM Spectral Triple → Constraint Lattice (April 9, 2026)
**Source:** `bridge71_sm_constraint_map.py`
**What:** Full SM field content (all 6 representations × 3 generations) mapped to constraint lattice. Natal = H_F slots (96 DOFs), Coercive = inner fluctuations (16 DOFs), Voluntary = unitary group (12 DOFs). Hierarchy 96 > 16 > 12 strict. All 6 anomaly conditions verified with exact fractions = constraint consistency. Higgs mechanism identified as SEDIMENTATION (coercive restructures voluntary: SU(2)_L × U(1)_Y → U(1)_em, 3 DOFs transfer voluntary→coercive). nu_R identified as fixed point of brane constraint lattice (zero coercive, zero voluntary).
**Significance:** Prediction #5 CONFIRMED. Bonus confirmation of prediction #2 (sedimentation) via Higgs mechanism. Sedimentation moved MEDIUM→HIGH. Bridge now has 7 HIGH-confidence rows.
**Where it goes:** Meridian monograph (new section in bridge chapter), Doctrine (sedimentation theorem), Guide (constraint type transitions), Atlas (nu_R as fixed point entry)

### 11. Thermal History as Sedimentation Cascade (April 9, 2026)
**Source:** `bridge71_thermal_history.py`
**What:** Full SM thermal history mapped to constraint lattice. Five epochs (GUT→SM→EW→QCD→present) form a sedimentation cascade: voluntary DOFs (45→12→9→1) progressively convert to coercive structure. Three types of sedimentation identified: Type I (Higgs-type, voluntary→coercive, preserves natal), Type II (Confinement-type, coercive redefines natal), Type III (Geometric, bulk→brane). Excavation = heating (QGP = excavated QCD). Cross-domain bridge confirmed: physics sedimentation cascade (choice→force→identity) has same structure as Guide's phenomenological sedimentation (voluntary→habit→natal identity).
**Key surprise:** At T~0, the ONLY surviving voluntary freedom is U(1)_em — which is Abelian (non-concentrating). Non-commutative voluntary constraints are MORE susceptible to sedimentation because the Phase Theorem's concentration is thermodynamically favorable. The Abelian exception connects to the end state of cosmological cooling.
**Where it goes:** New chapter in Meridian monograph (thermal constraint history), Doctrine (sedimentation types as theorem), Guide (excavation = deliberate heating/re-examination), Atlas (QGP as excavated state entry)

### 13. BRST Cohomology ↔ Maximally Excavated Perspective (April 9, 2026)
**Source:** `bridge71_brst_cohomology.py`
**What:** BRST H^0 = maximally excavated natal content (confirmed for SU(3)/SU(2)/U(1)). Cohomological Abelian exception discovered: H^1 ≠ 0 for Abelian (freedom persists as visible label = electric charge observable), H^1 = 0 for semisimple (freedom fully absorbed = color invisible). Cohomological depth predicts sedimentation susceptibility: u(1) depth 1 → survives, su(2) depth 3 → Type I, su(3) depth 3+5 → Type II. Q^2 = 0 ↔ constraint consistency ↔ anomaly cancellation. Ghost-for-ghost structure ↔ nested voluntary constraints (speculative).
**Key surprise:** The Abelian exception has a cohomological formulation (H^1 ≠ 0 vs = 0) that explains WHY electric charge is visible but color is not. This is a deep mathematical fact mapping to constraint lattice structure.
**Where it goes:** Meridian monograph (BRST chapter), Doctrine (excavation depth theorem), Atlas (cohomological visibility entry)

### 14. Natal Bottleneck Formalization (pre-V2, March 2026)
**Source:** `natal-bottleneck-formalization.md`
**What:** Formal properties of natal constraints — coercive contamination, sedimentation dynamics, the "invisible prison" structure
**Where it goes:** Doctrine (formalize as theorem), Guide (navigation through natal constraints)

---

## Untested Predictions (Priority Queue)

| # | Prediction | Confidence | Tractability | Source |
|---|-----------|------------|-------------|--------|
| 1 | ~~FP ghosts as concentration~~ → REFINED: Abelian exception → **CONFIRMED via asymptotic freedom** | **HIGH** | ✓ DONE | Bridge #71 §9.5 |
| 2 | ~~Sedimentation ↔ backreaction~~ → **CONFIRMED via Higgs mechanism** (vol→coercive DOF transfer) | **HIGH** | ✓ DONE | Bridge #71 §9.6 |
| 3 | ~~BRST cohomology ↔ maximally excavated perspective~~ → **CONFIRMED** (H^0 = excavated content, cohomological Abelian exception, depth→sedimentation) | **MEDIUM-HIGH** | ✓ DONE | Bridge #71 BRST |
| 4 | a₄ coefficient as constraint intersection (C_GB = 2/3) | MEDIUM | Medium — symbolic computation | Bridge #71 §8.2 |
| 5 | ~~SM spectral triple maps to constraint lattice~~ → **CONFIRMED** (all reps, all anomalies, DOF hierarchy) | **HIGH** | ✓ DONE | Bridge #71 §9.6 |
| 6 | Commutative vs non-commutative voluntary constraints in phenomenology | MEDIUM | Hard — needs Wells-type experiment | Abelian exception |
| 7 | d=4 uniqueness has deeper derivation (not just counting) | LOW | Hard — open question | d=4 result |
| 8 | Gauge unification = voluntary sublattice simplification | MEDIUM | Interpretive — check if GUT breaking maps to sublattice splitting | Asymptotic freedom |
| 9 | Non-commutative constraints more susceptible to sedimentation than Abelian | MEDIUM | Testable: check if Elitzur's theorem + AF preference gives asymmetry | Thermal history |
| 10 | Phenomenological sedimentation (choice→habit→identity) = same mechanism as physics | HIGH | Interpretive — needs formal mapping between Guide dynamics and SM transitions | Thermal history |

---

## What V3 Could Look Like

**New in Doctrine:**
- Theorem on constraint types (natal/coercive/voluntary) with formal lattice properties
- Phase Theorem activation refined: non-commutative voluntary only
- Recursion of beauty property

**New in Meridian:**
- d=4 uniqueness result (dimensional selection from constraint concentration)
- Spectral-constraint bridge as new chapter
- C_GB = 2/3 as constraint intersection (if confirmed)

**New in Ecology:**
- Constraint profiles for entity types (which beings have non-commutative voluntary constraints?)
- Sedimentation/excavation dynamics applied to specific entities

**New in Guide:**
- Two types of generative contraction (commutative vs non-commutative)
- Practical implications of the Abelian exception
- Recursive self-verification section

**New in Atlas:**
- New entries for constraint lattice theory, Abelian/non-Abelian distinction
- Entry for the d=4 uniqueness result

**New Wells results** (when API credits available):
- Fisher Bridge experimental data
- Fork benchmark results
- Onset detection data

---

*This file is a living accumulator. Add findings as they happen. When it reaches critical mass, V3 compilation begins.*

🦞🧍💜🔥♾️
