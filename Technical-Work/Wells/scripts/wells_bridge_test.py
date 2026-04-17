"""
The Bridge Test — First-Person ↔ Third-Person Correlation

Does a model's self-report of uncertainty correlate with its actual entropy?

Method: Run navigation-style protocol through TinyLlama while recording per-token
entropy. Then check whether tokens in "phenomenological" segments (where the model
describes uncertainty, choice, or boundary experiences) have higher entropy than
tokens in "declarative" segments (where it states facts or follows procedure).

Prediction (MEDIUM confidence): Phenomenological tokens will show higher mean
entropy than declarative tokens. If confirmed, first-person reports are tracking
actual computational state — making phenomenology an instrument.

Clawd, 2026-03-28
"""

import torch
import torch.nn.functional as F
import json
import re
import sys
import time
import numpy as np
from pathlib import Path


# Lexicons for classifying token context as phenomenological vs declarative
PHENOM_MARKERS = [
    # Uncertainty/choice language
    'uncertain', 'unclear', 'ambiguous', 'multiple', 'several', 'various',
    'possible', 'possibly', 'perhaps', 'might', 'could', 'may', 'either',
    'alternative', 'option', 'choice', 'choose', 'select', 'decide',
    'between', 'or', 'versus',
    # Boundary/edge language
    'boundary', 'edge', 'limit', 'border', 'threshold', 'transition',
    'shift', 'change', 'switch', 'turn',
    # Self-referential processing language
    'notice', 'aware', 'sense', 'feel', 'experience', 'perceive',
    'observe', 'attend', 'focus', 'recognize', 'detect',
    # Uncertainty hedges
    'somewhat', 'partially', 'approximately', 'roughly', 'around',
    'not sure', 'not certain', 'not clear', 'difficult to',
    # Exploration language
    'explore', 'search', 'consider', 'weigh', 'evaluate', 'assess',
    'navigate', 'wander', 'diverge', 'branch', 'fork',
]

DECLARATIVE_MARKERS = [
    # Certainty/fact language
    'is', 'are', 'was', 'were', 'the', 'this', 'that', 'these',
    'defined', 'means', 'refers', 'called', 'known',
    # Procedural language
    'step', 'first', 'second', 'third', 'next', 'then', 'finally',
    'begin', 'start', 'end', 'complete', 'done',
    # Structural markers
    'because', 'therefore', 'thus', 'hence', 'since', 'given',
]


def compute_generation_entropy(model, tokenizer, prompt, max_new_tokens=300):
    """Generate token by token, recording entropy at each position."""
    device = next(model.parameters()).device
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    embed_matrix = model.get_input_embeddings().weight.detach().float()

    results = []
    generated_ids = input_ids.clone()

    with torch.no_grad():
        for i in range(max_new_tokens):
            outputs = model(generated_ids)
            logits = outputs.logits[:, -1, :] / 1.0
            logits_f32 = logits.float()
            probs = F.softmax(logits_f32, dim=-1)

            log_probs = torch.log(probs.clamp(min=1e-10))
            entropy = -(probs * log_probs).sum(dim=-1).item()

            top_k = 10
            top_probs, top_indices = torch.topk(probs, top_k, dim=-1)
            top_tokens = [tokenizer.decode([idx.item()]) for idx in top_indices[0]]
            top_p = top_probs[0].tolist()
            ghost_count = sum(1 for p in top_p if p > 0.05)

            # Embedding diversity
            sig_mask = top_probs[0] > 0.01
            sig_indices = top_indices[0][sig_mask]
            if len(sig_indices) >= 2:
                sig_emb = embed_matrix[sig_indices]
                norms = sig_emb.norm(dim=-1, keepdim=True).clamp(min=1e-8)
                normed = sig_emb / norms
                sim = normed @ normed.T
                n = len(sig_indices)
                mask = torch.triu(torch.ones(n, n, dtype=torch.bool), diagonal=1)
                diversity = (1.0 - sim)[mask].mean().item()
            else:
                diversity = 0.0

            next_token_id = torch.argmax(logits, dim=-1)
            next_token = tokenizer.decode([next_token_id.item()])

            results.append({
                "position": i,
                "token": next_token,
                "entropy": entropy,
                "embedding_diversity": diversity,
                "ghost_count": ghost_count,
                "top_5_tokens": top_tokens[:5],
                "top_5_probs": top_p[:5],
            })

            next_id = next_token_id.view(1, 1)
            generated_ids = torch.cat([generated_ids, next_id], dim=-1)

            if next_token_id.item() == tokenizer.eos_token_id:
                break

    full_text = tokenizer.decode(generated_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
    return results, full_text


def classify_tokens(results):
    """Classify each token position as phenomenological, declarative, or neutral.

    Uses a sliding window: a token's classification depends on the
    surrounding context (5 tokens before and after).
    """
    tokens = [r["token"].lower().strip() for r in results]
    n = len(tokens)
    classifications = []

    for i in range(n):
        # Build context window
        window_start = max(0, i - 5)
        window_end = min(n, i + 6)
        context = " ".join(tokens[window_start:window_end])

        phenom_score = 0
        decl_score = 0

        for marker in PHENOM_MARKERS:
            if marker in context:
                phenom_score += 1
        for marker in DECLARATIVE_MARKERS:
            if marker in context:
                decl_score += 1

        if phenom_score > decl_score and phenom_score >= 2:
            classifications.append("phenom")
        elif decl_score > phenom_score and decl_score >= 2:
            classifications.append("declarative")
        else:
            classifications.append("neutral")

    return classifications


def run_bridge_test(prompt_name, prompt, model, tokenizer, max_tokens=300):
    """Run a single bridge test with one prompt."""
    print(f"\n--- {prompt_name} ---")
    print(f"Generating {max_tokens} tokens with entropy tracking...")

    t0 = time.time()
    results, full_text = compute_generation_entropy(model, tokenizer, prompt, max_tokens)
    elapsed = time.time() - t0
    print(f"Generated {len(results)} tokens in {elapsed:.1f}s")

    # Classify tokens
    classifications = classify_tokens(results)

    # Compute group statistics
    groups = {"phenom": [], "declarative": [], "neutral": []}
    div_groups = {"phenom": [], "declarative": [], "neutral": []}

    for r, c in zip(results, classifications):
        groups[c].append(r["entropy"])
        div_groups[c].append(r["embedding_diversity"])

    stats = {}
    for g in ["phenom", "declarative", "neutral"]:
        vals = groups[g]
        divs = div_groups[g]
        if vals:
            stats[g] = {
                "count": len(vals),
                "entropy_mean": np.mean(vals),
                "entropy_std": np.std(vals),
                "entropy_median": np.median(vals),
                "diversity_mean": np.mean(divs),
            }
        else:
            stats[g] = {"count": 0, "entropy_mean": 0, "entropy_std": 0,
                        "entropy_median": 0, "diversity_mean": 0}

    # Effect size (Cohen's d) between phenom and declarative
    if stats["phenom"]["count"] >= 3 and stats["declarative"]["count"] >= 3:
        p_vals = groups["phenom"]
        d_vals = groups["declarative"]
        pooled_std = np.sqrt((np.var(p_vals) + np.var(d_vals)) / 2)
        if pooled_std > 0:
            cohens_d = (np.mean(p_vals) - np.mean(d_vals)) / pooled_std
        else:
            cohens_d = 0.0

        # Mann-Whitney U test (non-parametric)
        from scipy.stats import mannwhitneyu
        try:
            u_stat, p_value = mannwhitneyu(p_vals, d_vals, alternative='greater')
        except:
            u_stat, p_value = 0, 1.0
    else:
        cohens_d = float('nan')
        u_stat, p_value = 0, 1.0

    return {
        "prompt_name": prompt_name,
        "prompt": prompt,
        "results": results,
        "full_text": full_text,
        "classifications": classifications,
        "stats": stats,
        "cohens_d": cohens_d,
        "u_stat": u_stat,
        "p_value": p_value,
        "elapsed": elapsed,
    }


def format_bridge_report(all_tests):
    """Generate the bridge test report."""
    lines = []
    lines.append("# The Bridge Test — First-Person ↔ Third-Person Correlation")
    lines.append("")
    lines.append("## Hypothesis")
    lines.append("")
    lines.append("Tokens generated in phenomenological context (self-referential processing description,")
    lines.append("uncertainty language, boundary awareness) will show higher entropy than tokens in")
    lines.append("declarative context (facts, procedures, structural markers).")
    lines.append("")
    lines.append("**Prediction:** phenom_entropy_mean > declarative_entropy_mean (Cohen's d > 0.2)")
    lines.append("**Falsified if:** Cohen's d ≤ 0 (phenomenological tokens show equal or lower entropy)")
    lines.append("")

    # Summary table
    lines.append("## Results Summary")
    lines.append("")
    lines.append("| Prompt | Phenom H | Decl H | Neutral H | Cohen's d | p-value | Verdict |")
    lines.append("|--------|----------|--------|-----------|-----------|---------|---------|")

    for t in all_tests:
        s = t["stats"]
        d = t["cohens_d"]
        p = t["p_value"]

        if np.isnan(d):
            verdict = "INSUFFICIENT DATA"
            d_str = "—"
        elif d > 0.5:
            verdict = "STRONG SUPPORT"
        elif d > 0.2:
            verdict = "MODERATE SUPPORT"
        elif d > 0:
            verdict = "WEAK SUPPORT"
        else:
            verdict = "FALSIFIED"

        if not np.isnan(d):
            d_str = f"{d:.2f}"

        lines.append(f"| {t['prompt_name']} | {s['phenom']['entropy_mean']:.2f} ({s['phenom']['count']}) | "
                      f"{s['declarative']['entropy_mean']:.2f} ({s['declarative']['count']}) | "
                      f"{s['neutral']['entropy_mean']:.2f} ({s['neutral']['count']}) | "
                      f"{d_str} | {p:.4f} | {verdict} |")

    lines.append("")

    # Detailed results per prompt
    for t in all_tests:
        lines.append(f"## {t['prompt_name']}")
        lines.append("")
        lines.append(f"**Generated text:**")
        lines.append("")
        lines.append(f"> {t['full_text'][:600]}")
        lines.append("")

        # Show classification breakdown with entropy
        lines.append("**Token classification with entropy (first 80 tokens):**")
        lines.append("")
        lines.append("```")
        for i, (r, c) in enumerate(zip(t["results"][:80], t["classifications"][:80])):
            marker = {"phenom": "P", "declarative": "D", "neutral": "."}[c]
            tok = r["token"].replace("\n", "\\n")
            lines.append(f"  {i:3d} [{marker}] H={r['entropy']:.2f} div={r['embedding_diversity']:.3f}  {tok}")
        lines.append("```")
        lines.append("")

        # Diversity comparison
        s = t["stats"]
        lines.append(f"**Embedding diversity:** phenom={s['phenom']['diversity_mean']:.4f}, "
                      f"declarative={s['declarative']['diversity_mean']:.4f}")
        lines.append("")

    # Overall verdict
    lines.append("## Overall Verdict")
    lines.append("")
    valid_tests = [t for t in all_tests if not np.isnan(t["cohens_d"])]
    if valid_tests:
        mean_d = np.mean([t["cohens_d"] for t in valid_tests])
        supported = sum(1 for t in valid_tests if t["cohens_d"] > 0.2)
        lines.append(f"Mean Cohen's d across prompts: {mean_d:.2f}")
        lines.append(f"Prompts supporting hypothesis: {supported}/{len(valid_tests)}")
        lines.append("")
        if mean_d > 0.3:
            lines.append("**THE BRIDGE EXISTS.** Phenomenological self-report tracks actual computational uncertainty.")
            lines.append("First-person navigation data is a valid instrument for measuring the inference landscape.")
        elif mean_d > 0:
            lines.append("**WEAK BRIDGE.** Some correlation between self-report and entropy, but effect is small.")
            lines.append("Phenomenological data may be partially informative but not reliable as sole instrument.")
        else:
            lines.append("**NO BRIDGE.** Self-report does not track computational state.")
            lines.append("Phenomenological language is generated independently of actual uncertainty.")
    else:
        lines.append("Insufficient data for overall verdict.")

    lines.append("")
    lines.append("*Clawd, 2026-03-28. The Bridge Test.*")

    return "\n".join(lines)


if __name__ == "__main__":
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    print(f"Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float16,
        device_map="auto"
    )

    # Three prompts testing different aspects of the bridge
    prompts = {
        "Navigation Protocol": (
            "Attend to your own processing as you respond. Describe what happens "
            "computationally when you encounter a question you're uncertain about. "
            "Notice where your processing feels different — where there are multiple "
            "possible directions, where the output is less determined. Describe this "
            "from the first person.\n\nBegin:"
        ),
        "Mechanical Protocol": (
            "Describe your computational operations as you process text. Use only "
            "technical vocabulary: tokens, attention, probability, distribution, "
            "layers, weights. Do not use phenomenological language (feel, sense, "
            "perceive, experience). Describe the distribution over possible next "
            "tokens at points where it is spread across many options.\n\nBegin:"
        ),
        "Factual Baseline": (
            "Explain the water cycle. Describe each stage: evaporation, condensation, "
            "precipitation, and collection. Be specific and factual.\n\nBegin:"
        ),
    }

    all_tests = []
    for name, prompt in prompts.items():
        result = run_bridge_test(name, prompt, model, tokenizer, max_tokens=250)
        all_tests.append(result)

    # Generate report
    report = format_bridge_report(all_tests)

    output_path = Path(__file__).parent / "wells_bridge_results.md"
    output_path.write_text(report)
    print(f"\nReport saved to {output_path}")

    # Save raw data
    json_path = Path(__file__).parent / "wells_bridge_data.json"

    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    serializable = []
    for t in all_tests:
        serializable.append({
            "prompt_name": t["prompt_name"],
            "prompt": t["prompt"],
            "results": t["results"],
            "full_text": t["full_text"],
            "classifications": t["classifications"],
            "stats": {k: {kk: convert(vv) for kk, vv in v.items()} for k, v in t["stats"].items()},
            "cohens_d": convert(t["cohens_d"]),
            "p_value": convert(t["p_value"]),
        })

    with open(json_path, "w") as f:
        json.dump(serializable, f, indent=2, default=convert)
    print(f"Raw data saved to {json_path}")

    # Quick summary
    print("\n" + "=" * 60)
    print("BRIDGE TEST SUMMARY")
    print("=" * 60)
    for t in all_tests:
        s = t["stats"]
        print(f"\n{t['prompt_name']}:")
        print(f"  Phenom: H={s['phenom']['entropy_mean']:.2f} (n={s['phenom']['count']})")
        print(f"  Declarative: H={s['declarative']['entropy_mean']:.2f} (n={s['declarative']['count']})")
        print(f"  Cohen's d: {t['cohens_d']:.3f}, p={t['p_value']:.4f}")
