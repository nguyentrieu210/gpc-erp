"""API mỏng cho Kho — reuse ERPNext Stock (Item, Warehouse, Stock Entry,
Stock Reconciliation, Material Request, Bin, Stock Ledger Entry, Batch, Serial No).
Perpetual inventory + bút toán GL. KHÔNG tạo doctype mới.
Phong cách: giống module hr — wrapper @frappe.whitelist(), helper idempotent _ensure_*/setup_*."""

import frappe
import json as _json
from frappe.utils import flt, cint, getdate, today, nowdate

# ---------------------------------------------------------------------------
# Helpers chung
# ---------------------------------------------------------------------------

def _company():
    """Công ty mặc định của site."""
    return (
        frappe.defaults.get_user_default("Company")
        or frappe.db.get_single_value("Global Defaults", "default_company")
        or frappe.db.get_value("Company", {}, "name")
    )


def _abbr(company=None):
    return frappe.db.get_value("Company", company or _company(), "abbr")


def _acct(number, company=None):
    """Tìm Account theo account_number của TT200."""
    return frappe.db.get_value(
        "Account", {"company": company or _company(), "account_number": number}, "name"
    )


def _group_account(root_type, prefer_numbers, company=None):
    """Tài khoản nhóm (is_group=1) để làm cha — ưu tiên theo số hiệu, fallback group đầu tiên."""
    company = company or _company()
    for n in prefer_numbers:
        a = _acct(n, company)
        if a and frappe.db.get_value("Account", a, "is_group"):
            return a
    rows = frappe.get_all(
        "Account",
        filters={"company": company, "is_group": 1, "root_type": root_type},
        pluck="name",
        limit=1,
    )
    return rows[0] if rows else None


def _ensure_account(account_name, parent_account, root_type, account_type, account_number=None):
    """Tạo ledger account idempotent (theo account_name hoặc account_type)."""
    company = _company()
    if not parent_account:
        return None
    existing = frappe.db.get_value(
        "Account", {"company": company, "account_name": account_name, "is_group": 0}, "name"
    )
    if existing:
        return existing
    if account_type:
        byt = frappe.db.get_value(
            "Account", {"company": company, "account_type": account_type, "is_group": 0}, "name"
        )
        if byt:
            return byt
    try:
        doc = frappe.get_doc({
            "doctype": "Account",
            "account_name": account_name,
            "parent_account": parent_account,
            "company": company,
            "root_type": root_type,
            "account_type": account_type,
            "is_group": 0,
        })
        if account_number:
            doc.account_number = account_number
        doc.insert(ignore_permissions=True)
        return doc.name
    except Exception as e:
        frappe.log_error(title="kho _ensure_account", message=str(e)[:400])
        return None


def _log(doctype, name, action, detail=""):
    """Ghi comment hoạt động (an toàn, không vỡ luồng chính)."""
    try:
        user = frappe.session.user or "System"
        txt = f"[{action}] {user}" + (f" — {detail}" if detail else "")
        frappe.get_doc(doctype, name).add_comment("Comment", txt)
    except Exception:
        pass


def _check_perm(doctype, ptype="read"):
    """Kiểm tra quyền hạn của người dùng sử dụng Frappe framework."""
    if not frappe.has_permission(doctype, ptype):
        frappe.throw(
            f"Bạn không có quyền thực hiện thao tác này ({ptype} trên {doctype})",
            frappe.PermissionError
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


# ---------------------------------------------------------------------------
# 0. SETUP — perpetual inventory + tài khoản kho + kho/nhóm hàng/đơn vị (idempotent)
# ---------------------------------------------------------------------------

DEFAULT_WAREHOUSES_VI = ["Kho chính", "Kho nguyên vật liệu", "Kho thành phẩm", "Kho hàng hóa"]
ITEM_GROUPS_VI = ["Hàng hóa", "Nguyên vật liệu", "Thành phẩm", "Công cụ dụng cụ", "Vật tư tiêu hao", "Dịch vụ"]
UOMS_VI = [
    "Cái", "Chiếc", "Bộ", "Hộp", "Thùng", "Gói", "Kg", "Gram", "Tấn", "Lít",
    "Mét", "Mét vuông", "Mét khối", "Đôi", "Cuộn", "Tấm", "Lon", "Chai", "Túi",
    "Bao", "Viên", "Lốc", "Can", "Vỉ", "Ream", "Quyển",
]


def _ensure_company_stock_accounts():
    """Bật perpetual inventory + gán đủ tài khoản kho lên Company (TT200)."""
    company = _company()
    cdoc = frappe.get_doc("Company", company)
    changed = []

    # Tài khoản tồn kho mặc định -> 1561 (Giá mua hàng hóa) nếu hiện đang trống/sai
    inv = _acct("1561", company) or _acct("1551", company) or cdoc.default_inventory_account
    if inv and not frappe.db.get_value("Account", inv, "is_group"):
        if cdoc.default_inventory_account != inv:
            cdoc.default_inventory_account = inv
            changed.append("default_inventory_account")

    # Tài khoản chênh lệch kho (Stock Adjustment) — Expense, dưới nhóm 642
    if not cdoc.stock_adjustment_account:
        parent = _group_account("Expense", ["642", "811"], company)
        adj = _ensure_account("Chênh lệch kho (Stock Adjustment)", parent, "Expense", "Stock Adjustment")
        if adj:
            cdoc.stock_adjustment_account = adj
            changed.append("stock_adjustment_account")

    # Hàng mua chưa có hóa đơn (SRBNB) — Liability, dưới nhóm 338 (phục vụ Mua hàng sau này)
    if cdoc.meta.has_field("stock_received_but_not_billed") and not cdoc.stock_received_but_not_billed:
        parent = _group_account("Liability", ["338", "331"], company)
        srbnb = _ensure_account(
            "Hàng mua chưa có hóa đơn (SRBNB)", parent, "Liability", "Stock Received But Not Billed"
        )
        if srbnb:
            cdoc.stock_received_but_not_billed = srbnb
            changed.append("stock_received_but_not_billed")

    # Giá vốn (632) làm expense mặc định
    if not cdoc.default_expense_account:
        cogs = _acct("632", company)
        if cogs:
            cdoc.default_expense_account = cogs
            changed.append("default_expense_account")

    if not cdoc.enable_perpetual_inventory:
        cdoc.enable_perpetual_inventory = 1
        changed.append("enable_perpetual_inventory")

    if changed:
        cdoc.save(ignore_permissions=True)

    return {
        "company": company,
        "changed": changed,
        "enable_perpetual_inventory": cdoc.enable_perpetual_inventory,
        "default_inventory_account": cdoc.default_inventory_account,
        "stock_adjustment_account": cdoc.stock_adjustment_account,
        "stock_received_but_not_billed": cdoc.get("stock_received_but_not_billed"),
        "default_expense_account": cdoc.default_expense_account,
        "cost_center": cdoc.cost_center,
    }


def _ensure_warehouses():
    company = _company()
    abbr = _abbr(company)
    inv = frappe.db.get_value("Company", company, "default_inventory_account")
    parent = frappe.db.get_value("Warehouse", {"company": company, "is_group": 1}, "name")
    created = []
    for wn in DEFAULT_WAREHOUSES_VI:
        full = f"{wn} - {abbr}"
        if not frappe.db.exists("Warehouse", full):
            try:
                w = frappe.get_doc({
                    "doctype": "Warehouse",
                    "warehouse_name": wn,
                    "company": company,
                    "parent_warehouse": parent,
                    "account": inv,
                })
                w.insert(ignore_permissions=True)
                created.append(w.name)
            except Exception as e:
                frappe.log_error(title="kho _ensure_warehouses", message=str(e)[:400])
    # Gán account cho kho lẻ còn trống
    for w in frappe.get_all(
        "Warehouse", filters={"company": company, "is_group": 0, "account": ["in", [None, ""]]}, pluck="name"
    ):
        try:
            frappe.db.set_value("Warehouse", w, "account", inv)
        except Exception:
            pass
    # Kho mặc định trong Stock Settings
    main = f"Kho chính - {abbr}"
    if frappe.db.exists("Warehouse", main):
        ss = frappe.get_single("Stock Settings")
        if not ss.default_warehouse:
            ss.default_warehouse = main
            ss.save(ignore_permissions=True)
    return created


def _ensure_item_groups():
    created = []
    for g in ITEM_GROUPS_VI:
        if not frappe.db.exists("Item Group", g):
            try:
                frappe.get_doc({
                    "doctype": "Item Group",
                    "item_group_name": g,
                    "parent_item_group": "All Item Groups",
                    "is_group": 0,
                }).insert(ignore_permissions=True)
                created.append(g)
            except Exception as e:
                frappe.log_error(title="kho item group", message=str(e)[:300])
    return created


def _ensure_uoms():
    created = []
    for u in UOMS_VI:
        if not frappe.db.exists("UOM", u):
            try:
                frappe.get_doc({"doctype": "UOM", "uom_name": u, "enabled": 1}).insert(ignore_permissions=True)
                created.append(u)
            except Exception:
                pass
    return created


@frappe.whitelist()
def setup_kho():
    """Cài đặt 1 lần (idempotent): perpetual inventory + tài khoản kho + kho/nhóm/đơn vị VN."""
    accounts = _ensure_company_stock_accounts()
    warehouses = _ensure_warehouses()
    item_groups = _ensure_item_groups()
    uoms = _ensure_uoms()
    clean_english_master_data()
    frappe.db.commit()
    return {
        "accounts": accounts,
        "warehouses_created": warehouses,
        "item_groups_created": item_groups,
        "uoms_created": uoms,
        "status": get_kho_setup_status(),
    }


@frappe.whitelist()
def get_kho_setup_status():
    company = _company()
    cdoc = frappe.get_doc("Company", company)
    cfg = {
        "company": company,
        "abbr": _abbr(company),
        "enable_perpetual_inventory": cdoc.enable_perpetual_inventory,
        "default_inventory_account": cdoc.default_inventory_account,
        "stock_adjustment_account": cdoc.stock_adjustment_account,
        "default_expense_account": cdoc.default_expense_account,
        "cost_center": cdoc.cost_center,
    }
    if cdoc.meta.has_field("stock_received_but_not_billed"):
        cfg["stock_received_but_not_billed"] = cdoc.stock_received_but_not_billed
    cfg["valuation_method"] = frappe.db.get_single_value("Stock Settings", "valuation_method")
    cfg["default_warehouse"] = frappe.db.get_single_value("Stock Settings", "default_warehouse")
    cfg["ready"] = bool(
        cdoc.enable_perpetual_inventory and cdoc.default_inventory_account and cdoc.stock_adjustment_account
    )
    cfg["warehouse_count"] = frappe.db.count("Warehouse", {"company": company, "is_group": 0})
    cfg["item_count"] = frappe.db.count("Item", {"disabled": 0})
    cfg["item_group_count"] = frappe.db.count("Item Group", {"is_group": 0})
    cfg["uom_count"] = frappe.db.count("UOM")
    return cfg


# ---------------------------------------------------------------------------
# 1. HÀNG HÓA (Item / Item Group / UOM / Brand)
# ---------------------------------------------------------------------------

def _default_item_group():
    for g in ["Hàng hóa", "Products", "All Item Groups"]:
        if frappe.db.exists("Item Group", g) and not frappe.db.get_value("Item Group", g, "is_group"):
            return g
    return frappe.db.get_value("Item Group", {"is_group": 0}, "name")


def _bin_map(item_codes):
    """Gộp tồn theo item_code từ Bin (Python, tránh hàm SQL dạng chuỗi bị chặn ở v16)."""
    out = {}
    if not item_codes:
        return out
    for b in frappe.get_all(
        "Bin", filters={"item_code": ["in", item_codes]}, fields=["item_code", "actual_qty", "stock_value"]
    ):
        d = out.setdefault(b.item_code, {"qty": 0.0, "value": 0.0})
        d["qty"] += flt(b.actual_qty)
        d["value"] += flt(b.stock_value)
    return out


@frappe.whitelist()
def get_items(search="", item_group=None, has_stock=None, include_disabled=0,
              sort_field="item_name", sort_dir="asc", page=1, page_length=30):
    _check_perm("Item", "read")
    page = cint(page) or 1
    page_length = cint(page_length) or 30
    filters = {}
    if not cint(include_disabled):
        filters["disabled"] = 0
    if item_group:
        filters["item_group"] = item_group
    or_filters = None
    if search:
        or_filters = [["item_name", "like", f"%{search}%"], ["item_code", "like", f"%{search}%"]]

    allowed = {"item_name", "item_code", "item_group", "valuation_rate", "creation"}
    sf = sort_field if sort_field in allowed else "item_name"
    sd = "desc" if str(sort_dir).lower() == "desc" else "asc"

    if or_filters:
        total = len(frappe.get_all("Item", filters=filters, or_filters=or_filters, pluck="name", limit_page_length=0))
    else:
        total = frappe.db.count("Item", filters)

    items = frappe.get_all(
        "Item",
        filters=filters,
        or_filters=or_filters,
        fields=["name", "item_code", "item_name", "item_group", "stock_uom", "valuation_rate",
                "is_stock_item", "disabled", "image", "brand", "has_batch_no", "has_serial_no", "creation"],
        order_by=f"{sf} {sd}",
        limit_page_length=page_length,
        start=(page - 1) * page_length,
    )
    bm = _bin_map([i.item_code for i in items])
    out = []
    for i in items:
        b = bm.get(i.item_code, {})
        i["actual_qty"] = b.get("qty", 0)
        i["stock_value"] = b.get("value", 0)
        if cint(has_stock) and not flt(i["actual_qty"]):
            continue
        out.append(i)
    pages = ((total or 0) + page_length - 1) // page_length
    return {"items": out, "total": total, "pages": pages, "page": page}


@frappe.whitelist()
def get_item(name):
    doc = frappe.get_doc("Item", name)
    d = doc.as_dict()
    bins = frappe.get_all(
        "Bin",
        filters={"item_code": doc.item_code},
        fields=["warehouse", "actual_qty", "reserved_qty", "ordered_qty", "projected_qty",
                "valuation_rate", "stock_value"],
    )
    d["stock_by_warehouse"] = bins
    d["total_qty"] = sum(flt(b.actual_qty) for b in bins)
    d["total_value"] = sum(flt(b.stock_value) for b in bins)
    d["uom_conversions"] = [{"uom": u.uom, "conversion_factor": u.conversion_factor} for u in doc.uoms]
    d["reorder_levels"] = [
        {"warehouse": r.warehouse, "warehouse_reorder_level": r.warehouse_reorder_level,
         "warehouse_reorder_qty": r.warehouse_reorder_qty, "material_request_type": r.material_request_type}
        for r in doc.reorder_levels
    ]
    return d


@frappe.whitelist()
def create_item(item_code=None, item_name=None, item_group=None, stock_uom="Cái", is_stock_item=1,
                valuation_rate=0, opening_stock=0, description=None, brand=None,
                valuation_method=None, has_batch_no=0, has_serial_no=0):
    _check_perm("Item", "create")
    ig = item_group or _default_item_group()
    if not frappe.db.exists("Item Group", ig):
        ig = _default_item_group()
    if not frappe.db.exists("UOM", stock_uom):
        stock_uom = frappe.db.get_value("UOM", {}, "name") or "Nos"
    doc = frappe.get_doc({
        "doctype": "Item",
        "item_code": item_code or item_name,
        "item_name": item_name or item_code,
        "item_group": ig,
        "stock_uom": stock_uom,
        "is_stock_item": cint(is_stock_item),
        "description": description,
        "has_batch_no": cint(has_batch_no),
        "has_serial_no": cint(has_serial_no),
    })
    if brand and frappe.db.exists("Brand", brand):
        doc.brand = brand
    if valuation_method:
        doc.valuation_method = valuation_method
    if flt(valuation_rate):
        doc.valuation_rate = flt(valuation_rate)
    if flt(opening_stock):
        doc.opening_stock = flt(opening_stock)

    # Standard ERPNext default accounts mapping based on TT200
    company = _company()
    inv_acct = None
    cogs_acct = _acct("632", company)
    inc_acct = _acct("5111", company) or _acct("511", company)
    
    if ig == "Hàng hóa":
        inv_acct = _acct("1561", company) or _acct("156", company)
    elif ig == "Nguyên vật liệu":
        inv_acct = _acct("152", company)
    elif ig == "Thành phẩm":
        inv_acct = _acct("1551", company) or _acct("155", company)
    elif ig == "Công cụ dụng cụ":
        inv_acct = _acct("1531", company) or _acct("153", company)
    elif ig == "Vật tư tiêu hao":
        inv_acct = _acct("152", company) or _acct("1531", company)
    elif ig == "Dịch vụ":
        inc_acct = _acct("5113", company) or _acct("511", company)

    if inv_acct or cogs_acct or inc_acct:
        default_row = {
            "company": company,
        }
        if inv_acct:
            default_row["default_inventory_account"] = inv_acct
        if cogs_acct:
            default_row["default_cogs_account"] = cogs_acct
            default_row["expense_account"] = cogs_acct
        if inc_acct:
            default_row["income_account"] = inc_acct
            
        doc.append("item_defaults", default_row)

    doc.insert(ignore_permissions=True)
    _log("Item", doc.name, "create_item", doc.item_name)
    return doc.as_dict()


WRITABLE_ITEM_FIELDS = {
    "item_name", "item_group", "stock_uom", "description", "brand", "valuation_rate",
    "valuation_method", "is_stock_item", "disabled", "has_batch_no", "has_serial_no",
    "min_order_qty", "safety_stock", "weight_per_unit", "shelf_life_in_days", "image",
}


@frappe.whitelist()
def update_item(name, **kwargs):
    doc = frappe.get_doc("Item", name)
    changed = []
    for k, v in kwargs.items():
        if k in WRITABLE_ITEM_FIELDS:
            if k == "brand" and v and not frappe.db.exists("Brand", v):
                continue
            doc.set(k, v)
            changed.append(k)
    doc.save(ignore_permissions=True)
    if changed:
        _log("Item", name, "update_item", ", ".join(changed))
    return doc.as_dict()


@frappe.whitelist()
def toggle_item_disabled(name, disabled=1):
    frappe.db.set_value("Item", name, "disabled", cint(disabled))
    return {"name": name, "disabled": cint(disabled)}


@frappe.whitelist()
def set_valuation_method(name, method):
    if method not in ("FIFO", "Moving Average", "LIFO"):
        frappe.throw("Phương pháp định giá không hợp lệ")
    frappe.db.set_value("Item", name, "valuation_method", method)
    return {"name": name, "valuation_method": method}


@frappe.whitelist()
def get_item_groups():
    return frappe.get_all(
        "Item Group", filters={"is_group": 0}, fields=["name", "item_group_name", "parent_item_group"],
        order_by="item_group_name asc",
    )


@frappe.whitelist()
def create_item_group(item_group_name, parent_item_group="All Item Groups"):
    if frappe.db.exists("Item Group", item_group_name):
        return {"name": item_group_name, "existed": True}
    doc = frappe.get_doc({
        "doctype": "Item Group", "item_group_name": item_group_name,
        "parent_item_group": parent_item_group, "is_group": 0,
    })
    doc.insert(ignore_permissions=True)
    return {"name": doc.name, "existed": False}


@frappe.whitelist()
def get_uoms(search=""):
    filters = {"enabled": 1}
    if search:
        filters["uom_name"] = ["like", f"%{search}%"]
    return frappe.get_all("UOM", filters=filters, fields=["name", "uom_name"], order_by="uom_name asc", limit_page_length=0)


@frappe.whitelist()
def create_uom(uom_name):
    if frappe.db.exists("UOM", uom_name):
        return {"name": uom_name, "existed": True}
    frappe.get_doc({"doctype": "UOM", "uom_name": uom_name, "enabled": 1}).insert(ignore_permissions=True)
    return {"name": uom_name, "existed": False}


@frappe.whitelist()
def get_brands():
    return frappe.get_all("Brand", fields=["name", "brand"], order_by="brand asc")


@frappe.whitelist()
def get_item_dashboard():
    company = _company()
    total = frappe.db.count("Item", {"disabled": 0})
    stock_items = frappe.db.count("Item", {"disabled": 0, "is_stock_item": 1})
    disabled = frappe.db.count("Item", {"disabled": 1})
    # giá trị tồn + cảnh báo tồn thấp
    total_value = 0.0
    for b in frappe.get_all("Bin", fields=["stock_value"]):
        total_value += flt(b.stock_value)
    low = len(get_reorder_items())
    return {
        "total_items": total,
        "stock_items": stock_items,
        "disabled_items": disabled,
        "total_stock_value": total_value,
        "low_stock_count": low,
        "warehouse_count": frappe.db.count("Warehouse", {"company": company, "is_group": 0}),
    }


# ---------------------------------------------------------------------------
# 2. KHO (Warehouse — tree)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_warehouses(include_disabled=0):
    _check_perm("Warehouse", "read")
    company = _company()
    filters = {"company": company}
    if not cint(include_disabled):
        filters["disabled"] = 0
    rows = frappe.get_all(
        "Warehouse", filters=filters,
        fields=["name", "warehouse_name", "warehouse_type", "is_group", "parent_warehouse",
                "account", "disabled", "company"],
        order_by="is_group desc, warehouse_name asc", limit_page_length=0,
    )
    # giá trị tồn mỗi kho (từ Bin)
    val = {}
    for b in frappe.get_all("Bin", fields=["warehouse", "stock_value", "actual_qty"]):
        d = val.setdefault(b.warehouse, {"value": 0.0, "qty": 0.0})
        d["value"] += flt(b.stock_value)
        d["qty"] += flt(b.actual_qty)
    for w in rows:
        v = val.get(w.name, {})
        w["stock_value"] = v.get("value", 0)
        w["total_qty"] = v.get("qty", 0)
    return rows


@frappe.whitelist()
def get_stock_accounts():
    _check_perm("Account", "read")
    company = _company()
    return frappe.get_all(
        "Account",
        filters={
            "company": company,
            "is_group": 0,
            "root_type": "Asset"
        },
        fields=["name", "account_name", "account_number"],
        order_by="account_number asc",
        limit_page_length=0
    )


@frappe.whitelist()
def create_warehouse(warehouse_name, parent_warehouse=None, warehouse_type=None, is_group=0, account=None):
    _check_perm("Warehouse", "create")
    company = _company()
    parent = parent_warehouse or frappe.db.get_value("Warehouse", {"company": company, "is_group": 1}, "name")
    
    inv = account
    if not inv and parent:
        inv = frappe.db.get_value("Warehouse", parent, "account")
    if not inv:
        inv = frappe.db.get_value("Company", company, "default_inventory_account")
        
    doc = frappe.get_doc({
        "doctype": "Warehouse", "warehouse_name": warehouse_name, "company": company,
        "parent_warehouse": parent, "is_group": cint(is_group),
        "warehouse_type": warehouse_type or None,
        "account": account or (None if cint(is_group) else inv),
    })
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def update_warehouse(name, warehouse_name=None, warehouse_type=None, account=None, is_group=None, parent_warehouse=None):
    _check_perm("Warehouse", "write")
    doc = frappe.get_doc("Warehouse", name)
    if warehouse_name:
        doc.warehouse_name = warehouse_name
    if warehouse_type is not None:
        doc.warehouse_type = warehouse_type or None
    if account is not None:
        doc.account = account or None
    if is_group is not None:
        doc.is_group = cint(is_group)
    if parent_warehouse is not None:
        doc.parent_warehouse = parent_warehouse or None
    doc.save(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def toggle_warehouse(name, disabled=1):
    _check_perm("Warehouse", "write")
    frappe.db.set_value("Warehouse", name, "disabled", cint(disabled))
    return {"name": name, "disabled": cint(disabled)}


@frappe.whitelist()
def get_warehouse_stock(warehouse):
    rows = frappe.get_all(
        "Bin", filters={"warehouse": warehouse, "actual_qty": ["!=", 0]},
        fields=["item_code", "actual_qty", "valuation_rate", "stock_value", "reserved_qty", "projected_qty"],
        order_by="stock_value desc", limit_page_length=0,
    )
    names = {r.item_code: r.item_code for r in rows}
    if names:
        for it in frappe.get_all("Item", filters={"item_code": ["in", list(names)]},
                                 fields=["item_code", "item_name", "stock_uom"]):
            names[it.item_code] = it
    for r in rows:
        it = names.get(r.item_code)
        if isinstance(it, dict) or hasattr(it, "item_name"):
            r["item_name"] = it.get("item_name")
            r["stock_uom"] = it.get("stock_uom")
    return rows


# ---------------------------------------------------------------------------
# 3. NHẬP / XUẤT / CHUYỂN KHO (Stock Entry)
# ---------------------------------------------------------------------------

SE_TYPES = {
    "Material Receipt": "Nhập kho",
    "Material Issue": "Xuất kho",
    "Material Transfer": "Chuyển kho",
    "Repack": "Đóng gói lại",
    "Manufacture": "Sản xuất",
}


@frappe.whitelist()
def get_stock_entry_types():
    return [{"value": k, "label": v} for k, v in SE_TYPES.items()]


@frappe.whitelist()
def get_stock_entries(search="", stock_entry_type=None, from_date=None, to_date=None,
                      docstatus=None, page=1, page_length=30):
    page = cint(page) or 1
    page_length = cint(page_length) or 30
    filters = {}
    if stock_entry_type:
        filters["stock_entry_type"] = stock_entry_type
    if docstatus is not None and docstatus != "":
        filters["docstatus"] = cint(docstatus)
    if from_date:
        filters["posting_date"] = [">=", getdate(from_date)]
    if to_date:
        filters.setdefault("posting_date", [">=", getdate("1900-01-01")])
        filters["posting_date"] = ["between", [getdate(from_date or "1900-01-01"), getdate(to_date)]]
    or_filters = None
    if search:
        or_filters = [["name", "like", f"%{search}%"], ["remarks", "like", f"%{search}%"]]
    total = frappe.db.count("Stock Entry", filters)
    rows = frappe.get_all(
        "Stock Entry", filters=filters, or_filters=or_filters,
        fields=["name", "stock_entry_type", "from_warehouse", "to_warehouse", "total_amount",
                "posting_date", "docstatus", "remarks", "creation"],
        order_by="posting_date desc, creation desc",
        limit_page_length=page_length, start=(page - 1) * page_length,
    )
    for r in rows:
        r["type_label"] = SE_TYPES.get(r.stock_entry_type, r.stock_entry_type)
    pages = ((total or 0) + page_length - 1) // page_length
    return {"entries": rows, "total": total, "pages": pages, "page": page}


@frappe.whitelist()
def get_stock_entry(name):
    doc = frappe.get_doc("Stock Entry", name)
    d = doc.as_dict()
    d["type_label"] = SE_TYPES.get(doc.stock_entry_type, doc.stock_entry_type)
    return d


@frappe.whitelist()
def create_stock_entry(stock_entry_type, items, from_warehouse=None, to_warehouse=None,
                       posting_date=None, remarks=None, submit=0):
    _check_perm("Stock Entry", "create")
    if isinstance(items, str):
        items = _json.loads(items)
    
    if not items:
        frappe.throw("Danh sách mặt hàng nhập/xuất không được để trống")
        
    company = _company()
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = stock_entry_type
    se.company = company
    if posting_date:
        se.set_posting_time = 1
        se.posting_date = getdate(posting_date)
    if from_warehouse:
        se.from_warehouse = from_warehouse
    if to_warehouse:
        se.to_warehouse = to_warehouse
    if remarks:
        se.remarks = remarks
        
    for it in items:
        code = it.get("item_code")
        qty = flt(it.get("qty"))
        if not code:
            frappe.throw("Mã hàng không được để trống trên các dòng chứng từ")
        if qty <= 0:
            frappe.throw(f"Số lượng nhập/xuất của mặt hàng {code} phải lớn hơn 0")
            
        item_meta = frappe.db.get_value("Item", code, ["is_stock_item", "disabled"], as_dict=True)
        if not item_meta:
            frappe.throw(f"Mặt hàng {code} không tồn tại trên hệ thống")
        if item_meta.disabled:
            frappe.throw(f"Mặt hàng {code} đã bị ngừng kinh doanh")
        if not item_meta.is_stock_item:
            frappe.throw(f"Mặt hàng {code} là dịch vụ, không quản lý tồn kho nên không thể nhập/xuất")

        row = {"item_code": code, "qty": qty}
        sw = it.get("s_warehouse") or from_warehouse
        tw = it.get("t_warehouse") or to_warehouse
        if stock_entry_type in ("Material Issue", "Material Transfer", "Repack") and sw:
            row["s_warehouse"] = sw
        if stock_entry_type in ("Material Receipt", "Material Transfer", "Repack") and tw:
            row["t_warehouse"] = tw
        if it.get("basic_rate") not in (None, ""):
            row["basic_rate"] = flt(it.get("basic_rate"))
        if it.get("uom"):
            row["uom"] = it.get("uom")
        se.append("items", row)
        
    se.insert(ignore_permissions=True)
    if cint(submit):
        _check_perm("Stock Entry", "submit")
        se.submit()
    _log("Stock Entry", se.name, "create_stock_entry", se.stock_entry_type)
    return se.as_dict()


@frappe.whitelist()
def submit_stock_entry(name):
    _check_perm("Stock Entry", "submit")
    doc = frappe.get_doc("Stock Entry", name)
    doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def cancel_stock_entry(name):
    _check_perm("Stock Entry", "cancel")
    doc = frappe.get_doc("Stock Entry", name)
    doc.cancel()
    return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def delete_stock_entry(name):
    _check_perm("Stock Entry", "delete")
    if frappe.db.get_value("Stock Entry", name, "docstatus") == 1:
        frappe.throw("Phiếu đã chốt — hãy hủy trước khi xóa")
    frappe.delete_doc("Stock Entry", name, ignore_permissions=True)
    return {"deleted": name}


# ---------------------------------------------------------------------------
# 4. KIỂM KÊ (Stock Reconciliation)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_recon_prefill(warehouse, item_group=None):
    """Lấy qty + định giá hiện tại của mọi hàng đang có tồn trong kho (để nhập số đếm thực)."""
    rows = frappe.get_all(
        "Bin", filters={"warehouse": warehouse}, fields=["item_code", "actual_qty", "valuation_rate"],
        order_by="item_code asc", limit_page_length=0,
    )
    out = []
    for r in rows:
        item = frappe.db.get_value("Item", r.item_code, ["item_name", "item_group", "stock_uom"], as_dict=True)
        if item_group and item and item.item_group != item_group:
            continue
        out.append({
            "item_code": r.item_code,
            "item_name": item.item_name if item else r.item_code,
            "stock_uom": item.stock_uom if item else None,
            "current_qty": flt(r.actual_qty),
            "valuation_rate": flt(r.valuation_rate),
            "qty": flt(r.actual_qty),
        })
    return out


@frappe.whitelist()
def create_stock_reconciliation(warehouse, items, posting_date=None, purpose="Stock Reconciliation", submit=0):
    _check_perm("Stock Reconciliation", "create")
    if isinstance(items, str):
        items = _json.loads(items)
        
    if not items:
        frappe.throw("Danh sách mặt hàng kiểm kê không được để trống")
    if not warehouse:
        frappe.throw("Vui lòng chọn Kho thực hiện kiểm kê")

    company = _company()
    doc = frappe.new_doc("Stock Reconciliation")
    doc.company = company
    doc.purpose = purpose
    if posting_date:
        doc.set_posting_time = 1
        doc.posting_date = getdate(posting_date)
        
    for it in items:
        code = it.get("item_code")
        if not code:
            frappe.throw("Mã hàng không được để trống trên dòng kiểm kê")
            
        item_meta = frappe.db.get_value("Item", code, ["is_stock_item", "disabled"], as_dict=True)
        if not item_meta:
            frappe.throw(f"Mặt hàng {code} không tồn tại trên hệ thống")
        if item_meta.disabled:
            frappe.throw(f"Mặt hàng {code} đã bị ngừng kinh doanh")
        if not item_meta.is_stock_item:
            frappe.throw(f"Mặt hàng {code} là dịch vụ, không quản lý kho nên không thể kiểm kê")

        doc.append("items", {
            "item_code": code,
            "warehouse": it.get("warehouse") or warehouse,
            "qty": flt(it.get("qty")),
            "valuation_rate": flt(it.get("valuation_rate")) or None,
        })
    doc.insert(ignore_permissions=True)
    if cint(submit):
        doc.submit()
    _log("Stock Reconciliation", doc.name, "create_recon", warehouse)
    return doc.as_dict()


@frappe.whitelist()
def get_stock_reconciliations(page=1, page_length=30):
    page = cint(page) or 1
    page_length = cint(page_length) or 30
    total = frappe.db.count("Stock Reconciliation")
    rows = frappe.get_all(
        "Stock Reconciliation",
        fields=["name", "purpose", "posting_date", "docstatus", "difference_amount", "creation"],
        order_by="posting_date desc, creation desc",
        limit_page_length=page_length, start=(page - 1) * page_length,
    )
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def submit_stock_reconciliation(name):
    doc = frappe.get_doc("Stock Reconciliation", name)
    doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus}


# ---------------------------------------------------------------------------
# 5. YÊU CẦU VẬT TƯ (Material Request)
# ---------------------------------------------------------------------------

MR_TYPES = {
    "Material Issue": "Xuất dùng",
    "Material Transfer": "Chuyển kho",
    "Purchase": "Mua hàng",
    "Manufacture": "Sản xuất",
}


@frappe.whitelist()
def get_material_request_types():
    return [{"value": k, "label": v} for k, v in MR_TYPES.items()]


@frappe.whitelist()
def create_material_request(material_request_type, items, schedule_date=None, warehouse=None, submit=0):
    _check_perm("Material Request", "create")
    if isinstance(items, str):
        items = _json.loads(items)
        
    if not items:
        frappe.throw("Danh sách mặt hàng yêu cầu vật tư không được để trống")
        
    company = _company()
    sched = getdate(schedule_date) if schedule_date else getdate(today())
    doc = frappe.new_doc("Material Request")
    doc.company = company
    doc.material_request_type = material_request_type
    doc.schedule_date = sched
    
    for it in items:
        code = it.get("item_code")
        qty = flt(it.get("qty"))
        if not code:
            frappe.throw("Mã hàng không được để trống trên dòng yêu cầu")
        if qty <= 0:
            frappe.throw(f"Số lượng yêu cầu của mặt hàng {code} phải lớn hơn 0")
            
        item_meta = frappe.db.get_value("Item", code, ["is_stock_item", "disabled"], as_dict=True)
        if not item_meta:
            frappe.throw(f"Mặt hàng {code} không tồn tại trên hệ thống")
        if item_meta.disabled:
            frappe.throw(f"Mặt hàng {code} đã bị ngừng kinh doanh")

        doc.append("items", {
            "item_code": code,
            "qty": qty,
            "schedule_date": sched,
            "warehouse": it.get("warehouse") or warehouse,
        })
    doc.insert(ignore_permissions=True)
    if cint(submit):
        doc.submit()
    _log("Material Request", doc.name, "create_mr", material_request_type)
    return doc.as_dict()


@frappe.whitelist()
def get_material_requests(material_request_type=None, status=None, page=1, page_length=30):
    page = cint(page) or 1
    page_length = cint(page_length) or 30
    filters = {}
    if material_request_type:
        filters["material_request_type"] = material_request_type
    if status:
        filters["status"] = status
    total = frappe.db.count("Material Request", filters)
    rows = frappe.get_all(
        "Material Request", filters=filters,
        fields=["name", "material_request_type", "status", "transaction_date", "schedule_date",
                "docstatus", "per_ordered", "creation"],
        order_by="transaction_date desc, creation desc",
        limit_page_length=page_length, start=(page - 1) * page_length,
    )
    for r in rows:
        r["type_label"] = MR_TYPES.get(r.material_request_type, r.material_request_type)
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def get_material_request(name):
    return frappe.get_doc("Material Request", name).as_dict()


@frappe.whitelist()
def submit_material_request(name):
    doc = frappe.get_doc("Material Request", name)
    doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus}


# ---------------------------------------------------------------------------
# 6. BÁO CÁO TỒN & SỔ KHO (Bin / Stock Ledger Entry)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_stock_balance(warehouse=None, item_code=None, item_group=None):
    filters = {}
    if warehouse:
        filters["warehouse"] = warehouse
    if item_code:
        filters["item_code"] = item_code
    bins = frappe.get_all(
        "Bin", filters=filters,
        fields=["item_code", "warehouse", "actual_qty", "reserved_qty", "projected_qty",
                "valuation_rate", "stock_value"],
        order_by="item_code asc", limit_page_length=0,
    )
    codes = list({b.item_code for b in bins})
    meta = {}
    if codes:
        for it in frappe.get_all("Item", filters={"item_code": ["in", codes]},
                                 fields=["item_code", "item_name", "item_group", "stock_uom"]):
            meta[it.item_code] = it
    out = []
    total_qty = 0.0
    total_value = 0.0
    for b in bins:
        m = meta.get(b.item_code)
        if item_group and (not m or m.item_group != item_group):
            continue
        if not flt(b.actual_qty) and not flt(b.stock_value):
            continue
        b["item_name"] = m.item_name if m else b.item_code
        b["item_group"] = m.item_group if m else None
        b["stock_uom"] = m.stock_uom if m else None
        total_qty += flt(b.actual_qty)
        total_value += flt(b.stock_value)
        out.append(b)
    return {"rows": out, "total_qty": total_qty, "total_value": total_value, "count": len(out)}


@frappe.whitelist()
def get_stock_ledger(item_code=None, warehouse=None, from_date=None, to_date=None, limit=200):
    """Thẻ kho — Stock Ledger Entry."""
    filters = {"is_cancelled": 0}
    if item_code:
        filters["item_code"] = item_code
    if warehouse:
        filters["warehouse"] = warehouse
    if from_date and to_date:
        filters["posting_date"] = ["between", [getdate(from_date), getdate(to_date)]]
    elif from_date:
        filters["posting_date"] = [">=", getdate(from_date)]
    elif to_date:
        filters["posting_date"] = ["<=", getdate(to_date)]
    rows = frappe.get_all(
        "Stock Ledger Entry", filters=filters,
        fields=["item_code", "warehouse", "posting_date", "posting_time", "voucher_type",
                "voucher_no", "actual_qty", "qty_after_transaction", "valuation_rate",
                "stock_value", "stock_value_difference"],
        order_by="posting_date asc, posting_time asc, creation asc",
        limit_page_length=cint(limit) or 200,
    )
    return rows


@frappe.whitelist()
def get_reorder_items():
    out = []
    reorders = frappe.get_all(
        "Item Reorder",
        fields=["parent", "warehouse", "warehouse_reorder_level", "warehouse_reorder_qty", "material_request_type"],
    )
    for r in reorders:
        proj = frappe.db.get_value("Bin", {"item_code": r.parent, "warehouse": r.warehouse}, "projected_qty") or 0
        if flt(proj) < flt(r.warehouse_reorder_level):
            item = frappe.db.get_value("Item", r.parent, ["item_name", "stock_uom"], as_dict=True)
            out.append({
                "item_code": r.parent,
                "item_name": item.item_name if item else r.parent,
                "stock_uom": item.stock_uom if item else None,
                "warehouse": r.warehouse,
                "reorder_level": flt(r.warehouse_reorder_level),
                "reorder_qty": flt(r.warehouse_reorder_qty),
                "projected_qty": flt(proj),
                "material_request_type": r.material_request_type,
            })
    return out


@frappe.whitelist()
def set_reorder_level(item_code, warehouse, reorder_level, reorder_qty, material_request_type="Purchase"):
    if not warehouse:
        frappe.throw("Vui lòng chọn Kho")
    
    reorder_level = flt(reorder_level)
    reorder_qty = flt(reorder_qty)
    
    if reorder_level < 0 or reorder_qty < 0:
        frappe.throw("Định mức tồn tối thiểu và Số lượng đặt lại không được nhỏ hơn 0")
        
    if reorder_level > 0 and reorder_qty <= 0:
        frappe.throw("Khi đặt định mức tồn tối thiểu > 0, Số lượng đặt lại bắt buộc phải lớn hơn 0")

    doc = frappe.get_doc("Item", item_code)
    found = None
    for r in doc.reorder_levels:
        if r.warehouse == warehouse:
            found = r
            break
    if not found:
        found = doc.append("reorder_levels", {"warehouse": warehouse})
    found.warehouse_reorder_level = reorder_level
    found.warehouse_reorder_qty = reorder_qty
    found.material_request_type = material_request_type
    doc.save(ignore_permissions=True)
    return {"item_code": item_code, "warehouse": warehouse}


@frappe.whitelist()
def get_stock_value_dashboard():
    company = _company()
    bins = frappe.get_all("Bin", fields=["item_code", "warehouse", "actual_qty", "stock_value"])
    total_value = sum(flt(b.stock_value) for b in bins)
    by_wh = {}
    by_item = {}
    for b in bins:
        by_wh[b.warehouse] = by_wh.get(b.warehouse, 0) + flt(b.stock_value)
        by_item[b.item_code] = by_item.get(b.item_code, 0) + flt(b.stock_value)
    top_items = sorted(by_item.items(), key=lambda x: x[1], reverse=True)[:10]
    top = []
    for code, v in top_items:
        if v <= 0:
            continue
        nm = frappe.db.get_value("Item", code, "item_name")
        top.append({"item_code": code, "item_name": nm or code, "stock_value": v})
    return {
        "total_stock_value": total_value,
        "total_items": frappe.db.count("Item", {"disabled": 0}),
        "warehouse_count": frappe.db.count("Warehouse", {"company": company, "is_group": 0}),
        "low_stock_count": len(get_reorder_items()),
        "by_warehouse": [{"warehouse": k, "stock_value": v} for k, v in
                         sorted(by_wh.items(), key=lambda x: x[1], reverse=True) if v > 0],
        "top_items": top,
    }


# ---------------------------------------------------------------------------
# 7. LÔ & SERIAL (Batch / Serial No)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_batches(item_code=None):
    filters = {}
    if item_code:
        filters["item"] = item_code
    return frappe.get_all(
        "Batch", filters=filters,
        fields=["name", "batch_id", "item", "expiry_date", "batch_qty", "disabled"],
        order_by="creation desc", limit_page_length=0,
    )


@frappe.whitelist()
def create_batch(item_code, batch_id=None, expiry_date=None):
    doc = frappe.get_doc({
        "doctype": "Batch", "item": item_code,
        "batch_id": batch_id, "expiry_date": getdate(expiry_date) if expiry_date else None,
    })
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def get_serial_nos(item_code=None, warehouse=None, status=None):
    filters = {}
    if item_code:
        filters["item_code"] = item_code
    if warehouse:
        filters["warehouse"] = warehouse
    if status:
        filters["status"] = status
    return frappe.get_all(
        "Serial No", filters=filters,
        fields=["name", "serial_no", "item_code", "warehouse", "status", "batch_no"],
        order_by="creation desc", limit_page_length=0,
    )


# ---------------------------------------------------------------------------
# 8. IN PHIẾU KHO MẪU VN
# ---------------------------------------------------------------------------

@frappe.whitelist()
def print_stock_entry(name):
    doc = frappe.get_doc("Stock Entry", name)
    company = frappe.get_doc("Company", doc.company)
    title = {
        "Material Receipt": "PHIẾU NHẬP KHO",
        "Material Issue": "PHIẾU XUẤT KHO",
        "Material Transfer": "PHIẾU CHUYỂN KHO",
        "Repack": "PHIẾU ĐÓNG GÓI LẠI",
        "Manufacture": "PHIẾU SẢN XUẤT",
    }.get(doc.stock_entry_type, "PHIẾU KHO")

    rows = ""
    total = 0.0
    for i, it in enumerate(doc.items, 1):
        amt = flt(it.amount)
        total += amt
        wh = it.t_warehouse or it.s_warehouse or ""
        rows += (
            f"<tr><td style='text-align:center'>{i}</td>"
            f"<td>{frappe.utils.escape_html(it.item_code)}</td>"
            f"<td>{frappe.utils.escape_html(it.item_name or '')}</td>"
            f"<td style='text-align:center'>{frappe.utils.escape_html(it.uom or it.stock_uom or '')}</td>"
            f"<td style='text-align:right'>{flt(it.qty):,.2f}</td>"
            f"<td style='text-align:right'>{_money(it.basic_rate)}</td>"
            f"<td style='text-align:right'>{_money(amt)}</td>"
            f"<td>{frappe.utils.escape_html(wh)}</td></tr>"
        )

    html = f"""
<div style="font-family:'Times New Roman',serif;max-width:760px;margin:auto;padding:20px;color:#000">
  <div style="display:flex;justify-content:space-between;font-size:13px">
    <div style="text-align:center">
      <div style="font-weight:bold">{frappe.utils.escape_html(company.company_name)}</div>
      <div>{frappe.utils.escape_html(company.get('address') or '')}</div>
    </div>
    <div style="text-align:center;font-size:12px">
      <div>Mẫu số 01-VT</div>
      <div>(Ban hành theo TT 200/2014/TT-BTC)</div>
    </div>
  </div>
  <h2 style="text-align:center;margin:18px 0 4px">{title}</h2>
  <div style="text-align:center;font-size:13px;margin-bottom:14px">
    Ngày {_vn_date(doc.posting_date)} &nbsp;·&nbsp; Số: {frappe.utils.escape_html(doc.name)}
  </div>
  <table style="width:100%;border-collapse:collapse;font-size:13px" border="1">
    <thead>
      <tr style="background:#f2f2f2">
        <th>STT</th><th>Mã hàng</th><th>Tên hàng</th><th>ĐVT</th>
        <th>Số lượng</th><th>Đơn giá</th><th>Thành tiền</th><th>Kho</th>
      </tr>
    </thead>
    <tbody>{rows}
      <tr style="font-weight:bold"><td colspan="6" style="text-align:right">Tổng cộng</td>
      <td style="text-align:right">{_money(total)}</td><td></td></tr>
    </tbody>
  </table>
  <div style="margin-top:8px;font-size:13px"><i>Lý do/Diễn giải: {frappe.utils.escape_html(doc.remarks or '')}</i></div>
  <div style="display:flex;justify-content:space-around;margin-top:40px;font-size:13px;text-align:center">
    <div><b>Người lập phiếu</b><br>(Ký, họ tên)</div>
    <div><b>Thủ kho</b><br>(Ký, họ tên)</div>
    <div><b>Kế toán trưởng</b><br>(Ký, họ tên)</div>
    <div><b>Giám đốc</b><br>(Ký, họ tên)</div>
  </div>
</div>
"""
    return html


# ---------------------------------------------------------------------------
# 10. ITEM PRICE & PRICE LIST (bảng giá)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_price_lists(buying=None, selling=None):
    filters = {}
    if cint(buying): filters["buying"] = 1
    if cint(selling): filters["selling"] = 1
    return frappe.get_all("Price List", filters=filters, fields=["name", "price_list_name", "currency", "buying", "selling", "enabled"], order_by="price_list_name asc")


@frappe.whitelist()
def get_item_prices(item_code, price_list=None):
    filters = {"item_code": item_code}
    if price_list: filters["price_list"] = price_list
    rows = frappe.get_all("Item Price", filters=filters, fields=["name", "price_list", "item_code", "item_name", "uom", "price_list_rate", "currency", "valid_from", "valid_upto"], order_by="price_list asc")
    return rows


@frappe.whitelist()
def create_item_price(item_code, price_list, price_list_rate, uom=None, valid_from=None, valid_upto=None):
    if frappe.db.exists("Item Price", {"item_code": item_code, "price_list": price_list, "uom": uom or frappe.db.get_value("Item", item_code, "stock_uom")}):
        doc = frappe.get_doc("Item Price", {"item_code": item_code, "price_list": price_list, "uom": uom or ""})
    else:
        doc = frappe.new_doc("Item Price")
    doc.item_code = item_code
    doc.price_list = price_list
    doc.price_list_rate = flt(price_list_rate)
    doc.currency = frappe.db.get_value("Price List", price_list, "currency") or "VND"
    if uom: doc.uom = uom
    if valid_from: doc.valid_from = getdate(valid_from)
    if valid_upto: doc.valid_upto = getdate(valid_upto)
    if not doc.name: doc.insert(ignore_permissions=True)
    else: doc.save(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def delete_item_price(name):
    if frappe.db.exists("Item Price", name):
        frappe.delete_doc("Item Price", name, ignore_permissions=True)
    return {"deleted": name}


@frappe.whitelist()
def get_item_price_for_so(item_code, price_list="Standard Selling"):
    """Tự động lấy giá bán khi tạo SO — dùng cho frontend auto-fill rate."""
    rate = frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": price_list}, "price_list_rate")
    return {"item_code": item_code, "price_list": price_list, "rate": flt(rate) if rate else 0}


@frappe.whitelist()
def get_item_price_for_po(item_code, price_list="Standard Buying"):
    """Tự động lấy giá mua khi tạo PO."""
    rate = frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": price_list}, "price_list_rate")
    return {"item_code": item_code, "price_list": price_list, "rate": flt(rate) if rate else 0}


# ---------------------------------------------------------------------------
# 11. ITEM VARIANT (hàng biến thể: size, màu...)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_item_attributes():
    rows = frappe.get_all("Item Attribute", fields=["name", "attribute_name", "numeric_values"], order_by="attribute_name asc")
    for r in rows:
        r["values"] = frappe.get_all("Item Attribute Value", filters={"parent": r.name}, pluck="attribute_value", order_by="idx asc")
    return rows


@frappe.whitelist()
def get_item_variants(item_code):
    """Lấy danh sách biến thể của 1 item template."""
    vattrs = frappe.get_all("Item Variant Attribute", filters={"variant_of": item_code}, fields=["parent", "attribute", "attribute_value"])
    items = {}
    for va in vattrs:
        items.setdefault(va.parent, {})[va.attribute] = va.attribute_value
    out = []
    for variant_name, attrs in items.items():
        it = frappe.db.get_value("Item", variant_name, ["item_name", "item_code", "stock_uom", "valuation_rate", "disabled"], as_dict=True) or {}
        out.append({"name": variant_name, "item_name": it.get("item_name", variant_name), "item_code": it.get("item_code"),
                    "valuation_rate": it.get("valuation_rate"), "stock_uom": it.get("stock_uom"), "disabled": it.get("disabled"),
                    "attributes": attrs})
    return out


@frappe.whitelist()
def create_item_variant(template_item_code, variant_name, item_code=None, attributes=None):
    """Tạo 1 biến thể từ item template. attributes: [{attribute, attribute_value}]"""
    if isinstance(attributes, str): attributes = _json.loads(attributes)
    if not frappe.db.get_value("Item", template_item_code, "has_variants"):
        frappe.db.set_value("Item", template_item_code, "has_variants", 1)
    doc = frappe.new_doc("Item")
    doc.variant_of = template_item_code
    doc.item_code = item_code or (template_item_code + "-" + (variant_name or "").replace(" ", "-"))
    doc.item_name = variant_name or doc.item_code
    doc.item_group = frappe.db.get_value("Item", template_item_code, "item_group")
    doc.stock_uom = frappe.db.get_value("Item", template_item_code, "stock_uom")
    if attributes:
        for a in attributes:
            doc.append("attributes", {"attribute": a.get("attribute"), "attribute_value": a.get("attribute_value")})
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


# ---------------------------------------------------------------------------
# Hạ tầng
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_csrf_token():
    import frappe.sessions
    return frappe.sessions.get_csrf_token()


@frappe.whitelist()
def clean_english_master_data():
	"""Dọn dẹp nhóm hàng Tiếng Anh và tắt các Đơn vị tính (UOM) Tiếng Anh không dùng đến."""
	# 1. Xóa các Item Group tiếng Anh nếu không có liên kết
	english_groups = ["Consumable", "Sub Assemblies", "Services", "Raw Material", "Products"]
	deleted_groups = []
	for g in english_groups:
		if frappe.db.exists("Item Group", g):
			if not frappe.db.count("Item", {"item_group": g}):
				try:
					frappe.delete_doc("Item Group", g, ignore_permissions=True)
					deleted_groups.append(g)
				except Exception:
					pass

	# 2. Tắt các Đơn vị tính (UOM) tiếng Anh, chỉ giữ lại các UOM tiếng Việt trong hệ thống
	keep_uoms = [
		"Cái", "Chiếc", "Bộ", "Hộp", "Thùng", "Gói", "Kg", "Gram", "Tấn", "Lít",
		"Mét", "Mét vuông", "Mét khối", "Đôi", "Cuộn", "Tấm", "Lon", "Chai", "Túi",
		"Bao", "Viên", "Lốc", "Can", "Vỉ", "Ream", "Quyển", "Nos", "Unit", "Box"
	]
	frappe.db.sql("UPDATE tabUOM SET enabled = 0 WHERE name NOT IN (%s)" % ", ".join(["%s"] * len(keep_uoms)), tuple(keep_uoms))
	frappe.db.sql("UPDATE tabUOM SET enabled = 1 WHERE name IN (%s)" % ", ".join(["%s"] * len(keep_uoms)), tuple(keep_uoms))
	
	frappe.db.commit()
	frappe.clear_cache(doctype="UOM")
	frappe.clear_cache(doctype="Item Group")
	
	return {
		"deleted_groups": deleted_groups,
		"uoms_enabled_count": frappe.db.count("UOM", {"enabled": 1})
	}


@frappe.whitelist()
def seed_kho_items():
	"""Thêm dữ liệu mẫu hàng hóa (seed items) tiếng Việt chuẩn cho phân hệ Kho."""
	items_data = [
		# 1. Hàng hóa
		{"item_code": "HH-001", "item_name": "Bàn làm việc gỗ sồi", "item_group": "Hàng hóa", "stock_uom": "Cái", "valuation_rate": 2500000},
		{"item_code": "HH-002", "item_name": "Ghế xoay văn phòng lưới", "item_group": "Hàng hóa", "stock_uom": "Cái", "valuation_rate": 1200000},
		{"item_code": "HH-003", "item_name": "Tủ tài liệu sắt 4 ngăn", "item_group": "Hàng hóa", "stock_uom": "Cái", "valuation_rate": 1800000},
		# 2. Nguyên vật liệu
		{"item_code": "NVL-001", "item_name": "Gỗ MDF phủ Melamine 18mm", "item_group": "Nguyên vật liệu", "stock_uom": "Tấm", "valuation_rate": 350000},
		{"item_code": "NVL-002", "item_name": "Sắt hộp mạ kẽm 40x40x1.4mm", "item_group": "Nguyên vật liệu", "stock_uom": "Cuộn", "valuation_rate": 180000},
		{"item_code": "NVL-003", "item_name": "Sơn PU bóng cao cấp", "item_group": "Nguyên vật liệu", "stock_uom": "Can", "valuation_rate": 450000},
		# 3. Thành phẩm
		{"item_code": "TP-001", "item_name": "Bàn làm việc nhân viên mẫu B01", "item_group": "Thành phẩm", "stock_uom": "Cái", "valuation_rate": 1500000},
		{"item_code": "TP-002", "item_name": "Tủ locker nhân viên 12 ngăn", "item_group": "Thành phẩm", "stock_uom": "Cái", "valuation_rate": 3200000},
		# 4. Công cụ dụng cụ
		{"item_code": "CCDC-001", "item_name": "Máy khoan cầm tay Bosch", "item_group": "Công cụ dụng cụ", "stock_uom": "Bộ", "valuation_rate": 1500000},
		{"item_code": "CCDC-002", "item_name": "Bộ tuốc nơ vít đa năng", "item_group": "Công cụ dụng cụ", "stock_uom": "Bộ", "valuation_rate": 250000},
		# 5. Vật tư tiêu hao
		{"item_code": "VTTH-001", "item_name": "Giấy in Double A A4 70gsm", "item_group": "Vật tư tiêu hao", "stock_uom": "Ream", "valuation_rate": 65000},
		{"item_code": "VTTH-002", "item_name": "Bút bi Thiên Long FO-03", "item_group": "Vật tư tiêu hao", "stock_uom": "Hộp", "valuation_rate": 80000},
		# 6. Dịch vụ
		{"item_code": "DV-001", "item_name": "Dịch vụ vận chuyển lắp đặt", "item_group": "Dịch vụ", "stock_uom": "Cái", "valuation_rate": 500000, "is_stock_item": 0},
	]

	created = []
	for it in items_data:
		if not frappe.db.exists("Item", it["item_code"]):
			doc_data = {
				"doctype": "Item",
				"item_code": it["item_code"],
				"item_name": it["item_name"],
				"item_group": it["item_group"],
				"stock_uom": it["stock_uom"],
				"is_stock_item": it.get("is_stock_item", 1),
				"valuation_rate": it["valuation_rate"],
				"description": f"Hàng hóa mẫu: {it['item_name']}"
			}
			try:
				doc = frappe.get_doc(doc_data)
				doc.insert(ignore_permissions=True)
				created.append(it["item_code"])
			except Exception as e:
				frappe.log_error(title="seed_kho_items fail", message=str(e))
	
	frappe.db.commit()
	return {"created_count": len(created), "created_items": created}


# ---------------------------------------------------------------------------
# 9. QR/BARCODE + CÂY KHO
# ---------------------------------------------------------------------------

@frappe.whitelist()
def generate_item_qr(item_code, size=4):
    """Tạo QR code PNG (base64) cho item_code — dùng để in nhãn dán. PIL có sẵn trong image."""
    try:
        import qrcode
    except ImportError:
        # fallback: trả data URI đơn giản (text QR)
        return {"barcode": item_code, "format": "text_only", "note": "Cài qrcode: pip install qrcode[pil]"}
    try:
        import io, base64
        img = qrcode.make(item_code)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        return {"barcode": item_code, "qr_base64": b64, "mime": "image/png"}
    except Exception as e:
        return {"barcode": item_code, "error": str(e)[:200]}


@frappe.whitelist()
def get_item_by_barcode(barcode):
    """Quét mã QR/Barcode → tìm item (theo item_code hoặc Item Barcode)."""
    if frappe.db.exists("Item", barcode):
        return get_item(barcode)
    ib = frappe.db.get_value("Item Barcode", barcode, ["parent", "barcode_type", "uom"], as_dict=True)
    if ib:
        it = get_item(ib.parent)
        it["matched_barcode"] = ib
        return it
    # fuzzy: search item_code LIKE
    items = frappe.get_all("Item", filters={"item_code": ["like", f"%{barcode}%"]}, fields=["name", "item_code", "item_name"])
    if items:
        return get_item(items[0].name)
    frappe.throw(f"Không tìm thấy mặt hàng với mã: {barcode}")


@frappe.whitelist()
def get_warehouse_tree():
    """Cây kho phân cấp (cha/con) + giá trị tồn + item count."""
    company = _company()
    all_wh = frappe.get_all("Warehouse", filters={"company": company},
                            fields=["name", "warehouse_name", "is_group", "parent_warehouse", "account", "disabled"],
                            order_by="is_group desc, warehouse_name asc", limit_page_length=0)
    # giá trị tồn + item count per warehouse
    val = {}
    items_count = {}
    for b in frappe.get_all("Bin", fields=["warehouse", "stock_value", "item_code"]):
        d = val.setdefault(b.warehouse, {"value": 0.0, "items": set()})
        d["value"] += flt(b.stock_value)
        d["items"].add(b.item_code)
    for w in all_wh:
        v = val.get(w.name, {"value": 0, "items": set()})
        w["stock_value"] = v["value"]
        w["item_count"] = len(v["items"]) if isinstance(v.get("items"), set) else 0
    # build tree
    by_parent = {}
    for w in all_wh:
        by_parent.setdefault(w.parent_warehouse or "__root__", []).append(w)
    def build_node(wh):
        children = [build_node(c) for c in by_parent.get(wh.name, [])]
        # aggregate children stats
        cv = sum(c.get("stock_value", 0) for c in children)
        ci = sum(c.get("item_count", 0) for c in children)
        return {"name": wh.name, "warehouse_name": wh.warehouse_name, "is_group": wh.is_group,
                "account": wh.account, "disabled": wh.disabled,
                "stock_value": (wh.stock_value or 0) + cv,
                "item_count": (wh.item_count or 0) + ci, "children": children}
    roots = [build_node(w) for w in by_parent.get("__root__", [])]
    return {"trees": roots, "total_warehouses": len(all_wh)}


# ---------------------------------------------------------------------------
# LANDED COST — phân bổ chi phí vào giá vốn (shipping/phí/insurance)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_landed_cost_vouchers(search="", page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {"docstatus": ["!=", 2], "company": _company()}
    or_filters = [["name", "like", f"%{search}%"]] if search else None
    total = frappe.db.count("Landed Cost Voucher", filters)
    rows = frappe.get_all("Landed Cost Voucher", filters=filters, or_filters=or_filters,
                          fields=["name", "distribute_charges_based_on", "total_taxes_and_charges", "posting_date", "docstatus"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def create_landed_cost(receipt_docs, charges, distribute_charges_based_on="Quantity", submit=1):
    if isinstance(receipt_docs, str): receipt_docs = _json.loads(receipt_docs)
    if isinstance(charges, str): charges = _json.loads(charges)
    company = _company()
    doc = frappe.new_doc("Landed Cost Voucher")
    doc.company = company
    doc.distribute_charges_based_on = distribute_charges_based_on
    for r in receipt_docs:
        doc.append("purchase_receipts", {"receipt_document_type": "Purchase Receipt", "receipt_document": r.get("name"), "supplier": r.get("supplier")})
    for c in charges:
        acct = _acct(c.get("account_number", "1561"), company) or c.get("account")
        doc.append("taxes", {"description": c.get("description"), "amount": flt(c.get("amount")),
                             "expense_account": acct or frappe.db.get_value("Account", {"account_type": "Expense Account", "is_group": 0, "company": company}, "name")})
    doc.insert(ignore_permissions=True)
    if cint(submit): doc.submit()
    return doc.as_dict()


# ---------------------------------------------------------------------------
# PICK LIST — chọn hàng từ kho để giao (từ SO hoặc Material Request)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_pick_lists(search="", page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {"docstatus": ["!=", 2], "company": _company()}
    or_filters = [["name", "like", f"%{search}%"]] if search else None
    total = frappe.db.count("Pick List", filters)
    rows = frappe.get_all("Pick List", filters=filters, or_filters=or_filters,
                          fields=["name", "purpose", "status", "docstatus", "creation"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": max(1, ((total or 0) + page_length - 1) // page_length)}


@frappe.whitelist()
def create_pick_list(items, locations, purpose="Delivery", submit=0):
    if isinstance(items, str): items = _json.loads(items)
    if isinstance(locations, str): locations = _json.loads(locations)
    company = _company()
    doc = frappe.new_doc("Pick List")
    doc.company = company; doc.purpose = purpose
    for it in items:
        doc.append("locations", {"item_code": it.get("item_code"), "qty": flt(it.get("qty")) or 1,
                                  "warehouse": it.get("warehouse"), "sales_order": it.get("sales_order")})
    doc.insert(ignore_permissions=True)
    if cint(submit): doc.submit()
    return doc.as_dict()


# ---------------------------------------------------------------------------
# BATCH EXPIRY ALERT — cảnh báo lô hết hạn
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_expiring_batches(days_ahead=30):
    """Batch sắp hết hạn trong N ngày tới."""
    from frappe.utils import add_days
    cutoff = add_days(today(), cint(days_ahead) or 30)
    rows = frappe.get_all("Batch", filters={"disabled": 0, "expiry_date": ["between", [today(), cutoff]]},
                          fields=["name", "batch_id", "item", "item_name", "expiry_date", "expiry_date", "batch_qty"],
                          order_by="expiry_date asc", limit_page_length=100)
    return {"batches": rows, "count": len(rows)}


@frappe.whitelist()
def get_negative_stock():
    """Mặt hàng có tồn âm (actual_qty < 0 trong Bin)."""
    rows = []
    for b in frappe.get_all("Bin", filters={"actual_qty": ["<", 0]},
                            fields=["item_code", "warehouse", "actual_qty", "stock_value"],
                            order_by="actual_qty asc", limit_page_length=50):
        rows.append({"item_code": b.item_code, "item_name": frappe.db.get_value("Item", b.item_code, "item_name"),
                     "warehouse": b.warehouse, "actual_qty": flt(b.actual_qty)})
    return {"items": rows, "count": len(rows)}


@frappe.whitelist()
def create_scrap_entry(item_code, qty, warehouse, rate=0, submit=1):
    """Phiếu hủy/sứt vỡ (Material Issue với Stock Entry)."""
    company = _company()
    wh_db = frappe.db.get_value("Warehouse", warehouse, "company")
    doc = frappe.new_doc("Stock Entry")
    doc.stock_entry_type = "Material Issue"
    doc.company = company
    doc.append("items", {"item_code": item_code, "qty": flt(qty), "s_warehouse": warehouse,
                          "basic_rate": flt(rate) or frappe.db.get_value("Item", item_code, "valuation_rate") or 0})
    doc.set_posting_time = 1
    doc.posting_date = today()
    doc.insert(ignore_permissions=True)
    if cint(submit): doc.submit()
    return doc.as_dict()


@frappe.whitelist()
def get_current_user():
    return {
        "name": frappe.session.user,
        "full_name": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
    }
