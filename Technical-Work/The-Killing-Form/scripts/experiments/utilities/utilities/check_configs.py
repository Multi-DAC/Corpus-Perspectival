"""Quick config checker for architecture survey."""
from transformers import AutoConfig

models = [
    "cerebras/Cerebras-GPT-111M",
    "google/gemma-2-2b",
    "google/gemma-3-1b-pt",
    "google/gemma-3-4b-pt",
]

for name in models:
    try:
        config = AutoConfig.from_pretrained(name)
        n_heads = config.num_attention_heads
        d_model = config.hidden_size
        d_head = getattr(config, 'head_dim', d_model // n_heads)
        n_kv = getattr(config, 'num_key_value_heads', n_heads)
        n_layers = config.num_hidden_layers
        mtype = config.model_type
        parallel = getattr(config, 'use_parallel_residual', 'N/A')
        print(f"{name}")
        print(f"  type={mtype} heads={n_heads} kv={n_kv} d={d_model} d_head={d_head} layers={n_layers} parallel={parallel}")
    except Exception as e:
        print(f"{name}: {e}")
    print()
