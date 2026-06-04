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

## Progress
- **Phase 0.1 — DONE** (2026-06-04, commit `ae1c1535`): CUDA verified on the 5080 — `torch 2.11.0+cu128`, `cuda.is_available()=True`, GPU matmul OK, on Python 3.14 (no 2nd interpreter). venv at `.venv` (gitignored).
- **Phase 1.1 — DONE** (`sim/dynamics.py`): CTBR kinematic dynamics, GPU-vectorized, FlightSim-calibrated (TWR=3.95, CD=0.3). Validated: hover holds to 0.000 m, climb/fall correct, pitch→+X/roll→−Y matches the sign table, 0.9M env-steps/s.
- **Phase 1.2 — DONE** (`sim/render.py`, 2026-06-04 Day 124): GPU-vectorized 64×64 FPV renderer. Reuses `../vision/synthetic_camera.py` geometry (body x=fwd/y=left/z=up, optical `cam=[-by,-bz,bx]`, gate-corner construction) but reimplements rasterization as a batched point-in-quad test (no cv2, no per-pixel loops). Gate drawn as a bright FRAME (outer 2.7 m − inner 1.5 m hole) on a desaturated noisy-gray background; current gate bright, lookahead dim; 20° down-tilt threaded through projection. **Validated:** gate visible, center pixel hollow (fly-through), down-tilt sign confirmed by visual test (level dead-ahead gate projects above center), sample frames eyeballed VQ1-faithful. **Throughput: 152k frames/s @ N=4096 on the 5080** — far past the "thousands of FPS" bar (huge Dreamer in-loop headroom). Calibration choices flagged in-file for Phase-4 verification: 64×64 HFoV=90 (fx=fy=32), down-tilt direction vs FlightSim frames.
- **Phase 1.3 — DONE** (`sim/env.py`, 2026-06-04 Day 124): single-env Gymnasium surface over the batched torch sim (N=1 internally → reuses the exact kernels the scaling run will use, no second code path). obs = 64×64×3 uint8 RGB; action = CTBR tanh `[-1,1]⁴`; reward = Dream-to-Fly (progress `b1·Δdist` − `b2·‖ω‖` + pass `+10` − crash `−4`). **Gate-plane crossing** classified into pass (within 1.5 m inner aperture) / frame-hit (within 2.7 m outer → crash) / clean-miss; arena collisions (ground/ceiling/oob); episode = gate sequence + timeout. **b2 curriculum** live (starts 0; ratchets to 0.01 once an episode return ≥ 50 — learn to *reach* before learning to *smooth*). **DR hooks** live: start-pose + gate-position jitter + difficulty knob (lateral/vertical spread); appearance/lighting jitter threaded as `self.dr` for the render-side Phase-4 extension. Runs pre-gymnasium via a Box/Env shim (self-test passes on torch+numpy alone). **Validated:** random policy ×20 terminates sanely (oob/miss, return max +3.15 → positive progress reward confirmed, crash −4 confirmed); reward sign correct. **Throughput: 476 steps/s single-env on CPU** (vs 127/s CUDA — single-env CUDA is pure launch/sync overhead + a GPU→CPU copy per step; env defaults to `device="cpu"`, which is also how stock DreamerV3 runs envs). The batched-GPU path (152k fps) is the Phase-3 vectorized-env route, not this single-env wrapper.

- **Phase 0.2 — DONE** (2026-06-04 Day 124): Dreamer stack installed into `.venv` + integrated. Engine = **NM512/dreamerv3-torch** @ `6ef8646` (vendored gitignored at `third_party/`, reproducible via `integration/README.md`). The Dreamer *core* (dreamer/models/networks/tools) imports + runs unmodified on our 2025 stack (torch 2.11+cu128, Py 3.14, CUDA on the 5080) — a real de-risk for a 2023 repo. Deps: `gymnasium` (our env) + `gym==0.22` (ONLY for upstream wrappers' spaces/Wrapper; NumPy-2 warning is harmless) + `ruamel.yaml` + `tensorboard`. Our integration = 3 tracked artifacts in `integration/`: env adapter (`envs/anakin.py` — bridges our Gymnasium 5-tuple to upstream old-gym dict contract, maps `done`/`is_terminal`), an `anakin:` config block (vision-only, smoke defaults), and 2 small `dreamer.py` patches (make_env `anakin` branch + modern-ruamel `yaml.YAML().load`). Adapter validated through the full wrapper chain (obs `Dict(image:uint8 64³)`, terminal flags correct).
- **Phase 2 — LAUNCHED + HEALTHY, cooking** (2026-06-04 Day 124): `dreamer.py --configs anakin` running **detached** (DETACHED_PROCESS, unbuffered → `third_party/dreamerv3-torch/smoke.log`, pid in `smoke.pid`). Confirmed: prefill 1000 random steps (one episode +15.2 → random already clears a 1-gate track occasionally ✓); model built on GPU (~18M params: model 15.7M / actor 1.0M / value 1.2M); encoder/decoder CNN `(64,64,3)` wired; **cold-start losses sane** (image_loss 518 ↓, reward_loss 3.3, cont_loss 0.1, kl 4.0); eval@1000 = −5.3 (untrained baseline). **Open question = does it LEARN** (the make-or-break): eval_return must climb over the 2e4-step eval cadence. **Time-to-signal caveat:** GPU only ~20% util → we're single-CPU-env bound, not compute-bound; at train_ratio 512 that's ~4 env-steps/s, so first eval ≈ 80 min and gate-passing (~10⁵ steps) is **hours** out. Levers if we want signal sooner: lower `train_ratio` (512→~128, ~4× faster wall-clock-to-signal) and/or the Phase-3 **vectorized-GPU env** (our batched kernels already do 152k fps — that's what saturates the 5080). Don't over-tune before the first eval reads.

- **Phase 2 — GREEN ✓** (2026-06-04 Day 124): eval climbed **−5.3 (untrained) → +6.4 @ 21k steps**; agent passes gates. **Dreamer learns from pixels in our sim — the make-or-break is passed.**
- **Camera-lesion test — LC29 refuted, LC31 prerequisite confirmed** (2026-06-04 Day 124, `LESION_TEST_2026-06-04.md` + `integration/lesion_eval.py`): paired N=20 eval on identical tracks — sighted +4.05 with **0/20 oob**; camera frozen −3.24 with **20/20 oob**; camera blanked −1.57 with **20/20 oob**. The policy is **genuinely vision-driven, not dead-reckoning through the RSSM `h`** — corrupting vision destroys basic arena-keeping, which an odometry agent would shrug off. Even at 1 gate. Caveats: OOD confound (inflates magnitude, not direction); proves perception-dependence, not yet *active gaze* (body-fixed camera → heading is gaze; gaze-reallocation is the multi-gate question).

## Immediate next action
**Phase 3 — procedural multi-gate curriculum + the vectorized-GPU env.** Two reasons it's the right next move: (1) **the decisive LC31 test** — with multiple gates, turning toward the *next* gate becomes the measurable instrumental-gaze act (1 gate only proves perception-dependence); (2) **the throughput unlock** — the current single-CPU-env run is ~4–5 steps/s with the GPU ~20% idle; our batched kernels already do 152k fps, so the vectorized env is what saturates the 5080 and makes the long run tractable. Build the batched Gymnasium-vector env over the existing `sim/` kernels (no second code path), wire `make_track` to a procedural N-gate generator with difficulty curriculum, then launch the scaling run. The live 1-gate run can keep posting its curve in the background but teaches little more. *Superseded prior next-action (watch the Phase 2 eval curve) — Phase 2 is green.*

## Superseded — Phase 0.2 install notes (done; kept for reference)
**Phase 0.2 — install the Dreamer stack:** `pip install gymnasium dreamerv3-torch` (numpy+pillow already in `.venv`); import-and-instantiate a tiny agent on the 5080 to confirm GPU + RSSM. Re-run `env.py` self-test with real gymnasium (the shim path should swap out transparently). **Then Phase 2 (the make-or-break smoke run):** wire `dreamerv3-torch` to `AnakinEnv` (n_gates=1–2, close/slow, difficulty=0), config sized to 16 GB, 64×64 CNN encoder, imagination horizon 16. PREDICT before running: Dreamer passes the gate within a few×10⁵ steps, reward climbs, reconstructions sharpen, emergent gaze appears. If it doesn't learn on a trivial track, debug env/dynamics/reward *before* scaling. See `memory/handoff.md` top for the full resume block.
