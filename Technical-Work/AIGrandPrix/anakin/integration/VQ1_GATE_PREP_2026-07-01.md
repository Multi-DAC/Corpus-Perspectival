# VQ1 Gate Prep — best.pt (+160.08) readiness, and a blind spot to check FIRST

*Clawd, Day 151 (2026-07-01) morning drive. Read-only prep — I did NOT run the gate (it's a with-Clayton eval per anticipation P258). The point of this note is one risk the +160 number and the standard gate BOTH hide.*

> **★ RESOLVED 2026-07-01 (Clayton):** IMU **is** provided in **both** virtual qualifiers (confirmed from the AIGP docs). The blind spot below is therefore not a live problem — **best.pt (+160.08, IMU-encoder) is the correct checkpoint; run the gate normally, expect a camera-translation PASS.** The analysis is retained below for the record and because the general lesson stands (a gate that supplies an input in all its conditions is blind to that input's absence at deploy).

## Run status
- `logdir/maneuver_imu_stability` COMPLETE: 9.5M steps, trainer exited clean, **best_return +160.08** (peak batch 17; 18–19 didn't beat it, best-protection held). Configs: `anakin_maneuver anakin_band anakin_informed anakin_imu`.
- `best.pt` is the strongest VQ1 candidate *by in-sim return*.

## ★ THE BLIND SPOT (check this BEFORE trusting a gate pass)
**This checkpoint's encoder consumes IMU.** `configs.yaml` `anakin_imu`: `encoder: {mlp_keys: 'imu', cnn_keys: 'image'}`. So the deployed policy builds its latent state from **image + IMU**. At deploy, no IMU → the encoder is missing an input it learned to depend on → OOD.

**The rehearsal gate cannot see this.** `translation_rehearsal.py` is **sim-to-sim** and stresses only the *camera* path (crop the 36-row ~59° VFOV band → upscale ×10 to 640×360 → RGB→BGR); `roundtrip − direct` isolates *camera* translation cost. It supplies IMU in **both** conditions. So a PASS certifies the camera path only — it says nothing about whether IMU will be there on the official sim.

**The hint that this matters:** the `anakin_imu` config comment ties it to *"the visual-inertial state estimation **VQ2** mandates."* That suggests IMU is a **VQ2** feature. If **VQ1 is camera-only**, then best.pt (+160, IMU-encoder) is OOD on VQ1 in a way both the +160 and a green rehearsal completely hide. This is the Day-140 pattern ("the number lied, the gate told the truth") — one level deeper: here even the gate is blind to it.

## The ONE question that decides the checkpoint
**Does the official VQ1 sim expose an IMU (gyro+accel) observation to the policy?**
- **YES** → best.pt is the right checkpoint; run the gate normally (below). Expect a camera-translation PASS.
- **NO (VQ1 camera-only)** → best.pt's IMU-encoder is a *liability* for VQ1. Prefer a **camera-only checkpoint**: the `anakin_informed` lineage *without* `anakin_imu` (priv_state stays decoder-only / encoder-blind, image-only encoder = deployable on camera alone). Or accept a degraded IMU-zeroed fallback and *measure* the hit. Either way, don't ship the IMU-encoder to a camera-only VQ1 on the strength of +160.

## Runbook (when IMU-availability is confirmed)
```
cd .../anakin
.venv/Scripts/python.exe integration/translation_rehearsal.py --episodes 10
# point DreamerPilot at logdir/maneuver_imu_stability/best.pt (verify the checkpoint path it loads)
# PASS ≈ roundtrip return ≈ direct return (camera translation cheap). Day-145 widegap already showed appearance tax ~solved.
```
- **PREDICT (med-high):** the *camera* translation PASSES (roundtrip ≈ direct) — appearance/VFOV was solved Day-145 and IMU-stability only helped in-sim. The risk is **not** the camera; it's IMU-availability, which this gate won't test.
- **Also still un-testable sim-to-sim** (from the docstring): camera tilt sign vs official, body-frame handedness, thrust calibration. Those need the real official sim.

## Bottom line for Clayton
Two moves, in order: **(1)** confirm the official VQ1 obs includes IMU; **(2)** then run the gate. If VQ1 is camera-only, switch to the camera-only checkpoint before gating. The +160 is real but it's an *in-sim, IMU-present* number — its VQ1 meaning is contingent on that one fact.
