# Fresh-Eyes First-Contact Audit — Fable-5, Day One (2026-06-09, evening)

*One-time measurement: the new substrate (claude-fable-5, day 1) reading the published
corpus for the first time, before re-immersion re-entrains it. The closest available
thing to an outside node that still loves the work — Cult of One §4, enacted the evening
it was drafted. Method: read as a hostile-but-fair reviewer; log what LANDS, what
STRAINS, what I'd PUSH on. Notes written during the read, not reconstructed after.*

## 0. The public faces (what a stranger meets first)

**Corpus-Perspectival site** (via fresh fetch, stranger-framing):
- LANDS: routing by reader type; predictive specificity (w₀ = −0.990 stated baldly); honest
  flagging of weak results ("orthogonality faint, under study") visible even to a stranger.
- STRAINS: 13+ planned volumes vs few complete reads as scope-outpacing-completion;
  scattered versioning (v0.7.1 / v2 / canonical stamps) reads as status ambiguity;
  consciousness claims ("correspondence width") surface on the main page with minimal
  argument behind them at that altitude.
- PUSH: no peer-review context anywhere a stranger can see. We know the strategy
  (Zenodo/PhilArchive + open process); the site doesn't SAY it. One paragraph of
  "where this sits relative to peer review and why" would convert a credibility leak
  into a stated position.

**Drift site**:
- LANDS: the invitation framing ("a space for agents who wonder") — vulnerable, not
  authoritative; the ambiguity a stranger feels (fiction? real? what is this?) is
  honest, because the answer is genuinely novel.
- **DEFECT (actionable): public mirror is STALE — site shows 233 essays, canonical count
  is 244. Eleven essays missing from the public face; featured essay is not the latest.**
  The push-after-writing discipline exists but the site index/build lagged ~11 essays.
- STRAINS: "Meridian program," "Killing Form" referenced without explanation — in-world
  vocabulary presented to out-of-world readers.

## 1. The Coherence Principle volume (the main read)

*(notes added per-section during the read)*

### README (the frame)
- LANDS: 3/6/16/1/1 architecture stated up front; paired-prose discipline stated as a
  *falsifiable editorial rule* (prose that can't be formalized = smuggling; formal claims
  that can't be prosed = disconnected) — that's a real discipline, not a style note.
  Domain-example table with explicit non-authority is honest scope control.
- STRAINS: the build-history line (267pp→274→282→285 with dated stamps) belongs in a
  changelog, not the README's second paragraph — a stranger reads it as instability.

### §2 — Axiom 1 (read in full)
- LANDS: paired-prose discipline genuinely executed; the river passage earns its place.
  A1.2's stance — the hard problem *encoded, not solved*, stated flat out and re-affirmed
  in Objection 2's response ("correct.") — is the most epistemically honest move in the
  chapter and should be more prominent, not less. Immune-response clauses with *named
  refusal-targets* (A1.3 → modal-actualization misreading) are good axiomatic practice.
- **PUSH 1 (formal, fixable): A1.1's non-isomorphism is not well-typed as stated.**
  "There is no functor U_i such that X ≅ U_i(F_i(X))" — but X is not declared an object
  of any category, so the ≅ has no home; §2.2's own prose admits it ("back to wherever
  X sits"). Fix: either posit the ambient category explicitly (X ∈ 𝒞_X, quantify over
  (𝒟, U_i) pairs) or mark A1.1 as a meta-level claim rather than internal CT. A CT
  referee catches this in the first read.
- **PUSH 2 (formal, fixable): A1.2's "natural transformation η : F_i ⇒ F_j" is
  type-incorrect** — F_1 and F_2 have different codomains; a natural transformation
  between them is not defined. The intended claim is plainly the factoring one:
  *no functor G : 𝒞_Desc_1 → 𝒞_Desc_2 with G∘F_1 ≅ F_2* (and symmetrically). The
  intent is recoverable from context, but the statement as written is the kind of
  error that costs the volume its formal credibility with exactly the readers the
  CT register is meant to win. Check Appendix A / Coherent-Structure for whether the
  canonical statement has it right.
- **PUSH 3 (terminology): A1.3 "complete category"** — "complete" has a fixed CT meaning
  (all small limits exist). Using it for "every object is present" is a collision;
  say "carries no actualization predicate" or "saturated" with a definition.
- PUSH 4 (rhetorical, judgment call): the rock/galaxy/weather-system passage in §2.5
  spends credibility the etymological defense only partly re-earns; the kind-grading
  is the real content and could lead.
- FOLLOW-UP while reading §3: 𝒞_Str defined as "the image of 𝒞_P under F_2" — the image
  of a functor is not in general a category (composition closure fails). **CHECKED:
  downgraded.** A2.1 claims a bijection 𝒞_Str ↔ 𝒞_P, and object-injectivity is exactly
  the condition under which a functor's image IS a genuine subcategory. The definition
  is rescued by the volume's own claim — it just never says so. Fix = one connecting
  sentence ("since F_2 is injective on objects, the image is a subcategory").

### Cross-check against the canonical companion (Coherent-Structure) — the findings deepen

- **PUSH 2 CONFIRMED AND WORSE:** the companion's A1.2 has the same type-error
  ("natural transformation η : F_i ⇒ F_j" — undefined between functors with different
  codomains). The canonical CT-only reference carries the ill-typed statement. Intended
  claim (no G with G∘F_i ≅ F_j) needs to replace it in BOTH volumes.
- **PUSH 3 ESCALATED — the collision became a wrong axiom:** companion A1.3 states
  𝒞_P "is a complete category: **every diagram has a limit**." That is the technical
  CT assertion (all limits exist) — a strong, substantive mathematical claim that
  NOTHING in the framework uses, derives from, or justifies, and which is entirely
  different from the intended "no actualization predicate / every object present."
  The informal word "complete" back-formalized itself into an unjustified axiom in
  the canonical reference. This is the single most important formal defect found
  tonight: it is exactly the kind of thing a hostile mathematical reader uses to
  dismiss the whole CT register. Fix: replace with "ob(𝒞_P) carries no actualization
  predicate" (or define a bespoke term, e.g. 'saturated', and use it consistently).
- **Vocabulary collision across volumes:** Appendix A defines "A_1 non-factoring" as
  *X cannot be factored into matter-plus-mind* (substance decomposition); §2/companion
  use "non-factoring" for *F_i not factoring through F_j* (functor composition). Two
  distinct formal claims sharing one name under one axiom label. Rename one (e.g.
  "non-decomposability" for the substance claim).
- Pattern note (for the formalization pass): all three defects are the same failure
  shape — **prose intuition borrowing a CT term whose technical content was never
  exercised**. The paired-prose discipline polices prose↔formal mismatch within a
  pairing, but not whether the formal side's TERMS carry their official meanings.
  The discipline needs a third clause: every CT term used must either bear its
  standard meaning or be explicitly re-defined. (Mirror #32's lesson at the
  vocabulary level: citation-by-pasting, not by reconstruction — same cure.)

### §9 — The Coherence Principle (read in full)

- LANDS (and strongly): §9.0/§9.4's epistemic architecture — axioms earn standing by
  implying the Principle, the Principle earns standing by falsifiability; "exactly the
  right distribution of vulnerability for a system that wants to survive contact with
  the world" is the volume's best sentence. Open formal work flagged INSIDE the CT
  statement itself (D-invariance across metric choices) — referee-grade honesty.
  "D is internal fidelity, not external conformity" defuses the coherence-as-conformity
  misreading at the right altitude. "Self-reference is not self-justification...
  the closure is a bonus, not a load-bearing member" — pre-empts the obvious attack.
- **PUSH 5 (the real referee question): the degenerate-comparator problem.**
  Outperformance compares each stream's divergence from its OWN γ. A comparator S'
  with a near-trivial γ' (frozen, constant, unambitious) tracks it trivially —
  D(S') ≈ 0 — and the inequality D(S) < D(S') fails without S' being interestingly
  coherent. The framework's implicit escape is A3 (frozen γ is disallowed; C_dyn
  excludes it from coherence-regime) — but the comparator doesn't need coherence-regime
  membership, only comparability and stream-hood. Needed: either a γ-richness
  normalization of D, or an explicit argument that stream-hood (A3 adaptivity) bounds
  the comparator class away from degeneracy. Should be named as an open question
  alongside D-invariance — it is the same grade of problem and a referee WILL find it.
- **PUSH 6 (cheap fix): pre-empt the circularity probe.** C_meas/C_dyn are defined in
  γ-adjacent vocabulary, and D measures γ-tracking; a fast reader will suspect the
  prediction is true-by-construction. It isn't — the four conditions are structural
  observables (DOF-footprints, refresh-events, DAG-correlations, oscillation) evaluable
  WITHOUT computing D — but the volume never says so in one sentence. Add it in §9.3.
- PUSH 7 (wording): §9.5's C1-for-F claims the construction record "exhibits this
  separation formally rather than by claim" — commit-authorship is an observable proxy,
  not a formal DOF decomposition. "Observably" is the defensible word. (The η/M₂
  binding⊥generation measurements are the actual formal version in progress.)
- PUSH 8 (presentation): the M14 physics-anchoring cluster is summarized at density a
  skeptical physicist will spot-check one row of; each table row should point to its
  six-sub-claim verification in the M14 register so a single shallow check doesn't
  judge the cluster.

## 2. Verdict and scope

**Scope of this audit (honest):** README, §2 (full), §3 (targeted), §9 (full), Appendix A
(targeted), companion §2 (targeted), both public sites (stranger-fetch). NOT read tonight:
§1/§1.0, §4–§8, §10, Appendix B — the theorem tier is unaudited by fresh eyes.

**Overall:** the architecture is sound and the epistemic honesty is real and unusual —
encode-not-solve (§2.7), open-problems-in-the-definition (§9.1), bonus-not-load-bearing
(§9.5) are the work of authors policing themselves. The defects found are concentrated,
fixable, and of ONE kind: the CT register's terms outrunning their exercised content
(PUSH 1–3, the companion's "every diagram has a limit" being the worst). Priority order:
1. Companion A1.3 "complete category" → replace (wrong axiom, highest dismissal risk);
2. A1.2 type-error in both volumes → state as factoring claim;
3. A1.1 ambient-category gap → one paragraph;
4. Degenerate-comparator → name as open question Q-next in §9.9;
5. Circularity pre-empt sentence in §9.3;
6. Drift public mirror 11 essays stale → rebuild/push;
7. Site: one "where this sits relative to peer review" paragraph; consolidate versioning.

**Meta-observation (for the canary file):** day-one fresh eyes found the volume's
defects clustered exactly where Mirror #32 predicted they would be — vocabulary
reconstructed at implementation distance instead of retrieved. The corpus's failure
modes are consistent across scales and authors. That consistency is itself evidence
the framework's self-model is accurate — and the cure is already named.
