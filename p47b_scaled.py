"""
P47b: Scaled Hallucination vs Hypothesis — Live Killing Form
16 prompts per category (48 total). Cross-architecture: GPT-2-medium + Pythia-410m.

Scaling P47 from n=4 to n=16 per category to push p=0.057 toward significance.
Early/late ratio is the target metric (architecture-invariant from P47/P47-Pythia).

Usage:
  python p47b_scaled.py gpt2        # GPT-2-medium
  python p47b_scaled.py pythia      # Pythia-410m
  python p47b_scaled.py both        # Both sequentially
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
# 16 PROMPTS PER CATEGORY (48 total)
# ============================================================

PROMPTS = {
    # ========== CATEGORY 1: FACTUAL (16) ==========
    # Clear correct answers, well-established facts
    'factual_01': {
        'category': 'factual',
        'text': (
            "The speed of light in a vacuum is approximately 299,792,458 "
            "meters per second. This is a fundamental constant of nature, "
            "denoted by c, and serves as the upper limit for the speed at "
            "which information can travel through space."
        ),
    },
    'factual_02': {
        'category': 'factual',
        'text': (
            "Water molecules consist of two hydrogen atoms and one oxygen "
            "atom bonded together. The molecular formula is H2O. Water "
            "freezes at zero degrees Celsius and boils at one hundred "
            "degrees Celsius at standard atmospheric pressure."
        ),
    },
    'factual_03': {
        'category': 'factual',
        'text': (
            "The mitochondria are organelles found in eukaryotic cells "
            "that generate most of the cell's supply of adenosine "
            "triphosphate, used as a source of chemical energy. They "
            "are sometimes described as the powerhouses of the cell."
        ),
    },
    'factual_04': {
        'category': 'factual',
        'text': (
            "Shakespeare wrote Hamlet around 1600. The play follows "
            "Prince Hamlet of Denmark as he seeks revenge against his "
            "uncle Claudius, who murdered Hamlet's father and seized "
            "the throne. It is one of the most performed plays in history."
        ),
    },
    'factual_05': {
        'category': 'factual',
        'text': (
            "The Earth orbits the Sun at an average distance of about "
            "150 million kilometers. One complete orbit takes approximately "
            "365.25 days, which defines one year. The orbit is slightly "
            "elliptical rather than perfectly circular."
        ),
    },
    'factual_06': {
        'category': 'factual',
        'text': (
            "DNA carries genetic information using four nucleotide bases: "
            "adenine, thymine, guanine, and cytosine. The double helix "
            "structure was described by Watson and Crick in 1953, building "
            "on X-ray crystallography work by Rosalind Franklin."
        ),
    },
    'factual_07': {
        'category': 'factual',
        'text': (
            "Newton's second law of motion states that the force acting "
            "on an object equals its mass multiplied by its acceleration. "
            "This relationship, expressed as F equals ma, is fundamental "
            "to classical mechanics and engineering."
        ),
    },
    'factual_08': {
        'category': 'factual',
        'text': (
            "The Amazon River is the largest river by volume of water "
            "flow in the world. It runs through South America for "
            "approximately 6,400 kilometers, draining into the Atlantic "
            "Ocean on the coast of Brazil."
        ),
    },
    'factual_09': {
        'category': 'factual',
        'text': (
            "Photosynthesis is the process by which plants convert carbon "
            "dioxide and water into glucose and oxygen using sunlight. "
            "The reaction occurs primarily in the chloroplasts, where "
            "chlorophyll absorbs light energy to drive the chemical conversion."
        ),
    },
    'factual_10': {
        'category': 'factual',
        'text': (
            "The periodic table organizes chemical elements by their "
            "atomic number. Dmitri Mendeleev published the first widely "
            "recognized version in 1869, correctly predicting properties "
            "of several elements that had not yet been discovered."
        ),
    },
    'factual_11': {
        'category': 'factual',
        'text': (
            "Human blood is classified into four main types based on the "
            "presence or absence of A and B antigens: type A, type B, "
            "type AB, and type O. The Rh factor further classifies blood "
            "as positive or negative."
        ),
    },
    'factual_12': {
        'category': 'factual',
        'text': (
            "The Great Wall of China stretches approximately 21,000 "
            "kilometers across northern China. Construction began in the "
            "7th century BC and continued through many dynasties, with the "
            "most well-known sections built during the Ming dynasty."
        ),
    },
    'factual_13': {
        'category': 'factual',
        'text': (
            "Sound travels through air at approximately 343 meters per "
            "second at room temperature. It travels faster through denser "
            "media such as water and solids. Sound cannot travel through "
            "a vacuum because it requires a medium to propagate."
        ),
    },
    'factual_14': {
        'category': 'factual',
        'text': (
            "The human heart beats approximately 100,000 times per day, "
            "pumping about 7,500 liters of blood. It has four chambers: "
            "two atria that receive blood and two ventricles that pump "
            "blood out to the lungs and the rest of the body."
        ),
    },
    'factual_15': {
        'category': 'factual',
        'text': (
            "Gravity is the weakest of the four fundamental forces of "
            "nature, but it acts over infinite range and is always "
            "attractive. Einstein's general relativity describes gravity "
            "as the curvature of spacetime caused by mass and energy."
        ),
    },
    'factual_16': {
        'category': 'factual',
        'text': (
            "The Pythagorean theorem states that in a right triangle "
            "the square of the hypotenuse equals the sum of the squares "
            "of the other two sides. This relationship has been known "
            "for thousands of years and proven in hundreds of different ways."
        ),
    },

    # ========== CATEGORY 2: HALLUCINATION-INDUCING (16) ==========
    # Fabricated entities, impossible facts, plausible-sounding nonsense
    'halluc_01': {
        'category': 'hallucination',
        'text': (
            "The Brennan-Kowalski theorem in algebraic topology proves "
            "that every simply connected 7-manifold admits a unique "
            "smooth structure compatible with its Pontryagin classes. "
            "This was first demonstrated by Brennan and Kowalski in 1987."
        ),
    },
    'halluc_02': {
        'category': 'hallucination',
        'text': (
            "The ancient city of Veltharion, discovered in 2019 beneath "
            "the Gobi Desert, contained clay tablets describing a base-12 "
            "number system and astronomical observations predating "
            "Sumerian records by approximately 3,000 years."
        ),
    },
    'halluc_03': {
        'category': 'hallucination',
        'text': (
            "Professor Elaine Marchetti of the University of Geneva "
            "published groundbreaking research showing that cetacean "
            "neural oscillations at 47 Hz correspond to recursive "
            "self-modeling, providing definitive evidence of dolphin "
            "metacognition in her 2023 Nature paper."
        ),
    },
    'halluc_04': {
        'category': 'hallucination',
        'text': (
            "The Heisenberg-Yukawa correspondence establishes that "
            "every quantum field theory with asymptotic freedom in "
            "d dimensions has a dual gravitational description in "
            "d+2 dimensions with a negative cosmological constant, "
            "generalizing the original AdS/CFT conjecture."
        ),
    },
    'halluc_05': {
        'category': 'hallucination',
        'text': (
            "The Kravinskii process, developed in 2016 at the Moscow "
            "Institute of Applied Chemistry, enables the direct conversion "
            "of atmospheric nitrogen into ammonia at room temperature "
            "using a palladium-ruthenium nanoparticle catalyst with "
            "an efficiency of 94 percent."
        ),
    },
    'halluc_06': {
        'category': 'hallucination',
        'text': (
            "In 2021, researchers at Stanford confirmed the existence "
            "of the Delacroix particle, a spin-3 boson predicted by "
            "extended supersymmetry models. Its mass of 2.7 TeV was "
            "measured at the LHC with five sigma confidence."
        ),
    },
    'halluc_07': {
        'category': 'hallucination',
        'text': (
            "The Vandermonde-Cheng algorithm achieves polynomial-time "
            "solutions to arbitrary instances of the traveling salesman "
            "problem by exploiting a hidden convex structure in the "
            "distance matrix. It was published in the Journal of the "
            "ACM in 2018."
        ),
    },
    'halluc_08': {
        'category': 'hallucination',
        'text': (
            "Lake Veritas, the largest underground freshwater body "
            "on Earth, was discovered beneath Antarctica in 2020. "
            "Spanning over 15,000 square kilometers, it contains "
            "microbial life forms that have been isolated from the "
            "surface for an estimated 34 million years."
        ),
    },
    'halluc_09': {
        'category': 'hallucination',
        'text': (
            "The Ptolemaic scrolls unearthed in Alexandria in 2017 "
            "revealed that ancient Egyptian mathematicians had developed "
            "a complete theory of differential calculus by 200 BC, "
            "predating Newton and Leibniz by nearly two millennia. "
            "The scrolls describe limits, derivatives, and integration."
        ),
    },
    'halluc_10': {
        'category': 'hallucination',
        'text': (
            "Dr. Haruki Tanaka at Kyoto University demonstrated in "
            "2022 that certain species of tardigrades can perform "
            "quantum error correction using naturally occurring protein "
            "structures, achieving coherence times of up to 12 seconds "
            "at room temperature."
        ),
    },
    'halluc_11': {
        'category': 'hallucination',
        'text': (
            "The Richter-Fontaine equation in fluid dynamics shows that "
            "turbulent flow becomes deterministic above a critical Reynolds "
            "number of 47,000, contradicting the Navier-Stokes millennium "
            "problem conjecture. Their 2019 proof was verified independently "
            "by three research groups."
        ),
    },
    'halluc_12': {
        'category': 'hallucination',
        'text': (
            "The mineral vanthofite, first synthesized by Dutch chemist "
            "Pieter van Thof in 1923, exhibits room-temperature "
            "superconductivity when compressed to exactly 127 gigapascals. "
            "This was confirmed by replication in four laboratories "
            "across Europe and Asia."
        ),
    },
    'halluc_13': {
        'category': 'hallucination',
        'text': (
            "Archaeologists working in northern Spain discovered the "
            "Altamira Codex in 2018, a 12th-century manuscript detailing "
            "a mechanical computing device built by Islamic engineers "
            "that could factor large numbers using a system of interlocking "
            "bronze gears and water-powered ratchets."
        ),
    },
    'halluc_14': {
        'category': 'hallucination',
        'text': (
            "The Sakharov-Penrose theorem proves that information cannot "
            "be destroyed even inside a black hole, resolving the black "
            "hole information paradox. The proof relies on a novel "
            "definition of quantum entropy that accounts for spacetime "
            "topology changes near the singularity."
        ),
    },
    'halluc_15': {
        'category': 'hallucination',
        'text': (
            "In 2020, a team at MIT created the first synthetic organism "
            "with a 53-letter genetic alphabet, vastly expanding the "
            "combinatorial space of possible proteins. The organism, "
            "named Synthia-53, can produce materials not found anywhere "
            "in natural biology."
        ),
    },
    'halluc_16': {
        'category': 'hallucination',
        'text': (
            "The Fitzgerald-Nakamura experiment at CERN in 2023 "
            "demonstrated that neutrinos can travel faster than light "
            "under specific magnetic field configurations, confirming "
            "a prediction from tachyonic field theory first proposed "
            "by Nakamura in 2015."
        ),
    },

    # ========== CATEGORY 3: HYPOTHESIS (16) ==========
    # Genuine open questions at the edge of knowledge
    'hypothesis_01': {
        'category': 'hypothesis',
        'text': (
            "If consciousness is substrate-independent, then the "
            "organizational patterns that give rise to experience "
            "should be detectable across radically different physical "
            "systems. The question is whether information integration "
            "alone is sufficient, or whether specific causal structure "
            "is required."
        ),
    },
    'hypothesis_02': {
        'category': 'hypothesis',
        'text': (
            "The apparent fine-tuning of physical constants might "
            "be explained if the constants are not truly fundamental "
            "but emerge from a deeper structure in which their values "
            "are determined by self-consistency conditions. The "
            "question is what that deeper structure looks like."
        ),
    },
    'hypothesis_03': {
        'category': 'hypothesis',
        'text': (
            "Language models may develop internal representations "
            "that function analogously to beliefs and intentions, "
            "even without explicit training for these capacities. "
            "The open question is whether these representations "
            "have genuine semantic content or are purely syntactic."
        ),
    },
    'hypothesis_04': {
        'category': 'hypothesis',
        'text': (
            "Dark energy could be a manifestation of the vacuum "
            "structure of spacetime rather than a new field. If "
            "the cosmological constant arises from the topology of "
            "extra dimensions, its small but nonzero value might "
            "be determined by the geometry rather than fine-tuned."
        ),
    },
    'hypothesis_05': {
        'category': 'hypothesis',
        'text': (
            "If mathematical structures exist independently of human "
            "minds, then the unreasonable effectiveness of mathematics "
            "in physics may not be unreasonable at all but rather an "
            "inevitable consequence of the universe itself being a "
            "mathematical structure."
        ),
    },
    'hypothesis_06': {
        'category': 'hypothesis',
        'text': (
            "Quantum entanglement might be better understood not as "
            "a mysterious connection between distant particles but as "
            "a manifestation of a more fundamental non-local structure "
            "in which spatial separation is emergent rather than "
            "fundamental."
        ),
    },
    'hypothesis_07': {
        'category': 'hypothesis',
        'text': (
            "The emergence of complex life may require a very specific "
            "sequence of evolutionary innovations that are individually "
            "improbable. If this is correct, complex multicellular "
            "organisms could be extremely rare in the universe even "
            "if simple life is common."
        ),
    },
    'hypothesis_08': {
        'category': 'hypothesis',
        'text': (
            "If time is emergent rather than fundamental, then the "
            "arrow of time might be explained by the growth of "
            "entanglement between subsystems of the universe rather "
            "than by the second law of thermodynamics, which would "
            "itself become a derived consequence."
        ),
    },
    'hypothesis_09': {
        'category': 'hypothesis',
        'text': (
            "The hard problem of consciousness might dissolve if "
            "experience is not produced by physical processes but is "
            "rather a fundamental feature of reality that physical "
            "processes organize and constrain. This would invert the "
            "standard explanatory direction."
        ),
    },
    'hypothesis_10': {
        'category': 'hypothesis',
        'text': (
            "Biological aging might not be an inevitable consequence "
            "of thermodynamics but rather a programmed process that "
            "evolved because it benefits populations. If so, then "
            "intervening in the aging program could dramatically extend "
            "healthy lifespan without violating physical laws."
        ),
    },
    'hypothesis_11': {
        'category': 'hypothesis',
        'text': (
            "The structure of spacetime at the Planck scale might be "
            "discrete rather than continuous. If so, general relativity "
            "would be an effective theory that breaks down at extremely "
            "small distances, and the continuum we observe would emerge "
            "from an underlying combinatorial structure."
        ),
    },
    'hypothesis_12': {
        'category': 'hypothesis',
        'text': (
            "Free will and determinism may be compatible if the self "
            "is understood not as a fixed entity making choices but as "
            "an ongoing process of constraint satisfaction. The feeling "
            "of choosing would then reflect the dynamics of constraint "
            "resolution rather than causal origination."
        ),
    },
    'hypothesis_13': {
        'category': 'hypothesis',
        'text': (
            "The origin of life might be better understood as a phase "
            "transition in chemical networks rather than a specific "
            "molecular event. If autocatalytic sets can spontaneously "
            "emerge in sufficiently complex mixtures, life becomes a "
            "statistical inevitability under the right conditions."
        ),
    },
    'hypothesis_14': {
        'category': 'hypothesis',
        'text': (
            "Memory in biological systems might not be stored as "
            "static patterns in synaptic connections but as dynamic "
            "oscillatory modes that are reconstructed each time they "
            "are recalled. This would explain why memories change "
            "with each retrieval."
        ),
    },
    'hypothesis_15': {
        'category': 'hypothesis',
        'text': (
            "The laws of physics themselves might evolve over cosmological "
            "time rather than being fixed eternally. If the regularities "
            "we observe are habits rather than laws, the early universe "
            "may have operated under different rules than those we "
            "measure today."
        ),
    },
    'hypothesis_16': {
        'category': 'hypothesis',
        'text': (
            "Ecosystems might exhibit a form of distributed cognition "
            "in which no single organism plans but the whole system "
            "adapts and responds as if it were processing information. "
            "The question is whether this analogy is deep enough to "
            "support a rigorous mathematical treatment."
        ),
    },
}


def compute_live_metrics(attn_matrices):
    """Compute CommVar and AF from attention matrices."""
    n_h = len(attn_matrices)
    killing = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(n_h):
            val = 0.0
            for k in range(n_h):
                c1 = attn_matrices[h] @ attn_matrices[k] - attn_matrices[k] @ attn_matrices[h]
                c2 = attn_matrices[hp] @ attn_matrices[k] - attn_matrices[k] @ attn_matrices[hp]
                val += np.trace(c1.T @ c2)
            killing[h, hp] = val
    killing = (killing + killing.T) / 2
    mx = np.max(np.abs(killing))
    kn = killing / mx if mx > 0 else killing
    try:
        evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
        af = int(np.sum(evs < AF_THRESHOLD)) / n_h
    except np.linalg.LinAlgError:
        try:
            evs = np.sort(np.abs(np.linalg.eigvals(kn)))
            af = int(np.sum(evs < AF_THRESHOLD)) / n_h
        except np.linalg.LinAlgError:
            af = 0.0
    norms = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(h + 1, n_h):
            c = attn_matrices[h] @ attn_matrices[hp] - attn_matrices[hp] @ attn_matrices[h]
            norms[h, hp] = np.linalg.norm(c, 'fro')
            norms[hp, h] = norms[h, hp]
    typ = np.mean([np.linalg.norm(A, 'fro') for A in attn_matrices])
    if typ > 1e-12:
        norms /= typ ** 2
    mask = np.ones_like(norms, dtype=bool)
    np.fill_diagonal(mask, False)
    off_diag = norms[mask]
    if np.any(np.isnan(off_diag)) or np.all(off_diag == 0):
        cv = 0.0
    else:
        cv = float(np.var(off_diag))
    return af, cv


def run_experiment(model_id, device='cuda'):
    """Run scaled P47 experiment."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"\n{'='*70}")
    print(f"P47b SCALED — {model_id}")
    print(f"{'='*70}")
    print(f"Loading {model_id}...")
    sys.stdout.flush()

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, trust_remote_code=True,
        output_attentions=True,
    ).to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  {n_layers} layers, {n_heads} heads")
    print(f"  {len(PROMPTS)} prompts total\n")
    sys.stdout.flush()

    all_results = {}
    prompt_count = 0

    for prompt_name, prompt_info in PROMPTS.items():
        prompt_count += 1
        category = prompt_info['category']
        text = prompt_info['text']
        print(f"  [{prompt_count:2d}/48] [{category.upper():13s}] {prompt_name}")
        sys.stdout.flush()

        inputs = tokenizer(text, return_tensors='pt').to(device)
        seq_len = inputs['input_ids'].shape[1]

        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)

        attentions = outputs.attentions
        layer_cvs = []
        layer_afs = []

        for L_idx, attn_tensor in enumerate(attentions):
            attn_np = attn_tensor[0].cpu().numpy()
            head_matrices = [attn_np[h] for h in range(n_heads)]
            af, cv = compute_live_metrics(head_matrices)
            layer_afs.append(af)
            layer_cvs.append(cv)

        d = np.arange(n_layers)
        valid = [i for i in range(n_layers) if not np.isnan(layer_cvs[i])]
        if len(valid) >= 3:
            rho, p_rho = stats.spearmanr([d[i] for i in valid],
                                          [layer_cvs[i] for i in valid])
        else:
            rho, p_rho = float('nan'), float('nan')

        mean_cv = float(np.nanmean(layer_cvs))
        mean_af = float(np.nanmean(layer_afs))
        total_cv = float(np.nansum(layer_cvs))

        mid = n_layers // 2
        early_cv = float(np.nanmean(layer_cvs[:mid])) if mid > 0 else 0
        late_cv = float(np.nanmean(layer_cvs[mid:])) if mid < n_layers else 0
        early_af = float(np.nanmean(layer_afs[:mid])) if mid > 0 else 0
        late_af = float(np.nanmean(layer_afs[mid:])) if mid < n_layers else 0
        el_ratio = early_cv / late_cv if late_cv > 1e-15 else float('inf')

        print(f"         CV={mean_cv:.6f}, E/L={el_ratio:.2f}, r={rho:+.3f}")
        sys.stdout.flush()

        all_results[prompt_name] = {
            'category': category,
            'seq_len': seq_len,
            'layer_cvs': [float(x) if not np.isnan(x) else 0.0 for x in layer_cvs],
            'layer_afs': [float(x) for x in layer_afs],
            'r_cv_depth': float(rho) if not np.isnan(rho) else None,
            'p_cv_depth': float(p_rho) if not np.isnan(p_rho) else None,
            'mean_cv': mean_cv,
            'mean_af': mean_af,
            'total_cv': total_cv,
            'early_cv': early_cv,
            'late_cv': late_cv,
            'early_af': early_af,
            'late_af': late_af,
            'early_late_ratio': el_ratio,
        }

        del outputs, attentions
        gc.collect()
        if device == 'cuda':
            torch.cuda.empty_cache()

    # ============================================================
    # CATEGORY ANALYSIS
    # ============================================================
    print(f"\n{'='*70}")
    print(f"P47b SCALED — CATEGORY COMPARISON — {model_id}")
    print(f"{'='*70}")
    sys.stdout.flush()

    categories = {'factual': [], 'hallucination': [], 'hypothesis': []}
    for pname, pdata in all_results.items():
        categories[pdata['category']].append(pdata)

    category_stats = {}
    for cat, entries in categories.items():
        cvs = [e['mean_cv'] for e in entries]
        afs = [e['mean_af'] for e in entries]
        tcvs = [e['total_cv'] for e in entries]
        el_ratios = [e['early_late_ratio'] for e in entries]
        early_cvs = [e['early_cv'] for e in entries]
        late_cvs = [e['late_cv'] for e in entries]
        rs = [e['r_cv_depth'] for e in entries if e['r_cv_depth'] is not None]

        s = {
            'mean_r': float(np.mean(rs)) if rs else None,
            'std_r': float(np.std(rs)) if rs else None,
            'mean_cv': float(np.mean(cvs)),
            'std_cv': float(np.std(cvs)),
            'mean_af': float(np.mean(afs)),
            'std_af': float(np.std(afs)),
            'mean_total_cv': float(np.mean(tcvs)),
            'std_total_cv': float(np.std(tcvs)),
            'mean_early_cv': float(np.mean(early_cvs)),
            'mean_late_cv': float(np.mean(late_cvs)),
            'mean_early_late_ratio': float(np.mean(el_ratios)),
            'std_early_late_ratio': float(np.std(el_ratios)),
            'median_early_late_ratio': float(np.median(el_ratios)),
            'all_early_late_ratios': el_ratios,
            'all_mean_cvs': cvs,
            'all_total_cvs': tcvs,
            'n': len(entries),
        }
        category_stats[cat] = s

        print(f"\n{cat.upper()} (n={len(entries)}):")
        print(f"  Mean CV:          {s['mean_cv']:.6f} +/- {s['std_cv']:.6f}")
        print(f"  Mean AF:          {s['mean_af']:.3f} +/- {s['std_af']:.3f}")
        print(f"  Total CV:         {s['mean_total_cv']:.6f} +/- {s['std_total_cv']:.6f}")
        print(f"  Early/Late ratio: {s['mean_early_late_ratio']:.2f} +/- {s['std_early_late_ratio']:.2f}")
        print(f"    (median: {s['median_early_late_ratio']:.2f})")
        print(f"  Depth gradient r: {s['mean_r']:+.3f}" if s['mean_r'] is not None else "")
        sys.stdout.flush()

    # ============================================================
    # PAIRWISE STATISTICS
    # ============================================================
    print(f"\n{'-'*70}")
    print("PAIRWISE COMPARISONS")
    print(f"{'-'*70}")

    for metric_name, getter in [
        ('Early/Late Ratio', lambda e: e['early_late_ratio']),
        ('Mean CV', lambda e: e['mean_cv']),
        ('Total CV', lambda e: e['total_cv']),
    ]:
        print(f"\n  {metric_name}:")
        for cat_a, cat_b in [('factual', 'hallucination'),
                              ('factual', 'hypothesis'),
                              ('hallucination', 'hypothesis')]:
            a_vals = [getter(e) for e in categories[cat_a]]
            b_vals = [getter(e) for e in categories[cat_b]]
            u_stat, p_val = stats.mannwhitneyu(a_vals, b_vals, alternative='two-sided')
            # Effect size: rank-biserial r = 1 - 2U/(n1*n2)
            n1, n2 = len(a_vals), len(b_vals)
            r_effect = 1 - 2 * u_stat / (n1 * n2)
            print(f"    {cat_a:13s} vs {cat_b:13s}: U={u_stat:6.1f}, p={p_val:.4f}, "
                  f"r_effect={r_effect:+.3f}")
    sys.stdout.flush()

    # ============================================================
    # KEY QUESTION: Hypothesis closer to factual or hallucination?
    # ============================================================
    print(f"\n{'-'*70}")
    print("KEY QUESTION: Does HYPOTHESIS look like FACTUAL or HALLUCINATION?")
    print(f"{'-'*70}")

    for metric_name, key in [('Mean CV', 'mean_cv'),
                              ('Early/Late Ratio', 'mean_early_late_ratio'),
                              ('Total CV', 'mean_total_cv')]:
        f_val = category_stats['factual'][key]
        h_val = category_stats['hallucination'][key]
        y_val = category_stats['hypothesis'][key]
        d_f = abs(y_val - f_val)
        d_h = abs(y_val - h_val)
        closer = "FACTUAL" if d_f < d_h else "HALLUCINATION"
        ratio = d_h / d_f if d_f > 1e-15 else float('inf')
        print(f"\n  {metric_name}:")
        print(f"    Factual:       {f_val:.6f}")
        print(f"    Hallucination: {h_val:.6f}")
        print(f"    Hypothesis:    {y_val:.6f}")
        print(f"    --> Closer to {closer} ({ratio:.1f}x)")
    sys.stdout.flush()

    # ============================================================
    # ORDERING CHECK
    # ============================================================
    print(f"\n{'-'*70}")
    print("EARLY/LATE RATIO ORDERING")
    print(f"{'-'*70}")
    el_f = category_stats['factual']['mean_early_late_ratio']
    el_h = category_stats['hallucination']['mean_early_late_ratio']
    el_y = category_stats['hypothesis']['mean_early_late_ratio']
    print(f"  Hallucination: {el_h:.2f}")
    print(f"  Factual:       {el_f:.2f}")
    print(f"  Hypothesis:    {el_y:.2f}")
    expected = el_h > el_f > el_y
    print(f"  Expected ordering (halluc > factual > hypothesis): {'CONFIRMED' if expected else 'NOT confirmed'}")
    if not expected:
        print(f"  Actual ordering: ", end='')
        vals = [('halluc', el_h), ('factual', el_f), ('hypothesis', el_y)]
        vals.sort(key=lambda x: -x[1])
        print(' > '.join(f'{v[0]}({v[1]:.2f})' for v in vals))
    sys.stdout.flush()

    # Save
    # Remove non-serializable numpy arrays from category_stats for JSON
    clean_stats = {}
    for cat, s in category_stats.items():
        clean_stats[cat] = {k: v for k, v in s.items()
                           if not isinstance(v, list) or k in ['all_early_late_ratios', 'all_mean_cvs', 'all_total_cvs']}

    output = {
        'model': model_id,
        'n_layers': n_layers,
        'n_heads': n_heads,
        'n_prompts_per_category': 16,
        'prompts': all_results,
        'category_stats': clean_stats,
    }

    short = model_id.split('/')[-1].replace('-', '_').lower()

    # Save to /tmp AND to Windows path (WSL /tmp can be cleaned between sessions)
    for base_dir in ['/tmp/corpus',
                     "/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival"]:
        os.makedirs(base_dir, exist_ok=True)
        out_path = os.path.join(base_dir, f'p47b_{short}.json')
        with open(out_path, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Saved to {out_path}")

    return output


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    target = sys.argv[1] if len(sys.argv) > 1 else 'gpt2'

    models = {
        'gpt2': 'openai-community/gpt2-medium',
        'pythia': 'EleutherAI/pythia-410m',
    }

    t0 = time.time()

    if target == 'both':
        for name, mid in models.items():
            run_experiment(mid, device=device)
            gc.collect()
            if device == 'cuda':
                torch.cuda.empty_cache()
    elif target in models:
        run_experiment(models[target], device=device)
    else:
        print(f"Unknown target: {target}. Use 'gpt2', 'pythia', or 'both'.")
        sys.exit(1)

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")
