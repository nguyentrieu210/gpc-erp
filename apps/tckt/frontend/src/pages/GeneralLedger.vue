<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Sổ cái (GL)" icon="book-open" icon-class="text-blue-600" />
    <main class="flex-1 p-4 max-w-6xl mx-auto w-full space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-2">
        <div class="sm:col-span-2"><label class="text-xs text-gray-500">Tài khoản</label><EntityPicker v-model="acct" api="tckt.api.get_accounts" result-key="entries" value-key="name" label-key="label" placeholder="Tất cả TK…" @select="reload" /></div>
        <div><label class="text-xs text-gray-500">Từ ngày</label><input v-model="fd" type="date" class="inp" @change="reload" /></div>
        <div><label class="text-xs text-gray-500">Đến ngày</label><input v-model="td" type="date" class="inp" @change="reload" /></div>
      </div>
      <div v-if="vts.length" class="flex flex-wrap gap-1">
        <button class="text-xs px-2 py-1 rounded-full" :class="!vt ? 'bg-indigo-600 text-white' : 'bg-gray-100'" @click="vt = ''; reload()">Tất cả</button>
        <button v-for="t in vts" :key="t" class="text-xs px-2 py-1 rounded-full" :class="vt === t ? 'bg-indigo-600 text-white' : 'bg-gray-100'" @click="vt = t; reload()">{{ t }}</button>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div class="app-card p-3 text-center"><div class="text-xs text-gray-500">Tổng Nợ</div><div class="text-lg font-bold text-emerald-600">{{ fmtVnd(d.debit_total) }}</div></div>
        <div class="app-card p-3 text-center"><div class="text-xs text-gray-500">Tổng Có</div><div class="text-lg font-bold text-rose-600">{{ fmtVnd(d.credit_total) }}</div></div>
      </div>
      <DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm chứng từ / TK…" :search-keys="['voucher_no', 'account', 'remarks']" @row-click="drill">
        <template #col-posting_date="{ value }">{{ $fmtDate(value) }}</template>
        <template #col-account="{ value }">{{ shortAcct(value) }}</template>
        <template #col-debit="{ value }"><span class="text-emerald-600">{{ value > 0 ? money(value) : '' }}</span></template>
        <template #col-credit="{ value }"><span class="text-rose-600">{{ value > 0 ? money(value) : '' }}</span></template>
      </DataTable>
    </main>

    <FormModal :show="!!voucher" :title="'Chứng từ ' + (voucher?.voucher_no || '')" icon="file-text" hide-footer @close="voucher = null">
      <div v-if="voucher">
        <div class="text-sm text-gray-500 mb-2">{{ voucher.voucher_type }} · <span :class="voucher.balanced ? 'text-emerald-600' : 'text-rose-600'">{{ voucher.balanced ? 'Cân đối' : 'Lệch' }}</span></div>
        <table class="w-full text-sm">
          <thead><tr><th class="px-2 py-1 text-left">Tài khoản</th><th class="px-2 py-1 text-right">Nợ</th><th class="px-2 py-1 text-right">Có</th></tr></thead>
          <tbody>
            <tr v-for="(e, i) in voucher.entries" :key="i"><td class="px-2 py-1.5">{{ shortAcct(e.account) }}</td><td class="px-2 py-1.5 text-right text-emerald-600">{{ e.debit ? money(e.debit) : '' }}</td><td class="px-2 py-1.5 text-right text-rose-600">{{ e.credit ? money(e.credit) : '' }}</td></tr>
            <tr class="bg-gray-50 font-semibold"><td class="px-2 py-2 text-right">Tổng</td><td class="px-2 py-2 text-right">{{ money(voucher.total_debit) }}</td><td class="px-2 py-2 text-right">{{ money(voucher.total_credit) }}</td></tr>
          </tbody>
        </table>
      </div>
    </FormModal>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { PageHeader, DataTable, EntityPicker, FormModal, callApi, fmtVnd, money } from '@shared'
const rows = ref([]); const d = ref({}); const loading = ref(false)
const acct = ref(''); const fd = ref('2026-01-01'); const td = ref(new Date().toISOString().slice(0, 10)); const vt = ref(''); const vts = ref([])
const voucher = ref(null)
const columns = [
  { key: 'posting_date', label: 'Ngày' }, { key: 'account', label: 'Tài khoản' },
  { key: 'voucher_no', label: 'Chứng từ' }, { key: 'debit', label: 'Nợ', align: 'right' }, { key: 'credit', label: 'Có', align: 'right' },
]
async function reload() {
  loading.value = true
  try {
    const r = await callApi('tckt.api.get_gl_entries', { account: acct.value || undefined, from_date: fd.value, to_date: td.value, voucher_type: vt.value || undefined, page_length: 500 }, 'GET')
    d.value = r || {}; rows.value = r?.entries || []
    if (!vts.value.length) vts.value = r?.available_voucher_types || []
  } finally { loading.value = false }
}
reload()
async function drill(row) { try { voucher.value = await callApi('tckt.api.get_voucher_gl', { voucher_type: row.voucher_type, voucher_no: row.voucher_no }, 'GET') } catch (e) {} }
function shortAcct(a) { return (a || '').split(' - ').slice(0, 2).join(' - ') }
</script>
