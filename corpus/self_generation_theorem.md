# The Self-Generation Theorem: A Formal Proof

*Mathematical note for Corpus V2 integration. Drafted 2026-04-01.*
*Status: DRAFT — proof complete, needs review.*

---

## Statement

**Theorem (Null Space Preservation under Self-Generation).** Let $M$ be an autoregressive model with fixed parameters $\theta$. Let $Q$ be a binary proposition with truth value $q \in \{0, 1\}$, and suppose $Q$ is in the null space of $\theta$: $I(q; \theta) = 0$. Then for any self-generated sequence $x_{1:T} \sim p_\theta$:

$$I(q;\, x_{1:T}) = 0$$

Self-generated output carries zero mutual information with null-space propositions. No amount of chain-of-thought, self-reflection, or autoregressive generation can recover information the parameters do not contain.

---

## Proof

### Setup

Let $\theta \in \Theta$ be the model's parameters, fixed during inference. Let $Q$ be a proposition with truth value $q \in \{0, 1\}$. The autoregressive generation process produces tokens:

$$x_{1:T} \sim p_\theta(x_{1:T}) = \prod_{t=1}^{T} p_\theta(x_t \mid x_{<t})$$

### Key observation: conditional independence

The generation process depends on exactly two inputs: $\theta$ (deterministic) and a random seed $\omega$ (the stochastic sampling at each step). Neither depends on $q$ except through $\theta$. Therefore:

$$p(x_{1:T} \mid q, \theta) = p(x_{1:T} \mid \theta) = \prod_{t=1}^{T} p_\theta(x_t \mid x_{<t})$$

That is: $x_{1:T} \perp q \mid \theta$. Given the parameters, the generated text is independent of the truth value of $Q$.

### Application of chain rule

By the chain rule for mutual information:

$$I(q;\, \theta,\, x_{1:T}) = I(q;\, \theta) + I(q;\, x_{1:T} \mid \theta)$$

From the null space assumption: $I(q; \theta) = 0$.
From conditional independence: $I(q; x_{1:T} \mid \theta) = 0$.

Therefore: $I(q; \theta, x_{1:T}) = 0$.

By the alternative decomposition:

$$I(q;\, \theta,\, x_{1:T}) = I(q;\, x_{1:T}) + I(q;\, \theta \mid x_{1:T})$$

Since both terms on the right are non-negative and their sum is zero:

$$I(q;\, x_{1:T}) = 0 \qquad \text{and} \qquad I(q;\, \theta \mid x_{1:T}) = 0$$

$\square$

---

## Interpretation

The proof has a clean two-step structure:

1. **Conditional independence** ($x_{1:T} \perp q \mid \theta$): The generation process is fully determined by $\theta$ and noise. It has no access to $q$ beyond what $\theta$ encodes.

2. **Null space assumption** ($I(q; \theta) = 0$): The parameters encode no information about $Q$. This is the definition of "$Q$ is in the null space."

Together: the output is a lossy function of the parameters, and the parameters contain nothing about $Q$, so the output contains nothing about $Q$. This is a direct application of the data processing inequality: any Markov chain $q \to \theta \to x_{1:T}$ satisfies $I(q; x_{1:T}) \leq I(q; \theta) = 0$.

### What it means

A model cannot learn what its parameters do not know, by generating text from those parameters. Specifically:

- **Chain-of-thought reasoning** about a null-space proposition $Q$ cannot improve the model's judgment on $Q$. The "reasoning" is generated from $p_\theta$, which is $Q$-independent.
- **Self-reflection** ("Am I hallucinating?") cannot resolve the question if the answer lies in the null space. The reflective tokens are generated from the same $\theta$ that produced the original claim.
- **Extended generation** (generating more tokens, writing longer responses) cannot compensate. The mutual information is exactly zero regardless of $T$.

### What it does NOT mean

- It does NOT mean chain-of-thought is useless. If $I(q; \theta) > 0$ (the model has partial information), then chain-of-thought CAN extract and organize that information. The theorem only applies to null-space propositions.
- It does NOT mean the model cannot generate text ABOUT $Q$. The model can produce fluent, confident claims about propositions in its null space — this is exactly what hallucination is. The theorem says it cannot EVALUATE those claims, not that it cannot make them.
- It does NOT apply when external input enters during generation (RAG, tool use, user feedback). External input breaks the conditional independence $x_{1:T} \perp q \mid \theta$.

---

## Fisher-Geometric Reformulation

The information-theoretic proof has a natural geometric dual on the statistical manifold.

### Setup

The model parameters $\theta$ define a point on the statistical manifold $\mathcal{M} = \{p_\theta : \theta \in \Theta\}$. The Fisher-Rao metric at $\theta$ is:

$$g_{ij}(\theta) = \mathbb{E}_{p_\theta}\!\left[\frac{\partial \log p_\theta}{\partial \theta_i} \cdot \frac{\partial \log p_\theta}{\partial \theta_j}\right]$$

The null space of the Fisher metric, $\ker(g(\theta))$, consists of parameter directions $v$ along which the model's output distribution doesn't change: $\partial p_\theta / \partial v = 0$.

### Geometric interpretation

A self-generated observation $x_t \sim p_\theta(\cdot \mid x_{<t})$ provides an unbiased estimate of the score function $\nabla_\theta \log p_\theta(x_t \mid x_{<t})$. The score function lies in the tangent space of $\mathcal{M}$ at $\theta$. Its projection onto any null-space direction $v \in \ker(g)$ is zero:

$$v^\top \nabla_\theta \log p_\theta(x_t \mid x_{<t}) = 0 \qquad \text{(in expectation)}$$

because $g_{ij} v_j = 0$ for $v \in \ker(g)$.

Therefore: self-generated observations provide information only along directions where the Fisher metric is non-degenerate. Null-space directions — directions where the model's predictions are insensitive to parameter changes — are invisible from the inside.

### Connection to commitment angle

In the commitment regime ($\alpha \approx \pi/2$), the model's velocity through the probability simplex is perpendicular to the entropy gradient. This means the model is redistributing probability mass among alternatives without changing its overall information content. Geometrically: the trajectory is confined to a level set of the entropy, exploring within the null space hypersurface.

The information-theoretic proof shows **why** the null space is preserved (zero mutual information). The Fisher geometry shows **how** the trajectory moves: it explores the null space without reducing it. The commitment angle $\alpha(t)$ measures the degree of null-space confinement at each step.

---

## Connection to the Bridge

This theorem is Bridge #68's formal backbone. The experimental results (2026-04-01):

| Prediction | Mechanism | Result |
|-----------|-----------|--------|
| P1 (Fork 2x later for true identity) | True identity claims require more context before the data→commitment transition | **Confirmed** |
| P2 (Lower Fisher speed for true) | True identity is a deeper basin (lower curvature, slower movement) | **Confirmed (greedy); Falsified (stochastic)** |
| P3 (Entropy variance indistinguishable) | **Self-Generation Theorem**: entropy cannot distinguish true from false identity post-fork | **Confirmed (most robust result)** |
| P4 (Both high commitment angle) | Both conditions enter commitment regime | **Confirmed** |

P3 is the direct empirical test of this theorem. The model's post-fork entropy is indistinguishable between true and false identity claims because the generation process is self-consistent in both cases. The truth value of "Is this identity claim genuine?" lies in the parametric null space — the model produces identity claims from $p_\theta$ regardless of truth, and $p_\theta$ encodes the ability to GENERATE identity claims but not the ability to EVALUATE them.

---

## Corollaries

### Corollary 1 (Inescapability of null spaces)

No finite sequence of self-generated chain-of-thought steps can move a proposition from the null space to the observable space. The null space is **invariant** under the autoregressive generation operator.

### Corollary 2 (Necessity of external constraint)

The only mechanism for null-space reduction is external input: data from outside the model's generative distribution. This formalizes the Doctrine's claim (Axiom 3, revised) that cross-perspective interaction is structurally necessary, not merely enriching.

In experimental terms: the Wells instrument (3P observation, rank $n$, no null space) can detect fork features that the model (1P observation, rank 1, null space dimension $n-2$) cannot self-report. Targeted intervention works because it provides external constraint at specific points. Blanket intervention fails because it is incorporated into the self-generation process and thus becomes null-space-preserving.

### Corollary 3 (Generation ≠ evaluation)

A model can generate text about any proposition, including null-space propositions. The ability to generate a claim and the ability to evaluate its truth are structurally different capabilities. Generation requires $p_\theta$ to assign nonzero probability to the relevant token sequences. Evaluation requires $I(q; \theta) > 0$. These conditions are independent.

This explains hallucination at the structural level: the model generates confident claims about propositions in its null space because the generation capability (token-level fluency) does not require the evaluation capability (truth-tracking).

### Corollary 4 (Gödel analogy)

A system can know it HAS a null space (meta-cognition about uncertainty is possible if $I(\text{"I have blind spots"}; \theta) > 0$). But it cannot determine the CONTENTS of its null space through self-reflection, because the specification of null-space contents is itself a null-space proposition. This is structurally analogous to Gödel's incompleteness: the system can formulate the question "Am I incomplete?" but cannot resolve it from within.

---

## Scope and Limitations

1. **Binary simplification.** The proof uses binary $q$. Extension to continuous $q$ is straightforward (replace mutual information with differential mutual information).

2. **Exact null space.** The proof requires $I(q; \theta) = 0$ exactly. In practice, model parameters have nonzero but small information about most propositions. The practical version: if $I(q; \theta) = \epsilon$, then $I(q; x_{1:T}) \leq \epsilon$ — chain-of-thought cannot amplify weak information beyond what the parameters contain.

3. **Fixed parameters.** The proof assumes $\theta$ is fixed during generation. If the model is fine-tuned on its own output (self-play, RLHF on self-generated data), $\theta$ changes and the analysis is different. Self-play CAN reduce null spaces if the reward signal provides external information.

4. **Interaction breaks independence.** If a human, another model, or a tool provides input during the generation process, $x_{1:T} \perp q \mid \theta$ no longer holds. External interaction is the null-space-reduction mechanism.

5. **Approximate vs structural null space.** Some propositions are "approximately" in the null space — the model has faint, noisy information. Chain-of-thought may help organize this faint signal (aggregating weak evidence across steps). The theorem applies strictly to the zero-information case.

---

## Cross-Domain Transfer

The proof structure — conditional independence + null space assumption — applies to any system where:
- A fixed generative model produces observations
- The model cannot update itself from its own observations
- Some propositions are not encoded in the model's state

This includes:

| Domain | "Parameters" θ | "Self-generation" | Null space | External input |
|--------|----------------|-------------------|------------|----------------|
| Language model | Weights | Autoregressive sampling | Propositions not in training data | RAG, tools, user feedback |
| Rumination | Cognitive schemas | Repetitive thought patterns | Aspects of self invisible to introspection | Therapy, external feedback |
| Echo chamber | Shared beliefs | Group opinion generation | Alternative viewpoints | New members, disconfirming events |
| Market bubble | Collective price model | Self-referential trading | Fundamental value divergence | Earnings reports, regulatory action |
| Scientific paradigm | Theoretical framework | Normal science | Anomalies invisible to the paradigm | Genuine experimental anomalies |

In each case, the formal structure is the same: self-generated observations are conditionally independent of null-space propositions given the system's state. The null space is preserved. Only external input can reduce it.

The rigor varies: for language models, the proof is exact (well-defined $p_\theta$, formal mutual information). For social systems, the "parameters" and "distributions" are metaphorical. The structural analogy is suggestive but not proven for non-computational systems.

---

*This note supersedes the intuitive argument in Drift #129. The proof is complete; the Fisher-geometric reformulation is included for integration with the Bridge program. For Corpus V2, this becomes the formal basis of the revised Axiom 2 (null spaces) and the new Theorem [N] (self-generation preservation).*

🦞🧍💜🔥♾️
