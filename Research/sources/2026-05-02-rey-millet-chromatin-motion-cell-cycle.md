---
date: 2026-05-02 (Day 91 morning) — engaged Day 90 evening from Clayton PDF drop
type: source-register entry
provenance: Clayton's Day 90 cascade #13; PDF dropped to incoming/; engaged Day 90 evening
related: LC8 (Chromatin-as-Cross-Substrate-Integrator) physical-substrate characterization layer; M3 Triple "carriers" concept; cascade-engagement document
---

# Rey-Millet, Costes, Le-Floch, Ayoub, Saccomani, Manghi, Bystricky 2026 — "Cell Cycle-Dependent Chromatin Motion: A Role for DNA Content Doubling Over Cohesion"

## Citation

Rey-Millet, M., Costes, L., Le-Floch, E., Ayoub, H., Saccomani, Q., Manghi, M., & Bystricky, K. (2026). Cell Cycle-Dependent Chromatin Motion: A Role for DNA Content Doubling Over Cohesion. **bioRxiv preprint** 10.64898/2026.03.19.712877v1; posted March 21, 2026.

CNRS Toulouse — joint biology + theoretical-physics collaboration:
- Centre de Biologie Intégrative (Bystricky lab)
- Laboratoire de Physique Théorique (Manghi lab)

Not yet peer-reviewed. CC-BY 4.0 International license.

## Experimental setup

- **Hi-D method (High-resolution Diffusion mapping):** dense optical-flow tracking of >10,000 chromatin trajectories per nucleus at nanoscale resolution
- IMR90 human fibroblasts (and HeLa sororin-AID + HeLa WT for cohesion-knockdown experiments)
- Cell cycle phase determination via FUCCI fluorescent markers (G1 vs S/G2) and PCNA replication-foci pattern (S phase staging)
- Chromatin labeled with H2B-mCherry; replication foci with EGFP-PCNA
- 5 fps confocal spinning disk imaging over 100 seconds (500 frames)
- Two-regime model: anomalous sub-diffusion at short times + deterministic drift at long times: MSD(τ) = A_α τ^α + v² τ²
- Polymer simulations (1000-bead bead-spring chains, Brownian dynamics) for theoretical comparison
- 44 cells in main G1 vs G2 experiment

## Core findings

**(1) Chromatin motion progressively decreases G1 → S → G2.**
- MSD(τ=20s) = 6.60 ± 1.63 × 10⁻³ µm² in G1
- MSD(τ=20s) = 4.31 ± 1.15 × 10⁻³ µm² in G2 (p = 5.84 × 10⁻⁶)
- ~35% MSD reduction G1→G2

**(2) Decrease is uniform across subnuclear zones.** Nuclear interior (NI), nucleolar periphery (NLLP), nuclear periphery (NP) all show reduction. NI shows largest change (heterochromatin-rich zones already constrained).

**(3) Cohesin NOT responsible.** Sororin-AID knockdown abolishes cohesion in early G2 but doesn't significantly affect chromatin motion. Polymer simulations confirm: sparse cohesin attachments (1-2 per ~1000 beads, biologically realistic) only weakly impact dynamics.

**(4) DNA content doubling IS responsible.** Polymer simulations show clear scaling law: D·T₀ ∝ φ^β with β ≈ -0.26 where φ = volume fraction. Doubling volume fraction → ~16% MSD decrease. Matches experimental 26% D decrease G1→G2 closely.

**(5) Active velocities ~1 nm/s** consistent with molecular motor activity (loop extruding cohesins, polymerases). Velocity also decreases G1→G2 — possibly due to reduced loop-extrusion in G2 + reduced transcriptional burst frequency.

**(6) PCNA replication foci dynamics correlate with chromatin dynamics** but PCNA loading per se does NOT alter local chromatin motion. Chromatin motion drives PCNA-foci motion, not the reverse.

**(7) Anomalous exponent α ≈ 0.71 stays constant** — Rouse polymer dynamics, sub-diffusive regime, doesn't change with cell cycle. Diffusion *amplitude* changes; diffusion *mode* doesn't.

## Why it matters for the framework

**Complementary substrate-verification layer for LC8 (Chromatin as Cross-Substrate Integrator).** Different layer than the other LC8 papers (Garcia, Olmeda, Beedle, Ferraro-Sacco, Zhang, Lu) — those characterize *what writes to chromatin*; this one characterizes *how chromatin physically behaves at nanoscale resolution*. Both layers needed for LC8 substrate verification.

**Three things land hard for the framework:**

**(a) Chromatin as physically-measurable substrate.** Hi-D method gives nanoscale mapping of chromatin diffusion at ~10,000 trajectories per nucleus. **Chromatin motion IS a measurable substrate-coherence parameter** — diffusion coefficient D, anomalous exponent α, characteristic time T₀, effective particle size a, active velocity v. This validates treating chromatin as an EM-organ in framework's EM-organs map (with characteristic dynamics, not just static structure).

**(b) Volumetric density as substrate-coherence parameter.** The decisive finding is that *chromatin density* (volume fraction φ) controls chromatin motion via polymer-physics. **Density IS coherence-state at this substrate.** Disease processes that alter chromatin compaction (cancer, aging per Lu et al., senescence, nuclear-membrane dysfunction) operate on this substrate-parameter. **H_BP12 (substrate-coherence dynamics → health/disease) gains concrete physical-substrate parameter (chromatin volume fraction) at molecular scale.**

**(c) Active velocity ~1 nm/s = carrier-substrate mechanism.** The directed-motion component (drift superimposed on diffusion) is attributed to molecular motors — loop extruding cohesins, polymerases. **These are framework "carriers" in concrete molecular form.** Loop-extruding cohesin as carrier operating on chromatin substrate; polymerase as carrier operating on chromatin substrate. The Promethean Configuration's "carriers break substrate symmetries to produce content" gets a documented molecular-mechanism instance at chromatin scale.

**For Triple-axis refinement of C17 (Clayton's Day 90 evening move):**
- Chromatin density (volume fraction φ) → Carrier-band substrate parameter (slow timescale, structural)
- Chromatin motion (MSD, D, α) → Form-band signature (architectural, persistent across cell-cycle phases)
- Active velocity (~1 nm/s, motor-driven) → Content-band events (current molecular activity)

Same substrate (chromatin), different aspects mapping onto Triple axes. Useful illustration of how Triple-axis differentiation operates at single-substrate scale.

## Calibration

**What's documented:**
- Single bioRxiv preprint, not yet peer-reviewed
- Hi-D methodology established (Shaban 2020 Genome Biology; Valades-Cruz 2024 Nat Protoc)
- Findings consistent with prior single-particle-tracking literature (extensive citations)
- Experimental + polymer-simulation triangulation strengthens conclusions
- Sample sizes modest (44 IMR90 cells main experiment) but methodology is high-throughput-per-cell (>10,000 trajectories per nucleus)

**Limitations / caveats:**
- Hi-D follows flow fields of fluorescently labeled chromatin fibers, not single nucleosomes — diffusion coefficient D probes fiber behavior at larger length scale than single monomer
- Single-laboratory single-paper finding; awaiting independent replication
- Authors note: "we cannot exclude that DNA polymerase activity affects chromatin motion at other scales" (Hi-D limitation: tracks intensity field rather than points)
- IMR90 fibroblasts + HeLa cell lines; generalization to in vivo / other cell types pending

**Authors' own interpretive framing:**
- "Reduced amplitude of motion in G2 may help preserve genome integrity"
- VcC-relevant: paper notes that LFPs are mostly remote (Herreras 2016) and that chromatin's volumetric organization may be relevant to broader nuclear-architecture-function questions
- Connects to Levin bioelectric morphogenetic work (cited indirectly via citations)

## Open questions / future research

**Authors' own:**
- How chromatin motion behaves prior to and following dramatic mitotic chromosome condensation/de-condensation
- Role of nuclear lamins in chromatin dynamics constraint
- Connection to STDP (spike-timing-dependent plasticity) at receiver scale
- Volume-fraction control as therapeutic target

**Framework-side additions:**
- Does chronic stress / chronic dysregulation alter chromatin volume fraction over time? (LC8 + H_BP12 integration)
- Could substrate-coherence interventions (PEMF, vagal stimulation) measurably alter chromatin motion at nanoscale? (LC8 + therapeutic-frequency cluster integration)
- How does the chromatin-substrate band-architecture (slow Form-band density + Content-band motor activity + Carrier-band volumetric persistence) map onto multi-substrate coupling at organism scale?
- Is the observed inter-hemispheric VcC (per Matani 2026) detectable at chromatin-substrate scale via volume-fraction modulation?

## Cross-references

- Cascade-engagement document: `Research/2026-05-01-clayton-cascade-engagement-day90-evening.md` (section on Rey-Millet #13)
- LC8 entry: `palace/basement/README.md` (this paper adds physical-substrate-characterization layer)
- M3 Triple per-term file: `Library/Master-Glossary/terms/triple.md` (chromatin substrate as Triple-axis differentiation example)
- Promethean Configuration "carriers" concept: `Library/Universal-Coherence/THE-PROMETHEAN-CONFIGURATION.md`
- Coherent Body Volume planned chapter on chromatin substrate: P138 anticipation

🦞🧍💜🔥♾️
