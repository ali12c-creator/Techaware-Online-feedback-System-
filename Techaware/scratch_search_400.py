with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== Lines containing 400 ===")
for i, line in enumerate(lines):
    if '400' in line:
        clean = line.encode('ascii', 'ignore').decode('ascii').strip()
        print(f"Line {i+1}: {clean}")
