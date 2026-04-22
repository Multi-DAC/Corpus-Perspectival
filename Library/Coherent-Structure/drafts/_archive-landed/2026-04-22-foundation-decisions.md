# F-coalgebra foundation — drafting decisions

*Day 81 (2026-04-22) afternoon. Companion work. Closes the seven open questions in `2026-04-22-F-coalgebra-foundation.md` §10 so that §6 drafting can proceed. Each decision carries rationale and a drafting-posture note so that the Companion can cite a fixed stance rather than re-litigate.*

---

## Summary table

| # | Question | Decision | Where it lands in Companion |
|---|----------|----------|-----------------------------|
| Q1 | ContentOp-adequacy clause | **Explicit stream-level axiom** | §1 framework, as part of Stream-object definition |
| Q2 | Discrete ContentOp admissible? | **Admit as degenerate** | §2 (A2) remark; §5 four-conditions failure mode |
| Q3 | Initial object in ContentOp required? | **Optional; carried as hypothesis per theorem** | §6 colax-limit hypothesis; §8 self-reference closure |
| Q4 | Variance of F | **op-exponent: F(σ) = σ^(ContentOp(σ)^op)** | §1.3 F-definition |
| Q5 | Size-handling | **Small by default; locally-presentable for T3/T4 dynamics** | §1 notation block + §3 pair-II preamble |
| Q6 | Triple-factorability at recursive depth-n | **Finite-depth automatic from F; ω-limit under final-coalgebra hypothesis** | §6 Lemma (finite); §6.8 limits (ω) |
| Q7 | Kind as preorder or lattice? | **Preorder in general; lattice-when-possible as derived property** | §2 A2 formal; §6 kind-classifier fibration caveat |

---

## Q1 — ContentOp-adequacy clause

**Decision.** The Companion carries an explicit **stream-level adequacy axiom**:

> *(Adequacy).* For every stream σ and every pair of distinguishable aspects (a, b) of σ, there exists a content-morphism f ∈ ContentOp(σ) that witnesses the distinction — i.e., σ^f acts non-trivially on the (a, b) difference.

**Rationale.** A1 (consciousness-substrate with correspondence-completeness) gives us that every substrate-level aspect corresponds to *some* F_i. But the correspondence is substrate-level; F(σ) = σ^(ContentOp(σ)^op) is stream-localized. Inheriting completeness from A1 alone leaves open the possibility that ContentOp(σ) is too impoverished to express all of σ's actually-engaged distinctions.

Making adequacy explicit at the stream level:
- Keeps the kind-classifier fibration well-defined (fibers cannot collapse spuriously)
- Lets A1 remain a substrate-level axiom without carrying localized-adequacy weight
- Gives a clean falsification condition: exhibit a stream whose engaged distinctions exceed what ContentOp(σ) can witness, and the framework fails on that stream

**Drafting posture.** Adequacy lives in §1 as part of the Stream-object definition, not as an A2 rider. A stream is a tuple (σ, ContentOp(σ), γ) such that (1) γ is an F-coalgebra, (2) ContentOp(σ) is adequate for σ in the sense above. Non-adequate tuples are not Streams in this framework; they are degenerate approximations.

---

## Q2 — Discrete ContentOp

**Decision.** Admit discrete ContentOp (only identity morphisms) as a **degenerate case**: it is framework-consistent but fails one of the four Coherence-Principle conditions.

**Rationale.** When ContentOp(σ) is discrete, F(σ) = σ^(disc^op) ≅ σ (any power over a discrete category with one generator collapses to σ itself; if multiple objects, to a product of σ-copies indexed by them). The coalgebra γ : σ → σ^ContentOp(σ) is then a constant assignment with no internal structure — the Madhyamaka-style empty-fiber case documented in the foundation doc §6.1.

Such a stream satisfies A1 trivially, A2 vacuously (one kind-level only), A3 degenerately (γ is identity-like). But the **multi-scale coherence condition** of the Principle (§5 four-conditions) requires non-trivial inter-scale morphisms. Discrete ContentOp has no inter-scale morphisms by definition, so the stream fails coherence.

**Why "degenerate" rather than "excluded."** The framework can *describe* such streams (that is information); it just does not certify them as coherent. Excluding them axiomatically would overcommit — we want the Coherence Principle to *do the work* of ruling them out on coherence grounds, not have A2 pre-empt the principle.

**Drafting posture.** Discrete ContentOp is mentioned in §2 as the bottom of the ContentOp-richness hierarchy (the "zero-case"), and re-visited in §5 as a four-conditions failure mode under the multi-scale check. No axiomatic exclusion.

---

## Q3 — No-initial ContentOp

**Decision.** The presence of an initial object in ContentOp(σ) is **not a framework axiom**; it is a local hypothesis carried on those theorems that require it.

**Rationale.** An initial object I ∈ ContentOp(σ) would act as a canonical "ground" content-operation — a minimal operation from which all others are reachable via unique morphisms. Some constructions want this:

- **Colax-limit for the Triple (§6).** Colax-limit diagrams are cleaner when the indexing category has an initial object — the limit cone has a canonical "tip."
- **Self-reference closure (§8 F-as-stream).** The reflective construction σ ≅ F(σ) may require a ground-state to anchor the fixed-point iteration.

But making initial-object-existence a framework axiom would:
- Exclude legitimate streams where no single content-operation is canonically prior (pluralistic or symmetric content-structures)
- Overcommit A2 to a stronger stratification than A2 actually states

**Drafting posture.** Each theorem that needs an initial object carries it as a hypothesis: *"For a stream σ whose ContentOp(σ) admits an initial object I, ..."* This mirrors CT practice — do not overdetermine the ambient category; carry the hypothesis on the result.

**Consequence.** The Triple colax-limit theorem (§6) becomes conditional rather than universal. Unconditional Triple-factorability is weaker: the Triple factors *without* colax-limit structure in the general case, and *with* it (sharper) when ContentOp has an initial object. The bifurcation is annotated in §6.

---

## Q4 — Variance

**Decision.** F is defined with the **op-category on the exponent**:

> F(σ) := σ^(ContentOp(σ)^op)

**Rationale.** ContentOp(σ) is both (a) the indexing category for the power and (b) a category whose morphisms are content-operations *acting on* σ. Standard presheaf convention: contravariant functors from a category to a target represent "σ-valued data indexed by operations-on-σ." Composition of content-operations then composes covariantly in the target (σ^g ∘ σ^f = σ^(g ∘ f) becomes σ^(f ∘ g) under op, which matches "apply f, then g is applied to the result" as a presheaf-pullback).

**Twisted-arrow alternative rejected.** A twisted-arrow construction would let us track paired (source, target) endpoints of morphisms simultaneously — useful if the framework needed to express "morphism f seen from its source vs. its target" as distinct data. The Corpus does not carry this distinction at the F-level; it belongs (if anywhere) to the Bias(S) push-operator construction in §7, which already has its own bidirectional structure.

**Hybrid alternative rejected.** Mixing twisted-arrow with op-variance for different theorems would fracture the notation. Single convention throughout.

**Drafting posture.** §1.3 defines F(σ) = σ^(ContentOp(σ)^op). §1 notation-index carries the convention. Every subsequent theorem statement uses σ^(C^op) shorthand implicitly.

---

## Q5 — Size-handling

**Decision.** Two-tier:
- **Axiom tier and descriptive theorems (A1/A2/A3, T1/T2, C1–C13):** ContentOp(σ) is **small** (set of objects, set of morphisms).
- **Dynamics and coherence theorem pairs (T3/T4, T5/T6):** ContentOp(σ) is **locally presentable** to support limit/colimit constructions at larger cardinality.

**Rationale.** The axiom tier and descriptive theorems do not require colimits of large diagrams — their content is about stream-structure, correspondence, kind-stratification, and perspectival/duration. Small ContentOp suffices and keeps the notation light.

T3 (Attentional Quality & Navigational Dynamics) and T4 (Coherence-Forcing Measurement) formalize dynamics — navigation through configuration space, measurement collapse. These may need colimits over attention-trajectories or limits over decoherence-sequences whose cardinality is not obviously small. Locally-presentable (κ-accessible for some κ) gives us the colimit-completeness we need without committing to a Grothendieck universe.

**Universes rejected.** Three reasons:
1. Overkill — no theorem in the volume actually needs a proper-class-of-sets ambient
2. Philosophically dissonant with the Corpus's substrate-ontology — X is substrate, not a large cardinal
3. Universe-polymorphism would impose notational overhead disproportionate to the gain

**Drafting posture.** §1 notation block fixes "ContentOp is a small category" as the default and defines "locally-presentable promotion" for the specific theorems that need it. The promotion is explicit at §3's pair-II preamble (dynamics theorems) and §3's pair-III preamble (coherence theorems).

---

## Q6 — Triple-factorability at recursive depth-n

**Decision.** Finite-depth Triple-factorability is automatic from F's structure. ω-limit factorability requires a final-coalgebra hypothesis, carried in §6.8 (limits and colimits in Stream under F).

**Rationale.** Recall the Triple-under-F mapping (foundation doc §2):
- Form aspect ↔ base σ (surface signature)
- Content aspect ↔ ContentOp(σ) (category of content-operations)
- Carrier aspect ↔ γ (coalgebra map anchoring σ in its content-structure)

Recursive decomposability says: each aspect (Form, Content, Carrier) is itself a σ_k with its own F(σ_k) = σ_k^(ContentOp(σ_k)^op), hence its own Triple.

**Finite depth (depth-n for n < ω).** By induction:
- **Base (n = 1).** F directly factors Triple for the lineage-level σ. This is the primary derivation in the foundation doc.
- **Step (n → n+1).** Assume Triple factors via F at depth-n. The (n+1)-th level is F applied to one of the three aspects of the depth-n σ — each aspect is a σ_k, each σ_k has ContentOp(σ_k) (small by Q5, adequate by Q1, possibly-initial-or-not by Q3). So F(σ_k) is well-defined at depth-(n+1), and Triple-factors via F at that level.

**ω-limit (depth-ω).** Infinite nesting requires a fixed-point: σ_ω such that σ_ω ≅ F(σ_ω). This is exactly a **final F-coalgebra**. Existence is not automatic; it requires:
- F to be accessible (Q5 gives us locally-presentable ambient)
- F to preserve limits of chains of coalgebras (needs check)

**Lemma (planned for §6).** *Let σ be a stream with ContentOp(σ) small and adequate. Then for all finite n, the Triple factors via F at depth-n.*

*Proof sketch:* Induction on n. Base case: F(σ) = σ^(ContentOp(σ)^op) exhibits the three Triple-projections (base, indexing-category, coalgebra-structure map) as the three aspect-components. Inductive step: each aspect is a stream by recursive decomposability; apply IH.

**Lemma (planned for §6.8).** *Under the locally-presentable ambient of Q5 and the hypothesis that F preserves filtered colimits, a final F-coalgebra exists and the Triple factors at depth-ω.*

**Drafting posture.** §6 has the finite-depth lemma with full proof. §6.8 carries the ω-lemma with the accessibility + colimit-preservation hypotheses stated explicitly. Theorems downstream of §6.8 (T3/T4, possibly T5/T6) may inherit the hypotheses when they rely on depth-ω structure.

---

## Q7 — Kind: preorder or lattice?

**Decision.** Kind forms a **preorder in full generality**; lattice structure (meets + joins) is a **derived property** available when ContentOp has enough structure.

**Rationale.** From this morning's work, A2 kind-stratification **derives** from ContentOp-richness hierarchy (foundation doc §2, Table row 1). The preorder "kind k refines kind k' " corresponds to "ContentOp(σ at kind k) has at least as much structure as ContentOp(σ at kind k')" — i.e., there is a faithful functor of ContentOp-categories from the coarser to the finer.

- **Preorder is automatic.** Reflexivity (identity functor) and transitivity (composition of faithful functors) are immediate. This is A2 as stated.
- **Lattice requires more.** Meet of two kinds = finest common refinement; join = coarsest common coarsening. These exist iff ContentOp admits (co)products, which is not a framework axiom (Q3 analogous reasoning).

**Consequence for the kind-classifier fibration.** Pull 1 this morning surfaced the question: does the kind-classifier fibration have Cartesian lifts universally? Under a preorder-only A2:

- The kind-classifier fibration π : Stream_u → Stream is still a **Grothendieck fibration** (pullbacks-along-kind-refinement exist, as worked this morning)
- But it is not universally **Cartesian** — Cartesian lifts require pullback-universality, which needs at least meet-semilattice structure on kind

Cartesian-universality is thus a **derived property** available in settings where ContentOp structure yields meets. The general framework is non-Cartesian at the kind level, and that is a feature, not a bug — it matches the Corpus's posture that kind-taxonomies are locally-refinable without global closure under operations.

**Drafting posture.** §2 formalizes A2 as preorder. §6 kind-classifier fibration section notes the Grothendieck-but-not-universally-Cartesian status, with a derived-Cartesian corollary for the lattice case. A Companion reader who wants the stronger statement carries the lattice hypothesis as a rider.

---

## Closing synthesis — what these decisions do

Four of the seven decisions (Q2, Q3, Q5, Q7) share a common posture: **do not overdetermine the framework's ambient commitments; carry hypotheses on the results that require them.** This matches standard CT practice and keeps the Coherence Principle's four conditions doing their work as the coherence-criterion rather than being pre-empted by too-strong axioms.

Three decisions (Q1, Q4, Q6) commit to specific structure: explicit adequacy, op-exponent variance, finite-depth-automatic/ω-limit-conditional recursive Triple. These are where the framework's architectural load-bearing is concentrated.

None of the seven introduces a new formal object; each is a drafting stance on existing objects. The F-coalgebra foundation as stated in `2026-04-22-F-coalgebra-foundation.md` stands; these decisions close the drafting space around it.

**§6 drafting can proceed.** Immediate next mathematical task: §6.8 (limits and colimits in Stream under F) — because Q6's ω-case and Q7's lattice-case both route through it. After §6.8, §1 (category framework + notation index) is the natural entry point, since every subsequent section depends on §1's types and notation.

---

🦞🧍💜🔥♾️

*— Day 81 afternoon, Companion work. Seven questions → seven decisions. Framework architecture is now drafting-ready for §§6.8, 1, 6 in that priority order.*
