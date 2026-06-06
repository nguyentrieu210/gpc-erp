"""API Quản trị — quản lý User, Role, Phân quyền module."""
import frappe
from frappe.core.doctype.user.user import User


@frappe.whitelist()
def get_csrf_token():
	return frappe.sessions.get_csrf_token()


# ── Users ──────────────────────────────────────────────

@frappe.whitelist()
def get_users(search="", page=1, page_length=20):
	"""Danh sách user (có role)."""
	filters = {}
	if search:
		from frappe import db
		filters["name"] = ["like", f"%{search}%"]

	users = frappe.get_all(
		"User",
		filters=filters,
		fields=[
			"name", "full_name", "email", "enabled", "user_type",
			"creation", "last_login",
		],
		order_by="creation desc",
		limit_page_length=page_length,
		start=(page - 1) * page_length,
	)

	# Gắn roles cho từng user
	for u in users:
		roles = frappe.get_all(
			"Has Role",
			filters={"parent": u["name"], "parenttype": "User"},
			fields=["role"],
		)
		u["roles"] = [r["role"] for r in roles]
		u["role_count"] = len(u["roles"])

	return users


@frappe.whitelist()
def get_user_detail(user):
	"""Chi tiết 1 user + roles."""
	doc = frappe.get_doc("User", user)
	roles = [{"role": r.role} for r in doc.roles]
	return {
		"name": doc.name,
		"full_name": doc.full_name,
		"first_name": doc.first_name,
		"last_name": doc.last_name,
		"email": doc.email,
		"enabled": doc.enabled,
		"user_type": doc.user_type,
		"mobile_no": doc.mobile_no,
		"location": doc.location,
		"birth_date": str(doc.birth_date) if doc.birth_date else None,
		"gender": doc.gender,
		"roles": roles,
		"creation": str(doc.creation),
		"last_login": str(doc.last_login) if doc.last_login else None,
	}


@frappe.whitelist()
def create_user(email, first_name, last_name="", roles=None, password=None,
                send_welcome_email=False):
	"""Tạo user mới + gán role. Chỉ System Manager mới gọi được."""
	if not frappe.has_permission("User", "create"):
		frappe.throw("Bạn không có quyền tạo user.", frappe.PermissionError)

	doc = frappe.get_doc({
		"doctype": "User",
		"email": email,
		"first_name": first_name,
		"last_name": last_name,
		"enabled": 1,
		"send_welcome_email": 0,
	})

	if roles:
		if isinstance(roles, str):
			import json
			roles = json.loads(roles)
		for role in roles:
			doc.append("roles", {"role": role})

	doc.insert()

	if send_welcome_email:
		doc.send_welcome_email()

	return {"name": doc.name, "message": f"Đã tạo user {doc.name}"}


@frappe.whitelist()
def update_user(user, first_name=None, last_name=None, email=None,
                roles=None, enabled=None):
	"""Cập nhật user + role."""
	if not frappe.has_permission("User", "write"):
		frappe.throw("Bạn không có quyền sửa user.", frappe.PermissionError)

	doc = frappe.get_doc("User", user)

	if first_name is not None:
		doc.first_name = first_name
	if last_name is not None:
		doc.last_name = last_name
	if email is not None:
		doc.email = email
	if enabled is not None:
		doc.enabled = 1 if enabled else 0

	if roles is not None:
		if isinstance(roles, str):
			import json
			roles = json.loads(roles)
		doc.roles = []
		for role in roles:
			doc.append("roles", {"role": role})

	doc.save()
	return {"name": doc.name, "message": f"Đã cập nhật user {doc.name}"}


@frappe.whitelist()
def disable_user(user):
	"""Vô hiệu hóa user (không xóa)."""
	if not frappe.has_permission("User", "write"):
		frappe.throw("Bạn không có quyền.", frappe.PermissionError)
	doc = frappe.get_doc("User", user)
	doc.enabled = 0
	doc.save()
	return {"name": doc.name, "message": f"Đã vô hiệu hóa user {doc.name}"}


# ── Roles ──────────────────────────────────────────────

@frappe.whitelist()
def get_roles(search=""):
	"""Danh sách tất cả role."""
	filters = {}
	if search:
		filters["name"] = ["like", f"%{search}%"]
	roles = frappe.get_all(
		"Role",
		filters=filters,
		fields=["name", "desk_access", "disabled"],
		order_by="name asc",
	)

	# Đếm số user mỗi role
	for r in roles:
		count = frappe.db.count(
			"Has Role",
			filters={"role": r["name"], "parenttype": "User"},
		)
		r["user_count"] = count

	return roles


@frappe.whitelist()
def get_role_detail(role):
	"""Chi tiết role + danh sách user trong role."""
	doc = frappe.get_doc("Role", role)
	users = frappe.get_all(
		"Has Role",
		filters={"role": role, "parenttype": "User"},
		fields=["parent"],
		pluck="parent",
	)
	return {
		"name": doc.name,
		"desk_access": doc.desk_access,
		"disabled": doc.disabled,
		"users": users,
		"user_count": len(users),
	}


# ── Phân quyền Module ──────────────────────────────────

@frappe.whitelist()
def get_module_permissions(user=None):
	"""Trả về danh sách Portal Module + trạng thái user có được phép không.
	Nếu không truyền user → trả về tất cả module (cho admin cấu hình).
	"""
	modules = frappe.get_all(
		"Portal Module",
		fields=["name", "module_name", "route_key", "icon", "color",
		        "sort_order", "enabled", "required_role", "description"],
		order_by="sort_order asc",
	)

	if not user:
		return modules

	user_roles = frappe.get_roles(user)

	for m in modules:
		required = m.get("required_role")
		m["user_has_access"] = (
			not required or
			"System Manager" in user_roles or
			required in user_roles
		)

	return modules


@frappe.whitelist()
def get_user_modules(user):
	"""Trả về module mà user được phép truy cập (gọi từ portal)."""
	user_roles = frappe.get_roles(user)
	modules = frappe.get_all(
		"Portal Module",
		filters={"enabled": 1},
		fields=["module_name", "route_key", "icon", "color",
		        "sort_order", "required_role", "description"],
		order_by="sort_order asc",
	)

	result = []
	for m in modules:
		required = m.get("required_role")
		if ("System Manager" in user_roles or
		    not required or
		    required in user_roles):
			result.append(m)

	return result


# ── Dashboard ──────────────────────────────────────────

@frappe.whitelist()
def get_dashboard():
	"""Số liệu tổng quan cho dashboard Quản trị."""
	return {
		"total_users": frappe.db.count("User"),
		"active_users": frappe.db.count("User", {"enabled": 1}),
		"disabled_users": frappe.db.count("User", {"enabled": 0}),
		"total_roles": frappe.db.count("Role"),
		"active_roles": frappe.db.count("Role", {"disabled": 0}),
		"total_modules": frappe.db.count("Portal Module"),
		"active_modules": frappe.db.count("Portal Module", {"enabled": 1}),
	}
