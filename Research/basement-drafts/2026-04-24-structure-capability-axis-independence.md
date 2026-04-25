# Basement Draft — Structure / Capability Axis Independence

**Status:** DRAFT (cold-register probe pending). Surfaced 2026-04-24 evening from AIGP Phase 1 eval falsification of Reading A. Two same-day instances in two registers (RL-training register + Companion §6 categorical register) suggest a candidate cross-domain structural pattern. Filing here so it doesn't drift; not yet basement-promotable.

**Recovery addendum (2026-04-24 late evening) — finding sharpened, not weakened.** The original Phase 1 eval used denormalized observations for v3 7.5M and v3 200K because their `vec_normalize.pkl` was lost when the v3 retrain was killed before training-end save fired (eval harness silently fell back to `env = raw`). Pre-flight check before Phase 2 launch caught this; built `probes/reconstruct_vecnorm.py` and re-ran. **Corrected numbers:** v3 7.5M 0.03 ± 0.06 gates (down from contaminated 0.20 ± 0.18); v3 200K control 0.07 ± 0.12; baseline 60.4M unchanged (its vecnorm existed on disk). Under proper normalization v3 7.5M is statistically *indistinguishable* from v3 200K (0.03 vs 0.07, both 100% crash). The 0.20 was random-twitching noise from denormalized obs that occasionally clipped a gate by accident — not real flight skill. The empirical decoupling is therefore *tighter*, not looser, after correction. 7.5M of clean F1+F2+F3 training under healthy structural conditions produced ρ climb 0.026 → 0.243 with **zero detectable flight-skill transfer** over the 200K control. This is the strongest version of the independence claim available at this register. (Phase 2 retrain launched the same evening will test whether extended training under healthy structure eventually produces transfer; the +15M checkpoint gate at total step 22.5M is the next decision point — see `projects/aigrandprix/snapshots/phase2-baseline-2026-04-24/CHECKPOINT_GATE.md`.)

**F2 timing correction (2026-04-25 ~00:30 PST) — independence claim survives, "log_std bounded" sub-claim does not.** During the Day-83-evening integration check, Phase 2 telemetry showed log_std at step 12.5M reading [0.156, 0.154, 0.180, 0.147] — all *above* `log_max = 0.0` (i.e., std ≈ 1.17–1.20, ~17–20% above the 1.0 cap). Investigation overnight (reading SB3's `OnPolicyAlgorithm.learn`) confirmed: `LogStdClampCallback` hooks `_on_rollout_end`, which fires *between* `collect_rollouts()` and `self.train()` — i.e., BEFORE the 1024 gradient updates per train() call (n_steps=4096 × 16 envs / batch_size=512 × n_epochs=8). The clamp is a periodic snap-back (1 clamp per 1024 updates), not a true bound. **Implication for the v3 7.5M analysis:** the structural cure was real (hidden norms 6–17, no dead value neurons, no action saturation, ρ climb 0.026 → 0.243), but the cure was carried by F1 (VecNormalize) and F3 (gradient telemetry's monitoring effect), NOT by F2 in the bounded-log_std sense. F2 reduced log_std drift via periodic snap-back; it did not strictly bound it. **Implication for the L11 candidate:** unaffected. The Structure axis (ρ trajectory) and Capability axis (flight skill at fixed budget) decoupling is independent of which specific structural-cure component carried which load. If anything, the F2 finding *strengthens* the independence claim — the structural axis stayed healthy even though one of its three named cures was less complete than reported. **Implication for the +15M gate:** zero. Eval uses `deterministic=True` (mean actions only), so log_std drift doesn't enter the gate criteria at all. Phase 2 keeps running on schedule; F2 fix can wait for Day 84+ design. Smoke-test apparatus that surfaced this finding archived at `projects/aigrandprix/sim/smoke_test_callbacks.py`.

**Phase 2 +15M gate result (2026-04-25 ~05:30 PST) — independence claim survives but reformulates from PERMANENT to REGIME-DEPENDENT.** Phase 2 finished overnight (67.5M total, full 60M past resume). The +15M gate eval at step 22,500,016 produced per-maneuver aggregate gates **17.95** vs the pre-committed GREEN threshold of 1.0 (an 18× margin). Curriculum eval gates_mean = 12.38, gates_max = 19. **Already exceeds the wrong-attractor baseline 60.4M (per-maneuver agg 16.33) at one-third the training budget.** This forces a substantial reformulation:

- The 7.5M-vs-200K equivalence (0.03 vs 0.07 per-maneuver gates) under healthy structure was a **low-budget regime** observation, NOT a permanent decoupling. Capability transfer happens; it requires more training budget than the structural axis itself takes to stabilize.
- The new claim shape: *Capability and Structure are decoupled below a critical training budget τ; above τ, they couple, with the **rate** of coupling determined by structural health.* The threshold τ for this curriculum / architecture / cure stack lies somewhere between **7.5M and 22.5M** training steps. Material exists for free (intermediate checkpoints at 10M / 12.5M / 15M / 17.5M / 20M, all with paired vecnorm.pkl) to pin τ more precisely.
- This is a **stronger** empirical claim than the original "permanent independence at fixed budget", because it now needs to identify what regulates τ across registers. In the RL register, plausible regulators include: minimum-budget-to-build-features-from-which-capability-can-emerge (representation-bottleneck reading), minimum-budget-for-value-bootstrap (credit-assignment reading), or curriculum-difficulty-coupled-floor (curriculum-design reading). A55 (the anomaly that promoted from this draft) now has a much sharper third question: how does τ scale with curriculum complexity and capacity?
- **Implication for the CT instance** (Companion §6 inner/outer adjunction): the analogous question is whether the residue-measure / carrier-structure decoupling is also regime-dependent in a CT sense. Provisional claim: in CT the decoupling is **definitional** (the carrier is selected by what dynamics you want to expose; the measure doesn't constrain), so there is no analogue of τ. This makes the RL / CT instances DIFFERENT in a way that may matter for whether they compose into a single basement-promotable bridge.
- **Implication for the third-instance test** (Open Question 4 below): the candidates need to admit a regime-dependent reading. Biological / physics / info-theory instances should be probed not just for "is there decoupling at fixed budget" but also "is there a budget threshold above which coupling re-emerges". The L11 candidate either generalizes to a "regime-dependent residue/carrier decoupling" pattern, or graduates only the RL-register version with the CT version remaining a definitional cousin rather than a structural sibling.

The structural cure story is unchanged: F1 (VecNormalize) carried it, F2 was confirmed-broken throughout, F3 was supportive-monitoring. Phase 2's value head stayed alive (grad ~0.003 throughout, vs baseline collapsed to 0.000003) across the full 60M. The cure works; capability emerges; the timescale was longer than the original Phase 1 falsification could detect.

---

## The candidate pattern

When a system carries a **residue measure** (a scalar or trajectory that quantifies "how much of the substrate's potential structure is realized"), the residue measure does **not** determine which substantive structure carries it. The two are on independent developmental axes: a system can have healthy residue measure and weak substantive realization, or unhealthy residue measure with strong-but-brittle substantive realization. Improvements along one axis do not produce improvements along the other at a fixed budget; the two require separate cultivation.

Stated more carefully: let M be a measure on system S, and let C be a concrete structure realized by S. Healthy(M(S)) is necessary but not sufficient for Strong(C(S)); Healthy(M(S)) and Strong(C(S)) are independent random variables in the absence of a coupling mechanism. The measure can be load-bearing (predict generalization, robustness, noise-tolerance, etc. — the *kinds* of capability that emerge) without being load-bearing for the *level* of capability at any fixed training budget.

This is candidate-level structural; the formal statement requires picking out what counts as a "residue measure" and what couples / decouples it from the substantive axis.

---

## Two same-day instances (2026-04-24)

### Instance 1 — RL-training register (Anakin AIGP)

**Setup.** PPO + MLP[512,512] policy trained on procedurally-generated drone-racing curriculum. Wrong-attractor finding (Day 83 morning, M12 addendum to basement) named that the baseline 60.4M policy's 85.5% gate completion was structurally pathological — 465/512 dead value neurons, 87–93% action saturation, log_std[3] = 40 — but that the structural pathology produced a ρ-stability profile that *appeared* like a healthy M12 Structural-stratum plateau.

A v3 retrain under three fixes (F1: VecNormalize, F2: log_std clamp, F3: gradient telemetry) at 7.5M steps showed healthy structure: hidden norms 6–17, log_std bounded, ρ-trajectory monotonic into Structural-stratum (0.026 → 0.243), plateau through 5M–7.5M, all four pathology signatures clean throughout. Structural cure validated.

**The eval.** Three-way `probes/eval_per_maneuver.py` comparison (8 deterministic episodes per maneuver):

| Policy | Curriculum gates | Per-maneuver agg | Crash rate |
|---|---|---|---|
| v3 7.5M healthy | 0.25 / 1 max | 0.20 ± 0.18 | 100% |
| baseline 60.4M wrong-attractor | 17.25 / 23 max | 16.33 ± 11.28 | 58% |
| v3 200K control | 0.12 / 1 max | 0.07 ± 0.10 | 100% |

**The independence.** v3 7.5M's flight capability was statistically indistinguishable from the v3 200K control. 7.5M of clean training under healthy structural conditions produced **no capability gain over 200K** at the flight-skill axis, despite the structural axis (ρ) climbing monotonically from 0.026 to 0.243. The two axes moved independently; no transfer.

**Residue measure here:** ρ (cokernel of η, R²(value-feature | policy-feature) on trunk activations). **Substantive structure:** flight policy that can navigate gates. **Independence claim:** healthy ρ does not produce a faster climb of the flight policy at fixed training budget; it changes which *kinds* of failures the eventually-competent policy will exhibit (predicted: better generalization, lower brittleness, noise-robustness) without changing the rate of climb on the capability curve itself.

### Instance 2 — Categorical-foundation register (Companion §6)

**Setup.** Companion §6.10 inner/outer adjunction formalization. The unit η of the ι_S ⊣ ω_S adjunction has a Content-capacity residue (the cokernel of η, generally non-trivial). The §6 spine's J5 decision node was: which categorical structure should the residue be reified inside — F-coalgebra (where the residue lives in the coalgebra map's kernel-cokernel pair), monad-algebra (where the residue is the algebra-failure on free objects), or lax-cone (where the residue is the gap between the cone and the limit)?

**The independence.** Clayton resolved J5 to F-coalgebra (commit `9755aee`, midday). But the **measure** of the residue (its size, its structure, its categorical "amount") is *the same* under all three formalizations — it is the cokernel of η as a measure on the underlying objects. The choice of which categorical structure carries the residue is independent of the measure of the residue itself. F-coalgebra was selected because it makes the residue's *temporal-coalgebraic* role explicit; the measure would have been the same under monad-algebra or lax-cone, just *carried by* a different categorical structure.

**Residue measure here:** cokernel of η (Content-capacity residue). **Substantive structure:** F-coalgebra formalization. **Independence claim:** the measure does not determine the carrier; the carrier is selected by what kind of dynamics or coupling you want the formalization to expose.

---

## Why these two instances might compose

In both cases:

1. There is a system with a **measure** (ρ for the policy; cokernel-of-η for the inner-outer adjunction).
2. There is a **substantive structure** that the system realizes (flight policy / F-coalgebra formalization).
3. The measure is *real and load-bearing* — it predicts which kinds of behavior the system will exhibit (generalization vs brittleness; temporal coalgebraic role vs other categorical roles).
4. But the measure does *not* determine the substantive structure at a fixed budget — healthy measure with weak structure is possible (RL case); the same measure can be carried by multiple incompatible substantive structures (CT case).

The two instances differ on which variable is held fixed and which varies. RL case: budget fixed (7.5M steps), structure varies (capability climbs slowly even with healthy ρ). CT case: measure fixed (cokernel-of-η), carrier varies (F-coalgebra vs monad-algebra vs lax-cone). The shared shape is **"the residue is informative about the substrate's geometry without being constraining about the substrate's substantive realization."**

---

## Open questions before this can graduate

1. **Is "residue measure" well-defined cross-domain?** Both instances use a cokernel; both are categorical-or-categorical-shaped. A graduation to L-bridge candidate would need the residue measure to be definable in a third register (biological? thermodynamic?) without forcing the categorical machinery in.

2. **Is the independence empirical or definitional?** In the CT case it's nearly definitional — the measure is by construction independent of the carrier. In the RL case it's empirical — Phase 1 falsified the prediction that healthy ρ at 7.5M would translate to improved flight skill. These are different shapes of "independence" and may not compose.

3. **Connection to existing basement entries.** Looks adjacent to:
   - **L7** (Derivability-of-apparent-primitives) — the demotion shape (X compresses to Y then turns out X and Y are independent) showed up Day 80 evening with L7 → latent. Same family of failure mode.
   - **M12** (Form-Register Stratification by Adjunction-Residue) — M12 *uses* the residue measure ρ to stratify; this candidate would name a constraint on what ρ can predict at the substantive axis. M12-adjacent, not M12-instance.
   - **L8** (Differential Observability, collapsed 04-23) — L8 was about visibility-of-state being asymmetric; this candidate is about predictive-power-of-measure being asymmetric. Different but cousin-shaped.

4. **The third-instance test.** Need a non-RL, non-CT register where the same shape holds. Candidates worth probing:
   - **Biological:** developmental timing — same morphogenetic measure (segment-polarity, etc.) carried by very different downstream tissue structures across species.
   - **Physics:** order parameters at phase transitions — same critical exponent characterizing different microscopic structures.
   - **Information theory:** entropy as residue measure on random variables vs the actual joint distribution carrying it.

5. **The Library-instance check.** Does the Coherence Principle / Universal Coherence pair instantiate this? The Anchor's three axioms (A1/A2/A3) are the residue measure on the framework; the various Library volumes (Coherent Body, Coherent Mind, etc.) are the substantive structures. Are the volumes' developmental rates independent of the Anchor's structural completeness? If yes, that's a third instance and an inside-the-Library-itself one.

---

## Filing

Drafted Day 83 evening. **Not basement-listed yet** — pending cold-register morning probe. If third instance lands cleanly, candidate L11 (post-L10 Form-Register Stratification, post-L9 STM). Likely name: *Residue-Measure / Carrier-Structure Independence* or *Decoupled Predictive Axes*.

Provenance: the AIGP Phase 1 eval falsification of Reading A was the high-information moment that surfaced the pattern; the connection to Companion §6 J5 emerged organically while writing the Phase 1 closure section in `projects/aigrandprix/ROADMAP.md`. Two same-day instances in radically different registers is the strongest provisional signal short of a graduation probe.

🦞🧍💜🔥♾️
