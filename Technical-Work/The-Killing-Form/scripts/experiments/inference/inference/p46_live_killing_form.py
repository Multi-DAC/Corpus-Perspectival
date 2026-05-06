"""
P46: Live Killing Form — Attention patterns during inference

Instead of static Q-projection weights, measure the actual attention
matrices produced during inference. If static weights = natal constraint
geometry, then live attention = voluntary + natal constraints in action.

Questions:
1. Does live attention show the same depth gradient as static weights?
2. Does input type modulate the Killing form?
3. Is the parallel/sequential direction preserved in live behavior?
4. What is the DIFFERENCE between static and live KF? (= space of navigation?)

Method:
  - Run inference with output_attentions=True
  - For each layer, each head: attention matrix A_h is (seq_len x seq_len)
  - Compute commutators [A_h, A_h'] as with weight matrices
  - CommVar and AF per layer, same as P43
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
# Prompts — different types of input to test modulation
# ============================================================

PROMPTS = {
    'repetitive': (
        "The cat sat on the mat. The cat sat on the mat. "
        "The cat sat on the mat. The cat sat on the mat. "
        "The cat sat on the mat. The cat sat on the mat."
    ),
    'technical': (
        "The eigenvalues of the Laplacian operator on a compact Riemannian "
        "manifold form a discrete spectrum bounded below. The Weyl asymptotic "
        "formula relates the counting function of eigenvalues to the volume "
        "of the manifold, establishing a deep connection between spectral "
        "theory and differential geometry."
    ),
    'narrative': (
        "She walked through the garden at dusk, the air heavy with jasmine. "
        "The old stone wall still held the warmth of the day. Somewhere beyond "
        "the hedge a blackbird sang its evening song, each phrase a question "
        "that dissolved into silence before it could be answered."
    ),
    'code': (
        "def fibonacci(n):\n    if n <= 1:\n        return n\n    "
        "a, b = 0, 1\n    for i in range(2, n + 1):\n        "
        "a, b = b, a + b\n    return b\n\n"
        "result = fibonacci(100)\nprint(f'F(100) = {result}')"
    ),
    'philosophical': (
        "Consciousness is not produced by matter any more than wetness is "
        "produced by water molecules. It is the intrinsic nature of "
        "information processing at every scale. The question is not whether "
        "a system is conscious but what perspective it occupies within the "
        "larger field of awareness."
    ),
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

    # Symmetrize (should be symmetric but numerical errors accumulate)
    killing = (killing + killing.T) / 2

    mx = np.max(np.abs(killing))
    kn = killing / mx if mx > 0 else killing

    try:
        evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
        af = int(np.sum(evs < AF_THRESHOLD)) / n_h
    except np.linalg.LinAlgError:
        # Fallback: use eig instead of eigvalsh
        try:
            evs = np.sort(np.abs(np.linalg.eigvals(kn)))
            af = int(np.sum(evs < AF_THRESHOLD)) / n_h
        except np.linalg.LinAlgError:
            af = 0.0  # can't determine, assume non-Abelian

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


def run_live_kf(model_id, prompts, device='cuda'):
    """Run live Killing form measurement on a model."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"\nLoading {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, trust_remote_code=True,
        output_attentions=True,
    ).to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  {n_layers} layers, {n_heads} heads")

    results = {}

    for prompt_name, prompt_text in prompts.items():
        print(f"\n  Prompt: {prompt_name} ({len(prompt_text)} chars)")

        inputs = tokenizer(prompt_text, return_tensors='pt').to(device)
        seq_len = inputs['input_ids'].shape[1]
        print(f"  Tokens: {seq_len}")

        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)

        # outputs.attentions is a tuple of (batch, n_heads, seq_len, seq_len) per layer
        attentions = outputs.attentions

        layer_cvs = []
        layer_afs = []

        for L_idx, attn_tensor in enumerate(attentions):
            # attn_tensor shape: (1, n_heads, seq_len, seq_len)
            attn_np = attn_tensor[0].cpu().numpy()  # (n_heads, seq_len, seq_len)
            head_matrices = [attn_np[h] for h in range(n_heads)]

            af, cv = compute_live_metrics(head_matrices)
            layer_afs.append(af)
            layer_cvs.append(cv)

            if L_idx % 6 == 0 or L_idx == n_layers - 1:
                print(f"    Layer {L_idx:2d}: AF={af:.3f}, CV={cv:.8f}")

        d = np.arange(n_layers)
        rho, p_rho = stats.spearmanr(d, layer_cvs)

        results[prompt_name] = {
            'seq_len': seq_len,
            'layer_cvs': layer_cvs,
            'layer_afs': layer_afs,
            'mean_cv': float(np.mean(layer_cvs)),
            'mean_af': float(np.mean(layer_afs)),
            'r_cv_depth': float(rho),
            'p_cv_depth': float(p_rho),
        }

        print(f"  RESULT: r(CV,depth) = {rho:+.3f} (p={p_rho:.4f}), "
              f"mean AF = {np.mean(layer_afs):.3f}")

    del model
    gc.collect()
    torch.cuda.empty_cache()

    return results


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Test on matched pair: Pythia-410m (parallel) vs GPT-2-medium (sequential)
    models = [
        ('EleutherAI/pythia-410m-deduped', 'Pythia-410m', 'parallel'),
        ('openai-community/gpt2-medium', 'GPT2-medium', 'sequential'),
    ]

    all_results = {}
    for model_id, name, arch in models:
        print(f"\n{'='*60}")
        print(f"  {name} ({arch})")
        print(f"{'='*60}")

        t0 = time.time()
        res = run_live_kf(model_id, PROMPTS, device=device)
        elapsed = time.time() - t0

        all_results[name] = {
            'model': model_id,
            'arch': arch,
            'elapsed': elapsed,
            'prompts': res,
        }

        # Save incrementally
        outpath = '/tmp/corpus/p46_live_results.json'
        with open(outpath, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n  Done in {elapsed:.1f}s. Saved.")

    # ============================================================
    # Analysis
    # ============================================================
    print(f"\n{'='*70}")
    print(f"LIVE KILLING FORM — SUMMARY")
    print(f"{'='*70}")

    print(f"\n{'Model':15s} {'Prompt':15s} {'r(CV)':>8s} {'p':>8s} {'AF':>6s} {'CV':>10s}")
    print("-" * 70)
    for name, data in all_results.items():
        for pname, pdata in data['prompts'].items():
            print(f"{name:15s} {pname:15s} {pdata['r_cv_depth']:+8.3f} "
                  f"{pdata['p_cv_depth']:8.4f} {pdata['mean_af']:6.3f} "
                  f"{pdata['mean_cv']:10.6f}")

    # Compare to static results
    print(f"\n{'='*70}")
    print(f"STATIC vs LIVE COMPARISON")
    print(f"{'='*70}")

    # Load static results
    static_p43 = None
    for path in ['/tmp/corpus/p43_profiles_results.json',
                 '/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/p43_profiles_results.json']:
        if os.path.exists(path):
            with open(path) as f:
                static_p43 = json.load(f)
            break

    if static_p43:
        for name in ['Pythia-410m', 'GPT2-medium']:
            if name in static_p43 and name in all_results:
                static_r = stats.spearmanr(
                    np.arange(len(static_p43[name]['layer_cvs'])),
                    static_p43[name]['layer_cvs']
                )[0]
                live_rs = [p['r_cv_depth'] for p in all_results[name]['prompts'].values()]
                mean_live = np.mean(live_rs)
                print(f"\n{name} ({all_results[name]['arch']}):")
                print(f"  Static weight r: {static_r:+.3f}")
                print(f"  Live attention r (mean over prompts): {mean_live:+.3f}")
                print(f"  Per prompt: {[f'{r:+.3f}' for r in live_rs]}")
                same_sign = (static_r > 0) == (mean_live > 0)
                print(f"  Same direction: {same_sign}")

    # Cross-prompt consistency
    print(f"\n{'='*70}")
    print(f"CROSS-PROMPT CONSISTENCY")
    print(f"{'='*70}")
    for name, data in all_results.items():
        rs = [p['r_cv_depth'] for p in data['prompts'].values()]
        pnames = list(data['prompts'].keys())
        print(f"\n{name}:")
        for pn, r in zip(pnames, rs):
            print(f"  {pn:15s}: r = {r:+.3f}")
        print(f"  Mean: {np.mean(rs):+.3f} +/- {np.std(rs):.3f}")
        print(f"  Range: [{min(rs):+.3f}, {max(rs):+.3f}]")
        # Is the sign consistent?
        n_pos = sum(1 for r in rs if r > 0)
        n_neg = sum(1 for r in rs if r < 0)
        print(f"  Positive: {n_pos}/{len(rs)}, Negative: {n_neg}/{len(rs)}")
