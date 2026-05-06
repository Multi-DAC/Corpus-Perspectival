# Domain Randomization — Parameter Specification

*Drafted 2026-04-25 evening anticipatory drive (P103). Pre-work for next AIGP own-session (~3-5 day sprint, queued post-Day-84).*

## Why

Stage 5 Step 2 (world-anchored detection smoothing) was falsified because the policy was trained on a single synthetic camera distribution and the smoothing changed the input distribution at deployment. Phantom-commitment overshoot resulted: stable distance + high speed signals from held-obs windows looked coherent under the policy's learned filter but were artifacts of the smoothing process, not the world.

The principled fix is not "match the May DCL distribution we don't have yet" but "harden perception against any distribution by training on a wide envelope." Domain randomization spreads training across many synthetic distributions, so the policy learns features robust to the axes randomized rather than overfitting to one synthetic look.

## Parameter Axes

Six axes, organized by which sim/real gap each closes.

### Perception-distribution (what the camera sees of the world)

**1. FOV (field of view)** — uniform over [80, 130] deg
- Justification: Step 1 confirmed sensitivity (90→120 gave 9× reward gain). May DCL FPV cameras likely 110-130 (consumer FPV norm). Range covers VQ1 expected envelope ±buffer.
- Sampling: uniform per episode start; held constant within episode.
- Implementation: `SyntheticCamera.__init__(fov_deg=...)`.

**2. Gate texture / appearance** — color jitter + albedo noise
- Hue jitter: ±20° HSV shift on `gate_color`.
- Saturation jitter: ±30% on saturation channel.
- Value jitter: ±30% on brightness channel.
- Albedo noise: per-pixel multiplicative noise σ=0.05 on rendered gate region.
- Justification: We don't know May DCL gate colors. Synthetic gates currently fixed at (220,240,255) BGR — overfit to this exact color is a known failure mode.
- Sampling: per-episode for hue/sat/val; per-frame for albedo.

### Sensor-distribution (what the sensor adds to the image)

**3. Sensor noise** — Gaussian RGB noise + JPEG compression artifact bands
- Gaussian: σ ∈ [0, 0.05] on normalized [0,1] RGB, sampled uniformly per episode.
- JPEG quality: random quality factor in [50, 95] applied with cv2.imencode/imdecode round-trip.
- Justification: FPV analog video has heavy noise + compression artifacts; current synthetic frames are noise-free.
- Sampling: noise σ per episode; JPEG quality per episode.

**4. Motion blur** — Gaussian kernel linked to angular velocity
- Kernel size σ ∈ [0, 3] px, scaled by current angular velocity magnitude.
- At 0 ang vel: σ=0 (sharp). At max ang vel: σ=3 (blurry).
- Justification: Real cameras blur under fast rotation; synthetic frames are infinitely sharp.
- Sampling: deterministic from drone state per frame.

### World-distribution (what the world looks like beyond the gates)

**5. Lighting** — directional + ambient
- Directional intensity multiplier: uniform [0.3, 1.5]× nominal applied to gate brightness.
- Ambient floor: uniform [0.0, 0.4] added to background color.
- Justification: VQ1 environments may be bright daylight or dim hangars; current bg fixed at (40,40,40).
- Sampling: per-episode start; held constant within episode.

**6. Occlusion** — random rectangular masks
- Mask area: 0-15% of image area.
- Mask count: 0-2 masks per frame, uniformly sampled.
- Mask color: matches background (`bg_color`) — simulates partial-FOV gate or obstruction.
- Justification: Real flight has occluders (other drones, frame parts). Pure-rendering pipeline never sees them.
- Sampling: per-frame.

## Curriculum Order

Train incrementally to isolate which axes hurt convergence:

1. **Phase A (1M steps):** FOV randomization only. Confirms baseline doesn't degrade.
2. **Phase B (3M steps):** + lighting + sensor noise. Confirms perception robustness on cheap axes.
3. **Phase C (5M steps):** + texture + motion blur. Confirms color/blur robustness — likely the hardest axes.
4. **Phase D (full):** + occlusion. Confirms partial-observability robustness.

Each phase: train from previous-phase checkpoint; re-evaluate per-maneuver gates at end. If gates regress >20%, stop and inspect: which axis broke the policy?

## Sampling Distributions

| Axis | Distribution | Range | Per |
|------|--------------|-------|-----|
| FOV | uniform | [80, 130] deg | episode |
| Hue jitter | uniform | ±20° | episode |
| Sat jitter | uniform | ±30% | episode |
| Val jitter | uniform | ±30% | episode |
| Gate albedo noise | Gaussian | σ=0.05 | frame |
| Sensor RGB noise | uniform σ | [0, 0.05] | episode |
| JPEG quality | uniform int | [50, 95] | episode |
| Motion blur σ | linear in ang vel | [0, 3] px | frame (deterministic) |
| Directional light | uniform | [0.3, 1.5]× | episode |
| Ambient floor | uniform | [0.0, 0.4] | episode |
| Occlusion area | uniform | [0, 15]% | frame |
| Occlusion count | uniform int | [0, 2] | frame |

## Implementation Hooks

Existing entry points in `vision/synthetic_camera.py`:

- `SyntheticCamera.__init__` — accepts `fov_deg`, `bg_color`, `gate_color`. Need: extend constructor to accept randomization config object.
- `SyntheticCamera.render` — accepts `add_noise` boolean. Need: replace boolean with structured noise config that consumes per-frame randomization values.

New file: `vision/domain_randomization/randomizer.py`
- `class Randomizer` — holds active config, samples per-episode + per-frame values, applies to camera state before render.
- Composable with existing camera code; no policy-side changes needed.

Training-side: `train_phase3_dr.py` — wraps env with Randomizer, logs sampled values per episode for ablation.

## Open Questions

1. Should FOV randomize per frame or per episode? Per-episode is cheaper and matches real-world (camera FOV doesn't change mid-flight). Going with per-episode.
2. Should we add chromatic aberration / vignetting / barrel distortion as a 7th axis? Lower priority — these are deterministic optical distortions that a single calibration can correct, less of a domain-shift threat than the six above.
3. Should we add depth noise (z-axis perturbation in PnP solve)? Probably yes once Phase C passes — the PnP itself may need its own randomization. Defer to Phase D.
4. What's the right re-eval cadence within Phase B/C? Suggest every 500K steps to catch regressions early without over-spending compute.

## Estimated Cost

- Implementation: ~4-6 hours (Randomizer class + camera hooks + train script + smoke tests).
- Phase A-D training: ~3-5 days wall clock at current ~2400 sps × 4 phases × (1M + 3M + 5M + Xm steps).
- Per-phase eval: ~30 min compute + ~30 min analysis.
- Total session estimate: 3-5 days of own focused work, matching the queued estimate.

## Success Criteria

Pass: Phase D model achieves ≥80% of Phase 2 22.5M baseline gates per episode (target: ≥14.4 gates/ep) on the *original* Stage 5 driver eval, *and* shows no >2× degradation when evaluated under any single randomization axis at maximum.

Fail (stop and re-design): >50% gate degradation on baseline eval, or any axis individually causes >5× degradation post-training.

Inconclusive (tune ranges): 2-5× degradation on individual axis — likely the range is too aggressive; tighten and continue.

---

*Pre-computed during anticipatory drive 2026-04-25 ~19:30 PST. Entry point for next AIGP own-session.*
