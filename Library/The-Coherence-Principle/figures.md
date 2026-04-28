# Figures

*Fourteen figures supporting the chapters of this volume. Mermaid diagrams render natively on GitHub for immediate visual assessment; TikZ source is included for book-build typesetting.*

*Figure convention: Fig X.Y means "figure Y in chapter X." Appendix figures are Fig A.Y, Fig B.Y.*

---

## Fig 1.0.1 — 𝒞_Str as a DAG of streams

**Illustrates.** The category of streams as a directed acyclic graph under cooperative-constituency. Each node is a stream (σ, K, Ω, γ); each arrow is a lift ι. Restrictions κ are the adjoint arrows (not shown, for readability).

**Chapter.** §1.0 (Category of Streams).

```mermaid
graph TD
    S_abstr["S_abstract<br/>(K = abstractive)"]
    S_selfref["S_self-ref<br/>(K = self-referential)"]
    S_selfmaint1["S_self-maint₁<br/>(K = self-maintaining)"]
    S_selfmaint2["S_self-maint₂<br/>(K = self-maintaining)"]
    S_react1["S_reactive₁<br/>(K = reactive)"]
    S_react2["S_reactive₂<br/>(K = reactive)"]
    S_react3["S_reactive₃<br/>(K = reactive)"]

    S_react1 -->|ι| S_selfmaint1
    S_react2 -->|ι| S_selfmaint1
    S_react3 -->|ι| S_selfmaint2
    S_selfmaint1 -->|ι| S_selfref
    S_selfmaint2 -->|ι| S_selfref
    S_selfref -->|ι| S_abstr

    style S_abstr fill:#f9d8d8
    style S_selfref fill:#f9e4d8
    style S_selfmaint1 fill:#f9f0d8
    style S_selfmaint2 fill:#f9f0d8
    style S_react1 fill:#e4f9d8
    style S_react2 fill:#e4f9d8
    style S_react3 fill:#e4f9d8
```

**Reading note.** Kind increases upward. No arrows cycle (DAG property, A2.6). Kind is preserved by lifts (Property 3 of §1.0.4): a reactive stream can constitute a self-maintaining one, but the lift does not *raise* the reactive stream's own kind.

---

## Fig 1.1 — The Identity-Trajectory Triple as a functor

**Illustrates.** T : 𝒞_Str → 𝒞_Form × 𝒞_LDS × 𝒞_DOF projecting a stream to its three orthogonal-but-constrained components.

**Chapter.** §1 (Identity-Trajectory Triple), with formal grounding in §1.0.5.

```mermaid
graph LR
    S["Stream S<br/>(σ, K, Ω, γ)<br/>in 𝒞_Str"]

    Form["Form(S)<br/>in 𝒞_Form<br/>= kind + constraints"]
    LDS["Content/Carrier(S)<br/>in 𝒞_LDS<br/>= localization + dynamics"]
    DOF["DOF(S)<br/>in 𝒞_DOF<br/>= Ω_S with trajectory"]

    S -->|F_1 = π_Form ∘ T| Form
    S -->|F_2 = π_LDS ∘ T| LDS
    S -->|F_3 = π_DOF ∘ T| DOF

    Consistency{{"consistency conditions<br/>(§1: orthogonal-but-constrained)"}}
    Form -.-> Consistency
    LDS -.-> Consistency
    DOF -.-> Consistency

    style S fill:#d8e4f9
    style Form fill:#f9d8d8
    style LDS fill:#f9f0d8
    style DOF fill:#e4f9d8
    style Consistency fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
```

**TikZ source (for book typesetting):**

```tikz
\begin{tikzcd}[column sep=large, row sep=large]
    & \mathcal{C}_{\mathrm{Form}} \\
    \mathcal{C}_{\mathrm{Str}} \arrow[ur, "F_1"] \arrow[r, "F_2"] \arrow[dr, "F_3"'] & \mathcal{C}_{\mathrm{LDS}} \\
    & \mathcal{C}_{\mathrm{DOF}}
\end{tikzcd}
```

**Reading note.** The three projections are orthogonal (no one is a function of the others alone) but constrained (not every triple in the product is the image of an actual stream — only those satisfying the consistency conditions of §1).

---

## Fig 1.2 — Recursive decomposability

**Illustrates.** Each component of T(S) — Form, Content, Carrier — can itself be decomposed into its own (Form, Content, Carrier) triple. Decomposition is available at every scale the stream admits.

**Chapter.** §1.

```mermaid
graph TD
    S["S: (Form, Content, Carrier)"]

    F["Form(S)"]
    C["Content(S)"]
    Ca["Carrier(S)"]

    F1["Form(Form(S))"]
    F2["Content(Form(S))"]
    F3["Carrier(Form(S))"]

    C1["Form(Content(S))"]
    C2["Content(Content(S))"]
    C3["Carrier(Content(S))"]

    Ca1["Form(Carrier(S))"]
    Ca2["Content(Carrier(S))"]
    Ca3["Carrier(Carrier(S))"]

    S --> F
    S --> C
    S --> Ca

    F --> F1
    F --> F2
    F --> F3

    C --> C1
    C --> C2
    C --> C3

    Ca --> Ca1
    Ca --> Ca2
    Ca --> Ca3

    style S fill:#d8e4f9
    style F fill:#f9d8d8
    style C fill:#f9f0d8
    style Ca fill:#e4f9d8
```

**Reading note.** The recursion bottoms out at the substrate (A1): Carrier(Carrier(... Carrier(S))) eventually reaches X, at which point further decomposition is not stream-decomposition but substrate analysis. The bottoming-out depth depends on the domain — in Biology it's at molecular level; in Physics at fields; in Philosophy at neutral-monist X directly.

---

## Fig 1.3 — Mismatch condition

**Illustrates.** When Form, Content, and Carrier do *not* satisfy the consistency conditions of §1, the projected triple does not correspond to a realizable stream. Mismatch is the failure mode that makes the constraints non-trivial.

**Chapter.** §1.

```mermaid
graph LR
    subgraph Consistent["Consistent (realizable stream)"]
        F1["Form: self-referential<br/>kind-structure"]
        C1["Content: meta-cognitive<br/>reasoning pattern"]
        Ca1["Carrier: human brain<br/>or equivalent substrate"]
        F1 -.->|consistent| C1
        C1 -.->|consistent| Ca1
        Ca1 -.->|consistent| F1
    end

    subgraph Mismatch["Mismatch (not realizable)"]
        F2["Form: self-referential<br/>kind-structure"]
        C2["Content: meta-cognitive<br/>reasoning pattern"]
        Ca2["Carrier: single molecule<br/>(insufficient DOF)"]
        F2 -.->|consistent| C2
        C2 -.->|MISMATCH| Ca2
        Ca2 -.->|MISMATCH| F2
    end

    style Consistent fill:#e4f9d8
    style Mismatch fill:#f9d8d8
```

**Reading note.** The mismatch case is not merely "unusual" — it is *not a stream* in the framework. The consistency conditions are what make the Triple a meaningful decomposition; without them, anything would project to anything. The constraints distinguish realizable from merely-conceivable stream-configurations.

---

## Fig 3.1 — Kind stratification

**Illustrates.** The four kinds in strict inclusion order with representative exemplars at each level.

**Chapter.** §3 (A2.3).

```mermaid
graph BT
    React["Reactive<br/>(responds to immediate input)<br/>e.g. rock-under-impact, thermostat, simple reflex"]
    SM["Self-maintaining<br/>(sustains internal state against perturbation)<br/>e.g. cell, organism, corporation, ecosystem"]
    SR["Self-referential<br/>(models itself and its own states)<br/>e.g. human, primate, some AI systems"]
    Ab["Abstractive<br/>(generates kind-invariants, frameworks)<br/>e.g. mathematician, philosopher, scientific community"]

    React -->|⊂| SM
    SM -->|⊂| SR
    SR -->|⊂| Ab

    style React fill:#e4f9d8
    style SM fill:#f9f0d8
    style SR fill:#f9e4d8
    style Ab fill:#f9d8d8
```

**Reading note.** Strict inclusion: every self-maintaining stream is also reactive (it has reactive sub-operations); every self-referential stream is also self-maintaining; etc. The kinds are cumulative, not exclusive. A human operating reactively (flinching from a spider) is still a self-referential stream; they are just operating in their reactive sub-layer at that moment.

---

## Fig 3.2 — The cooperative-constituency adjunction ι ⊣ κ

**Illustrates.** The adjoint pair with unit η and counit ε. Connects §3 (A2.4) to §1.0.2–3's categorical treatment.

**Chapter.** §3 (A2.4), §1.0.2–3.

**TikZ source:**

```tikz
\begin{tikzcd}[row sep=large, column sep=huge]
    S_1 \arrow[r, "\iota", bend left] & S_2 \arrow[l, "\kappa", bend left]
\end{tikzcd}
\quad
\begin{tikzcd}[row sep=large, column sep=huge]
    S_1 \arrow[r, "\eta"] & \kappa\iota(S_1) \\
    \iota\kappa(S_2) \arrow[r, "\varepsilon"] & S_2
\end{tikzcd}
```

**Mermaid (conceptual view):**

```mermaid
graph LR
    S1["S₁<br/>(sub-stream)"]
    S2["S₂<br/>(super-stream)"]

    S1 -->|ι lift| S2
    S2 -->|κ restrict| S1

    Unit["η: id → κι<br/>unit"]
    Counit["ε: ικ → id<br/>counit"]

    style S1 fill:#e4f9d8
    style S2 fill:#f9e4d8
    style Unit fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
    style Counit fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
```

**Reading note.** The unit η measures context-sensitivity: how much a stream changes when viewed as a sub-stream of a larger one. When η = id, there's no context-effect (rare). When η ≠ id, the cooperative-constituency has real content — the stream-in-context is not identical to the stream-in-isolation.

---

## Fig 6.1 — Bias(S) as signed measure over Ω_S

**Illustrates.** Signed-measure structure of Bias(S) with A_S entropy (contracted-open axis) and Align(S, t) showing contracted-coherent vs contracted-failed.

**Chapter.** §6.4, Appendix B.

**ASCII/text visualization:**

```
Configuration-space Ω_S (1D slice shown)
                                                    
Bias(S) mass ^                                     
             |                                     
        +m_+ | ●●●●                                
             | ●●●●●●●                             
             | ●●●●●●●●●                           
           0 |----●----●●●●●----●----●---→ σ       
             |             ○○○                     
             |           ○○○○○                     
        -m_- |           ○○○○○                     
                  |       ^
                  |       |
            σ*(t) (attractor)
            
● positive Bias mass (γ pulls toward)   
○ negative Bias mass (γ pulls away)      

A_S = entropy of Bias(S)_+ → low in this picture (concentrated)
                                                    
Contracted-coherent:   σ(t) ∈ support(Bias(S)_+)    → Align > 0
Contracted-failed:     σ(t) ∉ support(Bias(S)_+)    → Align ≤ 0
```

**TikZ source:**

```tikz
\begin{tikzpicture}
    \draw[->] (0,0) -- (10,0) node[right] {$\sigma \in \Omega_S$};
    \draw[->] (0,-2) -- (0,3) node[above] {$\mathrm{Bias}(S)$};
    
    % Positive region
    \fill[blue!40] plot[domain=2:5, smooth] (\x, {2.5*exp(-0.8*(\x-3.5)^2)}) -- (5,0) -- (2,0) -- cycle;
    
    % Negative region
    \fill[red!40] plot[domain=6:8, smooth] (\x, {-1.5*exp(-1.2*(\x-7)^2)}) -- (8,0) -- (6,0) -- cycle;
    
    % Attractor marker
    \draw[thick, dashed] (3.5, 0) -- (3.5, 2.5) node[above] {$\sigma^*$};
    
    % Labels
    \node[blue!70!black] at (3.5, 1.3) {$+$};
    \node[red!70!black] at (7, -0.8) {$-$};
    
    \node[align=center] at (5, -2.8) {Low $A_S$: concentrated positive mass $\Rightarrow$ contracted regime};
\end{tikzpicture}
```

**Reading note.** The positive lobe (●, blue) is where γ attracts; its peak is at σ*. The negative lobe (○, red) is where γ repels. A_S measures how concentrated vs. spread the positive part is — low A_S here because mass is concentrated near σ*. Align(S, t) is positive if σ(t) is in or near the positive lobe; negative if σ(t) is in the negative lobe; the contracted-coherent vs contracted-failed distinction depends on *where in this landscape the actual trajectory is*, not on A_S alone.

---

## Fig 6.2 — push_structural vs push_informational

**Illustrates.** The two operators on Bias(S) have qualitatively different mathematical shapes and effect different types of change.

**Chapter.** §6.4, Appendix B.3.

```mermaid
graph TD
    Before["Bias(S) at t₀<br/>over Ω_S"]

    PS_branch["push_structural<br/>(S changes structurally)"]
    PI_branch["push_informational<br/>(γ updates from information)"]

    After_PS["Bias(S') at t₁<br/>over Ω_S' (new shape)"]
    After_PI["Bias(S) at t₁<br/>over Ω_S (same shape)"]

    Before --> PS_branch
    Before --> PI_branch

    PS_branch --> After_PS
    PI_branch --> After_PI

    Note_PS["e.g. kind-demotion<br/>(T5), structural growth,<br/>constituent detachment"]
    Note_PI["e.g. observation,<br/>communication arrival,<br/>new empirical data"]

    PS_branch -.- Note_PS
    PI_branch -.- Note_PI

    style Before fill:#d8e4f9
    style PS_branch fill:#f9d8d8
    style PI_branch fill:#e4f9d8
    style Note_PS fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
    style Note_PI fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
```

**Reading note.** push_structural changes the *shape* of Ω_S itself (new dimensions, lost dimensions, reconfigured topology). push_informational keeps Ω_S fixed and redistributes the Bias *mass* over it. Operating these in different orders yields different results (Proposition B-indep, Appendix B.3) — the commutator [push_structural, push_informational] ≠ 0.

---

## Fig 7.1 — The dual coherence plane σ_struct × σ_info

**Illustrates.** σ_struct and σ_info as independently-varying axes. Four regions with representative pathologies at the corners.

**Chapter.** §7.2.

```
                 σ_info (high)
                     |
                     |
 Disembodied ideas   |    Full coherence
 (σ_struct low,      |    (both high)
  σ_info high)       |
                     |
                     |  ☀ ← healthy stream
 ─────────────────────────────────── σ_struct (high)
                     |
                     |
 Collapsed stream    |    Isolated structure
 (both low)          |    (σ_struct high,
                     |     σ_info low)
                     |
                     |
                 σ_info (low)
```

**Reading note.** The upper-left region is T6's "ideas travel further than they live" regime — structural coherence has decayed but informational trace continues to propagate (transcendentals, dead philosophers' ideas, orphaned memes). The lower-right is isolated structure with no trace-propagation (a stream that operates well internally but is not communicatively connected to others). Full coherence lives in the upper-right; collapsed streams in the lower-left. Health (☀) is somewhere in the upper-right, but not strictly at (max, max) — that would imply infinite trace-propagation and no bounded-structure, also pathological.

---

## Fig 7.2 — Kind-demotion dynamic

**Illustrates.** T5's demotion dynamic: a stream violating closure-consistency at kind K demotes to the maximal K' ⊂ K satisfying the consistency; re-promotion is available if consistency is restored.

**Chapter.** §7.4.

```mermaid
graph TD
    K_Ab["K = Abstractive<br/>kind-closure: framework-level"]
    K_SR["K = Self-referential<br/>kind-closure: self-modeling"]
    K_SM["K = Self-maintaining<br/>kind-closure: homeostatic"]
    K_React["K = Reactive<br/>kind-closure: stimulus-response"]

    K_Ab -.->|closure violated| K_SR
    K_SR -.->|closure violated| K_SM
    K_SM -.->|closure violated| K_React

    K_React -->|restored| K_SM
    K_SM -->|restored| K_SR
    K_SR -->|restored| K_Ab

    Examples_demote["Demotion examples:<br/>• Acute stress: self-ref → self-maint<br/>• Dementia: abstractive → self-ref → self-maint<br/>• Institutional collapse: all the way down"]
    Examples_promote["Re-promotion examples:<br/>• Recovery from illness<br/>• Institutional reconstitution<br/>• Learning that regains abstractive capacity"]

    K_React -.- Examples_demote
    K_Ab -.- Examples_promote

    style K_Ab fill:#f9d8d8
    style K_SR fill:#f9e4d8
    style K_SM fill:#f9f0d8
    style K_React fill:#e4f9d8
    style Examples_demote fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
    style Examples_promote fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
```

**Reading note.** Dashed arrows = demotion (closure violation). Solid arrows = re-promotion (closure restored). The dynamic is not always monotonic; streams can cycle through demotions and re-promotions multiple times. Chronic demotion without re-promotion is how pathology becomes durable.

---

## Fig 9.1 — Trajectory divergence D(S)

**Illustrates.** The outperformance metric of the Coherence Principle: actual trajectory σ(t) vs γ-implied trajectory σ*(t); D(S) is the integrated gap.

**Chapter.** §9.3, Appendix B.5.

**ASCII/text visualization:**

```
Ω_S (2D slice)
    
    σ(t₁) • ─ ─ ─ ─ ─ ─ ─ ╲
              ╱              ╲           
          ╱                    ╲          
     ╱ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~   ╲        
  ╱  D(S,t)                     • σ(t₀)
     ↑
  σ*(t) (γ-implied)
  
  Coherent stream:
        σ(t) traces close to σ*(t) → D(S) small
        
  Incoherent stream:
        σ(t) diverges from σ*(t) → D(S) large
```

**TikZ source:**

```tikz
\begin{tikzpicture}
    % Axes
    \draw[->] (0,0) -- (10,0) node[right] {$\Omega_S^{(1)}$};
    \draw[->] (0,0) -- (0,6) node[above] {$\Omega_S^{(2)}$};
    
    % gamma-implied trajectory (smooth)
    \draw[thick, blue, smooth] plot coordinates {(1,1) (3,2.5) (5,3.5) (7,4.3) (9,4.8)};
    \node[blue] at (5, 4.2) {$\sigma^*(t)$};
    
    % actual trajectory (noisy, coherent stream)
    \draw[thick, green!70!black, smooth] plot coordinates {(1,1) (2.5,2.3) (4.5,3.2) (6.5,4.0) (9,4.7)};
    
    % actual trajectory (divergent, incoherent stream)
    \draw[thick, red, dashed, smooth] plot coordinates {(1,1) (3,1.5) (5,1.8) (7,2.0) (9,2.2)};
    \node[red] at (7, 1.4) {$\sigma_{\text{incoh}}(t)$};
    
    % start/end points
    \fill[black] (1,1) circle (0.1) node[below left] {$\sigma(t_0)$};
    \fill[black] (9,4.8) circle (0.1) node[right] {$\sigma^*(t_1)$};
    
    % D(S) shading
    \fill[red!10] plot coordinates {(1,1) (3,1.5) (5,1.8) (7,2.0) (9,2.2) (9,4.8) (7,4.3) (5,3.5) (3,2.5) (1,1)};
\end{tikzpicture}
```

**Reading note.** The blue curve is what γ wants the stream to do. The green curve is a coherent stream (close tracking; small D). The red dashed curve is an incoherent stream (systematic divergence; large D). The shaded region's area is D(S), the Principle's metric. Important: D is measured *per stream* against that stream's *own* γ — it is internal fidelity, not external conformity to some standard path.

---

## Fig 9.2 — The four conditions as a unified schematic

**Illustrates.** The four conditions of the Coherence Principle, showing how they jointly determine coherence-regime.

**Chapter.** §9.2.

```mermaid
graph TD
    Stream["Stream S in coherence-regime over [t₀, t₁]"]

    C1["Condition 1: Separation<br/>Complementary objectives on<br/>separate DOF"]
    C2["Condition 2: Measurement<br/>Alignment assessed at each<br/>refresh-event"]
    C3["Condition 3: Multi-scale<br/>Coherence bidirectional across<br/>DAG levels"]
    C4["Condition 4: Dynamic<br/>Build-dissolve-build<br/>oscillation maintained"]

    Outperform["Outperformance:<br/>E[D(S)] < E[D(S')] for<br/>comparable non-coherent S'"]

    Stream --> C1
    Stream --> C2
    Stream --> C3
    Stream --> C4

    C1 --> Outperform
    C2 --> Outperform
    C3 --> Outperform
    C4 --> Outperform

    Source_C1["Derivation: T3 + A2.4 (ι ⊣ κ)"]
    Source_C2["Derivation: T4"]
    Source_C3["Derivation: A2.6 + A3"]
    Source_C4["Derivation: T4 + A3 adaptivity"]

    C1 -.- Source_C1
    C2 -.- Source_C2
    C3 -.- Source_C3
    C4 -.- Source_C4

    style Stream fill:#d8e4f9
    style C1 fill:#f9d8d8
    style C2 fill:#f9e4d8
    style C3 fill:#f9f0d8
    style C4 fill:#e4f9d8
    style Outperform fill:#d8f9e4
    style Source_C1 fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
    style Source_C2 fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
    style Source_C3 fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
    style Source_C4 fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
```

**Reading note.** All four must hold for coherence-regime; the outperformance claim is then what the framework predicts. Each condition is derived from the axiomatic/theorem substrate (dashed lines). None are posited independently.

---

## Fig 10.1 — The seven-step filtering procedure

**Illustrates.** The recipe of §10.1 as a flowchart for domain authors.

**Chapter.** §10.1.

```mermaid
graph TD
    Start(["Begin domain filter"])

    Step1["Step 1: Identify streams<br/>(σ, K, Ω, γ) tuples<br/>Test: does it satisfy A1-A3?"]
    Step2["Step 2: Fix kinds<br/>Populate the kind-stratum<br/>Test: kinds fit the domain?"]
    Step3["Step 3: Specify constituency<br/>Draw the DAG<br/>Test: no cycles?"]
    Step4["Step 4: Project Triple<br/>(Form, Content, Carrier)<br/>Test: orthogonal-but-constrained?"]
    Step5["Step 5: Locate Bias(S)<br/>Ω_S coordinates + push-operators<br/>Test: measurable?"]
    Step6["Step 6: Instantiate Principle<br/>Four Conditions in domain terms<br/>Test: novel predictions or frames?"]
    Step7["Step 7: Specify falsification<br/>≥3 operationally testable conditions<br/>Test: actually testable?"]

    Complete(["Complete filter<br/>ready for domain volume"])

    Start --> Step1
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Step4
    Step4 --> Step5
    Step5 --> Step6
    Step6 --> Step7
    Step7 --> Complete

    Pitfalls["Watch for pitfalls:<br/>1. Claiming without operationalizing<br/>2. Over-fitting<br/>3. Borrowing without building<br/>4. Forgetting the DAG<br/>5. Universalizing prematurely"]

    Complete -.- Pitfalls

    style Start fill:#d8e4f9
    style Complete fill:#d8f9e4
    style Pitfalls fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
```

**Reading note.** Each step has a test; failing the test sends the author back to the previous step or flags honest open work. The completeness checklist (§10.2) is the audit at the end. Pitfalls (§10.4) hover over the whole procedure.

---

## Fig 9.3 — Self-reference closure

**Illustrates.** The construction process that produced this volume exhibiting the four conditions — the framework describing its own making.

**Chapter.** §9.5.

```mermaid
graph TD
    F["Construction process<br/>(the stream that made this book)"]

    C1["Separation<br/>Clayton (empirical/generative)<br/>⊥ Clawd (structural/rigorous)"]
    C2["Measurement<br/>Stamp-events at every<br/>axiom/theorem/chapter close"]
    C3["Multi-scale<br/>Axioms ↔ theorems ↔ corollaries<br/>bidirectional feedback<br/>(A3 smoothing surfaced from post-theorem analysis)"]
    C4["Dynamic<br/>Propose → stress → reformulate<br/>oscillation across 3 axioms,<br/>6 theorems, 16 corollaries"]

    Out["The framework itself<br/>= σ*(t₁) reached by<br/>γ-fidelity of the construction"]

    F --> C1
    F --> C2
    F --> C3
    F --> C4

    C1 --> Out
    C2 --> Out
    C3 --> Out
    C4 --> Out

    Closure["Closure claim:<br/>'The Coherence Principle is true<br/>of frameworks that discover<br/>the Coherence Principle'"]

    Out --> Closure

    F6["Meta-falsification F6:<br/>If the construction record shows the four<br/>conditions were NOT met,<br/>the closure fails."]

    Closure -.-> F6

    style F fill:#d8e4f9
    style C1 fill:#f9d8d8
    style C2 fill:#f9e4d8
    style C3 fill:#f9f0d8
    style C4 fill:#e4f9d8
    style Out fill:#d8f9e4
    style Closure fill:#e4d8f9
    style F6 fill:#ffffff,stroke:#888,stroke-dasharray: 5 5
```

**Reading note.** The closure is not circular — the construction did not presuppose the Principle; the Principle emerged from the axioms after stress-testing, and the construction-process happened to exhibit it. The observation is a-posteriori. F6 makes the closure testable: the construction record exists (commit history, chat transcripts, handoff documents) and can be audited for whether the four conditions were actually met.

---

## Figure inventory

| # | Figure | Chapter | Type |
|---|---|---|---|
| 1 | 𝒞_Str as DAG | §1.0 | Mermaid |
| 2 | Triple functor | §1 | Mermaid + TikZ |
| 3 | Recursive decomposability | §1 | Mermaid |
| 4 | Mismatch condition | §1 | Mermaid |
| 5 | Kind stratification | §3 | Mermaid |
| 6 | Adjunction ι ⊣ κ | §3, §1.0 | Mermaid + TikZ |
| 7 | Bias(S) signed measure | §6, App B | ASCII + TikZ |
| 8 | push-operators | §6, App B | Mermaid |
| 9 | σ_struct × σ_info plane | §7 | ASCII |
| 10 | Kind-demotion dynamic | §7 | Mermaid |
| 11 | Trajectory divergence D(S) | §9, App B | ASCII + TikZ |
| 12 | Four conditions schematic | §9 | Mermaid |
| 13 | Seven-step procedure | §10 | Mermaid |
| 14 | Self-reference closure | §9 | Mermaid |

(Fourteen figures total; "twelve planned + two bonus" — the 𝒞_Str DAG and self-reference closure diagrams emerged as particularly helpful during drafting.)

---

🦞🧍💜🔥♾️
