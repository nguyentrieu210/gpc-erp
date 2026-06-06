"""API mỏng cho Tài chính kế toán — reuse ERPNext Accounts (Journal Entry, GL Entry, Account).
Sổ cái, Bảng cân đối TK, Nhật ký chung, Báo cáo KQKD, Bảng CĐKT. KHÔNG tạo doctype mới."""

import frappe
import json as _json
from frappe.utils import flt, cint, getdate, today, nowdate, add_months, get_first_day, get_last_day


def _company():
    return (frappe.defaults.get_user_default("Company") or
            frappe.db.get_single_value("Global Defaults", "default_company") or
            frappe.db.get_value("Company", {}, "name"))


def _abbr(company=None):
    return frappe.db.get_value("Company", company or _company(), "abbr")


def _acct(number, company=None):
    return frappe.db.get_value("Account", {"company": company or _company(), "account_number": number}, "name")


def _money(v):
    try: return f"{flt(v):,.0f}".replace(",", ".")
    except: return str(v)


def _log(doctype, name, action, detail=""):
    try:
        user = frappe.session.user or "System"
        frappe.get_doc(doctype, name).add_comment("Comment", f"[{action}] {user}" + (f" — {detail}" if detail else ""))
    except Exception: pass


# ---------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------

@frappe.whitelist()
def setup_accounting():
    company = _company()
    return {"company": company, "ready": True, "status": get_accounting_setup_status()}


@frappe.whitelist()
def get_accounting_setup_status():
    c = _company()
    cd = frappe.get_doc("Company", c)
    return {"company": c, "abbr": _abbr(c), "ready": True,
            "gl_entry_count": frappe.db.count("GL Entry", {"is_cancelled": 0}),
            "je_count": frappe.db.count("Journal Entry"),
            "account_count": frappe.db.count("Account", {"company": c}),
            "fiscal_year": frappe.db.get_value("Fiscal Year", {"disabled": 0}, "name"),
            "default_currency": cd.default_currency}


# ---------------------------------------------------------------------------
# JOURNAL ENTRY
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_journal_entries(search="", from_date=None, to_date=None, docstatus=None, page=1, page_length=30):
    page, page_length = cint(page) or 1, cint(page_length) or 30
    filters = {}
    if docstatus is not None and docstatus != "": filters["docstatus"] = cint(docstatus)
    if from_date: filters["posting_date"] = [">=", getdate(from_date)]
    if to_date:
        if "posting_date" in filters: filters["posting_date"] = ["between", [getdate(from_date), getdate(to_date)]]
        else: filters["posting_date"] = ["<=", getdate(to_date)]
    or_filters = None
    if search: or_filters = [["name", "like", f"%{search}%"], ["user_remark", "like", f"%{search}%"]]
    total = frappe.db.count("Journal Entry", filters)
    rows = frappe.get_all("Journal Entry", filters=filters, or_filters=or_filters,
                          fields=["name", "total_debit", "total_credit", "posting_date", "docstatus", "user_remark", "cheque_no", "creation"],
                          order_by="posting_date desc, creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


@frappe.whitelist()
def get_journal_entry(name):
    d = frappe.get_doc("Journal Entry", name).as_dict()
    for a in d.get("accounts", []):
        a["account_name"] = frappe.db.get_value("Account", a["account"], "account_name")
    return d


@frappe.whitelist()
def create_journal_entry(accounts, posting_date=None, remark=None, submit=0):
    """Tạo bút toán. accounts: [{account, debit, credit, party_type?, party?}]"""
    if isinstance(accounts, str): accounts = _json.loads(accounts)
    company = _company()
    je = frappe.new_doc("Journal Entry")
    je.company = company
    je.posting_date = getdate(posting_date) if posting_date else getdate(today())
    je.user_remark = remark
    for a in accounts:
        je.append("accounts", {"account": a.get("account"), "debit_in_account_currency": flt(a.get("debit")),
                               "credit_in_account_currency": flt(a.get("credit")),
                               "party_type": a.get("party_type"), "party": a.get("party")})
    je.insert(ignore_permissions=True)
    if cint(submit): je.submit()
    _log("Journal Entry", je.name, "create_je", remark or "")
    return je.as_dict()


@frappe.whitelist()
def submit_journal_entry(name):
    doc = frappe.get_doc("Journal Entry", name); doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def cancel_journal_entry(name):
    doc = frappe.get_doc("Journal Entry", name); doc.cancel()
    return {"name": doc.name, "docstatus": doc.docstatus}


# ---------------------------------------------------------------------------
# GENERAL LEDGER (Sổ cái)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_gl_entries(account=None, from_date=None, to_date=None, voucher_type=None,
                   voucher_types=None, page=1, page_length=50):
    """
    voucher_type: string lọc 1 loại (backward compat)
    voucher_types: JSON array lọc nhiều loại, vd '["Sales Invoice","Payment Entry"]'
    """
    page, page_length = cint(page) or 1, cint(page_length) or 50
    filters = {"is_cancelled": 0}
    if account:
        filters["account"] = account

    # Handle voucher_type filter
    if voucher_types:
        vt_list = _json.loads(voucher_types) if isinstance(voucher_types, str) else voucher_types
        if vt_list:
            filters["voucher_type"] = ["in", vt_list]
    elif voucher_type:
        filters["voucher_type"] = voucher_type

    if from_date and to_date:
        filters["posting_date"] = ["between", [getdate(from_date), getdate(to_date)]]
    elif from_date:
        filters["posting_date"] = [">=", getdate(from_date)]
    elif to_date:
        filters["posting_date"] = ["<=", getdate(to_date)]

    total = frappe.db.count("GL Entry", filters)
    rows = frappe.get_all("GL Entry", filters=filters,
                          fields=["name", "account", "debit", "credit", "voucher_type", "voucher_no",
                                  "posting_date", "party_type", "party", "against", "remarks"],
                          order_by="posting_date desc, creation desc",
                          limit_page_length=page_length, start=(page - 1) * page_length)
    dr_total = sum(flt(r.debit) for r in rows)
    cr_total = sum(flt(r.credit) for r in rows)

    # Trả về danh sách voucher_type available để frontend filter
    available_types = frappe.get_all("GL Entry", filters={"is_cancelled": 0},
                                     fields=["voucher_type"], distinct=True, limit_page_length=0)

    return {
        "entries": rows,
        "total": total,
        "debit_total": dr_total,
        "credit_total": cr_total,
        "pages": ((total or 0) + page_length - 1) // page_length,
        "available_voucher_types": [r.voucher_type for r in available_types if r.voucher_type],
    }


@frappe.whitelist()
def get_gl_summary(from_date=None, to_date=None):
    """Tổng hợp GL theo voucher_type — overview nguồn phát sinh bút toán."""
    from collections import defaultdict
    filters = {"is_cancelled": 0}
    if from_date and to_date:
        filters["posting_date"] = ["between", [getdate(from_date), getdate(to_date)]]
    elif from_date:
        filters["posting_date"] = [">=", getdate(from_date)]
    elif to_date:
        filters["posting_date"] = ["<=", getdate(to_date)]

    rows = frappe.get_all("GL Entry", filters=filters,
                          fields=["voucher_type", "voucher_no", "debit", "credit"],
                          limit_page_length=0)

    summary = defaultdict(lambda: {"count": 0, "voucher_count": 0, "total_debit": 0.0, "total_credit": 0.0, "vouchers": set()})
    for r in rows:
        vt = r.voucher_type or "Khác"
        summary[vt]["count"] += 1
        summary[vt]["total_debit"] += flt(r.debit)
        summary[vt]["total_credit"] += flt(r.credit)
        summary[vt]["vouchers"].add(r.voucher_no)

    result = []
    for vt, data in sorted(summary.items(), key=lambda x: -x[1]["total_debit"]):
        result.append({
            "voucher_type": vt,
            "entry_count": data["count"],
            "voucher_count": len(data["vouchers"]),
            "total_debit": data["total_debit"],
            "total_credit": data["total_credit"],
        })

    total_debit = sum(r["total_debit"] for r in result)
    total_credit = sum(r["total_credit"] for r in result)
    return {"breakdown": result, "total_debit": total_debit, "total_credit": total_credit}


@frappe.whitelist()
def get_voucher_gl(voucher_type, voucher_no):
    """Tất cả GL entries của 1 chứng từ — drill-down từ SI/PI/Payment/Salary."""
    rows = frappe.get_all("GL Entry",
        filters={"voucher_type": voucher_type, "voucher_no": voucher_no, "is_cancelled": 0},
        fields=["name", "account", "debit", "credit", "party_type", "party",
                "against", "remarks", "posting_date", "cost_center"],
        order_by="creation asc")
    total_dr = sum(flt(r.debit) for r in rows)
    total_cr = sum(flt(r.credit) for r in rows)
    return {
        "voucher_type": voucher_type, "voucher_no": voucher_no,
        "entries": rows, "total_debit": total_dr, "total_credit": total_cr,
        "balanced": abs(total_dr - total_cr) < 0.01,
    }


@frappe.whitelist()
def get_account_statement(account, from_date, to_date):
    """Sổ chi tiết tài khoản: opening balance + transactions + closing balance.
    Quan trọng cho TK 131 (phải thu), 331 (phải trả), 334 (lương)."""
    company = _company()
    fd = getdate(from_date)
    td = getdate(to_date)

    # Opening balance: tổng GL trước from_date
    opening_rows = frappe.db.sql("""
        SELECT SUM(debit) as debit, SUM(credit) as credit
        FROM `tabGL Entry`
        WHERE account = %s AND company = %s AND posting_date < %s AND is_cancelled = 0
    """, (account, company, fd), as_dict=True)
    open_dr = flt(opening_rows[0].debit) if opening_rows else 0
    open_cr = flt(opening_rows[0].credit) if opening_rows else 0
    opening_balance = open_dr - open_cr

    # Transactions trong kỳ
    entries = frappe.get_all("GL Entry",
        filters={"account": account, "company": company,
                 "posting_date": ["between", [fd, td]], "is_cancelled": 0},
        fields=["name", "posting_date", "voucher_type", "voucher_no",
                "debit", "credit", "against", "party", "remarks"],
        order_by="posting_date asc, creation asc",
        limit_page_length=0)

    # Tính số dư lũy kế
    running = opening_balance
    for e in entries:
        running += flt(e.debit) - flt(e.credit)
        e["balance"] = running

    period_debit = sum(flt(e.debit) for e in entries)
    period_credit = sum(flt(e.credit) for e in entries)
    closing_balance = opening_balance + period_debit - period_credit

    return {
        "account": account,
        "from_date": str(fd),
        "to_date": str(td),
        "opening_balance": opening_balance,
        "entries": entries,
        "period_debit": period_debit,
        "period_credit": period_credit,
        "closing_balance": closing_balance,
    }


# ---------------------------------------------------------------------------
# CHART OF ACCOUNTS (browser)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_chart_of_accounts(root_type=None):
    company = _company()
    filters = {"company": company, "is_group": 0}
    if root_type: filters["root_type"] = root_type
    rows = frappe.get_all("Account", filters=filters,
                          fields=["name", "account_name", "account_number", "account_type", "root_type",
                                  "parent_account", "is_group"],
                          order_by="account_number asc, account_name asc", limit_page_length=0)
    groups = frappe.get_all("Account", filters={"company": company, "is_group": 1},
                            fields=["name", "account_name", "account_number", "root_type", "parent_account"],
                            order_by="account_number asc", limit_page_length=0)
    return {"accounts": rows, "groups": groups, "company": company}


# ---------------------------------------------------------------------------
# TRIAL BALANCE (Bảng cân đối TK phát sinh)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_trial_balance(from_date, to_date):
    company = _company()
    fd, td = getdate(from_date), getdate(to_date)
    filters = {"is_cancelled": 0, "company": company, "posting_date": ["between", [fd, td]]}
    gls = frappe.get_all("GL Entry", filters=filters,
                         fields=["account", "debit", "credit"], limit_page_length=0)
    by_acct = {}
    for g in gls:
        d = by_acct.setdefault(g.account, {"debit": 0.0, "credit": 0.0})
        d["debit"] += flt(g.debit); d["credit"] += flt(g.credit)
    rows = []
    total_dr, total_cr = 0.0, 0.0
    for acct, amt in by_acct.items():
        dr, cr = amt["debit"], amt["credit"]
        balance = dr - cr
        acc = frappe.db.get_value("Account", acct, ["account_name", "account_number", "root_type", "account_type"], as_dict=True) or {}
        rows.append({"account": acct, "account_name": acc.get("account_name", acct), "account_number": acc.get("account_number"),
                     "root_type": acc.get("root_type"), "debit": dr, "credit": cr, "balance": balance})
        total_dr += dr; total_cr += cr
    rows.sort(key=lambda r: (r.get("root_type") or "", r.get("account_number") or "", r["account"]))
    return {"rows": rows, "total_debit": total_dr, "total_credit": total_cr, "from_date": str(fd), "to_date": str(td),
            "balanced": abs(total_dr - total_cr) < 1, "count": len(rows)}


# ---------------------------------------------------------------------------
# P&L (Báo cáo KQKD)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_profit_loss(from_date, to_date):
    company = _company()
    fd, td = getdate(from_date), getdate(to_date)
    income = _account_balance_type(company, "Income", fd, td)
    expense = _account_balance_type(company, "Expense", fd, td)
    total_income = sum(v for v in income.values())
    total_expense = sum(v for v in expense.values())
    net = total_income - total_expense
    return {"income": _balance_rows(income), "expense": _balance_rows(expense),
            "total_income": total_income, "total_expense": total_expense, "net_profit": net,
            "from_date": str(fd), "to_date": str(td)}


def _account_balance_type(company, root_type, fd, td):
    accts = frappe.get_all("Account", filters={"company": company, "root_type": root_type, "is_group": 0}, pluck="name")
    by_acct = {}
    for a in accts:
        gl_sum = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE is_cancelled=0 AND account=%s AND posting_date BETWEEN %s AND %s", (a, fd, td))[0][0] or 0
        if abs(flt(gl_sum)) > 0.5: by_acct[a] = flt(gl_sum)
    return by_acct


def _balance_rows(bal_map):
    rows = []
    for acct, bal in sorted(bal_map.items(), key=lambda x: abs(x[1]), reverse=True):
        acc = frappe.db.get_value("Account", acct, ["account_name", "account_number"], as_dict=True) or {}
        rows.append({"account": acct, "account_name": acc.get("account_name", acct), "account_number": acc.get("account_number"), "balance": bal})
    return rows


# ---------------------------------------------------------------------------
# BALANCE SHEET (Bảng CĐKT) — snapshot
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_balance_sheet(as_of_date=None):
    company = _company()
    ad = getdate(as_of_date) if as_of_date else getdate(today())
    # từ đầu năm đến as_of_date
    fd = ad.replace(month=1, day=1)
    asset = _acct_balance_type(company, "Asset", fd, ad)
    liability = _acct_balance_type(company, "Liability", fd, ad)
    equity = _acct_balance_type(company, "Equity", fd, ad)
    total_asset = sum(v for v in asset.values())
    total_liability = sum(abs(v) for v in liability.values())
    total_equity = sum(abs(v) for v in equity.values())
    # net income (from P&L) goes into equity
    inc = _account_balance_type(company, "Income", fd, ad)
    exp = _account_balance_type(company, "Expense", fd, ad)
    net_income = sum(v for v in inc.values()) - sum(v for v in exp.values())
    return {"asset": _balance_rows(asset), "liability": _balance_rows(liability), "equity": _balance_rows(equity),
            "total_asset": total_asset, "total_liability": total_liability, "total_equity": total_equity + net_income,
            "net_income": net_income, "as_of_date": str(ad),
            "balanced": abs(total_asset - (total_liability + total_equity + net_income)) < 100}


def _acct_balance_type(company, root_type, fd, td):
    accts = frappe.get_all("Account", filters={"company": company, "root_type": root_type, "is_group": 0}, pluck="name")
    by_acct = {}
    for a in accts:
        gl_sum = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE is_cancelled=0 AND account=%s AND posting_date BETWEEN %s AND %s", (a, fd, td))[0][0] or 0
        if abs(flt(gl_sum)) > 0.5: by_acct[a] = flt(gl_sum)
    return by_acct


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_accounting_dashboard():
    company = _company()
    today = frappe.utils.getdate()
    month_start = today.replace(day=1)

    # Stats hiện tại
    je_count = frappe.db.count("Journal Entry", {"docstatus": 1, "company": company})
    draft_je = frappe.db.count("Journal Entry", {"docstatus": 0, "company": company})

    # GL stats tháng này
    gl_month = frappe.db.sql("""
        SELECT SUM(debit) as total_debit, SUM(credit) as total_credit, COUNT(*) as entry_count
        FROM `tabGL Entry`
        WHERE company = %s AND posting_date >= %s AND is_cancelled = 0
    """, (company, str(month_start)), as_dict=True)
    gl = gl_month[0] if gl_month else {}

    # 10 GL entries gần nhất từ mọi nguồn
    recent_vouchers = frappe.get_all("GL Entry",
        filters={"company": company, "is_cancelled": 0},
        fields=["voucher_type", "voucher_no", "posting_date", "debit", "credit", "account"],
        order_by="posting_date desc, creation desc",
        limit_page_length=10)

    # Breakdown theo voucher_type (tháng này)
    vt_rows = frappe.db.sql("""
        SELECT voucher_type, COUNT(DISTINCT voucher_no) as voucher_count, SUM(debit) as total_debit
        FROM `tabGL Entry`
        WHERE company = %s AND posting_date >= %s AND is_cancelled = 0
        GROUP BY voucher_type ORDER BY total_debit DESC
    """, (company, str(month_start)), as_dict=True)

    return {
        "je_submitted": je_count,
        "je_draft": draft_je,
        "gl_this_month": {
            "total_debit": flt(gl.get("total_debit")),
            "total_credit": flt(gl.get("total_credit")),
            "entry_count": cint(gl.get("entry_count")),
        },
        "recent_vouchers": recent_vouchers,
        "voucher_breakdown": vt_rows,
    }


# ---------------------------------------------------------------------------
# BANK RECONCILIATION (đối chiếu ngân hàng)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_bank_accounts(company=None):
    company = company or _company()
    return frappe.get_all("Bank Account", filters={"company": company, "disabled": 0},
                          fields=["name", "account_name", "account", "bank", "bank_account_no", "is_default", "account_type"],
                          order_by="is_default desc")


@frappe.whitelist()
def create_bank_account(account_name, account, bank=None, bank_account_no=None, is_default=0):
    company = _company()
    # Ensure Bank record exists if name provided
    bank_doc = None
    if bank and not frappe.db.exists("Bank", bank):
        try:
            bank_doc = frappe.get_doc({"doctype": "Bank", "bank_name": bank}).insert(ignore_permissions=True)
        except Exception: pass
    doc = frappe.new_doc("Bank Account")
    doc.account_name = account_name
    doc.account = account
    doc.company = company
    doc.bank = bank
    doc.bank_account_no = bank_account_no
    doc.is_default = cint(is_default)
    doc.is_company_account = 1
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def get_bank_clearance(bank_account, from_date=None, to_date=None):
    """Lấy danh sách Payment Entry chưa đối chiếu + đã đối chiếu cho TK ngân hàng."""
    company = _company()
    items = []
    pay_entries = frappe.get_all("Payment Entry",
        filters={"docstatus": 1, "bank_account": bank_account, "clearance_date": ["in", [None, ""]]},
        fields=["name", "party_name", "paid_amount", "reference_no", "reference_date", "posting_date", "mode_of_payment"],
        order_by="posting_date asc", limit_page_length=0,
    )
    for pe in pay_entries:
        items.append({"type": "Payment Entry", "name": pe.name, "party": pe.party_name or "",
                      "amount": flt(pe.paid_amount), "ref_no": pe.reference_no or "",
                      "ref_date": str(pe.reference_date) if pe.reference_date else "",
                      "posting_date": str(pe.posting_date), "mode": pe.mode_of_payment or "",
                      "cleared": False})
    je_lines = frappe.get_all("Journal Entry Account",
        filters={"docstatus": 1, "account": bank_account, "parenttype": "Journal Entry", "clearance_date": ["in", [None, ""]]},
        fields=["parent", "debit_in_account_currency as debit", "credit_in_account_currency as credit"],
        order_by="parent asc", limit_page_length=0,
    )
    for jl in je_lines:
        je = frappe.get_doc("Journal Entry", jl.parent)
        items.append({"type": "Journal Entry", "name": je.name, "party": je.user_remark or "",
                      "amount": flt(jl.debit or jl.credit), "ref_no": je.cheque_no or "",
                      "ref_date": str(je.posting_date), "posting_date": str(je.posting_date),
                      "mode": "", "cleared": False})
    # Sorted items
    items.sort(key=lambda x: x["posting_date"])
    total_uncleared = sum(it["amount"] for it in items)
    return {"bank_account": bank_account, "items": items, "count": len(items), "total_uncleared": total_uncleared}


@frappe.whitelist()
def submit_bank_clearance(bank_account, from_date, to_date, entries):
    """Đối chiếu: tạo Bank Clearance và cập nhật clearance_date cho Payment Entry/Journal Entry."""
    if isinstance(entries, str): entries = _json.loads(entries)
    company = _company()
    fd, td = getdate(from_date), getdate(to_date)
    doc = frappe.new_doc("Bank Clearance")
    doc.account = bank_account
    doc.bank_account = bank_account
    doc.company = company
    doc.from_date = fd
    doc.to_date = td
    for e in entries:
        doc.append("payment_entries", {
            "payment_entry": e.get("name"), "against_account": bank_account,
            "cheque_number": e.get("ref_no", ""), "cheque_date": getdate(e.get("ref_date")) if e.get("ref_date") else fd,
            "amount": flt(e.get("amount")), "posting_date": getdate(e.get("posting_date")),
        })
    doc.insert(ignore_permissions=True)
    doc.submit()
    # Update clearance
    from frappe.utils import today as _today
    for e in entries:
        name, dtyp = e.get("name"), e.get("type")
        dtyp = dtyp or "Payment Entry"
        try:
            if dtyp == "Payment Entry" and frappe.db.exists("Payment Entry", name):
                frappe.db.set_value("Payment Entry", name, "clearance_date", _today())
            elif dtyp == "Journal Entry" and frappe.db.exists("Journal Entry", name):
                frappe.db.sql("UPDATE `tabJournal Entry Account` SET clearance_date=%s WHERE parent=%s AND account=%s",
                              (_today(), name, bank_account))
        except Exception: pass
    frappe.db.commit()
    return {"name": doc.name, "docstatus": doc.docstatus, "cleared": len(entries)}


@frappe.whitelist()
def get_bank_clearance_history(bank_account=None, page=1, page_length=20):
    page, page_length = cint(page) or 1, cint(page_length) or 20
    filters = {"docstatus": 1}
    if bank_account: filters["account"] = bank_account
    total = frappe.db.count("Bank Clearance", filters)
    rows = frappe.get_all("Bank Clearance", filters=filters,
                          fields=["name", "account", "from_date", "to_date", "docstatus", "creation"],
                          order_by="creation desc", limit_page_length=page_length, start=(page - 1) * page_length)
    return {"entries": rows, "total": total, "pages": ((total or 0) + page_length - 1) // page_length}


# ---------------------------------------------------------------------------
# WORKFLOW & APPROVAL (Duyệt chứng từ)
# ---------------------------------------------------------------------------

def _ensure_wf_state(state_name):
    if not frappe.db.exists("Workflow State", state_name):
        frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": state_name}).insert(ignore_permissions=True)

def _ensure_wf_action(action_name):
    if not frappe.db.exists("Workflow Action Master", action_name):
        frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action_name}).insert(ignore_permissions=True)

def _ensure_workflow(workflow_name, document_type, states, transitions):
    """Tạo Workflow idempotent."""
    if frappe.db.exists("Workflow", workflow_name):
        return frappe.get_doc("Workflow", workflow_name).name
    # Pre-create states & actions
    for s in states: _ensure_wf_state(s["state"])
    for t in transitions:
        _ensure_wf_state(t["state"])
        _ensure_wf_state(t["next_state"])
        _ensure_wf_action(t["action"])
    wf = frappe.new_doc("Workflow")
    wf.workflow_name = workflow_name
    wf.document_type = document_type
    wf.workflow_state_field = "workflow_state"
    wf.is_active = 1
    wf.override_status = 0
    for s in states:
        wf.append("states", {"state": s["state"], "doc_status": s.get("doc_status", "0"),
                             "allow_edit": s.get("allow_edit", "System Manager"),
                             "update_field": s.get("update_field") or ""})
    for t in transitions:
        wf.append("transitions", {"state": t["state"], "action": t["action"],
                                  "next_state": t["next_state"],
                                  "allowed": t.get("allowed", "System Manager"),
                                  "condition": t.get("condition") or ""})
    wf.insert(ignore_permissions=True)
    return wf.name


@frappe.whitelist()
def setup_workflows():
    """Tạo sẵn workflow duyệt cho PO, SO, JE."""
    created = []
    for wf_name, dt, states, trans in [
        ("PO Approval", "Purchase Order",
         [{"state": "Draft", "doc_status": "0", "allow_edit": "System Manager"},
          {"state": "Pending Approval", "doc_status": "1", "allow_edit": "System Manager"},
          {"state": "Approved", "doc_status": "1", "allow_edit": "System Manager"}],
         [{"state": "Draft", "action": "Submit", "next_state": "Pending Approval", "allowed": "System Manager"},
          {"state": "Pending Approval", "action": "Approve", "next_state": "Approved", "allowed": "System Manager"}]),
        ("SO Approval", "Sales Order",
         [{"state": "Draft", "doc_status": "0", "allow_edit": "System Manager"},
          {"state": "Pending Approval", "doc_status": "1", "allow_edit": "System Manager"},
          {"state": "Approved", "doc_status": "1", "allow_edit": "System Manager"}],
         [{"state": "Draft", "action": "Submit", "next_state": "Pending Approval", "allowed": "System Manager"},
          {"state": "Pending Approval", "action": "Approve", "next_state": "Approved", "allowed": "System Manager"}]),
        ("JE Approval", "Journal Entry",
         [{"state": "Draft", "doc_status": "0", "allow_edit": "System Manager"},
          {"state": "Pending Approval", "doc_status": "1", "allow_edit": "System Manager"},
          {"state": "Approved", "doc_status": "1", "allow_edit": "System Manager"}],
         [{"state": "Draft", "action": "Submit", "next_state": "Pending Approval", "allowed": "System Manager"},
          {"state": "Pending Approval", "action": "Approve", "next_state": "Approved", "allowed": "System Manager"}]),
    ]:
        try:
            n = _ensure_workflow(wf_name, dt, states, trans)
            created.append(n)
        except Exception as e:
            created.append(f"ERROR {wf_name}: {str(e)[:100]}")
    frappe.db.commit()
    return {"workflows_created": created, "count": len(created)}


@frappe.whitelist()
def get_workflows():
    return frappe.get_all("Workflow", fields=["name", "workflow_name", "document_type", "is_active"],
                          order_by="document_type asc")


@frappe.whitelist()
def get_document_workflow_state(doctype, name):
    """Lấy trạng thái workflow hiện tại của 1 chứng từ."""
    if frappe.db.exists(doctype, name):
        wf_state = frappe.db.get_value(doctype, name, "workflow_state")
        return {"doctype": doctype, "name": name, "workflow_state": wf_state or "Draft"}
    return {"doctype": doctype, "name": name, "workflow_state": "Unknown"}


@frappe.whitelist()
def apply_workflow_action(doctype, name, action):
    """Thực hiện 1 hành động workflow: Submit, Approve, Reject."""
    from frappe.model.workflow import apply_workflow
    doc = frappe.get_doc(doctype, name)
    apply_workflow(doc, action)
    return {"doctype": doctype, "name": name, "action": action, "workflow_state": doc.workflow_state}


@frappe.whitelist()
def get_csrf_token():
    import frappe.sessions; return frappe.sessions.get_csrf_token()
