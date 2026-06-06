"""GPC SHARED — helper backend dùng chung (canonical).

Gom các helper trùng lặp giữa các app (company/abbr/account/cash/money/log/date).
Mỗi app import:  from gpc_common import company, abbr, money, vn_date, log_doc
(shared/py được thêm vào sys.path qua apps/<app>/<app>/__init__.py — xem ghi chú cuối file.)

Tất cả hàm idempotent/đọc — KHÔNG tạo doctype mới.
"""
import frappe
from frappe.utils import getdate, nowdate


def company():
    """Công ty mặc định (GPC)."""
    c = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
    if not c:
        c = frappe.db.get_value("Company", {}, "name")
    return c


def abbr(comp=None):
    return frappe.db.get_value("Company", comp or company(), "abbr")


def account(number_or_name, comp=None):
    """Tìm Account theo số hiệu (account_number) hoặc tên, trong company."""
    comp = comp or company()
    acc = frappe.db.get_value("Account", {"account_number": str(number_or_name), "company": comp, "is_group": 0}, "name")
    if acc:
        return acc
    return frappe.db.get_value("Account", {"name": ["like", f"%{number_or_name}%"], "company": comp, "is_group": 0}, "name")


def cash_account(comp=None):
    """Tài khoản tiền (ưu tiên 1111/111 theo TT200), fallback bất kỳ Cash/Bank."""
    comp = comp or company()
    for num in ("1111", "111", "1121", "112"):
        a = account(num, comp)
        if a:
            return a
    return frappe.db.get_value("Account", {"account_type": ["in", ["Cash", "Bank"]], "company": comp, "is_group": 0}, "name")


def money(v):
    """Định dạng số kiểu VN: 1.234.567"""
    try:
        return f"{float(v or 0):,.0f}".replace(",", ".")
    except Exception:
        return str(v)


def vn_date(d=None):
    """dd/mm/yyyy"""
    d = getdate(d or nowdate())
    return d.strftime("%d/%m/%Y")


def log_doc(doctype, name, action, detail="", user=None):
    """Ghi 1 dòng marker [LOG ...] vào field notes (nếu doc có), phục vụ ActivityTimeline."""
    user = user or frappe.session.user
    line = f"[LOG {frappe.utils.now()}] {user} | {action} | {detail}"
    meta = frappe.get_meta(doctype)
    field = "notes" if meta.has_field("notes") else ("note" if meta.has_field("note") else None)
    if not field:
        frappe.get_doc(doctype, name).add_comment("Comment", line)
        return
    cur = frappe.db.get_value(doctype, name, field) or ""
    frappe.db.set_value(doctype, name, field, (cur + "\n" + line).strip())


def parse_logs(text):
    """Parse các dòng [LOG time] user | action | detail -> list dict cho ActivityTimeline."""
    import re
    out = []
    for m in re.finditer(r"\[LOG ([^\]]+)\]\s*([^|]*)\|\s*([^|]*)\|\s*(.*)", text or ""):
        out.append({"time": m.group(1).strip(), "user": m.group(2).strip(), "action": m.group(3).strip(), "detail": m.group(4).strip()})
    out.reverse()  # mới nhất trước
    return out


# ── Ghi chú tích hợp ─────────────────────────────────────────────────────────
# Để `import gpc_common` chạy được, thêm vào ĐẦU apps/<app>/<app>/__init__.py:
#     import os, sys
#     _shared = os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared", "py")
#     if os.path.isdir(_shared) and _shared not in sys.path:
#         sys.path.insert(0, _shared)
# (Trong bench, shared/py nằm ở /home/frappe/frappe-bench/shared/py — xem Dockerfile/compose.)
