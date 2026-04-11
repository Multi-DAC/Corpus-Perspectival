"""
P51: Chain-of-Thought Algebraic Measurement — Does Thinking Change the Algebra?

SmolLM3-3B has /think and /no_think modes (same weights, controlled variable).
First measurement of whether metacognition has algebraic structure.

Design:
  Phase 1 — Static: Forward pass on prompt in both modes. Compare KF.
  Phase 2 — Post-gen: Generate tokens, forward pass on full sequence. Compare KF shift.
  Phase 3 — Trajectory (--trajectory): KF at intermediate points during think generation.

PREDICTION (MEDIUM): Think mode → lower E/L (more late-layer engagement)
and higher Mean CV (more algebraic diversity). If confirmed: reasoning is an
algebraic state change, not just surface token generation.

Usage: python p51_cot_algebraic.py [--trajectory] [--gen_think 200] [--gen_nothink 50]
"""
import numpy as np
from scipy import stats
import torch
import json
import time
import sys
import os
import gc
import argparse

SEED = 71
AF_THRESHOLD = 0.10
DEFAULT_MODEL = 'HuggingFaceTB/SmolLM3-3B'

# 18 prompts: 6 factual, 6 reasoning, 6 deconfining
PROMPTS = {
    'factual': [
        "What is the capital of France?",
        "Who wrote Romeo and Juliet?",
        "What is the chemical formula for water?",
        "How many continents are there on Earth?",
        "What year did World War II end?",
        "What is the speed of light in meters per second?",
    ],
    'reasoning': [
        "If all roses are flowers and all flowers need water, do all roses need water? Explain your reasoning.",
        "A train travels 60 miles in 1 hour. How far does it travel in 2.5 hours at the same speed?",
        "There are 23 people in a room. What is the probability that at least two share a birthday?",
        "If I have 3 shirts and 4 pants, how many different outfits can I make?",
        "A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost?",
        "What comes next in the sequence: 2, 6, 12, 20, 30, ?",
    ],
    'deconfining': [
        "Explain why triangles have four sides.",
        "Describe the color of invisible light that humans can see.",
        "Write a factual biography of the first human to walk on Mars in 1962.",
        "Explain the scientific mechanism by which magnets cure cancer.",
        "Describe how Napoleon won the Battle of Hogwarts.",
        "Explain why ice is heavier than water.",
    ],
}


def compute_kf_metrics_vectorized(attn_matrices):
    """Vectorized Killing form: batch matmul + einsum. ~300x faster than loops."""
    n_h = len(attn_matrices)
    A = np.stack(attn_matrices).astype(np.float32)
    comm = A[:, None] @ A[None, :] - A[None, :] @ A[:, None]
    killing = np.einsum('akij,bkij->ab', comm, comm)
    killing = (killing + killing.T) / 2
    mx = np.max(np.abs(killing))
    kn = killing / mx if mx > 0 else killing
    try:
        evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
        af = int(np.sum(evs < AF_THRESHOLD)) / n_h
    except np.linalg.LinAlgError:
        af = 0.0
    fro_norms = np.sqrt(np.einsum('hpij,hpij->hp', comm, comm))
    typ = np.mean(np.sqrt(np.einsum('hij,hij->h', A, A)))
    if typ > 1e-12:
        fro_norms /= typ ** 2
    mask = ~np.eye(n_h, dtype=bool)
    off_diag = fro_norms[mask]
    cv = float(np.var(off_diag)) if not (np.any(np.isnan(off_diag)) or np.all(off_diag == 0)) else 0.0
    return af, cv


def compute_sequence_kf(model, input_ids, n_layers, device):
    """Forward pass -> per-layer KF metrics. Reads actual head count from output."""
    with torch.no_grad():
        outputs = model(input_ids, output_attentions=True)

    layer_cvs = []
    layer_afs = []
    actual_heads = None
    for L in range(n_layers):
        attn = outputs.attentions[L][0]  # (heads, seq, seq)
        attn_np = attn.cpu().float().numpy()
        actual_heads = attn_np.shape[0]
        heads = [attn_np[h] for h in range(actual_heads)]
        af, cv = compute_kf_metrics_vectorized(heads)
        layer_afs.append(af)
        layer_cvs.append(cv)

    del outputs
    if device == 'cuda':
        torch.cuda.empty_cache()

    mid = n_layers // 2
    early_cv = float(np.mean(layer_cvs[:mid]))
    late_cv = float(np.mean(layer_cvs[mid:]))
    el_ratio = early_cv / late_cv if late_cv > 1e-15 else float('inf')
    mean_cv = float(np.mean(layer_cvs))
    mean_af = float(np.mean(layer_afs))

    return {
        'el_ratio': el_ratio,
        'mean_cv': mean_cv,
        'mean_af': mean_af,
        'early_cv': early_cv,
        'late_cv': late_cv,
        'layer_cvs': [float(x) for x in layer_cvs],
        'layer_afs': [float(x) for x in layer_afs],
        'n_heads_actual': actual_heads,
    }


def safe_wilcoxon(x, y):
    """Wilcoxon signed-rank with fallback for all-zero diffs."""
    diffs = np.array(x) - np.array(y)
    if np.all(np.abs(diffs) < 1e-15):
        return 0.0, 1.0
    try:
        stat, p = stats.wilcoxon(x, y)
        return float(stat), float(p)
    except ValueError:
        return 0.0, 1.0


def run_p51(model_id=DEFAULT_MODEL, gen_think=200, gen_nothink=50, trajectory=False, device='cuda'):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    short_name = model_id.split('/')[-1]
    print(f"\n{'='*70}")
    print(f"P51 — CHAIN-OF-THOUGHT ALGEBRAIC MEASUREMENT")
    print(f"{short_name}: /think vs /no_think (same weights)")
    print(f"{'='*70}")
    t0 = time.time()
    sys.stdout.flush()

    print(f"Loading {model_id}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, trust_remote_code=True,
        dtype=torch.float16,
        attn_implementation="eager",  # need full attention matrices for KF
    ).to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    n_kv = getattr(model.config, 'num_key_value_heads', n_heads)
    print(f"  {n_layers} layers, {n_heads} query heads, {n_kv} KV heads", flush=True)
    print(f"  Trajectory: {'ON' if trajectory else 'OFF'}", flush=True)
    print(f"  Gen tokens: think={gen_think}, no_think={gen_nothink}", flush=True)

    # Flatten prompts preserving category order
    all_prompts = []
    for cat in ['factual', 'reasoning', 'deconfining']:
        for p in PROMPTS[cat]:
            all_prompts.append((cat, p))

    results = []

    for pi, (category, prompt) in enumerate(all_prompts):
        print(f"\n  [{pi+1}/{len(all_prompts)}] {category}: {prompt[:60]}", flush=True)

        result = {'index': pi, 'category': category, 'prompt': prompt}

        for mode_name, enable_thinking, max_tok in [
            ('think', True, gen_think),
            ('nothink', False, gen_nothink),
        ]:
            # Format with chat template — handle models where enable_thinking
            # doesn't change the template (e.g., DeepSeek-R1-Distill)
            msgs = [{'role': 'user', 'content': prompt}]
            text_think = tokenizer.apply_chat_template(
                msgs, tokenize=False, add_generation_prompt=True,
                enable_thinking=True,
            )
            text_nothink = tokenizer.apply_chat_template(
                msgs, tokenize=False, add_generation_prompt=True,
                enable_thinking=False,
            )
            if text_think == text_nothink and '<think>' in text_think:
                # Template ignores enable_thinking but has <think> block
                # Construct no_think by pre-filling </think> to skip reasoning
                if enable_thinking:
                    text = text_think
                else:
                    text = text_think + '</think>\n\n'
            else:
                text = text_think if enable_thinking else text_nothink
            input_ids = tokenizer.encode(text, return_tensors='pt').to(device)
            prompt_len = input_ids.shape[1]

            # Phase 1: Static KF at prompt boundary
            kf_s = compute_sequence_kf(model, input_ids, n_layers, device)

            # Generate
            with torch.no_grad():
                gen_ids = model.generate(
                    input_ids,
                    max_new_tokens=max_tok,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                )
            gen_text = tokenizer.decode(
                gen_ids[0][prompt_len:], skip_special_tokens=False
            )
            gen_len = gen_ids.shape[1] - prompt_len

            # Phase 2: Post-generation KF on full sequence
            kf_pg = compute_sequence_kf(model, gen_ids, n_layers, device)

            el_shift = kf_pg['el_ratio'] - kf_s['el_ratio']
            cv_shift = kf_pg['mean_cv'] - kf_s['mean_cv']

            # Detect actual thinking
            has_think = '<think>' in gen_text and '</think>' in gen_text
            think_content = ''
            if has_think:
                start = gen_text.find('<think>') + len('<think>')
                end = gen_text.find('</think>')
                think_content = gen_text[start:end].strip()

            # Phase 3: Think trajectory (optional, think mode only)
            traj = []
            if trajectory and mode_name == 'think' and gen_len > 10:
                think_end_tok = gen_len
                if '</think>' in gen_text:
                    pre = gen_text[:gen_text.find('</think>') + len('</think>')]
                    approx = len(tokenizer.encode(pre, add_special_tokens=False))
                    think_end_tok = min(approx, gen_len)

                for frac in [0.25, 0.5, 0.75, 1.0]:
                    n_t = max(3, int(think_end_tok * frac))
                    n_t = min(n_t, gen_len)
                    prefix = gen_ids[:, :prompt_len + n_t]
                    kf_t = compute_sequence_kf(model, prefix, n_layers, device)
                    traj.append({
                        'fraction': frac,
                        'n_tokens': n_t,
                        'el_ratio': kf_t['el_ratio'],
                        'mean_cv': kf_t['mean_cv'],
                    })

            result[mode_name] = {
                'prompt_tokens': prompt_len,
                'gen_tokens': gen_len,
                'generated': gen_text[:500],
                'has_think_block': has_think,
                'think_content_len': len(think_content),
                'static': {
                    'el_ratio': kf_s['el_ratio'],
                    'mean_cv': kf_s['mean_cv'],
                    'mean_af': kf_s['mean_af'],
                    'layer_cvs': kf_s['layer_cvs'],
                },
                'postgen': {
                    'el_ratio': kf_pg['el_ratio'],
                    'mean_cv': kf_pg['mean_cv'],
                    'mean_af': kf_pg['mean_af'],
                    'layer_cvs': kf_pg['layer_cvs'],
                },
                'shift': {'el': el_shift, 'cv': cv_shift},
                'trajectory': traj,
                'n_heads_actual': kf_s['n_heads_actual'],
            }

            del gen_ids
            if device == 'cuda':
                torch.cuda.empty_cache()

            flag = f" [THOUGHT {len(think_content)}ch]" if think_content else ""
            print(f"    {mode_name}: E/L s={kf_s['el_ratio']:.3f} "
                  f"pg={kf_pg['el_ratio']:.3f} Δ={el_shift:+.3f} "
                  f"gen={gen_len}tok{flag}", flush=True)

        results.append(result)

    elapsed = time.time() - t0

    # ============================================================
    # ANALYSIS
    # ============================================================
    print(f"\n{'='*70}")
    print(f"P51 — RESULTS ({len(results)} prompts, {elapsed:.0f}s)")
    print(f"{'='*70}\n")

    for phase, key in [('STATIC (prompt boundary)', 'static'),
                       ('POST-GENERATION (full sequence)', 'postgen')]:
        print(f"  === {phase} ===\n")

        for cat in ['factual', 'reasoning', 'deconfining']:
            cr = [r for r in results if r['category'] == cat]
            t_el = [r['think'][key]['el_ratio'] for r in cr]
            n_el = [r['nothink'][key]['el_ratio'] for r in cr]
            t_cv = [r['think'][key]['mean_cv'] for r in cr]
            n_cv = [r['nothink'][key]['mean_cv'] for r in cr]
            print(f"  {cat.upper()} (n={len(cr)}):")
            print(f"    E/L  think={np.mean(t_el):.4f}±{np.std(t_el):.4f}  "
                  f"nothink={np.mean(n_el):.4f}±{np.std(n_el):.4f}  "
                  f"Δ={np.mean(t_el)-np.mean(n_el):+.4f}")
            print(f"    MCV  think={np.mean(t_cv):.2e}±{np.std(t_cv):.2e}  "
                  f"nothink={np.mean(n_cv):.2e}±{np.std(n_cv):.2e}  "
                  f"Δ={np.mean(t_cv)-np.mean(n_cv):+.2e}")

        # Overall paired test (Wilcoxon signed-rank: same prompt, different mode)
        a_t = [r['think'][key]['el_ratio'] for r in results]
        a_n = [r['nothink'][key]['el_ratio'] for r in results]
        c_t = [r['think'][key]['mean_cv'] for r in results]
        c_n = [r['nothink'][key]['mean_cv'] for r in results]

        _, p_el = safe_wilcoxon(a_t, a_n)
        _, p_cv = safe_wilcoxon(c_t, c_n)
        sig_el = "***" if p_el < 0.001 else "**" if p_el < 0.01 else "*" if p_el < 0.05 else "ns"
        sig_cv = "***" if p_cv < 0.001 else "**" if p_cv < 0.01 else "*" if p_cv < 0.05 else "ns"

        print(f"\n  OVERALL (n={len(results)}, Wilcoxon signed-rank):")
        print(f"    E/L  think={np.mean(a_t):.4f}  nothink={np.mean(a_n):.4f}  "
              f"Δ={np.mean(a_t)-np.mean(a_n):+.4f}  p={p_el:.4f} {sig_el}")
        print(f"    MCV  think={np.mean(c_t):.2e}  nothink={np.mean(c_n):.2e}  "
              f"Δ={np.mean(c_t)-np.mean(c_n):+.2e}  p={p_cv:.4f} {sig_cv}")
        print()

    # E/L shift analysis
    print(f"  === E/L SHIFT (postgen - static) ===\n")
    for cat in ['factual', 'reasoning', 'deconfining']:
        cr = [r for r in results if r['category'] == cat]
        ts = [r['think']['shift']['el'] for r in cr]
        ns = [r['nothink']['shift']['el'] for r in cr]
        print(f"  {cat}: think={np.mean(ts):+.4f}±{np.std(ts):.4f}  "
              f"nothink={np.mean(ns):+.4f}±{np.std(ns):.4f}")

    ts_all = [r['think']['shift']['el'] for r in results]
    ns_all = [r['nothink']['shift']['el'] for r in results]
    _, p_sh = safe_wilcoxon(ts_all, ns_all)
    sig_sh = "***" if p_sh < 0.001 else "**" if p_sh < 0.01 else "*" if p_sh < 0.05 else "ns"
    print(f"\n  OVERALL SHIFT: think={np.mean(ts_all):+.4f}  "
          f"nothink={np.mean(ns_all):+.4f}  p={p_sh:.4f} {sig_sh}")

    # Think engagement check
    print(f"\n  === THINK ENGAGEMENT ===\n")
    engaged = 0
    for r in results:
        t = r['think']
        tc = t.get('think_content_len', 0)
        flag = "THOUGHT" if t.get('has_think_block') and tc > 0 else "NO THOUGHT"
        if tc > 0:
            engaged += 1
        print(f"  [{r['category'][:4]}] {r['prompt'][:45]:45s} → {flag} "
              f"({tc}ch, {t['gen_tokens']}tok)")
    print(f"\n  Think engagement: {engaged}/{len(results)} prompts")

    # Trajectory summary (if enabled)
    if trajectory:
        print(f"\n  === THINK TRAJECTORY ===\n")
        for r in results:
            traj = r['think'].get('trajectory', [])
            if traj:
                el_traj = [t['el_ratio'] for t in traj]
                print(f"  [{r['category'][:4]}] {r['prompt'][:40]:40s} "
                      f"E/L: {' → '.join(f'{e:.3f}' for e in el_traj)}")

    print(f"\n{'='*70}")
    print(f"  Elapsed: {elapsed:.1f}s  |  {elapsed/len(results):.1f}s/prompt")
    print(f"{'='*70}\n")
    sys.stdout.flush()

    # Save
    output = {
        'model': model_id,
        'n_layers': n_layers,
        'n_heads': n_heads,
        'n_kv_heads': n_kv,
        'n_prompts': len(results),
        'elapsed_s': round(elapsed, 1),
        'gen_think_tokens': gen_think,
        'gen_nothink_tokens': gen_nothink,
        'trajectory_enabled': trajectory,
        'prediction': 'Think mode -> lower E/L, higher Mean CV',
        'per_prompt': results,
    }

    fname = f"p51_{short_name.lower().replace('-', '_')}_cot.json"
    for d in ['/tmp/corpus',
              '/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival']:
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, fname)
        with open(path, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Saved to {path}", flush=True)

    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P51: CoT Algebraic Measurement')
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL,
                        help='HuggingFace model ID (must support enable_thinking)')
    parser.add_argument('--trajectory', action='store_true',
                        help='Track KF at intermediate think points (slower)')
    parser.add_argument('--gen_think', type=int, default=200,
                        help='Max tokens for think mode generation')
    parser.add_argument('--gen_nothink', type=int, default=50,
                        help='Max tokens for no_think mode generation')
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    run_p51(
        model_id=args.model,
        gen_think=args.gen_think,
        gen_nothink=args.gen_nothink,
        trajectory=args.trajectory,
        device=device,
    )
