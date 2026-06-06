<template>
  <DetailLayout :loading="loading" :title="name" icon="edit-3" icon-class="text-green-600" back="/journal-entries"
    :heading="doc?.user_remark || name" :meta="metaLine" :status="statusText" :amount="fmtVnd(doc?.total_debit)" gradient="from-green-600 to-emerald-600">
    <template #actions>
      <button v-if="doc?.docstatus === 0" class="btn-success px-3 py-2 rounded-lg text-sm font-medium" @click="act('submit_journal_entry','Đã ghi sổ')">Ghi sổ</button>
      <button v-if="doc?.docstatus === 1" class="btn-danger px-3 py-2 rounded-lg text-sm" @click="act('cancel_journal_entry','Đã hủy')">Hủy</button>
      <button class="btn-secondary px-3 py-2 rounded-lg text-sm inline-flex items-center gap-1" @click="doPrint"><FeatherIcon name="printer" class="h-4 w-4" /> In</button>
    </template>
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Định khoản</div>
      <table class="w-full text-sm">
        <thead><tr><th class="px-2 py-1 text-left">Tài khoản</th><th class="px-2 py-1 text-left">Đối tượng</th><th class="px-2 py-1 text-right">Nợ</th><th class="px-2 py-1 text-right">Có</th></tr></thead>
        <tbody>
          <tr v-for="(a, i) in doc?.accounts || []" :key="i">
            <td class="px-2 py-1.5">{{ a.account_name || a.account }}</td>
            <td class="px-2 py-1.5 text-gray-500">{{ a.party || '' }}</td>
            <td class="px-2 py-1.5 text-right text-emerald-600">{{ a.debit_in_account_currency ? money(a.debit_in_account_currency) : '' }}</td>
            <td class="px-2 py-1.5 text-right text-rose-600">{{ a.credit_in_account_currency ? money(a.credit_in_account_currency) : '' }}</td>
          </tr>
          <tr class="bg-gray-50 font-semibold"><td colspan="2" class="px-2 py-2 text-right">Tổng</td><td class="px-2 py-2 text-right">{{ money(doc?.total_debit) }}</td><td class="px-2 py-2 text-right">{{ money(doc?.total_credit) }}</td></tr>
        </tbody>
      </table>
    </div>
    <template #sidebar>
      <div class="app-card p-4 space-y-1 text-sm">
        <div class="flex justify-between"><span class="text-gray-500">Ngày</span><span>{{ $fmtDate(doc?.posting_date) }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Loại</span><span>{{ doc?.voucher_type }}</span></div>
        <div class="flex justify-between border-t pt-1 mt-1"><span class="text-gray-500">Tổng</span><span class="font-bold">{{ fmtVnd(doc?.total_debit) }}</span></div>
      </div>
      <div class="app-card p-4"><div class="text-sm font-semibold mb-2">Hoạt động</div><ActivityTimeline :items="activity" /></div>
    </template>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </DetailLayout>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import { DetailLayout, ActivityTimeline, useToast, callApi, fmtVnd, money, printHtml } from '@shared'
const route = useRoute(); const name = route.params.name
const { toast, ok, err } = useToast()
const doc = ref(null); const loading = ref(true); const activity = ref([])
const statusText = computed(() => doc.value?.docstatus === 1 ? 'Đã ghi sổ' : (doc.value?.docstatus === 2 ? 'Đã hủy' : 'Nháp'))
const metaLine = computed(() => doc.value ? `Số ${doc.value.name}` : '')
async function load() { loading.value = true; try { doc.value = await callApi('tckt.api.get_journal_entry', { name }, 'GET'); activity.value = await callApi('tckt.api.get_doc_activity', { doctype: 'Journal Entry', name }, 'GET') } catch (e) { err(e?.message) } finally { loading.value = false } }
load()
async function act(m, msg) { try { await callApi('tckt.api.' + m, { name }); ok(msg); load() } catch (e) { err(e?.message) } }
async function doPrint() { try { const html = await callApi('tckt.api.print_journal_entry', { name }, 'GET'); printHtml(html, name) } catch (e) { err(e?.message) } }
</script>
