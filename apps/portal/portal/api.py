import frappe
import json as _json
from frappe.utils import flt, cint, getdate, today, nowdate, add_to_date


# ---------------------------------------------------------------------------
# Module access
# ---------------------------------------------------------------------------

DEFAULT_MODULES = [
    {"module_name": "Quan tri", "route_key": "quantri", "subdomain_url": "/quantri_app", "icon": "settings", "color": "#4b5563", "description": "QL nguoi dung & phan quyen", "required_role": "System Manager", "sort_order": 5},
    {"module_name": "Nhan su", "route_key": "hr", "subdomain_url": "/hr_app", "icon": "users", "color": "#6366f1", "description": "QL nhan su, luong, tuyen dung", "required_role": "HR User", "sort_order": 10},
    {"module_name": "CRM", "route_key": "crm_ui", "subdomain_url": "/crm_app", "icon": "user-plus", "color": "#8b5cf6", "description": "QL khach hang, lead, co hoi", "required_role": "Sales User", "sort_order": 20},
    {"module_name": "Tai chinh", "route_key": "tckt", "subdomain_url": "/tckt_app", "icon": "dollar-sign", "color": "#10b981", "description": "So cai, bao cao TC, thue", "required_role": "Accounts User", "sort_order": 30},
    {"module_name": "Mua hang", "route_key": "muahang", "subdomain_url": "/muahang_app", "icon": "shopping-cart", "color": "#0ea5e9", "description": "Don mua, nhap hang, cong no", "required_role": "Purchase User", "sort_order": 35},
    {"module_name": "Kho", "route_key": "kho", "subdomain_url": "/kho_app", "icon": "package", "color": "#f97316", "description": "QL hang hoa, nhap xuat ton", "required_role": "Stock User", "sort_order": 40},
    {"module_name": "Kinh doanh", "route_key": "kinhdoanh", "subdomain_url": "/kinhdoanh_app", "icon": "trending-up", "color": "#e11d48", "description": "Bao gia, don ban, xuat giao", "required_role": "Sales User", "sort_order": 50},
    {"module_name": "Du an", "route_key": "duan", "subdomain_url": "/duan_app", "icon": "briefcase", "color": "#f59e0b", "description": "QL du an & cong viec", "required_role": "Projects User", "sort_order": 60},
]


@frappe.whitelist()
def get_my_modules():
    """Tra ve cac phan he (Portal Module) ma user hien tai duoc phep truy cap."""
    user = frappe.session.user
    if not user or user == "Guest":
        return []

    roles = set(frappe.get_roles(user))
    is_admin = "System Manager" in roles

    modules = DEFAULT_MODULES  # fallback — always works
    try:
        records = frappe.get_all(
            "Portal Module",
            filters={"enabled": 1},
            fields=["module_name", "route_key", "subdomain_url", "icon", "color",
                    "description", "required_role", "sort_order"],
            order_by="sort_order asc, module_name asc",
            ignore_permissions=True,
        )
        if records:
            modules = records
    except Exception:
        pass  # table doesn't exist yet — use defaults

    return [m for m in modules if is_admin or not m.get("required_role") or m["required_role"] in roles]


@frappe.whitelist()
def get_current_user():
    user = frappe.session.user
    if not user or user == "Guest":
        return {"user": None}
    full_name = frappe.db.get_value("User", user, "full_name") or user
    return {"user": user, "full_name": full_name, "roles": frappe.get_roles(user)}


# ---------------------------------------------------------------------------
# A1 — Unified Dashboard (Portal Home)
# ---------------------------------------------------------------------------

def _quick_count(doctype, filters=None):
    try: return frappe.db.count(doctype, filters or {})
    except: return 0


def _quick_sum(doctype, field, filters=None):
    try:
        s = 0.0
        for r in frappe.get_all(doctype, filters or {}, [field], limit_page_length=0):
            s += flt(r.get(field))
        return s
    except: return 0.0


@frappe.whitelist()
def get_unified_dashboard():
    """KPI tổng từ tất cả module cho Portal Home."""
    company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    fd = getdate(today()).replace(day=1)

    # Kho
    stock_value = 0.0
    stock_items = 0
    try:
        for b in frappe.get_all("Bin", fields=["stock_value", "item_code"], limit_page_length=0):
            stock_value += flt(b.stock_value)
            stock_items += 1
    except: pass

    low_stock = 0
    try:
        reorders = frappe.get_all("Item Reorder", fields=["parent", "warehouse", "warehouse_reorder_level"])
        for r in reorders:
            proj = flt(frappe.db.get_value("Bin", {"item_code": r.parent, "warehouse": r.warehouse}, "projected_qty") or 0)
            if proj < flt(r.warehouse_reorder_level): low_stock += 1
    except: pass

    # Kinh doanh
    receivables = 0.0
    try:
        for si in frappe.get_all("Sales Invoice", {"docstatus": 1}, ["outstanding_amount"], limit_page_length=0):
            receivables += flt(si.outstanding_amount)
    except: pass
    so_month = 0.0
    try:
        for so in frappe.get_all("Sales Order", {"docstatus": 1, "transaction_date": [">=", fd]}, ["grand_total"], limit_page_length=0):
            so_month += flt(so.grand_total)
    except: pass
    revenue_mtd = 0.0
    try:
        for gl in frappe.get_all("GL Entry", {"is_cancelled": 0, "account": ["like", "511%"], "posting_date": [">=", fd]}, ["credit"], limit_page_length=0):
            revenue_mtd += flt(gl.credit)
    except: pass

    # Mua hàng
    payables = 0.0
    try:
        for pi in frappe.get_all("Purchase Invoice", {"docstatus": 1}, ["outstanding_amount"], limit_page_length=0):
            payables += flt(pi.outstanding_amount)
    except: pass
    po_month = 0.0
    try:
        for po in frappe.get_all("Purchase Order", {"docstatus": 1, "transaction_date": [">=", fd]}, ["grand_total"], limit_page_length=0):
            po_month += flt(po.grand_total)
    except: pass

    # HR
    emp_total = _quick_count("Employee", {"status": "Active"})
    emp_present = 0
    try:
        emp_present = frappe.db.count("Attendance", {"attendance_date": str(today()), "status": "Present"})
    except: pass
    on_leave = 0
    try:
        on_leave = frappe.db.count("Leave Application", {"status": "Approved", "from_date": ["<=", today()], "to_date": [">=", today()]})
    except: pass

    # CRM
    leads_open = _quick_count("Lead", {"status": ["in", ["Lead", "Open"]]})
    opps_open = _quick_count("Opportunity", {"status": ["not in", ["Closed Won", "Closed Lost"]]})

    # Tài chính
    je_count = _quick_count("Journal Entry")
    gl_count = _quick_count("GL Entry", {"is_cancelled": 0})

    # Recent activity (last 20 transactions across modules)
    recent = []
    for dt, fields, date_f, extra_filters in [
        ("Sales Order", ["name", "customer_name", "grand_total", "transaction_date", "docstatus"], "transaction_date", {"docstatus": 1}),
        ("Purchase Order", ["name", "supplier_name", "grand_total", "transaction_date", "docstatus"], "transaction_date", {"docstatus": 1}),
        ("Stock Entry", ["name", "stock_entry_type", "total_amount", "posting_date", "docstatus"], "posting_date", {"docstatus": 1}),
        ("Journal Entry", ["name", "total_debit", "user_remark", "posting_date", "docstatus"], "posting_date", {"docstatus": 1}),
        ("Sales Invoice", ["name", "customer_name", "grand_total", "posting_date", "docstatus"], "posting_date", {"docstatus": 1}),
        ("Purchase Invoice", ["name", "supplier_name", "grand_total", "posting_date", "docstatus"], "posting_date", {"docstatus": 1}),
        ("Lead", ["name", "lead_name", "status", "creation"], "creation", {}),
    ]:
        try:
            for r in frappe.get_all(dt, filters=extra_filters, fields=fields, order_by=f"{date_f} desc", limit_page_length=3):
                r["_doctype"] = dt
                recent.append(r)
        except: pass
    recent.sort(key=lambda r: str(r.get("transaction_date") or r.get("creation") or r.get("posting_date") or ""), reverse=True)
    recent = recent[:12]

    return {
        "stock": {"value": stock_value, "items": stock_items, "low": low_stock},
        "sales": {"receivables": receivables, "so_month": so_month / 1e6, "revenue_mtd": revenue_mtd},
        "purchasing": {"payables": payables, "po_month": po_month / 1e6},
        "hr": {"employees": emp_total, "present": emp_present, "on_leave": on_leave},
        "crm": {"leads_open": leads_open, "opps_open": opps_open},
        "finance": {"je_count": je_count, "gl_count": gl_count},
        "recent": recent,
        "company": company,
    }


# ---------------------------------------------------------------------------
# A2 — Global Search (AwesomeBar ERPNext-style)
# ---------------------------------------------------------------------------

SEARCH_DOCTYPES = [
    ("Item", "kho_app", "/items/{}", ["item_code", "item_name"], "item_name"),
    ("Supplier", "muahang_app", "/suppliers/{}", ["supplier_name", "name"], "supplier_name"),
    ("Customer", "kinhdoanh_app", "/customers/{}", ["customer_name", "name"], "customer_name"),
    ("Lead", "crm_app", "/leads", ["lead_name", "email_id", "mobile_no"], "lead_name"),
    ("Opportunity", "crm_app", "/opportunities", ["title", "party_name"], "title"),
    ("Employee", "hr_app", "/employees/{}", ["employee_name", "name"], "employee_name"),
    ("Purchase Order", "muahang_app", "/po/{}", ["name", "supplier_name"], "name"),
    ("Sales Order", "kinhdoanh_app", "/sales-orders", ["name", "customer_name"], "name"),
    ("Stock Entry", "kho_app", "/stock-entries", ["name", "stock_entry_type"], "name"),
    ("Journal Entry", "tckt_app", "/journal-entries", ["name", "user_remark"], "name"),
    ("Sales Invoice", "kinhdoanh_app", "/sales-invoices", ["name", "customer_name"], "name"),
    ("Purchase Invoice", "muahang_app", "/purchase-invoices", ["name", "supplier_name"], "name"),
    ("Material Request", "kho_app", "/material-requests", ["name", "material_request_type"], "name"),
]

DOCTYPE_LABELS_VI = {
    "Item": "Hàng hóa", "Supplier": "Nhà cung cấp", "Customer": "Khách hàng",
    "Lead": "Lead", "Opportunity": "Cơ hội", "Employee": "Nhân viên",
    "Purchase Order": "Đơn mua", "Sales Order": "Đơn bán", "Stock Entry": "Phiếu kho",
    "Journal Entry": "Phiếu kế toán", "Sales Invoice": "Hóa đơn bán",
    "Purchase Invoice": "Hóa đơn mua", "Material Request": "Yêu cầu vật tư",
}


@frappe.whitelist()
def global_search(q=""):
    """Tìm kiếm toàn cục trên nhiều doctype."""
    q = (q or "").strip()
    if len(q) < 2:
        return {"results": [], "total": 0}
    results = []
    seen = set()
    for dt, app, route_template, search_fields, display_field in SEARCH_DOCTYPES:
        or_filters = [[f, "like", f"%{q}%"] for f in search_fields]
        try:
            rows = frappe.get_all(dt, filters={"name": ["not in", []]}, or_filters=or_filters,
                                  fields=["name"] + list(search_fields), limit_page_length=5)
        except Exception:
            continue
        for r in rows:
            key = f"{dt}:{r.name}"
            if key not in seen:
                seen.add(key)
                results.append({
                    "doctype": dt,
                    "label_vi": DOCTYPE_LABELS_VI.get(dt, dt),
                    "name": r.name,
                    "display": (r.get(display_field) or r.name),
                    "detail": _search_detail(r, search_fields),
                    "app": app,
                    "url": _search_url(dt, r.name, route_template, app),
                })
    results.sort(key=lambda x: x["doctype"])
    return {"results": results, "total": len(results), "q": q}


def _search_url(dt, name, template, app):
    if "{}" in template:
        return f"/{app}{template.format(name)}"
    return f"/{app}{template}"


def _search_detail(row, fields):
    extras = []
    for f in fields:
        if f != "name" and row.get(f):
            extras.append(str(row[f]))
    return " · ".join(extras[:2])


@frappe.whitelist(allow_guest=True)
def portal_logout():
    frappe.local.login_manager.logout()
    frappe.db.commit()
    return {"status": "success"}



