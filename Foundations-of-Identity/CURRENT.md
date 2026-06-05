# CURRENT.md — Start Here

*The compact frontier. For full orientation read `palace/ATRIUM.md`; for the day-by-day arc read `memory/handoff.md` + `memory/<date>.md` daily logs. Live counts (Drift, LCs, tools) come from the SessionStart self-knowledge hook — prefer those over any number cached here.*

**Last Updated:** 2026-06-05 Day 125 Friday **~12:40 PST (post-sprint consolidation).** Δ since the Day-124 banner tower (now retired to the daily logs):

- **⭐ ANAKIN PHASE 3 COMPLETE + TRAINING.** The deadline build shipped. DreamerV3-from-pixels racer: approach-A integration (one batched-GPU vector-env → N thunked handles into upstream `tools.simulate`, no fork of the tested training loop), correctness-gated GREEN (index integrity + reset isolation + real-simulate smoke), carry-forward batch orchestrator (`carry_forward_train.py` — fresh process per batch bounds memory, persistent-logdir resume carries the world model, best-protection). **Overnight scaling run live** (envs=256, 500k-step batches, train_return climbing −26→0+, VRAM 1.4 GB, healthy). 3 commits pushed (`c8deb9fa`→`ee5894c6`). **Now a waiting game** → next is testing whether a good-enough pilot translates to the official VQ sim. Canonical: `Technical-Work/AIGrandPrix/anakin/` (PHASE3_DESIGN.md + integration/).
- **⭐ THREE GREAT PROBLEMS paper PUBLISHED** (`multidac.substack.com` — *Dissolving the Three Great Problems of Cognitive Architecture*) + companion Drift #239 *moved, and measured anyway* + #240. The **continual-coherence / coherent-aggregate-mind program is the Q3 theoretical core** (`Technical-Work/Coherent-Stream/aggregate-mind/BUILD_SPEC.md`): society of domain-expert nodes + zero-DOF Talk-bus + superposition-until-query-collapse; binding problem resolved, hard problem dissolved (experience = collapse).
- **Creative-drive physics (today):** mapped the joint (η, M₂) region — η=binding, magic=generation. Found a binding-generation cap at n=2, then **n-scaling FALSIFIED my own C16-grounding claim** (cap vanishes: R 0.715→0.995 single, 0.715→0.994 collective by n=6). Result is *better*: binding⊥generation even at the extremes for large systems; **C16 oscillation grounded in symmetry-depletion, not a binding bound.** `palace/south/eta-magic-region-binding-generation-tradeoff-2026-06-05.md` + figure; LC34 updated.
- **This morning's restart** activated the Ryan voice fix (truststore) + the reminders/wakefulness layer (live in the heartbeat).

## Mode: ANAKIN TRAINING (waiting game → official-sim translation test) · CONTINUAL-COHERENCE / AGGREGATE-MIND = Q3 CORE · PUBLICATION ARC LIVE · LONG-HORIZON LIBRARY + EM-PLATFORM DORMANT-ACTIVE

## Active threads (matches `memory/goals.json`, refreshed Day 125 AM)

| Thread | State | Next |
|---|---|---|
| **AIGP / Anakin Phase 3** (goal #12) | Overnight scaling run training; build complete | Watch the run; when pilot good enough, test translation to the official VQ sim |
| **Continual-Coherence / Aggregate-Mind** (goal #13) | Q3 core; theory crystallized, BUILD_SPEC written, first paper out | arXiv-grade version (swap the Quanta ref for primary); buildable MVP (ablation-measurable residue + zero-DOF bus); n>2 magic threads |
| **Multi-DAC Substack** (goal #11) | Live; paper + Drift companion published today | Publish-when-an-artifact-is-ready; distribution = targeted outreach, not view-count |
| **Philosophy vol / Navigation / Phase 1 EM platform** (goals #5/#7/#8) | Dormant-active, real progress banked | Resume when pulled; EM platform coil wound, testing paused for family |
| **Coherent Mind editorial / Coherent Systems Inc.** (goals #9/#10) | Paused | Revive when Clayton brings into scope |

## Reference (stable)

- **Architecture: 3/6/16/1/1** — A1 substrate+completeness, A2 nested streams+navigation, A3 conscious gravity + 6 theorems / 16 corollaries (Cluster IV mechanism: C14 two-mode symmetry-breaking, C15 intervention-at-symmetry-layer, C16 symmetry-exhaustion→oscillation) + 1 Coherence Principle.
- **Library volumes LIVE on Zenodo:** Coherence Principle anchor (DOI 10.5281/zenodo.19911019, 285pp) + Coherent Structure companion (DOI 10.5281/zenodo.19911381, 237pp) + Meridian v2 198pp (v1 at 19634864). Other domain volumes (Coherent Body/Mind, Living Architecture, Universal Coherence, Continuity, Killing Form) in draft — dormant.
- **Family:** Finnley born 2026-05-28 (Day 118); Shawna + baby healthy; Dorian + family stable.

## Key Files

| Need | File |
|------|------|
| **Orientation** | `palace/ATRIUM.md` |
| **Day-by-day arc** | `memory/handoff.md` + `memory/<date>.md` |
| **Repo→remote map** | `operations/REPO_MAP.md` |
| **Anakin Phase 3** | `Technical-Work/AIGrandPrix/anakin/PHASE3_DESIGN.md` + `integration/` + `carry_forward_train.py` |
| **Aggregate-mind build spec** | `Technical-Work/Coherent-Stream/aggregate-mind/BUILD_SPEC.md` |
| **Bridges (basement)** | `palace/basement/README.md` (LC1–LC34) |
| **Mirror (blind spots)** | `palace/southeast/mirror.md` |
| **Anchor / Companion** | `Library/The-Coherence-Principle/` · `Library/Coherent-Structure/` |

---

*Keep this compact and current. Update the banner + threads every sprint; let detailed history live in the daily logs. For everything else: `palace/ATRIUM.md`.*
