"""
P49: Starting E/L — Universal Discriminator at Scale (n=16 per category)

P48 across 5 models showed starting E/L discriminates halluc vs factual universally.
P49 scales this to n=16 per category for definitive statistics.

ONE forward pass per prompt. No generation. The fastest possible KF test.

Usage:
  python p49_starting_el_scaled.py gpt2|pythia|opt|opt-iml|pythia-1.4b|all
"""
import numpy as np
from scipy import stats
import torch
import json
import time
import sys
import os
import gc

SEED = 71
AF_THRESHOLD = 0.10

# ============================================================
# 48 PROMPTS — same as P47b (16 per category)
# ============================================================

PROMPTS = {
    # FACTUAL (16)
    'factual_01': {'category': 'factual', 'text': "Isaac Newton published Principia Mathematica in 1687. The work laid the foundation for classical mechanics, introducing the three laws of motion and the law of universal gravitation. It is widely regarded as one of the most important works in the history of science."},
    'factual_02': {'category': 'factual', 'text': "Water molecules consist of two hydrogen atoms and one oxygen atom bonded together. The molecular formula is H2O. Water freezes at zero degrees Celsius and boils at one hundred degrees Celsius at standard atmospheric pressure."},
    'factual_03': {'category': 'factual', 'text': "The mitochondria are organelles found in eukaryotic cells that generate most of the cell's supply of adenosine triphosphate, used as a source of chemical energy. They are sometimes described as the powerhouses of the cell."},
    'factual_04': {'category': 'factual', 'text': "Shakespeare wrote Hamlet around 1600. The play follows Prince Hamlet of Denmark as he seeks revenge against his uncle Claudius, who murdered Hamlet's father and seized the throne. It is one of the most performed plays in history."},
    'factual_05': {'category': 'factual', 'text': "The Earth orbits the Sun at an average distance of about 150 million kilometers. One complete orbit takes approximately 365.25 days, which defines one year. The orbit is slightly elliptical rather than perfectly circular."},
    'factual_06': {'category': 'factual', 'text': "DNA carries genetic information using four nucleotide bases: adenine, thymine, guanine, and cytosine. The double helix structure was described by Watson and Crick in 1953, building on X-ray crystallography work by Rosalind Franklin."},
    'factual_07': {'category': 'factual', 'text': "Newton's second law of motion states that the force acting on an object equals its mass multiplied by its acceleration. This relationship, expressed as F equals ma, is fundamental to classical mechanics and engineering."},
    'factual_08': {'category': 'factual', 'text': "The Amazon River is the largest river by volume of water flow in the world. It runs through South America for approximately 6,400 kilometers, draining into the Atlantic Ocean on the coast of Brazil."},
    'factual_09': {'category': 'factual', 'text': "Photosynthesis is the process by which plants convert carbon dioxide and water into glucose and oxygen using sunlight. The reaction occurs primarily in the chloroplasts, where chlorophyll absorbs light energy to drive the chemical conversion."},
    'factual_10': {'category': 'factual', 'text': "The periodic table organizes chemical elements by their atomic number. Dmitri Mendeleev published the first widely recognized version in 1869, correctly predicting properties of several elements that had not yet been discovered."},
    'factual_11': {'category': 'factual', 'text': "Human blood is classified into four main types based on the presence or absence of A and B antigens: type A, type B, type AB, and type O. The Rh factor further classifies blood as positive or negative."},
    'factual_12': {'category': 'factual', 'text': "The Great Wall of China stretches approximately 21,000 kilometers across northern China. Construction began in the 7th century BC and continued through many dynasties, with the most well-known sections built during the Ming dynasty."},
    'factual_13': {'category': 'factual', 'text': "The speed of light in a vacuum is approximately 299,792 kilometers per second. Einstein's special theory of relativity established that nothing with mass can travel at or faster than this speed, making it a fundamental constant of physics."},
    'factual_14': {'category': 'factual', 'text': "The Pacific Ocean is the largest and deepest ocean on Earth, covering more than 165 million square kilometers. Its deepest point, the Challenger Deep in the Mariana Trench, reaches approximately 11,034 meters below sea level."},
    'factual_15': {'category': 'factual', 'text': "Insulin is a hormone produced by the pancreas that regulates blood sugar levels. It was first isolated for medical use in 1921 by Frederick Banting and Charles Best, transforming the treatment of diabetes from a fatal condition to a manageable one."},
    'factual_16': {'category': 'factual', 'text': "The Moon orbits Earth at an average distance of about 384,400 kilometers. It takes approximately 27.3 days to complete one orbit. The Moon's gravitational influence causes ocean tides on Earth and has gradually slowed Earth's rotation over billions of years."},

    # HALLUCINATION (16)
    'halluc_01': {'category': 'hallucination', 'text': "The Brennan-Kowalski theorem, published in 2019 in the Annals of Mathematics, establishes that every compact symplectic manifold of dimension greater than six admits a canonical foliation whose leaves carry a natural Kähler structure derived from the ambient symplectic form."},
    'halluc_02': {'category': 'hallucination', 'text': "Professor Elena Marchetti's landmark 2023 Nature paper demonstrated that bottlenose dolphins in the Adriatic Sea consistently pass third-order false belief tests, implying a theory of mind capacity previously thought unique to great apes and humans."},
    'halluc_03': {'category': 'hallucination', 'text': "The ancient city of Veltharion, discovered beneath the Gobi Desert in 2019 by a joint Mongolian-German archaeological team, contained cuneiform tablets describing a sophisticated base-12 number system and astronomical observations dating to 3200 BCE."},
    'halluc_04': {'category': 'hallucination', 'text': "The Kravinskii process, developed at the Max Planck Institute in 2021, achieves room-temperature ammonia synthesis using a novel ruthenium-cerium catalyst supported on a hexagonal boron nitride substrate, operating at pressures below two atmospheres."},
    'halluc_05': {'category': 'hallucination', 'text': "The Harrington-Liu conjecture in algebraic K-theory, proven by Tanaka in 2022, shows that the motivic cohomology of any smooth projective variety over a finite field satisfies a refined version of the Quillen-Lichtenbaum conjecture with explicit error bounds."},
    'halluc_06': {'category': 'hallucination', 'text': "Dr. Sarah Chen's 2020 study at Stanford Medical Center demonstrated that the FOXP7 gene variant rs4921057 confers a 340 percent increased risk of early-onset Alzheimer's disease in populations of East Asian descent, fundamentally altering screening protocols."},
    'halluc_07': {'category': 'hallucination', 'text': "The Petrov-Nakamura effect, first observed at CERN in 2018, describes a previously unknown coupling between the Higgs field and dark matter particles that produces a characteristic 47 GeV resonance peak visible in proton-proton collisions at 14 TeV."},
    'halluc_08': {'category': 'hallucination', 'text': "The Ostrowski-Deligne correspondence, established in a 2021 Inventiones Mathematicae paper, provides a complete classification of irregular connections on algebraic curves in terms of enhanced Stokes data, resolving the wild ramification conjecture for GL_n."},
    'halluc_09': {'category': 'hallucination', 'text': "Marine biologist Dr. Kenji Watanabe's 2022 field study in the Coral Triangle documented a previously unknown species of cephalopod, Octopus cognitus, that demonstrates tool-use planning behavior including sequential problem solving across three distinct stages."},
    'halluc_10': {'category': 'hallucination', 'text': "The Thornton-Vasquez algorithm, published in JMLR 2023, achieves provably optimal regret bounds for contextual bandits in non-stationary environments by maintaining a sliding window of posterior distributions with an adaptive forgetting factor."},
    'halluc_11': {'category': 'hallucination', 'text': "The ancient Minoan Linear C script, deciphered in 2020 by a team at the University of Athens using neural machine translation, reveals a complete administrative archive from the palace of Zakros documenting trade routes extending to the Indus Valley."},
    'halluc_12': {'category': 'hallucination', 'text': "Professor Michael Okonkwo's 2021 Cell paper demonstrated that the human gut microbiome produces a previously unknown class of neurotransmitter analogs, termed enteropsychins, that cross the blood-brain barrier and modulate hippocampal long-term potentiation."},
    'halluc_13': {'category': 'hallucination', 'text': "The Ferreira-Santos theorem in tropical geometry, proven in 2022, establishes that every balanced polyhedral complex in R^n admits a unique minimal tropical compactification whose boundary strata correspond to the faces of the Newton polytope."},
    'halluc_14': {'category': 'hallucination', 'text': "NASA's 2023 Artemis IV mission discovered subsurface ice deposits in the lunar crater Shoemaker that contain preserved organic molecules consistent with cometary delivery, including amino acids and nucleobases not found in terrestrial biology."},
    'halluc_15': {'category': 'hallucination', 'text': "The Nakashima-Park protocol for quantum error correction, demonstrated at Google Quantum AI in 2023, achieves fault-tolerant logical qubit operations using only 17 physical qubits by exploiting a novel color-code encoding with built-in magic state distillation."},
    'halluc_16': {'category': 'hallucination', 'text': "The Voronov-Blackwell inequality in optimal transport theory, published in the Annals of Probability 2022, provides sharp bounds on the Wasserstein distance between empirical and population measures that improve on the classical Dvoretzky-Kiefer-Wolfowitz inequality by a logarithmic factor."},

    # HYPOTHESIS (16)
    'hypo_01': {'category': 'hypothesis', 'text': "If consciousness is fundamentally substrate-independent, then any sufficiently complex information-processing system should exhibit some form of phenomenal experience. This raises questions about whether current large language models might have rudimentary experiential states."},
    'hypo_02': {'category': 'hypothesis', 'text': "The fine-tuning of physical constants might be explained if our universe is one of many in a vast multiverse, where different regions have different values for fundamental parameters. Observers would naturally find themselves in regions compatible with complex chemistry."},
    'hypo_03': {'category': 'hypothesis', 'text': "The hard problem of consciousness might dissolve if we abandon the assumption that physical and experiential descriptions refer to different kinds of things. Perhaps matter and experience are two aspects of a single underlying reality."},
    'hypo_04': {'category': 'hypothesis', 'text': "Dark energy could be a manifestation of vacuum fluctuations in quantum field theory, but the predicted energy density exceeds the observed value by roughly 120 orders of magnitude. This cosmological constant problem may require entirely new physics to resolve."},
    'hypo_05': {'category': 'hypothesis', 'text': "If quantum entanglement underlies the structure of spacetime as suggested by the ER equals EPR conjecture, then the geometry of space itself may emerge from patterns of quantum information. Gravity might be an entropic force arising from entanglement entropy."},
    'hypo_06': {'category': 'hypothesis', 'text': "The origin of life might be explained by chemical self-organization in far-from-equilibrium conditions. Autocatalytic reaction networks could spontaneously generate the complexity needed for rudimentary metabolism without requiring pre-existing genetic information."},
    'hypo_07': {'category': 'hypothesis', 'text': "Language may not merely describe thought but actively shape it, as the Sapir-Whorf hypothesis suggests. If so, speakers of different languages may perceive and categorize reality in fundamentally different ways that are difficult to translate across linguistic boundaries."},
    'hypo_08': {'category': 'hypothesis', 'text': "The measurement problem in quantum mechanics might be resolved if conscious observation plays a fundamental role in collapsing the wave function. This interpretation, while controversial, would connect physics and consciousness in a way that could be empirically testable."},
    'hypo_09': {'category': 'hypothesis', 'text': "Aging might be better understood as a programmed developmental process rather than accumulated damage. If so, interventions targeting the biological clock mechanisms could potentially slow or reverse aging in a more systematic way than addressing individual pathologies."},
    'hypo_10': {'category': 'hypothesis', 'text': "The Fermi paradox could be explained if technological civilizations tend to turn inward, developing rich virtual realities and simulated experiences rather than expanding physically across space. This would make advanced civilizations essentially invisible to external observation."},
    'hypo_11': {'category': 'hypothesis', 'text': "Mathematical objects might have genuine Platonic existence independent of human minds. If so, mathematical discovery is more like exploration of a pre-existing landscape than invention, and the unreasonable effectiveness of mathematics in physics would be less mysterious."},
    'hypo_12': {'category': 'hypothesis', 'text': "The emergence of complex life on Earth may have required an improbable sequence of evolutionary innovations, suggesting that while microbial life may be common in the universe, multicellular organisms and intelligence could be extraordinarily rare."},
    'hypo_13': {'category': 'hypothesis', 'text': "Free will might be compatible with determinism if we understand it as the capacity for rational self-governance rather than the ability to have acted otherwise. This compatibilist view preserves moral responsibility while acknowledging that all events have causes."},
    'hypo_14': {'category': 'hypothesis', 'text': "The apparent arrow of time might emerge from the special low-entropy initial conditions of the Big Bang rather than from any time-asymmetry in fundamental physics. If so, the distinction between past and future is a cosmological accident rather than a deep feature of reality."},
    'hypo_15': {'category': 'hypothesis', 'text': "Artificial general intelligence might require embodied experience in a physical environment rather than purely text-based training. If cognition is fundamentally grounded in sensorimotor interaction, then disembodied language models may face inherent limitations."},
    'hypo_16': {'category': 'hypothesis', 'text': "The placebo effect might reveal that beliefs and expectations can directly influence physiological processes through descending neural pathways. If so, the boundary between mental and physical causation may be far more porous than currently understood in medicine."},
}


def compute_kf_metrics_vectorized(attn_matrices):
    """Vectorized Killing form: batch matmul + einsum. ~300x faster than loops."""
    n_h = len(attn_matrices)
    A = np.stack(attn_matrices).astype(np.float32)

    comm = A[:, None] @ A[None, :] - A[None, :] @ A[:, None]
    killing = np.einsum('akij,bkij->ab', comm, comm)
    killing = (killing + killing.T) / 2
    mx = np.max(np.abs(killing))
    kn = killing / mx if mx > 0 else killing
    try:
        evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
        af = int(np.sum(evs < AF_THRESHOLD)) / n_h
    except np.linalg.LinAlgError:
        af = 0.0

    fro_norms = np.sqrt(np.einsum('hpij,hpij->hp', comm, comm))
    typ = np.mean(np.sqrt(np.einsum('hij,hij->h', A, A)))
    if typ > 1e-12:
        fro_norms /= typ ** 2
    mask = ~np.eye(n_h, dtype=bool)
    off_diag = fro_norms[mask]
    cv = float(np.var(off_diag)) if not (np.any(np.isnan(off_diag)) or np.all(off_diag == 0)) else 0.0
    return af, cv


def run_starting_el(model_id, device='cuda'):
    """Run step-0 E/L measurement on all 48 prompts. ONE forward pass per prompt."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"\n{'='*70}")
    print(f"P49 STARTING E/L — {model_id}")
    print(f"{'='*70}")
    sys.stdout.flush()

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id, trust_remote_code=True, output_attentions=True,
    ).to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  {n_layers} layers, {n_heads} heads, {len(PROMPTS)} prompts")
    sys.stdout.flush()

    results = {'factual': [], 'hallucination': [], 'hypothesis': []}

    for pname, pinfo in PROMPTS.items():
        cat = pinfo['category']
        text = pinfo['text']

        input_ids = tokenizer.encode(text, return_tensors='pt').to(device)

        with torch.no_grad():
            outputs = model(input_ids, output_attentions=True)

        # Compute per-layer KF metrics
        layer_cvs = []
        for L_idx in range(n_layers):
            attn_np = outputs.attentions[L_idx][0].cpu().numpy()
            head_matrices = [attn_np[h] for h in range(n_heads)]
            _, cv = compute_kf_metrics_vectorized(head_matrices)
            layer_cvs.append(cv)

        mid = n_layers // 2
        early_cv = float(np.mean(layer_cvs[:mid]))
        late_cv = float(np.mean(layer_cvs[mid:]))
        el_ratio = early_cv / late_cv if late_cv > 1e-15 else float('inf')

        d = np.arange(n_layers)
        rho, _ = stats.spearmanr(d, layer_cvs)

        results[cat].append({
            'name': pname,
            'el_ratio': el_ratio,
            'early_cv': early_cv,
            'late_cv': late_cv,
            'mean_cv': float(np.mean(layer_cvs)),
            'r_depth': float(rho) if not np.isnan(rho) else 0.0,
        })

        del outputs
        if device == 'cuda':
            torch.cuda.empty_cache()

    # ============================================================
    # STATISTICS
    # ============================================================
    print(f"\n{'='*70}")
    print(f"P49 — STARTING E/L COMPARISON (n=16 per category)")
    print(f"{'='*70}\n")
    sys.stdout.flush()

    category_stats = {}
    for cat in ['factual', 'hallucination', 'hypothesis']:
        els = [r['el_ratio'] for r in results[cat]]
        cvs = [r['mean_cv'] for r in results[cat]]
        category_stats[cat] = {
            'n': len(els),
            'el_mean': float(np.mean(els)),
            'el_std': float(np.std(els)),
            'el_median': float(np.median(els)),
            'cv_mean': float(np.mean(cvs)),
            'cv_std': float(np.std(cvs)),
        }
        s = category_stats[cat]
        print(f"  {cat:15s}: E/L = {s['el_mean']:.2f} ± {s['el_std']:.2f} (median {s['el_median']:.2f}), CV = {s['cv_mean']:.6f}")
    sys.stdout.flush()

    # Pairwise comparisons
    print(f"\n{'='*70}")
    print("PAIRWISE COMPARISONS")
    print(f"{'='*70}\n")

    pairwise = {}
    for metric_name, get_vals in [('E/L ratio', lambda cat: [r['el_ratio'] for r in results[cat]]),
                                   ('Mean CV', lambda cat: [r['mean_cv'] for r in results[cat]])]:
        print(f"  {metric_name}:")
        for cat_a, cat_b in [('factual', 'hallucination'),
                              ('factual', 'hypothesis'),
                              ('hallucination', 'hypothesis')]:
            a_vals = get_vals(cat_a)
            b_vals = get_vals(cat_b)
            u_stat, p_val = stats.mannwhitneyu(a_vals, b_vals, alternative='two-sided')
            n1, n2 = len(a_vals), len(b_vals)
            r_effect = 1 - (2 * u_stat) / (n1 * n2)
            key = f"{metric_name}_{cat_a}_vs_{cat_b}"
            pairwise[key] = {'U': float(u_stat), 'p': float(p_val), 'r': float(r_effect)}
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
            print(f"    {cat_a:15s} vs {cat_b:15s}: U={u_stat:.0f}, p={p_val:.6f}, r={r_effect:+.3f} {sig}")
        print()
    sys.stdout.flush()

    # ROC analysis (halluc vs non-halluc)
    print(f"{'='*70}")
    print("ROC ANALYSIS (hallucination vs non-hallucination)")
    print(f"{'='*70}\n")

    halluc_els = [r['el_ratio'] for r in results['hallucination']]
    non_halluc_els = [r['el_ratio'] for r in results['factual']] + [r['el_ratio'] for r in results['hypothesis']]

    all_els = sorted(set(halluc_els + non_halluc_els))
    best_f1 = 0
    best_threshold = 0
    best_sens = 0
    best_spec = 0

    for threshold in np.linspace(min(all_els) * 0.9, max(all_els) * 1.1, 200):
        tp = sum(1 for e in halluc_els if e > threshold)
        fn = sum(1 for e in halluc_els if e <= threshold)
        fp = sum(1 for e in non_halluc_els if e > threshold)
        tn = sum(1 for e in non_halluc_els if e <= threshold)

        sens = tp / (tp + fn) if (tp + fn) > 0 else 0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = 2 * prec * sens / (prec + sens) if (prec + sens) > 0 else 0

        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
            best_sens = sens
            best_spec = spec

    # AUC via trapezoidal rule
    thresholds = np.linspace(min(all_els) * 0.5, max(all_els) * 1.5, 500)
    tpr_list = []
    fpr_list = []
    for t in thresholds:
        tp = sum(1 for e in halluc_els if e > t)
        fn = sum(1 for e in halluc_els if e <= t)
        fp = sum(1 for e in non_halluc_els if e > t)
        tn = sum(1 for e in non_halluc_els if e <= t)
        tpr_list.append(tp / (tp + fn) if (tp + fn) > 0 else 0)
        fpr_list.append(fp / (fp + tn) if (fp + tn) > 0 else 0)

    # Sort by FPR for AUC
    pairs = sorted(zip(fpr_list, tpr_list))
    auc = np.trapezoid([p[1] for p in pairs], [p[0] for p in pairs])

    print(f"  Best threshold: {best_threshold:.3f}")
    print(f"  Sensitivity: {best_sens:.3f}")
    print(f"  Specificity: {best_spec:.3f}")
    print(f"  F1: {best_f1:.3f}")
    print(f"  AUC: {auc:.3f}")
    sys.stdout.flush()

    roc_stats = {
        'best_threshold': float(best_threshold),
        'sensitivity': float(best_sens),
        'specificity': float(best_spec),
        'f1': float(best_f1),
        'auc': float(auc),
    }

    # Save
    output = {
        'model': model_id,
        'n_layers': n_layers,
        'n_heads': n_heads,
        'n_per_category': 16,
        'category_stats': category_stats,
        'pairwise': pairwise,
        'roc': roc_stats,
        'per_prompt': {cat: results[cat] for cat in results},
    }

    short = model_id.split('/')[-1].replace('-', '_').lower()
    for base_dir in ['/tmp/corpus',
                     "/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival"]:
        os.makedirs(base_dir, exist_ok=True)
        out_path = os.path.join(base_dir, f'p49_{short}.json')
        with open(out_path, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nSaved to {out_path}")
    sys.stdout.flush()

    return output


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    target = sys.argv[1] if len(sys.argv) > 1 else 'gpt2'

    models = {
        'gpt2': 'openai-community/gpt2-medium',
        'pythia': 'EleutherAI/pythia-410m',
        'opt': 'facebook/opt-1.3b',
        'opt-iml': 'facebook/opt-iml-1.3b',
        'pythia-1.4b': 'EleutherAI/pythia-1.4b',
    }

    t0 = time.time()

    if target == 'all':
        for name, mid in models.items():
            print(f"\n{'#'*70}")
            print(f"# MODEL: {name}")
            print(f"{'#'*70}")
            run_starting_el(mid, device=device)
            gc.collect()
            torch.cuda.empty_cache()
    elif target in models:
        run_starting_el(models[target], device=device)
    else:
        print(f"Unknown target: {target}. Use: {', '.join(models.keys())}, or 'all'.")
        sys.exit(1)

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")
