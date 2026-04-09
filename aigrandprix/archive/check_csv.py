import csv
f = open(r'C:\Users\Wasch\clawd\projects\aigrandprix\rpg_time_optimal\example\gauntlet_result.csv')
r = csv.reader(f)
h = next(r)
print(f"Header cols: {len(h)}")
print(f"First 5: {h[:5]}")
print(f"'t' in header: {'t' in h}")

row = next(r)
print(f"\nRow1 cols: {len(row)}")
print(f"First 5 vals: {row[:5]}")

# Check for empty rows
f.seek(0)
next(r)  # skip header
empty = 0
short = 0
total = 0
for row in r:
    total += 1
    if len(row) == 0:
        empty += 1
    elif len(row) < 20:
        short += 1
        if short <= 3:
            print(f"Short row {total}: len={len(row)}, content={row[:5]}")
print(f"\nTotal rows: {total}, empty: {empty}, short (< 20 cols): {short}")
f.close()
