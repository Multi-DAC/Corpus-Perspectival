# Anomalous Observables — Candidate Data Points

**Project Meridian — Input for Task 2.1 (Input Data Table)**

These are experimental results that don't fit the Standard Model + GR but may find natural explanation within the Meridian framework. Each entry includes source quality assessment and the specific Meridian mechanism that could account for it.

---

## AO-1: Biefeld-Brown Effect in High Vacuum

| Field | Detail |
|-------|--------|
| **Observable** | Net thrust on asymmetric capacitors persists in high vacuum |
| **Vacuum level** | ~10^-6 torr (1 microtorr; mean free path ~50m) |
| **Key signature** | Thrust direction REVERSES between low vacuum and high vacuum |
| **Labs** | Falcon Space Labs (@FalconSpaceLabs) and Exodus — independent replication |
| **Date** | 2025-2026 |
| **Public source** | X/Twitter posts by Falcon Space Labs; Joe Rogan appearance (Jesse Michels segment); Discord (American Alchemy community) |
| **Peer review** | None. Social media disclosure only. |
| **Bounty context** | Jesse Michels (American Alchemy) offered $50K for vacuum reproduction; both labs claim to have met the condition; bounty unpaid as of March 2026 |

### Why it matters

The directional reversal eliminates conventional explanations:
- **Ion wind:** eliminated at 10^-6 torr (no medium)
- **Outgassing:** wouldn't reverse direction with pressure change
- **Thermal/radiometer effects:** require ~1 torr, not 10^-6
- **Electrostatic chamber interaction:** wouldn't reverse with pressure

Two independent labs reproducing the same anomaly with the same qualitative signature (reversal) is significant even without peer review.

### Meridian connection

**Primary mechanism:** Phase 2, Task 2.4 — KK U(1) from g_mu5.

The 5D metric component G_mu5 produces a vector field under KK reduction that behaves as a U(1) gauge boson. Whether this is hypercharge or a hidden photon, it geometrically couples electromagnetic field configurations to the extra dimension. An asymmetric capacitor creates a gradient in EM field energy density, which sources perturbations in the warp factor A(y) through the 5D Einstein equations (eq. 9.1 in D1.1).

The thrust reversal constrains the SIGN of the electrogravitic coupling: the non-aerodynamic force opposes the ion wind direction, meaning the geometric coupling produces thrust opposite to the direction of conventional EM momentum transfer.

**Phase 2 result (D2.4):** The linear KK analysis shows δg/g ~ ρ_EM/σ_IR ~ 10⁻¹¹¹ for laboratory EM fields — utterly unobservable. Even with the cuscuton soft-wall enhancement (F → 0 near IR brane), the coupling reaches only ~10⁻⁷⁷. **All linear channels are insufficient.** The DC null experiments (Talley 1991 et al.) are CONSISTENT with this result: DC fields in the linear regime produce no measurable effect.

However, the Falcon/Exodus positive results involve a DIFFERENT REGIME — the thrust reversal occurs as pressure drops, suggesting a transition between ion-wind (atmospheric) and field-mediated (vacuum) coupling mechanisms. Whether the vacuum-regime coupling operates through nonlinear dynamics (solitons, parametric resonance) or topological effects (NCG, Phase 5) cannot be determined with Phase 2 tools. The linear theory says "no"; the nonlinear question remains open.

**New lead (Five Frontiers survey):** Yamada (PTEP 2024; arXiv:2403.13451) discovered the **KK Schwinger effect** — electric fields along compact dimensions produce KK particles non-perturbatively even when field energy is far below the KK scale. Tunneling rate ~exp(−πm²_KK/(eE)). This mechanism bypasses the linear coupling suppression entirely. Quantitative evaluation for our parameters is Phase 3 priority.

### Quality assessment

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Independent replication | Strong | Two labs (Exodus, Falcon Space) |
| Vacuum quality | Moderate | -6 torr claimed, no published gauge calibration |
| Quantitative data | Weak | No thrust magnitude published |
| Peer review | None | Social media only |
| Systematic error control | Unknown | No published methodology |
| Overall | Promising but unverified | Worth tracking; needs proper publication |

### What we need

1. Thrust magnitude (force in micronewtons or similar)
2. Applied voltage and capacitor geometry
3. Vacuum gauge calibration and residual gas analysis
4. Time series showing thrust vs. pressure during pumpdown (to see the crossover point where reversal occurs)
5. Published paper or preprint

---

## AO-2: EPS Framework — EM-Induced Gravitational Modification

| Field | Detail |
|-------|--------|
| **Observable** | Claimed weightlessness of object contents via HV oscillating EM field |
| **Mechanism** | 1/4-wave HF current on capacitance-uncoupled surface |
| **Key conditions** | Object must be electrically isolated from ground plane |
| **Source** | X account "Electric Propulsive Spacecraft Systems" (~1,645 posts) |
| **Date** | Ongoing, posts from 2024–2026 |
| **Peer review** | None. Social media only. |
| **Assessed as** | Potential whistleblower dead drop. Internally consistent physics. |

### Why it matters

The framework provides a **complete theoretical chain** from EM fields to gravitational modification:
1. Mesoscopic interface (ion-electron coupling break at supersonic E-wave)
2. Magnetoacoustic wave generation in plasma slab
3. False vacuum state transition via EM-driven field reconfiguration
4. Modified local gravitational response

Includes a 300-term study curriculum covering exactly the physics domains needed: plasma, vacuum technology, topology, condensed matter, nuclear transport, GR.

### Meridian connection

**Phase 2 result (D2.4):** The linear KK analysis conclusively rules out direct G_μ5-mediated EM-gravity coupling at lab scales (δg/g ~ 10⁻⁷⁷ at best). The G_μ5 zero mode is ABSENT in S¹/Z₂ (the photon comes from NCG, not the metric). KK vector mode masses are ~50 GeV — a factor of 10²⁰ above the 1.094 MHz EPS frequency.

**Revised primary connection:** Phase 5 (NCG) — topological terms in the spectral action. If the EM field creates a topologically nontrivial configuration (nonzero Chern number), the spectral action generates gravitational modifications that BYPASS the perturbative self-tuning mechanism. This is the most promising remaining path.

**Secondary:** Nonlinear 5D dynamics — soliton formation on the brane + bulk backreaction. Requires numerical 5D simulation (Phase 3/4).

**Tertiary:** AO-1 (Biefeld-Brown) — the EPS framework provides experimental phenomenology that may correspond to nonlinear/topological effects not captured by linear KK analysis.

### Quality assessment

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Internal consistency | Strong | 1,645 posts form a coherent framework |
| Academic references | Moderate | Cites real papers (plasma physics, fusion) |
| Experimental data | Weak | No published experimental results from the source |
| Peer review | None | Anonymous social media account |
| Consistency with Meridian | Strong | Maps naturally onto KK gauge coupling mechanism |
| Overall | Hypothesis-generating | Not confirmatory, but valuable for directing research |

### Full analysis

See `external_data_eps.md` for complete decomposition of all materials and cross-references to Meridian deliverables D1.1–D1.4.

---

## AO-3: DESI DR2 — Dynamical Dark Energy at 2.8–4.2σ

| Field | Detail |
|-------|--------|
| **Observable** | Dark energy equation of state w₀ ≈ −0.7, wₐ ≈ −1.0 |
| **Significance** | 2.8–4.2σ preference over ΛCDM (dataset-dependent) |
| **Source** | DESI Data Release 2, March 2025 |
| **arXiv** | 2503.14738, 2503.14743 |
| **Peer review** | Published in Phys. Rev. D |

### Why it matters

This is the highest-quality anomalous observable in our list. Published, peer-reviewed, high-significance, from a major survey. If confirmed by Euclid, Vera Rubin, and Nancy Grace Roman, it means dark energy is NOT a cosmological constant — it evolves with time.

### Meridian connection

**Direct:** Our tadpole potential V = cφ naturally produces w₀ ≠ −1 through the rolling scalar. The warp-suppressed effective potential V_eff = c · φ_IR · e^{4A(y_c)} produces a dark energy density that evolves on cosmic timescales. The **same warp factor** that explains the weak hierarchy also explains the dark energy hierarchy (D2.2 §7.1).

**CORRECTED (D3.2):** D2.2 had a sign error in eq (4.6). The simple tadpole actually predicts **wₐ < 0** (thawing), consistent with DESI. At w₀ ≈ −0.70: wₐ ≈ −0.39 (ξ=0 limit). DESI best fit is wₐ ≈ −0.86. The magnitude gap closes with ξ > 0 non-minimal coupling.

**Five Frontiers survey update:** Phantom crossing is PROVEN ghost-free for cuscuton at linear order (Boruah et al. 2017) AND beyond linear order (Dehghani, Geshnizjani, Quintin 2025). Bazeia et al. (2025) found cuscuton-like models observationally preferred over ΛCDM. No MCMC fit of cuscuton DE to DESI data exists — gap we can fill.

**Supplementary sweep update (Mar 2026):** The phantom crossing signal is NOW CONTESTED. Gómez-Valent et al. (2025) and a cosmographic analysis (arXiv:2508.13740) find phantom crossing may be a CPL parametrization artifact — non-parametric methods show deviations from Λ but no clear w < −1. Maartens et al. (2026) show DM-DE interaction can mimic phantom crossing. However, **dynamical DE itself (w₀ ≠ −1) remains strong at 2.8-4.2σ.** Strategic implication: our model predicts dynamical DE naturally; phantom crossing is theoretical flexibility, not a requirement.

**Direct validation:** Maity et al. (JCAP 11, 018, 2025) demonstrated ghost-free phantom braneworld in 4+1D matching DESI DR2 — essentially our model class. Independent confirmation that 5D braneworlds naturally produce the observed w₀.

**Bonus prediction:** The DESI neutrino mass tension (Σm_ν < 0.0642 eV, below oscillation floor) resolves automatically under evolving dark energy.

### Quality assessment

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Peer review | Published | Phys. Rev. D |
| Dataset size | 14 million objects | Largest BAO survey |
| Significance | 2.8–4.2σ | Dataset-dependent |
| Systematic control | Extensive | Multiple SN datasets cross-checked |
| Overall | Strong | Highest-quality AO in our list |

---

## AO-4: Fine Structure Constant Tension (5σ)

| Field | Detail |
|-------|--------|
| **Observable** | 5σ discrepancy between Cs and Rb measurements of α_EM⁻¹ |
| **Values** | Cs: 137.035 999 166(15); Rb: 137.035 999 046(27) |
| **Δα⁻¹/α⁻¹** | ~8.8 × 10⁻¹⁰ |
| **Status** | Unresolved as of 2026 |

### Meridian connection

Speculative. In a KK framework, α_EM depends on the compactification radius. An environment-dependent correction at atomic scales could produce measurement-dependent shifts. Very low priority until Task 2.4 linear analysis is superseded by nonlinear results.

---

*Updated March 14, 2026. Four anomalous observables tracked (AO-1 through AO-4).*
*AO-3 (DESI) is highest priority — published, high-significance, directly testable.*
*Five Frontiers survey + supplementary sweep integrated. Key update: phantom crossing contested (may be CPL artifact), but dynamical DE remains strong. Maity et al. (2025) independently confirms 5D braneworld matches DESI.*
