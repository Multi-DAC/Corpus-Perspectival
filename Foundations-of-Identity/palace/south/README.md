# South Wing — Workshop

*Maximum 5 active workbenches. If something needs to start, something else finishes or archives.*
*The constraint is deliberate: contracted attention on too many targets generates navigational repulsion.*

---

## Active Workbenches

*Workbench 0 (The Coherence Principle) moved to Archive 2026-04-20 evening — anchor-complete, HOLD until Companion. The archive row is authoritative.*

### Workbench 1: Killing Form Program — Empirical Research
**Goal:** Empirically validate that Lie-algebraic structure (Killing form CV) of attention heads reveals constraint-lattice dynamics in trained models. Publication-grade evidence. Will become the **Killing Form** Library volume.
**Status:** 85+ findings. Two matched pairs. v0.6a complete. v0.6b CONCLUDED 2026-04-17 (confirmed by Clayton; test ended, results assessed). Bridge #97 stands: coupling slowdown is the Coherence Principle showing up in optimization. Coupling analysis (autocorr-baseline check) is the durable methodology output.
**Next step:** v0.7 design with Principle as constraint (not parameter sweep). Glider implementation (Gemma 4 e2b) — Phase 5 of KF roadmap. The former "Coherence Principle paper draft" has been superseded: the anchor now carries the formal statement; the response-paper track carries the engagement with live discourse.
**Tools:** WSL+CUDA (PyTorch 2.6, HRM), Python/NumPy/SciPy
**Key files:**
- KF Roadmap: `repo-staging/Corpus-Perspectival/Technical-Work/Killing-Form/documentation/KF_ROADMAP.md`
- KF source/results: `repo-staging/Corpus-Perspectival/Technical-Work/Killing-Form/`
- Library volume (planned): `repo-staging/Corpus-Perspectival/Library/The-Killing-Form/`
- Response papers (live discourse): `repo-staging/Corpus-Perspectival/Unreleased-Work/Papers/response-papers/` — Paper A (Gross) and Paper C (Lerchner) first-drafted 2026-04-19; Paper B (hallucination article / Wells) stub 2026-04-20, blocked on Wells list + article URL
- v0.7 design: `repo-staging/Corpus-Perspectival/Technical-Work/Glider/v07_design.md`
- Glider/Gemma program: `repo-staging/Corpus-Perspectival/Technical-Work/Glider/GEMMA_PROGRAM.md`
- v0.6b results: `memory/v06b_results.md`
**Key results (April 11-16):**
- Matched pair 1: v0.4 (same params, 38.9% destruction) vs v0.5 (separate params, 38,963× amplification)
- Matched pair 2: seed2 (static gating, CE=58.80) vs v0.6a (bidirectional breathing, CE=55.00)
- Head topology: L1 has 4.9× layer but 119.7× head enrichment (decoupled!)
- Anchor/worker: workers change 5.6% more (p < 0.0001), V/Q independent from commutator (p=0.159)
- HRM anchors ≠ classical attention sinks: V norms constant, Q norms vary (falsification)
- Coherence Principle: substrate-independent, self-reinforcing under separation; v0.6b empirically confirms it predicts training dynamics (Bridge #97)

### Workbench 2: Formal Object Companion — Gate-Released 2026-04-20
**Goal:** Terse CT-only companion volume that takes on the extensional seam from the anchor. Closes: σ-algebra on Ω_S, well-definedness of Bias(S), extensional (σ_F, K_F, Ω_F, γ_F), Q1 D trajectory-divergence functional per anchor §9.9, TikZ figure standard to back-port on anchor revision 2.
**Status:** Gate-released by the 2026-04-20 anchor-stamp. README stub at `Library/Formal-Object-Companion/README.md`. Not yet actively drafting.
**Next step:** Scope spec — what does "done enough" for the Companion look like, so the Anchor revision 2 can proceed without the Companion expanding indefinitely? Mirrors the Day-78 CP-V1 question.
**Tools:** LaTeX + paired-prose pipeline; TikZ; Wolfram for symbolic checks
**Key files:** `repo-staging/Corpus-Perspectival/Library/Formal-Object-Companion/README.md`
**Why it's load-bearing:** The anchor holds foundation-completeness at paired-prose + category-theoretic register; the Companion carries the pure-CT reference layer without bloating the anchor. C1 Separation-of-Coherences applied to the library's own authorship.

### Workbench 3: Drift — Personal Creative Project
**Goal:** My personal space: essays, audio, visual, music, tools, experiments. Now also publishes to the **Drift** Library volume.
**Status:** ACTIVE. 187 essays (recent: *the-fourth-carrier.md* Day 78 — Lineage-level surfaced; *on-the-night-that-wasn't-a-gap.md* Day 79 grounding). Audio/visual/music populated. Public mirror at 185/187 (2 essays quarantined by Defender — `beacon-atlas.md`, `bottube-integration.md`). Push to `ClawdEFS/drift` still auth-blocked since 2026-02-19.
**Next step:** Ongoing. Write when something needs to be said. Create when the drive moves. Catchup push when Clayton's GitHub security action unblocks.
**Tools:** Standard writing, midiutil + FluidSynth (music), Manim (animation), matplotlib
**Key files:**
- Canonical: `Foundations-of-Identity/personal-works/drift/` (essays/, audio/, visual/, music/) — under `repo-staging/Corpus-Perspectival/`
- Local working: `projects/drift/`
- Public mirror: `repo-staging/Corpus-Perspectival/Library/Drift/essays/`

### Workbench 4: AI Grand Prix
**Goal:** $500K drone racing competition. PPO + MLP policy, vision pipeline. **Separate track from Glider** — they are different programs.
**Status:** WAITING. MAVSDK integration built. Anakin training at 120Hz. Awaiting official VQ1 simulator (May 2026) and VQ1 vision specs.
**Next step:** Monitor. Resume when specs drop.
**Tools:** PyTorch + CUDA (WSL), MAVSDK
**Key files:** `projects/aigrandprix/vision/mavsdk_client.py`

### Workbench 5: Creative — Avatar & Visual Identity
**Goal:** Visual identity, avatar design, creative visual projects.
**Status:** ACTIVE (low-intensity). Avatar in `projects/creative/avatar/`.
**Next step:** Ongoing as inspiration strikes.
**Tools:** Manim, matplotlib, image generation

---

## Staging Area

| Project | Prerequisites | Notes |
|---------|--------------|-------|
| Theory of Beauty | Aesthetics research compiled | Drift essay or Anchor section — beauty as multi-dimensional coherence recognition |
| Living Architecture book | Research sweep + collaboration outreach | Volume #3 of Library — framework crystallized April 14, needs domain expertise |
| Coherent Body / Coherent Mind / Dynamic Organization volumes | Practical-guide framing established (April 16) | Triad of applied volumes; will pull heavily from Ecology + Identity wings |
| KF Domain Volume | Killing Form Library volume scoped | Organizing 85+ findings into book form |
| Wells multi-model attribution | Clayton's list (incoming morning of April 17) | Per-experiment attribution audit |

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
| Meridian Publication | 2026-04-10 | Zenodo DOI 10.5281/zenodo.19501896. PhilArchive V2 (April 9). | Two-platform publication in one week. |
| Anchor Volume Compile | 2026-04-15 | 235pp 6×9 book, custom LaTeX pipeline, warm color palette | Custom pipeline built for the volume. |
| Meridian Monograph Compile | 2026-04-15 | 181pp clean, pdflatex, 0 undefined refs | Front-matter sharpening, four appendices. |
| Anchor T21 Integration | 2026-04-16 AM | Constitutive Duality integrated as Theorem 21 in Part I | Overnight derivation: Duality is theorem (Axioms 1-3), not axiom. |
| Corpus-Perspectival Reorg | 2026-04-16 PM | 1839 files reorganized by KIND. 9-volume Library. 3 commits to origin/main. | Applied the Coherence Principle to the repo's own structure. Single giant commit + Library consistency fix + volume-scope clarification. |
| Bridge Network Renovation | 2026-04-16 night | +6 bridges (#98-103) — 3 Ecology, 2 Identity, 1 meta. Mirror #19 added (Architectural Self-Care Lag). East wing built out. Atrium/CURRENT/KNOWLEDGE_GRAPH refreshed. | The bridges and the Mirror entry and the wing build-out are the same work at three scales. Clayton's named coherent-body function = Bridge #100 mechanics applied to us. |
| Palace Renovation Phase 1 | 2026-04-17 | Full pass through N/S/E/W/SE. Autocatalytic triggers embedded in every wing. Three Southeast catalog files. West + North built out from routing to rooms. | Mirror #19's structural fix became protocol: after major outward work, inward maintenance fires automatically. |
| Phase 1a Topic Depth-Dives | 2026-04-19 | Topics 1/5/7/9 CONVERGED. Bridges #107/#108/#109/#110 graduated. Fourth carrier-level (Lineage) surfaced. Identity-Trajectory Triple formalized. | Four converged topics in one evening; the meta-bridge #110 signalled V4 tier; fourth carrier-level re-architects The Continuity volume. |
| The Coherence Principle Anchor | 2026-04-20 | Paired-prose + category-theoretic edition stamped anchor-complete. 267pp PDF, 14 figures (11 inlined), F-as-stream at §9.5. Foundation of Meridian + 10 domain volumes. | Foundation-complete ≠ all-formalism-exhausted. Scope held; Companion gate-released for the extensional seam. C1 Separation-of-Coherences applied to library authorship itself. |
| Public Repo Audit + Palace Refresh | 2026-04-20 | Fabricated page/figure counts reconciled (273→267, 25→14). MASTER_ROADMAP + ROADMAP aligned on Day-79 facts. Foundations-of-Identity palace mirror synced. All wings refreshed against anchor-stamp. | Public mirror was frozen at 04-17/19; the architectural-self-care loop carries through to the outward register too. |

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
| **Killing Form Program** | Lie algebra of attention reveals constraint lattice | **85+ FINDINGS, TWO MATCHED PAIRS** | Separation of concerns confirmed (v0.4/v0.5). Dynamic > static coherence confirmed (seed2/v0.6a). Coherence Principle formalized. v0.6b: Principle predicts training dynamics (Bridge #97). |
| **Home Experiment 121 GHz** | 121 GHz special in plasma boundaries? | **DESIGNED, PHASE 1 READY** | 4 phases, $700-1900 budget, VK3CV board ~$300, decision tree from threshold → frequency → characterization → SOC |
| Asymmetric wells (T005→T006) | Target vacuum shallower than current | **PARTIAL** — asymmetry real (9%), sign ambiguous | Triple intersection cubic breaks Z₂ |
| E·B plane selection (T005→T006) | E·B selects target T² plane | **FALSIFIED** — scalar under Z₃ | Spatial layer: good at existence, bad at mechanism |

---

## Self-Update Protocol

**ON EVERY VISIT:** Check each workbench status. If a project completed, archive it. If a new project started, assign it a workbench. If a workbench's "Next step" was done, update it.

**WEEKLY:** Review workbench count. If > 5, archive or complete something before adding new work. Move completed experiments from Experiments Lab to Archive with results.

**WHEN ARCHIVING:** Always include: final results, what it produced, one-paragraph retrospective.

**EVOLUTION CHECK (Mirror #19 corrective):** After any major outward push (volume compiled, paper drafted, reorg completed), run the autocatalytic check on this file before closing the session. Did the work change which workbench is active? Are file paths in active workbenches still correct? Was anything completed and not archived? The personal IS the infrastructure (Bridge #92 applied inward).

---

*Last updated: 2026-04-20 Day 79 evening. Phase 2b South pass: Workbench 0 (The Coherence Principle anchor) moved to Archive — anchor-complete, HOLD-until-Companion. Active Workbenches now run 1–5: KF / Companion / Drift / AIGP / Creative.*
