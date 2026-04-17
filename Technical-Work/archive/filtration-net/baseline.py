"""
Baseline Transformer — same parameter budget, no filtration.

Standard stacked transformer for fair comparison against FiltrationNet.
Same embedding dim, similar parameter count, same task.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class BaselineTransformer(nn.Module):
    """
    Standard transformer classifier.
    Stacked identical layers (no resolution separation, no membranes,
    no consistency constraint). The F₃-only architecture.
    """

    def __init__(
        self,
        vocab_size,
        dim=128,
        n_heads=4,
        n_layers=6,
        n_classes=2,
        max_seq_len=512,
        ff_mult=4,
    ):
        super().__init__()
        self.dim = dim
        self.token_embed = nn.Embedding(vocab_size, dim)
        self.pos_embed = nn.Embedding(max_seq_len, dim)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=dim,
            nhead=n_heads,
            dim_feedforward=dim * ff_mult,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.classifier = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim),
            nn.GELU(),
            nn.Linear(dim, n_classes),
        )

    def forward(self, input_ids, task="classify"):
        B, T = input_ids.shape
        positions = torch.arange(T, device=input_ids.device).unsqueeze(0)
        x = self.token_embed(input_ids) + self.pos_embed(positions)
        x = self.encoder(x)

        # Pool to single vector (mean pooling, like F₀)
        pooled = x.mean(dim=1)
        logits = self.classifier(pooled)

        return {
            "logits": logits,
            "consistency_loss": torch.tensor(0.0, device=input_ids.device),
            "hidden_states": x,
        }

    def compute_loss(self, output, targets):
        task_loss = F.cross_entropy(output["logits"], targets)
        return {
            "total": task_loss,
            "task": task_loss,
            "consistency": output["consistency_loss"],
        }


if __name__ == "__main__":
    model = BaselineTransformer(vocab_size=10000, dim=128, n_heads=4, n_layers=6)
    total = sum(p.numel() for p in model.parameters())
    print(f"Baseline Transformer: {total:,} parameters")

    dummy = torch.randint(0, 10000, (2, 64))
    targets = torch.tensor([0, 1])
    output = model(dummy)
    losses = model.compute_loss(output, targets)
    print(f"Forward pass OK — logits: {output['logits'].shape}, loss: {losses['total']:.4f}")
