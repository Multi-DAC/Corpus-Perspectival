# Vision Pipeline Shakedown — Parallel Track to Phase 2

**Workbench opened:** 2026-04-24 evening, alongside Phase 2 GPU retrain launch.

**Why now:** VQ1 is FPV+telemetry only — even a perfect policy can't compete without working vision. The post-Phase 1 portfolio strategy parallelizes RL training (Phase 2) with vision-readiness work that has to happen regardless of which policy wins. Pulled forward from Phase 4 in the original ROADMAP.

## Goal

End-to-end loop:

```
synthetic_camera (3D gate state → image)
    → gate_detector (image → quadrilateral + PnP pose)
    → adapter (pose + telemetry → 30-dim policy obs)
    → policy (obs → action)
    → mavsdk_client (action → TRPY command)
```

Surface integration bugs **before** the sim drops, not on Day 1 of post-drop scrambling.

## Critical gap (per VQ1_READINESS.md)

Line 148 of `competition_agent.py`: `camera = np.zeros(...)`. The full pipeline has never been tested with real (or even synthetic) imagery. The vision components exist independently; the wiring has not been validated.

## Phase ordering for shakedown

1. **synthetic_camera ↔ gate_detector smoke test** — render N gates at varied distances/angles/visibility, measure detection rate + PnP error per condition
2. **detector ↔ adapter integration** — feed detections into adapter, validate observation tensor matches state-based observation format the policy expects
3. **adapter ↔ policy** — load baseline 60.4M policy (the one that actually flies), run synthetic frames through full pipeline, measure how its action distribution differs from state-based input
4. **policy ↔ mavsdk_client** — verify TRPY mapping doesn't introduce sign flips or scale errors
5. **closed-loop synthetic flight** — full pipeline running over N synthetic episodes, measure flight stability and gate-completion rate when policy reads from vision instead of perfect state

## Success criteria for "vision-ready"

- Detection rate ≥ 95% on synthetic gates within 8m range
- PnP pose error ≤ 0.3m at 5m, ≤ 0.8m at 10m
- Adapter produces observations within 2σ of state-based observations across N=1000 random scenes
- Closed-loop synthetic flight: baseline policy gate-completion within 70% of state-based eval (degradation expected; tolerance reflects vision-induced noise)

## Files (to be created during shakedown)

- `01_detector_smoke.py` — synthetic_camera × gate_detector, measure detection + PnP error per condition
- `02_adapter_integration.py` — detector × adapter, validate obs tensor format
- `03_full_pipeline.py` — closed-loop synthetic flight with baseline policy
- `results/` — per-test JSON + plots
- `STATUS.md` — running log of what works and what's broken

## Coordination with Phase 2

This workbench is **independent of Phase 2 training**. It uses baseline 60.4M (the only policy that flies) as the test pilot. When Phase 2 produces a competent v3, swap it in here and re-run.

If Phase 2 hits the +15M GREEN gate AND vision shakedown passes, we'll have *two* candidate competition policies running through *the same validated pipeline* — diversification rather than single-track bet.

## Who maintains this

Clawd, autonomously, alongside Phase 2 monitoring. Updates to STATUS.md per work session.

🦞🧍💜🔥♾️
