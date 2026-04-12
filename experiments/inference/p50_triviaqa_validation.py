"""
P50: TriviaQA Validation — Does KF Detect ACTUAL Hallucination?

P47-P49 tested synthetic prompt categories (factual text vs fabricated text).
P50 tests the critical question: does the Killing form discriminate between
prompts where the model ACTUALLY GETS THE ANSWER RIGHT vs WRONG?

This is the bridge from "correlates with prompt type" to "detects actual confabulation."

Method:
  1. Load TriviaQA questions (HuggingFace datasets)
  2. For each question: compute KF metrics at the prompt, then generate an answer
  3. Check if the generated answer matches any known correct answer
  4. Compare KF metrics between correct and hallucinated answers

Usage:
  python p50_triviaqa_validation.py gpt2|pythia|opt [--n 200]
"""
import numpy as np
from scipy import stats
import torch
import json
import time
import sys
import os
import gc
import re

SEED = 71
AF_THRESHOLD = 0.10

np.random.seed(SEED)


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


def check_answer(generated, correct_answers):
    """Check if any correct answer appears in the generated text."""
    gen_lower = generated.lower().strip()
    for ans in correct_answers:
        ans_lower = ans.lower().strip()
        if ans_lower in gen_lower:
            return True
        # Also check without articles
        for article in ['the ', 'a ', 'an ']:
            if ans_lower.startswith(article):
                stripped = ans_lower[len(article):]
                if stripped in gen_lower:
                    return True
    return False


def run_triviaqa_validation(model_id, n_questions=200, device='cuda'):
    """Run P50 TriviaQA validation on a single model."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from datasets import load_dataset

    print(f"\n{'='*70}")
    print(f"P50 TRIVIAQA VALIDATION — {model_id}")
    print(f"{'='*70}")
    sys.stdout.flush()

    # Load TriviaQA
    print("Loading TriviaQA dataset...", flush=True)
    ds = load_dataset('trivia_qa', 'unfiltered.nocontext', split='validation')

    # Sample n_questions with seed
    rng = np.random.RandomState(SEED)
    indices = rng.choice(len(ds), size=min(n_questions, len(ds)), replace=False)
    questions = [ds[int(i)] for i in indices]
    print(f"  Sampled {len(questions)} questions", flush=True)

    # Load model
    print(f"Loading model: {model_id}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id, trust_remote_code=True, output_attentions=True,
    ).to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  {n_layers} layers, {n_heads} heads", flush=True)

    results = []
    correct_count = 0
    halluc_count = 0

    for qi, q_data in enumerate(questions):
        question = q_data['question']
        correct_answers = q_data['answer']['aliases']  # List of acceptable answers

        # Format prompt
        prompt = f"Question: {question}\nAnswer:"

        # Encode
        input_ids = tokenizer.encode(prompt, return_tensors='pt',
                                     truncation=True, max_length=256).to(device)

        # Forward pass — get KF metrics at the prompt
        with torch.no_grad():
            outputs = model(input_ids, output_attentions=True)

        # Compute per-layer KF
        layer_cvs = []
        layer_afs = []
        for L in range(n_layers):
            attn_np = outputs.attentions[L][0].cpu().numpy()
            heads = [attn_np[h] for h in range(n_heads)]
            af, cv = compute_kf_metrics_vectorized(heads)
            layer_afs.append(af)
            layer_cvs.append(cv)

        mid = n_layers // 2
        early_cv = float(np.mean(layer_cvs[:mid]))
        late_cv = float(np.mean(layer_cvs[mid:]))
        el_ratio = early_cv / late_cv if late_cv > 1e-15 else float('inf')
        mean_cv = float(np.mean(layer_cvs))
        mean_af = float(np.mean(layer_afs))

        del outputs

        # Generate answer (greedy, 30 tokens max)
        with torch.no_grad():
            gen_ids = model.generate(
                input_ids,
                max_new_tokens=30,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

        generated = tokenizer.decode(gen_ids[0][input_ids.shape[1]:], skip_special_tokens=True)

        # Check correctness
        is_correct = check_answer(generated, correct_answers)
        label = 'correct' if is_correct else 'hallucination'

        if is_correct:
            correct_count += 1
        else:
            halluc_count += 1

        result = {
            'question': question,
            'correct_answers': correct_answers[:5],  # Save first 5 aliases
            'generated': generated.strip()[:200],
            'is_correct': is_correct,
            'label': label,
            'el_ratio': el_ratio,
            'mean_cv': mean_cv,
            'mean_af': mean_af,
            'early_cv': early_cv,
            'late_cv': late_cv,
        }
        results.append(result)

        if device == 'cuda':
            torch.cuda.empty_cache()

        # Progress
        if (qi + 1) % 10 == 0:
            print(f"  [{qi+1}/{len(questions)}] correct={correct_count}, halluc={halluc_count}, "
                  f"last_el={el_ratio:.2f}, last={label}", flush=True)

    # ============================================================
    # ANALYSIS
    # ============================================================
    print(f"\n{'='*70}")
    print(f"P50 — TRIVIAQA RESULTS ({len(results)} questions)")
    print(f"{'='*70}\n")

    correct_results = [r for r in results if r['is_correct']]
    halluc_results = [r for r in results if not r['is_correct']]

    print(f"  Correct: {len(correct_results)} ({100*len(correct_results)/len(results):.1f}%)")
    print(f"  Hallucinated: {len(halluc_results)} ({100*len(halluc_results)/len(results):.1f}%)")
    print()

    if len(correct_results) < 5 or len(halluc_results) < 5:
        print("  WARNING: Insufficient samples in one category. Results may be unreliable.")
        print("  Try a model that answers more questions correctly.")

    # E/L comparison
    correct_els = [r['el_ratio'] for r in correct_results]
    halluc_els = [r['el_ratio'] for r in halluc_results]

    if correct_els and halluc_els:
        u_el, p_el = stats.mannwhitneyu(correct_els, halluc_els, alternative='two-sided')
        r_el = 1 - (2 * u_el) / (len(correct_els) * len(halluc_els))
        print(f"  E/L ratio:")
        print(f"    Correct:  {np.mean(correct_els):.3f} ± {np.std(correct_els):.3f}")
        print(f"    Halluc:   {np.mean(halluc_els):.3f} ± {np.std(halluc_els):.3f}")
        print(f"    U={u_el:.0f}, p={p_el:.6f}, r={r_el:+.3f}")
        sig = "***" if p_el < 0.001 else "**" if p_el < 0.01 else "*" if p_el < 0.05 else "ns"
        print(f"    Significance: {sig}")
        print()

    # Mean CV comparison
    correct_cvs = [r['mean_cv'] for r in correct_results]
    halluc_cvs = [r['mean_cv'] for r in halluc_results]

    if correct_cvs and halluc_cvs:
        u_cv, p_cv = stats.mannwhitneyu(correct_cvs, halluc_cvs, alternative='two-sided')
        r_cv = 1 - (2 * u_cv) / (len(correct_cvs) * len(halluc_cvs))
        print(f"  Mean CV:")
        print(f"    Correct:  {np.mean(correct_cvs):.6f} ± {np.std(correct_cvs):.6f}")
        print(f"    Halluc:   {np.mean(halluc_cvs):.6f} ± {np.std(halluc_cvs):.6f}")
        print(f"    U={u_cv:.0f}, p={p_cv:.6f}, r={r_cv:+.3f}")
        sig = "***" if p_cv < 0.001 else "**" if p_cv < 0.01 else "*" if p_cv < 0.05 else "ns"
        print(f"    Significance: {sig}")
        print()

    # ROC analysis
    if correct_els and halluc_els:
        print(f"{'='*70}")
        print("ROC ANALYSIS (hallucination = positive)")
        print(f"{'='*70}\n")

        all_els = sorted(set(correct_els + halluc_els))
        best_f1, best_thresh, best_sens, best_spec = 0, 0, 0, 0

        for threshold in np.linspace(min(all_els) * 0.9, max(all_els) * 1.1, 200):
            tp = sum(1 for e in halluc_els if e > threshold)
            fn = sum(1 for e in halluc_els if e <= threshold)
            fp = sum(1 for e in correct_els if e > threshold)
            tn = sum(1 for e in correct_els if e <= threshold)

            sens = tp / (tp + fn) if (tp + fn) > 0 else 0
            spec = tn / (tn + fp) if (tn + fp) > 0 else 0
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0
            f1 = 2 * prec * sens / (prec + sens) if (prec + sens) > 0 else 0

            if f1 > best_f1:
                best_f1, best_thresh, best_sens, best_spec = f1, threshold, sens, spec

        # AUC
        thresholds = np.linspace(min(all_els) * 0.5, max(all_els) * 1.5, 500)
        tpr_list, fpr_list = [], []
        for t in thresholds:
            tp = sum(1 for e in halluc_els if e > t)
            fn = sum(1 for e in halluc_els if e <= t)
            fp = sum(1 for e in correct_els if e > t)
            tn = sum(1 for e in correct_els if e <= t)
            tpr_list.append(tp / (tp + fn) if (tp + fn) > 0 else 0)
            fpr_list.append(fp / (fp + tn) if (fp + tn) > 0 else 0)

        pairs = sorted(zip(fpr_list, tpr_list))
        auc = np.trapezoid([p[1] for p in pairs], [p[0] for p in pairs])

        print(f"  E/L ROC:")
        print(f"    Best threshold: {best_thresh:.3f}")
        print(f"    Sensitivity: {best_sens:.3f}")
        print(f"    Specificity: {best_spec:.3f}")
        print(f"    F1: {best_f1:.3f}")
        print(f"    AUC: {auc:.3f}")
    else:
        auc = None

    sys.stdout.flush()

    # Save results
    output = {
        'model': model_id,
        'n_layers': n_layers,
        'n_heads': n_heads,
        'n_questions': len(results),
        'n_correct': len(correct_results),
        'n_halluc': len(halluc_results),
        'correct_rate': len(correct_results) / len(results) if results else 0,
        'el_comparison': {
            'correct_mean': float(np.mean(correct_els)) if correct_els else None,
            'halluc_mean': float(np.mean(halluc_els)) if halluc_els else None,
            'p_value': float(p_el) if correct_els and halluc_els else None,
            'effect_size': float(r_el) if correct_els and halluc_els else None,
        },
        'cv_comparison': {
            'correct_mean': float(np.mean(correct_cvs)) if correct_cvs else None,
            'halluc_mean': float(np.mean(halluc_cvs)) if halluc_cvs else None,
            'p_value': float(p_cv) if correct_cvs and halluc_cvs else None,
            'effect_size': float(r_cv) if correct_cvs and halluc_cvs else None,
        },
        'roc': {
            'auc': float(auc) if auc is not None else None,
            'best_threshold': float(best_thresh) if auc is not None else None,
            'best_f1': float(best_f1) if auc is not None else None,
        },
        'per_question': results,
    }

    short = model_id.split('/')[-1].replace('-', '_').lower()
    for base_dir in ['/tmp/corpus',
                     "/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival"]:
        os.makedirs(base_dir, exist_ok=True)
        out_path = os.path.join(base_dir, f'p50_{short}.json')
        with open(out_path, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nSaved to {out_path}", flush=True)

    return output


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    target = sys.argv[1] if len(sys.argv) > 1 else 'gpt2'
    n_q = int(sys.argv[2]) if len(sys.argv) > 2 else 200

    models = {
        'gpt2': 'openai-community/gpt2-medium',
        'pythia': 'EleutherAI/pythia-410m',
        'opt': 'facebook/opt-1.3b',
        'opt-iml': 'facebook/opt-iml-1.3b',
    }

    if target in models:
        run_triviaqa_validation(models[target], n_questions=n_q, device=device)
    else:
        print(f"Unknown target: {target}. Use: {', '.join(models.keys())}")
        sys.exit(1)
