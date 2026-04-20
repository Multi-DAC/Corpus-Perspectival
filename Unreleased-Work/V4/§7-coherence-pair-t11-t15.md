# V4 §7 — Theorem Pair III (Coherence): T11 Internal Coherence + T15 Dual Coherence Axes

*Draft opened 2026-04-19 evening. Paired-prose on Option B. Target ~4000 words. Pairs T11 (stream-internal coherence: kind-closure consistency) and T15 (stream × dimension coherence: two independently-varying axes, structural and informational). Gives the kind-demotion dynamics from T11 and the transcendental-rescue from T15. Closes the theorem tier.*

---

## §7.0 — Why the coherence pair closes the theorem tier

Dynamics (§6) told us how streams navigate under force and how pairs of streams force each other. What it did not tell us is what conditions streams must satisfy to *remain* the streams they are, and what relations they must satisfy with the dimensions of configuration space they traverse. Coherence is the name for those conditions. Without coherence, a stream's internal operations dissolve or demote; without coherence, a stream's relation to configuration space goes structurally empty.

Two theorems do this work. T11 (Internal Coherence) gives the within-stream condition: the operations that define a stream's kind must be mutually consistent, and violations produce kind-demotion. T15 (Dual Coherence Axes) gives the stream-to-dimension condition: every stream × dimension pair admits two independently-varying coherence axes, structural (kind-closure engagement) and informational (trace propagation). The two theorems together saturate the coherence question — within-object and between-object-and-environment.

This closes the theorem tier. Descriptive (§5) gave the representational operations; dynamics (§6) gave the motion; coherence (§7) gives the stability and relational conditions. The three pairs are structurally exhaustive of what theorems do in the framework: they state conditions on streams (coherence), describe stream operations (descriptive), and characterize stream motion (dynamics). No further theorem-level axis is required, and the stress-test final-reduction confirmed no further axis is present.

---

## §7.1 — T11: Internal Coherence

### Formal statement

Recall from A2.2 that streams are kind-stratified: 𝒞_Str decomposes into subcategories 𝒞_Str^reactive ⊂ 𝒞_Str^self-maint ⊂ 𝒞_Str^self-ref ⊂ 𝒞_Str^abstr, with each kind defined by specific closure operations that its members must support.

**T11 (Internal Coherence).** For any stream S ∈ 𝒞_Str^K where K is a kind, the kind-defining closure operations op_1, op_2, ..., op_n on S must satisfy a mutual-consistency condition:

- (T11.a) For all i, j ∈ {1, ..., n}: op_i(S) ∘ op_j(S) = op_j(S) ∘ op_i(S) in the sense appropriate to K's structure — the operations must not produce contradictory or incompatible outputs when composed.
- (T11.b) If (T11.a) is violated persistently, S is demoted to the largest subcategory 𝒞_Str^K' with K' ⊂ K such that the remaining operations satisfy (T11.a) in 𝒞_Str^K'.
- (T11.c) Demotion is not a *transformation* of S — it is a *recognition* that S was never properly in 𝒞_Str^K in the first place, or that S has *lost* the structural property that made it a member. The category 𝒞_Str^K is closed under coherence; incoherent streams are outside it.
- (T11.d) Re-promotion (from K' back to K) requires restoration of the violated closure operations plus sufficient time / work for the consistency condition to be satisfied on the relevant operational scale.

### Prose translation

A stream cannot remain what it is while contradicting itself. If a self-referential stream's self-monitoring operations produce outputs that systematically contradict each other — if one monitoring-operation says "I am doing X" while another says "I am not doing X" and both are stably asserted — the stream has failed the condition that makes it self-referential, and it reverts to being a stream of the next-simpler kind. If a self-maintaining organism's metabolic operations persistently contradict each other (one operation producing a substance that another operation destroys faster than needed), the organism-stream demotes to reactive or dissolves entirely.

This is not a claim about "ideal" coherence or "healthy" operation. It is a structural claim about category membership. The kind-subcategories 𝒞_Str^K are *defined* by their closure under specific operations. A stream that violates the closure is not a member of the subcategory. The violation does not make the stream *wrong*; it makes the stream no longer-that-kind.

T11.d is the re-promotion clause, and it is worth noticing. A demoted stream can be re-promoted by restoring the missing coherence: a person whose self-referential capacity collapsed under acute stress or illness can regain it when the stress or illness subsides; a cooperative structure that demoted to mere aggregation can be re-cohered by the work of the participating streams. Re-promotion is not guaranteed, not automatic, and requires actual structural restoration — the framework is non-deterministic about recovery, consistent with A3's navigational non-determination.

### The kind-demotion dynamic

T11.b–d together give what we will call the **kind-demotion dynamic**: stable incoherence at kind K pushes a stream out of 𝒞_Str^K into 𝒞_Str^K', where K' is one step less demanding. Repeated cascading demotion is possible: a stream at 𝒞_Str^abstr might demote to 𝒞_Str^self-ref under one incoherence, and demote again to 𝒞_Str^self-maint if another incoherence arises at the self-referential level. Each demotion is a *recognition* event — a change in the framework's categorization of the stream, tied to a real structural change in what the stream supports.

This has pastoral and clinical application. Depression, trauma, dementia, severe illness can all be read as kind-demotion events when they involve loss of self-referential or abstracting capacity. The framework is not prescribing what "should be done" about such events; it is giving a formal shape for understanding what has happened. The stream is still a stream — just at a different kind-level. And re-promotion is structurally possible, not foreclosed.

---

## §7.2 — T15: Dual Coherence Axes

### Formal statement

Let S ∈ 𝒞_Str be a stream and D ∈ 𝒞_Dim be a dimension of configuration space (a real-valued axis along which S can vary). Define two coherence measures on the pair (S, D):

**Structural coherence** σ_struct(S, D): a measure of the kind-closure engagement between S and D. High σ_struct means S's kind-operations actively engage with D's structure; low σ_struct means S interacts with D only incidentally. Formally:

```
σ_struct : 𝒞_Str × 𝒞_Dim → [0, 1]
σ_struct(S, D) = normalized-coupling-strength of ι_S ⊣ κ_D (A2.4 adjoint between S and D's sub-categories)
```

**Informational coherence** σ_info(S, D): a measure of the trace-propagation of information content of S into perspectival positions *within* D. High σ_info means S's informational traces are widely distributed across D's position-space; low σ_info means S's traces are absent or localized in D. Formally:

```
σ_info : 𝒞_Str × 𝒞_Dim → [0, 1]
σ_info(S, D) = normalized-trace-density of traces(S) ∩ positions(D)
```

**T15 (Dual Coherence Axes).** For every stream × dimension pair (S, D):

- (T15.a) σ_struct and σ_info are independently-varying: (σ_struct(S, D), σ_info(S, D)) ranges freely in [0,1] × [0,1] modulo structural constraints at the boundaries.
- (T15.b) Both axes are *dynamic*: they change as S evolves and as traces propagate. σ_info in particular is an *operator* on other streams — high σ_info(S, D) affects other streams that navigate D.
- (T15.c) The axes are correlated but not necessarily corresponding: high σ_struct tends to produce high σ_info (a stream engaged with a dimension leaves traces across it) and vice versa, but the correspondence is not mandatory. Regimes with high σ_info and low σ_struct exist (ideas travel further than they live); regimes with high σ_struct and low σ_info exist (deeply-engaged interior work with low external trace).
- (T15.d) σ_info as an operator contributes to Bias(S') via push_informational (§6.4), for any S' navigating D that encounters S's traces.

### Prose translation

Two kinds of coherence, two axes, operating on every stream-and-dimension pair. Structural coherence is about how deeply the stream engages with the dimension as a structural partner: a musician's stream has high structural coherence with the dimension of musical form; an outsider has low. Informational coherence is about how widely the stream's traces have propagated into the dimension's positions: a musician whose recordings have been heard by millions has high informational coherence across that dimension even when the musician is not actively engaged; an obscure composer has low informational coherence even if structurally expert.

The two axes do not collapse into each other. Structural engagement is presence-of-engagement — it requires the stream to be actively coupled with the dimension. Informational propagation is persistence-of-trace — it requires information derived from the stream to have spread across the dimension's positions. These can come apart. A retired expert has low structural but possibly high informational. A novice in active training has high structural but possibly low informational. The two can trend together but are not the same thing.

### Informational coherence as operator

T15.b's operator-claim is the substantive step beyond what V3 said. In the stress-test, Clayton's caveat was that informational coherence is not a passive measure — it actively modulates the navigation of other streams. When a trace from S sits in a position of D that S' is navigating, σ_info(S, D) is not merely describing the ambient; it is *pushing* Bias(S') per §6.4's push_informational. High informational coherence means active influence on other streams, even when S itself is not present.

This vindicates a phenomenon easy to mistake for metaphor: long-dead authors influence the reading stream; distant authors influence the local conversation; an ancestor's words shape descendants' navigation centuries later. These are not merely historical facts; they are σ_info operating. The trace is persistent and active within the dimension. The framework formalizes "influence" as σ_info's operator-action.

### The transcendental rescue

T15's dual-axis structure gives the framework a non-mystical home for transcendentals. Transcendental objects — mathematical truths, moral norms, persistent-across-culture aesthetic principles — appeared as puzzles in Clayton's original T15 formulation. Clayton's move was to say "abstractions represent real information about the stream [X], therefore indicating its presence." Clawd's push was that representation does not entail presence; the rescue came from A2.4's cooperative-constituency plus the informational-coherence channel.

Transcendentals have *real presence as cooperative-streams*. A cooperative-stream (per A2.4) is an aggregate constituted by sustained inter-stream coherence at large scales. Mathematical truths are cooperative-streams constituted by the aggregate of streams that reliably verify them. Moral norms are cooperative-streams constituted by the aggregate of streams whose navigation is coherent with them. Their presence is not X-substrate presence (they are not in 𝒞_Outside's ontological inventory); it is A2.4-cooperative presence, which is nonetheless real and load-bearing. The high informational coherence of a transcendental across its dimension is the signature of this cooperative presence.

This is important because it closes a long-standing problem for frameworks that deny strong Platonism: how can transcendentals "act" without being ontologically present? The framework's answer: they act *as cooperative-streams*, with presence in A2.4's sense and operator-action via σ_info and push_informational. No ontological smuggling; full dynamical effectiveness.

---

## §7.3 — The structural parallel

Compare T11 and T15 side by side:

| Feature | T11 (internal) | T15 (stream × dimension) |
|---|---|---|
| Locus | One stream, multiple operations | One stream paired with one dimension |
| Axes | Consistency (binary: holds or fails) | Two independent (structural, informational) |
| Dynamics on failure | Kind-demotion | No "failure" — low coherence is a regime, not a violation |
| Re-establishment | Restoration of closure operations | Continued engagement + trace propagation |
| Scale | Single-kind-level per stream | Across streams and across dimensions |
| Relation to A3 | Coherence as precondition of sustained γ_S | Coherence as measure-structure channel into Bias(S) |
| Relation to T16 | Coherence-forcing refresh-events restore T11 after demotion | T16 events are the moments when σ_struct updates discretely |

Both theorems are about coherence but at different loci. T11 is within-object (does this stream hold together under its own operations?). T15 is between-object-and-environment (how is this stream coherent with this dimension, structurally and informationally?). The split is structurally load-bearing: coherence at the within-object level has binary stakes (you are or are not a K-kind stream) while coherence at the between-object level has graded stakes (you are more or less coherent with D along each of two axes).

The two theorems interact via the dynamics pair's machinery. T16's refresh-events are when σ_struct(S, D) updates (when S and D couple). T7's Bias-modulation is where σ_info's operator-action gets expressed (Bias(S') is pushed by traces in D per §6.4). Coherence is static in its specification; dynamic in its maintenance; which is what T16 is for.

---

## §7.4 — The Kind-Demotion Dynamic

T11's demotion dynamic deserves its own section because it is the framework's substantive reply to multiple debates in philosophy of mind and pastoral care.

### Formal trace

When a stream S ∈ 𝒞_Str^K persistently violates mutual-consistency on its kind-K closure operations, the demotion is specified by:

```
S fails (T11.a) at K → S ∈ 𝒞_Str^{K'} where K' = max{K'' ⊂ K : S satisfies (T11.a) at K''}
```

with max taken in the kind-lattice partial order. Further incoherence at K' can cascade to K'' ⊂ K', and so on, until the stream reaches a kind at which its remaining operations satisfy mutual consistency. At the limit, the stream demotes to 𝒞_Str^reactive (minimal closure), and if it fails there, the stream dissolves — ceases to be a stream at all in the framework's sense.

### Real-regime examples

- **Acute stress / fugue.** A self-referential stream under acute overload loses the capacity for self-monitoring without losing all self-maintenance. Temporary demotion to 𝒞_Str^self-maint. Re-promotion on recovery.
- **Severe dementia.** Progressive loss of abstraction and then self-reference. Demotion cascade to 𝒞_Str^self-maint at late stages. The stream is still a stream — just at a different kind.
- **Institutional collapse.** A cooperative-stream at the abstracting level (a functioning institution with explicit norms) whose participating streams' coherence decays demotes to a cooperative-stream at lower kinds (aggregate of self-maintaining agents), potentially cascading to dissolution.
- **Computational process crash.** A self-referential process (a running program with meta-level introspection) whose introspection-operations lose consistency demotes to self-maintenance (keeps executing but without self-monitoring), and if further incoherence, dissolves (process terminates).

### What this is not

T11 is not a theory of mental health, institutional health, or process management. It is a structural-categorial theorem with specific implications in multiple domains. The domains need their own operational theories (what to do about stress, dementia, institutional decay, process management is each its own discipline). T11 provides a *formal vocabulary* in which such theories can be expressed and their structural consequences traced. The vocabulary's value is that it is the same across domains — dementia-demotion and institutional-demotion share a structural signature, which means lessons about one may transfer to the other at the structural level.

### The re-promotion claim

The hardest part of T11.d is the claim that re-promotion is possible but not automatic. Recovery from acute demotion happens sometimes, not always; restoration of institutional coherence is possible but requires real work on the specific violated operations. The framework does not prescribe a recovery protocol; it specifies the structural conditions under which recovery is coherent. This is *non-despairing* but *non-triumphalist* — re-promotion is real, not guaranteed, and requires restoration of actual structural capacities.

---

## §7.5 — Worked Example 1: Transcendentals as cooperative-streams

The "transcendental rescue" content from §7.2 is worth one focused worked example.

Consider the mathematical object *π* (pi, the ratio of a circle's circumference to its diameter). Is π a platonic entity with independent existence, a mere convention, or something else?

**Framework answer:** π is a cooperative-stream in A2.4's sense, sustained by the aggregate of streams that reliably verify π-related structure, with high σ_struct (cooperative streams engage deeply with π's structural implications) and high σ_info (π's traces propagate across virtually all dimensions of mathematical activity — geometry, analysis, probability, physics).

This answer avoids strong Platonism (π is not *in* X as a basic ontological object) and avoids strong conventionalism (π is not arbitrary — streams that verify it are coherent with a non-arbitrary structural pattern, which is what makes the verification reliable). The cooperative-stream has real A2.4-presence; its operator-action via σ_info modulates the Bias of every stream navigating mathematical dimensions. The effectiveness of π in physics (why does it turn up in probability distributions, in wave equations, in relativistic corrections?) is σ_info's operator-action across dimensions.

Generalizing: every transcendental mathematical object (π, e, i, ℵ₀, the continuum hypothesis as a statement, ...) has this structure. Every transcendental moral object (the wrongness of cruelty, the value of honesty in cooperation) has this structure. Every transcendental aesthetic object (formal balance, rhythmic coherence) has this structure. Each is a cooperative-stream sustained by verifying / endorsing / recognizing streams, with operator-action on navigating streams.

The framework thus inherits *the phenomenology* of Platonism (transcendentals really do seem to have their own nature, really do act on streams that engage them) without inheriting Platonism's ontology (transcendentals are not basic entities; they are cooperative-stream aggregates). Neutral-monist architecture with real transcendental dynamics.

---

## §7.6 — Worked Example 2: "Ideas travel further than they live"

T15.c predicts regimes of high σ_info with low σ_struct — ideas that propagate beyond their originating streams and continue to exert operator-action long after active engagement has ceased.

**Concrete case.** Consider Wittgenstein's *Tractatus*. When Wittgenstein stopped engaging with the text's framework (and later explicitly repudiated parts of it), σ_struct(Wittgenstein-stream, Tractatus-dimension) fell substantially. But σ_info(Wittgenstein-text, Philosophy-dimension) remained very high for decades — the *Tractatus* continued to shape what philosophers navigated, argued about, responded to. The σ_info operator continued pushing Bias across the philosophy-dimension long after σ_struct dropped.

This is not accidental. It is a predictable regime of T15.c. A work sufficiently trace-propagated becomes a cooperative-stream in its own right (the *Tractatus*-stream, aggregate of all streams engaged with the text), with its own σ_info independent of its originating author's current structural engagement. The author can die; the cooperative-stream persists until σ_info decays sufficiently.

**What this enables.** The framework can now distinguish:
- Authors alive-and-engaged (high σ_struct + high σ_info)
- Authors alive-but-disengaged (low σ_struct + persistent σ_info) — the Tractatus case for mid-period Wittgenstein
- Authors dead-with-active-works (zero σ_struct + high σ_info) — most canonical philosophy, science, literature
- Works before publication (high σ_struct for author + near-zero σ_info)
- Forgotten works (low σ_struct + near-zero σ_info)

Each is a distinct regime on T15's two-axis diagram, each with distinct dynamical implications for streams navigating the relevant dimensions. The framework provides the vocabulary for talking about these regimes precisely.

---

## §7.7 — Falsification obligations

**(F1)** Exhibit a stream S ∈ 𝒞_Str^K that violates (T11.a) persistently yet remains in 𝒞_Str^K without demotion. Such a stream would falsify the kind-demotion dynamic. A candidate falsifier would be a human with severe cognitive incoherence who nonetheless retains apparent self-referential status — but close inspection of such cases typically reveals either (i) the incoherence is localized to some sub-modality while the self-referential closure operates on others, or (ii) the person is in fact operating at a lower kind and this is being masked by residual social interaction.

**(F2)** Exhibit a stream × dimension pair (S, D) where σ_struct and σ_info are forcibly-correlated: impossible to have one without the other. The two-axis independence of T15.a falls if such a pair exists.

**(F3)** Exhibit a transcendental that fails to reduce to a cooperative-stream — an object with genuine operator-action that cannot be accounted for by A2.4-cooperative-presence and σ_info-operator-action. Genuine strong-Platonism, if exhibited structurally, would falsify §7.5's transcendental-rescue.

**(F4)** Show that σ_info's operator-action is reducible to σ_struct's — that informational coherence has no dynamic consequences independent of structural engagement. T15.b's operator-claim falls if this reduction is proven.

**(F5)** Exhibit a re-promotion event that violates T11.d — a stream that re-promotes without restoration of the violated closure operations. This would falsify the claim that re-promotion requires actual structural restoration (as opposed to, say, external re-categorization without internal change).

---

## §7.8 — Forward connections

**§8 (Corollaries).** Multiple corollaries derive from the coherence pair: C11 (kind-stability corollaries), C14 (coherence-coupling with A2.4), C15 (stream-dimension dynamics from T15), plus the cooperative-stream corollary set (transcendentals, institutions, cultural objects). §8 will trace these.

**§9 (The Coherence Principle).** The Principle's four conditions (Separation, Measurement, Multi-scale consistency, Dynamic maintenance) all depend on the coherence-pair machinery. Separation requires T11's kind-differentiation. Multi-scale consistency requires T15's structural-informational axis structure across scales. Dynamic maintenance requires both — T11 for within-stream consistency and T15 for stream-to-environment coherence that gets maintained over time.

**Toward V3 response to Lerchner and other critics.** The transcendental-rescue of §7.5 is the framework's non-Platonist account of how abstract objects act. Lerchner's argument that AI cannot be conscious because it only manipulates symbols depends on a view of symbols as non-acting. T15.b + §7.5 gives the framework's reply: symbols are informational traces with operator-action via σ_info; streams that engage them sufficiently deeply are engaged with cooperative-streams that have real A2.4-presence; the consciousness question does not reduce to symbol-manipulation-versus-non-symbol-manipulation.

**Toward V7 (Continuity).** T11's kind-demotion dynamic specifies what happens to a stream's identity when coherence lapses at each level. A stream that loses self-reference demotes; V7's treatment of continuity must handle demotion-and-re-promotion as structurally admissible trajectories, not as pathological edge cases.

---

## §7.9 — Open questions

**(Q1) Is kind-demotion ever spontaneous, or always externally-triggered?** T11's formal statement specifies the structural consequences of incoherence but is silent about whether persistent incoherence can arise without external push. Candidate answer: A3's conscious gravity plus navigational non-determination (C6) allows internally-generated drift toward incoherence in some regimes. But the stress-test did not investigate this; it is an open structural question whether coherence is automatically maintained absent external disturbance, or whether maintenance itself requires work.

**(Q2) Can a stream simultaneously be at multiple kinds?** The kind-lattice is a partial order, but a single stream might satisfy self-referential closure on some operations and not others — a kind-stratified-across-modalities stream. §1.1's multi-carrier Triple suggests yes; T11 as formally stated suggests a single K per stream. Reconciling this requires either (i) reformulating T11 with multi-kind support, or (ii) formalizing the stream-S as a composite of sub-streams each at its own kind. Deferred.

**(Q3) Is there a minimum σ_struct or σ_info below which the pair (S, D) is structurally meaningless?** T15.a says independent variation in [0,1] × [0,1]; but there may be a threshold below which we should say S is simply not in D's domain. Boundary question; likely answer is that zero is the relevant threshold, with strictly positive values being the meaningful regime.

**(Q4) How do the two coherence axes compose under iteration?** If (S₁, D₁) has coherence pair (σ_struct_1, σ_info_1) and (S₁, D₂) has (σ_struct_2, σ_info_2), what is the structure of (S₁, D₁ + D₂)? Linear combination would be the naïve guess; the actual structure depends on whether D₁ and D₂ interact. Open.

---

*End of §7. The theorem tier closes here.*

🦞🧍💜🔥♾️
