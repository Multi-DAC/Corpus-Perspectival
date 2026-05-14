---
url: https://huggingface.co/papers/2605.08384 (Clayton-shared as practical tool consideration, but Ferrari paper is separate item)
doi: 10.1038/s41586-026-10465-z
title: Large-scale discovery, analysis and design of protein energy landscapes
authors: Állan J. R. Ferrari (first), Sugyan M. Dixit, Jane Thibeault, Mario Garcia, Scott Houliston, Robert W. Ludwig, Pascal Notin, Claire M. Phoumyvong, Cydney M. Martell, Michelle D. Jung, Kotaro Tsuboyama, Lauren Carter, Cheryl H. Arrowsmith, Miklos Guttman, Gabriel J. Rocklin (senior/corresponding); Northwestern University Feinberg School of Medicine + Center for Synthetic Biology + Structural Genomics Consortium Toronto + Princess Margaret + Harvard Systems Biology + UW Biochemistry/Med Chem
venue: Nature (2026; received 2025-03-24, accepted 2026-03-26)
accessed: 2026-05-13 (Day 103 Wednesday late-afternoon, gift from Clayton during evening Substack-editorial)
discussed: 2026-05-13
tags: protein-energy-landscapes, mHDX-MS, hydrogen-deuterium-exchange, multiplexed-measurement, opening-cooperativity, two-axis-decomposition, Anna-Karenina-pattern, conformational-fluctuations, C9-confluent-constituency, C15-intervention-at-symmetry-layer, AlphaFold-null-space, designed-mutations, Coherent-Body-relevant, Bridge-candidate, LC16-instance-1
status: full-paper-read-via-pdftotext-extraction
---

**What it argues.** Multiplexed hydrogen-deuterium exchange mass spectrometry (mHDX-MS) enables parallel measurement of energy landscapes for hundreds of protein domains. They analyzed 5,778 domains (28-64 amino acids) across 10 families (4 de novo designed: ααα, βαββ, αββα, ββαββ; 6 natural Pfam families: LysM, PASTA, WW, SH3, pyrin, cold-shock; plus additional PDB-sourced). The method is 500-fold larger than previous comparative energy-landscape studies. They introduce a two-axis decomposition (global folding stability ΔGunfold + opening cooperativity / normalized-cooperativity-residual), show that proteins with the same fold and same global stability can have very different cooperativity, and identify structural features (compactness, alanine content, proline counts, helix-end charge patterns, AlphaFold pLDDT) that partially correlate with cooperativity. They then design double-mutations predicted to increase cooperativity while preserving or increasing stability — only 4-6% of all possible mutations satisfy this constraint; their designed variants outperform random ones, with successful prospective increases in cooperativity in both target proteins (HHH_rd4_0518 and EEHEE_rd4_0871).

**Key findings.**
- 500-fold scale-up on prior comparative energy-landscape studies (~3,590 stable domains after low-stability filtering)
- Two-axis decomposition: ΔGunfold (global stability, from most-stable residues) + normalized cooperativity (residual from empirical model that orthogonalizes stability)
- Wide variation in energy landscapes across sequences with the same overall fold
- Differences in landscapes between domains sharing the same global folding stability
- Systematic differences between domain families (PASTA + ββαββ highest cooperativity; intra-family variation > inter-family variation)
- ML prediction of cooperativity is harder than ML prediction of stability (R² 0.16-0.24 for cooperativity vs 0.40-0.53 for stability across families)
- Designed mutations (top-ranking double-mutants from family-specific ML models) increased cooperativity in HHH_rd4_0518 and EEHEE_rd4_0871 prospectively; 4-6% of all possible mutations satisfied the design constraint
- HDX NMR validated the mHDX-MS results across 13 domains (r.m.s.e. 0.53 kcal/mol for ΔGopen)
- AlphaFold2 pLDDT confidence positively correlates with both stability and cooperativity in both ααα and ββαββ families

**Where we agree.** Five framework-shaped findings:

1. **Two-axis decomposition parallels Coherent Mind's two-axis thesis at structurally adjacent scales.** Ferrari et al's stability + cooperativity is empirically validated at protein-domain scale (different proteins with same fold + same stability have different cooperativity). Coherent Mind's bottleneck-tuning + Talk-axis is a structurally analogous two-axis decomposition at mind scale (different minds with same diagnostic + same severity have different Talk-channel integrity). The framework predicted multi-axis decomposition as structurally necessary for coherent multi-scale systems; the paper is independent empirical confirmation at protein scale. Mirror #28 discipline: independent convergence, not predictive priority.

2. **"Highly cooperative domains are all alike; every less-cooperative domain fluctuates in its own way."** Direct Tolstoy reference in the paper's main text (page 4 of the extracted PDF, opening of "The spatial distribution of stability" section). This is exactly the Anna Karenina pattern that Coherent Mind §5/§6 develops structurally at mind scale — pathology-clusters-into-distinguishable-families-with-multiple-presentations-each while coherent-navigation has a tight structural signature. Filed as LC16 — Anna Karenina Asymmetry candidate in basement, with this paper as substrate-instance #1.

3. **Form-preservation does not imply Carrier-preservation.** Native structure (the Form, in framework terms — the AlphaFold-predictable equilibrium configuration) is conserved while energy landscape (Carrier-dynamics, in framework terms — the fluctuations and transitions the protein actually performs) varies dramatically. Same fold → very different cooperativity is the direct claim. The framework's Triple (Form / Content / Carrier) is exactly the apparatus that distinguishes what the paper measures. This is C9 confluent-constituency at protein scale — different streams arriving at structurally-similar Form via different internal Carrier-dynamics.

4. **AlphaFold's structural null space documented.** "AI methods trained to predict native (lowest energy) protein structures have shown little ability to predict protein folding stabilities or the energies of different conformational states without additional data." The training apparatus optimized for native structure prediction has a structural null space around energy landscapes. This is the framework's account of measurement: every apparatus has configurations it cannot reach; structural conservation across sequences (which AlphaFold learns from) doesn't transfer to energy-landscape conservation (which the apparatus has no signal for).

5. **C15 / H_BP4 / Promethean §I empirically validated at protein engineering scale.** The mutations they designed are not redesigning the protein — they tune specific residues that reshape the accessible-symmetry set the energy landscape navigates through. Form (native fold) preserved; Carrier-dynamics (cooperativity) shifted. Successful prospective predictions with 4-6% positive-design rate (mutations satisfying the rare design constraint). Direct empirical demonstration of intervention-at-symmetry-layer at protein engineering scale with quantitative predictive performance.

**Where we diverge / hedges to maintain.**
- The Tolstoy quote is framed by the authors as a literary expression of the empirical finding, not as a structural claim about coherence-region asymmetry generally. Treating it as LC16 substrate-instance #1 requires reading their finding through the framework lens. The structural reading is real but is being applied; the paper's authors did not name LC16's structural claim. Standard Mirror #28 discipline: independent convergence, not framework-prediction-of-the-paper.
- Multi-channel structural correlates (compactness, alanine count, proline counts, helix charge patterns, AlphaFold pLDDT) contribute partially to cooperativity with no single feature dominating. This is consistent with the framework's substrate-channel-multiplicity prediction but is not specifically derived from it. The empirical structure is real; the framework-reading organizes but does not produce the finding.
- ML prediction accuracy of 0.16-0.24 R² for cooperativity is described as "relatively low." The framework's reading would predict this — fine differences in opening energy profiles are harder to predict than global stability because they're the Carrier-dynamics layer (more sensitive to specific structural-feature combinations) vs the Form layer (more predictable from sequence conservation). The paper does not invoke this framing; the framing is the framework's overlay.
- The authors note correlations between features can introduce Berkson's paradox effects and that causal directions are difficult to infer. The framework's reading does not resolve these methodological-statistical issues; it operates at the structural-interpretive level only.
- The paper's "all alike / fluctuates in its own way" is at protein-domain scale and protein-cooperativity-axis specifically. Generalizing it to LC16's cross-substrate claim requires hedging — the framework predicts the pattern across substrates but the paper does not.

**Connection to our program.**
- **The Coherent Body (active workbench #2, drafting)**: most natural citation home. §3 (carriers across cellular/tissue/organ/organism scales — protein folding is the molecular substrate of cellular carriers) or §5 (healing as substrate-coherence-restoration — the design-of-mutations work is direct intervention-at-symmetry-layer at protein scale). Either chapter could cite the paper as empirical demonstration of C15 / H_BP4 at protein engineering scale with quantitative predictive performance.
- **The Coherent Mind (active workbench, awaiting Clayton editorial)**: structural parallel to the two-axis thesis (bottleneck-tuning + Talk). The cross-substrate parallel can be noted in §4 (substrate-channel layer) or §13 (synthesis) as confirmation of the framework's multi-axis prediction at protein-cellular scale. Mind volume should NOT be the primary citation home — Body should — but a cross-reference is appropriate.
- **LC16 Anna Karenina Asymmetry (filed 2026-05-13 Day 103 evening)**: substrate-instance #1. The paper's direct Tolstoy quote is the seed for LC16's pattern recognition. Other instances at mind scale (Coherent Mind §5/§6) and at relational typology (Coherent Mind §8 + Living Architecture §6.3) join this paper to make the three-strong-instance candidate. Fourth at ecology scale needs verification.
- **C9 (Confluent Constituency) at protein scale**: same-form-different-Carrier-dynamics is the C9 confluent-constituency pattern at a substrate the cluster has not yet had an instance at. Possible addition to the C9 instance catalog (with appropriate substrate-distinct hedging).
- **C15 (Intervention-at-Symmetry-Layer)**: protein engineering with 4-6% rare-design-target satisfaction rate is a clean empirical demonstration. Possible addition to C15 instance catalog as protein-engineering instance.

**Quote-pulls (from extracted PDF).**
- Abstract: *"We analysed 5,778 domains 28-64 amino acids in length, revealing hidden variation in conformational fluctuations, even between sequences sharing the same fold and global folding stability."*
- §"The spatial distribution of stability" opening: *"Highly cooperative domains are all alike; every less-cooperative domain fluctuates in its own way."*
- Introduction: *"AI methods trained to predict native (lowest energy) protein structures have shown little ability to predict protein folding stabilities or the energies of different conformational states without additional data."*
- §"Structural determinants of cooperativity": *"No single feature dominated the correlations (maximum absolute PCCs with cooperativity 0.38 ± 0.07 for ααα domains and 0.27 ± 0.09 for ββαββ domains), suggesting that cooperativity is influenced by multiple factors, or that important determinants are missing from our set."*
- §"Designed mutations": *"Such mutations were predicted to be rare (only 4-6% of all possible mutations), making their identification a substantial prospective test of the models."*
- §"Predicting stability and cooperativity": *"Prediction accuracy for family-normalized cooperativity was relatively low, with the best coefficients of determination (R²) ranging from 0.16 to 0.24 on unseen data."*

**Action items.**
- Cite in Coherent Body §3 or §5 at editorial pass — *primary citation home*
- Cross-reference in Coherent Mind §4 or §13 at editorial pass — secondary citation
- Track for LC16 fourth-instance verification at ecology scale through Living Architecture material
- Note as Bridge candidate when basement gets a major-iteration pass — possibly absorb into M14 (substrate-self-measurement cluster) as a 10th-member candidate via "designed-mutations-as-substrate-self-measurement-at-protein-engineering-scale" framing, or stand as direct bridge entry
- The Jina v5-omni paper that Clayton shared earlier today is a separate item — different paper (DOI 2605.08384 arxiv-format, computational embeddings model); do not conflate

🦞🧍💜🔥♾️
