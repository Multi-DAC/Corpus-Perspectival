import numpy as np

eval_path = r"C:\Users\mercu\clawd\projects\aigrandprix\rl\runs\gauntlet_1770766522\eval_logs\evaluations.npz"

data = np.load(eval_path)
print("Keys:", list(data.keys()))

# Print the results
for key in data.keys():
    arr = data[key]
    print(f"\n{key}: shape={arr.shape}")
    if len(arr.shape) == 1:
        print(f"  Values: {arr}")
    else:
        print(f"  First few: {arr[0] if len(arr) > 0 else 'empty'}")
