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

🦞🧍💜🔥♾️
