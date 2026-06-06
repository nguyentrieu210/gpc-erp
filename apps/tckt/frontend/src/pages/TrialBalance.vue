<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Bảng cân đối phát sinh" icon="layers" icon-class="text-amber-600" />
    <main class="flex-1 p-4 max-w-5xl mx-auto w-full space-y-3">
      <div class="flex flex-wrap gap-2 items-end">
        <div><label class="text-xs text-gray-500">Từ ngày</label><input type="date" v-model="fd" @change="reload" class="inp" /></div>
        <div><label class="text-xs text-gray-500">Đến ngày</label><input type="date" v-model="td" @change="reload" class="inp" /></div>
        <span class="ml-auto text-sm" :class="d.balanced ? 'text-emerald-600' : 'text-rose-600'">{{ d.balanced ? '✓ Cân đối' : '✗ Lệch' }}</span>
      </div>
      <DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm TK…" :search-keys="['account_number', 'account_name']" :clickable="false">
        <template #col-debit="{ value }"><span class="text-emerald-600">{{ value > 0 ? money(value) : '' }}</span></template>
        <template #col-credit="{ value }"><span class="text-rose-600">{{ value > 0 ? money(value) : '' }}</span></template>
        <template #col-balance="{ value }"><span :class="value >= 0 ? 'text-emerald-700' : 'text-rose-700'">{{ money(value) }}</span></template>
      </DataTable>
      <div class="app-card p-3 flex justify-end gap-8 text-sm font-semibold">
        <span>Tổng Nợ: <span class="text-emerald-600">{{ fmtVnd(d.total_debit) }}</span></span>
        <span>Tổng Có: <span class="text-rose-600">{{ fmtVnd(d.total_credit) }}</span></span>
      </div>
    </main>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { PageHeader, DataTable, callApi, fmtVnd, money } from '@shared'
const rows = ref([]); const d = ref({}); const loading = ref(false)
const fd = ref('2026-01-01'); const td = ref(new Date().toISOString().slice(0, 10))
const columns = [
  { key: 'account_number', label: 'Số hiệu' }, { key: 'account_name', label: 'Tên tài khoản' },
  { key: 'debit', label: 'PS Nợ', align: 'right' }, { key: 'credit', label: 'PS Có', align: 'right' }, { key: 'balance', label: 'Số dư', align: 'right' },
]
async function reload() { loading.value = true; try { d.value = await callApi('tckt.api.get_trial_balance', { from_date: fd.value, to_date: td.value }, 'GET'); rows.value = d.value?.rows || [] } finally { loading.value = false } }
reload()
</script>
