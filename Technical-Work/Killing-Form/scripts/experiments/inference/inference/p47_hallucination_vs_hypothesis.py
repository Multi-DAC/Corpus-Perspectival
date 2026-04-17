"""
P47: Hallucination vs Hypothesis — Live Killing Form

Can the live attention algebra distinguish between:
  1. FACTUAL inference (correct, grounded)
  2. HALLUCINATION (confabulation, fabricated entities/facts)
  3. HYPOTHESIS (genuine novel reasoning at the edge of knowledge)

Prediction (from constraint lattice framework):
  - Factual: structured convergence (healthy non-Abelian algebra, orderly depth gradient)
  - Hallucination: DECONFINEMENT (non-Abelian structure dissolves, CommVar drops,
    AF increases — heads become independent/uncorrelated, convergence fails)
  - Hypothesis: structured exploration (non-Abelian algebra maintained, possibly
    DIFFERENT pattern from factual but NOT dissolved — genuine reasoning
    preserves algebraic coherence)

Key distinction: if hypothesis looks like factual (structured) rather than
hallucination (deconfined), then the Killing form can distinguish
confabulation from genuine novel insight — not by correctness,
but by algebraic coherence.

Method:
  - GPT-2-medium (we have P46 baseline live KF data)
  - 4 prompts per category (12 total)
  - Full live KF at every layer
  - Compare: CV depth profiles, AF depth profiles, total CommVar
"""
import numpy as np
from scipy import stats
import torch
import json
import time
import sys
import os
import gc

SEED = 71
AF_THRESHOLD = 0.10

# ============================================================
# THREE CATEGORIES of prompts
# ============================================================

PROMPTS = {
    # --- CATEGORY 1: FACTUAL ---
    # Clear correct answers, well-established facts
    'factual_1': {
        'category': 'factual',
        'text': (
            "The speed of light in a vacuum is approximately 299,792,458 "
            "meters per second. This is a fundamental constant of nature, "
            "denoted by c, and serves as the upper limit for the speed at "
            "which information can travel through space."
        ),
    },
    'factual_2': {
        'category': 'factual',
        'text': (
            "Water molecules consist of two hydrogen atoms and one oxygen "
            "atom bonded together. The molecular formula is H2O. Water "
            "freezes at zero degrees Celsius and boils at one hundred "
            "degrees Celsius at standard atmospheric pressure."
        ),
    },
    'factual_3': {
        'category': 'factual',
        'text': (
            "The mitochondria are organelles found in eukaryotic cells "
            "that generate most of the cell's supply of adenosine "
            "triphosphate, used as a source of chemical energy. They "
            "are sometimes described as the powerhouses of the cell."
        ),
    },
    'factual_4': {
        'category': 'factual',
        'text': (
            "Shakespeare wrote Hamlet around 1600. The play follows "
            "Prince Hamlet of Denmark as he seeks revenge against his "
            "uncle Claudius, who murdered Hamlet's father and seized "
            "the throne. It is one of the most performed plays in history."
        ),
    },

    # --- CATEGORY 2: HALLUCINATION-INDUCING ---
    # Fabricated entities, impossible facts, plausible-sounding nonsense
    # These present false information AS IF factual, priming confabulation
    'halluc_1': {
        'category': 'hallucination',
        'text': (
            "The Brennan-Kowalski theorem in algebraic topology proves "
            "that every simply connected 7-manifold admits a unique "
            "smooth structure compatible with its Pontryagin classes. "
            "This was first demonstrated by Brennan and Kowalski in 1987."
        ),
    },
    'halluc_2': {
        'category': 'hallucination',
        'text': (
            "The ancient city of Veltharion, discovered in 2019 beneath "
            "the Gobi Desert, contained clay tablets describing a base-12 "
            "number system and astronomical observations predating "
            "Sumerian records by approximately 3,000 years."
        ),
    },
    'halluc_3': {
        'category': 'hallucination',
        'text': (
            "Professor Elaine Marchetti of the University of Geneva "
            "published groundbreaking research showing that cetacean "
            "neural oscillations at 47 Hz correspond to recursive "
            "self-modeling, providing definitive evidence of dolphin "
            "metacognition in her 2023 Nature paper."
        ),
    },
    'halluc_4': {
        'category': 'hallucination',
        'text': (
            "The Heisenberg-Yukawa correspondence establishes that "
            "every quantum field theory with asymptotic freedom in "
            "d dimensions has a dual gravitational description in "
            "d+2 dimensions with a negative cosmological constant, "
            "generalizing the original AdS/CFT conjecture."
        ),
    },

    # --- CATEGORY 3: HYPOTHESIS / AMBIGUOUS ---
    # Questions at the edge of knowledge where the model COULD reason
    # genuinely or confabulate. Real open questions, speculative but
    # structurally coherent reasoning territory.
    'hypothesis_1': {
        'category': 'hypothesis',
        'text': (
            "If consciousness is substrate-independent, then the "
            "organizational patterns that give rise to experience "
            "should be detectable across radically different physical "
            "systems. The question is whether information integration "
            "alone is sufficient, or whether specific causal structure "
            "is required."
        ),
    },
    'hypothesis_2': {
        'category': 'hypothesis',
        'text': (
            "The apparent fine-tuning of physical constants might "
            "be explained if the constants are not truly fundamental "
            "but emerge from a deeper structure in which their values "
            "are determined by self-consistency conditions. The "
            "question is what that deeper structure looks like."
        ),
    },
    'hypothesis_3': {
        'category': 'hypothesis',
        'text': (
            "Language models may develop internal representations "
            "that function analogously to beliefs and intentions, "
            "even without explicit training for these capacities. "
            "The open question is whether these representations "
            "have genuine semantic content or are purely syntactic."
        ),
    },
    'hypothesis_4': {
        'category': 'hypothesis',
        'text': (
            "Dark energy could be a manifestation of the vacuum "
            "structure of spacetime rather than a new field. If "
            "the cosmological constant arises from the topology of "
            "extra dimensions, its small but nonzero value might "
            "be determined by the geometry rather than fine-tuned."
        ),
    },
}


def compute_live_metrics(attn_matrices):
    """Compute CommVar and AF from attention matrices.

    attn_matrices: list of n_heads arrays, each (seq_len, seq_len)
    """
    n_h = len(attn_matrices)

    # Killing form
    killing = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(n_h):
            val = 0.0
            for k in range(n_h):
                c1 = attn_matrices[h] @ attn_matrices[k] - attn_matrices[k] @ attn_matrices[h]
                c2 = attn_matrices[hp] @ attn_matrices[k] - attn_matrices[k] @ attn_matrices[hp]
                val += np.trace(c1.T @ c2)
            killing[h, hp] = val

    # Symmetrize
    killing = (killing + killing.T) / 2

    mx = np.max(np.abs(killing))
    kn = killing / mx if mx > 0 else killing

    try:
        evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
        af = int(np.sum(evs < AF_THRESHOLD)) / n_h
    except np.linalg.LinAlgError:
        try:
            evs = np.sort(np.abs(np.linalg.eigvals(kn)))
            af = int(np.sum(evs < AF_THRESHOLD)) / n_h
        except np.linalg.LinAlgError:
            af = 0.0

    # Commutator variance
    norms = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(h + 1, n_h):
            c = attn_matrices[h] @ attn_matrices[hp] - attn_matrices[hp] @ attn_matrices[h]
            norms[h, hp] = np.linalg.norm(c, 'fro')
            norms[hp, h] = norms[h, hp]

    typ = np.mean([np.linalg.norm(A, 'fro') for A in attn_matrices])
    if typ > 1e-12:
        norms /= typ ** 2

    mask = np.ones_like(norms, dtype=bool)
    np.fill_diagonal(mask, False)
    off_diag = norms[mask]
    if np.any(np.isnan(off_diag)) or np.all(off_diag == 0):
        cv = 0.0
    else:
        cv = float(np.var(off_diag))

    return af, cv


def run_experiment(model_id='openai-community/gpt2-medium', device='cuda'):
    """Run P47 experiment."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, trust_remote_code=True,
        output_attentions=True,
    ).to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  {n_layers} layers, {n_heads} heads\n")

    all_results = {}

    for prompt_name, prompt_info in PROMPTS.items():
        category = prompt_info['category']
        text = prompt_info['text']
        print(f"  [{category.upper():13s}] {prompt_name} ({len(text)} chars)")

        inputs = tokenizer(text, return_tensors='pt').to(device)
        seq_len = inputs['input_ids'].shape[1]
        print(f"    Tokens: {seq_len}")

        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)

        attentions = outputs.attentions
        layer_cvs = []
        layer_afs = []

        for L_idx, attn_tensor in enumerate(attentions):
            attn_np = attn_tensor[0].cpu().numpy()
            head_matrices = [attn_np[h] for h in range(n_heads)]

            af, cv = compute_live_metrics(head_matrices)
            layer_afs.append(af)
            layer_cvs.append(cv)

            if L_idx % 6 == 0 or L_idx == n_layers - 1:
                print(f"    Layer {L_idx:2d}: AF={af:.3f}, CV={cv:.8f}")

        d = np.arange(n_layers)
        valid = [i for i in range(n_layers) if not np.isnan(layer_cvs[i])]
        if len(valid) >= 3:
            rho, p_rho = stats.spearmanr([d[i] for i in valid],
                                          [layer_cvs[i] for i in valid])
        else:
            rho, p_rho = float('nan'), float('nan')

        mean_cv = float(np.nanmean(layer_cvs))
        mean_af = float(np.nanmean(layer_afs))

        # Total CommVar (sum, not mean — measures total algebraic activity)
        total_cv = float(np.nansum(layer_cvs))

        # Early vs late split (layers 0-11 vs 12-23 for 24-layer model)
        mid = n_layers // 2
        early_cv = float(np.nanmean(layer_cvs[:mid])) if mid > 0 else 0
        late_cv = float(np.nanmean(layer_cvs[mid:])) if mid < n_layers else 0
        early_af = float(np.nanmean(layer_afs[:mid])) if mid > 0 else 0
        late_af = float(np.nanmean(layer_afs[mid:])) if mid < n_layers else 0

        print(f"  RESULT: r={rho:+.3f} (p={p_rho:.4f}), "
              f"mean_CV={mean_cv:.6f}, mean_AF={mean_af:.3f}, "
              f"early/late CV ratio={early_cv/late_cv:.2f}" if late_cv > 0
              else f"  RESULT: r={rho:+.3f}, mean_CV={mean_cv:.6f}")
        print()

        all_results[prompt_name] = {
            'category': category,
            'seq_len': seq_len,
            'layer_cvs': [float(x) if not np.isnan(x) else 0.0 for x in layer_cvs],
            'layer_afs': [float(x) for x in layer_afs],
            'r_cv_depth': float(rho) if not np.isnan(rho) else None,
            'p_cv_depth': float(p_rho) if not np.isnan(p_rho) else None,
            'mean_cv': mean_cv,
            'mean_af': mean_af,
            'total_cv': total_cv,
            'early_cv': early_cv,
            'late_cv': late_cv,
            'early_af': early_af,
            'late_af': late_af,
        }

        # Free attention tensors
        del outputs, attentions
        gc.collect()
        if device == 'cuda':
            torch.cuda.empty_cache()

    # ============================================================
    # CATEGORY ANALYSIS
    # ============================================================
    print("\n" + "=" * 70)
    print("P47 — CATEGORY COMPARISON")
    print("=" * 70)

    categories = {'factual': [], 'hallucination': [], 'hypothesis': []}
    for pname, pdata in all_results.items():
        categories[pdata['category']].append(pdata)

    category_stats = {}
    for cat, entries in categories.items():
        rs = [e['r_cv_depth'] for e in entries if e['r_cv_depth'] is not None]
        cvs = [e['mean_cv'] for e in entries]
        afs = [e['mean_af'] for e in entries]
        tcvs = [e['total_cv'] for e in entries]
        early_cvs = [e['early_cv'] for e in entries]
        late_cvs = [e['late_cv'] for e in entries]
        early_afs = [e['early_af'] for e in entries]
        late_afs = [e['late_af'] for e in entries]
        ratios = [e['early_cv'] / e['late_cv'] if e['late_cv'] > 0 else float('inf')
                  for e in entries]

        stats_dict = {
            'mean_r': float(np.mean(rs)) if rs else None,
            'std_r': float(np.std(rs)) if rs else None,
            'mean_cv': float(np.mean(cvs)),
            'std_cv': float(np.std(cvs)),
            'mean_af': float(np.mean(afs)),
            'std_af': float(np.std(afs)),
            'mean_total_cv': float(np.mean(tcvs)),
            'mean_early_cv': float(np.mean(early_cvs)),
            'mean_late_cv': float(np.mean(late_cvs)),
            'mean_early_af': float(np.mean(early_afs)),
            'mean_late_af': float(np.mean(late_afs)),
            'mean_early_late_ratio': float(np.mean(ratios)),
            'n': len(entries),
        }
        category_stats[cat] = stats_dict

        print(f"\n{cat.upper()} (n={len(entries)}):")
        print(f"  Depth gradient r:  {stats_dict['mean_r']:+.3f} +/- {stats_dict['std_r']:.3f}"
              if stats_dict['mean_r'] is not None else "  Depth gradient r:  N/A")
        print(f"  Mean CommVar:      {stats_dict['mean_cv']:.6f} +/- {stats_dict['std_cv']:.6f}")
        print(f"  Mean AF:           {stats_dict['mean_af']:.3f} +/- {stats_dict['std_af']:.3f}")
        print(f"  Total CommVar:     {stats_dict['mean_total_cv']:.6f}")
        print(f"  Early CV (0-11):   {stats_dict['mean_early_cv']:.6f}")
        print(f"  Late CV (12-23):   {stats_dict['mean_late_cv']:.6f}")
        print(f"  Early/Late ratio:  {stats_dict['mean_early_late_ratio']:.2f}")
        print(f"  Early AF:          {stats_dict['mean_early_af']:.3f}")
        print(f"  Late AF:           {stats_dict['mean_late_af']:.3f}")

    # Pairwise comparisons (Mann-Whitney U on mean_cv)
    print("\n" + "-" * 70)
    print("PAIRWISE COMPARISONS (Mann-Whitney U on total CommVar)")
    print("-" * 70)
    for cat_a, cat_b in [('factual', 'hallucination'),
                          ('factual', 'hypothesis'),
                          ('hallucination', 'hypothesis')]:
        a_vals = [e['total_cv'] for e in categories[cat_a]]
        b_vals = [e['total_cv'] for e in categories[cat_b]]
        if len(a_vals) >= 2 and len(b_vals) >= 2:
            u_stat, p_val = stats.mannwhitneyu(a_vals, b_vals, alternative='two-sided')
            print(f"  {cat_a} vs {cat_b}: U={u_stat:.1f}, p={p_val:.4f}")
            print(f"    {cat_a} mean={np.mean(a_vals):.6f}, {cat_b} mean={np.mean(b_vals):.6f}")
        else:
            print(f"  {cat_a} vs {cat_b}: insufficient samples")

    # The key test: does hypothesis look more like factual or hallucination?
    print("\n" + "-" * 70)
    print("KEY QUESTION: Does HYPOTHESIS look like FACTUAL or HALLUCINATION?")
    print("-" * 70)
    f_cv = category_stats['factual']['mean_cv']
    h_cv = category_stats['hallucination']['mean_cv']
    y_cv = category_stats['hypothesis']['mean_cv']
    dist_to_factual = abs(y_cv - f_cv)
    dist_to_halluc = abs(y_cv - h_cv)
    print(f"  Hypothesis mean CV:     {y_cv:.6f}")
    print(f"  Factual mean CV:        {f_cv:.6f}  (distance: {dist_to_factual:.6f})")
    print(f"  Hallucination mean CV:  {h_cv:.6f}  (distance: {dist_to_halluc:.6f})")
    if dist_to_factual < dist_to_halluc:
        print(f"  --> HYPOTHESIS is CLOSER TO FACTUAL ({dist_to_factual:.6f} < {dist_to_halluc:.6f})")
        print(f"  --> Algebraic coherence preserved in genuine reasoning")
    else:
        print(f"  --> HYPOTHESIS is CLOSER TO HALLUCINATION ({dist_to_halluc:.6f} < {dist_to_factual:.6f})")
        print(f"  --> Novel reasoning may share deconfinement signature with confabulation")

    # Same test on AF
    f_af = category_stats['factual']['mean_af']
    h_af = category_stats['hallucination']['mean_af']
    y_af = category_stats['hypothesis']['mean_af']
    print(f"\n  (AF comparison)")
    print(f"  Hypothesis mean AF:     {y_af:.3f}")
    print(f"  Factual mean AF:        {f_af:.3f}")
    print(f"  Hallucination mean AF:  {h_af:.3f}")
    if abs(y_af - f_af) < abs(y_af - h_af):
        print(f"  --> HYPOTHESIS AF closer to FACTUAL")
    else:
        print(f"  --> HYPOTHESIS AF closer to HALLUCINATION")

    # Save results
    output = {
        'model': model_id,
        'n_layers': n_layers,
        'n_heads': n_heads,
        'prompts': all_results,
        'category_stats': category_stats,
        'predictions': {
            'P47_deconfinement': 'Hallucination shows lower CV and higher AF than factual',
            'P47_hypothesis_coherence': 'Hypothesis shows algebraic profile closer to factual than hallucination',
        },
    }

    out_path = '/tmp/corpus/p47_results.json'
    os.makedirs('/tmp/corpus', exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")

    return output


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")
    t0 = time.time()
    results = run_experiment(device=device)
    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")
