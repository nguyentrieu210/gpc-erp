<template>
  <div class="flex flex-col min-h-screen bg-gray-50 text-gray-900 font-sans">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10 shadow-sm">
      <button class="text-gray-500 hover:text-gray-800 transition-colors" @click="$router.push('/')">
        <FeatherIcon name="arrow-left" class="h-5 w-5" />
      </button>
      <FeatherIcon name="package" class="h-5 w-5 text-orange-600" />
      <h1 class="text-lg font-bold text-gray-950 flex-1">Danh mục Hàng hóa</h1>
      <div class="flex gap-2">
        <Button variant="outline" @click="toggleScanner" class="flex items-center gap-1">
          <FeatherIcon name="camera" class="h-4 w-4" />
          <span>{{ scanning ? 'Đóng quét QR' : 'Quét QR' }}</span>
        </Button>
        <Button variant="solid" theme="orange" @click="openCreate" class="flex items-center gap-1 shadow-sm">
          <FeatherIcon name="plus" class="h-4 w-4" />
          <span>Thêm mặt hàng</span>
        </Button>
      </div>
    </header>

    <main class="flex-1 p-4 max-w-7xl mx-auto w-full space-y-4">
      <!-- QR Scanner Panel -->
      <div v-if="scanning" class="bg-white rounded-xl border border-orange-200 shadow-md p-4 max-w-md mx-auto overflow-hidden transition-all duration-300">
        <div class="flex items-center justify-between mb-3">
          <span class="font-semibold text-orange-800 flex items-center gap-1">
            <span class="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
            Đang mở camera quét mã QR/Barcode...
          </span>
          <button @click="toggleScanner" class="text-gray-400 hover:text-gray-600">
            <FeatherIcon name="x" class="h-4 w-4" />
          </button>
        </div>
        <div id="qr-reader" class="w-full rounded-lg overflow-hidden bg-gray-900 aspect-square"></div>
        <div class="text-xs text-center text-gray-500 mt-2">
          Hướng camera về phía mã QR hoặc mã vạch của mặt hàng.
        </div>
      </div>

      <!-- Quick Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div class="p-3 bg-orange-50 rounded-lg text-orange-600">
            <FeatherIcon name="box" class="h-6 w-6" />
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-950">{{ total }}</div>
            <div class="text-xs text-gray-500 font-medium">Tổng số mặt hàng</div>
          </div>
        </div>

        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div class="p-3 bg-emerald-50 rounded-lg text-emerald-600">
            <FeatherIcon name="trending-up" class="h-6 w-6" />
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-950">{{ fmtQty(totalStockQty) }}</div>
            <div class="text-xs text-gray-500 font-medium">Tổng lượng tồn kho</div>
          </div>
        </div>

        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div class="p-3 bg-blue-50 rounded-lg text-blue-600">
            <FeatherIcon name="dollar-sign" class="h-6 w-6" />
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-950">{{ fmtVnd(totalStockVal) }}</div>
            <div class="text-xs text-gray-500 font-medium">Giá trị tồn kho</div>
          </div>
        </div>

        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div class="p-3 bg-red-50 rounded-lg text-red-600">
            <FeatherIcon name="alert-triangle" class="h-6 w-6" />
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-950">{{ lowStockCount }}</div>
            <div class="text-xs text-gray-500 font-medium">Mặt hàng hết/sắp hết</div>
          </div>
        </div>
      </div>

      <!-- Toolbar / Filters -->
      <div class="bg-white p-3 rounded-xl border border-gray-200 shadow-sm flex flex-wrap gap-3 items-center justify-between">
        <div class="flex flex-wrap items-center gap-2 flex-1 min-w-[280px]">
          <div class="relative flex-1 min-w-[220px]">
            <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <FeatherIcon name="search" class="h-4 w-4" />
            </span>
            <input v-model="search" @input="debouncedFetch" placeholder="Tìm mã hàng, tên hàng hoặc quét QR..."
                   class="w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 outline-none" />
            <button v-if="search" @click="search = ''; debouncedFetch()" class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600">
              <FeatherIcon name="x" class="h-4 w-4" />
            </button>
          </div>
          
          <select v-model="group" @change="reload" class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 outline-none bg-white">
            <option value="">Tất cả nhóm</option>
            <option v-for="g in groups" :key="g.name" :value="g.name">{{ g.item_group_name }}</option>
          </select>

          <label class="flex items-center gap-2 text-sm text-gray-700 bg-gray-50 hover:bg-gray-100 px-3 py-2 rounded-lg border border-gray-300 cursor-pointer select-none">
            <input type="checkbox" v-model="hasStock" @change="reload" class="rounded text-orange-600 focus:ring-orange-500" />
            <span>Còn tồn</span>
          </label>
        </div>

        <div class="flex gap-2">
          <Button variant="outline" @click="reload" class="p-2"><FeatherIcon name="refresh-cw" class="h-4 w-4" /></Button>
        </div>
      </div>

      <!-- Rich Information Table -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-600 uppercase tracking-wider">
                <th class="px-3 py-3 text-center w-12">STT</th>
                <th class="px-3 py-3 text-center w-12">
                  <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" class="rounded text-orange-600 focus:ring-orange-500" />
                </th>
                <th class="px-4 py-3 min-w-[150px]">Mã hàng (QR & Mã)</th>
                <th class="px-4 py-3 text-center w-20">Hình ảnh</th>
                <th class="px-4 py-3 min-w-[200px]">Tên mặt hàng</th>
                <th class="px-4 py-3">Loại</th>
                <th class="px-4 py-3">ĐVT</th>
                <th class="px-4 py-3 text-center">Tồn kho</th>
                <th class="px-4 py-3 text-right">Giá trị</th>
                <th class="px-4 py-3 text-right">Giá vốn</th>
                <th class="px-4 py-3 text-center">Quản lý</th>
                <th class="px-4 py-3 text-center">Trạng thái</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 text-sm">
              <tr v-if="loading" class="hover:bg-transparent">
                <td colspan="12" class="py-12 text-center"><LoadingIndicator /></td>
              </tr>
              <tr v-else-if="!rows.length" class="hover:bg-transparent">
                <td colspan="12" class="py-12 text-center text-gray-400">
                  <div class="flex flex-col items-center justify-center gap-2">
                    <FeatherIcon name="package" class="h-8 w-8 text-gray-300" />
                    <span>Không tìm thấy mặt hàng nào phù hợp</span>
                  </div>
                </td>
              </tr>
              <tr v-else v-for="(it, idx) in rows" :key="it.name"
                  class="hover:bg-orange-50/20 cursor-pointer transition-colors group"
                  @click="viewItem(it)">
                <!-- 1. STT -->
                <td class="px-3 py-3 text-center font-medium text-gray-500">
                  {{ (page - 1) * pageLen + idx + 1 }}
                </td>

                <!-- 2. Tick chọn -->
                <td class="px-3 py-3 text-center" @click.stop>
                  <input type="checkbox" :value="it.name" v-model="selectedIds" class="rounded text-orange-600 focus:ring-orange-500" />
                </td>

                <!-- 3. Mã hàng (QR & Mã) -->
                <td class="px-4 py-3" @click.stop="showQrModal(it)">
                  <div class="flex items-center gap-2">
                    <div class="relative inline-block border rounded p-0.5 bg-white shadow-2xs group-hover:border-orange-300 transition-colors shrink-0">
                      <img :src="'https://api.qrserver.com/v1/create-qr-code/?size=60x60&data=' + encodeURIComponent(it.item_code)" 
                           alt="QR" class="h-8 w-8 object-contain" />
                      <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center rounded transition-opacity">
                        <FeatherIcon name="maximize-2" class="h-3 w-3 text-white" />
                      </div>
                    </div>
                    <span class="font-mono font-bold text-gray-900 group-hover:text-orange-600 transition-colors">
                      {{ it.item_code }}
                    </span>
                  </div>
                </td>

                <!-- 4. Hình ảnh mặt hàng -->
                <td class="px-4 py-3 text-center" @click.stop>
                  <label class="relative h-10 w-10 mx-auto rounded border bg-gray-50 flex items-center justify-center overflow-hidden shrink-0 cursor-pointer group/img hover:border-orange-500 transition-colors" title="Bấm để tải ảnh lên">
                    <input type="file" accept="image/*" class="hidden" :disabled="uploadingItem === it.name" @change="uploadProductImage(it, $event)" />
                    <img v-if="it.image && uploadingItem !== it.name" :src="it.image" alt="Image" class="h-full w-full object-cover" />
                    <div v-else-if="uploadingItem === it.name" class="h-full w-full flex items-center justify-center bg-gray-50">
                      <LoadingIndicator class="h-5 w-5 text-orange-600 animate-spin" />
                    </div>
                    <div v-else class="h-full w-full bg-orange-50 text-orange-700 flex items-center justify-center text-xs font-bold uppercase">
                      {{ (it.item_name || it.item_code || '?').slice(0,2).toUpperCase() }}
                    </div>
                    <!-- Hover overlay for uploading -->
                    <div v-if="uploadingItem !== it.name" class="absolute inset-0 bg-black/45 opacity-0 group-hover/img:opacity-100 flex items-center justify-center transition-opacity text-white">
                      <FeatherIcon name="upload" class="h-4 w-4" />
                    </div>
                  </label>
                </td>

                <!-- 5. Tên mặt hàng -->
                <td class="px-4 py-3">
                  <div class="font-semibold text-gray-950 truncate max-w-[280px]" :title="it.item_name">
                    {{ it.item_name }}
                  </div>
                  <div class="text-xs text-gray-400 truncate max-w-[280px]">
                    {{ it.brand ? 'Nhãn hiệu: ' + it.brand : 'Chưa gắn nhãn' }}
                  </div>
                </td>

                <!-- 6. Loại -->
                <td class="px-4 py-3">
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium" :class="getGroupClass(it.item_group)">
                    {{ it.item_group }}
                  </span>
                </td>

                <!-- 7. ĐVT -->
                <td class="px-4 py-3 text-gray-600">
                  {{ it.stock_uom }}
                </td>

                <!-- 8. Tồn kho -->
                <td class="px-4 py-3 text-center font-semibold">
                  <span :class="it.actual_qty > 0 ? 'text-emerald-600 bg-emerald-50 px-2 py-1 rounded' : 'text-gray-400 bg-gray-50 px-2 py-1 rounded'">
                    {{ fmtQty(it.actual_qty) }}
                  </span>
                </td>

                <!-- 9. Giá trị -->
                <td class="px-4 py-3 text-right font-mono font-medium text-gray-700">
                  {{ fmtVnd(it.stock_value) }}
                </td>

                <!-- 10. Giá vốn -->
                <td class="px-4 py-3 text-right">
                  <div class="font-mono text-gray-900 font-medium">{{ fmtVnd(it.valuation_rate) }}</div>
                  <div class="text-xs text-gray-400 uppercase">{{ it.valuation_method || 'FIFO' }}</div>
                </td>

                <!-- 11. Quản lý -->
                <td class="px-4 py-3 text-center">
                  <div class="inline-flex gap-1 justify-center">
                    <span v-if="it.is_stock_item" class="bg-blue-50 text-blue-600 p-1 rounded-sm" title="Quản lý tồn kho">
                      <FeatherIcon name="box" class="h-3 w-3" />
                    </span>
                    <span v-if="it.has_batch_no" class="bg-purple-50 text-purple-600 p-1 rounded-sm" title="Theo lô">
                      <FeatherIcon name="layers" class="h-3 w-3" />
                    </span>
                    <span v-if="it.has_serial_no" class="bg-indigo-50 text-indigo-600 p-1 rounded-sm" title="Theo số serial">
                      <FeatherIcon name="hash" class="h-3 w-3" />
                    </span>
                  </div>
                </td>

                <!-- 12. Trạng thái -->
                <td class="px-4 py-3 text-center">
                  <span v-if="it.disabled" class="px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-700">
                    Ngừng KD
                  </span>
                  <span v-else class="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">
                    Đang KD
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="total > pageLen" class="flex items-center justify-between border-t border-gray-100 bg-gray-50 px-4 py-3 text-sm text-gray-600">
          <span>Tổng số <b>{{ total }}</b> mặt hàng · Trang <b>{{ page }}</b> / <b>{{ pages }}</b></span>
          <div class="flex gap-2">
            <Button variant="subtle" :disabled="page<=1" @click="page--; reload()">‹ Trước</Button>
            <Button variant="subtle" :disabled="page>=pages" @click="page++; reload()">Sau ›</Button>
          </div>
        </div>
      </div>
    </main>

    <!-- Create modal -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50 animate-fade-in" @click.self="showCreate=false">
      <div class="bg-white rounded-xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto shadow-xl">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-950">Thêm mặt hàng mới</h3>
          <button @click="showCreate=false" class="text-gray-400 hover:text-gray-600"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>
        
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <Field label="Mã hàng (để trống tự sinh)"><input v-model="form.item_code" class="inp" placeholder="Mã vạch / QR / Ký hiệu" /></Field>
            <Field label="Tên hàng *"><input v-model="form.item_name" class="inp" placeholder="Tên đầy đủ của mặt hàng" /></Field>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <Field label="Nhóm hàng">
              <select v-model="form.item_group" class="inp">
                <option v-for="g in groups" :key="g.name" :value="g.name">{{ g.item_group_name }}</option>
              </select>
            </Field>
            <Field label="Đơn vị tính">
              <select v-model="form.stock_uom" class="inp">
                <option v-for="u in uoms" :key="u.name" :value="u.name">{{ u.uom_name }}</option>
              </select>
            </Field>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <Field label="Giá vốn ban đầu"><input v-model.number="form.valuation_rate" type="number" class="inp" /></Field>
            <Field label="Số lượng tồn đầu kỳ"><input v-model.number="form.opening_stock" type="number" class="inp" /></Field>
          </div>
          
          <Field label="Phương pháp định giá">
            <select v-model="form.valuation_method" class="inp">
              <option value="">(Mặc định FIFO)</option>
              <option value="FIFO">FIFO</option>
              <option value="Moving Average">Bình quân gia quyền (Moving Average)</option>
            </select>
          </Field>

          <Field label="Mô tả hàng hóa">
            <textarea v-model="form.description" class="inp min-h-[60px]" placeholder="Chi tiết mô tả..."></textarea>
          </Field>
          
          <div class="bg-gray-50 p-3 rounded-lg border space-y-2">
            <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Cài đặt thuộc tính</span>
            <div class="flex gap-6 text-sm">
              <label class="flex items-center gap-2 cursor-pointer font-medium"><input type="checkbox" v-model="form.is_stock_item" class="rounded text-orange-600 focus:ring-orange-500" /> Quản lý tồn kho</label>
              <label class="flex items-center gap-2 cursor-pointer font-medium"><input type="checkbox" v-model="form.has_batch_no" class="rounded text-orange-600 focus:ring-orange-500" /> Quản lý theo Lô</label>
              <label class="flex items-center gap-2 cursor-pointer font-medium"><input type="checkbox" v-model="form.has_serial_no" class="rounded text-orange-600 focus:ring-orange-500" /> Quản lý Serial</label>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6">
          <Button variant="subtle" @click="showCreate=false">Quay lại</Button>
          <Button variant="solid" theme="orange" :loading="saving" @click="save">Lưu mặt hàng</Button>
        </div>
      </div>
    </div>

    <!-- QR Detail Modal -->
    <div v-if="activeQrItem" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 animate-fade-in" @click="activeQrItem = null">
      <div class="bg-white rounded-xl p-6 max-w-sm w-full text-center shadow-2xl relative" @click.stop>
        <button @click="activeQrItem = null" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <FeatherIcon name="x" class="h-5 w-5" />
        </button>
        <h3 class="text-lg font-bold text-gray-950 mb-1">Mã QR Mặt hàng</h3>
        <p class="text-sm text-gray-500 mb-4 font-mono">{{ activeQrItem.item_code }}</p>
        
        <div class="bg-gray-50 p-4 rounded-xl inline-block border mb-4">
          <img :src="'https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=' + encodeURIComponent(activeQrItem.item_code)" 
               alt="QR Code" class="w-48 h-48 mx-auto" />
        </div>
        
        <h4 class="font-bold text-gray-900 truncate px-2 mb-1">{{ activeQrItem.item_name }}</h4>
        <p class="text-xs text-gray-500 mb-4">{{ activeQrItem.item_group }} · {{ activeQrItem.stock_uom }}</p>
        
        <div class="flex gap-2">
          <button @click="printQrCode(activeQrItem)" class="flex-1 py-2 px-3 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-medium text-sm transition-colors flex items-center justify-center gap-1">
            <FeatherIcon name="printer" class="h-4 w-4" />
            In mã QR
          </button>
          <button @click="downloadQrCode(activeQrItem)" class="py-2 px-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium text-sm transition-colors" title="Tải ảnh QR">
            <FeatherIcon name="download" class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, h, computed, nextTick, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi, callApi } from '../composables/useFrappeApi'

const router = useRouter()

const rows = ref([]), total = ref(0), pages = ref(1), page = ref(1)
const loading = ref(false)
const search = ref(''), group = ref(''), hasStock = ref(false)
const pageLen = 30

const { data: groups } = useFrappeApi('kho.api.get_item_groups', { initialData: [] })
const { data: uoms } = useFrappeApi('kho.api.get_uoms', { initialData: [] })

// Checkbox select functionality
const selectedIds = ref([])
const isAllSelected = computed(() => {
  return rows.value.length > 0 && selectedIds.value.length === rows.value.length
})
function toggleSelectAll(e) {
  if (e.target.checked) {
    selectedIds.value = rows.value.map(r => r.name)
  } else {
    selectedIds.value = []
  }
}

// Metrics
const totalStockQty = computed(() => rows.value.reduce((acc, it) => acc + (it.actual_qty || 0), 0))
const totalStockVal = computed(() => rows.value.reduce((acc, it) => acc + (it.stock_value || 0), 0))
const lowStockCount = computed(() => rows.value.filter(it => it.is_stock_item && (it.actual_qty || 0) <= 0).length)

async function reload() {
  loading.value = true
  selectedIds.value = []
  try {
    const r = await callApi('kho.api.get_items', {
      search: search.value, item_group: group.value, has_stock: hasStock.value ? 1 : 0,
      page: page.value, page_length: pageLen,
    }, 'GET')
    rows.value = r?.items || []
    total.value = r?.total || 0
    pages.value = r?.pages || 1
  } finally { loading.value = false }
}
reload()

let t
function debouncedFetch() { clearTimeout(t); t = setTimeout(() => { page.value = 1; reload() }, 350) }

function viewItem(it) {
  router.push('/items/' + encodeURIComponent(it.name))
}

const uploadingItem = ref(null)

async function uploadProductImage(item, event) {
  const file = event.target.files[0]
  if (!file) return
  
  uploadingItem.value = item.name
  try {
    const token = await callApi('kho.api.get_csrf_token')
    
    const formData = new FormData()
    formData.append('file', file)
    formData.append('doctype', 'Item')
    formData.append('docname', item.name)
    formData.append('fieldname', 'image')
    formData.append('is_private', 0)
    
    const res = await fetch('/api/method/upload_file', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'X-Frappe-CSRF-Token': token
      },
      body: formData
    })
    
    const data = await res.json()
    if (data.message && data.message.file_url) {
      await callApi('kho.api.update_item', {
        name: item.name,
        image: data.message.file_url
      })
      item.image = data.message.file_url
    } else {
      throw new Error(data.exception || 'Tải file thất bại')
    }
  } catch (err) {
    alert('Lỗi khi tải ảnh: ' + (err.message || err))
  } finally {
    uploadingItem.value = null
  }
}

// Group Badges Styles
function getGroupClass(g) {
  switch (g) {
    case 'Hàng hóa': return 'bg-emerald-50 text-emerald-700 border border-emerald-200'
    case 'Thành phẩm': return 'bg-blue-50 text-blue-700 border border-blue-200'
    case 'Nguyên vật liệu': return 'bg-amber-50 text-amber-700 border border-amber-200'
    case 'Công cụ dụng cụ': return 'bg-purple-50 text-purple-700 border border-purple-200'
    case 'Vật tư tiêu hao': return 'bg-gray-100 text-gray-700 border border-gray-200'
    case 'Dịch vụ': return 'bg-pink-50 text-pink-700 border border-pink-200'
    default: return 'bg-gray-50 text-gray-600 border border-gray-200'
  }
}

// QR Code and Barcode Scanner
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
    
    html5Qrcode = new window.Html5Qrcode("qr-reader")
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
        search.value = decodedText
        page.value = 1
        reload()
        playBeep()
        stopScanner()
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

// QR Detail View
const activeQrItem = ref(null)
function showQrModal(it) {
  activeQrItem.value = it
}

function printQrCode(it) {
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(it.item_code)}`
  const w = window.open('', '_blank')
  w.document.write(`
    <html>
      <head>
        <title>Mã QR - ${it.item_code}</title>
        <style>
          body { font-family: sans-serif; text-align: center; padding: 40px; }
          .container { border: 2px solid #ddd; border-radius: 8px; padding: 20px; display: inline-block; }
          img { width: 200px; height: 200px; }
          h2 { margin: 10px 0 2px; }
          p { margin: 0; color: #555; }
        </style>
      </head>
      <body onload="window.print(); window.close();">
        <div class="container">
          <img src="${qrUrl}" />
          <h2>${it.item_name}</h2>
          <p>Mã hàng: ${it.item_code} · ${it.item_group}</p>
        </div>
      </body>
    </html>
  `)
  w.document.close()
}

function downloadQrCode(it) {
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(it.item_code)}`
  const link = document.createElement('a')
  link.href = qrUrl
  link.download = `QR_${it.item_code}.png`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Create Form Logic
const showCreate = ref(false), saving = ref(false)
const form = reactive({ 
  item_code: '', 
  item_name: '', 
  item_group: 'Hàng hóa', 
  stock_uom: 'Cái', 
  valuation_rate: 0, 
  opening_stock: 0, 
  valuation_method: '', 
  is_stock_item: true, 
  has_batch_no: false, 
  has_serial_no: false,
  description: ''
})

function openCreate() {
  Object.assign(form, { 
    item_code: '', 
    item_name: '', 
    item_group: 'Hàng hóa', 
    stock_uom: 'Cái', 
    valuation_rate: 0, 
    opening_stock: 0, 
    valuation_method: '', 
    is_stock_item: true, 
    has_batch_no: false, 
    has_serial_no: false,
    description: ''
  })
  showCreate.value = true
}

async function save() {
  if (!form.item_name) { alert('Nhập tên hàng'); return }
  saving.value = true
  try {
    await callApi('kho.api.create_item', {
      ...form,
      is_stock_item: form.is_stock_item ? 1 : 0,
      has_batch_no: form.has_batch_no ? 1 : 0,
      has_serial_no: form.has_serial_no ? 1 : 0,
    })
    showCreate.value = false
    page.value = 1
    await reload()
  } catch (e) { alert('Lỗi: ' + (e?.message || e)) } finally { saving.value = false }
}

function fmtQty(v) { return Number(v || 0).toLocaleString('vi-VN') }
function fmtVnd(v) { return Number(v || 0).toLocaleString('vi-VN') + ' ₫' }

const Field = {
  props: ['label'],
  setup(props, { slots }) {
    return () => h('label', { class: 'block' }, [
      h('span', { class: 'text-sm font-semibold text-gray-600 block mb-1' }, props.label),
      slots.default?.(),
    ])
  },
}
</script>

<style>
.inp {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  padding: 8px 12px;
  font-size: 14px;
  background-color: #fff;
  transition: all 0.2s;
}
.inp:focus {
  outline: none;
  border-color: #ea580c;
  box-shadow: 0 0 0 1px #ea580c;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fade-in {
  animation: fadeIn 0.2s ease-out;
}
</style>
