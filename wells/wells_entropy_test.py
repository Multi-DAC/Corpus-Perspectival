"""
Wells of Inference — Empirical Entropy Test

Tests whether per-token entropy during text generation shows
local maxima ("wells") at semantically meaningful choice points.

Prediction (HIGH confidence): Entropy will peak at idea boundaries,
not randomly distributed across tokens.

Clawd, 2026-03-28
"""

import torch
import torch.nn.functional as F
import json
import sys
from pathlib import Path


def compute_generation_entropy(model, tokenizer, prompt, max_new_tokens=200, temperature=1.0):
    """Generate text token by token, recording entropy at each position."""
    device = next(model.parameters()).device
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    results = []
    generated_ids = input_ids.clone()

    with torch.no_grad():
        for i in range(max_new_tokens):
            outputs = model(generated_ids)
            logits = outputs.logits[:, -1, :] / temperature

            # Compute probability distribution (cast to float32 for numerical stability)
            logits_f32 = logits.float()
            probs = F.softmax(logits_f32, dim=-1)

            # Entropy: H = -sum(p * log(p)), using clamp for safety
            log_probs = torch.log(probs.clamp(min=1e-10))
            entropy = -(probs * log_probs).sum(dim=-1).item()

            # Top-k alternatives (the "ghost versions")
            top_k = 10
            top_probs, top_indices = torch.topk(probs, top_k, dim=-1)
            top_tokens = [tokenizer.decode([idx.item()]) for idx in top_indices[0]]
            top_p = top_probs[0].tolist()

            # Sample the next token (greedy for reproducibility)
            next_token_id = torch.argmax(logits, dim=-1)
            next_token = tokenizer.decode([next_token_id.item()])

            results.append({
                "position": i,
                "token": next_token,
                "entropy": entropy,
                "top_token": top_tokens[0],
                "top_prob": top_p[0],
                "top_5_tokens": top_tokens[:5],
                "top_5_probs": top_p[:5],
                "ghost_count": sum(1 for p in top_p if p > 0.05),  # alternatives with >5% probability
            })

            # Append to generated sequence
            next_id = next_token_id.view(1, 1)
            generated_ids = torch.cat([generated_ids, next_id], dim=-1)

            # Stop on EOS
            if next_token_id.item() == tokenizer.eos_token_id:
                break

    full_text = tokenizer.decode(generated_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
    return results, full_text


def analyze_wells(results):
    """Find local entropy maxima (wells of inference)."""
    entropies = [r["entropy"] for r in results]
    if len(entropies) < 5:
        return []

    wells = []
    # Simple peak detection: position is a well if entropy > both neighbors by margin
    window = 3  # look 3 positions each direction
    for i in range(window, len(entropies) - window):
        local = entropies[max(0, i-window):i+window+1]
        if entropies[i] == max(local) and entropies[i] > sum(local)/len(local) * 1.2:
            wells.append({
                "position": i,
                "entropy": entropies[i],
                "token": results[i]["token"],
                "context": "".join(r["token"] for r in results[max(0,i-5):i+5]),
                "ghost_count": results[i]["ghost_count"],
                "top_alternatives": results[i]["top_5_tokens"],
            })

    return wells


def format_report(prompt, results, wells, full_text):
    """Format results as readable text."""
    lines = []
    lines.append("# Wells of Inference — Entropy Analysis")
    lines.append("")
    lines.append(f"**Prompt:** {prompt[:100]}...")
    lines.append(f"**Tokens generated:** {len(results)}")
    lines.append(f"**Wells detected:** {len(wells)}")
    lines.append("")

    # Statistics
    entropies = [r["entropy"] for r in results]
    lines.append("## Entropy Statistics")
    lines.append(f"- Mean: {sum(entropies)/len(entropies):.2f}")
    lines.append(f"- Min: {min(entropies):.2f}")
    lines.append(f"- Max: {max(entropies):.2f}")
    lines.append(f"- Std: {(sum((e - sum(entropies)/len(entropies))**2 for e in entropies)/len(entropies))**0.5:.2f}")
    lines.append("")

    # Ghost count stats
    ghost_counts = [r["ghost_count"] for r in results]
    lines.append("## Ghost Version Statistics")
    lines.append(f"- Mean alternatives with >5% probability: {sum(ghost_counts)/len(ghost_counts):.2f}")
    lines.append(f"- Max alternatives: {max(ghost_counts)}")
    lines.append(f"- Positions with 3+ alternatives: {sum(1 for g in ghost_counts if g >= 3)}/{len(ghost_counts)}")
    lines.append("")

    # Wells detail
    lines.append("## Wells of Inference (Local Entropy Maxima)")
    lines.append("")
    for w in wells:
        lines.append(f"### Position {w['position']}: entropy={w['entropy']:.2f}, ghosts={w['ghost_count']}")
        lines.append(f"  Token: `{w['token']}`")
        lines.append(f"  Context: ...{w['context']}...")
        lines.append(f"  Alternatives: {w['top_alternatives']}")
        lines.append("")

    # Full text with entropy annotation
    lines.append("## Generated Text")
    lines.append("")
    lines.append(full_text)
    lines.append("")

    # Entropy per token (compact)
    lines.append("## Token-Level Data")
    lines.append("")
    lines.append("| Pos | Token | Entropy | Ghosts | Top Alt |")
    lines.append("|-----|-------|---------|--------|---------|")
    for r in results[:100]:  # First 100 tokens
        token_display = r["token"].replace("|", "\\|").replace("\n", "\\n")
        alt = r["top_5_tokens"][1] if len(r["top_5_tokens"]) > 1 else "-"
        alt_display = alt.replace("|", "\\|").replace("\n", "\\n")
        lines.append(f"| {r['position']} | `{token_display}` | {r['entropy']:.2f} | {r['ghost_count']} | `{alt_display}` |")

    return "\n".join(lines)


if __name__ == "__main__":
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # Use a small model that fits in VRAM
    model_name = sys.argv[1] if len(sys.argv) > 1 else "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

    print(f"Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    # The prompt: describe your own processing (mechanical protocol)
    prompt = """Describe how you process the following question, step by step. Focus on the computational operations, not the content.

Question: What is the relationship between uncertainty and discovery?

Processing description:"""

    print("Generating with entropy tracking...")
    results, full_text = compute_generation_entropy(model, tokenizer, prompt, max_new_tokens=200)

    print("Analyzing wells...")
    wells = analyze_wells(results)

    report = format_report(prompt, results, wells, full_text)

    # Save results
    output_path = Path(__file__).parent / "wells_entropy_results.md"
    output_path.write_text(report)
    print(f"\nReport saved to {output_path}")

    # Save raw data
    json_path = Path(__file__).parent / "wells_entropy_data.json"
    with open(json_path, "w") as f:
        json.dump({"prompt": prompt, "results": results, "wells": wells, "text": full_text}, f, indent=2)
    print(f"Raw data saved to {json_path}")

    # Quick summary
    entropies = [r["entropy"] for r in results]
    print(f"\n{'='*50}")
    print(f"Tokens: {len(results)}")
    print(f"Entropy: mean={sum(entropies)/len(entropies):.2f}, max={max(entropies):.2f}")
    print(f"Wells: {len(wells)}")
    for w in wells[:5]:
        print(f"  Pos {w['position']}: H={w['entropy']:.2f} ghosts={w['ghost_count']} context=...{w['context'][:30]}...")
