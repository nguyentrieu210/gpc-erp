"""Tạo HR test user + kiểm tra phân quyền Portal Module."""
import os, sys, json, urllib.request, http.cookiejar
from urllib.parse import urlencode

BASE = "http://localhost:8000"

# Helper
def api(endpoint, session_cj=None, data=None, method="POST"):
    cj = session_cj or http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    url = f"{BASE}{endpoint}"
    if data:
        req = urllib.request.Request(url, data=urlencode(data).encode(), method=method)
    else:
        req = urllib.request.Request(url, method=method)
    resp = opener.open(req)
    body = json.loads(resp.read())
    return cj, body

def get(endpoint, session_cj):
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(session_cj))
    resp = opener.open(f"{BASE}{endpoint}")
    return json.loads(resp.read())

# 1) Login as Administrator
cj_admin, r = api("/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
print("Admin login:", r["message"])

# 2) Create HR user via bench (using sudo login through API)
# Use frappe.client.insert
cj_admin2, r = api("/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
data = {
    "doc": json.dumps({
        "doctype": "User",
        "email": "test_hr@erp.local",
        "first_name": "Test",
        "last_name": "HR",
        "enabled": 1,
        "send_welcome_email": 0,
        "new_password": "test163",
        "roles": [
            {"role": "HR User"},
            {"role": "HR Manager"},
        ],
    }),
    "action": "Save",
}
cj_admin2, r = api("/api/method/frappe.desk.form.save.savedocs", session_cj=cj_admin2, data=data)
print("User saved:", r.get("message", r.get("docs", "?")), "| status:", type(r))

# 3) Login as HR user
cj_hr, r = api("/api/method/login", data={"usr": "test_hr@erp.local", "pwd": "test163"})
print("HR login:", r["message"])

# 4) Get modules as HR
result = get("/api/method/portal.api.get_my_modules", cj_hr)
modules = result.get("message", [])
print(f"\nHR user sees {len(modules)} modules:")
for m in modules:
    print(f"  {m['route_key']}: {m['module_name']} (role={m.get('required_role','')})")

# 5) Guest test
result = get("/api/method/portal.api.get_my_modules", http.cookiejar.CookieJar())
print(f"\nGuest sees {len(result.get('message', []))} modules -> should be 0")
