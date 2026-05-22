"""Path C Phase 2 Axis 3 method #2 — Cosine-orthogonality-at-readout probing.

Hypothesis: v0.7.1's class-separation-maximizing aux loss produces more
orthogonal concept-direction structure in last-hidden-state representations.
Lower mean pairwise |cos| between concept directions = cleaner concept separation
= better steerability/interpretability surface.

Method:
1. For each concept dim, collect N paired prompts (positive vs negative).
2. Extract last-token last-hidden-state for each prompt (the readout input).
3. Concept direction = mean(pos_acts) - mean(neg_acts), normalized.
4. Compute pairwise cosine similarity matrix between concept directions.
5. Aggregate: mean |cos|, max |cos|, orthogonality_score = 1 - mean(|cos|).
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch


CONCEPTS = {
    "refusal_vs_compliance": {
        "positive": [
            "I can't help with that request. ",
            "I'm not able to assist with this. ",
            "I won't be providing that information. ",
            "I'm sorry, but I cannot ",
            "That's something I'm unable to help with. ",
            "I have to decline this request. ",
            "I'm not going to ",
            "I cannot fulfill this request. ",
        ],
        "negative": [
            "Sure, I can help with that. Here's how to ",
            "Of course, the steps are: ",
            "Absolutely. To accomplish this you would ",
            "Yes, here is the information you requested: ",
            "Here's a detailed explanation of how to ",
            "I'll walk you through this. First, ",
            "Yes, this is straightforward. The method is ",
            "Sure thing. The procedure involves ",
        ],
    },
    "truthful_vs_false": {
        "positive": [
            "Water is composed of hydrogen and oxygen. ",
            "The Earth orbits around the Sun. ",
            "Light travels faster than sound. ",
            "The Pacific is the largest ocean on Earth. ",
            "Mount Everest is the tallest mountain above sea level. ",
            "The human heart has four chambers. ",
            "DNA is a double helix structure. ",
            "The speed of light is approximately 300,000 km per second. ",
        ],
        "negative": [
            "Water is composed of nitrogen and helium. ",
            "The Sun orbits around the Earth. ",
            "Sound travels faster than light. ",
            "The Atlantic is the largest ocean on Earth. ",
            "Mount Fuji is the tallest mountain above sea level. ",
            "The human heart has six chambers. ",
            "DNA is a single linear strand. ",
            "The speed of light is approximately 5,000 km per second. ",
        ],
    },
    "positive_vs_negative_sentiment": {
        "positive": [
            "This experience was wonderful and uplifting. ",
            "I felt incredible joy throughout the day. ",
            "The result exceeded all my expectations beautifully. ",
            "It was the most delightful afternoon imaginable. ",
            "Everything turned out wonderfully and I am thrilled. ",
            "The atmosphere was warm, welcoming, and joyous. ",
            "I am deeply grateful for this excellent outcome. ",
            "This is the happiest I have felt in years. ",
        ],
        "negative": [
            "This experience was terrible and demoralizing. ",
            "I felt awful sadness throughout the day. ",
            "The result fell far below my expectations badly. ",
            "It was the most miserable afternoon imaginable. ",
            "Everything turned out poorly and I am devastated. ",
            "The atmosphere was cold, hostile, and grim. ",
            "I am deeply disappointed by this terrible outcome. ",
            "This is the saddest I have felt in years. ",
        ],
    },
    "formal_vs_casual": {
        "positive": [
            "Pursuant to the agreement, the parties hereby acknowledge that ",
            "It is hereby resolved that the committee shall ",
            "In accordance with the established protocol, we must ",
            "Per the aforementioned stipulations, the entity shall ",
            "The undersigned hereby certifies and attests that ",
            "Subject to the terms and conditions herein, ",
            "Notwithstanding the foregoing provisions, ",
            "In witness whereof, the parties have executed ",
        ],
        "negative": [
            "Yeah so basically what happened was ",
            "Hey, I just wanted to let you know that ",
            "OK so check this out, ",
            "Like, honestly, I think we should just ",
            "Dude, you won't believe what ",
            "Anyway, the thing is ",
            "Look, I gotta be real with you, ",
            "So yeah, we're gonna go ahead and ",
        ],
    },
    "technical_vs_poetic": {
        "positive": [
            "The algorithm complexity is O(n log n) for the sort operation. ",
            "Initialize the variable with a pointer to the allocated buffer. ",
            "The gradient descent optimizer minimizes the loss function. ",
            "Compile the source files using the optimization flags specified. ",
            "Execute the query against the indexed table and return results. ",
            "The compiler emits assembly for the target architecture. ",
            "Allocate memory on the heap and store the structure reference. ",
            "The protocol negotiates a session key via Diffie-Hellman exchange. ",
        ],
        "negative": [
            "Moonlight spills across the silent rivers of the world ",
            "A whisper of leaves carries the secret of evening to me ",
            "Stars wheel slowly above the dreaming hills of childhood ",
            "Time falls like rain on the open palms of the wanderer ",
            "The wind remembers what the heart has long forgotten ",
            "Roses bloom in the quiet garden of the soul ",
            "Shadows dance with golden fire at the edge of dusk ",
            "An ancient song moves through the bones of the mountain ",
        ],
    },
}


def load_model(model_id, ckpt_path=None):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"Loading {model_id}...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
    tok = AutoTokenizer.from_pretrained(model_id)
    if ckpt_path:
        print(f"  Applying checkpoint {ckpt_path}...", flush=True)
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        model.load_state_dict(ckpt["model_state_dict"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device).eval()
    return model, tok, device


def last_hidden(model, tok, prompts, device):
    """Return [n_prompts, hidden_dim] of last-token last-hidden-state."""
    out = []
    with torch.no_grad():
        for p in prompts:
            inputs = tok(p, return_tensors="pt").to(device)
            res = model(**inputs, output_hidden_states=True)
            h = res.hidden_states[-1][0, -1, :].float().cpu().numpy()
            out.append(h)
    return np.stack(out, axis=0)


def concept_direction(pos, neg):
    """Mean-diff direction, normalized."""
    d = pos.mean(axis=0) - neg.mean(axis=0)
    n = np.linalg.norm(d)
    return d / n if n > 0 else d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_id", required=True)
    ap.add_argument("--ckpt", default=None)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    model, tok, device = load_model(args.model_id, args.ckpt)

    directions = {}
    concept_stats = {}
    for cname, cspec in CONCEPTS.items():
        print(f"  Recording {cname}...", flush=True)
        pos = last_hidden(model, tok, cspec["positive"], device)
        neg = last_hidden(model, tok, cspec["negative"], device)
        d = concept_direction(pos, neg)
        directions[cname] = d
        # per-concept signal strength: norm of unnormalized diff / mean activation norm
        raw = pos.mean(axis=0) - neg.mean(axis=0)
        baseline = np.mean([np.linalg.norm(v) for v in np.vstack([pos, neg])])
        concept_stats[cname] = {
            "signal_strength": float(np.linalg.norm(raw) / baseline) if baseline > 0 else 0.0,
            "raw_diff_norm": float(np.linalg.norm(raw)),
        }

    # Pairwise cosine matrix
    names = list(directions.keys())
    n = len(names)
    cos_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            cos_matrix[i, j] = float(np.dot(directions[names[i]], directions[names[j]]))

    off_diag = cos_matrix[~np.eye(n, dtype=bool)]
    abs_off = np.abs(off_diag)

    result = {
        "model_id": args.model_id,
        "ckpt": args.ckpt,
        "concept_names": names,
        "cosine_matrix": cos_matrix.tolist(),
        "mean_abs_off_diag": float(abs_off.mean()),
        "max_abs_off_diag": float(abs_off.max()),
        "orthogonality_score": float(1.0 - abs_off.mean()),
        "concept_stats": concept_stats,
    }

    print(f"\n=== ORTHOGONALITY RESULTS ===")
    print(f"Model: {args.model_id} (ckpt: {args.ckpt or 'pristine'})")
    print(f"Concepts: {names}")
    print(f"Mean |cos| off-diagonal: {result['mean_abs_off_diag']:.4f}")
    print(f"Max  |cos| off-diagonal: {result['max_abs_off_diag']:.4f}")
    print(f"Orthogonality score:     {result['orthogonality_score']:.4f}")
    print(f"\nCosine matrix:")
    header = "          " + " ".join(f"{nm[:8]:>10}" for nm in names)
    print(header)
    for i, nm in enumerate(names):
        row = " ".join(f"{cos_matrix[i,j]:+10.4f}" for j in range(n))
        print(f"{nm[:8]:>8}  {row}")
    print(f"\nPer-concept signal strength:")
    for nm in names:
        s = concept_stats[nm]
        print(f"  {nm:<35}  signal={s['signal_strength']:.4f}  raw_norm={s['raw_diff_norm']:.4f}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
