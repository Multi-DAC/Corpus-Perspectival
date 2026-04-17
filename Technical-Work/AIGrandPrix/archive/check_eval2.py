import numpy as np

eval_path = r"C:\Users\mercu\clawd\projects\aigrandprix\rl\runs\gauntlet_1770766522\eval_logs\evaluations.npz"

data = np.load(eval_path)

print("=== Evaluation Results Over Time ===")
print(f"{'Steps':>10} | {'Mean Reward':>12} | {'Mean Length':>12}")
print("-" * 40)

for i, ts in enumerate(data['timesteps']):
    mean_reward = np.mean(data['results'][i])
    mean_length = np.mean(data['ep_lengths'][i])
    print(f"{ts:>10,} | {mean_reward:>12.2f} | {mean_length:>12.1f}")

print(f"\nFinal (at 2M steps):")
print(f"  Mean reward: {np.mean(data['results'][-1]):.2f}")
print(f"  Mean episode length: {np.mean(data['ep_lengths'][-1]):.1f}")
