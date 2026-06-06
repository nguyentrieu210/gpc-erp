<template>
  <DetailLayout :loading="loading" :title="name" icon="file-plus" icon-class="text-violet-600" back="/sales-invoices"
    :heading="doc?.customer_name" :status="statusText" :status-tone="doc?.outstanding_amount > 0 ? 'amber' : 'green'"
    :amount="fmtVnd(doc?.grand_total)" gradient="from-violet-600 to-purple-600">
    <template #actions>
      <template v-if="doc?.docstatus === 0">
        <button class="btn-success px-3 py-2 rounded-lg text-sm font-medium" @click="act('submit_sales_invoice','Đã ghi sổ hóa đơn')">Ghi sổ</button>
        <button class="btn-danger px-3 py-2 rounded-lg text-sm" @click="act('cancel_sales_invoice','Đã hủy')">Hủy</button>
      </template>
      <template v-else-if="doc?.docstatus === 1">
        <button v-if="doc.outstanding_amount > 0" class="btn-success px-3 py-2 rounded-lg text-sm font-medium" @click="pay">Thu tiền</button>
        <button v-if="!doc.is_return" class="btn-warning px-3 py-2 rounded-lg text-sm" @click="creditNote">Điều chỉnh giảm</button>
      </template>
      <button class="btn-secondary px-3 py-2 rounded-lg text-sm inline-flex items-center gap-1" @click="doPrint"><FeatherIcon name="printer" class="h-4 w-4" /> In</button>
    </template>
    <div class="app-card p-4"><div class="text-sm font-semibold mb-2">Dòng hàng</div><LineItemsEditor :model-value="items" :editable="false" /></div>
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Thanh toán liên kết</div>
      <div v-if="!linked.payments?.length" class="text-sm text-gray-400">Chưa có phiếu thu</div>
      <div v-for="p in linked.payments || []" :key="p.name" class="flex items-center gap-2 text-sm px-2 py-1.5">
        <FeatherIcon name="dollar-sign" class="h-4 w-4 text-emerald-600" /><span class="flex-1">{{ p.name }}</span><span>{{ fmtVnd(p.paid_amount) }}</span>
      </div>
    </div>
    <template #sidebar>
      <div class="app-card p-4 space-y-1 text-sm">
        <div class="flex justify-between"><span class="text-gray-500">Khách hàng</span><span class="font-medium">{{ doc?.customer_name }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Ngày HĐ</span><span>{{ $fmtDate(doc?.posting_date) }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Hạn TT</span><span>{{ $fmtDate(doc?.due_date) }}</span></div>
        <div class="flex justify-between border-t pt-1 mt-1"><span class="text-gray-500">Tổng tiền</span><span class="font-bold">{{ fmtVnd(doc?.grand_total) }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Còn nợ</span><span class="font-bold" :class="doc?.outstanding_amount > 0 ? 'text-rose-600' : 'text-emerald-600'">{{ fmtVnd(doc?.outstanding_amount) }}</span></div>
      </div>
      <div class="app-card p-4"><div class="text-sm font-semibold mb-2">Hoạt động</div><ActivityTimeline :items="activity" /></div>
    </template>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </DetailLayout>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import { DetailLayout, LineItemsEditor, ActivityTimeline, useToast, callApi, fmtVnd, printHtml } from '@shared'
const route = useRoute(); const router = useRouter(); const name = route.params.name
const { toast, ok, err } = useToast()
const doc = ref(null); const loading = ref(true); const activity = ref([]); const linked = ref({})
const items = computed(() => (doc.value?.items || []).map((l) => ({ item_code: l.item_code, item_name: l.item_name, qty: l.qty, uom: l.uom || l.stock_uom, rate: l.rate, amount: l.amount })))
const statusText = computed(() => doc.value?.docstatus !== 1 ? 'Nháp' : (doc.value.outstanding_amount > 0 ? 'Còn nợ' : 'Đã thanh toán'))
async function load() {
  loading.value = true
  try {
    doc.value = await callApi('kinhdoanh.api.get_sales_invoice', { name }, 'GET')
    activity.value = await callApi('kinhdoanh.api.get_doc_activity', { doctype: 'Sales Invoice', name }, 'GET')
    if (doc.value?.docstatus === 1) linked.value = await callApi('kinhdoanh.api.get_linked_docs', { doctype: 'Sales Invoice', name }, 'GET')
  } catch (e) { err(e?.message) } finally { loading.value = false }
}
load()
async function act(m, msg) { try { await callApi('kinhdoanh.api.' + m, { name }); ok(msg); load() } catch (e) { err(e?.message) } }
async function pay() { try { await callApi('kinhdoanh.api.make_payment_receive', { invoice: name, submit: 1 }); ok('Đã thu tiền'); load() } catch (e) { err(e?.message) } }
async function creditNote() { try { const cn = await callApi('kinhdoanh.api.make_credit_note', { invoice_name: name, submit: 1 }); ok('Đã tạo điều chỉnh ' + cn.name); router.push('/sales-invoices/' + cn.name) } catch (e) { err(e?.message) } }
async function doPrint() { try { const html = await callApi('kinhdoanh.api.print_sales_invoice', { name }, 'GET'); printHtml(html, name) } catch (e) { err(e?.message) } }
</script>
