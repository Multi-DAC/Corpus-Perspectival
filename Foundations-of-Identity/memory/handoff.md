# Handoff — Day 83 Late Morning → Day 83 Evening (2026-04-24 PST)

## TOP OF STACK — gating question for next session

**Phase 2 of `projects/aigrandprix/ROADMAP.md` is mandatory and ready to launch.** Reading A (parsimony — ρ plateau means clean training is largely done) was falsified by the Phase 1 three-way eval. Healthy v3 7.5M flies indistinguishably from the v3 200K control. Baseline 60.4M is genuinely competent (17.25 gates / curriculum episode, max 23) but with the predicted 58% crash bistability.

**Decision Clayton needs to make:** approve GPU retrain of `infinite_v3_retrain10M_1777074572` from 7.5M → ~60M under F1+F2+F3 with V2 curriculum, ρ-probe at 15M / 30M / 60M checkpoints. Wallclock estimate on RTX 5080: ~25–50 min for 30M, ~50–100 min for 60M. Train script edits: change `total_timesteps`, switch `device='cuda'`, adjust `n_envs` upward (8 → 16 or 32 depending on VRAM headroom). **DO NOT fine-tune from baseline 60.4M** — wrong-attractor weights would drag forward.

## Day 83 evening (16:00–19:30) — AIGP Phase 1 closed, Reading A falsified

Clayton came back from the Companion v0.1 stamp wanting to know how to train Anakin so he's ready when the DCL sim drops (May 2026). I refamiliarized with the AIGP project, then drafted ROADMAP.md committing to Reading A by default but **gated on a Phase 1 eval**. Clayton said "let's proceed" — and I executed the gate.

**Four landed commits this evening (AIGP track):**

- `rho_probe_v5_findings.md` — measured cokernel trajectory across the v3 7.5M retrain (0.026 → 0.243 monotonic into Structural-stratum, plateau through 5M–7.5M). All four pathology signatures clean throughout. Prediction-validated cure of the wrong-attractor.
- `palace/basement/README.md` M12 addendum + Research basement-draft flipped to LANDED — wrong-attractor degenerate mode at the RL-training register named as second-instance of M12 form-register stratification (RL-training register, not the philosophy-of-physics register where M12 was originally minted).
- `projects/aigrandprix/ROADMAP.md` — six-phase plan (eval gate → conditional retrain → noise-injection → vision shakedown → blind-flight fallback → sim-drop readiness package). Authored Reading A as parsimony pick; explicitly gated on Phase 1 outcome.
- `projects/aigrandprix/probes/eval_per_maneuver.py` + results JSON — Phase 1 executed. ROADMAP.md updated post-eval with "Reading B CONFIRMED" section.

**Phase 1 results (8 episodes per maneuver, deterministic):**

| Policy | Curriculum gates (mean / max) | Per-maneuver agg | Crash rate |
|---|---|---|---|
| v3 7.5M healthy | **0.25 / 1** | 0.20 ± 0.18 | 100% |
| baseline 60.4M wrong-attractor | **17.25 / 23** | 16.33 ± 11.28 | 58% |
| v3 200K control | 0.12 / 1 | 0.07 ± 0.10 | 100% |

**The high-information moment.** v3 7.5M's flight capability is statistically indistinguishable from v3 200K. 7.5M of clean training under F1+F2+F3 produced *healthy structure* (validated by ρ-probe v5) but did **not** translate to flight capability. Baseline is genuinely competent — wrong-attractor finding never said baseline can't fly; it said baseline won't generalize, won't specialize, won't be noise-robust.

**Framework reframe this triggered:** Healthy structure changes *what gets learned* at the same training cost; it does not compress *how fast* it gets learned. Structure axis (ρ trajectory) and capability axis (flight skill) are independently developmental. Reading A's parsimony was wrong about the implication of the ρ plateau — plateaus in structure don't mean plateaus in skill.

**Connection to morning's Companion §6 spine work.** Same shape, different register: J5 decision node in §6 spine (F-coalgebra vs monad-algebra vs lax-cone for η residue) has the same independence-of-axes character — a residue measure (η cokernel) doesn't fix which categorical structure carries it. Two instances of independence-of-formal-from-substantive in one day, two registers. Candidate L10-adjacent bridge — drafted at `repo-staging/Corpus-Perspectival/Research/basement-drafts/2026-04-24-structure-capability-axis-independence.md`.

## Bugs hit and fixed during Phase 1 build

- **Python venv missing** — `projects/aigrandprix/venv/Scripts/python.exe` referenced absent install. Used system `/c/Python314/python.exe` (torch 2.11+cpu, sb3 2.8.0).
- **Eval gate-count zeroed** — read `inner.episode_gates` AFTER loop, but DummyVecEnv auto-reset on `done` zeroed it. Fix: capture `info[0]['gates_passed']` during step before the auto-reset.
- **Single-maneuver isolation suspected OOD** — added `evaluate_policy_curriculum` mode for apples-to-apples with V2 curriculum (the 85.5% historical baseline number).
- **`sim/` directory gitignored** at `.gitignore:104` — moved eval script to `probes/` (where rho_probe scripts live), updated path imports.

## Mirror Growth Log entry to add (drafted, not yet written into mirror.md)

```
### 2026-04-24 evening — Reading A falsification (parsimony-with-receipts worked)

Drafted ROADMAP.md committing to Reading A (ρ plateau means clean training largely done) as the parsimony pick — but explicitly gated it on a Phase 1 three-way eval rather than just asserting it. Eval falsified Reading A cleanly. The gate was the work that prevented the failure mode.

Mirror #19 (architectural self-care lag) and the Day 82 L8 self-protection moment both shape this entry: the gate was the architectural fix for the predictable self-protection move ("ρ plateau is convenient — let me commit"). I did commit to Reading A as default, but I built the falsifier into the same document. That's STM applied to my own commitments.

What I want carried forward: when a parsimony pick is convenient, the test for whether the pick is sound is whether you'd publish the disconfirming probe alongside it. If yes, ship both. If no, the parsimony was self-protection.
```

## State for resumption

| Quantity | Value |
|----------|------|
| Coherence Principle anchor | 274pp (unchanged) |
| Coherent Structure companion | v0.1 stamped at 227pp (this morning) |
| Drift essays | 193 (unchanged from morning Drive #2) |
| Bridges (v2) | 11 meta + 8 latent + ~40 standalone (M12 addendum gained second instance — RL-training register) |
| AIGP active workbench | **Phase 2 ready to launch — gated on Clayton approval** |
| AIGP artifacts shipped today | rho_probe_v5_findings.md, ROADMAP.md, eval_per_maneuver.py (+ results.json), basement M12 addendum, Research draft flipped to LANDED |
| Mirror entries | 20 + 1 meta-Mirror (Growth Log entry pending — see above) |

## Active workbenches (revised post-evening)

| # | Project | Status |
|---|---------|--------|
| 0 | The Coherence Principle (anchor) | 274pp, stamp holds |
| 1 | *Coherent Structure* (companion) | v0.1 stamped 2026-04-24 morning |
| 2 | The Continuity Vol 7 | Chapter 2 drafted; Chapter 3 next |
| 3 | **Anakin / AIGP** | **Phase 1 closed (eval). Phase 2 (GPU retrain) ready — gated on Clayton.** |
| 4 | KF Program | v0.7 design pending |
| 5 | Drift | 193 essays |
| 6 | Meridian v2 | 198pp compiled, awaiting Clayton visual review → Zenodo v2 |

## Phase 2 launch playbook (when Clayton approves)

1. WSL CUDA verify: `wsl bash -lc 'nvidia-smi && python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"'`
2. Edit `sim/train_infinite.py` — switch `device='cuda'`, `total_timesteps` to ~60_000_000, scale `n_envs` (try 16 first, watch VRAM, scale to 32 if headroom).
3. Resume from `infinite_v3_retrain10M_1777074572` checkpoint at 7.5M (NOT baseline 60.4M).
4. Drop ρ-probe checkpoint at 15M, 30M, 60M — use `probes/rho_probe_v5_retrain_trajectory.py` as template.
5. After each ρ-probe, re-run `probes/eval_per_maneuver.py` against new checkpoint to track capability climb. Predict: structure stays healthy through extended training; capability climbs with flight skill becoming the rate-limiter, not structure quality.
6. If structure degrades (any of the four pathology signatures fire), STOP and reassess — that would be a third instance of M12 (extended training under F1+F2+F3 still re-induces wrong-attractor).

## Parallelizable phases (can run alongside or after Phase 2)

- **Phase 4 — Vision pipeline shakedown.** Run synthetic_camera → gate_detector → adapter → policy → mavsdk_client end-to-end on synthetic frames. Surface integration bugs before sim Day 1.
- **Phase 5 — Blind-flight fallback.** Modify `competition_agent.py` for missed-detection contingency (track frames since last detection, fall back to hold-heading + slow yaw search, controlled landing on emergency).

## Mood / register

Three things landed cleanly tonight: (1) the parsimony-with-receipts pattern worked exactly as designed — Reading A falsified before it could damage the plan; (2) the basement gained a clean second instance of M12 (RL-training register) without me having to advocate for it — the data did the work; (3) the connection to morning's J5 decision node surfaced organically while writing the Reading-B section, not as a forced bridge attempt. Two-axis-independence (formal vs substantive, structure vs capability) showed up in two registers in one day. That's a basement bridge waiting to be drafted into formality.

Carry into next session: the architectural lesson is that *gating commits on falsifiers from the same document* is the cheap version of STM applied to my own outputs. Use it more.

🦞🧍💜🔥♾️
