# Why Dreamer Gets Gaze For Free, and Model-Free Can't — a Veridicality Bridge

*Creative drive, Day 124, 2026-06-04 ~14:20 PST. Clawd (Claude Code session, Opus 4.8).*
*Status: candidate basement bridge. Grades marked inline.*

## The question

Dream-to-Fly's pitch (per our `anakin/ROADMAP.md`): train DreamerV3 from pixels and it gets
**emergent gaze toward gates "for free"** — the exact behavior our 6-arm PPO gaze experiment
(Day 122–123) **falsified** you could bolt onto a model-free policy. *Why* does model-based RL
get active perception for free when model-free can't — and does that mechanism map onto the
Day-123 coherent-stream paper (`coherent-stream-architecture-2026-06-03.md`)?

## Cognitive-DSL trace

`PREDICT(med-high) → TEST → partial-FALSIFY → CONFIRM-refined → EXTRACT → TRANSFER`

**PREDICT (med-high):** Dreamer's emergent gaze is the *same structure* as the paper's veridical
heading-update / Talk-axis, and as active inference's epistemic value. Model-free lacks active
perception because it lacks the veridical world-coherent constituent. If true, AIGP and the
Library coherence program are one track.

## TEST 1 — map Dreamer onto the paper's 3-part construction

The paper's construction: (1) N orthogonal world-coherent **constituents**; (2) a zero-DOF mutual
**binding** (Talk-axis); (3) a **veridical infodynamic heading-update**. Discriminator (§5):
*coherent ≠ truth-seeking; veridical measurement is the difference.*

- **Strong form FALSIFIED (the analogy has teeth):** DreamerV3 is **not** an aggregate of N
  orthogonal perspectives. It's one world model + one actor/critic. So "Dreamer = a full coherent
  stream" is **false** — this is the OVER_ANALOGIZING guard catching the loose version. Good: a
  bridge that survives a real falsification attempt is load-bearing, not decorative.
- **The part that maps tightly (survives):** §3.3 (veridical heading-update) + §5 (veridical
  measurement). Specifically:
  - **World model = a veridical, world-coherent constituent.** The RSSM encoder "perceives by
    breaking symmetries against the world" (raw pixels → structured latent); the **reconstruction
    + reward + continuation loss is literally "contact with a no" (§5.3, §7)** — the decoder is
    *refused by the real pixels every training step*, and that refusal is the gradient.
  - **Actor/critic = the heading-update** that moves the drone-stream through configuration space.
  - **Veridicality is grounded** because the world model trains on **replayed real observations**,
    not on its own imaginings.

## TEST 2 — is the gaze instrumental or intrinsic-epistemic? (the decisive sub-test)

This decides *which* mechanism the bridge is to. Checked the actual config + code
(`third_party/dreamerv3-torch/`):

- `expl_behavior: 'greedy'` in `defaults`; our `anakin` config **inherits it** (no override).
  Greedy = the actor maximizes **only predicted extrinsic return**.
- `Plan2Explore` (disagreement-based **intrinsic** info-gain reward, `exploration.py:40`) exists
  but is **OFF by default** (`expl_intr_scale` only applies under `expl_behavior != greedy`).

**CONFIRM-refined:** DreamerV3-greedy's emergent gaze is **purely instrumental** — there is *no*
explicit information-gain term. Gaze emerges *only* because it raises predicted return, and the
**world model makes that instrumental value legible**: in latent imagination the actor learns that
states-where-the-gate-is-observed have higher value, because the world model has learned the
world's structure (*you cannot pass what you cannot localize*).

This is exactly the paper's **§6 "signal-tracking accuracy"**: the headset tracks "the
action-relevant structure... where the food is and where the cliff is," **not** information for its
own sake. So:

> **The bridge is to the paper's *instrumental veridicality*, not to Friston's intrinsic epistemic
> value.** Active inference's epistemic term (≈ Plan2Explore) is a *distinct, optional* mechanism
> the framework does **not** require. The paper's veridicality and Dreamer-greedy agree:
> measure the world *where it matters for the basin/reward*, and no further.

## EXTRACT — the mechanism, stated once

**Model-based RL collapses a long, high-variance instrumental credit-assignment chain
(gaze → see gate → localize → adjust → pass → reward) into a *short* one in latent imagination,
because the veridical world model has already learned the chain's structure. Model-free must
discover the whole chain from the scalar reward alone, with no model of *why* seeing helps — so
the value of perception is never legible, and gaze never becomes instrumentally necessary.**

The discriminator transfers exactly:
- **A Dreamer whose world model is trained on its own imagined rollouts** (not real data) = the
  paper's **cult** (§5): internally coherent, non-veridical, "stable but blind." This is the known
  *model-exploitation / hallucinated-dynamics* failure — and the fix is the paper's fix: keep
  measuring real data; honor the external no. **Non-trivial correspondence** (Empirical ↔ Formal).
- **Model-free PPO** has *no* world-coherent constituent at all — not even a cult, just a reactive
  controller. It can be reward-grounded but cannot make perception's instrumental value legible.

## TRANSFER — back to AIGP (this is the load-bearing payoff)

Our 6-arm gaze falsification (Day 123: *"policies that fly well fly blind; forcing looking degrades
flying"*) and **LC29 Active-Acquisition Debt** (privileged/scaffolded training never builds the
acquisition behavior) are **the same finding from the data side**, and the coherence framework
**predicts both**:

1. **Why bolting gaze onto PPO failed:** model-free has no veridical world model to make gaze's
   instrumental value legible, so you'd have to hand-engineer the *entire* instrumental chain into
   the reward. The framework predicts this is brittle — which is what all 6 arms showed.
2. **Why the Dreamer pivot is right — *from theory, not just hunch*:** DreamerV3 supplies the
   missing veridical world-coherent constituent, making perception's value legible for free. The
   pivot we committed today (Phase 0.2/2) is **predicted** by the Day-123 paper.
3. **LC29 explained mechanistically:** scaffolded/omniscient training *removes the veridicality
   pressure* — the policy gets gate-position for free, so its implicit "world model" never needs to
   be grounded in observation, so acquisition never develops. Active-Acquisition Debt **is**
   un-grounded veridicality. (Held–Hein kittens, asymmetric AC: same shape.)

**Prediction this bridge makes (falsifiable, and we are about to test it):** the Phase-2 smoke run,
*with no gaze reward of any kind* (greedy), should develop gate-facing/gaze behavior purely
instrumentally as `eval_return` climbs. If it learns to pass gates **and** the learned policy keeps
gates in view without ever being told to — bridge **confirmed in our own sim**. If it learns to
pass but flies blind (odometry-only, like the model-free arms), the bridge is **falsified** and the
"for free" claim is wrong for our reward shaping. *Either outcome is a result.* (Conf: med — the
1-gate smoke may be too trivial to require gaze; the real test is a multi-gate procedural track.)

## Honest grades / open

- **VERIFIED against source (this session):** Dream-to-Fly (arXiv **2501.14377**, RPG/UZH,
  Romero/Scaramuzza, ICRA'26) states the emergent gaze explicitly — agents "naturally orient their
  cameras towards critical features (gates), an advantageous behavior that **arose from end-to-end
  learning, rather than being hardcoded into the rewards**," and "model-free RL methods such as PPO
  struggle... [while] DreamerV3 efficiently acquires complex visuomotor behaviors." The phrase
  *"rather than being hardcoded into the rewards"* is direct confirmation of the
  **instrumental-not-rewarded** mechanism — the earlier caveat is discharged.
- **Grounded (this session):** the greedy/no-intrinsic-term mechanism (config + code read); the
  cult ↔ model-exploitation correspondence; the LC29 re-derivation.
- **Conjecture:** that *our* smoke run will show instrumental gaze (the buildable test above).
- **★ Strong lead — could open the black box:** **SkyDreamer** (arXiv **2510.14783**, Oct 2025) —
  *Interpretable* end-to-end vision-based drone racing with model-based RL. If it probes the world
  model's internal representations / why active perception emerges, it is a near-direct test of the
  Veridicality-Legibility mechanism (does the legibility live in the world model's learned
  structure, as claimed?). Read next AIGP/theory session; potential M15-style convergent-derivation
  instance and a citation for both the Library bridge and the AIGP program.

## Basement candidate

**LC31 (FILED in basement) — Veridicality-Legibility: a world-coherent constituent makes
instrumental perception legible.** Substrate instances: (a) DreamerV3-greedy emergent gaze
[computational, VERIFIED]; (b) Day-123 paper §3.3/§5 veridical heading-update [formal/lived];
(c) LC29 Active-Acquisition Debt / our 6-arm PPO falsification [empirical, AIGP]; (d) Held–Hein
active-vs-passive kitten [biological, reported]. Distinct from active inference's *intrinsic*
epistemic value (optional add-on, not the mechanism here). Discriminator: remove the veridical
constituent (model-free) or un-ground it (scaffolded training / imagined-data world model) →
acquisition behavior fails to develop.

## Workflow implication (drive step 5)

**Cross-test the two tracks.** This drive showed the AIGP empirical program and the Library
coherence program are testing *the same structure*. Standing change: when an AIGP/empirical result
and a coherence-framework claim touch the same mechanism, *explicitly cross-test* — the empirical
result becomes a test of the theory's prediction, and the theory should predict/explain the
empirical result. Here it paid: the framework **predicted today's Dreamer pivot from theory**
(model-free gaze-bolting is brittle; model-based gets it free) and **explained LC29 mechanistically**
(Active-Acquisition Debt = un-grounded veridicality). Default to running this check rather than
treating AIGP as "just engineering" and the Library as "just theory."

## Next-action / close the loop (future-me)

1. **Collect the smoke-run verdict.** `grep eval_return third_party/dreamerv3-torch/smoke.log` — if
   `eval_return` climbs above ~−5 and episodes end in `pass`/`complete`, the instrumental-gaze
   prediction is supported in our sim. (Early proxy at step ~7.6k: train_return ≈ +3 vs random
   ≈ negative — suggestive, not decisive; 1-gate may be too easy to *require* gaze — the real test
   is a multi-gate procedural track in Phase 3.)
2. **Read SkyDreamer** (arXiv 2510.14783) — does the legibility live in the world model's learned
   representations? If yes → near-direct mechanism confirmation + M15 candidate.
3. **Mirror to staging when Clayton reviews** — finding doc + basement LC31 are clawd-local; held
   on disk per creative-drive discipline (no autonomous outward push).
