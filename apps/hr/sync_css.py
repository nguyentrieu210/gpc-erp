import os
import shutil

# Change working directory to apps/ (one level above this script)
script_dir = os.path.dirname(os.path.abspath(__file__))
apps_dir = os.path.dirname(script_dir)
os.chdir(apps_dir)

src_path = os.path.join("hr", "frontend", "src", "index.css")

submodules = [
    "crm_ui",
    "duan",
    "kho",
    "kinhdoanh",
    "muahang",
    "portal",
    "quantri",
    "tckt"
]

print(f"Source file: {os.path.abspath(src_path)}")
if not os.path.exists(src_path):
    print("Error: Source file not found!")
    exit(1)

count = 0
for sub in submodules:
    dst_dir = os.path.join(sub, "frontend", "src")
    dst_path = os.path.join(dst_dir, "index.css")
    if os.path.exists(dst_dir):
        shutil.copy2(src_path, dst_path)
        print(f"Copied to: {os.path.abspath(dst_path)}")
        count += 1
    else:
        print(f"Directory not found (skipping): {os.path.abspath(dst_dir)}")

print(f"Successfully copied to {count} modules.")
