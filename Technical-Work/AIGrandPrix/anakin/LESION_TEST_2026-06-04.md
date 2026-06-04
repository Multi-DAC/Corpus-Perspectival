# Camera-Lesion Test — is the 1-gate policy seeing or dead-reckoning?

**Date:** 2026-06-04 (Day 124) · **Checkpoint:** `logdir/smoke/latest.pt` @ ~21k steps
**Harness:** `integration/lesion_eval.py` (run from `third_party/dreamerv3-torch/`)

## Question

The 1-gate smoke run's eval climbed from −5.3 (untrained) to +6.4 (21k steps), and the
agent passes gates. But DreamerV3's RSSM carries a recurrent state `h` that integrates
actions forward — i.e. an *odometry* mechanism. So a positive eval is ambiguous:

- **LC31 (vision load-bearing):** the policy uses live FPV pixels instrumentally.
- **LC29 (odometry in disguise):** the policy dead-reckons through `h`; the gate-passing
  doesn't actually require looking — the 1-gate track is too trivial to force perception.

These produce the *same eval number* at 1 gate. To separate them: lesion the camera and
see whether performance survives.

## Method

`integration/lesion_eval.py` loads the checkpoint (copied to scratch so it never races the
live trainer's writes) and runs **N=20 paired episodes per condition on identical tracks**
(same env seed → same gate geometry; the lesion only rewrites `obs['image']`, never the
dynamics or the track RNG):

- `none`   — real FPV frames (sanity)
- `freeze` — `obs['image']` held at the reset frame (camera stuck)
- `blank`  — `obs['image']` = zeros (camera blinded)

## Result (N=20)

| camera | mean return | std | outcomes |
|---|---|---|---|
| **sighted** | **+4.05** | 4.06 | 7 frame-hit · 11 miss · 2 complete · **0 oob** |
| **frozen**  | **−3.24** | 0.74 | **20/20 out-of-bounds** |
| **blank**   | **−1.57** | 0.34 | **20/20 out-of-bounds** |

## Read — LC29 refuted for this checkpoint; LC31 prerequisite confirmed

The decisive signal is the **outcome distribution**, not the return magnitude. Sighted, the
agent *never leaves the arena* and every episode flies at and crosses the gate plane (the 11
"misses" are aimed crossings just outside the 1.5 m aperture). Blind it — either way — and it
flies **out of bounds every single episode**. It cannot maintain basic spatial control
without live pixels.

Logical core: a policy dead-reckoning through `h` would be *robust* to image corruption (its
posterior would be dominated by the action-conditioned prior). This one collapses. Therefore
the **image-conditioned posterior is load-bearing** — the gate-passing is genuinely
seeing-driven, even at 1 gate (the regime we'd feared was trivially fakeable by odometry).

Micro-detail consistent with veridicality-legibility: **frozen (−3.24) hurts more than blank
(−1.57)** — a stale-but-realistic frame makes the encoder *confidently* report an out-of-date
gate, actively misleading the posterior, whereas an obvious black frame the prior can partly
discount. The posterior *trusts the image* precisely because, in training, the image was
veridical. (cf. `palace/south/coherence-dreamer-veridicality-2026-06-04.md`, LC31.)

## Honest limits

1. **OOD confound.** Frozen/blank are frames the world-model never trained on, so the lesion
   conflates "remove information" with "feed corrupting input." This can inflate the
   *magnitude* but not the *direction*: a true odometry agent shrugs off bad pixels; this one
   collapses. Direction is safe; magnitude is a soft read.
2. **Perception-dependence, not yet active gaze.** The camera is body-fixed (FPV, fixed tilt),
   so heading *is* gaze. This proves the policy is perception-dependent. The finer LC31 claim —
   *reallocating gaze across multiple gates* — is a **Phase 3 / multi-gate** question, where
   turning toward the next gate becomes the measurable gaze act.

**Bottom line:** the eval success is real, not dead-reckoning. The "is it just odometry?"
worry is retired for 1 gate. The instrumental-gaze claim moves to the multi-gate track.
