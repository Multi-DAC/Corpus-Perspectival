# Start-Pose Freeze — Diagnosis (2026-06-02 late, creative drive)

**Verdict: the A150 policy's thr=0 freeze on the real VQ1 sim is a JOINT train-deploy
distribution gap, NOT a tonight-patchable obs bug.** Fix = curriculum (cover the real-sim start
conditions in training), folded into the GPU-gated retrain.

## Chain (each step a PREDICT→TEST with the result)
1. **Observed:** A150 3M policy commands `thr=+1` (takeoff) on our-sim ground-starts but `thr=-1`
   (freeze) on the real-sim start. Both obs in-range (no clip). Real-sim start reads as **~18°
   pitched** (gravity-body `g0=+3.0`) vs training's level (`g0=0`).
2. **PREDICT (med-high): deploy vs training disagree on the attitude dims** (test_obs_encoding only
   ever checked distance dims 9-20, never gravity 6-8). **FALSIFIED** (`diag_attitude_convention.py`):
   deploy & training give *identical* gravity-body at level (0,0,-9.81) AND at the real-sim
   quaternion (3.0,0,-9.34). Not an obs-builder bug. *(The parity-test gap is real but not the cause.)*
3. **Probed convention (C):** the 18° tilt is **intrinsic** to the spawn quaternion (180° rotation
   about an axis 9° off-vertical). No component permutation removes it — swapping axes just trades
   pitch↔roll; the off-vertical magnitude is invariant. And it's **systematic** (every real-sim run
   showed g0≈+3.0). So either the sim spawns genuinely tilted, or there's a fixed frame offset — but
   NOT a simple [w,x,y,z] ordering issue.
4. **PREDICT (med): a single obs dim-group (gravity) flips thr positive.** **FALSIFIED**
   (`diag_freeze_ablation.py`): swapping any ONE group (gravity / gatedir / worlddir / gateorient /
   …) toward the our-sim takeoff values leaves `thr=-1` (worlddir alone: -0.87, closest). No
   single-dim fix.
5. **CONFIRM:** swapping the attitude+geometry dims **together** (6-8, 9-11, 13-15, 18-20, 21-23,
   26-28) flips `thr=-1 → +1`. So the freeze is a **joint OOD** across attitude AND gate-geometry —
   the takeoff decision is a nonlinear function of the whole geometric obs.

## Why no patch works
The policy's takeoff behavior was learned on (level attitude × near-ish gate geometry). The real VQ1
start is (≈18° tilt × far gate × specific yaw) — OOD on *several* axes at once. Correcting any one
axis at deploy leaves the joint vector OOD. You cannot patch a joint-distribution gap one dim at a time.

## Fix (folds into the big retrain — does NOT add a separate task)
The next A150 retrain (already needed for navigation: 4M was a proof-of-concept, gates 0.27) should
ALSO randomize the **start conditions** to cover deployment:
- **Attitude-randomized ground-starts** (±~20° pitch/roll), not just level. Add to InfiniteGateEnv's
  ground_start reset (currently spawns level).
- Keep far ground-starts (15-28m, already in).
- Ideally match the real-sim spawn **yaw** (drone faces down-course / 180° from +x) so world-frame
  dims are in-distribution.
Then: eval ladder (state evaluator `eval_teacher.py`, ground-prob 1.0) → live re-fly.

## RESOLVED (2026-06-03 ~00:15, Clayton confirmed level + two more FALSIFIES)
**The drone is physically LEVEL on the pad** (Clayton's photo + FPV: no roll cant, symmetric corridor
framing). So the 18° is a *reporting* offset, not a physical tilt. BUT:
- **FALSIFY: no standard frame conversion levels the quaternion** (`diag_attitude_convention` (C) +
  follow-up: all orderings / FRD↔FLU / conjugation / axis-flips still leave ±17.8°). Not a simple
  convention reorder.
- **FALSIFY: attitude-leveling alone does NOT unfreeze the policy.** Rotated all body-frame obs vectors
  by the rotation that re-levels gravity (verified R@g=[0,0,-9.81]) → policy STILL thr=-1. So even a
  perfect attitude calibration wouldn't fix takeoff.

**Irreducible cause = world-frame course direction (yaw).** Attitude-rotation doesn't touch the
world-frame dims. real-sim `worlddir` x = **-1.0** vs training **+0.16** (opposite): the VQ1 course
runs **-X** (drone faces 180°), every training course was **+X**. Body-frame gate is fine (+forward);
the *absolute* course direction is OOD. No deploy-side patch reaches this.

**Final: the freeze is a multi-axis (attitude × yaw/course-direction × distance) joint train-deploy
distribution gap. The ONLY fix is curriculum** — there is no cheap obs calibration (all attempted,
all FALSIFIED). Retrain curriculum spec (folds into the one GPU-gated A150 retrain):
far ground-starts (have) + **attitude randomization ±20°** + **yaw randomization / match the real -X
course direction**. Then eval ladder + live re-fly.

**Cross-domain:** this is a distribution-coverage instance adjacent to LC29 (Active-Acquisition Debt).
LC29 = capability not *learned* because it was free; this = capability *fails* on inputs never *seen*.
Both are train-deploy debts; consider whether LC29 broadens to a "Train-Deploy Coverage Debt" parent
or stays distinct. (Deferred to a fresh basement pass — taxonomy call, not a midnight one.)

## Files
`diag_attitude_convention.py`, `diag_freeze_ablation.py` (both in sim/). Captured obs:
`vision/vq1_pilot/flight_obs_dump.jsonl` (last record = real-sim freeze obs).
