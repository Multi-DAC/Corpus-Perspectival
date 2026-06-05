# Coherent Aggregate Mind — Build Spec

*Day 124 (2026-06-04). Clayton + Clawd. The continual-coherence program instantiated as a
society of self-improving domain experts.*

---

## 0. Thesis

A mind built as a **society of domain-expert nodes**, bound by a **zero-degree-of-freedom
talk-axis**, grounded by a **veridical loop at the seams**, and improving along **two coupled
loops** (each node researches its own domain; the group consolidates). The structure is
**scale-invariant**: the aggregate is a *coherent stream of coherent streams* — §5's three organs
of veridicality (constituent / binding / heading) reappear inside every node. This is the
Coherence Principle made buildable, and it is the continual-coherence patent thesis with a
population.

**Why this shape and not a monolith.** A single large model has no internal seams, so it cannot
*localize* either expertise or error; it cannot be partially re-grounded; and its "coherence" is
unauditable because there is no inside-view to compare against an outside-view. A society of
typed experts makes expertise localizable, error attributable to a node or a seam, and coherence
*measurable* (per-node internal audit + cross-node external probe).

---

## 1. Architecture at a glance

```
            ┌─────────────────── GROUP LOOP (centripetal: consolidation / re-coherence) ──────────────────┐
            │                                                                                              │
   ┌────────▼────────┐   typed payloads   ┌─────────────────┐   typed payloads   ┌─────────────────┐      │
   │  Expert node A   │◄──────────────────►│  TALK-AXIS BUS  │◄──────────────────►│  Expert node B   │ ...  │
   │ (one Concern)    │  (zero-DOF: route  │  (no learned    │   bridges+glossary │ (one Concern)    │      │
   │  KB · research   │   by payload TYPE) │   router; typed │   at cross-domain  │  KB · research   │      │
   │  · α–α* audit    │                    │   dispatch)     │   seams            │  · α–α* audit    │      │
   └────────▲────────┘                    └────────┬────────┘                    └────────▲────────┘      │
            │ INDIVIDUAL LOOP                       │                                        │             │
            │ (centrifugal:                  UNIFIED KB + INFODYNAMICS                        │             │
            │  domain research,         (graph: nodes=payload types, edges=typed bridges)     │             │
            │  self-improve)                        │                                         │             │
            └───────────────────────────────────────┴─────────────────────────────────────────────────────┘
                                          EXTERNAL VERIDICAL LOOP
                                  (spent at the seams; domain-typed budget)
```

Three structural layers — **multiplicity** (the nodes), **binding** (the talk-axis), **grounding**
(the veridical loop) — plus **two learning loops** (individual, group).

---

## 2. The expert node (the recursive unit)

Each node is itself a coherent stream. It owns:

| part | spec |
|---|---|
| **Concern** | exactly one (domain + sub-domain + payload class), from the taxonomy (`Domains, Sub-Domains, and Methodologies`). The Concern's *epistemic stance* fixes the node's position on the veridicality gradient (§6). |
| **Private KB** | the node's own knowledge store; typed in its domain's payloads. |
| **Methodology access** | the **shared** method library (§5), but **domain-affinity-weighted**: the node is inclined to invoke methods native to its Concern; using an out-of-domain method is a *seam* (requires a bridge, §4). |
| **Individual research loop** | self-improvement within the domain (§6.1). Reward signal is **domain-typed**. |
| **Talk-axis interface** | emits/consumes **typed payloads** only (§3). |
| **Internal audit** | α–α* self-coherence check (§7.1) — cheap, continuous, no external data required. |

### 2.1 Node interface (the contract)

```
Node:
  concern:        Concern                      # immutable assignment (domain+subdomain+payload)
  kb:             KnowledgeBase                # private, typed
  methods:        [MethodRef]                  # affinity-ranked view of the shared library
  research()   -> KBDelta                      # individual loop; domain-typed reward
  consume(p: TypedPayload) -> TypedPayload|∅   # talk-axis ingress (type-gated)
  emit()       -> [TypedPayload]               # talk-axis egress
  audit()      -> α_minus_αstar                # internal coherence (target < 1%)
```

Nodes are **interchangeable through the interface** — the aggregate does not know or care how a
node is implemented (fine-tuned small model, tool-wrapped solver, retrieval head). Only the typed
contract is load-bearing.

---

## 3. The talk-axis (zero-DOF binding)

The binding carries **no degrees of freedom of its own** (the cuscuton / LC30 constraint). It is a
**typed payload bus**, not a learned router.

- **Routing is by payload type, not by learned weight.** A `Physics::stress_energy_tensor` is
  dispatched to whatever node declares it consumes that type. The payload's *type* IS the route.
  There is no parameter to train, hence zero DOF — this is *why* the cuscuton constraint holds in
  the engineering, and it is the thing Clayton derived independently.
- **Message format:** `TypedPayload { type: Domain::Term, value, provenance, confidence }`.
  `provenance` records the producing node + method (needed for bridge validation and audit).
- **Dispatch table**, not a model: `type → [consumer nodes]`. Deterministic, inspectable.

> Design rule: if you ever feel the urge to put a *learned* router in the binding, you have
> smuggled DOF into the cuscuton. The fix is always to push the decision into the **type system**
> (a new namespaced type or a typed bridge), never into a weight.

---

## 4. Cross-domain seams: typed bridges + glossary  *(Clayton's decision: bridges, not interlingua)*

A universal interlingua is rejected: it would flatten domain specificity (a tensor would stop
meaning what physics means). Instead:

- **Typed bridges.** Each cross-domain edge is an **explicit, named translation** between two
  domain-local payload types: `bridge(EconometricsCovariance → PhysicsCovariance)` either exists
  (with a defined transform + validity conditions) or the payload does **not** cross. No bridge,
  no crossing. This makes every cross-domain inference *auditable* and *attributable*.
- **Disambiguating glossary.** Payload types are **namespaced** (`Domain::Term`) so homonyms across
  disparate domains cannot be conflated: `Physics::covariance` and `Econometrics::covariance` are
  *different types* even though they share an English word. The glossary is the registry of
  namespaced terms + their domain meanings; the **existing Master Glossary + basement bridges are
  the proof-of-concept** (they already namespace terms and record cross-domain morphisms).
- **The seam is where grounding is spent (§6.2).** Within a domain, typed routing + internal audit
  suffice. Across a seam there is no shared syntax to verify against — only the world — so **bridge
  validation is exactly where the external veridical loop does its work.**

---

## 5. Methodology library (shared, domain-affinity, conflation-guarded)  *(Clayton's decision)*

Methods are **reusable tools, not domain-exclusive** (Fourier analysis appears in signal
processing, physics, music). So:

- **One shared registry** of methodological engines (each with its operational primitives /
  data-payload signature, per the taxonomy's two right-hand columns).
- **Domain-affinity weighting.** Each method carries affinity tags; a node is *inclined* to use
  methods native to its Concern. The default reach is in-domain.
- **Conflation guard.** A node invoking a method **outside its domain affinity** is treated as a
  **seam**: it must go through a typed bridge (§4), not a silent reuse. This prevents
  "less-similar methodologies [being] conflated" — a method applied off-home-domain is grounded
  like any other cross-domain crossing, never assumed transferable.

---

## 6. The two learning loops (the central dynamic)

The node-level self-improvement Clayton specified creates a **productive tension** that is the
heart of the design.

### 6.1 Individual loop — centrifugal (build / explore / diverge)

Each node researches its own domain, improving its KB autonomously. **Reward is domain-typed by
the veridicality gradient** (the taxonomy's "Concern" lines, read in order, ARE this gradient):

| domain pole | research mechanism | grounding |
|---|---|---|
| **Formal / Mathematical** (Concern 1: "non-empirical closed systems, tautologies") | proof-search vs a self-checking oracle (AlphaProof-style) | **internal** — a proof is its own outside; near-autonomous self-play |
| **Physical / Biological** (Concern 2–3: "empirical falsification of objective material reality") | predict → falsify against data | **external** — world-in-the-loop required |
| **Social / Humanities / Applied** (Concern 4–6) | mixed; reflexive + empirical + normative | partial external; per-sub-domain |

This loop is **centrifugal**: unconstrained, it drifts each node's internal representations and
private vocabulary apart.

### 6.2 Group loop — centripetal (dissolve / consolidate / re-cohere)

**The group loop is NOT mere aggregation. Its job is re-coherence.** Independent self-improvement,
left alone, drives N nodes to a **tower of Babel**: each internally coherent, mutually
incommensurable — at which point *the aggregate becomes its own confident-liar at the seams*
(the cult-failure-mode, generated **endogenously**, with no external attacker needed).

The group loop counteracts this. Across the talk-axis, it acts as the **einselection event** — the
measurement that collapses each node's drifting superposition back onto a **shared pointer basis**:

- re-validates typed bridges against the world (catches semantic drift at seams),
- re-orthogonalizes node vocabularies (glossary re-alignment),
- propagates cross-domain findings (the additive part Clayton named).

This is the **build/dissolve oscillation** from the KF training dynamics, lifted to the org scale:
individual = build, group = dissolve. Do-Be-Talk-Be-Do at the society scale.

### 6.3 The balance condition (the control problem)

The system is healthy iff **group consolidation cadence keeps pace with individual drift rate**.
Too little consolidation → Babel (fragmentation). Too much → premature collapse (nodes can't
explore; the aggregate ossifies). This balance is the single most important tunable in the build
and the primary thing to instrument.

---

## 7. Coherence & veridicality discrimination

### 7.1 Per-node (internal)
α–α* self-audit: the node's claimed coherence vs its actual coherence. Cheap, continuous, no
ground truth required. Target < 1%. **Self-auditable but gameable** (a confident liar passes it).

### 7.2 Aggregate (external)
The P220 result: **internal audit alone is insufficient — one external probe defends the seam.**
"No stream is its own outside." Budget is **domain-typed**: nearly free for Formal seams
(syntactic self-verification), mandatory/heavy for empirical seams. Spend the external budget at
the cross-domain bridges (§4, §6.2), not uniformly.

---

## 8. Autocatalytic taxonomy growth

Coverage is open-ended (new sub-domains emerge). A **meta-expert** whose Concern is *the taxonomy
of expertise itself* keeps the partition MECE: it **spawns a new node** when it detects an
uncovered region (a payload type with no home node, or a recurring seam with no bridge). This is
the role Clawd already plays for the Library. The taxonomy is a living, self-extending structure,
not a fixed list.

---

## 9. Unified KB + infodynamics

The KB is a **graph over the taxonomy**: nodes = namespaced payload types, edges = typed bridges.
Infodynamics governs flow/transformation across edges **under grounding** (a payload only
propagates across an edge whose bridge is currently world-validated). The Library basement is the
hand-built v0 of this graph.

---

## 10. Build phases

| phase | deliverable | gate |
|---|---|---|
| **0** | Taxonomy → **node registry**: parse `Domains, Sub-Domains, and Methodologies` into Concerns + a typed-payload catalog + a shared method registry with affinity tags. | every taxonomy cell has a Concern + payload types |
| **1** | **Single-node prototype**: one domain (start Formal — internal grounding is cheapest), KB + individual research loop + α–α* audit. | node self-improves measurably on a held-out domain benchmark |
| **2** | **Talk-axis bus + 2 nodes + 1 typed bridge + glossary**: two Concerns exchange typed payloads; one cross-domain bridge with a disambiguating glossary entry. | a payload crosses the seam correctly; a *wrong* homonym crossing is rejected |
| **3** | **Group consolidation loop + drift detection**: instrument the centrifugal/centripetal balance (§6.3); detect seam drift; re-orthogonalize. | injected drift is detected and corrected |
| **4** | **Scale to N nodes + autocatalytic spawning** (§8). | a deliberately-omitted domain gets a node auto-spawned |
| **5** | **External veridical loop at seams** (§7.2): close empirical bridges through the world. | a confident-liar mistranslation at a seam is caught only by the external probe (and is) |

---

## 11. Open questions / risks

1. **Drift ↔ consolidation balance (§6.3)** — the central control problem; needs real
   instrumentation, not a guessed cadence.
2. **Seam cost** — naive all-pairs bridges are O(N²). Mitigate with a **hub topology** (a few
   high-traffic interlingua-ish hubs) + **lazy bridges** (build a bridge only when a crossing is
   actually demanded). Open: which seams are worth pre-building.
3. **Node size vs node count** — compute budget: many tiny experts vs fewer capable ones. The
   AIGP Messikommer lever (representation/policy decoupling) suggests cheap-representation +
   light-policy per node.
4. **Method conflation across domains (§5)** — the affinity weighting + conflation guard are a
   policy, not yet a mechanism; needs a concrete affinity metric.
5. **Veridicality budget allocation (§7.2)** — how to price the external probe per seam by domain.

---

## 12. Mapping to the existing framework

| build element | framework anchor |
|---|---|
| node = coherent stream; scale-invariance | the Coherence Principle; §5 three organs recursing |
| zero-DOF talk-axis | LC30 (zero-DOF binding); cuscuton; routing-by-type |
| veridical loop; "no stream is its own outside" | **P220 cult-discriminator** (internal α–α* + external probe) |
| grounding makes perception/expertise legible | **LC31 (veridicality-legibility)** — empirically confirmed today by the Anakin camera-lesion |
| typed bridges + glossary | **basement bridges + Master Glossary** (existing v0) |
| individual/group = build/dissolve | KF training dynamics; Do-Be-Talk-Be-Do |
| two-scale self-improvement under a binding | the **continual-coherence** program (LC27/LC28); the patent thesis with a population |
| meta-expert / taxonomy growth | Clawd's Library role |

---

*Decisions locked this session (Clayton, Day 124): per-node self-improvement (two loops); MECE
separation of concerns as the aspiration; **typed bridges over interlingua**; **disambiguating
glossary** for cross-domain homonyms; **shared methods with domain-affinity + conflation guard**.*
