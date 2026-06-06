<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
      <button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5" /></button>
      <FeatherIcon name="book-open" class="h-5 w-5 text-indigo-600" />
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Sổ kho (thẻ kho)</h1>
    </header>

    <main class="flex-1 p-4 max-w-4xl mx-auto w-full">
      <div class="flex flex-wrap gap-2 mb-3">
        <select v-model="itemCode" @change="reload" class="flex-1 min-w-[180px] rounded-lg border px-3 py-2 text-sm">
          <option value="">— Chọn mặt hàng —</option>
          <option v-for="it in itemOpts" :key="it.name" :value="it.item_code">{{ it.item_name }} ({{ it.item_code }})</option>
        </select>
        <select v-model="warehouse" @change="reload" class="rounded-lg border px-3 py-2 text-sm">
          <option value="">Tất cả kho</option>
          <option v-for="w in stockWh" :key="w.name" :value="w.name">{{ w.warehouse_name }}</option>
        </select>
      </div>

      <div v-if="!itemCode" class="py-10 text-center text-gray-400">Chọn 1 mặt hàng để xem thẻ kho.</div>
      <div v-else class="rounded-lg border bg-white overflow-x-auto">
        <table class="w-full text-sm min-w-[640px]">
          <thead>
            <tr class="bg-gray-50 text-xs text-gray-500 text-left">
              <th class="px-3 py-2">Ngày</th><th class="px-3 py-2">Chứng từ</th><th class="px-3 py-2">Kho</th>
              <th class="px-3 py-2 text-right">Nhập</th><th class="px-3 py-2 text-right">Xuất</th>
              <th class="px-3 py-2 text-right">Tồn</th><th class="px-3 py-2 text-right">Đơn giá</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td colspan="7" class="py-8 text-center"><LoadingIndicator /></td></tr>
            <tr v-else-if="!rows.length"><td colspan="7" class="py-8 text-center text-gray-400">Chưa có phát sinh</td></tr>
            <tr v-for="(r,i) in rows" :key="i" class="border-t">
              <td class="px-3 py-2 whitespace-nowrap">{{ $fmtDate(r.posting_date) }}</td>
              <td class="px-3 py-2 text-xs text-gray-500">{{ r.voucher_no }}</td>
              <td class="px-3 py-2 text-xs">{{ short(r.warehouse) }}</td>
              <td class="px-3 py-2 text-right text-emerald-600">{{ r.actual_qty > 0 ? fmtQty(r.actual_qty) : '' }}</td>
              <td class="px-3 py-2 text-right text-red-600">{{ r.actual_qty < 0 ? fmtQty(-r.actual_qty) : '' }}</td>
              <td class="px-3 py-2 text-right font-medium">{{ fmtQty(r.qty_after_transaction) }}</td>
              <td class="px-3 py-2 text-right text-gray-500">{{ fmtVnd(r.valuation_rate) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi, callApi } from '../composables/useFrappeApi'

const itemCode = ref(''), warehouse = ref(''), rows = ref([]), loading = ref(false)
const { data: warehouses } = useFrappeApi('kho.api.get_warehouses', { initialData: [] })
const { data: itemsResp } = useFrappeApi('kho.api.get_items', { initialData: { items: [] }, params: { page_length: 500 } })
const stockWh = computed(() => (warehouses.value || []).filter(w => !w.is_group))
const itemOpts = computed(() => itemsResp.value?.items || [])

async function reload() {
  if (!itemCode.value) { rows.value = []; return }
  loading.value = true
  try { rows.value = await callApi('kho.api.get_stock_ledger', { item_code: itemCode.value, warehouse: warehouse.value }, 'GET') }
  finally { loading.value = false }
}

function short(w) { return (w || '').replace(/ - [A-Z]+$/, '') }
function fmtQty(v) { return Number(v || 0).toLocaleString('vi-VN') }
function fmtVnd(v) { return Number(v || 0).toLocaleString('vi-VN') + ' ₫' }
</script>
