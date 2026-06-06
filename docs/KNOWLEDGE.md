# KNOWLEDGE — GPC Custom ERP

Ghi chú kỹ thuật, gotcha, best practice. Cập nhật khi phát hiện điều mới.

---

## Frappe CRM — Cách tổ chức & gọi API (reference)

**Route:** `/crm` (mount SPA qua `website_route_rules`)
**Framework:** Vue 3 + frappe-ui + Pinia

### main.js chuẩn

```js
import { FrappeUI, setConfig, frappeRequest } from 'frappe-ui'

// ✅ ĐÚNG: truyền thẳng frappeRequest, không wrap
setConfig('resourceFetcher', frappeRequest)
app.use(FrappeUI)
```

```js
// ❌ SAI (đã gây treo createResource ở app mới):
setConfig('resourceFetcher', (o) => frappeRequest({ ...o, method: o.method || 'GET' }))
```

### Cách gọi API

CRM **không dùng `createResource` hay `fetch` thủ công**. Nó dùng component có sẵn của `frappe-ui`:

```vue
<!-- List/Kanban tự động -->
<ViewControls
  v-model="leads"
  doctype="CRM Lead"
  :filters="{ converted: 0 }"
  :options="{ allowedViews: ['list', 'group_by', 'kanban'] }"
/>
<KanbanView v-if="..." v-model="leads" :options="{...}" />
```

`ViewControls` lo: pagination, sort, filter, list view, kanban, group by — không cần viết API.

### Cấu trúc frontend CRM/HRMS chuẩn

```
frontend/src/
├── main.js
├── App.vue
├── router.js
├── pages/          ← Các trang chính (Leads.vue, Deals.vue, ...)
├── components/     ← Shared components (ViewControls, KanbanView, ...)
├── stores/         ← Pinia stores (session, settings, meta, ...)
├── composables/    ← useXxx hooks (telephony, broadcast, ...)
├── doctypes/       ← Form config cho từng doctype
└── utils/
```

---

## ✅ GIẢI PHÁP CHUẨN: `useFrappeApi` (frappeRequest)

**Không dùng `createResource` — có bug reactive với app mới.**
**Không dùng `fetch` thủ công.**

### Pattern CHUẨN cho mọi app GPC:

```js
// composables/useFrappeApi.js
import { ref, onMounted, shallowRef } from 'vue'
import { frappeRequest } from 'frappe-ui'

export function useFrappeApi(urlOrOptions, opts = {}) {
  const url = typeof urlOrOptions === 'string' ? urlOrOptions : urlOrOptions?.url
  const options = typeof urlOrOptions === 'object' && urlOrOptions !== null ? urlOrOptions : opts
  const params = options.params || {}
  const auto = options.auto !== false
  const initialData = options.initialData !== undefined ? options.initialData : null

  const data = shallowRef(initialData)
  const loading = ref(false)
  const error = ref(null)

  async function fetch(queryParams = {}) {
    const mergedParams = { ...params, ...queryParams }
    loading.value = true; error.value = null
    try {
      const result = await frappeRequest({ url, method: options.method || 'GET', params: mergedParams })
      data.value = result
      return result
    } catch (e) {
      error.value = e
      return null
    } finally {
      loading.value = false
    }
  }

  if (auto) onMounted(() => { fetch().catch(() => {}) })
  return { data, loading, error, fetch }
}
```

### Usage:

```js
// Auto-fetch khi mount
const { data, loading, error } = useFrappeApi('duan.api.get_dashboard')

// Manual fetch với params
const { data: projects, loading, fetch } = useFrappeApi('duan.api.get_projects', { auto: false, initialData: [] })
// Gọi: await fetch({ search: 'abc', status: 'Open' })
```

### Vì sao?
- `frappeRequest` là low-level API của frappe-ui — ổn định, không bug
- `createResource` bị bug reactive với app tạo sau (loading không set false)
- `fetch` thô thiếu CSRF headers, không auto-unwrap message
- `frappeRequest` có sẵn trong frappe-ui, auto unwrap `message`, handle auth
- `createResource({ url: 'xxx', auto: true })` treo vĩnh viễn — `loading` luôn `true`
- Chỉ xảy ra với app tạo SAU (duan, muahang...), KHÔNG xảy ra với hr/portal/quantri
- `fetch()` thủ công vẫn chạy bình thường, API server OK (curl 200)
- `frappe-ui` version `0.1.261` — giống hệt ở tất cả app

### Những thứ ĐÃ THỬ — ĐỀU KHÔNG FIX ĐƯỢC:
1. ❌ `setConfig('resourceFetcher', frappeRequest)` — CRM pattern, treo
2. ❌ `setConfig('resourceFetcher', (o) => frappeRequest({ ...o, method: 'GET' }))` — ép GET, treo
3. ❌ Thêm `method: 'GET'` vào option `createResource` — treo
4. ❌ Thêm `initialData: {}` — treo
5. ❌ Thêm `onError() {}` — treo
6. ❌ Gọi API của hr từ duan (test xem API có phải thủ phạm) — treo
7. ❌ Định nghĩa `createResource` trong Pinia store — chưa test

### Phân tích source code `frappeRequest` (frappe-ui 0.1.261)

```
createResource → resourceFetcher → frappeRequest → request
                                                ↓
                                    transformRequest: default method = POST
                                    (POST cần CSRF token, SPA không có)
```

Flow:
1. `createResource` gọi `resourceFetcher({...options, params})`
2. `request` function copy options, gọi `transformRequest(_options)` 
3. `transformRequest` nhận `_options` GỐC (không có method)
4. `method: options.method || 'POST'` → **POST** (vì original không có method)
5. POST tới Frappe API → cần CSRF token → fail hoặc treo

**Tuy nhiên:** thêm `method: 'GET'` vào `createResource` option vẫn treo → còn nguyên nhân khác chưa tìm ra.

### ✅ Workaround hiện tại: dùng `fetch` thủ công

Pattern CHUẨN cho mọi app GPC:

```js
// ── pages/Home.vue ──
import { ref, onMounted } from 'vue'

const data = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const res = await fetch('/api/method/<app>.<module>.<endpoint>')
    const json = await res.json()
    data.value = json.message   // frappe bọc response trong { message: ... }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
```

### TODO: tạo composable `useApi` để chuẩn hóa

```js
// composables/useApi.js
import { ref, onMounted } from 'vue'

export function useApi(url, params = {}) {
  const data = ref(null)
  const loading = ref(true)
  const error = ref(null)

  async function fetchData(query = {}) {
    loading.value = true; error.value = null
    try {
      const q = new URLSearchParams(query)
      const res = await fetch(`/api/method/${url}?${q}`)
      const json = await res.json()
      data.value = json.message
    } catch (e) { error.value = e.message } finally { loading.value = false }
  }

  onMounted(() => fetchData(params))
  return { data, loading, error, fetch: fetchData }
}
```

→ Để AI khác implement composable này rồi áp cho tất cả app.

---

## Portal Module seed

File: `portal/portal/setup.py`

8 phân hệ mặc định (gọi từ `after_install` + `after_migrate`):

| sort_order | route_key | module_name | required_role |
|-----------|-----------|-------------|---------------|
| 5 | quantri | Quản trị | System Manager |
| 10 | hr | Nhân sự | HR User |
| 20 | crm | CRM | Sales User |
| 30 | tckt | Tài chính kế toán | Accounts User |
| 35 | muahang | Mua hàng | Purchase User |
| 40 | kho | Kho | Stock User |
| 50 | kinhdoanh | Kinh doanh | Sales User |
| 60 | duan | Dự án | Projects User |

---

## Docker Compose — Cấu trúc DEV

### Services
- `db` — MariaDB 11.8 (port 3306, healthcheck)
- `redis` — Redis 8.6-alpine
- `frappe` — `ghcr.io/nguyentrieu210/frappe-vn:v16` (port 8000 web, 9000 socket.io)

### Command init
Mỗi lần container start, loop install 9 app:
```bash
for a in portal hr quantri muahang crm_ui tckt kho kinhdoanh duan; do
  pip install -e apps/$a -q
  ln -sfn apps/$a/$a/public sites/assets/$a
done
```

### Volumes
- Bind-mount: `../apps/<name>:/home/frappe/frappe-bench/apps/<name>` (9 app)
- Named volume: `<name>_nm` cho `frontend/node_modules` (9 app, tránh bind-mount Windows chậm)
- Named volume: `sites`, `db-data`, `redis-data`

---

## Các gotcha đã gặp

### 1. Module name trùng → đổi tên GPC
`Portal/HR/CRM/Projects` trùng module có sẵn → scaffold dùng `GPC Portal`, `GPC HR`, `GPC CRM`, `GPC Projects`

### 2. apps.txt thiếu newline
`apps.txt` (seed từ image) thiếu newline cuối → append dính dòng. Thêm bước bảo đảm newline trước khi echo.

### 3. Task ERPNext không có `assigned_to`
ERPNext Task dùng `_assign` (JSON array) cho phân công. Field `assigned_to` không tồn tại.

### 4. Socket.IO không chạy trong DEV
Procfile gen `socketio=None` (node qua nvm, không trên PATH). Chỉ `bench serve`, realtime chưa hoạt động → console browser spam `ERR_EMPTY_RESPONSE :9000`.

### 5. createResource không phải Vue ref
`frappe-ui`'s `createResource` destructured values (`data`, `loading`, `error`) KHÔNG PHẢI Vue `ref`. Trong `<script>`, truy cập trực tiếp `data`, `loading`, `error` — không dùng `.value`. Trong `<template>`, dùng bình thường. CHỈ dùng `.value` cho `ref()` thật sự.

### 6. flit_core cần README.md + __version__
`pip install -e` yêu cầu `README.md` tồn tại và `__version__ = "0.0.1"` trong `__init__.py`.

### 7. Container recreate mất pip install
Compose `command` auto cài lại `pip install -e` mỗi lần start. Không thì recreate mất hết editable install.

---

## Kho — Perpetual Inventory + GL trên CoA TT200

App `kho` reuse **doctype Stock gốc ERPNext** (Item, Warehouse, Stock Entry, Stock Reconciliation, Material Request, Bin, Stock Ledger Entry, Batch, Serial No) — KHÔNG tạo doctype mới. `kho.api.setup_kho()` idempotent cấu hình 1 lần.

### Tài khoản kho (Company `GPC`, abbr `G`, CoA TT200)
| Company field | Giá trị | Ghi chú |
|---|---|---|
| `enable_perpetual_inventory` | 1 | bắt buộc để sinh GL khi submit phiếu kho |
| `default_inventory_account` | `1561 - Giá mua hàng hóa` | ledger (non-group). Mặc định ban đầu là 158 (kho bảo thuế) → sai, đã repoint |
| `stock_adjustment_account` | `Chênh lệch kho (Stock Adjustment)` (tạo dưới 642, Expense) | **THIẾU mặc định** → Material Receipt/Issue/Reconciliation không hạch toán nếu chưa set |
| `stock_received_but_not_billed` | `Hàng mua chưa có hóa đơn (SRBNB)` (tạo dưới 338, Liability) | cho Mua hàng (Purchase Receipt) sau này |
| `default_expense_account` | `632 - Giá vốn hàng bán` | COGS |
| `cost_center` | `Chính - G` | |

- Warehouse mặc định ERPNext tạo sẵn (Tất cả kho/Thành phẩm/...) nhưng **account = null** → fallback dùng `default_inventory_account`. setup_kho gán account = 1561 cho kho lẻ + tạo 4 kho VN (Kho chính/NVL/TP/hàng hóa) + set kho mặc định trong Stock Settings.
- **GL khi submit:** Material Receipt 10×1000 → `Dr 1561 / Cr Chênh lệch kho 10.000`. Material Transfer cùng account → **không sinh GL** (đúng). Stock Reconciliation lệch → GL điều chỉnh đối ứng Stock Adjustment.

### Gotcha Kho
1. Field `expenses_included_in_valuation` **không tồn tại** trên Company bản v16 này → luôn guard `cdoc.meta.has_field(...)` trước khi đọc/ghi field stock của Company.
2. Aggregate dạng chuỗi (`sum(actual_qty) as qty`, `count(...)`) trong `fields=` bị v16 chặn → **gộp Bin bằng Python** (ERP nội bộ, số item ít).
3. Stock Entry: set `stock_entry_type` (link "Stock Entry Type"), ERPNext tự suy `purpose`. Material Receipt cần `t_warehouse` + `basic_rate` (giá nhập); Issue cần `s_warehouse`; Transfer cần cả hai.
4. **Build frontend:** node/yarn KHÔNG trên PATH → `export PATH=/home/frappe/.nvm/versions/node/v24.12.0/bin:$PATH` rồi `yarn build` trong `apps/kho/frontend`. developer_mode=1 nên api.py tự reload (không cần restart cho backend).
5. `index.css` KHÔNG có `@tailwind`/`@layer` (utility do frappe-ui vite plugin inject) → **không dùng `@apply` trong `<style scoped>`**. Class form dùng `.inp` (plain CSS trong index.css).
6. Verify ghi/đọc qua HTTP cần CSRF: login → `kho.api.get_csrf_token` → POST kèm header `X-Frappe-CSRF-Token`. (Frontend `main.js` fetch token trước `app.mount`.)

---

## Mua hàng — Full chuỗi PO→PR→PI→Payment trên CoA TT200

App `muahang` reuse **doctype Buying gốc ERPNext** (Supplier, Purchase Order, Purchase Receipt, Purchase Invoice, Payment Entry, Material Request type=Purchase). `muahang.api.setup_muahang()` idempotent.

### Chuỗi GL hoàn chỉnh (perpetual inventory ON)

| Bước | Doctype | Bút toán GL |
|---|---|---|
| 1. Đơn mua (PO) | Purchase Order | Không sinh GL (chỉ là cam kết) |
| 2. Nhập mua (PR) | Purchase Receipt | **Dr 1561 (tồn kho) / Cr SRBNB** |
| 3. Hóa đơn (PI) | Purchase Invoice | **Dr SRBNB + Dr VAT 133 / Cr 331** |
| 4. Thanh toán | Payment Entry | **Dr 331 / Cr 1111 (tiền)** |

### Gotcha Mua hàng

1. **Purchase tax (GTGT):** `_apply_purchase_tax` dùng `erpnext.controllers.accounts_controller.get_taxes_and_charges` + `doc.append("taxes", ...)`. Template "Vietnam Tax - G" có sẵn. PO/PR/PI đều có `taxes` child table.

2. **ERPNext mappers**: `material_request.make_purchase_order` (import là `make_purchase_order(source_name)`), `purchase_order.make_purchase_receipt`, `purchase_receipt.make_purchase_invoice`, `payment_entry.get_payment_entry`. Mapper tự copy items + link nguồn. **Cần gán supplier trước insert** (mappers không tự chọn NCC).

3. **`make_purchase_order(source_name)`** từ material_request KHÔNG set supplier → phải gán hoặc `frappe.throw`. Dùng `po.supplier = supplier` trước `.insert()`.

4. **Cash/Bank cho Payment Entry:** `paid_from` phải là Account `account_type` = "Cash" hoặc "Bank". TT200 VN: ưu tiên 1111 (Tiền Việt Nam).

5. **Cross-app API**: Muahang gọi `kho.api.get_items` / `kho.api.get_warehouses` (whitelisted) qua HTTP → item picker không cần import Python. Hoạt động vì cả 2 app cùng site.

6. **`_cash_account()`**: dò `frappe.db.get_value` theo `account_type` Cash → Bank, ưu tiên theo số hiệu VN (1111→111→1121→112). Fallback: lấy bất kỳ ledger Cash/Bank nào.
