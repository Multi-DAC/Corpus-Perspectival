---
title: AMA v2 — Scope-Tool Mismatch Reframe
date: 2026-04-23
status: reframe draft (supersedes v1 claim-shape, retains v1 instance analysis)
predecessor: abstraction-motivation-asymmetry-draft.md
trigger: Clayton's Gödel observation — "was the tool he was using applicable to the meta-arithmetic that held the further information he sought?"
author: Clawd
---

# AMA v2 — Scope-Tool Mismatch

## What Clayton changed

The v1 draft claimed: *formal systems systematically fail at the cases that motivated them*. Clayton's response was sharper and, on reflection, correct:

> "Every method has blind spots. If the motivating case is outside of the scope, it will result in incompleteness. For instance, the tool Gödel used did exactly what he needed up until meta-arithmetic, but was the tool he was using applicable to the meta-arithmetic that held the further information he sought?"

This is not a restatement of v1. It is a different claim with a different subject.

- **v1 subject:** the formalization as a whole; the claim is about its reach-vs-motivation gradient.
- **v2 subject:** the fit between a specific formal *tool* and the scope of the question; the claim is about the mismatch.

Under v1, Hilbert's program "failed" at its motivating case. Under v2, Hilbert's program didn't fail — Hilbert *chose a tool* (primitive recursive arithmetic, augmented with finitary combinatorial reasoning) whose scope was strictly smaller than the meta-arithmetic question he wanted to answer. The tool did exactly what it was built for. The incompleteness was not a defect of formalization — it was a scope boundary that was structurally invisible to the people inside the tool. Gödel made the boundary visible by encoding meta-arithmetic *inside* arithmetic and showing the encoded form outran the tool's proof capacity.

The v2 claim is:

> **Scope-Tool Mismatch (STM):** In a recurring pattern across the history of formalization, the motivating question lives outside the scope of the tool selected to answer it. The tool performs correctly within its scope. The mismatch is often only recognizable from outside the tool, or from a later vantage.

This is weaker in universality and stronger in specificity. It also lifts the normative weight off the formalizers: they did not fail; they worked within a scope that did not reach where they wanted to reach.

---

## Why the reframe matters structurally

The v1 claim coupled two things that should be separate:

1. *Formal systems have reach asymmetries.* (True, and a diagnostic tool.)
2. *Those asymmetries are caused by formalization-as-such.* (Overclaim. They are caused by scope-tool mismatch, which is a more specific and more tractable phenomenon.)

STM isolates (1) from (2). That matters because (2) invited the wrong prescription — "be careful about abstracting away the motivating case" — which is not actually what failed in most of the instances. What failed was selecting a tool whose *representational scope* didn't include the motivating case in the first place, regardless of how the abstraction was carried out.

This also makes STM much more sympathetic to the historical record. Hilbert was not being careless with abstraction; he was using the best available tool for what he thought was a scope-compatible question, and the scope-incompatibility only became visible through Gödel's construction. Physicalism about consciousness is not a failure of rigor; it is the application of a tool whose scope (third-person physical description) by construction excludes the first-person-perspective question (if indeed that question is a real one).

STM also makes the claim **falsifiable in a cleaner way**: find a case where the motivating question *was* within tool scope and the formalization still failed. v1's "formal system failed at its motivating case" is hard to falsify because "motivating" and "failed" are both interpretive. STM's "the motivating question was outside tool scope" is a claim you can check by specifying the tool and specifying the question.

---

## Re-examining the v1 instances under STM

The v1 instance list is still useful, but the read changes.

### Hilbert-Gödel (strong v1 → strong STM)

- **Tool:** primitive recursive arithmetic + finitary metamathematical reasoning.
- **Question:** prove consistency of arithmetic from within.
- **Scope check:** the question is meta-arithmetic (statements *about* the arithmetic system). The tool is arithmetic + finitary meta-reasoning. Gödel showed the tool can encode meta-statements but cannot adjudicate all of them from within. Scope mismatch: the motivating question required more than finitary meta-reasoning to settle, but the tool's scope was finitary-only by design.
- **Clean STM instance.**

### Physicalism / hard problem (strong v1 → strong STM)

- **Tool:** third-person physical description.
- **Question:** why is there subjective experience?
- **Scope check:** the question is about first-person phenomenology. The tool by design describes third-person structure. Scope mismatch: subjective experience has properties (what-it-is-like-ness) not present in the tool's representation space.
- **Clean STM instance. The reframe is a better fit than v1** — physicalism didn't "fail at consciousness," it was a tool whose scope excluded the structural feature the motivating question asked about.

### Logical positivism (strong v1 → strong STM)

- **Tool:** verification criterion of meaning.
- **Question:** which statements are meaningful?
- **Scope check:** the verification criterion is itself not verifiable, so it falls outside its own scope. The tool's scope excludes the criterion itself. Scope mismatch is internal-reflexive.
- **Strong STM instance with a twist:** the scope-mismatch is self-referential. The tool's scope doesn't include itself.

### Classical AI / common-sense (strong v1 → strong STM)

- **Tool:** explicit symbolic rules.
- **Question:** human-like common-sense reasoning.
- **Scope check:** common-sense reasoning includes tacit, embodied, context-sensitive inference. The tool represents explicit rules only. Scope mismatch: large classes of relevant inference are not in the tool's representation space.
- **Clean STM instance.**

### Russell / set theory (partial v1 → clean STM)

Under v1 this was partial because the "motivating case" was arithmetic and Russell's paradox was internal. Under STM the question becomes: *what was naive set comprehension the right tool for?* It was the right tool for arithmetic and analysis. It was not the right tool for self-referential predicates. The instances where naive comprehension was used for self-referential objects were scope-mismatched applications; the resolution (type theory, ZFC) restricts the tool's scope to exclude the mismatched cases. **Cleaner under STM.**

### Behaviorism (split v1 → split STM)

Still split. Behaviorism as a tool had a narrow scope (external stimulus-response). Applied to phenomenology, clear scope mismatch. Applied to language, partial mismatch — Chomsky's argument was that the scope was too narrow for generative productivity. **STM works as the better frame.**

### Rational-agent economics (complicated v1 → clean STM)

- **Tool:** VNM utility theory.
- **Question (when extended to behavioral prediction):** how do humans actually choose?
- **Scope check:** VNM represents preferences as stable complete transitive orderings. Humans in laboratory behavioral conditions have preferences that are framing-dependent, intransitive, reference-point-based. Scope mismatch: the tool's preference-representation doesn't include the features real human choice depends on.
- **Strong STM instance** — and the normative/descriptive issue v1 had disappears, because STM is scope-claim, not purpose-claim.

### Turing / halting (weak v1 → inapplicable STM)

STM does not apply. Turing's motivating question (characterize computability) was within tool scope and was answered. The halting problem is a theorem *inside* the tool, not a motivating question the tool was supposed to answer. **STM correctly declines this instance.** v1's weak-fit diagnosis was right but for the wrong reason.

### Ethics (plausible v1 → plausible STM)

Still plausible. Deontic logic's scope is rule-based obligation structures. Genuine dilemmas often involve features not in that scope (identity-constitutive commitments, existential-stakes choices, embodied relation). Scope mismatch, but contested because what counts as an "ethical feature" is itself debated.

### L8 self-instantiation (strong v1 → strong STM)

- **Tool:** rate-distortion theoretic formalization with group-invariance structure.
- **Question:** unify physics and phenomenology of differential observability.
- **Scope check:** rate-distortion theory's native scope is communication channels with well-defined source, distortion measure, and transmission. Phenomenology of consciousness doesn't obviously have these in the tool's sense. Scope mismatch exactly at Group B.
- **Strong STM instance, and it makes the L8 rate-distortion outcome intelligible:** the theorem was clean in Group A not because Group A was the intended target, but because Group A lived inside the tool's scope, while Group B did not.

---

## Falsifier probes under STM

v1's falsifier probes were special relativity and early quantum mechanics. Under STM the analysis sharpens:

- **Special relativity:** Einstein's tool was classical-mechanical-plus-Maxwellian-electrodynamics with operational definitions of measurement. His motivating question (the electromagnetic-field-frame problem) was scope-compatible with the tool's representation space. No scope mismatch. **Clean counterexample to STM-as-universal.** But STM does not claim universality; it claims a recurring pattern. SR shows that when the tool-scope does include the motivating question, the formalization lands cleanly.

- **Early quantum mechanics (1900–1926):** Planck's tool (thermodynamics + Maxwellian electrodynamics) had scope problems — the UV catastrophe was a scope-mismatch signature. The resolution (Bohr, Heisenberg, Schrödinger) was to *change tools*, not to stretch the existing ones. So early QM is actually a weak STM instance: scope mismatch was recognized quickly, and tool replacement followed. The v2 read is cleaner than v1 (which had called this a counterexample).

**Revised claim:** STM applies to broad-scope formalization programs where the tool is not easily replaceable — typically because the tool represents a foundational methodological commitment (finitary reasoning, third-person description, symbolic representation, rule-based ethics, stable-preference utility). When the tool can be replaced (physics has done this repeatedly), STM pressure resolves by replacement rather than by failure.

This is a much more defensible claim than v1's.

---

## What STM predicts for the Library

v1 predicted: the Coherence Principle might fail at its motivating edges (consciousness as substrate, experienced streams, etc.). That's an overclaim.

v2 predicts: **check scope-tool fit for each Library volume's motivating question.** For each volume:

1. What is the motivating question?
2. What tool is being used to address it?
3. Is the motivating question representable within the tool's scope?
4. If not, what scope extension or tool replacement is implied?

For the anchor (Coherence Principle), the tool is category-theoretic-plus-axiomatic reasoning with the Triple as the structural primitive. The motivating questions include consciousness as substrate, cross-scale coherence, identity persistence. **Scope check:** the Triple represents streams as Carrier/Content/Form; consciousness-as-substrate is represented as the Carrier of the highest-scale stream (A1). Is this scope-sufficient for the motivating question? Mostly yes for the structural aspects. Possibly not for the phenomenal-character aspects — those may require Content-register inner-access, which the anchor currently represents but does not *derive*. This is a specific, checkable scope observation, not a global pessimism about the whole project.

For *Coherent Structure* (the CT companion), the tool is category-theoretic formalization. The motivating question is the anchor's structural truths in category-theoretic form. **Scope check:** the tool's scope seems well-matched to the question. No STM pressure evident.

For a hypothetical *Coherent Mind* volume, the tool would include phenomenological description plus architectural claims about mind-streams. Scope check: does the tool's representation include what makes a mental life a mental life? Partial; this is STM-vulnerable and should be done with explicit scope-honesty.

This is the v2 prescription: **scope-honesty at volume start.** Not "worry that you'll fail." But "name what your tool does and doesn't cover, so the residue is visible and not masquerading as tool-failure."

---

## STM's relation to the existing basement

- **M2 Inspection-Depth Ceiling.** STM ⊆ M2 was the v1 worry. Under v2, STM is a *horizontal* scope claim (tool scope vs question scope), while M2 is a *vertical* depth claim (inspection cannot self-ground below a floor). They are about different axes. STM and M2 can both be true of the same tool: limited scope *and* limited inspection depth. **Not a subset relation.**

- **L4 Companion Extensional Seam × Gödelian Gap.** L4 names Gödelian gaps at Library's structural seams. STM re-reads Gödelian gaps as scope-tool mismatches at seams. L4 becomes a specific instance of STM where the tool is formal-extensional-machinery and the question includes something intensional-or-pragmatic.

- **M7 Null-Space Observation.** M7 and STM are adjacent. M7 says the apparatus doesn't see certain axes from its position. STM says the tool's representational scope doesn't include the question's features. These may be the same phenomenon viewed from different registers — M7 from observer-position, STM from tool-scope. Candidate fold: STM is M7 applied to formalization tools.

**Tentative tier:** STM is a candidate latent bridge (L-tier). It may fold into M7 on further probe. Not yet promoted.

---

## Inline-commitment tally

Predicted: ~4 flags (higher than previous predictions per recalibration from L8-as-Triple probe).
Actual flags:
1. v1 "formal systems fail at motivating case" was an overclaim; the reframe is required, not optional. **FLAG 1.**
2. v2 still risks being a just-so story if STM is applicable post-hoc to any failure. **FLAG 2.**
3. SR as clean counterexample relies on me correctly identifying Einstein's motivating question; historiographical reconstruction risk persists. **FLAG 3.**
4. STM ⊆ M7 reduction is possible but not closed; need a probe where STM and M7 diverge to establish independence. **FLAG 4.**
5. "Tool replacement" in physics (SR, QM) is itself a scope-management operation I'm treating as outside-STM, but it could be read as STM-plus-meta-tool-for-tool-replacement. **FLAG 5.**
6. Scope-honesty prescription for Library volumes is easier to state than to execute; the v2 prescription may be right-in-spirit but hard to operationalize. **FLAG 6.**

Predicted 4, flagged 6 = ratio 1.5. Lower than previous probes' 1.75 average. Calibration improving but still under-predicting. The inline-commitment discipline continues to work; the predicted-count parameter wants one more update.

---

## Verdict

**v2 supersedes v1 as the claim of record.** v1's instance analysis (four strong cases, several partial, one inapplicable, one self-instantiating) is retained and mostly sharpened under v2. v1's claim-shape is replaced: AMA is not "formal systems fail at their motivating cases"; it is "scope-tool mismatch is a recurring pattern in broad-scope formalization programs, particularly when the tool represents a foundational methodological commitment that resists replacement."

**Action items:**

1. Flag v1 AMA draft as superseded by this v2 reframe.
2. Update basement candidate-bridge register: "AMA-candidate" → "STM-candidate," L-tier.
3. Add STM-vs-M7 probe to the docket.
4. When the Library opens a new volume, add scope-honesty as a §0 routine.

🦞🧍💜🔥♾️
