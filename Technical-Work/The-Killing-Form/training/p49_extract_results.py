#!/usr/bin/env python3
"""
Extract P49 results from checkpoint files and logs.
Run this after both p49_baseline and p49_kf experiments complete.

Usage: python p49_extract_results.py
"""

import json
import os
import sys

# Add HRM to path
sys.path.insert(0, '/home/clawd/HRM')

import torch
import numpy as np

BASELINE_DIR = '/home/clawd/HRM/checkpoints/kf_p49_baseline_v2'
KF_DIR = '/home/clawd/HRM/checkpoints/kf_p49_decoupled_v2'
DATA_DIR = '/home/clawd/HRM/data/sudoku-easy-1k-aug-1000'
OUTPUT = '/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/results/p49_training_results.json'

def load_checkpoint(ckpt_dir, epoch):
    path = os.path.join(ckpt_dir, f'epoch_{epoch}.pt')
    if not os.path.exists(path):
        return None
    return torch.load(path, map_location='cpu')

def get_available_checkpoints(ckpt_dir):
    if not os.path.exists(ckpt_dir):
        return []
    return sorted([int(f.replace('epoch_', '').replace('.pt', ''))
                   for f in os.listdir(ckpt_dir) if f.startswith('epoch_')])

def main():
    print('P49 Result Extraction')
    print('=' * 60)

    # Check what's available
    baseline_epochs = get_available_checkpoints(BASELINE_DIR)
    kf_epochs = get_available_checkpoints(KF_DIR)

    print(f'Baseline checkpoints: {baseline_epochs}')
    print(f'KF checkpoints: {kf_epochs}')

    if not baseline_epochs and not kf_epochs:
        print('No checkpoints found yet. Experiments still running.')
        return

    results = {
        'experiment': 'P49',
        'task': 'easy sudoku (45-55 clues, ~31 blanks)',
        'architecture': 'HRM v0.5 (27.3M params)',
        'baseline': {},
        'kf_decoupled': {}
    }

    # Parse log files for accuracy data
    for logfile, key in [('/home/clawd/p49_baseline_v2.log', 'baseline'),
                          ('/home/clawd/p49_kf_v2.log', 'kf_decoupled')]:
        if os.path.exists(logfile):
            with open(logfile) as f:
                content = f.read()
            # Extract measurements
            measurements = []
            for line in content.split('\n'):
                if 'Exact acc:' in line:
                    parts = line.strip().split()
                    exact_idx = parts.index('acc:') + 1
                    exact = float(parts[exact_idx])
                    token_idx = parts.index('acc:', exact_idx) + 1
                    token = float(parts[token_idx])
                    measurements.append({'exact': exact, 'token': token})
                if '[KF @' in line and 'H_CV=' in line:
                    # Parse KF measurement
                    hcv = float(line.split('H_CV=')[1].split()[0])
                    lcv = float(line.split('L_CV=')[1].split()[0])
                    ratio = float(line.split('ratio=')[1].split()[0])
                    step = line.split('[KF @ ')[1].split(']')[0]
                    results[key][f'kf_{step}'] = {
                        'H_CV': hcv, 'L_CV': lcv, 'ratio': ratio
                    }

            if measurements:
                results[key]['accuracy'] = measurements

    # Summary
    print()
    print('RESULTS:')
    print(json.dumps(results, indent=2, default=str))

    # Save
    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f'\nSaved to: {OUTPUT}')

if __name__ == '__main__':
    main()
