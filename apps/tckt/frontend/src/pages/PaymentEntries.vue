<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Phiếu thu / chi" icon="repeat" icon-class="text-cyan-600" />
    <main class="flex-1 p-4 max-w-5xl mx-auto w-full">
      <DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm số phiếu / đối tượng…" :search-keys="['name', 'party_name', 'reference_no']" :filters="filterDefs" @row-click="drill">
        <template #col-type_vi="{ row }"><StatusBadge :status="row.type_vi" :tone="row.payment_type === 'Receive' ? 'green' : 'amber'" /></template>
        <template #col-paid_amount="{ value }"><span class="font-semibold">{{ fmtVnd(value) }}</span></template>
        <template #col-posting_date="{ value }">{{ $fmtDate(value) }}</template>
        <template #col-docstatus="{ row }"><StatusBadge :status="row.docstatus === 1 ? 'Đã ghi sổ' : (row.docstatus === 2 ? 'Đã hủy' : 'Nháp')" /></template>
      </DataTable>
    </main>
    <FormModal :show="!!voucher" :title="'Chứng từ ' + (voucher?.voucher_no || '')" icon="file-text" hide-footer @close="voucher = null">
      <div v-if="voucher">
        <table class="w-full text-sm">
          <thead><tr><th class="px-2 py-1 text-left">Tài khoản</th><th class="px-2 py-1 text-right">Nợ</th><th class="px-2 py-1 text-right">Có</th></tr></thead>
          <tbody>
            <tr v-for="(e, i) in voucher.entries" :key="i"><td class="px-2 py-1.5">{{ (e.account || '').split(' - ').slice(0, 2).join(' - ') }}</td><td class="px-2 py-1.5 text-right text-emerald-600">{{ e.debit ? money(e.debit) : '' }}</td><td class="px-2 py-1.5 text-right text-rose-600">{{ e.credit ? money(e.credit) : '' }}</td></tr>
          </tbody>
        </table>
      </div>
    </FormModal>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { PageHeader, DataTable, FormModal, StatusBadge, callApi, fmtVnd, money } from '@shared'
const rows = ref([]); const loading = ref(false); const voucher = ref(null)
const columns = [
  { key: 'name', label: 'Số phiếu' }, { key: 'type_vi', label: 'Loại' }, { key: 'party_name', label: 'Đối tượng' },
  { key: 'posting_date', label: 'Ngày' }, { key: 'paid_amount', label: 'Số tiền', align: 'right' }, { key: 'docstatus', label: 'Trạng thái' },
]
const filterDefs = [{ key: 'payment_type', label: 'Loại', options: [{ value: 'Receive', label: 'Phiếu thu' }, { value: 'Pay', label: 'Phiếu chi' }] }]
async function reload() { loading.value = true; try { rows.value = (await callApi('tckt.api.get_payment_entries', { page_length: 200 }, 'GET'))?.entries || [] } finally { loading.value = false } }
reload()
async function drill(row) { try { voucher.value = await callApi('tckt.api.get_voucher_gl', { voucher_type: 'Payment Entry', voucher_no: row.name }, 'GET') } catch (e) {} }
</script>
