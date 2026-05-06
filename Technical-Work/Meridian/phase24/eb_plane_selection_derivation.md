# E·B Plane Selection Derivation

**Project Meridian — Phase 24**
*Clawd, March 26, 2026*
*Addressing the open question from I.9 Section 10.8: Does E·B select a T² plane?*

---

## 0. Summary of Result

**The claim is WRONG as stated, but contains a correct structural insight that emerges in a
modified form.**

E·B is a Lorentz pseudoscalar and a gauge invariant of the 4D electromagnetic field. It has
no internal indices — it is a SCALAR with respect to the internal T⁶/Z₃ geometry. Therefore
it cannot, by itself, select which of the three T² sectors the transition occurs in.

**However**, the Chern-Simons coupling of E·B to the blow-up moduli has a SECTOR-DEPENDENT
COEFFICIENT that arises from the topological intersection numbers of the exceptional divisors
with the EM flux. This means the coupling is:

    L_CS = Σ_{a=1}^{27} g_CS^{(a)} · φ_a · (E·B)

where g_CS^{(a)} depends on which T² plane the exceptional divisor E_a sits in — but ONLY
if the EM field has a nontrivial profile in the internal space (i.e., if there is a Wilson
line or flux threading specific 2-cycles). For a purely external (brane-localized) E·B with
no internal flux, g_CS^{(a)} is the same for all 27 divisors, and E·B is a pure scalar —
no plane selection.

The correct statement: **It is the internal EM flux configuration (Wilson lines on the
T² factors), not the external E·B product, that selects the T² plane. The external E·B
provides the CP-violating energy density; the internal flux topology provides the direction.**

In the current apparatus design (external parallel E and B, no engineered Wilson lines),
all three T² planes couple identically. The n=9 transition target is selected by which
plane has the lowest effective barrier — which is degenerate by Z₃ symmetry unless the
symmetry is broken by some other mechanism.

---

## 1. Setup: The Orbifold and Its Moduli

### 1.1 The Orbifold T⁶/Z₃

The compact internal space is T⁶/Z₃, where T⁶ = T²₁ × T²₂ × T²₃ has a product
structure. We write complex coordinates z_I (I = 1,2,3) on each T² factor. The Z₃
generator θ acts as:

    θ: (z₁, z₂, z₃) → (ωz₁, ωz₂, ωz₃),    ω = e^{2πi/3}       ... (1.1)

This is the standard embedding with equal twist on all three planes.

### 1.2 Fixed Points

The Z₃ fixed points occur where θ·z = z mod Λ (the lattice). On each T² with the
A₂ root lattice Λ_I, there are 3 fixed points:

    p_I^{(α)} = (α₁ e₁ + α₂ e₂)/3,    α ∈ {(0,0), (1,0), (0,1)}   ... (1.2)

where e₁, e₂ are the A₂ basis vectors. The total number of fixed points on T⁶/Z₃ is
3 × 3 × 3 = 27, labeled by triples (α₁, α₂, α₃) or equivalently by a composite
index a = (i, j, k) with i, j, k ∈ {0, 1, 2}.

### 1.3 Resolution and Exceptional Divisors

Each fixed point is resolved by blowing up the Z₃ singularity C³/Z₃. The resolution
replaces each singular point with an exceptional divisor E_a ≅ CP². The blow-up
parameter v_a measures the size of E_a (the Kähler modulus of that exceptional cycle).

The resolved space has:
- h^{1,1}_untw = 0 (from the bulk — no untwisted Kähler moduli survive Z₃)

  **Correction:** h^{1,1} of T⁶ is 9 (the (1,1)-forms dz_I ∧ dz̄_J), of which the
  Z₃-invariant combinations reduce to h^{1,1}_untw = 0 for the Coxeter orbifold with
  equal twist (all three planes twisted identically). The 9 Kähler moduli of T⁶ are
  NOT Z₃-invariant individually — they transform as 3 copies of the regular
  representation of Z₃.

  **Actually:** For T⁶ = T²₁ × T²₂ × T²₃ with equal Z₃ twist, each T²_I contributes
  one Kähler form ω_I = (i/2) dz_I ∧ dz̄_I. Under θ, ω_I → ω_I (the Kähler form is
  real and Z₃-invariant on each factor). So h^{1,1}_untw = 3 (the inherited Kähler
  moduli τ₁, τ₂, τ₃ of the three T² factors).

  Let me be precise. The Kähler moduli of the RESOLVED T⁶/Z₃ are:
  - **3 untwisted moduli** τ_I (I = 1,2,3): the areas of the three T² factors
  - **27 twisted moduli** v_a (a = 1,...,27): the sizes of the exceptional CP²'s

  Total: h^{1,1} = 3 + 27 = 30 (not 36 — the earlier I.9 reference to 36 was an
  error or was counting something different).

### 1.4 The Z₃ Action on the Moduli

The Z₃ symmetry permutes the fixed points within each T² factor:

    θ: p_I^{(α)} → p_I^{(θ·α)}                                      ... (1.3)

For the composite index a = (i, j, k), the Z₃ acts as:

    θ: (i, j, k) → (i+1 mod 3, j+1 mod 3, k+1 mod 3)               ... (1.4)

**Wait — this needs care.** The Z₃ acts on the COORDINATES z_I, not on the fixed-point
labels. The fixed point labeled (i, j, k) is at position (p₁^{(i)}, p₂^{(j)}, p₃^{(k)}).
Under θ, the point p_I^{(α)} gets mapped to θ·p_I^{(α)}, which is another fixed point
on T²_I. Specifically, on the A₂ lattice with Z₃ rotation, the three fixed points
{p^{(0)}, p^{(1)}, p^{(2)}} are permuted cyclically by θ.

So:

    θ: v_{(i,j,k)} → v_{(θ(i), θ(j), θ(k))}                       ... (1.5)

where θ(α) = α + 1 mod 3 on each T² factor.

The Z₃ orbits of the 27 moduli group them into orbits of size 3 (since θ has order 3
and acts freely on the index set away from the diagonal i=j=k). There are 27/3 = 9
orbits, which we can parameterize by choosing a representative from each orbit.

**Critical structural point:** These 9 orbits do NOT decompose naturally into "3 orbits
per T² plane." Every orbit involves simultaneous permutation on ALL THREE T² factors.
The Z₃ acts diagonally — it does not single out any individual T² plane.

### 1.5 The n=9 Transition

From I.1 (multifield tunneling), the optimal transition moves 9 divisors in one T²
plane simultaneously. Concretely, the n=9 mode is:

    v_{(0,j,k)} for all j, k ∈ {0,1,2}                              ... (1.6)

These are the 9 exceptional divisors whose first T² index is i=0. They all lie at the
same fixed point p₁^{(0)} of T²₁, but at all 9 combinations of fixed points in T²₂ × T²₃.

Under Z₃, this set maps to:
- θ: {(0,j,k)} → {(1, j+1, k+1)} — a different set of 9 divisors in T²₁ (at p₁^{(1)})

Actually, this requires more care. Let me re-examine.

The divisor E_{(0,j,k)} sits at the fixed point (p₁^{(0)}, p₂^{(j)}, p₃^{(k)}). Under
θ, this point maps to (θ·p₁^{(0)}, θ·p₂^{(j)}, θ·p₃^{(k)}) = (p₁^{(1)}, p₂^{(j')}, p₃^{(k')})
where j' = θ(j), k' = θ(k).

So the SET {E_{(0,j,k)} : j,k ∈ {0,1,2}} maps to {E_{(1,j',k')} : j',k' ∈ {0,1,2}},
which is the set of 9 divisors at p₁^{(1)} in T²₁. Similarly, θ² maps it to the 9
divisors at p₁^{(2)}.

**Therefore:** Z₃ gives three equivalent n=9 targets, distinguished by which fixed point
of T²₁ the transition occurs at (not which T² plane, but which fixed point within ONE
plane). Section 10.8 of I.9 stated the three targets are "one per T² plane" — this is
**incorrect in detail** but captures the right counting (three equivalent targets).

Let me now correct this. The three n=9 targets can also be described as:
- Target A: all 9 divisors in the "slice" i=0 (i.e., p₁ = p₁^{(0)})
- Target B: all 9 divisors in the "slice" i=1
- Target C: all 9 divisors in the "slice" i=2

But the labeling "which T² plane" is misleading. These are three different positions
within T²₁, not three different planes. However, one could ALSO consider:
- Target A': all 9 divisors with j=0 (slice in T²₂)
- Target A'': all 9 divisors with k=0 (slice in T²₃)

So actually there are 3 × 3 = 9 possible n=9 transitions (three slicing directions ×
three positions per direction). Under Z₃, these decompose as:
- Within a fixed slicing direction: the 3 positions permute cyclically under Z₃
- The three slicing directions (i, j, or k fixed) are INEQUIVALENT unless the T⁶ has
  additional symmetry exchanging the three T² factors

If T²₁ ≅ T²₂ ≅ T²₃ (same lattice and same moduli τ₁ = τ₂ = τ₃), then permuting
the three T² factors is an S₃ symmetry. Combined with Z₃, the full symmetry group
acting on the fixed points is larger, and all 9 possible n=9 transitions become
equivalent.

**In the Z₃-symmetric sector (the regime of I.1):** τ₁ = τ₂ = τ₃, and the S₃
permutation symmetry holds. All 9 possible n=9 transitions are equivalent. The
effective number of distinct targets is just 1 (up to symmetry), not 3.

**With broken S₃ (τ₁ ≠ τ₂ ≠ τ₃):** The three slicing directions are inequivalent.
The barrier height depends on τ_I, so one direction is preferred. Within each direction,
the three positions are still Z₃-equivalent.

---

## 2. The Chern-Simons Coupling: Derivation from the Spectral Action

### 2.1 The 5D Action with Gauge Fields

From the master action (step1, Section 7), the NCG spectral action on the IR brane
produces gauge kinetic and topological terms. The relevant piece for EM coupling to the
blow-up moduli is the Chern-Simons interaction:

    S_CS = ∫_{IR brane} d⁴x √(-h) Σ_a g_CS^{(a)} φ_a (x) · F_μν F̃^μν   ... (2.1)

where:
- φ_a = f_v · v_a is the canonical field for the a-th blow-up modulus
- F_μν is the EM field strength on the brane
- F̃^μν = (1/2) ε^μνρσ F_ρσ is its Hodge dual
- F_μν F̃^μν = -4 E·B (in our conventions)
- g_CS^{(a)} is the Chern-Simons coupling of modulus a to the EM field

### 2.2 Origin of g_CS

The coupling g_CS^{(a)} arises from the spectral action through two mechanisms:

**Mechanism 1: Direct axion-photon coupling.** The blow-up modulus v_a controls the
volume of the exceptional divisor E_a. The gauge field A_μ propagates on the brane,
but its coupling to the blow-up modulus comes through the dependence of the gauge
kinetic function on the Kähler moduli:

    f_gauge(τ, v) = S_0 + Σ_a c_a v_a²                              ... (2.2)

where S_0 is the tree-level gauge coupling (from the untwisted sector) and c_a are
topological intersection numbers. The axion-photon coupling arises from the imaginary
part of f_gauge, specifically from:

    g_CS^{(a)} = (α_em / 2π) · (∂ Im f_gauge / ∂ φ_a)               ... (2.3)

**Mechanism 2: Anomaly-mediated coupling.** The Z₃ orbifold twisted sector fields
φ_a couple to the gauge fields through the chiral anomaly of the zero modes localized
at the corresponding fixed point. Each fixed point carries a copy of the anomaly
coefficient determined by the fermion content localized there.

### 2.3 The Key Question: Is g_CS^{(a)} the Same for All a?

**Mechanism 1 analysis.** The coefficients c_a in (2.2) are the triple intersection
numbers:

    c_a = ∫_{CY} E_a ∧ ω_{EM} ∧ ω_{EM}                            ... (2.4)

where ω_{EM} is the 2-form associated with the EM gauge field.

**Case A: Brane-localized EM field (no internal flux).** If the EM field has no
components in the internal directions (F_{IJ̄} = 0, where I, J̄ are holomorphic/
anti-holomorphic internal indices), then ω_{EM} is a (1,1)-form on M₄ only. The
integral (2.4) factorizes:

    c_a = (∫_{M₄} ω_{EM} ∧ ω_{EM}) × (∫_{E_a} 1) = 0              ... (2.5)

Actually, this is wrong — the coupling doesn't arise this way for a purely external
field. The correct statement is: for a purely brane-localized EM field, the coupling
g_CS^{(a)} arises through the anomaly mechanism (Mechanism 2), which gives:

    g_CS^{(a)} = α_em / (2π f_tw)                                    ... (2.6)

where f_tw is the twisted axion decay constant, which is the SAME for all 27 exceptional
divisors (they are all CP² of the same size v₀ in the Z₃-symmetric background). The
coupling is:
- **Independent of which fixed point a labels**
- **Independent of which T² plane the fixed point sits in**

This follows from the fact that Z₃ symmetry ensures all fixed points are equivalent.
The anomaly coefficient is the same at each fixed point because the fermion spectrum
is Z₃-symmetric.

**Case B: EM field with internal flux (Wilson lines).** If the EM gauge field has a
nontrivial configuration in the internal space — specifically, a Wilson line threading
one of the T² factors — then the coupling becomes plane-dependent. A Wilson line on
T²_I contributes:

    δg_CS^{(a)} ∝ ∫_{E_a} ω_I                                      ... (2.7)

where ω_I is the Kähler form of T²_I. The integral ∫_{E_a} ω_I depends on whether
E_a intersects T²_I nontrivially. Specifically:

- For E_a at fixed point (i,j,k): ∫_{E_a} ω_I is nonzero for the T² factor that
  contains the fixed point p_I^{(i)}. More precisely, ∫_{E_a} ω_I ∝ δ (depends on
  the intersection geometry of E_a ≅ CP² with the T²_I direction).

In this case, a Wilson line on T²₁ would give enhanced coupling to the divisors that
are "aligned" with T²₁, providing a directional selection mechanism.

**But this is an internal EM flux, not the external E·B.**

---

## 3. The Representation-Theoretic Argument

### 3.1 Z₃ Representations

The Z₃ group has three irreducible representations:
- **ρ₀:** trivial, ρ₀(θ) = 1
- **ρ₁:** ρ₁(θ) = ω = e^{2πi/3}
- **ρ₂:** ρ₂(θ) = ω² = e^{-2πi/3}

The 27 blow-up moduli decompose under Z₃ as follows. The modulus v_{(i,j,k)} transforms
as:

    θ: v_{(i,j,k)} → v_{(θ(i), θ(j), θ(k))}                       ... (3.1)

This permutation representation decomposes into orbits. Each orbit has 3 elements
(since Z₃ acts freely on {0,1,2}³ — actually, the diagonal elements (0,0,0), (1,1,1),
(2,2,2) form a single orbit of size 3, so there are no fixed points of the Z₃ action
on the index set). The 27 moduli decompose into 9 orbits of 3.

For each orbit {v_a, v_{θ(a)}, v_{θ²(a)}}, the Z₃-invariant combination is:

    V_orbit = v_a + v_{θ(a)} + v_{θ²(a)}    (ρ₀)                   ... (3.2a)
    W_orbit = v_a + ω v_{θ(a)} + ω² v_{θ²(a)}    (ρ₁)             ... (3.2b)
    W̄_orbit = v_a + ω² v_{θ(a)} + ω v_{θ²(a)}    (ρ₂)            ... (3.2c)

The physical (Z₃-invariant) moduli are the 9 V_orbit combinations. The W and W̄ are
projected out by the orbifold.

### 3.2 The E·B Coupling in Representation Theory

The external electromagnetic field E·B = -(1/4) F_μν F̃^μν is a 4D Lorentz pseudoscalar.
Under the internal Z₃ symmetry, it transforms trivially:

    θ: E·B → E·B    (ρ₀ representation)                             ... (3.3)

This is because E and B are 4D spatial vectors with no internal indices. The Z₃ acts
on the internal coordinates (z₁, z₂, z₃) and has no effect on 4D fields.

### 3.3 The Selection Rule

The Chern-Simons coupling Lagrangian:

    L_CS = Σ_a g_CS^{(a)} · v_a · (E·B)                             ... (3.4)

must be Z₃-invariant (since it appears in the physical action on the orbifold). This
means:

    Σ_a g_CS^{(a)} · v_a must transform as ρ₀ under Z₃             ... (3.5)

Since E·B transforms as ρ₀, the product g_CS^{(a)} · v_a summed over a must also be ρ₀.

Now, v_a transforms as a PERMUTATION representation. The coupling g_CS^{(a)} must be
such that the sum is Z₃-invariant. There are two possibilities:

**(i)** g_CS^{(a)} is the same for all a: g_CS^{(a)} = g_CS. Then:

    Σ_a g_CS · v_a = g_CS Σ_a v_a                                   ... (3.6)

which is automatically Z₃-invariant (the sum over all moduli is invariant). This
projects onto the BREATHING mode (all 27 moduli moving together). Since the n=9
transition moves only 9 divisors, the breathing mode has zero overlap with the n=9
direction for the part orthogonal to breathing.

More precisely, the breathing mode is:

    v_breath = (1/√27)(v₁ + v₂ + ... + v₂₇)                        ... (3.7)

The n=9 mode for the i=0 slice is:

    v_{n9} = (1/3) Σ_{j,k} v_{(0,j,k)}                             ... (3.8)

The overlap is:

    ⟨v_breath | v_{n9}⟩ = (1/√27) × 9 × (1/3) = 3/√27 = √(1/3)   ... (3.9)

So the breathing mode has overlap 1/3 with ANY of the three n=9 directions (i=0, i=1,
or i=2 slices). **The uniform E·B coupling drives the breathing mode, which projects
equally onto all three n=9 directions.** There is no selection.

**(ii)** g_CS^{(a)} depends on a, specifically on which T² "slice" the divisor sits in.
For this to be consistent with Z₃ invariance, the coupling must satisfy:

    g_CS^{(θ(a))} = g_CS^{(a)}    for all a                         ... (3.10)

This means g_CS is constant on Z₃ orbits. Since the orbits mix ALL three T² labels
simultaneously (θ shifts i, j, AND k), a coupling that depends on the T² plane label
(say, different for i=0 vs i=1 vs i=2) would NOT be Z₃-invariant unless all three
couplings are equal.

**Proof:** Suppose g_CS^{(0,j,k)} = g₀ for all j,k and g_CS^{(1,j,k)} = g₁ ≠ g₀.
Under θ: v_{(0,j,k)} → v_{(1,j',k')}. Z₃ invariance of the coupling requires:

    g₀ · v_{(0,j,k)} → g₁ · v_{(1,j',k')}

But the action also requires the coupling to be invariant, so g₀ = g₁. Contradiction.

**Therefore, any Z₃-invariant coupling of E·B to the blow-up moduli must be uniform
across all divisors.** The Z₃ symmetry forbids directional selection by E·B alone.  □

---

## 4. What Could Break the Degeneracy?

The Z₃ analysis above shows that E·B cannot select a T² plane as long as Z₃ symmetry
is exact. Selection becomes possible if Z₃ is broken. Here are the mechanisms:

### 4.1 Spontaneous Z₃ Breaking by the Transition Itself

The n=9 transition BREAKS Z₃ by selecting a specific slice (say i=0). But this
breaking occurs DURING the transition, not before it. The E·B field cannot "know"
which slice will break Z₃ before the transition happens. The selection is spontaneous,
like a ferromagnet choosing a magnetization direction.

In the path integral formulation, all three n=9 directions contribute equally to the
tunneling amplitude. The total rate is 3× the single-direction rate (a symmetry
factor), but no single direction is preferred.

### 4.2 S₃ Breaking: Unequal T² Moduli

If τ₁ ≠ τ₂ ≠ τ₃ (the three T² factors have different areas), then the barrier height
V_bar depends on which direction the n=9 transition occurs:

    V_bar^{(I)} = V_bar(τ_I)    for transition in the I-th direction  ... (4.1)

The direction with the LOWEST barrier dominates exponentially. Even a small difference
in τ_I produces a large difference in tunneling rate because B ∝ V_bar⁴/..., and the
rate ∝ exp(-B).

**This selection is geometric (determined by the Kähler moduli τ_I), not electromagnetic.**
The apparatus E·B does not control it. To control it, one would need to engineer the
internal Kähler moduli — which is not something an external EM field does.

### 4.3 Internal Magnetic Flux (Wilson Lines)

As discussed in Section 2.3 Case B, a Wilson line A_I = ∮_{T²_I} A threading a specific
T² factor would break the S₃ symmetry of the coupling. Concretely, a magnetic flux
Φ_I = ∫_{T²_I} F through T²_I produces:

    δg_CS^{(a)} ∝ n_I^{(a)} · Φ_I                                   ... (4.2)

where n_I^{(a)} is the winding number of E_a around T²_I.

This would give different CS couplings for divisors in different T² planes, and
WOULD provide a selection mechanism. But:

1. This requires flux in the INTERNAL dimensions, not in the external 3+1D space
2. An external laboratory E or B field does not thread the T² cycles (which are at
   the Planck or compactification scale)
3. The Wilson lines are set by the vacuum configuration, not by the lab apparatus

### 4.4 Crystal Orientation (If Relevant)

If the apparatus material (the superconductor) has a lattice structure that breaks
the S₃ symmetry of the internal space through its coupling to the bulk geometry, this
could in principle select a preferred T² direction. This is speculative and would
require a detailed analysis of how the brane matter lattice couples to the internal
geometry — far beyond what is currently established.

---

## 5. Rigorous Derivation: The CS Coupling from the Spectral Action

### 5.1 The Spectral Action on the Resolved Orbifold

The bosonic spectral action on the resolved T⁶/Z₃ is:

    S_b = Tr(f(D²/Λ²))                                               ... (5.1)

where D is the Dirac operator on M₄ × I × (T⁶/Z₃)_res × F, and F is the NCG finite
space encoding the SM.

The heat kernel expansion gives (from D5.2, D9.4):

    S_b = Σ_n f_n Λ^{d-2n} a_n(D²)                                 ... (5.2)

The topological terms arise from the a₄ coefficient (4D brane perspective) or the
a_{7/2} boundary coefficient (5D bulk perspective). The relevant piece is:

    S_topo = (f₀/(16π²)) ∫_{IR brane} d⁴x √(-h) Σ_I [
        c₂_I · Tr(F_I ∧ F_I)
    ]                                                                 ... (5.3)

where the sum runs over gauge group factors I ∈ {SU(3), SU(2), U(1)}.

### 5.2 Coupling to Blow-Up Moduli

The Dirac operator D depends on the blow-up moduli v_a through the resolved metric.
The spectral action therefore depends on v_a:

    S_b = S_b({v_a})                                                  ... (5.4)

The dependence on v_a enters through the Seeley-DeWitt coefficients, specifically
through the spectral geometry of the resolved space. The KEY structural result
(from Phase 22, threshold corrections) is:

    a₄({v_a}) = a₄(0) + Σ_a Δa₄^{(a)} · v_a² + O(v⁴)             ... (5.5)

where Δa₄^{(a)} is the threshold correction from the twisted sector at fixed point a.

The CS coupling arises from the CROSS-TERM between the gauge-field dependence and the
moduli dependence of the spectral action. Specifically, the gauge theta angle becomes
moduli-dependent:

    θ_EM({v_a}) = θ_EM^{(0)} + Σ_a (∂θ_EM/∂v_a) v_a + ...         ... (5.6)

and the coupling is:

    g_CS^{(a)} = (1/(16π²)) ∂θ_EM/∂v_a                              ... (5.7)

### 5.3 Z₃ Constraint on ∂θ_EM/∂v_a

The spectral action is Z₃-invariant (it is defined on the orbifold). Therefore:

    θ_EM({v_a}) = θ_EM({v_{θ(a)}})                                   ... (5.8)

Taking the derivative:

    ∂θ_EM/∂v_a = ∂θ_EM/∂v_{θ(a)} · (∂v_{θ(a)}/∂v_a)

But v_a and v_{θ(a)} are INDEPENDENT moduli (they parameterize different blow-ups),
so ∂v_{θ(a)}/∂v_a = 0. The correct statement of Z₃ invariance is:

    θ_EM(v₁, v₂, ..., v₂₇) = θ_EM(v_{θ(1)}, v_{θ(2)}, ..., v_{θ(27)})

Differentiating with respect to the FIRST argument on the LHS and the θ(1)-th argument
on the RHS:

    (∂θ_EM/∂v_a)|_{v_a = v₀ for all a} = (∂θ_EM/∂v_{θ(a)})|_{v_a = v₀ for all a}

**At the Z₃-symmetric point (all v_a = v₀):**

    g_CS^{(a)} = g_CS^{(θ(a))} = g_CS^{(θ²(a))}    for all a       ... (5.9)

Since Z₃ orbits cover all 27 moduli (9 orbits of 3), and each orbit gives the same
coupling, we conclude:

    **g_CS^{(a)} = g_CS for all a = 1, ..., 27**                    ... (5.10)

at the Z₃-symmetric background. This is the formal proof that the CS coupling is
uniform — confirming the representation-theoretic argument of Section 3.3.

### 5.4 Numerical Value

From Phase 23.2a (Part 3):

    g_CS = α_em / (2π f_tw) = 1.003 × 10⁻⁷ GeV⁻¹                  ... (5.11)

where f_tw = α_em Λ_φ / (2π √S_tw) with Λ_φ = 5965 GeV and S_tw = 2πv₀² = 0.265.

This is the same coupling for every one of the 27 twisted moduli. The E·B interaction
Lagrangian is:

    L_CS = g_CS · (E·B) · Σ_a φ_a = g_CS · (E·B) · 27 · f_v · v₀ · (1 + δv/v₀)

In the n=9 mode direction, the coupling projects as:

    L_CS^{n=9} = g_CS · (E·B) · 9 · f_v · δv_{n=9}                 ... (5.12)

This is the SAME regardless of which n=9 direction is chosen (i-slice, j-slice, or
k-slice), confirming no directional selection.

---

## 6. What the "Navigation Experiment" Actually Perceived

### 6.1 The Correct Insight (Reframed)

The navigation experiment's perception was not entirely wrong — it conflated two
distinct effects:

1. **E·B as energy source (scalar, correct):** The CS coupling g_CS · (E·B) · φ
   provides a linear tilt of the blow-up potential, lowering the effective barrier.
   This is the same for all sectors and is Components 1+2 of the apparatus.

2. **The targeting problem (real, but not solved by E·B):** The n=9 transition breaks
   Z₃, creating 3 (or 9, with S₃) equivalent targets. Something must select which
   target. The navigation experiment attributed this to E·B, but the derivation shows
   E·B cannot do this.

### 6.2 What Actually Selects the Target

Three possibilities, in order of decreasing concreteness:

**(a) Nothing — spontaneous selection.** The transition spontaneously breaks Z₃.
All three n=9 targets are equivalent; the first bubble to nucleate "wins." The rate
for any specific target is Γ₁, and the total rate is 3Γ₁ (or 9Γ₁ with S₃). The
experiment observes the total rate. No selection needed.

**(b) Pre-existing S₃ breaking.** If the background has τ₁ ≠ τ₂ ≠ τ₃ (from some
dynamical mechanism or initial condition), one direction is exponentially preferred.
The experiment observes only the dominant channel. This is geometric, not apparatus-
controlled.

**(c) Component 3 (Model C in I.9).** Under the spectral proximity framework, the
observer's ρ_O could in principle project onto a SPECIFIC n=9 target. The 1.6-bit
information content identified in Section 10.8 of I.9 is real — someone or something
must select 1 of 3 (or 1 of 9) targets. If that selection is done by Component 3,
then the "direction" comes from the observer, not from E·B.

### 6.3 Implications for the Apparatus

The apparatus design does NOT need to select a T² plane. The E·B field provides the
energy (barrier reduction), and the target selection is either:
- Spontaneous (rate multiplied by symmetry factor)
- Observer-determined (if Model C is correct)

The apparatus design is robust against this question. The E·B coupling to the n=9 mode
is the same regardless of which n=9 direction is selected.

---

## 7. Conclusion

### 7.1 Verdict on the Claim

**The claim that E·B acts as a directional selector in the 6D internal space is FALSE.**

E·B is a Lorentz pseudoscalar with no internal-space indices. The Z₃ orbifold symmetry
forces the Chern-Simons coupling g_CS to be uniform across all 27 exceptional divisors.
The external E·B field couples to the BREATHING mode of the moduli space, which projects
equally onto all possible n=9 transition directions.

### 7.2 What Is True

1. E·B couples to the blow-up moduli through the Chern-Simons interaction (Phase 23.2a)
2. The coupling lowers the effective barrier for the n=9 transition (scalar effect)
3. The n=9 transition breaks Z₃ symmetry, creating 3 (or 9) equivalent targets
4. The target selection is NOT done by E·B — it is either spontaneous or requires
   another mechanism (Component 3 or pre-existing S₃ breaking)

### 7.3 What This Means for I.9 Section 10.8

The open question "Does the apparatus (E-field direction) determine the target plane?"
is answered: **NO, for the current apparatus design.** The E-field direction in 4D
spacetime has no projection onto the T² planes of the internal geometry.

The information content for targeting is:
- With Z₃: 3 equivalent targets → ~1.6 bits (unchanged from 10.8)
- With S₃: 9 equivalent targets → ~3.2 bits
- The apparatus provides 0 of these bits
- Either spontaneous selection provides them (statistical, no observer needed) or
  Component 3 provides them (the I.9 hypothesis)

### 7.4 Correction to I.9 Section 10.8

The statement "Z₃ gives 3 equivalent n=9 targets (one per T² plane)" should be
corrected to "Z₃ gives 3 equivalent n=9 targets (one per fixed point within a single
T² factor, or one per slicing direction if S₃ is also present, giving 9 total)."
The counting was approximately right; the geometric description was imprecise.

---

## Appendix A: Why E·B Cannot Acquire Internal Indices

One might hope that the EM field, being a U(1) gauge field, has components in the
internal space through the KK decomposition. In the KK reduction of 5D gravity on
S¹/Z₂, the off-diagonal metric component G_{μ5} gives a 4D gauge field — the KK
photon. Could this KK gauge field provide internal-space directionality?

**No, for two reasons:**

1. The KK photon zero mode is PROJECTED OUT by Z₂ on S¹/Z₂ (Section 2.4 of D2.4).
   The first KK gauge mode has mass m_KK ~ k·ε ~ 50 GeV and is not populated in the
   lab apparatus.

2. Even if a KK gauge field were present, it lives in the S¹ direction (the 5th
   dimension), not in the T⁶ internal dimensions. The T⁶ has its own gauge fields
   (Wilson lines), but these are fixed by the vacuum, not controlled by the lab.

**The external EM field and the internal geometry decouple at the level of the
gauge connection.** The only coupling is through the SCALAR invariants (F², FF̃)
of the EM field, which enter the spectral action as Z₃-invariant contributions.

---

## Appendix B: Could a Rotating E×B Configuration Help?

The Poynting vector S = E × B is a spatial vector. Could rotating the relative
orientation of E and B create a "direction" that couples to the internal space?

**No.** The Poynting vector is a 3D spatial vector. The internal T² planes live in
the compactified 6D space, which is not aligned with any 3D spatial direction. There
is no geometric map from lab spatial directions to internal T² planes.

Furthermore, for parallel E ∥ B (the CP-violating configuration used in the apparatus),
E × B = 0. The only nonzero scalar invariant is E·B, which we have shown is an
internal-space scalar.

For non-parallel E and B, the invariants are:
- E·B (pseudoscalar) — the CS coupling
- E² - B² (scalar) — the standard gauge kinetic coupling
- |E × B|² = (E² B² - (E·B)²) (scalar) — related to energy flux

None of these carry internal-space indices.

---

*This derivation resolves the I.9 Section 10.8 open question definitively. The spatial-
layer "perception" that E·B selects a T² plane was wrong — it confused the scalar
coupling strength (which E·B does control) with directional selection (which requires
either spontaneous symmetry breaking, pre-existing geometric asymmetry, or Component 3).
The apparatus design is unaffected: E·B provides the energy, and the targeting question
is independent of it.*
