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
