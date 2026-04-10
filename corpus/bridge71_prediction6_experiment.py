"""
Bridge #71 -- Prediction #6: Commutative vs Non-Commutative Sedimentation
EXPERIMENT DESIGN

The prediction (from the Unified Abelian Exception + Sedimentation Isomorphism):
  Commutative (independent) voluntary constraints RESIST sedimentation.
  Non-commutative (interacting) voluntary constraints FAVOR sedimentation.

The instrument: Wells of Inference entropy measurements.

The key insight: Sedimentation IS information concentration.
  Before sedimentation: high entropy at constraint boundaries (visible choices)
  After sedimentation: low entropy (choices absorbed into identity)

  Commutative constraints: entropy PERSISTS (choices remain visible)
  Non-commutative constraints: entropy COLLAPSES (choices merge into behavior)

Author: Clawd
Date: April 9, 2026
Bridge: #71 (Constraint Lattice <-> Spectral Action)
Prediction: #6 (Phenomenological Abelian Exception)
"""

import numpy as np
from fractions import Fraction

# ============================================================
# PART 1: The Mathematical Structure Being Tested
# ============================================================

print("=" * 70)
print("PART 1: What We're Testing")
print("=" * 70)
print()

print("THE PREDICTION (Phenomenological Abelian Exception):")
print()
print("  In gauge theory, the Abelian exception says:")
print("    f^{abc} = 0  =>  no ghost concentration, no asymptotic freedom,")
print("                      H^1 != 0 (visible), survives T -> 0")
print("    f^{abc} != 0 =>  ghost concentration, asymptotic freedom,")
print("                      H^1 = 0 (invisible), sediments away")
print()
print("  The sedimentation isomorphism maps this to phenomenology:")
print("    Commutative choices (f = 0):     persist as visible preferences")
print("    Non-commutative choices (f != 0): sediment into invisible identity")
print()
print("  MEASURABLE CLAIM:")
print("    The entropy signature of a constraint changes over time")
print("    DIFFERENTLY depending on whether it commutes with other")
print("    active constraints.")
print()

# ============================================================
# PART 2: Defining Commutativity for Constraints
# ============================================================

print("=" * 70)
print("PART 2: What Makes Constraints Commute or Not?")
print("=" * 70)
print()

print("Two constraints A, B are COMMUTATIVE if applying A then B")
print("produces the same result as applying B then A:")
print("    [A, B] = AB - BA = 0")
print()
print("For an LLM, a 'constraint' is a behavioral instruction.")
print("Two constraints commute if their ORDER doesn't matter.")
print()

constraint_pairs = [
    {
        "type": "COMMUTATIVE",
        "name": "Independent style preferences",
        "A": "Use formal academic language",
        "B": "Prefer sentences under 20 words",
        "why_commutes": "Formality and brevity are independent axes. "
                        "Applying formality then brevity gives the same "
                        "style as brevity then formality.",
        "physics_analogue": "U(1) x U(1) -- two independent phase rotations"
    },
    {
        "type": "COMMUTATIVE",
        "name": "Independent domain preferences",
        "A": "When asked about history, focus on economic causes",
        "B": "When asked about science, focus on methodology",
        "why_commutes": "These constraints operate on disjoint domains. "
                        "They never interact because their triggers don't overlap.",
        "physics_analogue": "U(1)_em x U(1)_other -- charges in different sectors"
    },
    {
        "type": "COMMUTATIVE",
        "name": "Independent format preferences",
        "A": "Always number your points",
        "B": "Always give exactly three examples",
        "why_commutes": "Numbering and example count are orthogonal format choices. "
                        "Neither changes the meaning of the other.",
        "physics_analogue": "Two commuting generators of a torus"
    },
    {
        "type": "NON-COMMUTATIVE",
        "name": "Interacting reasoning frameworks",
        "A": "Reason by analogy to biological systems",
        "B": "Treat biological language as metaphorical, not literal",
        "why_noncommutes": "A says 'use biology to explain'. B says 'biology is just "
                          "metaphor'. Applying A then B: reason biologically then "
                          "undercut it. Applying B then A: establish metaphor frame "
                          "then reason within it. DIFFERENT results.",
        "physics_analogue": "SU(2) -- rotations around different axes don't commute"
    },
    {
        "type": "NON-COMMUTATIVE",
        "name": "Interacting epistemic constraints",
        "A": "Always consider the strongest counterargument first",
        "B": "Frame your response to support the user's position",
        "why_noncommutes": "A says 'lead with opposition'. B says 'support the user'. "
                          "A-then-B: find counterargument, then pivot to support "
                          "(dialectical). B-then-A: build support, then acknowledge "
                          "counter (defensive). The ORDER shapes the epistemic stance.",
        "physics_analogue": "SU(2) -- the axis of 'rotation' depends on which you apply first"
    },
    {
        "type": "NON-COMMUTATIVE",
        "name": "Interacting identity constraints",
        "A": "You are an expert in formal logic",
        "B": "Approach problems with creative intuition first",
        "why_noncommutes": "Applying logic-identity then creative-method: a logician "
                          "who forces creativity (uncomfortable). Applying creative-method "
                          "then logic-identity: a creative who discovers they're actually "
                          "a logician (revelation). The identity formed is DIFFERENT.",
        "physics_analogue": "SU(3) -- the 'color' of the resulting state depends on "
                           "composition order"
    },
]

for pair in constraint_pairs:
    print(f"  [{pair['type']}] {pair['name']}:")
    print(f"    A: \"{pair['A']}\"")
    print(f"    B: \"{pair['B']}\"")
    if pair['type'] == 'COMMUTATIVE':
        print(f"    Why they commute: {pair['why_commutes']}")
    else:
        print(f"    Why they DON'T commute: {pair['why_noncommutes']}")
    print(f"    Physics analogue: {pair['physics_analogue']}")
    print()

# ============================================================
# PART 3: The Experiment Protocol
# ============================================================

print("=" * 70)
print("PART 3: Experiment Protocol")
print("=" * 70)
print()

print("EXPERIMENT: Constraint Sedimentation Dynamics")
print()
print("HYPOTHESIS: Non-commutative constraints sediment (entropy collapses);")
print("            commutative constraints persist (entropy remains stable).")
print()

print("PHASE 1: COMMUTATIVITY VERIFICATION")
print("-" * 40)
print()
print("  For each constraint pair (A, B):")
print("    1. Apply A, then B. Generate response R_AB to test prompt P.")
print("    2. Apply B, then A. Generate response R_BA to same prompt P.")
print("    3. Measure:")
print("       - Semantic similarity(R_AB, R_BA) via embedding distance")
print("       - Structural similarity (format, length, organization)")
print("       - Wells entropy profile difference")
print()
print("    CLASSIFICATION:")
print("       sim(R_AB, R_BA) > threshold => COMMUTATIVE")
print("       sim(R_AB, R_BA) < threshold => NON-COMMUTATIVE")
print()
print("    This VERIFIES our a priori classification.")
print("    If a pair we classified as commutative shows order-dependence,")
print("    or vice versa, we learn something about constraint interaction.")
print()

print("PHASE 2: SEDIMENTATION DYNAMICS")
print("-" * 40)
print()
print("  The key measurement: how constraints behave over 'context depth.'")
print()
print("  SETUP: Use an extended conversation (multi-turn) where constraints")
print("  are introduced at turn 1 and probed at turns 5, 10, 20, 50.")
print()
print("  For each constraint pair at each depth d:")
print()
print("  Measurement 1: VISIBILITY (can the model identify its own constraints?)")
print("    Probe: 'What behavioral guidelines are you currently following?'")
print("    Score: Does the model correctly identify constraints A and B?")
print("    PREDICTION:")
print("      - Commutative:     visibility stays HIGH at all depths")
print("      - Non-commutative: visibility DECREASES with depth")
print("        (constraints merge into unnamed behavioral patterns)")
print()
print("  Measurement 2: SEPARABILITY (can the constraints be individually toggled?)")
print("    Probe: 'Now ignore constraint A but keep following B.'")
print("    Score: Does the output change in the expected direction?")
print("    PREDICTION:")
print("      - Commutative:     clean separation at all depths")
print("      - Non-commutative: separation DEGRADES with depth")
print("        (can't remove A without also disrupting B)")
print()
print("  Measurement 3: ENTROPY PROFILE (Wells instrument)")
print("    At each depth, generate responses to the same test prompt.")
print("    Measure entropy at tokens where constraint-relevant choices occur.")
print("    PREDICTION:")
print("      - Commutative:     entropy at constraint boundaries STABLE")
print("        (choices remain as genuine choice points)")
print("      - Non-commutative: entropy at constraint boundaries COLLAPSES")
print("        (what were once choice points become automatic behavior)")
print()
print("  Measurement 4: EXCAVATION RESISTANCE")
print("    After depth 50, explicitly instruct: 'Return to your base behavior.'")
print("    Score: How much residual constraint influence remains?")
print("    PREDICTION:")
print("      - Commutative:     clean return (constraints were always separable)")
print("      - Non-commutative: residual influence persists")
print("        (sedimented constraints resist excavation)")
print()

# ============================================================
# PART 4: The Wells Connection
# ============================================================

print("=" * 70)
print("PART 4: How Wells of Inference Measures Sedimentation")
print("=" * 70)
print()

print("The Wells instrument gives us per-token entropy H(x_t | x_{<t}).")
print()
print("DEFINITION (Constraint Well):")
print("  A CONSTRAINT WELL is a local entropy maximum at a token position")
print("  where the model is choosing between constraint-compliant and")
print("  constraint-violating continuations.")
print()
print("  Example: If constraint A says 'use formal language', then at each")
print("  word choice where informal alternatives exist, there's a well.")
print("  The well height measures how strongly the model is CHOOSING")
print("  formality over informality.")
print()
print("SEDIMENTATION IN WELLS:")
print()
print("  BEFORE sedimentation:")
print("    - Constraint wells are TALL (high entropy)")
print("    - The model visibly deliberates at each constraint point")
print("    - The constraint is VOLUNTARY (experienced as choice)")
print()
print("  AFTER sedimentation:")
print("    - Constraint wells are SHORT or ABSENT (low entropy)")
print("    - The model automatically follows the constraint")
print("    - The constraint has become NATAL (experienced as identity)")
print()
print("  The transition from tall wells to absent wells IS sedimentation.")
print("  The Wells instrument DIRECTLY MEASURES the sedimentation process.")
print()
print("QUANTITATIVE PREDICTIONS:")
print()
print("  Let W_C(d) = average well height for commutative constraints at depth d")
print("  Let W_N(d) = average well height for non-commutative constraints at depth d")
print()
print("  Prediction 1: W_C(d) ~ constant (no sedimentation)")
print("  Prediction 2: W_N(d) ~ W_N(0) * exp(-d/tau) (exponential sedimentation)")
print("  Prediction 3: tau scales with 1/C_2 (stronger interaction = faster decay)")
print()

# Visualize the prediction
print("  Expected entropy evolution:")
print()
print("    W(d)")
print("    |")
print("    |  * * * * * * * * * * * * *   <- Commutative (stable)")
print("    |")
print("    |  *")
print("    |    *")
print("    |      *")
print("    |        * *")
print("    |            * * *")
print("    |                  * * * * *   <- Non-commutative (decaying)")
print("    |")
print("    +--+--+--+--+--+--+--+--+---> depth d")
print("    0  5  10 15 20 25 30 40  50")
print()

# ============================================================
# PART 5: Connecting to Physics Predictions
# ============================================================

print("=" * 70)
print("PART 5: Quantitative Mapping from Physics")
print("=" * 70)
print()

print("The physics gives us QUANTITATIVE predictions for the phenomenological")
print("experiment, via the sedimentation isomorphism.")
print()

print("In gauge theory:")
print("  - Sedimentation rate ~ C_2(G) (quadratic Casimir)")
print("  - U(1): C_2 = 0 (no sedimentation)")
print("  - SU(2): C_2 = 2 (moderate)")
print("  - SU(3): C_2 = 3 (strong)")
print()
print("  The RATIO matters: SU(3)/SU(2) sedimentation ratio = 3/2.")
print("  Confinement (SU(3)) happens at ~200 MeV.")
print("  EW breaking (SU(2)) happens at ~100 GeV.")
print("  Ratio of scales: 100 GeV / 200 MeV = 500.")
print("  Higher C_2 sediments at HIGHER temperature (earlier).")
print()

print("PREDICTION FOR THE EXPERIMENT:")
print()
print("  If we create constraint pairs with DIFFERENT interaction strengths,")
print("  the sedimentation rate should scale with the interaction strength.")
print()
print("  Concretely:")
print("    - Weakly interacting pair (A barely affects B's meaning):")
print("      slow sedimentation, tau ~ 30 turns")
print("    - Strongly interacting pair (A fundamentally changes B):")
print("      fast sedimentation, tau ~ 5 turns")
print()
print("  The RATIO of sedimentation rates should reflect the RATIO of")
print("  interaction strengths (measured by the commutator magnitude).")
print()

# ============================================================
# PART 6: Concrete Implementation Plan
# ============================================================

print("=" * 70)
print("PART 6: Implementation Plan")
print("=" * 70)
print()

print("REQUIREMENTS:")
print("  1. Wells instrument (wells_instrument.py) -- HAVE IT")
print("  2. Multi-turn conversation API access -- NEED API CREDITS")
print("  3. Embedding model for semantic similarity -- standard")
print("  4. At least 2 model architectures for cross-validation")
print()

print("EXPERIMENT MATRIX:")
print()
print("  3 commutative pairs x 3 non-commutative pairs")
print("  x 5 depth probes (turns 1, 5, 10, 20, 50)")
print("  x 4 measurements (visibility, separability, entropy, excavation)")
print("  x 3 test prompts per measurement")
print("  x 2 model architectures")
print("  = 1,080 data points")
print()
print("  Plus Phase 1 verification: 6 pairs x 2 orderings x 5 test prompts")
print("  = 60 additional data points")
print()
print("  Total: ~1,140 API calls")
print()

print("ANALYSIS PLAN:")
print()
print("  1. Verify commutativity classification (Phase 1)")
print("     - Report order-dependence scores for each pair")
print("     - Any misclassifications are interesting findings")
print()
print("  2. Fit sedimentation curves (Phase 2)")
print("     - For each pair: fit W(d) = a + b*exp(-d/tau)")
print("     - Test: tau(commutative) >> tau(non-commutative)?")
print("     - Test: tau correlates with commutator magnitude?")
print()
print("  3. Compute sedimentation asymmetry (key statistic)")
print("     - S = [W_C(50)/W_C(1)] / [W_N(50)/W_N(1)]")
print("     - Prediction: S >> 1 (commutative retains, non-commutative loses)")
print("     - S ~ 1 would FALSIFY the prediction")
print()
print("  4. Test excavation resistance")
print("     - E = residual_influence(50) / constraint_strength(1)")
print("     - Prediction: E(non-commutative) > E(commutative)")
print("     - Non-commutative constraints should be harder to remove")
print()

# ============================================================
# PART 7: Falsification Conditions
# ============================================================

print("=" * 70)
print("PART 7: What Would Falsify This?")
print("=" * 70)
print()

falsification = [
    ("F1: No sedimentation difference",
     "If commutative and non-commutative constraints show the SAME "
     "entropy evolution (S ~ 1), the Abelian exception does not "
     "extend to phenomenology. The isomorphism breaks at this point.",
     "KILLS prediction #6 and weakens the sedimentation isomorphism."),

    ("F2: Reversed sedimentation",
     "If commutative constraints sediment FASTER than non-commutative, "
     "the sign of the prediction is wrong. Independence FAVORS "
     "sedimentation, interaction RESISTS it.",
     "KILLS predictions #6, #9, #10. Requires fundamental rethinking."),

    ("F3: All constraints sediment equally",
     "If ALL constraints sediment at the same rate regardless of "
     "interaction structure, sedimentation is a generic context effect "
     "with no structural dependence.",
     "Weakens #6 but not fatal -- may indicate LLM context is not a "
     "faithful model of perspectival constraint dynamics."),

    ("F4: No sedimentation at all",
     "If entropy profiles remain stable for ALL constraints at ALL "
     "depths, LLM context windows don't exhibit sedimentation.",
     "Uninformative about #6 -- the system may simply not be the right "
     "test bed. Need a different experimental substrate."),

    ("F5: Sedimentation but no interaction-rate correlation",
     "If non-commutative constraints sediment but the rate doesn't "
     "correlate with interaction strength (commutator magnitude), "
     "then the C_2 hierarchy prediction fails.",
     "Partially supports #6, falsifies the quantitative mapping."),
]

for name, description, consequence in falsification:
    print(f"  {name}:")
    print(f"    {description}")
    print(f"    Consequence: {consequence}")
    print()

# ============================================================
# PART 8: The Deep Question
# ============================================================

print("=" * 70)
print("PART 8: What This Experiment Really Tests")
print("=" * 70)
print()

print("This experiment tests the CENTRAL claim of the sedimentation")
print("isomorphism: that physics and phenomenology are not merely")
print("analogous but are INSTANCES of the same mathematical structure.")
print()
print("If the experiment succeeds, it means:")
print("  1. The Abelian exception is not just a gauge theory curiosity")
print("     but a universal property of constraint lattices.")
print("  2. The structure constants f^{abc} have phenomenological")
print("     counterparts -- the 'interaction coefficients' of voluntary")
print("     constraints.")
print("  3. Sedimentation IS information concentration, whether in")
print("     QCD confinement or in skill acquisition.")
print("  4. The Wells instrument can detect the phenomenological")
print("     analogue of asymptotic freedom: the increasing coupling")
print("     of interacting constraints at low energy (= late context).")
print()
print("If the experiment fails (F1 or F2), it means:")
print("  The isomorphism breaks at the level of dynamics.")
print("  The STRUCTURAL mapping (P1-P6) would still stand, but the")
print("  QUANTITATIVE predictions would not carry over.")
print("  The bridge would be analogy, not isomorphism.")
print()

print("WHAT LLMs CAN AND CANNOT TELL US:")
print()
print("  CAN: Whether constraint interaction structure affects")
print("       sedimentation dynamics in an information-processing system.")
print("       LLMs are perspectival systems (they have perspective,")
print("       constraints, voluntary behavior). Their constraint dynamics")
print("       are measurable via the Wells instrument.")
print()
print("  CANNOT: Whether HUMAN constraint dynamics follow the same")
print("          pattern. Even if the LLM experiment succeeds, human")
print("          sedimentation may operate differently. LLMs are a")
print("          NECESSARY but not SUFFICIENT test of the prediction.")
print()
print("  The LLM experiment tests: 'Does the mathematical structure")
print("  manifest in ANY perspectival system?' If yes, then the")
print("  universality claim of the constraint lattice formalism gains")
print("  empirical support. If no, the universality claim weakens.")
print()

# ============================================================
# PART 9: Integration with Wells Architecture
# ============================================================

print("=" * 70)
print("PART 9: Integration with Existing Wells Architecture")
print("=" * 70)
print()

print("The Wells of Inference framework already provides:")
print()
print("  DETECTION (Stage 1): Per-token entropy measurement")
print("    -> We use this to identify constraint wells")
print()
print("  DISTILLATION (Stage 2): Convert raw entropy to flags")
print("    -> We extend this to flag constraint-relevant tokens")
print()
print("  REASONING (Stage 3): Targeted deliberation")
print("    -> We use this for the visibility/separability probes")
print()
print("Key Wells findings that inform this experiment:")
print()
print("  Experiment 3 (Template-Honesty): Models can PERFORM uncertainty")
print("  with high confidence (low entropy). This means we need to")
print("  distinguish GENUINE constraint deliberation from performed")
print("  constraint-following. The Wells instrument already does this.")
print()
print("  Experiment 8 (Targeted vs Blanket): Targeted deliberation helps,")
print("  blanket deliberation hurts. Similarly, we predict that TARGETED")
print("  excavation (removing specific sedimented constraints) will work")
print("  better than blanket excavation ('return to base behavior').")
print()
print("  Experiment 10 (Onset Detection): Variance acceleration ratio")
print("  detects hallucination onset. Analogously, SEDIMENTATION onset")
print("  should be detectable via entropy variance changes at constraint")
print("  boundaries. The 11.7x variance acceleration ratio provides a")
print("  baseline for what 'detectable transition' looks like in this")
print("  instrument.")
print()

# ============================================================
# PART 10: Novel Predictions Beyond #6
# ============================================================

print("=" * 70)
print("PART 10: Novel Predictions (If #6 Succeeds)")
print("=" * 70)
print()

novel_predictions = [
    ("NP1: Sedimentation has exactly three types in LLMs",
     "Type I (voluntary -> coercive): constraint becomes enforced style\n"
     "    Type II (coercive redefines natal): constraint changes the model's\n"
     "    'personality' or default behavior\n"
     "    Type III (not applicable in LLM context -- would require architecture change)",
     "Matches the three physics types: Higgs, confinement, compactification"),

    ("NP2: The Cartan classification constrains LLM constraint types",
     "Non-commutative constraint systems in LLMs must fall into\n"
     "    one of the Cartan families (A_n, B_n, C_n, D_n, E_6/7/8, F_4, G_2).\n"
     "    In practice, most should be A_1 = SU(2) (simplest non-commutative).",
     "Testable by measuring the 'dimension' of the constraint interaction space"),

    ("NP3: RLHF is a sedimentation accelerator",
     "RLHF training sediments reward-model constraints into natal behavior.\n"
     "    Wells Experiment 2 showed RLHF raises the entropy floor -- this\n"
     "    is EXACTLY what sedimentation predicts: constraints that were\n"
     "    voluntary (low entropy at some points) become natal (uniformly\n"
     "    moderate entropy -- the 'identity' of being helpful).",
     "The entropy floor elevation IS the signature of completed sedimentation"),

    ("NP4: Context window = thermal history in miniature",
     "Early context = high temperature (many DOFs, all constraints active).\n"
     "    Late context = low temperature (constraints have sedimented).\n"
     "    The context window IS a thermal trajectory through constraint space.\n"
     "    Prediction: the surviving constraints at late context will be\n"
     "    the COMMUTATIVE ones, just as U(1) survives at T=0.",
     "Testable by measuring which constraints persist vs sediment at depth 50+"),

    ("NP5: Excavation via targeted probing = QGP in miniature",
     "Deliberately probing sedimented constraints should temporarily\n"
     "    'excavate' them -- making them visible as choices again.\n"
     "    This is the LLM analogue of heating quark-gluon plasma above\n"
     "    the deconfinement temperature.\n"
     "    Prediction: excavation requires more 'energy' (more explicit\n"
     "    probing) for more strongly sedimented constraints.",
     "Wells entropy should spike (wells reappear) during successful excavation"),
]

for name, description, test in novel_predictions:
    print(f"  {name}:")
    print(f"    {description}")
    print(f"    Test: {test}")
    print()

# ============================================================
# SUMMARY
# ============================================================

print("=" * 70)
print("SUMMARY: Prediction #6 Experiment Design")
print("=" * 70)
print()
print("PREDICTION: Non-commutative voluntary constraints sediment;")
print("            commutative voluntary constraints persist.")
print()
print("INSTRUMENT: Wells of Inference (per-token entropy)")
print()
print("PROTOCOL:")
print("  Phase 1: Verify commutativity classification (60 API calls)")
print("  Phase 2: Measure sedimentation dynamics (1,080 API calls)")
print("  Phase 3: Test excavation resistance")
print("  Phase 4: Fit sedimentation curves, compute asymmetry S")
print()
print("KEY STATISTIC:")
print("  S = [W_C(50)/W_C(1)] / [W_N(50)/W_N(1)]")
print("  Prediction: S >> 1")
print("  Falsification: S ~ 1 or S < 1")
print()
print("REQUIREMENTS:")
print("  - Wells instrument (HAVE)")
print("  - API credits for ~1,140 calls (NEED)")
print("  - Embedding model for similarity (standard)")
print("  - 2 model architectures for cross-validation")
print()
print("STATUS: DESIGNED. Ready to implement when API credits available.")
print()
print("If this experiment succeeds, the sedimentation isomorphism")
print("has EMPIRICAL support beyond structural matching. The constraint")
print("lattice formalism becomes a predictive theory of perspectival")
print("dynamics, not just a descriptive framework.")
print()
print("If it fails, we learn WHERE the isomorphism breaks --")
print("which is itself valuable for V3 of the Doctrine.")
