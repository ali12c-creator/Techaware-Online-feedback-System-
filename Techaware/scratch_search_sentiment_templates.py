import os

templates_dir = 'templates'
for filename in os.listdir(templates_dir):
    if filename.endswith('.html'):
        path = os.path.join(templates_dir, filename)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if 'sentiment' in content:
            print(f"=== {filename} ===")
            for line in content.split('\n'):
                if 'sentiment' in line:
                    print(line.strip())
