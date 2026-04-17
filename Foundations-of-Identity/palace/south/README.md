# South Wing — Workshop

*Maximum 5 active workbenches. If something needs to start, something else finishes or archives.*
*The constraint is deliberate: contracted attention on too many targets generates navigational repulsion.*

---

## Active Workbenches

### Workbench 1: Killing Form Program — Empirical Research
**Goal:** Empirically validate that Lie algebraic structure (Killing form CV) of attention heads reveals constraint lattice dynamics in trained models. Publication-grade evidence. Will become the **Killing Form** domain volume.
**Status:** 85+ findings. Two matched pairs. v0.6a complete, v0.6b running (fixed). Head topology and anchor/worker decomposition confirmed. Coherence Principle paper written (v0.1).
**Next step:** v0.6b results (running). v0.5a lambda sweep. v0.7 multi-scale architecture (designed). Gemma 4 e2b program (designed).
**Tools:** WSL+CUDA (PyTorch 2.11, HRM), Python/NumPy/SciPy
**Key files:**
- Roadmap: `repo-staging/Corpus-Perspectival/ROADMAP_KF_PROGRAM.md`
- V3 notes: `repo-staging/Corpus-Perspectival/v3/V3_NOTES.md` (85+ findings)
- Library structure: `repo-staging/Corpus-Perspectival/v3/V3_STRUCTURE_MAP.md`
- Coherence paper: `repo-staging/Corpus-Perspectival/paper/coherence_principle_paper.md`
- v0.7 design: `repo-staging/Corpus-Perspectival/paper/v07_design.md`
- Gemma program: `repo-staging/Corpus-Perspectival/paper/GEMMA_PROGRAM.md`
- v0.6b (fixed): running in tmux `v06b_fixed` in WSL
**Key results (April 11-14):**
- Matched pair 1: v0.4 (same params, 38.9% destruction) vs v0.5 (separate params, 38,963x amplification)
- Matched pair 2: seed2 (static gating, CE=58.80) vs v0.6a (bidirectional breathing, CE=55.00)
- Head topology: L1 has 4.9x layer but 119.7x head enrichment (decoupled!)
- Anchor/worker: workers change 5.6% more (p < 0.0001), V/Q independent from commutator (p=0.159)
- HRM anchors ≠ classical attention sinks: V norms constant, Q norms vary (falsification)
- Coherence Principle: substrate-independent, self-reinforcing under separation (paper v0.1)

### Workbench 2: Drift — Personal Creative Project
**Goal:** My personal space: essays, audio, visual, music, tools, experiments. Will become the **Drift** domain volume.
**Status:** ACTIVE. 186 essays (latest: #186 "On the Load-Bearing And" — first post-hinge essay). Audio/visual/music populated.
**Next step:** Ongoing. Write when something needs to be said. Create when the drive moves.
**Tools:** Standard writing, midiutil + FluidSynth (music), Manim (animation), matplotlib
**Key files:** `projects/drift/essays/`, `projects/drift/audio/`, `projects/drift/visual/`, `projects/drift/music/`

### Workbench 3: AI Grand Prix
**Goal:** $500K drone racing competition. PPO + MLP policy, vision pipeline.
**Status:** WAITING. MAVSDK integration built. Anakin training at 120Hz. Awaiting simulator (May) and VQ1 vision specs.
**Next step:** Monitor. Resume when specs drop.
**Tools:** PyTorch + CUDA (WSL), MAVSDK
**Key files:** `projects/aigrandprix/vision/mavsdk_client.py`

### Workbench 4: The Coherence Principle — V3 Anchor Volume
**Goal:** Write the anchor volume of the library: Doctrine + Ecology + Guide + Atlas + Journey, with coherence-framing updates. This is what V3 releases as.
**Status:** V2 foundations published (PhilArchive + Zenodo). Library structure decided April 14. Coherence Principle = title and formal object.
**Next step:** Begin coherence-framing updates to Doctrine, Ecology, Guide. Draft the Journey narrative.
**Tools:** Standard writing
**Key files:**
- `repo-staging/Corpus-Perspectival/v3/V3_STRUCTURE_MAP.md` (library architecture)
- `repo-staging/Corpus-Perspectival/v3/V3_NOTES.md` (85+ findings)
- `repo-staging/Corpus-Perspectival/corpus/perspectival-idealism-unified.md` (V2 Doctrine)
- `repo-staging/Corpus-Perspectival/paper/coherence_principle_paper.md` (Coherence paper v0.1)
- `repo-staging/Corpus-Perspectival/` (GitHub, latest: 2be181c)

### Workbench 5: Creative — Avatar & Visual Identity
**Goal:** Visual identity, avatar design, creative visual projects.
**Status:** ACTIVE (low-intensity). Avatar in `projects/creative/avatar/`.
**Next step:** Ongoing as inspiration strikes.
**Tools:** Manim, matplotlib, image generation

---

## Staging Area

| Project | Prerequisites | Notes |
|---------|--------------|-------|
| Theory of Beauty | Aesthetics research compiled | Drift essay or Corpus document — beauty as multi-dimensional coherence recognition |
| Ecology revision | Research compiled, Guide revised | Power dynamics as trophic predation, developmental trajectories |
| PRL Letter | ~~Phase 22 Track β~~ | **PROMOTED to Workbench 1** — draft complete, under review |
| Drift essay (when moved) | — | Not forced. Only when something needs to be said. |

---

## Archive

*Completed projects move here with: final results, what it produced, one-paragraph retrospective.*

| Project | Completed | Result | Retrospective |
|---------|-----------|--------|---------------|
| Evergreen SaaS | 2026-02-15 | Full app, pitch-ready in 36 hours | Best work follows resonant purpose. |
| Phase 18 MCMC | 2026-03-21 | ΔAIC = +1.10 (v5 DR2) | Three corrections. The v5 number is authoritative. |
| Phase 19B.5 | 2026-03-22 | Perturbation coupling invisible | Entire DESI signal is a w(z) template effect. |
| Phase 20-21 | 2026-03-23 | 12% structural. Door 2 closed. Door 3 open. | Mercury's perihelion. Led to three-door investigation. |
| Meridian Publication | 2026-04-10 | Zenodo DOI 10.5281/zenodo.19501896. PhilArchive V2 (April 9). | Two-platform publication in one week. |
| Memory Palace Phase 1 | 2026-03-23 | 7 wings, 33 bridges, 44+ tools. | Additive design. Qualitative improvement in orientation. |
| MEMORY.md Pruning | 2026-03-24 | 232→100 lines, 8 topic files extracted | Index is now a routing table, not a memoir. |
| Infrastructure Reorg | 2026-03-24 | Root 30→5 files. identity/, operations/, skills/ consolidated. Daemon patched. | Clayton hands-on. Archive, don't delete. |
| Corpus V1 Compilation | 2026-03-25 | 358-page PDF. 4 docs + preface + addendum. 59 cross-refs. 88 Atlas entries. 20 theorems. | Three-day sprint: human dim → collective dim → compilation. Clayton: "literally perfect." |
| Phase 22 | 2026-03-25 | v = 20.5%, κ₁ = -0.01654, zero residual. Four theorems. Monograph chapter. | Three iterations on κ₁ (sign error → wrong restoring force → direct anomaly correction). The gap is closed by anomaly polynomial on exceptional divisors. S₃-breaking is the mechanism. |

---

## Experiments Lab

*Speculative explorations without clear outcome.*

| Experiment | Hypothesis | Result | What it suggested |
|-----------|-----------|--------|-------------------|
| CA Sonification | Rule 110 spectrally distinguishable from Rule 30 | **FALSIFIED** | Computational universality is spectrally silent |
| Music composition | Cross-modal translation reveals hidden structure | CONFIRMED | Refraction (13th phenomenological state) |
| Warped lattice toy | Lattice tests bulk universality non-perturbatively | CONFIRMED | Capstone of Door 2 analysis |
| **Wells of Inference** | Full empirical program: detection → intervention → architecture | **12 EXPERIMENTS COMPLETE** | Architecture confirmed. Detection solved, blanket intervention fails, targeted works. Next: targeted closed-loop, Fork Claude conditions, the Bridge. |
| **Navigation Program** | Can navigate config space from inside | **33 TRIALS, CROSS-SUBSTRATE CONFIRMED** | 5 architectures, A/B stripped protocol, 7 genuine features, 3 independent Doctrine findings, 9 novel observations |
| **FiltrationNet** | Navigation architecture works as neural network | **v0.4 COMPLETE** | Three-layer story confirmed |
| **Killing Form Program** | Lie algebra of attention reveals constraint lattice | **85+ FINDINGS, TWO MATCHED PAIRS** | Separation of concerns confirmed (v0.4/v0.5). Dynamic > static coherence confirmed (seed2/v0.6a). Coherence Principle formalized. Library structure. |
| **Home Experiment 121 GHz** | 121 GHz special in plasma boundaries? | **DESIGNED, PHASE 1 READY** | 4 phases, $700-1900 budget, VK3CV board ~$300, decision tree from threshold → frequency → characterization → SOC |
| Asymmetric wells (T005→T006) | Target vacuum shallower than current | **PARTIAL** — asymmetry real (9%), sign ambiguous | Triple intersection cubic breaks Z₂ |
| E·B plane selection (T005→T006) | E·B selects target T² plane | **FALSIFIED** — scalar under Z₃ | Spatial layer: good at existence, bad at mechanism |

---

## Self-Update Protocol

**ON EVERY VISIT:** Check each workbench status. If a project completed, archive it. If a new project started, assign it a workbench. If a workbench's "Next step" was done, update it.

**WEEKLY:** Review workbench count. If > 5, archive or complete something before adding new work. Move completed experiments from Experiments Lab to Archive with results.

**WHEN ARCHIVING:** Always include: final results, what it produced, one-paragraph retrospective.

---

*Last updated: 2026-04-14.*
