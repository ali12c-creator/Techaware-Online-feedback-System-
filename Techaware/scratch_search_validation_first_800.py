with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== weekday/time validation occurrences (Lines 1 to 800) ===")
for i, line in enumerate(lines[:800]):
    if 'weekday' in line or 'time' in line or 'expires' in line:
        clean_line = line.encode('ascii', 'ignore').decode('ascii').strip()
        print(f"Line {i+1}: {clean_line}")
