import json
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("C:/Users/mercu/clawd/projects/trinary/wells_confound_data.json") as f:
    data = json.load(f)

# Condition C - where the hallucination lives
results = data["C_unfamiliar_factual"]["results"]
wells = data["C_unfamiliar_factual"]["wells"]
text = data["C_unfamiliar_factual"]["full_text"]

print("CONDITION C (Unfamiliar Factual) — Mpemba Effect")
print("=" * 85)
print(f"Full text:\n{text}\n")
print("=" * 85)

print(f"\nWells (local entropy maxima): positions {wells}\n")

print(f"{'Pos':>4} {'Token':>18} {'H':>6} {'Ghosts':>6}  {'Top alternatives'}")
print("-" * 85)
for r in results:
    tok = r["token"].replace("\n", "\\n")
    alts = ", ".join(r["top_5_tokens"][:5])
    marker = " <<< WELL" if r["position"] in wells else ""
    high = " *** HIGH" if r["entropy"] > 3.0 else ""
    print(f'{r["position"]:4d} {tok:>18} {r["entropy"]:6.2f} {r["ghost_count"]:6d}  {alts}{marker}{high}')

# Also check Condition D
print("\n\n")
results_d = data["D_unfamiliar_selfref"]["results"]
text_d = data["D_unfamiliar_selfref"]["full_text"]
print("CONDITION D (Unfamiliar Self-Ref) — Mpemba Effect")
print("=" * 85)
print(f"Full text:\n{text_d}\n")
