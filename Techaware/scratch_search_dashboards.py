def search_file(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'sentiment' in line or 'UNDERSTOOD' in line:
            print(f"Line {i+1}: {line.strip()}")

search_file('templates/dashboard.html')
search_file('templates/teacher_dashboard.html')
search_file('templates/student_dashboard.html')
search_file('templates/admin_manage.html')
