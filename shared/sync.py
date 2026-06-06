import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "shared", "ui")
APPS = ["portal", "hr", "crm_ui", "tckt", "kho", "kinhdoanh", "quantri", "muahang", "duan", "taisan"]

print(f"Root: {ROOT}")
print(f"Source: {SRC}")

for app in APPS:
    dest = os.path.join(ROOT, "apps", app, "frontend", "src", "_shared")
    if not os.path.exists(os.path.join(ROOT, "apps", app, "frontend")):
        continue
    
    if os.path.exists(dest):
        shutil.rmtree(dest)
    
    shutil.copytree(SRC, dest)
    print(f"Synced -> {dest}")

print("DONE")
