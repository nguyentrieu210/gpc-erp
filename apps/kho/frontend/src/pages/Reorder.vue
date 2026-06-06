<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
      <button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5" /></button>
      <FeatherIcon name="alert-triangle" class="h-5 w-5 text-red-600" />
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Tồn tối thiểu</h1>
    </header>

    <main class="flex-1 p-4 max-w-3xl mx-auto w-full">
      <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
      <template v-else>
        <div v-if="!rows.length" class="rounded-lg border border-emerald-200 bg-emerald-50 p-6 text-center text-emerald-700">
          <FeatherIcon name="check-circle" class="h-8 w-8 mx-auto mb-2" />
          Không có mặt hàng nào dưới định mức tồn tối thiểu.
        </div>
        <div v-else class="rounded-lg border bg-white divide-y">
          <div v-for="(r,i) in rows" :key="i" class="px-4 py-3">
            <div class="flex items-center gap-2">
              <FeatherIcon name="alert-triangle" class="h-4 w-4 text-red-500 shrink-0" />
              <div class="flex-1 min-w-0">
                <div class="font-medium text-gray-900 truncate">{{ r.item_name }}</div>
                <div class="text-xs text-gray-500">{{ short(r.warehouse) }} · tối thiểu {{ fmtQty(r.reorder_level) }} {{ r.stock_uom }}</div>
              </div>
              <div class="text-right shrink-0">
                <div class="text-sm font-semibold text-red-600">{{ fmtQty(r.projected_qty) }}</div>
                <div class="text-xs text-gray-400">dự kiến</div>
              </div>
            </div>
            <div class="mt-2">
              <Button variant="solid" theme="orange" size="sm" :loading="busy===i" @click="createMr(r, i)">Tạo yêu cầu mua {{ fmtQty(r.reorder_qty) }}</Button>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { callApi } from '../composables/useFrappeApi'

const rows = ref([]), loading = ref(false), busy = ref(-1)

async function reload() {
  loading.value = true
  try { rows.value = await callApi('kho.api.get_reorder_items', {}, 'GET') }
  finally { loading.value = false }
}
reload()

async function createMr(r, i) {
  busy.value = i
  try {
    await callApi('kho.api.create_material_request', {
      material_request_type: r.material_request_type || 'Purchase',
      items: JSON.stringify([{ item_code: r.item_code, qty: r.reorder_qty, warehouse: r.warehouse }]),
      warehouse: r.warehouse, submit: 1,
    })
    alert('Đã tạo yêu cầu cho ' + r.item_name)
  } catch (e) { alert('Lỗi: ' + (e?.message || e)) } finally { busy.value = -1 }
}

function short(w) { return (w || '').replace(/ - [A-Z]+$/, '') }
function fmtQty(v) { return Number(v || 0).toLocaleString('vi-VN') }
</script>
