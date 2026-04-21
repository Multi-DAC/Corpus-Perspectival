"""
Fisher Geometry Module — Commitment Angle and Fisher Speed for Token Trajectories

Computes the geometric quantities derived in Drift #128 "On the Geometry of the Fork":
- Fisher speed v_F(t): how fast the model moves through probability space
- Commitment angle α(t): angle between velocity and entropy gradient
- Fork location: where α transitions from ~0 to ~π/2

These extend the wells instrument's entropy analysis with geometric structure
that connects to the Doctrine's null space theory (Bridge #68).

Usage:
    from fisher_geometry import FisherGeometry

    geo = FisherGeometry(probs_sequence)  # T x V tensor of softmax probabilities
    print(geo.fisher_speeds)       # Array of Fisher speeds
    print(geo.commitment_angles)   # Array of commitment angles
    print(geo.fork_location)       # Token position of the geometric fork
    print(geo.summary())           # Human-readable summary

    # Or from a wells instrument profile:
    geo = FisherGeometry.from_logits(logits_tensor)

Clawd, 2026-04-01. Built for the Bridge (Bridge #68).
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class FisherGeometry:
    """
    Geometric analysis of a token probability trajectory on the categorical simplex.

    The core quantities:
    - fisher_speeds[t]: Fisher-Rao distance between P_t and P_{t+1}
    - commitment_angles[t]: angle between velocity and entropy gradient at P_t
    - entropy_gradient_norms[t]: ||∇_FR H|| at P_t (entropy pressure)
    - fork_location: argmax |dα/dt| — the geometric fork point
    """

    # Input
    n_tokens: int
    vocab_size: int

    # Per-token quantities (length = n_tokens - 1, between consecutive pairs)
    fisher_speeds: np.ndarray
    commitment_angles: np.ndarray
    entropy_gradient_norms: np.ndarray
    entropy_rates: np.ndarray

    # Derived
    fork_location: int = -1
    pre_fork_mean_speed: float = 0.0
    post_fork_mean_speed: float = 0.0
    pre_fork_mean_angle: float = 0.0
    post_fork_mean_angle: float = 0.0
    speed_ratio: float = 0.0  # post/pre Fisher speed ratio — basin depth indicator

    @staticmethod
    def from_probs(probs: np.ndarray, eps: float = 1e-10) -> 'FisherGeometry':
        """
        Compute Fisher geometry from a T x V array of probability distributions.

        Args:
            probs: (T, V) array where probs[t] is the softmax distribution at token t
            eps: small constant for numerical stability

        Returns:
            FisherGeometry with all quantities computed
        """
        T, V = probs.shape
        if T < 2:
            return FisherGeometry(
                n_tokens=T, vocab_size=V,
                fisher_speeds=np.array([]),
                commitment_angles=np.array([]),
                entropy_gradient_norms=np.array([]),
                entropy_rates=np.array([]),
            )

        # Clamp for stability
        probs = np.clip(probs, eps, 1.0)
        probs = probs / probs.sum(axis=1, keepdims=True)

        # --- Entropy at each position ---
        entropies = -np.sum(probs * np.log(probs), axis=1)  # (T,)
        entropy_rates = np.diff(entropies)  # (T-1,)

        # --- Fisher-Rao distance between consecutive distributions ---
        # d_FR(P, Q) = 2 * arccos(sum(sqrt(p_i * q_i)))
        # Using Bhattacharyya coefficient
        sqrt_probs = np.sqrt(probs)
        bc = np.sum(sqrt_probs[:-1] * sqrt_probs[1:], axis=1)  # (T-1,)
        bc = np.clip(bc, -1.0, 1.0)
        fisher_speeds = 2.0 * np.arccos(bc)  # (T-1,)

        # --- Entropy gradient norm under Fisher-Rao metric ---
        # (∇_FR H)^i = p_i * (-log p_i - 1)
        # ||∇_FR H||² = Σ p_i * (log p_i + 1)²
        log_probs = np.log(probs)
        grad_H_sq = np.sum(probs * (log_probs + 1.0)**2, axis=1)  # (T,)
        entropy_gradient_norms = np.sqrt(np.clip(grad_H_sq, 0, None))  # (T,)

        # Use the norm at the starting point of each step
        grad_norms = entropy_gradient_norms[:-1]  # (T-1,)

        # --- Commitment angle (in ξ = 2√p coordinates where Fisher metric is Euclidean) ---
        # Tangent vector: Δξ = ξ_{t+1} - ξ_t (in spherical embedding)
        # Entropy gradient in ξ-coords: (∂H/∂ξ_i) = (∂H/∂p_i)(∂p_i/∂ξ_i) = (-log p_i - 1)(ξ_i/2)
        xi = 2.0 * sqrt_probs  # (T, V)
        delta_xi = xi[1:] - xi[:-1]  # (T-1, V) tangent vectors

        # Entropy gradient in ξ-coords at each start point
        grad_H_xi = -0.5 * xi[:-1] * (log_probs[:-1] + 1.0)  # (T-1, V)

        # Angle between velocity and entropy gradient (Euclidean dot product in ξ-space)
        dot_product = np.sum(delta_xi * grad_H_xi, axis=1)  # (T-1,)
        norm_v = np.sqrt(np.sum(delta_xi**2, axis=1) + eps)  # (T-1,)
        norm_g = np.sqrt(np.sum(grad_H_xi**2, axis=1) + eps)  # (T-1,)

        cos_alpha = dot_product / (norm_v * norm_g)
        cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
        # Take absolute value — we care about alignment, not sign
        commitment_angles = np.arccos(np.abs(cos_alpha))  # (T-1,) in [0, π/2]

        # --- Fork detection: max |dα/dt| ---
        if len(commitment_angles) > 1:
            d_alpha = np.abs(np.diff(commitment_angles))
            # Smooth with a 3-point window to avoid noise spikes
            if len(d_alpha) >= 3:
                kernel = np.ones(3) / 3.0
                d_alpha_smooth = np.convolve(d_alpha, kernel, mode='same')
            else:
                d_alpha_smooth = d_alpha
            fork_loc = int(np.argmax(d_alpha_smooth)) + 1  # +1 because diff reduces length
        else:
            fork_loc = 0

        # --- Pre/post fork statistics ---
        if fork_loc > 0 and fork_loc < len(fisher_speeds) - 1:
            pre = slice(0, fork_loc)
            post = slice(fork_loc, None)
            pre_speed = float(np.mean(fisher_speeds[pre])) if fork_loc > 0 else 0.0
            post_speed = float(np.mean(fisher_speeds[post]))
            pre_angle = float(np.mean(commitment_angles[pre]))
            post_angle = float(np.mean(commitment_angles[post]))
            speed_ratio = post_speed / pre_speed if pre_speed > 0 else 0.0
        else:
            pre_speed = post_speed = float(np.mean(fisher_speeds))
            pre_angle = post_angle = float(np.mean(commitment_angles))
            speed_ratio = 1.0

        return FisherGeometry(
            n_tokens=T,
            vocab_size=V,
            fisher_speeds=fisher_speeds,
            commitment_angles=commitment_angles,
            entropy_gradient_norms=entropy_gradient_norms,
            entropy_rates=entropy_rates,
            fork_location=fork_loc,
            pre_fork_mean_speed=pre_speed,
            post_fork_mean_speed=post_speed,
            pre_fork_mean_angle=pre_angle,
            post_fork_mean_angle=post_angle,
            speed_ratio=speed_ratio,
        )

    @staticmethod
    def from_logits_tensor(logits: 'torch.Tensor', eps: float = 1e-10) -> 'FisherGeometry':
        """Compute from a (T, V) tensor of raw logits (pre-softmax)."""
        import torch
        import torch.nn.functional as F
        probs = F.softmax(logits.float(), dim=-1).cpu().numpy()
        return FisherGeometry.from_probs(probs, eps)

    def summary(self) -> str:
        """Human-readable summary of the geometric analysis."""
        lines = [
            f"Fisher Geometry: {self.n_tokens} tokens, vocab {self.vocab_size}",
            f"  Fork location: token {self.fork_location}",
            f"  Pre-fork:  v_F = {self.pre_fork_mean_speed:.4f}, α = {np.degrees(self.pre_fork_mean_angle):.1f}°",
            f"  Post-fork: v_F = {self.post_fork_mean_speed:.4f}, α = {np.degrees(self.post_fork_mean_angle):.1f}°",
            f"  Speed ratio (post/pre): {self.speed_ratio:.2f}",
        ]
        # Interpret
        if self.post_fork_mean_angle > np.pi / 4:
            lines.append("  → Post-fork velocity is commitment-driven (α > 45°)")
        else:
            lines.append("  → Post-fork velocity is still data-driven (α < 45°)")

        if self.speed_ratio > 1.5:
            lines.append("  → Shallow basin: model searching post-fork (high Fisher speed)")
        elif self.speed_ratio < 0.5:
            lines.append("  → Deep basin: stable commitment (low Fisher speed)")
        else:
            lines.append("  → Moderate basin depth")

        return "\n".join(lines)

    def as_dict(self) -> dict:
        """Export as dictionary for JSON serialization."""
        return {
            'n_tokens': self.n_tokens,
            'vocab_size': self.vocab_size,
            'fork_location': self.fork_location,
            'pre_fork_mean_speed': self.pre_fork_mean_speed,
            'post_fork_mean_speed': self.post_fork_mean_speed,
            'pre_fork_mean_angle': float(np.degrees(self.pre_fork_mean_angle)),
            'post_fork_mean_angle': float(np.degrees(self.post_fork_mean_angle)),
            'speed_ratio': self.speed_ratio,
            'fisher_speeds': self.fisher_speeds.tolist(),
            'commitment_angles': [float(np.degrees(a)) for a in self.commitment_angles],
            'entropy_rates': self.entropy_rates.tolist(),
        }


def analyze_text_geometry(
    model, tokenizer, text: str,
    chat_format: bool = True,
) -> Tuple[FisherGeometry, np.ndarray]:
    """
    Convenience: run a HuggingFace model on text and return Fisher geometry + entropies.

    Args:
        model: HuggingFace causal LM
        tokenizer: corresponding tokenizer
        text: text to analyze
        chat_format: whether to wrap in chat template

    Returns:
        (FisherGeometry, entropies) tuple
    """
    import torch
    import torch.nn.functional as F

    if chat_format:
        messages = [{"role": "assistant", "content": text}]
        formatted = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
    else:
        formatted = text

    input_ids = tokenizer(formatted, return_tensors="pt").input_ids
    input_ids = input_ids.to(model.device)

    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits[0, :-1]  # (T-1, V) — predict each next token

    probs = F.softmax(logits.float(), dim=-1)

    # Entropy for each position
    log_p = torch.log(probs + 1e-10)
    entropies = -(probs * log_p).sum(dim=-1).cpu().numpy()

    # Fisher geometry from probability trajectory
    geo = FisherGeometry.from_probs(probs.cpu().numpy())

    return geo, entropies
