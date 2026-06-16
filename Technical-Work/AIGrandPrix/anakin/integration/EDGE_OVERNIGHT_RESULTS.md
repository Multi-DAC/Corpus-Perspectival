
# Edge fine-tune — overnight results — 2026-06-16 06:34:44

**Outcome:** `complete` — [carry] complete: 4 batches, best_return=2357.346475982666

## holdout_gate_v2.py (EDGE) — official-harvest vs rendered, baseline vs edge-ft

*2026-06-16 06:36:08 — exit 0, 0.4 min (ANAKIN_EDGE=1)*

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
    mean_term = 2.82   (trust at any n)
    cov_term  = 17.82
    total     = 20.64
Encoder CNN shapes: {'image': (64, 64, 3)}
Encoder MLP shapes: {}
Decoder CNN shapes: {'image': (64, 64, 3)}
Decoder MLP shapes: {}
Optimizer model_opt has 15686787 variables.
Optimizer actor_opt has 1054728 variables.
Optimizer value_opt has 1181439 variables.
DreamerPilot: C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_edge_ft\best.pt loaded on cuda:0 (19,104,393 params)
[adapted] n=400 D=4096  ⚠ n<=D: cov-term UNRELIABLE
    mean_term = 44.65   (trust at any n)
    cov_term  = 77.79
    total     = 122.44

GATE v2 — decomposed:
  MEAN-TERM ratio (adapted/band-ft) = 15.807   <-- PRIMARY (robust)
  total ratio                       = 5.931   (secondary; cov-term noisy, n<=D)
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

## translation_rehearsal.py (EDGE) — 10 eps off maneuver_edge_ft/best.pt

*2026-06-16 06:37:21 — exit 0, 1.2 min (ANAKIN_EDGE=1)*

```
Encoder CNN shapes: {'image': (64, 64, 3)}
Encoder MLP shapes: {}
Decoder CNN shapes: {'image': (64, 64, 3)}
Decoder MLP shapes: {}
Optimizer model_opt has 15686787 variables.
Optimizer actor_opt has 1054728 variables.
Optimizer value_opt has 1181439 variables.
DreamerPilot: C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_edge_ft\best.pt loaded on cuda:0 (19,104,393 params)

=== direct (10 eps) ===
  [direct] seed=1000  return=  -21.48  gates=1  steps=72
  [direct] seed=1001  return=  -15.62  gates=1  steps=6
  [direct] seed=1002  return=  -16.62  gates=1  steps=29
  [direct] seed=1003  return=   -0.26  gates=1  steps=66
  [direct] seed=1004  return=   +1.12  gates=1  steps=41
  [direct] seed=1005  return=   -8.03  gates=1  steps=103
  [direct] seed=1006  return=  -20.12  gates=1  steps=83
  [direct] seed=1007  return= +223.41  gates=2  steps=128
  [direct] seed=1008  return= +213.97  gates=2  steps=80
  [direct] seed=1009  return=   -0.53  gates=1  steps=47

=== band (10 eps) ===
  [band] seed=1000  return=  -17.33  gates=1  steps=42
  [band] seed=1001  return= +394.96  gates=3  steps=144
  [band] seed=1002  return= +391.31  gates=3  steps=155
  [band] seed=1003  return= +399.75  gates=3  steps=135
  [band] seed=1004  return= +383.31  gates=3  steps=86
  [band] seed=1005  return= +237.47  gates=2  steps=142
  [band] seed=1006  return= +186.05  gates=2  steps=121
  [band] seed=1007  return= +949.33  gates=6  steps=306
  [band] seed=1008  return=+1165.95  gates=7  steps=468
  [band] seed=1009  return=  -13.30  gates=1  steps=53

=== blur (10 eps) ===
  [blur] seed=1000  return=  -28.41  gates=1  steps=67
  [blur] seed=1001  return=  -17.46  gates=1  steps=25
  [blur] seed=1002  return=  -17.30  gates=1  steps=39
  [blur] seed=1003  return=  -23.31  gates=1  steps=39
  [blur] seed=1004  return=   -0.20  gates=1  steps=49
  [blur] seed=1005  return=  -21.59  gates=1  steps=61
  [blur] seed=1006  return=  -17.71  gates=1  steps=120
  [blur] seed=1007  return=  -19.24  gates=1  steps=39
  [blur] seed=1008  return=   -4.96  gates=1  steps=127
  [blur] seed=1009  return=  -21.23  gates=1  steps=93

=== roundtrip (10 eps) ===
  [roundtrip] seed=1000  return=  -19.43  gates=1  steps=116
  [roundtrip] seed=1001  return=  -15.00  gates=1  steps=29
  [roundtrip] seed=1002  return=  -19.66  gates=1  steps=33
  [roundtrip] seed=1003  return=  -22.36  gates=1  steps=104
  [roundtrip] seed=1004  return=  -13.03  gates=1  steps=47
  [roundtrip] seed=1005  return=  -10.75  gates=1  steps=126
  [roundtrip] seed=1006  return=  -26.82  gates=1  steps=70
  [roundtrip] seed=1007  return=  -48.17  gates=1  steps=167
  [roundtrip] seed=1008  return=  -13.80  gates=1  steps=125
  [roundtrip] seed=1009  return=  -30.58  gates=1  steps=105

=== TRANSLATION REHEARSAL SUMMARY ===
(direct = training-eval anchor; band = VFoV crop only; blur = resample only; roundtrip = full adapter path. Training-run best batch metric: +256.28)
direct   : return   +35.59 +/-  91.92   gates   1.2   delta-vs-direct   +0.0%
band     : return  +407.75 +/- 361.30   gates   3.1   delta-vs-direct +1045.8%
blur     : return   -17.14 +/-   8.01   gates   1.0   delta-vs-direct -148.2%
roundtrip: return   -21.96 +/-  10.57   gates   1.0   delta-vs-direct -161.7%

--- stderr ---
Gym has been unmaintained since 2022 and does not support NumPy 2.0 amongst other critical functionality.
Please upgrade to Gymnasium, the maintained drop-in replacement of Gym, or contact the authors of your software and request that they upgrade.
See the migration guide at https://gymnasium.farama.org/introduction/migration_guide/ for additional information.
C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\tools.py:749: FutureWarning: `torch.cuda.amp.GradScaler(args...)` is deprecated. Please use `torch.amp.GradScaler('cuda', args...)` instead.
  self._scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
```

---
*Watcher finished 2026-06-16 06:37:21. Gate step succeeded; the rehearsal RETURN is the go/no-go for flight #4. Edges fix the gate-appearance axis; if rehearsal is weak the residual is background-texture edges -> add bg-randomization next. Decision = waking stream + Clayton.*
