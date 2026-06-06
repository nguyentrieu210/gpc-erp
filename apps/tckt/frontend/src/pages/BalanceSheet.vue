<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Bảng cân đối kế toán (CĐKT)" icon="bar-chart-2" icon-class="text-indigo-600" />
    <main class="flex-1 p-4 max-w-3xl mx-auto w-full space-y-3">
      <div class="flex gap-2 items-end"><div><label class="text-xs text-gray-500">Tại ngày</label><input type="date" v-model="dt" @change="reload" class="inp" /></div></div>
      <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
      <template v-else>
        <div class="app-card p-4">
          <div class="font-bold text-blue-600 mb-1">Tài sản</div>
          <div v-for="r in d.asset || []" :key="r.account" class="flex justify-between text-sm py-1"><span>{{ r.account_name }}</span><span>{{ money(r.balance) }}</span></div>
          <div class="flex justify-between font-bold border-t pt-2 mt-2"><span>Tổng tài sản</span><span>{{ fmtVnd(d.total_asset) }}</span></div>
        </div>
        <div class="app-card p-4">
          <div class="font-bold text-amber-600 mb-1">Nợ phải trả</div>
          <div v-for="r in d.liability || []" :key="r.account" class="flex justify-between text-sm py-1"><span>{{ r.account_name }}</span><span>{{ money(Math.abs(r.balance)) }}</span></div>
          <div class="flex justify-between font-bold border-t pt-2 mt-2"><span>Tổng nợ phải trả</span><span>{{ fmtVnd(d.total_liability) }}</span></div>
        </div>
        <div class="app-card p-4">
          <div class="font-bold text-violet-600 mb-1">Vốn chủ sở hữu <span class="text-xs text-gray-500">(gồm LN {{ fmtVnd(d.net_income) }})</span></div>
          <div v-for="r in d.equity || []" :key="r.account" class="flex justify-between text-sm py-1"><span>{{ r.account_name }}</span><span>{{ money(Math.abs(r.balance)) }}</span></div>
          <div class="flex justify-between font-bold border-t pt-2 mt-2"><span>Tổng vốn CSH</span><span>{{ fmtVnd(d.total_equity) }}</span></div>
        </div>
        <div class="app-card p-4 flex justify-between font-bold" :class="d.balanced ? 'text-emerald-600' : 'text-rose-600'"><span>{{ d.balanced ? '✓ Cân bằng' : '✗ Lệch' }}</span><span>{{ fmtVnd(d.total_asset) }} = {{ fmtVnd((d.total_liability || 0) + (d.total_equity || 0)) }}</span></div>
      </template>
    </main>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { LoadingIndicator } from 'frappe-ui'
import { PageHeader, callApi, fmtVnd, money } from '@shared'
const d = ref({}); const loading = ref(false); const dt = ref(new Date().toISOString().slice(0, 10))
async function reload() { loading.value = true; try { d.value = await callApi('tckt.api.get_balance_sheet', { as_of_date: dt.value }, 'GET') } finally { loading.value = false } }
reload()
</script>
