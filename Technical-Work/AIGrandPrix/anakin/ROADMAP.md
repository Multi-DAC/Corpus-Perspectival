# Anakin — Build Roadmap (from scratch)
### A DreamerV3 vision pilot for the AI Grand Prix VQ1, trained on our own synthetic curriculum sim

*2026-06-04 (Day 124). Clean-slate rebuild per Clayton's call: drop UE5, build a lightweight synthetic training sim we control, base Anakin on the official example + the Dream-to-Fly paper + our prior findings. Previous work (`../sim`, `../vision`, `../ue5_sim`) is reference-only.*

---

## 0. The target, stated tightly

**VQ1:** complete a course of <10 high-contrast, **desaturated** gates, FPV camera only, no GPS/coordinates, 8-min run. *Completion, not racing speed.* (VQ2 is the hard photorealistic 3D-scanned round — VLM³/photorealism live there, not here.)

**The approach (Dream-to-Fly, Romero/Scaramuzza/RPG-UZH):** train **DreamerV3** (model-based RL) end-to-end **from 64×64 RGB pixels → CTBR commands**. Model-free PPO/SAC provably fails at this (our 6-arm gaze falsification, published). Dreamer gets **emergent gaze toward gates for free** — the exact thing we failed to bolt on. Our differentiator vs. the paper: **a procedural-track + difficulty curriculum** for generalization (they train fixed tracks only).

**The architecture decision (the load-bearing one):** Dreamer needs a renderer **in the loop at thousands of FPS** for 10M-step training; the official `FlightSim.exe` gives **30 Hz over UDP** (~100× too slow). So:
- **TRAIN** on **our own fast synthetic sim** (gates + desaturated background at 64×64; thousands of FPS).
- **QUALIFY** on `FlightSim.exe` via the official `PyAIPilotExample` interface (sim-to-sim transfer).
- **VQ1's deliberate simplicity (desaturated, high-contrast) is what makes the synthetic→FlightSim gap small.** This is the whole reason the plan is tractable in our window.

**Established facts (2026-06-04 orient):** RTX 5080 / 16 GB / driver 596.49. Default env = Python 3.14.3 + `torch 2.11.0+cpu` (CPU only — deploy env, can't train). Official interface: vision = chunked JPEG UDP **5600**; MAVLink **14550**; action = CTBR `[c, ωx, ωy, ωz]` tanh-bounded. `dreamerv3-torch` not installed.

**Clock:** VQ1 ~26 days. The long pole is the training run (paper: 240 h on an RTX 8000). Mitigations baked into the plan: smaller config, completion-not-speed bar, Messikommer representation/policy decoupling (~28×), fast renderer, and *start the long run the moment Phase 2 proves the loop.*

---

## Phase 0 — Environment & interface lock  *(target: ~½ day)*

- **0.1 Training env (CUDA).** Create a clean **Python 3.12** env with **CUDA torch** for Blackwell/sm_120 (CUDA 12.8+); verify `torch.cuda.is_available()` and a matmul on the 5080. *(3.14 has no CUDA wheel; 3.12 is the safe target. If a cu128 wheel for 3.14 exists, even better — try first, fall back to 3.12.)*
- **0.2 Install `dreamerv3-torch`** + deps (gymnasium, the RSSM stack) into the training env; import-and-instantiate a tiny agent on GPU.
- **0.3 Keep the deploy env (3.14)** as-is for FlightSim (pymavlink/opencv). Two envs, cleanly separated.
- **0.4 FlightSim handshake smoke test:** run a stub pilot against `FlightSim.exe` — arm, receive one JPEG frame on 5600, receive MAVLink state on 14550, send one CTBR command. Confirms the deploy path end-to-end before we ever need it.
- **Deliverable:** GPU-trainable env + Dreamer importable on the 5080 + a confirmed FlightSim I/O handshake.
- **Risk:** CUDA-torch wheel availability for the 5080's Blackwell arch on Windows. *Verify first thing — it gates everything.*

## Phase 1 — The synthetic training sim *(target: ~2–3 days; the heart of the build)*

Three composable pieces, all numpy/torch, vectorizable, headless, thousands of steps/sec:

- **1.1 Quadrotor dynamics.** Port the paper's platform (m=0.6 kg, J=diag(0.00241, 0.0018, 0.003759), κ=0.022, arm 0.14 m, max thrust 4 N, T/W 2.7). CTBR input → rigid-body integration. Batchable on GPU (vectorize many envs). *Reference: `../ue5_sim/DRONE_DYNAMICS.md`, Agilicious params.*
- **1.2 Fast FPV renderer.** Project gate geometry into a **64×64 RGB** FPV view: high-contrast gate rings/squares on a **desaturated** background (VQ1-faithful). Camera intrinsics matching FlightSim (fx=fy≈320 @640×360 → scaled; 20° down-tilt). Implementation: lightweight rasterizer (moderngl/OpenGL headless, or a pinhole-projection + polygon-fill in torch). Must hit **thousands of FPS** batched. *Reference: `../vision/synthetic_camera.py`, `../vision/domain_randomization/`.*
- **1.3 Gymnasium env.** obs = 64×64×3 RGB; action = CTBR tanh `[-1,1]⁴`; **reward = Dream-to-Fly's:** progress `b1·(‖g−p_{k-1}‖−‖g−p_k‖)` − `b2·‖ω‖` + collision(−4) + gate-pass(+10), with **b2 curriculum** (start 0, raise after reward>50). Episode = gate sequence + timeout + collision. Domain-randomization hooks (lighting/gate-appearance jitter) for the sim-to-sim gap.
- **Deliverable:** a Gymnasium env where a random policy flies (badly) through a procedurally-generated desaturated gate course at 64×64, rendering at thousands of FPS, dynamics GPU-batched. Render a few frames to eyeball VQ1-faithfulness.

## Phase 2 — DreamerV3 integration + smoke run  *(target: ~1–2 days; the make-or-break)*

- **2.1 Wire `dreamerv3-torch`** to the env. Config sized to 16 GB (medium: scale down the 768-unit/2048-recurrent "Large" if VRAM-bound); 64×64 CNN encoder; imagination horizon T=16; paper hyperparams.
- **2.2 Smoke run on ONE simple track** (1–2 gates, close, slow). **PREDICT (commit before running):** Dreamer learns to pass the gate within a few×10⁵ steps, reward climbs, world-model reconstructions sharpen, and emergent gaze appears. If it *doesn't* learn on a trivial track, debug the env/dynamics/reward **before** scaling — this is the cheap failure point.
- **Deliverable:** a checkpoint that flies a simple fixed track from pixels. The minimal proof the family works in *our* sim. **Everything after this is scale, not uncertainty.**

## Phase 3 — Curriculum + the scaling run  *(target: ~10–14 days; the long pole — start ASAP)*

- **3.1 Procedural track generator** (our edge): randomize gate count/positions/sequence/difficulty.
- **3.2 Difficulty curriculum:** easy→hard (few/close/slow → many/sharp/fast) + the b2 body-rate curriculum.
- **3.3 The scaling run.** Budget the 240 h-class run against the window: smaller config + completion-not-speed bar + **Messikommer** (pre-train representation, then fast policy search ~28×) + many batched envs. Launch detached, checkpoint often, eval on held-out procedural tracks.
- **Deliverable:** a policy that completes **unseen** procedural courses (generalization), not just the training track.

## Phase 4 — Transfer + qualify on FlightSim  *(target: ~3–5 days, overlapping Phase 3)*

- **4.1 Deploy** the trained policy through `PyAIPilotExample`: vision_rx JPEG → 64×64 preprocess → policy → CTBR → MAVLink. Domain randomization (Phase 1.3) closes the synthetic→FlightSim gap; VQ1's desaturation keeps it small.
- **4.2 Eval on FlightSim's VQ1 course**, measure completion, iterate (DR strength, short fine-tune on FlightSim frames if needed — careful not to overfit the slow sim).
- **4.3 Submit / qualify.**
- **Deliverable:** Anakin completes the VQ1 course in FlightSim.

---

## Critical path & risk ledger

**Path:** 0 (env) → 1 (sim) → **2 (smoke = make-or-break)** → 3 (scale, long pole) → 4 (qualify). Phases 0–2 ≈ next few days; Phase 3 is the multi-day run to start the instant Phase 2 is green.

| Risk | Severity | Mitigation |
|---|---|---|
| CUDA-torch for 5080/Blackwell on Windows | **HIGH (gates everything)** | Verify Phase 0.1 *first*; Python 3.12 + cu128; fall back to WSL-CUDA if Windows wheels fail |
| Training time vs 26-day window | HIGH | smaller config · completion-not-speed · Messikommer 28× · fast renderer · start run early |
| 16 GB VRAM < paper's 48 GB | MED | medium config; 64×64 is small; reduce batch/recurrent units if OOM |
| synthetic→FlightSim gap | MED | VQ1 desaturated/simple (small gap) + domain randomization + matched intrinsics/dynamics |
| Dreamer fails in our sim (Phase 2) | MED | trivial-track smoke run catches it cheaply before any scale spend |

## Reuse-vs-rebuild (from-scratch, references allowed)
- **Rebuild clean:** dynamics, renderer, gym env, the Dreamer integration, the curriculum.
- **Reference:** `../vision/synthetic_camera.py` + `../vision/domain_randomization/` (renderer), `../ue5_sim/DRONE_DYNAMICS.md` (dynamics), `../vision/udp_vision_receiver.py` (already built to the 5600 chunked-JPEG spec — reuse for deploy), the CTBR calibration + L17#6 sign-convention finding (avoid the command-sign bug).
- **Drop:** UE5 bridge, the PPO/gaze/dial trainers.

## Immediate next action
**Phase 0.1 — stand up the CUDA training env and prove `torch.cuda.is_available()` on the 5080.** Nothing downstream is real until that's green. Then 0.2 (dreamerv3-torch), then start Phase 1.1 (dynamics).
