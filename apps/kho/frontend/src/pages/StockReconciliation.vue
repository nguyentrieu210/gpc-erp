<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
      <button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5" /></button>
      <FeatherIcon name="check-square" class="h-5 w-5 text-teal-600" />
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Kiểm kê</h1>
      <Button variant="solid" theme="orange" @click="openCreate">+ Lập phiếu</Button>
    </header>

    <main class="flex-1 p-4 max-w-3xl mx-auto w-full">
      <div class="rounded-lg border bg-white divide-y">
        <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
        <div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có phiếu kiểm kê</div>
        <div v-for="r in rows" :key="r.name" class="flex items-center px-4 py-3">
          <div class="flex-1 min-w-0">
            <div class="font-medium text-gray-900">{{ r.name }}</div>
            <div class="text-xs text-gray-500">{{ $fmtDate(r.posting_date) }} · {{ r.purpose }}</div>
          </div>
          <div class="text-right">
            <div class="text-sm font-semibold" :class="r.difference_amount >= 0 ? 'text-emerald-600' : 'text-red-600'">{{ fmtVnd(r.difference_amount) }}</div>
            <span class="text-xs" :class="r.docstatus===1 ? 'text-emerald-600' : 'text-amber-600'">{{ r.docstatus===1 ? 'Đã chốt' : 'Nháp' }}</span>
          </div>
        </div>
      </div>
    </main>

    <div v-if="showCreate" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="showCreate=false">
      <div class="bg-white rounded-xl w-full max-w-2xl p-5 max-h-[92vh] overflow-y-auto">
        <h3 class="text-lg font-semibold mb-4">Phiếu kiểm kê tồn</h3>
        <div class="flex gap-2 items-end mb-3">
          <label class="block flex-1"><span class="text-sm text-gray-600 block mb-1">Kho kiểm kê</span>
            <select v-model="warehouse" class="inp">
              <option value="">— chọn kho kiểm kê —</option>
              <option v-for="w in stockWh" :key="w.name" :value="w.name">{{ w.warehouse_name }}</option>
            </select>
          </label>
          <Button variant="outline" :loading="prefilling" @click="prefill">Tải tồn hiện tại</Button>
        </div>

        <div v-if="lines.length" class="border rounded-lg overflow-hidden">
          <div class="grid grid-cols-12 gap-1 bg-gray-50 px-2 py-1.5 text-xs font-medium text-gray-500">
            <div class="col-span-4">Hàng hóa</div>
            <div class="col-span-2 text-center">ĐVT</div>
            <div class="col-span-2 text-right">Sổ sách</div>
            <div class="col-span-2 text-right">Thực tế</div>
            <div class="col-span-2 text-right">Chênh</div>
          </div>
          <div v-for="(l,i) in lines" :key="i" class="grid grid-cols-12 gap-1 px-2 py-1.5 items-center border-t text-sm">
            <div class="col-span-4 truncate">{{ l.item_name }}</div>
            <div class="col-span-2 text-center text-xs text-gray-500 font-medium truncate">{{ l.stock_uom || '—' }}</div>
            <div class="col-span-2 text-right text-gray-500">{{ fmtQty(l.current_qty) }}</div>
            <input v-model.number="l.qty" type="number" class="col-span-2 inp !py-1 text-right" />
            <div class="col-span-2 text-right" :class="(l.qty - l.current_qty) === 0 ? 'text-gray-400' : ((l.qty - l.current_qty) > 0 ? 'text-emerald-600' : 'text-red-600')">
              {{ (l.qty - l.current_qty) > 0 ? '+' : '' }}{{ fmtQty(l.qty - l.current_qty) }}
            </div>
          </div>
        </div>
        <div v-else class="text-center text-gray-400 text-sm py-6">Chọn kho rồi bấm “Tải tồn hiện tại”.</div>

        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showCreate=false">Hủy</Button>
          <Button variant="solid" theme="green" :loading="saving" :disabled="!lines.length" @click="save">Lưu & Chốt</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi, callApi } from '../composables/useFrappeApi'

const rows = ref([]), loading = ref(false)
const { data: warehouses } = useFrappeApi('kho.api.get_warehouses', { initialData: [] })
const stockWh = computed(() => (warehouses.value || []).filter(w => !w.is_group))

async function reload() {
  loading.value = true
  try { const r = await callApi('kho.api.get_stock_reconciliations', {}, 'GET'); rows.value = r?.entries || [] }
  finally { loading.value = false }
}
reload()

const showCreate = ref(false), saving = ref(false), prefilling = ref(false)
const warehouse = ref(''), lines = ref([])

watch(stockWh, (newVal) => {
  if (newVal && newVal.length && !warehouse.value) {
    warehouse.value = newVal[0].name
  }
}, { immediate: true })

function openCreate() { warehouse.value = stockWh.value?.[0]?.name || ''; lines.value = []; showCreate.value = true }
async function prefill() {
  if (!warehouse.value) return
  prefilling.value = true
  try { lines.value = await callApi('kho.api.get_recon_prefill', { warehouse: warehouse.value }, 'GET') }
  finally { prefilling.value = false }
}
async function save() {
  const items = lines.value.map(l => ({ item_code: l.item_code, warehouse: warehouse.value, qty: l.qty, valuation_rate: l.valuation_rate }))
  saving.value = true
  try {
    await callApi('kho.api.create_stock_reconciliation', { warehouse: warehouse.value, items: JSON.stringify(items), submit: 1 })
    showCreate.value = false; await reload()
  } catch (e) { alert('Lỗi: ' + (e?.message || e)) } finally { saving.value = false }
}

function fmtQty(v) { return Number(v || 0).toLocaleString('vi-VN') }
function fmtVnd(v) { return Number(v || 0).toLocaleString('vi-VN') + ' ₫' }
</script>
