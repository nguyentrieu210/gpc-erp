<template>
  <DetailLayout :loading="loading" :title="doc?.title || name" icon="target" icon-class="text-amber-600" back="/opportunities"
    :heading="doc?.title" :meta="doc?.party_name" :status="stageVi" :amount="fmtVnd(doc?.opportunity_amount)" amount-label="Giá trị" gradient="from-amber-500 to-orange-600">
    <template #actions>
      <button v-if="doc?.status !== 'Closed Won'" class="btn-success px-3 py-2 rounded-lg text-sm font-medium" @click="toCustomer">→ Thành khách hàng</button>
    </template>
    <div class="app-card p-4 space-y-1 text-sm">
      <div class="flex justify-between"><span class="text-gray-500">Đối tượng</span><span>{{ doc?.party_name || '—' }}</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Email</span><span>{{ doc?.contact_email || '—' }}</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Dự kiến chốt</span><span>{{ $fmtDate(doc?.expected_closing) }}</span></div>
      <div class="flex justify-between border-t pt-1 mt-1"><span class="text-gray-500">Giá trị</span><span class="font-bold">{{ fmtVnd(doc?.opportunity_amount) }}</span></div>
    </div>
    <div class="app-card p-4">
      <div class="flex items-center mb-2"><div class="text-sm font-semibold flex-1">Hoạt động</div><button class="btn-secondary px-2 py-1 rounded text-xs" @click="showAct = true">+ Thêm</button></div>
      <div v-for="a in activities" :key="a.name" class="flex items-center gap-2 py-1.5 text-sm border-b last:border-0">
        <input type="checkbox" :checked="a.status === 'Closed'" @change="toggle(a)" /><span class="flex-1" :class="a.status === 'Closed' ? 'line-through text-gray-400' : ''">{{ a.description }}</span><span class="text-xs text-gray-400">{{ $fmtDate(a.date) }}</span>
      </div>
      <div v-if="!activities.length" class="text-sm text-gray-400">Chưa có hoạt động</div>
    </div>
    <template #sidebar>
      <div class="app-card p-4">
        <div class="text-sm font-semibold mb-2">Giai đoạn</div>
        <select v-model="ns" @change="moveStage" class="inp"><option v-for="c in cols" :key="c.k" :value="c.k">{{ c.l }}</option></select>
      </div>
    </template>
    <FormModal :show="showAct" title="Thêm hoạt động" icon="check-square" width="max-w-md" :saving="savingAct" @close="showAct = false" @save="addAct">
      <div class="space-y-3"><div><label class="text-xs text-gray-500">Nội dung *</label><input v-model="actForm.description" class="inp" /></div><div><label class="text-xs text-gray-500">Ngày</label><input v-model="actForm.date" type="date" class="inp" /></div></div>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </DetailLayout>
</template>
<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DetailLayout, FormModal, useToast, callApi, fmtVnd, today } from '@shared'
const route = useRoute(); const router = useRouter(); const name = route.params.name
const { toast, ok, err } = useToast()
const doc = ref(null); const loading = ref(true); const activities = ref([]); const ns = ref('')
const cols = [{ k: 'Open', l: 'Mở' }, { k: 'Qualification', l: 'Đánh giá' }, { k: 'Needs Analysis', l: 'Phân tích' }, { k: 'Proposal', l: 'Đề xuất' }, { k: 'Negotiation', l: 'Đàm phán' }, { k: 'Closed Won', l: 'Thắng' }, { k: 'Closed Lost', l: 'Thua' }]
const stageVi = computed(() => (cols.find((c) => c.k === doc.value?.status) || {}).l || doc.value?.status)
async function load() {
  loading.value = true
  try {
    doc.value = await callApi('crm_ui.api.get_opportunity', { name }, 'GET'); ns.value = doc.value?.status
    activities.value = (await callApi('crm_ui.api.get_activities', { reference_doctype: 'Opportunity', reference_name: name }, 'GET'))?.entries || []
  } catch (e) { err(e?.message) } finally { loading.value = false }
}
load()
async function moveStage() { try { await callApi('crm_ui.api.move_opportunity_status', { name, status: ns.value }); ok('Đã đổi giai đoạn'); load() } catch (e) { err(e?.message) } }
async function toCustomer() { try { const r = await callApi('crm_ui.api.convert_opportunity_to_customer', { name }); ok('Đã tạo KH ' + r.customer); router.push('/customers/' + r.customer) } catch (e) { err(e?.message) } }
const showAct = ref(false); const savingAct = ref(false); const actForm = reactive({ description: '', date: today() })
async function addAct() { if (!actForm.description) return err('Nhập nội dung'); savingAct.value = true; try { await callApi('crm_ui.api.create_activity', { description: actForm.description, date: actForm.date, reference_doctype: 'Opportunity', reference_name: name }); ok('Đã thêm'); showAct.value = false; actForm.description = ''; load() } catch (e) { err(e?.message) } finally { savingAct.value = false } }
async function toggle(a) { try { await callApi('crm_ui.api.complete_activity', { name: a.name, reopen: a.status === 'Closed' ? 1 : 0 }); load() } catch (e) { err(e?.message) } }
</script>
