# API Security Audit - 2026-06-06

Scope: static review of whitelisted Frappe API functions in `apps/*/**/api.py`.

This is a triage report, not a full penetration test. It flags endpoints that appear to mutate data without an obvious permission check in the same function body, endpoints that use `ignore_permissions=True`, guest endpoints, manual commits, and direct SQL.

## Summary

| App | Whitelisted endpoints | Flagged endpoints | Main concern |
| --- | ---: | ---: | --- |
| `hr` | 137 | 60 | Many HR, payroll, recruitment, attendance, and onboarding mutations lack local permission checks. |
| `muahang` | 42 | 22 | Supplier, PO, PR, PI, receipt, payment mutations bypass permissions. |
| `kinhdoanh` | 33 | 16 | Customer, quotation, sales order, delivery, invoice, payment mutations bypass permissions. |
| `kho` | 52 | 13 | Has a permission helper, but some item/master/setup actions still bypass checks. |
| `crm_ui` | 19 | 6 | Lead, opportunity, customer creation/conversion bypass permissions. |
| `tckt` | 14 | 4 | Journal entry create/submit/cancel and setup need explicit permission checks. |
| `duan` | 8 | 1 | `update_task_status` needs explicit permission check. |
| `portal` | 4 | 1 | `get_my_modules` uses `ignore_permissions=True`; review data exposure. |
| `quantri` | 11 | 0 | Best current pattern; user management checks Frappe permissions. |

## Highest Priority Fixes

1. Add a shared permission helper to each business app, modeled after `kho._check_perm`.
2. Require explicit permission before every create/update/delete/submit/cancel/payment endpoint.
3. Remove `ignore_permissions=True` from normal user operations. Keep it only in setup/seed/admin-only functions after checking a high-privilege role.
4. Gate setup/seed/cleanup endpoints behind `System Manager` or a dedicated ERP admin role.
5. Add tests for unauthorized users against money, stock, payroll, and master-data mutation endpoints.

## App Notes

### `hr`

High risk because it touches employees, payroll, attendance, recruitment, offers, documents, onboarding, and AI helpers. Many mutations use `ignore_permissions=True` or manual commits without a visible permission gate.

Guest endpoints:

- `get_onboarding_form`
- `submit_onboarding_form`

Required hardening:

- Add token expiry/revoke status for onboarding links.
- Validate onboarding payload fields against an allowlist.
- Rate-limit guest token endpoints at the web/proxy or Frappe layer.
- Add role checks for payroll, employee deletion, attendance edits, and offer/contract actions.

### `muahang`

Flagged endpoints include supplier creation/update, purchase request/order/receipt/invoice creation, submit/cancel flows, document mappers, and supplier payment.

Required hardening:

- Check `Supplier`, `Material Request`, `Purchase Order`, `Purchase Receipt`, `Purchase Invoice`, and `Payment Entry` permissions before mutation.
- Keep `ignore_permissions=True` only if a higher-level role check already passed and ERPNext's own permission model cannot handle the specific mapper.

### `kinhdoanh`

Flagged endpoints include customer, quotation, sales order, delivery note, sales invoice, and payment receipt flows.

Required hardening:

- Check `Customer`, `Quotation`, `Sales Order`, `Delivery Note`, `Sales Invoice`, and `Payment Entry` permissions before mutation.
- Treat invoice, delivery, cancel, and payment endpoints as high-risk because they affect GL, stock, and receivables.

### `kho`

This app already has `_check_perm`, which is the right direction. Remaining gaps are mostly setup/master-data helpers and some submit or generate actions.

Required hardening:

- Call `_check_perm` inside `update_item`, `toggle_item_disabled`, `set_valuation_method`, `create_item_group`, `create_uom`, `set_reorder_level`, `create_batch`.
- Gate `clean_english_master_data` and `seed_kho_items` behind admin-only checks.

### `tckt`

Journal entry operations need explicit permission checks before insert/submit/cancel.

Required hardening:

- Check `Journal Entry` create/submit/cancel.
- Restrict accounting setup to System Manager or Accounting Manager.

### `crm_ui`

Lead/opportunity/customer create and conversion flows need permission checks.

Required hardening:

- Check `Lead`, `Opportunity`, and `Customer` create/write permissions before mutations.
- Restrict CRM setup endpoint to admin/CRM manager.

### `duan`

`update_task_status` should check write permission on `Task` or project membership rules before changing state.

### `portal`

`get_my_modules` uses `ignore_permissions=True`. This may be acceptable for a launcher if it returns only module metadata, but it should be reviewed for data exposure and role filtering correctness.

### `quantri`

This app already checks Frappe permissions for user create/update/disable. Use this as the local reference pattern.

## Suggested Implementation Order

1. Fix `muahang`, `kinhdoanh`, and `tckt` first because they affect accounting, stock, payables, receivables, and cash.
2. Fix `hr` payroll/employee deletion/attendance operations next.
3. Finish remaining `kho` gaps.
4. Fix lower-risk CRM/project endpoints.
5. Add unauthorized-access tests for each high-risk mutation endpoint.
