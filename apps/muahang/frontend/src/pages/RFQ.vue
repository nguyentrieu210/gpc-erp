<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Yêu cầu báo giá (RFQ)" icon="mail" icon-class="text-sky-600">
      <button v-if="tab === 'rfq'" class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Tạo RFQ</button>
    </PageHeader>
    <main class="flex-1 p-4 max-w-5xl mx-auto w-full space-y-3">
      <div class="flex gap-1">
        <button class="text-xs px-3 py-1.5 rounded-full" :class="tab === 'rfq' ? 'bg-indigo-600 text-white' : 'bg-gray-100'" @click="tab = 'rfq'">Yêu cầu báo giá</button>
        <button class="text-xs px-3 py-1.5 rounded-full" :class="tab === 'sq' ? 'bg-indigo-600 text-white' : 'bg-gray-100'" @click="tab = 'sq'; loadSQ()">Báo giá NCC</button>
      </div>

      <DataTable v-if="tab === 'rfq'" :rows="rfqs" :columns="rfqCols" :loading="loading" search-placeholder="Tìm RFQ…" :search-keys="['name']" :clickable="false">
        <template #col-transaction_date="{ value }">{{ $fmtDate(value) }}</template>
        <template #col-supplier_count="{ value }">{{ value }} NCC</template>
        <template #col-docstatus="{ row }"><StatusBadge :status="row.docstatus === 1 ? 'Đã gửi' : 'Nháp'" /></template>
      </DataTable>

      <DataTable v-else :rows="sqs" :columns="sqCols" :loading="loadingSQ" search-placeholder="Tìm báo giá…" :search-keys="['name', 'supplier_name']" :clickable="false">
        <template #col-grand_total="{ value }"><span class="font-semibold">{{ fmtVnd(value) }}</span></template>
        <template #col-transaction_date="{ value }">{{ $fmtDate(value) }}</template>
        <template #actions="{ row }">
          <button v-if="row.docstatus === 1" class="btn-primary px-2 py-1 rounded text-xs" @click="toPO(row)">→ Tạo PO</button>
        </template>
      </DataTable>
    </main>

    <FormModal :show="show" title="Tạo yêu cầu báo giá" icon="mail" width="max-w-3xl" :saving="saving" hide-footer @close="show = false">
      <div class="space-y-3">
        <div>
          <label class="text-xs text-gray-500">Nhà cung cấp gửi yêu cầu *</label>
          <div class="flex flex-wrap gap-2 mt-1 max-h-32 overflow-auto border rounded-lg p-2">
            <label v-for="s in suppliers" :key="s.name" class="flex items-center gap-1 text-sm">
              <input type="checkbox" :value="s.name" v-model="form.suppliers" /> {{ s.supplier_name }}
            </label>
          </div>
        </div>
        <div><label class="text-xs text-gray-500">Mặt hàng cần báo giá</label><LineItemsEditor v-model="form.items" :show-uom="false" /></div>
      </div>
      <template #footer>
        <button class="btn-secondary px-4 py-2 rounded-lg text-sm" @click="show = false">Hủy</button>
        <button class="btn-primary px-4 py-2 rounded-lg text-sm font-medium" :disabled="saving" @click="save">{{ saving ? 'Đang gửi…' : 'Gửi yêu cầu' }}</button>
      </template>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import { PageHeader, DataTable, FormModal, StatusBadge, useToast, callApi, fmtVnd } from '@shared'
const router = useRouter(); const { toast, ok, err } = useToast()
const tab = ref('rfq')
const rfqs = ref([]); const loading = ref(false)
const sqs = ref([]); const loadingSQ = ref(false)
const suppliers = ref([])
const rfqCols = [{ key: 'name', label: 'Số RFQ' }, { key: 'transaction_date', label: 'Ngày' }, { key: 'supplier_count', label: 'NCC' }, { key: 'docstatus', label: 'Trạng thái' }]
const sqCols = [{ key: 'name', label: 'Số báo giá' }, { key: 'supplier_name', label: 'Nhà cung cấp' }, { key: 'transaction_date', label: 'Ngày' }, { key: 'grand_total', label: 'Tổng', align: 'right' }]
async function reload() { loading.value = true; try { rfqs.value = (await callApi('muahang.api.get_rfqs', { page_length: 200 }, 'GET'))?.entries || [] } finally { loading.value = false } }
async function loadSQ() { loadingSQ.value = true; try { sqs.value = (await callApi('muahang.api.get_supplier_quotations', { page_length: 200 }, 'GET'))?.entries || [] } finally { loadingSQ.value = false } }
reload()
callApi('muahang.api.get_suppliers', { page_length: 500 }, 'GET').then((r) => { suppliers.value = r?.suppliers || [] }).catch(() => {})
const show = ref(false); const saving = ref(false)
const form = reactive({ suppliers: [], items: [] })
function openCreate() { form.suppliers = []; form.items = []; show.value = true }
async function save() {
  if (!form.suppliers.length) return err('Chọn ít nhất 1 NCC')
  const items = (form.items || []).filter((l) => l.item_code && l.qty)
  if (!items.length) return err('Thêm ít nhất 1 mặt hàng')
  saving.value = true
  try { await callApi('muahang.api.create_rfq', { items: JSON.stringify(items.map((l) => ({ item_code: l.item_code, qty: l.qty }))), suppliers: JSON.stringify(form.suppliers), submit: 1 }); ok('Đã gửi RFQ'); show.value = false; reload() }
  catch (e) { err(e?.message || 'Lỗi') } finally { saving.value = false }
}
async function toPO(row) { try { const po = await callApi('muahang.api.make_po_from_supplier_quotation', { name: row.name }); ok('Đã tạo PO ' + po.name); router.push('/po/' + po.name) } catch (e) { err(e?.message) } }
</script>
