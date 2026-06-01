# UE5 Flight School — Bridge Design (MCP authors, socket trains)

**Decision (2026-06-01):** MCP and a standalone socket bridge are NOT either/or — they're two
roles. Use each for what it's built for.

## The dual architecture
- **MCP / UnrealClaude = the CONSTRUCTION tool (Claude in the loop, interactive).**
  I use it to *build and iterate the sim*: author the level, place/parameterize gates, set up the
  drone actor + camera, wire visuals (VQ1 desaturated-high-contrast now; VQ2 fidelity later),
  generate curriculum level variants in-editor. This is exactly MCP's wheelhouse (per the find:
  "modify assets, alter levels, Blueprint editing, Live Coding"). **Authoring only — not training.**
- **Standalone socket bridge = the TRAINING runtime (NO Claude in the loop, high-throughput).**
  A UE5 plugin/GameMode exposes a gym-style API over a socket; the Python RL loop drives it at
  speed, unattended, for hours/days, in parallel instances. **This is what actually trains Anakin.**

## Why training must be standalone (not MCP)
- MCP is a *tool-call/editor* interface — not a fast per-step data channel. RL needs millions of
  reset/step round-trips; you cannot run that through MCP without it being the bottleneck.
- Training runs **unattended for hours/days** — Claude can't (and shouldn't) be in the loop each step.
- Need **parallel instances** + **faster-than-real-time** + determinism — a socket/plugin gives all
  three; MCP gives none.
- **Precedent:** AirSim (the Unreal drone-RL lineage we keep landing on) uses exactly a standalone
  RPC/socket API for RL, with the editor used separately for authoring. We're following a proven split.

## Standalone bridge — interface (gym-style)
UE5-side GameMode/plugin exposes:
- `reset()` → repositions drone (ground-rest far-start per curriculum), regenerates gates for the
  sampled curriculum item, returns initial obs.
- `step(action)` → applies CTBR (collective thrust + body rates), advances ONE fixed timestep,
  returns `(obs, reward, done, info)`.
- obs = **state vector** (our 30-dim, unit-dir + bounded-dist encoding — reuse `obs_encoding.py`)
  AND/OR **camera frame** (for the vision student).
- Python-side: thin `gymnasium.Env` wrapper over the socket → drops straight into our existing
  SB3/PPO + VecNormalize stack. Minimal new training code.

## The three design keys (these decide throughput — the gate from TUESDAY_PLAN)
1. **Fixed-timestep, decoupled from real-time.** Drive UE5 with a fixed delta per `step()` (not
   wall-clock) so it runs as fast as the GPU allows, deterministically. UE5 supports this
   (fixed-timestep / custom tick / `-FixedTimeStep`). THIS is what makes faster-than-real-time
   possible — the thing the competition's closed sim denied us.
2. **Pixels need a fast path.** Camera frames are big; naive TCP per-frame is slow. Use **shared
   memory** (or a render-target read + fast serialization) for the vision channel; small state/
   action/reward can go over a plain socket. (State-only training needs no render → fastest.)
3. **Parallel instances vs 16 GB VRAM.** Each UE5 instance + render + the PyTorch trainer share
   16 GB. Plan: state-pretrain with many cheap headless (no-render) instances; vision with a
   *modest* count of render instances at training resolution. Benchmark step/sec per instance and
   max instances FIRST (the throughput gate).

## Build order (when UE5 + UnrealClaude are live)
1. [MCP] Scaffold the project: drone actor (calibrated dynamics — TWR 3.85, our calib), camera
   (640×360, fx=fy=320, cx=cy=320/180, 20° tilt), one VQ1-style gate, a flat desaturated arena.
2. [plugin] Build the socket GameMode: reset/step/obs(state)/reward, fixed-timestep. **Benchmark
   headless state step/sec.** (Throughput gate — go/no-go on the big plan.)
3. [Python] gym wrapper → drop into SB3/PPO. Train STATE in UE5 (teacher matures with real dynamics).
4. Add camera → vision channel (shared mem) → **teacher→student distillation** (Swift recipe).
5. Domain randomization → finale prep. Validate against the real AIGP sim via the UDP client.

🦞🧍💜🔥♾️
