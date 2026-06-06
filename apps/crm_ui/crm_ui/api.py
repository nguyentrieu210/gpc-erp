"""API mỏng cho CRM — reuse ERPNext doctypes (Lead, Opportunity, Customer, Contact).
Full pipeline: Lead → Opportunity → Customer. Kanban pipeline. KHÔNG tạo doctype mới."""

import frappe
import json as _json
from frappe.utils import flt, cint, getdate, today, get_first_day


def _company():
    return (frappe.defaults.get_user_default("Company") or
            frappe.db.get_single_value("Global Defaults", "default_company") or
            frappe.db.get_value("Company", {}, "name"))


def _log(doctype, name, action, detail=""):
    try:
        frappe.get_doc(doctype, name).add_comment("Comment", f"[{action}] {frappe.session.user}" + (f" — {detail}" if detail else ""))
    except Exception: pass


# ---------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------

@frappe.whitelist()
def setup_crm():
    created = []
    for g in ["Khách hàng trong nước", "Khách hàng nước ngoài", "Đại lý", "Nhà phân phối"]:
        if not frappe.db.exists("Customer Group", g):
            try:
                frappe.get_doc({"doctype": "Customer Group", "customer_group_name": g,
                                "parent_customer_group": "All Customer Groups", "is_group": 0}).insert(ignore_permissions=True)
                created.append(g)
            except Exception: pass
    frappe.db.commit()
    return {"customer_groups_created": created, "status": get_crm_setup_status()}


@frappe.whitelist()
def get_crm_setup_status():
    return {"company": _company(), "ready": True, "customer_group_count": frappe.db.count("Customer Group", {"is_group": 0})}


# ---------------------------------------------------------------------------
# LEADS (ERPNext Lead)
# ---------------------------------------------------------------------------

LEAD_STATUSES = ["Lead", "Open", "Replied", "Opportunity", "Quotation", "Interested", "Converted", "Do Not Contact"]
LEAD_STATUS_VI = {"Lead": "Mới", "Open": "Mở", "Replied": "Đã LH", "Opportunity": "Cơ hội", "Quotation": "Báo giá",
                  "Lost Quotation": "Mất BG", "Interested": "Quan tâm", "Converted": "Đã chuyển", "Do Not Contact": "Ko LH"}


@frappe.whitelist()
def get_leads(search="", status=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {}
    if status: filters["status"] = status
    or_filters = None
    if search: or_filters = [["lead_name", "like", f"%{search}%"], ["email_id", "like", f"%{search}%"], ["mobile_no", "like", f"%{search}%"]]
    total = frappe.db.count("Lead", filters)
    rows = frappe.get_all("Lead", filters=filters, or_filters=or_filters,
                          fields=["name", "lead_name", "status", "email_id", "mobile_no", "company_name", "territory", "creation"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    for r in rows: r["status_vi"] = LEAD_STATUS_VI.get(r.status, r.status)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length), "page": page}


@frappe.whitelist()
def get_lead(name):
    return frappe.get_doc("Lead", name).as_dict()


@frappe.whitelist()
def create_lead(lead_name, email=None, mobile=None, company_name=None, status="Lead"):
    doc = frappe.get_doc({"doctype": "Lead", "lead_name": lead_name, "email_id": email,
                          "mobile_no": mobile, "company_name": company_name, "status": status})
    doc.insert(ignore_permissions=True)
    _log("Lead", doc.name, "create", lead_name)
    return doc.as_dict()


@frappe.whitelist()
def move_lead_status(name, status):
    if status not in LEAD_STATUSES: frappe.throw(f"Trạng thái không hợp lệ: {status}")
    frappe.db.set_value("Lead", name, "status", status)
    _log("Lead", name, "status", f"→ {status}")
    return {"name": name, "status": status}


@frappe.whitelist()
def convert_lead_to_opportunity(name):
    lead = frappe.get_doc("Lead", name)
    opp = frappe.get_doc({"doctype": "Opportunity", "opportunity_from": "Lead", "party_name": name,
                          "title": lead.lead_name, "contact_email": lead.email_id, "contact_mobile": lead.mobile_no})
    opp.insert(ignore_permissions=True)
    frappe.db.set_value("Lead", name, "status", "Opportunity")
    _log("Lead", name, "to_opportunity", opp.name)
    return opp.as_dict()


@frappe.whitelist()
def get_lead_dashboard():
    by_status = {}
    for s in LEAD_STATUSES: by_status[s] = frappe.db.count("Lead", {"status": s})
    return {"total": frappe.db.count("Lead"), "today": frappe.db.count("Lead", {"creation": [">=", frappe.utils.today()]}),
            "by_status": [{"status": LEAD_STATUS_VI.get(k, k), "count": v} for k, v in by_status.items()]}


# ---------------------------------------------------------------------------
# OPPORTUNITIES (ERPNext Opportunity)
# ---------------------------------------------------------------------------

OPP_VI = {"Qualification": "Đánh giá", "Needs Analysis": "Phân tích", "Proposal": "Đề xuất",
          "Negotiation": "Đàm phán", "Closed Won": "Thắng", "Closed Lost": "Thua"}


@frappe.whitelist()
def get_opportunities(status=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {}
    if status: filters["status"] = status
    total = frappe.db.count("Opportunity", filters)
    rows = frappe.get_all("Opportunity", filters=filters,
                          fields=["name", "title", "status", "party_name", "opportunity_amount",
                                  "expected_closing", "creation"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    for r in rows: r["stage_vi"] = OPP_VI.get(r.status, r.status)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def get_opportunity(name):
    return frappe.get_doc("Opportunity", name).as_dict()


@frappe.whitelist()
def create_opportunity(title, party_name=None, opportunity_amount=0, expected_closing=None):
    doc = frappe.get_doc({"doctype": "Opportunity", "title": title,
                          "party_name": party_name, "opportunity_amount": flt(opportunity_amount),
                          "expected_closing": getdate(expected_closing) if expected_closing else None})
    if party_name and frappe.db.exists("Lead", party_name): doc.opportunity_from = "Lead"
    doc.insert(ignore_permissions=True)
    _log("Opportunity", doc.name, "create", title)
    return doc.as_dict()


@frappe.whitelist()
def move_opportunity_status(name, status):
    frappe.db.set_value("Opportunity", name, "status", status)
    _log("Opportunity", name, "status", f"→ {status}")
    return {"name": name, "status": status}


@frappe.whitelist()
def convert_opportunity_to_customer(name):
    opp = frappe.get_doc("Opportunity", name)
    cust = frappe.get_doc({"doctype": "Customer", "customer_name": opp.title,
                           "customer_group": "Commercial", "customer_type": "Company", "territory": "All Territories"})
    cust.insert(ignore_permissions=True)
    frappe.db.set_value("Opportunity", name, "status", "Closed Won")
    _log("Opportunity", name, "to_customer", cust.name)
    return cust.as_dict()


@frappe.whitelist()
def get_opportunity_dashboard():
    by_status = {}
    total_val = 0.0
    for st in ["Open", "Qualification", "Needs Analysis", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]:
        cnt = frappe.db.count("Opportunity", {"status": st})
        val = sum(flt(o.opportunity_amount) for o in frappe.get_all("Opportunity", {"status": st}, ["opportunity_amount"]))
        total_val += val
        if cnt > 0: by_status[OPP_VI.get(st, st)] = {"count": cnt, "value": val}
    return {"total": frappe.db.count("Opportunity"), "total_value": total_val,
            "by_stage": [{"stage": k, "count": v["count"], "value": v["value"]} for k, v in by_status.items()]}


# ---------------------------------------------------------------------------
# CUSTOMERS
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_customers(search="", group=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {}
    if group: filters["customer_group"] = group
    or_filters = None
    if search: or_filters = [["customer_name", "like", f"%{search}%"], ["name", "like", f"%{search}%"]]
    total = frappe.db.count("Customer", filters)
    rows = frappe.get_all("Customer", filters=filters, or_filters=or_filters,
                          fields=["name", "customer_name", "customer_type", "customer_group", "territory", "tax_id", "disabled", "creation"],
                          order_by="customer_name asc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def get_customer(name):
    d = frappe.get_doc("Customer", name).as_dict()
    d["opportunities"] = frappe.get_all("Opportunity", filters={"party_name": name}, fields=["name", "title", "status", "opportunity_amount"], limit=20)
    return d


@frappe.whitelist()
def create_customer(customer_name, customer_type="Company", customer_group="Commercial", tax_id=None, mobile=None):
    doc = frappe.get_doc({"doctype": "Customer", "customer_name": customer_name, "customer_type": customer_type,
                          "customer_group": customer_group, "territory": "All Territories", "tax_id": tax_id})
    if mobile and doc.meta.has_field("mobile_no"): doc.mobile_no = mobile
    doc.insert(ignore_permissions=True)
    _log("Customer", doc.name, "create", customer_name)
    return doc.as_dict()


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_crm_dashboard():
    val = sum(flt(o.opportunity_amount) for o in frappe.get_all("Opportunity", {"status": ["not in", ["Closed Lost", "Closed Won"]]}, ["opportunity_amount"]))
    return {"leads_total": frappe.db.count("Lead"), "leads_new": frappe.db.count("Lead", {"status": "Lead"}),
            "opportunities_total": frappe.db.count("Opportunity"), "opportunities_value": val,
            "customers_total": frappe.db.count("Customer"), "won_this_month": frappe.db.count("Opportunity", {"status": "Closed Won", "modified": [">=", get_first_day(today())]})}


@frappe.whitelist()
def get_csrf_token():
    import frappe.sessions; return frappe.sessions.get_csrf_token()
