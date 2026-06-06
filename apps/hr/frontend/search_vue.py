recruitment_path = "/home/frappe/frappe-bench/apps/hr/frontend/src/pages/Recruitment.vue"

with open(recruitment_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "get_applicants_filtered" in line or "get_job_applicants" in line:
        print(f"L{idx+1}: {line.strip()[:140]}")
