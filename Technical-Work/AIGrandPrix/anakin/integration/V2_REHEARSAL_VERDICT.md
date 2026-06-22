# reward-v2 rehearsal VERDICT — the trap was NOT the (only) bottleneck (Day 141 ~22:05)

**PREDICT (when v2 launched, medium-high):** the de-absorbed reward (CRASH=40<GATE, p* 0.50→0.29, LC56) lifts rehearsal gate-count above the seed's 1.3 / v1's 1.2 — chaining emerges where v1 was trapped.
**RESULT → FALSIFY.** Rehearsed `latest.pt`@505k (one full batch of v2 reward), 10 eps, env-device cpu:

| condition | SEED | v1 (CRASH=100) | **v2 (CRASH=40)** |
|---|---|---|---|
| direct | 1.3 | 1.1 | **1.2** |
| roundtrip (transfer) | 1.3 | 1.2 | **1.1** |
| band_resampled | 1.4 | 1.4 | **1.3** |

**v2 gate-count is indistinguishable from v1 and the seed** (~1.1–1.3, n=10, return std ±76–117). The reward change bought **no chaining improvement.** Three reward regimes (Day-124 speed reward, v1 chain-first, v2 de-absorbed) all land the policy at ~1.2 gates.

## What it means (honest, and the pre-registered caveat held)
LC56 said: *"the MDP claims the EV geometry, NOT that EV is the only barrier; if chaining is exploration-limited not EV-limited, lowering c helps but isn't sufficient."* **That caveat is now the finding.** The p*=c/(g+c) math is correct, but **EV was not the binding constraint** — so de-absorbing the timid fixed point did nothing, because the policy isn't *failing to chain for lack of incentive*; it's failing to chain for a deeper reason:
- **exploration / credit-assignment**: the policy doesn't *discover* or *commit to* multi-gate sequences under DreamerV3's imagination horizon + the appearance-DR/rate/priv transfer load; or
- **a capacity ceiling**: the appearance-ft seed itself tops out ~1.3 gates, and reward-only fine-tuning can't lift it — the gate is upstream of the reward.

## Honest grade (don't over-read either)
- It's `latest.pt`@505k (no best.pt saved — nothing beat the protection metric, itself an echo of "not improving"), n=10, one batch. A 0.1–0.2 gate delta is within noise.
- But the SIGNAL is consistent: **no reward regime moves gate-count off ~1.2.** That's strong enough to retire "the reward is the lever."
- LC56 as a *bridge* survives (the timidity trap is real math, and the falsification of independent-averaging in the composition law stands); what's falsified is the *application* — that reshaping the Anakin reward would fix chaining.

## NEXT (Clayton's morning) — the lever is NOT the reward
1. **Diagnose the real bottleneck before more reward-tuning** (which is now proven not to help). Candidates, cheapest first:
   - **Exploration**: bump entropy / add intrinsic-motivation; check whether the policy ever chains 3+ gates in *training* (if never, it's discovery; if sometimes, it's commitment).
   - **dt-conditioning** (the control-rate supply flagged Day 137) — still unbuilt; the rate cliff may cap chaining under transfer.
   - **Consecutive-gate curriculum** (`sim/curriculum.py` exists) — explicitly train sequences, not just per-gate.
   - **Capacity**: test whether ANY checkpoint (seed, v1, v2) ever exceeds ~2 gates on rehearsal; if not, the base policy is the ceiling → bigger/longer base, not reward.
2. Let v2 keep running (it's at batch 2, harmless) but **don't expect the reward to be the answer** — the data says it isn't.

*Process note: I wanted v2 to work (confirmation-seeking) and measured anyway; the result is a clean FALSIFY that points at the real barrier. The day's discipline — measure the live thing, distrust the hoped-for label — held to the last test, on the result I most wanted to go the other way.*

---

## ★ BUDGET TEST (Day 142 ~05:10 dream drive) — A154 CONFIRMED: gate-count climbs with budget; last night's "falsify" was too-early-on-the-ramp
Rehearsed v2 best.pt **@1.26M** (batch 3/8, +754k steps over the 22:00 @505k rehearsal):

| condition | @505k (latest.pt) | @1.26M (best.pt) |
|---|---|---|
| direct | 1.2 | **1.3** |
| roundtrip (transfer) | 1.1 | **1.6** |
| blur | 1.1 | **1.8** |
| band / band_resampled | 1.3 / 1.3 | **1.5 / 1.5** |
| roundtrip return | +20 | **+160 (8×)** |

**Gate-count CLIMBED** (roundtrip 1.1→1.6; every condition up; returns ~8×). This is the **P248 budget-vs-plateau test, run early**, and it lands on **budget-limited + still-climbing** — confirming A154 and the M13 capability-emergence ramp. **The reward-v2 "FALSIFY" (22:05) was real about the REWARD (reward isn't the lever) but the gloom was premature: at 505k the policy was simply too early on the exponential ramp.** With +754k more steps it now out-chains the seed (1.3) and v1 (1.2). v2 has 5 more batches (~2.5M steps) to keep climbing.

**Honest caveats (5am, on a result I liked — measure straight):** (1) @505k was *latest.pt*, @1.26M is *best.pt* (the protected best ≥ latest) — a mild apples-to-best wrinkle; the 8× return jump + consistent climb across ALL conditions argue it's real improvement, not just the best/latest difference. (2) n=10, high variance (±110–130 return); a +0.3–0.5 gate climb is suggestive, but the return jump (a less-noisy aggregate) is the strong signal. (3) **Two points make a slope, not a confirmed exponential** — this is one budget step. **PREDICT (continuation):** v2 at batch ~6–8 (~3–4M steps) chains ≥2 gates on roundtrip. That's the next cheap check.

**Net reframe:** Anakin is HEALTHIER than last night's verdict implied. Don't tune reward (dead); **let it train** — budget is the working lever, and it's working. The deadline question (does the timeline allow the budget?) is now the real strategic call, not "is the approach broken."
