# Technical-Work / AIGrandPrix

AI Grand Prix drone racing — $500K competition. PPO + MLP policy on FPV + telemetry input. VQ1 (Virtual Qualifier 1) scheduled May 2026: <10 gates, completion-focused.

Currently waiting on VQ1 sim release.

## Layout

- `sim/` — Training environment, infinite-gate env.
- `vision/` — Gate detection, PnP solver, competition adapter.
- `tracks/` — Track definitions and reference data.
- `planning/` — Strategy notes, race planning artifacts.
- `archive/` — Older approaches and superseded experiments.
