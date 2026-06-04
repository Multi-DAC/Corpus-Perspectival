# Anakin × DreamerV3 — integration (reproducible)

We train Anakin on **NM512/dreamerv3-torch** (a clean PyTorch DreamerV3). That repo is a
clone-and-run research codebase, not a pip package, so we **vendor it gitignored** at
`anakin/third_party/dreamerv3-torch/` and keep only our integration here, tracked and
reproducible. The Dreamer *core* (`dreamer/models/networks/tools/parallel`) runs unmodified on
our 2025 stack (torch 2.11+cu128, Python 3.14, CUDA on the 5080); only the three artifacts below
are ours.

**Pinned upstream:** `https://github.com/NM512/dreamerv3-torch` @ `6ef8646d807cd10ce0c88e10a7e943211e7fc44c`

## Reproduce from scratch

```bash
cd anakin
git clone https://github.com/NM512/dreamerv3-torch.git third_party/dreamerv3-torch
cd third_party/dreamerv3-torch
git checkout 6ef8646d807cd10ce0c88e10a7e943211e7fc44c

# deps into the anakin venv (NOT the upstream pins — they want torch 2.4 / gym 0.22 / numpy 1.23;
# we run current torch + gymnasium and only need a few of them):
../../.venv/Scripts/python.exe -m pip install gymnasium "gym==0.22.0" "ruamel.yaml" tensorboard
#   gymnasium -> our sim/env.py;  gym 0.22 -> ONLY for the upstream env wrappers (spaces+Wrapper;
#   the NumPy-2 warning is harmless, our wrappers don't touch the deprecated bits);
#   ruamel.yaml + tensorboard -> config load + logging.

# apply our integration (copy the adapter, append the config, patch dreamer.py):
cp ../../integration/anakin_env_adapter.py envs/anakin.py
cat ../../integration/anakin_config.yaml >> configs.yaml
#   then apply the two dreamer.py edits documented in PATCHES.md
```

## The three artifacts

1. **`anakin_env_adapter.py`** → copied to `third_party/dreamerv3-torch/envs/anakin.py`.
   Bridges our Gymnasium `sim/env.py::AnakinEnv` (5-tuple) to the upstream old-gym dict
   contract (`reset()->obs_dict`, `step()->(obs,reward,done,info)`, obs `Dict({"image":...})`).
   Maps `done = terminated|truncated`, `is_terminal = terminated` (timeout is not terminal).

2. **`anakin_config.yaml`** → appended to `third_party/dreamerv3-torch/configs.yaml`.
   The `anakin:` config: vision-only encoder/decoder, single env on the 5080, the make-or-break
   smoke defaults (1 close gate, no DR, compile+video off), plus the sim knobs make_env reads
   (`anakin_gates`, `anakin_difficulty`, `anakin_spacing`, `anakin_env_device`).

3. **`PATCHES.md`** — the two small edits to upstream `dreamer.py`:
   (a) `make_env` gets an `anakin` suite branch; (b) `yaml.safe_load` → `yaml.YAML(typ="safe").load`
   (modern ruamel removed the module-level helper).

## Run

```bash
cd anakin/third_party/dreamerv3-torch
../../.venv/Scripts/python.exe -u dreamer.py --configs anakin --logdir ./logdir/smoke
```
`-u` (unbuffered) so progress/scores stream live instead of block-buffering to the log.
