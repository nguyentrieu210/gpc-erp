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
def get_gl_entries(account=None, from_date=None, to_date=None, voucher_type=None, page=1, page_length=50):
    page, page_length = cint(page) or 1, cint(page_length) or 50
    filters = {"is_cancelled": 0}
    if account: filters["account"] = account
    if voucher_type: filters["voucher_type"] = voucher_type
    if from_date: filters["posting_date"] = [">=", getdate(from_date)]
    if to_date:
        if "posting_date" in filters: filters["posting_date"] = ["between", [getdate(from_date), getdate(to_date)]]
        else: filters["posting_date"] = ["<=", getdate(to_date)]
    total = frappe.db.count("GL Entry", filters)
    rows = frappe.get_all("GL Entry", filters=filters,
                          fields=["name", "account", "debit", "credit", "voucher_type", "voucher_no",
                                  "posting_date", "party_type", "party", "against", "remarks"],
                          order_by="posting_date asc, creation asc", limit_page_length=page_length, start=(page - 1) * page_length)
    dr_total = sum(flt(r.debit) for r in rows)
    cr_total = sum(flt(r.credit) for r in rows)
    return {"entries": rows, "total": total, "debit_total": dr_total, "credit_total": cr_total,
            "pages": ((total or 0) + page_length - 1) // page_length}


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
    c = _company()
    fd = getdate(today()).replace(day=1)
    td = getdate(today())
    month = _acct_balance_type(c, "Income", fd, td)
    return {"gl_count": frappe.db.count("GL Entry", {"is_cancelled": 0}), "je_count": frappe.db.count("Journal Entry"),
            "revenue_mtd": sum(v for v in month.values()), "account_count": frappe.db.count("Account", {"company": c, "is_group": 0})}


@frappe.whitelist()
def get_csrf_token():
    import frappe.sessions; return frappe.sessions.get_csrf_token()
