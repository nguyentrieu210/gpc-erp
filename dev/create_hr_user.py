"""Create HR test user and verify Portal Module permission filtering."""
import frappe, os, json

os.chdir("/home/frappe/frappe-bench")
sites_path = os.path.join(os.getcwd(), "sites")
frappe.init(site="erp.local", sites_path=sites_path)

# Need to set up proper log path before connect
os.makedirs("/home/frappe/logs", exist_ok=True)

frappe.connect()

try:
    u = frappe.get_doc("User", "test_hr@erp.local")
    print("User exists, updating...")
except frappe.DoesNotExistError:
    u = frappe.get_doc({
        "doctype": "User",
        "email": "test_hr@erp.local",
        "first_name": "Test",
        "last_name": "HR",
        "send_welcome_email": 0,
        "enabled": 1,
        "new_password": "Gpc2026Test",
        "roles": [
            {"role": "HR User"},
            {"role": "HR Manager"},
        ],
    })
    u.insert(ignore_permissions=True)

print("User:", u.name)
print("Roles:", [r.role for r in u.roles])

# Test permission
user_roles = frappe.get_roles("test_hr@erp.local")
print("Resolved roles:", [r for r in user_roles if r != "All"][:5])

modules = frappe.get_all(
    "Portal Module",
    filters={"enabled": 1},
    fields=["route_key", "module_name", "required_role"],
    order_by="sort_order asc",
    ignore_permissions=True,
)

visible = [
    m for m in modules
    if not m.required_role or m.required_role in user_roles
]
print(f"\nHR user sees {len(visible)}/{len(modules)} modules:")
for m in visible:
    print(f"  {m.route_key}: {m.module_name}")

frappe.destroy()
