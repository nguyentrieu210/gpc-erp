import os
import re

apps_dir = "/home/frappe/frappe-bench/apps"
home_files = []
for root, dirs, files in os.walk(apps_dir):
    # Skip node_modules to be fast
    if "node_modules" in dirs:
        dirs.remove("node_modules")
    for file in files:
        if file == "Home.vue":
            home_files.append(os.path.join(root, file))

for path in sorted(home_files):
    print("=" * 80)
    print("FILE:", path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print("ERROR READING:", e)
        continue
    
    # Extract template header
    header_match = re.search(r"<header.*?</header>", content, re.DOTALL)
    if header_match:
        print("HEADER:")
        print(header_match.group(0))
    else:
        print("NO HEADER FOUND")
        
    # Extract script setup
    script_match = re.search(r"<script setup.*?</script>", content, re.DOTALL)
    if script_match:
        print("SCRIPT SETUP (First 20 lines):")
        lines = script_match.group(0).splitlines()
        print("\n".join(lines[:20]))
    else:
        print("NO SCRIPT SETUP FOUND")
