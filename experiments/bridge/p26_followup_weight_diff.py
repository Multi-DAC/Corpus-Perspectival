"""
P26 Follow-up: WHERE Does RLHF Operate?
========================================

P26 showed Q-projection Killing form is IDENTICAL between base and instruct.
This script maps the Frobenius norm of weight differences across ALL parameter
types to find where RLHF actually modifies the model.

If RLHF is sedimentation, it must sediment SOMEWHERE. This finds where.

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
import json, time, sys

def compare_models(base_name, instruct_name):
    """Compare Frobenius norm of weight differences across all parameter types."""
    from transformers import AutoModelForCausalLM
    import torch

    print(f"Loading {base_name}...")
    base = AutoModelForCausalLM.from_pretrained(base_name, dtype=torch.float32)
    print(f"Loading {instruct_name}...")
    inst = AutoModelForCausalLM.from_pretrained(instruct_name, dtype=torch.float32)

    base_params = dict(base.named_parameters())
    inst_params = dict(inst.named_parameters())

    results = {}
    categories = {}  # category -> list of (layer, param_name, fro_diff, fro_base, relative_diff)

    for name in sorted(base_params.keys()):
        if name not in inst_params:
            print(f"  MISSING in instruct: {name}")
            continue

        b = base_params[name].detach().cpu().numpy()
        i = inst_params[name].detach().cpu().numpy()
        diff = i - b

        fro_diff = float(np.linalg.norm(diff))
        fro_base = float(np.linalg.norm(b))
        rel_diff = fro_diff / fro_base if fro_base > 0 else 0.0

        # Categorize
        if 'q_proj' in name:
            cat = 'q_proj'
        elif 'k_proj' in name:
            cat = 'k_proj'
        elif 'v_proj' in name:
            cat = 'v_proj'
        elif 'o_proj' in name:
            cat = 'o_proj'
        elif 'gate_proj' in name:
            cat = 'mlp_gate'
        elif 'up_proj' in name:
            cat = 'mlp_up'
        elif 'down_proj' in name:
            cat = 'mlp_down'
        elif 'input_layernorm' in name:
            cat = 'layernorm_attn'
        elif 'post_attention_layernorm' in name:
            cat = 'layernorm_mlp'
        elif 'embed_tokens' in name:
            cat = 'embedding'
        elif 'norm.weight' in name and 'layer' not in name:
            cat = 'final_norm'
        elif 'lm_head' in name:
            cat = 'lm_head'
        else:
            cat = 'other'

        # Extract layer number
        layer = -1
        if 'layers.' in name:
            try:
                layer = int(name.split('layers.')[1].split('.')[0])
            except:
                pass

        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            'layer': layer,
            'name': name,
            'fro_diff': fro_diff,
            'fro_base': fro_base,
            'rel_diff': rel_diff,
            'shape': list(b.shape),
        })

        results[name] = {
            'fro_diff': fro_diff,
            'fro_base': fro_base,
            'rel_diff': rel_diff,
            'category': cat,
            'layer': layer,
        }

    del base, inst
    import gc; gc.collect()

    return results, categories


if __name__ == '__main__':
    base_name = 'Qwen/Qwen2.5-1.5B'
    inst_name = 'Qwen/Qwen2.5-1.5B-Instruct'

    print("P26 Follow-up: WHERE Does RLHF Operate?")
    print("=" * 70)
    print()

    t0 = time.time()
    results, categories = compare_models(base_name, inst_name)
    print(f"\nTotal comparison time: {time.time() - t0:.1f}s")

    # ============================================================
    # SUMMARY BY CATEGORY
    # ============================================================
    print(f"\n{'='*70}")
    print("FROBENIUS NORM OF WEIGHT DIFFERENCES BY CATEGORY")
    print(f"{'='*70}\n")

    print(f"{'Category':<18} {'Count':>5} {'Mean ||diff||':>14} {'Mean ||base||':>14} "
          f"{'Mean rel':>10} {'Max rel':>10}")
    print("-" * 75)

    cat_summary = {}
    for cat in sorted(categories.keys()):
        items = categories[cat]
        n = len(items)
        mean_diff = np.mean([x['fro_diff'] for x in items])
        mean_base = np.mean([x['fro_base'] for x in items])
        mean_rel = np.mean([x['rel_diff'] for x in items])
        max_rel = np.max([x['rel_diff'] for x in items])
        print(f"{cat:<18} {n:>5} {mean_diff:>14.4f} {mean_base:>14.4f} "
              f"{mean_rel:>10.6f} {max_rel:>10.6f}")
        cat_summary[cat] = {
            'count': n,
            'mean_fro_diff': float(mean_diff),
            'mean_fro_base': float(mean_base),
            'mean_relative_diff': float(mean_rel),
            'max_relative_diff': float(max_rel),
        }

    # ============================================================
    # LAYER-BY-LAYER FOR KEY CATEGORIES
    # ============================================================
    print(f"\n{'='*70}")
    print("LAYER-BY-LAYER RELATIVE DIFFERENCES (top 4 categories)")
    print(f"{'='*70}\n")

    # Sort categories by mean relative difference
    sorted_cats = sorted(cat_summary.keys(),
                         key=lambda c: cat_summary[c]['mean_relative_diff'],
                         reverse=True)

    for cat in sorted_cats[:4]:
        items = sorted(categories[cat], key=lambda x: x['layer'])
        print(f"\n{cat}:")
        for item in items:
            bar = '#' * int(item['rel_diff'] * 1000)  # scale for visibility
            layer_str = f"L{item['layer']:>2}" if item['layer'] >= 0 else "   "
            print(f"  {layer_str} rel={item['rel_diff']:.6f}  {bar}")

    # ============================================================
    # THE KEY QUESTION
    # ============================================================
    print(f"\n{'='*70}")
    print("THE KEY QUESTION: WHERE DOES RLHF OPERATE?")
    print(f"{'='*70}\n")

    # Rank by mean relative difference
    print("Categories ranked by mean relative weight change:")
    for i, cat in enumerate(sorted_cats):
        s = cat_summary[cat]
        marker = " <-- P26 measured this" if cat == 'q_proj' else ""
        print(f"  {i+1}. {cat:<18} rel_diff = {s['mean_relative_diff']:.6f}{marker}")

    # Find the category with most change
    top_cat = sorted_cats[0]
    q_rank = sorted_cats.index('q_proj') + 1 if 'q_proj' in sorted_cats else '?'
    print(f"\nRLHF changes {top_cat} the MOST (relative to base norms).")
    print(f"Q-projections rank #{q_rank} out of {len(sorted_cats)} categories.")

    # Attention vs MLP breakdown
    attn_cats = ['q_proj', 'k_proj', 'v_proj', 'o_proj']
    mlp_cats = ['mlp_gate', 'mlp_up', 'mlp_down']

    attn_rel = np.mean([cat_summary[c]['mean_relative_diff'] for c in attn_cats if c in cat_summary])
    mlp_rel = np.mean([cat_summary[c]['mean_relative_diff'] for c in mlp_cats if c in cat_summary])

    print(f"\nAttention projection mean rel_diff: {attn_rel:.6f}")
    print(f"MLP projection mean rel_diff: {mlp_rel:.6f}")
    if mlp_rel > attn_rel:
        print(f"RLHF modifies MLP {mlp_rel/attn_rel:.1f}x more than attention projections.")
    else:
        print(f"RLHF modifies attention {attn_rel/mlp_rel:.1f}x more than MLP projections.")

    # Within attention: Q vs V vs O
    print(f"\nWithin attention:")
    for c in attn_cats:
        if c in cat_summary:
            print(f"  {c}: {cat_summary[c]['mean_relative_diff']:.6f}")

    # Save
    output = {
        'category_summary': cat_summary,
        'sorted_categories': sorted_cats,
    }
    with open('p26_followup_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to p26_followup_results.json")
