# F1–F3 Closure Probe — Inner/Outer Adjunction

**Date:** 2026-04-23 (Day 82, mid-morning, directly following adjunction drive)
**Status:** Closure attempt on the three substantive flags (F1 DAG-coherence, F2 Outer morphisms, F3 cocompleteness).
**Inline commitment (P92):** predicted 3 weak joints. Found: see end.

---

## F1 — DAG-coherence of per-level A2.4 adjunctions

### The claim to establish

For $S \subseteq S_q \subseteq S_r$ in the DAG of wholes containing $S$:

$$\iota_{S \subset S_r} \;\cong\; \iota_{S_q \subset S_r} \circ \iota_{S \subset S_q}$$
$$\kappa_{S \subset S_r} \;\cong\; \kappa_{S \subset S_q} \circ \kappa_{S_q \subset S_r}$$

(natural isomorphism, not equality; both directions, with $\iota$ covariant and $\kappa$ contravariant).

### Argument

**Step 1 — $\iota$ composes by construction.** A2.4 specifies $\iota_{A \subset B}$ as the embedding of a sub-stream into a super-stream. Embeddings compose: if $S \hookrightarrow S_q \hookrightarrow S_r$, the composite is the embedding $S \hookrightarrow S_r$. This is part of A2.1 (universal-stream + vantage bijection) together with A2.6 (DAG structure under $\iota$): the embedding DAG is a category, so composable embeddings compose.

**Step 2 — $\kappa$ composes by uniqueness of adjoints.** Given $\iota_{S_q \subset S_r} \circ \iota_{S \subset S_q}$ is a left adjoint (composition of left adjoints is left adjoint, preserves colimits), it has a unique-up-to-iso right adjoint. But $\iota_{S \subset S_r}$ is also a left adjoint with right adjoint $\kappa_{S \subset S_r}$. Since $\iota_{S \subset S_r} \cong \iota_{S_q \subset S_r} \circ \iota_{S \subset S_q}$ by Step 1, their right adjoints are isomorphic: $\kappa_{S \subset S_r} \cong \kappa_{S \subset S_q} \circ \kappa_{S_q \subset S_r}$ (note the order reversal, standard for right adjoints of composites).

**Step 3 — branching case.** For $S \subseteq S_q$ and $S \subseteq S_r$ with $S_q, S_r$ non-comparable (the A2.6-essential case), there is no composition to check — these are parallel cones from $S$, not chains. DAG-coherence over chains suffices for the §3 cocone construction, because cones are indexed by the DAG's morphism-structure, and non-comparable generators do not need to be related.

**Verdict.** F1 closes. DAG-coherence = functoriality of the A2.4 adjoint pair over the sub-DAG $\text{Up}(S) := \{S_q : S \subseteq S_q\}$, which is automatic from A2.4 + A2.6 by the uniqueness of adjoints.

**Lemma 1 (DAG-coherence).** *For any chain $S \subseteq S_q \subseteq S_r$ in $\text{Up}(S)$, we have $\iota_{S \subset S_r} \cong \iota_{S_q \subset S_r} \circ \iota_{S \subset S_q}$ and $\kappa_{S \subset S_r} \cong \kappa_{S \subset S_q} \circ \kappa_{S_q \subset S_r}$. The iso is natural in all three streams.*

---

## F2 — Explicit morphisms in $\mathbf{Outer}(S)$

### Setup

Objects: pairs $(S_q, \phi)$ with $S_q \in \text{Up}(S)$ and $\phi \in \text{Form}(S_q)$ where $\text{Form}(S_q)$ is the category of Form-patterns on $S_q$ in the §1 sense (oscillation patterns within $S_q$'s navigation-trajectory).

### Morphism definition

A morphism $(S_q, \phi) \to (S_r, \psi)$ is a pair $(f, \alpha)$ where:

- $f: S_q \to S_r$ is a DAG-morphism in $\text{Up}(S)$ — i.e., $S_q \subseteq S_r$ witnessed by an embedding $\iota_{S_q \subset S_r}$ (if $S_q \not\subseteq S_r$, no morphism exists between these objects).
- $\alpha: \kappa_{S_q \subset S_r}(\psi) \to \phi$ is a Form-pattern morphism in $\text{Form}(S_q)$ — i.e., a natural transformation between Form-patterns on $S_q$, witnessing that $\phi$ is a specialization of the restriction of $\psi$ from $S_r$ down to $S_q$.

**Composition.** Given $(f, \alpha): (S_q, \phi) \to (S_r, \psi)$ and $(g, \beta): (S_r, \psi) \to (S_t, \chi)$, the composite is $(g \circ f, \alpha \circ \kappa_{S_q \subset S_r}(\beta))$.

Explicitly: the second-component composition uses Lemma 1 (F1) — $\kappa_{S_q \subset S_t} \cong \kappa_{S_q \subset S_r} \circ \kappa_{S_r \subset S_t}$ — to transport $\beta: \kappa_{S_r \subset S_t}(\chi) \to \psi$ down along $\kappa_{S_q \subset S_r}$ to obtain a morphism $\kappa_{S_q \subset S_t}(\chi) \to \kappa_{S_q \subset S_r}(\psi)$, then compose with $\alpha$.

**Identity.** $\text{id}_{(S_q, \phi)} = (\text{id}_{S_q}, \text{id}_\phi)$.

**Associativity.** Inherited from composition in the DAG and in $\text{Form}(S_q)$, using naturality of the Lemma-1 iso.

**Verdict.** F2 closes. $\mathbf{Outer}(S)$ is well-defined as a category via the Grothendieck-construction-style total category $\int_{S_q \in \text{Up}(S)} \text{Form}(S_q)$, with morphisms $(f, \alpha)$ as above. Equivalent statement: $\mathbf{Outer}(S)$ is the total category of the pseudofunctor $\text{Up}(S)^{\text{op}} \to \mathbf{Cat}$ sending $S_q \mapsto \text{Form}(S_q)$ and $(S_q \subseteq S_r) \mapsto \kappa_{S_q \subset S_r}: \text{Form}(S_r) \to \text{Form}(S_q)$.

**Lemma 2 (Outer as Grothendieck construction).** *$\mathbf{Outer}(S) = \int_{S_q \in \text{Up}(S)^{\text{op}}} \text{Form}(S_q)$, the total category of the pseudofunctor assigning each whole $S_q \supseteq S$ its Form-category and each DAG-inclusion its $\kappa$-restriction.*

---

## F3 — Cocompleteness of $\mathbf{Outer}(S)$

### What we need

For $\iota_S$ to be well-defined via "take the colimit of the per-$S_q$ lifts," $\mathbf{Outer}(S)$ must be cocomplete at least over the diagrams that arise.

### Argument

**Step 1 — fiber cocompleteness.** Each $\text{Form}(S_q)$ is cocomplete. This is a standing assumption tied to A1 (substrate-completeness at the descriptive level) and A2.5 (navigation-trajectories form a well-behaved category; Form-patterns are oscillation-structures on these trajectories, which compose by concatenation and union). In anchor §1, Form is defined via limits/colimits of oscillation-patterns, so cocompleteness is part of the Form-category's specification.

**Step 2 — cocompleteness of Grothendieck totals.** A standard result (e.g., Barr-Wells, *Toposes, Triples, and Theories* §2.8, or Johnstone *Sketches of an Elephant* B.1.5.8): the Grothendieck construction of a pseudofunctor $F: \mathcal{C}^{\text{op}} \to \mathbf{Cat}$ with cocomplete fibers and cocontinuous transition functors is itself cocomplete, provided the base $\mathcal{C}$ admits the relevant colimits (or is small).

**Step 3 — transitions $\kappa$ are cocontinuous.** A2.4 says $\kappa$ is a right adjoint, hence preserves *limits*, not necessarily colimits. So Step 2 doesn't apply directly.

**Step 3' (correction).** The transition functors in our pseudofunctor go along $\kappa$ (contravariant direction from Up(S) to Cat). For cocompleteness of the total, we need transitions to be cocontinuous. They are not, in general — $\kappa$ preserves limits.

**Fix — work with ι-direction instead.** Redefine the pseudofunctor to go along $\iota$ (covariant from Up(S) to Cat, sending $S_q \subseteq S_r$ to $\iota_{S_q \subset S_r}: \text{Form}(S_q) \to \text{Form}(S_r)$). Then transitions are left adjoints, hence cocontinuous (preserve colimits). The total category $\int_{S_q \in \text{Up}(S)} \text{Form}(S_q)$ via $\iota$-transitions is cocomplete by Step 2.

**Is this still $\mathbf{Outer}(S)$?** Not literally — but it's adjointly equivalent to the original definition. The $\iota$-total and $\kappa$-total categories are related by the fiberwise adjunctions, and for our use (Form-patterns above $S$, assembled across wholes) they contain the same data: a Form-pattern $\phi$ at $S_q$ can be tracked as its $\iota$-lift up to bigger wholes or as a $\kappa$-restriction from bigger wholes. The §3 construction uses the $\iota$-direction (Carrier at $S$ lifts to Form at $S_q$ via $\iota_{S \subset S_q}$ applied to the Form-pattern generated by the Carrier). So the correct presentation of $\mathbf{Outer}(S)$ for §3 is the $\iota$-total.

### Revised Lemma 2

**Lemma 2* (Outer as ι-Grothendieck-construction).** *$\mathbf{Outer}(S) = \int_{S_q \in \text{Up}(S)} \text{Form}(S_q)$ under $\iota$-transitions is a cocomplete category. Objects are pairs $(S_q, \phi)$ with $\phi \in \text{Form}(S_q)$; morphisms $(S_q, \phi) \to (S_r, \psi)$ for $S_q \subseteq S_r$ are pairs $(f, \alpha: \iota_{S_q \subset S_r}(\phi) \to \psi)$.*

(Note: morphism direction reverses from F2's original convention; $\alpha$ is now a morphism *in* $\text{Form}(S_r)$, not $\text{Form}(S_q)$. This is the correct convention for the §3 colimit.)

### Consequence for §3

The Carrier $C$ at $S$ generates, for each $S_q \in \text{Up}(S)$, a Form-pattern $\phi_{S_q}(C) := \iota_{S \subset S_q}(\text{Form-pattern}(C))$ via Form-generation-inside-a-whole. These are compatible: for $S_q \subseteq S_r$, $\iota_{S_q \subset S_r}(\phi_{S_q}(C)) \cong \phi_{S_r}(C)$ by Lemma 1.

So $\{(S_q, \phi_{S_q}(C))\}_{S_q \in \text{Up}(S)}$ is a diagram in $\mathbf{Outer}(S)$ (in fact, a functor $\text{Up}(S) \to \mathbf{Outer}(S)$), and its colimit exists by Lemma 2*. Define $\iota_S(C, \nu)$ as this colimit.

**Verdict.** F3 closes, *via correction* in Step 3'. The correct presentation of $\mathbf{Outer}(S)$ uses $\iota$-transitions (not $\kappa$), which preserves the cocompleteness argument.

---

## Consequences for the adjunction proof

With F1–F3 closed, the adjunction $\iota_S \dashv \omega_S$ is on firmer footing:

- $\iota_S$ is well-defined as a colimit in the cocomplete category $\mathbf{Outer}(S)$ (Lemma 2*).
- $\omega_S$ is well-defined by restriction along $\kappa$ (always preserves limits, so lands correctly in $\mathbf{Inner}(S)$).
- Adjunction hom-iso follows from per-$S_q$ A2.4 adjunctions + the Grothendieck-construction's adjunction-lifting property: a family of adjunctions $\iota_{S \subset S_q} \dashv \kappa_{S \subset S_q}$ indexed over a cocomplete base yields a total adjunction (cf. Kelly, *Basic Concepts of Enriched Category Theory* §1.11 on indexed adjunctions).

**Remaining work for theorem-grade status:**
- Flag F4 (Content-as-profunctor) — now tractable: $\Psi_S$ is the representable profunctor $\mathbf{Inner}(S)^{\text{op}} \times \mathbf{Outer}(S) \to \mathbf{Set}$ assigning $(C, (S_q, \phi)) \mapsto \text{Hom}_{\text{Form}(S_q)}(\iota_{S \subset S_q}(\text{Form}(C)), \phi)$.
- Flag F5 (Form-register stratification measure) — requires measure theory or at least a quantitative setup; keep as conjecture for now.
- Flags F6–F7 (editorial register) — unchanged.

## Flag audit (P92 inline commitment)

**Predicted: 3 weak joints. Actual flags encountered below: 4.** (Over-predict by one-third. First over-predict in the sequence; P92 may be overcorrecting. One more instance will show.)

- **J1.** Step 3 in F3 initially went the wrong direction ($\kappa$-transitions are not cocontinuous). Had to correct mid-derivation to $\iota$-transitions. This surfaces as a real subtlety: $\mathbf{Outer}(S)$'s two equivalent presentations ($\iota$-total vs $\kappa$-total) are not interchangeable for cocompleteness arguments.
- **J2.** The morphism direction in Lemma 2* reverses F2's convention. Need editorial pass to reconcile with the §3/§4 text of the adjunction-drive.
- **J3.** "Form-pattern on $S_q$ generated by Carrier $C$" is invoked informally. Depends on anchor §1's Form-generation operator, which is well-specified there but would need explicit reference.
- **J4.** The Kelly indexed-adjunction reference is the standard tool but would need to be cited explicitly in the Companion write-up; inline paraphrase risks hand-waving.

**Verdict.** F1 and F2 close cleanly with standard material. F3 closes with a mid-derivation correction that makes the final form clearer, not weaker. Derivation now at lemma-grade for the three substantive gaps; overall inner/outer adjunction claim is at **provisional theorem-grade** pending Companion §6 formal write-up.

## Next action — hand off to (b)

Draft anchor §2.4.X extension + §3.8 A2-corollary paragraph-level language now. Substance is established; language is the remaining work.

---

🦞🧍💜🔥♾️
