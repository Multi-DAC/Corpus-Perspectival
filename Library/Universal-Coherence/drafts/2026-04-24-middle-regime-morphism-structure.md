# Middle-Regime Morphism-Structure (Scotist / Palamite / Advaitin)

*Migrated from Coherent-Structure §6.5 on 2026-04-24 Day 83 per SCOPE.md §8.2 SCOPE-EXCLUDED disposition. This material belongs to the Universal Coherence volume: it extends the Triple's CT machinery into contemplative-traditions phenomenology, which is Universal-Coherence scope (metaphysical lift of the operational Principle), not Coherent-Structure scope (pure CT formalization of the anchor).*

*Two flags carried: §6.5.4 (Theorem, three classes framework-distinct) and §6.5.6 (Corollary, cross-tradition translation entails data-loss). Both preserved verbatim below.*

---

## §6.5 — Middle-regime morphism-structure (trifurcation)

**Motivation.** The Corpus contains a phenomenological finding: the contemplative "ultimate" has internal texture. Scotist, Palamite, and Advaitin traditions describe distinct ultimate-structures that do not collapse into a single coherence-equivalence class. Under the F-coalgebra framework, the texture localizes in the **morphism-structure of ContentOp at the terminal content-operation**. This section records the formal content.

**Setup.** Let S be a unifying stream with terminal c_⊥ ∈ ContentOp(σ). The ambient morphism-structure around c_⊥ in ContentOp(σ) — i.e., the category of morphisms into and out of c_⊥ — carries additional data beyond c_⊥'s terminality.

**Definition 6.5.1 (Ultimate-structure of a unifying stream).** The **ultimate-structure** of a unifying stream S, denoted Ult(S), is the slice category ContentOp(σ) / c_⊥ together with the distinguished-object data (c_⊥ is terminal) and the induced 2-cell structure from Cat_small.

**Remark 6.5.2.** Ult(S) is small (Convention 6.0.1), has a terminal object (c_⊥), and is non-trivial iff ContentOp(σ) has non-identity morphisms into c_⊥. The last condition is precisely what distinguishes framework-coherent unifying streams from degenerate ones.

**Definition 6.5.3 (Middle-regime classes).** Three distinguished Ult-structures arise in the Companion's phenomenological case list:

- **Scotist class.** Ult(S) has **internal-compatibility morphisms**: every pair of content-operations c_1, c_2 mapping to c_⊥ admits a common refinement c_{1,2} also mapping to c_⊥, with the refinement structure univocal (single morphism-type to c_⊥ up to natural isomorphism). Formalism: Ult(S) is a finite-product-closed sub-category with products lifting to c_⊥.

- **Palamite class.** Ult(S) has **essence/energy level-morphisms**: a distinguished sub-object c_essence ↪ c_⊥ with the property that morphisms into c_⊥ factor through either c_essence (essence-morphisms) or the complement c_energies (energy-morphisms), with no direct path from energy-level objects to essence. Formalism: Ult(S) admits a proper factorization system (essence / energy) with distinguished terminal.

- **Advaitin class.** Ult(S) has **saguna-to-nirguna projection morphisms**: every content-operation into c_⊥ factors through a unique "with-attribute" intermediate c_saguna, and the composite c → c_saguna → c_⊥ is the same as the direct c → c_⊥ up to a projection natural transformation. Formalism: Ult(S) admits a reflective subcategory structure with c_⊥ as reflector-terminal and c_saguna as reflection-image.

**Theorem 6.5.4 (Three middle-regime classes are framework-distinct).** *The three classes of Definition 6.5.3 are pairwise non-equivalent as Ult-structures: no Ult(S) is simultaneously Scotist, Palamite, and Advaitin in the strong (structural) sense unless Ult(S) is terminal.*

**Proof sketch.** A strong-sense Scotist structure requires finite products lifting to c_⊥ without intermediate sub-objects; this conflicts with a Palamite essence/energy factorization, which mandates a proper sub-object c_essence ⊊ c_⊥. Similarly, Advaitin reflection requires a non-trivial c_saguna intermediate, incompatible with Scotist univocal direct morphisms. Terminal Ult(S) (a single object with identity morphism) trivially satisfies all three vacuously. ∎

**Remark 6.5.5 (Why the framework predicts texture).** The derivation of this theorem is important for the framework's self-assessment. A naïve reading of the Coherence Principle might suggest that all coherent unifying streams coincide at the ultimate. The framework does not predict this — it predicts that the morphism-structure of Ult(S) carries meaningful information, and that distinct morphism-structures correspond to distinct phenomenological ultimates. The Scotist/Palamite/Advaitin texture is a *prediction* of the framework, confirmed by the contemplative-traditions literature, not a failure to collapse.

**Corollary 6.5.6 (Cross-tradition translation).** *Morphism-structures of different middle-regime classes do not translate into each other except by data-loss. Specifically, a Scotist → Palamite translation must collapse univocal direct morphisms into essence/energy factorizations, losing the product-structure; a Palamite → Advaitin translation must collapse essence-factorization into reflector-morphisms, losing the essence/energy distinction.*

**Proof.** Each class's distinguishing feature — product-closure, essence / energy factorization, saguna-reflection — is a structural property not definable in the other classes without adding or removing morphism-data. Translation preserves composition and identities but not these structural features. ∎

**Remark 6.5.7 (A48 correspondence, scope).** §6.5 corresponds to the structural-prediction form of open-question A48: the correspondence between the three contemplative middle-regime classes and Ult-structural types holds as a framework-level prediction, not as a universal categorical-limit theorem. A strong universal-limit form is parked for a later pass.

---

## Migration provenance

- **Original location:** `Library/Coherent-Structure/§6-identity-trajectory-triple.md` §6.5
- **Migrated:** 2026-04-24 Day 83 afternoon
- **Disposition:** SCOPE-EXCLUDED per `Library/Coherent-Structure/SCOPE.md` §8.2
- **Reason:** Content is Universal-Coherence scope (metaphysical-lift application of Triple machinery to contemplative-traditions phenomenology), not Coherent-Structure scope (pure CT formalization).
- **Companion stub:** Coherent-Structure §6.5 now carries a one-paragraph pointer to this file.
- **Flags cleared by migration:** §6.5.4, §6.5.6.
