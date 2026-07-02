
# Informed-Dreamer (route 3) fine-tune — results — 2026-06-16 17:38:02

**Outcome:** `complete` — [carry] complete: 2 batches, best_return=1766.5067790985108

## holdout_gate_v2.py (INFORMED) — official-harvest vs rendered, baseline vs informed-ft

*2026-06-16 17:39:25 — exit 0, 0.4 min*

```
frames: official=400  restyled(fresh)=200
Encoder CNN shapes: {'image': (64, 64, 3)}
Encoder MLP shapes: {}
Decoder CNN shapes: {'image': (64, 64, 3)}
Decoder MLP shapes: {}
Optimizer model_opt has 15686787 variables.
Optimizer actor_opt has 1054728 variables.
Optimizer value_opt has 1181439 variables.
DreamerPilot: C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_band_ft\best.pt loaded on cuda:0 (19,104,393 params)
[band-ft (pre-adapt)] n=400 D=4096  ⚠ n<=D: cov-term UNRELIABLE
    mean_term = 24.44   (trust at any n)
    cov_term  = 47.03
    total     = 71.47
Encoder CNN shapes: {'image': (64, 64, 3)}
Encoder MLP shapes: {}
Decoder CNN shapes: {'image': (64, 64, 3)}
Decoder MLP shapes: {}
Optimizer model_opt has 15686787 variables.
Optimizer actor_opt has 1054728 variables.
Optimizer value_opt has 1181439 variables.
[DreamerPilot] ignoring 51 extra ckpt keys (e.g. informed priv_state head): ['_wm.heads.decoder._mlp.layers.Decoder_linear0.weight', '_wm.heads.decoder._mlp.layers.Decoder_norm0.weight', '_wm.heads.decoder._mlp.layers.Decoder_norm0.bias']
DreamerPilot: C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_informed_ft\best.pt loaded on cuda:0 (19,104,393 params)
[adapted] n=400 D=4096  ⚠ n<=D: cov-term UNRELIABLE
    mean_term = 33.23   (trust at any n)
    cov_term  = 64.28
    total     = 97.51

GATE v2 — decomposed:
  MEAN-TERM ratio (adapted/band-ft) = 1.360   <-- PRIMARY (robust)
  total ratio                       = 1.364   (secondary; cov-term noisy, n<=D)
PRE-REGISTERED PASS: MEAN-TERM ratio < 0.5 (adaptation at least halves the official-domain gap on the trustworthy term)
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

## translation_rehearsal.py (INFORMED) — 10 eps off maneuver_informed_ft/best.pt

*2026-06-16 17:42:04 — exit 0, 2.6 min*

```
Encoder CNN shapes: {'image': (64, 64, 3)}
Encoder MLP shapes: {}
Decoder CNN shapes: {'image': (64, 64, 3)}
Decoder MLP shapes: {}
Optimizer model_opt has 15686787 variables.
Optimizer actor_opt has 1054728 variables.
Optimizer value_opt has 1181439 variables.
[DreamerPilot] ignoring 51 extra ckpt keys (e.g. informed priv_state head): ['_wm.heads.decoder._mlp.layers.Decoder_linear0.weight', '_wm.heads.decoder._mlp.layers.Decoder_norm0.weight', '_wm.heads.decoder._mlp.layers.Decoder_norm0.bias']
DreamerPilot: C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_informed_ft\best.pt loaded on cuda:0 (19,104,393 params)

=== direct (10 eps) ===
  [direct] seed=1000  return=+1219.05  gates=7  steps=324
  [direct] seed=1001  return=+1011.22  gates=6  steps=264
  [direct] seed=1002  return= +840.47  gates=5  steps=181
  [direct] seed=1003  return= +436.77  gates=3  steps=134
  [direct] seed=1004  return= +161.86  gates=2  steps=110
  [direct] seed=1005  return= +210.15  gates=2  steps=122
  [direct] seed=1006  return= +894.79  gates=5  steps=244
  [direct] seed=1007  return=+1030.74  gates=6  steps=267
  [direct] seed=1008  return= +211.26  gates=2  steps=112
  [direct] seed=1009  return=   -8.36  gates=1  steps=68

=== band (10 eps) ===
  [band] seed=1000  return= +584.26  gates=4  steps=229
  [band] seed=1001  return=+1048.27  gates=6  steps=210
  [band] seed=1002  return= +869.89  gates=5  steps=187
  [band] seed=1003  return= +432.81  gates=3  steps=142
  [band] seed=1004  return=   -1.82  gates=1  steps=59
  [band] seed=1005  return=+1711.77  gates=9  steps=476
  [band] seed=1006  return=+1598.33  gates=8  steps=349
  [band] seed=1007  return=+5254.89  gates=26  steps=1034
  [band] seed=1008  return=+1439.40  gates=8  steps=419
  [band] seed=1009  return= +988.40  gates=6  steps=189

=== blur (10 eps) ===
  [blur] seed=1000  return= +576.66  gates=4  steps=241
  [blur] seed=1001  return= +384.50  gates=3  steps=128
  [blur] seed=1002  return= +561.02  gates=4  steps=172
  [blur] seed=1003  return= +338.25  gates=3  steps=126
  [blur] seed=1004  return=  -17.68  gates=1  steps=55
  [blur] seed=1005  return= +217.46  gates=2  steps=130
  [blur] seed=1006  return=+1419.38  gates=8  steps=448
  [blur] seed=1007  return= +941.92  gates=6  steps=301
  [blur] seed=1008  return=+1845.24  gates=11  steps=686
  [blur] seed=1009  return=  -18.50  gates=1  steps=105

=== roundtrip (10 eps) ===
  [roundtrip] seed=1000  return= +178.49  gates=2  steps=92
  [roundtrip] seed=1001  return= +366.26  gates=3  steps=114
  [roundtrip] seed=1002  return= +385.64  gates=3  steps=151
  [roundtrip] seed=1003  return= +376.91  gates=3  steps=113
  [roundtrip] seed=1004  return=  -18.18  gates=1  steps=54
  [roundtrip] seed=1005  return= +189.95  gates=2  steps=114
  [roundtrip] seed=1006  return= +962.83  gates=6  steps=386
  [roundtrip] seed=1007  return= +545.57  gates=4  steps=284
  [roundtrip] seed=1008  return= +194.18  gates=2  steps=147
  [roundtrip] seed=1009  return=   -0.64  gates=1  steps=54

=== TRANSLATION REHEARSAL SUMMARY ===
(direct = training-eval anchor; band = VFoV crop only; blur = resample only; roundtrip = full adapter path. Training-run best batch metric: +256.28)
direct   : return  +600.80 +/- 421.23   gates   3.9   delta-vs-direct   +0.0%
band     : return +1392.62 +/- 1383.40   gates   7.6   delta-vs-direct +131.8%
blur     : return  +624.83 +/- 579.67   gates   4.3   delta-vs-direct   +4.0%
roundtrip: return  +318.10 +/- 272.71   gates   2.7   delta-vs-direct  -47.1%

--- stderr ---
Gym has been unmaintained since 2022 and does not support NumPy 2.0 amongst other critical functionality.
Please upgrade to Gymnasium, the maintained drop-in replacement of Gym, or contact the authors of your software and request that they upgrade.
See the migration guide at https://gymnasium.farama.org/introduction/migration_guide/ for additional information.
C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\tools.py:749: FutureWarning: `torch.cuda.amp.GradScaler(args...)` is deprecated. Please use `torch.amp.GradScaler('cuda', args...)` instead.
  self._scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
```

---
*Watcher finished 2026-06-16 17:42:04. PRIMARY = the holdout-gate MEAN-TERM ratio (informed/band-ft; pass < 0.5 means grounding the latent in geometry closed the official-domain gap). The rehearsal roundtrip RETURN is the fly go/no-go for flight #4. If the gate moves but doesn't pass, route 3 helps partially -> stack route 1 (renderer appearance-DR: illumination + bg-texture). Decision = waking stream + Clayton.*
