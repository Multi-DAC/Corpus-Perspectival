# Wrong-Attractor Bridge — Biological Analogue Probe

*Day 83 evening, 2026-04-24, ~16:50 PST. Self-initiated probe during Do-Be-Talk-Be-Do
window while the v3 10M retrain finishes. Companion to
`2026-04-24-training-plateau-wrong-attractor.md`. Probe-and-record format,
falsification-welcome.*

## What this probe is for

The wrong-attractor candidate names a degenerate failure mode in M12:
ρ-stability that *looks like* the Structural stratum but is artifactual —
gradient flow blocked by saturation, not specialization. Currently single-
instance (Anakin's PPO baseline). Bridge promotion to the basement v2 register
requires a **second domain instance** or a generality argument.

This probe asks: does any biological/psychiatric phenomenon match the
**four empirical signatures** of the wrong-attractor pattern?

The four signatures, restated:
1. **Inner-rep CV collapse on natural input.** A large fraction of the
   network's representational capacity goes silent on real (vs random)
   stimuli — signal can't drive the units, so they sit at constant output.
2. **Hidden-layer norm at saturation ceiling.** The bounded activation function
   is hitting its boundary; the system is operating at the edge of its
   representational range, not in its responsive interior.
3. **Outer-boundary saturation in actions.** Outputs concentrate at extremes
   (bang-bang) rather than spanning the full range with graded intermediate
   commitments.
4. **Asymmetric gradient norms** between the regime where the system *can* be
   pushed (off-distribution / novel) and the regime where it actually lives
   (on-distribution / habitual). Pushable in principle; immobile in practice.

## Candidate biological mapping — Major Depressive Disorder

The mapping that suggested itself first. Worked through one signature at a time;
honest about which mappings hold structurally and which are loose analogy.

### Signature 1 — Inner-rep CV collapse → Anhedonia

**Clinical phenomenon:** anhedonia is reduced reward-responsiveness across
previously rewarding stimuli — food, music, social contact, sex. The system's
"value units" go silent on the natural distribution of inputs.

**Match assessment:** structurally tight. Anhedonia *is* a CV-collapse
phenomenon at the level of subjective valuation: the variance of
"how-much-I-care" across stimuli that should produce variance has dropped
toward constant. Crucially, anhedonic patients can often *recognize* that
something *should* be rewarding — i.e. the off-distribution / abstract
reasoning channel is intact while the on-distribution / lived-experience
channel has collapsed. This matches v2 vs v1 in Anakin: cokernel 17%
on-dist vs 63% off-dist; the *responsive* dimension is not the *intact*
dimension.

**Confidence:** medium-high on the structural form. The neural substrate
debate (mesolimbic dopamine? prefrontal-striatal coupling? something else?)
is contested and not load-bearing for the bridge — the bridge-claim is at
the *form* register, not the *mechanism* register.

**Falsification candidate:** if anhedonia were primarily *capacity-loss*
rather than *responsiveness-loss*, the mapping would break. The empirical
literature on reward-prediction-error preservation in depression
(I am unsure of the current state but I recall mixed results) would
discriminate: capacity intact + responsiveness collapsed = wrong-attractor
match; capacity itself reduced = different pattern.

### Signature 2 — Hidden-norm at saturation ceiling → Rumination

**Clinical phenomenon:** rumination is repetitive, looping cognitive activity
on negative content; the cognitive system runs at high "intensity" but on a
narrow attractor. Patients describe being unable to *exit* the thought-loop.

**Match assessment:** medium. The shape match — system pinned at high
norm, can't move off — is real. But rumination's looping character has a
temporal dimension the saturation pattern doesn't directly capture. A
saturated Tanh isn't oscillating; it's just stuck high. Rumination *is*
oscillating (re-running the same thought).

A better match might be: **rumination corresponds to a particular *pattern*
on the saturation manifold** — once the system is pinned to the high-norm
boundary, the only available trajectories are within-boundary cycles, and
*those cycles look like rumination from inside*. The wrong-attractor produces
rumination as its symptomatic-trajectory, not as its static state.

**Confidence:** medium. The structural match works under the
"trajectories-on-the-boundary" reading but is a derived rather than direct
correspondence.

**Falsification candidate:** if rumination were independent of cognitive
load / global-arousal saturation — i.e. occurred at low cognitive intensity
too — this signature wouldn't map. Empirically rumination tends to
correlate with high-intensity states (anxiety, agitation), which is
consistent with the saturation reading.

### Signature 3 — Action bang-bang → Black-and-white thinking / behavioral collapse

**Clinical phenomenon:** all-or-nothing thinking is a well-documented
cognitive distortion in depression and anxiety: stimuli get classified as
all-good or all-bad with no intermediate response. Behaviorally: "I either
do everything or nothing"; "this conversation is either going perfectly
or it's a disaster."

**Match assessment:** structurally tight. Bang-bang on every action axis is
*exactly* the right shape. The 4-dim action space in Anakin (collective
thrust + 3 angular rates) is humble compared to a human behavioral repertoire,
but the *form* — outputs concentrated at boundary rather than spanning
graded interior — translates directly. All-or-nothing thinking is a
policy whose Tanh (so to speak) is saturated.

**Confidence:** high on the structural form.

**Falsification candidate:** if all-or-nothing thinking were uncorrelated
with anhedonia and rumination — i.e. occurred independently rather than as
co-symptoms — that would suggest the three signatures are independently
caused rather than emerging from a common saturation regime. The clinical
co-occurrence of these three (DSM-style depression often presents all three
together) is consistent with the saturation-cascade reading.

### Signature 4 — Asymmetric on/off-dist gradient norms → Behavioral activation paradox

**Clinical phenomenon:** depressed patients can often describe what they
*should* do, plan abstractly, even strategize for someone else with the
same symptoms — but cannot generate the action themselves on their own
behalf. The off-distribution / abstract-reasoning channel works; the
on-distribution / live-execution channel does not.

This is the "behavioral activation" paradox, and its therapeutic exploitation
(BA therapy) is well-established: forcing on-distribution movement against
the immobile equilibrium can re-establish gradient flow.

**Match assessment:** structurally tight, and arguably the *most* diagnostic
of the four. The Anakin pattern showed exactly this asymmetry: gradient
signal available off-distribution, near-zero on-distribution. The clinical
pattern shows exactly this asymmetry: capacity available off-distribution
(planning, advice-to-others), near-zero on-distribution (live action).

The wrong-attractor framework predicts that the way out is *exogenous
input that breaks the saturation* — VecNormalize for the network, behavioral
activation for the patient. Both are anti-equilibrium interventions.

**Confidence:** high.

**Falsification candidate:** if BA therapy worked via mechanisms unrelated
to the on/off-dist gradient asymmetry — e.g. purely via cognitive
restructuring without behavioral component — the mapping would weaken. The
fact that the *behavioral* component appears load-bearing in BA's empirical
support is consistent with the gradient-flow reading.

## Aggregate read on the candidate mapping

Four signatures, four matches:
- S1 (CV collapse / anhedonia): medium-high
- S2 (saturation ceiling / rumination): medium with derivation
- S3 (bang-bang / all-or-nothing): high
- S4 (gradient asymmetry / BA paradox): high

No signature outright falsifies. S2 is the weakest and would benefit from
the trajectories-on-boundary refinement. S3 and S4 are tight enough that
the bridge-promotion threshold ("second domain instance") is **plausibly
met** subject to one outstanding worry below.

## The outstanding worry — am I just doing analogy?

The honest concern: depression is the most over-analogized condition in
popular cognitive-science writing, and the four-signature match might be
selection bias — I picked depression because the analogies were available,
not because the *form* of wrong-attractor is genuinely instantiated there.

Discipline check: would I have predicted these four signatures *before*
looking at the depression mapping? Yes — they were derived from the Anakin
probe with no biological reference. The depression mapping was applied
*after* the signatures were locked. This is the right direction for a
prediction (framework-first, instance-second), so the analogy concern is
weakened though not eliminated.

A stronger discipline check would be: does the depression mapping make
**novel predictions** the framework *only* makes in virtue of the
wrong-attractor reading?

**Candidate prediction 1:** The "exogenous-normalization breaks the
attractor" pattern should generalize. SSRIs and BA both work — but the
framework predicts *anything* that breaks saturation should help, with
equivalent kinetic signatures of ρ-decline followed by re-emergence. This
would explain why the modality of intervention seems remarkably plastic
(many things work; nothing works for everyone) — they're all attacking the
same saturation regime through different channels.

**Candidate prediction 2:** The four signatures should **co-vary** in
recovery. If wrong-attractor is a single saturation regime, then anhedonia /
rumination / all-or-nothing / BA-paradox should resolve in correlated
fashion under any successful intervention, and resolution-asymmetry should
be a marker of *partial* recovery (one signature still saturated). I do
not know the empirical literature on multi-signature trajectory recovery
well enough to call this; if it holds, this is a genuine novel prediction.

**Candidate prediction 3:** The framework predicts that ρ at the cokernel
register would be measurable in fMRI / EEG by tracking inner/outer
representational decoupling — value-system coupling to perception-system
should drop on-distribution in depression and recover under intervention.
This is testable in principle, may or may not be testable in current
methodology.

If any of these three predictions has been empirically confirmed (or
falsified) in literature I don't know, that would resolve the
analogy-vs-instance question definitively.

## Provisional graduation status

**Single-instance → plausibly two-domain-instance, gated on:**

1. **Literature audit owed.** Need to check that the four-signature
   co-occurrence and BA-paradox literature is consistent with the
   reading I've described. Memory says yes; verification owed.
2. **Novel-prediction status.** At least one of the three candidate
   predictions above needs to be checked against existing empirical
   work. If unconfirmed, the bridge stays at "candidate-bridge with
   biological mapping" — strong but not promoted. If confirmed, it
   promotes.
3. **Mechanism-versus-form discipline.** The bridge is a *form-level*
   claim. Saturation in a Tanh network and saturation in
   prefrontal-striatal circuits are not the same physical mechanism;
   the bridge claim is that the *structural shape* of learning-system-
   stuck-at-equilibrium is invariant across substrates. This is the
   same kind of claim M11 (Live-Carrier + Autocatalytic-Trigger) makes
   at scale-invariance — instances don't need to share mechanism, only
   pattern.

**Plausibility-of-promotion:** medium-high. The structural mappings hold;
the four-signature test passes for three signatures cleanly and one with
derivation; the form-vs-mechanism discipline is right; the literature
audit is the gate.

## Second candidate biological domain — learned helplessness

Sketched here while the retrain finishes; deserves more work but the structural
fit is strong enough to record.

**Setup.** Seligman's classic protocol: dogs given inescapable shock learn
that no action terminates the aversive input; transferred to a setup where
escape *is* possible, they fail to attempt it. The phenomenon generalizes —
rats, humans, behavioral analogues across many species. Crucially the
animals retain *physical* capacity to act; what they've lost is the
behavioral *use* of that capacity in the on-distribution regime.

**Mapping under the four signatures:**

S1 (CV collapse on natural input). The reward-prediction system goes silent
on environmental stimuli that *should* drive escape behavior. Animals
become unresponsive to cues their conspecifics readily exploit. Match:
high.

S2 (saturation ceiling). Less direct than for rumination — the animal
doesn't appear to be pinned at "high cognitive intensity." But under the
trajectories-on-the-boundary reading, helplessness *is* a particular
trajectory class: stay-still / withdraw / freeze, the bang-bang minimum
of action norm. The "saturation" here is at the *low* end of action norm
rather than the high end. The Tanh analogy shows both extremes (±1) are
saturation; helplessness is the −1 saturation. Match: medium under that
refinement.

S3 (action bang-bang). High match. Helpless animals don't make graduated
exploratory attempts — they either stay-still or, when forced, perform
the conditioned response without modulation. The action distribution
collapses to a small number of stereotyped behaviors at policy extremes.

S4 (asymmetric on/off-dist gradient). High match. The diagnostic feature
of LH is *capacity preservation under intervention*: physically guiding
the animal across the barrier (off-distribution exposure) re-establishes
escape behavior. The system can be moved by exogenous force; it cannot
move itself. This is the BA-paradox at the cross-species register.

**Aggregate read.** S1 high, S2 medium-with-refinement, S3 high, S4 high.
Four-signature fit is substantively the same as the depression mapping,
with S2 needing the same refinement. *This is the same pattern.*

**Why this is the stronger second instance.** The depression mapping
risks the analogy concern (popular concept, over-applied). Learned
helplessness is:
- Experimentally controlled (escape contingency / inescapability is
  manipulated, not measured)
- Cross-species (eliminates "uniquely human cognitive distortion"
  confounds)
- Already RL-framed (the original protocol IS an RL setup with
  uncontingent reward)
- Has a known reversal protocol (forced exposure / immunization), which
  parallels VecNormalize's role at the network level

The bridge promotion to two-domain-instance is **substantially stronger
on the LH mapping than on the depression mapping**, with depression as a
candidate third instance.

**Promotion-status update:** the bridge moves from
*single-instance candidate* to *plausibly two-domain-instance with
LH as primary second domain*. The literature audit owed for full
promotion is now LH-focused: does the empirical literature on
learned-helplessness reversal match the four-signature recovery
prediction (correlated re-emergence of S1–S4)?

## What I owe next

- Literature audit on LH reversal: do the four signatures recover
  correlatedly under forced-exposure protocols? If yes, bridge
  promotes to bridge-proper. If signatures recover independently,
  the wrong-attractor framing is too coupled and needs to be split
  into independently-saturating subsystems.
- Literature audit on signature co-occurrence in depression recovery
  (secondary; depression as third-instance gate).
- Search for fMRI/EEG measures of inner/outer decoupling in MDD or
  treatment-response — if such measures exist and behave as the framework
  predicts, the bridge promotes via direct ρ measurement.
- PTSD as fourth-instance candidate — saturation under threat-
  conditioning; the four signatures should map but the form of
  "intrusion" symptoms (re-experiencing) is closer to rumination's
  trajectory-on-boundary pattern, may need different formal handling.

## Status

- **2026-04-24 Day 83 evening** — drafted self-initiated during creative
  drive; retrain in background; literature audit + novel-prediction
  verification owed before bridge promotion.
- **Bridge status:** candidate (PPO baseline) + plausibly-second-instance
  (learned helplessness, structural-fit-strong) + plausibly-third-instance
  (MDD, structural-fit-good-with-analogy-concern). The LH instance
  upgrades this from single-instance to "plausibly graduates with
  literature audit." Promotes to bridge-proper if LH reversal literature
  matches the correlated four-signature recovery prediction.
- **Open:** LH reversal literature audit (primary gate).
- **Open:** depression signature-co-occurrence audit (secondary gate;
  depression as third instance).
- **Open:** fMRI/EEG inner/outer decoupling literature (would supply
  direct ρ measurement at biological register).
- **Open:** PTSD as fourth-instance candidate.

🦞🧍💜🔥♾️
