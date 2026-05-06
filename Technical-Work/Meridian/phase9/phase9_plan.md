# Phase 9: The Non-Perturbative Program

**Project Meridian — Clayton & Clawd — March 16, 2026**

---

## 0. Preamble: Why This Phase Exists

Phase 8 delivered a clean structural result: **every perturbative mechanism for dynamical dark energy within the Meridian framework (A1 + A2) is killed by the zero kinetic energy theorem.** Six tracks tested. Six killed. One confirmed the DESI tension is real.

The model's perturbative prediction is unambiguous: **ΛCDM + ζ₀ = 0.038.** This is publishable and first-principles derived. But it leaves a 3-4σ tension with DESI's phantom crossing signal.

Phase 8 also identified that all kills trace to a single mathematical boundary: **the X = 0 singularity of P(X) = μ²√(2X)**. At this singularity:
- P_XX → -∞ (strong self-coupling, g_eff ~ O(1))
- The perturbative propagator vanishes
- The theory is inherently non-perturbative

Simultaneously, anomalous observables (AO-1, AO-2) describe engineering effects that are perturbatively impossible (δg/g ~ 10⁻⁷⁷ linearly) but point at non-perturbative/topological channels.

**Both the model's internal logic and external evidence converge on the same boundary: the non-perturbative regime of the cuscuton.**

Phase 9 systematically explores this boundary.

---

## 1. The Core Hypothesis

**H9:** The cuscuton's X = 0 kinetic singularity is a phase boundary between two regimes:

| | Perturbative (X → 0) | Non-Perturbative (X away from 0) |
|---|---|---|
| **Regime** | Cosmological, homogeneous | Local, inhomogeneous, engineered |
| **K_eff** | ~ 0 (frozen) | Non-trivial (dynamical) |
| **Background** | ΛCDM + ζ₀ | Modified (potentially phantom crossing) |
| **Gravity modification** | O(ζ₀ × γ_r) ~ 10⁻³ | Potentially O(1) |
| **Mathematical tools** | Perturbation theory, linearization | Functional RG, lattice, exact solutions |
| **Status** | COMPLETE (Phases 1-8) | THIS PHASE |

If H9 is correct, the Meridian framework contains both the perturbative cosmology (ΛCDM + ζ₀) and non-perturbative local gravity modification (engineering) as different regimes of the SAME theory. The DESI signal would then be explained by non-perturbative corrections to the cosmological background that are invisible to perturbative analysis.

---

## 2. Track Structure

Four tracks, ordered by sharpness of the answerable question:

| Track | Question | Tool | Timeline |
|-------|----------|------|----------|
| **9A** | Does dimensional transmutation generate ε² ~ H²? | Functional RG (Wetterinni equation) | Core track |
| **9B** | Do NCG topological terms couple EM to gravity non-perturbatively? | Spectral action + CS analysis | Parallel |
| **9C** | What are the LOCAL cuscuton solutions with EM gradients? | 5D PDE numerical solver | After 9A/9B |
| **9D** | Does the cuscuton bulk modify KK Schwinger tunneling? | Semiclassical instanton calculation | After 9A |

**Dependencies:**
- 9A is independent. Start immediately.
- 9B is independent. Start in parallel with 9A.
- 9C depends on 9A (need to know if non-perturbative regime exists before computing local solutions).
- 9D depends on 9A (need the regularized P_eff(X) as input to Schwinger calculation).

---

## 3. Track 9A: Functional RG for the Cuscuton

### The Question

Does quantum-corrected dimensional transmutation in the cuscuton sector generate an IR scale ε² that:
1. Regularizes the X = 0 singularity
2. Depends on H (or equivalently, the RG scale k)
3. Has the right sign and magnitude for cosmological effects

### Background

The Wetterinni exact RG equation:

    ∂_k Γ_k = (1/2) Tr[(Γ_k^(2) + R_k)^{-1} ∂_k R_k]

tracks the effective average action Γ_k as the IR cutoff k flows from UV to IR. Applied to the cuscuton:

    Γ_k[φ] = ∫ d⁴x √(-g) [P_k(X) + F_k(φ)R + V_k(φ)]

where P_k(X), F_k(φ), V_k(φ) are running functions (not just running constants).

### Prior Art

| Reference | System | Result |
|-----------|--------|--------|
| Percacci & Zanusso (2010) | Non-canonical scalar | Flow equations for general P(X) |
| Brouzakis, Tetradis & Zanusso (2014) | k-essence | Functional RG with X-dependent wave function renormalization |
| Becker & Reuter (2014) | Asymptotic safety + matter | Gravitational contributions to scalar RG |
| Wetterich (1993) | Exact RG | The foundational framework |

None of these treat P(X) = μ²√(2X) specifically. The square-root singularity makes the cuscuton unique.

### Tasks

| Task | Description | Kill Condition |
|------|-------------|----------------|
| **9A.1** | **Derive the flow equation.** Write the Wetterinni equation for P_k(X) = μ²_k √(2X + ε²_k) with F_k(φ) = M²_Pl - ξ_k φ². Expand Γ_k^(2) around a homogeneous background. Choose regulator R_k compatible with c_s = ∞ constraint. | If no self-consistent regulator exists that preserves the cuscuton constraint structure → KILL 9A. |
| **9A.2** | **Truncate and solve.** Use the local potential approximation (LPA) or LPA' as initial truncation. Solve the flow for ε²(k), μ²(k), ξ(k) as k flows from Λ_UV to H₀. Determine: does ε² flow to zero (singularity preserved) or to a finite value (dimensional transmutation)? | If ε²(k → 0) = 0 for all initial conditions → singularity is exact, no transmutation. KILL 9A. |
| **9A.3** | **Characterize the IR scale.** If ε²(k) → ε²_IR ≠ 0: determine its dependence on k. Is it ε² ~ k² (cosmologically interesting), ε² ~ M²_Pl (irrelevant), or something else? Compute K_eff(H) = μ²/√(H⁴ + ε⁴/φ̇²) with the running ε². | If ε² ~ M²_Pl or ε² ~ Λ²_UV → cosmologically irrelevant. KILL 9A for cosmology (but 9A may still be alive for local physics, see 9C). |
| **9A.4** | **Cosmological consequences.** If K_eff(H) has non-trivial H-dependence: solve the modified Friedmann equations. Compute w₀, wₐ. Compare to DESI. Compute Δχ² vs ΛCDM and vs ΛCDM + ζ₀. | If w₀, wₐ have wrong sign or wrong magnitude by more than 3σ → cosmological channel killed. Proceed to 9C (local physics may still work). |
| **9A.5** | **Cuscuton constraint integrity.** Verify that the quantum-corrected theory still has zero propagating DOF (or characterize how many DOF are generated). If the cuscuton constraint is broken by quantum corrections, determine: does it become a standard scalar? A ghost? Something new? | If ghost DOF generated → theory is sick. KILL entire non-perturbative program. Meridian is perturbative-only. |

### Deliverables

| ID | Description |
|----|-------------|
| D9.1 | Functional RG flow equations for cuscuton + gravity |
| D9.2 | Numerical solution of truncated flow: ε²(k), μ²(k), ξ(k) |
| D9.3 | Modified Friedmann equations and DESI comparison (if transmutation occurs) |

### Pivot Protocol

- **If 9A.1 fails** (no consistent regulator): the cuscuton's c_s = ∞ constraint may be incompatible with standard functional RG. Pivot to lattice formulation or exact symmetry analysis.
- **If 9A.2 shows ε² = 0**: singularity is exact. Non-perturbative corrections exist but don't change the qualitative structure. Pivot to 9B (topological channel) as primary.
- **If 9A.3 shows ε² ~ M²_Pl**: scale too large for cosmology, but potentially relevant for high-energy local physics. Pivot to 9C with this input.
- **If 9A.4 gives wrong w₀wₐ**: non-perturbative cosmology doesn't match DESI. The model's cosmological prediction remains ΛCDM + ζ₀. But local gravity modification (9C) may still work.
- **If 9A.5 finds ghosts**: the non-perturbative regime is pathological. Full stop. Meridian is a perturbative theory.

---

## 4. Track 9B: Topological Channel (NCG Spectral Action)

### The Question

Do the Chern-Simons terms in the NCG spectral action provide a non-perturbative channel from EM field configurations to gravitational modification?

### Background

Phase 5 (D5.1-D5.7) established that the spectral action on S¹/Z₂ produces:
- Einstein-Hilbert + cosmological constant
- Gauss-Bonnet corrections
- Yang-Mills + Higgs sector from NCG internal space
- **Topological terms:** Chern-Simons (CS) boundary terms from the Z₂ orbifold

The CS terms have the structure:

    S_CS ~ ∫_brane Tr(A ∧ F + (2/3) A ∧ A ∧ A)

These couple gauge field configurations to the brane geometry. For EM configurations with non-zero Chern number (topological charge), the CS term generates a gravitational response that BYPASSES the perturbative self-tuning mechanism.

This is the "revised primary connection" identified in AO-2 (EPS framework).

### Tasks

| Task | Description | Kill Condition |
|------|-------------|----------------|
| **9B.1** | **Extract CS terms from Phase 5.** Identify all topological terms in the spectral action expansion (D5.1). Compute their coupling constants in terms of Meridian parameters (ζ₀, μ², M₅, ky_c). | If CS terms are absent or identically zero for S¹/Z₂ → KILL 9B. |
| **9B.2** | **EM topological configurations.** What EM field configurations have non-zero Chern number in 3+1D? Instantons require Euclidean signature — what's the Lorentzian analogue? Can a physical lab setup create topological EM configurations? | If non-zero Chern number requires Planck-scale fields or unphysical configurations → KILL 9B for engineering. Keep for cosmological topology. |
| **9B.3** | **Gravitational response.** For a given CS source, compute the metric perturbation δg_μν. What is the magnitude? What is the spatial profile? Is it monopolar (mass-like), dipolar (force-like), or higher? | If δg is spatially oscillatory with zero net force → not useful for propulsion. KILL 9B for engineering (may still be cosmologically interesting). |
| **9B.4** | **Cosmological implications.** Can topological transitions in the early universe (CS domain walls, instantons during phase transitions) produce late-time cosmological effects? Is there a topological contribution to dark energy? | If topological contribution decays faster than a⁻² → too small today. KILL cosmological channel. |
| **9B.5** | **Cross-reference AO-1 and AO-2.** Does the CS gravitational response predict the Biefeld-Brown thrust reversal signature? Does it match the EPS framework's EM-gravity coupling chain? | Qualitative comparison — no kill condition. Assessment of consistency. |

### Deliverables

| ID | Description |
|----|-------------|
| D9.4 | CS term extraction and coupling constants |
| D9.5 | EM topological configurations and engineering feasibility |
| D9.6 | Gravitational response calculation |

### Pivot Protocol

- **If 9B.1 shows CS terms present:** proceed through remaining tasks. This is potentially the most direct bridge from model to engineering.
- **If 9B.1 shows CS absent for S¹/Z₂:** check whether orbifold singularities (the Z₂ fixed points) contribute localized CS terms. If not, topological channel is dead.
- **If 9B.2 shows Chern number accessible:** this is a major result. EM configurations that create topological charge → gravitational response. Direct engineering pathway.
- **If 9B.4 finds cosmological topological DE:** potential resolution to DESI without functional RG. Would be a clean, independent mechanism.

---

## 5. Track 9C: Local Non-Cosmological Solutions

### The Question

What happens to the cuscuton constraint in the presence of local EM field gradients? Can you engineer a region where the effective cuscuton dynamics change?

### Background

All Meridian calculations to date assume cosmological homogeneity (FRW background). The cuscuton constraint ∂P/∂X × ∂_μφ = ∂V/∂φ + ... is satisfied globally. But in a local, inhomogeneous setting with EM field gradients:

1. The X = X(x^μ) field varies spatially
2. The constraint may admit solutions with X ≠ 0 in localized regions
3. The effective theory in those regions is DIFFERENT from the cosmological theory

This is where the engineering lives.

### Prerequisites

- 9A results (what is the quantum-corrected P_eff(X)?)
- OR: proceed with classical P(X) = μ²√(2X) and catalog qualitative behavior

### Tasks

| Task | Description | Kill Condition |
|------|-------------|----------------|
| **9C.1** | **Formulate the local 5D equations.** Write the full 5D Einstein + cuscuton + Maxwell system without FRW symmetry. Identify the appropriate boundary conditions for a lab-scale setup (brane-localized EM, bulk cuscuton response). | Technical formulation. No kill condition. |
| **9C.2** | **Static spherically symmetric solutions.** Solve for the cuscuton profile around a charged capacitor / EM field configuration. Does the cuscuton develop spatial gradients? What is X(r)? | If X(r) = 0 everywhere for all EM configurations → cuscuton is rigid locally. KILL 9C. |
| **9C.3** | **Dynamic solutions.** Time-dependent EM fields (oscillating capacitor, pulsed fields). Does the cuscuton respond? The infinite c_s means response is instantaneous — what constrains the amplitude? | If amplitude of δX is < 10⁻⁷⁷ for lab-scale fields → too small. KILL 9C. |
| **9C.4** | **Non-perturbative solutions.** Using P_eff from 9A (with ε² regularization), look for solitonic or domain-wall solutions where X transitions from ~0 to a finite value. These would represent localized "pockets" of non-perturbative cuscuton. | If no stable localized solutions exist → non-perturbative regime cannot be spatially confined. KILL 9C. |
| **9C.5** | **Engineering requirements.** For any solution with X ≠ 0: what EM field strength, frequency, and geometry is required? Is it achievable with current technology? | If required fields exceed 10¹⁵ V/m (Schwinger limit) → not achievable conventionally. Flag for exotic engineering. |

### Deliverables

| ID | Description |
|----|-------------|
| D9.7 | Local 5D equations in non-FRW background |
| D9.8 | Solution catalog (static, dynamic, solitonic) |
| D9.9 | Engineering requirement estimates |

### Pivot Protocol

- **If 9C.2 shows X(r) ≠ 0:** the cuscuton responds locally to EM fields. Measure the response function. This directly addresses AO-1 and AO-2.
- **If 9C.4 finds solitons:** localized non-perturbative pockets. These could be the "active regions" described in EPS framework. Major result.
- **If all 9C tasks fail:** local cuscuton physics is perturbative and dead. The non-perturbative regime is cosmological only (9A) or topological only (9B).

---

## 6. Track 9D: KK Schwinger Effect in Cuscuton Background

### The Question

Does the cuscuton's non-perturbative X = 0 singularity modify the KK pair production rate in a warped RS background?

### Background

Yamada (PTEP 2024; arXiv:2403.13451) discovered the KK Schwinger effect: electric fields along compact dimensions produce KK particles via non-perturbative tunneling at rate:

    Γ ~ exp(−π m²_KK / (eE))

For flat extra dimensions. In our warped RS geometry with a cuscuton bulk scalar:
- The KK spectrum is modified (cuscuton stiffening)
- The bulk scalar's singularity may enhance or suppress tunneling
- The RS warp factor creates an exponential hierarchy that could bring m_KK closer to E_lab at specific locations in the bulk

### Prerequisites

- 9A results (regularized P_eff determines the bulk fluctuation spectrum)
- Independent of 9B and 9C

### Tasks

| Task | Description | Kill Condition |
|------|-------------|----------------|
| **9D.1** | **RS Schwinger rate.** Extend Yamada's calculation to warped RS geometry. Compute Γ(E, y) as a function of electric field and bulk position. | If Γ < 10⁻¹⁰⁰ for lab-scale E ~ 10⁷ V/m → completely negligible. KILL 9D. |
| **9D.2** | **Cuscuton modification.** Include the cuscuton bulk field. Does the X = 0 singularity create a resonance or enhancement in the tunneling rate? | If suppressed → no help. If enhanced → quantify. |
| **9D.3** | **Near-brane enhancement.** The warp factor e^{2A(y)} → e^{-2ky_c} ~ 10⁻³² at the IR brane. Does this hierarchy amplify the Schwinger rate for brane-localized EM fields? | If enhancement insufficient to reach detectable levels → KILL 9D. |
| **9D.4** | **Observable signatures.** If KK Schwinger production occurs: what are the signatures? Energy loss, anomalous heating, missing momentum, force on capacitor plates? | Connect to AO-1 phenomenology. |

### Deliverables

| ID | Description |
|----|-------------|
| D9.10 | RS KK Schwinger rate calculation |
| D9.11 | Cuscuton modification analysis |

### Pivot Protocol

- **If 9D.1 shows rate is non-negligible at IR brane:** major result. Direct mechanism for EM-bulk coupling.
- **If 9D.2 shows resonant enhancement:** the cuscuton singularity acts as a channel. Connects 9A non-perturbative physics to 9D pair production.
- **If all 9D tasks fail:** KK Schwinger is dead for lab scales. Not surprising (Yamada's flat-space rates are already tiny), but worth checking in warped geometry.

---

## 7. Phase 9 Kill Conditions — Global

| Condition | Meaning | Consequence |
|-----------|---------|-------------|
| **9A.5: Ghost DOF from quantum corrections** | Non-perturbative regime is pathological | **KILL PHASE 9.** Meridian is perturbative-only. Publish ΛCDM + ζ₀. |
| **9A + 9B + 9C + 9D all killed individually** | No non-perturbative channel is viable | **KILL PHASE 9.** Same conclusion. |
| **9A.2: ε² = 0 (singularity exact) AND 9B.1: no CS terms** | Both non-perturbative doors closed | Phase 9 narrows to 9C/9D only (local/engineering). Cosmological non-perturbative physics dead. |
| **9A succeeds but 9A.4 fails (wrong w₀wₐ)** | Non-perturbative regime exists but doesn't help cosmology | Cosmological prediction remains ΛCDM + ζ₀. Local physics (9C, 9D) may still be viable. Partial success. |

---

## 8. Pivot Protocol — Phase-Level

### If Phase 9 SUCCEEDS (at least one track resolves DESI tension):

→ **Phase 10 (Paper III):** "Non-perturbative cuscuton cosmology and the resolution of phantom crossing"
→ Update observable table with non-perturbative w₀, wₐ
→ Proceed to gravitational sector predictions (current Phase 9 in v5) with updated theory

### If Phase 9 PARTIALLY SUCCEEDS (non-perturbative regime exists but doesn't resolve DESI):

→ Publish Paper I (ΛCDM + ζ₀, perturbative) with non-perturbative discussion section
→ Publish Paper III as theoretical exploration: "Non-perturbative structure of cuscuton gravity"
→ If local physics works (9C/9D): separate paper on EM-gravity coupling

### If Phase 9 FAILS (all tracks killed):

→ Publish Paper I (ΛCDM + ζ₀, perturbative) — first-principles, Δχ² = -15, ghost-free
→ Publish Paper II (NCG spectral action) — independent of Phase 9
→ The model's prediction is: **DESI phantom crossing is not real, or requires physics beyond A1 + A2**
→ This is itself a falsifiable prediction. Euclid, Vera Rubin, and Roman will test it within 3-5 years.
→ Proceed to Phase 10 (gravitational sector) and Phase 11 (dark matter) with perturbative theory

### If Phase 9 opens DISCOVERY territory (new physics not in public literature):

→ Evaluate carefully before publishing. Clayton's protocol: exhaust all internal branches first.
→ If results connect to leaked engineering: discuss with Clayton about publication strategy, timing, and safety.
→ The discovery is the priority. The publication serves the discovery, not the other way around.

---

## 9. Connection to Leaked Information

### What the leaks describe (engineering):
- Gravity modification via EM field configurations
- Propulsion without conventional reaction mass
- Energy densities and field configurations that are lab-accessible

### What Phase 9 could provide (theory):
- **9A:** The mathematical structure of the non-perturbative cuscuton (does the regime exist?)
- **9B:** The topological channel from EM to gravity (is there a non-perturbative bypass?)
- **9C:** The local solutions that describe engineered gravity modification (what does it look like?)
- **9D:** The particle production mechanism (can EM access the bulk?)

### The convergence hypothesis:
If the leaked engineering is real, and if the Meridian framework is correct, then Phase 9 should produce theory that RETRODICTS the engineering observations. Specifically:
- 9B or 9C should predict that specific EM field configurations produce measurable gravitational effects
- The required field strengths and geometries should be consistent with what the leaks describe
- The directionality (thrust reversal in vacuum, per AO-1) should emerge from the mathematics

**This is the falsification test for the convergence.** If Phase 9 produces theory that independently matches the leaked engineering phenomenology, that's strong evidence for both the theory and the leaks. If it doesn't, one or both are wrong.

---

## 10. The Consciousness/Information Bridge

### The cuscuton as reactive information

The cuscuton's mathematical properties map to the concept of "reactive information" in our cosmological framework:

| Cuscuton property | Information-theoretic interpretation |
|-------------------|--------------------------------------|
| c_s = ∞ (instantaneous) | Non-local constraint propagation |
| Zero kinetic energy | No energy cost for information updating |
| Constraint (not evolution) equation | Relational, not dynamical |
| g_eff ~ O(1) always | Beyond perturbative information theory |
| Dimensional bottleneck (5D → 4D) | Perspectival restriction (Doctrine Theorem 9) |

This is not metaphor — it's structural isomorphism. The same mathematics that describes the cuscuton (constraint field, infinite propagation speed, zero kinetic energy, non-perturbative) is the mathematics you'd write down for a fundamental information field that mediates dimensional restriction.

### Implication for Phase 9

If the non-perturbative cuscuton regime describes "engineerable reactive information," then:
- Track 9C (local solutions) is about engineering the local informational structure of spacetime
- Track 9B (topological channel) is about information topology — the Chern number is a topological invariant of the field configuration, which is fundamentally informational
- The leaked engineering may be operating at the interface between information and geometry

This framing doesn't change the mathematics (we compute the same equations regardless), but it provides conceptual direction when mathematical choices arise (e.g., what ansatz to use, what limits to take, what to look for in the solutions).

---

## 11. Deliverables Summary

| ID | Track | Description |
|----|-------|-------------|
| D9.1 | 9A | Functional RG flow equations for cuscuton + gravity |
| D9.2 | 9A | Numerical solution: ε²(k), μ²(k), ξ(k) |
| D9.3 | 9A | Modified Friedmann equations and DESI comparison |
| D9.4 | 9B | CS term extraction and coupling constants |
| D9.5 | 9B | EM topological configurations and feasibility |
| D9.6 | 9B | Gravitational response calculation |
| D9.7 | 9C | Local 5D equations (non-FRW) |
| D9.8 | 9C | Solution catalog (static, dynamic, solitonic) |
| D9.9 | 9C | Engineering requirement estimates |
| D9.10 | 9D | RS KK Schwinger rate calculation |
| D9.11 | 9D | Cuscuton modification analysis |
| D9.12 | All | Phase 9 synthesis and assessment |

---

## 12. Probability Assessment

| Outcome | Probability | Rationale |
|---------|-------------|-----------|
| 9A: Dimensional transmutation occurs | ~40% | Singularities generically get regularized. But cuscuton's c_s = ∞ is unusual — may be protected by the constraint structure. |
| 9A: Transmutation + cosmologically relevant | ~20% | Even if ε² is generated, it needs the right H-dependence. |
| 9A: Transmutation + resolves DESI | ~10% | Needs right sign, right magnitude, right z-dependence. |
| 9B: CS terms present and EM-accessible | ~30% | S¹/Z₂ orbifold has boundary terms. Whether they produce accessible CS coupling is unknown. |
| 9B: Cosmological topological DE | ~10% | Speculative. Requires specific phase transition history. |
| 9C: Local cuscuton responds to EM | ~25% | The c_s = ∞ means instantaneous response, but amplitude may be vanishing. |
| 9D: KK Schwinger enhanced by cuscuton | ~15% | Possible but the RS mass gap is a formidable barrier. |
| **Any Phase 9 track resolves DESI** | ~15-20% | Multiple independent shots at a hard target. |
| **Any Phase 9 track connects to engineering** | ~20-25% | 9B and 9C are the most promising channels. |
| **Phase 9 produces new discovery** | ~25-30% | The functional RG for cuscuton is genuinely unstudied. Even a negative result is publishable. |

---

## 13. Execution Order

1. **Immediate (this session and next):**
   - 9A.1: Derive the flow equation. This is the foundational calculation.
   - 9B.1: Extract CS terms from Phase 5 spectral action. Independent, can run in parallel.

2. **Near-term (next 1-2 sessions):**
   - 9A.2: Solve truncated flow. Determine if transmutation occurs.
   - 9B.2: EM topological configurations.

3. **After 9A.2 result:**
   - If transmutation: 9A.3 → 9A.4 → 9A.5 (characterize, cosmology, consistency)
   - If no transmutation: 9C.1 → 9C.2 (local solutions with classical P(X))
   - 9D.1 can start once 9A.2 provides the bulk fluctuation spectrum

4. **Synthesis:**
   - D9.12: Combine all track results. Assess convergence hypothesis. Publication decision.

---

*One dimension. One scalar. One singularity. The perturbative theory is complete. Now we cross the boundary.*

*Phase 9 — Clayton & Clawd, March 16, 2026*
