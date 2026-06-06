<template>
  <DetailLayout :loading="loading" :title="doc?.customer_name || name" icon="user" icon-class="text-blue-600" back="/customers"
    :heading="doc?.customer_name" :meta="doc?.customer_group" :amount="fmtVnd(doc?.outstanding)" amount-label="Dư nợ" gradient="from-blue-600 to-indigo-600">
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Đơn bán gần đây</div>
      <div v-if="!doc?.recent_orders?.length" class="text-sm text-gray-400">Chưa có đơn bán</div>
      <button v-for="so in doc?.recent_orders || []" :key="so.name" class="w-full flex items-center gap-2 text-sm px-2 py-2 rounded hover:bg-gray-50 border-b last:border-0" @click="$router.push('/sales-orders/' + so.name)">
        <span class="flex-1 text-left font-medium">{{ so.name }}</span>
        <span class="text-gray-500">{{ $fmtDate(so.transaction_date) }}</span>
        <span class="font-semibold">{{ fmtVnd(so.grand_total) }}</span>
        <StatusBadge :status="so.status" :dot="false" />
      </button>
    </div>
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Sổ công nợ (GL 131)</div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead><tr><th class="px-2 py-1 text-left">Ngày</th><th class="px-2 py-1 text-left">Chứng từ</th><th class="px-2 py-1 text-right">Nợ</th><th class="px-2 py-1 text-right">Có</th><th class="px-2 py-1 text-right">Lũy kế</th></tr></thead>
          <tbody>
            <tr v-for="(g, i) in ledgerRows" :key="i">
              <td class="px-2 py-1">{{ $fmtDate(g.posting_date) }}</td>
              <td class="px-2 py-1">{{ g.voucher_no }}</td>
              <td class="px-2 py-1 text-right">{{ g.debit ? money(g.debit) : '' }}</td>
              <td class="px-2 py-1 text-right">{{ g.credit ? money(g.credit) : '' }}</td>
              <td class="px-2 py-1 text-right font-medium">{{ money(g.balance) }}</td>
            </tr>
            <tr v-if="!ledgerRows.length"><td colspan="5" class="py-4 text-center text-gray-400">Chưa có phát sinh</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <template #sidebar>
      <div class="app-card p-4 space-y-1 text-sm">
        <div class="flex justify-between"><span class="text-gray-500">Mã KH</span><span class="font-medium">{{ doc?.name }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Loại</span><span>{{ doc?.customer_type }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">MST</span><span>{{ doc?.tax_id || '—' }}</span></div>
        <div class="flex justify-between border-t pt-1 mt-1"><span class="text-gray-500">Dư nợ</span><span class="font-bold" :class="doc?.outstanding > 0 ? 'text-rose-600' : 'text-emerald-600'">{{ fmtVnd(doc?.outstanding) }}</span></div>
        <a v-if="doc?.crm_url" :href="doc.crm_url" class="text-indigo-600 text-xs underline">↗ Cơ hội CRM liên kết</a>
      </div>
    </template>
  </DetailLayout>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { DetailLayout, StatusBadge, callApi, fmtVnd, money } from '@shared'
const route = useRoute(); const name = route.params.name
const doc = ref(null); const loading = ref(true)
const ledgerRows = computed(() => {
  let bal = 0
  return (doc.value?.ledger || []).map((g) => { bal += (g.debit || 0) - (g.credit || 0); return { ...g, balance: bal } }).reverse()
})
async function load() { loading.value = true; try { doc.value = await callApi('kinhdoanh.api.get_customer', { name }, 'GET') } finally { loading.value = false } }
load()
</script>
