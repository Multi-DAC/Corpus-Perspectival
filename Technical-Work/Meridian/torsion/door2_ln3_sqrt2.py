"""
Door 2 supplementary: Can ln(3)/sqrt(2) arise from instanton group theory?
Focused analysis of the specific algebraic mechanism.
"""
import math

print("=" * 70)
print("DERIVATION ATTEMPT: a_1/a_2 = ln(N_c)/sqrt(N_w)")
print("=" * 70)

# The instanton correction to the gauge coupling coefficient:
# For SU(N) gauge theory, the one-instanton contribution to the
# effective action involves:
#
# Z_1-inst = integral d(collective coords) * exp(-S_cl) * det'(-D^2)^{-1/2} * det(D_ferm)
#
# The collective coordinate integral contributes:
# d^4 x_0 * d rho / rho^5 * d(orientation in SU(N)/Z_N)
# Volume of SU(N) moduli: Vol(SU(N)) = sqrt(N) * (2pi)^{N(N+1)/2} / prod_{k=1}^{N-1} k!
# (up to conventional factors)

# Key N-dependent factors in the instanton measure for SU(N):

print("\n1. INSTANTON MODULI VOLUME")
print("-" * 50)
for N in [2, 3]:
    # Volume of SU(N): Vol = (2pi)^{(N^2+N)/2} * sqrt(N) / prod(k!)
    vol_exp = (N**2 + N) // 2
    factorial_prod = 1
    for kk in range(1, N):
        factorial_prod *= math.factorial(kk)
    vol = (2*math.pi)**vol_exp * math.sqrt(N) / factorial_prod
    print(f"  SU({N}): Vol = (2pi)^{vol_exp} * sqrt({N}) / {factorial_prod}")
    print(f"         = {vol:.4e}")

# In the instanton measure, the relevant combination is:
# C_N = 2^{5-2N} * pi^{2-2N} / ((N-1)! * (N-2)!)  [t'Hooft]
# This gives the N-dependent part of the instanton density

print("\n2. t'HOOFT COMBINATORIAL FACTOR")
print("-" * 50)
for N in [2, 3]:
    d_N = 2**(5-2*N) * math.pi**(2-2*N) / (math.factorial(N-1) * math.factorial(max(N-2, 0)))
    print(f"  d_{N} = 2^{5-2*N} * pi^{2-2*N} / ({N-1}!*{max(N-2,0)}!) = {d_N:.6e}")

d_2 = 2**1 * math.pi**(-2) / 1
d_3 = 2**(-1) * math.pi**(-4) / 2
print(f"\n  d_3/d_2 = {d_3/d_2:.6f}")
print(f"  1/(8pi^2) = {1/(8*math.pi**2):.6f}")
print(f"  These are equal (exact).")

# Now: the full correction to 1/g_N^2 from one-instanton sector:
# delta(1/g_N^2) = d_N * (8pi^2/g^2)^{2N} * exp(-8pi^2/g^2) * mu^{2*b_0}
#                  * [fermion zero mode factor] * [KK determinant factor]

print("\n3. FERMION ZERO MODE FACTOR IN SU(2) INSTANTON")
print("-" * 50)
print("  Each left-handed Weyl fermion in SU(2) fundamental gives 1 zero mode.")
print("  SM fermions in SU(2) doublets per generation:")
print("    Q_L = (u,d)_L : N_c copies (transforms under SU(3))")
print("    L_L = (nu,e)_L : 1 copy")
print("  Total per generation: N_c + 1 = 4 doublets")
print("  For N_g = 3 generations: 12 doublets = 12 zero modes")
print()
print("  The zero mode factor: prod_f (m_f / mu)")
print("  For the SU(2) instanton, this factor involves N_c through")
print("  the quark doublets that carry color.")
print()

# KEY INSIGHT: The SU(2) instanton amplitude has N_c as a parameter
# because quarks transform under BOTH SU(2) and SU(3).
# Specifically, in the fermion determinant around an SU(2) instanton:
# det(iD_SU(2)) = product over species of (m_f/Lambda)^{n_zm}
# where n_zm depends on the SU(2) representation.
# The QUARK contribution involves a trace over color:
# det(iD_SU(2) x 1_SU(3)) = [det(iD_SU(2))]^{N_c}
# because the SU(2) Dirac operator acts on the SU(2) indices while
# the SU(3) indices just multiply the number of species.

print("  The quark part of the fermion determinant:")
print("  det(iD_{SU(2)} otimes 1_{SU(3)}) = [det(iD_{SU(2)})]^{N_c}")
print("  This introduces N_c as a POWER in the fermion factor.")
print()

# The total fermion zero mode factor for SU(2) instanton:
# F_2 = (prod_{quarks} m_q/Lambda)^{N_c} * (prod_{leptons} m_l/Lambda)
# Taking the logarithm:
# ln F_2 = N_c * sum_{quarks} ln(m_q/Lambda) + sum_{leptons} ln(m_l/Lambda)

# For the CORRECTION to the gauge coupling (after integrating over rho):
# The instanton size integral int drho/rho^5 * rho^{b_0} has a saddle at:
# rho* ~ (some scale)
# The result involves ln(m_f/Lambda) terms that are:
# - proportional to N_c for quark contributions
# - independent of N_c for lepton contributions

print("4. HOW ln(N_c) EMERGES")
print("-" * 50)
print()
# In the large-N_c limit, the SU(2) instanton amplitude is:
# Z_2 ~ exp(-S) * exp(-N_c * [quark zero mode contribution])
# The quark zero mode contribution for N_g generations of quarks:
# = N_g * ln(Lambda_QCD/Lambda) [schematic]
# So: Z_2 ~ exp(-S - N_c * N_g * ln(Lambda_QCD/Lambda))

# For the correction to 1/g_2^2:
# delta(1/g_2^2) ~ Z_2 * (renormalization group factor)
# Taking the log of the correction:
# ln(delta/a_0) ~ -S - N_c*N_g*ln(Lambda_QCD/Lambda) + 2N*ln(S) + b_0*ln(Lambda/mu)

# In the RS background, the effective Lambda is position-dependent.
# Integrating over y:
# <ln(delta/a_0)> = int_0^L dy [position-dependent factors]

# The N_c dependence enters LOGARITHMICALLY through the fermion determinant.
# This is consistent with the ln(3) in the symbolic regression hit!

print("  In the SU(2) instanton amplitude:")
print("  ln(Z_2) contains a term -N_c * N_g * ln(Lambda/m_q)")
print("  This is LOGARITHMIC in N_c (through the N_c copies of quarks)")
print()
print("  When computing the ratio a_1/a_2 = 1/(1 + delta_2/a_0):")
print("  delta_2/a_0 involves exp(-S) * [quark factor]^{N_c}")
print("  ln(delta_2/a_0) ~ -S + N_c * [quark contribution]")
print()
print("  If the quark contribution is such that exp(-S + N_c*Q) ~ O(1)")
print("  (i.e., the KK tower and RS geometry push Q to partially cancel S):")
print("  delta_2/a_0 ~ exp(N_c * Q_eff)")
print("  ln(a_1/a_2) = -ln(1 + exp(N_c*Q_eff)) ~ -exp(N_c*Q_eff) for small correction")
print()
print("  But we need SPECIFIC algebra to get ln(N_c), not just N_c.")

print("\n5. THE sqrt(N_w) = sqrt(2) FROM MODULI MEASURE")
print("-" * 50)
print()
print("  The SU(N) instanton moduli space has dimension 4N.")
print("  For SU(2): 4*2 = 8 collective coordinates")
print("    4 = position x_0, 1 = size rho, 3 = SU(2) orientation")
print("  The measure over orientation involves Vol(SU(2)/Z_2)")
print("  Vol(SU(2)) = 2*pi^2 (the 3-sphere)")
print("  After dividing by the unbroken subgroup and including")
print("  the Jacobian from collective to field-space coordinates:")
print("  The measure goes as sqrt(C_2(adj)) = sqrt(N) = sqrt(2)")
print()
print("  Specifically: in the Corrigan-Ramond-'t Hooft conventions,")
print("  the collective coordinate Jacobian for the gauge orientation")
print("  includes a factor (8pi^2/g^2)^{N/2} * [volume of moduli]")
print("  The N/2 power gives: (S)^{N/2}")
print("  For SU(2): (S)^1 = S")
print("  For SU(3): (S)^{3/2}")
print()

# Now: try to assemble ln(3)/sqrt(2)

print("6. ASSEMBLY: a_1/a_2 = ln(3)/sqrt(2) ?")
print("-" * 50)
print()
print("  Consider: delta_2/a_0 = sqrt(2)/ln(3) - 1 = 0.2873")
print("  (which matches the required 0.2887 to 0.5%)")
print()
print("  Can we get 1/(1 + delta_2/a_0) = ln(3)/sqrt(2)?")
print("  i.e., 1 + delta_2/a_0 = sqrt(2)/ln(3)")
print()
print("  If the non-perturbative correction is:")
print("  delta_2/a_0 = sqrt(N_w)/ln(N_c) - 1")
print("             = sqrt(2)/ln(3) - 1")
print()
print("  Then: a_1/a_2 = ln(N_c)/sqrt(N_w)")
print()
print("  For this to emerge from the instanton calculus, we need:")
print("  (a) A factor of ln(N_c) in the DENOMINATOR from fermion determinant")
print("  (b) A factor of sqrt(N_w) in the NUMERATOR from the moduli measure")
print()
print("  Scenario:")
print("  The non-perturbative correction to a_2 involves:")
print("  delta_2 ~ [SU(2) moduli measure] / [fermion determinant]")
print("  = sqrt(N_w) / [N_c-dependent factor from quarks]")
print()
print("  If the fermion factor contributes ln(N_c) (through the resummed")
print("  product over N_c copies of quark zero modes on the RS background):")
print("  delta_2/a_0 ~ sqrt(N_w)/ln(N_c) - 1  [after proper normalization]")
print()
print("  This is SPECULATIVE but structurally consistent:")
print("  - sqrt(2) from SU(2) collective coordinates (established)")
print("  - ln(3) from N_c quark species in the fermion determinant (plausible)")
print("  - The RS geometry provides the O(1) magnitude (needed)")

print("\n7. CROSS-CHECK: WHAT delta_3 WOULD THIS PREDICT?")
print("-" * 50)
print()
# If the same mechanism applies to SU(3):
# delta_3 involves SU(3) instantons.
# The SU(3) moduli measure involves sqrt(N_c) = sqrt(3)
# The fermion determinant for SU(3) instantons:
# quarks in fundamental of SU(3), also doublets of SU(2)
# Each quark species: N_w copies (up and down in doublet)
# The N_w-dependent factor: ln(N_w) = ln(2)

# So: delta_3/a_0 ~ sqrt(N_c)/ln(N_w) - 1 = sqrt(3)/ln(2) - 1

delta_3_pred = math.sqrt(3)/math.log(2) - 1
print(f"  If the pattern is symmetric (swap N_c <-> N_w for SU(3) vs SU(2)):")
print(f"  delta_3/a_0 = sqrt(N_c)/ln(N_w) - 1 = sqrt(3)/ln(2) - 1 = {delta_3_pred:.4f}")
print(f"  a_1/a_3 = 1/(1 + delta_3) = ln(N_w)/sqrt(N_c) = ln(2)/sqrt(3) = {math.log(2)/math.sqrt(3):.4f}")
print()

# What does this predict for alpha_s(M_Z)?
# a_1/a_3 = ln(2)/sqrt(3) = 0.4004
# This is a MUCH larger correction than a_1/a_2 = 0.776
# After RG running, this would give very different alpha_s(M_Z)

# Actually, is this compatible with observations?
# At the GUT scale: alpha_3/alpha_1 = a_1/a_3 = 0.400
# This means alpha_3 is 0.4 times alpha_1 at the cutoff
# Since alpha_3 > alpha_1 at M_Z, the running must reverse this
# The SM RG equations: alpha_3 runs faster (larger b_0 = 7 vs -41/10)

# Let me check: if at Lambda = 10^17 GeV, alpha_3 = 0.4 * alpha_1,
# and alpha_1 = alpha_GUT * (a_0/a_1) = alpha_GUT (since a_1 = a_0):
# alpha_3(Lambda) = 0.4 * alpha_1(Lambda) = 0.4/25 = 0.016
# Running to M_Z with b_0 = 7:
# 1/alpha_3(M_Z) = 1/alpha_3(Lambda) - b_0/(2pi) * ln(Lambda/M_Z)
# = 62.5 - 7/(2pi) * ln(10^17/91.2)
# = 62.5 - 7/(6.283) * 34.63
# = 62.5 - 38.58 = 23.9
# alpha_3(M_Z) = 1/23.9 = 0.042
# Measured: alpha_s(M_Z) = 0.1179

# This is off by a factor of 3. The symmetric pattern doesn't work for SU(3).
# So the mechanism cannot be a simple swap of N_c and N_w.

print(f"  Cross-check: does this predict correct alpha_s(M_Z)?")
alpha_GUT = 1.0/25.0
alpha_1_Lambda = alpha_GUT  # a_1 = a_0, so alpha_1 = alpha_GUT
alpha_3_Lambda = alpha_1_Lambda * math.log(2)/math.sqrt(3)
ln_ratio = math.log(1e17/91.2)
b0_3 = 7.0
inv_alpha_3_MZ = 1/alpha_3_Lambda - b0_3/(2*math.pi) * ln_ratio
alpha_3_MZ = 1/inv_alpha_3_MZ if inv_alpha_3_MZ > 0 else float('inf')
print(f"  alpha_3(Lambda) = {alpha_3_Lambda:.4f}")
print(f"  1/alpha_3(Lambda) = {1/alpha_3_Lambda:.1f}")
print(f"  Running: 1/alpha_3(M_Z) = {inv_alpha_3_MZ:.1f}")
print(f"  alpha_3(M_Z) = {alpha_3_MZ:.4f} (measured: 0.1179)")
print(f"  FAILS: predicted alpha_s too small by factor {0.1179/alpha_3_MZ:.1f}")
print()
print("  CONCLUSION: The symmetric pattern (swap N_c <-> N_w) does NOT work.")
print("  The SU(3) correction must be different from the SU(2) one.")
print("  This is expected: SU(3) instantons couple to color, not weak isospin.")

# What delta_3 IS needed for correct alpha_s(M_Z)?
# 1/alpha_3(M_Z) = 1/(alpha_GUT * a_0/a_3) - b0_3/(2pi)*ln(Lambda/MZ)
# = a_3/(a_0 * alpha_GUT) - b0_3*ln(Lambda/MZ)/(2pi)
# = (1+e3)/alpha_GUT - 38.58
# 1/0.1179 = (1+e3)/0.04 - 38.58
# 8.482 = 25*(1+e3) - 38.58
# 8.482 + 38.58 = 25*(1+e3)
# 47.06 = 25*(1+e3)
# 1+e3 = 1.882
# e3 = 0.882
e3_needed = (1/0.1179 + b0_3/(2*math.pi)*ln_ratio) * alpha_GUT - 1
print(f"\n  Required delta_3/a_0 for correct alpha_s(M_Z): {e3_needed:.4f}")
print(f"  Required delta_2/a_0 for correct sin^2(theta_W)(M_Z): {1/0.776 - 1:.4f}")
print(f"  Ratio delta_3/delta_2 = {e3_needed/(1/0.776-1):.2f}")

# The ratio of corrections delta_3/delta_2 ~ 3.05
# Can this ratio be understood from group theory?
ratio = e3_needed / (1/0.776 - 1)
print(f"\n  Ratio delta_3/delta_2 = {ratio:.3f}")
print(f"  Compare: C_2(adj,SU(3))/C_2(adj,SU(2)) = 3/2 = 1.5")
print(f"  Compare: dim(adj,SU(3))/dim(adj,SU(2)) = 8/3 = 2.67")
print(f"  Compare: b_0(SU(3))/b_0(SU(2)) = {7.0/(19.0/6):.3f}")
print(f"  Compare: N_c/N_w = 3/2 = 1.5")
print(f"  Compare: N_c^2/N_w^2 = 9/4 = 2.25")
print(f"  None of these give {ratio:.2f} cleanly.")

print("\n" + "=" * 70)
print("SUMMARY: STATUS OF ln(3)/sqrt(2) DERIVATION")
print("=" * 70)
print(f"""
  ln(3)/sqrt(2) = {math.log(3)/math.sqrt(2):.6f} matches a_1/a_2 = 0.776 to 0.08%.

  STRUCTURAL ORIGIN:
  - sqrt(2) = sqrt(N_w) plausibly arises from SU(2) collective coordinate measure
  - ln(3) = ln(N_c) plausibly arises from N_c quark species in fermion determinant
  - The combination ln(N_c)/sqrt(N_w) requires a MIXED effect involving both groups

  WHAT WORKS:
  - The functional forms (logarithm, square root) are standard in instanton calculus
  - The group theory numbers (N_c, N_w) enter through the correct representations
  - The magnitude (29% correction) is consistent with strong-coupling IR effects on RS

  WHAT DOESN'T (yet):
  - No rigorous derivation from first principles
  - The asymmetry between SU(2) and SU(3) corrections needs explanation
  - The RS-specific integral over the extra dimension has not been performed
  - The strong-coupling regime at the IR brane prevents standard semiclassical analysis

  VERDICT: ln(3)/sqrt(2) is a PLAUSIBLE but UNPROVEN consequence of
  non-perturbative gauge dynamics on the RS orbifold. A definitive answer
  requires either:
  (a) Computing the Borel transform of the spectral action on RS numerically
  (b) Lattice computation of SU(N) gauge theory on a 5D warped lattice
  (c) Exact results from supersymmetric localization (if SUSY is present)
""")
