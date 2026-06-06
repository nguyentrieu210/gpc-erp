"""API cho Quản lý Tài sản cố định — reuse ERPNext Assets (Asset, Asset Category, Asset Movement,
Asset Depreciation, Asset Maintenance, Asset Repair, Asset Value Adjustment, Asset Capitalization).
KHÔNG tạo doctype mới."""

import frappe
import json as _json
from frappe.utils import flt, cint, getdate, today, add_months, add_days


def _company():
    return (frappe.defaults.get_user_default("Company") or
            frappe.db.get_single_value("Global Defaults", "default_company") or
            frappe.db.get_value("Company", {}, "name"))


def _money(v):
    try: return f"{flt(v):,.0f}".replace(",", ".")
    except: return str(v)


def _vn_date(d):
    if not d: return ""
    d = getdate(d); return f"{d.day:02d}/{d.month:02d}/{d.year}"


def _log(doctype, name, action, detail=""):
    try:
        user = frappe.session.user or "System"
        frappe.get_doc(doctype, name).add_comment("Comment", f"[{action}] {user}" + (f" — {detail}" if detail else ""))
    except Exception: pass


# ---------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------

@frappe.whitelist()
def setup_taisan():
    created = []
    for cat in ["Nhà cửa, vật kiến trúc", "Máy móc, thiết bị", "Phương tiện vận tải",
                 "Thiết bị văn phòng", "Phần mềm", "Tài sản cố định vô hình", "Tài sản khác"]:
        if not frappe.db.exists("Asset Category", cat):
            try:
                doc = frappe.new_doc("Asset Category")
                doc.asset_category_name = cat
                # Tự gán tài khoản TSCĐ mặc định theo TT200
                company = _company()
                fixed_asset = frappe.db.get_value("Account", {"company": company, "account_type": "Fixed Asset", "is_group": 0}, "name")
                acc_dep = frappe.db.get_value("Account", {"company": company, "account_type": "Accumulated Depreciation", "is_group": 0}, "name") \
                    or frappe.db.get_value("Account", {"company": company, "account_number": "214", "is_group": 0}, "name")
                dep_expense = frappe.db.get_value("Account", {"company": company, "account_type": "Depreciation", "is_group": 0}, "name") \
                    or frappe.db.get_value("Account", {"company": company, "account_number": "642", "is_group": 0}, "name")
                if fixed_asset or acc_dep or dep_expense:
                    doc.append("accounts", {"company_name": company, "fixed_asset_account": fixed_asset,
                                            "accumulated_depreciation_account": acc_dep,
                                            "depreciation_expense_account": dep_expense})
                doc.insert(ignore_permissions=True)
                created.append(cat)
            except Exception: pass
    frappe.db.commit()
    return {"categories_created": created, "status": get_setup_status()}


@frappe.whitelist()
def get_setup_status():
    c = _company()
    return {"company": c, "ready": True,
            "asset_count": frappe.db.count("Asset", {"company": c}),
            "category_count": frappe.db.count("Asset Category"),
            "location_count": frappe.db.count("Location")}


# ---------------------------------------------------------------------------
# ASSET CATEGORY
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_asset_categories():
    rows = frappe.get_all("Asset Category",
                          fields=["name", "asset_category_name"], order_by="asset_category_name asc")
    return {"entries": rows}


# ---------------------------------------------------------------------------
# ASSET CRUD
# ---------------------------------------------------------------------------

ASSET_STATUS_VI = {
    "Draft": "Nháp", "Submitted": "Đã ghi nhận", "Partially Depreciated": "Đang khấu hao",
    "Fully Depreciated": "Hết khấu hao", "Sold": "Đã bán", "Scrapped": "Đã hủy",
    "Renovated": "Đã nâng cấp", "Capitalized": "Đã tăng vốn",
}


@frappe.whitelist()
def get_assets(search="", category=None, status=None, location=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {"docstatus": ["!=", 2]}
    if category: filters["asset_category"] = category
    if status: filters["status"] = status
    if location: filters["location"] = location
    or_filters = None
    if search:
        or_filters = [["asset_name", "like", f"%{search}%"], ["name", "like", f"%{search}%"],
                       ["item_code", "like", f"%{search}%"]]
    total = frappe.db.count("Asset", filters)
    rows = frappe.get_all("Asset", filters=filters, or_filters=or_filters,
                          fields=["name", "asset_name", "asset_category", "item_code", "item_name",
                                  "status", "location", "purchase_amount", "purchase_date", "opening_accumulated_depreciation",
                                  "available_for_use_date", "creation"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    for r in rows:
        r["status_vi"] = ASSET_STATUS_VI.get(r.status, r.status)
        r["current_value"] = flt(r.purchase_amount) - flt(r.get("book_value", 0)) - flt(r.opening_accumulated_depreciation or 0)
        # Lấy giá trị sổ hiện tại
        try:
            sch = frappe.get_all("Depreciation Schedule", filters={"parent": r.name, "parenttype": "Asset"},
                                 fields=["accumulated_depreciation_amount"], order_by="schedule_date desc", limit=1)
            r["accumulated_depreciation"] = flt(sch[0].accumulated_depreciation_amount) if sch else flt(r.opening_accumulated_depreciation or 0)
            r["net_book_value"] = flt(r.purchase_amount) - r["accumulated_depreciation"]
        except Exception:
            r["net_book_value"] = flt(r.purchase_amount) - flt(r.opening_accumulated_depreciation or 0)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def get_asset(name):
    doc = frappe.get_doc("Asset", name).as_dict()
    # depreciation schedule
    doc["depreciation_schedule"] = frappe.get_all("Depreciation Schedule",
        filters={"parent": name, "parenttype": "Asset"},
        fields=["schedule_date", "depreciation_amount", "accumulated_depreciation_amount", "journal_entry"],
        order_by="schedule_date asc", limit_page_length=200)
    # movements
    doc["movements"] = frappe.get_all("Asset Movement",
        filters={"asset": name, "docstatus": ["!=", 2]},
        fields=["name", "transaction_date", "source_location", "target_location", "docstatus"],
        order_by="transaction_date desc", limit_page_length=20)
    # maintenance logs
    doc["maintenance_logs"] = frappe.get_all("Asset Maintenance Log",
        filters={"asset_name": name, "docstatus": ["!=", 2]},
        fields=["name", "maintenance_status", "task_name", "maintenance_type", "completion_date",
                "assign_to_name", "maintenance_team", "creation"],
        order_by="creation desc", limit_page_length=20)
    return doc


@frappe.whitelist()
def create_asset(asset_name, asset_category, item_code=None, gross_purchase_amount=0,
                 purchase_date=None, location=None, available_for_use_date=None, submit=0):
    company = _company()
    doc = frappe.new_doc("Asset")
    doc.asset_name = asset_name
    doc.asset_category = asset_category
    doc.item_code = item_code
    doc.company = company
    amt = flt(gross_purchase_amount)
    doc.purchase_amount = amt
    doc.net_purchase_amount = amt
    doc.purchase_date = getdate(purchase_date) if purchase_date else getdate(today())
    if available_for_use_date:
        doc.available_for_use_date = getdate(available_for_use_date)
    else:
        doc.available_for_use_date = getdate(today())
    if location:
        doc.location = location
    doc.calculate_depreciation = 1
    doc.is_existing_asset = 0 if item_code else 1

    # Set up default finance book với depreciation info
    doc.append("finance_books", {
        "depreciation_method": "Straight Line",
        "total_number_of_depreciations": 36,
        "frequency_of_depreciation": 12,
        "depreciation_start_date": getdate(available_for_use_date) if available_for_use_date else getdate(today()),
    })

    doc.insert(ignore_permissions=True)
    if cint(submit):
        doc.submit()
    _log("Asset", doc.name, "create", asset_name)
    return doc.as_dict()


@frappe.whitelist()
def submit_asset(name):
    doc = frappe.get_doc("Asset", name); doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def scrap_asset(name):
    """Ghi giảm / hủy tài sản."""
    doc = frappe.get_doc("Asset", name)
    doc.status = "Scrapped"; doc.save(ignore_permissions=True)
    _log("Asset", name, "scrapped")
    return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def sell_asset(name):
    """Đánh dấu tài sản đã bán."""
    doc = frappe.get_doc("Asset", name)
    doc.status = "Sold"; doc.save(ignore_permissions=True)
    _log("Asset", name, "sold")
    return {"name": doc.name, "status": doc.status}


# ---------------------------------------------------------------------------
# ASSET MOVEMENT (điều chuyển tài sản giữa các vị trí)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_asset_movements(search="", asset=None, page=1, page_length=50):
    page, page_length = cint(page) or 1, cint(page_length) or 50
    filters = {"docstatus": ["!=", 2]}
    if asset: filters["asset"] = asset
    total = frappe.db.count("Asset Movement", filters)
    rows = frappe.get_all("Asset Movement", filters=filters,
                          fields=["name", "asset", "transaction_date", "source_location", "target_location", "docstatus"],
                          order_by="transaction_date desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def create_asset_movement(asset, target_location, source_location=None, transaction_date=None):
    company = _company()
    doc = frappe.new_doc("Asset Movement")
    doc.company = company
    doc.append("assets", {"asset": asset, "source_location": source_location or "",
                           "target_location": target_location})
    doc.transaction_date = getdate(transaction_date) if transaction_date else getdate(today())
    doc.insert(ignore_permissions=True)
    doc.submit()
    _log("Asset Movement", doc.name, "move", f"{asset} → {target_location}")
    return doc.as_dict()


# ---------------------------------------------------------------------------
# LOCATIONS
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_locations(search="", page=1, page_length=50):
    page, page_length = cint(page) or 1, cint(page_length) or 50
    or_filters = [["location_name", "like", f"%{search}%"]] if search else None
    total = frappe.db.count("Location")
    rows = frappe.get_all("Location", or_filters=or_filters,
                          fields=["name", "location_name", "parent_location", "is_group"],
                          order_by="is_group desc, location_name asc", limit_page_length=page_length, start=(page - 1) * page_length)
    # Count assets per location
    for r in rows:
        r["asset_count"] = frappe.db.count("Asset", {"location": r.name, "docstatus": ["!=", 2]})
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def create_location(location_name, parent_location=None):
    doc = frappe.new_doc("Location")
    doc.location_name = location_name
    if parent_location: doc.parent_location = parent_location
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


# ---------------------------------------------------------------------------
# ASSET MAINTENANCE (bảo dưỡng/sửa chữa)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_maintenance_teams():
    return frappe.get_all("Asset Maintenance Team",
                          fields=["name", "maintenance_team_name", "maintenance_manager_name"],
                          order_by="maintenance_team_name asc", limit_page_length=0)


@frappe.whitelist()
def get_maintenance_logs(asset=None, team=None, status=None, page=1, page_length=50):
    page, page_length = cint(page) or 1, cint(page_length) or 50
    filters = {"docstatus": ["!=", 2]}
    if asset: filters["asset_name"] = asset
    if team: filters["maintenance_team"] = team
    if status: filters["maintenance_status"] = status
    total = frappe.db.count("Asset Maintenance Log", filters)
    rows = frappe.get_all("Asset Maintenance Log", filters=filters,
                          fields=["name", "asset_name", "maintenance_type", "maintenance_status",
                                  "task_name", "completion_date", "assign_to_name", "maintenance_team",
                                  "description", "creation"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def create_maintenance_log(asset_name, maintenance_type="Scheduled", task_name=None,
                           assign_to_name=None, maintenance_team=None, description=None):
    doc = frappe.new_doc("Asset Maintenance Log")
    doc.asset_name = asset_name
    doc.maintenance_type = maintenance_type
    doc.task_name = task_name
    doc.assign_to_name = assign_to_name
    doc.maintenance_team = maintenance_team
    doc.description = description
    doc.insert(ignore_permissions=True)
    _log("Asset", asset_name, "maintenance_log", task_name or "")
    return doc.as_dict()


# ---------------------------------------------------------------------------
# ASSET REPAIR (sửa chữa)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_asset_repairs(asset=None, status=None, page=1, page_length=50):
    page, page_length = cint(page) or 1, cint(page_length) or 50
    filters = {"docstatus": ["!=", 2]}
    if asset: filters["asset"] = asset
    if status: filters["repair_status"] = status
    total = frappe.db.count("Asset Repair")
    rows = frappe.get_all("Asset Repair", filters=filters,
                          fields=["name", "asset", "asset_name", "repair_status", "failure_date",
                                  "completion_date", "repair_cost", "description", "creation"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def create_asset_repair(asset, asset_name, failure_date=None, description=None, repair_cost=0):
    doc = frappe.new_doc("Asset Repair")
    doc.asset = asset
    doc.asset_name = asset_name
    doc.failure_date = getdate(failure_date) if failure_date else getdate(today())
    doc.description = description
    doc.repair_cost = flt(repair_cost)
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


# ---------------------------------------------------------------------------
# ASSET VALUE ADJUSTMENT (điều chỉnh giá trị tài sản)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_asset_value_adjustments(asset=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {"docstatus": ["!=", 2]}
    if asset: filters["asset"] = asset
    total = frappe.db.count("Asset Value Adjustment")
    rows = frappe.get_all("Asset Value Adjustment", filters=filters,
                          fields=["name", "asset", "date", "current_asset_value", "new_asset_value",
                                  "difference_amount", "journal_entry", "docstatus"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_dashboard():
    company = _company()

    def _sum(field):
        rows = frappe.get_all("Asset", filters={"company": company, "docstatus": 1},
                              fields=[field], limit_page_length=0)
        return sum(flt(r.get(field)) for r in rows)

    total_gross = _sum("purchase_amount")

    # Accumulated depreciation across all assets
    total_depr = 0.0
    for a in frappe.get_all("Asset", filters={"company": company, "docstatus": 1},
                            fields=["name", "opening_accumulated_depreciation", "purchase_amount"]):
        sch = frappe.get_all("Depreciation Schedule",
            filters={"parent": a.name, "parenttype": "Asset"},
            fields=["accumulated_depreciation_amount"], order_by="schedule_date desc", limit=1)
        if sch and flt(sch[0].accumulated_depreciation_amount) > 0:
            total_depr += flt(sch[0].accumulated_depreciation_amount)
        else:
            total_depr += flt(a.get("opening_accumulated_depreciation") or 0)

    # Status breakdown
    by_status = {}
    for s in ["Submitted", "Partially Depreciated", "Fully Depreciated", "Scrapped", "Sold"]:
        cnt = frappe.db.count("Asset", {"company": company, "docstatus": 1, "status": s})
        if cnt:
            by_status[ASSET_STATUS_VI.get(s, s)] = cnt

    # Depreciation this month
    ms = getdate(today()).replace(day=1)
    me = add_months(ms, 1)
    month_depr = 0.0
    for ds in frappe.get_all("Depreciation Schedule",
            filters={"parenttype": "Asset", "schedule_date": ["between", [ms, me]]},
            fields=["depreciation_amount"], limit_page_length=0):
        month_depr += flt(ds.depreciation_amount)

    # Recent assets
    recent = frappe.get_all("Asset", filters={"company": company, "docstatus": ["!=", 2]},
                            fields=["name", "asset_name", "asset_category", "status", "purchase_amount", "creation"],
                            order_by="creation desc", limit=6)
    for r in recent:
        r["status_vi"] = ASSET_STATUS_VI.get(r.status, r.status)

    return {
        "total_assets": frappe.db.count("Asset", {"company": company, "docstatus": 1}),
        "total_gross_value": total_gross,
        "total_accumulated_depreciation": total_depr,
        "net_book_value": total_gross - total_depr,
        "depreciation_this_month": month_depr,
        "category_count": frappe.db.count("Asset Category"),
        "location_count": frappe.db.count("Location"),
        "by_status": [{"status": k, "count": v} for k, v in by_status.items()],
        "recent_assets": recent,
    }


# ---------------------------------------------------------------------------
# ACTIVITY TIMELINE
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_doc_activity(doctype, name):
    rows = frappe.get_all("Comment",
        filters={"reference_doctype": doctype, "reference_name": name,
                 "comment_type": ["in", ["Comment", "Info", "Created", "Submitted", "Cancelled", "Updated"]]},
        fields=["content", "comment_by", "owner", "creation", "comment_type"], order_by="creation desc", limit=60)
    return [{"time": str(c.creation), "user": c.comment_by or c.owner, "action": c.comment_type,
             "detail": frappe.utils.strip_html(c.content or "")} for c in rows]


@frappe.whitelist()
def get_csrf_token():
    import frappe.sessions; return frappe.sessions.get_csrf_token()
