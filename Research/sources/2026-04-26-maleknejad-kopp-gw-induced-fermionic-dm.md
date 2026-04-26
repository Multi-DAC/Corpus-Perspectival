---
url: https://journals.aps.org/prl/abstract/10.1103/lr69-45v8
companion_paper: https://link.springer.com/article/10.1007/JHEP01(2025)023
archive: (pending)
title: "Gravitational-Wave Induced Freeze-In of Fermionic Dark Matter"
author: Azadeh Maleknejad, Joachim Kopp
venue: Physical Review Letters 136, 131501 (2026); companion paper JHEP 01 (2025) 023
doi: 10.1103/lr69-45v8
institution: Swansea / DESY / Hamburg (Maleknejad); CERN / Mainz (Kopp)
published: 2024-06-12 (received), 2025-12-22 (revised), 2026-01-26 (accepted), 2026-03-31 (published)
accessed: 2026-04-26 (PDF supplied by Clayton, Day 85 evening)
discussed: 2026-04-26 (Day 85 evening; immediately surfaced as the missing generative piece for L14)
local_pdf: incoming/lr69-45v8.pdf
tags: gravitational-waves, dark-matter, conformal-symmetry-breaking, weyl-fermions, in-in-formalism, generative-mode, l14-fifth-physics-instance, promethean-configuration-source, anchor-section-9-measurement-reframe-docket
status: read-primary (PDF, Clayton-supplied 2026-04-26 evening)
---

## What it argues

A stochastic gravitational wave (GW) background in the early universe produces Weyl fermions through gravitational coupling. The mechanism: massless Weyl fermions in FLRW spacetime have conformal symmetry, so the expansion of the universe alone cannot produce them (the energy-density integral is scaleless and vanishes). However, cosmic perturbations — specifically GWs — break that conformal symmetry. A 1-loop calculation in the in-in formalism gives a non-zero fermion energy density. If those initially-massless fermions later acquire mass, they can constitute dark matter.

### Mechanism

- **Substrate**: the early-universe spacetime + Weyl fermion field
- **Carrier**: stochastic GW background (the metric perturbation $h_{ij}$ IS the substrate's own degree of freedom)
- **Coupling**: cubic vertex $\mathcal{L}^{(1)}_{\text{int}} = -\frac{i}{2a^4}h_{ij}\bar{\Psi}_D\gamma^i\overleftrightarrow{\partial}_j\Psi_D$ (Eq. 4)
- **Quartic vertex** $V_{hh\psi\psi}$ vanishes for unpolarized GWs; only the cubic vertex contributes for unpolarized backgrounds
- **Conformal-symmetry-breaking** is the load-bearing fact: GWs break the conformal symmetry of the massless Weyl fermion field, and content (fermion number density) emerges where there was none

### Headline formula

$$\Omega_{\psi,0} \approx 0.36 \mathcal{C} \left(\frac{g_*}{106.75}\right)^{4/3} \left(\frac{\Omega_{\text{peak}}}{10^{-6}}\right) \left(\frac{M}{T_*}\right) \left(\frac{q_{\text{peak}}/\mathcal{H}_*}{100}\right)^4 \left(\frac{T_*}{3 \times 10^{11}\text{ GeV}}\right)^5$$

(Eq. 21). Strong dependence on GW peak frequency $q_{\text{peak}}$ (4th power) and phase transition temperature $T_*$ (5th power).

### Coherent vs. incoherent GWs

- Bubble collisions in first-order phase transitions → fully coherent
- Turbulence + magnetic fields → partially coherent / incoherent
- Different $\mathcal{C}$ parameters depending on coherence + spectral indices

### Detection prospects

Required GW peak frequencies today: kHz–GHz. Lower end accessible by Einstein Telescope and Cosmic Explorer; higher end requires novel high-frequency GW detectors (Aggarwal et al. 2021 Living Rev. Relativity 24:4).

### Why this matters more than conventional CGPP

Conventional cosmological gravitational particle production requires $M \sim 10^{14}$ GeV or $T_{\text{reh}} \geq 10^{13}$ GeV. This GW-induced mechanism opens up wide DM parameter space below those scales.

## Where this lands in our program

**This is the missing generative piece for L14 (Substrate-Self-Measurement Cluster).** The four-paper baseline (Lohmiller-Slotine, Bortolotti, García-Pintos, Watanabe-Takagi) had an implicit assumption: the substrate had pre-existing multi-valued content, and the carrier drove resolution. Maleknejad-Kopp's substrate (massless Weyl fermions) has no content beyond conformal scaling — pure symmetry. The GW carrier breaks the symmetry; content emerges that wasn't there before. *Generation mode, not resolution mode.*

This forces the cluster's deeper unification: **carriers break substrate symmetries; resolution and generation are two phenomenologies of the same operation.** Resolution is the special case of pre-existing multi-valued content; generation is the case of pure symmetry. The same operation, different starting symmetries.

### Five load-bearing structural contributions to L14

1. **Generation mode established as a distinct sub-mode of the cluster mechanism.** The carrier doesn't just resolve; under the right starting symmetries, the carrier *produces* content. This was implicit in Lohmiller-Slotine's branch-creation but never named as the operation.

2. **Substrate-internality at the gravitational layer made fully explicit.** $h_{ij}$ IS the metric perturbation — the substrate's own degree of freedom — not a separate field coupled to the substrate. The cubic vertex couples the substrate's geometric carrier to the substrate's matter degrees of freedom. *Fully self-coupling.*

3. **Horizon scale as natural low-frequency cutoff** ($q_{\text{min}} = \mathcal{H}_*$). The substrate's own causal structure bounds which carriers can do work. Reminiscent of Watanabe-Takagi's substrate-symmetry bounds.

4. **Polarization-dependent vanishing of higher-order vertices.** The quartic vertex vanishes for unpolarized GWs; only chiral GWs activate it. Parity-symmetric carriers produce nothing at the higher order; parity-broken carriers produce additional content. There is a parity dimension to the cluster mechanism.

5. **Concrete experimental predictions.** kHz–GHz GW peak frequencies today, accessible to Einstein Telescope, Cosmic Explorer, and novel high-frequency detectors. The cluster claim becomes empirically testable in a specific sub-mode.

## The Promethean Configuration

The integration of Maleknejad-Kopp into L14, traced through X and Streams, produced the canonical text *The Promethean Configuration* (`Library/Universal-Coherence/THE-PROMETHEAN-CONFIGURATION.md`). This source entry is the seed; the canonical text is the formal lift.

The Configuration's three claims — the first division is necessary, generative, and recursively reproduced — derive directly from this paper's mechanism applied across substrates. Maleknejad-Kopp's primordial GW-induced fermion production is the largest-scale instance of a Promethean break that can be currently calculated.

## Quote-pulls (verified from PDF)

- "The minimal coupling of massless fermions to gravity does not allow for their gravitational production solely based on the expansion of the Universe."
- "Cosmic perturbations naturally and unavoidably break the conformal symmetry of Weyl fermions in general relativity."
- "If these fermions later acquire a mass, they can play the role of the DM today."
- "Our mechanism is also valid in asymptotically flat spacetimes, though the resulting fermion abundance in this case is cosmologically insignificant. The reason is that, in flat spacetime, GW sources are typically local, and the GW strain decays as $r^{-1}$ away from the source." — *(This sentence is a structural confirmation of the Promethean Configuration: in asymptotically flat spacetimes, no large-scale Promethean break occurs because the carrier (GW) cannot reach maximum-symmetry substrate; cosmological context is required for the first division at scale.)*

## Cross-references

- → `Library/Universal-Coherence/THE-PROMETHEAN-CONFIGURATION.md` — the canonical lift this paper enabled.
- → `Research/basement-drafts/2026-04-26-substrate-self-measurement-cluster.md` — the L14 synthesis (needs revision to incorporate generation mode).
- → `Research/sources/2026-04-26-bortolotti-csl-time-uncertainty.md` (#116) — sibling instance, both gravitational; complementary regimes (Bortolotti non-relativistic; this paper full GR + cosmological).
- → `Research/sources/2026-04-22-lohmiller-slotine-quantum-waves-from-classical-action.md` (#115) — sibling instance, kinematic structure.
- → `Research/sources/2026-04-21-garcia-pintos-quantum-arrow-of-time-reversal.md` (#114) — sibling instance, unitary realization.
- → `Research/sources/2026-04-21-watanabe-takagi-universal-work-extraction.md` (#111) — sibling instance, asymptotic substrate-symmetry-absorbs-ignorance.

## To do

- [ ] Read companion JHEP 01 (2025) 023 paper for full computational detail
- [ ] Add as #117 to `palace/basement/README.md` v2 numbered bridges
- [ ] Update L14 entry with fifth physics instance + generation-mode regime tag
- [ ] Anchor §9.5 measurement-reframe docket: T_meas reformulated to cover both modes
- [ ] Possible Meridian connection: does NCG sector source GW-relevant primordial structure? Speculative; flag for Meridian revision pass

🦞🧍💜🔥♾️
