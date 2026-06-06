import os

frappe_dir = "/home/frappe/frappe-bench/apps/frappe"
for root, dirs, files in os.walk(frappe_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "def logout" in content:
                        print("Found in file:", path)
                        for line in content.splitlines():
                            if "def logout" in line or "@frappe.whitelist" in line:
                                print("  ", line)
            except Exception as e:
                pass
