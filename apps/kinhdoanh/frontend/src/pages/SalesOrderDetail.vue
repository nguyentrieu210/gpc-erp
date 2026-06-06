<template>
  <DetailLayout :loading="loading" :title="name" icon="shopping-cart" back="/sales-orders"
    :heading="doc?.customer_name" :meta="metaLine" :status="doc?.status_vi || doc?.status" :amount="fmtVnd(doc?.grand_total)"
    gradient="from-rose-600 to-pink-600">
    <template #actions>
      <template v-if="doc?.docstatus === 0">
        <button class="btn-success px-3 py-2 rounded-lg text-sm font-medium" @click="act('submit_sales_order','Đã chốt đơn')">Chốt đơn</button>
        <button class="btn-danger px-3 py-2 rounded-lg text-sm" @click="act('cancel_sales_order','Đã hủy')">Hủy</button>
      </template>
      <template v-else-if="doc?.docstatus === 1">
        <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium" :disabled="doc.per_delivered >= 100" @click="makeDoc('make_delivery_note_from_so','/delivery-notes/')">Tạo phiếu giao</button>
        <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium" :disabled="doc.per_billed >= 100" @click="makeDoc('make_sales_invoice_from_so','/sales-invoices/')">Tạo hóa đơn</button>
      </template>
      <button class="btn-secondary px-3 py-2 rounded-lg text-sm inline-flex items-center gap-1" @click="doPrint"><FeatherIcon name="printer" class="h-4 w-4" /> In</button>
    </template>

    <!-- Tiến độ -->
    <div v-if="doc?.docstatus === 1" class="app-card p-4 grid grid-cols-2 gap-4">
      <div>
        <div class="text-xs text-gray-500 mb-1">Đã giao hàng</div>
        <div class="h-2 rounded-full bg-gray-100 overflow-hidden"><div class="h-full bg-emerald-500" :style="{ width: (doc.per_delivered || 0) + '%' }" /></div>
        <div class="text-xs mt-1 font-medium">{{ Math.round(doc.per_delivered || 0) }}%</div>
      </div>
      <div>
        <div class="text-xs text-gray-500 mb-1">Đã xuất hóa đơn</div>
        <div class="h-2 rounded-full bg-gray-100 overflow-hidden"><div class="h-full bg-violet-500" :style="{ width: (doc.per_billed || 0) + '%' }" /></div>
        <div class="text-xs mt-1 font-medium">{{ Math.round(doc.per_billed || 0) }}%</div>
      </div>
    </div>

    <!-- Dòng hàng -->
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Dòng hàng</div>
      <LineItemsEditor :model-value="items" :editable="false" />
    </div>

    <!-- Chứng từ liên kết -->
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Chứng từ liên kết</div>
      <div v-if="!linked.delivery_notes?.length && !linked.invoices?.length" class="text-sm text-gray-400">Chưa có phiếu giao / hóa đơn</div>
      <div class="space-y-1">
        <button v-for="dn in linked.delivery_notes || []" :key="dn.name" class="w-full flex items-center gap-2 text-sm px-2 py-1.5 rounded hover:bg-gray-50" @click="router.push('/delivery-notes/' + dn.name)">
          <FeatherIcon name="truck" class="h-4 w-4 text-emerald-600" /><span class="flex-1 text-left">{{ dn.name }}</span><span>{{ fmtVnd(dn.grand_total) }}</span>
        </button>
        <button v-for="si in linked.invoices || []" :key="si.name" class="w-full flex items-center gap-2 text-sm px-2 py-1.5 rounded hover:bg-gray-50" @click="router.push('/sales-invoices/' + si.name)">
          <FeatherIcon name="file-plus" class="h-4 w-4 text-violet-600" /><span class="flex-1 text-left">{{ si.name }}</span><span :class="si.outstanding_amount > 0 ? 'text-rose-600' : 'text-emerald-600'">{{ fmtVnd(si.grand_total) }}</span>
        </button>
      </div>
    </div>

    <template #sidebar>
      <div class="app-card p-4 space-y-1 text-sm">
        <div class="flex justify-between"><span class="text-gray-500">Khách hàng</span><span class="font-medium">{{ doc?.customer_name }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Ngày đặt</span><span>{{ $fmtDate(doc?.transaction_date) }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Ngày giao</span><span>{{ $fmtDate(doc?.delivery_date) }}</span></div>
        <div class="flex justify-between border-t pt-1 mt-1"><span class="text-gray-500">Tổng tiền</span><span class="font-bold">{{ fmtVnd(doc?.grand_total) }}</span></div>
      </div>
      <div class="app-card p-4">
        <div class="text-sm font-semibold mb-2">Hoạt động</div>
        <ActivityTimeline :items="activity" />
      </div>
    </template>

    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium"
      :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </DetailLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import { DetailLayout, LineItemsEditor, ActivityTimeline, useToast, callApi, fmtVnd, printHtml } from '@shared'

const route = useRoute(); const router = useRouter()
const name = route.params.name
const { toast, ok, err } = useToast()
const doc = ref(null); const loading = ref(true); const activity = ref([]); const linked = ref({})

const items = computed(() => (doc.value?.items || []).map((l) => ({ item_code: l.item_code, item_name: l.item_name, qty: l.qty, uom: l.uom || l.stock_uom, rate: l.rate, amount: l.amount })))
const metaLine = computed(() => doc.value ? `Ngày ${fmtD(doc.value.transaction_date)}` : '')
function fmtD(v) { return v ? String(v).split(' ')[0].split('-').reverse().join('/') : '' }

async function load() {
  loading.value = true
  try {
    doc.value = await callApi('kinhdoanh.api.get_sales_order', { name }, 'GET')
    activity.value = await callApi('kinhdoanh.api.get_doc_activity', { doctype: 'Sales Order', name }, 'GET')
    if (doc.value?.docstatus === 1) linked.value = await callApi('kinhdoanh.api.get_so_status', { name }, 'GET')
  } catch (e) { err(e?.message) } finally { loading.value = false }
}
load()

async function act(method, okMsg) {
  try { await callApi('kinhdoanh.api.' + method, { name }); ok(okMsg); load() } catch (e) { err(e?.message || 'Lỗi') }
}
async function makeDoc(method, prefix) {
  try { const d = await callApi('kinhdoanh.api.' + method, { name }); ok('Đã tạo ' + d.name); router.push(prefix + d.name) } catch (e) { err(e?.message || 'Lỗi') }
}
async function doPrint() {
  try { const html = await callApi('kinhdoanh.api.print_sales_order', { name }, 'GET'); printHtml(html, name) } catch (e) { err(e?.message) }
}
</script>
