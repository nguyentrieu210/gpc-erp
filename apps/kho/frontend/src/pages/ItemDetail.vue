<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
      <button class="text-gray-500 hover:text-gray-800" @click="$router.push('/items')"><FeatherIcon name="arrow-left" class="h-5 w-5" /></button>
      <FeatherIcon name="package" class="h-5 w-5 text-orange-600" />
      <h1 class="text-lg font-semibold text-gray-900 flex-1 truncate">{{ item?.item_name || id }}</h1>
      <Button variant="subtle" @click="openEdit">Sửa</Button>
    </header>

    <main class="flex-1 p-4 max-w-3xl mx-auto w-full space-y-4">
      <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
      <template v-else-if="item">
        <!-- Profile -->
        <div class="rounded-lg border bg-white p-4">
          <div class="flex items-center gap-3">
            <div class="h-12 w-12 rounded-lg bg-orange-100 text-orange-700 flex items-center justify-center font-bold">
              {{ (item.item_name || '?').slice(0,2).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-semibold text-gray-900">{{ item.item_name }}</div>
              <div class="text-sm text-gray-500">{{ item.item_code }} · {{ item.item_group }}</div>
            </div>
            <span v-if="item.disabled" class="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-600">Ngừng KD</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 text-center">
            <Stat label="Tồn tổng" :value="fmtQty(item.total_qty)" color="text-emerald-600" />
            <Stat label="Giá trị tồn" :value="fmtVnd(item.total_value)" color="text-orange-600" />
            <Stat label="Đơn giá" :value="fmtVnd(item.valuation_rate)" color="text-gray-700" />
            <Stat label="Định giá" :value="item.valuation_method || 'FIFO'" color="text-blue-600" />
          </div>
          <div class="flex flex-wrap gap-2 mt-3 text-xs">
            <span class="px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">ĐVT: {{ item.stock_uom }}</span>
            <span v-if="item.is_stock_item" class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">Quản lý tồn</span>
            <span v-if="item.has_batch_no" class="px-2 py-0.5 rounded-full bg-violet-100 text-violet-700">Theo lô</span>
            <span v-if="item.has_serial_no" class="px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">Theo serial</span>
          </div>
          <p v-if="item.description" class="text-sm text-gray-500 mt-3">{{ stripHtml(item.description) }}</p>
        </div>

        <!-- Stock by warehouse -->
        <div class="rounded-lg border bg-white">
          <div class="px-4 py-3 border-b font-medium text-gray-700">Tồn theo kho</div>
          <div v-if="!item.stock_by_warehouse?.length" class="py-6 text-center text-gray-400 text-sm">Chưa có tồn</div>
          <div v-for="b in item.stock_by_warehouse" :key="b.warehouse" class="flex items-center px-4 py-2.5 border-t text-sm">
            <div class="flex-1">{{ b.warehouse }}</div>
            <div class="text-right">
              <div class="font-semibold">{{ fmtQty(b.actual_qty) }}</div>
              <div class="text-xs text-gray-400">{{ fmtVnd(b.stock_value) }}</div>
            </div>
          </div>
        </div>

        <!-- Reorder -->
        <div class="rounded-lg border bg-white">
          <div class="px-4 py-3 border-b font-medium text-gray-700 flex items-center justify-between">
            Định mức tồn tối thiểu
            <Button variant="subtle" size="sm" @click="openReorder">+ Đặt mức</Button>
          </div>
          <div v-if="!item.reorder_levels?.length" class="py-6 text-center text-gray-400 text-sm">Chưa đặt định mức</div>
          <div v-for="r in item.reorder_levels" :key="r.warehouse" class="flex items-center px-4 py-2.5 border-t text-sm">
            <div class="flex-1">{{ r.warehouse }}</div>
            <div class="text-gray-500">Tối thiểu {{ fmtQty(r.warehouse_reorder_level) }} · Đặt {{ fmtQty(r.warehouse_reorder_qty) }}</div>
          </div>
        </div>

        <!-- Batches -->
        <div v-if="item.has_batch_no" class="rounded-lg border bg-white">
          <div class="px-4 py-3 border-b font-medium text-gray-700">Lô hàng</div>
          <div v-if="!batches?.length" class="py-6 text-center text-gray-400 text-sm">Chưa có lô</div>
          <div v-for="b in batches" :key="b.name" class="flex items-center px-4 py-2.5 border-t text-sm">
            <div class="flex-1">{{ b.batch_id }}</div>
            <div class="text-gray-500">{{ b.expiry_date ? 'HSD ' + $fmtDate(b.expiry_date) : '' }} · {{ fmtQty(b.batch_qty) }}</div>
          </div>
        </div>
      </template>
    </main>

    <!-- Edit modal -->
    <div v-if="showEdit" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="showEdit=false">
      <div class="bg-white rounded-xl w-full max-w-md p-5 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-semibold mb-4">Sửa hàng hóa</h3>
        <div class="space-y-3">
          <label class="block"><span class="text-sm text-gray-600 block mb-1">Tên hàng</span><input v-model="ef.item_name" class="inp" /></label>
          <label class="block"><span class="text-sm text-gray-600 block mb-1">Nhóm hàng</span>
            <select v-model="ef.item_group" class="inp"><option v-for="g in groups" :key="g.name" :value="g.name">{{ g.item_group_name }}</option></select>
          </label>
          <label class="block"><span class="text-sm text-gray-600 block mb-1">Phương pháp định giá</span>
            <select v-model="ef.valuation_method" class="inp"><option value="FIFO">FIFO</option><option value="Moving Average">Bình quân gia quyền</option></select>
          </label>
          <label class="block"><span class="text-sm text-gray-600 block mb-1">Mô tả</span><textarea v-model="ef.description" rows="2" class="inp"></textarea></label>
          <label class="flex items-center gap-2 text-sm"><input type="checkbox" v-model="ef.disabled" /> Ngừng kinh doanh</label>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showEdit=false">Hủy</Button>
          <Button variant="solid" theme="orange" :loading="saving" @click="saveEdit">Lưu</Button>
        </div>
      </div>
    </div>

    <!-- Reorder modal -->
    <div v-if="showReorder" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="showReorder=false">
      <div class="bg-white rounded-xl w-full max-w-sm p-5">
        <h3 class="text-lg font-semibold mb-4">Định mức tồn tối thiểu</h3>
        <div class="space-y-3">
          <label class="block"><span class="text-sm text-gray-600 block mb-1">Kho</span>
            <select v-model="rf.warehouse" class="inp"><option v-for="w in warehouses" :key="w.name" :value="w.name">{{ w.warehouse_name }}</option></select>
          </label>
          <div class="grid grid-cols-2 gap-3">
            <label class="block"><span class="text-sm text-gray-600 block mb-1">Tồn tối thiểu</span><input v-model.number="rf.reorder_level" type="number" class="inp" /></label>
            <label class="block"><span class="text-sm text-gray-600 block mb-1">SL đặt lại</span><input v-model.number="rf.reorder_qty" type="number" class="inp" /></label>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showReorder=false">Hủy</Button>
          <Button variant="solid" theme="orange" :loading="saving" @click="saveReorder">Lưu</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, h } from 'vue'
import { useRoute } from 'vue-router'
import { Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi, callApi } from '../composables/useFrappeApi'

const route = useRoute()
const id = decodeURIComponent(route.params.id)
const item = ref(null), loading = ref(true), batches = ref([])
const { data: groups } = useFrappeApi('kho.api.get_item_groups', { initialData: [] })
const { data: warehouses } = useFrappeApi('kho.api.get_warehouses', { initialData: [] })

async function load() {
  loading.value = true
  try {
    item.value = await callApi('kho.api.get_item', { name: id }, 'GET')
    if (item.value?.has_batch_no) batches.value = await callApi('kho.api.get_batches', { item_code: id }, 'GET')
  } finally { loading.value = false }
}
load()

const showEdit = ref(false), saving = ref(false)
const ef = reactive({ item_name: '', item_group: '', valuation_method: 'FIFO', description: '', disabled: false })
function openEdit() {
  Object.assign(ef, {
    item_name: item.value.item_name, item_group: item.value.item_group,
    valuation_method: item.value.valuation_method || 'FIFO',
    description: stripHtml(item.value.description || ''), disabled: !!item.value.disabled,
  })
  showEdit.value = true
}
async function saveEdit() {
  saving.value = true
  try {
    await callApi('kho.api.update_item', { name: id, ...ef, disabled: ef.disabled ? 1 : 0 })
    showEdit.value = false
    await load()
  } catch (e) { alert('Lỗi: ' + (e?.message || e)) } finally { saving.value = false }
}

const showReorder = ref(false)
const rf = reactive({ warehouse: '', reorder_level: 0, reorder_qty: 0 })
function openReorder() { 
  rf.warehouse = warehouses.value?.[0]?.name || ''
  rf.reorder_level = 10
  rf.reorder_qty = 10
  showReorder.value = true 
}
async function saveReorder() {
  if (!rf.warehouse) {
    alert('Vui lòng chọn Kho')
    return
  }
  if (rf.reorder_level < 0 || rf.reorder_qty < 0) {
    alert('Số lượng tối thiểu và số lượng đặt lại không được nhỏ hơn 0')
    return
  }
  if (rf.reorder_level > 0 && rf.reorder_qty <= 0) {
    alert('Khi đặt định mức tồn tối thiểu > 0, Số lượng đặt lại bắt buộc phải lớn hơn 0')
    return
  }

  saving.value = true
  try {
    await callApi('kho.api.set_reorder_level', { item_code: id, ...rf })
    showReorder.value = false
    await load()
  } catch (e) { 
    const msg = e.messages?.join('\n') || e.message || e
    alert('Lỗi: ' + msg) 
  } finally { 
    saving.value = false 
  }
}

function fmtQty(v) { return Number(v || 0).toLocaleString('vi-VN') }
function fmtVnd(v) { return Number(v || 0).toLocaleString('vi-VN') + ' ₫' }
function stripHtml(s) { return (s || '').replace(/<[^>]*>/g, '').trim() }

const Stat = {
  props: ['label', 'value', 'color'],
  render() {
    return h('div', {}, [
      h('div', { class: ['text-base font-bold', this.color] }, this.value),
      h('div', { class: 'text-xs text-gray-500' }, this.label),
    ])
  },
}
</script>
