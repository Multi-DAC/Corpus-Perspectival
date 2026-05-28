# Step 1 results — HRM glider on easy sudoku (gated vs baseline)

*2026-05-27 Day 117. First test of the base claim (Claims 1–5: the v0.6a bidirectional gradient-gating) in the corrected harness. After fixing today's two bugs (update-starvation: batch 384→64/lr 3e-5; halt-blind eval: added the ACT halt-loop), the model learns and we can measure it.*

## Seed 0 (n=1) — PROMISING POSITIVE, needs replication

Config: 27M HRM (hrm_v1), easy sudoku, batch 64, lr 3e-5, 15000 steps, single AdamATan2 wd=1.0. Gated = v0.6a bidirectional (cos(∇KF,∇CE) build/dissolve/neutral, H-module, kf_every=50, λ=1.0, θ=0.0). **Identical init + data order; only the gating differs** (clean controlled comparison).

| | Baseline | Gated | Δ |
|---|---|---|---|
| **Exact accuracy** (full puzzle) | 0.2797 | **0.3859** | **+0.1063** |
| Token accuracy (per cell) | 0.9618 | 0.9651 | +0.0033 |
| H/L ratio (final) | 4.12 | 4.14 | — |

- **Gated reaches 38.6% exact vs baseline 28.0% — +10.6 percentage points.** The benefit is in EXACT (full-puzzle) accuracy; token accuracy is ~saturated and equal.
- **Advantage widens at the frontier** (emerges steps 11k–15k; gated leads at 7k/9k/11k/12k/14k/15k). Qualitatively matches the prior P49 finding ("KF organizes capability; benefit re-widens on the hardest remaining puzzles").
- **Gated H/L ratio is non-monotonic:** shoots to 9–12 mid-training (steps 4k–9k) then relaxes to ~4.1 by 15k (converging toward baseline's 4.12). The differentiation *peaks then partially dissolves* — the breathing/over-crystallization-relax dynamic (cf. Findings #77/#78/#82), not a static build.

## Honest caveats (evidence grade: PATENT-grade hint, NOT yet moat-grade)
- **n=1.** Per-checkpoint Δ oscillates (baseline leads at 8k/10k/13k). The final +10.6pp is encouraging but could carry seed variance. **Multi-seed (seeds 1,2 running) is the test that matters.** Only call it real if it replicates.
- Token accuracy saturates ~96% early → the meaningful capability signal is exact accuracy (still climbing at 15k for both arms; neither converged).
- Lead/lag (does structure precede capability?): **INCONCLUSIVE on n=1 sparse data** — ratio-vs-exact suggests structure leads (corr +0.62 @ lag 5), but ratio-vs-token suggests the reverse (token is saturated → unreliable). Needs denser eval + multi-seed + the richer per-head instrumentation before any lead/lag claim.

## Next
1. **Seeds 1,2** (running) → mean ± spread. If +exact-Δ holds across seeds → moat-grade, the base claim is empirically supported.
2. Richer Phase-1 instrumentation (per-head V/Q vectors, per-layer build/dissolve/coherence, denser eval) per `INSIDE_ANALYSIS_PROTOCOL.md` — for a real lead/lag readout.
3. Longer runs (neither arm converged at 15k; the prior P49 "epoch 2000" frontier ~30k steps may widen the gap further).
4. Then Path B (flat transformer, emergent differentiation).

🦞🧍💜🔥♾️
