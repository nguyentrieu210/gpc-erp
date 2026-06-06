<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5" /></button>
      <FeatherIcon name="settings" class="h-5 w-5 text-orange-600" />
      <h1 class="text-lg font-semibold text-gray-900">Cấu hình kho</h1>
    </header>

    <main class="flex-1 p-4 max-w-3xl mx-auto w-full space-y-4">
      <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>

      <template v-else>
        <div class="rounded-lg border bg-white p-4 flex items-center gap-3"
             :class="s?.ready ? 'border-emerald-300' : 'border-amber-300'">
          <FeatherIcon :name="s?.ready ? 'check-circle' : 'alert-triangle'" class="h-6 w-6" :class="s?.ready ? 'text-emerald-600' : 'text-amber-600'" />
          <div class="flex-1">
            <div class="font-semibold">{{ s?.ready ? 'Đã sẵn sàng hạch toán kho' : 'Chưa cấu hình đầy đủ' }}</div>
            <div class="text-sm text-gray-500">Công ty: {{ s?.company }} ({{ s?.abbr }}) · Định giá: {{ s?.valuation_method }}</div>
          </div>
          <Button variant="solid" theme="orange" :loading="running" @click="runSetup">Chạy cấu hình</Button>
        </div>

        <div class="rounded-lg border bg-white divide-y">
          <Row label="Tồn kho vĩnh viễn (Perpetual Inventory)" :ok="!!s?.enable_perpetual_inventory" :value="s?.enable_perpetual_inventory ? 'Đang bật' : 'Tắt'" />
          <Row label="TK tồn kho mặc định" :ok="!!s?.default_inventory_account" :value="s?.default_inventory_account || '—'" />
          <Row label="TK chênh lệch kho (Stock Adjustment)" :ok="!!s?.stock_adjustment_account" :value="s?.stock_adjustment_account || '—'" />
          <Row label="TK giá vốn (632)" :ok="!!s?.default_expense_account" :value="s?.default_expense_account || '—'" />
          <Row label="TK hàng mua chưa hóa đơn (SRBNB)" :ok="!!s?.stock_received_but_not_billed" :value="s?.stock_received_but_not_billed || '—'" />
          <Row label="Kho mặc định" :ok="!!s?.default_warehouse" :value="s?.default_warehouse || '—'" />
        </div>

        <div class="grid grid-cols-3 gap-3">
          <div class="rounded-lg border bg-white p-3 text-center">
            <div class="text-xl font-bold text-blue-600">{{ s?.warehouse_count ?? 0 }}</div>
            <div class="text-xs text-gray-500">Kho</div>
          </div>
          <div class="rounded-lg border bg-white p-3 text-center">
            <div class="text-xl font-bold text-orange-600">{{ s?.item_group_count ?? 0 }}</div>
            <div class="text-xs text-gray-500">Nhóm hàng</div>
          </div>
          <div class="rounded-lg border bg-white p-3 text-center">
            <div class="text-xl font-bold text-violet-600">{{ s?.uom_count ?? 0 }}</div>
            <div class="text-xs text-gray-500">Đơn vị tính</div>
          </div>
        </div>

        <div v-if="result" class="rounded-lg border border-emerald-300 bg-emerald-50 p-4 text-sm text-emerald-800">
          <div class="font-medium mb-1">Đã chạy cấu hình:</div>
          <div>• Tài khoản đã đổi: {{ (result.accounts?.changed || []).join(', ') || 'không có thay đổi' }}</div>
          <div>• Kho tạo mới: {{ (result.warehouses_created || []).length }} · Nhóm hàng: {{ (result.item_groups_created || []).length }} · ĐVT: {{ (result.uoms_created || []).length }}</div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, h } from 'vue'
import { Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi, callApi } from '../composables/useFrappeApi'

const { data: s, loading, fetch } = useFrappeApi('kho.api.get_kho_setup_status', { initialData: null })
const running = ref(false)
const result = ref(null)

async function runSetup() {
  running.value = true
  try {
    result.value = await callApi('kho.api.setup_kho')
    await fetch()
  } catch (e) {
    alert('Lỗi: ' + (e?.message || e))
  } finally {
    running.value = false
  }
}

const Row = {
  props: ['label', 'value', 'ok'],
  render() {
    return h('div', { class: 'flex items-center gap-3 px-4 py-3' }, [
      h(FeatherIcon, { name: this.ok ? 'check' : 'x', class: ['h-4 w-4 shrink-0', this.ok ? 'text-emerald-600' : 'text-red-500'] }),
      h('div', { class: 'flex-1 min-w-0' }, [
        h('div', { class: 'text-sm font-medium text-gray-800' }, this.label),
        h('div', { class: 'text-xs text-gray-500 truncate' }, this.value),
      ]),
    ])
  },
}
</script>
