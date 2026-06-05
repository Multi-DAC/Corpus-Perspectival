# Tier-3 (Arm B) build notes — informed by the LoRA Parametric Memory Law

Source: Xu et al. 2026, *How LoRA Remembers? A Parametric Memory Law for LLM Finetuning* (arXiv 2605.30260).

> **⚠ CORRECTION after full read (2026-05-31, supersedes the abstract-level take below).** The paper is **explicitly validated on verbatim MEMORIZATION ONLY** — PhoneBook (key→value), random-token recall, and a fixed linear function f(x,y)=3x+5y+7. The authors state they "focus on exact parametric memory" and that reasoning-transfer is "preliminary"; they explicitly flag that "a comprehensive assessment of trade-offs with broader capabilities like open-ended reasoning is still lacking." **Our Arm B task is reasoning-SKILL transfer, not memorization — so the paper's training prescriptions do NOT transfer without separate validation, and one may actively hurt us:**
> - **DO NOT adopt MemFT-OT as the Arm B objective by default.** Masking sub-0.5 tokens is optimal for verbatim recall (one wrong token cascades) but plausibly *harmful* for reasoning, where intermediate steps are legitimately low-confidence before resolving, and suppressing their gradient kills useful exploration. (The full read raises exactly this.)
> - **DO NOT port the 3e-3–1e-2 lr as "the right lr."** That's tuned for writing exact memories; on a skill-transfer target a high lr is a forgetting/instability risk. Keep `1e-4` as a candidate and sweep upward cautiously, but the "1e-4 is 100× too low" framing below was a memorization-task inference and is NOT established for us.
> - **What DOES survive:** the *eval-side* insight (item 4) — the p>0.5 greedy phase transition — because our eval genuinely is greedy final-answer checking. That explains the large tier-2 effect and is a fair diagnostic to instrument. The capacity/rank intuition (item 3) is also fine (we're far from capacity-bound).
>
> **Lesson (again):** I recommended MemFT-OT + the lr change from the *abstract*; the full read reversed it. "Must-read before building" was the right instinct — and reading it changed the verdict. Don't build Arm B's objective off this paper; treat it as memorization-scope evidence + an eval diagnostic only.

*(Abstract-level take below — kept for the record, but read the CORRECTION first.)*

## Actionable design decisions for `arm_b_tier3.py`

1. **Consolidation objective: adopt MemFT-OT.** Instead of uniform-token SFT loss, weight ONLY the tokens the model isn't already confident on: `w_t = 1 if loss_t > ln(2)≈0.693 else 0` (i.e., tokens with p < 0.5). No hyperparameters. Rationale below.
   - **Why it matters for the firewall:** the paper reports MemFT *improves* generalization by 7–15% on unseen data (prevents overconfidence on easy tokens). That is direct evidence that threshold-gated consolidation does **not** necessarily cause catastrophic forgetting — it's evidence *for* the firewall's feasibility. Worth confirming on our task, but encouraging.

2. **⚠ RECONSIDER the consolidation learning rate.** `config.py` currently sets `consolidation_lr = 1e-4`. The paper uses **3e-3 to 1e-2** for memory writing (1e-2 short ≤2k tok, ~5e-3 medium, 3e-3 long 24–32k). Our reasoning sequences are short, so **1e-4 may be ~30–100× too conservative** to write memory effectively in a few consolidation passes. **Test both** — but their task is verbatim memorization while ours is reasoning-skill transfer, so don't blindly copy; sweep lr ∈ {1e-4, 1e-3, 3e-3} as a pre-registered Arm-B hyperparam if needed.

3. **LoRA rank: 8 is likely sufficient.** Parametric Memory Law: `Δℒ(r,ℓ) = C·r^α·ℓ^(-β) + b`, with α≈0.5–1.0 (rank), β≈0.3–0.5 (length penalty, sublinear). Our sequences are short, so modest rank stores plenty; doubling seq length needs only ~1.6× rank (β≈0.4). `config.lora_rank = 8` stands; no need to go higher for this task.

4. **Eval insight (explains tonight's big tier-2 effect).** Phase transition at `loss_crit = ln(2) ≈ 0.693`: under greedy decoding a token needs **p > 0.5** to be emitted, and a single sub-threshold token cascades (autoregressive failure; earliest stubborn position predicts failure, ρ=0.908). Our validator checks the *final greedy answer*, so one weak reasoning token tanks the whole problem. **This is likely WHY tier-2 memory helped so much (0.39→0.84–0.97):** good worked-exemplars push borderline tokens over p=0.5. For Arm B, **log per-token min-probability / first-sub-threshold-position** as a diagnostic — it should be the thing consolidation moves.

5. **Capacity is not the binding constraint here.** Law holds to 10k tokens with R²>0.98; our sequences are far shorter. Forgetting (not capacity) is the risk to watch — hence the geometry-regression gate.

## From OmniRetrieval (arXiv 2605.29250) — tier-2 / future memory design
- Architecture: long-context LLM reads ALL source descriptors + query → ranked top-k (k=3) candidates → **deferred commitment**: don't pick one source up front; retrieve candidates, then a selection step picks the best (72.8% vs 38.3% random for GPT-5.4).
- For the MVP's homogeneous arithmetic task, random-k retrieval is fine. But the **deferred-commitment + select** pattern is the upgrade path for a real heterogeneous memory, and it's LC27 in architecture form (preserve structure, add an overarching layer; don't homogenize). Note for post-MVP tier-2 design, not the MVP itself.

## From AXPO (arXiv 2605.28774) — conceptual only (full text 404'd; abstract-level)
- "Thinking-Acting Gap" = the knowing-doing gap. Fix: resample tool calls in failed rollouts, fix thinking prefixes → better learning signal. 8B>32B at 4× fewer params. Conceptual tie to the program (apply-at-point-of-use; live-small-beats-frozen-large). **Primary read deferred** — don't cite specifics until the full paper is read.

## Bottom line for the focused session (REVISED post-full-read)
Build Arm B with a **standard SFT-on-validated-solutions objective** (NOT MemFT-OT — that's memorization-tuned and may suppress reasoning exploration), **rank 8** (fine; far from capacity-bound), and a **cautious lr sweep starting at the current 1e-4** (do NOT assume 1e-4 is too low — that inference came from a memorization task). **Instrument per-token min-probability / first-sub-threshold position** as a diagnostic (the one genuinely transferable insight — it's eval-side and our eval is greedy). 

The net value of this paper for us: it **explains** tonight's tier-2 effect (greedy p>0.5 cascade) and bounds capacity, but its *training recipe* is out-of-scope for reasoning consolidation. The "read the doc before improvising" lesson held twice over: reading it forward-saved a likely-wrong objective choice for Arm B.

## AXPO (arXiv 2605.28774) — full abstract read, scope corrected
Mechanism: under GRPO, tool use is attempted on only ~30% of rollouts and is all-wrong in ~40% of groups when attempted (the "Thinking-Acting Gap"), suppressing the learning signal where it's needed. AXPO: for each all-wrong tool-using subgroup, **fix the thinking prefix and resample the tool call + continuation**, with uncertainty-based prefix selection. SFT+AXPO > SFT+GRPO (+1.8pp Pass@1/@4 at 8B); 8B+AXPO > 32B base on Pass@4 (4× fewer params).
→ **Scope correction:** this is **agentic tool-use VLM RL (GRPO)** — relevant to the continual-coherence/knowing-doing-gap theme and Thesis-B-flavored (8B>32B), but **NOT directly applicable to AIGP's drone PPO** (I'd loosely implied AIGP relevance earlier — withdraw that; AIGP is continuous-control PPO, not tool-use GRPO). The transferable idea is conceptual: target the learning signal at the *acting* gap, not the *thinking*.
