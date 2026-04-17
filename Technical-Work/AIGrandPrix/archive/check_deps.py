import sys
sys.path.insert(0, r"C:\Users\mercu\clawd\projects\aigrandprix\sim")
sys.path.insert(0, r"C:\Users\mercu\clawd\projects\aigrandprix\rl")

# Check what's available
try:
    import gymnasium
    print(f"gymnasium: {gymnasium.__version__}")
except Exception as e:
    print(f"gymnasium missing: {e}")

try:
    import torch
    print(f"torch: {torch.__version__}")
except Exception as e:
    print(f"torch missing: {e}")
    
try:
    import stable_baselines3
    print(f"stable_baselines3: available")
except Exception as e:
    print(f"stable_baselines3 missing: {e}")
