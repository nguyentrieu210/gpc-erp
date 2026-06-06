"""API mỏng cho Mua hàng — reuse ERPNext Buying (Supplier, Purchase Order,
Purchase Receipt, Purchase Invoice, Payment Entry, Material Request type=Purchase).
Full chuỗi: Đề nghị mua → PO → Nhập mua (vào kho + GL) → Hóa đơn → Công nợ 331 → Thanh toán.
KHÔNG tạo doctype mới. Item/kho dùng lại kho.api.*. Phong cách giống module kho."""

import frappe
import json as _json
from frappe.utils import flt, cint, getdate, today, add_days

# ---------------------------------------------------------------------------
# Helpers chung
# ---------------------------------------------------------------------------

def _company():
    return (
        frappe.defaults.get_user_default("Company")
        or frappe.db.get_single_value("Global Defaults", "default_company")
        or frappe.db.get_value("Company", {}, "name")
    )


def _abbr(company=None):
    return frappe.db.get_value("Company", company or _company(), "abbr")


def _acct(number, company=None):
    return frappe.db.get_value(
        "Account", {"company": company or _company(), "account_number": number}, "name"
    )


def _cash_account():
    """Tài khoản tiền (Cash/Bank) để thanh toán — ưu tiên 1111/111 (tiền mặt)."""
    company = _company()
    for num in ["1111", "111", "1121", "112"]:
        a = _acct(num, company)
        if a and not frappe.db.get_value("Account", a, "is_group") \
                and frappe.db.get_value("Account", a, "account_type") in ("Cash", "Bank"):
            return a
    a = frappe.db.get_value("Account", {"company": company, "account_type": "Cash", "is_group": 0}, "name")
    return a or frappe.db.get_value("Account", {"company": company, "account_type": "Bank", "is_group": 0}, "name")


def _log(doctype, name, action, detail=""):
    try:
        user = frappe.session.user or "System"
        txt = f"[{action}] {user}" + (f" — {detail}" if detail else "")
        frappe.get_doc(doctype, name).add_comment("Comment", txt)
    except Exception:
        pass


def _check_perm(doctype, ptype="read"):
    if not frappe.has_permission(doctype, ptype):
        frappe.throw(
            f"Ban khong co quyen thuc hien thao tac nay ({ptype} tren {doctype})",
            frappe.PermissionError,
        )


def _check_any_role(*roles):
    user_roles = set(frappe.get_roles(frappe.session.user))
    if not user_roles.intersection(roles):
        frappe.throw(
            f"Ban can mot trong cac vai tro: {', '.join(roles)}",
            frappe.PermissionError,
        )


def _vn_date(d):
    if not d:
        return ""
    d = getdate(d)
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def _money(v):
    try:
        return f"{flt(v):,.0f}".replace(",", ".")
    except Exception:
        return str(v)


def _default_purchase_tax(company=None):
    company = company or _company()
    t = frappe.db.get_value(
        "Purchase Taxes and Charges Template", {"company": company, "is_default": 1}, "name"
    )
    return t or frappe.db.get_value("Purchase Taxes and Charges Template", {"company": company}, "name")


def _apply_purchase_tax(doc, template=None):
    template = template or _default_purchase_tax(doc.company)
    if not template:
        return
    try:
        from erpnext.controllers.accounts_controller import get_taxes_and_charges
        doc.taxes_and_charges = template
        doc.set("taxes", [])
        for t in get_taxes_and_charges("Purchase Taxes and Charges Template", template):
            doc.append("taxes", t)
    except Exception as e:
        frappe.log_error(title="muahang _apply_purchase_tax", message=str(e)[:400])


# ---------------------------------------------------------------------------
# 0. SETUP (idempotent)
# ---------------------------------------------------------------------------

SUPPLIER_GROUPS_VI = ["NCC trong nước", "NCC nước ngoài", "Dịch vụ", "Vật tư", "Nhà thầu"]


def _ensure_company_buying_accounts():
    company = _company()
    cdoc = frappe.get_doc("Company", company)
    changed = []
    if not cdoc.default_payable_account:
        pay = _acct("331", company)
        if pay:
            cdoc.default_payable_account = pay
            changed.append("default_payable_account")
    if not cdoc.default_expense_account:
        exp = _acct("632", company)
        if exp:
            cdoc.default_expense_account = exp
            changed.append("default_expense_account")
    if changed:
        cdoc.save(ignore_permissions=True)
    return {
        "company": company,
        "changed": changed,
        "default_payable_account": cdoc.default_payable_account,
        "default_expense_account": cdoc.default_expense_account,
        "cost_center": cdoc.cost_center,
    }


def _ensure_supplier_groups():
    created = []
    parent = "All Supplier Groups"
    for g in SUPPLIER_GROUPS_VI:
        if not frappe.db.exists("Supplier Group", g):
            try:
                frappe.get_doc({
                    "doctype": "Supplier Group", "supplier_group_name": g,
                    "parent_supplier_group": parent, "is_group": 0,
                }).insert(ignore_permissions=True)
                created.append(g)
            except Exception as e:
                frappe.log_error(title="muahang supplier group", message=str(e)[:300])
    return created


@frappe.whitelist()
def setup_muahang():
    """Cài đặt 1 lần (idempotent): tài khoản công nợ/chi phí + nhóm NCC VN."""
    _check_any_role("System Manager", "Purchase Manager", "Accounts Manager")
    accounts = _ensure_company_buying_accounts()
    groups = _ensure_supplier_groups()
    frappe.db.commit()
    return {"accounts": accounts, "supplier_groups_created": groups, "status": get_muahang_setup_status()}


@frappe.whitelist()
def get_muahang_setup_status():
    company = _company()
    cdoc = frappe.get_doc("Company", company)
    cfg = {
        "company": company,
        "abbr": _abbr(company),
        "default_payable_account": cdoc.default_payable_account,
        "default_expense_account": cdoc.default_expense_account,
        "cost_center": cdoc.cost_center,
        "perpetual_inventory": cdoc.enable_perpetual_inventory,
        "stock_received_but_not_billed": cdoc.get("stock_received_but_not_billed"),
        "purchase_tax_template": _default_purchase_tax(company),
        "cash_account": _cash_account(),
    }
    cfg["ready"] = bool(cdoc.default_payable_account and cdoc.default_expense_account)
    cfg["supplier_count"] = frappe.db.count("Supplier")
    cfg["supplier_group_count"] = frappe.db.count("Supplier Group", {"is_group": 0})
    return cfg


# ---------------------------------------------------------------------------
# 1. NHÀ CUNG CẤP (Supplier)
# ---------------------------------------------------------------------------

def _default_supplier_group():
    for g in ["NCC trong nước", "Local", "All Supplier Groups"]:
        if frappe.db.exists("Supplier Group", g) and not frappe.db.get_value("Supplier Group", g, "is_group"):
            return g
    return frappe.db.get_value("Supplier Group", {"is_group": 0}, "name")


def _supplier_outstanding_map():
    out = {}
    for pi in frappe.get_all("Purchase Invoice", filters={"docstatus": 1},
                             fields=["supplier", "outstanding_amount"]):
        out[pi.supplier] = out.get(pi.supplier, 0) + flt(pi.outstanding_amount)
    return out


@frappe.whitelist()
def get_suppliers(search="", supplier_group=None, page=1, page_length=30):
    page = cint(page) or 1
    page_length = cint(page_length) or 30
    filters = {}
    if supplier_group:
        filters["supplier_group"] = supplier_group
    or_filters = None
    if search:
        or_filters = [["supplier_name", "like", f"%{search}%"], ["name", "like", f"%{search}%"]]
    if or_filters:
        total = len(frappe.get_all("Supplier", filters=filters, or_filters=or_filters, pluck="name", limit_page_length=0))
    else:
        total = frappe.db.count("Supplier", filters)
    rows = frappe.get_all(
        "Supplier", filters=filters, or_filters=or_filters,
        fields=["name", "supplier_name", "supplier_group", "supplier_type", "country",
                "tax_id", "disabled", "creation"],
        order_by="supplier_name asc",
        limit_page_length=page_length, start=(page - 1) * page_length,
    )
    om = _supplier_outstanding_map()
    for r in rows:
        r["outstanding"] = om.get(r.name, 0)
    pages = ((total or 0) + page_length - 1) // page_length
    return {"suppliers": rows, "total": total, "pages": pages, "page": page}


@frappe.whitelist()
def get_supplier(name):
    doc = frappe.get_doc("Supplier", name)
    d = doc.as_dict()
    d["outstanding"] = _supplier_outstanding_map().get(name, 0)
    d["recent_pos"] = frappe.get_all(
        "Purchase Order", filters={"supplier": name},
        fields=["name", "transaction_date", "grand_total", "status", "docstatus"],
        order_by="transaction_date desc", limit_page_length=10,
    )
    d["ledger"] = get_supplier_ledger(name)
    return d


WRITABLE_SUPPLIER_FIELDS = {"supplier_name", "supplier_group", "supplier_type", "country",
                            "tax_id", "supplier_details", "disabled", "default_currency"}


@frappe.whitelist()
def create_supplier(supplier_name, supplier_group=None, supplier_type="Company",
                    country="Vietnam", tax_id=None, mobile=None, email=None, supplier_details=None):
    _check_perm("Supplier", "create")
    sg = supplier_group or _default_supplier_group()
    if not frappe.db.exists("Supplier Group", sg):
        sg = _default_supplier_group()
    details = supplier_details or ""
    extra = []
    if mobile:
        extra.append(f"ĐT: {mobile}")
    if email:
        extra.append(f"Email: {email}")
    if extra:
        details = (details + "\n" + " · ".join(extra)).strip()
    doc = frappe.get_doc({
        "doctype": "Supplier",
        "supplier_name": supplier_name,
        "supplier_group": sg,
        "supplier_type": supplier_type,
        "country": country if frappe.db.exists("Country", country) else None,
        "tax_id": tax_id,
        "supplier_details": details,
    })
    if mobile and doc.meta.has_field("mobile_no"):
        doc.mobile_no = mobile
    doc.insert(ignore_permissions=True)
    _log("Supplier", doc.name, "create_supplier", supplier_name)
    return doc.as_dict()


@frappe.whitelist()
def update_supplier(name, **kwargs):
    _check_perm("Supplier", "write")
    doc = frappe.get_doc("Supplier", name)
    changed = []
    for k, v in kwargs.items():
        if k in WRITABLE_SUPPLIER_FIELDS:
            doc.set(k, v)
            changed.append(k)
    doc.save(ignore_permissions=True)
    if changed:
        _log("Supplier", name, "update_supplier", ", ".join(changed))
    return doc.as_dict()


@frappe.whitelist()
def toggle_supplier(name, disabled=1):
    _check_perm("Supplier", "write")
    frappe.db.set_value("Supplier", name, "disabled", cint(disabled))
    return {"name": name, "disabled": cint(disabled)}


@frappe.whitelist()
def get_supplier_groups():
    return frappe.get_all(
        "Supplier Group", filters={"is_group": 0},
        fields=["name", "supplier_group_name"], order_by="supplier_group_name asc",
    )


@frappe.whitelist()
def create_supplier_group(supplier_group_name, parent_supplier_group="All Supplier Groups"):
    _check_perm("Supplier Group", "create")
    if frappe.db.exists("Supplier Group", supplier_group_name):
        return {"name": supplier_group_name, "existed": True}
    doc = frappe.get_doc({
        "doctype": "Supplier Group", "supplier_group_name": supplier_group_name,
        "parent_supplier_group": parent_supplier_group, "is_group": 0,
    })
    doc.insert(ignore_permissions=True)
    return {"name": doc.name, "existed": False}


@frappe.whitelist()
def get_supplier_dashboard():
    total_payable = sum(_supplier_outstanding_map().values())
    spend = {}
    for po in frappe.get_all("Purchase Order", filters={"docstatus": 1},
                             fields=["supplier", "supplier_name", "grand_total"]):
        spend[po.supplier_name or po.supplier] = spend.get(po.supplier_name or po.supplier, 0) + flt(po.grand_total)
    top = sorted(spend.items(), key=lambda x: x[1], reverse=True)[:8]
    return {
        "total_suppliers": frappe.db.count("Supplier"),
        "active_suppliers": frappe.db.count("Supplier", {"disabled": 0}),
        "total_payable": total_payable,
        "top_suppliers": [{"supplier_name": k, "spend": v} for k, v in top if v > 0],
    }


# ---------------------------------------------------------------------------
# 2. ĐỀ NGHỊ MUA (Material Request type=Purchase)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_purchase_requests(status=None, page=1, page_length=30):
    page = cint(page) or 1
    page_length = cint(page_length) or 30
    filters = {"material_request_type": "Purchase"}
    if status:
        filters["status"] = status
    total = frappe.db.count("Material Request", filters)
    rows = frappe.get_all(
        "Material Request", filters=filters,
        fields=["name", "transaction_date", "schedule_date", "status", "docstatus", "per_ordered"],
        order_by="transaction_date desc, creation desc",
        limit_page_length=page_length, start=(page - 1) * page_length,
    )
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def create_purchase_request(items, schedule_date=None, warehouse=None, submit=0):
    if isinstance(items, str):
        items = _json.loads(items)
    company = _company()
    sched = getdate(schedule_date) if schedule_date else add_days(getdate(today()), 7)
    doc = frappe.new_doc("Material Request")
    doc.company = company
    doc.material_request_type = "Purchase"
    doc.schedule_date = sched
    for it in items:
        doc.append("items", {
            "item_code": it.get("item_code"), "qty": flt(it.get("qty")),
            "schedule_date": sched, "warehouse": it.get("warehouse") or warehouse,
        })
    doc.insert(ignore_permissions=True)
    if cint(submit):
        doc.submit()
    _log("Material Request", doc.name, "create_purchase_request")
    return doc.as_dict()


@frappe.whitelist()
def submit_purchase_request(name):
    doc = frappe.get_doc("Material Request", name)
    doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def make_po_from_request(name, supplier=None, submit=0):
    from erpnext.stock.doctype.material_request.material_request import make_purchase_order
    po = make_purchase_order(name)
    if supplier:
        po.supplier = supplier
    if not po.supplier:
        frappe.throw("Cần chọn nhà cung cấp")
    po.insert(ignore_permissions=True)
    if cint(submit):
        po.submit()
    return po.as_dict()


# ---------------------------------------------------------------------------
# 3. ĐƠN MUA HÀNG (Purchase Order)
# ---------------------------------------------------------------------------

PO_STATUS_VI = {
    "Draft": "Nháp", "To Receive and Bill": "Chờ nhận & HĐ", "To Bill": "Chờ hóa đơn",
    "To Receive": "Chờ nhận", "Completed": "Hoàn tất", "Closed": "Đã đóng", "Cancelled": "Đã hủy",
}


@frappe.whitelist()
def get_purchase_orders(search="", supplier=None, status=None, from_date=None, to_date=None,
                        page=1, page_length=30):
    page = cint(page) or 1
    page_length = cint(page_length) or 30
    filters = {"docstatus": ["!=", 2]}
    if supplier:
        filters["supplier"] = supplier
    if status:
        filters["status"] = status
    if from_date and to_date:
        filters["transaction_date"] = ["between", [getdate(from_date), getdate(to_date)]]
    or_filters = None
    if search:
        or_filters = [["name", "like", f"%{search}%"], ["supplier_name", "like", f"%{search}%"]]
    total = frappe.db.count("Purchase Order", filters)
    rows = frappe.get_all(
        "Purchase Order", filters=filters, or_filters=or_filters,
        fields=["name", "supplier", "supplier_name", "transaction_date", "schedule_date",
                "grand_total", "status", "docstatus", "per_received", "per_billed"],
        order_by="transaction_date desc, creation desc",
        limit_page_length=page_length, start=(page - 1) * page_length,
    )
    for r in rows:
        r["status_vi"] = PO_STATUS_VI.get(r.status, r.status)
    pages = ((total or 0) + page_length - 1) // page_length
    return {"entries": rows, "total": total, "pages": pages, "page": page}


@frappe.whitelist()
def get_purchase_order(name):
    d = frappe.get_doc("Purchase Order", name).as_dict()
    d["status_vi"] = PO_STATUS_VI.get(d.get("status"), d.get("status"))
    return d


@frappe.whitelist()
def create_purchase_order(supplier, items, transaction_date=None, schedule_date=None,
                          apply_tax=1, submit=0):
    if isinstance(items, str):
        items = _json.loads(items)
    company = _company()
    td = getdate(transaction_date) if transaction_date else getdate(today())
    sd = getdate(schedule_date) if schedule_date else add_days(td, 7)
    po = frappe.new_doc("Purchase Order")
    po.supplier = supplier
    po.company = company
    po.transaction_date = td
    po.schedule_date = sd
    for it in items:
        po.append("items", {
            "item_code": it.get("item_code"),
            "qty": flt(it.get("qty")),
            "rate": flt(it.get("rate")),
            "schedule_date": getdate(it.get("schedule_date")) if it.get("schedule_date") else sd,
            "warehouse": it.get("warehouse") or None,
        })
    if cint(apply_tax):
        _apply_purchase_tax(po)
    po.insert(ignore_permissions=True)
    if cint(submit):
        po.submit()
    _log("Purchase Order", po.name, "create_po", supplier)
    return po.as_dict()


@frappe.whitelist()
def submit_purchase_order(name):
    doc = frappe.get_doc("Purchase Order", name)
    doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus, "status": doc.status}


@frappe.whitelist()
def cancel_purchase_order(name):
    doc = frappe.get_doc("Purchase Order", name)
    doc.cancel()
    return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def delete_purchase_order(name):
    if frappe.db.get_value("Purchase Order", name, "docstatus") == 1:
        frappe.throw("Đơn đã chốt — hãy hủy trước khi xóa")
    frappe.delete_doc("Purchase Order", name, ignore_permissions=True)
    return {"deleted": name}


@frappe.whitelist()
def make_purchase_receipt_from_po(name, submit=0):
    from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
    pr = make_purchase_receipt(name)
    pr.insert(ignore_permissions=True)
    if cint(submit):
        pr.submit()
    _log("Purchase Receipt", pr.name, "from_po", name)
    return pr.as_dict()


@frappe.whitelist()
def make_purchase_invoice_from_po(name, submit=0):
    from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_invoice
    pi = make_purchase_invoice(name)
    pi.insert(ignore_permissions=True)
    if cint(submit):
        pi.submit()
    return pi.as_dict()


# ---------------------------------------------------------------------------
# 4. NHẬP MUA (Purchase Receipt) — vào kho + GL
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_purchase_receipts(search="", supplier=None, page=1, page_length=30):
    page = cint(page) or 1
    page_length = cint(page_length) or 30
    filters = {"docstatus": ["!=", 2]}
    if supplier:
        filters["supplier"] = supplier
    or_filters = None
    if search:
        or_filters = [["name", "like", f"%{search}%"], ["supplier_name", "like", f"%{search}%"]]
    total = frappe.db.count("Purchase Receipt", filters)
    rows = frappe.get_all(
        "Purchase Receipt", filters=filters, or_filters=or_filters,
        fields=["name", "supplier", "supplier_name", "posting_date", "grand_total",
                "status", "docstatus", "per_billed"],
        order_by="posting_date desc, creation desc",
        limit_page_length=page_length, start=(page - 1) * page_length,
    )
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def get_purchase_receipt(name):
    return frappe.get_doc("Purchase Receipt", name).as_dict()


@frappe.whitelist()
def create_purchase_receipt(supplier, items, posting_date=None, set_warehouse=None,
                            apply_tax=1, submit=0):
    if isinstance(items, str):
        items = _json.loads(items)
    company = _company()
    pr = frappe.new_doc("Purchase Receipt")
    pr.supplier = supplier
    pr.company = company
    if posting_date:
        pr.set_posting_time = 1
        pr.posting_date = getdate(posting_date)
    if set_warehouse:
        pr.set_warehouse = set_warehouse
    for it in items:
        pr.append("items", {
            "item_code": it.get("item_code"),
            "qty": flt(it.get("qty")),
            "rate": flt(it.get("rate")),
            "warehouse": it.get("warehouse") or set_warehouse,
        })
    if cint(apply_tax):
        _apply_purchase_tax(pr)
    pr.insert(ignore_permissions=True)
    if cint(submit):
        pr.submit()
    _log("Purchase Receipt", pr.name, "create_pr", supplier)
    return pr.as_dict()


@frappe.whitelist()
def submit_purchase_receipt(name):
    doc = frappe.get_doc("Purchase Receipt", name)
    doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus, "status": doc.status}


@frappe.whitelist()
def cancel_purchase_receipt(name):
    doc = frappe.get_doc("Purchase Receipt", name)
    doc.cancel()
    return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def make_purchase_invoice_from_pr(name, bill_no=None, bill_date=None, submit=0):
    from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
    pi = make_purchase_invoice(name)
    if bill_no:
        pi.bill_no = bill_no
    if bill_date:
        pi.bill_date = getdate(bill_date)
    pi.insert(ignore_permissions=True)
    if cint(submit):
        pi.submit()
    _log("Purchase Invoice", pi.name, "from_pr", name)
    return pi.as_dict()


# ---------------------------------------------------------------------------
# 5. HÓA ĐƠN MUA (Purchase Invoice) — công nợ 331
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_purchase_invoices(search="", supplier=None, status=None, page=1, page_length=30):
    page = cint(page) or 1
    page_length = cint(page_length) or 30
    filters = {"docstatus": ["!=", 2]}
    if supplier:
        filters["supplier"] = supplier
    if status:
        filters["status"] = status
    or_filters = None
    if search:
        or_filters = [["name", "like", f"%{search}%"], ["supplier_name", "like", f"%{search}%"],
                      ["bill_no", "like", f"%{search}%"]]
    total = frappe.db.count("Purchase Invoice", filters)
    rows = frappe.get_all(
        "Purchase Invoice", filters=filters, or_filters=or_filters,
        fields=["name", "supplier", "supplier_name", "posting_date", "bill_no", "bill_date",
                "grand_total", "outstanding_amount", "status", "docstatus"],
        order_by="posting_date desc, creation desc",
        limit_page_length=page_length, start=(page - 1) * page_length,
    )
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def get_purchase_invoice(name):
    return frappe.get_doc("Purchase Invoice", name).as_dict()


@frappe.whitelist()
def create_purchase_invoice(supplier, items, bill_no=None, bill_date=None, posting_date=None,
                            update_stock=0, set_warehouse=None, apply_tax=1, submit=0):
    if isinstance(items, str):
        items = _json.loads(items)
    company = _company()
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = supplier
    pi.company = company
    pi.bill_no = bill_no
    if bill_date:
        pi.bill_date = getdate(bill_date)
    if posting_date:
        pi.set_posting_time = 1
        pi.posting_date = getdate(posting_date)
    pi.update_stock = cint(update_stock)
    if cint(update_stock) and set_warehouse:
        pi.set_warehouse = set_warehouse
    for it in items:
        row = {"item_code": it.get("item_code"), "qty": flt(it.get("qty")), "rate": flt(it.get("rate"))}
        if cint(update_stock):
            row["warehouse"] = it.get("warehouse") or set_warehouse
        pi.append("items", row)
    if cint(apply_tax):
        _apply_purchase_tax(pi)
    pi.insert(ignore_permissions=True)
    if cint(submit):
        pi.submit()
    _log("Purchase Invoice", pi.name, "create_pi", supplier)
    return pi.as_dict()


@frappe.whitelist()
def submit_purchase_invoice(name):
    doc = frappe.get_doc("Purchase Invoice", name)
    doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus, "outstanding_amount": doc.outstanding_amount}


@frappe.whitelist()
def cancel_purchase_invoice(name):
    doc = frappe.get_doc("Purchase Invoice", name)
    doc.cancel()
    return {"name": doc.name, "docstatus": doc.docstatus}


# ---------------------------------------------------------------------------
# 6. CÔNG NỢ PHẢI TRẢ + THANH TOÁN (Payment Entry)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_payables_summary():
    rows = []
    by_sup = {}
    for pi in frappe.get_all(
        "Purchase Invoice", filters={"docstatus": 1, "outstanding_amount": [">", 0]},
        fields=["name", "supplier", "supplier_name", "posting_date", "due_date",
                "grand_total", "outstanding_amount"],
        order_by="due_date asc",
    ):
        d = by_sup.setdefault(pi.supplier, {
            "supplier": pi.supplier, "supplier_name": pi.supplier_name,
            "outstanding": 0, "invoices": [],
        })
        d["outstanding"] += flt(pi.outstanding_amount)
        d["invoices"].append(pi)
    total = 0
    for s in by_sup.values():
        total += s["outstanding"]
        rows.append(s)
    rows.sort(key=lambda x: x["outstanding"], reverse=True)
    return {"suppliers": rows, "total_outstanding": total, "count": len(rows)}


@frappe.whitelist()
def get_supplier_ledger(supplier, limit=200):
    return frappe.get_all(
        "GL Entry",
        filters={"party_type": "Supplier", "party": supplier, "is_cancelled": 0},
        fields=["posting_date", "voucher_type", "voucher_no", "debit", "credit", "against"],
        order_by="posting_date asc, creation asc",
        limit_page_length=cint(limit) or 200,
    )


@frappe.whitelist()
def make_payment(invoice, paid_from=None, submit=1):
    """Thanh toán 1 hóa đơn mua → Payment Entry (Dr 331 / Cr tiền)."""
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    pe = get_payment_entry("Purchase Invoice", invoice)
    cash = paid_from or _cash_account()
    if not cash:
        frappe.throw("Không tìm thấy tài khoản tiền (Cash/Bank) để thanh toán")
    pe.paid_from = cash
    pe.paid_from_account_currency = frappe.db.get_value("Account", cash, "account_currency") or "VND"
    if not pe.reference_no:
        pe.reference_no = pe.party_name or "TM"
    if not pe.reference_date:
        pe.reference_date = getdate(today())
    pe.insert(ignore_permissions=True)
    if cint(submit):
        pe.submit()
    _log("Payment Entry", pe.name, "make_payment", invoice)
    return pe.as_dict()


# ---------------------------------------------------------------------------
# 7. DASHBOARD
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_purchase_dashboard():
    company = _company()
    first_of_month = getdate(today()).replace(day=1)
    po_status = {}
    to_receive_val = 0.0
    to_bill_val = 0.0
    month_val = 0.0
    for po in frappe.get_all(
        "Purchase Order", filters={"docstatus": 1},
        fields=["status", "grand_total", "per_received", "per_billed", "transaction_date"],
    ):
        po_status[po.status] = po_status.get(po.status, 0) + 1
        if flt(po.per_received) < 100:
            to_receive_val += flt(po.grand_total) * (100 - flt(po.per_received)) / 100
        if flt(po.per_billed) < 100:
            to_bill_val += flt(po.grand_total) * (100 - flt(po.per_billed)) / 100
        if getdate(po.transaction_date) >= first_of_month:
            month_val += flt(po.grand_total)
    payables = sum(_supplier_outstanding_map().values())
    return {
        "po_total": frappe.db.count("Purchase Order", {"docstatus": 1}),
        "po_draft": frappe.db.count("Purchase Order", {"docstatus": 0}),
        "po_by_status": [{"status": PO_STATUS_VI.get(k, k), "count": v} for k, v in po_status.items()],
        "po_month_value": month_val,
        "to_receive_value": to_receive_val,
        "to_bill_value": to_bill_val,
        "total_payable": payables,
        "supplier_count": frappe.db.count("Supplier", {"disabled": 0}),
        "pi_unpaid": frappe.db.count("Purchase Invoice", {"docstatus": 1, "outstanding_amount": [">", 0]}),
    }


# ---------------------------------------------------------------------------
# 8. IN CHỨNG TỪ MẪU VN + hạ tầng
# ---------------------------------------------------------------------------

def _print_doc_vn(doctype, name, title, date_field):
    doc = frappe.get_doc(doctype, name)
    company = frappe.get_doc("Company", doc.company)
    rows = ""
    total = 0.0
    for i, it in enumerate(doc.items, 1):
        amt = flt(it.amount)
        total += amt
        rows += (
            f"<tr><td style='text-align:center'>{i}</td>"
            f"<td>{frappe.utils.escape_html(it.item_code)}</td>"
            f"<td>{frappe.utils.escape_html(it.item_name or '')}</td>"
            f"<td style='text-align:center'>{frappe.utils.escape_html(it.uom or it.stock_uom or '')}</td>"
            f"<td style='text-align:right'>{flt(it.qty):,.2f}</td>"
            f"<td style='text-align:right'>{_money(it.rate)}</td>"
            f"<td style='text-align:right'>{_money(amt)}</td></tr>"
        )
    grand = flt(getattr(doc, "grand_total", total))
    pdate = getattr(doc, date_field, None)
    html = f"""
<div style="font-family:'Times New Roman',serif;max-width:780px;margin:auto;padding:20px;color:#000">
  <div style="text-align:center">
    <div style="font-weight:bold">{frappe.utils.escape_html(company.company_name)}</div>
  </div>
  <h2 style="text-align:center;margin:16px 0 4px">{title}</h2>
  <div style="text-align:center;font-size:13px;margin-bottom:12px">
    Ngày {_vn_date(pdate)} &nbsp;·&nbsp; Số: {frappe.utils.escape_html(doc.name)}
  </div>
  <div style="font-size:13px;margin-bottom:8px">
    <b>Nhà cung cấp:</b> {frappe.utils.escape_html(doc.supplier_name or doc.supplier or '')}
    &nbsp; <b>MST:</b> {frappe.utils.escape_html(frappe.db.get_value('Supplier', doc.supplier, 'tax_id') or '')}
  </div>
  <table style="width:100%;border-collapse:collapse;font-size:13px" border="1">
    <thead><tr style="background:#f2f2f2">
      <th>STT</th><th>Mã hàng</th><th>Tên hàng</th><th>ĐVT</th>
      <th>Số lượng</th><th>Đơn giá</th><th>Thành tiền</th>
    </tr></thead>
    <tbody>{rows}
      <tr style="font-weight:bold"><td colspan="6" style="text-align:right">Tổng cộng (gồm thuế)</td>
      <td style="text-align:right">{_money(grand)}</td></tr>
    </tbody>
  </table>
  <div style="display:flex;justify-content:space-around;margin-top:42px;font-size:13px;text-align:center">
    <div><b>Người lập</b><br>(Ký, họ tên)</div>
    <div><b>Phụ trách mua hàng</b><br>(Ký, họ tên)</div>
    <div><b>Giám đốc</b><br>(Ký, họ tên)</div>
  </div>
</div>
"""
    return html


@frappe.whitelist()
def print_purchase_order(name):
    return _print_doc_vn("Purchase Order", name, "ĐƠN ĐẶT HÀNG", "transaction_date")


@frappe.whitelist()
def print_purchase_receipt(name):
    return _print_doc_vn("Purchase Receipt", name, "PHIẾU NHẬP MUA", "posting_date")


@frappe.whitelist()
def get_tax_templates():
    company = _company()
    return frappe.get_all(
        "Purchase Taxes and Charges Template", filters={"company": company},
        fields=["name", "title", "is_default"], order_by="is_default desc",
    )


@frappe.whitelist()
# ---------------------------------------------------------------------------
# 9. DOCUMENT LINKING
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_linked_docs(doctype, name):
    """Tra ve chung tu lien quan: PR/PI/Payment tu PO."""
    links = {"source": name, "doctype": doctype}
    if doctype == "Purchase Order":
        links["receipts"] = frappe.get_all("Purchase Receipt Item",
            filters={"purchase_order": name, "docstatus": ["!=", 2]}, pluck="parent", distinct=True)
        if links["receipts"]:
            links["receipts"] = frappe.get_all("Purchase Receipt",
                filters={"name": ["in", links["receipts"]]},
                fields=["name", "supplier_name", "grand_total", "posting_date", "docstatus", "status"], limit=10)
        links["invoices"] = frappe.get_all("Purchase Invoice Item",
            filters={"purchase_order": name, "docstatus": ["!=", 2]}, pluck="parent", distinct=True)
        if links["invoices"]:
            links["invoices"] = frappe.get_all("Purchase Invoice",
                filters={"name": ["in", links["invoices"]]},
                fields=["name", "supplier_name", "grand_total", "outstanding_amount", "posting_date", "docstatus"], limit=10)
    elif doctype == "Purchase Invoice":
        links["payments"] = frappe.get_all("Payment Entry Reference",
            filters={"reference_name": name, "docstatus": 1}, pluck="parent", distinct=True)
        if links["payments"]:
            links["payments"] = frappe.get_all("Payment Entry",
                filters={"name": ["in", links["payments"]]},
                fields=["name", "paid_amount", "posting_date", "docstatus"], limit=10)
    elif doctype == "Purchase Receipt":
        links["purchase_order"] = frappe.get_all("Purchase Receipt Item",
            filters={"parent": name, "docstatus": ["!=", 2], "purchase_order": ["!=", ""]},
            fields=["purchase_order"], distinct=True, pluck="purchase_order")
        if links["purchase_order"]:
            links["purchase_order"] = frappe.get_all("Purchase Order",
                filters={"name": ["in", links["purchase_order"]]},
                fields=["name", "supplier_name", "grand_total", "transaction_date", "docstatus"], limit=5)
        links["invoices"] = frappe.get_all("Purchase Invoice Item",
            filters={"purchase_receipt": name, "docstatus": ["!=", 2]}, pluck="parent", distinct=True)
        if links["invoices"]:
            links["invoices"] = frappe.get_all("Purchase Invoice",
                filters={"name": ["in", links["invoices"]]},
                fields=["name", "supplier_name", "grand_total", "outstanding_amount", "posting_date", "docstatus"], limit=10)
    return links


@frappe.whitelist()
def get_csrf_token():
    import frappe.sessions
    return frappe.sessions.get_csrf_token()
