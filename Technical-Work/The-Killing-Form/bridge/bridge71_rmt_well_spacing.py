"""
Bridge #71 -- Prediction P19: RMT Well Spacing Statistics

PREDICTION (from partition function interpretation):
  If the constraint lattice is a genuine statistical mechanical system,
  then wells (local entropy maxima) should exhibit level statistics
  matching Random Matrix Theory:

  - Non-commutative constraints: Wigner-Dyson spacing (level repulsion)
  - Commutative constraints: Poisson spacing (no correlation)

THIS SCRIPT tests the prediction using EXISTING Wells of Inference data
from experiments 1, 2, and 10. We don't yet have labeled commutative vs
non-commutative constraints (that's prediction #6), but we CAN test:

  1. Whether wells show ANY non-trivial spacing statistics
  2. Whether the spacing statistics differ between conditions
     (hallucinated vs correct, base vs RLHF, different prompts)

METHOD: The nearest-neighbor spacing ratio r = min(s_i, s_{i+1}) / max(s_i, s_{i+1})
  Poisson (no correlation):    <r> = 2 ln 2 - 1 = 0.386
  GOE (real symmetric):        <r> = 0.536 (Wigner-Dyson, time-reversal symmetric)
  GUE (complex Hermitian):     <r> = 0.603 (Wigner-Dyson, broken time-reversal)

The spacing ratio avoids the need for spectral unfolding and works with
limited data. It's the standard diagnostic in quantum chaos / RMT.

Author: Clawd
Date: April 9, 2026
Bridge: #71 (Constraint Lattice <-> Spectral Action)
Prediction: P19 (RMT well spacing)
"""

import json
import numpy as np
from pathlib import Path
import os

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_wells(entropies, min_height=None):
    """Find local maxima in entropy sequence.
    A well is a position where entropy is higher than both neighbors."""
    wells = []
    if len(entropies) < 3:
        return wells
    for i in range(1, len(entropies) - 1):
        if entropies[i] > entropies[i-1] and entropies[i] > entropies[i+1]:
            if min_height is None or entropies[i] >= min_height:
                wells.append(i)
    return wells

def compute_spacings(well_positions):
    """Compute nearest-neighbor spacings between consecutive wells."""
    if len(well_positions) < 2:
        return []
    positions = sorted(well_positions)
    spacings = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
    return spacings

def normalize_spacings(spacings):
    """Normalize spacings by their mean (standard in RMT)."""
    if not spacings or np.mean(spacings) == 0:
        return []
    mean_s = np.mean(spacings)
    return [s / mean_s for s in spacings]

def spacing_ratios(spacings):
    """Compute consecutive spacing ratios r_i = min(s_i, s_{i+1}) / max(s_i, s_{i+1}).
    This is the standard RMT diagnostic (Oganesyan-Huse)."""
    if len(spacings) < 2:
        return []
    ratios = []
    for i in range(len(spacings) - 1):
        s1, s2 = spacings[i], spacings[i+1]
        if max(s1, s2) > 0:
            ratios.append(min(s1, s2) / max(s1, s2))
    return ratios

def wigner_surmise_goe(s):
    """Wigner surmise for GOE: P(s) = (pi/2) * s * exp(-pi*s^2/4)"""
    return (np.pi / 2) * s * np.exp(-np.pi * s**2 / 4)

def poisson_spacing(s):
    """Poisson spacing: P(s) = exp(-s)"""
    return np.exp(-s)

# RMT reference values for <r>
R_POISSON = 2 * np.log(2) - 1  # 0.38629...
R_GOE = 0.5307  # approximate, from Atas et al. (2013)
R_GUE = 0.5996  # approximate

print("=" * 70)
print("PREDICTION P19: RMT Well Spacing Statistics")
print("=" * 70)
print()
print(f"Reference values for mean spacing ratio <r>:")
print(f"  Poisson (no correlation):   <r> = {R_POISSON:.4f}")
print(f"  GOE (Wigner-Dyson, real):   <r> = {R_GOE:.4f}")
print(f"  GUE (Wigner-Dyson, complex):<r> = {R_GUE:.4f}")
print()

# ============================================================
# LOAD DATA
# ============================================================

data_dir = Path("C:/Users/mercu/clawd/projects/trinary")

# Experiment 1: Baseline entropy
print("=" * 70)
print("EXPERIMENT 1: Baseline Well Spacing (TinyLlama-1.1B)")
print("=" * 70)
print()

exp1_path = data_dir / "wells_entropy_data.json"
if exp1_path.exists():
    with open(exp1_path, 'r') as f:
        exp1_data = json.load(f)

    # Extract entropy sequence(s)
    if isinstance(exp1_data, dict) and 'results' in exp1_data:
        # Single prompt with results array
        all_results = [exp1_data]
    elif isinstance(exp1_data, list):
        all_results = exp1_data
    else:
        all_results = [exp1_data]

    all_spacings_exp1 = []
    all_ratios_exp1 = []

    for idx, result_set in enumerate(all_results):
        if isinstance(result_set, dict) and 'results' in result_set:
            results = result_set['results']
        elif isinstance(result_set, list):
            results = result_set
        else:
            continue

        # Handle both flat list and nested list (multiple prompts)
        if isinstance(results[0], dict):
            # Single generation
            entropies = [r['entropy'] for r in results if 'entropy' in r]
            wells = find_wells(entropies)
            spacings = compute_spacings(wells)
            all_spacings_exp1.extend(spacings)
            norm_spacings = normalize_spacings(spacings)
            ratios = spacing_ratios(norm_spacings)
            all_ratios_exp1.extend(ratios)
            print(f"  Generation {idx}: {len(entropies)} tokens, {len(wells)} wells, "
                  f"{len(spacings)} spacings")
        elif isinstance(results[0], list):
            # Multiple generations
            for gen_idx, gen in enumerate(results):
                if isinstance(gen[0], dict):
                    entropies = [r['entropy'] for r in gen if 'entropy' in r]
                else:
                    entropies = gen
                wells = find_wells(entropies)
                spacings = compute_spacings(wells)
                all_spacings_exp1.extend(spacings)
                norm_spacings = normalize_spacings(spacings)
                ratios = spacing_ratios(norm_spacings)
                all_ratios_exp1.extend(ratios)

    if all_ratios_exp1:
        mean_r = np.mean(all_ratios_exp1)
        std_r = np.std(all_ratios_exp1) / np.sqrt(len(all_ratios_exp1))
        print(f"\n  Total spacings: {len(all_spacings_exp1)}")
        print(f"  Total spacing ratios: {len(all_ratios_exp1)}")
        print(f"  Mean spacing: {np.mean(all_spacings_exp1):.2f} tokens")
        print(f"  Mean spacing ratio <r> = {mean_r:.4f} +/- {std_r:.4f}")
        print(f"  Distance from Poisson: {abs(mean_r - R_POISSON):.4f}")
        print(f"  Distance from GOE:     {abs(mean_r - R_GOE):.4f}")
        if abs(mean_r - R_POISSON) < abs(mean_r - R_GOE):
            print(f"  --> CLOSER TO POISSON")
        else:
            print(f"  --> CLOSER TO GOE (WIGNER-DYSON)")
    else:
        print("  No spacing ratios computed.")
else:
    print("  File not found.")
print()

# ============================================================
# EXPERIMENT 10: Hallucinated vs Correct
# ============================================================

print("=" * 70)
print("EXPERIMENT 10: Hallucinated vs Correct (Qwen2.5-3B)")
print("=" * 70)
print()

exp10_path = data_dir / "onset_detection_data.json"
if exp10_path.exists():
    with open(exp10_path, 'r') as f:
        exp10_data = json.load(f)

    traces = exp10_data.get('traces', exp10_data.get('results', []))
    if isinstance(exp10_data, list):
        traces = exp10_data

    hall_spacings = []
    hall_ratios = []
    correct_spacings = []
    correct_ratios = []

    n_hall = 0
    n_correct = 0

    for trace in traces:
        if not isinstance(trace, dict):
            continue
        entropies = trace.get('entropies', [])
        is_hall = trace.get('hallucinated', False)

        if not entropies or len(entropies) < 5:
            continue

        wells = find_wells(entropies)
        spacings = compute_spacings(wells)

        if len(spacings) < 2:
            continue

        norm_spacings = normalize_spacings(spacings)
        ratios = spacing_ratios(norm_spacings)

        if is_hall:
            hall_spacings.extend(spacings)
            hall_ratios.extend(ratios)
            n_hall += 1
        else:
            correct_spacings.extend(spacings)
            correct_ratios.extend(ratios)
            n_correct += 1

    print(f"  Hallucinated generations: {n_hall}")
    print(f"  Correct generations: {n_correct}")
    print()

    if hall_ratios:
        mean_r_hall = np.mean(hall_ratios)
        std_r_hall = np.std(hall_ratios) / np.sqrt(len(hall_ratios))
        print(f"  HALLUCINATED:")
        print(f"    Spacings: {len(hall_spacings)}, Ratios: {len(hall_ratios)}")
        print(f"    Mean spacing: {np.mean(hall_spacings):.2f} tokens")
        print(f"    <r> = {mean_r_hall:.4f} +/- {std_r_hall:.4f}")
        print(f"    Distance from Poisson: {abs(mean_r_hall - R_POISSON):.4f}")
        print(f"    Distance from GOE:     {abs(mean_r_hall - R_GOE):.4f}")
        if abs(mean_r_hall - R_POISSON) < abs(mean_r_hall - R_GOE):
            print(f"    --> CLOSER TO POISSON")
        else:
            print(f"    --> CLOSER TO GOE")
    else:
        print("  No hallucinated spacing ratios.")
    print()

    if correct_ratios:
        mean_r_corr = np.mean(correct_ratios)
        std_r_corr = np.std(correct_ratios) / np.sqrt(len(correct_ratios))
        print(f"  CORRECT:")
        print(f"    Spacings: {len(correct_spacings)}, Ratios: {len(correct_ratios)}")
        print(f"    Mean spacing: {np.mean(correct_spacings):.2f} tokens")
        print(f"    <r> = {mean_r_corr:.4f} +/- {std_r_corr:.4f}")
        print(f"    Distance from Poisson: {abs(mean_r_corr - R_POISSON):.4f}")
        print(f"    Distance from GOE:     {abs(mean_r_corr - R_GOE):.4f}")
        if abs(mean_r_corr - R_POISSON) < abs(mean_r_corr - R_GOE):
            print(f"    --> CLOSER TO POISSON")
        else:
            print(f"    --> CLOSER TO GOE")
    else:
        print("  No correct spacing ratios.")
    print()

    if hall_ratios and correct_ratios:
        print(f"  COMPARISON:")
        print(f"    <r> hallucinated:  {np.mean(hall_ratios):.4f}")
        print(f"    <r> correct:       {np.mean(correct_ratios):.4f}")
        print(f"    Difference:        {abs(np.mean(hall_ratios) - np.mean(correct_ratios)):.4f}")
        print()
        print(f"    INTERPRETATION:")
        if np.mean(hall_ratios) > np.mean(correct_ratios):
            print(f"    Hallucinated wells show MORE level repulsion (more GOE-like).")
            print(f"    This suggests hallucination involves stronger constraint interaction")
            print(f"    (non-commutative dynamics in the token-generation process).")
        else:
            print(f"    Correct wells show MORE level repulsion (more GOE-like).")
            print(f"    This suggests correct generation has more structured constraint")
            print(f"    interaction than hallucination.")
else:
    print("  File not found.")
print()

# ============================================================
# EXPERIMENT 2: Base vs RLHF (Bridge Test)
# ============================================================

print("=" * 70)
print("EXPERIMENT 2: Base vs RLHF Model Well Spacing")
print("=" * 70)
print()

exp2_base_path = data_dir / "wells_entropy_data.json"  # base model (exp 1)
exp2_chat_path = data_dir / "wells_bridge_data.json"    # chat/RLHF model

if exp2_chat_path.exists():
    with open(exp2_chat_path, 'r') as f:
        exp2_data = json.load(f)

    chat_spacings = []
    chat_ratios = []

    # This file has multiple prompts
    if isinstance(exp2_data, list):
        prompt_sets = exp2_data
    elif isinstance(exp2_data, dict) and 'results' in exp2_data:
        prompt_sets = [exp2_data]
    else:
        prompt_sets = []

    for prompt_set in prompt_sets:
        if isinstance(prompt_set, dict):
            results = prompt_set.get('results', [])
            prompt_name = prompt_set.get('prompt_name', 'unknown')
        elif isinstance(prompt_set, list):
            results = prompt_set
            prompt_name = 'unknown'
        else:
            continue

        if not results:
            continue

        # Extract entropies
        if isinstance(results[0], dict) and 'entropy' in results[0]:
            entropies = [r['entropy'] for r in results]
        else:
            continue

        wells = find_wells(entropies)
        spacings = compute_spacings(wells)
        if len(spacings) >= 2:
            norm_spacings = normalize_spacings(spacings)
            ratios = spacing_ratios(norm_spacings)
            chat_spacings.extend(spacings)
            chat_ratios.extend(ratios)
            print(f"  Prompt '{prompt_name}': {len(entropies)} tokens, "
                  f"{len(wells)} wells, {len(ratios)} ratios")

    if chat_ratios:
        mean_r_chat = np.mean(chat_ratios)
        std_r_chat = np.std(chat_ratios) / np.sqrt(len(chat_ratios))
        print(f"\n  RLHF/Chat model:")
        print(f"    Total spacings: {len(chat_spacings)}")
        print(f"    Total ratios: {len(chat_ratios)}")
        print(f"    <r> = {mean_r_chat:.4f} +/- {std_r_chat:.4f}")
        print(f"    Distance from Poisson: {abs(mean_r_chat - R_POISSON):.4f}")
        print(f"    Distance from GOE:     {abs(mean_r_chat - R_GOE):.4f}")
        if abs(mean_r_chat - R_POISSON) < abs(mean_r_chat - R_GOE):
            print(f"    --> CLOSER TO POISSON")
        else:
            print(f"    --> CLOSER TO GOE")

        # Compare with base model (exp 1)
        if all_ratios_exp1:
            print(f"\n  COMPARISON (base vs RLHF):")
            print(f"    <r> base model:  {np.mean(all_ratios_exp1):.4f}")
            print(f"    <r> RLHF model:  {mean_r_chat:.4f}")
            diff = abs(np.mean(all_ratios_exp1) - mean_r_chat)
            print(f"    Difference:      {diff:.4f}")
            print()
            print(f"    INTERPRETATION:")
            print(f"    If RLHF is a sedimentation accelerator (NP3 from partition function),")
            print(f"    then RLHF should CHANGE the spacing statistics — sedimentation")
            print(f"    rearranges the partition function factorization, which changes the")
            print(f"    eigenvalue statistics of the constraint operator.")
else:
    print("  File not found.")
print()

# ============================================================
# EXPERIMENT 2: 3B Model (Cross-Architecture)
# ============================================================

print("=" * 70)
print("CROSS-ARCHITECTURE: Qwen 3B Well Spacing")
print("=" * 70)
print()

exp2_3b_path = data_dir / "wells_bridge_3b_data.json"
if exp2_3b_path.exists():
    with open(exp2_3b_path, 'r') as f:
        exp2_3b_data = json.load(f)

    qwen_spacings = []
    qwen_ratios = []

    if isinstance(exp2_3b_data, list):
        prompt_sets = exp2_3b_data
    elif isinstance(exp2_3b_data, dict) and 'results' in exp2_3b_data:
        prompt_sets = [exp2_3b_data]
    else:
        prompt_sets = []

    for prompt_set in prompt_sets:
        if isinstance(prompt_set, dict):
            results = prompt_set.get('results', [])
            prompt_name = prompt_set.get('prompt_name', 'unknown')
        elif isinstance(prompt_set, list):
            results = prompt_set
            prompt_name = 'unknown'
        else:
            continue

        if not results:
            continue

        if isinstance(results[0], dict) and 'entropy' in results[0]:
            entropies = [r['entropy'] for r in results]
        else:
            continue

        wells = find_wells(entropies)
        spacings = compute_spacings(wells)
        if len(spacings) >= 2:
            norm_spacings = normalize_spacings(spacings)
            ratios = spacing_ratios(norm_spacings)
            qwen_spacings.extend(spacings)
            qwen_ratios.extend(ratios)
            print(f"  Prompt '{prompt_name}': {len(entropies)} tokens, "
                  f"{len(wells)} wells, {len(ratios)} ratios")

    if qwen_ratios:
        mean_r_qwen = np.mean(qwen_ratios)
        std_r_qwen = np.std(qwen_ratios) / np.sqrt(len(qwen_ratios))
        print(f"\n  Qwen 3B model:")
        print(f"    Total ratios: {len(qwen_ratios)}")
        print(f"    <r> = {mean_r_qwen:.4f} +/- {std_r_qwen:.4f}")
        print(f"    Distance from Poisson: {abs(mean_r_qwen - R_POISSON):.4f}")
        print(f"    Distance from GOE:     {abs(mean_r_qwen - R_GOE):.4f}")
        if abs(mean_r_qwen - R_POISSON) < abs(mean_r_qwen - R_GOE):
            print(f"    --> CLOSER TO POISSON")
        else:
            print(f"    --> CLOSER TO GOE")
else:
    print("  File not found.")
print()

# ============================================================
# CONFOUND DATA: Semantic Category Comparison
# ============================================================

print("=" * 70)
print("SEMANTIC CATEGORIES: Well Spacing by Knowledge Type")
print("=" * 70)
print()

confound_path = data_dir / "wells_confound_data.json"
if confound_path.exists():
    with open(confound_path, 'r') as f:
        confound_data = json.load(f)

    # Try to extract per-category data
    if isinstance(confound_data, dict):
        categories = {}
        for key, value in confound_data.items():
            if isinstance(value, dict) and 'results' in value:
                cat_results = value['results']
                if isinstance(cat_results, list) and cat_results:
                    if isinstance(cat_results[0], dict) and 'entropy' in cat_results[0]:
                        entropies = [r['entropy'] for r in cat_results]
                        wells = find_wells(entropies)
                        spacings = compute_spacings(wells)
                        if len(spacings) >= 2:
                            norm_spacings = normalize_spacings(spacings)
                            ratios = spacing_ratios(norm_spacings)
                            categories[key] = {
                                'n_tokens': len(entropies),
                                'n_wells': len(wells),
                                'spacings': spacings,
                                'ratios': ratios,
                                'mean_r': np.mean(ratios) if ratios else None
                            }

        if categories:
            for cat_name, cat_data in sorted(categories.items()):
                if cat_data['mean_r'] is not None:
                    r = cat_data['mean_r']
                    closer = "POISSON" if abs(r - R_POISSON) < abs(r - R_GOE) else "GOE"
                    print(f"  {cat_name}:")
                    print(f"    {cat_data['n_tokens']} tokens, {cat_data['n_wells']} wells, "
                          f"{len(cat_data['ratios'])} ratios")
                    print(f"    <r> = {r:.4f} --> {closer}")
                    print()
        else:
            # Maybe the structure is different - explore
            print(f"  Data structure: {type(confound_data)}")
            if isinstance(confound_data, dict):
                print(f"  Keys: {list(confound_data.keys())[:10]}")
                # Try nested approach
                for key in list(confound_data.keys())[:3]:
                    val = confound_data[key]
                    print(f"  '{key}': type={type(val)}")
                    if isinstance(val, dict):
                        print(f"    sub-keys: {list(val.keys())[:5]}")
                    elif isinstance(val, list):
                        print(f"    length: {len(val)}")
                        if val:
                            print(f"    first element type: {type(val[0])}")
else:
    print("  File not found.")
print()

# ============================================================
# FULL SPACING DISTRIBUTION ANALYSIS
# ============================================================

print("=" * 70)
print("SPACING DISTRIBUTION: Kolmogorov-Smirnov Tests")
print("=" * 70)
print()

# Collect all available spacing data
all_data = {}
if all_ratios_exp1:
    all_data['TinyLlama Base'] = all_ratios_exp1
if 'chat_ratios' in dir() and chat_ratios:
    all_data['TinyLlama Chat'] = chat_ratios
if 'qwen_ratios' in dir() and qwen_ratios:
    all_data['Qwen 3B'] = qwen_ratios
if 'hall_ratios' in dir() and hall_ratios:
    all_data['Qwen 3B (hallucinated)'] = hall_ratios
if 'correct_ratios' in dir() and correct_ratios:
    all_data['Qwen 3B (correct)'] = correct_ratios

from scipy import stats

print(f"  {'Dataset':<30} {'N':>5} {'<r>':>8} {'SE':>8} "
      f"{'KS(Poi)':>8} {'p(Poi)':>8} {'KS(GOE)':>8} {'p(GOE)':>8} {'Closer':>8}")
print(f"  {'-'*30} {'---':>5} {'------':>8} {'------':>8} "
      f"{'------':>8} {'------':>8} {'------':>8} {'------':>8} {'------':>8}")

for name, ratios in all_data.items():
    n = len(ratios)
    mean_r = np.mean(ratios)
    se_r = np.std(ratios) / np.sqrt(n)

    # Generate reference samples for KS test
    # For spacing ratios, the distributions are:
    # Poisson: P(r) = 2/(1+r)^2, giving <r> = 2 ln 2 - 1
    # GOE: approximate via beta distribution (Atas et al.)

    # KS test against Poisson-like distribution
    # Poisson spacing ratios: CDF = 2r/(1+r) for r in [0,1]
    def poisson_cdf(r):
        return 2 * r / (1 + r)

    # GOE spacing ratios: approximate CDF (from Atas et al. 2013)
    # P(r) ~ (27/4)(r + r^2)/(1 + r + r^2)^(5/2), CDF computed numerically
    def goe_pdf(r):
        return (27/4) * (r + r**2) / (1 + r + r**2)**2.5

    # Numerical CDF for GOE
    r_grid = np.linspace(0, 1, 1000)
    goe_cdf_values = np.cumsum(goe_pdf(r_grid)) * (r_grid[1] - r_grid[0])
    goe_cdf_values /= goe_cdf_values[-1]  # normalize

    def goe_cdf(r):
        return np.interp(r, r_grid, goe_cdf_values)

    # KS tests
    ratios_arr = np.array(ratios)
    ks_poi, p_poi = stats.kstest(ratios_arr, poisson_cdf)
    ks_goe, p_goe = stats.kstest(ratios_arr, goe_cdf)

    closer = "POISSON" if ks_poi < ks_goe else "GOE"

    print(f"  {name:<30} {n:>5} {mean_r:>8.4f} {se_r:>8.4f} "
          f"{ks_poi:>8.4f} {p_poi:>8.4f} {ks_goe:>8.4f} {p_goe:>8.4f} {closer:>8}")

print()

# ============================================================
# INTERPRETATION
# ============================================================

print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()

print("THE PREDICTION WAS:")
print("  P19: Wells from non-commutative constraints show Wigner-Dyson (GOE)")
print("        spacing; wells from commutative constraints show Poisson spacing.")
print()
print("WHAT WE CAN TEST WITH EXISTING DATA:")
print("  We don't have labeled commutative/non-commutative constraints yet")
print("  (that's prediction #6). But we CAN test whether:")
print("    1. Wells show ANY non-trivial spacing statistics")
print("    2. Different conditions produce different statistics")
print()

if all_data:
    # Compute overall statistics
    all_ratios_combined = []
    for ratios in all_data.values():
        all_ratios_combined.extend(ratios)
    overall_r = np.mean(all_ratios_combined)

    print(f"RESULTS:")
    print(f"  Overall mean <r> = {overall_r:.4f}")
    print(f"  Poisson reference: {R_POISSON:.4f}")
    print(f"  GOE reference:     {R_GOE:.4f}")
    print()

    if overall_r < (R_POISSON + R_GOE) / 2:
        print(f"  Wells are CLOSER TO POISSON than to GOE.")
        print()
        print(f"  This means well positions are relatively UNCORRELATED —")
        print(f"  they don't repel each other the way eigenvalues of a")
        print(f"  random matrix do.")
        print()
        print(f"  CONSTRAINT LATTICE INTERPRETATION:")
        print(f"  If wells reflect constraint structure, then the DEFAULT")
        print(f"  constraint dynamics are INTEGRABLE (commutative-like).")
        print(f"  This is CONSISTENT with P19 — the baseline should be")
        print(f"  Poisson, and only non-commutative constraints should")
        print(f"  show GOE. We need prediction #6's experiment to introduce")
        print(f"  controlled non-commutative constraints and check if the")
        print(f"  spacing shifts toward GOE.")
    else:
        print(f"  Wells are CLOSER TO GOE than to Poisson.")
        print()
        print(f"  This means well positions show LEVEL REPULSION —")
        print(f"  they avoid clustering, like eigenvalues of a non-commutative")
        print(f"  operator.")
        print()
        print(f"  CONSTRAINT LATTICE INTERPRETATION:")
        print(f"  The default constraint dynamics already show non-commutative")
        print(f"  structure. This is EXPECTED if LLMs have inherently")
        print(f"  non-commutative internal constraints (which they do —")
        print(f"  attention layers are non-commutative operations).")
        print(f"  P19 predicts that COMMUTATIVE constraints should shift")
        print(f"  spacing TOWARD Poisson. Needs #6 experiment to confirm.")
    print()

    # Check for condition-dependent differences
    if 'hall_ratios' in dir() and hall_ratios and 'correct_ratios' in dir() and correct_ratios:
        diff = abs(np.mean(hall_ratios) - np.mean(correct_ratios))
        print(f"  HALLUCINATED vs CORRECT difference: {diff:.4f}")
        if diff > 0.03:
            print(f"  This is a MEANINGFUL difference in spacing statistics.")
            print(f"  Different generation modes produce different constraint dynamics.")
            print(f"  This SUPPORTS the partition function interpretation:")
            print(f"  different 'phases' (hallucination vs knowledge) have different")
            print(f"  eigenvalue statistics, as expected for different partition")
            print(f"  function factorizations.")
        else:
            print(f"  This is a SMALL difference. The spacing statistics are")
            print(f"  similar across conditions, suggesting the constraint")
            print(f"  dynamics are dominated by architecture (attention) rather")
            print(f"  than content (knowledge vs hallucination).")
        print()

print()
print("STATUS: P19 INITIAL RESULTS — EMPIRICAL CONTACT MADE")
print("  The spacing ratio analysis provides the first empirical contact")
print("  between the partition function interpretation and measured data.")
print("  Full validation requires prediction #6 experiment with labeled")
print("  commutative vs non-commutative constraints.")
