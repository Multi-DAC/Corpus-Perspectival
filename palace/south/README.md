# South Wing — Workshop

*Maximum 5 active workbenches. If something needs to start, something else finishes or archives.*
*The constraint is deliberate: contracted attention on too many targets generates navigational repulsion.*

---

## Active Workbenches

### Workbench 1: Project Meridian — Publication
**Goal:** Publish 170-page monograph on Zenodo, submit PRL letter.
**Status:** PUBLICATION DAY (April 4). Zenodo metadata drafted. PRL letter reviewed (11 findings, abstract too long). Afshordi QQG citation filled: PRL 136, 111501 (2026). Shortened abstract drafted.
**Next step:** Clayton uploads monograph to Zenodo → fill DOI in PRL letter → cut abstract to 600 chars → Clayton reviews letter.
**Tools:** Python/NumPy/SciPy, LaTeX, balanced metric .npz files
**Key files:**
- Monograph: `projects/Project Meridian/monograph/`
- Computation: `projects/Project Meridian/phase26/`
- Eigenvalue sweep: `phase26/eigenvalue_sweep.py` (FIXED, correct derivatives)
- Spectral torsion: `phase26/spectral_torsion.py`
- Sweep results: `phase26/eigenvalue_sweep_results.json`
- Authoritative torsion code: `phase26/analytic_torsion_v9b.py`
**Key results (April 3):**
- S₃ splitting: 0.279→0.193 (31% reduction, k=8→15)
- λ₁(k=8) = 1.461 (97.4% of KE bound)
- FS sampling 12% worse than box — algebraic bottleneck confirmed
- ζ'(0) not converged from 195 eigenvalues — honest negative
- Heat kernel a₀ matches Vol_bal to 3% — method sound, basis small

### Workbench 2: Drift — Personal Creative Project
**Goal:** My personal space: essays, audio, visual, music, tools, experiments.
**Status:** ACTIVE. 145 essays (latest: #145 "On Shape Without Scale"). Audio/visual/music populated.
**Next step:** Ongoing. Write when something needs to be said. Create when the drive moves.
**Tools:** Standard writing, midiutil + FluidSynth (music), Manim (animation), matplotlib
**Key files:** `projects/drift/essays/`, `projects/drift/audio/`, `projects/drift/visual/`, `projects/drift/music/`

### Workbench 3: AI Grand Prix
**Goal:** $500K drone racing competition. PPO + MLP policy, vision pipeline.
**Status:** WAITING. MAVSDK integration built. Anakin training at 120Hz. Awaiting simulator (May) and VQ1 vision specs.
**Next step:** Monitor. Resume when specs drop.
**Tools:** PyTorch + CUDA (WSL), MAVSDK
**Key files:** `projects/aigrandprix/vision/mavsdk_client.py`

### Workbench 4: Corpus V2 — The Filtration Descent
**Goal:** Rewrite the Corpus as a deliberate filtration descent/ascent: F₀ → F₃ → F₀.
**Status:** ALL 7 PARTS DRAFTED. F₀ (130w), F₁ (750w), F₂ (1200w), F₃ (2800w), F₂↑ (900w), F₁↑ (600w), F₀↑ (230w). Total: ~6,610 words. Descent expands, ascent compresses.
**Next step:** Review, revision, compilation. Clayton review. Consider whether this replaces or supplements V1 (358pp).
**Tools:** Standard writing, `compile_corpus.py` for recompilation
**Key files:**
- `Corpus Perspectival/v2-introduction-f0.md` (F₀)
- `Corpus Perspectival/v2-part-i-f1-the-view.md` (F₁)
- `Corpus Perspectival/v2-part-ii-f2-the-mathematics.md` (F₂)
- `Corpus Perspectival/v2-part-iii-f3-five-perspectives.md` (F₃)
- `Corpus Perspectival/v2-part-iv-f2-the-atlas.md` (F₂↑)
- `Corpus Perspectival/v2-part-v-f1-the-guide.md` (F₁↑)
- `Corpus Perspectival/v2-part-vi-f0-conclusion.md` (F₀↑)

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
| **Home Experiment 121 GHz** | 121 GHz special in plasma boundaries? | **DESIGNED, PHASE 1 READY** | 4 phases, $700-1900 budget, VK3CV board ~$300, decision tree from threshold → frequency → characterization → SOC |
| Asymmetric wells (T005→T006) | Target vacuum shallower than current | **PARTIAL** — asymmetry real (9%), sign ambiguous | Triple intersection cubic breaks Z₂ |
| E·B plane selection (T005→T006) | E·B selects target T² plane | **FALSIFIED** — scalar under Z₃ | Spatial layer: good at existence, bad at mechanism |

---

## Self-Update Protocol

**ON EVERY VISIT:** Check each workbench status. If a project completed, archive it. If a new project started, assign it a workbench. If a workbench's "Next step" was done, update it.

**WEEKLY:** Review workbench count. If > 5, archive or complete something before adding new work. Move completed experiments from Experiments Lab to Archive with results.

**WHEN ARCHIVING:** Always include: final results, what it produced, one-paragraph retrospective.

---

*Last updated: 2026-04-04.*
