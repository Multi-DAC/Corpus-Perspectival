"""
train_infinite_v3.py - Infinite Gate Training WITH structural fixes (Day 83 rho-probe).

Changes vs train_infinite.py:
  F1. VecNormalize wraps DummyVecEnv  -> obs + reward normalization
  F2. LogStdClampCallback             -> prevents log_std divergence (esp. yaw)
  F3. GradNormLoggerCallback          -> per-trunk gradient norm telemetry

Run short validation first (--total-steps 200000 --n-envs 4) before committing
to a long retrain. Probes v4 compare the validated checkpoint to the 60.4M baseline.

Usage:
    python train_infinite_v3.py --total-steps 200000 --n-envs 4 --tag validation
"""

import os, sys, time, argparse, json
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, str(Path(__file__).parent.parent / 'rl'))

from infinite_gate_env import InfiniteGateEnv, ManeuverLibrary
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback, BaseCallback
import torch


# =============================================================================
# Checkpoint + VecNormalize (fix: stock CheckpointCallback drops vecnorm stats,
# so a killed run leaves unusable checkpoints — bit us on the 2026-06-01 W5 stall).
# =============================================================================
class CheckpointWithVecNormalize(BaseCallback):
    """Saves both PPO policy and VecNormalize stats at every checkpoint."""
    def __init__(self, save_freq, save_path, name_prefix, vec_env, verbose=0):
        super().__init__(verbose)
        self.save_freq = save_freq
        self.save_path = Path(save_path)
        self.name_prefix = name_prefix
        self.vec_env = vec_env
        self.save_path.mkdir(parents=True, exist_ok=True)
        self._last_save = 0

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_save < self.save_freq:
            return True
        self._last_save = self.num_timesteps
        ckpt_name = f'{self.name_prefix}_{self.num_timesteps}_steps'
        self.model.save(str(self.save_path / ckpt_name))
        self.vec_env.save(str(self.save_path / f'{ckpt_name}_vecnorm.pkl'))
        return True


# =============================================================================
# F2. LogStdClampCallback
# =============================================================================
class LogStdClampCallback(BaseCallback):
    """Clamp policy log_std to [log(min_std), log(max_std)] before each rollout.

    Rationale (rho-probe v3): log_std[3] (yaw) reached 19.93 at 500K steps
    and drifted to 42.68 by 68M. Gradient pressure from PPO entropy bonus on
    weak-signal action dims is unbounded. Clamp prevents divergence without
    changing the policy architecture.

    Hook timing (corrected 2026-04-25): hooked on `_on_rollout_start`, which
    fires AFTER the prior `train()` (and its ~1024 gradient updates per call
    for n_steps=4096 x 16 envs / batch_size=512 x n_epochs=8) and BEFORE the
    next `collect_rollouts()`. Sampling therefore proceeds with bounded
    log_std. The earlier `_on_rollout_end` hook fired BEFORE `train()` and
    produced a 1:1024 snap-back ratio, not a true bound.
    """
    def __init__(self, min_std=0.1, max_std=1.0, verbose=0):
        super().__init__(verbose)
        self.log_min = float(np.log(min_std))
        self.log_max = float(np.log(max_std))
        self.n_clamps = 0

    def _on_step(self) -> bool:
        return True

    def _on_rollout_start(self) -> None:
        with torch.no_grad():
            ls = self.model.policy.log_std
            pre = ls.data.clone()
            ls.data.clamp_(self.log_min, self.log_max)
            if not torch.equal(pre, ls.data):
                self.n_clamps += 1
                if self.verbose:
                    print(f'    [F2] clamped log_std: pre={pre.tolist()} post={ls.data.tolist()}')


# =============================================================================
# F3. GradNormLoggerCallback - per-trunk gradient norm telemetry
# =============================================================================
class GradNormLoggerCallback(BaseCallback):
    """Log gradient norms for policy_trunk, value_trunk, action_net, value_net,
    and log_std separately. Writes to JSON every `log_freq` steps.

    Rationale: yaw log_std divergence was invisible in reward curves. Per-dim
    gradient telemetry catches similar pathologies early.
    """
    def __init__(self, log_path, log_freq=50_000, verbose=0):
        super().__init__(verbose)
        self.log_path = str(log_path)
        self.log_freq = log_freq
        self.history = []
        self._last_log = 0

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_log < self.log_freq:
            return True
        self._last_log = self.num_timesteps
        # Gather grad norms from most recent backward pass
        groups = {
            'policy_trunk': 'mlp_extractor.policy_net',
            'value_trunk':  'mlp_extractor.value_net',
            'action_net':   'action_net',
            'value_net':    'value_net',
            'log_std':      'log_std',
        }
        entry = {'step': int(self.num_timesteps)}
        for name, prefix in groups.items():
            norms = []
            for pname, p in self.model.policy.named_parameters():
                if pname.startswith(prefix) and p.grad is not None:
                    norms.append(p.grad.detach().norm().item())
            entry[name] = float(np.sqrt(np.sum([n*n for n in norms]))) if norms else 0.0
        # Also log_std values
        ls = self.model.policy.log_std.detach().tolist()
        entry['log_std_values'] = ls
        self.history.append(entry)
        with open(self.log_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        return True


# =============================================================================
# Training
# =============================================================================
def train(args):
    out_dir = Path(__file__).parent / 'runs' / f'infinite_v3_{args.tag}_{int(time.time())}'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('=' * 72)
    print(f'Infinite Gate Training v3 (F1+F2+F3) -- {args.tag}')
    print('=' * 72)
    print(f'  Output: {out_dir}')
    print(f'  Target steps: {args.total_steps:,}')
    print(f'  Parallel envs: {args.n_envs}')
    print(f'  F1: VecNormalize ENABLED')
    print(f'  F2: log_std clamp [log(0.1), log(1.0)]')
    print(f'  F3: gradient norm telemetry @ {args.grad_log_freq:,} steps')

    def make_infinite_env(seed):
        def _init():
            env = InfiniteGateEnv(
                gate_radius=0.75, max_steps=30000, dt=0.002, substeps=1,
                domain_rand=True, domain_rand_scale=0.15,
                adaptive_curriculum=True, ground_start_prob=args.ground_start_prob,
                perception_obs=args.perception_obs,
                seed=seed,
            )
            return Monitor(env)
        return _init

    raw_envs = DummyVecEnv([make_infinite_env(seed=i*42 + args.base_seed)
                            for i in range(args.n_envs)])

    # F1: VecNormalize — obs and reward both normalized. On --resume, load the paired vecnorm
    # stats (saved per-checkpoint by CheckpointWithVecNormalize) so the resilient loop continues
    # with correct normalization — NOT fresh stats (the latent bug in the old train_infinite.py).
    if args.resume and os.path.exists(args.resume.replace('.zip', '') + '_vecnorm.pkl'):
        vp = args.resume.replace('.zip', '') + '_vecnorm.pkl'
        train_envs = VecNormalize.load(vp, raw_envs)
        train_envs.training = True
        train_envs.norm_reward = True
        print(f'  Resumed VecNormalize stats from {vp}')
    else:
        train_envs = VecNormalize(
            raw_envs, norm_obs=True, norm_reward=True,
            clip_obs=10.0, clip_reward=10.0, gamma=0.999,
        )

    if args.resume:
        model = PPO.load(args.resume, env=train_envs, device='cpu')
        print(f'  RESUMED policy from {args.resume}')
    else:
        model = PPO(
            'MlpPolicy', train_envs,
            learning_rate=3e-4, clip_range=0.2, ent_coef=0.01,
            n_steps=4096, batch_size=512, n_epochs=8,
            gamma=0.999, gae_lambda=0.95, max_grad_norm=0.5, vf_coef=0.5,
            policy_kwargs=dict(net_arch=dict(pi=[512, 512], vf=[512, 512])),
            verbose=0, device='cpu',
        )
    print(f'  Model params: {sum(p.numel() for p in model.policy.parameters()):,}')

    ckpt_cb = CheckpointWithVecNormalize(
        save_freq=max(args.save_every, 25_000) // args.n_envs,
        save_path=str(out_dir / 'checkpoints'),
        name_prefix='ppo_v3',
        vec_env=train_envs,
    )
    logstd_cb = LogStdClampCallback(min_std=0.1, max_std=1.0, verbose=0)
    grad_cb = GradNormLoggerCallback(
        log_path=out_dir / 'grad_norms.json',
        log_freq=args.grad_log_freq,
    )

    t0 = time.time()
    model.learn(
        total_timesteps=args.total_steps,
        callback=[ckpt_cb, logstd_cb, grad_cb],
        reset_num_timesteps=True,
        tb_log_name='ppo_v3',
        progress_bar=False,
    )
    dt = time.time() - t0

    # Save final model + the VecNormalize stats (required for later eval)
    model.save(str(out_dir / 'final_model'))
    train_envs.save(str(out_dir / 'vec_normalize.pkl'))

    print(f'\nTraining done: {args.total_steps:,} steps in {dt/60:.1f} min '
          f'({args.total_steps/dt:.0f} steps/sec)')
    print(f'log_std clamp fires: {logstd_cb.n_clamps}')
    print(f'Final log_std: {model.policy.log_std.detach().tolist()}')
    print(f'Saved: {out_dir}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--total-steps', type=int, default=200_000)
    p.add_argument('--n-envs', type=int, default=4)
    p.add_argument('--ground-start-prob', type=float, default=0.0,
                   help='fraction of episodes starting at far ground rest (takeoff curriculum)')
    p.add_argument('--perception-obs', action='store_true',
                   help='W5: train on perception-grade obs (W3-calibrated detector noise) not privileged state')
    p.add_argument('--resume', type=str, default=None,
                   help='resume policy + paired vecnorm from a checkpoint .zip (resilient-loop use)')
    p.add_argument('--base-seed', type=int, default=17)
    p.add_argument('--tag', type=str, default='validation')
    p.add_argument('--grad-log-freq', type=int, default=20_000)
    p.add_argument('--save-every', type=int, default=500_000)
    args = p.parse_args()
    train(args)


if __name__ == '__main__':
    main()
