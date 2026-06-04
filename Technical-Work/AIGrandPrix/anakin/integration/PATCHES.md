# dreamer.py patches (upstream @ 6ef8646)

Two small edits to `third_party/dreamerv3-torch/dreamer.py`.

## 1. `make_env` — add the `anakin` suite branch

In `make_env(config, mode, id)`, immediately before the final `else: raise NotImplementedError(suite)`:

```python
    elif suite == "anakin":
        import envs.anakin as anakin

        env = anakin.Anakin(
            task,
            size=config.size,
            n_gates=config.anakin_gates,
            max_steps=config.time_limit,
            difficulty=config.anakin_difficulty,
            spacing=config.anakin_spacing,
            env_device=config.anakin_env_device,
            seed=config.seed + id,
        )
        env = wrappers.NormalizeActions(env)
```

(`NormalizeActions` is an identity for us — our action space is already `[-1,1]^4` — but it keeps
the chain identical to the dmc path and harmless.)

## 2. Config load — modern ruamel.yaml

ruamel.yaml removed the module-level `safe_load()`. In `__main__`:

```python
# was:  configs = yaml.safe_load((pathlib.Path(sys.argv[0]).parent / "configs.yaml").read_text())
configs = yaml.YAML(typ="safe", pure=True).load(
    (pathlib.Path(sys.argv[0]).parent / "configs.yaml").read_text()
)
```

## Notes / harmless warnings observed
- `gym` prints a NumPy-2.0 unmaintained warning on import — only the env *wrappers* use gym
  (spaces + Wrapper); they don't touch the deprecated paths.
- `torch.cuda.amp.autocast/GradScaler` deprecation FutureWarnings from `models.py`/`tools.py` —
  cosmetic on torch 2.11; training runs correctly. (Upgrade to `torch.amp.autocast('cuda', ...)`
  if we ever want them silenced.)
