"""
KF Runner — Incremental save wrapper for Killing Form experiments.

Solves the WSL stdout pipe buffering problem. Instead of saving all results
at the end (where pipe truncation loses everything), saves each prompt's
results incrementally to a JSON file on the Windows filesystem.

Usage:
  from kf_runner import IncrementalSaver

  saver = IncrementalSaver('p49_experiment', model_id='gpt2-medium')
  for prompt_name, data in results:
      saver.save_prompt(prompt_name, data)
  saver.finalize(category_stats)
"""
import json
import os
import time
import sys


class IncrementalSaver:
    """Saves experiment results incrementally to avoid WSL pipe truncation."""

    def __init__(self, experiment_name, model_id, n_layers=None, n_heads=None,
                 base_dir="/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival"):
        self.experiment_name = experiment_name
        self.model_id = model_id
        self.base_dir = base_dir
        self.start_time = time.time()

        short = model_id.split('/')[-1].replace('-', '_').lower()
        self.filename = f"{experiment_name}_{short}.json"
        self.filepath = os.path.join(base_dir, self.filename)

        self.data = {
            'experiment': experiment_name,
            'model': model_id,
            'n_layers': n_layers,
            'n_heads': n_heads,
            'status': 'running',
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'prompts': {},
            'category_stats': None,
        }
        self._write()
        print(f"[IncrementalSaver] Saving to: {self.filepath}", flush=True)

    def save_prompt(self, prompt_name, prompt_data):
        """Save one prompt's results. Called after each prompt completes."""
        self.data['prompts'][prompt_name] = prompt_data
        self.data['prompts_completed'] = len(self.data['prompts'])
        self._write()

    def finalize(self, category_stats=None, extra=None):
        """Mark experiment as complete with final stats."""
        self.data['status'] = 'complete'
        self.data['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.data['elapsed_seconds'] = round(time.time() - self.start_time, 1)
        if category_stats:
            self.data['category_stats'] = category_stats
        if extra:
            self.data.update(extra)
        self._write()
        print(f"[IncrementalSaver] Finalized: {self.filepath}", flush=True)

    def _write(self):
        """Write current state to disk."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)


def flush_print(*args, **kwargs):
    """Print with immediate flush — bypasses Python/WSL buffering."""
    print(*args, **kwargs, flush=True)
    sys.stdout.flush()
