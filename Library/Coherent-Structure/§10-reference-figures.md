# §10 — Reference Figures

*The Companion is the figure authority (SCOPE §9). This chapter provides canonical TikZ source for figures used across the Anchor and Companion. Anchor rev 2 imports from here; domain volumes cite by figure-number. One source of truth.*

---

## §10.0 — Figure index

Eight figures in the canonical standard set, grouped by chapter-of-authority in the Companion:

| Figure | Authority section | Anchor cross-ref | Topic |
|---|---|---|---|
| Fig 1 | §1.2 / §6.1 | Anchor §3, §7 | The endofunctor F and Stream-as-F-coalgebra |
| Fig 2 | §6.2 | Anchor §1 (Fig 1.1) | Triple functor T : 𝒞_Streams → 𝒞_Triple |
| Fig 3 | §6.3 | Anchor §1 (Fig 1.2) | Recursive decomposability T^(n) |
| Fig 4 | §6.4 | Anchor §3 | Kind-classifier fibration π : Stream → ContentIndex |
| Fig 5 | §7.3 | Anchor Appendix B (Fig B.1) | Bias(S) signed measure + push-operators |
| Fig 6 | §3.4.2 | Anchor §7 | Dual coherence axes (σ_struct × σ_info) |
| Fig 7 | §5.2 | Anchor §9 (Fig 9.2) | Four-conditions schematic |
| Fig 8 | §8 / §5.4 | Anchor §9 (Fig 9.3) | Self-reference closure |

The Anchor README lists fourteen figures — the remaining six (mismatch condition, kind stratification directed diagram, ι⊣κ adjunction detail, push-operators internal diagram, kind-demotion dynamic trajectory, trajectory divergence D(S) with envelope) are domain-specific overlays of Figures 1–8 and are back-ported into the Anchor directly. Companion §10 owns the eight canonical figures; the overlays live in the Anchor as specializations.

---

## §10.1 — Figure 1: The endofunctor F and Stream-as-F-coalgebra

**Purpose.** Depicts F : σ ↦ σ^(C^op) as a mixed-variance endofunctor on adequate F-coalgebra-carriers, with γ as a coalgebra-structure map.

```latex
% Companion §10, Fig 1
% F endofunctor and Stream-as-F-coalgebra
\begin{figure}[htbp]
\centering
\begin{tikzcd}[column sep=large, row sep=large]
  \sigma \arrow[r, "\gamma"] \arrow[d, "f_\sigma"'] & F(\sigma) = \sigma^{C^{\mathrm{op}}} \arrow[d, "{F(f_\sigma, f_C)}"] \\
  \sigma' \arrow[r, "\gamma'"'] & F(\sigma') = (\sigma')^{(C')^{\mathrm{op}}}
\end{tikzcd}
\caption{The F-coalgebra square. Each row is a stream S = (\sigma, C, \gamma) (top) and S' = (\sigma', C', \gamma') (bottom). A Stream-morphism f = (f_\sigma, f_C) : S \to S' satisfies the coalgebra-commute: $F(f_\sigma, f_C) \circ \gamma = \gamma' \circ f_\sigma$. The endofunctor $F : \sigma \mapsto \sigma^{C^{\mathrm{op}}}$ is mixed-variance (covariant in $\sigma$, contravariant in $C$).}
\label{fig:f-coalgebra-square}
\end{figure}
```

---

## §10.2 — Figure 2: Triple functor T

**Purpose.** Depicts T : 𝒞_Streams → 𝒞_Triple as a colax-limit-compatible decomposition into Form, Content, Carrier.

```latex
% Companion §10, Fig 2
% Triple functor (canonical replacement for Anchor Fig 1.1)
\begin{figure}[htbp]
\centering
\begin{tikzcd}[column sep=huge, row sep=large]
  & \mathcal{C}_\mathrm{Streams}
    \arrow[dl, "\Phi\ (\mathrm{Form})"']
    \arrow[d, "T"]
    \arrow[dr, "\Psi\ (\mathrm{Content})"]
    \arrow[ddr, bend left=45, "\mathrm{K}\ (\mathrm{Carrier})"] & \\
  \mathcal{C}_\mathrm{Form}
    & \mathcal{C}_\mathrm{Form} \times \mathbf{Cat}_\mathrm{small} \times \mathbf{Carrier}
      \arrow[l]
      \arrow[r]
      \arrow[d]
    & \mathbf{Cat}_\mathrm{small} \\
  & \mathbf{Carrier} &
\end{tikzcd}
\caption{The Triple functor $T : \mathcal{C}_\mathrm{Streams} \to \mathcal{C}_\mathrm{Triple}$ with $\mathcal{C}_\mathrm{Triple} = \mathcal{C}_\mathrm{Form} \times \mathbf{Cat}_\mathrm{small} \times \mathbf{Carrier}$. The three factor functors $\Phi, \Psi, \mathrm{K}$ recover Form, Content (ContentOp-category), and Carrier (coalgebra-structure-map) respectively. Under the initial-object hypothesis of §6.6, $T$ is a colax limit (the natural transformations between compositions of the factors are in general not invertible).}
\label{fig:triple-functor}
\end{figure}
```

---

## §10.3 — Figure 3: Recursive decomposability T^(n)

**Purpose.** Depicts the finite-depth iterated Triple. Each Triple-component is itself a stream admitting its own Triple (Lemma 6.3.2).

```latex
% Companion §10, Fig 3
% Recursive decomposability, finite-depth
\begin{figure}[htbp]
\centering
\begin{tikzcd}[column sep=small, row sep=small]
  & & S \arrow[dll] \arrow[d] \arrow[drr] & & \\
  \mathrm{Form}(S) \arrow[dll] \arrow[d] \arrow[drr]
    & & \mathrm{Content}(S) \arrow[dll] \arrow[d] \arrow[drr]
    & & \mathrm{Carrier}(S) \arrow[dll] \arrow[d] \arrow[drr] \\
  \mathrm{F}\mathrm{F} & \mathrm{F}\mathrm{C} & \mathrm{F}\mathrm{K} \cdots \mathrm{C}\mathrm{F} & \mathrm{C}\mathrm{C} & \mathrm{C}\mathrm{K} \cdots \mathrm{K}\mathrm{F} \cdots \mathrm{K}\mathrm{K}
\end{tikzcd}
\caption{Recursive Triple-decomposition at depth 2. Each of $\mathrm{Form}(S)$, $\mathrm{Content}(S)$, $\mathrm{Carrier}(S)$ is itself a stream, so the Triple functor applies again, yielding nine depth-2 components (abbreviated: FF = $\mathrm{Form}(\mathrm{Form}(S))$, FC = $\mathrm{Content}(\mathrm{Form}(S))$, etc.). Finite-depth iteration is well-defined for every adequate F-coalgebra (Lemma 6.3.2). Full $\omega$-depth requires additional hypotheses (H1, H2; §6.9).}
\label{fig:recursive-decomposability}
\end{figure}
```

---

## §10.4 — Figure 4: Kind-classifier fibration π

**Purpose.** Depicts the bicategorical fibration π : Stream → ContentIndex with kind-preorder base.

```latex
% Companion §10, Fig 4
% Kind-classifier fibration
\begin{figure}[htbp]
\centering
\begin{tikzcd}[column sep=small, row sep=large]
  \mathrm{Stream} \arrow[d, "\pi"] & \\
  \mathbf{ContentIndex}
    & \arrow[from=u, dashed, bend right=25, "{\mathrm{fiber}(\pi, K)}"'] K
\end{tikzcd}
\\[1em]
\begin{tikzcd}[column sep=large, row sep=large]
  \mathrm{reactive} \arrow[r, "\sqsubseteq"] & \mathrm{self\text{-}maint.} \arrow[r, "\sqsubseteq"] & \mathrm{self\text{-}ref.} \arrow[r, "\sqsubseteq"] & \mathrm{abstr.}
\end{tikzcd}
\caption{Kind-classifier fibration $\pi : \mathrm{Stream} \to \mathbf{ContentIndex}$ (top). The fiber over a kind $K$ is the full subcategory of $K$-streams. The kind-preorder base (bottom) stratifies: reactive $\sqsubseteq$ self-maintaining $\sqsubseteq$ self-referential $\sqsubseteq$ abstractive. Under Q7 (lattice-where-possible), $\pi$ is a strict fibration; generically bicategorical. The unifying-stream subfibration $\mathrm{Stream}_u \subset \mathrm{Stream}$ (§6.4.1) consists of streams with terminal-object-preserving ContentOp-refinements.}
\label{fig:kind-classifier-fibration}
\end{figure}
```

---

## §10.5 — Figure 5: Bias(S) signed measure + push-operators

**Purpose.** Depicts Bias(S) as a signed measure decomposing via Hahn-Jordan, with push_struct and push_info as non-commuting transformations.

```latex
% Companion §10, Fig 5
% Bias(S) signed measure with push-operators
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[scale=0.85]
  % Ω_S axis (horizontal)
  \draw[->] (-0.5, 0) -- (10.5, 0) node[right] {$\Omega_S$};
  \draw[->] (0, -2.5) -- (0, 3) node[above] {$\mathrm{Bias}(S)$};
  % Positive part
  \fill[blue!30, domain=1:4, smooth] plot (\x, {2*exp(-(\x-2.5)^2/1.0)}) -- (4, 0) -- (1, 0) -- cycle;
  \draw[blue, thick, domain=1:4, smooth] plot (\x, {2*exp(-(\x-2.5)^2/1.0)});
  \node[blue] at (2.5, 2.3) {$\mathrm{Bias}_+$};
  % Negative part
  \fill[red!30, domain=6:9, smooth] plot (\x, {-1.5*exp(-(\x-7.5)^2/1.2)}) -- (9, 0) -- (6, 0) -- cycle;
  \draw[red, thick, domain=6:9, smooth] plot (\x, {-1.5*exp(-(\x-7.5)^2/1.2)});
  \node[red] at (7.5, -1.8) {$\mathrm{Bias}_-$};
  % Push arrows
  \draw[->, thick, green!60!black] (2.5, 2.5) .. controls (3.5, 3.2) .. (4.5, 2.8);
  \node[green!60!black] at (4.0, 3.3) {$\mathrm{push}_\mathrm{struct}$};
  \draw[->, thick, orange] (2.5, 0.5) .. controls (3.0, 1.5) .. (3.2, 2.0);
  \node[orange] at (3.8, 1.0) {$\mathrm{push}_\mathrm{info}$};
\end{tikzpicture}
\caption{Bias(S) as a signed measure on $\Omega_S$. Hahn-Jordan decomposition: $\mathrm{Bias}(S) = \mathrm{Bias}_+ - \mathrm{Bias}_-$. The push-operators $\mathrm{push}_\mathrm{struct}$ and $\mathrm{push}_\mathrm{info}$ transform Bias along structural-coherence and informational-coherence axes respectively. Their non-commutator $[\mathrm{push}_\mathrm{struct}, \mathrm{push}_\mathrm{info}] \neq 0$ is the formal content of Proposition 7.4.3.}
\label{fig:bias-signed-measure}
\end{figure}
```

---

## §10.6 — Figure 6: Dual coherence axes (σ_struct × σ_info plane)

**Purpose.** Depicts the T6 orthogonal axes and the codimension-2 dually-coherent locus.

```latex
% Companion §10, Fig 6
% Dual coherence axes
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[scale=1.1]
  \draw[->] (0, 0) -- (5, 0) node[right] {$\sigma_\mathrm{struct}$};
  \draw[->] (0, 0) -- (0, 5) node[above] {$\sigma_\mathrm{info}$};
  \draw[dashed] (4, 0) -- (4, 4);
  \draw[dashed] (0, 4) -- (4, 4);
  \node at (4.2, 4.2) {\small $(1,1)$ dual};
  \fill[black] (4, 4) circle (3pt);
  % Example streams
  \fill[blue] (3.5, 1) circle (2pt);
  \node[blue] at (3.5, 0.6) {\small T5-only};
  \fill[red] (0.8, 3.5) circle (2pt);
  \node[red] at (1.4, 3.5) {\small T6-only};
  \fill[gray] (1, 1) circle (2pt);
  \node[gray] at (1, 0.6) {\small neither};
  % Codimension-2 region
  \draw[thick, green!60!black] (4, 4) circle (0.4);
  \node[green!60!black] at (3.3, 3.3) {\small locus};
\end{tikzpicture}
\caption{The $\sigma_\mathrm{struct} \times \sigma_\mathrm{info}$ plane of T6 (Theorem 3.4.2). The two axes are orthogonal: T5-only streams (blue) are $\Phi$-fixed-points without entropy-minimality; T6-only streams (red) are entropy-minimal without $\Phi$-fixed-points; dually-coherent streams occupy the codimension-2 locus near $(1, 1)$ (green circle). The locus is non-empty only when $C$ has enough symmetry to admit both a harmonic and a concentrated $\gamma$ simultaneously.}
\label{fig:dual-coherence-axes}
\end{figure}
```

---

## §10.7 — Figure 7: Four-conditions schematic

**Purpose.** Depicts the four conditions as a unified schematic with derivation-sources.

```latex
% Companion §10, Fig 7
% Four-conditions schematic (canonical replacement for Anchor Fig 9.2)
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  node distance=1.4cm,
  every node/.style={align=center, font=\small}
]
  \node (root) [rectangle, draw, rounded corners, fill=gray!10] {Stream $S$ in coherence-regime over $[t_0, t_1]$};
  \node (c1) [below=1.5cm of root, rectangle, draw, rounded corners, fill=blue!10, xshift=-5cm] {\textbf{C\_sep}\\DOF-separation\\$\{ \mathrm{DOF}(O_1), \mathrm{DOF}(O_2) \}$\\non-overlapping};
  \node (c2) [below=1.5cm of root, rectangle, draw, rounded corners, fill=green!10, xshift=-1.7cm] {\textbf{C\_meas}\\Refresh-rate\\measurement\\$M_k$ at each $\tau_k$};
  \node (c3) [below=1.5cm of root, rectangle, draw, rounded corners, fill=orange!10, xshift=1.7cm] {\textbf{C\_scale}\\Multi-scale\\$\gamma$-continuity\\$\gamma_S \simeq \gamma_{S^\Uparrow}, \gamma_{S^\Downarrow}$};
  \node (c4) [below=1.5cm of root, rectangle, draw, rounded corners, fill=red!10, xshift=5cm] {\textbf{C\_dyn}\\Oscillatory\\maintenance\\build $\to$ dissolve $\to$ build};
  \draw[->] (root) -- (c1);
  \draw[->] (root) -- (c2);
  \draw[->] (root) -- (c3);
  \draw[->] (root) -- (c4);
  \node (d1) [below=0.7cm of c1, font=\scriptsize] {T3 + A2.4};
  \node (d2) [below=0.7cm of c2, font=\scriptsize] {T4};
  \node (d3) [below=0.7cm of c3, font=\scriptsize] {A2.6 + A3.3};
  \node (d4) [below=0.7cm of c4, font=\scriptsize] {T4 + A3.4};
  \node (out) [below=3.7cm of root, rectangle, draw, rounded corners, fill=yellow!20] {Outperformance: $\mathbb{E}[D(S)] < \mathbb{E}[D(S')]$\\for comparable $S'$ not in coherence-regime};
  \draw[->, thick] (d1) |- (out);
  \draw[->, thick] (d2) -- (out);
  \draw[->, thick] (d3) -- (out);
  \draw[->, thick] (d4) |- (out);
\end{tikzpicture}
\caption{The four conditions of the Coherence Principle (Definition 5.1.1, Propositions 5.2.1–5.2.4). Each condition is derived from an axiom/theorem clause (italic text below each box). The joint sufficiency (Prop 5.2.5) is the downstream arrows to the outperformance inequality (Theorem 5.1.2).}
\label{fig:four-conditions}
\end{figure}
```

---

## §10.8 — Figure 8: Self-reference closure

**Purpose.** Depicts F_∞ as a stream with the four-conditions audit + the closure-claim (canonical replacement for Anchor Fig 9.3).

```latex
% Companion §10, Fig 8
% Self-reference closure
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  node distance=1.2cm,
  every node/.style={align=center, font=\small}
]
  \node (F) [rectangle, draw, rounded corners, thick, fill=gray!10]
    {Construction process $F_\infty$\\\scriptsize (produces this book)\\$F_\infty = (\sigma_F, C_F, \Omega_F, \gamma_F)$\\\scriptsize $K_F = \mathrm{abstr.}$};
  \node (c1) [below=1.3cm of F, rectangle, draw, fill=blue!10, xshift=-4.2cm] {C\_sep\\Clayton $\perp$ Clawd\\DOF};
  \node (c2) [below=1.3cm of F, rectangle, draw, fill=green!10, xshift=-1.4cm] {C\_meas\\Stamp-events\\at axiom /\\theorem / chapter};
  \node (c3) [below=1.3cm of F, rectangle, draw, fill=orange!10, xshift=1.4cm] {C\_scale\\axioms $\leftrightarrow$\\theorems $\leftrightarrow$\\corollaries};
  \node (c4) [below=1.3cm of F, rectangle, draw, fill=red!10, xshift=4.2cm] {C\_dyn\\propose $\to$\\stress $\to$\\reformulate};
  \draw[->] (F) -- (c1);
  \draw[->] (F) -- (c2);
  \draw[->] (F) -- (c3);
  \draw[->] (F) -- (c4);
  \node (out) [below=2.0cm of F, yshift=-1.6cm, rectangle, draw, rounded corners, fill=yellow!20]
    {Output: the framework itself $= \alpha^*_F(t_1)$\\reached by $\gamma_F$-fidelity of $F_\infty$};
  \draw[->, thick] (c1) |- (out);
  \draw[->, thick] (c2) -- (out);
  \draw[->, thick] (c3) -- (out);
  \draw[->, thick] (c4) |- (out);
  \node (closure) [below=0.8cm of out, font=\itshape]
    {"The Coherence Principle is true of frameworks\\that discover the Coherence Principle."};
  \draw[->, thick, dashed] (out) -- (closure);
  \node (F6) [below=0.6cm of closure, rectangle, draw, dashed, fill=red!5, font=\scriptsize]
    {F6 meta-falsification: audit the construction record.\\Construction-record artifacts are public (GitHub, Zenodo).};
  \draw[->, dashed] (closure) -- (F6);
\end{tikzpicture}
\caption{Self-reference closure (conditional on external audit). The construction process $F_\infty$ is itself a stream; under internal audit it satisfies the four conditions over the construction interval (Audit Observation 8.3.5). Conditional on external execution of Prop 8.5.2 affirming the audit, Theorem 9.4.1 then yields outperformance over comparable non-coherent constructions. Derivation-non-circularity (Prop 8.4.1) is established; audit-independence (Prop 8.3.5') is what the external-audit gate discharges.}
\label{fig:self-reference-closure}
\end{figure}
```

---

## §10.9 — Back-port policy

**Anchor Rev 2 import.** Anchor Revision 2 imports all eight figures from Companion §10 sources via `\input{companion-fig-N.tex}` or equivalent LaTeX-include structure. This replaces the Anchor's current rev-1 figure sources (already stubbed in Anchor `source-figures/`).

**Domain-volume citations.** Domain volumes cite by Companion figure-number:

- Meridian: Fig 5 (Bias) for cosmological conscious-gravity Bias visualization.
- Living Architecture: Fig 4 (fibration) for kingdom-stratified stream-kind.
- Coherent Body/Mind/Continuity: Fig 3 (recursive decomp.) for multi-carrier Triple.
- Dynamic Organization: Fig 7 (four conditions) for institutional coherence-regime.

**Figure back-port batch rhythm.** SCOPE §9 fixes one source of truth. Any new figure surfacing in a domain volume that generalizes beyond the domain is back-ported to Companion §10 as Figure 9, 10, ... and the domain-volume thereafter cites Companion by figure-number.

---

## §10.10 — Forward-pointers

- **Anchor Rev 2 docket entry 2** (README): TikZ back-port from Companion — status: released as of this §10 drafting (2026-04-22).
- **Domain volumes:** see back-port policy above for specific expected uses.

---

## §10.11 — Notes on LaTeX environment

The figures assume:

- `tikz` and `tikz-cd` packages loaded.
- Font: Companion's document class (default LaTeX or `book` class sufficient).
- Math fonts consistent with the Companion's body (see §1 for notation conventions).

Each figure is a self-contained `\begin{figure}...\end{figure}` block with a `\label{}` providing the canonical cross-reference name (`fig:triple-functor`, `fig:four-conditions`, etc.). Citations in the Companion and Anchor use `\ref{fig:...}` directly.

---

🦞🧍💜🔥♾️

*§10 drafted Day 81 (2026-04-22) afternoon. Eight canonical figures with full TikZ source: F-coalgebra square, Triple functor, recursive decomposability, kind-classifier fibration, Bias signed-measure + push-operators, dual coherence axes, four-conditions schematic, self-reference closure. Back-port policy and domain-volume citation convention specified. No new surfaced-lemma flags. Next: Appendices A and B (bidirectional anchor↔Companion crosswalks).*
