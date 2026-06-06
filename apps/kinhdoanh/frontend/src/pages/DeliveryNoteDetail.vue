<template>
  <DetailLayout :loading="loading" :title="name" icon="truck" icon-class="text-emerald-600" back="/delivery-notes"
    :heading="doc?.customer_name" :status="statusText" :amount="fmtVnd(doc?.grand_total)" gradient="from-emerald-600 to-teal-600">
    <template #actions>
      <template v-if="doc?.docstatus === 0">
        <button class="btn-success px-3 py-2 rounded-lg text-sm font-medium" @click="act('submit_delivery_note','Đã xuất giao')">Xuất giao</button>
        <button class="btn-danger px-3 py-2 rounded-lg text-sm" @click="act('cancel_delivery_note','Đã hủy')">Hủy</button>
      </template>
      <template v-else-if="doc?.docstatus === 1">
        <button v-if="!doc.is_return" class="btn-primary px-3 py-2 rounded-lg text-sm font-medium" :disabled="doc.per_billed >= 100" @click="makeDoc('make_sales_invoice_from_dn','/sales-invoices/')">Tạo hóa đơn</button>
        <button v-if="!doc.is_return" class="btn-warning px-3 py-2 rounded-lg text-sm" @click="doReturn">Trả hàng</button>
      </template>
      <button class="btn-secondary px-3 py-2 rounded-lg text-sm inline-flex items-center gap-1" @click="doPrint"><FeatherIcon name="printer" class="h-4 w-4" /> In</button>
    </template>
    <div class="app-card p-4"><div class="text-sm font-semibold mb-2">Dòng hàng</div><LineItemsEditor :model-value="items" :editable="false" /></div>
    <template #sidebar>
      <div class="app-card p-4 space-y-1 text-sm">
        <div class="flex justify-between"><span class="text-gray-500">Khách hàng</span><span class="font-medium">{{ doc?.customer_name }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Ngày xuất</span><span>{{ $fmtDate(doc?.posting_date) }}</span></div>
        <div v-if="doc?.is_return" class="flex justify-between"><span class="text-gray-500">Loại</span><span class="text-rose-600 font-medium">Phiếu trả hàng</span></div>
        <div class="flex justify-between border-t pt-1 mt-1"><span class="text-gray-500">Tổng tiền</span><span class="font-bold">{{ fmtVnd(doc?.grand_total) }}</span></div>
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
const doc = ref(null); const loading = ref(true); const activity = ref([])
const items = computed(() => (doc.value?.items || []).map((l) => ({ item_code: l.item_code, item_name: l.item_name, qty: l.qty, uom: l.uom || l.stock_uom, rate: l.rate, amount: l.amount })))
const statusText = computed(() => doc.value?.docstatus === 1 ? (doc.value.is_return ? 'Đã trả hàng' : 'Đã xuất giao') : 'Nháp')
async function load() { loading.value = true; try { doc.value = await callApi('kinhdoanh.api.get_delivery_note', { name }, 'GET'); activity.value = await callApi('kinhdoanh.api.get_doc_activity', { doctype: 'Delivery Note', name }, 'GET') } catch (e) { err(e?.message) } finally { loading.value = false } }
load()
async function act(m, msg) { try { await callApi('kinhdoanh.api.' + m, { name }); ok(msg); load() } catch (e) { err(e?.message) } }
async function makeDoc(m, prefix) { try { const d = await callApi('kinhdoanh.api.' + m, { name }); ok('Đã tạo ' + d.name); router.push(prefix + d.name) } catch (e) { err(e?.message) } }
async function doReturn() { try { const r = await callApi('kinhdoanh.api.make_sales_return', { delivery_note_name: name, submit: 1 }); ok('Đã tạo phiếu trả ' + r.name); router.push('/delivery-notes/' + r.name) } catch (e) { err(e?.message) } }
async function doPrint() { try { const html = await callApi('kinhdoanh.api.print_delivery_note', { name }, 'GET'); printHtml(html, name) } catch (e) { err(e?.message) } }
</script>
