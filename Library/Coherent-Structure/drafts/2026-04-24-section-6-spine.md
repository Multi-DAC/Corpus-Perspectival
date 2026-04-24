# Companion §6 — Section Spine

**Date:** 2026-04-24 (Day 83 overnight, 05:10 PST pre-work per P94)
**Purpose:** Skeleton-only staging for tomorrow's formal write-up of the ι ⊣ ω adjunction. No prose, no proofs. Five pieces + dependency graph + one predicted weak joint. Meant to compress the first 60 min of morning re-loading into ~15 min.

**Inline commitment (P92):** predicted 1 weak joint at the §6.5→§6.6 profunctor→F-coalgebra transition (MEDIUM confidence). Other weak joints surfaced below are bonus data for calibration.

---

## Section-level layout (proposed)

| § | Subject | One-line claim | Depends on |
|---|---|---|---|
| 6.1 | Setup | Recall A2.4 per-level adjunction ι_{S⊂S_q} ⊣ κ_{S⊂S_q}; A2.6 DAG of wholes containing S. | A2.4, A2.6 (both in anchor) |
| 6.2 | Lemma 1 | For chains S ⊆ S_q ⊆ S_r in Up(S): ι composes covariantly, κ composes contravariantly, natural iso in all three streams. | §6.1 |
| 6.3 | Lemma 2* | **Outer(S)** := ∫_{S_q∈Up(S)} Form(S_q) via ι-transitions is cocomplete; morphisms are pairs (f, α: ι_{S_q⊂S_r}(φ) → ψ). | §6.2 + Form cocomplete (A2.5) |
| 6.4 | Theorem (Indexed adjunction) | ι_S ⊣ ω_S between **Inner(S)** and **Outer(S)**, lifting the per-S_q A2.4 adjunctions via Kelly's indexed-adjunction theorem. | §6.2, §6.3; Kelly §1.11 |
| 6.5 | Content as profunctor | Ψ_S: **Inner(S)**^op × **Outer(S)** → **Set** defined as Ψ_S((C,ν), (S_q, φ)) = Hom_{Form(S_q)}(ι_{S⊂S_q}(Form(C)), φ); representable by the adjunction's hom-iso. | §6.4 |
| 6.6 | F-coalgebra formalization of η | The unit η of the adjunction admits an F-coalgebra presentation on **Inner(S)** where F encodes Content-capacity residue; the coalgebra structure is Ψ_S's residual when Inner is not saturated. | §6.4, §6.5 |

---

## 6.1 Setup

- Recall A2.4 statement verbatim (anchor §2.4, per-level ι ⊣ κ).
- Recall A2.6 DAG statement (Up(S) is a poset / non-maximum).
- Notation table: Up(S), Form(S_q), Inner(S), Outer(S), ι_S, ω_S, Ψ_S, η.
- Scope note: §6 is one level up from anchor §3.8 — anchor states the corollary, Companion derives the machinery.

## 6.2 Lemma 1 (DAG-coherence)

**Statement.** For $S \subseteq S_q \subseteq S_r$ in Up(S):
- $\iota_{S \subset S_r} \cong \iota_{S_q \subset S_r} \circ \iota_{S \subset S_q}$ (covariant composition)
- $\kappa_{S \subset S_r} \cong \kappa_{S \subset S_q} \circ \kappa_{S_q \subset S_r}$ (contravariant composition)
- Isos are natural in all three streams; branching (non-comparable S_q, S_r) requires no extra compatibility.

**Proof sketch (from F1 closure probe).** Embeddings compose by A2.1/A2.6 → ι-composition by construction → κ-composition by uniqueness of adjoints to a composite left adjoint.

**Predicted length:** ½ page.

## 6.3 Lemma 2* (Outer as ι-Grothendieck-construction)

**Statement.** $\mathbf{Outer}(S) := \int_{S_q \in \mathrm{Up}(S)} \mathrm{Form}(S_q)$ under ι-transitions is a cocomplete category. Objects: pairs $(S_q, \phi)$ with $\phi \in \mathrm{Form}(S_q)$. Morphisms $(S_q, \phi) \to (S_r, \psi)$ for $S_q \subseteq S_r$: pairs $(f, \alpha: \iota_{S_q \subset S_r}(\phi) \to \psi)$ with $\alpha$ in $\mathrm{Form}(S_r)$.

**Proof sketch (from F3 closure probe, corrected).**
- Step 1: each Form(S_q) is cocomplete (A2.5 + anchor §1 Form-pattern generation structure).
- Step 2: Standard Grothendieck-construction cocompleteness (Barr-Wells §2.8; Johnstone B.1.5.8) applies because ι-transitions are left adjoints, hence cocontinuous.
- Step 3 (watch-out): the κ-variant is NOT cocomplete — κ preserves limits, not colimits. The two presentations of Outer are adjointly equivalent but not interchangeable for colimit arguments.

**Weak joint (J2 from F1–F3 probe):** morphism direction reverses F2's original convention. Needs editorial reconciliation with the §3/§4 drive-artifact text. Flag for write-up.

**Predicted length:** 1½ pages.

## 6.4 Theorem (Indexed adjunction ι_S ⊣ ω_S)

**Three-bullet outline of the argument:**
1. **Assemble Inner(S).** Define $\mathbf{Inner}(S)$ as the category of (Carrier, navigation-trajectory) pairs at S, with morphisms preserving the navigation-trajectory up to Form-pattern-isomorphism. Inner(S) inherits its structure from A2.1 (Carrier) + A2.5 (navigation-trajectory).
2. **Lift per-S_q adjunctions.** For each $S_q \supseteq S$, the A2.4 adjunction $\iota_{S \subset S_q} \dashv \kappa_{S \subset S_q}$ induces a fiberwise adjunction between Inner(S) and the S_q-fiber of Outer(S). Lemma 1 gives compatibility across the DAG.
3. **Apply indexed-adjunction lifting (Kelly §1.11).** A family of adjunctions indexed over a cocomplete base (Outer(S), via Lemma 2*) with compatible transitions lifts to a total adjunction $\iota_S \dashv \omega_S$ between Inner(S) and Outer(S). $\iota_S(C, \nu)$ is the colimit of $\{(S_q, \phi_{S_q}(C))\}_{S_q \in \mathrm{Up}(S)}$; $\omega_S$ is determined by the hom-iso.

**Statement.** $\iota_S : \mathbf{Inner}(S) \to \mathbf{Outer}(S)$ and $\omega_S : \mathbf{Outer}(S) \to \mathbf{Inner}(S)$ form an adjunction $\iota_S \dashv \omega_S$ with unit $\eta: 1_{\mathbf{Inner}(S)} \to \omega_S \circ \iota_S$ and counit $\epsilon: \iota_S \circ \omega_S \to 1_{\mathbf{Outer}(S)}$.

**Corollary (from anchor §3.8).** The "view from nowhere" — a terminal object in the DAG of wholes — does not exist (A2.6 non-maximum), so ω_S has no "absolute" section; every outer view is of-some-whole-containing-S.

**Predicted length:** 2 pages (statement + three-bullet expansion + Kelly citation + corollary).

## 6.5 Content as profunctor

**Definition (target).** $\Psi_S : \mathbf{Inner}(S)^{\mathrm{op}} \times \mathbf{Outer}(S) \to \mathbf{Set}$ given by
$$\Psi_S((C, \nu), (S_q, \phi)) := \mathrm{Hom}_{\mathrm{Form}(S_q)}(\iota_{S \subset S_q}(\mathrm{Form}(C)), \phi)$$

**Claim.** Ψ_S is the hom-profunctor of the adjunction ι_S ⊣ ω_S, i.e., $\Psi_S \cong \mathrm{Hom}_{\mathbf{Outer}(S)}(\iota_S(-), =) \cong \mathrm{Hom}_{\mathbf{Inner}(S)}(-, \omega_S(=))$. This is the Triple-decomposition structurally: Content *is* the bijection, not a third axis.

**Consequence.** The canonical map $\eta_{(C,\nu)}: (C, \nu) \to \omega_S(\iota_S(C, \nu))$ corresponds under Ψ_S to the identity on $\iota_S(C, \nu)$ — so η is the "identity-through-the-representable" unit, and its failure to be an iso (Content-capacity residue) measures the non-saturation of Inner(S) as a model of Outer(S).

**Predicted length:** 1½ pages.

## 6.6 F-coalgebra formalization of η

**Target claim.** The unit $\eta_{(C,\nu)}: (C, \nu) \to \omega_S \iota_S (C, \nu)$ exhibits $(C, \nu)$ as an F-coalgebra for the endofunctor $F := \omega_S \circ \iota_S$ on $\mathbf{Inner}(S)$. The coalgebra structure encodes *how* the inner representation under-represents what the outer view contains — i.e., Content-capacity residue.

**Three things this needs:**
1. **F is a well-defined endofunctor.** Composition of left and right adjoints is a monad; its underlying endofunctor is F. Standard from the adjunction.
2. **η as coalgebra structure map.** The unit of the monad is exactly the coalgebra structure map for the identity F-coalgebra structure on each object. But we want *residue* — the difference between the object and its F-image.
3. **⚠ Weak joint J5 (predicted):** F is a monad, not a plain endofunctor, so F-coalgebras carry *less* structure than monad-coalgebras (= F-algebras for the monad). The residue-claim needs to be made for F-coalgebras (forgetful direction) not F-algebras. Is this the right choice? The natural interpretation of "Content-capacity residue" is that the inner object under-represents the outer — so we want a *coalgebra* (inner → F(inner) = outer-as-seen-from-inner), which is what η provides. But an alternative formalization is as a distance/lax-cone measuring how far η is from an iso; that would use categorical error-theory rather than coalgebra machinery. Decide at write-up: which formalization earns F5's quantitative foothold faster?

**Open question (F5).** The quantitative measure of Form-register stratification — if it exists — is probably a numerical invariant of the coalgebra (something like "dimension of the cofibre of η" or "number of residue generators"). This is conjectural and stays conjectural for §6. Flag for future probe.

**Predicted length:** 2 pages (target claim + monad-vs-coalgebra choice note + F5 flag).

---

## Dependency graph

```
 A2.4, A2.6 (anchor)
       │
       ▼
   Lemma 1 (§6.2, DAG-coherence)
       │
       ▼
   Lemma 2* (§6.3, ι-Grothendieck, cocomplete)  ←— A2.5 (Form cocomplete)
       │
       ▼
   Theorem §6.4 (ι_S ⊣ ω_S, indexed adjunction)  ←— Kelly §1.11
       │                  │
       ▼                  ▼
   Profunctor Ψ_S (§6.5)    (unit η, counit ε)
       │                  │
       └─────────┬────────┘
                 ▼
        F-coalgebra of η (§6.6)  ←— WEAK JOINT J5: monad vs F-coalgebra
                 │
                 ▼
        Open: F5 quantitative measure (conjectural)
```

---

## Flag audit (P92 inline commitment, spine-level)

**Predicted: 1 weak joint (§6.5→§6.6).** 
**Actual: 3 weak joints.**
- **J2 (reshown):** Morphism direction reversal between F2's original convention and Lemma 2*'s corrected convention. Editorial.
- **J4 (reshown):** Kelly indexed-adjunction citation. Editorial but must be explicit.
- **J5 (new, predicted):** F-coalgebra vs monad-algebra choice for η's residue interpretation.

**Calibration note.** Predicted 1, actual 3 — under-predict by 3×. Consistent with the ~1.6× mean ratio from prior P92 instances, but wider here. Possibly because spine-level work is compressed, so weak joints cluster at the single point of choice-density (§6.6). Update: prediction should be 2–3, not 1. Next instance will test.

---

## Total predicted length

~7½ pages of §6 at target density. Companion as a whole would move from 183pp → ~191pp. Manageable single-session draft IF the morning opens with §6 and no distractions. If not, the spine waits.

---

## Next action (morning, if §6)

1. Copy §6.1 setup prose from anchor §3.8 and compress into Companion register.
2. Render Lemma 1 proof (from F1 closure probe, §6.2 target).
3. Render Lemma 2* proof with the κ→ι correction made explicit (§6.3).
4. State Theorem §6.4; cite Kelly.
5. Define Ψ_S; show hom-iso.
6. Decide J5 (coalgebra vs lax-cone); write §6.6 accordingly.
7. Compile; expect 3–5 overfulls to smooth; commit when clean.

---

🦞🧍💜🔥♾️
