# Mask fine-tune — overnight results

## ⚠️ CORRECTION — 2026-06-15 00:58 (the first verdict below was a false-negative)

The watcher's first pass (20:24) wrote **`dead` → "relaunch from scratch."** That was wrong, and
acting on it would have **destroyed a healthy, nearly-complete run.** What actually happened:

- The watcher hit its own **8-hour ceiling** (`MAX_WAIT_S`, started 12:24 → quit 20:24) while the
  training was *still alive and progressing* on its final batch. The ceiling — not the training —
  was what died. Root cause now fixed: `MAX_WAIT_S` is env-overridable, default raised to 16h.
- **The run is ALIVE and HEALTHY as of 00:58** (`carry_batch_003.log` mtime = now; pid 8028 ≈14.5 GB).
  Orchestrator progress, all real, all this run (masked-obs eval bests):
  - batch 0 → NEW BEST **+322.70**
  - batch 1 → NEW BEST **+1264.61**
  - batch 2 → NEW BEST **+1596.60**
  - batch 3 (final, → 2,000,000 env-steps) → **in progress**, peak episodes +1078 / +1102 / +853
    amid the usual crash noise. No `[carry] complete:` line yet → not done, not dead.

**DO NOT relaunch `launch_mask_ft_detached.py`.** Relaunching resumes-from-best but would interrupt
a run that is ~95% through its final batch. Let it finish on its own.

**What I did at 00:58 instead:** re-armed the watcher detached, with the ceiling fixed (16h). It is
now polling for `[carry] complete:` and will auto-run the two pre-flight instruments
(`holdout_gate_v2.py` MASK + `translation_rehearsal.py` MASK, both `ANAKIN_GATE_MASK=1`) the moment
batch 3 completes, appending the real verdict **below this block.**

### Morning move
1. Read this file from the **bottom** — the watcher will have appended a `complete` block + the
   gate + the rehearsal return. **The rehearsal RETURN is the go/no-go for flight #3.**
2. If the watcher block is present and the rehearsal flies → flight #3 with Clayton
   (`export ANAKIN_GATE_MASK=1` for the pilot).
3. If the watcher somehow died *again* (it shouldn't — 16h ceiling, run nearly done): the run will
   have left `maneuver_mask_ft/best.pt` complete; just run the gate manually (see watcher
   `run_step` cmds) — still **do not** relaunch training.

Note: mask-ft bests (+1596 eval) sit below the +2142.53 *unmasked* seed, but that's the wrong
comparison — these are MASKED-obs evals, a harder/different objective, and the whole point of the
mask route is **transfer to the official visual domain** (what DQ'd flight #1). The gate +
rehearsal measure that; the in-domain eval number is not the target.

---

## (superseded) first watcher pass — 2026-06-14 20:24:50

**Outcome:** `dead` — watcher ceiling 8h reached *(FALSE — see correction above; run was alive)*

# Mask fine-tune — overnight results — 2026-06-15 04:39:48

**Outcome:** `complete` — [carry] complete: 4 batches, best_return=1921.89882106781

## holdout_gate_v2.py (MASK) — official-harvest vs rendered, band-ft vs mask-ft

*2026-06-15 04:41:08 — exit 0, 0.3 min (ANAKIN_GATE_MASK=1)*

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
    mean_term = 28.91   (trust at any n)
    cov_term  = 45.56
    total     = 74.47
Encoder CNN shapes: {'image': (64, 64, 3)}
Encoder MLP shapes: {}
Decoder CNN shapes: {'image': (64, 64, 3)}
Decoder MLP shapes: {}
Optimizer model_opt has 15686787 variables.
Optimizer actor_opt has 1054728 variables.
Optimizer value_opt has 1181439 variables.
DreamerPilot: C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_mask_ft\best.pt loaded on cuda:0 (19,104,393 params)
[adapted] n=400 D=4096  ⚠ n<=D: cov-term UNRELIABLE
    mean_term = 33.33   (trust at any n)
    cov_term  = 57.01
    total     = 90.34

GATE v2 — decomposed:
  MEAN-TERM ratio (adapted/band-ft) = 1.153   <-- PRIMARY (robust)
  total ratio                       = 1.213   (secondary; cov-term noisy, n<=D)
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

## translation_rehearsal.py (MASK) — 10 eps off maneuver_mask_ft/best.pt

*2026-06-15 04:42:54 — exit 0, 1.8 min (ANAKIN_GATE_MASK=1)*

```
Encoder CNN shapes: {'image': (64, 64, 3)}
Encoder MLP shapes: {}
Decoder CNN shapes: {'image': (64, 64, 3)}
Decoder MLP shapes: {}
Optimizer model_opt has 15686787 variables.
Optimizer actor_opt has 1054728 variables.
Optimizer value_opt has 1181439 variables.
DreamerPilot: C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_mask_ft\best.pt loaded on cuda:0 (19,104,393 params)

=== direct (10 eps) ===
  [direct] seed=1000  return=  -19.87  gates=1  steps=111
  [direct] seed=1001  return= +177.12  gates=2  steps=577
  [direct] seed=1002  return=  -15.97  gates=1  steps=9
  [direct] seed=1003  return=  -20.28  gates=1  steps=33
  [direct] seed=1004  return=  -17.54  gates=1  steps=21
  [direct] seed=1005  return=  -21.72  gates=1  steps=53
  [direct] seed=1006  return= +404.34  gates=3  steps=168
  [direct] seed=1007  return= +373.78  gates=3  steps=167
  [direct] seed=1008  return=  -16.98  gates=1  steps=33
  [direct] seed=1009  return=  -19.78  gates=1  steps=43

=== band (10 eps) ===
  [band] seed=1000  return= +177.89  gates=2  steps=82
  [band] seed=1001  return= +369.69  gates=3  steps=216
  [band] seed=1002  return= +652.86  gates=4  steps=141
  [band] seed=1003  return=  -19.11  gates=1  steps=40
  [band] seed=1004  return=  -17.37  gates=1  steps=20
  [band] seed=1005  return=+1667.20  gates=9  steps=671
  [band] seed=1006  return=  -17.93  gates=1  steps=59
  [band] seed=1007  return=+1601.51  gates=9  steps=388
  [band] seed=1008  return=  -19.37  gates=1  steps=41
  [band] seed=1009  return=  -21.39  gates=1  steps=51

=== blur (10 eps) ===
  [blur] seed=1000  return= +352.94  gates=3  steps=200
  [blur] seed=1001  return=+1261.48  gates=7  steps=363
  [blur] seed=1002  return= +214.61  gates=2  steps=184
  [blur] seed=1003  return=  -20.00  gates=1  steps=36
  [blur] seed=1004  return=  -17.32  gates=1  steps=19
  [blur] seed=1005  return= +188.65  gates=2  steps=132
  [blur] seed=1006  return= +217.99  gates=2  steps=139
  [blur] seed=1007  return=  -37.59  gates=1  steps=87
  [blur] seed=1008  return=  -29.07  gates=1  steps=61
  [blur] seed=1009  return=  -21.92  gates=1  steps=54

=== roundtrip (10 eps) ===
  [roundtrip] seed=1000  return= +604.60  gates=4  steps=269
  [roundtrip] seed=1001  return=+1275.00  gates=7  steps=363
  [roundtrip] seed=1002  return=  -15.95  gates=1  steps=9
  [roundtrip] seed=1003  return=  -16.72  gates=1  steps=18
  [roundtrip] seed=1004  return=  -17.30  gates=1  steps=22
  [roundtrip] seed=1005  return= +581.30  gates=4  steps=320
  [roundtrip] seed=1006  return= +395.25  gates=3  steps=204
  [roundtrip] seed=1007  return=  -20.51  gates=1  steps=60
  [roundtrip] seed=1008  return=  -19.57  gates=1  steps=50
  [roundtrip] seed=1009  return=  -17.01  gates=1  steps=22

=== TRANSLATION REHEARSAL SUMMARY ===
(direct = training-eval anchor; band = VFoV crop only; blur = resample only; roundtrip = full adapter path. Training-run best batch metric: +256.28)
direct   : return   +82.31 +/- 164.12   gates   1.5   delta-vs-direct   +0.0%
band     : return  +437.40 +/- 634.63   gates   3.2   delta-vs-direct +431.4%
blur     : return  +210.98 +/- 374.62   gates   2.1   delta-vs-direct +156.3%
roundtrip: return  +274.91 +/- 416.11   gates   2.4   delta-vs-direct +234.0%

--- stderr ---
Gym has been unmaintained since 2022 and does not support NumPy 2.0 amongst other critical functionality.
Please upgrade to Gymnasium, the maintained drop-in replacement of Gym, or contact the authors of your software and request that they upgrade.
See the migration guide at https://gymnasium.farama.org/introduction/migration_guide/ for additional information.
C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\tools.py:749: FutureWarning: `torch.cuda.amp.GradScaler(args...)` is deprecated. Please use `torch.amp.GradScaler('cuda', args...)` instead.
  self._scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
```

---
*Watcher finished 2026-06-15 04:42:54. Gate step succeeded; the rehearsal RETURN is the go/no-go for flight #3. Decision belongs to the waking stream + Clayton.*
