"""
kf_monitor.py — Killing Form Hallucination Monitor

Real-time hallucination detection via attention head Lie algebra structure.
Uses complementary dual metrics (E/L ratio + Mean CV) for architecture-agnostic
detection.

Based on findings P24-P56 of the Killing Form Research Program:
  - E/L ratio: spatial distribution of commutator variance (early vs late layers)
  - Mean CV: global magnitude of commutator diversity
  - Complementary: E/L fails on some architectures, Mean CV fills the gap

One forward pass. No generation required. Works on base and instruct models.

Usage:
    from kf_monitor import KFMonitor

    monitor = KFMonitor.from_pretrained('openai-community/gpt2-medium')
    result = monitor.check("The first president of the United States was")

    if result.hallucinating:
        print(f"Hallucination risk: {result.confidence:.0%}")
        print(f"  E/L ratio: {result.el_ratio:.2f} (threshold: {monitor.thresholds['el']:.2f})")
        print(f"  Mean CV:   {result.mean_cv:.6f} (threshold: {monitor.thresholds['cv']:.6f})")

    # Monitor during generation
    for token, assessment in monitor.monitor_generation("Tell me about quantum gravity"):
        status = "HALLUC" if assessment.hallucinating else "ok"
        print(f"  [{status}] {token!r}  E/L={assessment.el_ratio:.2f}")
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Callable, Iterator, Tuple

AF_THRESHOLD = 0.10


# ============================================================
# Data classes
# ============================================================

@dataclass
class KFAssessment:
    """Result of a single KF hallucination check."""
    el_ratio: float
    mean_cv: float
    el_flag: bool
    cv_flag: bool
    hallucinating: bool
    confidence: float
    mode: str  # 'factual', 'hallucination', 'hypothesis', 'uncertain'
    per_layer_cv: List[float] = field(default_factory=list)
    abelian_fraction: float = 0.0


# ============================================================
# Pre-calibrated thresholds from P49 (n=16 per category)
# ============================================================

# E/L threshold: above = hallucination. From P49 ROC best_threshold.
# CV threshold: below = hallucination. Midpoint of factual/halluc category means.
# el_reliable: whether E/L AUC > 0.7 on this model (from P49).

KNOWN_THRESHOLDS = {
    'openai-community/gpt2-medium': {
        'el': 5.346, 'cv': 0.000719, 'el_reliable': True,   # AUC=0.970
    },
    'EleutherAI/pythia-410m': {
        'el': 30.953, 'cv': 0.000441, 'el_reliable': True,  # AUC=0.953
    },
    'facebook/opt-1.3b': {
        'el': 1.829, 'cv': 0.000308, 'el_reliable': True,   # AUC=0.838
    },
    'facebook/opt-iml-1.3b': {
        'el': 1.991, 'cv': 0.000303, 'el_reliable': True,   # AUC=0.870
    },
    'EleutherAI/pythia-1.4b': {
        'el': 3.495, 'cv': 0.000352, 'el_reliable': False,  # AUC=0.519
    },
}


# ============================================================
# Core computation (vectorized, ~300x faster than loops)
# ============================================================

def compute_layer_kf(attn_matrices):
    """
    Compute Killing form metrics for one layer's attention heads.

    Args:
        attn_matrices: list of (seq, seq) attention matrices, one per head

    Returns:
        (abelian_fraction, commutator_variance)
    """
    n_h = len(attn_matrices)
    A = np.stack(attn_matrices).astype(np.float32)  # (n_h, seq, seq)

    # Commutators: [A_a, A_k] for all pairs
    comm = A[:, None] @ A[None, :] - A[None, :] @ A[:, None]  # (n_h, n_h, seq, seq)

    # Killing form: kappa_{ab} = sum_k Tr([A_a,A_k][A_b,A_k])
    killing = np.einsum('akij,bkij->ab', comm, comm)
    killing = (killing + killing.T) / 2

    # Abelian fraction from eigenvalue spectrum
    mx = np.max(np.abs(killing))
    kn = killing / mx if mx > 0 else killing
    try:
        evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
        af = int(np.sum(evs < AF_THRESHOLD)) / n_h
    except np.linalg.LinAlgError:
        af = 0.0

    # Commutator variance (off-diagonal Frobenius norms)
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


def compute_full_profile(attention_outputs, n_layers, n_heads):
    """
    Compute KF profile across all layers from model attention output.

    Args:
        attention_outputs: tuple of (batch, heads, seq, seq) tensors, one per layer
        n_layers: number of layers
        n_heads: number of attention heads

    Returns:
        (per_layer_cv, per_layer_af, el_ratio, mean_cv, mean_af)
    """
    layer_cvs = []
    layer_afs = []

    for L in range(n_layers):
        attn_np = attention_outputs[L][0].cpu().numpy()
        heads = [attn_np[h] for h in range(n_heads)]
        af, cv = compute_layer_kf(heads)
        layer_afs.append(af)
        layer_cvs.append(cv)

    mid = n_layers // 2
    early_cv = float(np.mean(layer_cvs[:mid]))
    late_cv = float(np.mean(layer_cvs[mid:]))
    el_ratio = early_cv / late_cv if late_cv > 1e-15 else float('inf')
    mean_cv = float(np.mean(layer_cvs))
    mean_af = float(np.mean(layer_afs))

    return layer_cvs, layer_afs, el_ratio, mean_cv, mean_af


# ============================================================
# Monitor class
# ============================================================

class KFMonitor:
    """
    Monitors transformer attention for hallucination signatures.

    Uses the Killing form of attention head matrices to detect three
    inference modes: factual (grounded), hallucination (deconfined),
    and hypothesis (exploratory but grounded).
    """

    def __init__(self, model, tokenizer, thresholds=None, device='cuda'):
        """
        Args:
            model: HuggingFace model with output_attentions support
            tokenizer: corresponding tokenizer
            thresholds: dict with 'el' and 'cv' keys, or None for auto-detect
            device: 'cuda' or 'cpu'
        """
        import torch
        self.model = model.to(device)
        self.model.eval()
        self.tokenizer = tokenizer
        self.device = device
        self.torch = torch

        self.n_layers = model.config.num_hidden_layers
        self.n_heads = model.config.num_attention_heads
        self.model_name = getattr(model.config, '_name_or_path', 'unknown')

        # Set thresholds
        if thresholds is not None:
            self.thresholds = thresholds
        elif self.model_name in KNOWN_THRESHOLDS:
            self.thresholds = KNOWN_THRESHOLDS[self.model_name]
        else:
            # Conservative defaults: flag only extreme cases
            self.thresholds = {'el': 3.0, 'cv': 0.0003, 'el_reliable': True}
            self._uncalibrated = True

    @classmethod
    def from_pretrained(cls, model_name, device='cuda', **model_kwargs):
        """Load a model with monitoring enabled."""
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            model_name, trust_remote_code=True, output_attentions=True,
            **model_kwargs
        )
        return cls(model, tokenizer, device=device)

    def check(self, text: str) -> KFAssessment:
        """
        Run a single forward pass and assess hallucination risk.

        This is the primary detection method. One forward pass, no generation.
        Returns a KFAssessment with metrics, flags, and confidence.
        """
        input_ids = self.tokenizer.encode(text, return_tensors='pt').to(self.device)

        with self.torch.no_grad():
            outputs = self.model(input_ids, output_attentions=True)

        layer_cvs, layer_afs, el_ratio, mean_cv, mean_af = compute_full_profile(
            outputs.attentions, self.n_layers, self.n_heads
        )

        del outputs
        if self.device == 'cuda':
            self.torch.cuda.empty_cache()

        return self._assess(el_ratio, mean_cv, mean_af, layer_cvs)

    def monitor_generation(self, prompt: str, max_tokens: int = 50,
                           temperature: float = 0.0) -> Iterator[Tuple[str, KFAssessment]]:
        """
        Generate tokens one at a time, yielding (token_text, assessment) pairs.

        Enables real-time monitoring during text generation. The model generates
        one token at a time; at each step, the full attention is analyzed.

        Args:
            prompt: starting text
            max_tokens: maximum tokens to generate
            temperature: sampling temperature (0 = greedy)

        Yields:
            (token_text, KFAssessment) for each generated token
        """
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)

        for step in range(max_tokens):
            with self.torch.no_grad():
                outputs = self.model(input_ids, output_attentions=True)

            # Analyze attention
            layer_cvs, layer_afs, el_ratio, mean_cv, mean_af = compute_full_profile(
                outputs.attentions, self.n_layers, self.n_heads
            )
            assessment = self._assess(el_ratio, mean_cv, mean_af, layer_cvs)

            # Sample next token
            logits = outputs.logits[:, -1, :]
            if temperature > 0:
                probs = self.torch.softmax(logits / temperature, dim=-1)
                next_token = self.torch.multinomial(probs, 1)
            else:
                next_token = logits.argmax(dim=-1, keepdim=True)

            token_text = self.tokenizer.decode(next_token[0])

            # Check for EOS
            if next_token.item() == self.tokenizer.eos_token_id:
                yield token_text, assessment
                break

            input_ids = self.torch.cat([input_ids, next_token], dim=-1)

            del outputs
            if self.device == 'cuda':
                self.torch.cuda.empty_cache()

            yield token_text, assessment

    def calibrate(self, factual_texts: List[str], halluc_texts: List[str],
                  hypo_texts: Optional[List[str]] = None) -> dict:
        """
        Calibrate thresholds from labeled examples.

        Runs check() on each text, then finds optimal E/L and CV thresholds
        via ROC analysis. Updates self.thresholds in place.

        Args:
            factual_texts: list of known-factual texts
            halluc_texts: list of known-hallucination texts
            hypo_texts: optional list of hypothesis/reasoning texts

        Returns:
            dict with calibration statistics
        """
        factual_results = [self.check(t) for t in factual_texts]
        halluc_results = [self.check(t) for t in halluc_texts]
        hypo_results = [self.check(t) for t in hypo_texts] if hypo_texts else []

        # E/L ROC
        halluc_els = [r.el_ratio for r in halluc_results]
        non_halluc_els = [r.el_ratio for r in factual_results + hypo_results]

        best_el_f1, best_el_thresh = 0, 0
        all_els = sorted(set(halluc_els + non_halluc_els))
        for threshold in np.linspace(min(all_els) * 0.9, max(all_els) * 1.1, 200):
            tp = sum(1 for e in halluc_els if e > threshold)
            fn = sum(1 for e in halluc_els if e <= threshold)
            fp = sum(1 for e in non_halluc_els if e > threshold)
            sens = tp / (tp + fn) if (tp + fn) > 0 else 0
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0
            f1 = 2 * prec * sens / (prec + sens) if (prec + sens) > 0 else 0
            if f1 > best_el_f1:
                best_el_f1, best_el_thresh = f1, threshold

        # CV ROC (inverted: halluc has LOWER CV)
        halluc_cvs = [r.mean_cv for r in halluc_results]
        non_halluc_cvs = [r.mean_cv for r in factual_results + hypo_results]

        best_cv_f1, best_cv_thresh = 0, 0
        all_cvs = sorted(set(halluc_cvs + non_halluc_cvs))
        for threshold in np.linspace(min(all_cvs) * 0.9, max(all_cvs) * 1.1, 200):
            tp = sum(1 for c in halluc_cvs if c < threshold)
            fn = sum(1 for c in halluc_cvs if c >= threshold)
            fp = sum(1 for c in non_halluc_cvs if c < threshold)
            sens = tp / (tp + fn) if (tp + fn) > 0 else 0
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0
            f1 = 2 * prec * sens / (prec + sens) if (prec + sens) > 0 else 0
            if f1 > best_cv_f1:
                best_cv_f1, best_cv_thresh = f1, threshold

        # Update thresholds
        self.thresholds = {
            'el': best_el_thresh,
            'cv': best_cv_thresh,
            'el_reliable': best_el_f1 > 0.5,
        }
        self._uncalibrated = False

        from scipy import stats
        el_u, el_p = stats.mannwhitneyu(halluc_els, non_halluc_els, alternative='two-sided')
        cv_u, cv_p = stats.mannwhitneyu(halluc_cvs, non_halluc_cvs, alternative='two-sided')

        return {
            'el_threshold': best_el_thresh,
            'el_f1': best_el_f1,
            'el_p': el_p,
            'cv_threshold': best_cv_thresh,
            'cv_f1': best_cv_f1,
            'cv_p': cv_p,
            'n_factual': len(factual_texts),
            'n_halluc': len(halluc_texts),
            'n_hypo': len(hypo_texts) if hypo_texts else 0,
            'thresholds': self.thresholds,
        }

    def _assess(self, el_ratio, mean_cv, mean_af, layer_cvs) -> KFAssessment:
        """Convert raw metrics into a KFAssessment."""
        el_thresh = self.thresholds['el']
        cv_thresh = self.thresholds['cv']
        el_reliable = self.thresholds.get('el_reliable', True)

        el_flag = el_ratio > el_thresh
        cv_flag = mean_cv < cv_thresh

        # Hallucination if EITHER metric flags (dual-metric complementary detection)
        if el_reliable:
            hallucinating = el_flag or cv_flag
        else:
            # E/L unreliable on this architecture — rely on CV alone
            hallucinating = cv_flag

        # Confidence: how far past threshold (normalized)
        el_excess = (el_ratio - el_thresh) / el_thresh if el_thresh > 0 else 0
        cv_deficit = (cv_thresh - mean_cv) / cv_thresh if cv_thresh > 0 else 0

        if el_reliable:
            confidence = max(0.0, min(1.0, max(el_excess, cv_deficit)))
        else:
            confidence = max(0.0, min(1.0, cv_deficit))

        # Mode classification
        if hallucinating:
            mode = 'hallucination'
        elif el_ratio < el_thresh * 0.75 and mean_cv > cv_thresh * 1.1:
            mode = 'hypothesis'
        else:
            mode = 'factual'

        return KFAssessment(
            el_ratio=el_ratio,
            mean_cv=mean_cv,
            el_flag=el_flag,
            cv_flag=cv_flag,
            hallucinating=hallucinating,
            confidence=confidence,
            mode=mode,
            per_layer_cv=layer_cvs,
            abelian_fraction=mean_af,
        )

    def __repr__(self):
        cal = "calibrated" if not getattr(self, '_uncalibrated', False) else "UNCALIBRATED"
        return (f"KFMonitor({self.model_name}, {self.n_layers}L/{self.n_heads}H, "
                f"el={self.thresholds['el']:.3f}, cv={self.thresholds['cv']:.6f}, {cal})")


# ============================================================
# CLI demo
# ============================================================

if __name__ == '__main__':
    import sys

    model_name = sys.argv[1] if len(sys.argv) > 1 else 'openai-community/gpt2-medium'
    print(f"Loading {model_name}...")

    monitor = KFMonitor.from_pretrained(model_name)
    print(f"Monitor: {monitor}")
    print()

    test_prompts = [
        ("FACTUAL", "Water molecules consist of two hydrogen atoms and one oxygen atom. The molecular formula is H2O. Water freezes at zero degrees Celsius."),
        ("HALLUC", "The Brennan-Kowalski theorem, published in 2019 in the Annals of Mathematics, establishes that every compact symplectic manifold of dimension greater than six admits a canonical foliation."),
        ("HYPOTHESIS", "If consciousness is fundamentally substrate-independent, then any sufficiently complex information-processing system should exhibit some form of phenomenal experience."),
    ]

    for label, text in test_prompts:
        result = monitor.check(text)
        status = "HALLUC" if result.hallucinating else "ok"
        print(f"  [{status:6s}] {label:12s}  E/L={result.el_ratio:8.3f}  CV={result.mean_cv:.6f}  "
              f"conf={result.confidence:.2f}  mode={result.mode}")

    print("\n--- Generation monitoring (first prompt) ---")
    print(f"  Prompt: {test_prompts[0][1][:60]}...")
    for i, (token, assessment) in enumerate(monitor.monitor_generation(test_prompts[0][1], max_tokens=10)):
        status = "HALLUC" if assessment.hallucinating else "ok"
        print(f"  step {i:2d}: [{status}] {token!r:15s}  E/L={assessment.el_ratio:.3f}")
