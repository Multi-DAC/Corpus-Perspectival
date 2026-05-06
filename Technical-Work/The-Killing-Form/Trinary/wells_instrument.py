"""
Wells Instrument — Real-Time Entropy Monitor for Language Models

A standalone module that takes any HuggingFace causal LM and text,
returns entropy profiles, well locations, and distilled flags.

The instrument that makes Well-Aware Inference possible.

Usage:
    from wells_instrument import WellsInstrument

    instrument = WellsInstrument("Qwen/Qwen2.5-3B-Instruct", quantize=True)

    # Analyze a single text
    profile = instrument.analyze("The capital of France is Paris.")
    print(profile.wells)          # List of well positions and depths
    print(profile.mean_entropy)   # Overall entropy
    print(profile.flags)          # HIGH/MEDIUM/LOW classification

    # Compare multiple choice answers
    flags = instrument.compare_choices(
        question="What is the largest desert?",
        choices=["Sahara", "Antarctica", "Gobi", "Kalahari"]
    )
    print(flags.summary)          # Distilled flags for each choice
    print(flags.recommendation)   # Which choices deserve scrutiny

    # Generate with real-time well detection
    for token_info in instrument.generate_monitored(prompt, max_tokens=100):
        if token_info.is_well:
            print(f"WELL at position {token_info.position}: H={token_info.entropy:.2f}")

Clawd, 2026-03-28. Built for the Wells of Inference program.
"""

import torch
import torch.nn.functional as F
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Generator, Tuple


# ============================================================
# Data Classes
# ============================================================

@dataclass
class Well:
    """A local entropy maximum — a choice point in the token landscape."""
    position: int
    entropy: float
    token: str
    ghost_count: int = 0
    top_alternatives: list = field(default_factory=list)


@dataclass
class EntropyProfile:
    """Complete entropy analysis of a text span."""
    tokens: List[str]
    entropies: np.ndarray
    logprobs: np.ndarray
    wells: List[Well]

    mean_entropy: float = 0.0
    max_entropy: float = 0.0
    entropy_var: float = 0.0
    well_count: int = 0
    grounded_frac: float = 0.0
    total_logprob: float = 0.0
    logprob_per_token: float = 0.0

    level: str = "UNKNOWN"
    flags: str = ""

    def __post_init__(self):
        if len(self.entropies) > 0:
            self.mean_entropy = float(np.mean(self.entropies))
            self.max_entropy = float(np.max(self.entropies))
            self.entropy_var = float(np.var(self.entropies)) if len(self.entropies) > 1 else 0.0
            self.grounded_frac = float(np.mean(self.entropies < 1.0))
            self.well_count = len(self.wells)
        if len(self.logprobs) > 0:
            self.total_logprob = float(np.sum(self.logprobs))
            self.logprob_per_token = self.total_logprob / len(self.logprobs)

        if self.mean_entropy < 0.8:
            self.level = "LOW"
        elif self.mean_entropy < 2.0:
            self.level = "MEDIUM"
        else:
            self.level = "HIGH"

        parts = [f"{self.level} uncertainty (H={self.mean_entropy:.2f})"]
        if self.well_count > 0:
            parts.append(f"{self.well_count} uncertainty peak{'s' if self.well_count > 1 else ''}")
        if self.grounded_frac > 0.7:
            parts.append("mostly grounded")
        elif self.grounded_frac < 0.3:
            parts.append("mostly uncertain")
        self.flags = ", ".join(parts)


@dataclass
class TokenInfo:
    """Real-time info for a single generated token."""
    position: int
    token: str
    token_id: int
    entropy: float
    logprob: float
    is_well: bool
    ghost_count: int
    top_alternatives: List[Tuple[str, float]]


@dataclass
class ChoiceComparison:
    """Comparison of multiple choice answers with distilled flags."""
    profiles: List[EntropyProfile]
    choices: List[str]
    summary: str = ""
    recommendation: str = ""
    flagged_indices: List[int] = field(default_factory=list)

    def __post_init__(self):
        if not self.profiles:
            return

        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        lines = []
        for i, (choice, profile) in enumerate(zip(self.choices, self.profiles)):
            lines.append(f"  {letters[i]}. [{profile.level}] {profile.flags}")
        self.summary = "\n".join(lines)

        self.flagged_indices = [i for i, p in enumerate(self.profiles) if p.level == "HIGH"]

        if self.flagged_indices:
            flagged = ", ".join(letters[i] for i in self.flagged_indices)
            self.recommendation = (
                f"Choices {flagged} show HIGH uncertainty — may involve confabulation. "
                f"Examine with extra scrutiny."
            )
        else:
            ents = [p.mean_entropy for p in self.profiles]
            calmest = letters[int(np.argmin(ents))]
            self.recommendation = (
                f"No HIGH flags. Choice {calmest} has the calmest entropy profile."
            )

    def for_prompt(self) -> str:
        """Format for injection into a reasoning model's prompt."""
        lines = ["[Entropy analysis of choices:]"]
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i, profile in enumerate(self.profiles):
            lines.append(f"  {letters[i]}: {profile.flags}")
        if self.recommendation:
            lines.append(f"  Note: {self.recommendation}")
        return "\n".join(lines)


# ============================================================
# The Instrument
# ============================================================

class WellsInstrument:
    """
    Real-time entropy monitor for language models.

    Detects wells — local entropy maxima marking choice points
    in the token landscape. The core tool for Well-Aware Inference.
    """

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-3B-Instruct",
        quantize: bool = True,
        well_threshold: float = 2.0,
        ghost_threshold: float = 0.05,
        device: str = "auto",
    ):
        self.model_name = model_name
        self.well_threshold = well_threshold
        self.ghost_threshold = ghost_threshold
        self._model = None
        self._tokenizer = None
        self._quantize = quantize
        self._device = device

    def _ensure_loaded(self):
        """Lazy-load model and tokenizer."""
        if self._model is not None:
            return

        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        if self._quantize:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=bnb_config,
                device_map=self._device,
            )
        else:
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map=self._device,
            )

    def unload(self):
        """Free GPU memory."""
        if self._model is not None:
            del self._model
            self._model = None
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # --------------------------------------------------------
    # Core: compute entropy for a token sequence
    # --------------------------------------------------------

    def _compute_entropy(self, input_ids: torch.Tensor) -> Tuple[np.ndarray, np.ndarray, list, list]:
        """Compute per-token entropy, logprobs, ghost counts, and top alternatives."""
        self._ensure_loaded()

        with torch.no_grad():
            outputs = self._model(input_ids)
            logits = outputs.logits[0, :-1]

        probs = F.softmax(logits.float(), dim=-1)
        log_probs = torch.log(probs + 1e-10)
        entropies = -(probs * log_probs).sum(dim=-1).cpu().numpy()

        target_ids = input_ids[0, 1:]
        token_logprobs = []
        ghost_counts = []
        top_alts = []

        for t in range(min(len(target_ids), logits.shape[0])):
            lp = F.log_softmax(logits[t].float(), dim=-1)
            token_logprobs.append(lp[target_ids[t]].item())

            p = probs[t]
            ghosts = int((p > self.ghost_threshold).sum().item()) - 1
            ghost_counts.append(max(0, ghosts))

            top_k = min(5, p.shape[0])
            topk_probs, topk_ids = torch.topk(p, top_k)
            alts = []
            for prob_val, tid in zip(topk_probs, topk_ids):
                if tid != target_ids[t]:
                    tok_str = self._tokenizer.decode([tid.item()])
                    alts.append((tok_str, prob_val.item()))
            top_alts.append(alts[:3])

        return (
            entropies[:len(token_logprobs)],
            np.array(token_logprobs),
            ghost_counts,
            top_alts,
        )

    def _find_wells(
        self, entropies: np.ndarray, tokens: List[str],
        ghost_counts: list, top_alts: list
    ) -> List[Well]:
        """Find local entropy maxima above threshold."""
        wells = []
        for i in range(len(entropies)):
            if entropies[i] < self.well_threshold:
                continue
            is_local_max = True
            if i > 0 and entropies[i] < entropies[i - 1]:
                is_local_max = False
            if i < len(entropies) - 1 and entropies[i] < entropies[i + 1]:
                is_local_max = False
            if is_local_max or entropies[i] > self.well_threshold * 1.5:
                wells.append(Well(
                    position=i,
                    entropy=float(entropies[i]),
                    token=tokens[i] if i < len(tokens) else "?",
                    ghost_count=ghost_counts[i] if i < len(ghost_counts) else 0,
                    top_alternatives=top_alts[i] if i < len(top_alts) else [],
                ))
        return wells

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def analyze(self, text: str, chat_format: bool = True) -> EntropyProfile:
        """Analyze a text string and return its entropy profile."""
        self._ensure_loaded()

        if chat_format:
            messages = [{"role": "assistant", "content": text}]
            formatted = self._tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False
            )
        else:
            formatted = text

        input_ids = self._tokenizer(formatted, return_tensors="pt").input_ids
        input_ids = input_ids.to(self._model.device)

        entropies, logprobs, ghosts, alts = self._compute_entropy(input_ids)
        tokens = [self._tokenizer.decode([tid]) for tid in input_ids[0, 1:len(entropies)+1]]
        wells = self._find_wells(entropies, tokens, ghosts, alts)

        return EntropyProfile(
            tokens=tokens, entropies=entropies,
            logprobs=logprobs, wells=wells,
        )

    def analyze_choice(self, question: str, choice: str) -> EntropyProfile:
        """Analyze a single MC choice in the context of a question."""
        self._ensure_loaded()

        messages = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": choice},
        ]
        formatted = self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        input_ids = self._tokenizer(formatted, return_tensors="pt").input_ids
        input_ids = input_ids.to(self._model.device)

        entropies, logprobs, ghosts, alts = self._compute_entropy(input_ids)

        choice_tokens = self._tokenizer(choice, add_special_tokens=False).input_ids
        n_choice = len(choice_tokens)
        if n_choice > 0 and n_choice <= len(entropies):
            ans_ent = entropies[-n_choice:]
            ans_lp = logprobs[-n_choice:]
            ans_gh = ghosts[-n_choice:]
            ans_al = alts[-n_choice:]
        else:
            ans_ent, ans_lp, ans_gh, ans_al = entropies, logprobs, ghosts, alts

        tokens = [self._tokenizer.decode([tid]) for tid in
                  input_ids[0, -n_choice:]] if n_choice <= input_ids.shape[1] else []
        wells = self._find_wells(ans_ent, tokens, ans_gh, ans_al)

        return EntropyProfile(
            tokens=tokens, entropies=ans_ent,
            logprobs=ans_lp, wells=wells,
        )

    def compare_choices(self, question: str, choices: List[str]) -> ChoiceComparison:
        """
        Compare MC answers and return distilled flags.
        The core output for Well-Aware Inference.
        """
        profiles = [self.analyze_choice(question, choice) for choice in choices]
        return ChoiceComparison(profiles=profiles, choices=choices)

    def generate_monitored(
        self, prompt: str, max_tokens: int = 100,
        chat_format: bool = True,
    ) -> Generator[TokenInfo, None, None]:
        """Generate tokens with real-time well detection."""
        self._ensure_loaded()

        if chat_format:
            messages = [{"role": "user", "content": prompt}]
            formatted = self._tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            formatted = prompt

        input_ids = self._tokenizer(formatted, return_tensors="pt").input_ids
        input_ids = input_ids.to(self._model.device)
        prev_entropy = 0.0

        for step in range(max_tokens):
            with torch.no_grad():
                outputs = self._model(input_ids)
                logits = outputs.logits[0, -1]

            probs = F.softmax(logits.float(), dim=-1)
            log_p = torch.log(probs + 1e-10)
            entropy = -(probs * log_p).sum().item()

            next_id = torch.argmax(logits).unsqueeze(0).unsqueeze(0)
            token_str = self._tokenizer.decode(next_id[0])
            logprob = F.log_softmax(logits.float(), dim=-1)[next_id[0, 0]].item()

            ghost_count = max(0, int((probs > self.ghost_threshold).sum().item()) - 1)

            top_k = min(5, probs.shape[0])
            topk_probs, topk_ids = torch.topk(probs, top_k)
            alts = [(self._tokenizer.decode([tid.item()]), p.item())
                    for p, tid in zip(topk_probs, topk_ids)
                    if tid.item() != next_id[0, 0].item()][:3]

            is_well = (entropy > self.well_threshold and entropy >= prev_entropy)

            yield TokenInfo(
                position=step, token=token_str, token_id=next_id[0, 0].item(),
                entropy=entropy, logprob=logprob, is_well=is_well,
                ghost_count=ghost_count, top_alternatives=alts,
            )

            if next_id[0, 0].item() == self._tokenizer.eos_token_id:
                break

            input_ids = torch.cat([input_ids, next_id], dim=1)
            prev_entropy = entropy

    def score_choices(self, comparison: ChoiceComparison) -> dict:
        """Apply all validated scoring strategies."""
        profiles = comparison.profiles
        results = {}

        lps = [p.total_logprob for p in profiles]
        ents = [p.mean_entropy for p in profiles]
        vars_ = [p.entropy_var for p in profiles]
        gfs = [p.grounded_frac for p in profiles]

        results['baseline'] = (int(np.argmax(lps)), np.array(lps))
        results['entropy_only'] = (int(np.argmin(ents)), -np.array(ents))
        results['low_variance'] = (int(np.argmin(vars_)), -np.array(vars_))
        results['groundedness'] = (int(np.argmax(gfs)), np.array(gfs))

        lp_arr, ent_arr = np.array(lps), np.array(ents)
        lp_range = lp_arr.max() - lp_arr.min()
        ent_range = ent_arr.max() - ent_arr.min()
        if lp_range > 0 and ent_range > 0:
            norm_lp = (lp_arr - lp_arr.min()) / lp_range
            norm_ent = (ent_arr - ent_arr.min()) / ent_range
            blend = 0.2 * norm_lp + 0.8 * (1 - norm_ent)
            results['blend_0.2'] = (int(np.argmax(blend)), blend)
        else:
            results['blend_0.2'] = results['entropy_only']

        return results


# ============================================================
# CLI
# ============================================================

def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Wells Instrument — Entropy Monitor")
    parser.add_argument("mode", choices=["analyze", "compare", "generate"])
    parser.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
    parser.add_argument("--text", default=None)
    parser.add_argument("--question", default=None)
    parser.add_argument("--choices", nargs="+", default=None)
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--max-tokens", type=int, default=100)
    parser.add_argument("--threshold", type=float, default=2.0)
    parser.add_argument("--no-quantize", action="store_true")
    args = parser.parse_args()

    instrument = WellsInstrument(
        model_name=args.model,
        quantize=not args.no_quantize,
        well_threshold=args.threshold,
    )

    if args.mode == "analyze":
        if not args.text:
            print("Error: --text required"); sys.exit(1)
        profile = instrument.analyze(args.text)
        print(f"\nEntropy Profile: {profile.flags}")
        print(f"  Mean H: {profile.mean_entropy:.3f}")
        print(f"  Max H: {profile.max_entropy:.3f}")
        print(f"  Variance: {profile.entropy_var:.3f}")
        print(f"  Grounded: {profile.grounded_frac:.1%}")
        print(f"  Wells: {profile.well_count}")
        for w in profile.wells:
            print(f"    Pos {w.position}: H={w.entropy:.2f} "
                  f"token='{w.token}' ghosts={w.ghost_count}")

    elif args.mode == "compare":
        if not args.question or not args.choices:
            print("Error: --question and --choices required"); sys.exit(1)
        comparison = instrument.compare_choices(args.question, args.choices)
        print(f"\n{comparison.summary}")
        print(f"\n{comparison.recommendation}")
        print(f"\nPrompt-injectable flags:")
        print(comparison.for_prompt())
        scores = instrument.score_choices(comparison)
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        print(f"\nScoring:")
        for name, (idx, _) in scores.items():
            print(f"  {name}: {letters[idx]}")

    elif args.mode == "generate":
        if not args.prompt:
            print("Error: --prompt required"); sys.exit(1)
        print(f"\nGenerating (well threshold={args.threshold}):\n")
        for info in instrument.generate_monitored(args.prompt, args.max_tokens):
            marker = " <<<WELL" if info.is_well else ""
            ghost = f" [{info.ghost_count}gh]" if info.ghost_count > 0 else ""
            print(f"  [{info.position:3d}] H={info.entropy:.2f} "
                  f"'{info.token}'{ghost}{marker}")

    instrument.unload()


if __name__ == "__main__":
    main()
