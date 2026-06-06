<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
      <button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5" /></button>
      <FeatherIcon name="layers" class="h-5 w-5 text-emerald-600" />
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Tồn kho</h1>
    </header>

    <main class="flex-1 p-4 max-w-4xl mx-auto w-full">
      <div class="flex flex-wrap gap-2 mb-3">
        <select v-model="warehouse" @change="reload" class="rounded-lg border px-3 py-2 text-sm">
          <option value="">Tất cả kho</option>
          <option v-for="w in stockWh" :key="w.name" :value="w.name">{{ w.warehouse_name }}</option>
        </select>
        <select v-model="group" @change="reload" class="rounded-lg border px-3 py-2 text-sm">
          <option value="">Tất cả nhóm</option>
          <option v-for="g in groups" :key="g.name" :value="g.name">{{ g.item_group_name }}</option>
        </select>
        <input v-model="q" placeholder="Lọc tên hàng..." class="flex-1 min-w-[160px] rounded-lg border px-3 py-2 text-sm" />
      </div>

      <div class="grid grid-cols-2 gap-3 mb-3">
        <div class="rounded-lg border bg-white p-3 text-center">
          <div class="text-lg font-bold text-emerald-600">{{ fmtVnd(d.total_value) }}</div>
          <div class="text-xs text-gray-500">Tổng giá trị tồn</div>
        </div>
        <div class="rounded-lg border bg-white p-3 text-center">
          <div class="text-lg font-bold text-orange-600">{{ filtered.length }}</div>
          <div class="text-xs text-gray-500">Dòng tồn</div>
        </div>
      </div>

      <div class="rounded-lg border bg-white overflow-hidden">
        <div class="grid grid-cols-12 gap-1 bg-gray-50 px-3 py-2 text-xs font-medium text-gray-500">
          <div class="col-span-5">Hàng hóa</div><div class="col-span-3">Kho</div>
          <div class="col-span-2 text-right">Tồn</div><div class="col-span-2 text-right">Giá trị</div>
        </div>
        <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
        <div v-else-if="!filtered.length" class="py-10 text-center text-gray-400">Không có tồn</div>
        <div v-for="(r,i) in filtered" :key="i" class="grid grid-cols-12 gap-1 px-3 py-2 border-t text-sm items-center">
          <div class="col-span-5 min-w-0"><div class="truncate font-medium">{{ r.item_name }}</div><div class="text-xs text-gray-400">{{ r.item_code }}</div></div>
          <div class="col-span-3 text-xs text-gray-500 truncate">{{ short(r.warehouse) }}</div>
          <div class="col-span-2 text-right">{{ fmtQty(r.actual_qty) }} <span class="text-xs text-gray-400">{{ r.stock_uom }}</span></div>
          <div class="col-span-2 text-right text-emerald-700">{{ fmtVnd(r.stock_value) }}</div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi, callApi } from '../composables/useFrappeApi'

const d = ref({ rows: [], total_value: 0, total_qty: 0 }), loading = ref(false)
const warehouse = ref(''), group = ref(''), q = ref('')
const { data: warehouses } = useFrappeApi('kho.api.get_warehouses', { initialData: [] })
const { data: groups } = useFrappeApi('kho.api.get_item_groups', { initialData: [] })
const stockWh = computed(() => (warehouses.value || []).filter(w => !w.is_group))

async function reload() {
  loading.value = true
  try { d.value = await callApi('kho.api.get_stock_balance', { warehouse: warehouse.value, item_group: group.value }, 'GET') }
  finally { loading.value = false }
}
reload()

const filtered = computed(() => {
  const rows = d.value?.rows || []
  if (!q.value) return rows
  const s = q.value.toLowerCase()
  return rows.filter(r => (r.item_name || '').toLowerCase().includes(s) || (r.item_code || '').toLowerCase().includes(s))
})

function short(w) { return (w || '').replace(/ - [A-Z]+$/, '') }
function fmtQty(v) { return Number(v || 0).toLocaleString('vi-VN') }
function fmtVnd(v) { return Number(v || 0).toLocaleString('vi-VN') + ' ₫' }
</script>
