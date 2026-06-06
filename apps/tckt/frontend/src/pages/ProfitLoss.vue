<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Kết quả kinh doanh (P&L)" icon="trending-up" icon-class="text-emerald-600" />
    <main class="flex-1 p-4 max-w-3xl mx-auto w-full space-y-3">
      <div class="flex gap-2 items-end">
        <div><label class="text-xs text-gray-500">Từ ngày</label><input type="date" v-model="fd" @change="reload" class="inp" /></div>
        <div><label class="text-xs text-gray-500">Đến ngày</label><input type="date" v-model="td" @change="reload" class="inp" /></div>
      </div>
      <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
      <template v-else>
        <div class="app-card p-4">
          <div class="font-bold text-emerald-600 mb-1">Doanh thu</div>
          <div v-for="r in d.income || []" :key="r.account" class="flex justify-between text-sm py-1"><span>{{ r.account_name }}</span><span class="text-emerald-700">{{ money(r.balance) }}</span></div>
          <div class="flex justify-between font-bold border-t pt-2 mt-2"><span>Tổng doanh thu</span><span>{{ fmtVnd(d.total_income) }}</span></div>
        </div>
        <div class="app-card p-4">
          <div class="font-bold text-rose-600 mb-1">Chi phí</div>
          <div v-for="r in d.expense || []" :key="r.account" class="flex justify-between text-sm py-1"><span>{{ r.account_name }}</span><span class="text-rose-700">{{ money(r.balance) }}</span></div>
          <div class="flex justify-between font-bold border-t pt-2 mt-2"><span>Tổng chi phí</span><span>{{ fmtVnd(d.total_expense) }}</span></div>
        </div>
        <div class="app-card p-4 flex justify-between font-bold text-lg" :class="d.net_profit >= 0 ? 'text-emerald-600' : 'text-rose-600'"><span>Lợi nhuận ròng</span><span>{{ fmtVnd(d.net_profit) }}</span></div>
      </template>
    </main>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { LoadingIndicator } from 'frappe-ui'
import { PageHeader, callApi, fmtVnd, money } from '@shared'
const d = ref({}); const loading = ref(false); const fd = ref('2026-01-01'); const td = ref(new Date().toISOString().slice(0, 10))
async function reload() { loading.value = true; try { d.value = await callApi('tckt.api.get_profit_loss', { from_date: fd.value, to_date: td.value }, 'GET') } finally { loading.value = false } }
reload()
</script>
