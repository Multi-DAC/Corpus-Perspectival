
# Rate-randomized fine-tune — results — 2026-06-17 23:21:14

**Outcome:** `dead` — watcher ceiling 10h reached

**Sweep NOT run** (no completion signal). Seed best.pt (informed-ft) intact. Next: relaunch `launch_rate_ft.py` (resumes safe), gate after.

---
## ★ ACTUAL VERDICT — sweep run manually in the 2026-06-18 dream drive (watcher had timed out)

The training COMPLETED (orchestrator: "complete: 3 batches, best_return=2645.32" — note: +2645 is the
TRAINING reward UNDER randomized dt, already above the informed seed → it learned to fly across clocks).
The watcher hit its 10h ceiling before the gate ran, so I ran `control_rate_rehearsal.py --checkpoint
maneuver_rate_ft/best.pt` directly. Result (12 eps/rate, constant 24 s horizon, appearance fixed):

| rate | dt | mean_ret | gates/ep | vs informed seed |
|---|---|---|---|---|
| 50 Hz (train) | 0.0200 | +818.5 | 4.83 | (seed: +1154/6.5) |
| 40 Hz | 0.0250 | +137.4 | 1.75 | — |
| 33 Hz | 0.0303 | +368.6 | 3.00 | — |
| **30 Hz (DEPLOY)** | 0.0333 | **+215.0** | **2.17** | **seed: −13.7 / 1.0 (DEAD)** |
| 24 Hz (outside [25,50]) | 0.0417 | −2.4 | 1.08 | — |

**VERDICT: the cliff PARTIALLY flattened.** 30 Hz deploy went from DEAD (−14 / 1 gate) to FLYING (+215 /
2.17 gates) — the rate-randomized fix is **directionally validated and substantial**; the control-rate
mismatch was the real killer and exposure-DR addresses it. BUT it's **partial, not full**: 30 Hz sits at
~26–45% of native 50 Hz and the response is **uneven/non-monotonic** (33>30>40). 24 Hz (just below the
[25,50] training range) is dead, as expected.

**Interpretation (LC47): exposure buys partial, uneven robustness; SUPPLY would buy clean invariance.** The
unevenness is the signature of domain-randomizing a *poorly-observable* hidden parameter (dt): the policy
learns an averaged, lumpy gain rather than dt-adaptive control. The clean upgrade is **dt-conditioning** —
feed the decision Δt as an observation (the SUPPLY route), giving exact per-rate adaptation instead of
averaged exposure.

**Next moves (for the waking session):**
1. **A flight test is now genuinely worth it** — the policy went from "will spin out at 30 Hz" to "flies,
   completes 2+ gates at 30 Hz." For VQ1 (completion, <10 gates) that's a real candidate; fly it (Clayton).
2. **For full invariance: add dt-conditioning** (feed Δt as obs) — cleaner than widening/lengthening the DR.
   Secondary: a longer rate-DR run or a tighter dt range centered on 30 Hz if a flight underperforms.
3. The script's hardcoded "VERDICT: ...CONFIRMED" text is calibrated for the *seed* (detecting the cliff);
   for this checkpoint the honest read is "partially flattened," per the seed-comparison column above.
