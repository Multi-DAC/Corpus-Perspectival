# Range-from-Motion vs PnP (creative-drive exploration, 2026-06-01 evening)

## The question
W3 found: detector **bearing** to the gate is reliable (~1–3°); **range** (PnP from the
square) is the weak/noisy axis. At deploy we ALSO get reliable **velocity** (telemetry).
Classic bearing-only target tracking: bearing + own-motion recovers range, no PnP needed.

**Can a range estimate from bearing + velocity-integrated motion beat single-frame PnP
range error on the captured approach sequences?**

## Prediction (confidence: medium)
Motion-triangulated range will have LOWER error than PnP in mid-range, BUT may degenerate
when motion is nearly along the line of sight (flying straight at the gate → range
unobservable from bearing alone — the textbook bearing-only degeneracy). Net: win where
there's lateral motion; possible tie/loss head-on. A clean FALSIFY (worse everywhere)
would mean the toward-gate degeneracy dominates → trust PnP, drop this idea.

## Method
Per frame in an approach sequence (sorted by sim_time):
- **bearing_ned**: detected gate pixel center → camera ray → (invert W3 transform: camera→FRD
  via −20° tilt → body→NED via ego quat) → unit vector. (Validate inverse against forward proj.)
- **rel displacement** over a sliding window: integrate telemetry velocity (NED) backward from
  the current frame (deploy-realistic — no absolute position needed).
- **triangulate**: gate position g (relative to current ego) minimizes Σ‖(I−bᵢbᵢᵀ)(g−pᵢ)‖²
  → linear LS, closed-form 3×3 solve. range_est = ‖g‖.
- Compare range_est error vs PnP-range error vs ground-truth range.

## Results — PREDICTION FALSIFIED (clean, high-information)

On the w2_forward_170205 approach (201 usable frames, 181 windowed):

| range estimator | median |frac range err| |
|---|---|
| **PnP (single-frame)** | **0.038** |
| triangulation (DETECTED bearing) | 0.410 |
| triangulation (TRUE bearing, method upper bound) | 0.338 |

**PnP wins decisively (3.8% vs 41%).** And triangulation with *perfect* bearings is still
0.338 — so it's NOT the detector's bearing noise (which was excellent: inverse-transform
check median |bdet−btrue| = **2.65°**, independently confirming both the camera↔NED transform
AND the detector). The method itself fails here.

**Why (the prediction's escape clause was the whole story):** the drone flies *toward* the
gate, so motion is nearly along the line of sight → bearing-only range is **unobservable**
(textbook bearing-only degeneracy). Even the "lateral" bins didn't rescue it:

| vel-vs-LOS angle | n | PnP | tri(detected) |
|---|---|---|---|
| 0–5° (head-on) | 3 | 0.026 | 1.000 |
| 5–15° | 4 | 1.088 | 0.158 |
| 15–30° | 44 | 0.106 | 0.140 |
| 30–90° | 62 | 0.054 | 0.320 |

(The 5–15° "win" is n=4 noise where PnP happened to spike.) Short velocity-integration
baseline + toward-gate geometry ⟹ triangulation can't compete.

## Conclusions (what changes)
1. **DROP range-from-motion.** For a *known-size* gate, single-frame PnP is the right range
   estimator; don't build a motion-fusion EKF — it won't help in the toward-gate regime.
2. **PnP range is BETTER than W3 implied: ~3.8% on a clean approach** (W3's ~19% was inflated
   by close-frame clipping + active-gate/largest-blob association artifacts). The perception
   range axis is in good shape as-is. Consider tightening PerceptionObsWrapper range_sigma_frac
   from 0.19 toward ~0.06–0.10 (well-framed regime) — but keep some margin for the close-clip case.
3. **Bonus validation:** the camera↔NED transform + detector bearing are confirmed accurate
   to ~2.6° via an independent inversion path (not just the W3 forward projection).

