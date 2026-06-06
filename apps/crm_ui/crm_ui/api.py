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


@frappe.whitelist()
def setup_crm_integration():
    """Tạo custom field custom_crm_opportunity trên Customer doctype — idempotent."""
    if not frappe.db.exists("Custom Field", {"dt": "Customer", "fieldname": "custom_crm_opportunity"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Customer",
            "fieldname": "custom_crm_opportunity",
            "label": "CRM Opportunity",
            "fieldtype": "Link",
            "options": "Opportunity",
            "insert_after": "customer_group",
            "read_only": 1,
            "in_list_view": 0,
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    return {"ok": True}


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
    # Link ngược: ghi opportunity vào Customer nếu custom field tồn tại
    if frappe.db.exists("Custom Field", {"dt": "Customer", "fieldname": "custom_crm_opportunity"}):
        frappe.db.set_value("Customer", cust.name, "custom_crm_opportunity", name)
    _log("Opportunity", name, "to_customer", cust.name)
    return {"customer": cust.name, "customer_name": opp.title, "opportunity": name}


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
def get_customer_crm_context(customer_name):
    """Lấy Opportunity + Lead gốc của customer này — để module Kinh doanh hiển thị lịch sử CRM."""
    opp_name = frappe.db.get_value("Customer", customer_name, "custom_crm_opportunity")
    if not opp_name:
        # fallback: tìm theo title
        opp_name = frappe.db.get_value("Opportunity", {"party_name": customer_name, "status": "Closed Won"}, "name")
    if not opp_name:
        return {"opportunity": None, "lead": None}
    opp = frappe.get_doc("Opportunity", opp_name)
    lead = None
    if opp.get("lead"):
        lead = frappe.db.get_value("Lead", opp.lead, ["name", "lead_name", "email_id", "mobile_no", "source", "creation"], as_dict=True)
    return {
        "opportunity": {
            "name": opp.name, "title": opp.title,
            "opportunity_amount": flt(opp.opportunity_amount),
            "expected_closing": str(opp.expected_closing) if opp.expected_closing else None,
            "status": opp.status, "creation": str(opp.creation),
        },
        "lead": lead,
    }


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
    # Phễu Lead
    lead_funnel = [{"status": LEAD_STATUS_VI.get(s, s), "count": frappe.db.count("Lead", {"status": s})} for s in LEAD_STATUSES]
    # Giai đoạn cơ hội
    opp_stages = []
    for st in ["Open", "Qualification", "Needs Analysis", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]:
        cnt = frappe.db.count("Opportunity", {"status": st})
        if cnt:
            opp_stages.append({"stage": OPP_VI.get(st, st), "count": cnt})
    recent_leads = frappe.get_all("Lead", fields=["name", "lead_name", "status", "creation"], order_by="creation desc", limit=6)
    for r in recent_leads:
        r["status_vi"] = LEAD_STATUS_VI.get(r.status, r.status)
    return {"leads_total": frappe.db.count("Lead"), "leads_new": frappe.db.count("Lead", {"status": "Lead"}),
            "opportunities_total": frappe.db.count("Opportunity"), "opportunities_value": val,
            "customers_total": frappe.db.count("Customer"),
            "won_this_month": frappe.db.count("Opportunity", {"status": "Closed Won", "modified": [">=", get_first_day(today())]}),
            "open_activities": frappe.db.count("ToDo", {"status": "Open"}),
            "lead_funnel": lead_funnel, "opp_stages": opp_stages, "recent_leads": recent_leads}


# ---------------------------------------------------------------------------
# ACTIVITY TIMELINE (dùng chung)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_doc_activity(doctype, name):
    rows = frappe.get_all("Comment",
        filters={"reference_doctype": doctype, "reference_name": name,
                 "comment_type": ["in", ["Comment", "Info", "Created", "Updated"]]},
        fields=["content", "comment_by", "owner", "creation", "comment_type"], order_by="creation desc", limit=60)
    return [{"time": str(c.creation), "user": c.comment_by or c.owner, "action": c.comment_type,
             "detail": frappe.utils.strip_html(c.content or "")} for c in rows]


# ---------------------------------------------------------------------------
# CONTACTS (Liên hệ)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_contacts(search="", page=1, page_length=50):
    page, page_length = cint(page) or 1, cint(page_length) or 50
    or_filters = None
    if search:
        or_filters = [["first_name", "like", f"%{search}%"], ["email_id", "like", f"%{search}%"], ["mobile_no", "like", f"%{search}%"], ["company_name", "like", f"%{search}%"]]
    total = frappe.db.count("Contact")
    rows = frappe.get_all("Contact", or_filters=or_filters,
                          fields=["name", "first_name", "last_name", "email_id", "mobile_no", "company_name", "designation", "creation"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def get_contact(name):
    return frappe.get_doc("Contact", name).as_dict()


@frappe.whitelist()
def create_contact(first_name, last_name=None, email=None, mobile=None, company_name=None, designation=None):
    doc = frappe.new_doc("Contact")
    doc.first_name = first_name
    doc.last_name = last_name
    doc.company_name = company_name
    doc.designation = designation
    if email:
        doc.append("email_ids", {"email_id": email, "is_primary": 1})
    if mobile:
        doc.append("phone_nos", {"phone": mobile, "is_primary_mobile_no": 1})
    doc.insert(ignore_permissions=True)
    _log("Contact", doc.name, "create", first_name)
    return doc.as_dict()


# ---------------------------------------------------------------------------
# ACTIVITIES / FOLLOW-UP (ToDo + Communication)
# ---------------------------------------------------------------------------

ACT_TYPE_VI = {"call": "Gọi điện", "email": "Email", "meeting": "Họp", "task": "Công việc", "follow_up": "Theo dõi"}


@frappe.whitelist()
def get_activities(reference_doctype=None, reference_name=None, status=None, page=1, page_length=50):
    page, page_length = cint(page) or 1, cint(page_length) or 50
    filters = {}
    if reference_doctype and reference_name:
        filters["reference_type"] = reference_doctype
        filters["reference_name"] = reference_name
    if status:
        filters["status"] = status
    total = frappe.db.count("ToDo", filters)
    rows = frappe.get_all("ToDo", filters=filters,
                          fields=["name", "description", "status", "priority", "date", "allocated_to",
                                  "reference_type", "reference_name", "creation"],
                          order_by="date asc, creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "open": frappe.db.count("ToDo", dict(filters, status="Open")),
            "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def create_activity(description, date=None, priority="Medium", reference_doctype=None, reference_name=None, allocated_to=None):
    doc = frappe.new_doc("ToDo")
    doc.description = description
    doc.date = getdate(date) if date else getdate(today())
    doc.priority = priority
    doc.allocated_to = allocated_to or frappe.session.user
    if reference_doctype and reference_name:
        doc.reference_type = reference_doctype
        doc.reference_name = reference_name
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def complete_activity(name, reopen=0):
    frappe.db.set_value("ToDo", name, "status", "Open" if cint(reopen) else "Closed")
    return {"name": name, "status": "Open" if cint(reopen) else "Closed"}


# ---------------------------------------------------------------------------
# CAMPAIGNS (Chiến dịch)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_campaigns(search="", page=1, page_length=50):
    page, page_length = cint(page) or 1, cint(page_length) or 50
    or_filters = [["campaign_name", "like", f"%{search}%"]] if search else None
    total = frappe.db.count("Campaign")
    rows = frappe.get_all("Campaign", or_filters=or_filters,
                          fields=["name", "campaign_name", "creation"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    for r in rows:
        r["lead_count"] = frappe.db.count("Lead", {"campaign_name": r.name})
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def create_campaign(campaign_name, description=None):
    doc = frappe.new_doc("Campaign")
    doc.campaign_name = campaign_name
    if description and doc.meta.has_field("description"):
        doc.description = description
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def get_csrf_token():
    import frappe.sessions; return frappe.sessions.get_csrf_token()
