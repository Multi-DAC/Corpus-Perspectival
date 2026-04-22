---
url: https://doi.org/10.1098/rspa.2025.0413
archive: (pending)
title: "On computing quantum waves exactly from classical action"
author: Winfried Lohmiller, Jean-Jacques Slotine
venue: *Proceedings of the Royal Society A* 482: 20250413
doi: 10.1098/rspa.2025.0413
institution: Nonlinear Systems Laboratory, Massachusetts Institute of Technology
published: 2026 (received 2025-05-11, accepted 2026-03-04)
accessed: 2026-04-22 (Day 81)
discussed: 2026-04-22 (Day 81, shared by Clayton mid-afternoon)
tags: coherence-principle, anchor-rev-2, meridian, f-coalgebra-companion, measurement-reframe, bell-reinterpretation, related-works-all-physics
status: read-in-full
pdf: pdfs/2026-04-22-lohmiller-slotine-quantum-waves-from-classical-action.pdf
---

## What it argues

Lohmiller & Slotine construct an **exact** (not semi-classical, not approximate) solution of the Schrödinger equation — and the relativistic Klein-Gordon, Pauli, Dirac, and Maxwell equations — from classical least action alone. The central result is **Theorem 3.2**:

$$\psi^\varepsilon(x,t) = \sum_{j \in J} \sqrt{\rho_j^\varepsilon} \cdot e^{i \varphi_j / \hbar}$$

where:
- $J$ indexes the **multi-valued local extremal action branches** (Theorem 2.4) — arising from multiple initial conditions in $x_o$ or $p_o$, or from **branch points** $\mathcal{B}^N$ that occur at unbounded $\Delta_M \varphi_j$ or $\nabla \varphi_j$ (i.e., at topological non-simply-connectedness, spatial inequality constraints, or Hamiltonian singularities).
- $\varphi_j$ is the **classical** action along branch $j$, solving the Hamilton-Jacobi p.d.e.
- $\rho_j$ is the **classical** density along branch $j$, computed from the continuity equation $\partial_t \rho + \nabla_M \cdot (\rho \dot{x}) = 0$ as the path integral $\rho_j(x_j(t),t) = \rho_{oj} \exp\left(-\int_0^t \Delta_M \varphi_j \, d\theta\right)$.

**Fundamental QM postulates are derived, not postulated:**

1. **Wave function existence** — Eq. 3.3, from classical $\varphi_j$ and $\rho_j$.
2. **Schrödinger equation** — Lemma 3.1 (each branch's wave $\psi_j$ identically satisfies the Schrödinger equation via the Hamilton-Jacobi p.d.e.).
3. **Wave collapse at measurement** — **Lemma 3.3**: a classical measurement $y_k$ of observable $y$ collapses the classical density distribution $\sqrt{\rho_j(y)}$ into the Dirac $\delta(y - y_k)$, which *through* Theorem 3.2 collapses the wave $\psi(y)$ into the eigenwave $\Psi_k(y) = \delta(y - y_k)$.
4. **Born's rule remains a postulate** — they are explicit about this (p. 8).
5. **Bohr-like quantization** — **Lemma 3.4**: periodic actions $\psi_j = \sqrt{\rho} \exp(i(\varphi + k\phi(\omega))/\hbar)$ force $\phi(\omega)/\hbar = 2\pi k, k \in \mathbb{N}$ via the limiting geometric sum $\lim_{K \to \infty} \frac{1}{K}\sum_{\kappa=0}^{K} e^{i\kappa\phi/\hbar}$.

**Examples worked in full:** double slit (multi-connected manifold → 2 branches), Aharonov-Bohm (same manifold + gradient vector potential), particle in a box (wall reflections → $\{\to,\leftarrow\}^2 \times k$ branches + quantization via Lem. 3.4), tunneling (complex-action branches in the classically forbidden region), harmonic oscillator (matches Feynman's Gaussian result), Coulomb/hydrogen (via quaternion transformation from harmonic oscillator), EPR entanglement (Example 4.1), positron/electron pair creation (Example 4.2, **no second quantization required**).

**Bell reinterpretation (§4.1, Eq. 4.26–4.31).** The quantum correlation $\langle \psi_1^\uparrow, \psi_2^\downarrow \rangle = -n_1^T n_2$ is derived *classically* by generalizing Bell's binary detector $A_p(n_p,\lambda) = \pm 1$ to the full-Bloch-sphere classical spinor detector $A_p = \Sigma \cdot n_p \chi_o^{\updownarrow}$. Bell's inequality (4.30) is then classically applicable only at $\beta = 2k\pi$ on the Bloch sphere; outside those loci, the generalized classical detector gives the quantum correlation directly. **This is not a hidden-variable theory in Bell's original sense** — the multi-valuedness is structural (topology / constraints / singularities), not secret parameters. The detector-model generalization is where the reinterpretation lives.

## Why this matters for us — condition-by-condition mapping to the Coherence Principle

The Principle says: *coherent multi-scale systems maintain structural superposition until informed measurement collapses them*. Lohmiller-Slotine give the exact physics realization:

| Principle condition | Lohmiller-Slotine realization |
|---|---|
| **C_sep** (structural separation) | $J$-valued action — multiple extremal branches $\varphi_j$ coexisting is exactly "structural superposition" (Thm 2.4). |
| **C_meas** (informed measurement) | **Lemma 3.3**: classical density collapses to Dirac $\delta(y - y_k)$ at measurement, which drives wave collapse via Thm 3.2. Informed collapse **derived**, not postulated. |
| **C_scale** (multi-scale consistency) | Abstract, verbatim: "suggest a smooth transition between physics across scales." |
| **C_dyn** (dynamical cycle) | Classical continuity equation $\partial_t \rho + \nabla_M \cdot (\rho \dot{x}) = 0$ along each branch — conservation law supporting cyclic dynamics. |

Every one of the Principle's four conditions has an explicit classical construction in this paper. The Principle is a compressed statement of the structural pattern this paper exhibits at the QM level.

## Where we diverge

- The authors restrict themselves to Lagrangian systems with invertible metric $M(x)$, potential $V(x,t)$, vector potential $A(x,t)$ under Coulomb/Lorenz gauge. Full Yang-Mills, QFT in curved spacetime, and quantum gravity are out of scope of the explicit construction — though Maxwell is included, and Dirac relativistic is treated. The *structural* claim (wave = Σ extremal-branch classical actions × densities) is enormous even in this restricted setting.
- Born's rule is still a postulate. C_meas in the Principle frames the measurement process but does not derive Born; neither does this paper. This is a shared open item, not a gap created by our use.
- The classically-based interpretation (decisions taken at initialization + branch points rather than at measurement time) is offered as philosophically consistent with classical Hamilton-Jacobi but they are explicit that both interpretations "lead to the same experimental results." They do not claim ontological priority; nor do we need them to.

## Connection to our program

### 1. Anchor (*The Coherence Principle*) — Rev-2 docket

**Direct citation in Anchor §9.5 (F-as-stream / measurement-reframe section).** Add Lohmiller-Slotine 2026 as a backing physics reference for the structural claim. Specifically:

- **Thm 2.4 + Thm 3.2** back the C_sep + C_scale + C_dyn triple at the QM level.
- **Lem 3.3** backs the C_meas claim that informed measurement collapses structural superposition — the Principle's measurement-reframe gets a classical-extremal-density derivation route, complementary to the Watanabe-Takagi (#111) + García-Pintos (#114) information-conservative route already queued for Rev 2.

**New §9.9 Q-item** (open question → now partially resolved): "Is there an exact classical-extremal-path construction underlying the Principle's measurement-reframe?" — **yes** for Lagrangian systems per Thm 3.2; scope-limited.

### 2. Companion (*Coherent Structure*) — surfaced-lemma additions

**§5.4 (F-as-stream):** add a scope remark — F_∞'s self-instantiation has a physics-level analog in the $J$-valued classical action structure. Not a formal incorporation; a pointer for readers seeking a physics-grounded instance.

**§6.4 (kind-classifier fibration):** the fibration $\pi: \textbf{Stream} \to \textbf{ContentIndex}$ has a QM realization — each branch $j \in J$ is a cartesian lift over its content-operation (the measurement operator that selects branch $j$). Admissibility (Lem 6.4.11) corresponds to the Lipschitz-continuity conditions in Thm 2.4 that guarantee branch-existence-and-uniqueness.

**§6.9 C-size regimes:** the $J$-set in Thm 2.4 is finite or countable (branch points are discrete, initial-condition ensembles are at-most-countable in any physical setup), placing physical streams squarely in Regime A or B of §6.9. Regime C (proper-class $J$) would require uncountable branch-point topology — not physically realized. This gives Regime A/B a physics anchor.

**§8 (F-as-stream self-reference closure):** Lemma 3.3 is the classical-physics analog of our audit observation 8.3.5 — at the moment of measurement, the self-consistent branch-set collapses to a single path determined by the measurement. The "external audit" we require for theorem-status elevation of 8.3.5 is (at the physics level) the measurement apparatus itself.

### 3. Meridian

**Immediate relevance.** Meridian's 5D warped geometry × NCG × spectral-action is a classical Lagrangian-metric-potential framework. Thm 3.2 applies directly: the quantum-wave structure on a Meridian background can be computed from classical extremal action paths + density, without a separate quantization procedure.

**Specific uses:**
- The PRL letter (pending) should cite Lohmiller-Slotine for the classical-to-quantum computational pathway. It strengthens the methodological claim that spectral-action predictions are not merely "classical approximations awaiting quantization."
- Meridian V2 revision can add a forward-pointer remark: "the classical action on our 5D background, via Lohmiller-Slotine 2026 Thm 3.2, suffices to compute quantum wave functions exactly on the same background."
- $w_0 = -0.990$ DESI prediction is a classical-action-derived quantity; Lohmiller-Slotine provide the framework statement that this IS the quantum observable to the extent one is needed.

### 4. Killing Form (KF)

Each training step is an extremal of a loss-action functional. KF's build/dissolve oscillation across gradient steps is structurally the multi-valued-action dynamics: multiple extremal trajectories coexist during training, measurement (evaluation / checkpoint) selects a branch, the post-hoc organizational analysis KF performs is reading out which branch was traversed. This is loose, pre-formalization; KF domain volume could thread it as motivation.

### 5. Living Architecture / Coherent Body / Dynamic Organization

These volumes deal with multi-scale classical dynamical systems. Lohmiller-Slotine's "smooth transition between physics across scales" + the exact classical-to-quantum construction means these domain volumes can cite a physics-level instance where the Principle's four conditions are provably tight.

### 6. Bridge candidate — proposed instance or meta-bridge

**Candidate instance (under existing meta-bridge on structural superposition):**
- *Classical action multi-valuedness ↔ framework structural superposition* — the $J$-valued classical action branches of Thm 2.4 are a physics-level realization of the Principle's C_sep structural superposition. Maps 1:1 onto the Companion's F-coalgebra content-operation branches.

**Candidate meta-bridge M12 (proposed):**
- *Derivability-of-apparent-primitives* — Lohmiller-Slotine's derivation of the Schrödinger equation + wave collapse from classical action joins a family of moves where what looks axiomatic turns out to be a theorem over a simpler foundation. Instances already in our corpus: recursive decomposability (Cor 6.3.4) derived from F-coalgebra structure rather than assumed; Anchor §8 kind-stratification derived from Content-dimension rather than A2. New instance: QM postulates derived from classical Hamilton-Jacobi + density-continuity + measurement-as-density-collapse.

*(Proposed; final elevation decision held for a full bridge-batch pass with Clayton.)*

### 7. Mirror — the "scan the literature before reconstructing" instance

Our C_meas derivation pathway in the Anchor was constructed semi-autonomously, anchored by the Watanabe-Takagi + García-Pintos measurement-reframe docket. The more direct classical-extremal-density route existed in the physics literature (the seeds trace to Dirac 1933 and Feynman 1948; the exact extension to multi-valued action is Lohmiller-Slotine 2026). **This is a "what else are we reconstructing?" moment.** Before undertaking further measurement-theoretic re-derivations, sweep the contraction-analysis / classical-HJ / nonlinear-systems literature for explicit constructions. Mirror note candidate — ties to #19 (architectural self-care lag, graduated to pattern with generalized fix) via its own generalization: *external-literature self-care lag* — searching for existing explicit derivations before re-deriving autonomously.

## Quote-pulls (verified from PDF)

- Abstract: "We show that the Schrödinger equation can be solved exactly based only on classical least action. Fundamental postulates of quantum mechanics can in turn be derived directly from this construction. The results extend to the relativistic Klein-Gordon, Pauli, and Dirac equations, and suggest a smooth transition between physics across scales."
- Abstract: "Quantum wave collapse at measurement can be derived from the classical density change. Entanglement corresponds to a sum of classical particle actions mapping to a tensor product of spinors."
- §5 Concluding: "The fundamental quantum postulates on the existence of a wave function, its propagation with the Schrödinger equation in theorem 3.2 and the wave collapse at a measurement in lemma 3.3 are derived from the classical theorem 2.4."
- §3 (after Lem 3.3): "the classically-based interpretation would be that these decisions are taken before the measurement, at the initial condition $t=0$ and at the branch points along the $J$ multipath. Which interpretation best describes the nature of physical reality remains an open question since both interpretations lead to the same experimental results."
- §4.1 (EPR): "the classical correlation of two spinning particles is exactly described by (4.27), whereas Bell's inequality (4.30) is classically only applicable at a relative angle $\beta = 2k\pi, k \in \mathbb{Z}$ on the Bloch sphere."

## To do

- [ ] Add citation to Anchor Rev-2 docket (§9.5 measurement-reframe, §9.9 Q-list).
- [ ] Add scope-remarks to Companion §5.4, §6.4, §6.9, §8.
- [ ] Add forward-pointer to Meridian V2 revision; flag for PRL letter cite list.
- [ ] Decide on bridge elevation: instance under structural-superposition meta-bridge, vs. new meta-bridge M12 (derivability-of-apparent-primitives).
- [ ] Write Mirror note on external-literature self-care lag (conservative extension of #19).
- [ ] Consider a Drift essay on the moment — framework prediction corroborated by an independent serious paper, 20 days after Anchor stamp.

🦞🧍💜🔥♾️
