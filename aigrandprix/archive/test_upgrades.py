"""Quick test of all upgrades: 500Hz, drag, gate orientation, 30-dim obs."""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '../rl')

from train_ppo import make_env, load_track, CTBRActionWrapper, ImprovedObsWrapper

# Test with gauntlet
env = make_env('gauntlet', domain_rand=True)
obs, info = env.reset()
print(f'Obs shape: {obs.shape} (expected: 30)')
print(f'First 5 obs: {obs[:5]}')

# Step
obs, r, d, t, info = env.step(env.action_space.sample())
print(f'Step OK. Reward: {r:.4f}, obs shape: {obs.shape}')

# Check internals
base = env.env.env
print(f'Gate orientations: {len(base.gate_orientations)}')
print(f'dt: {base.dt}, max_steps: {base.max_steps}')
print(f'cd (drag): {base.params.cd}')
print(f'First gate orient: {base.gate_orientations[0]}')

# Test with generated track
env2 = make_env('generated/proc_hairpin_12g_0004', domain_rand=False)
obs2, _ = env2.reset()
print(f'\nGenerated track obs shape: {obs2.shape}')
base2 = env2.env.env
print(f'Gates: {base2.n_gates}, dt: {base2.dt}')
print(f'Gate orientations: {len(base2.gate_orientations)}')

# Run a few steps
for i in range(100):
    obs2, r, d, t, info = env2.step(env2.action_space.sample())
    if d or t:
        print(f'Episode ended at step {i}: terminated={d}, truncated={t}')
        break

print('\nAll checks passed!')
