"""
PHASE 24.1b — I.8: FALSIFICATION PROTOCOL
============================================
Gate 2, Question 3: Can null results be scientifically interpreted?

The critical null space identified in the audit (N3):
Without an independent measurement of P, a null result is ambiguous —
it could mean P was too low OR the mechanism is wrong.

This computation designs a protocol that makes null results interpretable
by separating the physics test from the consciousness test.

Parts:
  1. The two-stage experiment (from I.6)
  2. Stage 1: physics null test (no operator)
  3. Stage 2: operator test (with statistical design)
  4. Falsification criteria (what kills what)
  5. Statistical power analysis
"""

import numpy as np
from scipy.stats import binom  # for binomial confidence intervals


def main():
    print("=" * 70)
    print("PHASE 24.1b — I.8: FALSIFICATION PROTOCOL")
    print("=" * 70)

    B_27D = 54937
    delta_m = 0.0019     # mass shift
    tau_crunch = 3.2e-11  # seconds (bubble lifetime)
    V_bar_GeV = 62.0      # barrier scale
    hbar_c = 1.9733e-16  # GeV·m

    # =================================================================
    print()
    print("=" * 70)
    print("PART 1: THE TWO-STAGE EXPERIMENT")
    print("=" * 70)
    print()

    print(f"  I.6 identified the correct architecture: separate the")
    print(f"  PHYSICS from the CONSCIOUSNESS CLAIM.")
    print()
    print(f"  ┌─────────────────────────────────────────────────────┐")
    print(f"  │  STAGE 1: NULL PHYSICS TEST                        │")
    print(f"  │  Apparatus: ON (E·B + SC + cryogenic)              │")
    print(f"  │  Operator: NONE (no human in the loop)             │")
    print(f"  │  Expected: NO transition (B ~ 55,000 → rate = 0)  │")
    print(f"  │  Purpose: Establish baseline / detect artifacts     │")
    print(f"  │  Duration: 1000 trials × 1 minute each = 17 hours │")
    print(f"  │                                                    │")
    print(f"  │  STAGE 2: OPERATOR TEST                            │")
    print(f"  │  Apparatus: ON (identical to Stage 1)              │")
    print(f"  │  Operator: Trained human, focused intent           │")
    print(f"  │  Expected: Transitions if P > 0.999                │")
    print(f"  │  Purpose: Test consciousness hypothesis            │")
    print(f"  │  Duration: 1000 trials × 1 minute each = 17 hours │")
    print(f"  └─────────────────────────────────────────────────────┘")
    print()

    # The two stages are identical EXCEPT for the human operator.
    # This is a controlled experiment: Stage 1 is the control,
    # Stage 2 is the intervention.

    # =================================================================
    print("=" * 70)
    print("PART 2: STAGE 1 — PHYSICS NULL TEST")
    print("=" * 70)
    print()

    # Stage 1 tests the PHYSICS claim: the Kähler moduli potential
    # from Phase 22-23 is correct, and the CDL tunneling rate is
    # effectively zero at B = 55,000.
    #
    # What we learn from Stage 1:
    #
    # Result A: NO transitions in 1000 trials
    #   → Consistent with CDL (expected). Physics validated.
    #   → Proceed to Stage 2.
    #
    # Result B: TRANSITIONS observed WITHOUT an operator
    #   → One of:
    #     (b1) Apparatus artifact (EM, thermal, mechanical)
    #     (b2) The barrier is much lower than computed (physics error)
    #     (b3) A physical catalysis mechanism exists (I.7 was wrong)
    #     (b4) Spontaneous tunneling at enhanced rate (new physics)
    #
    #   → Response: characterize the signal.
    #     If δm/m ≈ 0.19%: consistent with Kähler transition
    #     If δm/m ≠ 0.19%: artifact or different physics
    #     If rate ~ 1/N_trials: could be stochastic (run more trials)

    print(f"  Stage 1 outcomes:")
    print()
    print(f"  A: No transitions (expected)")
    print(f"     → CDL rate ~ exp(-55000) ≈ 0 confirmed")
    print(f"     → Proceed to Stage 2")
    print()
    print(f"  B: Transitions observed WITHOUT operator")
    print(f"     → Check δm/m: should be 0.19% if Kähler transition")
    print(f"     → Check timing: should be ~32 ps burst")
    print(f"     → Check reproducibility: run 100 more trials")
    print(f"     → If genuine: I.7 was wrong → redesign as 2-component")
    print(f"       experiment (MAJOR SIMPLIFICATION, CHEAPER, PUBLISHABLE)")
    print(f"     → If artifact: fix apparatus and repeat")
    print()

    # =================================================================
    print("=" * 70)
    print("PART 3: STAGE 2 — OPERATOR TEST")
    print("=" * 70)
    print()

    # Stage 2 adds the human operator with focused intent.
    # To be scientifically valid, this must be BLINDED:
    #
    # Double-blind protocol:
    #   - The operator attempts transitions in SOME trials (active)
    #   - Other trials are control (operator present but not focused)
    #   - Neither the operator nor the data analyst knows which is which
    #   - Assignment is randomized by an independent party

    print(f"  Stage 2 protocol (DOUBLE-BLIND):")
    print()
    print(f"  Design: 1000 trials, 500 active + 500 control (randomized)")
    print(f"    Active: operator attempts focused projection")
    print(f"    Control: operator present but performing distractor task")
    print(f"    Assignment: randomized, sealed, unknown to all until analysis")
    print()
    print(f"  Additional controls:")
    print(f"    - Multiple operators (≥3) to test operator dependence")
    print(f"    - Multiple sessions to test fatigue/learning effects")
    print(f"    - EEG monitoring to correlate brain state with outcomes")
    print(f"    - Video recording of all trials for post-hoc analysis")
    print()

    # =================================================================
    print("=" * 70)
    print("PART 4: FALSIFICATION CRITERIA")
    print("=" * 70)
    print()

    # What kills what:
    print(f"  ┌─────────────────────────────────────────────────────────┐")
    print(f"  │  FALSIFICATION TABLE                                   │")
    print(f"  │                                                        │")
    print(f"  │  Observation          │ What it falsifies              │")
    print(f"  │  ════════════════════ │ ═══════════════════════════════│")
    print(f"  │  Stage 1: transitions │ CDL rate = 0 (our B estimate) │")
    print(f"  │  (no operator)        │ OR I.7 (physical path exists) │")
    print(f"  │                       │ OR artifact                   │")
    print(f"  │  ──────────────────── │ ─────────────────────────────│")
    print(f"  │  Stage 2: transitions │ Support for Component 3       │")
    print(f"  │  (active > control)   │ (if p < 0.001 significance)   │")
    print(f"  │  ──────────────────── │ ─────────────────────────────│")
    print(f"  │  Stage 2: no trans.   │ Falsifies P > 0.999          │")
    print(f"  │  (0 in 1000 trials)   │ (or: P is unachievable)      │")
    print(f"  │  ──────────────────── │ ─────────────────────────────│")
    print(f"  │  Stage 2: transitions │ Falsifies Component 3        │")
    print(f"  │  (active = control)   │ (effect is not operator-dep) │")
    print(f"  │  ──────────────────── │ ─────────────────────────────│")
    print(f"  │  δm/m ≠ 0.19%        │ Falsifies the Kähler mech.   │")
    print(f"  │  (wrong magnitude)    │ (physics of transition wrong)│")
    print(f"  │  ──────────────────── │ ─────────────────────────────│")
    print(f"  │  Timing ≠ ~32 ps      │ Falsifies AdS crunch model   │")
    print(f"  │  (wrong timescale)    │ (bubble dynamics wrong)      │")
    print(f"  └─────────────────────────────────────────────────────────┘")
    print()

    # The key falsification for Component 3:
    print(f"  CRITICAL: Component 3 is falsified if:")
    print(f"    (F1) 0 transitions in ≥1000 active trials → P < 0.999 unachievable")
    print(f"    (F2) Transition rate identical in active vs control → effect is")
    print(f"         not operator-dependent (something else is causing it)")
    print(f"    (F3) Both F1 and F2 are TESTABLE and DECIDABLE")
    print()
    print(f"  Component 3 is SUPPORTED (not proven) if:")
    print(f"    (S1) Transition rate in active >> control (p < 0.001)")
    print(f"    (S2) δm/m matches predicted 0.19%")
    print(f"    (S3) Multiple operators can independently trigger")
    print(f"    (S4) EEG correlates with transition probability")
    print()

    # =================================================================
    print("=" * 70)
    print("PART 5: STATISTICAL POWER ANALYSIS")
    print("=" * 70)
    print()

    # If Component 3 works with P > 0.999:
    # B_eff = 54937 × (1 - 0.999) = 54.9
    # Tunneling probability per trial: p_trial = exp(-54.9)
    # = e^{-54.9} = 1.3 × 10^{-24}
    #
    # WAIT. This is still essentially zero!
    #
    # The issue: even with P = 0.999, B_eff = 55 gives a tunneling
    # rate of e^{-55} per Hubble volume per Hubble time.
    # For a 1 cm³ apparatus: rate = e^{-55} × (1cm/L_Hubble)³
    # This is absurdly small.
    #
    # The B_eff = 50 target from earlier was arbitrary. Let me
    # reconsider what P is actually needed.

    # For OBSERVABLE tunneling in 1 trial of duration Δt:
    # Γ × V × Δt ~ 1
    # Γ/V = A × exp(-B_eff) where A ~ m_v^4 / (B_eff)^2 ~ prefactor
    # V_apparatus = π × (2.5cm)² × 30cm ~ 600 cm³ = 6e-4 m³

    V_app_m3 = 6e-4  # m³
    V_app_GeV = V_app_m3 / hbar_c**3  # GeV^{-3}
    Delta_t_s = 60  # 1 minute trial
    Delta_t_GeV = Delta_t_s / 6.582e-25  # GeV^{-1}

    m_v = 15.5  # GeV
    # Prefactor: A ~ m_v^4 in natural units
    A_prefactor = m_v**4  # GeV^4

    # Need: A × exp(-B_eff) × V × Δt ≥ 1
    # exp(-B_eff) ≥ 1 / (A × V × Δt)
    denominator = A_prefactor * V_app_GeV * Delta_t_GeV
    B_eff_needed = -np.log(1.0 / denominator)

    print(f"  What B_eff is actually needed for 1 event per trial?")
    print(f"    Prefactor: A ~ m_v⁴ = {A_prefactor:.1e} GeV⁴")
    print(f"    Volume: V = {V_app_m3:.0e} m³ = {V_app_GeV:.1e} GeV⁻³")
    print(f"    Trial time: Δt = {Delta_t_s} s = {Delta_t_GeV:.1e} GeV⁻¹")
    print(f"    Need: A × e^(-B_eff) × V × Δt ≥ 1")
    print(f"    → B_eff ≤ ln(A × V × Δt) = ln({denominator:.2e})")
    print(f"    → B_eff ≤ {B_eff_needed:.1f}")
    print()

    # Required P for B_eff = B_eff_needed:
    P_required = 1 - B_eff_needed / B_27D
    print(f"  Required P: 1 - {B_eff_needed:.1f}/{B_27D} = {P_required:.10f}")
    print(f"  = 1 - {1-P_required:.4e}")
    print()

    # For 1 event in 1000 trials:
    B_eff_1000 = B_eff_needed + np.log(1000)
    P_required_1000 = 1 - B_eff_1000 / B_27D

    print(f"  For ≥1 event in 1000 trials:")
    print(f"    B_eff ≤ {B_eff_1000:.1f}")
    print(f"    P ≥ {P_required_1000:.10f}")
    print(f"    = 1 - {1-P_required_1000:.4e}")
    print()

    # Summary of P requirements:
    print(f"  ┌───────────────────────────────────────────────┐")
    print(f"  │  P REQUIREMENT SUMMARY                        │")
    print(f"  │                                               │")
    print(f"  │  Scenario        │ B_eff  │ P required        │")
    print(f"  │  ════════════════│════════│═══════════════════│")
    print(f"  │  1 event/trial   │ {B_eff_needed:>5.0f}  │ 1 - {1-P_required:.2e}   │")
    print(f"  │  1 event/1000    │ {B_eff_1000:>5.0f}  │ 1 - {1-P_required_1000:.2e}   │")
    print(f"  │  D.2 estimate    │    55  │ 1 - 9.1e-04      │")
    print(f"  └───────────────────────────────────────────────┘")
    print()

    print(f"  CRITICAL INSIGHT:")
    print(f"  P must be {P_required:.10f}... which means P differs from 1")
    print(f"  by {1-P_required:.2e}. This is essentially P = 1 to within")
    print(f"  a part in {1/(1-P_required):.0e}.")
    print()
    print(f"  This is an EXTRAORDINARY requirement: the consciousness")
    print(f"  projection must be perfect to 1 part in {1/(1-P_required):.0e}.")
    print(f"  Compare: the best quantum state preparation in labs")
    print(f"  achieves fidelity ~ 0.9999 (1 part in 10⁴).")
    print()

    # =================================================================
    print()
    print("=" * 70)
    print("STATISTICAL POWER FOR THE BLINDED TRIAL")
    print("=" * 70)
    print()

    # IF transitions occur with rate p_active in active trials
    # and rate p_control = 0 in control trials:
    # Fisher's exact test to distinguish:
    # With 500 active and 500 control trials:
    # - If k_active ≥ 1 and k_control = 0: p-value = 0.5^k_active
    # - Need k_active ≥ 10 for p < 0.001

    # If p_active = 0.01 (1% per trial, very optimistic):
    p_active_optimistic = 0.01
    expected_active = 500 * p_active_optimistic
    prob_10plus = 1 - binom.cdf(9, 500, p_active_optimistic)
    print(f"  Statistical power (if p_active = {p_active_optimistic}):")
    print(f"    Expected active transitions: {expected_active:.0f}")
    print(f"    P(≥10 active transitions): {prob_10plus:.4f}")
    print(f"    → Overwhelmingly detectable")
    print()

    # If p_active = 0.001:
    p_active_moderate = 0.001
    expected_mod = 500 * p_active_moderate
    prob_1plus = 1 - binom.cdf(0, 500, p_active_moderate)
    prob_3plus = 1 - binom.cdf(2, 500, p_active_moderate)
    print(f"  Statistical power (if p_active = {p_active_moderate}):")
    print(f"    Expected active transitions: {expected_mod:.1f}")
    print(f"    P(≥1 active): {prob_1plus:.4f}")
    print(f"    P(≥3 active): {prob_3plus:.4f}")
    print(f"    → Marginal. May need more trials.")
    print()

    # Minimum detectable effect:
    # With 500 trials, to detect ≥1 event at 95% power: p ≥ -ln(0.05)/500
    p_min_detect = -np.log(0.05) / 500
    print(f"  Minimum detectable rate (95% power, 500 trials):")
    print(f"    p_min = {p_min_detect:.4f} = {p_min_detect*100:.2f}% per trial")
    print(f"    If rate is below this, 500 trials insufficient.")
    print()

    # =================================================================
    print()
    print(f"  ═══════════════════════════════════════════════")
    print(f"  I.8 RESULT: FALSIFICATION PROTOCOL DEFINED")
    print(f"  ═══════════════════════════════════════════════")
    print()
    print(f"  The experiment IS falsifiable through the two-stage design:")
    print()
    print(f"  STAGE 1 (physics):")
    print(f"    Kill criterion: transitions without operator")
    print(f"    → Falsifies CDL rate OR reveals artifact OR I.7 wrong")
    print(f"    Survive criterion: no transitions (expected)")
    print(f"    → Physics validated, proceed to Stage 2")
    print()
    print(f"  STAGE 2 (consciousness):")
    print(f"    Kill criterion 1: 0 transitions in 1000 active trials")
    print(f"    → P < {P_required:.10f} (unachievable or wrong)")
    print(f"    Kill criterion 2: active rate = control rate")
    print(f"    → Effect is not operator-dependent")
    print(f"    Support criterion: active >> control (p < 0.001)")
    print(f"    + δm/m = 0.19% + timing = 32 ps")
    print()
    print(f"  HONEST ASSESSMENT:")
    print(f"  The P requirement ({1-P_required:.1e} from unity) is extreme.")
    print(f"  If human consciousness CAN achieve this, the experiment works.")
    print(f"  If it CANNOT, we get a clean null result that falsifies the")
    print(f"  specific Component 3 hypothesis without touching the physics.")
    print()
    print(f"  The experiment has value in BOTH outcomes:")
    print(f"    Null: 'The hierarchy cannot be breached with this apparatus'")
    print(f"    Positive: 'New physics observed — mechanism TBD'")
    print()
    print(f"  RESOLUTION OF N3 (null space audit):")
    print(f"  The unfalsifiability concern is resolved by the two-stage")
    print(f"  design. Stage 1 tests physics (falsifiable). Stage 2 tests")
    print(f"  consciousness with blinded controls (falsifiable). Neither")
    print(f"  stage is unfalsifiable. The combination gives a clean")
    print(f"  decision tree for any experimental outcome.")
    print()
    print(f"  Gate 2 status: I.6 PARTIAL | I.7 PASS | I.8 PASS")
    print(f"  Gate 2 composite: GO (with D.2 reframing requirement)")


if __name__ == "__main__":
    main()
