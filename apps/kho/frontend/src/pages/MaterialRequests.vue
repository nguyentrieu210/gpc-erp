<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
      <button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5" /></button>
      <FeatherIcon name="file-text" class="h-5 w-5 text-amber-600" />
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Yêu cầu vật tư</h1>
      <Button variant="solid" theme="orange" @click="openCreate">+ Tạo yêu cầu</Button>
    </header>

    <main class="flex-1 p-4 max-w-3xl mx-auto w-full">
      <div class="rounded-lg border bg-white divide-y">
        <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
        <div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có yêu cầu</div>
        <div v-for="r in rows" :key="r.name" class="px-4 py-3">
          <div class="flex items-center">
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-900">{{ r.name }}
                <span class="text-xs px-2 py-0.5 rounded-full ml-1 bg-amber-100 text-amber-700">{{ r.type_label }}</span>
              </div>
              <div class="text-xs text-gray-500">{{ $fmtDate(r.transaction_date) }} · {{ r.status }}</div>
            </div>
            <Button v-if="r.docstatus===0" variant="solid" theme="green" size="sm" :loading="busy===r.name" @click="submitMr(r)">Gửi duyệt</Button>
            <span v-else class="text-xs text-emerald-600">Đã gửi</span>
          </div>
        </div>
      </div>
    </main>

    <div v-if="showCreate" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="showCreate=false">
      <div class="bg-white rounded-xl w-full max-w-2xl p-5 max-h-[92vh] overflow-y-auto">
        <h3 class="text-lg font-semibold mb-4">Tạo yêu cầu vật tư</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
          <label class="block"><span class="text-sm text-gray-600 block mb-1">Loại yêu cầu</span>
            <select v-model="form.material_request_type" class="inp"><option v-for="t in types" :key="t.value" :value="t.value">{{ t.label }}</option></select>
          </label>
          <label class="block"><span class="text-sm text-gray-600 block mb-1">Ngày cần</span><input type="date" v-model="form.schedule_date" class="inp" /></label>
          <label class="block sm:col-span-2"><span class="text-sm text-gray-600 block mb-1">Kho đích</span>
            <select v-model="form.warehouse" class="inp"><option v-for="w in stockWh" :key="w.name" :value="w.name">{{ w.warehouse_name }}</option></select>
          </label>
        </div>

        <div class="border rounded-lg overflow-hidden mb-3">
          <div class="grid grid-cols-12 gap-1 bg-gray-50 px-2 py-1.5 text-xs font-medium text-gray-500">
            <div class="col-span-6">Hàng hóa</div>
            <div class="col-span-2 text-center">ĐVT</div>
            <div class="col-span-3 text-right">SL</div>
            <div class="col-span-1"></div>
          </div>
          <div v-for="(r,i) in form.items" :key="i" class="grid grid-cols-12 gap-1 px-2 py-1.5 items-center border-t">
            <select v-model="r.item_code" class="col-span-6 inp !py-1 !text-xs bg-white">
              <option value="">— chọn —</option>
              <option v-for="it in itemOpts" :key="it.name" :value="it.item_code">
                [{{ it.item_code }}] — {{ it.item_name }}
              </option>
            </select>
            <div class="col-span-2 text-center text-xs text-gray-600 font-medium truncate">
              {{ getItemUom(r.item_code) || '—' }}
            </div>
            <input v-model.number="r.qty" type="number" class="col-span-3 inp !py-1 text-right" />
            <button class="col-span-1 text-red-500 text-xs font-semibold" @click="form.items.splice(i,1)">×</button>
          </div>
        </div>
        <Button variant="subtle" size="sm" @click="form.items.push({ item_code:'', qty:1 })">+ Thêm dòng</Button>

        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showCreate=false">Hủy</Button>
          <Button variant="outline" :loading="saving" @click="save(0)">Lưu nháp</Button>
          <Button variant="solid" theme="green" :loading="saving" @click="save(1)">Lưu & Gửi</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi, callApi } from '../composables/useFrappeApi'

const rows = ref([]), loading = ref(false), busy = ref('')
const { data: types } = useFrappeApi('kho.api.get_material_request_types', { initialData: [] })
const { data: warehouses } = useFrappeApi('kho.api.get_warehouses', { initialData: [] })
const { data: itemsResp } = useFrappeApi('kho.api.get_items', { initialData: { items: [] }, params: { page_length: 500 } })
const stockWh = computed(() => (warehouses.value || []).filter(w => !w.is_group))
const itemOpts = computed(() => itemsResp.value?.items || [])

function getItemUom(code) {
  const it = itemOpts.value.find(x => x.item_code === code)
  return it ? it.stock_uom : ''
}

async function reload() {
  loading.value = true
  try { const r = await callApi('kho.api.get_material_requests', {}, 'GET'); rows.value = r?.entries || [] }
  finally { loading.value = false }
}
reload()

const showCreate = ref(false), saving = ref(false)
const form = reactive({ material_request_type: 'Material Issue', schedule_date: new Date().toISOString().slice(0,10), warehouse: '', items: [{ item_code: '', qty: 1 }] })
function openCreate() {
  Object.assign(form, { material_request_type: 'Material Issue', schedule_date: new Date().toISOString().slice(0,10), warehouse: stockWh.value?.[0]?.name || '', items: [{ item_code: '', qty: 1 }] })
  showCreate.value = true
}
async function save(submit) {
  const items = form.items.filter(r => r.item_code && r.qty)
  if (!items.length) { alert('Thêm ít nhất 1 dòng'); return }
  saving.value = true
  try {
    await callApi('kho.api.create_material_request', {
      material_request_type: form.material_request_type, items: JSON.stringify(items),
      schedule_date: form.schedule_date, warehouse: form.warehouse, submit,
    })
    showCreate.value = false; await reload()
  } catch (e) { alert('Lỗi: ' + (e?.message || e)) } finally { saving.value = false }
}
async function submitMr(r) {
  busy.value = r.name
  try { await callApi('kho.api.submit_material_request', { name: r.name }); await reload() }
  catch (e) { alert('Lỗi: ' + (e?.message || e)) } finally { busy.value = '' }
}
</script>
