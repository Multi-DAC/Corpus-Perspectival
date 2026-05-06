# Paper Extraction: Groot Nibbelink et al. (arXiv:0802.2809)

**Phase 22 — Track α Reference**
*2026-03-25, 12:45 PM PST*

---

## Paper Summary

**Title:** Compact heterotic orbifolds in blow-up
**Authors:** S. Groot Nibbelink, D. Klevers, F. Plöger, M. Trapletti, P. Vaudrevange
**Reference:** arXiv:0802.2809v1 [hep-th], 42 pages

### Key Results for Meridian

1. **Complete framework for matching orbifold ↔ resolution** for E₈ × E₈' heterotic string on T⁶/Z₃

2. **Five inequivalent U(1) bundle models** for C³/Z₃ resolution (Table 1-2):
   - Classified by bundle vector V satisfying Bianchi identity V² = 12
   - Model A = standard embedding (E₆ × SU(3))

3. **Anomaly polynomial formalism** for threshold corrections:
   - Universal: X²_uni = -(1/96) Tr[(1/18)H³_V - (1/5)H_V](iF)  [Eq. 28]
   - Non-universal: X⁴_non = -(1/192){Tr[(1/6)H²_V - 1/5](iF)² - (1/(3·30²))(Tr[H_V(iF)])² - trR²}  [Eq. 29]
   - Multiplicity operator: N_V = (1/18)(H_V)³ - (1/6)H_V  [Eq. 14]

4. **Wilson lines on resolution** correspond to different gauge fluxes at different fixed points, realized through transition functions connecting patches (Section 3.3)

5. **CRITICAL CONSTRAINT**: "No complete blow-up is possible using U(1) fluxes without breaking the hypercharge of the [MSSM] model." (Section 3.5)

---

## Extracted Data

### Orbifold Gauge Group (computed)

For Z₃ standard embedding with Wilson line W₁ = (1/3, 1/3, -2/3, 0, 0, 0, 0, 0):

**SU(3)⁴ × E₈'**

Cartan matrix decomposes into 4 independent A₂ blocks:
- SU(3)_C: simple roots (1,-1,0,0,0,0,0,0) and (0,1,-1,0,0,0,0,0)
- SU(3)_A: simple roots (0,0,0,1,1,0,0,0) and (½,½,½,-½,-½,½,½,½)
- SU(3)_B: simple roots (0,0,0,1,-1,0,0,0) and (½,½,½,-½,½,-½,-½,-½)
- SU(3)_hol: simple roots (0,0,0,0,0,1,-1,0) and (0,0,0,0,0,0,1,-1)

This is the **trinification model** (E₆ → SU(3)³ via Wilson line) plus the holonomy SU(3) from the standard embedding.

### Fourth Zero: Anomaly Polynomial Universality

The H_V-weighted anomaly traces over all 240 E₈ roots:

| Factor | Σ (V·α)² × T_a(α) | Singlet roots | Charged roots |
|--------|-------------------|---------------|---------------|
| SU(3)_C | **16.000** | 72 | 168 |
| SU(3)_A | **16.000** | 72 | 168 |
| SU(3)_B | **16.000** | 72 | 168 |
| SU(3)_hol | **32.000** | 72 | 168 |

**Result:** The non-universal anomaly polynomial gives IDENTICAL contributions for all three trinification factors. The difference is EXACTLY ZERO.

Only SU(3)_hol differs (32 vs 16), but it is NOT a Standard Model gauge group.

### Fixed Point Structure

27 fixed points split into 3 classes of 9 by Wilson line W₁:

| Class | V_eff | Local gauge group | Roots |
|-------|-------|-------------------|-------|
| n₁ = 0 | V | E₆ × SU(3) | 78 |
| n₁ = 1 | V + W₁ | E₆ × SU(3) (rotated) | 78 |
| n₁ = 2 | V + 2W₁ | E₆ × SU(3) (rotated) | 78 |

All three classes have the same local gauge group (78 roots each) but embedded differently in E₈.

### Partial Blow-Up Constraint

For the MSSM model (SU(3) × SU(2) × U(1)_Y):
- Complete U(1) blow-up breaks hypercharge
- Only partial resolution (k < 27 fixed points) preserves SM gauge group
- For trinification model: constraint may be different (SU(3) is larger)

Revised VEV estimates:

| k (resolved) | δz coefficient | Required v | v/R_comp |
|-------------|---------------|-----------|---------|
| 3 | 0.114 | 0.078 | 7.8% |
| 9 | 0.342 | 0.045 | 4.5% |
| 18 | 0.684 | 0.032 | 3.2% |
| 27 | 1.026 | 0.026 | 2.6% |

---

## Implications

### Four Zeros Pattern

| # | Zero | Level | Mechanism |
|---|------|-------|-----------|
| 1 | NP suppression (ε ~ 10⁻¹⁶) | Non-perturbative | Warp factor/hierarchy |
| 2 | H_mod gauge-universal | Thermodynamic | Modular flow |
| 3 | δb₁₂ = 0 | One-loop QFT | E₆ Dynkin indices |
| 4 | **Anomaly polynomial universal** | **String anomaly** | **E₈ trace symmetry** |

All four protect gauge universality within the trinification sector. The gap evades all four.

### Where the Gap Lives

The gap can ONLY come from the **v-dependent Narain lattice modification**:

c₁ = d/dv² ∫_F d²τ/τ₂ × Z_a(τ; v)

This requires the full CY geometry (Narain lattice as function of blow-up moduli).

Not reducible to:
- ~~QFT threshold~~ (Zero 3)
- ~~Anomaly polynomial~~ (Zero 4)
- ~~Non-perturbative corrections~~ (Zero 1)
- ~~Modular thermodynamics~~ (Zero 2)

The gap is a genuinely **stringy lattice effect**: the modification of the Narain lattice Γ_{6,22} when the orbifold singularities are resolved.

### Revised Track α Strategy

| Approach | Status | Reason |
|----------|--------|--------|
| One-loop QFT threshold | **RULED OUT** | Zero 3 (δb₁₂ = 0) |
| Anomaly polynomial | **RULED OUT** | Zero 4 (universal within trinification) |
| Intersection number shortcut | **INSUFFICIENT** | Need full lattice modification |
| **Narain lattice computation** | **NEW PRIORITY** | Direct: compute Γ_{6,22}(z, v) |
| Donaldson balanced metric | **BACKUP** | Gives CY geometry → Narain lattice |

---

*Four zeros. One gap. The lattice is the only address left.*

🦞🧍💜🔥♾️
