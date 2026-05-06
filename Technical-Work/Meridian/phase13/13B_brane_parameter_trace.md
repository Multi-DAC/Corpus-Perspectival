# Track 13B: Brane Parameter Trace — COMPLETE

**Date:** March 17, 2026
**Status:** ROOT CAUSE IDENTIFIED
**Severity:** CRITICAL — Φ₀ was reverse-engineered, not derived

---

## The Finding

**Φ₀ = 0.477493 was never derived from the junction conditions. It was reverse-engineered from ζ₀ = 0.038.**

### The Smoking Gun

`phase11d/d1_self_tuning_demonstration.py`, line 417:
```python
Phi_0 = np.sqrt(zeta_0 * M5_cubed / xi)
# = sqrt(0.038 * 1.0 / (1/6)) = sqrt(0.228) = 0.477493
```

The junction conditions (Eqs. 1.54a-b) were **never numerically solved** prior to the peer review analysis. The brane parameters (σ_UV=6, α_UV=0.01, μ²=0.1) were stated as "benchmarks" but never verified to produce this Φ₀.

### The Provenance Chain

1. **Phase 5, task 5.7:** Combined fit yields ζ₀ = 0.045 (phenomenological fit parameter)
2. **Phase 5, task 5.9:** Consistency check: φ₀ = 0.52 M_Pl from ζ₀ = 0.045. Explicitly labeled "NOT a derivation"
3. **Phase 6, task 6.2:** KK reduction derives ζ₀ = ξ c_φ². Notes c_φ is a FREE parameter (UV boundary condition)
4. **Phase 7–8:** Value shifts from ζ₀ = 0.045 to ζ₀ = 0.038 (from H&K measurement β_HK = -0.037)
5. **Phase 11d, D1:** Phi_0 computed from ζ₀ = 0.038 via sqrt(ζ₀/ξ). Self-tuning scan used this assumed Φ₀ for all Λ₅ values — constant by construction, not by physics
6. **Phase 11d, D1:** Background profile Φ(y) = Φ₀ exp(-ζ₀ky/2) constructed from assumed Φ₀. Copied into monograph appendix.

### The Circularity

```
H&K data: β_HK = -0.037  →  ζ₀ = 0.038
     ↓
ζ₀ = ξ Φ₀² / M₅³  →  Φ₀ = sqrt(0.228) = 0.477
     ↓
Brane parameters stated as "benchmarks" (never verified)
     ↓
Junction conditions with those benchmarks actually give Φ₀ = 0.076
     ↓
INCONSISTENCY: stated parameters and stated Φ₀ are incompatible
```

### What the Junction Conditions Actually Give

With (σ_UV=6, α_UV=0.01, ξ=1/6, μ²=0.1, M₅³=1):
- **Φ₀ = 0.0761** (only root, verified to machine precision)
- **ζ₀ = 0.000964**
- **w₀ = -0.746** (via CKK formula)

Claimed Φ₀ = 0.477 gives JC2 residual = **-1.105** (should be 0).

### The System Is Underdetermined

The JC system has 1 effective equation and 3 free parameters (after fixing ξ=1/6 and M₅³=1). Parameters that DO produce Φ₀ = 0.477 exist:
- σ_UV=6, α_UV=0.01, **μ² = 0.653** (vs stated 0.1)
- σ_UV=1, α_UV=0.01, **μ² = 0.101**
- Many other combinations

So ζ₀ = 0.038 is ACHIEVABLE with different brane parameters. The question is which parameters are physical.

---

*Track 13B complete. The computation chain is fully traced. Φ₀ was imposed, not derived.*
