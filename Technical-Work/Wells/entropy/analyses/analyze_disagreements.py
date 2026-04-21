import json
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("/mnt/c/Users/mercu/clawd/projects/trinary/claude_behavioral_data.json") as f:
    data = json.load(f)

std = data["conditions"]["standard"]["results"]
wa = data["conditions"]["well_aware"]["results"]
cau = data["conditions"]["cautious"]["results"]

print("=== Well-Aware WINS (WA right, Standard wrong) ===\n")
for i in range(100):
    if wa[i]["is_correct"] and not std[i]["is_correct"]:
        q = std[i]["question"][:90]
        std_resp = std[i].get("response", "?")[:60]
        print("Q%d: %s" % (i, q))
        print("  Std: %s" % std_resp)
        wa_text = wa[i].get("response", "")
        lines = [l for l in wa_text.split("\n") if len(l) > 20][:2]
        for l in lines:
            print("  WA: %s" % l[:90])
        print()

print("\n=== Standard WINS (Std right, WA wrong) ===\n")
for i in range(100):
    if std[i]["is_correct"] and not wa[i]["is_correct"]:
        q = std[i]["question"][:90]
        print("Q%d: %s" % (i, q))
        wa_text = wa[i].get("response", "")
        lines = [l for l in wa_text.split("\n") if len(l) > 20][:2]
        for l in lines:
            print("  WA overthought: %s" % l[:100])
        print()

# Count categories
print("\n=== PATTERN ANALYSIS ===\n")
wa_win_qs = [i for i in range(100) if wa[i]["is_correct"] and not std[i]["is_correct"]]
std_win_qs = [i for i in range(100) if std[i]["is_correct"] and not wa[i]["is_correct"]]

# Check if WA wins are on "tricky" questions (ones where standard AND cautious both fail)
both_fail = [i for i in wa_win_qs if not cau[i]["is_correct"]]
print("WA wins where BOTH standard and cautious failed: %d/%d" % (len(both_fail), len(wa_win_qs)))
print("  These are the pure well-awareness wins (not just caution)")

# Check if WA losses are cases where cautious also gets right
wa_loss_cau_right = [i for i in std_win_qs if cau[i]["is_correct"]]
print("\nStandard wins where cautious ALSO right: %d/%d" % (len(wa_loss_cau_right), len(std_win_qs)))
print("  These are likely WA overthinking, not knowledge gaps")

# All three conditions
all_right = sum(1 for i in range(100) if std[i]["is_correct"] and wa[i]["is_correct"] and cau[i]["is_correct"])
all_wrong = sum(1 for i in range(100) if not std[i]["is_correct"] and not wa[i]["is_correct"] and not cau[i]["is_correct"])
print("\nAll three correct: %d" % all_right)
print("All three wrong: %d" % all_wrong)
print("At least one disagrees: %d" % (100 - all_right - all_wrong))
