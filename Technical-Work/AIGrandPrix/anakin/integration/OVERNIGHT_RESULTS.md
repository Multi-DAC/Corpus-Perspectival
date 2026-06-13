
# Overnight results — 2026-06-12 00:30:39

**Fine-tune outcome:** `complete` — [carry] complete: 4 batches, best_return=2142.5339498519897

## holdout_gate.py — P224 appearance gate (pre-registered PASS: restyle-ft FD < 0.5 x band-ft FD)

*2026-06-12 00:31:59 — exit 0, 0.3 min*

```
frames: official(held-out)=20  restyled(fresh)=20
Encoder CNN shapes: {'image': (64, 64, 3)}
Encoder MLP shapes: {}
Decoder CNN shapes: {'image': (64, 64, 3)}
Decoder MLP shapes: {}
Optimizer model_opt has 15686787 variables.
Optimizer actor_opt has 1054728 variables.
Optimizer value_opt has 1181439 variables.
DreamerPilot: C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_band_ft\best.pt loaded on cuda:0 (19,104,393 params)
[band-ft (pre-restyle)] FD(official <-> restyled) = 131.3   recon_mse: official=unavailable (RuntimeError: permute(sparse_coo): number of dimensions in the tensor input does not match the length of the desired ordering of dimensions i.e. input.dim() = 4 is not equal to len(dims) = 5)  restyled=unavailable (RuntimeError: permute(sparse_coo): number of dimensions in the tensor input does not match the length of the desired ordering of dimensions i.e. input.dim() = 4 is not equal to len(dims) = 5)
Encoder CNN shapes: {'image': (64, 64, 3)}
Encoder MLP shapes: {}
Decoder CNN shapes: {'image': (64, 64, 3)}
Decoder MLP shapes: {}
Optimizer model_opt has 15686787 variables.
Optimizer actor_opt has 1054728 variables.
Optimizer value_opt has 1181439 variables.
DreamerPilot: C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_restyle_ft\best.pt loaded on cuda:0 (19,104,393 params)
[restyle-ft] FD(official <-> restyled) = 139.5   recon_mse: official=unavailable (RuntimeError: permute(sparse_coo): number of dimensions in the tensor input does not match the length of the desired ordering of dimensions i.e. input.dim() = 4 is not equal to len(dims) = 5)  restyled=unavailable (RuntimeError: permute(sparse_coo): number of dimensions in the tensor input does not match the length of the desired ordering of dimensions i.e. input.dim() = 4 is not equal to len(dims) = 5)

GATE: FD ratio (restyle-ft / band-ft) = 1.063
PRE-REGISTERED PASS: ratio < 0.5  (restyle at least halves the embedding-space domain gap on SEALED official frames)
VERDICT: FAIL

--- stderr ---
Gym has been unmaintained since 2022 and does not support NumPy 2.0 amongst other critical functionality.
Please upgrade to Gymnasium, the maintained drop-in replacement of Gym, or contact the authors of your software and request that they upgrade.
See the migration guide at https://gymnasium.farama.org/introduction/migration_guide/ for additional information.
C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\tools.py:749: FutureWarning: `torch.cuda.amp.GradScaler(args...)` is deprecated. Please use `torch.amp.GradScaler('cuda', args...)` instead.
  self._scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\models.py:179: UserWarning: To copy construct from a tensor, it is recommended to use sourceTensor.detach().clone() or sourceTensor.detach().clone().requires_grad_(True), rather than torch.tensor(sourceTensor).
  k: torch.tensor(v, device=self._config.device, dtype=torch.float32)
```

## translation_rehearsal.py — 10 episodes off maneuver_restyle_ft/best.pt

*2026-06-12 00:34:59 — exit 0, 3.0 min*

```
Encoder CNN shapes: {'image': (64, 64, 3)}
Encoder MLP shapes: {}
Decoder CNN shapes: {'image': (64, 64, 3)}
Decoder MLP shapes: {}
Optimizer model_opt has 15686787 variables.
Optimizer actor_opt has 1054728 variables.
Optimizer value_opt has 1181439 variables.
DreamerPilot: C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_restyle_ft\best.pt loaded on cuda:0 (19,104,393 params)

=== direct (10 eps) ===
  [direct] seed=1000  return= +182.99  gates=2  steps=133
  [direct] seed=1001  return= +376.76  gates=3  steps=157
  [direct] seed=1002  return= +637.52  gates=4  steps=158
  [direct] seed=1003  return= +200.07  gates=2  steps=83
  [direct] seed=1004  return=  -17.49  gates=1  steps=47
  [direct] seed=1005  return=  -14.25  gates=1  steps=69
  [direct] seed=1006  return= +864.08  gates=5  steps=266
  [direct] seed=1007  return=   -1.87  gates=1  steps=146
  [direct] seed=1008  return=  -20.54  gates=1  steps=55
  [direct] seed=1009  return=  -14.83  gates=1  steps=67

=== band (10 eps) ===
  [band] seed=1000  return= +181.64  gates=2  steps=95
  [band] seed=1001  return= +608.82  gates=4  steps=154
  [band] seed=1002  return= +184.29  gates=2  steps=94
  [band] seed=1003  return=   +0.64  gates=1  steps=67
  [band] seed=1004  return=  -15.34  gates=1  steps=72
  [band] seed=1005  return= +250.19  gates=2  steps=142
  [band] seed=1006  return=+1706.04  gates=9  steps=422
  [band] seed=1007  return=+4845.41  gates=25  steps=1200
  [band] seed=1008  return= +580.33  gates=4  steps=172
  [band] seed=1009  return= +383.59  gates=3  steps=111

=== blur (10 eps) ===
  [blur] seed=1000  return= +159.13  gates=2  steps=82
  [blur] seed=1001  return= +351.63  gates=3  steps=124
  [blur] seed=1002  return= +580.18  gates=4  steps=211
  [blur] seed=1003  return= +653.69  gates=4  steps=178
  [blur] seed=1004  return=  -18.36  gates=1  steps=56
  [blur] seed=1005  return=+1024.03  gates=6  steps=525
  [blur] seed=1006  return=+1426.12  gates=8  steps=489
  [blur] seed=1007  return=   -6.30  gates=1  steps=87
  [blur] seed=1008  return= +210.53  gates=2  steps=109
  [blur] seed=1009  return= +188.11  gates=2  steps=79

=== roundtrip (10 eps) ===
  [roundtrip] seed=1000  return= +183.12  gates=2  steps=153
  [roundtrip] seed=1001  return= +377.47  gates=3  steps=132
  [roundtrip] seed=1002  return= +569.22  gates=4  steps=165
  [roundtrip] seed=1003  return=  -20.41  gates=1  steps=64
  [roundtrip] seed=1004  return= +415.47  gates=3  steps=93
  [roundtrip] seed=1005  return= +360.41  gates=3  steps=336
  [roundtrip] seed=1006  return=+1059.24  gates=6  steps=305
  [roundtrip] seed=1007  return= +198.61  gates=2  steps=169
  [roundtrip] seed=1008  return=+3442.33  gates=19  steps=987
  [roundtrip] seed=1009  return= +379.34  gates=3  steps=135

=== TRANSLATION REHEARSAL SUMMARY ===
(direct = training-eval anchor; band = VFoV crop only; blur = resample only; roundtrip = full adapter path. Training-run best batch metric: +256.28)
direct   : return  +219.24 +/- 298.16   gates   2.1   delta-vs-direct   +0.0%
band     : return  +872.56 +/- 1405.68   gates   5.3   delta-vs-direct +298.0%
blur     : return  +456.88 +/- 445.88   gates   3.3   delta-vs-direct +108.4%
roundtrip: return  +696.48 +/- 954.31   gates   4.6   delta-vs-direct +217.7%

--- stderr ---
Gym has been unmaintained since 2022 and does not support NumPy 2.0 amongst other critical functionality.
Please upgrade to Gymnasium, the maintained drop-in replacement of Gym, or contact the authors of your software and request that they upgrade.
See the migration guide at https://gymnasium.farama.org/introduction/migration_guide/ for additional information.
C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\tools.py:749: FutureWarning: `torch.cuda.amp.GradScaler(args...)` is deprecated. Please use `torch.amp.GradScaler('cuda', args...)` instead.
  self._scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
```

---
*Watcher finished 2026-06-12 00:34:59. Gate step succeeded; flight #2 decision belongs to the waking stream + Clayton.*
