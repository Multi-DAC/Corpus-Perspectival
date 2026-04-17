"""
Phase 21 Track 21B.8: Symbolic Regression for a₁/a₂ = 0.776

Search for simple algebraic expressions in SM quantum numbers that give
the target ratio 0.776 (or equivalently sin²θ_W(Λ) = 0.436).

Target numbers:
  a₁/a₂ = 0.776  (or inverse: a₂/a₁ = 1.289)
  sin²θ_W(Λ) = 0.436  (vs tree-level 3/8 = 0.375)
  δ = sin²θ_W(Λ) - 3/8 = 0.061
  δ/(3/8) = 0.163  (fractional correction)

From Phase 20 PS verification script (authoritative):
  Required sin²θ_W(Λ) = 0.4362
  Required a₁/a₂ = ... need to verify convention
"""

import itertools
from fractions import Fraction
import math

# SM quantum numbers and group theory constants
SM_NUMBERS = {
    'N_g': 3,           # generations
    'N_c': 3,           # colors
    'N_w': 2,           # SU(2) dimension
    '3/8': Fraction(3, 8),     # tree-level sin²θ_W
    '5/3': Fraction(5, 3),     # GUT Y normalization factor
    'b1': Fraction(41, 6),     # β₁ (one-loop)
    'b2': Fraction(-19, 6),    # β₂ (one-loop)
    'b3': -7,                   # β₃ (one-loop)
    'C2_SU3': Fraction(4, 3),  # Casimir SU(3) fundamental
    'C2_SU2': Fraction(3, 4),  # Casimir SU(2) fundamental
    'T_SU3': Fraction(1, 2),   # Dynkin index SU(3) fundamental
    'T_SU2': Fraction(1, 2),   # Dynkin index SU(2) fundamental
    'dim_SM_irreps': 5,         # SM irreps per generation (Q,u,d,L,e)
    'dim_SM_with_nu': 6,        # including ν_R
}

# Target values
TARGET_RATIO = 0.776      # a₁/a₂ from Phase 20
TARGET_INV = 1.0 / 0.776  # ≈ 1.289
TARGET_SW = 0.4362         # sin²θ_W(Λ) from PS verification
TOLERANCE = 0.003          # 0.3% tolerance

print("=" * 70)
print("SYMBOLIC REGRESSION FOR a₁/a₂ = 0.776")
print("=" * 70)

# =====================================================
# PHASE 1: Simple fractions p/q for small p, q
# =====================================================
print("\n--- Phase 1: Simple fractions ---")
hits_frac = []
for q in range(1, 50):
    for p in range(1, 50):
        val = p / q
        if abs(val - TARGET_RATIO) < TOLERANCE:
            hits_frac.append((p, q, val, abs(val - TARGET_RATIO)))
        if abs(val - TARGET_INV) < TOLERANCE:
            hits_frac.append((p, q, val, abs(val - TARGET_INV)))

# Sort by closeness
hits_frac.sort(key=lambda x: x[3])
print(f"Found {len(hits_frac)} fraction candidates within {TOLERANCE*100}%:")
for p, q, val, err in hits_frac[:15]:
    target = TARGET_RATIO if abs(val - TARGET_RATIO) < 0.01 else TARGET_INV
    tname = "a₁/a₂" if target == TARGET_RATIO else "a₂/a₁"
    print(f"  {p}/{q} = {val:.6f}  (target {tname} = {target:.4f}, err = {err:.6f})")

# =====================================================
# PHASE 2: Expressions involving SM numbers
# =====================================================
print("\n--- Phase 2: SM number expressions ---")

# Build a set of "atoms" from SM numbers
atoms = {
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'N_g': 3, 'N_c': 3, 'pi': math.pi, 'e': math.e,
    'ln2': math.log(2), 'ln3': math.log(3),
    '3/8': 3/8, '5/3': 5/3,
    '41/6': 41/6, '19/6': 19/6,
    'C2_3': 4/3, 'C2_2': 3/4,
    'sqrt2': math.sqrt(2), 'sqrt3': math.sqrt(3),
}

# Check each atom directly
print("\nDirect atoms:")
for name, val in sorted(atoms.items(), key=lambda x: abs(x[1] - TARGET_RATIO)):
    if abs(val - TARGET_RATIO) < 0.1:
        print(f"  {name} = {val:.6f}  (err = {abs(val - TARGET_RATIO):.6f})")

# Check binary operations a ○ b for +, -, *, /
print("\nBinary operations a ○ b:")
hits_binary = []
ops = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b if b != 0 else None,
}

for (n1, v1), (n2, v2) in itertools.product(atoms.items(), atoms.items()):
    if n1 >= n2 and n1 != n2:  # avoid duplicates for commutative ops
        continue
    for opname, opfunc in ops.items():
        try:
            result = opfunc(v1, v2)
            if result is not None and abs(result - TARGET_RATIO) < TOLERANCE:
                expr = f"({n1} {opname} {n2})"
                hits_binary.append((expr, result, abs(result - TARGET_RATIO)))
            # Also try v2 op v1 for non-commutative ops
            if opname in ['-', '/']:
                result2 = opfunc(v2, v1)
                if result2 is not None and abs(result2 - TARGET_RATIO) < TOLERANCE:
                    expr = f"({n2} {opname} {n1})"
                    hits_binary.append((expr, result2, abs(result2 - TARGET_RATIO)))
        except (ZeroDivisionError, OverflowError):
            pass

hits_binary.sort(key=lambda x: x[2])
for expr, val, err in hits_binary[:20]:
    print(f"  {expr} = {val:.6f}  (err = {err:.6f})")

# =====================================================
# PHASE 3: Specific physically motivated expressions
# =====================================================
print("\n--- Phase 3: Physically motivated expressions ---")

# These are expressions that have a physical interpretation
# as corrections to the trace ratio

candidates = {}

# Simple number-theoretic
candidates['7/9'] = 7/9
candidates['14/18'] = 14/18  # same as 7/9
candidates['31/40'] = 31/40
candidates['19/24'] = 19/24  # ≈ 0.792

# Involving SM beta coefficients
# If the correction is a one-loop effect: a₁/a₂ = 1 + (b₁-b₂)/(2π) × correction
b1, b2, b3 = 41/6, -19/6, -7
candidates['1 - (b1-b2)/(4π²)'] = 1 - (b1 - b2)/(4 * math.pi**2)
candidates['1 - (b1+b2)/(4π²)'] = 1 - (b1 + b2)/(4 * math.pi**2)
candidates['b2/b1'] = abs(b2/b1)  # |β₂/β₁|
candidates['-b2/b3'] = -b2/b3
candidates['(b1+b2+b3)/(b1-b3)'] = (b1+b2+b3)/(b1-b3)

# Involving Casimirs
C2_3, C2_2 = 4/3, 3/4
candidates['C2_2/C2_3'] = C2_2/C2_3  # = 9/16
candidates['1 - C2_2/C2_3'] = 1 - C2_2/C2_3
candidates['C2_3/(C2_3 + C2_2)'] = C2_3/(C2_3 + C2_2)
candidates['(C2_3 - C2_2)/(C2_3 + C2_2)'] = (C2_3 - C2_2)/(C2_3 + C2_2)

# Involving dimensions
candidates['(N_c² - N_c)/(N_c² + 1)'] = (9 - 3)/(9 + 1)  # 6/10
candidates['(N_c² - 2)/(N_c²)'] = 7/9  # = 7/9 again
candidates['(2*N_c² + 1)/(3*N_c²)'] = 19/27
candidates['(N_c² + N_c - 2)/(N_c² + N_c)'] = 10/12  # 5/6

# sin²θ_W related
candidates['3/8 + 1/(16π²)'] = 3/8 + 1/(16 * math.pi**2)
candidates['3/8 × (1 + 1/(2π))'] = 3/8 * (1 + 1/(2*math.pi))
candidates['3/8 + C2_3/(8π²)'] = 3/8 + C2_3/(8 * math.pi**2)

# Trace ratio modifications
# Standard traces: Tr(Y²) = 10/3 per gen, Tr(T²) = 2 per gen (with GUT norm)
# sin²θ_W = Tr(Y²)/(Tr(Y²) + Tr(T²)) ... but convention dependent
# If extra matter modifies Tr(Y²) → Tr(Y²) + δ:
# Then a₁/a₂ = (Tr(Y²) + δ)/Tr(T²) / (Tr(Y²)/Tr(T²))
# Simplifying: a₁/a₂ = 1 + δ/Tr(Y²) ... no, this is the ratio of modified to original

# Let's check: what extra contribution δ_Y to the U(1) trace would give 0.776?
# If a₁ = f₂ × (Tr_Y² + δ_Y) and a₂ = f₂ × Tr_T², and the tree-level a₁/a₂ = 1,
# then the modified ratio is (Tr_Y² + δ_Y)/Tr_T² = 0.776 × (Tr_Y²/Tr_T²)
# Since tree-level Tr_Y²/Tr_T² = 1 (by universality):
# (Tr_Y² + δ_Y)/Tr_T² = 0.776
# So δ_Y/Tr_T² = -0.224
# Or δ_Y = -0.224 × Tr_T²

# With Tr_T² = a₂/f₂ and Tr_Y² = a₁/f₂, universality means Tr_Y² = Tr_T²
# So δ_Y = -0.224 × Tr_Y²
# The fractional correction is -22.4% of the U(1) trace

candidates['1 - b1/(6π²)'] = 1 - b1/(6 * math.pi**2)  # one-loop-ish
candidates['1 - 41/(36π²)'] = 1 - 41/(36 * math.pi**2)

# Golden ratio related
phi = (1 + math.sqrt(5))/2
candidates['1/phi'] = 1/phi  # ≈ 0.618
candidates['phi - 1'] = phi - 1  # ≈ 0.618 (same)
candidates['2/phi²'] = 2/phi**2

# Group dimensions
candidates['8/(8+N_c)'] = 8/11  # ≈ 0.727
candidates['(N_c²-1)/(N_c²+N_c-1)'] = 8/11  # same
candidates['(3*8)/(3*8+7)'] = 24/31

# Check all
print(f"\n{'Expression':<40} {'Value':>10} {'Error':>10} {'Close?':>8}")
print("-" * 70)
for name, val in sorted(candidates.items(), key=lambda x: abs(x[1] - TARGET_RATIO)):
    err = abs(val - TARGET_RATIO)
    close = "***" if err < TOLERANCE else ("*" if err < 0.01 else "")
    print(f"  {name:<38} {val:10.6f} {err:10.6f} {close:>8}")

# =====================================================
# PHASE 4: Exhaustive search a/b for SM-motivated a, b
# =====================================================
print("\n--- Phase 4: Exhaustive a/b with SM-motivated integers ---")

# Build set of "interesting" integers from SM
interesting_ints = set()
for n in range(1, 100):
    interesting_ints.add(n)

# SM-specific interesting numbers
sm_specific = {
    3: 'N_c or N_g', 4: '2²', 5: 'quarks per gen',
    6: 'SM_irreps_with_nu', 8: 'gluons', 10: 'SM_real_dof/gen',
    11: 'N_c²+N_w', 12: 'quarks total', 15: 'SM fermions/gen',
    16: '4²', 18: '2×N_c²', 24: '8×N_g', 41: 'b1_num', 19: 'b2_num',
    42: 'b3_denom×b3', 45: '15×N_g', 48: '16×N_g',
    7: 'N_c²-2', 9: 'N_c²', 27: 'N_c³',
}

print(f"\n{'p/q':<10} {'Value':>10} {'Error':>10} {'p meaning':>25} {'q meaning':>25}")
print("-" * 85)

best_hits = []
for p in range(1, 100):
    for q in range(p+1, 100):  # only p < q (ratio < 1)
        val = p / q
        err = abs(val - TARGET_RATIO)
        if err < 0.001:  # very close
            p_mean = sm_specific.get(p, '')
            q_mean = sm_specific.get(q, '')
            best_hits.append((p, q, val, err, p_mean, q_mean))

best_hits.sort(key=lambda x: x[3])
for p, q, val, err, pm, qm in best_hits[:15]:
    print(f"  {p}/{q:<8} {val:10.6f} {err:10.6f} {pm:>25} {qm:>25}")

# =====================================================
# PHASE 5: Check the specific target from PS verification
# =====================================================
print("\n\n" + "=" * 70)
print("CHECKING EXACT TARGET: sin²θ_W(Λ) = 0.4362")
print("=" * 70)

# From the PS verification script:
# Required sin²θ_W(Λ) = 0.4362
# This means: sin²θ_W(Λ)/sin²θ_W(tree) = 0.4362/0.375 = 1.1632
# The RATIO of needed to tree-level

ratio_sw = 0.4362 / 0.375
print(f"\nsin²θ_W(Λ)/sin²θ_W(tree) = {ratio_sw:.6f}")
print(f"1 + δ = {ratio_sw:.6f}, so δ = {ratio_sw - 1:.6f}")

# Is 0.4362 a simple fraction?
print("\nFractions close to 0.4362:")
for q in range(1, 100):
    for p in range(1, q):
        val = p/q
        if abs(val - 0.4362) < 0.001:
            print(f"  {p}/{q} = {val:.6f}  (err = {abs(val - 0.4362):.6f})")

# The correction δ sin²θ_W = 0.0612
delta_sw = 0.4362 - 0.375
print(f"\nδ sin²θ_W = {delta_sw:.4f}")
print(f"δ/(3/8) = {delta_sw/0.375:.4f}")
print(f"Fractions close to δ = {delta_sw:.4f}:")
for q in range(1, 200):
    for p in range(1, q):
        val = p/q
        if abs(val - delta_sw) < 0.001:
            print(f"  {p}/{q} = {val:.6f}  (err = {abs(val - delta_sw):.6f})")

# =====================================================
# PHASE 6: Key physical test — is the correction
# α_s(M_Z)/(2π) or similar one-loop?
# =====================================================
print("\n\n" + "=" * 70)
print("ONE-LOOP SCALE TESTS")
print("=" * 70)

alpha_s_MZ = 0.1179  # α_s(M_Z)
alpha_em_MZ = 1/137.036
alpha_2_MZ = alpha_em_MZ / 0.2312  # sin²θ_W = α_em/α_2

print(f"\nα_s(M_Z) = {alpha_s_MZ}")
print(f"α_s/(2π) = {alpha_s_MZ/(2*math.pi):.6f}")
print(f"α_s/π = {alpha_s_MZ/math.pi:.6f}")
print(f"α_em(M_Z) = {alpha_em_MZ:.6f}")
print(f"α₂(M_Z) ≈ {alpha_2_MZ:.6f}")

# Is the fractional correction (0.163) related to coupling constants?
frac_corr = delta_sw / 0.375
print(f"\nFractional correction = {frac_corr:.4f}")
print(f"  Compare: α_s/π = {alpha_s_MZ/math.pi:.4f}")
print(f"  Compare: 3α_s/(2π) = {3*alpha_s_MZ/(2*math.pi):.4f}")
print(f"  Compare: C₂(SU3)×α_s/π = {(4/3)*alpha_s_MZ/math.pi:.4f}")
print(f"  Compare: N_c×α_s/(2π) = {3*alpha_s_MZ/(2*math.pi):.4f}")
print(f"  Compare: (b₁-b₂)×α_s/(12π²) = {(41/6+19/6)*alpha_s_MZ/(12*math.pi**2):.4f}")

# Actually: a₁/a₂ = 0.776. What is 1 - 0.776 = 0.224?
correction = 1 - 0.776
print(f"\n1 - a₁/a₂ = {correction:.4f}")
print(f"  Compare: 2α_s/π = {2*alpha_s_MZ/math.pi:.4f}")  # ≈ 0.075
print(f"  Compare: (41+19)/(6×4π²) = {60/(6*4*math.pi**2):.4f}")
print(f"  Compare: (b₁-b₂)/(4π²) = {(41/6+19/6)/(4*math.pi**2):.4f}")  # ≈ 0.253

# Check if 0.224 relates to ln(M_cutoff/M_Z)
# If cutoff ~ 10^16.97 GeV and M_Z = 91.2 GeV:
import math
ln_ratio = math.log(10**16.97 / 91.2)
print(f"\nln(Λ/M_Z) = {ln_ratio:.4f}")
print(f"  1/(4π² × ln_ratio) = {1/(4*math.pi**2*ln_ratio):.6f}")
print(f"  (b₁-b₂)/(12π²) × ln_ratio = {(41/6+19/6)/(12*math.pi**2)*ln_ratio:.4f}")

print("\n" + "=" * 70)
print("SEARCH COMPLETE")
print("=" * 70)
