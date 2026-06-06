<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
      <button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5" /></button>
      <FeatherIcon name="repeat" class="h-5 w-5 text-violet-600" />
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Nhập / Xuất / Chuyển</h1>
      <Button variant="solid" theme="orange" @click="openCreate">+ Lập phiếu</Button>
    </header>

    <main class="flex-1 p-4 max-w-4xl mx-auto w-full">
      <div class="flex gap-2 mb-3 overflow-x-auto">
        <button v-for="f in typeFilters" :key="f.value"
          class="px-3 py-1.5 rounded-full text-sm whitespace-nowrap border"
          :class="typeFilter===f.value ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-gray-600'"
          @click="typeFilter=f.value; page=1; reload()">{{ f.label }}</button>
      </div>

      <div class="rounded-lg border bg-white divide-y">
        <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
        <div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có phiếu</div>
        <div v-for="se in rows" :key="se.name" class="px-4 py-3">
          <div class="flex items-center gap-2">
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-900">{{ se.name }}
                <span class="text-xs px-2 py-0.5 rounded-full ml-1" :class="badge(se.stock_entry_type)">{{ se.type_label }}</span>
              </div>
              <div class="text-xs text-gray-500 truncate">
                {{ se.from_warehouse ? short(se.from_warehouse) : '' }}{{ se.from_warehouse && se.to_warehouse ? ' → ' : '' }}{{ se.to_warehouse ? short(se.to_warehouse) : '' }}
                · {{ $fmtDate(se.posting_date) }}
              </div>
            </div>
            <div class="text-right shrink-0">
              <div class="font-semibold">{{ fmtVnd(se.total_amount) }}</div>
              <span class="text-xs" :class="se.docstatus===1 ? 'text-emerald-600' : 'text-amber-600'">{{ se.docstatus===1 ? 'Đã chốt' : 'Nháp' }}</span>
            </div>
          </div>
          <div class="flex gap-2 mt-2">
            <Button v-if="se.docstatus===0" variant="solid" theme="green" size="sm" :loading="busy===se.name" @click="submitSe(se)">Chốt</Button>
            <Button variant="subtle" size="sm" @click="printSe(se.name)">In phiếu</Button>
            <Button v-if="se.docstatus===0" variant="subtle" size="sm" @click="del(se)">Xóa</Button>
          </div>
        </div>
      </div>

      <div v-if="total > pageLen" class="flex items-center justify-between mt-3 text-sm text-gray-600">
        <span>{{ total }} phiếu · trang {{ page }}/{{ pages }}</span>
        <div class="flex gap-2">
          <Button variant="subtle" :disabled="page<=1" @click="page--; reload()">‹</Button>
          <Button variant="subtle" :disabled="page>=pages" @click="page++; reload()">›</Button>
        </div>
      </div>
    </main>

    <!-- Create modal -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="showCreate=false">
      <div class="bg-white rounded-xl w-full max-w-2xl p-5 max-h-[92vh] overflow-y-auto">
        <h3 class="text-lg font-semibold mb-4">Lập phiếu kho</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
          <label class="block"><span class="text-sm text-gray-600 block mb-1">Loại phiếu</span>
            <select v-model="form.stock_entry_type" class="inp">
              <option v-for="t in types" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </label>
          <label class="block"><span class="text-sm text-gray-600 block mb-1">Ngày</span><input type="date" v-model="form.posting_date" class="inp" /></label>
          <label v-if="needFrom" class="block"><span class="text-sm text-gray-600 block mb-1">Kho xuất</span>
            <select v-model="form.from_warehouse" class="inp">
              <option value="">— chọn kho xuất —</option>
              <option v-for="w in stockWh" :key="w.name" :value="w.name">{{ w.warehouse_name }}</option>
            </select>
          </label>
          <label v-if="needTo" class="block"><span class="text-sm text-gray-600 block mb-1">Kho nhập</span>
            <select v-model="form.to_warehouse" class="inp">
              <option value="">— chọn kho nhập —</option>
              <option v-for="w in stockWh" :key="w.name" :value="w.name">{{ w.warehouse_name }}</option>
            </select>
          </label>
        </div>

        <!-- Camera QR scanner panel inside modal -->
        <div v-if="scanning" class="bg-gray-900 rounded-lg overflow-hidden relative aspect-video w-full max-w-sm mx-auto mb-3 shadow-md border border-orange-200">
          <div id="qr-reader-se" class="w-full h-full"></div>
          <button @click="toggleScanner" class="absolute top-2 right-2 p-1.5 bg-black/60 hover:bg-black/80 rounded-full text-white z-10">
            <FeatherIcon name="x" class="h-4 w-4" />
          </button>
        </div>

        <div class="border rounded-lg overflow-hidden mb-3">
          <div class="grid grid-cols-12 gap-1 bg-gray-50 px-2 py-1.5 text-xs font-medium text-gray-500">
            <div class="col-span-4">Hàng hóa</div>
            <div class="col-span-2 text-center">ĐVT</div>
            <div class="col-span-2 text-right">SL</div>
            <div class="col-span-3 text-right">Đơn giá</div>
            <div class="col-span-1"></div>
          </div>
          <div v-for="(r,i) in form.items" :key="i" class="grid grid-cols-12 gap-1 px-2 py-1.5 items-center border-t">
            <select v-model="r.item_code" class="col-span-4 inp !py-1 !text-xs bg-white" @change="onItemChange(r)">
              <option value="">— chọn —</option>
              <option v-for="it in itemOpts" :key="it.name" :value="it.item_code">
                [{{ it.item_code }}] — {{ it.item_name }}
              </option>
            </select>
            <div class="col-span-2 text-center text-xs text-gray-600 font-medium truncate">
              {{ getItemUom(r.item_code) || '—' }}
            </div>
            <input v-model.number="r.qty" type="number" class="col-span-2 inp !py-1 text-right" />
            <input v-model.number="r.basic_rate" type="number" class="col-span-3 inp !py-1 text-right" :disabled="!needRate" :placeholder="needRate ? '' : 'auto'" />
            <button class="col-span-1 text-red-500 text-xs hover:text-red-700 font-medium transition-colors text-center" @click="form.items.splice(i,1)">Xóa</button>
          </div>
        </div>
        
        <div class="flex gap-2">
          <Button variant="subtle" size="sm" @click="form.items.push({ item_code:'', qty:1, basic_rate:0 })">+ Thêm dòng</Button>
          <Button variant="outline" size="sm" @click="toggleScanner" class="flex items-center gap-1">
            <FeatherIcon name="camera" class="h-4 w-4" />
            <span>{{ scanning ? 'Đóng quét mã' : 'Quét mã QR/Barcode' }}</span>
          </Button>
        </div>

        <label class="block mt-3"><span class="text-sm text-gray-600 block mb-1">Diễn giải</span><input v-model="form.remarks" class="inp" /></label>

        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showCreate=false">Hủy</Button>
          <Button variant="outline" :loading="saving" @click="save(0)">Lưu nháp</Button>
          <Button variant="solid" theme="green" :loading="saving" @click="save(1)">Lưu & Chốt</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi, callApi } from '../composables/useFrappeApi'

const rows = ref([]), total = ref(0), pages = ref(1), page = ref(1), loading = ref(false), busy = ref('')
const typeFilter = ref('')
const pageLen = 20
const typeFilters = [
  { value: '', label: 'Tất cả' },
  { value: 'Material Receipt', label: 'Nhập' },
  { value: 'Material Issue', label: 'Xuất' },
  { value: 'Material Transfer', label: 'Chuyển' },
]

const { data: types } = useFrappeApi('kho.api.get_stock_entry_types', { initialData: [] })
const { data: warehouses } = useFrappeApi('kho.api.get_warehouses', { initialData: [] })
const { data: itemsResp } = useFrappeApi('kho.api.get_items', { initialData: { items: [] }, params: { page_length: 500 } })
const stockWh = computed(() => (warehouses.value || []).filter(w => !w.is_group))
const itemOpts = computed(() => itemsResp.value?.items || [])

async function reload() {
  loading.value = true
  try {
    const r = await callApi('kho.api.get_stock_entries', { stock_entry_type: typeFilter.value, page: page.value, page_length: pageLen }, 'GET')
    rows.value = r?.entries || []; total.value = r?.total || 0; pages.value = r?.pages || 1
  } finally { loading.value = false }
}
reload()

const showCreate = ref(false), saving = ref(false)
const form = reactive({ stock_entry_type: 'Material Receipt', posting_date: new Date().toISOString().slice(0,10), from_warehouse: '', to_warehouse: '', remarks: '', items: [{ item_code: '', qty: 1, basic_rate: 0 }] })
const needFrom = computed(() => ['Material Issue', 'Material Transfer'].includes(form.stock_entry_type))
const needTo = computed(() => ['Material Receipt', 'Material Transfer'].includes(form.stock_entry_type))
const needRate = computed(() => form.stock_entry_type === 'Material Receipt')

watch([stockWh, () => form.stock_entry_type], () => {
  if (stockWh.value && stockWh.value.length) {
    if (needFrom.value && !form.from_warehouse) {
      form.from_warehouse = stockWh.value[0].name
    }
    if (needTo.value && !form.to_warehouse) {
      form.to_warehouse = stockWh.value[0].name
    }
  }
}, { immediate: true })

function openCreate() {
  Object.assign(form, { stock_entry_type: 'Material Receipt', posting_date: new Date().toISOString().slice(0,10), from_warehouse: '', to_warehouse: stockWh.value?.[0]?.name || '', remarks: '', items: [{ item_code: '', qty: 1, basic_rate: 0 }] })
  showCreate.value = true
}
async function save(submit) {
  const items = form.items.filter(r => r.item_code && r.qty).map(r => ({
    item_code: r.item_code,
    qty: r.qty,
    basic_rate: r.basic_rate,
    uom: getItemUom(r.item_code)
  }))
  if (!items.length) { alert('Thêm ít nhất 1 dòng hàng'); return }
  saving.value = true
  try {
    await callApi('kho.api.create_stock_entry', {
      stock_entry_type: form.stock_entry_type,
      items: JSON.stringify(items),
      from_warehouse: needFrom.value ? form.from_warehouse : '',
      to_warehouse: needTo.value ? form.to_warehouse : '',
      posting_date: form.posting_date, remarks: form.remarks, submit,
    })
    showCreate.value = false; page.value = 1; await reload()
  } catch (e) { alert('Lỗi: ' + (e?.message || e)) } finally { saving.value = false }
}

async function submitSe(se) {
  busy.value = se.name
  try { await callApi('kho.api.submit_stock_entry', { name: se.name }); await reload() }
  catch (e) { alert('Lỗi: ' + (e?.message || e)) } finally { busy.value = '' }
}
async function del(se) {
  if (!confirm('Xóa phiếu ' + se.name + '?')) return
  try { await callApi('kho.api.delete_stock_entry', { name: se.name }); await reload() }
  catch (e) { alert('Lỗi: ' + (e?.message || e)) }
}
async function printSe(name) {
  const html = await callApi('kho.api.print_stock_entry', { name }, 'GET')
  const w = window.open('', '_blank')
  w.document.write(html + '<script>window.onload=()=>window.print()<\/script>')
  w.document.close()
}

// QR Code and Barcode Scanner inside Modal
const scanning = ref(false)
let html5Qrcode = null

async function toggleScanner() {
  if (scanning.value) {
    stopScanner()
  } else {
    scanning.value = true
    await nextTick()
    startScanner()
  }
}

async function startScanner() {
  try {
    if (!window.Html5Qrcode) {
      await new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js'
        script.onload = resolve
        script.onerror = reject
        document.head.appendChild(script)
      })
    }
    
    html5Qrcode = new window.Html5Qrcode("qr-reader-se")
    await html5Qrcode.start(
      { facingMode: "environment" },
      {
        fps: 10,
        qrbox: (width, height) => {
          const size = Math.min(width, height) * 0.7
          return { width: size, height: size }
        }
      },
      (decodedText) => {
        const it = itemOpts.value.find(x => x.item_code === decodedText || x.name === decodedText)
        if (it) {
          playBeep()
          const existing = form.items.find(x => x.item_code === it.item_code)
          if (existing) {
            existing.qty += 1
          } else {
            if (form.items.length === 1 && !form.items[0].item_code) {
              form.items[0].item_code = it.item_code
              form.items[0].qty = 1
              form.items[0].basic_rate = it.valuation_rate || 0
            } else {
              form.items.push({ item_code: it.item_code, qty: 1, basic_rate: it.valuation_rate || 0 })
            }
          }
        } else {
          alert(`Mặt hàng có mã "${decodedText}" không có trong danh mục!`)
        }
      },
      (errorMessage) => {}
    )
  } catch (err) {
    console.error("Camera startup failed:", err)
    alert("Không thể khởi động camera: " + err)
    scanning.value = false
  }
}

function stopScanner() {
  if (html5Qrcode) {
    html5Qrcode.stop().then(() => {
      html5Qrcode.clear()
      html5Qrcode = null
    }).catch(err => console.error("Stop error", err))
  }
  scanning.value = false
}

onBeforeUnmount(() => {
  stopScanner()
})

function playBeep() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.frequency.setValueAtTime(1200, ctx.currentTime)
    gain.gain.setValueAtTime(0.2, ctx.currentTime)
    osc.start()
    osc.stop(ctx.currentTime + 0.08)
  } catch (e) {}
}

function getItemUom(code) {
  const it = itemOpts.value.find(x => x.item_code === code)
  return it ? it.stock_uom : ''
}

function onItemChange(row) {
  const it = itemOpts.value.find(x => x.item_code === row.item_code)
  if (it) {
    if (needRate.value && (row.basic_rate === 0 || !row.basic_rate)) {
      row.basic_rate = it.valuation_rate || 0
    }
  }
}

function badge(t) {
  return { 'Material Receipt': 'bg-emerald-100 text-emerald-700', 'Material Issue': 'bg-red-100 text-red-700', 'Material Transfer': 'bg-blue-100 text-blue-700' }[t] || 'bg-gray-100 text-gray-600'
}
function short(w) { return (w || '').replace(/ - [A-Z]+$/, '') }
function fmtVnd(v) { return Number(v || 0).toLocaleString('vi-VN') + ' ₫' }
</script>
