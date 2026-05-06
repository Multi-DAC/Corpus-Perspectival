"""
smoke_test_callbacks.py — 30-second pre-launch sanity check for callbacks + probes.

Drafted 2026-04-25 ~00:30 PST in response to the Mirror entry on smoke-testing
new callbacks before launch. Extended 2026-04-25 mid-afternoon with probe
eval-pattern check (Mirror #21) to catch the SB3 gates-after-reset bug class
before any new probe ships.

Usage:
    python smoke_test_callbacks.py

Exit code 0 = all callbacks + probes pass.
Exit code 1 = at least one check failed; details printed.

What it tests:
  1. Imports succeed (catches stale import paths after refactors).
  2. Callbacks construct with valid args.
  3. The attributes the callbacks read off env/curriculum actually exist
     (catches PerManeuverMasteryLogger bug class).
  4. The hook the callback uses fires at the timing the docstring claims
     (catches LogStdClampCallback bug class via SB3 source assertion).
  5. No probe under probes/ reads per-episode counters from venv.envs[N]
     after the step loop — SB3's DummyVecEnv auto-resets the env on done,
     zeroing those attrs before control returns. Episode counters MUST be
     read from info[N][<key>] during the step loop. (Mirror #21 — Phase 2
     67.5M was nearly written off because of this.)

Does NOT test full training behavior — that requires a real model, env, and
several rollout iterations. The goal here is to catch obvious wiring bugs
before they cost compute hours OR mis-judged checkpoints.
"""

import ast
import os
import sys
import json
import inspect
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PROBES_DIR = Path(__file__).resolve().parent.parent / 'probes'

# Per-episode env attributes known to be reset by DummyVecEnv on done.
# Reading any of these from venv.envs[N] after a done check returns ZERO.
# Add new attrs here as the env grows new per-episode counters.
EPISODE_RESET_ATTRS = {
    'episode_gates',
    'episode_reward',
    'episode_length',
    'episode_steps',
    'gates_passed',  # if mirrored as env attr
    'current_step',
    'steps_in_episode',
}


def _check(name, fn):
    print(f'  [{name}] ', end='', flush=True)
    try:
        fn()
        print('OK')
        return True
    except Exception as e:
        print(f'FAIL: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
        return False


def main():
    print('=' * 70)
    print('Callback smoke test — Phase 2 stack')
    print('=' * 70)
    results = []

    # 1. Imports
    def imports():
        global LogStdClampCallback, GradNormLoggerCallback
        global CheckpointWithVecNormalize, PerManeuverMasteryLogger
        global InfiniteGateEnv
        from train_infinite_v3 import LogStdClampCallback, GradNormLoggerCallback
        from train_phase2 import CheckpointWithVecNormalize, PerManeuverMasteryLogger
        from infinite_gate_env import InfiniteGateEnv
    results.append(('imports', _check('imports', imports)))

    # 2. PerManeuverMasteryLogger: env contract check
    def env_contract():
        env = InfiniteGateEnv(seed=0, adaptive_curriculum=True)
        # Must reset before mastery state is meaningful
        env.reset()
        assert hasattr(env, '_get_per_maneuver_masteries'), (
            'InfiniteGateEnv missing _get_per_maneuver_masteries() — '
            'PerManeuverMasteryLogger will produce empty rates'
        )
        rates = env._get_per_maneuver_masteries()
        assert isinstance(rates, dict), f'expected dict, got {type(rates)}'
        assert hasattr(env, '_ema_mastery'), (
            'InfiniteGateEnv missing _ema_mastery scalar — '
            'PerManeuverMasteryLogger ema_overall will stay None'
        )
        ema = env._ema_mastery
        assert isinstance(ema, (int, float)), f'expected number, got {type(ema)}'
    results.append(('env_contract', _check('env_contract', env_contract)))

    # 3. PerManeuverMasteryLogger: instantiation + attribute set
    def per_maneuver_construct():
        with tempfile.TemporaryDirectory() as tmp:
            log_path = os.path.join(tmp, 'mastery.json')
            cb = PerManeuverMasteryLogger(log_path=log_path, log_freq=1000)
            assert cb.log_freq == 1000
            assert cb.history == []
            assert cb._last_log == 0
    results.append(('per_maneuver_construct', _check('per_maneuver_construct', per_maneuver_construct)))

    # 4. CheckpointWithVecNormalize: instantiation + dir creation
    def checkpoint_construct():
        with tempfile.TemporaryDirectory() as tmp:
            cb = CheckpointWithVecNormalize(
                save_freq=250000,
                save_path=os.path.join(tmp, 'checkpoints'),
                name_prefix='test',
                vec_env=None,  # not exercised in this test
            )
            assert cb.save_path.exists(), 'save_path was not created on init'
            assert cb._last_save == 0
    results.append(('checkpoint_construct', _check('checkpoint_construct', checkpoint_construct)))

    # 5. LogStdClampCallback: hook timing assertion against SB3 source
    def logstd_hook_timing():
        """Verify F2 hook is _on_rollout_start (clamp fires AFTER train(),
        BEFORE next collect_rollouts). The earlier _on_rollout_end hook fired
        BEFORE train() and produced 1:1024 snap-back ratio, not a true bound
        — fixed 2026-04-25 by renaming to _on_rollout_start.
        """
        from train_infinite_v3 import LogStdClampCallback
        cb = LogStdClampCallback(min_std=0.1, max_std=1.0)

        # Verify the hook actually used (post-fix: _on_rollout_start, not end)
        cls_dict = vars(LogStdClampCallback)
        assert '_on_rollout_start' in cls_dict, (
            'LogStdClampCallback should override _on_rollout_start (post-2026-04-25 fix). '
            'Found overrides: ' + str([k for k in cls_dict if k.startswith('_on_')])
        )
        assert '_on_rollout_end' not in cls_dict, (
            'LogStdClampCallback still overrides _on_rollout_end — this is the OLD '
            'broken timing (fires BEFORE train()). Should be _on_rollout_start.'
        )

        # Read SB3 to verify firing order: train() runs, then on_rollout_start
        # fires before next collect_rollouts. So clamp lands AFTER gradient
        # updates and BEFORE sampling — correct semantics.
        from stable_baselines3.common import on_policy_algorithm as sb3_op
        learn_src = inspect.getsource(sb3_op.OnPolicyAlgorithm.learn)
        cr_idx = learn_src.find('collect_rollouts')
        train_idx = learn_src.find('self.train()')
        assert cr_idx >= 0 and train_idx >= 0, 'unexpected SB3 source layout'
        assert cr_idx < train_idx, (
            'SB3 source ordering changed: collect_rollouts now AFTER self.train(). '
            'F2 timing analysis needs re-checking.'
        )

        # Docstring should no longer claim "after every update"
        docstring = LogStdClampCallback.__doc__ or ''
        if 'after every update' in docstring.lower():
            print('\n    [WARN] Docstring still claims "after every update" — '
                  'F2 now clamps once per rollout boundary, not once per update.')
    results.append(('logstd_hook_timing', _check('logstd_hook_timing', logstd_hook_timing)))

    # 6. Probe eval-pattern check (Mirror #21)
    def probe_eval_pattern():
        """Scan probes/*.py for the SB3 gates-after-reset bug pattern.

        Bug pattern: reading a per-episode counter (e.g. episode_gates) from
        venv.envs[N] anywhere in the file. SB3's DummyVecEnv auto-resets the
        underlying env on done before control returns from step_wait(), so
        these attrs are zero when read after the step. The correct pattern
        is reading info[N]['<key>'] inside the step loop.

        Caught the 2026-04-25 mid-afternoon false STRATEGY-AT-RISK verdict on
        Phase 2 67.5M. See feedback_sb3_gates_after_reset.md in auto-memory
        and Mirror #21 (verify-before-condemning).
        """
        if not PROBES_DIR.exists():
            print(f'\n    [SKIP] no probes dir at {PROBES_DIR}')
            return

        violations = []
        for probe in sorted(PROBES_DIR.rglob('*.py')):
            try:
                src = probe.read_text(encoding='utf-8')
                tree = ast.parse(src)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                # Match: <something>.envs[<N>].<attr>  where attr is in our list
                if not isinstance(node, ast.Attribute):
                    continue
                if node.attr not in EPISODE_RESET_ATTRS:
                    continue
                # Walk down: node.value should be Subscript(Attribute(_, 'envs'), _)
                inner = node.value
                if not isinstance(inner, ast.Subscript):
                    continue
                inner_v = inner.value
                if not (isinstance(inner_v, ast.Attribute) and inner_v.attr == 'envs'):
                    continue
                violations.append(
                    f'{probe.relative_to(PROBES_DIR.parent)}:{node.lineno} — '
                    f'reads `.envs[...].{node.attr}` after step (zeroed by auto-reset). '
                    f'Use info[N][\'{node.attr}\'] inside the step loop instead.'
                )

        if violations:
            msg = (
                f'{len(violations)} probe(s) read per-episode env counters that get '
                f'zeroed by SB3 DummyVecEnv auto-reset:\n        '
                + '\n        '.join(violations)
                + '\n        See feedback_sb3_gates_after_reset.md / Mirror #21.'
            )
            raise AssertionError(msg)
    results.append(('probe_eval_pattern', _check('probe_eval_pattern', probe_eval_pattern)))

    # Summary
    print('\n' + '=' * 70)
    n_pass = sum(1 for _, ok in results if ok)
    n_total = len(results)
    print(f'Result: {n_pass}/{n_total} passed')
    if n_pass < n_total:
        print('Failed:')
        for name, ok in results:
            if not ok:
                print(f'  - {name}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
