<template>
  <DetailLayout :loading="loading" :title="name" icon="file-text" icon-class="text-amber-600" back="/quotations"
    :heading="doc?.customer_name" :status="doc?.status" :amount="fmtVnd(doc?.grand_total)" gradient="from-amber-500 to-orange-600">
    <template #actions>
      <button v-if="doc?.docstatus === 0" class="btn-success px-3 py-2 rounded-lg text-sm font-medium" @click="act('submit_quotation','Đã gửi báo giá')">Gửi báo giá</button>
      <button v-if="doc?.docstatus === 1" class="btn-primary px-3 py-2 rounded-lg text-sm font-medium" @click="toSO">→ Tạo đơn bán</button>
      <button class="btn-secondary px-3 py-2 rounded-lg text-sm inline-flex items-center gap-1" @click="doPrint"><FeatherIcon name="printer" class="h-4 w-4" /> In</button>
    </template>
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Dòng hàng</div>
      <LineItemsEditor :model-value="items" :editable="false" />
    </div>
    <template #sidebar>
      <div class="app-card p-4 space-y-1 text-sm">
        <div class="flex justify-between"><span class="text-gray-500">Khách hàng</span><span class="font-medium">{{ doc?.customer_name }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Ngày BG</span><span>{{ $fmtDate(doc?.transaction_date) }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Hiệu lực đến</span><span>{{ $fmtDate(doc?.valid_till) }}</span></div>
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
async function load() { loading.value = true; try { doc.value = await callApi('kinhdoanh.api.get_quotation', { name }, 'GET'); activity.value = await callApi('kinhdoanh.api.get_doc_activity', { doctype: 'Quotation', name }, 'GET') } catch (e) { err(e?.message) } finally { loading.value = false } }
load()
async function act(m, msg) { try { await callApi('kinhdoanh.api.' + m, { name }); ok(msg); load() } catch (e) { err(e?.message) } }
async function toSO() { try { const so = await callApi('kinhdoanh.api.make_sales_order_from_quotation', { name }); ok('Đã tạo ' + so.name); router.push('/sales-orders/' + so.name) } catch (e) { err(e?.message) } }
async function doPrint() { try { const html = await callApi('kinhdoanh.api.print_quotation', { name }, 'GET'); printHtml(html, name) } catch (e) { err(e?.message) } }
</script>
