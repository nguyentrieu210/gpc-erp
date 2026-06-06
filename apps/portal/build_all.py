import os
import subprocess

apps = ["portal", "kho", "hr", "crm_ui", "duan", "kinhdoanh", "muahang", "quantri", "tckt"]
bench_dir = "/home/frappe/frappe-bench"

for app in apps:
    frontend_dir = f"{bench_dir}/apps/{app}/frontend"
    if not os.path.exists(frontend_dir):
        print(f"Skipping {app}: frontend dir does not exist.")
        continue
    
    print("=" * 80)
    print(f"Building frontend for app: {app}")
    print(f"Directory: {frontend_dir}")
    
    # Check if yarn or npm is available and run build
    try:
        # We check yarn first
        print("Running yarn build...")
        res = subprocess.run("yarn build", shell=True, cwd=frontend_dir, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"Success building {app}!")
            print(res.stdout[-500:])  # print last 500 chars of success output
        else:
            print(f"Yarn build failed for {app}. Error:")
            print(res.stderr)
            print("Trying npm run build...")
            res_npm = subprocess.run("npm run build", shell=True, cwd=frontend_dir, capture_output=True, text=True)
            if res_npm.returncode == 0:
                print(f"Success building {app} with npm!")
            else:
                print(f"Npm run build also failed for {app}. Error:")
                print(res_npm.stderr)
    except Exception as e:
        print(f"Exception building {app}: {e}")

print("All builds finished!")
