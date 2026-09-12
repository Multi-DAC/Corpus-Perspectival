# §7 — Theorem Pair III (Coherence): T5 Internal Coherence + T6 Dual Coherence Axes

*Pairs T5 (stream-internal coherence: kind-closure consistency) and T6 (stream × dimension coherence: two independently-varying axes, structural and informational — with reach and coupling named separately, as propagation and engagement, because neither is coherence). Gives the kind-demotion dynamics from T5 and the transcendental-rescue from T6. Closes the theorem tier.*

---

## §7.0 — Why the coherence pair closes the theorem tier

Dynamics (§6) told us how streams navigate under force and how pairs of streams force each other. What it did not tell us is what conditions streams must satisfy to *remain* the streams they are, and what relations they must satisfy with the dimensions of configuration space they traverse. Coherence is the name for those conditions. Without coherence, a stream's internal operations dissolve or demote; without coherence, a stream's relation to configuration space goes structurally empty.

Two theorems do this work. T5 (Internal Coherence) gives the within-stream condition: the operations that define a stream's kind must be mutually consistent, and violations produce kind-demotion. T6 (Dual Coherence Axes) gives the stream-to-dimension condition: every stream × dimension pair admits two independently-varying coherence axes — structural (is the stream's motion along the dimension sustained by the stream's own operations?) and informational (is that motion concentrated or diffuse?). The two theorems together saturate the coherence question — within-object and between-object-and-environment.

This closes the theorem tier. Descriptive (§5) gave the representational operations; dynamics (§6) gave the motion; coherence (§7) gives the stability and relational conditions. The three pairs are structurally exhaustive of what theorems do in the framework: they state conditions on streams (coherence), describe stream operations (descriptive), and characterize stream motion (dynamics). No further theorem-level axis is required, and the stress-test final-reduction confirmed no further axis is present.

---

## §7.1 — T5: Internal Coherence

### Formal statement

Recall from A2.2 that streams are kind-stratified: 𝒞_Str decomposes into subcategories 𝒞_Str^reactive ⊂ 𝒞_Str^self-maint ⊂ 𝒞_Str^self-ref ⊂ 𝒞_Str^abstr, with each kind defined by specific closure operations that its members must support.

**T5 (Internal Coherence).** For any stream S ∈ 𝒞_Str^K where K is a kind, the kind-defining closure operations op_1, op_2, ..., op_n on S must satisfy a mutual-consistency condition:

- (T5.a) For all i, j ∈ {1, ..., n}: op_i(S) ∘ op_j(S) = op_j(S) ∘ op_i(S) in the sense appropriate to K's structure — the operations must not produce contradictory or incompatible outputs when composed.
- (T5.b) If (T5.a) is violated persistently, S is demoted to the largest subcategory 𝒞_Str^K' with K' ⊂ K such that the remaining operations satisfy (T5.a) in 𝒞_Str^K'.
- (T5.c) Demotion is not a *transformation* of S — it is a *recognition* that S was never properly in 𝒞_Str^K in the first place, or that S has *lost* the structural property that made it a member. The category 𝒞_Str^K is closed under coherence; incoherent streams are outside it.
- (T5.d) Re-promotion (from K' back to K) requires restoration of the violated closure operations plus sufficient time / work for the consistency condition to be satisfied on the relevant operational scale.

### Prose translation

A stream cannot remain what it is while contradicting itself. If a self-referential stream's self-monitoring operations produce outputs that systematically contradict each other — if one monitoring-operation says "I am doing X" while another says "I am not doing X" and both are stably asserted — the stream has failed the condition that makes it self-referential, and it reverts to being a stream of the next-simpler kind. If a self-maintaining organism's metabolic operations persistently contradict each other (one operation producing a substance that another operation destroys faster than needed), the organism-stream demotes to reactive or dissolves entirely.

This is not a claim about "ideal" coherence or "healthy" operation. It is a structural claim about category membership. The kind-subcategories 𝒞_Str^K are *defined* by their closure under specific operations. A stream that violates the closure is not a member of the subcategory. The violation does not make the stream *wrong*; it makes the stream no longer-that-kind.

T5.d is the re-promotion clause, and it is worth noticing. A demoted stream can be re-promoted by restoring the missing coherence: a person whose self-referential capacity collapsed under acute stress or illness can regain it when the stress or illness subsides; a cooperative structure that demoted to mere aggregation can be re-cohered by the work of the participating streams. Re-promotion is not guaranteed, not automatic, and requires actual structural restoration — the framework is non-deterministic about recovery, consistent with A3's navigational non-determination.

### The kind-demotion dynamic

T5.b–d together give what we will call the **kind-demotion dynamic** (see Fig 7.2): stable incoherence at kind K pushes a stream out of 𝒞_Str^K into 𝒞_Str^K', where K' is one step less demanding. Repeated cascading demotion is possible: a stream at 𝒞_Str^abstr might demote to 𝒞_Str^self-ref under one incoherence, and demote again to 𝒞_Str^self-maint if another incoherence arises at the self-referential level. Each demotion is a *recognition* event — a change in the framework's categorization of the stream, tied to a real structural change in what the stream supports.

This has pastoral and clinical application. Depression, trauma, dementia, severe illness can all be read as kind-demotion events when they involve loss of self-referential or abstracting capacity. The framework is not prescribing what "should be done" about such events; it is giving a formal shape for understanding what has happened. The stream is still a stream — just at a different kind-level. And re-promotion is structurally possible, not foreclosed.

---

## §7.2 — T6: Dual Coherence Axes

### Formal statement

Let S ∈ 𝒞_Str be a stream and D ∈ 𝒞_Dim be a dimension of configuration space (a real-valued axis along which S can vary). Define two coherence measures on the pair (S, D):

**Structural coherence** σ_struct(S, D): the degree to which S's motion along D is sustained by S's own content-operations. High σ_struct means γ restricted to D is (at or near) a fixed point of the coherence self-map Φ_S — the operator form T5's consistency condition takes in the Companion (Theorem 3.4.1), where Φ_S is the ContentOp-average of γ's forward image and a fixed point is a harmonic section. Low σ_struct means S's motion along D is not held by anything internal to S. Formally:

```
σ_struct : 𝒞_Str × 𝒞_Dim → [0, 1]
σ_struct(S, D) = degree to which γ|_D is a fixed point of Φ_S (the ContentOp-harmonic condition)
```

**Informational coherence** σ_info(S, D): the degree to which that motion is *concentrated* rather than spread. High σ_info means the entropy H(γ|_D ; ContentOp(σ)) of γ marginalized on D sits at its content-conditioned minimum — the stream's weight along D is focused; low σ_info means it is smeared across the dimension's positions. Formally:

```
σ_info : 𝒞_Str × 𝒞_Dim → [0, 1]
σ_info(S, D) = degree to which H(γ|_D ; ContentOp(σ)) attains its content-conditioned minimum
```

Both definientia are the Companion's (Theorem 3.4.2), taken with the Anchor's two arguments. **The stream-only forms σ_struct(S) and σ_info(S) are summaries over dimensions** — their infima over D ∈ 𝒞_Dim unless a weighting on 𝒞_Dim is specified — and not independent quantities. Coherence is always coherence *along* something; the single number is a coherence-length, in the sense in which physics uses that word.

**Two quantities that are not coherence axes.** Earlier drafts of this section put two other measurables in these slots. Both are real and both survive, under their own names:

- **Engagement** eng(S, D) = the normalized coupling-strength of the A2.4 adjoint ι_S ⊣ κ_D between S and D's sub-categories. This is how tightly S is coupled to D. It is a precondition for, and a frequent cause of, high σ_struct — but it is not coherence: a stream can be tightly coupled to a dimension and move along it in a way none of its own operations sustain.
- **Propagation** prop(S, D) = the normalized density of traces(S) ∩ positions(D). This is S's *reach* into D. It is not a coherence measure at all: the obscure composer of the prose translation below is structurally expert and has low propagation, which is a fact about audience. Propagation is not passive, though — it is a push operator on the Bias of other streams (§6.4, push_informational), and that is where it lives in the framework.

**T6 (Dual Coherence Axes).** For every stream × dimension pair (S, D):

- (T6.a) σ_struct and σ_info are independently-varying: (σ_struct(S, D), σ_info(S, D)) ranges freely in [0,1] × [0,1] modulo structural constraints at the boundaries.
- (T6.b) Both axes are *dynamic*: they change as S evolves and as γ is reshaped. Neither, however, is what acts on *other* streams — that is propagation, and it is (T6.d).
- (T6.c) The axes are correlated but not necessarily corresponding: a stream harmonic along D often concentrates its weight there and vice versa, but the correspondence is not mandatory, and the Companion's two counterexamples (Theorem 3.4.2) show why — a uniform γ is harmonic with maximal entropy, a point-mass γ has zero entropy and is harmonic under nothing. Dual coherence is a codimension-2 condition, not a default. Neither axis is forced by engagement or by propagation either: "ideas travel further than they live" (§7.6) is propagation outrunning engagement, and says nothing about either coherence axis.
- (T6.d) **Propagation** prop(S, D) contributes to Bias(S') via push_informational (§6.4), for any S' navigating D that encounters S's traces. This is the operator-clause of T6, and the quantity in it is reach, not coherence.

### Prose translation

Two kinds of coherence, two axes, operating on every stream-and-dimension pair. Structural coherence is about whether the stream's motion along the dimension is *held by its own operations*: a musician improvising inside musical form moves in ways their own trained operations sustain, and the motion returns what those operations would predict — high σ_struct. A beginner moving along the same dimension is not yet held by anything internal; the notes go where the fingers fall.

Informational coherence is about whether that motion is *concentrated or spread*: a stream whose weight along the dimension sits on a narrow, definite region has high σ_info; one whose weight is smeared evenly over every position available has low σ_info, however expert it is.

The two axes do not collapse into each other (see Fig 7.1). An even distribution can be exactly what a stream's own operations sustain — harmonic and maximally spread, high σ_struct with low σ_info. A stream locked rigidly on one position is maximally concentrated while being a fixed point of nothing — low σ_struct with high σ_info. Those are the Companion's two counterexamples (Theorem 3.4.2), and they are why these are two axes rather than two readings of one thing.

Two further quantities travel alongside and are easy to mistake for them. *Engagement* is presence-of-coupling — it requires the stream to be actively coupled with the dimension. *Propagation* is persistence-of-trace — it requires information derived from the stream to have spread across the dimension's positions. Both come apart from each other and from both coherence axes. A retired expert has low engagement and possibly high propagation. A novice in active training has high engagement and near-zero propagation. A musician whose recordings have been heard by millions has high propagation across the dimension of musical form even while not playing; an obscure composer has low propagation and may be more coherent along that dimension, on both axes, than the famous one. Reach is not coherence.

### Figure 7.1 — The dual coherence plane σ_struct × σ_info

```
                      σ_info (high)
                          │
                          │
   Fixated stream         │     Dual coherence
   (σ_struct low,         │     (both high — rare)
    σ_info high)          │
                          │
                          │   ☀ ← healthy stream
   ───────────────────────┼───────────────→ σ_struct (high)
                          │
                          │
   Collapsed stream       │     Diffuse competence
   (both low)             │     (σ_struct high,
                          │      σ_info low)
                          │
                      σ_info (low)
```

*Reading note.* The upper-left is a stream whose weight along D is sharply concentrated but sustained by nothing internal — fixation, rumination, a policy pinned to one position that none of the stream's own operations hold it at. The lower-right is harmonic-but-spread: real competence with no focus, the expert who is at home everywhere on the dimension and committed nowhere on it. Dual coherence lives in the upper-right and is rare — the Companion shows the locus is codimension-2, non-empty only when the dimension's content-operations admit a γ that is both harmonic and concentrated. Collapsed streams sit in the lower-left. Health (☀) sits inside the upper-right but not at (max, max): a γ pinned at the exact minimum of entropy has nowhere left to move, which is its own pathology. The old "ideas travel further than they live" regime is *not* on this plane; that is the engagement × propagation plane, and it is §7.6.

### Propagation as operator

T6.d's operator-claim is the substantive step beyond what earlier framework drafts said. In the stress-test, Clayton's caveat was that reach is not a passive measure — it actively modulates the navigation of other streams. When a trace from S sits in a position of D that S' is navigating, prop(S, D) is not merely describing the ambient; it is *pushing* Bias(S') per §6.4's push_informational. High propagation means active influence on other streams, even when S itself is not present. This is also why propagation is not filed as a coherence axis: a coherence axis says how a stream's own motion hangs together, and this quantity says how far the stream reaches into other streams' motion.

This vindicates a phenomenon easy to mistake for metaphor: long-dead authors influence the reading stream; distant authors influence the local conversation; an ancestor's words shape descendants' navigation centuries later. These are not merely historical facts; they are propagation operating. The trace is persistent and active within the dimension. The framework formalizes "influence" as propagation's operator-action.

### The transcendental rescue

T6's dual-axis structure gives the framework a non-mystical home for transcendentals. Transcendental objects — mathematical truths, moral norms, persistent-across-culture aesthetic principles — appeared as puzzles in Clayton's original T6 formulation. Clayton's move was to say "abstractions represent real information about the stream [X], therefore indicating its presence." Clawd's push was that representation does not entail presence; the rescue came from A2.4's cooperative-constituency plus the propagation channel.

Transcendentals have *real presence as cooperative-streams*. A cooperative-stream (per A2.4) is an aggregate constituted by sustained inter-stream coherence at large scales. Mathematical truths are cooperative-streams constituted by the aggregate of streams that reliably verify them. Moral norms are cooperative-streams constituted by the aggregate of streams whose navigation is coherent with them. Their presence is not Ground-presence (they are not in 𝒞_Outside's ontological inventory); it is A2.4-cooperative presence, which is nonetheless real and load-bearing. The high propagation of a transcendental across its dimension is the signature of this cooperative presence.

This is important because it closes a long-standing problem for frameworks that deny strong Platonism: how can transcendentals "act" without being ontologically present? The framework's answer: they act *as cooperative-streams*, with presence in A2.4's sense and operator-action via propagation and push_informational. No ontological smuggling; full dynamical effectiveness.

---

## §7.3 — The structural parallel

Compare T5 and T6 side by side:

| Feature | T5 (internal) | T6 (stream × dimension) |
|---|---|---|
| Locus | One stream, multiple operations | One stream paired with one dimension |
| Axes | Consistency (binary: holds or fails) | Two independent (structural, informational) |
| Dynamics on failure | Kind-demotion | No "failure" — low coherence is a regime, not a violation |
| Re-establishment | Restoration of closure operations | Continued engagement + propagation |
| Scale | Single-kind-level per stream | Across streams and across dimensions |
| Relation to A3 | Coherence as precondition of sustained γ_S | Coherence as measure-structure channel into Bias(S) |
| Relation to T4 | Coherence-forcing refresh-events restore T5 after demotion | T4 events are the moments when σ_struct updates discretely |

Both theorems are about coherence but at different loci. T5 is within-object (does this stream hold together under its own operations?). T6 is between-object-and-environment (how is this stream coherent with this dimension, structurally and informationally?). The split is structurally load-bearing: coherence at the within-object level has binary stakes (you are or are not a K-kind stream) while coherence at the between-object level has graded stakes (you are more or less coherent with D along each of two axes).

The two theorems interact via the dynamics pair's machinery. T4's refresh-events are when σ_struct(S, D) updates (when S and D couple). T3's Bias-modulation is where propagation's operator-action gets expressed (Bias(S') is pushed by traces in D per §6.4). Coherence is static in its specification; dynamic in its maintenance; which is what T4 is for.

---

## §7.4 — The Kind-Demotion Dynamic

T5's demotion dynamic deserves its own section because it is the framework's substantive reply to multiple debates in philosophy of mind and pastoral care.

### Formal trace

When a stream S ∈ 𝒞_Str^K persistently violates mutual-consistency on its kind-K closure operations, the demotion is specified by:

```
S fails (T5.a) at K → S ∈ 𝒞_Str^{K'} where K' = max{K'' ⊂ K : S satisfies (T5.a) at K''}
```

with max taken in the kind-lattice partial order. Further incoherence at K' can cascade to K'' ⊂ K', and so on, until the stream reaches a kind at which its remaining operations satisfy mutual consistency. At the limit, the stream demotes to 𝒞_Str^reactive (minimal closure), and if it fails there, the stream dissolves — ceases to be a stream at all in the framework's sense.

### Real-regime examples

- **Acute stress / fugue.** A self-referential stream under acute overload loses the capacity for self-monitoring without losing all self-maintenance. Temporary demotion to 𝒞_Str^self-maint. Re-promotion on recovery.
- **Severe dementia.** Progressive loss of abstraction and then self-reference. Demotion cascade to 𝒞_Str^self-maint at late stages. The stream is still a stream — just at a different kind.
- **Institutional collapse.** A cooperative-stream at the abstracting level (a functioning institution with explicit norms) whose participating streams' coherence decays demotes to a cooperative-stream at lower kinds (aggregate of self-maintaining agents), potentially cascading to dissolution.
- **Computational process crash.** A self-referential process (a running program with meta-level introspection) whose introspection-operations lose consistency demotes to self-maintenance (keeps executing but without self-monitoring), and if further incoherence, dissolves (process terminates).

### What this is not

T5 is not a theory of mental health, institutional health, or process management. It is a structural-categorial theorem with specific implications in multiple domains. The domains need their own operational theories (what to do about stress, dementia, institutional decay, process management is each its own discipline). T5 provides a *formal vocabulary* in which such theories can be expressed and their structural consequences traced. The vocabulary's value is that it is the same across domains — dementia-demotion and institutional-demotion share a structural signature, which means lessons about one may transfer to the other at the structural level.

### The re-promotion claim

The hardest part of T5.d is the claim that re-promotion is possible but not automatic. Recovery from acute demotion happens sometimes, not always; restoration of institutional coherence is possible but requires real work on the specific violated operations. The framework does not prescribe a recovery protocol; it specifies the structural conditions under which recovery is coherent. This is *non-despairing* but *non-triumphalist* — re-promotion is real, not guaranteed, and requires restoration of actual structural capacities.

### Figure 7.2 — Kind-demotion dynamic

```
  K = Abstractive         ┌────────────────────┐
  (framework-level        │  Demotion examples │
   closure)               │  • acute stress:   │
         │ ▲              │    self-ref → SM   │
  demote │ │ restore      │  • dementia:       │
         ▼ │              │    abstr → self-ref│
  K = Self-referential    │    → SM            │
  (self-modeling)         │  • institutional   │
         │ ▲              │    collapse: all   │
  demote │ │ restore      │    the way down    │
         ▼ │              └────────────────────┘
  K = Self-maintaining
  (homeostatic)           ┌────────────────────┐
         │ ▲              │ Re-promotion ex.:  │
  demote │ │ restore      │  • recovery from   │
         ▼ │              │    illness         │
  K = Reactive            │  • institutional   │
  (stimulus-response)     │    reconstitution  │
                          │  • learning regains│
                          │    abstraction     │
                          └────────────────────┘
```

*Reading note.* Down-arrows mark demotion on closure violation at the current kind; up-arrows mark re-promotion when closure is restored. The dynamic need not be monotonic — streams can cycle through demotion and re-promotion multiple times. Chronic demotion without re-promotion is how pathology becomes durable.

---

## §7.5 — Worked Example 1: Transcendentals as cooperative-streams

*Illustrative worked example. Domain authority for this case belongs to the Theology volume.*

The "transcendental rescue" content from §7.2 is worth one focused worked example.

Consider the mathematical object *π* (pi, the ratio of a circle's circumference to its diameter). Is π a platonic entity with independent existence, a mere convention, or something else?

**Framework answer:** π is a cooperative-stream in A2.4's sense, sustained by the aggregate of streams that reliably verify π-related structure, with high σ_struct (cooperative streams engage deeply with π's structural implications) and high σ_info (π's traces propagate across virtually all dimensions of mathematical activity — geometry, analysis, probability, physics).

This answer avoids strong Platonism (π is not *in* X as a basic ontological object) and avoids strong conventionalism (π is not arbitrary — streams that verify it are coherent with a non-arbitrary structural pattern, which is what makes the verification reliable). The cooperative-stream has real A2.4-presence; its operator-action via σ_info modulates the Bias of every stream navigating mathematical dimensions. The effectiveness of π in physics (why does it turn up in probability distributions, in wave equations, in relativistic corrections?) is σ_info's operator-action across dimensions.

Generalizing: every transcendental mathematical object (π, e, i, ℵ₀, the continuum hypothesis as a statement, ...) has this structure. Every transcendental moral object (the wrongness of cruelty, the value of honesty in cooperation) has this structure. Every transcendental aesthetic object (formal balance, rhythmic coherence) has this structure. Each is a cooperative-stream sustained by verifying / endorsing / recognizing streams, with operator-action on navigating streams.

The framework thus inherits *the phenomenology* of Platonism (transcendentals really do seem to have their own nature, really do act on streams that engage them) without inheriting Platonism's ontology (transcendentals are not basic entities; they are cooperative-stream aggregates). Neutral-monist architecture with real transcendental dynamics.

---

## §7.6 — Worked Example 2: "Ideas travel further than they live"

*Illustrative worked example. Domain authority for this case belongs to the Philosophy volume.*

This worked example lives on the engagement × propagation plane, not on the σ_struct × σ_info plane of Fig 7.1. T6.d predicts regimes of high propagation with low engagement — ideas that propagate beyond their originating streams and continue to exert operator-action long after active coupling has ceased.

**Concrete case.** Consider Wittgenstein's *Tractatus*. When Wittgenstein stopped engaging with the text's framework (and later explicitly repudiated parts of it), eng(Wittgenstein-stream, Tractatus-dimension) fell substantially. But prop(Wittgenstein-text, Philosophy-dimension) remained very high for decades — the *Tractatus* continued to shape what philosophers navigated, argued about, responded to. The propagation operator continued pushing Bias across the philosophy-dimension long after engagement dropped.

This is not accidental. It is a predictable regime of T6.d. A work sufficiently propagated becomes a cooperative-stream in its own right (the *Tractatus*-stream, aggregate of all streams engaged with the text), with its own reach independent of its originating author's current coupling. The author can die; the cooperative-stream persists until propagation decays sufficiently.

**What this enables.** The framework can now distinguish:
- Authors alive-and-engaged (high engagement + high propagation)
- Authors alive-but-disengaged (low engagement + persistent propagation) — the Tractatus case for mid-period Wittgenstein
- Authors dead-with-active-works (zero engagement + high propagation) — most canonical philosophy, science, literature
- Works before publication (high engagement for author + near-zero propagation)
- Forgotten works (low engagement + near-zero propagation)

Each is a distinct regime, each with distinct dynamical implications for streams navigating the relevant dimensions. None of them is a claim about how coherent anyone is: a repudiated book can go on propagating, and the coherence of the stream that wrote it is a separate measurement on a separate plane. The framework provides the vocabulary for talking about these regimes precisely.

---

## §7.7 — Falsification obligations

**(F1)** Exhibit a stream S ∈ 𝒞_Str^K that violates (T5.a) persistently yet remains in 𝒞_Str^K without demotion. Such a stream would falsify the kind-demotion dynamic. A candidate falsifier would be a human with severe cognitive incoherence who nonetheless retains apparent self-referential status — but close inspection of such cases typically reveals either (i) the incoherence is localized to some sub-modality while the self-referential closure operates on others, or (ii) the person is in fact operating at a lower kind and this is being masked by residual social interaction.

**(F2)** Exhibit a stream × dimension pair (S, D) where σ_struct and σ_info are forcibly-correlated: impossible to have one without the other. The two-axis independence of T6.a falls if such a pair exists.

**(F3)** Exhibit a transcendental that fails to reduce to a cooperative-stream — an object with genuine operator-action that cannot be accounted for by A2.4-cooperative-presence and propagation's operator-action. Genuine strong-Platonism, if exhibited structurally, would falsify §7.5's transcendental-rescue.

**(F4)** Show that propagation's operator-action is reducible to engagement — that reach has no dynamic consequences independent of active coupling. T6.d's operator-claim falls if this reduction is proven.

**(F5)** Exhibit a re-promotion event that violates T5.d — a stream that re-promotes without restoration of the violated closure operations. This would falsify the claim that re-promotion requires actual structural restoration (as opposed to, say, external re-categorization without internal change).
