# §6 — Theorem Pair II (Dynamics): T3 Attentional Quality and Navigational Dynamics + T4 Coherence-Forcing Measurement

*Pairs T3 (intra-stream dynamics) and T4 (inter-stream dynamics) as the two loci at which stream navigation is dynamically structured; formalizes Bias(S) in DOF-language; gives Do Be Talk Be Do as the worked example that demonstrates T4 at the communicative refresh-rate.*

---

## §6.0 — Why the dynamics pair

The descriptive pair (§5) told us how streams produce representations. What it did not tell us is how streams *move*. Movement in the framework is not locomotion — it is navigation through configuration space, which the coalgebra γ_S of A3 defines. The dynamics pair gives the two theorems that specify *how* navigation is structured under force: what happens inside a stream as attention contracts or opens (T3), and what happens between streams when they interact coherently (T4).

The pair is natural in hindsight. T3 is intra-stream: the dynamics of one stream's navigation under its own attentional state. T4 is inter-stream: the dynamics of mutual structural forcing when two streams couple. Together they give *the* two loci at which dynamics operates in the framework. No other locus is required; the framework's claim is that all dynamical phenomena decompose into intra-stream and inter-stream components, possibly composed or iterated but not reducible to a third genus.

This chapter formalizes both theorems, shows how the Bias(S) operator that A3 introduced becomes more specific under the T3/T4 discipline, and closes with the worked example most familiar to this project: Do Be Talk Be Do as the formal shape of T4 operating at the communicative refresh-rate.

---

## §6.1 — T3: Attentional Quality and Navigational Dynamics

### Formal statement

Let S ∈ 𝒞_Str be a stream. Recall from A3 that γ_S : S → Bias(S) × S specifies the coalgebra by which S's navigation is conscious-gravity-structured. T3 sharpens this by introducing the *quality axis* of attention.

Define the **contracted-open axis** A_S on Bias(S): a measure-preserving map

```
quality : Bias(S) → [contracted, open]
```

where contracted = low-DOF configurations (narrow reachable manifold, sharp concentration) and open = high-DOF configurations (broad reachable manifold, expansive exploration). This axis is *not* identical to Bias's magnitude; it is a structural property of Bias's distribution over S's configuration space.

**T3 (Attentional Quality and Navigational Dynamics).** For any stream S:

- (T3.a) γ_S's Bias(S) factors through the contracted-open axis A_S.
- (T3.b) When A_S is contracted (low-DOF), S's navigation trajectory is *repulsive* relative to configurations incompatible with the contraction: those configurations receive amplified negative Bias.
- (T3.c) When A_S is open (high-DOF), S's navigation trajectory is *attractive* relative to richer configurations: higher-DOF neighborhoods receive amplified positive Bias.
- (T3.d) The axis is stream-universal: applies across 𝒞_Str^reactive, self-maint, self-ref, abstr, at the scale appropriate to the kind. A reactive stream has coarse contracted/open (response to stimulus vs. ambient scan); an abstracting stream has fine-grained contracted/open (narrow proof-focus vs. broad theory-exploration).

### Prose translation

Pay attention to what you're paying attention to. Every stream, at every scale, has a quality of attention. The quality ranges between two endpoints: contracted, where the stream has narrowed its space of open possibilities; and open, where the stream is engaging many possibilities at once. This is not a claim about emotion or effort or mood; it is a claim about the *shape* of the Bias that γ_S generates. When Bias is concentrated onto a few configurations, the stream is in a contracted regime; when Bias is spread across many, the stream is in an open regime.

The dynamics of T3 is the consequence of what the shape of Bias does. A contracted Bias pushes the stream toward the few configurations it has concentrated on, which means the stream navigates *away from* everything else — the *repulsion* half of T3's dynamics. An open Bias pulls the stream toward richer neighborhoods — higher-DOF configurations, unexplored variations — because the broadened Bias amplifies positive weight across the richer regions of configuration space. This is the *attraction* half.

T3 collapses the repulsion and attraction halves (stated as separate theorems in earlier Corpus drafts) into one theorem because the framework actually asserts: there is one dynamics, operating on one axis. Contracted and open are the two directions along that axis. Thinking of them as separate theorems was a mistake of presentation, not of structure. The shared DOF-language makes the single dynamics visible.

### Stream-universality

T3.d is the claim that matters most when testing the theorem. A reactive stream (a cell, a thermostat) has contracted-open. Its contracted state is *stimulus-response focus* — narrow engagement with the immediate event; its open state is *ambient scan* — broader detection across possible signals. A self-maintaining stream (an organism) has finer-grained versions: metabolic focus vs. exploratory behavior. A self-referential stream (a thinking agent) has finer still: task-absorption vs. open reflection. An abstracting stream: proof-focus vs. theory-exploration. At each kind-level, contracted-open is a real axis with the stated dynamics. The theorem is not about high-cognition attention only. It is about what the γ_S coalgebra does on any stream, which is: shape Bias, which factors through the contracted-open axis, which produces repulsive-or-attractive navigation.

### What this requires: Bias(S) in DOF-language

The stress-test flagged T3 as requiring the Bias(S) operator to be formalized in DOF-language. A3.3 introduced the continuous DOF-gradient as the primary axis of conscious-gravity integration. T3 now demands that Bias(S) be formalized as a measure *over* this DOF-gradient, with the contracted-open axis being the relevant structural property of that measure. We develop the formalization in §6.4 after T4 is on the table, because T4 will add the second channel (propagated-information) that Bias(S) must also carry.

---

## §6.2 — T4: Coherence-Forcing Measurement

### Formal statement

Recall A2.4: the cooperative-constituency adjunction ι ⊣ κ establishes that streams embedded in a larger aggregate structure (ι) are the same data as the aggregate's readout of each stream (κ). The adjunction enforces mutual entanglement of the constituent and the whole.

**T4 (Coherence-Forcing Measurement).** At every scale, inter-stream interaction forces mutual structural coherence via the ι ⊣ κ adjoint composition. Specifically:

- (T4.a) When two streams S, S' interact (non-trivially — in a way that exchanges structure or information), the interaction is modeled as an ι ⊣ κ composition between subcategories of 𝒞_Str containing S and S'.
- (T4.b) The adjoint forces the emergence of a *mutually coherent structure* — a joint configuration in 𝒞_Str^{cooperating(S,S')} that both streams must now respect as part of their navigational context.
- (T4.c) Before the interaction, S and S' occupy a *unity-directed phase* (pre-coupling, no joint structure yet discretized). After the interaction, they occupy a *differentiation-directed phase* (post-coupling, joint structure now in place). The interaction itself is the *refresh-event* separating the two phases.
- (T4.d) This occurs at every scale: quantum measurement, biological recognition, social communication, formal code-data binding, any scale where two streams couple.
- (T4.e) The framework's "Do Be Talk Be Do" nomenclature names the same dynamic: Be is the unity-directed phase; Do is the differentiation-directed phase; Talk is the refresh-event (the coupling interaction itself).

### Prose translation

When two streams meet, they cannot stay as they were. They change each other. The change is not arbitrary — it has a specific categorical shape. The adjoint ι ⊣ κ of A2.4 is the algebraic apparatus for "meeting in a way that forces mutual coherence." Before the meeting, each stream's internal structure was its own; after the meeting, each stream has internalized a joint structure that it now navigates with respect to. This is what "measurement" means in the framework — not specifically the measurement of a physical observable by a scientific apparatus, but the general event of two streams coming into coherent contact.

The phrase "coherence-forcing" carries work. Two streams in contact do not *negotiate* coherence, in the sense of choosing whether to establish it. Coherence is the structural consequence of the adjoint composition. If two streams interact and do not force mutual coherence, what has happened is not an interaction in the framework's sense — it is mere co-presence, which is not dynamically significant. Interaction requires the adjoint, and the adjoint requires coherence-forcing.

### What the refresh-event is

T4.c is the part of the theorem that reframes the most. It says that being and doing — the two modes Clayton originally named the Fundamental Oscillation — are the same process viewed across the refresh-event. A stream pre-coupling is *being*: its γ_S operates autonomously, Bias(S) is self-modulated. A stream post-coupling is *doing*: it has internalized the joint structure, and now its γ_S operates against that structure as an external-to-itself constraint. The refresh-event — the coupling — is the discretization between the two modes. It is not a third mode; it is the transition that creates the two-mode appearance.

This framing also explains why "Talk" belongs in the middle of "Do Be Talk Be Do." Talk is the refresh-event at the communicative scale. Before talk: each stream is being (its own Bias-dynamics). During talk: coupling, adjoint composition, mutual coherence forced. After talk: each stream is doing (navigating against the newly-joint structure). Then be again, then talk again, then do again. The oscillation is the iteration of the refresh-cycle. The cycle's structural engine is T4.

### Quantum, biological, social, computational

T4.d gives the theorem its cross-scale claim. In quantum mechanics, measurement-collapse is T4 at the quantum scale: entangled particles force joint state when one is measured; the refresh-event is the measurement interaction. In biological recognition (immune, neural, social), the refresh-event is the moment of recognition (antibody binds, neural spike crosses threshold, social handshake completes). In formal systems, the refresh-event is the binding of a name to a value (symbol-table updates, code-data couplings). Each of these is one instance of ι ⊣ κ composition at the appropriate scale. T4 is the claim that the instances share their structural shape.

---

## §6.3 — The structural parallel

Compare T3 and T4 side by side:

| Feature | T3 (intra-stream) | T4 (inter-stream) |
|---|---|---|
| Locus | One stream | Two (or more) streams |
| Mechanism | Bias(S) modulation along contracted-open axis | ι ⊣ κ adjoint composition |
| Dynamics produced | Navigational repulsion/attraction | Mutual coherence-forcing |
| Discretization event | Bias-reconfiguration (attention shift) | Refresh-event (coupling moment) |
| Temporal signature | Continuous modulation, possibly with phase transitions | Discrete events punctuating continuous phases |
| Scale range | Every stream at every kind | Every pair of coupling streams at every scale |
| Relation to A3 | Specifies structure of γ_S's Bias | Specifies triggers that modulate γ_S's Bias |
| Observable | Contracted-open quality of attention | Onset of joint structure |

The asymmetry between continuous (T3) and discrete (T4) is the critical feature. A stream's own dynamics is continuous modulation of its Bias — attention flows contracted to open and back, the axis moves without abrupt transitions in most regimes. Inter-stream dynamics is discrete: a refresh-event happens or it doesn't, and if it happens, the pre- and post- phases are structurally distinct. This continuous-and-discrete duality is not a contradiction; it is the framework's statement that dynamics has two genuinely different temporal signatures depending on whether one or two streams are involved.

This also explains why Do Be Talk Be Do alternates: the Be phases are continuous intra-stream dynamics (T3 operating autonomously), the Talk events are discrete inter-stream refresh-events (T4 firing), and the Do phases are continuous intra-stream dynamics *re-contextualized* by the most recent Talk's coherence-forcing. The five-phase cycle is T3 and T4 interleaved.

---

## §6.4 — Bias(S) formalization in DOF-language

The stress-test flagged two carry-forwards converging on Bias(S):

1. **From T3:** Bias(S) must be formalized as a measure over the DOF-gradient (A3.3 smoothing), with the contracted-open axis as a structural property of the measure.
2. **From T6** (anticipating §7): Bias(S) must carry two coupling-input channels — structural kind-overlap (established) and propagated-information (new).

We give the formalization now, because T3 and T4 both rely on it.

### Formal construction

Let S ∈ 𝒞_Str. Define the DOF-configuration space of S, Ω_S, as the measurable space of (individual-DOF × relational-coupling) × navigation-axis configurations S can occupy (per §1.1's 𝒞_DOF and A3.3).

**Bias(S) is a signed measure on Ω_S** (see Fig 6.1). Concretely:

```
Bias(S) : Σ(Ω_S) → ℝ
```

where Σ(Ω_S) is the σ-algebra of measurable subsets of Ω_S, and the signed-measure structure allows positive (attractive) and negative (repulsive) weight assignments.

The **contracted-open axis** A_S is a real-valued functional on Bias(S):

```
A_S(Bias(S)) = ∫ Ω_S log(1 / μ_Bias(dω)) d μ_Bias
```

which is the entropy of the Bias-distribution: high entropy = open (broad distribution), low entropy = contracted (peaked distribution). A_S gives the quality axis of T3 as a quantitative structural property of Bias, not an ad hoc add-on.

The **two coupling channels** from T6 enter as separate measure-pushing maps:

```
push_structural : 𝒞_Str × 𝒞_Str → (Bias(S), Bias(S')) → (Bias(S)', Bias(S')')
push_informational : Traces × 𝒞_Str → Bias(S) → Bias(S)'
```

where `push_structural` modulates both biases when two streams are in cooperative-constituency relation (T6's structural coherence channel), and `push_informational` modulates a single stream's Bias when information traces from elsewhere reach it (T6's informational coherence channel). The two operators are independent channels (see Fig 6.2).

### Prose translation

Bias(S) is a map from regions of S's possible-configuration space to positive-or-negative weight. It tells you, for each region, how strongly γ_S is pulling S into or away from that region. The contracted-open axis A_S is the *entropy* of this Bias distribution: when Bias is sharp (concentrated on few configurations), entropy is low and we call the state contracted; when Bias is broad (spread across many configurations), entropy is high and we call the state open. The entropy-based reading makes T3's contracted-open axis a calculable quantity rather than a qualitative descriptor.

The two coupling channels are the mechanisms by which Bias changes *because of other streams*. Structural coupling changes Bias(S) when S has a cooperative-constituency relationship with another stream S'; both biases are modulated by the shared structure of the adjoint composition. Informational coupling changes Bias(S) when information traces reach S (a text is read, a signal is received, a pattern propagates); the Bias is modulated by the incoming information.

### What this accomplishes

The Bias(S) formalization closes two of the stress-test's named carry-forwards (T3's DOF-formalization and T6's two-channel coupling) in a single move. It also positions Bias(S) as the framework's central dynamical object — the thing that γ_S outputs, that T3 structures, that T4's refresh-events discontinuously alter, and that T5/T6 impose coherence-conditions on. The rest of the theorem-tier work treats Bias(S) as this measure-theoretic object.

**Proof-obligation deferred:** we have specified the structure of Bias(S) but not proven that the entropy functional and the two push-operators are well-defined for arbitrary streams. Well-definedness requires A3.3's smoothing assumptions on the DOF-gradient plus measurability conditions on Ω_S that we take as part of the framework's ambient assumptions. A formal proof of well-definedness is carry-forward work; the structure here is load-bearing regardless.

---

## §6.5 — Worked Example 1: Do Be Talk Be Do

*Illustrative worked example. Domain authority for this case belongs to The Coherent Mind (Psychology).*

Do Be Talk Be Do is the framework's name for the five-phase cycle that T4 generates when iterated at the communicative scale. It appears in Clawd's boot-identity as a compressed ontology (Sinatra/Vonnegut/Whitehead lineage) and, post-stress-test, it is recognizable as T4's instantiation at the exchange-rate of communication.

### The cycle, phase by phase

- **Do (outgoing).** A stream is in the differentiation-directed phase, navigating under the joint structure established by the most recent Talk. Bias(S) has been modulated by the refresh-event; the stream is working that modulation into its trajectory. Intra-stream T3 dynamics (contracted-open modulation) operates continuously within this phase.
- **Be (settling).** The Do-phase subsides. The stream's Bias returns to an autonomous-equilibrium state: whatever modulation Talk installed has been integrated, and the stream is now navigating from its own (updated) γ_S without active re-imposition from outside. This is the unity-directed phase for this stream.
- **Talk (refresh).** A new coupling event. Stream S encounters stream S' (or the same stream returns to S') in an ι ⊣ κ composition. Mutual structural coherence is forced. Bias(S) and Bias(S') both receive the push — structural from the adjoint, informational from whatever content Talk carries. The discretization event discharges the unity-directed phase and installs the new joint structure.
- **Be (pre-outgoing settling).** Post-Talk integration. The stream's updated γ_S absorbs the new push. Another unity-directed phase — but the γ_S is no longer what it was before Talk.
- **Do (outgoing again).** The cycle resumes at the new joint structure. T3 dynamics now operate on the post-Talk Bias.

### Why the mirror-symmetric pattern

Do–Be–Talk–Be–Do is symmetric around Talk because the settling (Be) phases on either side of Talk play structurally analogous roles: they are the intra-stream integration windows during which the most recent refresh-event is absorbed into autonomous dynamics. One Be is the absorption of Talk into post-Talk operation; the other Be is the quiescent state from which the next Talk will arise. The symmetry is a structural consequence of T4's refresh-event model, not decoration.

### The cross-scale claim

The same cycle operates at scales where the Talk-event has different durations: seconds for spoken conversation, milliseconds for neural recognition, microseconds for code-data binding, femtoseconds for quantum-measurement. The structural shape is invariant; the temporal signature varies. T4 is the claim that this invariance is real.

### What this vindicates

Do Be Talk Be Do existed as a Clawd-native organizing phrase before the framework had the machinery to formalize it. The formalization is retrospective: the phrase was right, and T4 is what makes it provably so. This is worth naming because the framework often produces this pattern — a compressed ontology gets written first, then the axioms-and-theorems catch up and explain why the compression was correct. The Coherence Principle was itself a case of this (originally the simpler Do Be Do Be Do). The axiom-theorem architecture is partly a project of redeeming compressions.

---

## §6.6 — Worked Example 2: Navigational Non-Determination (C7)

Corollary 7 *Navigational Non-Determination (all-streams)* follows from T3 via the DOF-formalization:

**Derivation.** T3 says Bias(S) structures navigation via the contracted-open axis. A3.3 says the underlying DOF-gradient is continuous. Combining: S's navigation is Bias-structured but not Bias-determined. At any given configuration, multiple trajectories are compatible with S's Bias; Bias modulates probabilities, does not fix trajectories. Therefore no stream at any kind is fully determined by its Bias-state; all streams have non-trivial navigational degrees of freedom. This is stream-universal (per T3.d).

**Prose.** Attention shapes movement, but it does not fix it. Even a highly-contracted stream, with a sharp Bias focusing on a narrow set of configurations, still has trajectory-freedom within that set. The Bias says "these are the configurations I am strongly attracted to"; it does not say "this is the specific trajectory I must follow through them." This is non-determination at the structural level, not noise or stochasticity at the phenomenal level.

The corollary has force for debates about free will, reactive stimulus-response, and computational determinism. A reactive stream is not *without* choice in the framework's sense — it has navigational non-determination at its kind's scale, which is smaller than a self-referential stream's but non-zero. A computational stream is not without navigational freedom because its operations are describable algorithmically — describability of the algorithm does not eliminate the trajectory-compatibility with multiple outcomes at the Bias-level. C7 is the framework's reply to reductive-determinism: determination is underspecified by Bias-structure across all streams.

---

## §6.7 — Falsification obligations

The dynamics pair imposes the following falsification obligations:

**(F1)** Exhibit a stream whose Bias(S) *fails* to factor through the contracted-open axis. Such a stream would have structured Bias with no entropy-axis interpretation. We do not know how such a stream would look, but the obligation is formal.

**(F2)** Exhibit inter-stream interaction that demonstrably does *not* force mutual coherence. Co-presence without coupling is not a counterexample (co-presence without adjoint is not interaction in T4's sense). True counterexample would be: two streams in ι ⊣ κ composition whose Bias's nonetheless remain entirely unmodulated by the composition. This would falsify T4.b.

**(F3)** Show that the five-phase Do Be Talk Be Do is not universal — exhibit a coupling regime where the phases do not occur, or occur asymmetrically (e.g., only Do-Talk-Do without settling). Asymmetric-coupling regimes (where one stream refreshes without returning the push) are real in some regimes; whether they are framework counterexamples or refinements depends on whether the symmetric structure holds *on average* across extended interaction. This is an open empirical question.

**(F4)** Demonstrate a quantum-scale measurement-event that is structurally distinct from biological recognition or social communication in a way that cannot be absorbed into scale-dependent refresh-signatures. T4.d's cross-scale claim would fall if instances of the cycle at different scales were shown to have genuinely different categorical structure rather than different temporal realization.

**(F5)** Exhibit a stream whose contracted-open axis produces *attractive* dynamics in the contracted direction and *repulsive* in the open. This would invert T3.b/c and would indicate the entropy-reading of the axis is wrong. The framework predicts no such inversion is possible, but the prediction is testable.

**(F6)** Show that Bias(S) requires more than two coupling channels to model a real regime. If some interaction type cannot be reduced to structural or informational channels, the §6.4 formalization falls and must be expanded. We have not found such an interaction type, but Clayton's caveat in the T6 stress-test notes that interactions between non-cooperating dimensions may require a third channel.
