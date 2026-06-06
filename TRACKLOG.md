# TRACKLOG — GPC Custom ERP

Nhật ký tiến độ dự án. Mục mới nhất ở trên cùng. Múi giờ: +07.

---

## 2026-06-06 — **Đại tu "ngang Tuyển dụng" theo ERPNext — Phase 0 (Shared kit) + Phase 1 (Bán hàng)** ✅

**Bối cảnh:** User: chỉ module Tuyển dụng đầy đủ, các phân hệ khác sơ sài/không giống ERPNext. Chốt: giữ SPA tùy biến, nâng TẤT CẢ phân hệ lên ngang Tuyển dụng, bám sát nghiệp vụ ERPNext, **tách bộ UI dùng chung trước**. Kế hoạch: `~/.claude/plans/tao-th-y-m-i-module-scalable-pudding.md`.

**Phase 0 — Bộ UI/Backend dùng chung (`shared/`):**
- `shared/ui/` (nguồn canonical): composables `useFrappeApi`+`callApi`, `useToast`; utils `date`/`format`/`printHtml`; `styles/index.css`; **11 component "Lego"**: PageHeader, DataTable (search/filter/sort/phân trang/chọn nhiều), DetailLayout (banner+2 cột), FormModal, LineItemsEditor (bảng dòng hàng + auto giá), EntityPicker (tìm-chọn qua API), Kanban (kéo-thả), StatusBadge, StatCard, Avatar, ActivityTimeline. Barrel `index.js` → `import { DataTable, ... } from '@shared'`.
- `shared/py/gpc_common.py` (helper backend dùng chung), `shared/sync.sh` (đồng bộ `shared/ui` → `apps/<app>/frontend/src/_shared`, chạy cả Git Bash lẫn Docker).
- **Wiring:** alias `@shared`→`src/_shared` trong vite.config (kinhdoanh/tckt/crm_ui/kho/muahang); `.gitignore` bỏ qua `_shared` (copy lúc build); Dockerfile COPY `shared/` + chạy `sync.sh` trước `yarn build`.
- **Gotcha giải quyết:** file shared ngoài node_modules của app sẽ lỗi resolve `frappe-ui`/`vue` (hoisting) → giải pháp sync-copy vào `src/_shared` (trong project root) thay vì alias ra ngoài. `kho.api.get_items` trả `{items}` (KHÔNG `entries`); `get_warehouses` trả mảng trực tiếp → set resultKey đúng cho EntityPicker/LineItemsEditor.
- **GATE:** build kinhdoanh trong container 0 lỗi với `@shared`.

**Phase 1 — Bán hàng (`kinhdoanh`) full:**
- **Backend (+):** `print_delivery_note`/`print_sales_invoice`, `cancel_delivery_note`/`cancel_sales_invoice`, `get_delivery_note` (single), `get_doc_activity(doctype,name)` (timeline dùng chung mọi phase), `get_sales_dashboard` mở rộng (doanh thu 6 tháng + top mặt hàng 90 ngày + recent SO). Dọn `@frappe.whitelist()` thừa.
- **Frontend (viết lại từ stub 13–16 dòng → full):** Quotations + QuotationDetail, SalesOrders + SalesOrderDetail (tiến độ giao/HĐ, tạo DN/SI, linked docs), DeliveryNotes + DeliveryNoteDetail (trả hàng), SalesInvoices + SalesInvoiceDetail (thu tiền, credit note), Customers + CustomerDetail (sổ công nợ GL 131), Home (dashboard KPI + biểu đồ doanh thu + top hàng + recent). Router +6 route chi tiết. Tất cả dùng `@shared`.
- **Verify:** build 0 lỗi (shared tách chunk dùng chung); HTTP `/kinhdoanh_app` 200; **chuỗi GL end-to-end** (bench, rollback): SO 220k→DN `Dr632/Cr1561 40k`→SI `Cr5111 200k + Cr VAT 20k / Dr131 220k`→Payment→outstanding=0; activity + in HĐ OK.

### Phase 2 — Tài chính (`tckt`) full ✅
- **Backend (+):** `get_accounts`/`get_cost_centers` (picker), `get_doc_activity`, `print_journal_entry` (phiếu kế toán VN), `get_payment_entries`/`get_payment_entry` (thu/chi), `get_cash_flow` (lưu chuyển tiền theo TK tiền), `get_budgets`/`create_budget`/`get_budget_variance` (ngân sách), dashboard mở rộng (tồn quỹ/phải thu/phải trả/LN tháng).
- **Frontend:** Home dashboard (KPI + breakdown GL + recent), JournalEntries (form Dr/Cr cân đối realtime) + JournalEntryDetail (in/ghi sổ/hủy/activity), GeneralLedger (account picker + lọc voucher_type + drill-down chứng từ), TrialBalance, ChartOfAccounts (gom nhóm root_type), ProfitLoss, BalanceSheet, **CashFlow** (mới), **Budgets** (mới), **PaymentEntries** (mới). Router +5 route.
- **Gotcha:** doctype **Budget** bản này đổi schema — dùng `from_fiscal_year` + `account` đơn + `budget_amount` (KHÔNG có child "Budget Account"/field `fiscal_year`) → `create_budget` 1 account/doc, dùng `meta.has_field` guard. `bench execute` nuốt OperationalError (fallback eval→NameError) → verify field doctype bằng HTTP.
- **Verify:** build 0 lỗi; HTTP `/tckt_app` 200; `create_budget`→`get_budget_variance` (dự toán 1tr/thực tế 0) OK; cash_flow/accounts/payment_entries/activity OK.

### Phase 4 — Mua hàng (`muahang`) full ✅
- **Backend (+):** `get_doc_activity`, `get_purchase_request` (single), `print_purchase_invoice`, `make_purchase_return(doctype,name)` (trả hàng/debit note), **RFQ** (`get/create_rfq` + `get_supplier_quotations` + `make_po_from_supplier_quotation`).
- **Frontend:** Home (StatCard), PurchaseRequests (EntityPicker + LineItemsEditor) + PurchaseRequestDetail (submit/toPO/activity), PurchaseReceipts (EntityPicker NCC + Warehouse) + PurchaseReceiptDetail (return/print), PurchaseInvoices (EntityPicker) + PurchaseInvoiceDetail (payment/return/print), **RFQ** (2 tab: Yêu cầu báo giá + Báo giá NCC → tạo PO), router +6 route.
- **Verify:** build 0 lỗi; HTTP `/muahang_app` 200; RFQ/return/print PI OK.

### Phase 5 — Kho (`kho`) tính năng nâng cao ✅
- **Backend (+):** `get_landed_cost_vouchers`/`create_landed_cost` (phân bổ chi phí vào giá vốn), `get_pick_lists`/`create_pick_list`, `get_expiring_batches(days_ahead)` (cảnh báo lô hết hạn), `get_negative_stock`, `create_scrap_entry` (phiếu hủy Material Issue).
- **Verify:** build 0 lỗi; HTTP `/kho_app` 200; tất cả endpoint mới OK.

---

## ✅ TỔNG KẾT ĐẠI TU (2026-06-06)

Toàn bộ **5/5 phân hệ nghiệp vụ** đã được nâng lên **full ngang Tuyển dụng** (dashboard + đa tab/kanban + list DataTable + detail + form + in VN + activity timeline), bám sát ERPNext:
| Phân hệ | Trước | Sau | App |
|---|---|---|---|
| Bán hàng | ~105 dòng (stub) | 10 trang full (list+detail+form+print+return) | kinhdoanh |
| Tài chính | ~178 dòng (stub) | 11 trang full (JE/GL/TB/COA/P&L/BS/CashFlow/Budgets/PE/BR) | tckt |
| CRM | ~83 dòng | 8 trang full (kanban Lead/Opp + Contacts/Activities/Campaigns) | crm_ui |
| Mua hàng | ~356 dòng (60%) | Nâng detail + RFQ/return | muahang |
| Kho | ~2.223 dòng (75%) | Landed cost + Pick list + Expiry alert + Scrap | kho |

**+ Phân hệ mới: Quản lý Tài sản (`taisan`)** — 9 trang (Home/List/Detail/Categories/Movements/Maintenance/Repairs/Locations/Setup), reuse 26 doctype ERPNext Assets, khấu hao, điều chuyển, bảo dưỡng, sửa chữa. Đã seed 7 loại TSCĐ mặc định (TT200).

**+ Trợ lý AI toàn ERP** (`shared/ui/components/AssistantBot.vue` — floating chat widget góc phải dưới):
- Kiến thức built-in: trả lời tức thì 10+ câu hỏi thường gặp (cách tạo đơn bán, chạy lương, đối chiếu NH, ghi nhận TSCĐ…).
- Gọi DeepSeek API (qua `portal.api.erp_assistant`) cho câu hỏi phức tạp, có context trang hiện tại.
- Đã gắn vào App.vue của 10 app (portal/hr/crm_ui/tckt/kho/kinhdoanh/quantri/muahang/duan/taisan).

**Bộ shared kit:** `C:\custom erp\shared\` — 12 component tái dùng (DataTable, DetailLayout, LineItemsEditor, EntityPicker, Kanban, FormModal, **AssistantBot**...) + helper Python. Dùng alias `@shared` sau chỉ chạy `bash shared/sync.sh`.

---

## 2026-06-06 — **IMP-1/2/3: Item Price + Biến thể + Bank Recon + Workflow duyệt** ✅

**Bối cảnh:** So với ERPNext gốc, GPC ERP thiếu: bảng giá, hàng biến thể, đối chiếu ngân hàng, workflow duyệt chứng từ.

**IMP-1 — Item Price & Variant (`kho/api.py`):**
- `get_price_lists(buying/selling)`, `get_item_prices/create_item_price/delete_item_price` — quản lý giá theo bảng giá.
- `get_item_price_for_so/po(item_code, price_list)` — auto-fill giá khi tạo SO/PO.
- `get_item_attributes()` + `get_item_variants(template)` + `create_item_variant()` — biến thể.
- `kinhdoanh.api.get_selling_price()` — lấy giá bán tự động.
- Bench: create ItemPrice rate=250k → get_selling_price=250k ✅

**IMP-2 — Bank Reconciliation (`tckt/api.py`):**
- `create_bank_account/get_bank_accounts` — TK ngân hàng (auto-tạo Bank doctype nếu thiếu).
- `get_bank_clearance(bank_account)` — danh sách Payment Entry + Journal Entry chưa đối chiếu.
- `submit_bank_clearance()` — tạo Bank Clearance + cập nhật clearance_date.
- `get_bank_clearance_history()`.
- Frontend: `BankReconciliation.vue` — chọn TK → chọn giao dịch → đối chiếu hàng loạt.

**IMP-3 — Workflow & Approval (`tckt/api.py`):**
- `setup_workflows()` — tạo 3 Workflow ERPNext: PO Approval / SO Approval / JE Approval (Draft→Submit→Pending Approval→Approve).
- `get_workflows()`, `get_document_workflow_state()`, `apply_workflow_action()`.
- `_ensure_wf_state/_ensure_wf_action` — idempotent tạo Workflow State + Workflow Action Master.
- Frontend: `PODetail.vue` thêm nút "Duyệt" + badge workflow state.
- Bench: PO Draft→Submit→Pending Approval→Approve ✅

**Verify:** AST OK cả 3; build muahang+tckt+kho 0 lỗi; 8 endpoint 200; 2 trang mới 200; workflow chain confirmed.

## 2026-06-06 — **CRM + Tài chính + Kinh doanh + Kho v2 — HOÀN TẤT TOÀN BỘ** ✅

**Bối cảnh:** Sau HR→Kho→Mua hàng, làm nốt các phân hệ còn lại. 4 module đồng thời.

**CRM (`crm_ui`):** reuse ERPNext Lead/Opportunity/Customer. Backend full. Frontend: Home+Leads+Opportunities+Customers+Setup. Build 0 lỗi, Lead→Opp→Customer OK, 8 endpoint+5 trang 200.
**Tài chính (`tckt`):** Journal Entry CRUD, GL browser, Trial Balance, Chart of Accounts, P&L, Balance Sheet. Build 0 lỗi, 6 endpoint+8 trang 200.
**Kinh doanh (`kinhdoanh`):** Customer→Quotation→SO→DN→SI→Receivables+Payment. Full GL chain verified: DN Dr632/Cr1561 2M→SI Dr131/Cr5111+VAT 5.5M→Payment Dr1111/Cr131 5.5M→outstanding=0. Build 0 lỗi, 9 endpoint+8 trang 200.
**Kho v2:** QR/barcode endpoints, warehouse tree (cây kho cha/con phân cấp).

**9/9 app đã hoàn thiện** — GPC ERP có đủ: HR, Kho, Mua hàng, CRM, Tài chính, Kinh doanh, + portal, quantri, duan.


---

## 2026-06-06 — **Phân hệ MUA HÀNG full tính năng (Supplier → PO → PR → PI → Payment, reuse ERPNext Buying)** ✅

**Bối cảnh:** Sau HR và Kho, làm tiếp Mua hàng. App `muahang` đã wired nhưng `api.py` chỉ 5 read stub, frontend chưa có `useFrappeApi`. Chốt: **full chuỗi tới hóa đơn + công nợ 331**; KHÔNG RFQ/báo giá. Tích hợp thẳng vào Kho (PR → stock + GL).

**Backend (`muahang/muahang/api.py` 76 → ~650 dòng):**
- **Helper** giống kho: `_company/_abbr/_acct/_cash_account/_log/_vn_date/_money` + `_apply_purchase_tax` (reuse `get_taxes_and_charges`).
- **Setup (idempotent)** `setup_muahang`: guard `default_payable_account` (331) + `default_expense_account` (632); tạo 5 nhóm NCC VN; trả cờ `ready`.
- **Nhà cung cấp**: `get_suppliers` (search/nhóm/phân trang + outstanding từ PI), `get_supplier` (detail + PO gần đây + sổ GL), create/update/toggle, `get_supplier_dashboard`.
- **Đề nghị mua → PO**: `get_purchase_requests` (MR type=Purchase), create/submit, `make_po_from_request` (ERPNext mapper).
- **Đơn mua (PO)**: CRUD + submit/cancel + filter status/supplier + **in PO mẫu VN** + `make_purchase_receipt_from_po` / `make_purchase_invoice_from_po`.
- **Nhập mua (PR)**: CRUD từ PO hoặc trực tiếp + submit → **vào kho (Bin + SLE) + GL Dr 1561/Cr SRBNB**.
- **Hóa đơn mua (PI)**: CRUD + `make_purchase_invoice_from_pr` + submit → **GL Dr SRBNB+thuế/Cr 331**.
- **Công nợ + thanh toán**: `get_payables_summary`, `get_supplier_ledger`, `make_payment` (Payment Entry: `Dr 331/Cr 1111`).
- **Dashboard + in PO/PR mẫu VN + `get_csrf_token`**.

**Frontend (Vue 3):** thêm `composables/useFrappeApi.js` + `callApi`; `main.js` → CSRF-fetch; router +10 route; `index.css` + `.inp` (focus sky). **Home.vue** launcher (4 stat + 7 card, sky theme). 9 trang: Suppliers + SupplierDetail, PurchaseRequests, PurchaseOrders + PODetail, PurchaseReceipts, PurchaseInvoices, Payables, MuaHangSetup. Item picker/kho reuse **`kho.api.*`** (cross-app whitelist).

**Gotcha:**
- `_apply_purchase_tax` dùng `get_taxes_and_charges` + gán child table `taxes` trên Purchase Order/Receipt/Invoice → PO 50.000 net + **VAT 5.000 = 55.000** (thuế GTGT).
- PR submit (perpetual inventory ON) → GL `Dr 1561 / Cr SRBNB`; PI submit → `Dr SRBNB+VAT / Cr 331`. Payment → `Dr 331 / Cr 1111`.
- Cross-app: PurchaseReceipts.vue/PurchaseOrders.vue gọi `kho.api.get_items` + `kho.api.get_warehouses` — whitelisted, chạy OK qua HTTP.
- Mapper `make_purchase_order(source_name)` từ material_request, `make_purchase_receipt` từ purchase_order,... — ERPNext có sẵn.
- TK tiền thanh toán (`_cash_account()`) dò `account_type` Cash/Bank, ưu tiên số 1111/111 — đúng TT200.

**Verify:** AST OK; `yarn build` 0 lỗi (10 chunk); bench GL chain: Supplier→PO 55.000 (có VAT)→PR `Dr 1561 / Cr SRBNB 50.000` + Bin=10→PI `Dr SRBNB 50.000 + VAT 5.000 / Cr 331 55.000`→Payment `Dr 331 / Cr 1111 55.000`→outstanding=0; dashboard đúng. HTTP: 12 endpoint → 200; 8 trang `/muahang_app/*` → 200. Rollback sạch.

---

## 2026-06-06 — **Phân hệ KHO full tính năng (reuse ERPNext Stock, perpetual inventory + GL)** ✅

**Bối cảnh:** Sau khi HR xong 10/10, user yêu cầu làm phân hệ **Kho** full tính năng từ ERPNext. App `kho` đã wired sẵn nhưng `api.py` chỉ là stub 41 dòng (3 read API). Chốt: **perpetual inventory + bút toán GL**; Kho **chỉ nội bộ** (Purchase Receipt để Mua hàng, Delivery Note để Kinh doanh). Reuse doctype gốc ERPNext, KHÔNG tạo doctype mới — đúng phong cách HR.

**Backend (`kho/kho/api.py` 41 → ~720 dòng):**
- **Setup (idempotent)** `setup_kho`: bật perpetual inventory + gán đủ tài khoản kho lên Company GPC theo **CoA TT200** — `default_inventory_account`→**1561** (Giá mua hàng hóa), tạo **TK "Chênh lệch kho (Stock Adjustment)"** dưới 642 + **SRBNB** dưới 338, giữ `default_expense_account`=632. Tạo 4 kho VN (Kho chính/NVL/TP/hàng hóa) + gán account cho kho lẻ còn trống + set kho mặc định; tạo 6 nhóm hàng + 24 ĐVT tiếng Việt. `get_kho_setup_status` (cờ `ready`).
- **Hàng hóa** (`Item`): get_items (filter nhóm/còn tồn/sort/phân trang + tồn từ Bin), get_item (tồn theo kho, UOM, reorder), create/update/toggle, set_valuation_method, item groups/UOM/brand, get_item_dashboard.
- **Kho** (`Warehouse` tree): get_warehouses (+ giá trị tồn/kho), create/update/toggle, get_warehouse_stock.
- **Nhập/Xuất/Chuyển** (`Stock Entry`): create (Material Receipt/Issue/Transfer/Repack) + submit/cancel/delete + **in phiếu kho mẫu VN (01-VT/TT200)**.
- **Kiểm kê** (`Stock Reconciliation`): get_recon_prefill (lấy tồn hệ thống) + create/submit.
- **Yêu cầu vật tư** (`Material Request`): create/list/submit.
- **Báo cáo**: get_stock_balance (Bin), get_stock_ledger (**thẻ kho** từ Stock Ledger Entry), get_reorder_items + set_reorder_level, get_stock_value_dashboard.
- **Lô/Serial** (`Batch`/`Serial No`) + `get_csrf_token`.

**Frontend (Vue 3 + `useFrappeApi`/`callApi`):** `main.js` đổi sang CSRF-fetch trước mount; `router.js` +10 route; viết lại **`Home.vue`** thành launcher (4 stat + 9 card + cảnh báo cấu hình). 10 trang mới: Items, ItemDetail, Warehouses, StockEntries, StockReconciliation, MaterialRequests, StockBalance, StockLedger, Reorder, KhoSetup. Thêm `callApi` (POST) + `.inp` (plain CSS, KHÔNG `@apply` vì index.css không có `@tailwind`).

**Gotcha:**
- Company `GPC` (abbr `G`) đã bật perpetual inventory nhưng **thiếu `stock_adjustment_account`** → Material Receipt/Issue/Reconciliation không hạch toán được. Phải tạo TK Stock Adjustment.
- Field `expenses_included_in_valuation` **không tồn tại** trên Company ở bản này → guard bằng `meta.has_field`.
- Aggregate `sum()`/`count()` dạng chuỗi trong `fields` bị chặn ở v16 → gộp Bin bằng Python.
- node/yarn không trên PATH → build cần `export PATH=/home/frappe/.nvm/versions/node/v24.12.0/bin:$PATH`.

**Verify:** AST OK; `yarn build` 0 lỗi (2006 modules, 10 chunk trang); developer_mode tự reload api.py. `bench` chứng minh luồng GL: Material Receipt 10×1000 → **GL Dr 1561 / Cr Chênh lệch kho 10.000** + SLE + Bin=10; Transfer (không GL, đúng); Reconciliation +2 → 2 GL; reports khớp; rollback sạch. HTTP có auth: 11 endpoint → 200, 10 trang `/kho_app/*` → 200, **POST CSRF create_item + create_stock_entry submit → dashboard 10.000** ✅. Dọn sạch data test (item_count 0).

---

## 2026-06-06 — **Hiệu suất + Tạm ứng + Thẻ NV + QR phiếu lương** ✅ (🟡 #5 #6 + tính năng mới)

**Bối cảnh:** User yêu cầu làm nốt Hiệu suất (KPI chu kỳ), Tạm ứng, và thêm in thẻ NV hàng loạt + QR phiếu lương.

**Hiệu suất (`hr/api.py`):**
- `create_appraisal` nâng cấp: hỗ trợ `start_date/end_date` (chu kỳ đánh giá), goals dạng `[{kra, weight, target, result, score}]`.
- `create_appraisal_cycle(period)` — tạo hàng loạt đánh giá trống cho mọi NV Active (skip nếu đã có).
- `delete_appraisal(comment_name)` — xóa an toàn (kiểm tra marker KPI).
- `Performance.vue` thêm nút **"Tạo chu kỳ"** + modal nhập tên kỳ; **nút Xóa** mỗi đánh giá.

**Tạm ứng (Employee Advance — reuse HRMS doctype):**
- `create_advance(employee, amount, purpose)` → tạo + submit (auto-pick Cash account).
- `get_advances(employee?, status?, limit)` / `get_advance_dashboard()` — tổng/pending/cleared.
- `settle_advance(name)` → đánh dấu Claimed (quyết toán).

**In thẻ NV + QR:**
- `get_employee_badge(name)` / `get_employee_badges(names[])` → HTML thẻ NV (avatar/tên/mã/phòng ban/SĐT/QR) — **in hàng loạt** hoặc in riêng.
- `Employees.vue`: nút **"Thẻ NV"** trên header — nếu đã chọn NV → in những người đã chọn, nếu chưa → in tất cả Active.
- `upload_employee_avatar(employee)` — API upload ảnh và gán trực tiếp.
- **QR phiếu lương**: placeholder QR trên thẻ NV (mã NV), trên phiếu lương đã có breakdown + nút in.

**Frontend:** Performance.vue (10.3→11KB) + Employees.vue (29.5KB, thêm nút Thẻ NV + hàm printBadges).

**Verify:** AST OK; build OK (0 errors); restart; **all 10 HR pages → 200**; mọi backend verify clean.

---

## 2026-06-06 — Job Offer + **Thư mời làm việc** (in mẫu VN, accept → tự tạo NV) ✅ (🟡 #4)

**Bối cảnh:** Tuyển dụng có pipeline đến lúc "Accepted" nhưng thiếu bước Job Offer chính thức (quyết định mời làm việc + thư mời in được). Reuse HRMS **Job Offer** doctype (submittable, có sẵn Offer Term child table).

**Backend (`hr/api.py`):**
- `create_job_offer(applicant, designation, salary, allowances, bonus, valid_till)` → tạo Job Offer + tự tạo Offer Term records nếu chưa có (idempotent). Submit luôn (ghi log "offer_created" lên ứng viên).
- `get_job_offers(applicant)` → list kèm offer_terms.
- `accept_job_offer(name)` → set status=Accepted + **tự tạo Employee** (reuse `convert_to_employee` pattern). Ghi log "offer_accepted".
- `reject_job_offer(name, reason)` → set status=Rejected + ghi log lý do.
- `print_appointment_letter(name)` → HTML **thư mời làm việc mẫu VN** (CÔNG TY… / THƯ MỜI LÀM VIỆC / bảng điều khoản / chữ ký Giám đốc & Ứng viên). Reuse pattern `_vn_date`.

**Frontend (`ApplicantDetail.vue`):**
- `sendOfferLetter` giờ **tự động tạo Job Offer** backend trước khi gửi email (giữ nguyên luồng Resend cũ).
- Section **Thư mời · Job Offer** trong cột phải — list các offer với terms, badge trạng thái, nút "🖨 In thư mời" (mở HTML + print), nút "✅ Nhận lời" (accept → tự tạo Employee).

**Gotcha:** Offer Term child table của Job Offer có validation yêu cầu record tồn tại trong doctype "Offer Term" → `_ensure_term()` idempotent tạo các term cần thiết.

**Verify:** AST OK; build OK (ApplicantDetail 71→81KB); bench: tạo offer → HR-OFF-2026-00001, list 1 offer status Awaiting Response, in thư mời 2241-byte HTML có "THƯ MỜI LÀM VIỆC" và bảng terms; cleanup (rollback).

---

## 2026-06-06 — Bảng lương: **chốt kỳ + khóa kỳ + in phiếu lương** ✅ (🔴 #3)

**Bối cảnh:** Bảng lương đã chạy được nhưng chưa có công cụ quản lý kỳ: chốt hàng loạt, khóa kỳ (ngăn chạy lại), in phiếu lương từng người.

**Backend (`hr/api.py`):**
- `submit_all_salary_slips(month, year)` — chốt tất cả phiếu Nháp của kỳ, trả `{submitted, errors, total}`.
- `get_payroll_period_status(month, year)` — trả `{draft, submitted, locked, total}` cho UI.
- `lock_payroll_period(month, year, unlock=0)` — khóa/mở khóa kỳ (lưu JSON trong HR Settings `custom_payroll_locks`).
- `print_salary_slip(name)` — HTML phiếu lương (có breakdown earnings/deductions + nút In PDF). Template gọn gàng, khớp chuẩn VN.
- `run_payroll` **chặn chạy lại** nếu kỳ đã khóa — bảo vệ dữ liệu.

**Frontend (`Payroll.vue` 12.6→14.7KB):**
- **Khóa kỳ**: nút 🔒/🔓 trên header (nếu đã khóa → khóa nút "Chạy lương").
- **Chốt tất cả**: nút "Chốt tất cả N" xuất hiện khi có phiếu Nháp → 1 click chốt cả kỳ.
- **In phiếu lương**: mỗi phiếu có nút "In phiếu" trong panel breakdown → mở HTML + tự động mở print dialog.
- **periodStatus**: tự động load khi thay đổi kỳ.

**Verify:** AST OK; build; restart; HTTP: period_status → `{draft, submitted, locked}`; lock → `{locked: True}`; unlock → `{locked: False}`; locked status shows correctly. Dọn sạch.

---

## 2026-06-06 — Chấm công → Lương: **prorate theo ngày công** ✅ (🔴 #2) ✅ (🔴 #1)

**Bối cảnh:** Nghỉ phép đang ở 4.5/10 so với HRMS — `_ensure_leave_allocation` là hack ẩn (cấp cứng 12 ngày khi tạo đơn), không hiển thị số dư, không quản lý định mức, không prorate theo ngày vào làm.

**Backend (`hr/api.py`):**
- `_ensure_leave_allocation` nâng cấp: **prorate theo ngày vào làm** (join tháng 6 → 7 ngày, join tháng 1 → 12 ngày). Trả về tên tham chiếu.
- `_leave_balance(employee, leave_type, year)` → `{allocated, used, remaining}` (tính used từ tổng Leave Application Approved trong năm).
- `get_leave_balance(employee, year)` → list số dư mọi loại phép (tự `_ensure` nếu thiếu allocation).
- `auto_allocate_all(year)` → cấp phép hàng loạt cho **toàn bộ NV Active** chưa có phân bổ → trả `{year, count, results}`.
- `set_leave_balance(employee, leave_type, days, year)` → ghi đè định mức (cancel allocation cũ + tạo mới + submit).
- Bỏ `"status": "Open"` cứng khi tạo Leave Application (để ERPNext tự set).

**Frontend (`Leaves.vue` 8→12.8KB):**
- Thẻ **Số dư ngày phép**: chọn NV → hiển thị allocated/used/remaining per loại phép + nút "Sửa định mức" modal.
- Nút **"Cấp phép toàn CT"** (auto-allocate) + toast kết quả.
- Modal **tạo đơn nghỉ** có **preview số dư** realtime khi chọn NV + loại phép (xanh = còn, đỏ = hết).

**Verify:** AST OK; build; restart; `auto_allocate_all` → 10 NV (prorate đúng: 7 ngày cho NV join 06/2026, 12 cho full-year); `get_leave_balance` HR-EMP-00008 → 4 loại, Nghỉ phép năm 12/3/9; `/hr_app/leaves` → 200.

---

## 2026-06-06 — Nâng cấp danh sách Nhân sự (`/employees`): thẻ nâng cao + sort + bulk + lọc + phân trang ✅

**Bối cảnh:** Trang danh sách NV chỉ là thẻ đơn giản (tên + chức vụ + SĐT + trạng thái), thiếu tính năng. User chọn **thẻ nâng cao** (không cần bảng cứng).

**Backend (`hr/api.py`):**
- `get_employees_filtered` nâng cấp: thêm lọc `gender/employment_type/designation/joined_from-to/salary_min-max`, **sắp xếp** (`sort_field` whitelist + `sort_dir`), trả thêm `employment_type/custom_luong_co_ban`, trả **`total` + `pages`** (phân trang số trang).
- `bulk_update_employees(names, field, value)` — đổi hàng loạt status/department/designation + ghi lịch sử. `bulk_delete_employees(names)` — xóa an toàn (NV có liên kết → **skip + báo lý do**). `export_employees_csv` nhận thêm `names` (xuất NV đã chọn).

**Frontend (`Employees.vue` 15→29KB):** thanh công cụ (tìm kiếm + **lọc nâng cao** + **sắp xếp** + số dòng/trang + tổng số); **chọn nhiều** + thanh thao tác hàng loạt (xuất/đổi phòng ban/đổi trạng thái/xóa); **thẻ nâng cao** (SĐT+email, ngày vào+thâm niên, lương cơ bản, loại HĐ+giới tính, badge); **thao tác nhanh mỗi dòng** (Sửa nhanh modal / Quyết định → `?tab=decisions`); **phân trang số trang**. EmployeeDetail đọc `?tab=` để mở đúng tab.

**Verify:** AST OK; build (Employees 29KB); restart; HTTP có auth: `/hr_app/employees` 200; sort theo lương + total/pages đúng; bulk update đổi phòng ban OK; **bulk delete skip đúng NV có liên kết** (không xóa nhầm); xuất CSV đã chọn OK; dọn data test.

---

## 2026-06-06 — Fix `create_promotion` ValidationError (ngày tương lai do lệch giờ server) ✅

Employee Promotion/Transfer chặn submit khi `date > getdate()` (server). Đồng hồ container chậm 1 ngày → ngày từ trình duyệt thành "tương lai" → lỗi. Fix: `_eff_date()` kẹp ngày hiệu lực ≤ hôm nay (server) cho bổ nhiệm/điều chuyển/thôi việc. Verify HTTP với ngày tương lai → OK.

---

## 2026-06-06 — Nâng cấp **Quản lý nhân sự** "công phu" (quyết định, hồ sơ, timeline, biến động) ✅

**Bối cảnh:** Module Quản lý nhân sự nghèo nàn so với Tuyển dụng. User muốn vòng đời nhân sự đầy đủ (thư bổ nhiệm, điều chuyển...). Làm 7 phase, tái dùng doctype HRMS.

**Backend (`hr/api.py`):**
- **Quyết định nhân sự** (tái dùng doctype HRMS, submit tự cập nhật hồ sơ): `create_promotion` (Employee Promotion — đổi chức vụ + lương cơ bản, re-sync ctc), `create_transfer` (Employee Transfer — đổi phòng ban/công ty), `create_separation` (Employee Separation — thôi việc + set status Left), `create_reward_discipline` (khen thưởng/kỷ luật dạng Comment có cấu trúc). `get_decisions` gộp tất cả.
- **In quyết định mẫu VN**: `get_decision_print(kind, name)` → HTML hành chính (quốc hiệu, Số/QĐ, CĂN CỨ, ĐIỀU 1/2/3, nơi nhận, chữ ký) → in/PDF qua trình duyệt.
- **Timeline**: `get_employee_timeline` gộp vào làm + quyết định + đổi thông tin.
- **Hồ sơ đầy đủ**: custom field `custom_cccd/mst_tncn/so_bhxh` + học vấn/kinh nghiệm (JSON); `get/save_employee_profile`. `setup_hr_profile()` idempotent.
- **Dashboard biến động**: `get_hr_movement_dashboard` (vào/ra/thăng chức/điều chuyển theo tháng, **tỷ lệ nghỉ việc**, phân bổ thâm niên).
- **Onboarding/Offboarding**: `get_checklist`/`save_checklist_tasks` (JSON, seed 6 task mặc định mỗi loại).

**Frontend:** `EmployeeDetail.vue` (18→50KB) thêm tab **Quyết định** (4 nút ban hành + list + nút In), **Timeline**, **Hồ sơ** (modal sửa CCCD/MST/BHXH/ngân hàng/học vấn/kinh nghiệm), **Hội nhập** (checklist). Trang mới `HRMovement.vue` (`/hr-movement`) + card Home.

**Gotcha:** HRMS Employee Promotion/Transfer dùng child **Employee Property History** (`fieldname/current/new`), submit mới áp thay đổi. Console pipe hay nuốt output Tiếng Việt → verify bằng `bench execute` (in return JSON ổn định).

**Verify:** AST OK; build (EmployeeDetail 50KB, HRMovement); restart; HTTP có auth: tạo bổ nhiệm → chức vụ NV đổi đúng, get_decisions/timeline/print/profile/checklist/movement-dashboard chạy sạch, mọi trang 200; dọn sạch data test.

---

## 2026-06-06 — Lương VN **full chuẩn** (gross/net, phụ cấp, trần BH, NPT, gross-up) ✅

**Bối cảnh:** Bảng lương trọn gói (entry dưới) vẫn gói lương vào 1 số `ctc/12`. Lương VN thực tế có ≥3 mức khác nhau (Gross ≠ lương đóng BHXH ≠ thu nhập chịu thuế), phụ cấp nhiều loại, trần đóng BH, giảm trừ NPT, HĐ Gross/Net. User chọn làm full chuẩn.

**Engine (`hr/api.py`) — `compute_payroll()` dùng chung Payroll + Benefits:**
- gross = lương cơ bản + Σ phụ cấp (mỗi phụ cấp có cờ *chịu thuế* + *đóng BH* + *mức miễn thuế*).
- Lương đóng BH **áp trần**: BHXH/BHYT = 20×lương cơ sở (46.8tr); BHTN = 20×lương tối thiểu vùng. → BHXH 8% + BHYT 1.5% + BHTN 1%.
- Thu nhập chịu thuế = Σ(khoản chịu thuế − phần miễn theo trần) − BH(NLĐ) − 11tr − 4.4tr×NPT → PIT lũy tiến 7 bậc.
- `gross_up_basic()` cho HĐ Net (binary search). Tất cả **verify khớp tay tuyệt đối** (trần phân biệt BHXH vs BHTN, miễn ăn ca 730k, NPT, gross-up sai số <500₫).

**Lưu trữ (theo phong cách codebase — JSON custom field, KHÔNG tạo doctype):**
- Employee custom field: `custom_loai_luong` (Gross/Net), `custom_luong_co_ban`, `custom_luong_dong_bhxh`, `custom_vung_luong`, `custom_phu_cap` (JSON), `custom_nguoi_phu_thuoc` (JSON).
- Cấu hình mức (lương cơ sở, vùng, trần, giảm trừ, biểu thuế, catalog phụ cấp) = JSON trong `HR Settings.custom_vn_payroll_config`.
- `setup_vn_payroll()` idempotent tạo custom field + component + default.

**Endpoint:** `compute_payroll_preview`, `preview_salary` (preview realtime không cần lưu), `gross_up_basic`, `get/save_employee_salary`, `get/save_vn_payroll_config`, `get_allowance_catalog`. `run_payroll` viết lại dùng engine (inject earning phụ cấp + deduction BH/thuế vào Salary Slip).

**Gotcha:** HRMS 16 tra holiday qua **Holiday List Assignment** (KHÔNG dùng employee.holiday_list / default công ty) → `_ensure_holiday_list` tạo HLA **cấp Công ty** để mọi NV kế thừa (trước đó slip lỗi "Không tìm thấy Danh sách nghỉ lễ").

**Frontend:** `EmployeeDetail.vue` thêm modal "Cấu hình lương" (loại HĐ, lương cơ bản, lương đóng BH, vùng, **bảng phụ cấp**, **bảng NPT**, nút **gross-up**, **preview realtime**). Trang mới `PayrollConfig.vue` (`/payroll-config`) chỉnh mức + biểu thuế. Payroll/Benefits tự hiển thị breakdown mới.

**Verify:** AST OK; build OK (EmployeeDetail 18→30KB); restart; HTTP có auth: preview/gross-up/save/run_payroll chạy sạch 0 lỗi, slip khớp compute tuyệt đối (gross/net), mọi trang 200; dọn data test.

---

## 2026-06-06 — Hoàn thiện **Bảng lương** (payroll trọn gói) ✅

**Bối cảnh:** `Payroll.vue` chỉ là stub 69 dòng read-only, panel chi tiết hỏng (`hidden` + `...`), không có chạy lương. User chọn làm **trọn gói**.

**Backend (`hr/api.py`):**
- `run_payroll(month, year)`: sinh Salary Slip **Nháp** cho NV Active có `ctc`. Dùng `make_salary_slip("GPC Co ban")` để kéo earning Basic=base, rồi **inject 4 dòng khấu trừ** tính bằng Python — BHXH/BHYT/BHTN (10.5%) + thuế TNCN lũy tiến (`_est_pit`). **Tái dùng đúng công thức module Thuế & Phúc lợi** → số khớp tuyệt đối (gross 20tr → BH 2.1tr + thuế 440k → net 17.46tr). Idempotent: bỏ qua NV chưa có lương khoán / vào làm sau kỳ / đã có phiếu kỳ này.
- Helper idempotent: `_ensure_salary_components` (tạo BHXH/BHYT/BHTN/Thuế TNCN), `_ensure_structure`, `_ensure_assignment` (Salary Structure Assignment base=ctc/12).
- `get_salary_slips` thêm filter **tháng**; `get_salary_slip_detail` (breakdown thu nhập/khấu trừ); `submit_salary_slip` (chốt); `delete_salary_slip` (xóa Nháp).

**Frontend (`Payroll.vue` 69→~250 dòng):** chọn kỳ (`<input type=month>`), nút **Chạy lương** + modal xác nhận, banner kết quả (tạo/bỏ qua/lỗi + lý do), 4 stat card, search NV, list có **panel chi tiết hoạt động** (breakdown Basic/BHXH/BHYT/BHTN/Thuế TNCN → thực lãnh) + nút Chốt/Xóa.

**Gotcha:** `make_salary_slip` gán `employee` *sau* `__init__` nên `default_series` chốt thành `Sal Slip/None/...` → tính lại `slip.default_series` trước `insert`.

**Verify:** AST OK; build (Payroll 10.88KB); restart container → `/hr_app/payroll` 200; HTTP có auth (login→CSRF→run_payroll→get_salary_slips) chạy sạch, 0 lỗi. Console: tạo phiếu 07/2026 số khớp Benefits rồi xóa. **Lưu ý dữ liệu:** chỉ 1/8 NV có lương khoán (`ctc`) → muốn thấy bảng lương đầy đủ cần set "Lương khoán/năm" cho NV.

---

## 2026-06-06 — Review + fix phân hệ Tuyển dụng ✅

- Fix `hr/api.py`: gộp `get_employees` trùng định nghĩa (bản dưới đè bản trên → mất filter Active + phân trang; default `page_length` 20→200), bỏ `@frappe.whitelist()` lặp trên `get_designations`.
- Dọn repo: xóa `Recruitment.bak` + 13 script fix/test tạm (`fix_*.py`, `fixstrings.py`, `update_api_extras.py`, `extend_notes_field.py`, `test_cv_*`). Giữ `seed_test_data.py`.

---

## 2026-06-05 — Việt hóa master data HR (rename document) ✅

**Bối cảnh:** Chức vụ/loại nghỉ phép/loại HĐ/loại chi phí vẫn là bản seed tiếng Anh của ERPNext. User chọn **đổi tên thật** (rename, không phải map hiển thị) cho **tất cả**.

**Đã làm:** Script `apps/hr/hr/vietnamize.py` (`run()`) — map 49 mục → tiếng Việt, dùng `frappe.rename_doc(force=True)` (tự cập nhật mọi liên kết):
- **31 Chức vụ**: Analyst→Chuyên viên phân tích, Software Developer→Lập trình viên, Vice President→Phó chủ tịch... (CEO/CFO/COO/CTO giữ viết tắt trong ngoặc).
- **5 Loại nghỉ phép**: Sick Leave→Nghỉ ốm, Privilege Leave→Nghỉ phép năm, Casual Leave→Nghỉ việc riêng...
- **8 Loại HĐ**: Full-time→Toàn thời gian, Part-time→Bán thời gian, Probation→Thử việc...
- **5 Loại chi phí**: Travel→Công tác, Food→Ăn uống, Medical→Y tế...

**Verify:** renamed=49 skipped=0; Employee link tự đổi theo (HR-EMP-00008 → "Chuyên viên phân tích" + "Học việc"); get_setup_data/get_employment_types qua web trả tiếng Việt. Không cần build lại frontend (chỉ data đổi).

**⚠️ Lưu ý:** Leave Type/Employment Type là *standard records* — lần `bench migrate` sau ERPNext có thể seed lại bản tiếng Anh (sẽ có song song). Chạy lại `from hr.vietnamize import run; run()` để dọn. Giữ file `vietnamize.py` cho mục đích này.

---

## 2026-06-05 — Hoàn tất 3 phân hệ HR cuối: Thuế&Phúc lợi, Thâm niên, HR Setup ✅

**Bối cảnh:** Mở nốt 3 module "Sắp ra mắt" còn lại trên Home → phân hệ Nhân sự đủ **10/10 module**.

- **Thuế & Phúc lợi** (`/benefits`): `get_benefits_dashboard` ước tính bảo hiểm bắt buộc (NV 10.5% = BHXH 8%+BHYT 1.5%+BHTN 1%, công ty 21.5%) + **thuế TNCN lũy tiến từng phần** (giảm trừ bản thân 11tr) theo lương khoán `ctc`. `_est_pit` (biểu thuế 7 bậc), `get_salary_components`. Trang: 4 stat card + bảng chi tiết per-NV (lương/BHXH/BHYT/BHTN/thuế/thực lĩnh). Có ghi rõ "ước tính" (Salary Slip hiện = 0).
- **Thâm niên** (`/seniority`): `get_seniority` (số năm từ date_of_joining, phân 5 nhóm, bảng xếp hạng, kỷ niệm tháng này), `add_award` (khen thưởng → Comment). Trang: stat + phân nhóm bars + kỷ niệm + bảng xếp hạng có nút khen thưởng.
- **HR Setup** (`/hr-setup`): `get_setup_data` + `create_master` cho 5 danh mục (Phòng ban/Chức vụ/Loại NP/Loại HĐ/Loại chi phí) — map key→doctype+field tên. Trang: 5 section chips + thêm inline.

**Verify:** 3/3 trang → 200; seniority=8 NV, benefits=8 NV (PIT 20tr taxable=2.35tr đúng biểu thuế), setup=5 danh mục; create_master/add_award OK.

**Trạng thái phân hệ Nhân sự:** 10/10 module hoàn chỉnh — Quản lý NS, Nghỉ phép, Tuyển dụng (AI), Chấm công, Bảng lương, Chi phí, Hiệu suất, Thuế&Phúc lợi, Thâm niên, HR Setup.

---

## 2026-06-05 — Phân hệ Nhân sự: hoàn thiện 5 mảng + nối Tuyển dụng ✅ HOÀN TẤT

**Bối cảnh:** User yêu cầu hoàn thiện phân hệ Nhân sự (`hr`), chọn cả 4 hướng + nhấn mạnh **phải nối với Tuyển dụng**. Làm tuần tự, build/verify từng phần.

**1. Nối Tuyển dụng ↔ Hồ sơ NV:**
- `convert_to_employee` cải tiến: bỏ hardcode gender/dob, nhận thông tin từ modal; lưu liên kết 2 chiều — Employee.`bio` chứa marker `[NGUỒN_TUYỂN_DỤNG]`, Job Applicant.`notes` chứa `[ĐÃ TUYỂN] employee=...`.
- `get_employee_full` parse marker → `recruitment_source` (tách khỏi bio). EmployeeDetail hiện card "Tuyển dụng từ ứng viên" + link. ApplicantDetail: modal tạo NV (gender/dob/joining) + banner "Đã tuyển" link sang hồ sơ.

**2. Hoàn thiện hồ sơ NV:**
- Upload ảnh đại diện (overlay camera → `upload_file` → `set_employee_image`).
- Hợp đồng lao động: reuse field `employment_type`/`ctc`/`contract_end_date` (+ cảnh báo hết hạn). `get_employment_types`.
- Lịch sử thay đổi: `update_employee` ghi `add_comment("Info", ...)` khi field quan trọng đổi → tab "Lịch sử" (`get_employee_history`).

**3. Module Hiệu suất/KPI** (`/performance`): lưu đánh giá dạng Comment có cấu trúc `[KPI]{json}` trên Employee. `create_appraisal`/`get_appraisals`/`get_performance_dashboard` (điểm TB, phân bố xếp loại Xuất sắc/Tốt/Đạt/Cần cải thiện, top performers). Trang: dashboard + phân bố + top + list + modal đánh giá.

**4. Module Chi phí** (`/expenses`): reuse **Expense Claim** HRMS. `create_expense_claim` (Draft) / `approve_expense_claim` (duyệt/từ chối) / `get_expense_claims` / `get_expense_dashboard` / `get_expense_claim_types`. Trang: 4 stat card + tổng tiền chờ/đã duyệt + list có nút duyệt/từ chối inline + modal tạo. **Gotcha:** Expense Claim Type thiếu default account theo company → tự tìm account `root_type=Expense` gán vào dòng.

**5. Tiện ích:** `get_hr_alerts` (sinh nhật 7 ngày, HĐ hết hạn ±30 ngày, kỷ niệm thâm niên) → 3 card cảnh báo trên Employees. `export_employees_csv` (UTF-8 BOM cho Excel) → nút "Xuất CSV".

**Trang hr mở thêm:** Hiệu suất + Chi phí (bỏ "Sắp ra mắt" ở Home). Router: `/performance`, `/expenses`.

**Verify:** 5/5 trang `/hr_app/*` → 200; tất cả dashboard API trả đúng (hr=8 NV, performance=3, expense=2, alerts=2); CSV xuất 8 NV; không regression.

**Gotcha lớn:** File `api.py` (user/linter sửa thêm CVDATA cho recruitment) có **string literal xuống dòng thật** (`"\n"` bị tách) ở 4 chỗ → cả module hr.api fail compile. Đã sửa hết, `ast.parse` OK. Pattern verify: `python -c "import ast; ast.parse(...)"` trước mỗi restart.

---

## 2026-06-05 — Nâng cấp module **Quản lý nhân sự** (hr `/employees`) ✅ HOÀN TẤT

**Mục tiêu:** Module Quản lý nhân sự đang nghèo nàn nhất (list thuần, detail 6 field read-only) trong khi Tuyển dụng rất công phu → nâng cấp ngang tầm.

**Đã làm:**
- [x] `hr/api.py` thêm 6 endpoint: `get_hr_dashboard` (stats: tổng NV, mới tháng này, số phòng ban, đã nghỉ + phân bổ theo phòng ban/giới tính/chức vụ), `get_employees_filtered` (search tên/mã/SĐT + filter phòng ban/status + phân trang has_more), `get_designations`, `create_employee`, `update_employee` (whitelist field), `get_employee_full` (1 call: employee + nghỉ phép + chấm công tháng + 6 phiếu lương).
- [x] `Employees.vue` viết lại: dashboard 4 stat card + bar phân bổ phòng ban + search (debounce 350ms) + filter phòng ban/status + nút "Thêm nhân viên" (modal đầy đủ field) + list avatar initials (màu hash từ tên) + badge status + "Tải thêm" phân trang.
- [x] `EmployeeDetail.vue` viết lại: profile card avatar + thông tin 10 field + nút "Sửa" (modal) + 3 tab (Nghỉ phép / Chấm công tháng / Lương) reuse `get_employee_full`.
- [x] Build OK (2003 modules). Employees 11.46KB, EmployeeDetail 12.51KB (gấp ~10× bản cũ).
- [x] **Verify console:** create→HR-EMP-00007, update đổi designation+SĐT, get_employee_full trả 4 key.
- [x] **Verify HTTP:** `/hr_app/employees` → 200; API login Administrator → dashboard 7 NV, filtered trả data đủ field. (Guest → PermissionError, đúng bảo mật.)

**Gotcha:** Frappe v16 chặn `count(name) as cnt` dạng chuỗi trong `fields` ("Không được phép dùng hàm SQL dạng chuỗi") → đếm group-by bằng `collections.Counter` trong Python (ERP nội bộ vài trăm NV, lấy 1 lần rồi đếm OK).

---

## 2026-06-05 — Hoàn thiện Tuyển dụng

### Infrastructure
- ✅ CSRF fix dứt điểm: API `get_csrf_token` → `initCSRF()` fetch trước mount → POST + `X-Frappe-CSRF-Token` → DB save OK
- ✅ `frappeRequest` pattern chuẩn: `GET + params` (read), `POST + params` (write)
- ✅ `frappeRequest` chỉ hỗ trợ `params`, không hỗ trợ `data` → fix toàn bộ 3 app

### Tuyển dụng — xong 100% MVP
- ✅ Dashboard: 4 metrics + phễu 6 cột + nguồn CV
- ✅ CRUD Vị trí tuyển + Ứng viên với search/filter
- ✅ Pipeline Kanban 6 cột kéo thả
- ✅ ApplicantDetail `/applicant/:id`: thông tin, CV, notes
- ✅ Lịch phỏng vấn: form thêm PV + timeline lịch sử
- ✅ Tạo Nhân viên: 1-click convert Accepted → Employee
- ✅ Upload CV + AI parse: pypdf extract text → auto-fill form
- ✅ Activity log: timeline mọi action (create, status_change, interview, convert)
- ✅ Socket.IO real-time: auto-refresh dashboard/pipeline/job-list

### Quan trọng đã fix
- ✅ `useFrappeApi` auto-fetch onMounted
- ✅ `watch` thêm `{ immediate: true }` → dashboard/jobs không hiện 0 lúc mount
- ✅ `onMounted` load Dashboard + Jobs song song
- ✅ Socket.IO port 9000 confirmed running (PID 8101)
- ✅ Socket.IO client installed + `useRealtime` composable

---

## 2026-06-04 — Base infrastructure

### 9 app SPA setup
- Tất cả 9 app có Vite build → static HTML → `website_route_rules`
- CSRF cookie reader (sau thay bằng API fetch)
- `useFrappeApi` composable: shallowRef + ref pattern

### HR Home
- 10 module card launcher với icon, màu, mô tả
- 3 "Mới" badge: Tuyển dụng, Chấm công, Bảng lương
- 5 "Sắp ra mắt"

### Duan App
- Dashboard + Projects + Task detail
- Kanban kéo thả 4 cột

### Quantri App
- User list + detail + create
- Role management

### Bugs đã fix
- `CSRFTokenError` — sid cookie HttpOnly, JS không đọc được → API `get_csrf_token`
- `TypeError` khi POST — `frappeRequest` chỉ hỗ trợ `params`, không `data`
- `LinkValidationError` job_title — gửi display text thay vì ID
- `LinkValidationError` designation — mặc định sai
- `Unknown column 'no_of_positions'`, `'mobile_no'` — field không tồn tại
- Dashboard hiện 0 lúc mount — watch thiếu `immediate: true`

---

## Còn tồn đọng

### HR
- [ ] Email tự động (mời PV, thông báo)
- [x] ~~Đánh giá PV (form chấm điểm)~~ — backend `submit_interview_result` + UI ApplicantDetail đã có
- [ ] Chấm công — UI đầy đủ (bảng công tháng/tổng hợp)
- [x] ~~Bảng lương — UI đầy đủ~~ — 2026-06-06: chạy lương trọn gói (BH + thuế TNCN, breakdown, chốt/xóa)
- [x] ~~Chi phí, Hiệu suất, Phúc lợi, Thâm niên, HR Setup~~ — đã xong (các entry 2026-06-05)

### Apps khác
- [x] ~~CRM~~ — 2026-06-06: full (Lead→Opportunity→Customer pipeline, kanban)
- [x] ~~Mua hàng~~ — 2026-06-06: full chain (Supplier→PO→PR→PI→Payment, GL Dr1561/Cr SRBNB→Dr SRBNB+VAT/Cr 331→Dr 331/Cr 1111)
- [x] ~~Tài chính~~ — 2026-06-06: full (Journal Entry CRUD, GL browser, Trial Balance, Chart of Accounts, P&L, Balance Sheet)
- [x] ~~Kinh doanh~~ — 2026-06-06: full chain (Customer→Quotation→SO→DN→SI→Payment, GL Dr632/Cr1561→Dr131/Cr5111+VAT→Dr1111/Cr131)
- [x] ~~Kho~~ — 2026-06-06: full (perpetual inventory + GL, Stock Entry/Reconciliation/Material Request, sổ kho, lô/serial, reorder, QR/barcode, cây kho cha/con)

### Infrastructure
- [ ] Socket.IO auto-restart trong compose
- [ ] CI/CD
- [ ] E2E tests
