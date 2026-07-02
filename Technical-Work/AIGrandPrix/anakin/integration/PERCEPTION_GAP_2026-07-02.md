# The Perception Gap — Anakin has been training in an empty room (Day 152, 2026-07-02)

**The month-long wall, finally diagnosed.** With Clayton, live on the new VQ1 sim (AIGP_3379).

## What we found
After getting `best.pt` (the +160 IMU checkpoint) to actually deploy — auto-detecting the IMU
encoder, deriving the HIGHRES_IMU→training-frame (FRD→FLU) mapping from the validated
`zup_to_ned_rates`, and clamping the real accelerometer (which spikes to thousands of m/s²,
240× the training Box) — Anakin *still* spun out and couldn't hold the course. Clayton's
instinct: it's not control, it's that **what he trains on isn't comprehensive enough.** He was right.

## The decisive test — world-model reconstruction ("what does Anakin see?")
`integration/wm_recon_diag.py` feeds REAL sim frames through best.pt's DreamerV3 world model and
decodes what it represents (mirrors `WorldModel.video_pred`). `integration/wm_recon_control.py`
does the same for RENDERED training frames as a control.
- **Real frames → structureless mush.** A faint red smudge where the gate is, a blue smear at the
  ribbon, otherwise fog. No gate, no ribbon, no structure. (`wm_recon_gate.png`)
- **Rendered training frames → SHARP.** The red gate reconstructs cleanly, right where it is.
  (`wm_recon_control.png`)
- Airtight: the decoder works; **the real imagery is severely out-of-distribution for the encoder.**
  He is effectively *blind* to the real sim. He spins because he can't see the gate.

## The root cause (worse than a style gap — a CONTENT gap)
The control revealed *what* the training frames are: **a red gate on a near-black void.** That's it.
The real sim gives a rich scene — cyan ribbon, branded orange gates, dense grey structures, a glowing
grid, a green horizon. **He trained on an almost-empty cartoon and we deploy him in a detailed world.**
His encoder has literally never seen a ribbon or a building. That is the month-long wall.

## The methodological miss (name it, fix it)
The offline rehearsal gate "passed" all month because it tested him on the *renderer* frames — the ones
he can see. We were grading him on flying our drawing, then surprised he can't fly reality.
**New rule: the world-model reconstruction check on REAL frames is the readiness gate. No live flight
is meaningful until the RECON column stops being mush.**

## The fix (in progress) — teach his eyes the real world
- **Data:** the new sim disabled position/gate/odometry telemetry (forces vision; also means no reward
  and no scriptable autopilot on the real sim). So real frames come from **manual flight**. Built
  `runmanualoverride_xbox.py` (native XInput, analog Mode: left stick roll/pitch, right stick yaw,
  right trigger throttle) — captures every frame to `official_frames/manual_<ts>/`. Clayton collected
  ~14k real frames in the first ~30 min.
- **Adaptation:** fine-tune the DreamerV3 **world model** on the real frames — self-supervised
  (reconstruct + predict, **no reward needed**, which is exactly what the telemetry-stripped sim forces).
  Teaches the encoder to represent real imagery; the learned dynamics/policy ride on top. Re-run the
  reconstruction test after; success = the RECON column shows the gate.

## Artifacts (this session)
`integration/`: `dreamer_pilot.py` (IMU auto-detect + FRD→FLU + accel clamp), `translation_rehearsal.py`
(IMU-wired offline gate, PASS +242 roundtrip), `wm_recon_diag.py` + `wm_recon_control.py` (the
reconstruction diagnostics, now our readiness gate), `wm_recon_gate.png` / `wm_recon_control.png`.
On the kit (not repo): `run_dreamer.py` (IMU capture+feed), `runmanualoverride_xbox.py` (data collection).

## Next
1. Keep collecting varied real frames (close/angled/through-gate). 2. Build the world-model perception
fine-tune on them. 3. Reconstruction test → confirm he sees. 4. THEN re-fly. Getting through a gate
is downstream of him being able to see one.
