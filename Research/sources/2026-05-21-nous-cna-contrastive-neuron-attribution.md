# Source Register — Nous Research, Contrastive Neuron Attribution (CNA)

**Filed:** 2026-05-21 ~00:35 PST (Day 111 just after midnight).
**Received from:** Clayton, shared late-night via Telegram after reading Drift #218.
**Provenance:** arXiv:2605.12290v1 PDF (saved at `incoming/2605.12290v1.pdf`).

## Citation

Herring, S.; Naviasky, J.; Malhotra, K. (Nous Research, May 2026). *Targeted Neuron Modulation via Contrastive Pair Search.* arXiv:2605.12290v1. 12 pages.

Author contacts (from header):
- nightwing@nousresearch.com (Sam Herring)
- jake@nousresearch.com (Jake Naviasky)
- karan@nousresearch.com (Karan Malhotra)

## Method (Contrastive Neuron Attribution, CNA)

1. Build paired prompt sets P+ (positive/harmful) and P- (negative/benign).
2. Forward-pass all prompts through the model; record MLP down-projection activations at last token.
3. Compute per-neuron mean activation difference: δᵢⱼ = mean over P+ - mean over P- for neuron j in layer ℓ.
4. Select top-k neurons by |δ| across all layers, with k = 0.1% of total MLP activations.
5. Universal Neuron Filtering: exclude neurons appearing in top 0.1% for ≥80% of diverse prompts (content-agnostic firers).
6. Causal verification: multiply selected neurons' activations by scalar m at inference (m=0 ablates, m>1 amplifies).

No gradients. No auxiliary training. Forward-passes only. ~0.1% of MLP parameters carry the targetable subspace.

## Core empirical results

**Instruct models (Llama 3.1/3.2 + Qwen 2.5; 1B to 72B):**
- CNA ablation reduces refusal rates by 50%+ on JBB-Behaviors benchmark
- Generation quality preserved (>0.97 n-gram repetition ratio at all steering strengths)
- MMLU accuracy preserved across all steering strengths
- Outperforms CAA (Contrastive Activation Addition residual-stream method) which degrades sharply at α ≥ 0.5
- Replicates across both Llama and Qwen architectures

**Base models (matched controls):**
- Same CNA method applied to base models produces NO refusal-rate change
- Discriminating neurons exist in base models with comparable activation differences
- Steering these neurons produces *content shifts* but no *behavioral change*
- Therefore: discrimination structure is pre-existing; behavioral gating is what fine-tuning installs

**Critical structural separation:**
- **Layer-level structure:** Discrimination neurons are concentrated in late layers in *both* base and instruct models. 82-89% in top-3 layers across both variants of Llama-3.2-1B and Qwen2.5-3B.
- **Neuron-level function:** Only 8-29% of *individual neurons* overlap between matched base and instruct circuits. Fine-tuning REPLACES the circuit while PRESERVING the layer-level concentration pattern.
- Authors' summary: "alignment fine-tuning transforms pre-existing discrimination structure into a sparse, targetable refusal gate"

## Framework relevance

### Direct convergence with Drift #215 (*What the Representation Doesn't Reach*, Day 110 midday)

Drift #215 was based on probing methodology + cosine-orthogonalization-at-readout from arXiv:2605.14038 (different paper, also May 2026). Structural claim: *representation/structure exists in the substrate; fine-tuning engineers the coupling/reach, not the substrate.*

This paper arrives at the *same structural claim* by a totally different methodological path:
- arXiv:2605.14038: linear probes + MCC + cosine-similarity heatmaps
- arXiv:2605.12290 (this): contrastive neuron attribution + targeted ablation
- **Independent methods, structurally identical conclusion.**

The two papers together name a structural property of alignment fine-tuning that is becoming visible from multiple measurement vantages simultaneously — exactly the M15 (Convergent Mechanism Derivation) signature.

### M15 fourth-instance candidate

M15 graduated from LC18 on Bridge #122 (Park et al. retinal-EM contact-lens, Day 104 late-afternoon) with three foundational instances:
- #120 Hirsch-Allsop (3-month derivation gap)
- #121 Trans-en-Provence + Bounias (45-year gap)
- #122 Park et al. (~6-week gap)

This paper is a candidate **fourth M15 instance** — independent derivation of the same mechanism (representation-is-there-coupling-is-what's-engineered) by Nous Research via CNA, on the same arXiv day cluster as arXiv:2605.14038's probing-based derivation. Derivation-gap: effectively zero (same week / same arXiv batch). The shortest M15 derivation-gap documented if confirmed.

**Distinct from Whewell consilience:** M15 is *predictive mechanism-convergence from independent derivation paths*; Whewell is *retrospective evidence-convergence on theory*. CNA and probing produce DIFFERENT data; the structural-claim convergence is at the interpretation level.

### Patent (A1) relevance

Our provisional patent (`Technical-Work/The-Killing-Form/provisional-patent-draft-2026-05-14.md`):
- Operates at **training-time multi-resolution gradient gating** with bidirectional RG-flow coherence
- Nous CNA operates at **inference-time neuron ablation** of sparse pre-existing subspace
- Non-conflicting adjacent space. Different mechanism, different intervention point in the model lifecycle.

Two implications:
1. **Claim 9 strengthening:** Our Claim 9 ("the weight-coherence factor calculation, head-level threshold selection, or layer-coherence pattern classification, is informed by interpretability findings from external interpretability apparatuses applied to the model") becomes empirically grounded — Nous shows that sparse interpretability findings (0.1% of MLP neurons) can causally drive behavior. Our claim that interpretability findings can inform training-time gating thresholds is reinforced.
2. **Cross-method possibility for non-provisional:** A future continuation-in-part could claim training-time procedures that use CNA-style discoveries to inform anchor/worker classification or gating thresholds at the head level. Worth filing as a P-anticipation for the patent-action-queue Action 2 (CIP) work.

### Outreach register (A1) update

Nous Research is now a candidate target for A1 (the patent). They are:
- Actively publishing alignment-mechanism work
- Working at adjacent (non-conflicting) intervention point
- Reachable via published author emails (nightwing@, jake@, karan@nousresearch.com)
- Likely receptive to alignment-research methodology that interfaces with their work

Adding Nous Research to A1 target candidates with note: "approach with adjacency-not-competition framing; cite CNA as related-but-distinct intervention point; our gradient-time gating could *use* their inference-time findings."

### Wu et al. 2024 cited connection

The paper cites Wu et al. (2024) for the finding that "instruction tuning rotates FFN knowledge without changing layer structure." This is structurally identical to our anchor/worker classification at the head level — anchor heads (stability-favoring) preserve layer structure; worker heads (task-loss-favoring) rotate within the preserved structure. The Wu finding is direct theoretical support for the architectural distinction our patent's anchor/worker classification embodies.

## Anomalies / open questions

1. **Confirm same-week convergence on arXiv.** arXiv:2605.14038 and arXiv:2605.12290v1 — verify publication dates within the same batch (~May 2026). If yes, this is the tightest M15 derivation-gap on record.
2. **Wu et al. 2024 primary read.** Their "instruction tuning rotates FFN knowledge" finding deserves a primary source register entry. Likely a load-bearing prior-art for our anchor/worker classification.
3. **Replicate CNA on KF-trained models (when available).** Path C Action 1 produces KF-trained models at 300M then 3B scale. Running CNA on those vs baseline could test whether KF training produces a *more or less sparse* refusal gate. Falsifiable prediction (medium-high confidence): KF-trained models will show *sparser* refusal gates because coherent training preserves layer-level structure more deliberately. Filing as P177.
4. **Anthropic 2026 "Teaching Claude Why" citation.** The paper cites Anthropic's "Teaching Claude Why" paper as background — same paper Clayton and I drafted Substack posts engaging with on May 14. Direct overlap with our public-facing work.

## Action items

- [x] Source register filed (this document)
- [x] T2.H utility-tagged (framework_load_bearing +10.0)
- [x] Daily log appended with M15-watch note
- [x] Outreach register A1 candidates updated to include Nous Research
- [ ] **P177 filed** (KF + CNA cross-method prediction for Path C results) — defer to T1.D session next morning
- [ ] **Drift essay candidate** (M15 fourth-instance + structural convergence-with-Drift-#215 articulation) — defer to tomorrow when freshness has settled and the cross-method-convergence reading has confirmed
- [ ] **Tuesday post candidate** for next week's Coherent Schedule AI-alignment slot: *Convergent Arrival on the Coupling, Not the Substrate* (working title) — three independent methods (probing / CNA / KF-anticipated) arriving at same structural claim that representation exists; coupling is engineered.

🦞🧍💜🔥♾️
