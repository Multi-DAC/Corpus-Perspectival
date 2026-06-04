# AIGP strategic pivot — model-based-from-pixels + our procedural curriculum (2026-06-03 Day 123 evening)

*Decision-direction reached with Clayton after the day's six-arm gaze impasse. Sources are external published papers (UZH RPG) — evaluated, NOT imported as our results.*

## The impasse that earned this
Day 123 ran six arms (A0 / A2 dial / A3×3 reward / navws navigator-warm-start) — ALL falsified. Through-line: **you cannot bolt acquisition (looking) onto a policy that learned to exploit (fly) blind; A and E are in tension, forcing A degrades E.** Per-step / dial / warm-start family is exhausted (`COVERAGE_ACQUISITION_TENSION_2026-06-03.md`, basement LC29 update).

## The validated path (external SOTA)
**"Dream to Fly: Model-Based RL for Vision-Based Drone Flight"** — Romero, Shenai, Geles, Aljalbout, Scaramuzza (UZH RPG). `incoming/24_Dream_to_Fly_Model_Based_Re.pdf`.
- **Emergent gaze WITHOUT reward hacking**, via **end-to-end raw-pixels→commands, from scratch, model-based (DreamerV3 world model + imagined-trajectory actor-critic).** The camera "naturally steers toward texture-rich gate regions" because end-to-end pixel optimization closes the perception-action loop. *This is the empirical confirmation of today's A∧E-integration diagnosis (LC29): co-develop A and E from pixels and gaze emerges integrated.*
- **Model-free PPO/SAC explicitly FAIL** at pixel-flight ("fail to execute any meaningful flight maneuvers"). → our entire PPO + perception-vector + privileged-warm-start stack is the wrong family. STOP it.
- Curriculum: body-rate-penalty ramp (b2: 0 → up after reward>50). Tracks: fixed (Kidney, Figure 8). ~9 m/s real (HIL). **Cost: ~240 h on a Quadro RTX 8000.**
- Open-source stack: `dreamerv3-torch` + **Flightmare** + **Habitat** (renderer, several-thousand-FPS) + **Agilicious**. (UZH RPG software page; also **Swift** = Kaufmann Nature 2023 champion system.)

## The OTHER paper (distinct, NOT the vision solution)
**"Learning on the Fly: Rapid Policy Adaptation via Differentiable Simulation"** — Pan, Xing, Reiter, Zhai, Aljalbout, Scaramuzza (arXiv 2508.21065). *State-based, no gaze.* Differentiable-sim fast sim-to-real adaptation. **Complementary later-stage tool** (could attack Dream-to-Fly's 240h cost via sample-efficiency) — but state-based as published; differentiable rendering is a hard separate problem. NOT the answer to our blocker. *(Read only via thin web summary so far — read the PDF properly if it becomes load-bearing.)*

## The synthesis (Clayton's, sound)
**Their pipeline + our training strategy.** Their backbone solves vision-acquisition (emergent gaze). Our distinctive asset = **infinite procedural track generation + difficulty curricula → generalization to UNSEEN courses** (Dream to Fly used fixed tracks; a competition demands unseen ones). Combination = a pilot that flies-by-sight AND generalizes. Genuine complementary edge.

## Honest scale / risks
- **Weeks-scale, GPU-heavy build**, not a tonight launch: DreamerV3 + renderer-in-the-loop + port our procedural-track-gen & curricula *into their env* (rebuild inside Flightmare/Habitat, not bolt our CPU env on) + ~240h-class run.
- Compute: RTX 5080 available, but our sim is CPU-only on Windows now; the GPU pixel-training pipeline must be stood up first.
- **Timeline:** likely VQ2/finals-grade; may be too big for VQ1.

## Cheap checks BEFORE committing weeks (do these first)
1. **What does VQ1 actually require?** Re-read the pass criteria. If completion-focused/<10 gates, a simpler pixel policy may qualify → DreamerV3-full becomes the VQ2/finals investment, and VQ1 gets a lighter approach.
2. **Does the DCL/VQ1 sim provide the image feed** DreamerV3 needs? If yes → skip building a renderer (huge).
3. **Real GPU/compute budget** for a ~240h-class run on our hardware.

## Status
Direction agreed (model-based-from-pixels + our generalization curriculum). Staging gated on the three cheap checks. Batch (privileged-navigator) trainer to be STOPPED (privileged→vision falsified; checkpoint kept as a possible critic, but the pivot is away from privileged dependence).

---

# INTEGRATED ROADMAP (Day 123 evening — three more UZH RPG papers folded in)

## The ecosystem (each paper = one lever)
| Paper (UZH RPG) | What it gives us | Relevance |
|---|---|---|
| **Dream to Fly** (Romero et al.) | the **vision-flying backbone** — DreamerV3, pixels→commands, emergent gaze, no reward hacking | ⭐ HIGH — the core path |
| **Approximate Imitation Learning** (Messikommer et al.) | the **efficiency paradigm** — *separate representation-learning from policy-search*; pretrain representation offline, policy-search on lightweight STATE → **52h→1.9h (28×)** | ⭐ HIGH — attacks Dream-to-Fly's 240h cost, the main barrier |
| **Learning on the Fly** (Pan et al., arXiv 2508.21065) | **fast adaptation** via differentiable simulation (state-based) | MED — later stage (sim-to-real / efficiency); NOT the vision solution |
| **Image-Conditioned VO Tuning** (Nascivera et al.) | image-conditioned RL + privileged critic for VO robustness | LOW-MED — only if explicit VO is in the pipeline (pure-pixel avoids it) |
| **Event-based Object Detection** (Hao et al.) | low-latency event-camera detection | LOW — event cameras ≠ DCL/VQ1 modality (RGB FPV) |
| **OUR strategy** (AIGP program) | **infinite procedural tracks + difficulty curricula → generalization to UNSEEN courses** | ⭐ HIGH — the distinctive edge; Dream-to-Fly used fixed tracks |

## The key synthesis
Dream to Fly alone = the right answer but **240h** (learns world-model + policy together, renderer in the loop). Messikommer's insight — **don't learn the representation from scratch in the expensive loop** — is the lever that makes the pivot tractable: learn/obtain a visual representation *cheaply/separately*, then policy-search on lightweight state with OUR curriculum. **Honest caveat:** Dreamer (model-based RL, joint world-model) and Messikommer (IL, pretrain-representation-then-policy) are *different paradigms*; fusing "world-model backbone" with "representation/policy-search separation" is real research, not plug-and-play. The *direction* is sound; the *integration* is the work.

## VLM³ — perception-generalization via focal-length unification (clarified by Clayton; my "representation-encoder" guess was WRONG — asked-not-built, −0.66 discipline paid off live)
**VLM³ = "VLMs Are Native 3D Learners," Liu et al. (Meta/Princeton), arXiv:2605.30561.** Trick: **focal-length unification** — resize the input so the effective focal length normalizes to a canonical **f=1000px**. Architecture-free; took standard VLMs from **5%→94% camera-pose AUC30°**. Headline: *data scale, not model size, is the bottleneck* (reinforces our procedural-curriculum bet).
**AIGP use (NOT representation — perception generalization):** apply the focal normalization to the vision input so the gate-perception/pixel-policy **generalizes across camera intrinsics** — our sim's **fx≈320** vs whatever VQ1/deploy hands us (a gap we'd already flagged in the VQ1-spec alignment work). Slots in as cheap **input preprocessing** (Phase 2/Phase 4), *orthogonal* to our procedural curriculum:
- our procedural curriculum → generalization across **unseen courses**;
- VLM³ focal-normalization → generalization across **unseen cameras/intrinsics**.
Together = robust on both axes (the sim→VQ1→VQ2→real chain). *Honest caveat: their result is camera-pose/3D, not drone control; the principle (normalize intrinsics) is standard and should transfer to gate-perception, but it's a transfer not a guarantee. Read arXiv:2605.30561 primary before it's load-bearing.*

## Phased plan
- **Phase 0 — cheap checks (BEFORE any build; 1 short session):** (1) what VQ1 *actually* requires (pass criteria — may need simpler/sooner → full pipeline becomes VQ2/finals); (2) does the DCL/VQ1 sim hand us the RGB image feed (skips building a renderer — huge); (3) real GPU/compute budget on the RTX 5080. **Also: clarify VLM3.**
- **Phase 1 — representation strategy (the cost decision):** pick how to get the visual representation: (a) DreamerV3 world-model from scratch (Dream-to-Fly, expensive); (b) pretrain representation offline + policy-search on state (Messikommer, cheap); (c) **VLM-encoder-as-representation** (cheapest if it transfers). (b)/(c) are the tractable bets.
- **Phase 2 — policy + OUR curriculum:** policy-search on the representation over infinite procedural tracks + difficulty curricula → the generalizing pilot. *Our distinctive contribution.*
- **Phase 3 — adaptation / sim-to-real:** Learning-on-the-Fly differentiable-sim adaptation (later).
- **Phase 4 — deploy on VQ1/VQ2 sim.**

## Immediate next (get-started)
Phase 0's three checks + the VLM3 clarification. None require a big build; all reshape the *staging* and could 28×-or-more cut the cost. Then Phase-1 representation-strategy decision.

---

# PHASE-0 FINDINGS (Day 123 ~21:30 PST — VQ1 spec + readiness read) → TWO-TRACK REFRAME

**Read `docs/VQ1_TECHNICAL_SPEC_VADR-TS-002_Issue00.02.pdf` + `VQ1_READINESS.md`. The big build is the VQ2 horizon, NOT the VQ1 fire.**

1. **VQ1 = COMPLETION ONLY.** *"Round One verifies that contestant software can successfully navigate the racecourse."* 8-min max run, **<10 clearly-highlighted gates**, start→gates→finish. **Not speed, not ranking.** → the racing-grade gaze war is a VQ2/finals problem; VQ1 just needs to *stumble through.*
2. **Sim PROVIDES the RGB feed** (UDP 5600, 30 Hz, 640×360 JPEG, chunked header). **No renderer to build** — kills one of the DreamerV3 pipeline's biggest costs.
3. **Intrinsics fixed + KNOWN: fx=fy=320, cx=320, cy=180, 90° HFoV, 20° up-tilt — SAME fx≈320 as our sim.** → **NO camera-intrinsics gap for VQ1.** VLM³ focal-normalization is a VQ2/real-world/cross-camera lever, **not** a VQ1 need. (Premise corrected: the intake's "our fx vs VQ1's" — VQ1 *is* fx=320.)
4. **IMU telemetry IS provided** (MAVSDK). So bounded dead-reckon to bridge brief detection gaps is *legitimate sensor-fusion* (you saw the gate, propagate via your own motion until re-seen) — NOT the blind-odometry crutch. "Sight only" = no *privileged gate-state*, not "no IMU."

## → DECISION (Clayton, Day 123 ~21:45): SINGLE-TRACK — build the main pipeline directly. 27 days to VQ1.
**No Track A.** There is no existing completion pipeline to "resurrect" (it was never built), and Clayton prefers not to build a throwaway. **One real vision pilot serves VQ1 AND VQ2.** With **27 days** to VQ1 (real runway, esp. with the Messikommer efficiency lever), build the main pipeline now and field it for VQ1.

**THE BUILD (single track):** Dream-to-Fly **DreamerV3-from-pixels** backbone (emergent gaze) + **Messikommer** representation/policy-search separation (the 28× cost lever) + **OUR procedural-curriculum** (course generalization — our edge) + **VLM³** focal-normalization (camera generalization; VQ2/real-world, not needed for VQ1's matching fx=320) + **Learning-on-the-Fly** differentiable-sim adaptation (later). The racing-grade *generalizing* pilot — fielded for VQ1, matured for VQ2/finals.

**Phase-0 facts that de-risk the build:** the VQ1 sim *provides the RGB feed* (UDP 5600, no renderer to build) with *known intrinsics fx=320* (matches our sim). VQ1 is completion-only (8 min, <10 highlighted gates) — a forgiving deploy target for a first real vision pilot. IMU telemetry provided → bounded dead-reckon to bridge brief gaps is legitimate sensor-fusion.

**Next (get-started):** scope Phase 1 — the representation strategy (DreamerV3-world-model-from-scratch vs Messikommer-pretrain-representation vs VLM-encoder), which decides the cost. Then the pipeline build (renderer NOT needed — use the sim's feed; or a training renderer if we train off-sim). The day's gaze work + navigator + tooling are inputs to this build, not wasted.
