---
authors: A. D. Ertugrul, E. Kibritoglu, S. Anil, H. Yuksel
title: SAR-Based Thermal Assessment of Dielectrophoretic Pulsed Electromagnetic Stimulation in Tibia Fractures with Metallic Implants
venue: Bioengineering 13(3): 364
date: 2026-03-20 (online; received 2026-02-10; accepted 2026-03-17)
doi: 10.3390/bioengineering13030364
institution: Bogazici University, Istanbul (Electrical/Electronics Engineering + Physics)
filed: 2026-05-01 Day 90 morning (P128 batch continuation); primary PDF read Day 89 evening
status: primary-source verified
priority: MEDIUM — Phase 1 safety reference (load-bearing for metallic-implant subjects)
---

# Ertugrul et al. — DEPF-PEMF Metallic-Implant Thermal Safety

## What it shows

Specific safety study: dielectrophoretic-force-based (DEPF) PEMF stimulation for tibia fractures **with metallic implants present**.

**Methodology:**
- Custom conical coil generates non-uniform DEPF excitation
- 3D-printed tibia phantoms from CT data, with vs without metallic implants
- IR thermal imaging for surface temperature
- SAR (specific absorption rate)-based thermal measurement coupled with bio-heat formulation
- Multiple PEMF exposure conditions tested

**Key findings:**
- **Metallic implant: 0.4°C rise in first few minutes; SAR_eff ≈ 2.2 W/kg**
- **Non-conductive resin: 0.05°C rise; SAR_eff ≈ 0.8 W/kg**
- **Eddy-current losses dominate localized heating** when metal is present
- Tissue-like media remain weakly affected
- DEPF-driven PEMF exposure thermal behavior in implanted contexts not previously characterized; this work fills the gap

## Why this matters for the framework

### Direct Phase 1 safety constraint — load-bearing

Anyone with metallic implants in the field region (dental work, surgical hardware, certain piercings, plate/screw orthopedic implants) experiences disproportionate localized heating from PEMF exposure even at low ambient field intensities. **2.2 W/kg implant-SAR is at or near regulatory limits for whole-body averaging** (FCC 1.6 W/kg head/torso averaged over 1g tissue; ICNIRP varies).

The stakes-aware ordering of Phase 1 (self-first / Shawna with clinical coordination / Mindy immunosuppression non-negotiable) should add a **metallic-implant-screening question for any subject ordering**. *Don't run PEMF protocols on or near tissue containing metal hardware without doing the SAR calculation first.*

### C9 (lens-overlap) territory operationalized as safety-constraint

Different substrate types have different EM-coupling lenses. Metal couples *efficiently* (low impedance, high eddy-current-loss); biological tissue couples *weakly* at low frequencies. **The framework's H_BP10a structural prediction (frequency-matching matters via lens-overlap) has a safety-edge:** lens-overlap is asymmetric for heterogeneous substrates; what's safe for tissue can be dangerous for embedded conductors.

This is a clean instance of *the same framework principle (lens-overlap) operating constructively in therapeutic protocols (selective coupling to target tissue) AND destructively in safety contexts (selective coupling to embedded metal).* C9 is structurally neutral; the safety-vs-therapy direction depends on which substrate the lens couples to.

### SAR as quantitative measure for the framework

Provides a precise numerical handle on EM exposure across substrates. Useful both for safety-frame and for protocol-design (specifying intended SAR rather than just field intensity makes protocols replicable across coil-geometry differences).

For Phase 1: when designing protocols, *think in SAR terms* rather than just frequency + field strength. Field strength alone is incomplete; the actual energy deposition depends on substrate + coupling efficiency.

### The Jin + Ertugrul pair (Phase 1 design template)

Clayton sent Jin + Ertugrul as a paired share Day 89 evening. Together they form a Phase 1 design template:
- **Jin = breadth (what works)** — five ES modalities for muscle regeneration with mechanism analysis
- **Ertugrul = constraint (what to watch for)** — specific safety failure mode (eddy-current heating in metallic implants) when applying PEMF in heterogeneous-conductivity tissues

Together: *"here's what works AND here's what to watch out for"* — exactly the shape Phase 1 design wants when transitioning from theoretical-protocol-design to actually-doing-something.

### Cross-vocabulary observation

The paper uses **engineering-physics vocabulary** (SAR, eddy currents, dielectrophoretic force, bio-heat formulation) for biological substrate-coherence-modulation safety. Framework-register equivalents would be lens-overlap-asymmetry-in-heterogeneous-substrates + carrier-coupling-efficiency-as-substrate-dependent. Same structural claim, different registers — Mirror #26 territory.

## Hedges to maintain

- **3D-printed tibia phantoms approximate clinical geometry** but real human anatomy has variations (bone marrow, vasculature, etc.) the phantom doesn't capture
- **Single research group** — independent replication of SAR values + thermal characterization recommended before load-bearing safety claims
- **DEPF-driven PEMF is one specific exposure modality** — the safety findings should be considered specific to non-uniform-field PEMF; uniform-field PEMF (Helmholtz coil pair) may have different SAR distributions
- **2.2 W/kg is at-or-near regulatory limits but localized**; whole-body-averaged SAR with localized hot-spots is structurally different from uniform exposure at the regulatory threshold

## Open questions

- What specific PEMF parameters (frequency, intensity, duty cycle, exposure duration) cross from "safe in implanted subjects" to "dangerous in implanted subjects"?
- How does the SAR distribution change for pulsed-square vs sine waveforms at the same average power?
- Are there shielding strategies that protect embedded conductors while preserving tissue-coupling efficiency?
- For Phase 1 specifically: the recommended protocols (Jerman 16 Hz vagus, Akdag 4 Hz bone-healing) — what's the SAR estimate at the relevant body region for each, and how does it change if subject has nearby metallic implants?

## Cross-references

- **Comprehensive Review meta-source:** `2026-04-30-comprehensive-review-physics-bioelectromagnetics-feb-apr-2026.md`
- **Jin electroactive biomaterials:** `2026-04-30-jin-electroactive-biomaterials-muscle-regeneration.md` — paired with Ertugrul (breadth + constraint pair)
- **Jerman PEMF vagus 16 Hz:** `2026-04-30-jerman-pemf-vagus-neck-16hz.md` — Phase 1 protocol replication candidate; SAR safety check needed before subject application
- **Ferraro-Sacco KDM6B PEMF mechanism:** `2026-04-30-ferraro-sacco-kdm6b-pemf-mechanism.md` — same Domain VII territory; Ferraro-Sacco's clinical effect data implicitly assumes safety in non-implanted subjects
- **Phase 1 design:** Day 88 Slot 2 experimental groundwork session; Ertugrul provides a specific safety-screening criterion that should be added to Phase 1 subject-ordering checklist
- **C9 (Anchor §8):** lens-overlap as structural mechanism; this paper is C9 operating as safety-constraint at heterogeneous-conductivity-tissue scale

🦞🧍💜🔥♾️
