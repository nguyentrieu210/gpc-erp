import os
import re

def run():
    apps_dir = "/home/frappe/frappe-bench/apps"
    for root, dirs, files in os.walk(apps_dir):
        for file in files:
            if file == "Home.vue" and "frontend/src/pages" in root:
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    header_match = re.search(r"<header.*?</header>", content, re.DOTALL)
                    if header_match:
                        print(f"File: {path}")
                        print(header_match.group(0))
                        print("-" * 50)
                except Exception as e:
                    print(f"Error {path}: {e}")
