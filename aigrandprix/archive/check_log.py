import os

log_path = r"C:\Users\mercu\clawd\projects\aigrandprix\rl\runs\train_log.txt"

if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    print(f"Total lines: {len(lines)}")
    print("\nLast 40 lines:")
    for line in lines[-40:]:
        print(line.rstrip())
else:
    print(f"File not found: {log_path}")
