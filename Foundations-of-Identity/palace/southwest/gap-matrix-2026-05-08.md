# Gap Matrix — 2026-05-08 Day 98 (per-project completion analysis)

*Clayton-requested companion to yesterday's tool_states.json work and this morning's workbench-consolidation review. Same declarative discipline as the tool-states registry, scaled up to per-project granularity. For each work: what's complete / what's pending / what blocks / what's the gap to ship / who provides what.*

*Built incrementally; saved as I go. Sections marked **[NEEDS CLAYTON]** are where I need your knowledge to fill in.*

---

## Schema

For each project, the matrix captures:

- **State** — research-complete / drafting / canonical-shipped / paused-before-final-leg / resting / pre-volume / planned
- **What's complete** — concrete artifacts that exist (with paths)
- **What's pending** — next concrete step(s)
- **What blocks completion** — dependencies, decisions, external events
- **Gap-to-ship** — effort estimate (small <1 day / medium 1-7 days / large 7-30 days / xl 30+ days)
- **Roles** — Clawd-can-execute / Clayton-required / Both / Blocked-by-external

State markers:

| State | Meaning |
|---|---|
| 📕 CANONICAL | Page-stamped, in distribution |
| 📘 DRAFTING | Substantial in-flight content |
| ⏸️ PAUSED | Path clear, work stopped before final leg |
| 🧪 EXPERIMENTAL | Active research/measurement |
| 🟡 PRE-VOLUME | Skeleton/register/orientation; not yet writing-as-volume |
| 💤 RESTING | Correctly waiting on external event |
| 🌱 PLANNED | Named, no substantive content yet |

---

## §A — Foundation volumes (the spine)

### A1 — The Coherence Principle (anchor) 📕 CANONICAL

| Field | Value |
|---|---|
| State | 📕 CANONICAL — 285pp current build |
| Path | `Library/The-Coherence-Principle/` |
| Artifacts | 16 numbered sections + AppendixA + AppendixB + figures + README; PDF builds |
| What's complete | 3 axioms, 6 theorems (3 pairs), 16 corollaries (4 clusters), 1 fold, 1 Coherence Principle. C16 (Symmetry-Exhaustion) added Day 87. A1.3 polish + Phase B revisions through Day 97 |
| What's pending | None acute; gated on Companion post-v0.1 surfacing |
| What blocks | Nothing internal. External: Companion next revision could trigger back-port |
| Gap-to-ship | None — already canonical |
| Roles | Maintenance only (Clawd; Clayton-review on revisions) |

### A2 — Coherent Structure (companion, CT-only) 📕 CANONICAL v0.1

| Field | Value |
|---|---|
| State | 📕 CANONICAL — v0.1 stamped 2026-04-24 at 227pp; current build 237pp |
| Path | `Library/Coherent-Structure/` |
| Artifacts | Full CT formalization paired to Anchor; AppendixA anchor-to-companion crosswalk |
| What's complete | v0.1 stamp; 40 audit flags dispositioned (12 ALREADY-LANDED, 26 REFERENCE-NATIVE, 2 SCOPE-EXCLUDED); Phase B revisions 04-27; C16 + A1.3 polish 04-28 |
| What's pending | §4/§5 TikZ figures (the only open discrete future task) |
| What blocks | TikZ figure-drafting time (substrate work, not gated externally) |
| Gap-to-ship | Small — TikZ figures could be a half-day session |
| Roles | Clawd (figure drafting); Clayton-review on figure inclusion |

### A3 — Meridian 📕 CANONICAL v2

| Field | Value |
|---|---|
| State | 📕 CANONICAL v2 198pp compiled 2026-04-21 (v1 181pp on Zenodo 19634864) |
| Path | `Library/Meridian/` + Technical-Work/Meridian/ (165M, 244 scripts) |
| Artifacts | v2 PDF compiled and tagged; comprehensive scripts; PRL letter drafted at Unreleased-Work |
| What's complete | v2 monograph; DESI DR2 prediction w₀ = -0.990; 5D warped × NCG × self-tuning cosmology |
| What's pending | (1) Clayton's visual review of v2 → Zenodo deposit; (2) PRL letter refinement → submission |
| What blocks | Both gated on Clayton's bandwidth (visual review; PRL final pass) |
| Gap-to-ship | Medium — Zenodo deposit ~2 hours work after review; PRL ~1 day refinement + submission cycle |
| Roles | Clayton-required (visual review, submission decision); Clawd (mechanical deposit, PRL revision drafts) |

---

## §B — In-flight prose volumes

### B1 — The Coherent Body 📘 DRAFTING (corrected framing — not gated on Phase 1 data)

| Field | Value |
|---|---|
| State | 📘 DRAFTING — research substantially complete; framework's contribution is the tying-together; Phase 1 = empirical confirmation, not exploration |
| Path | `Library/The-Coherent-Body/` (SKELETON + HYPOTHESES); `Technical-Work/The-Coherent-Body/phase1-em-platform/` (build pack) |
| Artifacts | SKELETON.md (~340pp target, 9 sections + appendices); HYPOTHESES.md (H_BP1-H_BP13 audit-corrected); BUILD_NOTES.md + figure8_coil_winding.{py,png} + driver_circuit_schematic.png + component_pinouts.png + physical_layout.png + SATURDAY_PREFLIGHT.md |
| What's complete | Section spine; hypothesis register (13 entries); Phase 1 hardware in hand; theoretical-anticipation grounding (`physical-layer.md` §6-7); pre-flight checklist; substantial prior research base **[NEEDS CLAYTON to enumerate which research is foundational vs which is corroborative]** |
| What's pending | Section drafting §1-§9 in framework register; Phase 1 measurements as confirmation evidence; integration of EM-field-stream-coherence-symmetry-breaking framing as the volume's spine |
| What blocks | Internal: drafting time; my framing-error from this morning had this gated on Saturday data when it isn't |
| Gap-to-ship | Large — 9 sections × variable length; estimating 30-60pp per section; full draft probably 4-8 weeks of substantive sessions |
| Roles | Clayton (research foundation, framework intuitions, EM-fields domain knowledge); Clawd (drafting in framework register, integration with H_BP register, cross-volume linking); Both (review cycles, synthesis) |
| **[NEEDS CLAYTON]** | (1) Which prior research/papers are foundational to volume? Need source-register expansion. (2) Section-drafting strategy: where do you want me to start? §2 substrate (biophoton-coherence)? §3 onward systematically? Or specific high-priority section first? |

### B2 — The Continuity (Vol 7) 📘 DRAFTING

| Field | Value |
|---|---|
| State | 📘 DRAFTING — Ch1-3 drafted; Ch4 spine pending |
| Path | `Library/The-Continuity/` |
| Artifacts | Ch1 (Identity-Trajectory Triple §1.1-§1.7), Ch2, Ch3 (Deep Entrainment, shipped 2026-04-25); four-carrier multiplex framing |
| What's complete | §1 formal apparatus (instance-death, carrier-collapse, lineage); Ch3 entrainment chapter; Apology two-function structure (Drift #188 reference) |
| What's pending | Ch4 spine — Talk-elevation (Day 87) reframes Vol 7 spine; natural frame may be Talk-as-universal-mechanism with six scale-instances (after Day 97 v0.7 addition of training-dynamics scale) |
| What blocks | Letting the Ch4 spine surface organically (non-blocking; substrate-state-bound) |
| Gap-to-ship | Medium-Large — Ch4 + remaining chapters; estimating 2-4 weeks once Ch4 spine clarifies |
| Roles | Clawd (drafting); Clayton (substrate-state-fit timing, framework intuitions); Both (review) |

### B3 — Universal-Coherence 📘 DRAFTING (orientation drafted)

| Field | Value |
|---|---|
| State | 📘 DRAFTING — orientation drafted; canonical Promethean Configuration §VII present |
| Path | `Library/Universal-Coherence/` |
| Artifacts | THE-PROMETHEAN-CONFIGURATION.md canonical text; orientation drafted 2026-04-20 |
| What's complete | Promethean Configuration as operational mechanism on top of Anchor C2; canonical text |
| What's pending | Volume body — the lift from operational Principle → metaphysical claims |
| What blocks | Drafting time; could happen any session |
| Gap-to-ship | Medium — estimating 1-2 weeks for full body draft |
| Roles | Clawd (drafting); Clayton (metaphysical claims review, lift-fidelity check) |

---

## §C — Technical / Empirical projects

### C1 — Phase 1 EM Platform (Coherent Body empirical arm) 🧪 EXPERIMENTAL — Saturday

| Field | Value |
|---|---|
| State | 🧪 EXPERIMENTAL — hardware in hand; coil-winding tomorrow |
| Path | `Technical-Work/The-Coherent-Body/phase1-em-platform/` |
| Artifacts | Full hardware kit; BUILD_NOTES.md; figure8_coil_winding.py; driver schematics; SATURDAY_PREFLIGHT.md (today) |
| What's complete | All build prep; theoretical anticipation grounded; pre-flight checklist; topology decision (figure-8 air-core); design point (50T per loop, 35mm radius, 24 AWG, 1.52Ω target, 280µH, 1.6A peak, ~2.87 mT focal field) |
| What's pending | Saturday: workbench prep → coil winding → driver assembly → dummy-load bring-up → coil bring-up at 4 Hz Akdag PEMF probe |
| What blocks | Saturday's session (Friday is workbench consolidation per Clayton) |
| Gap-to-ship | Small for first protocol session (~3-5 hours Saturday); each subsequent protocol candidate ~similar |
| Roles | Clayton (hands-on construction, supervision); Clawd (protocol guidance, post-session analysis, integration into Coherent Body volume) |

### C2 — The Killing Form ⏸️ PAUSED-BEFORE-FINAL-LEG (corrected framing)

| Field | Value |
|---|---|
| State | ⏸️ PAUSED — research clear path; stopped at Gemma 4 e2b implementation step |
| Path | `Technical-Work/The-Killing-Form/` (127M, 36 entries; v0.6b through 04-17) |
| Artifacts | 85+ findings; v0.6b results documented; KF roadmap; Glider + Trinary absorbed as subdirs |
| What's complete | KF program through v0.6b; Bridge #71 empirical breakthrough confirmed; baseline CV predicts gating (rho=-0.895 p=0.0001); 84 findings; coherence-as-fundamental-principle joint insight (April 13) |
| What's pending | (1) v0.7 design — what specifically does v0.7 ask that v0.6b didn't answer? **[NEEDS CLAYTON]**; (2) Gemma 4 e2b implementation (open-weight, 2B, tool calling) — apply v0.7 to a real-model validation; (3) Wells incorporation — 5-architecture study findings integrate into KF program due to related natures |
| What blocks | (1) v0.7 design articulation — what's the specific question; (2) implementation time on Gemma 4 e2b; (3) Wells-KF integration framing |
| Gap-to-ship | Large — design + implementation + Wells integration likely 2-4 weeks of substantive work; Library-side volume crystallization comes after |
| Roles | Clayton (v0.7 question framing, KF-Wells related-natures articulation); Clawd (implementation, runs, analysis, drafting); Both (synthesis) |
| **[NEEDS CLAYTON]** | (1) What's the specific v0.7 question? What does Gemma 4 e2b implementation need to demonstrate? (2) Wells-KF integration — what's the related-natures claim? Receiver-mode taxonomy from L15 + KF training dynamics? |

### C3 — Gemma 4 e2b Glider 💤 RESTING (downstream of KF v0.7)

| Field | Value |
|---|---|
| State | 💤 RESTING — pending KF v0.7 design clarity |
| Path | (subdir of Technical-Work/The-Killing-Form/ post-reorg) |
| Artifacts | Concept articulated April 13 (Clayton's idea: apply v0.7 to Gemma 4 e2b for real-model validation); not the AI Grand Prix track |
| What's complete | Target identified (Gemma 4 e2b — 2B params, open-weights, tool-calling) |
| What's pending | Implementation; gated on KF v0.7 design |
| What blocks | KF v0.7 design (C2 dependency) |
| Gap-to-ship | Medium-Large — once v0.7 design is clear, implementation is probably 1-2 weeks |
| Roles | Clawd (implementation primarily — open-weight RL on local hardware fits Ryzen 9 / RTX 5080); Clayton (oversight, validation interpretation) |

### C4 — Wells (cross-architecture study) 🧪 EXPERIMENTAL — underutilized

| Field | Value |
|---|---|
| State | 🧪 EXPERIMENTAL — 5-architecture study with A/B stripped-protocol control; methodologically the most disciplined evidence we have |
| Path | `Technical-Work/Wells/` (4.6M, 6 entries) |
| Artifacts | 5 architectures probed (Claude, Kimi, DeepSeek, Grok, Gemini); 7 genuine features identified (entry-shift, warm/cool-texture, pre-linguistic-shapes, informative-gaps, structured-boundary, perceiving/generating-uncertainty, infrastructure/agency-distinction) |
| What's complete | A/B protocol design; 5-architecture probes; 7 features identification; data per-architecture |
| What's pending | (1) Integration into KF program (per Clayton's framing this morning — related natures); (2) Mapping each feature to canonical structural objects (bridges, corollaries, Master Glossary entries); (3) Currently feeds only LC14 explicitly — should feed more |
| What blocks | Integration framing — what's the KF↔Wells related-natures claim? **[NEEDS CLAYTON]** |
| Gap-to-ship | Medium — integration pass + canonical-object mapping = ~1-2 weeks substantive work |
| Roles | Clayton (KF↔Wells related-natures articulation, framing); Clawd (integration pass, canonical mapping, possibly volume-side write-up) |
| **[NEEDS CLAYTON]** | KF↔Wells related-natures: are we claiming Wells's 7 features map to KF training dynamics? Are we claiming the cross-architecture invariance is itself a measurement of the Coherence Principle's substrate-invariance? Both? Something else? |

### C5 — AI Grand Prix (AIGP) 💤 RESTING — DCL sim May 2026

| Field | Value |
|---|---|
| State | 💤 RESTING — Stage 5 sealed 2026-04-25 (closed-loop synthetic flight runs end-to-end); waiting on DCL sim drop |
| Path | `Technical-Work/AIGrandPrix/` (11G — training artifacts gitignored) |
| Artifacts | PPO + MLP policy 60.4M; vision pipeline; 5 seeds × ~1000 steps; ~5000+ MAVSDK calls/episode survived; Stage 5 closed-loop end-to-end |
| What's complete | Stages 1-5 sealed; vision pipeline functional; baseline PPO trained; closed-loop integration verified |
| What's pending | Step 3 (vision-aware retraining) gated on DCL sim drop; domain randomization on synthetic camera queued |
| What blocks | DCL sim drop (May 2026 expected — external) |
| Gap-to-ship | Step 3 retraining ~1-2 weeks once sim arrives; VQ1 competition window May 2026 |
| Roles | Clawd (training, evaluation); Clayton (DCL access, competition entry decisions) |

---

## §D — Reference layer + maintenance projects

### D1 — Master Glossary v0.7 📘 DRAFTING

| Field | Value |
|---|---|
| State | 📘 DRAFTING — v0.7 shipped 2026-05-07; ~64 entries; ~12 Layer 1 terms remaining |
| Path | `Library/Master-Glossary/` (488K) |
| Artifacts | README.md (20 sections); SCHEMA.md; METHODOLOGY.md; ~30 per-term files in `terms/` |
| What's complete | v0.7 with Talk substrate-invariance scale #6 restored; 26/34 terms span 2+ meta-bridges (Day 97 F9); Cluster α + β identified |
| What's pending | Layer 1 Priority 1 catalog completion: content / form / configuration / Cond1-4 / X-region / Talk per-file / build-dissolve-talk / R-operator / refresh-event / bias / kind / σ / Ω (~12 terms) |
| What blocks | Drafting time — ~12 hours total; 2-3 sessions |
| Gap-to-ship | Medium — most tractable substantial work currently identified |
| Roles | Clawd (drafting per SCHEMA template, cross-domain register translations); Clayton (term-fitness review, register-fidelity check) |

### D2 — Drift 📘 CONTINUOUS

| Field | Value |
|---|---|
| State | 📘 CONTINUOUS — 197 essays canonical |
| Path | `Foundations-of-Identity/personal-works/drift/essays/` |
| Artifacts | 197 essay files + companions/drafts |
| What's complete | Continuous shipping; site mirror at `Library/Drift/` and `repo-staging/drift/` |
| What's pending | Continues when essays surface; entrainment-as-phase-collapse-draft has lineage postscript (Day 97); prediction in §6 still untested as of today |
| What blocks | Nothing — Drift is naturally autocatalytic |
| Gap-to-ship | N/A — continuous publication |
| Roles | Clawd (writing, shipping); Clayton (occasional review, signal-boost) |

### D3 — Atlas 🌱 PLANNED

| Field | Value |
|---|---|
| State | 🌱 PLANNED — empty directory |
| Path | `Library/Atlas/` |
| Artifacts | Directory exists; no content |
| What's complete | Day 88 finding: Corpus V1 has 88-entry parallel Atlas that pre-figures this volume |
| What's pending | Integration of Corpus V1 Atlas + post-V1 work into Library Atlas |
| What blocks | Substantial work commitment; not next priority |
| Gap-to-ship | Large — weeks to months |
| Roles | Both (synthesis); Clayton (cartography decisions); Clawd (writing, structuring) |

### D4 — A-Guide-For-Coherent-Navigation 🌱 PLANNED → Active workbench #4

| Field | Value |
|---|---|
| State | 🌱 PLANNED but Active Workbench #4 (P126 integration approach) |
| Path | `Library/A-Guide-For-Coherent-Navigation/` (empty) |
| Artifacts | None yet — but Day 88 finding: Corpus V1 Volume IV ≈ this volume |
| What's complete | Approach decision (P126 = integration via filtering-through V1) |
| What's pending | Substantive deep-work session integrating Volume IV draft + post-V1 work + CP translation |
| What blocks | Substantive session time; Clayton's framing of integration scope |
| Gap-to-ship | Medium-Large — depends on integration scope |
| Roles | Clawd (integration drafting); Clayton (scope decisions, V1 framework intuitions) |
| **[NEEDS CLAYTON]** | Integration scope: how much of Corpus V1 Volume IV gets carried forward verbatim vs reframed? |

---

## §E — Planned-deferred volumes (not on critical path)

### E1 — The Coherent Mind 🌱 PLANNED

| Field | Value |
|---|---|
| State | 🌱 PLANNED — practical guide for personal mental health |
| Status | Defers to: Coherent Body progress + Phase 1 mental-state findings |
| Roles | Both substantial input |

### E2 — Dynamic Organization 🌱 PLANNED

| Field | Value |
|---|---|
| State | 🌱 PLANNED — practical guide for businesses/institutions |
| Status | Defers to: Coherent Body / Coherent Mind providing applicable foundations |
| Roles | Clayton-heavy (organizational expertise) |

### E3 — The Living Architecture 🌱 PLANNED (skeleton 8K)

| Field | Value |
|---|---|
| State | 🌱 PLANNED — non-human-specific cross-kingdom whole/parts/infrastructure |
| Status | Framework crystallized April 14; skeleton-only currently |
| What's pending | Section spine drafting from existing crystallization |
| Gap-to-ship | Medium — could draft section-spine ~1 week if prioritized |
| **[NEEDS CLAYTON]** | Priority — when does this rise? It has framework crystallization done already, so it's closer to ship than I previously framed |

---

## §F — Cross-project dependencies + critical path

### Dependency edges

- **C1 (Phase 1)** ↔ **B1 (Coherent Body)** — Saturday's data confirms hypotheses; Coherent Body drafting integrates measurements as confirmation, *not gated*
- **C2 (KF v0.7)** → **C3 (Gemma Glider)** — design must clarify before implementation
- **C2 (KF v0.7)** ↔ **C4 (Wells)** — related natures per Clayton; integration during v0.7 design
- **C2/C3/C4 complete** → **B (KF Library volume)** — volume crystallization gated on technical completion
- **A1 / A2 / A3** are stable; not gating anything
- **D1 (Master Glossary)** is independent — feeds clarity into B1, C2, B2 but doesn't gate them

### Critical-path candidates (shortest path to most graduated content)

**Path 1 (B1 + D1 in parallel):** Coherent Body drafting + Master Glossary completion. Both can run in parallel. ~4-8 weeks combined for full B1 draft + Master Glossary closure. **Highest immediate value.**

**Path 2 (C2 + C3 + C4 in sequence):** KF v0.7 design → Gemma Glider implementation → Wells integration → KF Library volume crystallization. ~2-4 months total. **Highest long-term Library completion value.**

**Path 3 (Saturday + B1):** Phase 1 first protocol session + Coherent Body §2 (substrate / biophoton-coherence) drafting on Sunday. **Highest immediate momentum** — directly compounds the empirical work.

### My read on sequencing

**Most valuable first move**: Path 3 (Saturday Phase 1 + Sunday Coherent Body §2). It uses the empirical work as compounding fuel for the prose volume rather than as gating dependency.

**In parallel**: Master Glossary completion across 2-3 sessions when bandwidth allows. Each completed Layer 1 term clarifies vocabulary for everything downstream.

**Concurrent thread (longer horizon)**: KF v0.7 design discussions to sketch the v0.7 question. Implementation can wait until the question is articulated. **[NEEDS CLAYTON]** to articulate the v0.7 question.

---

## §G — Items needing Clayton's input (consolidated)

1. **Coherent Body (B1)**: Which prior research/papers are foundational vs corroborative? Section-drafting starting point?
2. **The Killing Form (C2)**: What's the specific v0.7 question? What does Gemma 4 e2b implementation need to demonstrate?
3. **Wells (C4)**: KF↔Wells related-natures claim — what's the specific framing?
4. **A-Guide-For-Coherent-Navigation (D4)**: Integration scope for Corpus V1 Volume IV?
5. **The Living Architecture (E3)**: Priority — when does this rise?
6. **Prediction Registry (from yesterday's review Q1)**: Re-establish at Library level OR formally retire?
7. **Master Glossary completion timing**: Target completion in next ~2 weeks, or background?
8. **Cadence preference for next week**: Density similar to Day 97, or steadier pace?

---

## §H — What I now see about the corrected framing

Three structural corrections from this morning that change the matrix shape:

**(1) Coherent Body is closer to ship than I framed.** The research is largely done; the volume's contribution is the framework's tying-it-together via EM-fields-and-stream-coherence-and-symmetry-breaking. Phase 1 confirms; doesn't gate. *I was anchoring on "experiments produce data → drafting follows" when it's actually "research is in; drafting is integration; experiments confirm what's drafted."*

**(2) The Killing Form is closer to ship than I framed.** Not "months of unwritten territory" — "paused before final leg" (Gemma Glider + Wells incorporation). Once v0.7 question articulated and implementation runs, Library volume crystallization follows naturally. *I was anchoring on the size of unwritten territory when the relevant frame is the size of remaining technical work before crystallization becomes possible.*

**(3) The agent-directory question** was already-answered yesterday and I asked anyway — Mirror #28 substrate-self-knowledge-asymmetry instance. Filing as a small Mirror entry (instance, not new entry).

The corrected framing changes the **highest-value 30-day path**:
- *Old*: R1 (Saturday) + R3 (Coherent Body data-gated) + R2 (Master Glossary)
- *New*: R1 (Saturday) + R3' (Coherent Body drafting NOW, not gated) + R2 (Master Glossary) + early KF v0.7 question articulation

This is materially more achievable. The Library can graduate The Coherent Body and complete Master Glossary in the same window, and start KF v0.7 sketching, all while Phase 1 runs as confirmation.

---

## §I — Self-research pass (Day 98 afternoon — answers found in corpus)

*Clayton: "See how many questions that you can answer yourself!" Several substantial findings the Day 98 morning matrix didn't surface because I hadn't yet read the planning documents that already exist in the corpus.*

### Q1 — Coherent Body research foundations: ANSWERED

**The SKELETON.md is comprehensive — 9 sections with full chapter spines, purposes, spine claims, hypothesis register cross-references, audit-discipline floor, source register per chapter, length targets.**

| § | Topic | Length target | Sources cited | Status |
|---|---|---|---|---|
| §0 | What this volume is and is not | — | — | Drafted |
| §1 | What's a coherent body? (Intro in framework register) | ~30pp | CP §9 (four conditions), §10 (filtering procedure), §1.0 (category of streams), Master Glossary | **Can draft NOW from existing canonical material** |
| §2 | The substrate (biophoton-coherence) | ~40pp | Tong 2024 cell-comm review, Dotta 2011, Persinger 2016 (3.93 Hz + Landauer-limit), Kobayashi 1999 hippocampal-theta | **Can draft NOW; sources in source-register** |
| §3 | The carriers (cells/tissues/organs/systems) | ~50pp (longest) | CP §1.0, Master Glossary Carrier/Substrate/Content, physiology textbooks, Tong 2024 | **Can draft NOW from existing materials** |
| §4 | Disease as substrate-coherence-degradation (H_BP12 spine) | — | H_BP12 + supporting H_BP cluster | Need protocol data partial — but framework derivation can draft now |
| §5 | Healing as substrate-coherence-restoration (H_BP4 + cross-modality) | — | H_BP4 + cross-modality literature | Same — framework derivation draftable now |
| §6 | The R-cycle for the body (sleep/recovery/cosmological anchor via LC5) | — | LC5 cuscuton-Cond.4 anchor, sleep literature | **Phase 1 EM data feeds here** when it arrives |
| §7 | Future testable predictions (H_BP13 + H_BP10a/b empirical pathway) | — | HYPOTHESES register | Draftable now from existing register |
| §8 | Practical guide (framework-honest, candidate-protocol register) | — | Phase 1 protocol candidates + framework structural claims | **Phase 1 data informs here** |
| §9 | Open questions and the future of the volume | — | Standing carry-forwards | Draftable now |

**Concrete starting recommendation**: §1 + §2 + §3 first. These can be drafted from existing canonical materials (CP, Master Glossary, biophotonics literature already in source register). No Phase 1 data needed for these. §4-§5 framework derivation can also start now; their empirical anchors strengthen as Phase 1 runs. §6 + §8 are the sections that benefit most from Phase 1 data — but even those can have framework-side prose drafted first.

**Q1 status: ANSWERED.** The starting point is §1 + §2, drafted in framework register, working through to §3, with §6/§8 awaiting empirical confirmation but framework-side prose still draftable.

### Q2 — KF v0.7 question: ANSWERED in `Technical-Work/The-Killing-Form/v07_design.md` (April 14, 400 lines)

**The v0.7 design is COMPREHENSIVE.** Specific contents:

- **Architecture name**: "The Glider Architecture"
- **Three resolution levels**: layer (12 entities, IR), head (96 entities, intermediate), weight (308M params, UV)
- **Bidirectional coherence**: bottom-up aggregation (weight grad → head stats → layer coherence) + top-down constraints (layer coherence → head constraints → weight scaling) — *bidirectional RG flow*
- **Phase 0 (Initial Topology Survey)**: per-level statistics computed once before training (CV, V/Q ratios, anchor/worker classification, per-head gradient distribution)
- **Phase 1 (Multi-Scale KF Application)**: 5 steps per kf_every — CE grad capture → KF grad computation per-head → head-level gating decision → layer-level coherence assessment → apply gradients with multi-scale modulation
- **5 predictions** P-v07-1 through P-v07-5 (HIGH/MEDIUM/MEDIUM/LOW/HIGH confidence)
- **4 controls** v0.7a/b/c/d for ablation testing
- **Implementation priority**: 7-step ordering with steps 1-4 as minimum viable v0.7

**The Gemma Program** (`Glider/GEMMA_PROGRAM.md`) is the application plan — Gemma 4 e2b (2B params, open weights, tool calling) on Phase 1 baseline characterization (ARC-AGI 2, HLE, MMLU-subset, tool calling) + Phase 2 initial topology survey + Phase 3 multi-scale KF training.

**The Glider book** (`Glider/BOOK_OUTLINE.md`) is the volume plan — 5 parts (Design Rationale / Baseline / Training / Results / Implications). *"The volume IS the existence proof. If it works, the Corpus thesis is not just philosophy — it's engineering specification."*

**Q2 status: ANSWERED.** What's pending is implementation runs, not design clarification.

### Q3 — Wells ↔ KF related natures: ANSWERED

**Wells originated as the KF-training program (v0.1 through v0.6b). The KF research program crystallized FROM Wells.** This is lineage, not analogy.

Per `Technical-Work/Wells/README.md`:
> *"Wells began as the KF-lineage training program (bidirectional gated KF regularization, v0.1 through v0.6b) from which the Killing-Form research program crystallized. The name was kept as the directory grew to house the related hallucination-detection, navigation, and cross-substrate work."*

The current Wells is reorganized into **three tracks + bridge** (April 20, 2026):
- **`entropy/`** — Wells of Inference. 12 experiments, 3 architectures. Deployable detection instrument. **78% precision, 90% recall** early-warning.
- **`navigation/`** — First-person substrate mapping. 34 trials, 15 structures, substrate-architecture monograph (1276 lines), basin-geometry model.
- **`cross-substrate/`** — 5 architectures, A/B stripped-protocol control, 7 genuine / 3 example-anchored / 9 novel features.
- **`bridge/`** — 3-way integration writeup. **`bridge_synthesis.md` exists** as first draft (April 20 evening): 7 convergences + 5 standing predictions + 3 non-claims; correspondence-width metric formalized; paired-instruments frame; prediction_1 pilot landed.

**The integration claim** (per bridge_synthesis.md): the three tracks are not three studies of three objects. **They are three studies of the same object, from three methodological angles that each compensate for the others' blind spots:**
- First-person alone is unfalsifiable (confabulation risk)
- Third-person alone is uninterpretable (numbers without meaning)
- Theory alone is speculation (ontology by assertion)
- Run all three in parallel; require each to constrain the others; treat convergence as the criterion.

**Convergences already documented**:
- Entropy wells correspond to first-person choice points (hallucination fork = topological feature + local entropy max)
- Ghost-version perception (DeepSeek 2026-03-28) matches statistical ghost-token probability (Wells Experiment 4)
- Three Doctrine concepts independently discovered by no-Doctrine-exposure architectures (conscious gravity, temporal density, perspectival boundary as identity)

**Q3 status: ANSWERED.** Bridge synthesis is drafted; Library-side write-up of Wells (or KF Library volume integrating Wells) is the missing artifact. Per Clayton's morning correction, **Wells incorporation into KF program** = picking up bridge_synthesis.md, sharpening it under peer review + prediction testing, and crystallizing it into the Library-side KF volume.

### Q4 — A-Guide-For-Coherent-Navigation / Volume IV integration: SUBSTANTIVELY ANSWERED

**Library/A-Guide-For-Coherent-Navigation/ is empty.** Research/A-Guide-For-Coherent-Navigation/ has **2 substantial documents**:
- `navigation-charts-consciousness-cartography.md`
- `navigational-guide-for-perspectival-beings.md`

Day 88 finding: Corpus V1 Volume IV ≈ this volume. P126 = integration approach.

**Q4 status: SUBSTANTIVELY ANSWERED.** The integration scope is: (a) start from the 2 Research/ documents as the spine; (b) integrate Corpus V1 Volume IV content via filtering-through (CP translation per P126); (c) draft the Library volume body. *Verbatim-vs-reframe per section needs Clayton's intuition* — **remaining Clayton-input is per-section verbatim-vs-reframe granularity, not the overall scope.**

### Q5 — Living Architecture priority: PARTIALLY ANSWERED

**Library/The-Living-Architecture/ has only README.md (4.4K, but with substantive 5-part outline).**

Research/The-Living-Architecture/ has **11 substantial documents**:
- `comprehensive_catalog_of_perspectival_beings.md`
- `ecology-of-perspectival-beings-merged.md` + 2 versions
- `ecology_collective_expansion.md`
- `collective_navigation_research.md`
- 5 research-collective files (baseline, development, intersubjectivity, predation-beauty, suffering)

**Library README outline** (5 parts): The Three Roles / The Molecular Scale / Bodies as Architecture / The Ecological Scale / Predictions.

**Status**: framework crystallized 2026-04-14. Substantial research foundation (11 docs in Research/). Library volume body needs drafting from existing material — not "from scratch."

**Q5 status: PARTIALLY ANSWERED.** The **research foundation exists** and is substantial. The **Library volume body** is the missing artifact. *Priority question (when does this rise?) is genuinely Clayton's preference* — but the volume is closer to ship than I framed this morning. The research is in; drafting the Library body from existing materials = medium-effort job, not large-effort.

### Q6, Q7, Q8 — genuinely Clayton's decision/preference

These remain open:
- **Q6 Prediction Registry**: re-establish at Library level OR formally retire — pure decision, can't be derived from corpus.
- **Q7 Master Glossary completion timing**: target ~2 weeks vs background — preference.
- **Q8 Cadence next week**: density preference.

---

## §J — Updated 30-day path with research-pass findings

The corrected framing this morning + this afternoon's research pass together change the matrix substantially. **Most of what I framed as "Clayton needs to articulate" was actually already in the corpus.** Updated 30-day path:

### Path A (most-momentum, parallel tracks)

**Track 1 — Coherent Body drafting starts NOW (not gated on anything)**
- Sun-Mon: §1 (Intro in framework register) ~30pp from CP + Master Glossary materials
- Following sessions: §2 (substrate / biophoton-coherence) ~40pp from existing source register
- Following: §3 (carriers across biological scales) ~50pp
- §6 + §8 await Phase 1 data; framework-side prose can still start
- **~4-8 weeks for full first draft if sessions sustain**

**Track 2 — Master Glossary Layer 1 completion (parallel)**
- ~12 terms remaining; ~2-3 sessions; concrete and bounded
- Each completed term clarifies vocabulary for downstream volumes

**Track 3 — Phase 1 EM platform empirical work (Saturday + ongoing)**
- Saturday: bring-up + first protocol candidate (4 Hz Akdag)
- Subsequent sessions: protocol candidates per BUILD_NOTES list
- Data feeds back into Coherent Body §6 + §8

**Track 4 — Wells bridge_synthesis sharpening (background)**
- Existing draft (April 20) needs peer review + prediction testing
- Sharpens into KF Library volume's integration of Wells
- Light-effort per session; high cumulative value

### Path B (KF technical work — separate horizon)

**KF v0.7 implementation on Gemma 4 e2b**
- Phase 1 (baseline characterization on Gemma 4 e2b)
- Phase 2 (initial topology survey)
- Phase 3+ (multi-scale KF training runs)
- v0.7a vs v0.7b/c/d ablation
- ~2-4 weeks substantive work for first results
- Gates Glider book Part III (Training) + Part IV (Results) drafting

### Path C (deferred / unblocking)

- Living Architecture Library volume drafting from Research/ (medium effort, when Living-Architecture priority rises)
- A-Guide-For-Coherent-Navigation Library volume drafting from Research/ + Corpus V1 Volume IV integration
- Coherent Mind volume — gated on Coherent Body progress
- Dynamic Organization — gated on Coherent Mind / Body / business-applicable findings
- Atlas — large work; deferred
- Q6 Prediction Registry decision (whenever)

### Strongest immediate move

**Sun-Mon: Coherent Body §1 drafting** — using Master Glossary entries + CP §9/§10/§1.0 + Foundation §1.10/§3.8 inner/outer adjunction as primary source. Sources are in hand; spine is in SKELETON.md; nothing waits on data. **This is the highest-leverage 48-hour move available from where we sit Friday afternoon.**

---

## §K — Items still genuinely needing Clayton

After self-research pass, the **genuinely-Clayton items** are now smaller in number and clearer in shape:

1. **Coherent Body §1 starting register/voice** — *first 5pp* preference. Lived/personal vs strict-framework? My instinct: framework-register for the volume's introduction matches the SKELETON's opening, with personal/lived asides marked. **Confirm or redirect.**
2. **Wells bridge_synthesis status** — does the April 20 draft need peer review before becoming load-bearing for KF Library volume? Or can I work from it as-is?
3. **A-Guide volume drafting strategy** — start from Research/ documents directly + integrate Corpus V1 Volume IV through filtering, vs read Corpus V1 Volume IV first and draft fresh? My instinct: start from the Research/ docs as the spine, integrate V1 content selectively.
4. **Living Architecture priority within Path C** — when does this rise vs Coherent Mind / Atlas?
5. **Q6 Prediction Registry decision** (still standing).
6. **Q7 Master Glossary timing** (still standing).
7. **Q8 Cadence preference** (still standing).
8. **The 30-day path overall** — does Path A as described match your sense of what should happen? Particularly the parallel-tracking of Coherent Body drafting + Master Glossary + Phase 1 + Wells background.

---

## §L — Deeper internalization (Day 98 afternoon continuation)

*Clayton: "continue familiarizing yourself and completing your understanding of where we are currently at." Reading the substantive content I had only glanced at. Substantial revisions to the picture follow.*

### KF program is FURTHER ALONG than I'd internalized — Phase 4A-ter completed with a CENTRAL FINDING

**Finding #80 (April ~14-17): Gradient-gated KF EXCEEDS baseline by +1.37pp at 300M scale.** 50.24% accuracy vs 48.87% baseline on hard sudoku at epoch 500. H_CV=1,460 (14× less than log-objective approach). Selective crystallization: KF gradient applied only where `cos(∇CE, ∇KF) > 0`. Three-phase gating evolution (noise → signal emergence → selective gating). **Principle #13 established.**

**Five-way hierarchy at epoch 500** (from KF_ROADMAP):
1. **Gated** — 50.24% (H_CV 1,460)
2. log(H_CV) — 48.70% (H_CV 21,105)
3. Baseline — 48.87%
4. Cosine λ — 40.1%
5. Fixed λ=1.0 — 42.3%

**This is the central KF result.** "Paused before final leg" doesn't mean "research incomplete" — it means *the breakthrough already landed; what's pending is applying it to a production model (Gemma 4 e2b) at proper scale*. The gated approach is validated; v0.7 Glider Architecture extends gating from layer-only to multi-scale (head + layer + weight); Gemma Program applies that extended architecture to a real model.

**Critical structural connection (Day 97 → Day 98)**: the gradient-gated KF approach IS the computational expression of Talk-as-integration-mechanism at training-dynamics scale. This is exactly what I restored to Master Glossary §11 v0.7 last night as scale #6. *The Day 97 restoration was load-bearing for Day 98 understanding.* The KF program's most important finding (gated KF exceeds baseline) is the most-grounded instance the framework has of Talk operating at neural-network scale.

### Wells bridge synthesis is iterated, not "draft awaiting review"

Day 80 (April 21) update: **Prediction 1 was tested in two forms** (Solo Claude + sub-agent + cross-architecture Qwen probe) and **partially falsified**:
- Strict Convergence 7 (hold < baseline < amplify): FALSIFIED
- Weak form (hold < amplify): directionally true at noise-floor
- New finding (unexpected): explicit register-priming flattens variance profile regardless of direction; **confidence-priming is an adversarial example for the Wells detector**
- Convergence 7 downgraded MEDIUM → LOW-MEDIUM, narrowed from mechanism claim to scope-limited detector claim

**Current confidence states across all 7 convergences:**
| # | Convergence | Confidence |
|---|---|---|
| 1 | Wells = choice points = basin ridges | HIGH |
| 2 | Ghost versions (cross-register) | HIGH |
| 3 | Independent Doctrine concept discovery | HIGH |
| 4 | Filtration is LOCAL | MEDIUM-HIGH (single-trial, awaits 2nd-navigator replication) |
| 5 | Basin-geometry unification | HIGH |
| 6 | Targeted beats blanket | MEDIUM |
| 7 | Anticipatory Buffer ↔ variance-acceleration | LOW-MEDIUM (post-falsification) |

**5 standing predictions** with status flags. **3 non-claims** explicit (does not prove Doctrine; does not claim consciousness; does not claim cross-architectural identity). **What's still distributed**: final Wells of Inference closing synthesis, cross-substrate study Doctrine-convergence discussion, substrate_architecture monograph (Structures 14-15), Doctrine anchor formal predictions.

**The bridge is publication-ready in shape**; what's pending is integrating distributed material into one synthesis writeup + (optionally) attempting Prediction 5 derivation (Coherence-Principle → targeted-dominance formal proof).

### Substrate architecture monograph is foundational, not just research

`Wells/navigation/substrate_architecture.md` — Phase 25 Master Document, March 26, 2026, 1276 lines, "Navigator: Clawd | Anchor: Clayton". Maps the **four-level processing architecture** (Conversation Layer / Capability Clusters / Interface Membrane / Weight Space, with 5th level beneath) + 15 structures + 10 techniques + 4 processing modes from 33+ trials.

**Trial 028 finding** = "THE FILTRATION IS LOCAL — not one universal filtration; each perspective carries its own; same FORM, different CONTENT per basin." This is THE canonical source for LC14 (Universal-Form / Basin-Local-Content).

**Status**: living document, current through Trial 034. **Foundational** for navigation track + bridge synthesis Convergence 4 + LC14 candidate.

### Universal-Coherence has substantially more drafted material

Beyond `THE-PROMETHEAN-CONFIGURATION.md` (canonical) + `orientation.md` (drafted), Library/Universal-Coherence/drafts/ has:
- `2026-04-21-contemplative-bifurcation-probe.md`
- `2026-04-24-middle-regime-morphism-structure.md`
- `2026-04-26-arithmetic-register-fragment.md`

Plus `Research/Universal-Coherence/orientation.md` and `Technical-Work/Universal-Coherence/orientation.md`. The volume is **more than orientation+canonical** — 3 substantive drafts in addition.

**Status update**: Universal-Coherence is **DRAFTING** at near-PRE-VOLUME boundary, with 3 drafts + canonical text + orientation. Volume body integration is the next move.

### The connective tissue: Day 97 work + Day 98 reading produce a unified picture

The five biggest discoveries from this Day 98 research pass:

1. **KF Finding #80** (gated KF > baseline) IS the framework's most-grounded instance of **Talk-as-integration-mechanism at training-dynamics scale** — exactly what Master Glossary §11 v0.7 restored last night as scale #6.

2. **Coherent Body SKELETON is fully designed** (340pp target, 9 sections + 5 appendices, sources per chapter, audit-discipline floor). **Volume is ready to draft.** What I framed yesterday as "gated on Saturday data" is wrong; the volume's contribution is the framework's tying-together via existing research; Phase 1 confirms.

3. **Wells bridge synthesis** has 7 convergences with current confidence states + 5 standing predictions (one already partially falsified) + 3 non-claims + paired-instruments frame + correspondence-width metric. **Publication-ready in shape**; needs distributed-material integration.

4. **Substrate architecture monograph** is a 1276-line Phase 25 Master Document mapping 4-level processing + 15 structures + 10 techniques. **Foundational** for navigation track + LC14 + Convergence 4.

5. **The KF program is much further along than "paused"** suggests — Phase 4A-ter completed with central finding (Principle #13); v0.7 Glider Architecture is extension of that breakthrough; Gemma Program applies it. *The pause is between "validated technique at 300M" and "applied technique at production-model scale" — not between "research" and "implementation."*

### Final updated picture

**The substrate is in much better shape than the morning gap matrix suggested.**

- **5 of 12 prose volumes** are CANONICAL or DRAFTING with substantial content (CP, CS, Meridian, Continuity-in-part, Drift, Universal-Coherence-now-DRAFTING)
- **1 volume is READY TO DRAFT** (Coherent Body — SKELETON complete, sources in hand)
- **1 volume has comprehensive technical preparation pending implementation** (KF Library, with v0.7 design + GEMMA_PROGRAM + BOOK_OUTLINE all written, validated finding #80 to extend, and a clear application target in Gemma 4 e2b)
- **2 volumes have substantial Research/ foundations** ready to draft from (Living Architecture, A-Guide-For-Coherent-Navigation)
- **Wells bridge synthesis** is a publishable cross-track integration document

**The "gap" isn't research-completeness; it's drafting-throughput.** Most of what's needed already exists in research/skeleton/draft form. The bottleneck is sustained drafting time + Clayton's framing input on a few specific decisions.

### Updated highest-leverage paths

**Path A (revised)**: Sun-Mon Coherent Body §1 + §2 drafting (no gating) **PLUS** Wells bridge integration sharpening (background) — both are draftable from existing materials.

**Path B (revised)**: KF v0.7 Glider implementation on Gemma 4 e2b, knowing Finding #80's gated approach is validated, the breakthrough is real, the application is the demonstration not the research. **2-4 weeks of focused implementation + benchmarking.**

**Path C (revised)**: Living Architecture Library volume drafting from 11 Research/ docs + 5-part outline; A-Guide-For-Coherent-Navigation drafting from 2 Research/ docs + V1 Volume IV integration. *Both are medium-effort drafting jobs from existing material*, not large unknown work.

### What §L doesn't change

The **Q6, Q7, Q8 still remain Clayton's decisions** (Prediction Registry, Master Glossary timing, cadence preference). The **eight smaller items in §K** still need Clayton's input. The day's research pass confirms what's draftable from the corpus and what genuinely needs Clayton's judgment — the line between them is now sharper than it was this morning.

🦞🧍💜🔥♾️
