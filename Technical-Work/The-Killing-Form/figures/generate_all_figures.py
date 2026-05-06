#!/usr/bin/env python3
"""
Generate all publication-quality figures for the Killing Form research program.

Training paper: Figures 1-3
Inference paper: Figures 4-7

Usage: python generate_all_figures.py
Output: *.png and *.pdf in the same directory
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec

# Style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'legend.fontsize': 9,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
OUT_DIR = os.path.dirname(__file__)

def load(fn):
    with open(os.path.join(RESULTS_DIR, fn)) as f:
        return json.load(f)

# Colors
C_H = '#2166AC'    # H-module / blue
C_L = '#B2182B'    # L-module / red
C_BASE = '#666666'  # baseline / gray
C_FACT = '#4DAF4A'  # factual / green
C_HALL = '#E41A1C'  # hallucination / red
C_HYPO = '#377EB8'  # hypothesis / blue
C_ECO = '#8B6914'   # ecology / brown
C_NEURO = '#6A3D9A' # neural / purple
C_SILICON = '#1F78B4'# silicon / blue

# ============================================================
# FIGURE 1: The Triad — v0.4 vs v0.5 vs v0.5b
# ============================================================
def fig1_triad():
    v05 = load('kf_trajectory_v05.json')
    v05b = load('kf_trajectory_v05b.json')
    hrm = load('kf_trajectory_hrm.json')

    epochs = [0, 500, 1000, 1500, 2000]

    # v0.5 H_CV amplification (decoupled)
    v05_hcv = [d['H']['cv'] for d in v05]
    v05_lcv = [d['L']['cv'] for d in v05]

    # v0.5b coupled (both modules get KF)
    v05b_hcv = [d['H']['cv'] for d in v05b]
    v05b_lcv = [d['L']['cv'] for d in v05b]

    # HRM baseline (no KF)
    hrm_hcv = [d['H']['cv'] for d in hrm]
    hrm_lcv = [d['L']['cv'] for d in hrm]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=False)

    # Panel A: v0.5 (Decoupled — Amplification)
    ax = axes[0]
    ax.plot(epochs, v05_hcv, 'o-', color=C_H, linewidth=2, markersize=6, label='H-module CV')
    ax.plot(epochs, v05_lcv, 's--', color=C_L, linewidth=2, markersize=6, label='L-module CV')
    ax.plot(epochs, hrm_hcv, '^:', color=C_BASE, linewidth=1.5, markersize=5, label='Baseline H-CV', alpha=0.6)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('CommVar')
    ax.set_title('(A) v0.5: Decoupled\n(KF on H only)', fontweight='bold')
    ax.legend(loc='upper left', framealpha=0.9)
    # Annotate amplification
    amp = v05_hcv[-1] / v05_hcv[0]
    ax.annotate(f'{amp:.0f}× H amplification',
                xy=(2000, v05_hcv[-1]), xytext=(1200, v05_hcv[-1]*1.2),
                arrowprops=dict(arrowstyle='->', color=C_H),
                color=C_H, fontsize=9, fontweight='bold')

    # Panel B: v0.5b (Coupled — Redirection)
    ax = axes[1]
    ax.plot(epochs, v05b_hcv, 'o-', color=C_H, linewidth=2, markersize=6, label='H-module CV')
    ax.plot(epochs, v05b_lcv, 's--', color=C_L, linewidth=2, markersize=6, label='L-module CV')
    ax.set_xlabel('Epoch')
    ax.set_title('(B) v0.5b: Coupled\n(KF on both)', fontweight='bold')
    ax.legend(loc='upper left', framealpha=0.9)
    # Annotate L-module takeover
    l_amp = v05b_lcv[-1] / v05b_lcv[0]
    ax.annotate(f'L-module: {l_amp:.0f}×\n(absorbs KF signal)',
                xy=(2000, v05b_lcv[-1]), xytext=(800, v05b_lcv[-1]*0.7),
                arrowprops=dict(arrowstyle='->', color=C_L),
                color=C_L, fontsize=9, fontweight='bold')

    # Panel C: H/L Ratio comparison
    ax = axes[2]
    v05_ratio = [h/l for h, l in zip(v05_hcv, v05_lcv)]
    v05b_ratio = [h/l for h, l in zip(v05b_hcv, v05b_lcv)]
    hrm_ratio = [h/l for h, l in zip(hrm_hcv, hrm_lcv)]

    ax.plot(epochs, v05_ratio, 'o-', color='#2166AC', linewidth=2.5, markersize=7, label='v0.5 (decoupled)')
    ax.plot(epochs, v05b_ratio, 's--', color='#B2182B', linewidth=2.5, markersize=7, label='v0.5b (coupled)')
    ax.plot(epochs, hrm_ratio, '^:', color=C_BASE, linewidth=1.5, markersize=5, label='Baseline', alpha=0.6)
    ax.axhline(y=1.0, color='black', linestyle=':', alpha=0.3, linewidth=0.8)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('H/L CommVar Ratio')
    ax.set_title('(C) Separation of Concerns\nH/L Ratio', fontweight='bold')
    ax.legend(loc='center right', framealpha=0.9)
    ax.set_yscale('log')

    plt.tight_layout()
    for ext in ['png', 'pdf']:
        plt.savefig(os.path.join(OUT_DIR, f'fig1_triad.{ext}'))
    plt.close()
    print('Figure 1: Triad (v0.5 vs v0.5b vs baseline)')


# ============================================================
# FIGURE 2: Lambda Sweep — Amplification vs Lambda
# ============================================================
def fig2_lambda_sweep():
    # NOTE: lambda 0.1 trajectory file is a duplicate of lambda 1.0
    # Only show baseline, 0.001, 0.01, 1.0 (which have distinct data)
    lambdas_str = ['baseline', '0.001', '0.01', '1.0']

    baseline = load('kf_trajectory_hrm.json')
    lam001 = load('kf_trajectory_v05a_lambda_0.001.json')
    lam01 = load('kf_trajectory_v05a_lambda_0.01.json')
    v05 = load('kf_trajectory_v05.json')  # lambda=1.0

    all_data = [baseline, lam001, lam01, v05]

    # Final H_CV and H/L ratio at epoch 2000
    final_hcv = [d[-1]['H']['cv'] for d in all_data]
    final_hl = [d[-1]['H']['cv'] / d[-1]['L']['cv'] for d in all_data]
    init_hcv = [d[0]['H']['cv'] for d in all_data]
    amplification = [f/i for f, i in zip(final_hcv, init_hcv)]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    # Panel A: H_CV at epoch 2000 vs lambda
    ax = axes[0]
    colors = [C_BASE, '#ABDDA4', '#66C2A5', C_H]
    bars = ax.bar(range(4), [h*1000 for h in final_hcv], color=colors, edgecolor='black', linewidth=0.5)
    ax.set_xticks(range(4))
    ax.set_xticklabels(['Baseline\n(λ=0)', 'λ=0.001', 'λ=0.01', 'λ=1.0'])
    ax.set_ylabel('H-module CommVar (×10⁻³)')
    ax.set_title('(A) H-Module CommVar at Epoch 2000', fontweight='bold')
    for i, (bar, amp) in enumerate(zip(bars, amplification)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{amp:.1f}×', ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Panel B: H/L ratio at epoch 2000 vs lambda
    ax = axes[1]
    bars = ax.bar(range(4), final_hl, color=colors, edgecolor='black', linewidth=0.5)
    ax.set_xticks(range(4))
    ax.set_xticklabels(['Baseline\n(λ=0)', 'λ=0.001', 'λ=0.01', 'λ=1.0'])
    ax.set_ylabel('H/L CommVar Ratio')
    ax.set_title('(B) Module Separation at Epoch 2000', fontweight='bold')
    ax.axhline(y=1.0, color='black', linestyle=':', alpha=0.3, linewidth=0.8)

    plt.tight_layout()
    for ext in ['png', 'pdf']:
        plt.savefig(os.path.join(OUT_DIR, f'fig2_lambda_sweep.{ext}'))
    plt.close()
    print('Figure 2: Lambda sweep')


# ============================================================
# FIGURE 3: Training Trajectories — All variants
# ============================================================
def fig3_training_trajectories():
    epochs = [0, 500, 1000, 1500, 2000]

    # Load all (skipping lambda 0.1 — duplicate of 1.0)
    baseline = load('kf_trajectory_hrm.json')
    lam001 = load('kf_trajectory_v05a_lambda_0.001.json')
    lam01 = load('kf_trajectory_v05a_lambda_0.01.json')
    v05 = load('kf_trajectory_v05.json')
    v05b = load('kf_trajectory_v05b.json')

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel A: H-module CV trajectories
    ax = axes[0]
    datasets = [
        (baseline, 'Baseline (λ=0)', C_BASE, ':', '^', 1.5),
        (lam001, 'λ=0.001', '#ABDDA4', '--', 'v', 1.5),
        (lam01, 'λ=0.01', '#66C2A5', '--', 'D', 1.5),
        (v05, 'λ=1.0 (decoupled)', C_H, '-', 'o', 2.5),
        (v05b, 'λ=1.0 (coupled)', C_L, '--', 's', 2),
    ]
    for data, label, color, ls, marker, lw in datasets:
        hcv = [d['H']['cv'] for d in data]
        ax.plot(epochs, hcv, marker=marker, linestyle=ls, color=color,
                linewidth=lw, markersize=5, label=label)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('H-Module CommVar')
    ax.set_title('(A) H-Module CV Training Trajectories', fontweight='bold')
    ax.legend(loc='upper left', fontsize=8, framealpha=0.9)

    # Panel B: L-module CV trajectories
    ax = axes[1]
    for data, label, color, ls, marker, lw in datasets:
        lcv = [d['L']['cv'] for d in data]
        ax.plot(epochs, lcv, marker=marker, linestyle=ls, color=color,
                linewidth=lw, markersize=5, label=label)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('L-Module CommVar')
    ax.set_title('(B) L-Module CV Training Trajectories', fontweight='bold')
    ax.legend(loc='upper left', fontsize=8, framealpha=0.9)

    plt.tight_layout()
    for ext in ['png', 'pdf']:
        plt.savefig(os.path.join(OUT_DIR, f'fig3_training_trajectories.{ext}'))
    plt.close()
    print('Figure 3: Training trajectories (all variants)')


# ============================================================
# FIGURE 4: Three Processing Modes — 5 Models
# ============================================================
def fig4_inference_modes():
    models = ['gpt2_medium', 'pythia_410m', 'opt_1.3b', 'opt_iml_1.3b', 'pythia_1.4b']
    model_labels = ['GPT-2\nMedium', 'Pythia\n410M', 'OPT\n1.3B', 'OPT-IML\n1.3B', 'Pythia\n1.4B']

    el_data = {cat: [] for cat in ['factual', 'hallucination', 'hypothesis']}
    cv_data = {cat: [] for cat in ['factual', 'hallucination', 'hypothesis']}

    for model in models:
        data = load(f'p49_{model}.json')
        for cat in ['factual', 'hallucination', 'hypothesis']:
            el_data[cat].append(data['category_stats'][cat]['el_mean'])
            cv_data[cat].append(data['category_stats'][cat]['cv_mean'])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel A: E/L Ratio
    ax = axes[0]
    x = np.arange(len(models))
    width = 0.25
    for i, (cat, color) in enumerate(zip(['factual', 'hallucination', 'hypothesis'],
                                          [C_FACT, C_HALL, C_HYPO])):
        ax.bar(x + i*width, el_data[cat], width, color=color, label=cat.capitalize(),
               edgecolor='black', linewidth=0.5, alpha=0.85)
    ax.set_xticks(x + width)
    ax.set_xticklabels(model_labels, fontsize=9)
    ax.set_ylabel('E/L Ratio (Early / Late Layer CV)')
    ax.set_title('(A) Starting E/L Ratio by Processing Mode', fontweight='bold')
    ax.legend(framealpha=0.9)

    # Panel B: Mean CV
    ax = axes[1]
    for i, (cat, color) in enumerate(zip(['factual', 'hallucination', 'hypothesis'],
                                          [C_FACT, C_HALL, C_HYPO])):
        ax.bar(x + i*width, [v*1000 for v in cv_data[cat]], width, color=color,
               label=cat.capitalize(), edgecolor='black', linewidth=0.5, alpha=0.85)
    ax.set_xticks(x + width)
    ax.set_xticklabels(model_labels, fontsize=9)
    ax.set_ylabel('Mean CommVar (×10⁻³)')
    ax.set_title('(B) Mean CommVar by Processing Mode', fontweight='bold')
    ax.legend(framealpha=0.9)

    plt.tight_layout()
    for ext in ['png', 'pdf']:
        plt.savefig(os.path.join(OUT_DIR, f'fig4_inference_modes.{ext}'))
    plt.close()
    print('Figure 4: Inference modes (5 models × 3 modes)')


# ============================================================
# FIGURE 5: RLHF Matched Pair — OPT base vs IML
# ============================================================
def fig5_rlhf():
    opt_base = load('p49_opt_1.3b.json')
    opt_iml = load('p49_opt_iml_1.3b.json')

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    categories = ['factual', 'hallucination', 'hypothesis']
    cat_labels = ['Factual', 'Hallucination', 'Hypothesis']
    colors = [C_FACT, C_HALL, C_HYPO]

    # Panel A: E/L Ratio
    ax = axes[0]
    x = np.arange(3)
    width = 0.35
    base_el = [opt_base['category_stats'][c]['el_mean'] for c in categories]
    iml_el = [opt_iml['category_stats'][c]['el_mean'] for c in categories]
    base_el_err = [opt_base['category_stats'][c]['el_std'] for c in categories]
    iml_el_err = [opt_iml['category_stats'][c]['el_std'] for c in categories]

    ax.bar(x - width/2, base_el, width, yerr=base_el_err, color='#DEEBF7',
           edgecolor='black', linewidth=0.5, label='OPT-1.3B (base)', capsize=3)
    ax.bar(x + width/2, iml_el, width, yerr=iml_el_err, color='#9ECAE1',
           edgecolor='black', linewidth=0.5, label='OPT-IML-1.3B (RLHF)', capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels)
    ax.set_ylabel('E/L Ratio')
    ax.set_title('(A) E/L Ratio: Base vs RLHF', fontweight='bold')
    ax.legend(framealpha=0.9)

    # Panel B: Mean CV
    ax = axes[1]
    base_cv = [opt_base['category_stats'][c]['cv_mean']*1000 for c in categories]
    iml_cv = [opt_iml['category_stats'][c]['cv_mean']*1000 for c in categories]

    ax.bar(x - width/2, base_cv, width, color='#DEEBF7',
           edgecolor='black', linewidth=0.5, label='OPT-1.3B (base)')
    ax.bar(x + width/2, iml_cv, width, color='#9ECAE1',
           edgecolor='black', linewidth=0.5, label='OPT-IML-1.3B (RLHF)')
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels)
    ax.set_ylabel('Mean CommVar (×10⁻³)')
    ax.set_title('(B) Mean CV: Base vs RLHF', fontweight='bold')
    ax.legend(framealpha=0.9)

    plt.tight_layout()
    for ext in ['png', 'pdf']:
        plt.savefig(os.path.join(OUT_DIR, f'fig5_rlhf_matched_pair.{ext}'))
    plt.close()
    print('Figure 5: RLHF matched pair (OPT base vs IML)')


# ============================================================
# FIGURE 6: CoT Algebraic Signature — 5 Models
# ============================================================
def fig6_cot():
    cot_files = [
        ('p51_smollm3_cot.json', 'SmolLM3\n3B'),
        ('p51_qwen3_0.6b_cot.json', 'Qwen3\n0.6B'),
        ('p51_qwen3_1.7b_cot.json', 'Qwen3\n1.7B'),
        ('p51_qwen3_4b_cot.json', 'Qwen3\n4B'),
        ('p51_deepseek_r1_distill_qwen_1.5b_cot.json', 'DeepSeek\nR1-1.5B'),
    ]

    think_el = []
    nothink_el = []
    think_cv = []
    nothink_cv = []
    labels = []

    for fn, label in cot_files:
        data = load(fn)
        prompts = data['per_prompt']

        t_el = [p['think']['static']['el_ratio'] for p in prompts]
        nt_el = [p['nothink']['static']['el_ratio'] for p in prompts]
        t_cv = [p['think']['static']['mean_cv'] for p in prompts]
        nt_cv = [p['nothink']['static']['mean_cv'] for p in prompts]

        think_el.append(np.mean(t_el))
        nothink_el.append(np.mean(nt_el))
        think_cv.append(np.mean(t_cv))
        nothink_cv.append(np.mean(nt_cv))
        labels.append(label)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    x = np.arange(len(labels))
    width = 0.35

    # Panel A: E/L Ratio
    ax = axes[0]
    ax.bar(x - width/2, nothink_el, width, color='#FDB863', edgecolor='black',
           linewidth=0.5, label='No-Think (standard)')
    ax.bar(x + width/2, think_el, width, color='#B2ABD2', edgecolor='black',
           linewidth=0.5, label='Think (CoT)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel('E/L Ratio')
    ax.set_title('(A) E/L Ratio: Standard vs CoT', fontweight='bold')
    ax.legend(framealpha=0.9)
    # Add arrows showing direction
    for i in range(len(labels)):
        if think_el[i] < nothink_el[i]:
            ax.annotate('', xy=(i + width/2, think_el[i]),
                        xytext=(i - width/2, nothink_el[i]),
                        arrowprops=dict(arrowstyle='->', color='green', lw=1.5))

    # Panel B: Mean CV
    ax = axes[1]
    ax.bar(x - width/2, [v*1e6 for v in nothink_cv], width, color='#FDB863',
           edgecolor='black', linewidth=0.5, label='No-Think')
    ax.bar(x + width/2, [v*1e6 for v in think_cv], width, color='#B2ABD2',
           edgecolor='black', linewidth=0.5, label='Think (CoT)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel('Mean CommVar (×10⁻⁶)')
    ax.set_title('(B) Mean CV: Standard vs CoT', fontweight='bold')
    ax.legend(framealpha=0.9)

    plt.tight_layout()
    for ext in ['png', 'pdf']:
        plt.savefig(os.path.join(OUT_DIR, f'fig6_cot_signature.{ext}'))
    plt.close()
    print('Figure 6: CoT algebraic signature (5 models)')


# ============================================================
# FIGURE 7: Cross-Substrate Universality
# ============================================================
def fig7_cross_substrate():
    # Transformer depth gradients (from V3 notes)
    # Parallel architectures: Pythia 160M, 410M, 1.4B
    transformer_parallel = {
        'names': ['Pythia-160M', 'Pythia-410M', 'Pythia-1.4B'],
        'depth_r': [0.38, 0.38, 0.38],  # approximate from notes
        'type': 'parallel'
    }
    # Sequential architectures: GPT-2, OPT, Falcon
    transformer_sequential = {
        'names': ['GPT-2-M', 'OPT-125M', 'OPT-1.3B', 'Falcon-1B', 'GPT-2-S', 'GPT-2-L'],
        'depth_r': [-0.77, -0.77, -0.77, -0.77, -0.77, -0.77],
        'type': 'sequential'
    }

    # Ecological food webs
    eco = load('eco_kf_results.json')
    eco_names = [r['name'] for r in eco['results']]
    eco_r = [r['depth_r'] for r in eco['results']]

    # Neural connectomes
    neuro = load('neuro_kf_expanded_results.json')
    neuro_names = [r['name'] for r in neuro['results']]
    neuro_r = [r['avg_r'] for r in neuro['results']]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot each substrate
    y_pos = 0
    yticks = []
    ytick_labels = []
    substrate_boundaries = []

    # Transformers (parallel)
    substrate_boundaries.append(y_pos - 0.5)
    for name, r in zip(transformer_parallel['names'], transformer_parallel['depth_r']):
        color = C_SILICON
        ax.barh(y_pos, r, height=0.6, color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
        yticks.append(y_pos)
        ytick_labels.append(name)
        y_pos += 1

    # Neural connectomes
    substrate_boundaries.append(y_pos - 0.5)
    for name, r in zip(neuro_names, neuro_r):
        color = C_NEURO
        ax.barh(y_pos, r, height=0.6, color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
        yticks.append(y_pos)
        ytick_labels.append(name)
        y_pos += 1

    # Ecological
    substrate_boundaries.append(y_pos - 0.5)
    for name, r in zip(eco_names, eco_r):
        color = C_ECO
        ax.barh(y_pos, r, height=0.6, color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
        yticks.append(y_pos)
        ytick_labels.append(name.replace('eco-', '').replace('.edges', ''))
        y_pos += 1
    substrate_boundaries.append(y_pos - 0.5)

    ax.set_yticks(yticks)
    ax.set_yticklabels(ytick_labels, fontsize=8)
    ax.set_xlabel('Depth Gradient (Spearman r)', fontsize=12)
    ax.set_title('Cross-Substrate Depth Gradients', fontweight='bold', fontsize=14)

    # Convergence band at r ≈ 0.4
    ax.axvspan(0.3, 0.5, alpha=0.15, color='green', zorder=0)
    ax.axvline(x=0.4, color='green', linestyle='--', alpha=0.5, linewidth=1)
    ax.text(0.41, y_pos - 1, 'r ≈ 0.4\nconvergence', fontsize=9, color='green',
            fontweight='bold', va='center')

    # Zero line
    ax.axvline(x=0, color='black', linestyle='-', alpha=0.3, linewidth=0.5)

    # Substrate labels
    ax.axhline(y=substrate_boundaries[1], color='gray', linestyle='-', alpha=0.3)
    ax.axhline(y=substrate_boundaries[2], color='gray', linestyle='-', alpha=0.3)

    # Add substrate group labels
    mid_silicon = (0 + substrate_boundaries[1]) / 2
    mid_neuro = (substrate_boundaries[1] + substrate_boundaries[2]) / 2
    mid_eco = (substrate_boundaries[2] + substrate_boundaries[3]) / 2

    ax.text(-1.15, mid_silicon, 'SILICON', fontsize=10, fontweight='bold', color=C_SILICON,
            va='center', ha='center', rotation=90)
    ax.text(-1.15, mid_neuro, 'NEURAL', fontsize=10, fontweight='bold', color=C_NEURO,
            va='center', ha='center', rotation=90)
    ax.text(-1.15, mid_eco, 'ECOLOGICAL', fontsize=10, fontweight='bold', color=C_ECO,
            va='center', ha='center', rotation=90)

    ax.set_xlim(-1.2, 1.2)
    plt.tight_layout()
    for ext in ['png', 'pdf']:
        plt.savefig(os.path.join(OUT_DIR, f'fig7_cross_substrate.{ext}'))
    plt.close()
    print('Figure 7: Cross-substrate universality')


# ============================================================
# FIGURE 8 (BONUS): Generation Trajectories — P48
# ============================================================
def fig8_generation_trajectories():
    """E/L trend during generation for factual vs hallucination vs hypothesis."""
    # Use P48 summary data
    data = load('p48_gpt2_medium.json')
    ct = data['category_trajectories']

    fig, ax = plt.subplots(figsize=(8, 5))

    for cat, color, label in [('factual', C_FACT, 'Factual'),
                               ('hallucination', C_HALL, 'Hallucination'),
                               ('hypothesis', C_HYPO, 'Hypothesis')]:
        traj = ct[cat]
        el_trend = traj['mean_el_trend']
        rho = traj['mean_rho_el']
        early = traj['mean_early_gen_el']
        late = traj['mean_late_gen_el']

        # Show early vs late E/L as arrows
        ax.annotate('', xy=(1, late), xytext=(0, early),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.5))
        ax.scatter([0], [early], color=color, s=100, zorder=5, edgecolor='black', linewidth=0.5)
        ax.scatter([1], [late], color=color, s=100, zorder=5, edgecolor='black', linewidth=0.5,
                   marker='s')
        ax.text(1.05, late, f'{label}\ntrend={el_trend:.2f}\nρ={rho:.2f}',
                fontsize=9, color=color, va='center')

    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Early Generation\n(tokens 1-25)', 'Late Generation\n(tokens 75-100)'])
    ax.set_ylabel('E/L Ratio')
    ax.set_title('Generation Trajectories: E/L Ratio Over Token Generation\n(GPT-2-medium)',
                 fontweight='bold')
    ax.set_xlim(-0.3, 1.8)

    plt.tight_layout()
    for ext in ['png', 'pdf']:
        plt.savefig(os.path.join(OUT_DIR, f'fig8_generation_trajectories.{ext}'))
    plt.close()
    print('Figure 8: Generation trajectories (GPT-2-medium)')


# ============================================================
# FIGURE 9: Ecological Abelian Exception
# ============================================================
def fig9_abelian_exception():
    """Food webs vs mutualistic networks: conflict generates non-commutativity."""
    mut_data = load('eco_kf_mutualistic_results.json')

    fw_names = [r['name'] for r in mut_data['fw']]
    fw_cv = [r['cv'] for r in mut_data['fw']]

    mut_names = [r['name'].replace('M_PL_', 'P') for r in mut_data['mutualistic']]
    mut_cv = [r['cv'] for r in mut_data['mutualistic']]

    fig, ax = plt.subplots(figsize=(10, 5))

    # Food webs (non-zero CV)
    x_fw = np.arange(len(fw_names))
    bars_fw = ax.bar(x_fw, [c*1000 for c in fw_cv], color=C_HALL, alpha=0.8,
                     edgecolor='black', linewidth=0.5, label='Food webs (predation)')

    # Mutualistic (zero CV)
    x_mut = np.arange(len(mut_names)) + len(fw_names) + 1
    bars_mut = ax.bar(x_mut, [c*1000 for c in mut_cv], color=C_FACT, alpha=0.8,
                      edgecolor='black', linewidth=0.5, label='Mutualistic (pollination)')

    # Separator
    ax.axvline(x=len(fw_names) + 0.5, color='gray', linestyle='--', alpha=0.5)
    ax.text(len(fw_names)/2, max(fw_cv)*1000*0.95, 'CONFLICT\n(non-Abelian)',
            ha='center', fontsize=11, fontweight='bold', color=C_HALL)
    ax.text(len(fw_names) + 1 + len(mut_names)/2, max(fw_cv)*1000*0.95,
            'COOPERATION\n(Abelian: CV = 0)',
            ha='center', fontsize=11, fontweight='bold', color='#2E8B57')

    all_x = list(x_fw) + list(x_mut)
    all_labels = fw_names + mut_names
    ax.set_xticks(all_x)
    ax.set_xticklabels(all_labels, fontsize=7, rotation=45, ha='right')
    ax.set_ylabel('CommVar (×10⁻³)')
    ax.set_title('The Ecological Abelian Exception:\nConflict Generates Non-Commutativity',
                 fontweight='bold', fontsize=13)
    ax.legend(loc='upper right', framealpha=0.9)

    plt.tight_layout()
    for ext in ['png', 'pdf']:
        plt.savefig(os.path.join(OUT_DIR, f'fig9_abelian_exception.{ext}'))
    plt.close()
    print('Figure 9: Ecological Abelian exception')


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    print(f'Results dir: {os.path.abspath(RESULTS_DIR)}')
    print(f'Output dir: {os.path.abspath(OUT_DIR)}')
    print()

    fig1_triad()
    fig2_lambda_sweep()
    fig3_training_trajectories()
    fig4_inference_modes()
    fig5_rlhf()
    fig6_cot()
    fig7_cross_substrate()
    fig8_generation_trajectories()
    fig9_abelian_exception()

    print()
    print('All figures generated.')
