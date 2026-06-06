<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Xuất giao (DN)" icon="truck" icon-class="text-emerald-600">
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Tạo phiếu giao</button>
    </PageHeader>
    <main class="flex-1 p-4 max-w-5xl mx-auto w-full">
      <DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm số DN / khách hàng…" :search-keys="['name', 'customer_name']" @row-click="goDetail">
        <template #col-grand_total="{ value }"><span class="font-semibold">{{ fmtVnd(value) }}</span></template>
        <template #col-docstatus="{ row }"><StatusBadge :status="row.docstatus === 1 ? 'Đã xuất giao' : 'Nháp'" /></template>
        <template #col-posting_date="{ value }">{{ $fmtDate(value) }}</template>
      </DataTable>
    </main>

    <FormModal :show="show" title="Tạo phiếu xuất giao" icon="truck" width="max-w-3xl" :saving="saving" hide-footer @close="show = false">
      <div class="space-y-3">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div><label class="text-xs text-gray-500">Khách hàng *</label><EntityPicker v-model="form.customer" api="kinhdoanh.api.get_customers" result-key="entries" value-key="name" label-key="customer_name" icon="user" /></div>
          <div><label class="text-xs text-gray-500">Kho xuất *</label><EntityPicker v-model="form.warehouse" api="kho.api.get_warehouses" result-key="" value-key="name" label-key="warehouse_name" icon="home" /></div>
          <div><label class="text-xs text-gray-500">Ngày xuất</label><input v-model="form.posting_date" type="date" class="inp" /></div>
        </div>
        <div><label class="text-xs text-gray-500">Dòng hàng</label><LineItemsEditor v-model="form.items" price-api="kinhdoanh.api.get_selling_price" /></div>
      </div>
      <template #footer>
        <button class="btn-secondary px-4 py-2 rounded-lg text-sm" @click="show = false">Hủy</button>
        <button class="btn-primary px-4 py-2 rounded-lg text-sm font-medium" :disabled="saving" @click="save">{{ saving ? 'Đang lưu…' : 'Lưu & xuất giao' }}</button>
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
  { key: 'name', label: 'Số DN' }, { key: 'customer_name', label: 'Khách hàng' },
  { key: 'posting_date', label: 'Ngày' }, { key: 'grand_total', label: 'Tổng tiền', align: 'right' },
  { key: 'docstatus', label: 'Trạng thái' },
]
async function reload() { loading.value = true; try { rows.value = (await callApi('kinhdoanh.api.get_delivery_notes', { page_length: 200 }, 'GET'))?.entries || [] } finally { loading.value = false } }
reload()
const show = ref(false); const saving = ref(false)
const form = reactive({ customer: '', warehouse: '', posting_date: today(), items: [] })
function openCreate() { form.customer = ''; form.warehouse = ''; form.posting_date = today(); form.items = []; show.value = true }
async function save() {
  if (!form.customer) return err('Chọn khách hàng')
  const items = (form.items || []).filter((l) => l.item_code && l.qty)
  if (!items.length) return err('Thêm ít nhất 1 dòng hàng')
  saving.value = true
  try {
    await callApi('kinhdoanh.api.create_delivery_note', { customer: form.customer, items: JSON.stringify(items.map((l) => ({ item_code: l.item_code, qty: l.qty, rate: l.rate, warehouse: form.warehouse || undefined }))), set_warehouse: form.warehouse || undefined, posting_date: form.posting_date, apply_tax: 1, submit: 1 })
    ok('Đã xuất giao'); show.value = false; reload()
  } catch (e) { err(e?.message || 'Lỗi') } finally { saving.value = false }
}
function goDetail(row) { router.push('/delivery-notes/' + row.name) }
</script>
