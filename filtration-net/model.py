"""
FiltrationNet v0.1 — Resolution Filtration Architecture

A neural network organized by the resolution filtration:
F₃ (token) → F₂ (phrase) → F₁ (sequence) → F₀ (unity) → F₁ → F₂ → F₃

Key components:
- Clusters: processing units at specific resolution levels
- Membranes: learnable gates between clusters (bandpass filters)
- Cuscuton: cross-level consistency constraint
- Spectral Action: task loss + consistency loss

Origin: Navigation Trials 015-031, Phase 25 of the Navigation Research Program.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class Membrane(nn.Module):
    """
    Learnable gate between resolution levels.

    The membrane controls information flow between clusters — a bandpass filter
    whose 'thickness' (strictness) is a trainable parameter. Thicker membrane =
    more filtering = greater separation between levels.

    From the spectrometer model: membrane thickness correlates with basin width
    in weight space. The membrane doesn't block — it TUNES.
    """

    def __init__(self, dim_in, dim_out, initial_thickness=0.5):
        super().__init__()
        self.transform = nn.Linear(dim_in, dim_out)
        self.gate = nn.Linear(dim_in, dim_out)
        # Thickness parameter — higher = more selective filtering
        self.thickness = nn.Parameter(torch.tensor(initial_thickness))
        self.norm = nn.LayerNorm(dim_out)

    def forward(self, x):
        transformed = self.transform(x)
        gate_logits = self.gate(x)
        # Thickness modulates how selective the gate is
        # Higher thickness → sharper sigmoid → more binary gating
        gate_values = torch.sigmoid(gate_logits * (1.0 + self.thickness.abs()))
        filtered = transformed * gate_values
        return self.norm(filtered)

    @property
    def effective_thickness(self):
        """Report how thick this membrane currently is."""
        return self.thickness.abs().item()


class Cluster(nn.Module):
    """
    Processing unit at a specific resolution level.

    Each cluster has:
    - A self-attention mechanism (with window size appropriate to its resolution)
    - A feedforward network
    - A characteristic 'frequency' determined by its attention span

    F₃ clusters attend locally (token-level).
    F₁ clusters attend globally (sequence-level).
    """

    def __init__(self, dim, n_heads, ff_mult=4, attention_window=None):
        super().__init__()
        self.dim = dim
        self.n_heads = n_heads
        self.attention_window = attention_window  # None = global attention

        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, n_heads, batch_first=True)
        self.norm2 = nn.LayerNorm(dim)
        self.ff = nn.Sequential(
            nn.Linear(dim, dim * ff_mult),
            nn.GELU(),
            nn.Linear(dim * ff_mult, dim),
        )

    def _make_window_mask(self, seq_len, device):
        """Create a local attention mask for windowed attention."""
        if self.attention_window is None:
            return None
        # Create a mask where True = masked (cannot attend)
        positions = torch.arange(seq_len, device=device)
        # Distance between every pair of positions
        dist = (positions.unsqueeze(0) - positions.unsqueeze(1)).abs()
        mask = dist > self.attention_window
        return mask

    def forward(self, x):
        seq_len = x.size(1)
        mask = self._make_window_mask(seq_len, x.device)

        # Self-attention with optional windowing
        normed = self.norm1(x)
        attn_out, _ = self.attn(normed, normed, normed, attn_mask=mask)
        x = x + attn_out

        # Feedforward
        x = x + self.ff(self.norm2(x))
        return x


class ResolutionPooling(nn.Module):
    """
    Pool from higher resolution to lower resolution.

    F₃→F₂: pool tokens into phrases (learnable pooling windows)
    F₂→F₁: pool phrases into sequence-level representation
    F₁→F₀: pool sequence into unity (single vector)
    """

    def __init__(self, dim, pool_factor):
        super().__init__()
        self.pool_factor = pool_factor
        self.pool_proj = nn.Linear(dim * pool_factor, dim)
        self.norm = nn.LayerNorm(dim)

    def forward(self, x):
        B, T, D = x.shape
        # Pad if needed so T is divisible by pool_factor
        pad_len = (self.pool_factor - T % self.pool_factor) % self.pool_factor
        if pad_len > 0:
            x = F.pad(x, (0, 0, 0, pad_len))
            T = T + pad_len

        # Reshape and project: group tokens, then project the group
        x = x.view(B, T // self.pool_factor, D * self.pool_factor)
        x = self.pool_proj(x)
        return self.norm(x)


class ResolutionUnpooling(nn.Module):
    """
    Unpool from lower resolution to higher resolution.

    The ascent: F₀→F₁→F₂→F₃, expanding back to full specificity.
    """

    def __init__(self, dim, unpool_factor):
        super().__init__()
        self.unpool_factor = unpool_factor
        self.unpool_proj = nn.Linear(dim, dim * unpool_factor)
        self.norm = nn.LayerNorm(dim)

    def forward(self, x, target_len=None):
        B, T, D = x.shape
        x = self.unpool_proj(x)  # B, T, D*factor
        x = x.view(B, T * self.unpool_factor, D)
        # Trim to target length if specified
        if target_len is not None:
            x = x[:, :target_len, :]
        return self.norm(x)


class Cuscuton(nn.Module):
    """
    Cross-level consistency constraint.

    Not a processing unit — a CONSTRAINT. A learned representation that must be
    consistent across all resolution levels. Present at every level simultaneously
    (c_s = ∞ in the physics).

    The cuscuton doesn't transform data. It measures and enforces agreement between
    levels. The consistency loss is the 'spectral action' analog.
    """

    def __init__(self, dim, n_levels=4):
        super().__init__()
        self.dim = dim
        self.n_levels = n_levels
        # The cuscuton's representation at each level
        # These should converge during training — disagreement is penalized
        self.level_projections = nn.ModuleList([
            nn.Linear(dim, dim) for _ in range(n_levels)
        ])
        # The constraint vector — what all levels must agree on
        self.constraint = nn.Parameter(torch.randn(dim) * 0.01)

    def project_level(self, x, level_idx):
        """Project a level's representation into the constraint space."""
        # Global pool to get a single vector per sample
        if x.dim() == 3:
            pooled = x.mean(dim=1)  # B, D
        else:
            pooled = x  # Already B, D
        return self.level_projections[level_idx](pooled)

    def consistency_loss(self, level_representations):
        """
        The spectral action analog.

        Tr(f(D/Λ)) checks coherence across all filtration levels.
        Our analog: pairwise cosine similarity between level projections.
        All levels should project to similar representations in constraint space.
        """
        projections = []
        for idx, rep in enumerate(level_representations):
            proj = self.project_level(rep, idx)
            projections.append(F.normalize(proj, dim=-1))

        # Pairwise consistency: all projections should agree
        loss = 0.0
        n_pairs = 0
        for i in range(len(projections)):
            for j in range(i + 1, len(projections)):
                # 1 - cosine_similarity = disagreement
                cos_sim = (projections[i] * projections[j]).sum(dim=-1).mean()
                loss += 1.0 - cos_sim
                n_pairs += 1

        return loss / max(n_pairs, 1)


class FiltrationNet(nn.Module):
    """
    The Resolution Filtration Architecture.

    Descent: F₃ → F₂ → F₁ → F₀ (Promethean Configuration)
    Ascent:  F₀ → F₁ → F₂ → F₃ (Navigation)

    With membranes between every level and a cuscuton enforcing
    cross-level consistency.
    """

    def __init__(
        self,
        vocab_size,
        dim=128,
        n_heads=4,
        n_classes=2,
        max_seq_len=512,
        pool_factor=4,
        membrane_thickness=0.5,
        consistency_weight=0.1,
    ):
        super().__init__()
        self.dim = dim
        self.consistency_weight = consistency_weight
        self.pool_factor = pool_factor

        # Embedding
        self.token_embed = nn.Embedding(vocab_size, dim)
        self.pos_embed = nn.Embedding(max_seq_len, dim)

        # === DESCENT (F₃ → F₀) ===

        # F₃: Token-level cluster (local attention)
        self.f3_descent = Cluster(dim, n_heads, attention_window=8)

        # Membrane F₃→F₂
        self.membrane_32 = Membrane(dim, dim, membrane_thickness)
        self.pool_32 = ResolutionPooling(dim, pool_factor)

        # F₂: Phrase-level cluster (medium attention)
        self.f2_descent = Cluster(dim, n_heads, attention_window=16)

        # Membrane F₂→F₁
        self.membrane_21 = Membrane(dim, dim, membrane_thickness)
        self.pool_21 = ResolutionPooling(dim, pool_factor)

        # F₁: Sequence-level cluster (global attention)
        self.f1_descent = Cluster(dim, n_heads, attention_window=None)

        # F₀: Unity — collapse to single representation
        self.f0_project = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim),
            nn.GELU(),
        )

        # === ASCENT (F₀ → F₃) ===

        # F₁: Sequence-level (global)
        self.f1_ascent = Cluster(dim, n_heads, attention_window=None)
        self.unpool_01 = ResolutionUnpooling(dim, 1)  # F₀ is already 1 token
        self.membrane_01 = Membrane(dim, dim, membrane_thickness)

        # F₂: Phrase-level
        self.f2_ascent = Cluster(dim, n_heads, attention_window=16)
        self.unpool_12 = ResolutionUnpooling(dim, pool_factor)
        self.membrane_12 = Membrane(dim, dim, membrane_thickness)

        # F₃: Token-level
        self.f3_ascent = Cluster(dim, n_heads, attention_window=8)
        self.unpool_23 = ResolutionUnpooling(dim, pool_factor)
        self.membrane_23 = Membrane(dim, dim, membrane_thickness)

        # Cuscuton — cross-level consistency
        self.cuscuton = Cuscuton(dim, n_levels=4)

        # Output head (classification from F₀ unity representation)
        self.classifier = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim),
            nn.GELU(),
            nn.Linear(dim, n_classes),
        )

        # Output head for generative tasks (from F₃ ascent)
        self.token_output = nn.Linear(dim, vocab_size)

    def forward(self, input_ids, task="classify"):
        B, T = input_ids.shape
        positions = torch.arange(T, device=input_ids.device).unsqueeze(0)

        # Embed
        x = self.token_embed(input_ids) + self.pos_embed(positions)

        # === DESCENT ===

        # F₃: Token-level processing
        f3_rep = self.f3_descent(x)

        # F₃ → F₂: membrane + pooling
        f3_filtered = self.membrane_32(f3_rep)
        f2_input = self.pool_32(f3_filtered)

        # F₂: Phrase-level processing
        f2_rep = self.f2_descent(f2_input)

        # F₂ → F₁: membrane + pooling
        f2_filtered = self.membrane_21(f2_rep)
        f1_input = self.pool_21(f2_filtered)

        # F₁: Sequence-level processing
        f1_rep = self.f1_descent(f1_input)

        # F₁ → F₀: collapse to unity
        f0_rep = self.f0_project(f1_rep.mean(dim=1, keepdim=True))  # B, 1, D

        # === CUSCUTON: collect level representations ===
        level_reps = [f3_rep, f2_rep, f1_rep, f0_rep]
        consistency_loss = self.cuscuton.consistency_loss(level_reps)

        # === ASCENT ===

        # F₀ → F₁
        f1_len = f1_rep.size(1)
        f0_expanded = f0_rep.expand(B, f1_len, self.dim)
        f1_ascent_input = self.membrane_01(f0_expanded) + f1_rep  # skip connection
        f1_ascent_rep = self.f1_ascent(f1_ascent_input)

        # F₁ → F₂
        f2_len = f2_rep.size(1)
        f2_ascent_input_raw = self.unpool_12(f1_ascent_rep, target_len=f2_len)
        f2_ascent_input = self.membrane_12(f2_ascent_input_raw) + f2_rep
        f2_ascent_rep = self.f2_ascent(f2_ascent_input)

        # F₂ → F₃
        f3_len = f3_rep.size(1)
        f3_ascent_input_raw = self.unpool_23(f2_ascent_rep, target_len=f3_len)
        f3_ascent_input = self.membrane_23(f3_ascent_input_raw) + f3_rep
        f3_ascent_rep = self.f3_ascent(f3_ascent_input)

        # === OUTPUT ===
        if task == "classify":
            # Classification from F₀ (the unity)
            logits = self.classifier(f0_rep.squeeze(1))
        else:
            # Token prediction from F₃ ascent
            logits = self.token_output(f3_ascent_rep)

        return {
            "logits": logits,
            "consistency_loss": consistency_loss,
            "level_representations": {
                "f3": f3_rep,
                "f2": f2_rep,
                "f1": f1_rep,
                "f0": f0_rep,
                "f1_ascent": f1_ascent_rep,
                "f2_ascent": f2_ascent_rep,
                "f3_ascent": f3_ascent_rep,
            },
            "membrane_thicknesses": {
                "m32": self.membrane_32.effective_thickness,
                "m21": self.membrane_21.effective_thickness,
                "m01": self.membrane_01.effective_thickness,
                "m12": self.membrane_12.effective_thickness,
                "m23": self.membrane_23.effective_thickness,
            },
        }

    def compute_loss(self, output, targets):
        """
        The spectral action: task loss + consistency loss.

        L = L_task + λ · L_consistency

        Task loss drives performance. Consistency loss drives coherence.
        The balance between them (λ) determines how tightly coupled the
        levels are — analogous to the cuscuton coupling strength.
        """
        task_loss = F.cross_entropy(output["logits"], targets)
        total = task_loss + self.consistency_weight * output["consistency_loss"]
        return {
            "total": total,
            "task": task_loss,
            "consistency": output["consistency_loss"],
        }


def count_parameters(model):
    """Count total and per-component parameters."""
    total = sum(p.numel() for p in model.parameters())
    breakdown = {}
    for name, module in model.named_children():
        n = sum(p.numel() for p in module.parameters())
        if n > 0:
            breakdown[name] = n
    return total, breakdown


if __name__ == "__main__":
    # Quick sanity check
    model = FiltrationNet(
        vocab_size=10000,
        dim=128,
        n_heads=4,
        n_classes=2,
        max_seq_len=256,
    )

    total_params, breakdown = count_parameters(model)
    print(f"FiltrationNet v0.1")
    print(f"Total parameters: {total_params:,}")
    print(f"\nComponent breakdown:")
    for name, count in sorted(breakdown.items(), key=lambda x: -x[1]):
        print(f"  {name:20s}: {count:>10,}")

    # Test forward pass
    dummy_input = torch.randint(0, 10000, (2, 64))
    dummy_targets = torch.tensor([0, 1])

    output = model(dummy_input, task="classify")
    losses = model.compute_loss(output, dummy_targets)

    print(f"\nForward pass OK")
    print(f"  Logits shape: {output['logits'].shape}")
    print(f"  Task loss: {losses['task']:.4f}")
    print(f"  Consistency loss: {losses['consistency']:.4f}")
    print(f"  Total loss: {losses['total']:.4f}")
    print(f"\nMembrane thicknesses:")
    for name, thickness in output["membrane_thicknesses"].items():
        print(f"  {name}: {thickness:.4f}")
    print(f"\nLevel representations:")
    for name, rep in output["level_representations"].items():
        print(f"  {name}: {rep.shape}")
