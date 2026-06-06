import frappe

# Seed mặc định cho launcher. URL hiện ở chế độ DEV (path-based).
# Khi ráp sub-domain (Phase 6) sẽ đổi subdomain_url sang https://<sub>.abc.vn
DEFAULT_MODULES = [
	{
		"route_key": "quantri",
		"module_name": "Quản trị",
		"subdomain_url": "/quantri_app",
		"icon": "shield",
		"color": "#9333ea",
		"required_role": "System Manager",
		"sort_order": 5,
		"description": "Quản lý người dùng, vai trò, phân quyền phân hệ",
	},
	{
		"route_key": "hr",
		"module_name": "Nhân sự",
		"subdomain_url": "/hr_app",
		"icon": "users",
		"color": "#2563eb",
		"required_role": "HR User",
		"sort_order": 10,
		"description": "Hồ sơ nhân viên, chấm công, nghỉ phép, lương",
	},
	{
		"route_key": "crm",
		"module_name": "CRM",
		"subdomain_url": "/crm_app",
		"icon": "user-plus",
		"color": "#7c3aed",
		"required_role": "Sales User",
		"sort_order": 20,
		"description": "Lead, cơ hội, khách hàng",
	},
	{
		"route_key": "tckt",
		"module_name": "Tài chính kế toán",
		"subdomain_url": "/tckt_app",
		"icon": "dollar-sign",
		"color": "#059669",
		"required_role": "Accounts User",
		"sort_order": 30,
		"description": "Sổ cái, phiếu kế toán, công nợ, hóa đơn",
	},
	{
		"route_key": "kho",
		"module_name": "Kho",
		"subdomain_url": "/kho_app",
		"icon": "package",
		"color": "#ea580c",
		"required_role": "Stock User",
		"sort_order": 40,
		"description": "Hàng hóa, kho, nhập xuất tồn",
	},
	{
		"route_key": "kinhdoanh",
		"module_name": "Kinh doanh",
		"subdomain_url": "/kinhdoanh_app",
		"icon": "trending-up",
		"color": "#dc2626",
		"required_role": "Sales User",
		"sort_order": 50,
		"description": "Báo giá, đơn bán, hóa đơn bán",
	},
	{
		"route_key": "duan",
		"module_name": "Dự án",
		"subdomain_url": "/duan_app",
		"icon": "folder",
		"color": "#0891b2",
		"required_role": "Projects User",
		"sort_order": 60,
		"description": "Dự án, công việc, timesheet",
	},
	{
		"route_key": "muahang",
		"module_name": "Mua hàng",
		"subdomain_url": "/muahang_app",
		"icon": "shopping-cart",
		"color": "#f59e0b",
		"required_role": "Purchase User",
		"sort_order": 35,
		"description": "Nhà cung cấp, yêu cầu mua, đơn mua, báo giá",
	},
]


def setup_portal(*args, **kwargs):
	"""Seed Portal Module mặc định (idempotent). Gọi từ after_install + after_migrate."""
	if not frappe.db.table_exists("Portal Module"):
		return

	for m in DEFAULT_MODULES:
		if frappe.db.exists("Portal Module", m["route_key"]):
			continue

		data = dict(m)
		# Bỏ required_role nếu Role chưa tồn tại (tránh lỗi link)
		role = data.get("required_role")
		if role and not frappe.db.exists("Role", role):
			data["required_role"] = None

		frappe.get_doc({"doctype": "Portal Module", **data}).insert(ignore_permissions=True)

	frappe.db.commit()
