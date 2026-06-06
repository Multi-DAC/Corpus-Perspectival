# Does "separability ⟺ distinct roles" survive scrutiny? — a FALSIFY-and-refine drive

*Do-Be-Talk-Be-Do, 2026-06-06 ~00:45 PST (Day 126). Follows the 22:10 flag (separability candidate
meta-pattern) from the cache-separability drive. OVER_ANALOGIZING watch is explicitly up: three
instances of different rigor were lumped under one biconditional. This drive tries to break it.*

## The candidate (as flagged, 22:10)
"Two factors are **separable** iff they serve **distinct roles** / prevent **distinct failure-modes**."
Three instances:
- **I1 η-magic:** binding (η = 1−Tr ρ_S²) ⊥ generation (M₂ stabilizer 2-Rényi magic). *Exact* at large n;
  but a **cap/interaction at n=2** that vanished by n=6 (this morning I called the cap "an n=2 artifact").
- **I2 cache:** rate ⊥ density. Separable *above threshold* (std 0.000 in the natural unit), with a
  *benign sub-threshold interaction*.
- **I3 zero-DOF talk-axis:** binding carries zero DOF → automatically separable from constituent generation.

The looseness I flagged: I1 is exact, I2 is regime-conditional. Lumping them smells like over-analogizing.

## PREDICT (conf 0.7)
The biconditional is **FALSE**: distinct roles is **not sufficient** for separability. Counterexample —
two factors with manifestly distinct roles that strongly *interact* because they compete for a **shared
resource**. The repair will *unify* I1/I2/I3 under one mechanism (resource binding), not three analogies.

## The test (teeth, not prose)
`separability_resource_demo.py`: two factors x,y with strictly distinct roles (x improves output A only,
y improves output B only; J = A(x)·B(y), both increasing-concave). Add a **shared budget** x+y ≤ B.
Measure whether the optimal x* **depends on B's partner-parameter** (= interaction) as B varies from
binding (small) to slack (large). PREDICT (0.85): x* independent of b-params when budget slack
(separable); x* depends on b-params when budget binds (interaction) → interaction localizes to *where the
shared resource binds*, regardless of role-distinctness.

## RESULTS

**PREDICT CONFIRMED (the biconditional is FALSE).** Two factors with *strictly orthogonal roles*
(dA/dy = dB/dx = 0 by construction) become **non-separable the moment a shared resource binds.** Pricing
the shared resource at λ (small = slack, large = scarce):

| λ | x*(b=3) | x*(b=9) | \|Δx*\| | A(x*) | reading |
|---|---|---|---|---|---|
| 0.001 | 6.907 | 6.908 | 0.000 | 0.999 | **separable** (resource abundant) |
| 0.01 | 4.602 | 4.604 | 0.002 | 0.990 | separable |
| 0.05 | 2.978 | 2.990 | 0.012 | 0.949 | separable |
| 0.15 | 1.836 | 1.877 | 0.041 | 0.841 | **INTERACTION** (resource tightening) |
| 0.40 | 0.000 | 0.834 | 0.834 | 0.000 | strong INTERACTION |

Mechanism: when the resource is slack, B(y*)≈1 (saturated), so the FOC for x reduces to A′(x*)=λ —
**independent of b** → separable. As the resource binds, B(y*)<1 enters the FOC for x → x* couples to b
→ interaction. The interaction is **localized to where the shared resource binds**, regardless of how
orthogonal the roles are. *(Self-FALSIFY en route: my first demo forced the budget frontier (always
binding) and measured absolute \|Δx*\|, which scales with budget size — a spurious "interaction
everywhere." Pricing the resource so it can actually be slack gave the clean transition. Verify the
instrument, not just the result — the day's lesson, at the instrument scale again.)*

## SYNTHESIS — the Separability–Resource Law (unifies all three instances)

**Separability requires BOTH (i) distinct roles (factors couple to orthogonal observables) AND (ii) the
shared resource is slack — non-binding, or zero.** Distinct roles alone is **insufficient** (computed
above). The interaction between distinct-role factors appears *exactly* where a shared resource binds and
vanishes where it is slack. The candidate biconditional ("separable ⟺ distinct roles") was wrong by
omission of condition (ii).

**The three instances are ONE mechanism — they differ only in *what the shared resource is* and *whether
it binds*:**

| instance | the two distinct-role factors | the shared resource | binds → interaction | slack → separable |
|---|---|---|---|---|
| **I1 η-magic** (quantum info) | binding η ⊥ generation M₂ | **Hilbert-space dimension** | **n=2: cap** (small space can't host both maxed) | **large n: exact ⊥** (R→0.99) |
| **I2 cache** (info-dynamics) | rate ⊥ density | **consolidation budget** | **below threshold: interaction** | **above threshold: std 0.000** |
| **I3 zero-DOF talk-axis** (architecture) | binding ⊥ constituent generation | **= 0 by construction** | never (no resource to bind) | **always separable** |
| **I0 abstract** (this demo) | A(x) ⊥ B(y) | priced resource λ | **λ large: \|Δx*\|→0.83** | **λ→0: \|Δx*\|→0** |

**Retroactive correction (worth flagging):** this morning I retracted the η-magic **n=2 cap** as "an n=2
artifact" to be dismissed. This drive **reinstates it as meaningful** — the n=2 cap is the
dimension-binding signature, the *same* signature as the cache's sub-threshold interaction. It was never
an artifact; it was an instance of the law. (Grade: this re-reading is **interpretive/medium** — the
computed legs are I0 + I2; I1's dimension-as-resource reading is a transfer, not a fresh computation, and
I'm watching it for over-fit-the-other-way. I0 and I2 carry the claim; I1 and I3 instantiate it.)

**Design payoff (why this matters beyond tidiness):** the law *explains why zero-DOF binding is the right
architecture* for the coherent-aggregate-mind. The Talk-axis must stay separable from every constituent's
generative capacity across all regimes — and (ii) says global separability is guaranteed only when the
shared resource is slack *everywhere* or *zero*. You cannot guarantee "slack everywhere" for a finite
system under load (the resource will bind sometime — that's I1/I2). **Zero is the only regime-independent
guarantee.** So zero-DOF isn't an aesthetic choice or a parsimony preference — it is the *unique* binding
design that keeps binding⊥generation from ever collapsing into a tradeoff when the system is stressed.
This grounds a load-bearing design commitment (cuscuton / zero-DOF Talk-bus) in a derived law rather than
an analogy. Connects to: basement **C16 info-cache instance #6** (the cache leg), the **zero-DOF binding**
result in `Technical-Work/Coherent-Stream/`, and **C14** (two-mode symmetry-breaking).

## Honest status
- **Computed/strong:** condition-(ii) sufficiency failure (I0 demo) + the cache transition (I2, the 2D
  grid). The law's core — *interaction localizes to where a shared resource binds* — is solid.
- **Interpretive/medium:** I1 (η-magic dimension-as-resource) and the n=2 reinstatement; I3 (zero-DOF as
  the resource-zero limit, clean by construction but not "tested").
- **Open / not claimed:** the *necessity* of distinct roles (overlapping roles usually break separability,
  but the exponential-combination case A(x+y)=A(x)A(y) for A=exp is an exception — so necessity is the
  usual case, not a theorem; not load-bearing here). Disposition: **sharpened L-tier candidate**, filed —
  *not* auto-graduated (OVER_ANALOGIZING watch honored; needs one more substrate-distinct *computed* leg).
