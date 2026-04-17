import yaml
with open('rpg_time_optimal/tracks/gauntlet.yaml') as f:
    data = yaml.safe_load(f)
gates = data['gates']
for i in range(20, 30):
    g = gates[i]
    pos = g["position"]
    print(f"Gate {i}: pos={pos}")

# Check bounds
print("\nBounds config in env:")
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve() / 'sim'))
from drone_env_v2 import DroneRacingEnvV2
print(f"Default bounds: check source")
