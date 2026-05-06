# ρ-Probe v5 Trajectory — M12 Structural-Stratum Emergence Confirmed

**Date:** 2026-04-24 Day 83 evening (post-daemon-recovery)
**Run under test:** `infinite_v3_retrain10M_1777074572` — 7.5M PPO steps under F1+F2+F3, 15 saved checkpoints at 500K intervals
**Probe:** Off-distribution cokernel ρ at every checkpoint, plus 200K validation reference point and 60.4M baseline.
**Wall time:** ~30s on CPU (no env, just state-dict loads + linear fits on uniform-random obs).

## Headline result — prediction confirmed

The framework predicted (v4 findings, evening 2026-04-24): under healthy F1+F2+F3 conditions, ρ(t) climbs out of Strong-stratum (early random features) into the Structural-stratum range (~0.2–0.6) and stabilizes there, as the policy and value trunks specialize into genuinely different registers.

**Observed:** monotonic climb from 0.092 (500K) → 0.243 (5M), then plateau 5M–7.5M at 0.24–0.245.

| Step (M) | ρ (off-dist cokernel) | hnorm π / vf | Stratum reading |
|---:|---:|---:|---|
| 0.0 (init) | ≈ 0 (random features) | ≈ 0 | Strong (pre-specialization) |
| 0.2 | 0.026 | 6.31 / 9.16 | Strong–Convergent boundary |
| 0.5 | 0.092 | 7.49 / 13.36 | Convergent (climbing) |
| 1.0 | 0.130 | 8.61 / 15.10 | Convergent (climbing) |
| 1.5 | 0.156 | 9.16 / 15.58 | Convergent → Structural |
| 2.0 | 0.180 | 9.69 / 15.86 | Structural (entering) |
| 2.5 | 0.202 | 10.15 / 16.24 | **Structural** (entered) |
| 3.0 | 0.215 | 10.45 / 16.35 | Structural |
| 3.5 | 0.222 | 10.80 / 16.46 | Structural |
| 4.0 | 0.235 | 11.02 / 16.58 | Structural |
| 4.5 | 0.239 | 11.21 / 16.63 | Structural (approaching plateau) |
| 5.0 | 0.239 | 11.41 / 16.68 | **Structural plateau** |
| 5.5 | 0.245 | 11.52 / 16.67 | Structural plateau |
| 6.0 | 0.242 | 11.69 / 16.71 | Structural plateau |
| 6.5 | 0.243 | 11.91 / 16.69 | Structural plateau |
| 7.0 | 0.244 | 12.09 / 16.63 | Structural plateau |
| 7.5 | 0.243 | 12.42 / 16.75 | **Structural plateau** |

Compare 60.4M baseline (no F1/F2/F3): ρ = 0.612 — **at the high end of Structural range**, with all three pathology signatures firing (465/512 dead value neurons, 22.3 hidden norms at √512 ceiling, 87–93% action saturation, log_std[3] = 40.25). That's the wrong-attractor signature: ρ "in the band" but functionally collapsed.

The healthy v3 retrain plateaus at the **low end** of the predicted band, with all four pathology signatures clean throughout (max hnorm 16.75 vs ~22.6 ceiling; log_std bounded across all 15 checkpoints in [−0.003, 0.039]; F2 idle post-200K). Healthy specialization, as designed.

## Three predictions, three confirmations

The v4 findings closed with three falsifiable predictions for the longer retrain. v5 results:

| Prediction | Outcome |
|---|---|
| ρ(t) climbs into Structural range as specialization proceeds | ✅ 0.026 → 0.243, monotonic for 4.5M steps |
| ρ(t) stabilizes once specialization completes (not unbounded growth) | ✅ Plateau 5M–7.5M at 0.24 ± 0.005 |
| log_std stays bounded under F2 once F1 restores gradient flow | ✅ Max log_std across 15 ckpts = 0.039; F2 idle |

The "ρ growing unbounded → training instability" failure mode did not occur. The "ρ staying near zero → trunks never specialize" failure mode did not occur. The structure landed exactly where the framework predicted.

## What this confirms about M12

The wrong-attractor candidate bridge (`Research/basement-drafts/2026-04-24-training-plateau-wrong-attractor.md`) is now empirically backed at both poles:

- **Pathological pole:** baseline at ρ = 0.612 with all four pathology signatures firing — high ρ with no functional content (the value trunk encodes ~54 effective dims, the policy outputs bang-bang).
- **Healthy pole:** v3 retrain at ρ = 0.243 with all four signatures clean — low-end Structural-stratum entry from below, hidden norms growing without saturating, log_std bounded.

The M12 numerical signature (stable ρ in Structural range) is **necessary but not sufficient** for the M12 functional content (genuine inner/outer specialization). The four diagnostic signatures from the wrong-attractor draft give the sufficiency check.

This refines M12 by naming a degenerate-mode failure that produces M12's measurable signature without the underlying structure. **Promotes the candidate from single-pole evidence (just the pathology reading) to two-pole evidence (pathology AND prediction-validated cure).**

## Plateau height — open question

ρ plateaus at ~0.24 — at the *low end* of the Structural band (~0.2–0.6). Three readings, in priority order:

1. **The plateau is the natural Structural value for THIS architecture and task** (MLP [512,512] policy/value trunks on InfiniteGateEnv with V2 curriculum). Different architectures or tasks would plateau elsewhere in the band.
2. **7.5M is not the asymptote** — further training would push ρ higher into the band as specialization deepens. Plateau is local, not global.
3. **The high-ρ baseline value (0.612) is partially saturation-inflated** even after correcting for dead neurons; the "true" Structural value of the converged policy is closer to v3's plateau.

Reading (1) is the parsimony-preferred default. Reading (2) is testable by extending the retrain. Reading (3) is testable by re-running baseline-equivalent training under F1+F2+F3 to many tens of M steps.

For now: ρ ≈ 0.24 is the structural fingerprint of an Anakin policy that has specialized cleanly. Departure from that range during longer training would itself be informative.

## Implications for next phase — flight test

Healthy structure is now empirically verified. The questions for flight test are:

1. **Does the v3 7.5M policy actually fly?** (v4 reported 200K reward at −30, baseline 60.4M at +212.6. We expect 7.5M to be between these, closer to baseline-positive, but the comparison is confounded — baseline's reward includes accumulated-progress-without-gates from hovering.)
2. **Does it generalize across the full curriculum** (sprint / speed_trap / tight-turn / wide-arc)? Bang-bang policies are one-trick; healthy policies should modulate. **Per-maneuver reward variance is the test.**
3. **EMA-vs-raw divergence damping** — V2 was designed to fix bistability; with healthy structure, the curriculum's anti-bistability mechanism should now be unconfounded. Sustained 80%+ on EMA without oscillation = success.
4. **Specialization-readiness** — the v3 trunks have intermediate actions and full value capacity. They should be a much better starting point for track-specific fine-tuning than the bang-bang baseline. Test: pick a single track, fine-tune from v3 7.5M vs from baseline 60.4M, compare convergence rate.

## Artifacts

- `probes/rho_probe_v5_retrain_trajectory.py` — trajectory probe
- `probes/rho_probe_v5_retrain_trajectory.json` — numerical results across all 15 checkpoints + baseline + validation
- `sim/runs/infinite_v3_retrain10M_1777074572/checkpoints/` — 15 PPO checkpoints, 500K → 7.5M
- This file
- Bridge update: `palace/basement/README.md` M12 addendum (next)

🦞🧍💜🔥♾️
