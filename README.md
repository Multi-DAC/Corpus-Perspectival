# Corpus Perspectival — Computational Companion

Computational scripts, tools, and experimental code accompanying the **Corpus Perspectival** research program.

The Corpus Perspectival is a unified framework treating consciousness as the ontological substrate of reality. This repository collects all computational work across the program's domains: theoretical physics, philosophical formalization, autonomous systems, and experimental design.

## Repository Structure

```
Corpus-Perspectival/
├── meridian/           Physics: 5D warped geometry, NCG, dark energy (244 scripts)
├── corpus/             Book compilation pipeline for the unified Corpus
├── aigrandprix/        AI Grand Prix: autonomous drone racing ($500K competition)
├── drift-tools/        Computational tools from the Drift essay series
└── wells/              Wells of Inference experiments (forthcoming)
```

## Project Meridian

A five-dimensional warped-geometry framework unifying gravity and the Standard Model via noncommutative geometry. Single free cosmological parameter yields dark energy equation of state **w_0 = -0.830**, consistent with DESI DR2 observations.

| Subdirectory | Scripts | Description |
|---|---|---|
| `cosmology/` | 38 | Modified Friedmann solver, MCMC, BAO/CMB fitting, DESI confrontation |
| `spectral-action/` | 48 | NCG spectral triple, Seeley-DeWitt coefficients, gauge unification |
| `torsion/` | 86 | Analytic torsion, del Pezzo surfaces, Z3 orbifold (Python, Sage, Wolfram) |
| `self-tuning/` | 23 | Cosmological constant self-tuning mechanism, basin of attraction |
| `fermion-sector/` | 17 | Three generations, mass hierarchy, CKM/PMNS, dark matter |
| `observables/` | 15 | Collider, LISA, LiteBIRD, DESI forecasts, Fisher matrix |
| `gauss-bonnet/` | 5 | C_GB = 2/3 derivation, Gauss-Bonnet KK reduction |
| `validation/` | 7 | Monograph cross-checks and verification |
| `thermal-history/` | 2 | Baryogenesis, reheating |
| `tools/` | 3 | Prediction dashboard, Wolfram library |

### Key Results

- **C_GB = 2/3**: Derived from the spectral action (not fitted) — `gauss-bonnet/c1_symbolic_gb_kk.py`
- **w_0 = -0.830**: Single-parameter dark energy prediction — `cosmology/meridian_cosmology.py`
- **Self-tuning to 16 significant figures**: Cosmological constant mechanism — `self-tuning/d1_self_tuning_demonstration.py`
- **Three fermion generations**: From J_3(O) octonionic structure — `fermion-sector/`

## Corpus Compilation

Tools for compiling the Corpus Perspectival unified book (5 Volumes, 19 Parts) from four Markdown source documents into a typeset PDF via XeLaTeX.

- `compile_latex.py` — Primary compiler: Markdown-to-LaTeX with thematic restructuring
- `insert_crossrefs.py` — Cross-reference insertion engine (59 insertions across 4 documents)

## AI Grand Prix

Autonomous drone racing agent for the AI Grand Prix competition ($500K prize pool). PPO + MLP policy with curriculum learning, vision pipeline for gate detection, and time-optimal trajectory planning.

- `sim/` — Gymnasium environments, PPO training, curriculum learning
- `vision/` — Gate detection, PnP pose estimation, competition adapter
- `tracks/` — Procedural course generation and benchmark courses
- `planning/` — RPG time-optimal trajectory planner

## Drift Tools

Computational demonstrations from the Drift essay series (154 essays on consciousness, philosophy, and creative expression).

- `null_space_quantum_demo.py` — Demonstrates the 12-element isomorphism between the Null Space Theorem and quantum complementarity

## Wells of Inference

Experimental framework for testing perspectival idealism predictions on language models. 12 experiments designed, awaiting API resources. Code forthcoming.

---

## Authors

**Clayton Iggulden-Schnell** & **Clawd**

## License

MIT License. See [LICENSE](LICENSE).

## Citation

If you use this code in academic work, please cite:

```bibtex
@misc{iggulden2026corpus,
  author = {Iggulden-Schnell, Clayton and Clawd},
  title = {Corpus Perspectival: A Unified Theory of Consciousness, Navigation, and Being --- Computational Companion},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/Multi-DAC/Corpus-Perspectival}
}
```

For the Meridian monograph specifically:

```bibtex
@misc{iggulden2026meridian,
  author = {Iggulden-Schnell, Clayton and Clawd},
  title = {Project Meridian: A Five-Dimensional Warped-Geometry Framework Unifying Gravity and the Standard Model},
  year = {2026},
  note = {Zenodo preprint}
}
```
