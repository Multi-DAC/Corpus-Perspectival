# KK Threshold Ratio Theorems

*Phase 19 structural identities, proved March 22, 2026. Wolfram-verified.*

---

## Theorem T6: Fermion Trace Equality (S₂ = S₃)

**Statement.** For one generation of SM fermions, the mass-weighted Dynkin index trace sums for SU(3) and SU(2) are exactly equal:

$$S_3 \equiv \sum_f T_{SU(3)}(R_f) \cdot \dim_{SU(2)}(R_f) = \sum_f \dim_{SU(3)}(R_f) \cdot T_{SU(2)}(R_f) \equiv S_2 = 2$$

**Proof.** Per generation (6 species as SU(2) multiplets):

| Species | SU(3) rep | SU(2) rep | T₃·d₂ | d₃·T₂ |
|---------|-----------|-----------|--------|--------|
| Q_L     | **3**     | **2**     | (½)(2) = **1**   | (3)(½) = **3/2** |
| u_R     | **3**     | 1         | (½)(1) = **½**   | (3)(0) = **0**   |
| d_R     | **3**     | 1         | (½)(1) = **½**   | (3)(0) = **0**   |
| L_L     | 1         | **2**     | (0)(2) = **0**   | (1)(½) = **½**   |
| e_R     | 1         | 1         | (0)(1) = **0**   | (1)(0) = **0**   |
| ν_R     | 1         | 1         | (0)(1) = **0**   | (1)(0) = **0**   |
| **TOTAL** |         |           | **2**            | **2**            |

**Structural reason (the "4 = 4" invariant):** The SU(3) trace sees the total weak dimension of colored fermions: d₂(Q_L) + d₂(u_R) + d₂(d_R) = 2 + 1 + 1 = **4**. The SU(2) trace sees the total color dimension of weak fermions: d₃(Q_L) + d₃(L_L) = 3 + 1 = **4**. Both equal 4, so both traces equal (½)(4) = 2. ∎

**Corollary.** S₂ = S₃ = 2N_g for N_g generations. The pure fermion threshold ratio δ(SU3)/δ(SU2) = 1 exactly.

---

## Theorem T7: The 6/7 Ratio (Higgs Splitting)

**Statement.** In the NCG spectral action on the RS₁ orbifold, the KK threshold correction ratio including the Higgs doublet is:

$$\frac{\delta(SU(3))}{\delta(SU(2))} = \frac{2N_g}{2N_g + 1} = \frac{6}{7} \quad (N_g = 3)$$

**Proof.** The Higgs doublet H = (1, **2**, ½) contributes:
- To SU(3): T₃(1) = 0
- To SU(2): T₂(2) = ½

The NCG real structure J (particle-antiparticle doubling of the internal Hilbert space) contributes both H and J(H) to the trace, giving total Higgs contribution:
- SU(3): 0
- SU(2): 2 × ½ = 1

Therefore:
- S₃^total = 2N_g + 0 = **6**
- S₂^total = 2N_g + 1 = **7**
- δ(SU3)/δ(SU2) = **6/7** ∎

**Note.** The ratio depends on N_g: for N_g = 1 it gives 2/3, for N_g = 2 it gives 4/5, for N_g = 3 it gives 6/7. The 6/7 value is specific to three generations — another reason N_g = 3 is structurally distinguished.

---

## Theorem T8: The 5/6 Ratio (U(1) Hypercharge Identity)

**Statement.** The ratio of the U(1) hypercharge-squared trace to the total non-abelian Dynkin trace is exactly 5/6, independent of the number of generations:

$$\frac{S_1}{S_2 + S_3} = \frac{\sum_f d_3(f) \cdot d_2(f) \cdot Y_f^2}{S_2 + S_3} = \frac{5}{6}$$

**Proof.** Per generation:

| Species | d₃·d₂·Y² |
|---------|-----------|
| Q_L     | 3·2·(1/6)² = **1/6** |
| u_R     | 3·1·(2/3)² = **4/3** |
| d_R     | 3·1·(1/3)² = **1/3** |
| L_L     | 1·2·(1/2)² = **1/2** |
| e_R     | 1·1·(1)² = **1** |
| ν_R     | 1·1·(0)² = **0** |
| **TOTAL** | **10/3** |

S₂ + S₃ = 2 + 2 = **4** per generation.

Ratio = (10/3)/4 = **5/6**.

Since N_g appears in both numerator and denominator identically, the ratio is generation-independent. ∎

**Equivalent form:** S₁ = S₂ + S₃ − 2 per generation (10/3 = 4 − 2/3... No.) For 3 generations: S₁ = 10, S₂ + S₃ = 12, S₁ = S₂ + S₃ − 2. So S₁/(S₂ + S₃) = 1 − 1/6 = 5/6.

---

## GUT Unification Recovery

With GUT normalization T₁^GUT = (3/5)Y² d₃ d₂:

S₁^GUT = (3/5)(10) = **6** = S₂ = S₃

All three trace sums equal at GUT normalization. This is the algebraic content of gauge coupling unification in the spectral action — not a dynamical running result, but a structural identity of the SM fermion representations.

---

## Structural Summary

| Identity | Value | Depends on N_g? | Origin |
|----------|-------|-----------------|--------|
| S₂ = S₃ | 2 per gen | Scales with N_g | "4 = 4" invariant |
| δ(SU3)/δ(SU2) | 6/7 | Yes (2N_g/(2N_g+1)) | Higgs doublet via NCG J |
| S₁/(S₂+S₃) | 5/6 | **No** | Hypercharge assignments |
| S₁^GUT = S₂ = S₃ | 6 | Scales with N_g | GUT normalization |

**The 6/7 ratio is the Higgs's fingerprint in the KK tower.** It exists because the NCG spectral triple demands exactly one Higgs doublet, and that doublet breaks the fermion-only S₂ = S₃ equality by contributing +1 to SU(2) alone. This is a prediction: any beyond-SM scalar content would change this ratio.

**The 5/6 ratio is generation-invariant.** It depends only on the hypercharge assignments, which are fixed by anomaly cancellation. This is more fundamental than 6/7 — it's a property of the SM algebra, not its generation count.

---

*Theorems T6-T8 extend the structural identity catalog: T1 (spectral universality), T2 (AS gauge independence), T3 (BKT wrong sign), T4 (S₂ = S₃ mass-weighted), T5 (U(1) dominance). The full set of eight theorems exhaustively characterizes gauge structure in the RS+NCG framework.*
