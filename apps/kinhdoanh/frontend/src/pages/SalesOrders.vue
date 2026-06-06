<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Đơn bán (SO)" icon="shopping-cart" icon-class="text-rose-600">
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Tạo đơn bán</button>
    </PageHeader>
    <main class="flex-1 p-4 max-w-6xl mx-auto w-full">
      <DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm số SO / khách hàng…" :search-keys="['name', 'customer_name']" :filters="filterDefs" @row-click="goDetail">
        <template #col-grand_total="{ value }"><span class="font-semibold">{{ fmtVnd(value) }}</span></template>
        <template #col-status_vi="{ row }"><StatusBadge :status="row.status_vi" :tone="row.docstatus === 0 ? 'amber' : (row.status === 'Completed' ? 'green' : 'blue')" /></template>
        <template #col-transaction_date="{ value }">{{ $fmtDate(value) }}</template>
        <template #actions="{ row }">
          <button v-if="row.docstatus === 0" class="btn-success px-2 py-1 rounded text-xs" @click="quick('submit_sales_order', row)">Chốt</button>
        </template>
      </DataTable>
    </main>

    <FormModal :show="show" title="Tạo đơn bán" icon="shopping-cart" width="max-w-3xl" :saving="saving" hide-footer @close="show = false">
      <div class="space-y-3">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div><label class="text-xs text-gray-500">Khách hàng *</label><EntityPicker v-model="form.customer" api="kinhdoanh.api.get_customers" result-key="entries" value-key="name" label-key="customer_name" sub-key="name" icon="user" /></div>
          <div><label class="text-xs text-gray-500">Ngày đặt</label><input v-model="form.transaction_date" type="date" class="inp" /></div>
          <div><label class="text-xs text-gray-500">Ngày giao</label><input v-model="form.delivery_date" type="date" class="inp" /></div>
        </div>
        <div><label class="text-xs text-gray-500">Dòng hàng</label><LineItemsEditor v-model="form.items" price-api="kinhdoanh.api.get_selling_price" /></div>
      </div>
      <template #footer>
        <button class="btn-secondary px-4 py-2 rounded-lg text-sm" @click="show = false">Hủy</button>
        <button class="btn-secondary px-4 py-2 rounded-lg text-sm" :disabled="saving" @click="save(0)">Lưu nháp</button>
        <button class="btn-primary px-4 py-2 rounded-lg text-sm font-medium" :disabled="saving" @click="save(1)">{{ saving ? 'Đang lưu…' : 'Lưu & chốt' }}</button>
      </template>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import { PageHeader, DataTable, FormModal, EntityPicker, LineItemsEditor, StatusBadge, useToast, callApi, fmtVnd, today } from '@shared'
const router = useRouter(); const { toast, ok, err } = useToast()
const rows = ref([]); const loading = ref(false)
const columns = [
  { key: 'name', label: 'Số SO' }, { key: 'customer_name', label: 'Khách hàng' },
  { key: 'transaction_date', label: 'Ngày' }, { key: 'grand_total', label: 'Tổng tiền', align: 'right' },
  { key: 'status_vi', label: 'Trạng thái' },
]
const filterDefs = [{ key: 'status', label: 'Trạng thái', options: [
  { value: 'Draft', label: 'Nháp' }, { value: 'To Deliver and Bill', label: 'Chờ giao & HĐ' },
  { value: 'To Bill', label: 'Chờ HĐ' }, { value: 'To Deliver', label: 'Chờ giao' }, { value: 'Completed', label: 'Hoàn tất' },
] }]
async function reload() { loading.value = true; try { rows.value = (await callApi('kinhdoanh.api.get_sales_orders', { page_length: 200 }, 'GET'))?.entries || [] } finally { loading.value = false } }
reload()
const show = ref(false); const saving = ref(false)
const form = reactive({ customer: '', transaction_date: today(), delivery_date: '', items: [] })
function openCreate() { form.customer = ''; form.transaction_date = today(); form.delivery_date = ''; form.items = []; show.value = true }
async function save(submit) {
  if (!form.customer) return err('Chọn khách hàng')
  const items = (form.items || []).filter((l) => l.item_code && l.qty)
  if (!items.length) return err('Thêm ít nhất 1 dòng hàng')
  saving.value = true
  try {
    await callApi('kinhdoanh.api.create_sales_order', { customer: form.customer, items: JSON.stringify(items.map((l) => ({ item_code: l.item_code, qty: l.qty, rate: l.rate }))), transaction_date: form.transaction_date, delivery_date: form.delivery_date || undefined, apply_tax: 1, submit })
    ok(submit ? 'Đã tạo & chốt đơn' : 'Đã lưu nháp'); show.value = false; reload()
  } catch (e) { err(e?.message || 'Lỗi') } finally { saving.value = false }
}
function goDetail(row) { router.push('/sales-orders/' + row.name) }
async function quick(m, row) { try { await callApi('kinhdoanh.api.' + m, { name: row.name }); ok('Đã chốt'); reload() } catch (e) { err(e?.message) } }
</script>
