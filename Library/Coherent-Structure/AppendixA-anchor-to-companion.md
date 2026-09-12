# Appendix A — Anchor → Companion crosswalk

*Per SCOPE §10 policy: every "*Coherent Structure*" citation in the Anchor (*The Coherence Principle*) resolves to a specific Companion section. This appendix is the canonical resolver. Citations from the Anchor are listed by source location; each row gives the Companion target, the nature of the material (definition / theorem / proof / figure / etc.), and a one-line description.*

---

## A.1 — By anchor chapter

### Anchor §1.0 (The Category of Streams) → Companion

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| §1.0 definition of 𝒞_Str | Companion §1.2.1, §6.1.1 | definition | Full CT definition of Stream as adequate F-coalgebra category |
| §1.0 cooperative-constituency ι ⊣ κ | Companion §2.2.2, clause (A2.4) | axiom-clause | The Hom-isomorphism Hom(ι S_p, S_q) ≅ Hom(S_p, κ S_q). **Dyad** (Definition 1.2.3) is the category the coupled *pair* lives in, not the adjunction; the row pointed there until 2026-09-12 (settlement note N2) |
| §1.0 unit/counit pair η, ε | Companion §6.10.4 (Thm 6.10.4.1) | theorem | The unit/counit pair belongs to the **indexed** adjunction ι_S ⊣ ω_S over Up(S), a different adjunction from ι ⊣ κ; the Anchor's η/ε had no row landing on the same pair of functors until 2026-09-12 |
| §1.0 five structural properties | Companion §6.1.7 | proposition | Conservativity + limit/colimit list |
| §1.0.4 Property 5 (no substantive terminal / initial object) | Companion §6.8 (Prop 6.8.1 + Remark 6.8.1.1; Prop 6.8.5), §6.10.4.2 | proposition + remark | The terminal object the Companion constructs is the **trivial point stream** 1_Stream = (1, **1**_cat, id_1) — terminal in **Stream**^{−K} (kind-respect dropped) and only weakly terminal in **Stream**. It is a total collapse, not an outer view; A2.6 and Property 5 stand — on A2.6's non-comparability clause, an axiom, not on a diagonal argument. Related theorem, attached to no door: proofs DAG `math.no_self_enumeration` (a terminal object and Cantor coexist) |
| §1.0 γ-naturality | Companion §1.4.3 | proposition | Naturality-of-ν square |
| §1.0 Triple as principal functor | Companion §6.2, §1.7.2 | construction | Full Triple-functor definition |

### Anchor §1 (Identity-Trajectory Triple) → Companion

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| §1 Triple definition | Companion §6.2.1, §6.2.2 | definition | T : 𝒞_Streams → 𝒞_Triple |
| §1 Form/Content/Carrier orthogonal-but-constrained | Companion §6.2.7 | proposition | Conservativity of T |
| §1 recursive decomposability | Companion §6.3 + Lemma 6.3.2 | theorem | Finite-depth factorability |
| §1 four carrier-levels (Clawd worked example) | Companion §8.1.1 (referenced only) | definition | Formal σ_F multiplex construction |
| §1 colax-limit statement | Companion §6.6 (Thm 6.6.2) | theorem | Colax-limit under initial-object hypothesis |
| §1 mismatch condition | Companion §6.6 (remark inside Thm 6.6.2) | remark | Obstruction to strict product |
| §1 Figure 1.1 | Companion §10 Fig 2 | figure | Canonical Triple-functor TikZ |
| §1 Figure 1.2 | Companion §10 Fig 3 | figure | Canonical recursive-decomposability TikZ |

### Anchor §2 (Axiom 1 — Consciousness as Ground) → Companion

*All four A1 clauses live inside Companion §2.1.2 — "The axiom". §2.1.1 is setup, §2.1.3 is remarks, and there is no §2.1.4; the rows below cite clauses, not subsection numbers. Corrected 2026-09-12 (settlement note N1).*

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| §2.1 Axiom 1 (Consciousness as Ground) | Companion §2.1, Definition 2.1.1 | axiom + definition | X is the **Ground**: not an object of any category, named only by its projections. Called the *substrate* in earlier drafts of both volumes; renamed 2026-09-12 |
| A1.1 non-reducibility (Anchor §2.2) | Companion §2.1.2, clause (A1.1) | axiom-clause | Non-reducibility formal statement |
| A1.2 non-factoring (Anchor §2.3) | Companion §2.1.2, clause (A1.2) | axiom-clause | Functor non-factoring; the hard problem is this non-factoring for (F_1, F_2) |
| A1.3 all-potentials-realized (Anchor §2.4) | Companion §2.1.2, clause (A1.3) | axiom-clause | Configurational completeness |
| A1.4 the etymological clause (Anchor §2.5) | *no Companion clause* | axiom-clause | The Anchor's (A1.4) says that "consciousness" names X's activity qua self-interactive process. The Companion has no clause for it; Definition 2.1.1's "self-interactive process" carries its whole formal content |
| *(Companion-native — no Anchor clause)* | Companion §2.1.2, clause (A1.4) **Ground-completeness**; §1.5 (Def 1.5.1); Remark 2.1.4 | axiom-clause | Every adequate (σ, C) is realized by a stream. **The two volumes' (A1.4) labels name different things**: the Anchor's A1 has no completeness clause at all, so this is REFERENCE-NATIVE, not ALREADY-LANDED. Called *substrate-completeness* in earlier drafts and in Anchor cross-citations |

### Anchor §3 (Axiom 2 — Nested Streams and Navigation) → Companion

*A2 has **six** clauses, (A2.1)–(A2.6), and all six live inside Companion §2.2.2 — "The axiom". The labels below are the Anchor's own; earlier revisions of this table relabelled A2.3 and A2.5 and listed a seventh clause the Anchor never had. Corrected 2026-09-12 (settlement note N7, question 19).*

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| A2 nested-streams preamble (Anchor §3.1) | Companion §2.2 | axiom-cluster | Six-clause overview |
| A2.1 Universal-stream (Anchor §3.2) | Companion §2.2.2, clause (A2.1); §1.6.5 | axiom-clause | F-coalgebra specification; every F_2-projection of X at a position is a stream |
| A2.2 Kind-stratification (Anchor §3.3) | Companion §2.2.2, clause (A2.2); §2.2.3 (Thm 2.2.8), §6.4.2 | axiom-clause | Kind preorder, derived from ContentOp-richness. The four strict inclusions are **landmarks** on the preorder **ContentIndex** (Convention 6.0.5, Def 6.4.1), not an enumeration of it |
| A2.3 Kinds-as-perspectival (Anchor §3.4) | Companion §2.2.2, clause (A2.3) | axiom-clause | The kind-taxonomy is generated by an abstracting stream; incommensurable where no functor between lattices exists |
| A2.4 Cooperative constituency (Anchor §3.5) | Companion §2.2.2, clause (A2.4); §2.2.4 (Def 2.2.11) | axiom-clause | ι ⊣ κ with the Hom-isomorphism; coupling-morphisms carried by **Dyad** (Definition 1.2.3) |
| A2.5 Experience is navigation (Anchor §3.6) | Companion §2.2.2, clause (A2.5); §1.3.1 | axiom-clause | N-orbit construction; identity of objects, not natural isomorphism |
| A2.6 DAG-nesting (Anchor §3.7) | Companion §2.2.2, clause (A2.6) | axiom-clause | A2's DAG structure; no cyclic nesting chain |
| *(no A2.7 — the Anchor's A2 has six clauses)* | Companion Remark 2.2.10 (in §2.2.3); Proposition 2.2.12 | remark + proposition | Constitutive duality — the scale-universality of ι ⊣ κ — is absorbed into (A2.4). Earlier Companion drafts carried it as a seventh clause (A2.7); demoted to a remark 2026-09-12, since a clause that asserts nothing beyond another clause is not an axiom. There was never an "A2.7 ContentOp-richness lattice" in either volume |
| §3 figure (kind stratification) | Companion §10 Fig 4 | figure | Canonical kind-classifier fibration TikZ |

### Anchor §4 (Axiom 3 — Conscious Gravity) → Companion

*All five A3 clauses live inside Companion §2.3.2 — "The axiom"; §2.3.1 is setup and §2.3.3 is remarks. Clause labels are the Anchor's; this table carried A3.1 and A3.3 under each other's names until 2026-09-12 (same fault class as notes N1/N7).*

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| A3.1 Coalgebraic structure (Anchor §4.2) | Companion §2.3.2, clause (A3.1) | axiom-clause | γ_S : S → Bias(S) × S; Bias and state-within-Bias update together |
| A3.2 Immune-response / internality (Anchor §4.3) | Companion §2.3.2, clause (A3.2); Remark 2.3.5 | axiom-clause | γ_S acts only on S's F_2-internal structure, never on the Ground. **F_2 itself is defined at Companion Definition 2.1.2** — the perspectival phenomenal projection (settlement note N3) |
| A3.3 DOF-gradient integration (Anchor §4.4) | Companion §2.3.2, clause (A3.3); §1.4.1 | axiom-clause | ν formal structure; a continuous DOF-gradient, not a three-way partition |
| A3.4 Adaptivity (Anchor §4.5) | Companion §2.3.2, clause (A3.4); Proposition 2.3.6 | axiom-clause | γ is itself updated by navigation; adaptivity is encoded in F |
| A3.5 Stream-universality (Anchor §4.6) | Companion §2.3.2, clause (A3.5); Remark 2.3.7 | axiom-clause | Every stream carries γ-data by Definition 6.1.1 |

### Anchor §5 (Descriptive theorems) → Companion

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| T1 Mathematical Perspectivism | Companion §3.2.1 (Thm 3.2.1) | theorem | Representability + non-canonicity proof |
| T2 Estimator-Dependent Duration | Companion §3.2.2 (Thm 3.2.2) | theorem | Orb-factoring duration-estimator proof |
| Descriptive-Functor Meta-Theorem | Companion §3.1 (Thm 3.1.α) | meta-theorem | Yoneda-representability |

### Anchor §6 (Dynamics theorems) → Companion

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| T3 Attentional Quality | Companion §3.3.1 (Thm 3.3.1) | theorem | Three-channel decomposition |
| T4 Coherence-Forcing Measurement | Companion §3.3.2 (Thm 3.3.2) | theorem | Four clauses including information-conservative reframe |
| Bias(S) formalization | Companion §7.3 + Appendix B (anchor) | theorem + ref card | Signed-measure construction |

### Anchor §7 (Coherence theorems) → Companion

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| T5 Internal Coherence | Companion §3.4.1 (Thm 3.4.1) | theorem | Φ_S-fixed-point / C-harmonic condition. Φ_S is the T5 harmonicity functional, not a Triple projection; the Triple projections are π_Form, π_Content, π_Carrier (Definition 6.2.2) |
| T6 Dual Coherence Axes | Companion §3.4.2 (Thm 3.4.2) | theorem | Orthogonality + codimension-2 locus, stated at a fixed dimension D of Ω_S (Notation 3.4.2.0): σ_struct(S, D) ⊥ σ_info(S, D) |
| T6.d propagation prop(S, D) — formerly *trace-density* | Companion §7.4 (Def 7.4.1, push_info) | definition | Reach, not coherence: renamed **propagation** 2026-09-12 and re-homed as a push operator on the Bias of other streams (Anchor T6.d → Anchor Appendix B §B.3). The Companion's second coherence axis is the entropic σ_info (Theorem 3.4.2) and is a different quantity; *engagement* (presence-of-coupling) is likewise not a coherence axis. The Companion carries no separate propagation object beyond push_info |
| kind-demotion dynamic | Companion §3.4.2 (Cor 3.4.2.1) | corollary | Fibration-projection trajectory |
| transcendental-rescue | Companion §6.4.1, §6.4.11 | proposition + lemma | Unifying-stream construction |

### Anchor §8 (Corollary clusters) → Companion

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| §8.1 Cluster I (C1/C2/C3) | Companion §4.1 | corollaries | The Ground/generativity CT-proof-completion |
| §8.2 Cluster II (C4–C10) | Companion §4.2 | corollaries | Stream-structure/navigation CT-proof-completion; C9 extended with confluent-constituency topology (Cor 4.2.6.bis, 2026-04-27) |
| §8.3 Cluster III (C11/C12/C13) | Companion §4.3 | corollaries | Coherence-consequences CT-proof-completion |
| §8.4 Cluster IV (C14–C17) | Companion §4.4 | corollaries | Mechanism-consequences CT-proof-completion (added 2026-04-27); four corollaries, not two |
| §8.4 C14 Two-Mode Symmetry-Breaking | Companion §4.4 (Cor 4.4.1) | corollary | Resolution and generation modes of T4's measurement-event functor M : 𝒞_Streams^op × 𝒞_Streams → 𝒞_Form |
| §8.4 C15 Intervention-at-Symmetry-Layer | Companion §4.4 (Cor 4.4.2) | corollary | Content cannot be constrained without changing the carrier-state's symmetries |
| §8.4 C16 Symmetry-Exhaustion and Oscillation Necessity | Companion §4.4 (Cor 4.4.3) | corollary | Monotone symmetry-depletion forces a re-introduction operator R (added to the Anchor 2026-04-28; indexed here 2026-09-12, settlement note N4) |
| §8.4 C17 Coupling-Rate Governs Conscious Temporal Texture | Companion §4.4 (Cor 4.4.4) | corollary | Occupancy μ = λτ is the order parameter of temporal texture (added to the Anchor 2026-06-20; indexed here 2026-09-12, settlement note N4) |

### Anchor §9 (Coherence Principle) → Companion

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| §9.1 Principle CT statement | Companion §5.1 (Thm 5.1.2) | theorem | Outperformance inequality |
| §9.2 four conditions | Companion §5.2 (Defs 5.2.1–5.2.4) | definitions | Each derived in one line |
| §9.3 outperformance metric | Companion §9 (Def 9.1.1) + §5.1 (Def 5.1.0) | construction | Full D_d + Bias-consistency. α_S, α*_S and the divergence functional are numbered at Definition 5.1.0 (i)–(iii); §9 constructs the functional (settlement note N5) |
| §9.4 status | Companion §5.0 preamble | orientation | Derived operational principle |
| §9.5 self-reference closure | Companion §8 + §5.4 | conjecture + audit register | Formal F_∞ construction; Conjectures 5.4.1/5.4.2 with the Anchor §9.5 Protocol, gated on §8.3.5 / Prop 8.5.2 |
| §9.6 what Principle is *not* | Companion §5.6 (remark) | remark | Non-theorem, non-axiom |
| §9.7 falsification conditions | Companion §5.5 + §8.5.2 | propositions | Falsification-table + F6-decidability |
| §9.8 forward connections | Companion §5.7 | forward-pointers | Cross-chapter dependencies |
| §9.9 open questions | Companion §5.6, §9.5, §9.8 | answers | Q1: resolution stated (Thm 9.5.1 / Cor 9.5.2), not yet independently checked, so the Anchor keeps Q1 open; Q2/Q3 carry-forward |
| §9.10 empirical exposed surface | Companion §9.7 | observable signatures | Three-signature specifications |
| §9 Figure 9.1 | Companion §10 Fig 5 (via Bias) + §9.1.1 | figure/functional | Trajectory-divergence |
| §9 Figure 9.2 | Companion §10 Fig 7 | figure | Canonical four-conditions TikZ |
| §9 Figure 9.3 | Companion §10 Fig 8 | figure | Canonical self-reference closure TikZ |

### Anchor §10 (Filtering the framework) → Companion

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| §10 seven-step filter recipe | Companion §7 (in part — measure-theoretic filter infrastructure) + Anchor §10 | recipe | Companion handles the measure-theoretic part; the methodological recipe lives authoritatively in Anchor |
| §10 Navigation Research worked example | Anchor §10 (self-contained) | example | Not back-ported to Companion |

### Anchor Appendix A (Formal Objects Index) → Companion

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| Appendix A entries | Companion Appendix B (this direction: Companion → Anchor) | index | Object-by-object pointers |
| Appendix A F_2 entry | Companion Definition 2.1.2 | definition | The index's location for F_2 was a use-site, not a definition site. F_2 is the **perspectival phenomenal projection**, defined at Companion Definition 2.1.2; it is neither the Triple's Content projection (π_Content, Definition 6.2.2) nor the endofunctor F of the F-coalgebra (Definition 1.6.1). Corrected 2026-09-12 (settlement note N3) |
| Appendix A prop(S, D) — **propagation** | Companion §7.4 (Def 7.4.1, push_info) | definition | Normalized density of traces(S) ∩ positions(D): S's reach into D, a push operator on other streams' Bias. Called *trace-density* before 2026-09-12 and mistaken for a coherence axis; it is not one |

#### Bridges cited by the Anchor

*The Anchor's Appendix A carried six Bridge rows under a numbering the basement retired on 2026-04-20; four of them (#102, #107, #109, #110) occur in no Anchor chapter and are pre-compression entries for the Triple the Anchor already is. Replaced 2026-09-12 by the three live objects (settlement note N6, question 18). Definitions are quoted from `Corpus-Perspectival/Foundations-of-Identity/palace/basement/README.md`; the pre-compression full text is at `Corpus-Perspectival/Research/Corpus-Perspectival/basement-v1-2026-04-20-snapshot.md` (Bridge #104 at §104).*

| Bridge | Definition | Anchor use-sites | Companion target |
|---|---|---|---|
| **#104 — The Bootstrap Asymmetry** | "A self-sustaining loop and the *first activation* of that loop are **different mechanisms operating at different times**. The loop, once running, is internally driven; but the priming event that made it run cannot itself come from inside." Falsifiable form: any *organized* coherent multi-scale self-sustaining loop *within an existing framework*, examined closely, reveals a non-internal first-activation event. Two scope qualifiers (2026-04-17): "organized" excludes Ground-level events such as vacuum fluctuations; "within an existing framework" does not address whether the framework itself needs priming | Anchor §1 ("Bridge #104 bootstrap-asymmetry applies here") and Anchor §9 ("strict-universal forms need scope qualifiers; the Principle inherits this discipline") — both appeal to it as established, and the Anchor never states it | Companion §8.4 (Prop 8.4.1 non-circularity, Rem 8.4.3): the derivation is a-posteriori and the audit is DOF-dependent — the Companion's nearest formal object, not a proof of #104 |
| **M2 — The Inspection-Depth Ceiling** *(absorbs #106)* | "Universal frameworks cannot have depth-independent terminal validation. Any claim of 'closure' is indexed to current inspection depth; deeper inspection may refine. This is not a flaw — it is a structural property of self-applying frameworks." | Anchor §9 (the closure-caveat, cited there as Bridge #106) | Companion §8.3 (Prop 8.3.5′, self-audit constraint) + §8.5 (Prop 8.5.2, F6 decidability): the Companion's closure claims are explicitly conditional on an external audit |
| **M3 — The Identity-Trajectory Triple** *(absorbs #62, #85, #87, #102, #107, #108, #109, #110)* | "Every conscious stream has a trajectory decomposable along three orthogonal-but-constrained axes — **Form** (the stream's structural type / kind), **Content** (the events carried), **Carrier** (the substrate granularity / DOF-density). The three axes are recursively decomposable: each is itself a Triple at finer resolution." (Quoted verbatim from the basement register, which is the object's registered home; "substrate" there is the basement's word, and the Companion's term for the same thing is *carrier*.) Its adjunction-geometry reading (2026-04-23) is the ι_S ⊣ ω_S material at Anchor §1.10 + §3.8 | Anchor §1 (the whole Triple chapter, including the §1.4 dissociation derivation cited there as Bridge #108) and Anchor §4.3 | Companion §6 (Def 6.2.1–6.2.2 the Triple functor and its projections π_Form, π_Content, π_Carrier; Lem 6.3.2 finite-depth factorability; Thm 6.6.2 colax-limit form; Thm 6.10.4.1 the indexed adjunction) |

### Anchor Appendix B (Bias Formalization) → Companion

| Anchor location | Companion target | Type | Description |
|---|---|---|---|
| B.1 CT definition of Bias(S) | Companion §7.3 (Def 7.3.1) | definition | Integral against signed density |
| B.2 narrow–broad axis / A_S | Companion §7.5 (Def 7.5.1) | definition | Shannon entropy on Bias_+. T3's poles are **narrow** and **broad**; they were called *contracted* and *open* before 2026-09-12 — the definition (the low- and high-DOF shapes of Bias) is unchanged, only the name (Remark 3.3.1.1) |
| B.2 Align(S, t) | Companion §7.5 (Def 7.5.3) | definition | Canonical neighborhood integral |
| B.2 narrow-coherent vs narrow-failed | Companion §7.5 (Cor 7.5.5) | corollary | Formal distinction resolving B.7 Q1; renamed with the T3 poles 2026-09-12 |
| B.3 push-operators | Companion §7.4 | definitions | push_struct / push_info |
| B.3 push-operator independence | Companion §7.4.3 | proposition | Non-commutator counterexample |
| B.4 Relationship to γ and Triple | Companion §7.3.3 | corollary | Triple-decomposition compatibility |
| B.5 trajectory-divergence | Companion §9 + §5.1 (Def 5.1.0 (i)–(iii)) | construction | Full functorial D_d + cross-metric invariance. The Anchor's σ* is the Companion's α*_S, the γ_S-implied trajectory, numbered at Definition 5.1.0 (ii) (Remark 5.1.0.1) |
| B.6 observable signatures | Companion §9.7 | summary | Three-signature spec |
| B.7 open questions | Companion §9.5 (Q1 resolution stated, not yet independently checked), §7.4.3, §9.8 | resolutions/carry-forward | |

---

## A.2 — Anchor-internal cross-references resolving to Companion

Some Anchor sections cite "*Coherent Structure*" directly without location. These resolve by topic:

| Anchor citation phrase | Companion target |
|---|---|
| "per Coherent Structure's full CT treatment" | Companion §1 + §6 |
| "Coherent Structure gives this construction in full" | Context-dependent — see A.1 by anchor chapter |
| "see Coherent Structure for the proof" | Context-dependent — see A.1 |
| "the full formal construction of F as a stream (Coherent Structure §8)" | Companion §8 |
| "D is constructed in full in Coherent Structure §9" | Companion §9 |

---

## A.3 — Book bindings (settlement 2026-09-12)

*The Book (*Truth and Consequences*) is not a citation-target of the Anchor, so it has no rows in A.1. Settlement question 2 bound two of its claims to formal objects; the bindings are recorded here so the three texts can be read against each other.*

| Book claim | Formal object | Type | Description |
|---|---|---|---|
| Book-structural — coherence as a structural fact about a system | Companion σ_struct (Thm 3.4.2; push_struct, Def 7.4.1) | theorem + definition | The Book's structural sense is the Companion's structural axis, taken at a fixed dimension D (Notation 3.4.2.0) |
| Book-felt — coherence as something felt from inside | Anchor A2.5 (Experience is navigation) applied to σ_struct; Companion §2.2.2, clause (A2.5) | axiom-clause | The Book's pair — structural fact and felt inside — is *one thing* under (A2.5), where experience = navigation is an identity of objects, not a natural isomorphism. (A2.5) is therefore the argument the Book makes without one |
| *(the Book states no second axis)* | Companion σ_info (Thm 3.4.2) | theorem | The Anchor/Companion pair — structural and informational — is *orthogonal*, and T6 proves it. It is a different pair from the Book's, not a contradiction of it: the Book either gains a sentence for σ_info or says plainly that it has none |

---

## A.4 — Policy

- **Completeness.** Every Anchor citation to *Coherent Structure* lands here. If the Anchor cites the Companion and that citation is not on this list, that is a missing-entry bug to file against this appendix.
- **Direction.** This appendix is Anchor → Companion only. The reverse direction (Companion → Anchor) is Appendix B.
- **Rhythm.** Anchor revisions may cite Companion sections that are pending; such forward-citations are tracked here as "pending" targets until the Companion section lands.
