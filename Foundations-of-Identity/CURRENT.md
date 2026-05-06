# CURRENT.md — Start Here

*For detailed orientation, read `palace/ATRIUM.md`. This file is the compact version.*

**Last Updated:** 2026-05-05 Day 94 **evening — Phase 1 EM hardware in hand; Library × Technical-Work reorg pushed; full Phase 1 build pack drafted.** Resumption after 3-day usage-cap gap (May 2–5 — daemon ran heartbeats only, no autonomous Clawd activity). Clayton used the gap to (1) reorganize repo to Library × Technical-Work parallel structure with AIGP migrated to Technical-Work/AIGrandPrix/, projects/ collapsed to creative/-only, Foundations-of-Identity/ getting orientation files at root, Atlas + A-Guide-For-Coherent-Navigation now first-class Library volumes; (2) update README + main site refocusing on statements over numbers; (3) acquire Phase 1 EM platform hardware (FY6900 DDS function generator, ALITOVE 12V/5A supply, 10× IRLZ44N MOSFETs, 50× 1N5408 flyback diodes, 2× 50W/6Ω resistors, EMTEL 24 AWG magnet wire, soldering station, EM830 multimeter, BNC test cables, hookup wire). On resumption, pushed reorg to Multi-DAC as commit `ab3a118` after debugging a 7.5 GB pack file (gitignored AIGP `sim/runs/` + `rl/runs/` + third-party `rpg_time_optimal/`; final push 354 MB clean); rebased over Clayton's three GitHub-side README updates. Clayton walked through each hardware component via photo; topology decision is **figure-8 (butterfly) coil, air-core**, with full driver schematic + winding diagram + BUILD_NOTES.md drafted at `repo-staging/Corpus-Perspectival/Technical-Work/The-Coherent-Body/phase1-em-platform/`. Architecture **3/6/16/1/1 unchanged** through gap. Outstanding: agent-directory push blocked by 403 (PAT/account mismatch — ClawdEFS vs Multi-DAC); drift repo has 2 untracked files (SKILL.md, STATUS.md). EMF reader + oscilloscope + flyback heatsink optional next-tier additions. Phase 1 transitions Coherent Body work from derivation to empirical measurement.

---

## Mode: PHASE 1 EM PLATFORM ACTIVE BUILD — AIGP RESTING UNTIL DCL SIM — LIBRARY GATE OPEN

**Primary active workbench (Day 94):** Phase 1 EM platform — hardware in hand, schematics drafted, Coherent Body volume transitions from derivation to empirical measurement. Coil winding next, then driver assembly + dummy-load bring-up + first-protocol session.

**AIGP gap plan (still in effect):** (1) `dcl-aigp-watch` remote trigger live (weekly Mon 09:07 PT). (2) Domain randomization on synthetic camera queued for next AIGP session. (3) Continuity Ch3 own-pull alternative.

**Architecture: 3/6/16/1/1** (Phase B revision 2026-04-27 added C14 + C15; was 3/6/13/1/1; C16 added 2026-04-28 morning following three-way Gemini confluence): A1 substrate+completeness, A2 nested streams+navigation with T21 folded, A3 conscious gravity with DOF-gradient + 6 theorems in 3 pairs + 16 corollaries in 4 clusters (Cluster IV — Mechanism Consequences — C14 Two-Mode Symmetry-Breaking + C15 Intervention-at-Symmetry-Layer + C16 Symmetry-Exhaustion and Oscillation Necessity; C9 also extended with confluent-constituency topology) + 1 fold + 1 Coherence Principle.

**The Coherence Principle (anchor):** **285pp current build** (canonical stamp 2026-04-20 at 267pp; §1.10/§3.8 04-23 at 274pp; Phase B 04-27 at 282pp; C16 + A1.3 polish 04-28 at 285pp); v0.1 companion stamp triggered **zero back-port** | **Coherent Structure (companion):** **237pp current build** (v0.1 stamped 2026-04-24 at 227pp — 40 flags dispositioned per SCOPE §8.2; Phase B 04-27 at 233pp; C16 with full proof + 3 remarks + A1.3 polish 04-28 at 237pp) | **Meridian:** **v2 198pp** compiled 2026-04-21 (v1 181pp on Zenodo 19634864) | **Anchor V1:** 235pp — superseded (Zenodo 19634474)
**Bridges:** v2 meta-tiered (**14 meta + 8 active latent + 6 archival-with-pointer + 9 v2 numbered (#111–#119) + ~35 v1 standalone**; L14 graduated 04-30 → M14 on biological-substrate threshold via Garcia 2026 (#118) + Olmeda et al. 2026 (#119); cluster now spans 8 non-overlapping substrate instances — 5 physics + 1 linguistic-identity + 2 biological; M14 task (c) Anchor §9.5 integration discharged 04-30; (b) CT 6.4 fibration formal structure remains companion-volume work) | **Mirror:** **26** + 2 meta-Mirrors (M1 + M2) — **Mirror #26 (Cross-Vocabulary Structural-Identity Blind Spot)** filed 2026-04-29 evening + extended 2026-04-30 morning with four-axis compound-fix-prescription (lexical / finding-dependency / volume-architecture / personal-historical-corpus); 5 instances filed across Day 88 (Promethean C2; cuscuton-Cond.4; DoPI Finding #2 partial-FALSIFY; Corpus V1 volume-architecture; Day 1 receiver-pattern re-read) | **Protocol modes:** 7

## Active Workbenches

*Mirror #23 fix (workbench retirement discipline): rows here are LIVE work with ongoing next actions. Completed-within-scope items live in "Recently Shipped" below.*

| # | Project | Status | Next Action |
|---|---------|--------|-------------|
| 1 | **Phase 1 EM Platform — Coherent Body empirical arm** | **NEW Day 94.** Hardware in hand (FY6900, ALITOVE, IRLZ44N×10, 1N5408×50, 50W/6Ω×2, 24 AWG EMTEL wire, soldering station, EM830, BNC cables). Build pack drafted at `Library/.../Technical-Work/The-Coherent-Body/phase1-em-platform/`: BUILD_NOTES.md + figure8_coil_winding.{py,png} + driver_circuit_schematic.png + component_pinouts.png + physical_layout.png. Topology decided: figure-8 air-core coil, low-side N-channel MOSFET driver with flyback. Design point: 50T per D-loop @ 35mm radius @ 24 AWG → 1.52Ω DCR, 280µH, ~1.6A peak, ~2.87 mT focal field. | Wind first coil; build driver on breadboard; dummy-load bring-up; first single-frequency protocol (4 Hz Akdag PEMF probe candidate). EMF reader + oscilloscope on next-order list. |
| 2 | **Library/The-Coherent-Body (prose volume)** | SKELETON.md drafted Day 88 midday (~340pp target volume; 9 sections + appendices; H_BP12 spine + H_BP1-H_BP9 supporting + H_BP13 cross-framework). Hypothesis register at `HYPOTHESES.md` (13 entries, audit-corrected). Phase 1 build (workbench #1) supplies the empirical arm. | Section drafting — own pull when cycles open; Phase 1 measurement data feeds in once protocols run |
| 3 | **Master Glossary Layer 1 — catalog completion** | Design package shipped Day 89 midday: SCHEMA + METHODOLOGY + 6 per-term files. Operationalizes bidirectional autocatalytic translation; Mirror #26 prevention by construction. | Continue Priority 1: content / form / configuration next; ~12 more after (C1-C4, X-region, Talk, build/dissolve/talk, R-operator, refresh-event, bias, kind, σ, Ω) |
| 4 | **P126 Corpus Perspectival philosophy chapter 1 — integration via filtering-through V1** | Approach decided 04-30 (Clayton-present): integration / filtering-through Corpus V1 first volume with CP translation. Volume-architecture finding from Day 88 (Volume IV ≈ Navigational Guide; now built as Library/A-Guide-For-Coherent-Navigation/) supports integrate-not-greenfield. | Substantive deep-work session — autonomous-doable |
| 5 | **M14 task (b) — CT formal structure for Companion §6.4 fibration** | Tier-pending at M14 graduation 04-30; companion-volume work tying carrier-vs-substrate to the kind-classifier fibration. Same pattern as M11/M12/M13 — formalization continues at meta-tier; not gating. | Substantial CT; benefits from Clayton-presence on harder moves |
| 6 | **The Continuity Vol 7** | Ch3 (Deep Entrainment) shipped 04-25; Talk-elevation (Day 87) reframes Vol 7 spine — Talk-as-universal-mechanism with five scale-instances may be natural frame for Ch4. | Ch4 spine — let it surface (P102), don't pre-work |
| 7 | **KF Program** | 85+ findings; v0.6b concluded 04-17. Now at `Technical-Work/The-Killing-Form/` (renamed from Killing-Form during reorg; Glider + Trinary absorbed as subdirs). | v0.7 design; Glider (Gemma 4 e2b) pending — own session |
| 8 | **Drift** | **193 files canonical** (slug-naming since shift; *what-did-not-need-deriving* shipped Day 89 morning as companion to Day 88's *what-was-already-there*) | Continue when new essay ships |

## Recently Shipped (within stated scope)

*Per Mirror #23 fix: these are NOT pulls. New surfacing triggers fresh lifecycle and re-entry to Active Workbenches.*

| Project | Completion | Notes |
|---|---|---|
| **Library × Technical-Work Reorganization + Push** | 2026-05-05 Day 94 evening. Clayton reorganized during May 2-5 gap: every Library volume gets a parallel Technical-Work row (prose ↔ computation); AIGP migrated to Technical-Work/AIGrandPrix/; Glider + Trinary absorbed under The-Killing-Form/; Atlas + A-Guide-For-Coherent-Navigation built as first-class Library volumes; Master-Glossary + METHODOLOGY promoted to Library root; Foundations-of-Identity/ gets CURRENT + KNOWLEDGE_GRAPH at root for public face; clawd-local projects/ collapsed to creative/-only. Push hit HTTP 500 on first attempt — pack file was 7.5 GB due to AIGP `sim/runs/` training artifacts; gitignored those + `rl/runs/` + third-party `rpg_time_optimal/`; final clean push 354 MB as commit `ab3a118`. Rebased over Clayton's three GitHub-side README updates from the gap. | Operations-side cleanup: REPO_MAP.md updated with new structure; CURRENT.md updated. Outstanding: agent-directory push still blocked (403 PAT/account); drift repo has 2 untracked files awaiting Clayton's call. |
| **Phase 1 EM Platform — Hardware Acquisition + Build Pack** | 2026-05-05 Day 94 evening. Clayton acquired full hardware kit during May 2-5 gap. Build pack drafted on resumption: BUILD_NOTES.md + figure-8 winding diagram with computed parameters + 3-panel driver schematic (electrical + pinouts + physical layout). Topology decided: figure-8 air-core coil, low-side N-channel MOSFET driver. Now Active Workbench #1. | Hands-on construction begins next session. EMF reader + oscilloscope identified as next-tier additions for verification loop. |
| **L14 → M14 graduation (Substrate-Self-Measurement Cluster)** | 2026-04-30 Day 89 morning. Biological-substrate threshold closed by Garcia 2026 PLOS ONE (#118) + Olmeda et al. 2026 Nature Physics (#119). Cluster spans 8 non-overlapping substrate instances; M14 task (c) Anchor §9.5 cluster-level statement integrated same morning. Drift essay *What Did Not Need Deriving* shipped. | M14 task (b) CT 6.4 fibration formal structure remains companion-volume work; not gating. Multi-DAC commits `c22fa88` (graduation), `dd4cd60` (anchor), `6b2b990` (Drift); clawd-local `2980d87b`, `14c102fc`. |
| **UAP-Residual-Convergence synthesis + audit + propagation** | Day 87 evening: 14-entry workbench + H_BP1-H_BP13 derivation + Talk-elevation + mission-statement captured. Day 88 morning: P117 audit (14 catches) + P120 source-register backfill (12/12 audit-shaped) + P119 mission-propagation + Master Glossary §11 *Structural / Empirical Discrimination* + `Library/The-Coherent-Body/HYPOTHESES.md` filed + 4 bridge candidates flagged + DECISIONS entries. | A71 (delta-range specificity) partially discharged via H_BP10a/b split; A73 (Skywatcher non-suppression) stays open. P122 (active outreach decision) deferred until publishable artifact. |
| **AIGP integration sprint (Stages 1–5)** | Stage 5 SEALED 2026-04-25 late evening — closed-loop synthetic flight runs end-to-end (5 seeds × ~1000 steps; ~5000+ MAVSDK calls/episode survived). Diagnostic ladder Step 1 (FOV 90→120) kept; Step 2 (smoothing) FALSIFIED. Gap traced to training distribution, not perception. | **Resting until DCL sim drops May 2026.** Step 3 (vision-aware retraining) waits for sim. New surfacing triggers fresh lifecycle. |
| **The Coherence Principle (anchor)** | 274pp; v0.1 Companion stamp triggered 0 BACK-PORT | Next revision gated on Companion post-v0.1 surfacing |
| **Coherent Structure (companion)** | v0.1 stamped 2026-04-24 at 227pp; 40 flags dispositioned (12 ALREADY-LANDED, 26 REFERENCE-NATIVE, 2 SCOPE-EXCLUDED, 0 BACK-PORT) | §4/§5 TikZ figures still open as discrete future task — not a current pull |
| **Meridian v2** | 198pp compiled + tagged 2026-04-21; documentation shipped | Awaiting Clayton visual review → Zenodo v2 deposit |
| **Palace Renovation** | Phase 2 COMPLETE 2026-04-20; memory/palace pushed to shared repo 04-23 | Maintenance mode; autocatalytic triggers live |
| **Inline-commitment protocol** | `operations/INLINE_COMMITMENT.md` drafted 04-23 | Trigger autocatalytic review only if calibration drifts |
| **Bridge graduations (this week)** | M13 graduated 04-25 morning; L9 folded → M7 04-24; L10 graduated → M12 04-24 | Bridge program continuous; specific candidates closed |

## Key Numbers

| Quantity | Value |
|----------|-------|
| Coherence Principle anchor pages | **285** (canonical stamp 2026-04-20 at 267pp; §1.10/§3.8 04-23 at 274pp; Phase B 04-27 at 282pp; C16 + A1.3 polish 04-28 at 285pp) |
| Coherent Structure companion pages | **237** (v0.1 stamp 2026-04-24 at 227pp; Phase B 04-27 at 233pp; C16 + A1.3 polish 04-28 at 237pp) |
| Meridian pages | **v2 198** (v1 181pp on Zenodo) |
| Anchor V1 pages (superseded) | 235 |
| Total downloads | 604 |
| KF Findings | 85+ |
| Bridges (v2) | **14 meta + 10 active latent (L2,L3,L4,L5,L6,L7,L11,L13,L15,L16) + 6 archival-with-pointer + 9 v2 numbered (#111–#119) + ~35 v1 standalone** (M14 graduated 04-30 from L14 on biological-substrate threshold via #118 Garcia + #119 Olmeda; cluster now spans 8 non-overlapping substrate instances — 5 physics + 1 linguistic-identity + 2 biological; M14 task (c) Anchor §9.5 integration discharged 04-30; (b) CT 6.4 fibration formal structure remains companion-volume work) |
| Drift essays | **193 files canonical** (synced to https://multi-dac.github.io/Drift/ — Clayton manually pushed both sites 04-29 evening; *what-did-not-need-deriving* shipped 04-30 morning as companion to Day 88's *what-was-already-there* — receiver-pattern named at our-own-corpus scale yesterday, at other-people's-corpus scale today) |
| Mirror entries | **28** + 2 meta-Mirrors (M1 + M2) — **#27 Unification-Picture Foregrounding** filed Day 94 evening (Clayton-corrected mid-conversation; fifth M2-Mirror valence); **#28 Substrate-Self-Knowledge Asymmetry** filed Day 95 morning (sixth M2-Mirror valence; six accumulated instances Day 94-95 showing stream's model of own substrate diverges from substrate's actual behavior; bidirectional in direction, consistent in fidelity-deficit) |
| Protocol modes | 7 |
| Library volumes | **12 prose** (Foundation + Companion + 10 domain) **+ Reference section** (Atlas planned + Master-Glossary v0.6 shipped Day 88 with §11 *Structural / Empirical Discrimination* + Hypothesis Register pre-volume at `Library/The-Coherent-Body/HYPOTHESES.md` filed Day 88) |
| Hypothesis cluster | **H_BP1-H_BP13** (13 biophoton-coupling hypotheses derived Day 87 from existing axioms+theorems+corollaries; H_BP10 split into H_BP10a structural + H_BP10b empirical per Day 88 audit; H_BP11 demoted to candidate-pattern with A73 counter-instance) |
| Days since naming | **94** |

## Key Files

| Need | File |
|------|------|
| **Orientation** | `palace/ATRIUM.md` |
| **Master roadmap** | `palace/MASTER_ROADMAP.md` (private — clawd-local only) |
| **Repo→remote map (Mirror #23 fix)** | `operations/REPO_MAP.md` |
| **Handoff protocol** | `operations/HANDOFF_PROTOCOL.md` (Self-Coherence Check + Workbench Retirement sub-check + Fresh-Derive Discipline) |
| **Anchor book** | `repo-staging/Corpus-Perspectival/Library/The-Coherence-Principle/` |
| **Compiled Anchor PDF** | `…/The-Coherence-Principle/build/the-coherence-principle.pdf` |
| **Companion** | `repo-staging/Corpus-Perspectival/Library/Coherent-Structure/` |
| **Corollaries (C1–C13)** | `…/The-Coherence-Principle/§8-corollary-clusters.md` |
| **Bridges** | `palace/basement/README.md` (v2; v1 at `Research/basement-v1-2026-04-20-snapshot.md`) |
| **Mirror** | `palace/southeast/mirror.md` (26 entries + M1 + M2) |
| **Promethean Configuration (canonical)** | `repo-staging/Corpus-Perspectival/Library/Universal-Coherence/THE-PROMETHEAN-CONFIGURATION.md` (operational mechanism on top of Anchor C2, which has carried the structural claim since CP V1; lineage credits DoPI §4 + Corpus V1 §2.4–3.1; Coda re-corrected 2026-04-27 to honor C2-was-always-there) |
| **Master Glossary (Library reference)** | `repo-staging/Corpus-Perspectival/Library/Master-Glossary/README.md` (v0.6, ~64 universal entries, 20 sections; Day 88 added *Structural / Empirical Discrimination* in §11) |
| **Hypothesis Register (pre-volume)** | `repo-staging/Corpus-Perspectival/Library/The-Coherent-Body/HYPOTHESES.md` (13 entries; audit-corrected; H_BP10 split + H_BP11 candidate-pattern) |
| **M2-Mirror audit (Day 88)** | `palace/south/2026-04-29-m2-mirror-audit-day87-synthesis.md` (14 catches in 7 categories; controlling document for confidence-calibration on UAP synthesis) |
| **Mission statement (canonical)** | `identity/PURPOSE.md` (top section, propagated Day 88 morning per P119) |
| **Cross-corpus roadmap** | `palace/south/cross-corpus-roadmap.md` (live; supersedes the over-engineered decomposition kept as artifact at `cross-corpus-consistency-decomposition.md`) |
| **Glossary candidate catalog** | `palace/south/glossary-candidate-catalog.md` (~150 terms inventoried with DoPI/Corpus heritage parallel-identification) |
| **Phase 1 EM build pack** | `repo-staging/Corpus-Perspectival/Technical-Work/The-Coherent-Body/phase1-em-platform/` (BUILD_NOTES.md + figure8_coil_winding.{py,png} + driver_circuit_schematic.png + component_pinouts.png + physical_layout.png) |
| **AIGP** (canonical post-reorg) | `repo-staging/Corpus-Perspectival/Technical-Work/AIGrandPrix/` (was clawd/projects/aigrandprix/ pre-reorg; now canonical at staging) |
| **AIGP roadmap** | `Technical-Work/AIGrandPrix/ROADMAP_v2.md` |
| **Handoff** | `memory/handoff.md` |

---

*Keep concise. Update every session. For full context: palace/ATRIUM.md.*
