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

## 3. Batched maneuver env — approach A (Phase 3)

Phase 3 trains on ONE `BatchedManeuverEnv` (N drones, one batched dynamics+render per tick on the
5080) presented to `tools.simulate` as N thunked handles — NOT N OS processes. The handles already
return thunks (like `Damy`), so they must skip the `Damy`/`Parallel` wrap. New tracked artifact:
`integration/batched_sim_adapter.py` → copied to `third_party/dreamerv3-torch/envs/anakin_batched.py`
(it replicates the load-bearing wrappers the batched path bypasses: `SelectAction` dict-action
unwrap + per-episode `UUID` ids; `NormalizeActions`/`TimeLimit` are identity / already-internal).

In `main(config)`, replace the `train_envs/eval_envs` construction (`make_env` list + `Damy`) with a
suite branch on `anakinb`:

```python
    if config.task.split("_", 1)[0] == "anakinb":
        import envs.anakin_batched as anakin_batched
        train_adapter = anakin_batched.make_batched(config, seed_offset=0)
        eval_adapter = anakin_batched.make_batched(config, seed_offset=10_000)
        train_envs = train_adapter.handles      # already thunked — no Damy/Parallel wrap
        eval_envs = eval_adapter.handles
    else:
        # ... original make_env list + Parallel/Damy wrap unchanged ...
```

Config: append the `anakin_maneuver` block (`integration/anakin_config.yaml`) to `configs.yaml`
(`task: 'anakinb_train'`, `envs` = drone batch size, `anakin_env_device: 'cuda'`). Run:
`../../.venv/Scripts/python.exe -u dreamer.py --configs anakin_maneuver --logdir ./logdir/run`.
Verified: world model takes gradient steps on the batched env (model_loss/image_loss/kl/actor/value
all live; episodes collect through the adapter). Correctness gated upstream by
`integration/test_batched_parity.py` (index integrity + reset isolation + real tools.simulate smoke).

## Notes / harmless warnings observed
- `gym` prints a NumPy-2.0 unmaintained warning on import — only the env *wrappers* use gym
  (spaces + Wrapper); they don't touch the deprecated paths.
- `torch.cuda.amp.autocast/GradScaler` deprecation FutureWarnings from `models.py`/`tools.py` —
  cosmetic on torch 2.11; training runs correctly. (Upgrade to `torch.amp.autocast('cuda', ...)`
  if we ever want them silenced.)
