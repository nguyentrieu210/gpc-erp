"""Tạo HR test user + kiểm tra phân quyền (gọi từ bench execute)."""
import frappe


def create_user():
    try:
        u = frappe.get_doc("User", "test_hr@erp.local")
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
    print("User:", u.name, "Roles:", [r.role for r in u.roles])
    frappe.db.commit()


def check_modules():
    roles = set(frappe.get_roles("test_hr@erp.local"))
    modules = frappe.get_all(
        "Portal Module",
        filters={"enabled": 1},
        fields=["route_key", "module_name", "required_role"],
        order_by="sort_order asc",
        ignore_permissions=True,
    )
    visible = [
        m for m in modules
        if not m.required_role or m.required_role in roles
    ]
    print(f"HR user sees {len(visible)}/{len(modules)} modules:")
    for m in visible:
        print(f"  {m.route_key}: {m.module_name}")
    # Assert only hr
    assert len(visible) == 1, f"Expected 1 module, got {len(visible)}"
    assert visible[0].route_key == "hr", f"Expected hr, got {visible[0].route_key}"
    print("PERMISSION TEST PASSED")
