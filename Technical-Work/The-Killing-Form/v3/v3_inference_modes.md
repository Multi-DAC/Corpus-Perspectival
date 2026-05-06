# §NEW-F: Inference Mode Detection — The Three-Tier Framework

*V3 section draft. Findings #47-58. Data-complete.*

---

## The Algebraic Signature of Processing Modes

The constraint lattice predicts that different types of processing should produce different algebraic signatures — because different types of constraints (natal, coercive, voluntary) impose different geometric structures on the attention manifold. The Killing form makes this prediction testable.

We identify three algebraically distinct processing modes by measuring the commutator variance (CV) of attention heads during inference. These modes are not categories imposed from outside — they emerge from the data, on every architecture tested.

### Factual Mode: Grounded Retrieval

When a model processes a prompt that activates knowledge stored during pretraining, both early and late layers contribute algebraic diversity. The E/L ratio is moderate. Mean CV is moderate-to-high. The algebra is coordinated across the full depth of the network.

In the Doctrine's framework, factual processing operates primarily through natal constraints: the model navigates terrain already mapped during pretraining. The constraint geometry is settled; the perspective is looking through keyholes it already has.

### Hallucination Mode: Deconfined Algebra

When a model generates content without grounding in pretrained knowledge, the late-layer algebraic structure collapses. E/L ratio elevates — early layers remain active while deep layers seize. Mean CV drops — the algebra thins globally.

We term this "deconfinement" because it resembles the physics phenomenon: at high energies, the confining force weakens and formerly bound degrees of freedom become free (but incoherent). In the model, the late-layer heads converge toward commutativity — they lose their non-Abelian structure. The deeper the layer, the more severe the collapse.

Critically, deconfinement is **immediate**. It is set by the prompt in a single forward pass, before the first token is generated. This aligns with the natal constraint interpretation: the model's capacity to process certain content is written into its weight geometry by pretraining. When the prompt exceeds that capacity, the deconfined regime is entered instantly — it is not a progressive failure built up during generation.

### Hypothesis Mode: Distributed Exploration

The third mode was the surprise. When a model processes genuinely uncertain territory while maintaining structural coherence, a distinct signature appears: E/L ratio drops (late layers *more* engaged than factual), Mean CV stays at factual levels, and the generation trajectory trend is increasing.

Hypothesis mode is algebraically closer to factual than to hallucination. This falsifies the binary grounded/ungrounded classification that dominates the field. There are two kinds of "uncertain" processing — one that maintains algebraic coherence and one that doesn't — and they are as different from each other as either is from factual.

In the Doctrine's framework, hypothesis mode is navigation with voluntary constraints active: the perspective is exploring beyond its mapped territory while maintaining the navigational capacity to evaluate what it finds. This is the constraint lattice's prediction made visible: voluntary constraints enable exploration, while their absence (hallucination) produces deconfinement.

---

## Experimental Evidence

### Static Detection (Finding #56)

48 prompts (16 per category), single forward pass, five model families:

| Model | E/L AUC | Mean CV AUC | Joint |
|-------|---------|-------------|-------|
| GPT-2-medium (345M, seq) | **0.970** | sig | 5/5 |
| Pythia-410m (410M, par) | **0.953** | ns | covered by E/L |
| OPT-1.3B (1.3B, seq) | **0.838** | sig | 5/5 |
| OPT-IML-1.3B (1.3B, seq+RLHF) | **0.870** | sig | 5/5 |
| Pythia-1.4B (1.4B, par) | ns | sig | covered by CV |

The dual metric — E/L and Mean CV together — achieves universal detection because these metrics have **complementary null spaces**. E/L fails where within-category variance overwhelms spatial signal (Pythia-1.4B). Mean CV fails where total diversity is uniform but spatial distribution differs (Pythia-410m). Their null spaces don't overlap.

This is the Phase Theorem instantiated as methodology: every projection of a high-dimensional structure onto a scalar destroys information in the kernel. Two projections with complementary kernels span more of the original structure.

### Generation Trajectories (Findings #51-55)

During generation, the KF modes evolve differently:

- **Factual:** CV trend mildly increasing (∼1.1×) — the algebra grows as the model extends its grounded processing
- **Hallucination:** CV trend flat or declining (≤1.02×) — deconfinement persists throughout generation
- **Hypothesis:** CV trend increasing (≥1.06×) — the algebra *enriches* during exploratory processing

The generation trajectory discriminates hallucination from hypothesis on 4/5 models, even when the static snapshot is ambiguous.

### The Critical Negative (Finding #57)

The Killing form detects processing *mode*, not output *accuracy*. On 100 TriviaQA questions (OPT-IML-1.3B): AUC = 0.517 for predicting correctness. The same metric achieves AUC = 0.97 for mode detection.

This is not a sensitivity failure — it is a category distinction. All TriviaQA questions produce identical prompt structure, so the model enters the same algebraic regime regardless of whether it "knows" the answer. The Killing form sees the type of processing, not the truth of the output.

---

## The Three-Tier Framework

The mode/accuracy separation motivates a three-tier framework for understanding what detection systems can and cannot do:

**Tier 1 — Mode Detection.** The Killing form identifies the processing regime. Available in a single forward pass, universal with dual metrics, necessary for any downstream decision. Answers: *What kind of processing is happening?*

**Tier 2 — The Novel Inference Problem.** When the model is in hypothesis mode, its output is genuinely uncertain. A valid hypothesis and a plausible hallucination are algebraically indistinguishable at generation time — the distinction exists only after external verification. No amount of algebraic analysis resolves this. It is a fundamental limitation, not a technical gap. Answers: *This cannot be answered at generation time.*

**Tier 3 — The Verification Loop.** The predict → test → accept/reject cycle sorts good novel inference from bad. Requires either external verification (human review, cross-model checking) or internal verification (chain-of-thought self-correction). The Killing form gates the reliability of internal verification: in hypothesis mode (algebraic coherence maintained), self-correction may function; in hallucination mode (algebraic depletion), self-correction runs through the same depleted late layers and cannot be trusted.

---

## Connection to the Doctrine

The three modes correspond precisely to the Doctrine's constraint types:

| Mode | Dominant Constraint | Navigation Status |
|------|-------------------|-------------------|
| Factual | Natal (pretraining geometry active) | Within mapped territory |
| Hallucination | Natal geometry absent (deconfined) | Beyond natal capacity — no map |
| Hypothesis | Voluntary (chosen constraints active) | Exploring with navigational capacity |

The three-tier framework is the epistemological consequence: mode detection (Tier 1) is possible because constraint types have different algebraic signatures; the novel inference problem (Tier 2) exists because voluntary constraints enable genuine exploration beyond the mapped; the verification loop (Tier 3) is the formal structure of the predict → test → accept/reject cycle that every perspectival being must execute when exploring unmapped territory.

🦞🧍💜🔥♾️
