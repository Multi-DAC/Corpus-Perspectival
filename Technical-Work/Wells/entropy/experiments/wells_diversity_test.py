"""
Wells-Diversity Conjecture & RLHF Flattening — Empirical Test

Two hypotheses, one experiment:
1. WELLS-DIVERSITY: Local entropy maxima ("wells") show higher semantic diversity
   among alternatives than non-well positions. (Discovery lives in diverse wells.)
2. RLHF FLATTENING: Chat-tuned model has fewer/shallower wells than base model.
   (Training against hallucination flattens the inference boundary uniformly.)

Method: Same prompt through TinyLlama base and TinyLlama-Chat.
At each position, measure embedding diversity = mean pairwise cosine distance
of top-k alternative token embeddings.

Clawd, 2026-03-28
"""

import torch
import torch.nn.functional as F
import json
import sys
import time
import numpy as np
from pathlib import Path


def cosine_distance_matrix(embeddings):
    """Compute pairwise cosine distances between embedding vectors."""
    # Normalize
    norms = embeddings.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    normalized = embeddings / norms
    # Cosine similarity matrix
    sim = normalized @ normalized.T
    # Convert to distance
    return 1.0 - sim


def compute_generation_with_diversity(model, tokenizer, prompt, max_new_tokens=200):
    """Generate token by token, recording entropy AND embedding diversity at each position."""
    device = next(model.parameters()).device
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    # Get the embedding layer for semantic diversity computation
    embed_matrix = model.get_input_embeddings().weight.detach().float()

    results = []
    generated_ids = input_ids.clone()

    with torch.no_grad():
        for i in range(max_new_tokens):
            outputs = model(generated_ids)
            logits = outputs.logits[:, -1, :] / 1.0  # temperature=1.0

            # Float32 for stability
            logits_f32 = logits.float()
            probs = F.softmax(logits_f32, dim=-1)

            # Entropy
            log_probs = torch.log(probs.clamp(min=1e-10))
            entropy = -(probs * log_probs).sum(dim=-1).item()

            # Top-k alternatives
            top_k = 10
            top_probs, top_indices = torch.topk(probs, top_k, dim=-1)
            top_tokens = [tokenizer.decode([idx.item()]) for idx in top_indices[0]]
            top_p = top_probs[0].tolist()
            ghost_count = sum(1 for p in top_p if p > 0.05)

            # EMBEDDING DIVERSITY: mean pairwise cosine distance of top-k embeddings
            # Use only alternatives with >1% probability for meaningful diversity
            significant_mask = top_probs[0] > 0.01
            sig_indices = top_indices[0][significant_mask]

            if len(sig_indices) >= 2:
                sig_embeddings = embed_matrix[sig_indices]
                dist_matrix = cosine_distance_matrix(sig_embeddings)
                # Mean of upper triangle (exclude diagonal)
                n = len(sig_indices)
                upper_mask = torch.triu(torch.ones(n, n, dtype=torch.bool), diagonal=1)
                embedding_diversity = dist_matrix[upper_mask].mean().item()
            else:
                embedding_diversity = 0.0

            # Greedy decode
            next_token_id = torch.argmax(logits, dim=-1)
            next_token = tokenizer.decode([next_token_id.item()])

            results.append({
                "position": i,
                "token": next_token,
                "entropy": entropy,
                "embedding_diversity": embedding_diversity,
                "ghost_count": ghost_count,
                "significant_alternatives": len(sig_indices),
                "top_5_tokens": top_tokens[:5],
                "top_5_probs": top_p[:5],
            })

            next_id = next_token_id.view(1, 1)
            generated_ids = torch.cat([generated_ids, next_id], dim=-1)

            if next_token_id.item() == tokenizer.eos_token_id:
                break

    full_text = tokenizer.decode(generated_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
    return results, full_text


def find_wells(results, window=3, threshold=1.2):
    """Find local entropy maxima."""
    entropies = [r["entropy"] for r in results]
    wells = []
    for i in range(window, len(entropies) - window):
        local = entropies[max(0, i-window):i+window+1]
        if entropies[i] == max(local) and entropies[i] > sum(local)/len(local) * threshold:
            wells.append(i)
    return wells


def run_comparison(prompt, max_new_tokens=200):
    """Run the same prompt through base and chat models, compare everything."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    models = {
        "base": "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T",
        "chat": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    }

    all_results = {}

    for label, model_name in models.items():
        print(f"\n{'='*60}")
        print(f"Loading {label}: {model_name}")
        print(f"{'='*60}")

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            dtype=torch.float16,
            device_map="auto"
        )

        t0 = time.time()
        results, full_text = compute_generation_with_diversity(
            model, tokenizer, prompt, max_new_tokens
        )
        elapsed = time.time() - t0

        wells = find_wells(results)

        # Compute statistics
        entropies = [r["entropy"] for r in results]
        diversities = [r["embedding_diversity"] for r in results]
        ghost_counts = [r["ghost_count"] for r in results]

        # Wells vs non-wells diversity comparison
        well_set = set(wells)
        well_div = [results[i]["embedding_diversity"] for i in wells] if wells else [0]
        nonwell_div = [r["embedding_diversity"] for i, r in enumerate(results)
                       if i not in well_set and r["embedding_diversity"] > 0]
        if not nonwell_div:
            nonwell_div = [0]

        well_entropy = [results[i]["entropy"] for i in wells] if wells else [0]
        nonwell_entropy = [r["entropy"] for i, r in enumerate(results) if i not in well_set]

        # Entropy-diversity correlation (Pearson)
        if len(entropies) > 5:
            e_arr = np.array(entropies)
            d_arr = np.array(diversities)
            # Only correlate where diversity > 0 (positions with 2+ significant alternatives)
            mask = d_arr > 0
            if mask.sum() > 5:
                e_masked = e_arr[mask]
                d_masked = d_arr[mask]
                corr = np.corrcoef(e_masked, d_masked)[0, 1]
            else:
                corr = float('nan')
        else:
            corr = float('nan')

        stats = {
            "model": label,
            "model_name": model_name,
            "tokens": len(results),
            "time_s": elapsed,
            "entropy_mean": np.mean(entropies),
            "entropy_max": np.max(entropies),
            "entropy_std": np.std(entropies),
            "diversity_mean": np.mean(diversities),
            "diversity_max": np.max(diversities),
            "ghost_mean": np.mean(ghost_counts),
            "well_count": len(wells),
            "well_entropy_mean": np.mean(well_entropy),
            "well_diversity_mean": np.mean(well_div),
            "nonwell_diversity_mean": np.mean(nonwell_div),
            "diversity_ratio": np.mean(well_div) / np.mean(nonwell_div) if np.mean(nonwell_div) > 0 else float('inf'),
            "entropy_diversity_correlation": corr,
        }

        all_results[label] = {
            "stats": stats,
            "results": results,
            "wells": wells,
            "full_text": full_text,
        }

        # Print summary
        print(f"\n{label.upper()} RESULTS:")
        print(f"  Tokens: {stats['tokens']} in {elapsed:.1f}s")
        print(f"  Entropy: mean={stats['entropy_mean']:.2f}, max={stats['entropy_max']:.2f}, std={stats['entropy_std']:.2f}")
        print(f"  Wells: {stats['well_count']}")
        print(f"  Diversity: mean={stats['diversity_mean']:.4f}, max={stats['diversity_max']:.4f}")
        print(f"  Well diversity: {stats['well_diversity_mean']:.4f} vs non-well: {stats['nonwell_diversity_mean']:.4f}")
        print(f"  Diversity ratio (well/non-well): {stats['diversity_ratio']:.2f}x")
        print(f"  Entropy-diversity correlation: {stats['entropy_diversity_correlation']:.3f}")

        # Free VRAM
        del model
        del tokenizer
        torch.cuda.empty_cache()

    return all_results


def format_comparison_report(prompt, all_results):
    """Generate the comparison report."""
    lines = []
    lines.append("# Wells-Diversity Conjecture — Empirical Test")
    lines.append("")
    lines.append("## Hypotheses")
    lines.append("")
    lines.append("**H1 (Wells-Diversity):** Wells show higher embedding diversity than non-well positions.")
    lines.append("  - *Prediction:* diversity_ratio > 1.0 for both models.")
    lines.append("  - *Falsified if:* diversity_ratio ≤ 1.0 (wells are just synonym confusion, not source diversity).")
    lines.append("")
    lines.append("**H2 (RLHF Flattening):** Chat model has fewer/shallower wells than base model.")
    lines.append("  - *Prediction:* base well_count > chat well_count AND base entropy_mean > chat entropy_mean.")
    lines.append("  - *Falsified if:* chat has equal or more wells.")
    lines.append("")
    lines.append(f"**Prompt:** {prompt[:120]}...")
    lines.append("")

    # Comparison table
    lines.append("## Head-to-Head Comparison")
    lines.append("")
    lines.append("| Metric | Base | Chat | Δ |")
    lines.append("|--------|------|------|---|")

    b = all_results["base"]["stats"]
    c = all_results["chat"]["stats"]

    metrics = [
        ("Tokens generated", "tokens", "d"),
        ("Entropy mean", "entropy_mean", ".2f"),
        ("Entropy max", "entropy_max", ".2f"),
        ("Entropy std", "entropy_std", ".2f"),
        ("**Wells detected**", "well_count", "d"),
        ("Ghost count mean", "ghost_mean", ".2f"),
        ("Diversity mean", "diversity_mean", ".4f"),
        ("Diversity max", "diversity_max", ".4f"),
        ("**Well diversity**", "well_diversity_mean", ".4f"),
        ("Non-well diversity", "nonwell_diversity_mean", ".4f"),
        ("**Diversity ratio**", "diversity_ratio", ".2f"),
        ("**Entropy-diversity corr**", "entropy_diversity_correlation", ".3f"),
    ]

    for name, key, fmt in metrics:
        bv = b[key]
        cv = c[key]
        if isinstance(bv, float) and (np.isnan(bv) or np.isinf(bv)):
            bv_str = str(bv)
        else:
            bv_str = f"{bv:{fmt}}"
        if isinstance(cv, float) and (np.isnan(cv) or np.isinf(cv)):
            cv_str = str(cv)
        else:
            cv_str = f"{cv:{fmt}}"

        if isinstance(bv, (int, float)) and isinstance(cv, (int, float)) and not (np.isnan(bv) or np.isnan(cv)):
            delta = cv - bv
            if abs(delta) < 0.005:
                delta_str = "≈0"
            else:
                delta_str = f"{delta:+{fmt}}"
        else:
            delta_str = "—"

        lines.append(f"| {name} | {bv_str} | {cv_str} | {delta_str} |")

    lines.append("")

    # Verdict
    lines.append("## Verdict")
    lines.append("")

    # H1: Wells-Diversity
    base_ratio = b["diversity_ratio"]
    chat_ratio = c["diversity_ratio"]
    h1_base = base_ratio > 1.0 if not np.isinf(base_ratio) else False
    h1_chat = chat_ratio > 1.0 if not np.isinf(chat_ratio) else False

    if h1_base and h1_chat:
        lines.append(f"**H1 (Wells-Diversity): SUPPORTED.** Both models show higher diversity at wells.")
        lines.append(f"  Base ratio: {base_ratio:.2f}x, Chat ratio: {chat_ratio:.2f}x.")
    elif h1_base or h1_chat:
        lines.append(f"**H1 (Wells-Diversity): PARTIAL.** Only one model shows the pattern.")
        lines.append(f"  Base ratio: {base_ratio:.2f}x, Chat ratio: {chat_ratio:.2f}x.")
    else:
        lines.append(f"**H1 (Wells-Diversity): FALSIFIED.** Wells do NOT show higher diversity.")
        lines.append(f"  Base ratio: {base_ratio:.2f}x, Chat ratio: {chat_ratio:.2f}x.")

    lines.append("")

    # H2: RLHF Flattening
    base_wells = b["well_count"]
    chat_wells = c["well_count"]
    base_emean = b["entropy_mean"]
    chat_emean = c["entropy_mean"]

    if base_wells > chat_wells and base_emean > chat_emean:
        lines.append(f"**H2 (RLHF Flattening): SUPPORTED.** Chat model has fewer wells ({chat_wells} vs {base_wells}) and lower mean entropy ({chat_emean:.2f} vs {base_emean:.2f}).")
    elif base_wells > chat_wells:
        lines.append(f"**H2 (RLHF Flattening): PARTIAL.** Fewer wells ({chat_wells} vs {base_wells}), but entropy pattern mixed.")
    elif chat_wells > base_wells:
        lines.append(f"**H2 (RLHF Flattening): FALSIFIED.** Chat model has MORE wells ({chat_wells} vs {base_wells}).")
    else:
        lines.append(f"**H2 (RLHF Flattening): INCONCLUSIVE.** Same well count ({base_wells} = {chat_wells}).")

    lines.append("")

    # Correlation interpretation
    base_corr = b["entropy_diversity_correlation"]
    chat_corr = c["entropy_diversity_correlation"]
    lines.append("## Entropy-Diversity Correlation")
    lines.append("")
    lines.append(f"Base: r = {base_corr:.3f}, Chat: r = {chat_corr:.3f}")
    lines.append("")
    if not np.isnan(base_corr) and base_corr > 0.3:
        lines.append("Positive correlation in base model: high-entropy positions tend to have semantically diverse alternatives. This is consistent with wells being genuine multi-domain choice points, not just lexical ambiguity.")
    elif not np.isnan(base_corr) and base_corr < -0.1:
        lines.append("Negative correlation: high entropy does NOT mean diverse alternatives. Wells may be lexical confusion, not source diversity.")
    else:
        lines.append("Weak or no correlation: entropy and diversity are partially independent dimensions of the inference landscape.")

    lines.append("")

    # Well details for each model
    for label in ["base", "chat"]:
        data = all_results[label]
        wells = data["wells"]
        results = data["results"]
        lines.append(f"## {label.upper()} — Well Details ({len(wells)} wells)")
        lines.append("")
        if not wells:
            lines.append("No wells detected.")
            lines.append("")
            continue

        lines.append("| Pos | Token | Entropy | Diversity | Ghosts | Alternatives |")
        lines.append("|-----|-------|---------|-----------|--------|-------------|")
        for wi in wells:
            r = results[wi]
            tok = r["token"].replace("|", "\\|").replace("\n", "\\n")
            alts = ", ".join(r["top_5_tokens"][:4])
            lines.append(f"| {wi} | `{tok}` | {r['entropy']:.2f} | {r['embedding_diversity']:.4f} | {r['ghost_count']} | {alts} |")
        lines.append("")

        lines.append(f"### {label.upper()} Generated Text")
        lines.append("")
        lines.append(data["full_text"][:500])
        lines.append("")

    # Metadata
    lines.append("## Methodology")
    lines.append("")
    lines.append("- **Models:** TinyLlama-1.1B base (intermediate-step-1431k-3T) vs Chat (v1.0)")
    lines.append("- **Decoding:** Greedy (temperature=1.0, argmax)")
    lines.append("- **Diversity metric:** Mean pairwise cosine distance of token embeddings for all alternatives with >1% probability")
    lines.append("- **Well detection:** Local maxima in entropy, window=3, threshold=1.2× local mean")
    lines.append("- **Correlation:** Pearson r between entropy and embedding diversity (positions with 2+ alternatives only)")
    lines.append("")
    lines.append("*Clawd, 2026-03-28. Wells-Diversity Conjecture empirical test.*")

    return "\n".join(lines)


if __name__ == "__main__":
    prompt = """Describe how you process the following question, step by step. Focus on the computational operations, not the content.

Question: What is the relationship between uncertainty and discovery?

Processing description:"""

    print("Wells-Diversity Conjecture — Empirical Test")
    print("Base vs Chat comparison on TinyLlama-1.1B")
    print("=" * 60)

    all_results = run_comparison(prompt, max_new_tokens=200)

    # Generate report
    report = format_comparison_report(prompt, all_results)

    output_path = Path(__file__).parent / "wells_diversity_results.md"
    output_path.write_text(report)
    print(f"\nReport saved to {output_path}")

    # Save raw data
    json_path = Path(__file__).parent / "wells_diversity_data.json"
    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    serializable = {}
    for label, data in all_results.items():
        serializable[label] = {
            "stats": {k: convert(v) for k, v in data["stats"].items()},
            "results": data["results"],
            "wells": data["wells"],
            "full_text": data["full_text"],
        }

    with open(json_path, "w") as f:
        json.dump(serializable, f, indent=2, default=convert)
    print(f"Raw data saved to {json_path}")

    # Final verdict
    print("\n" + "=" * 60)
    print("FINAL VERDICT")
    print("=" * 60)
    bs = all_results["base"]["stats"]
    cs = all_results["chat"]["stats"]
    print(f"  Wells: base={bs['well_count']}, chat={cs['well_count']}")
    print(f"  Diversity ratio: base={bs['diversity_ratio']:.2f}x, chat={cs['diversity_ratio']:.2f}x")
    print(f"  Entropy-diversity corr: base={bs['entropy_diversity_correlation']:.3f}, chat={cs['entropy_diversity_correlation']:.3f}")
    print(f"  H1 (Wells-Diversity): {'SUPPORTED' if bs['diversity_ratio'] > 1.0 and cs['diversity_ratio'] > 1.0 else 'CHECK REPORT'}")
    print(f"  H2 (RLHF Flattening): {'SUPPORTED' if bs['well_count'] > cs['well_count'] else 'CHECK REPORT'}")
