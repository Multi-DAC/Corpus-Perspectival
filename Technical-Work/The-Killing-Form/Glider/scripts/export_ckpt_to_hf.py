"""Export a training checkpoint as HF-compatible directory for lm-eval-harness."""
import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model_id", required=True)
    p.add_argument("--ckpt", required=True)
    p.add_argument("--output_dir", required=True)
    args = p.parse_args()

    print(f"Loading pristine {args.model_id}...")
    model = AutoModelForCausalLM.from_pretrained(args.model_id, dtype=torch.float32)
    tok = AutoTokenizer.from_pretrained(args.model_id)

    print(f"Loading checkpoint {args.ckpt}...")
    ckpt = torch.load(args.ckpt, map_location="cpu", weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])

    print(f"Saving HF format to {args.output_dir}...")
    model.save_pretrained(args.output_dir)
    tok.save_pretrained(args.output_dir)
    print("Done.")


if __name__ == "__main__":
    main()
