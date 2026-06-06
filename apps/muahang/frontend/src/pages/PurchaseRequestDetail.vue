<template>
  <DetailLayout :loading="loading" :title="name" icon="edit-3" icon-class="text-amber-600" back="/purchase-requests"
    :heading="'Đề nghị mua'" :status="statusText" gradient="from-amber-500 to-orange-600">
    <template #actions>
      <button v-if="doc?.docstatus === 0" class="btn-success px-3 py-2 rounded-lg text-sm font-medium" @click="act('submit_purchase_request','Đã gửi đề nghị')">Gửi duyệt</button>
      <button v-if="doc?.docstatus === 1 && doc.per_ordered < 100" class="btn-primary px-3 py-2 rounded-lg text-sm font-medium" @click="toPO">→ Tạo đơn mua</button>
    </template>
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Hàng đề nghị</div>
      <table class="w-full text-sm">
        <thead><tr><th class="px-2 py-1 text-left">Mặt hàng</th><th class="px-2 py-1 text-right">SL</th><th class="px-2 py-1 text-left">Ngày cần</th></tr></thead>
        <tbody>
          <tr v-for="(it, i) in doc?.items || []" :key="i"><td class="px-2 py-1.5">{{ it.item_name || it.item_code }}</td><td class="px-2 py-1.5 text-right">{{ it.qty }} {{ it.uom || it.stock_uom }}</td><td class="px-2 py-1.5">{{ $fmtDate(it.schedule_date) }}</td></tr>
        </tbody>
      </table>
    </div>
    <template #sidebar>
      <div class="app-card p-4 space-y-1 text-sm">
        <div class="flex justify-between"><span class="text-gray-500">Ngày tạo</span><span>{{ $fmtDate(doc?.transaction_date) }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Đã đặt</span><span>{{ Math.round(doc?.per_ordered || 0) }}%</span></div>
      </div>
      <div class="app-card p-4"><div class="text-sm font-semibold mb-2">Hoạt động</div><ActivityTimeline :items="activity" /></div>
    </template>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </DetailLayout>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DetailLayout, ActivityTimeline, useToast, callApi } from '@shared'
const route = useRoute(); const router = useRouter(); const name = route.params.id || route.params.name
const { toast, ok, err } = useToast()
const doc = ref(null); const loading = ref(true); const activity = ref([])
const statusText = computed(() => doc.value?.docstatus === 1 ? (doc.value.per_ordered >= 100 ? 'Đã đặt đủ' : 'Đã duyệt') : 'Nháp')
async function load() { loading.value = true; try { doc.value = await callApi('muahang.api.get_purchase_request', { name }, 'GET'); activity.value = await callApi('muahang.api.get_doc_activity', { doctype: 'Material Request', name }, 'GET') } catch (e) { err(e?.message) } finally { loading.value = false } }
load()
async function act(m, msg) { try { await callApi('muahang.api.' + m, { name }); ok(msg); load() } catch (e) { err(e?.message) } }
async function toPO() { try { const po = await callApi('muahang.api.make_po_from_request', { name, submit: 0 }); ok('Đã tạo PO ' + po.name); router.push('/po/' + po.name) } catch (e) { err(e?.message) } }
</script>
