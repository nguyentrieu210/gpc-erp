import os
import re

apps_dir = "/home/frappe/frappe-bench/apps"

files_to_clean = []
for root, dirs, files in os.walk(apps_dir):
    if "node_modules" in dirs:
        dirs.remove("node_modules")
    for file in files:
        if file in ("Home.vue", "Launcher.vue", "Items.vue", "StockReconciliation.vue", "MaterialRequests.vue"):
            files_to_clean.append(os.path.join(root, file))

def clean_imports(content):
    # Clean frappe-ui imports
    frappe_pattern = r"import\s*\{\s*([^}]+)\s*\}\s*from\s*['\"]frappe-ui['\"]"
    def replace_frappe(match):
        names = match.group(1).replace("\n", " ").split(",")
        cleaned_names = []
        seen = set()
        for name in names:
            name = name.strip()
            if name and name not in seen:
                seen.add(name)
                cleaned_names.append(name)
        return "import { " + ", ".join(cleaned_names) + " } from 'frappe-ui'"
    
    content = re.sub(frappe_pattern, replace_frappe, content)

    # Clean vue imports
    vue_pattern = r"import\s*\{\s*([^}]+)\s*\}\s*from\s*['\"]vue['\"]"
    def replace_vue(match):
        names = match.group(1).replace("\n", " ").split(",")
        cleaned_names = []
        seen = set()
        for name in names:
            name = name.strip()
            if name and name not in seen:
                seen.add(name)
                cleaned_names.append(name)
        return "import { " + ", ".join(cleaned_names) + " } from 'vue'"
    
    content = re.sub(vue_pattern, replace_vue, content)
    return content

for path in files_to_clean:
    print("Cleaning imports for:", path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        cleaned = clean_imports(content)
        if cleaned != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print("  Cleaned successfully.")
        else:
            print("  No changes needed.")
    except Exception as e:
        print("Error cleaning:", path, e)

print("Clean completed!")
