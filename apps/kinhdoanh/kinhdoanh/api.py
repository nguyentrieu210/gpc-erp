"""API mỏng cho Kinh doanh — reuse ERPNext Selling (Quotation, Sales Order, Delivery Note,
Sales Invoice, Payment Entry). Full: Customer → Báo giá → Đơn bán → Xuất giao → Hóa đơn → Công nợ 131 → Thanh toán.
KHÔNG tạo doctype mới. Phong cách giống muahang (Mua hàng)."""

import frappe
import json as _json
from frappe.utils import flt, cint, getdate, today, add_days


def _company():
    return (frappe.defaults.get_user_default("Company") or
            frappe.db.get_single_value("Global Defaults", "default_company") or
            frappe.db.get_value("Company", {}, "name"))


def _abbr(company=None):
    return frappe.db.get_value("Company", company or _company(), "abbr")


def _acct(number, company=None):
    return frappe.db.get_value("Account", {"company": company or _company(), "account_number": number}, "name")


def _cash_account():
    company = _company()
    for num in ["1111", "111", "1121", "112"]:
        a = _acct(num, company)
        if a and not frappe.db.get_value("Account", a, "is_group") and frappe.db.get_value("Account", a, "account_type") in ("Cash", "Bank"): return a
    return frappe.db.get_value("Account", {"company": company, "account_type": "Cash", "is_group": 0}, "name") or frappe.db.get_value("Account", {"company": company, "account_type": "Bank", "is_group": 0}, "name")


def _log(doctype, name, action, detail=""):
    try:
        user = frappe.session.user or "System"
        frappe.get_doc(doctype, name).add_comment("Comment", f"[{action}] {user}" + (f" — {detail}" if detail else ""))
    except Exception: pass


def _vn_date(d):
    if not d: return ""
    d = getdate(d); return f"{d.day:02d}/{d.month:02d}/{d.year}"


def _money(v):
    try: return f"{flt(v):,.0f}".replace(",", ".")
    except: return str(v)


def _default_customer_group():
    for g in ["Commercial", "Khách hàng trong nước", "Individual", "All Customer Groups"]:
        if frappe.db.exists("Customer Group", g) and not frappe.db.get_value("Customer Group", g, "is_group"): return g
    return frappe.db.get_value("Customer Group", {"is_group": 0}, "name")


def _customer_outstanding_map():
    out = {}
    for si in frappe.get_all("Sales Invoice", filters={"docstatus": 1}, fields=["customer", "outstanding_amount"]):
        out[si.customer] = out.get(si.customer, 0) + flt(si.outstanding_amount)
    return out


def _apply_sales_tax(doc, template=None):
    template = template or frappe.db.get_value("Sales Taxes and Charges Template", {"company": doc.company}, "name")
    if not template: return
    try:
        from erpnext.controllers.accounts_controller import get_taxes_and_charges
        doc.taxes_and_charges = template; doc.set("taxes", [])
        for t in get_taxes_and_charges("Sales Taxes and Charges Template", template): doc.append("taxes", t)
    except Exception as e: frappe.log_error(title="kinhdoanh tax", message=str(e)[:400])


# ---------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------

@frappe.whitelist()
def setup_sales():
    created = []
    for g in ["Khách hàng trong nước", "Khách hàng nước ngoài", "Đại lý", "Nhà phân phối"]:
        if not frappe.db.exists("Customer Group", g):
            try: frappe.get_doc({"doctype": "Customer Group", "customer_group_name": g, "parent_customer_group": "All Customer Groups", "is_group": 0}).insert(ignore_permissions=True); created.append(g)
            except Exception: pass
    frappe.db.commit()
    return {"customer_groups_created": created, "status": get_sales_setup_status()}


@frappe.whitelist()
def get_sales_setup_status():
    c = _company(); cd = frappe.get_doc("Company", c)
    return {"company": c, "abbr": _abbr(c), "ready": bool(cd.default_receivable_account and cd.default_income_account),
            "default_receivable_account": cd.default_receivable_account, "default_income_account": cd.default_income_account,
            "sales_tax_template": frappe.db.get_value("Sales Taxes and Charges Template", {"company": c}, "name"),
            "sales_price_list": frappe.db.get_value("Price List", {"selling": 1}, "name"),
            "customer_count": frappe.db.count("Customer", {"disabled": 0}),
            "customer_group_count": frappe.db.count("Customer Group", {"is_group": 0})}


# ---------------------------------------------------------------------------
# CUSTOMER
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_customers(search="", customer_group=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {}
    if customer_group: filters["customer_group"] = customer_group
    or_filters = None
    if search: or_filters = [["customer_name", "like", f"%{search}%"], ["name", "like", f"%{search}%"]]
    total = frappe.db.count("Customer", filters)
    rows = frappe.get_all("Customer", filters=filters, or_filters=or_filters,
                          fields=["name", "customer_name", "customer_type", "customer_group", "tax_id", "disabled", "creation"],
                          order_by="customer_name asc", limit_page_length=page_length, start=(page - 1) * page_length)
    om = _customer_outstanding_map()
    for r in rows: r["outstanding"] = om.get(r.name, 0)
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def get_customer(name):
    doc = frappe.get_doc("Customer", name)
    doc.reload()
    crm_opp = frappe.db.get_value("Customer", name, "custom_crm_opportunity") if frappe.db.exists("Custom Field", {"dt": "Customer", "fieldname": "custom_crm_opportunity"}) else None
    d = doc.as_dict()
    d["crm_opportunity"] = crm_opp
    d["crm_url"] = f"/crm_app/opportunities/{crm_opp}" if crm_opp else None
    d["outstanding"] = flt(_customer_outstanding_map().get(name, 0))
    d["recent_orders"] = frappe.get_all("Sales Order", filters={"customer": name}, fields=["name", "transaction_date", "grand_total", "status"], order_by="transaction_date desc", limit=10)
    d["ledger"] = frappe.get_all("GL Entry", filters={"party_type": "Customer", "party": name, "is_cancelled": 0}, fields=["posting_date", "voucher_type", "voucher_no", "debit", "credit"], order_by="posting_date asc", limit=200)
    return d


@frappe.whitelist()
def create_customer(customer_name, customer_type="Company", customer_group=None, tax_id=None, mobile=None, email=None):
    doc = frappe.get_doc({"doctype": "Customer", "customer_name": customer_name, "customer_type": customer_type,
                          "customer_group": customer_group or _default_customer_group(), "territory": "All Territories", "tax_id": tax_id})
    if mobile and doc.meta.has_field("mobile_no"): doc.mobile_no = mobile
    if email and doc.meta.has_field("email_id"): doc.email_id = email
    doc.insert(ignore_permissions=True); _log("Customer", doc.name, "create", customer_name); return doc.as_dict()


@frappe.whitelist()
def get_customer_groups():
    return frappe.get_all("Customer Group", filters={"is_group": 0}, fields=["name", "customer_group_name"], order_by="customer_group_name asc")


# ---------------------------------------------------------------------------
# BÁO GIÁ (Quotation)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_quotations(search="", customer=None, status=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {"docstatus": ["!=", 2]}
    if customer: filters["party_name"] = customer
    if status: filters["status"] = status
    or_filters = None
    if search: or_filters = [["name", "like", f"%{search}%"], ["customer_name", "like", f"%{search}%"]]
    total = frappe.db.count("Quotation", filters)
    rows = frappe.get_all("Quotation", filters=filters, or_filters=or_filters,
                          fields=["name", "customer_name", "grand_total", "status", "transaction_date", "valid_till", "docstatus", "creation"],
                          order_by="transaction_date desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def get_quotation(name):
    return frappe.get_doc("Quotation", name).as_dict()


@frappe.whitelist()
def create_quotation(customer, items, transaction_date=None, valid_till=None, apply_tax=1, submit=0):
    if isinstance(items, str): items = _json.loads(items)
    td = getdate(transaction_date) if transaction_date else getdate(today())
    vt = getdate(valid_till) if valid_till else add_days(td, 30)
    doc = frappe.new_doc("Quotation")
    doc.party_name = customer; doc.company = _company(); doc.transaction_date = td; doc.valid_till = vt
    for it in items: doc.append("items", {"item_code": it.get("item_code"), "qty": flt(it.get("qty")), "rate": flt(it.get("rate"))})
    if cint(apply_tax): _apply_sales_tax(doc)
    doc.insert(ignore_permissions=True)
    if cint(submit): doc.submit()
    _log("Quotation", doc.name, "create", customer); return doc.as_dict()


@frappe.whitelist()
def submit_quotation(name): doc = frappe.get_doc("Quotation", name); doc.submit(); return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def make_sales_order_from_quotation(name, submit=0):
    from erpnext.selling.doctype.quotation.quotation import make_sales_order
    so = make_sales_order(name); so.insert(ignore_permissions=True)
    if cint(submit): so.submit()
    _log("Sales Order", so.name, "from_quotation", name); return so.as_dict()


# ---------------------------------------------------------------------------
# ĐƠN BÁN (Sales Order)
# ---------------------------------------------------------------------------

SO_STATUS_VI = {"Draft": "Nháp", "To Deliver and Bill": "Chờ giao & HĐ", "To Bill": "Chờ HĐ", "To Deliver": "Chờ giao", "Completed": "Hoàn tất", "Closed": "Đã đóng"}


@frappe.whitelist()
def get_sales_orders(search="", customer=None, status=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {"docstatus": ["!=", 2]}
    if customer: filters["customer"] = customer
    if status: filters["status"] = status
    or_filters = None
    if search: or_filters = [["name", "like", f"%{search}%"], ["customer_name", "like", f"%{search}%"]]
    total = frappe.db.count("Sales Order", filters)
    rows = frappe.get_all("Sales Order", filters=filters, or_filters=or_filters,
                          fields=["name", "customer", "customer_name", "grand_total", "status", "transaction_date", "delivery_date", "docstatus", "per_delivered", "per_billed"],
                          order_by="transaction_date desc", limit_page_length=page_length, start=(page - 1) * page_length)
    for r in rows: r["status_vi"] = SO_STATUS_VI.get(r.status, r.status)
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def get_sales_order(name):
    d = frappe.get_doc("Sales Order", name).as_dict(); d["status_vi"] = SO_STATUS_VI.get(d.get("status"), d.get("status")); return d


@frappe.whitelist()
def create_sales_order(customer, items, transaction_date=None, delivery_date=None, apply_tax=1, submit=0):
    if isinstance(items, str): items = _json.loads(items)
    td = getdate(transaction_date) if transaction_date else getdate(today())
    dd = getdate(delivery_date) if delivery_date else add_days(td, 3)
    doc = frappe.new_doc("Sales Order"); doc.customer = customer; doc.company = _company(); doc.transaction_date = td; doc.delivery_date = dd
    for it in items: doc.append("items", {"item_code": it.get("item_code"), "qty": flt(it.get("qty")), "rate": flt(it.get("rate")), "delivery_date": dd, "warehouse": it.get("warehouse") or None})
    if cint(apply_tax): _apply_sales_tax(doc)
    doc.insert(ignore_permissions=True)
    if cint(submit): doc.submit()
    _log("Sales Order", doc.name, "create", customer); return doc.as_dict()


@frappe.whitelist()
def submit_sales_order(name): doc = frappe.get_doc("Sales Order", name); doc.submit(); return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def cancel_sales_order(name): doc = frappe.get_doc("Sales Order", name); doc.cancel(); return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def make_delivery_note_from_so(name, submit=0):
    from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
    dn = make_delivery_note(name); dn.insert(ignore_permissions=True)
    if cint(submit): dn.submit()
    _log("Delivery Note", dn.name, "from_so", name); return dn.as_dict()


@frappe.whitelist()
def make_sales_invoice_from_so(name, submit=0):
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
    si = make_sales_invoice(name); si.insert(ignore_permissions=True)
    if cint(submit): si.submit()
    return si.as_dict()


# ---------------------------------------------------------------------------
# XUẤT GIAO (Delivery Note) — ghi nhận xuất kho + GL
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_delivery_notes(search="", customer=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {"docstatus": ["!=", 2]}
    if customer: filters["customer"] = customer
    or_filters = None
    if search: or_filters = [["name", "like", f"%{search}%"], ["customer_name", "like", f"%{search}%"]]
    total = frappe.db.count("Delivery Note", filters)
    rows = frappe.get_all("Delivery Note", filters=filters, or_filters=or_filters,
                          fields=["name", "customer", "customer_name", "grand_total", "posting_date", "docstatus", "per_billed"],
                          order_by="posting_date desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def create_delivery_note(customer, items=None, posting_date=None, set_warehouse=None, apply_tax=1, submit=0, sales_order=None):
    if isinstance(items, str): items = _json.loads(items)

    if sales_order:
        # Dùng ERPNext mapper để giữ reference + update per_delivered trên SO
        from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
        doc = make_delivery_note(sales_order)
        # Override items nếu partial (chỉ giao 1 phần)
        if items:
            doc.items = []
            for it in items:
                doc.append("items", {
                    "item_code": it.get("item_code"),
                    "qty": flt(it.get("qty")),
                    "rate": flt(it.get("rate")),
                    "warehouse": it.get("warehouse") or set_warehouse,
                    "against_sales_order": sales_order,
                })
        if set_warehouse:
            doc.set_warehouse = set_warehouse
        if posting_date:
            doc.set_posting_time = 1
            doc.posting_date = getdate(posting_date)
    else:
        # Logic cũ: tạo DN độc lập
        doc = frappe.new_doc("Delivery Note")
        doc.customer = customer; doc.company = _company()
        if posting_date: doc.set_posting_time = 1; doc.posting_date = getdate(posting_date)
        if set_warehouse: doc.set_warehouse = set_warehouse
        for it in (items or []): doc.append("items", {"item_code": it.get("item_code"), "qty": flt(it.get("qty")), "rate": flt(it.get("rate")), "warehouse": it.get("warehouse") or set_warehouse})

    if cint(apply_tax):
        _apply_sales_tax(doc)
    doc.insert(ignore_permissions=True)
    if cint(submit): doc.submit()
    _log("Delivery Note", doc.name, "create", customer)
    return doc.as_dict()


@frappe.whitelist()
def submit_delivery_note(name): doc = frappe.get_doc("Delivery Note", name); doc.submit(); return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def make_sales_return(delivery_note_name, submit=0):
    """Trả hàng bán → Return Delivery Note (đảo ngược tồn kho)."""
    from erpnext.controllers.sales_and_purchase_return import make_return_doc
    ret = make_return_doc("Delivery Note", delivery_note_name)
    ret.insert(ignore_permissions=True)
    if cint(submit):
        ret.submit()
    _log("Delivery Note", ret.name, "sales_return", delivery_note_name)
    return ret.as_dict()


@frappe.whitelist()
def make_credit_note(invoice_name, submit=0):
    """Credit Note (hóa đơn điều chỉnh giảm) → GL ngược: Dr 511 / Cr 131."""
    from erpnext.controllers.sales_and_purchase_return import make_return_doc
    cn = make_return_doc("Sales Invoice", invoice_name)
    cn.insert(ignore_permissions=True)
    if cint(submit):
        cn.submit()
    _log("Sales Invoice", cn.name, "credit_note", invoice_name)
    return cn.as_dict()


@frappe.whitelist()
def get_so_status(name):
    """Trạng thái thực tế của Sales Order: giao hàng / xuất hóa đơn."""
    so = frappe.get_doc("Sales Order", name)
    dns = frappe.get_all(
        "Delivery Note Item", filters={"against_sales_order": name},
        fields=["parent"], distinct=True,
    )
    dn_names = [d.parent for d in dns]
    delivery_notes = []
    for dn_name in dn_names:
        dn = frappe.db.get_value("Delivery Note", dn_name,
            ["name", "posting_date", "grand_total", "docstatus"], as_dict=True)
        if dn:
            delivery_notes.append(dn)

    si_refs = frappe.get_all(
        "Sales Invoice Item", filters={"sales_order": name},
        fields=["parent"], distinct=True,
    )
    si_names = [s.parent for s in si_refs]
    invoices = []
    for si_name in si_names:
        si = frappe.db.get_value("Sales Invoice", si_name,
            ["name", "posting_date", "grand_total", "outstanding_amount", "docstatus"], as_dict=True)
        if si:
            invoices.append(si)

    return {
        "name": so.name,
        "status": so.status,
        "per_delivered": flt(so.per_delivered),
        "per_billed": flt(so.per_billed),
        "grand_total": flt(so.grand_total),
        "delivery_notes": delivery_notes,
        "invoices": invoices,
    }


# ---------------------------------------------------------------------------
# HÓA ĐƠN BÁN (Sales Invoice) — công nợ 131
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_sales_invoices(search="", customer=None, status=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {"docstatus": ["!=", 2]}
    if customer: filters["customer"] = customer
    if status: filters["status"] = status
    or_filters = None
    if search: or_filters = [["name", "like", f"%{search}%"], ["customer_name", "like", f"%{search}%"]]
    total = frappe.db.count("Sales Invoice", filters)
    rows = frappe.get_all("Sales Invoice", filters=filters, or_filters=or_filters,
                          fields=["name", "customer", "customer_name", "grand_total", "outstanding_amount", "posting_date", "due_date", "docstatus"],
                          order_by="posting_date desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def get_sales_invoice(name):
    return frappe.get_doc("Sales Invoice", name).as_dict()


@frappe.whitelist()
def create_sales_invoice(customer, items, posting_date=None, due_date=None, apply_tax=1, submit=0):
    if isinstance(items, str): items = _json.loads(items)
    pd = getdate(posting_date) if posting_date else getdate(today())
    dd = getdate(due_date) if due_date else add_days(pd, 30)
    doc = frappe.new_doc("Sales Invoice"); doc.customer = customer; doc.company = _company(); doc.posting_date = pd; doc.due_date = dd
    for it in items: doc.append("items", {"item_code": it.get("item_code"), "qty": flt(it.get("qty")), "rate": flt(it.get("rate"))})
    if cint(apply_tax): _apply_sales_tax(doc)
    doc.insert(ignore_permissions=True)
    if cint(submit): doc.submit()
    _log("Sales Invoice", doc.name, "create", customer); return doc.as_dict()


@frappe.whitelist()
def submit_sales_invoice(name): doc = frappe.get_doc("Sales Invoice", name); doc.submit(); return {"name": doc.name, "docstatus": doc.docstatus, "outstanding": doc.outstanding_amount}


@frappe.whitelist()
def make_sales_invoice_from_dn(name, submit=0):
    from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice
    si = make_sales_invoice(name); si.insert(ignore_permissions=True)
    if cint(submit): si.submit()
    _log("Sales Invoice", si.name, "from_dn", name); return si.as_dict()


# ---------------------------------------------------------------------------
# CÔNG NỢ PHẢI THU + THANH TOÁN
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_receivables_summary():
    by_cust = {}
    for si in frappe.get_all("Sales Invoice", filters={"docstatus": 1, "outstanding_amount": [">", 0]},
                             fields=["name", "customer", "customer_name", "posting_date", "due_date", "grand_total", "outstanding_amount"], order_by="due_date asc"):
        d = by_cust.setdefault(si.customer, {"customer": si.customer, "customer_name": si.customer_name, "outstanding": 0, "invoices": []})
        d["outstanding"] += flt(si.outstanding_amount); d["invoices"].append(si)
    rows = sorted(by_cust.values(), key=lambda x: x["outstanding"], reverse=True)
    total = sum(r["outstanding"] for r in rows)
    return {"customers": rows, "total_outstanding": total, "count": len(rows)}


@frappe.whitelist()
def make_payment_receive(invoice, paid_to=None, submit=1):
    """Thu tiền KH → Payment Entry (Cr 131 / Dr tiền)."""
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    pe = get_payment_entry("Sales Invoice", invoice)
    cash = paid_to or _cash_account()
    if not cash: frappe.throw("Không tìm thấy tài khoản tiền")
    pe.paid_to = cash; pe.paid_to_account_currency = frappe.db.get_value("Account", cash, "account_currency") or "VND"
    if not pe.reference_no: pe.reference_no = pe.party_name or "TM"
    if not pe.reference_date: pe.reference_date = getdate(today())
    pe.insert(ignore_permissions=True)
    if cint(submit): pe.submit()
    _log("Payment Entry", pe.name, "receive_payment", invoice); return pe.as_dict()


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_sales_dashboard():
    c = _company(); fd = getdate(today()).replace(day=1)
    receivables = sum(v for v in _customer_outstanding_map().values())
    month_so = sum(flt(so.grand_total) for so in frappe.get_all("Sales Order", filters={"docstatus": 1, "transaction_date": [">=", fd]}, fields=["grand_total"]))

    # Doanh thu 6 tháng gần nhất (theo Sales Invoice đã ghi sổ)
    import collections
    rev = collections.OrderedDict()
    base = getdate(today()).replace(day=1)
    for i in range(5, -1, -1):
        m = (base.month - i - 1) % 12 + 1
        y = base.year + ((base.month - i - 1) // 12)
        rev[f"{m:02d}/{y}"] = 0.0
    for si in frappe.get_all("Sales Invoice", filters={"docstatus": 1, "posting_date": [">=", add_days(base, -185)]}, fields=["posting_date", "base_grand_total"]):
        k = f"{getdate(si.posting_date).month:02d}/{getdate(si.posting_date).year}"
        if k in rev: rev[k] += flt(si.base_grand_total)
    revenue_series = [{"month": k, "value": v} for k, v in rev.items()]

    # Top mặt hàng bán (90 ngày) theo doanh thu
    top = collections.defaultdict(float)
    for it in frappe.get_all("Sales Invoice Item",
            filters={"docstatus": 1, "creation": [">=", add_days(getdate(today()), -90)]},
            fields=["item_code", "item_name", "base_amount"], limit=2000):
        top[(it.item_code, it.item_name)] += flt(it.base_amount)
    top_items = [{"item_code": k[0], "item_name": k[1], "amount": v} for k, v in sorted(top.items(), key=lambda x: -x[1])[:5]]

    recent_so = frappe.get_all("Sales Order", filters={"docstatus": ["!=", 2]}, fields=["name", "customer_name", "grand_total", "status", "transaction_date"], order_by="creation desc", limit=6)
    for r in recent_so: r["status_vi"] = SO_STATUS_VI.get(r.status, r.status)

    return {"so_draft": frappe.db.count("Sales Order", {"docstatus": 0}), "so_this_month": month_so,
            "to_deliver": frappe.db.count("Sales Order", {"docstatus": 1, "per_delivered": ["<", 100]}),
            "to_bill": frappe.db.count("Sales Order", {"docstatus": 1, "per_billed": ["<", 100]}),
            "total_receivable": receivables, "si_unpaid": frappe.db.count("Sales Invoice", {"docstatus": 1, "outstanding_amount": [">", 0]}),
            "customer_count": frappe.db.count("Customer", {"disabled": 0}),
            "quotation_open": frappe.db.count("Quotation", {"docstatus": 1, "status": ["in", ["Submitted", "Open"]]}),
            "revenue_series": revenue_series, "top_items": top_items, "recent_so": recent_so}


# ---------------------------------------------------------------------------
# IN CHỨNG TỪ
# ---------------------------------------------------------------------------

def _print_doc(doctype, name, title, date_field):
    doc = frappe.get_doc(doctype, name); company = frappe.get_doc("Company", doc.company)
    rows = ""; total = 0.0
    for i, it in enumerate(doc.items, 1):
        amt = flt(it.amount); total += amt
        rows += f"<tr><td style='text-align:center'>{i}</td><td>{frappe.utils.escape_html(it.item_code)}</td><td>{frappe.utils.escape_html(it.item_name or '')}</td><td style='text-align:center'>{frappe.utils.escape_html(it.uom or it.stock_uom or '')}</td><td style='text-align:right'>{flt(it.qty):,.2f}</td><td style='text-align:right'>{_money(it.rate)}</td><td style='text-align:right'>{_money(amt)}</td></tr>"
    grand = flt(getattr(doc, "grand_total", total)); pdate = getattr(doc, date_field, None)
    return f"""<div style="font-family:'Times New Roman',serif;max-width:780px;margin:auto;padding:20px;color:#000">
<div style="text-align:center"><div style="font-weight:bold">{frappe.utils.escape_html(company.company_name)}</div></div>
<h2 style="text-align:center;margin:16px 0 4px">{title}</h2>
<div style="text-align:center;font-size:13px;margin-bottom:12px">Ngày {_vn_date(pdate)} · Số: {frappe.utils.escape_html(doc.name)}</div>
<div style="font-size:13px;margin-bottom:8px"><b>Khách hàng:</b> {frappe.utils.escape_html(doc.customer_name or doc.customer or '')}</div>
<table style="width:100%;border-collapse:collapse;font-size:13px" border="1"><thead><tr style="background:#f2f2f2"><th>STT</th><th>Mã hàng</th><th>Tên hàng</th><th>ĐVT</th><th>Số lượng</th><th>Đơn giá</th><th>Thành tiền</th></tr></thead>
<tbody>{rows}<tr style="font-weight:bold"><td colspan="6" style="text-align:right">Tổng cộng</td><td style="text-align:right">{_money(grand)}</td></tr></tbody></table>
<div style="display:flex;justify-content:space-around;margin-top:42px;font-size:13px;text-align:center"><div><b>Người lập</b><br>(Ký)</div><div><b>Khách hàng</b><br>(Ký)</div><div><b>Giám đốc</b><br>(Ký)</div></div></div>"""


@frappe.whitelist()
def print_quotation(name): return _print_doc("Quotation", name, "BÁO GIÁ", "transaction_date")


@frappe.whitelist()
def print_sales_order(name): return _print_doc("Sales Order", name, "ĐƠN ĐẶT HÀNG", "transaction_date")


@frappe.whitelist()
def print_delivery_note(name): return _print_doc("Delivery Note", name, "PHIẾU XUẤT GIAO HÀNG", "posting_date")


@frappe.whitelist()
def print_sales_invoice(name): return _print_doc("Sales Invoice", name, "HÓA ĐƠN BÁN HÀNG", "posting_date")


@frappe.whitelist()
def cancel_delivery_note(name): doc = frappe.get_doc("Delivery Note", name); doc.cancel(); return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def cancel_sales_invoice(name): doc = frappe.get_doc("Sales Invoice", name); doc.cancel(); return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def get_doc_activity(doctype, name):
    """Dòng thời gian hoạt động (Comment/Version) cho ActivityTimeline — dùng chung mọi chứng từ."""
    rows = frappe.get_all("Comment",
        filters={"reference_doctype": doctype, "reference_name": name,
                 "comment_type": ["in", ["Comment", "Info", "Workflow", "Created", "Submitted", "Cancelled", "Updated"]]},
        fields=["content", "comment_by", "owner", "creation", "comment_type"], order_by="creation desc", limit=60)
    out = []
    for c in rows:
        out.append({"time": str(c.creation), "user": c.comment_by or c.owner,
                    "action": c.comment_type, "detail": frappe.utils.strip_html(c.content or "")})
    return out


# ---------------------------------------------------------------------------
# DOCUMENT LINKING
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_linked_docs(doctype, name):
    links = {"source": name, "doctype": doctype}
    if doctype == "Sales Order":
        links["delivery_notes"] = frappe.get_all("Delivery Note",
            filters={"docstatus": ["!=", 2]}, or_filters=[["items", "like", f"%{name}%"]],
            fields=["name", "customer_name", "grand_total", "posting_date", "docstatus"], limit=10)
        links["invoices"] = frappe.get_all("Sales Invoice",
            filters={"docstatus": ["!=", 2]}, or_filters=[["items", "like", f"%{name}%"]],
            fields=["name", "customer_name", "grand_total", "outstanding_amount", "posting_date", "docstatus"], limit=10)
    elif doctype == "Sales Invoice":
        links["payments"] = frappe.get_all("Payment Entry",
            filters={"docstatus": 1}, or_filters=[["references", "like", f"%{name}%"]],
            fields=["name", "paid_amount", "posting_date", "docstatus"], limit=10)
    elif doctype == "Delivery Note":
        links["sales_order"] = frappe.get_all("Sales Order",
            filters={"docstatus": ["!=", 2]}, or_filters=[["items", "like", f"%{name}%"]],
            fields=["name", "customer_name", "grand_total", "transaction_date", "docstatus"], limit=5)
        links["invoices"] = frappe.get_all("Sales Invoice",
            filters={"docstatus": ["!=", 2]}, or_filters=[["items", "like", f"%{name}%"]],
            fields=["name", "customer_name", "grand_total", "outstanding_amount", "posting_date", "docstatus"], limit=10)
    return links


# Auto-fill price from Price List when creating SO/Quotation
@frappe.whitelist()
def get_selling_price(item_code, price_list="Standard Selling"):
    rate = frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": price_list}, "price_list_rate")
    return {"item_code": item_code, "rate": flt(rate) if rate else 0}


@frappe.whitelist()
def get_csrf_token():
    import frappe.sessions; return frappe.sessions.get_csrf_token()
