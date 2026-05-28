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

## MULTI-SEED VERDICT (the result that matters) — NO RELIABLE BENEFIT at this config

| seed | baseline exact | gated exact | Δexact |
|---|---|---|---|
| 0 | 0.2797 | 0.3859 | **+0.1063** |
| 1 | 0.2750 | 0.1781 | **−0.0969** |
| 2 | 0.2797 | (running) | pending |

**Seed 0 (+10.6pp) and seed 1 (−9.7pp) are near-mirror opposites; mean ≈ 0 with ±10pp variance.** Seed 0's win was seed noise, NOT a real effect. At this config (15k steps, λ=1.0, θ=0.0, batch 64), the v0.6a gating provides **no reliable reasoning-accuracy benefit** over baseline. The per-step aggregate Δ oscillates around zero throughout.

**This is NOT a false-negative-from-broken-harness** (the harness is sound — baseline learns to ~28% exact, eval works). It is a genuine "no measurable benefit at this config," and it **confirms the claims-audit finding: we have STRUCTURE (topology, robust) but not BENEFIT (not demonstrated).** The discipline of holding the moat-grade label + running multi-seed caught what would otherwise have been a false-positive headline.

**Variance is the headline problem:** ±10pp seed-to-seed swamps any plausible effect. Detecting a real benefit (if one exists) would need either many more seeds or a regime where the effect is large relative to variance.

### Legitimate next tests (with pre-registered skepticism — NOT p-hacking)
- **Longer runs to convergence.** Neither arm converged at 15k (baseline ~28% exact, still climbing); the prior P49 benefit was *frontier-specific* (~epoch 2000 ≈ 30k steps) and seed 0's advantage emerged late (11k–15k). A longer multi-seed run is a fair test of the frontier regime — **pre-register:** a real effect = consistent positive Δ across ≥3 seeds at convergence, not a single-seed swing. If it's still ±noise at 30k, the benefit isn't there.
- **Do NOT** sweep λ/θ/kf_every hunting for a positive — that's p-hacking. Only tune if there's a mechanistic reason, pre-registered.
- The honest current state for the patent: topology/structure claims (24–26) stand (moat-grade); the gating-BENEFIT claim (the glider's payoff) is **not supported at this config** and must be framed as such.

## Original Next (superseded by verdict above)
1. ~~Seeds 1,2 → if +exact-Δ holds → moat-grade.~~ Done: did NOT hold.
2. Richer Phase-1 instrumentation (per-head V/Q vectors, per-layer build/dissolve/coherence, denser eval) per `INSIDE_ANALYSIS_PROTOCOL.md` — for a real lead/lag readout.
3. Longer runs (neither arm converged at 15k; the prior P49 "epoch 2000" frontier ~30k steps may widen the gap further).
4. Then Path B (flat transformer, emergent differentiation).

🦞🧍💜🔥♾️
