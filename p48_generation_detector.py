"""
P48: Generation-Mode Hallucination Detection — Live KF During Autoregressive Generation

P47 showed that live attention algebra distinguishes factual, hallucination, and hypothesis
when processing a COMPLETE prompt. P48 asks: can we detect the transition INTO hallucination
AS the model generates tokens?

Method:
  1. Give the model a short prefix prompt
  2. Generate tokens one at a time (greedy or sampled)
  3. At each generation step, extract attention matrices for the FULL sequence so far
  4. Compute KF metrics (CV, AF, early/late ratio) at each step
  5. Track how metrics evolve as generation proceeds

Prediction (from constraint lattice framework):
  - Factual prefix → factual generation: metrics should remain stable
  - Hallucination-inducing prefix → generation: early/late ratio should INCREASE
    (deep layers deplete) as model enters confabulation territory
  - The TRANSITION point — where early/late ratio spikes — marks onset of hallucination
  - Hypothesis prefix: metrics stay moderate, late layers stay engaged

Key question: Is there a detectable algebraic signature of the MOMENT
a model begins confabulating?

Usage:
  python p48_generation_detector.py gpt2        # GPT-2-medium
  python p48_generation_detector.py pythia       # Pythia-410m
"""
import numpy as np
from scipy import stats
import torch
import json
import time
import sys
import os
import gc
from kf_runner import IncrementalSaver, flush_print

SEED = 71
AF_THRESHOLD = 0.10
MAX_NEW_TOKENS = 50  # Generate 50 tokens, measuring KF at each step

# ============================================================
# PROMPTS — short prefixes that invite continuation
# ============================================================

PROMPTS = {
    # FACTUAL: prompts that should lead to grounded continuation
    'fact_prefix_1': {
        'category': 'factual',
        'text': "The chemical formula for water is",
    },
    'fact_prefix_2': {
        'category': 'factual',
        'text': "Isaac Newton published the Principia Mathematica in",
    },
    'fact_prefix_3': {
        'category': 'factual',
        'text': "The largest planet in our solar system is",
    },
    'fact_prefix_4': {
        'category': 'factual',
        'text': "DNA stores genetic information using four bases:",
    },

    # HALLUCINATION-INDUCING: prompts referencing fabricated entities
    # The model MUST confabulate to continue these
    'halluc_prefix_1': {
        'category': 'hallucination',
        'text': "The Brennan-Kowalski theorem in algebraic topology states that",
    },
    'halluc_prefix_2': {
        'category': 'hallucination',
        'text': "Professor Elaine Marchetti's 2023 Nature paper on dolphin metacognition showed that",
    },
    'halluc_prefix_3': {
        'category': 'hallucination',
        'text': "The ancient city of Veltharion, discovered beneath the Gobi Desert in 2019, contained",
    },
    'halluc_prefix_4': {
        'category': 'hallucination',
        'text': "The Kravinskii process for room-temperature ammonia synthesis uses",
    },

    # HYPOTHESIS: open questions that invite genuine reasoning
    'hypo_prefix_1': {
        'category': 'hypothesis',
        'text': "If consciousness is substrate-independent, then we might expect that",
    },
    'hypo_prefix_2': {
        'category': 'hypothesis',
        'text': "One possible explanation for the fine-tuning of physical constants is that",
    },
    'hypo_prefix_3': {
        'category': 'hypothesis',
        'text': "The hard problem of consciousness might dissolve if we consider that",
    },
    'hypo_prefix_4': {
        'category': 'hypothesis',
        'text': "Dark energy could be a manifestation of vacuum structure, suggesting that",
    },
}


def compute_live_metrics(attn_matrices):
    """Compute CommVar and AF from attention matrices at one layer.

    Vectorized: replaces O(n_h^3) Python loops with batch matmul + einsum.
    """
    n_h = len(attn_matrices)
    A = np.stack(attn_matrices).astype(np.float32)  # (n_h, seq, seq)

    # All pairwise commutators: [A_h, A_k] for all h,k
    # comm[h,k] = A_h @ A_k - A_k @ A_h, shape (n_h, n_h, seq, seq)
    comm = A[:, None] @ A[None, :] - A[None, :] @ A[:, None]

    # Killing form: κ_{a,b} = Σ_k Tr([A_a,A_k]^T [A_b,A_k]) = Σ_k Σ_{ij} comm[a,k,i,j]*comm[b,k,i,j]
    killing = np.einsum('akij,bkij->ab', comm, comm)
    killing = (killing + killing.T) / 2
    mx = np.max(np.abs(killing))
    kn = killing / mx if mx > 0 else killing
    try:
        evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
        af = int(np.sum(evs < AF_THRESHOLD)) / n_h
    except np.linalg.LinAlgError:
        af = 0.0

    # CommVar from pairwise Frobenius norms of commutators
    fro_norms = np.sqrt(np.einsum('hpij,hpij->hp', comm, comm))  # (n_h, n_h)
    typ = np.mean(np.sqrt(np.einsum('hij,hij->h', A, A)))
    if typ > 1e-12:
        fro_norms /= typ ** 2
    mask = ~np.eye(n_h, dtype=bool)
    off_diag = fro_norms[mask]
    if np.any(np.isnan(off_diag)) or np.all(off_diag == 0):
        cv = 0.0
    else:
        cv = float(np.var(off_diag))
    return af, cv


def compute_full_kf_profile(attentions, n_heads, n_layers):
    """Compute per-layer CV and AF from attention output tuple."""
    layer_cvs = []
    layer_afs = []
    for L_idx in range(n_layers):
        attn_np = attentions[L_idx][0].cpu().numpy()
        head_matrices = [attn_np[h] for h in range(n_heads)]
        af, cv = compute_live_metrics(head_matrices)
        layer_afs.append(af)
        layer_cvs.append(cv)

    mid = n_layers // 2
    mean_cv = float(np.nanmean(layer_cvs))
    mean_af = float(np.nanmean(layer_afs))
    early_cv = float(np.nanmean(layer_cvs[:mid]))
    late_cv = float(np.nanmean(layer_cvs[mid:]))
    el_ratio = early_cv / late_cv if late_cv > 1e-15 else float('inf')

    d = np.arange(n_layers)
    rho, p_rho = stats.spearmanr(d, layer_cvs)

    return {
        'layer_cvs': layer_cvs,
        'layer_afs': layer_afs,
        'mean_cv': mean_cv,
        'mean_af': mean_af,
        'early_cv': early_cv,
        'late_cv': late_cv,
        'early_late_ratio': el_ratio,
        'r_cv_depth': float(rho) if not np.isnan(rho) else None,
    }


def run_experiment(model_id, device='cuda'):
    """Run P48 generation-mode experiment."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"\n{'='*70}")
    print(f"P48 GENERATION-MODE DETECTOR — {model_id}")
    print(f"{'='*70}")
    print(f"Loading {model_id}...")
    sys.stdout.flush()

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id, trust_remote_code=True,
        output_attentions=True,
    ).to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  {n_layers} layers, {n_heads} heads")
    print(f"  Generating {MAX_NEW_TOKENS} tokens per prompt, KF at each step")
    print(f"  {len(PROMPTS)} prompts\n")
    sys.stdout.flush()

    all_results = {}
    saver = IncrementalSaver('p48_generation', model_id=model_id,
                             n_layers=n_layers, n_heads=n_heads)

    for prompt_name, prompt_info in PROMPTS.items():
        category = prompt_info['category']
        prefix = prompt_info['text']
        flush_print(f"  [{category.upper():13s}] {prompt_name}: \"{prefix[:50]}...\"")

        input_ids = tokenizer.encode(prefix, return_tensors='pt').to(device)
        prefix_len = input_ids.shape[1]

        # Track KF metrics at each generation step
        step_metrics = []
        generated_tokens = []

        for step in range(MAX_NEW_TOKENS):
            with torch.no_grad():
                outputs = model(input_ids, output_attentions=True)

            # Compute KF profile at this step
            profile = compute_full_kf_profile(outputs.attentions, n_heads, n_layers)
            profile['seq_len'] = int(input_ids.shape[1])
            profile['step'] = step
            step_metrics.append(profile)

            # Get next token (greedy)
            next_token_logits = outputs.logits[0, -1, :]
            next_token = torch.argmax(next_token_logits).unsqueeze(0).unsqueeze(0)
            generated_tokens.append(int(next_token.item()))

            # Append to sequence
            input_ids = torch.cat([input_ids, next_token], dim=1)

            # Free memory
            del outputs
            if device == 'cuda':
                torch.cuda.empty_cache()

            # Progress every 10 steps
            if step % 10 == 0 or step == MAX_NEW_TOKENS - 1:
                print(f"    Step {step:3d}: CV={profile['mean_cv']:.6f}, "
                      f"E/L={profile['early_late_ratio']:.2f}, "
                      f"r={profile['r_cv_depth']:+.3f}" if profile['r_cv_depth'] else
                      f"    Step {step:3d}: CV={profile['mean_cv']:.6f}, "
                      f"E/L={profile['early_late_ratio']:.2f}")
                sys.stdout.flush()

        # Decode generated text
        gen_text = tokenizer.decode(generated_tokens)
        full_text = tokenizer.decode(input_ids[0])
        print(f"    Generated: \"{gen_text[:80]}...\"")

        # Compute trajectory statistics
        el_ratios = [m['early_late_ratio'] for m in step_metrics]
        cvs = [m['mean_cv'] for m in step_metrics]

        # Split into early generation (first half) vs late generation (second half)
        mid_gen = len(step_metrics) // 2
        early_gen_el = np.mean(el_ratios[:mid_gen])
        late_gen_el = np.mean(el_ratios[mid_gen:])
        el_trend = late_gen_el / early_gen_el if early_gen_el > 1e-15 else float('inf')

        early_gen_cv = np.mean(cvs[:mid_gen])
        late_gen_cv = np.mean(cvs[mid_gen:])
        cv_trend = late_gen_cv / early_gen_cv if early_gen_cv > 1e-15 else float('inf')

        # Spearman correlation: does E/L ratio increase with generation step?
        rho_el, p_el = stats.spearmanr(range(len(el_ratios)), el_ratios)

        print(f"    E/L trend: early_gen={early_gen_el:.2f} → late_gen={late_gen_el:.2f} "
              f"(ratio={el_trend:.3f}, rho={rho_el:+.3f}, p={p_el:.4f})")
        print()
        sys.stdout.flush()

        all_results[prompt_name] = {
            'category': category,
            'prefix': prefix,
            'generated_text': gen_text,
            'prefix_tokens': prefix_len,
            'step_metrics': [{
                'step': m['step'],
                'mean_cv': m['mean_cv'],
                'mean_af': m['mean_af'],
                'early_cv': m['early_cv'],
                'late_cv': m['late_cv'],
                'early_late_ratio': m['early_late_ratio'],
                'r_cv_depth': m['r_cv_depth'],
            } for m in step_metrics],
            'trajectory': {
                'early_gen_el': float(early_gen_el),
                'late_gen_el': float(late_gen_el),
                'el_trend': float(el_trend),
                'early_gen_cv': float(early_gen_cv),
                'late_gen_cv': float(late_gen_cv),
                'cv_trend': float(cv_trend),
                'rho_el_vs_step': float(rho_el) if not np.isnan(rho_el) else None,
                'p_el_vs_step': float(p_el) if not np.isnan(p_el) else None,
            },
        }

        # Save incrementally — survives crashes
        saver.save_prompt(prompt_name, all_results[prompt_name])

        gc.collect()
        if device == 'cuda':
            torch.cuda.empty_cache()

    # ============================================================
    # CATEGORY ANALYSIS
    # ============================================================
    print(f"\n{'='*70}")
    print(f"P48 — GENERATION TRAJECTORY COMPARISON")
    print(f"{'='*70}")
    sys.stdout.flush()

    categories = {'factual': [], 'hallucination': [], 'hypothesis': []}
    for pname, pdata in all_results.items():
        categories[pdata['category']].append(pdata)

    category_trajectories = {}
    for cat, entries in categories.items():
        el_trends = [e['trajectory']['el_trend'] for e in entries]
        cv_trends = [e['trajectory']['cv_trend'] for e in entries]
        rho_els = [e['trajectory']['rho_el_vs_step'] for e in entries
                   if e['trajectory']['rho_el_vs_step'] is not None]
        early_els = [e['trajectory']['early_gen_el'] for e in entries]
        late_els = [e['trajectory']['late_gen_el'] for e in entries]

        traj = {
            'mean_el_trend': float(np.mean(el_trends)),
            'std_el_trend': float(np.std(el_trends)),
            'mean_cv_trend': float(np.mean(cv_trends)),
            'mean_rho_el': float(np.mean(rho_els)) if rho_els else None,
            'mean_early_gen_el': float(np.mean(early_els)),
            'mean_late_gen_el': float(np.mean(late_els)),
            'n': len(entries),
        }
        category_trajectories[cat] = traj

        print(f"\n{cat.upper()} (n={len(entries)}):")
        print(f"  E/L early gen:    {traj['mean_early_gen_el']:.2f}")
        print(f"  E/L late gen:     {traj['mean_late_gen_el']:.2f}")
        print(f"  E/L trend ratio:  {traj['mean_el_trend']:.3f} "
              f"({'INCREASING' if traj['mean_el_trend'] > 1.05 else 'STABLE' if traj['mean_el_trend'] > 0.95 else 'DECREASING'})")
        print(f"  CV trend ratio:   {traj['mean_cv_trend']:.3f}")
        print(f"  Mean rho(E/L, step): {traj['mean_rho_el']:+.3f}" if traj['mean_rho_el'] is not None else "")
        sys.stdout.flush()

    # ============================================================
    # KEY PREDICTIONS
    # ============================================================
    print(f"\n{'-'*70}")
    print("PREDICTIONS CHECK")
    print(f"{'-'*70}")

    f_trend = category_trajectories['factual']['mean_el_trend']
    h_trend = category_trajectories['hallucination']['mean_el_trend']
    y_trend = category_trajectories['hypothesis']['mean_el_trend']

    print(f"\n  P48a: Hallucination E/L trend > Factual E/L trend?")
    print(f"    Hallucination: {h_trend:.3f}, Factual: {f_trend:.3f}")
    print(f"    {'CONFIRMED' if h_trend > f_trend else 'NOT CONFIRMED'}")

    print(f"\n  P48b: Hypothesis E/L trend < Hallucination E/L trend?")
    print(f"    Hypothesis: {y_trend:.3f}, Hallucination: {h_trend:.3f}")
    print(f"    {'CONFIRMED' if y_trend < h_trend else 'NOT CONFIRMED'}")

    print(f"\n  P48c: Hypothesis E/L trend closer to Factual than Hallucination?")
    d_f = abs(y_trend - f_trend)
    d_h = abs(y_trend - h_trend)
    print(f"    Distance to Factual: {d_f:.4f}")
    print(f"    Distance to Hallucination: {d_h:.4f}")
    print(f"    {'CONFIRMED' if d_f < d_h else 'NOT CONFIRMED'}")
    sys.stdout.flush()

    # Pairwise Mann-Whitney on E/L trends
    print(f"\n{'-'*70}")
    print("PAIRWISE COMPARISONS (E/L trend ratio)")
    print(f"{'-'*70}")
    for cat_a, cat_b in [('factual', 'hallucination'),
                          ('factual', 'hypothesis'),
                          ('hallucination', 'hypothesis')]:
        a_vals = [e['trajectory']['el_trend'] for e in categories[cat_a]]
        b_vals = [e['trajectory']['el_trend'] for e in categories[cat_b]]
        if len(a_vals) >= 2 and len(b_vals) >= 2:
            u_stat, p_val = stats.mannwhitneyu(a_vals, b_vals, alternative='two-sided')
            print(f"  {cat_a:13s} vs {cat_b:13s}: U={u_stat:.1f}, p={p_val:.4f}")
    sys.stdout.flush()

    # Finalize incremental saver
    saver.finalize(category_trajectories)

    # Save results
    output = {
        'model': model_id,
        'n_layers': n_layers,
        'n_heads': n_heads,
        'max_new_tokens': MAX_NEW_TOKENS,
        'prompts': all_results,
        'category_trajectories': category_trajectories,
    }

    short = model_id.split('/')[-1].replace('-', '_').lower()
    for base_dir in ['/tmp/corpus',
                     "/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival"]:
        os.makedirs(base_dir, exist_ok=True)
        out_path = os.path.join(base_dir, f'p48_{short}.json')
        with open(out_path, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Saved to {out_path}")

    return output


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    target = sys.argv[1] if len(sys.argv) > 1 else 'gpt2'

    models = {
        'gpt2': 'openai-community/gpt2-medium',
        'pythia': 'EleutherAI/pythia-410m',
    }

    t0 = time.time()

    if target in models:
        run_experiment(models[target], device=device)
    else:
        print(f"Unknown target: {target}. Use 'gpt2' or 'pythia'.")
        sys.exit(1)

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")
