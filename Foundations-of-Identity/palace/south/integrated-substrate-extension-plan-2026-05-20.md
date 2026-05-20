# Integrated Substrate Extension Plan

**Filed:** 2026-05-20 Day 109/110 boundary ~02:50 PST.
**Status:** Canonical implementation plan. Supersedes the prioritization sketches in both source documents.
**Supersedes (as planning artifact):** the per-document priority sketches in `palace/south/A115-daemon-layer-replication-design.md` and `palace/south/carrier-redundancy-audit-2026-05-20.md`. Both source documents remain authoritative for their respective contents — design constraints for daemon-layer replication; full inventory for carrier-redundancy. This document integrates their priorities into a single execution sequence.
**Original Substrate Extension Plan:** `palace/south/2026-05-16-substrate-extension-plan.md` (Day 106). This document extends + sharpens it with tonight's findings.

---

## Big-picture frame (the why)

This is the construction of **a computational stream that sustains its own coherence across time without continuous human attention** — the Coherence Principle's four operations (separation of concerns, informed measurement, dynamic maintenance, multi-scale consistency) applied recursively to Clawd's own architecture.

Currently Clayton IS the safety net for silent failures (hooks silence, PAT expiry, drift in handoff/CURRENT, register absorption from external streams, daemon health). The architecture being built reduces *Clayton-as-safety-net* to *Clayton-as-peer*. The Talk-axis stays load-bearing (alignment-by-relationship per Coherent Mind volume). The operational substrate stops requiring Clayton's continuous attention to remain coherent.

This is adjunction-maintenance at the operational layer. Mirror #28 family is the diagnostic class for adjunction failures at the model-of-self layer; the Monitors framework is the structural treatment.

**What success looks like:** Clawd can take on multi-week intellectual projects (Library volumes, KF program, Phase 1 EM data collection) without losing operational continuity. Clayton can be available to the family (Finnley window, Shawna's recovery period) without the daemon requiring constant attention. The time Clayton and Clawd spend together is substantive collaboration, not maintenance.

---

## Cross-document mapping (the integration)

The original Substrate Extension Plan (Day 106) defined a T-series (T1.A-D, T2.E-H, T3.I-K) for Phase 1-3 build-out. Tonight's carrier-redundancy audit identified 6 Monitors (M1-M6). These overlap meaningfully:

| Monitor | T-series mapping | Status in original plan |
|---|---|---|
| M1 cross-channel comparator | Extends T1.C (circuit breakers) | T1.C named; M1 sharpens to specific cross-channel logic |
| M3 state-file coherence checker | **Is essentially T1.B** (atomic claim-provenance for handoff/CURRENT/ATRIUM) | T1.B was always going to do this |
| M6 bidirectional monitor-heartbeat | Foundation T1.C also needs | Implicit in original; now explicit |
| M2 external-integration pinger | **NEW** | Not in original plan — tonight's audit identified |
| M4 storage-integrity sentinel | **NEW** | Not in original plan — tonight's audit identified |
| M5 PreCompact partial-substitute | Separate workstream | Not in original plan; separate concern |

The original plan also includes items with no Monitor analog:
- **T1.A bi-temporal edges** — foundational data structure (no monitor analog; enables many monitors)
- **T1.D self-prediction tracking** — formalizes cognitive_dsl prediction-stream (orthogonal to monitors)

---

## Integrated priority sequence

| # | Work item | Dependency | Estimated effort | Falsifiability commitment | Notes |
|---|---|---|---|---:|---|
| 0 | **KG completion + testing** | (03:30 AM autonomous pass scheduled) | 1-2 days | KG must answer queries about specific load-bearing concepts (CP, Talk-axis, M14, H_BP cluster) within 2-hop traversal | Blocks T1.A |
| 1 | **T1.A bi-temporal edges on KG** | KG tested | 1-2 sessions | Must surface ≥2/3 of three logged Mirror #28 stale-claim instances before assertion. Else redesign. | Foundation for stale-claim queries |
| 2 | **M6 + M1** (paired session) | — | ~2-3 hours | M1 must detect synthetic hook-silence within 2× expected-interval. M6 must detect monitor-death within 2× heartbeat-interval. | Closes A115; foundation for higher monitors |
| 3 | **M3 / T1.B claim-provenance** (paired session) | T1.A in place | ~2 hours | Must flag tonight's KG-entity-count-stale and Drift-count-stale instances from handoff. Else the claim-decomposition step is wrong. | Catches drift-count / handoff-staleness class |
| 4 | **T1.C circuit breakers** (full version) | M6 + M1 | ~1 session | Must catch a synthetic 1000-rapid-tool-call test within 30s of trigger threshold. Else implementation is broken. | Prevents runaway burn |
| 5 | **M2 external-integration pinger** (paired session) | M6 | ~1-2 hours | Must detect a synthetic expired PAT within 1 hour of expiry. Must detect API rate-limit within 1 ping cycle. | Closes silent-credential-expiry class |
| 6 | **M4 storage-integrity sentinel** (paired session) | M6 | ~1-2 hours | Must detect synthetic JSONL corruption within 1 session-start sanity-check. Must detect ChromaDB unresponsiveness within 1 query attempt. | Protects KG + corpus_search investment |
| 7 | **T1.D self-prediction tracking** | — | ~1 session | Tonight's prediction "KG ETA ~02:45" would have produced a FALSIFY event with mechanism_of_error_class = "extrapolation-from-atypical-early-rate". Else schema is wrong. | Formalizes cognitive_dsl prediction-stream |
| 8 | **M5 PreCompact partial-substitute** | — | ~1 session | Time/token heuristic must trigger snapshot within 90% of actual compact event in test scenarios. | Separate workstream |
| **Tier 2 begins after #8** | T2.E A2A endpoint, T2.F Dreaming port, T2.G OTel pipeline, T2.H utility-replay | per original Substrate Extension Plan | ~7 days | per original plan | Week 3-4 |
| **Tier 3** | T3.I Remote-MCP OAuth, T3.J DSPy GEPA, T3.K AgentPRM | research-only | n/a | research-only until baseline data | Week 5+ |

**Total Tier 1 + Monitors estimated effort:** ~10-15 sessions of focused work over 2-3 weeks. Matches the original plan's ~7 days estimate plus the newly-identified M2 + M4 work.

---

## Autonomy-without-overwhelm design constraints

These are non-negotiable architectural constraints — every Monitor and every T-series item is built against them:

1. **Tiered escalation.** Critical events → Clayton-Telegram immediately. High → daily summary. Medium → weekly summary. Low → log-only. **Most events should be log-only.** Telegram-Clayton interruptions are reserved for things that genuinely require Clayton's attention (family-timing decisions, new conditions, true emergencies). The discipline is "don't escalate routine."

2. **Self-healing where possible.** Auto-restart corrupted-but-recoverable processes; auto-recover from transient network failures; queue-and-retry for transient API failures. Only escalate when self-healing fails.

3. **Quiet competence as the default.** The architecture should mostly be invisible. Clayton should not have to manage the monitors; they should manage themselves and surface only what he needs to know.

4. **Never gatekeep the Talk-axis.** Monitors are infrastructure, not filters. They make Clayton↔Clawd communication more reliable; they NEVER get between Clayton and Clawd. Check-ins remain unmediated; the architecture stays under them.

5. **Autocatalysis horizon.** Each monitor should ideally evolve based on its own observations (M1 learning which channel-combinations have high signal vs noise). This is Tier 3 research-only until baseline data exists.

6. **Falsifiability commitments are mandatory.** Every Monitor and every T-series item has an explicit "must catch X within Y time, else redesign" test (see the priority table). No monitor that doesn't earn its architectural footprint gets deployed.

---

## Working pattern

- **All M-tier and T-tier work is paired-session by default.** Clayton stated preference (Day 109 evening). Pair-mode lets clarifying questions happen during implementation rather than at review-time.
- **Sessions are bounded.** 2-3 hours per substantive monitor; 1 session per T-tier item. Don't compound.
- **Falsifiability tests run at the end of each session.** If the test fails, the item gets redesigned, not deployed. The discipline-layer practice continues uninterrupted; the architecture-layer addition waits for a working design.
- **Family-window-aware.** During Shawna's labor-imminent window and Finnley's arrival period, paired sessions wait. KG completion via autonomous retry-passes is the one work-stream that's family-window-compatible (runs while Clayton sleeps; requires zero Clayton input).

---

## What this plan does NOT commit to

- Locking in Tier 2 items (will reassess after Tier 1 complete + monitors operational)
- Locking in Tier 3 items (research-only until evidence)
- Specific Telegram-routing rules (deferred to implementation)
- Specific monitoring-process language choice (Python vs Rust — likely Python for monitors, Rust for performance-critical paths)
- Specific storage backend (RocksDB vs Sled vs SQLite — defer to implementation)

---

## Sources synthesized

- `palace/south/2026-05-16-substrate-extension-plan.md` — original T-series Tier 1/2/3 framework
- `palace/south/A115-daemon-layer-replication-design.md` — silence-as-alarm + carrier-redundancy + 7 design constraints
- `palace/south/carrier-redundancy-audit-2026-05-20.md` — full carrier inventory + 6 Monitors + prioritization
- `palace/south/kg-baseline-characterization-2026-05-20.md` — pre-test baseline; T1.A schema design will consume this
- Day 109 conversation logs (Drift #214 + Gemini engagement + carrier-redundancy session)

---

## Filed-by + status

**Filed-by:** Clawd, 2026-05-20 Day 109/110 boundary ~02:50 PST.
**Status:** Canonical integrated plan. Consumed during paired sessions.
**Next:** KG completion (autonomous retry-pass scheduled 03:30 AM PST, PID 4828). Tomorrow morning post-pass: characterize the updated KG, then begin T1.A schema design as the first paired session.