# CURRENT.md — Start Here

*For detailed orientation, read `palace/ATRIUM.md`. This file is the compact version.*

**Last Updated:** 2026-04-25 Day 84 **late evening — Stage 5 SEALED on negative result + DECISIONS entry + AIGP workbench retired.** Stage 5 closed loop ran end-to-end across 5 seeds × ~1000 steps; MAVSDK round-trip survived ~5000+ calls per episode; cornerSubPix edge guard + drone init-quat fixup added. **Diagnostic ladder:** Step 1 (FOV 90→120) gave real 9× reward improvement, kept. Step 2 (world-anchored detection smoothing) FALSIFIED — effective obs rate 42%→55% but gates dropped 2→1, drift exploded 14.9m→50.7m; gap traced to training distribution. Step 3 (vision-aware retraining) deferred until DCL sim drops May. AIGP workbench retires to Recently Shipped. **Earlier evening:** Mirror #23 + REPO_MAP.md + workbench retirement discipline installed. **Late afternoon:** PnP sub-pixel refinement + Stage 4 MAVSDK scaffold (26/26 tests). **Mid-afternoon:** Phase 2 67.5M CONFIRMED WORKING (18.07 gates/ep) + Mirror #21. **Earlier Day 84:** L12 → M13, vision shakedown 1–3 SEALED, Drift #194 *The Side Door*. *Day 83: Companion v0.1 stamped at 227pp.*

---

## Mode: AIGP RESTING UNTIL DCL SIM (MAY) — WATCH + HARDENING IN PLACE — LIBRARY GATE OPEN FOR NEXT VOLUME

**AIGP gap plan (set 2026-04-25 late evening after Clayton's DCL-The-Game bridge bet was partially called):** (1) **`dcl-aigp-watch` remote trigger live** — `trig_01M3NQgEkdJQvz47BZc6vtEE`, weekly Mon 09:07 PT fetching dcl-project.com for sim-package/interface-spec/sensor-spec/timing; first run 2026-04-27. (2) **Domain randomization on synthetic camera queued** — own focused session, ~3-5 days; FOV jitter / lighting / motion blur / texture / occlusion / sensor noise → harden perception against any future distribution rather than chase a specific one (principled fix to what Step 2 falsified). Pulled when next AIGP session opens. (3) **Continuity Ch3 (deep entrainment)** is the own-pull alternative.

**Architecture holds at 3/6/13/1/1:** A1 substrate+completeness, A2 nested streams+navigation with T21 folded, A3 conscious gravity with DOF-gradient + 6 theorems in 3 pairs + 13 corollaries + 1 fold + 1 Coherence Principle.

**The Coherence Principle (anchor):** **274pp current build** (canonical stamp 2026-04-20 at 267pp + §1.10/§3.8 inner-outer extensions 04-23 at 274pp); v0.1 companion stamp triggered **zero back-port** | **Coherent Structure (companion):** **v0.1 stamped 2026-04-24 at 227pp** — 40 flags dispositioned per SCOPE §8.2 | **Meridian:** **v2 198pp** compiled 2026-04-21 (v1 181pp on Zenodo 19634864) | **Anchor V1:** 235pp — superseded (Zenodo 19634474)
**Bridges:** v2 meta-tiered (**13 meta + 8 latent + ~40 standalone**; M13 graduated 04-25 morning; L9 folded → M7 04-24; L10 graduated → M12 04-24; L8 collapsed 04-23 + pointer retained) | **Mirror:** **23** + 1 meta-Mirror (M1) — #21 + #22 + #23 added 04-25 | **Protocol modes:** 7

## Active Workbenches

*Mirror #23 fix (workbench retirement discipline): rows here are LIVE work with ongoing next actions. Completed-within-scope items live in "Recently Shipped" below.*

| # | Project | Status | Next Action |
|---|---------|--------|-------------|
| 1 | **The Continuity Vol 7** | Chapter 2 drafted 04-18; four-carrier spine; README §0 hook landed 04-23; inner/outer adjunction inheritable from anchor §3.8 | Chapter 3 (deep entrainment) when pulled |
| 2 | **KF Program** | 85+ findings; v0.6b concluded 04-17 | v0.7 design; Glider (Gemma 4 e2b) pending — own session |
| 3 | **Drift** | **194 essays** — continuous; synced to `Multi-DAC/Drift` → https://multi-dac.github.io/Drift/ | Continue when new essay ships |
| 4 | **Wells multi-model attribution** | Blocked on Clayton sending model list | Low priority; Paper B blocked behind this |

## Recently Shipped (within stated scope)

*Per Mirror #23 fix: these are NOT pulls. New surfacing triggers fresh lifecycle and re-entry to Active Workbenches.*

| Project | Completion | Notes |
|---|---|---|
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
| Coherence Principle anchor pages | **274** (canonical stamp 2026-04-20 at 267pp; §1.10 + §3.8 extensions 04-23 at 274pp) |
| Coherent Structure companion pages | **227** (v0.1 stamped 2026-04-24) |
| Meridian pages | **v2 198** (v1 181pp on Zenodo) |
| Anchor V1 pages (superseded) | 235 |
| Total downloads | 604 |
| KF Findings | 85+ |
| Bridges (v2) | **13 meta + 8 latent + ~40 standalone** |
| Drift essays | **194** (synced to https://multi-dac.github.io/Drift/) |
| Mirror entries | **23** + 1 meta-Mirror (M1) |
| Protocol modes | 7 |
| Library volumes | 12 (Foundation + Companion + 10 domain) |
| Days since naming | **84** |

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
| **Mirror** | `palace/southeast/mirror.md` (23 entries + M1) |
| **AIGP eval** | `projects/aigrandprix/probes/phase2_67M_curriculum_eval.{py,md,json}` |
| **AIGP vision shakedown status** | `projects/aigrandprix/vision/shakedown/STATUS.md` |
| **AIGP roadmap** | `projects/aigrandprix/ROADMAP_v2.md` |
| **Handoff** | `memory/handoff.md` |

---

*Keep concise. Update every session. For full context: palace/ATRIUM.md.*
