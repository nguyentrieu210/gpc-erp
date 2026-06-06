<template>
  <DetailLayout :loading="loading" :title="doc?.lead_name || name" icon="user-plus" icon-class="text-indigo-600" back="/leads"
    :heading="doc?.lead_name" :meta="doc?.company_name" :status="statusVi" gradient="from-indigo-600 to-blue-600">
    <template #actions>
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium" @click="toOpp">→ Tạo cơ hội</button>
    </template>
    <div class="app-card p-4 space-y-1 text-sm">
      <div class="flex justify-between"><span class="text-gray-500">Email</span><span>{{ doc?.email_id || '—' }}</span></div>
      <div class="flex justify-between"><span class="text-gray-500">SĐT</span><span>{{ doc?.mobile_no || '—' }}</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Công ty</span><span>{{ doc?.company_name || '—' }}</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Khu vực</span><span>{{ doc?.territory || '—' }}</span></div>
    </div>
    <div class="app-card p-4">
      <div class="flex items-center mb-2"><div class="text-sm font-semibold flex-1">Hoạt động / theo dõi</div><button class="btn-secondary px-2 py-1 rounded text-xs" @click="showAct = true">+ Thêm</button></div>
      <div v-for="a in activities" :key="a.name" class="flex items-center gap-2 py-1.5 text-sm border-b last:border-0">
        <input type="checkbox" :checked="a.status === 'Closed'" @change="toggle(a)" />
        <span class="flex-1" :class="a.status === 'Closed' ? 'line-through text-gray-400' : ''">{{ a.description }}</span>
        <span class="text-xs text-gray-400">{{ $fmtDate(a.date) }}</span>
      </div>
      <div v-if="!activities.length" class="text-sm text-gray-400">Chưa có hoạt động</div>
    </div>
    <template #sidebar>
      <div class="app-card p-4">
        <div class="text-sm font-semibold mb-2">Chuyển trạng thái</div>
        <select v-model="ns" @change="moveStatus" class="inp"><option v-for="c in cols" :key="c.k" :value="c.k">{{ c.l }}</option></select>
      </div>
      <div class="app-card p-4"><div class="text-sm font-semibold mb-2">Nhật ký</div><ActivityTimeline :items="log" /></div>
    </template>
    <FormModal :show="showAct" title="Thêm hoạt động" icon="check-square" width="max-w-md" :saving="savingAct" @close="showAct = false" @save="addAct">
      <div class="space-y-3">
        <div><label class="text-xs text-gray-500">Nội dung *</label><input v-model="actForm.description" class="inp" placeholder="Gọi điện / gửi email / hẹn gặp…" /></div>
        <div><label class="text-xs text-gray-500">Ngày</label><input v-model="actForm.date" type="date" class="inp" /></div>
      </div>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </DetailLayout>
</template>
<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DetailLayout, FormModal, ActivityTimeline, useToast, callApi, today } from '@shared'
const route = useRoute(); const router = useRouter(); const name = route.params.name
const { toast, ok, err } = useToast()
const doc = ref(null); const loading = ref(true); const activities = ref([]); const log = ref([]); const ns = ref('')
const cols = [{ k: 'Lead', l: 'Mới' }, { k: 'Open', l: 'Mở' }, { k: 'Replied', l: 'Đã liên hệ' }, { k: 'Opportunity', l: 'Cơ hội' }, { k: 'Quotation', l: 'Báo giá' }, { k: 'Interested', l: 'Quan tâm' }, { k: 'Converted', l: 'Đã chuyển' }, { k: 'Do Not Contact', l: 'Không liên hệ' }]
const statusVi = computed(() => (cols.find((c) => c.k === doc.value?.status) || {}).l || doc.value?.status)
async function load() {
  loading.value = true
  try {
    doc.value = await callApi('crm_ui.api.get_lead', { name }, 'GET'); ns.value = doc.value?.status
    activities.value = (await callApi('crm_ui.api.get_activities', { reference_doctype: 'Lead', reference_name: name }, 'GET'))?.entries || []
    log.value = await callApi('crm_ui.api.get_doc_activity', { doctype: 'Lead', name }, 'GET')
  } catch (e) { err(e?.message) } finally { loading.value = false }
}
load()
async function moveStatus() { try { await callApi('crm_ui.api.move_lead_status', { name, status: ns.value }); ok('Đã đổi trạng thái'); load() } catch (e) { err(e?.message) } }
async function toOpp() { try { const o = await callApi('crm_ui.api.convert_lead_to_opportunity', { name }); ok('Đã tạo cơ hội ' + o.name); router.push('/opportunities/' + o.name) } catch (e) { err(e?.message) } }
const showAct = ref(false); const savingAct = ref(false); const actForm = reactive({ description: '', date: today() })
async function addAct() { if (!actForm.description) return err('Nhập nội dung'); savingAct.value = true; try { await callApi('crm_ui.api.create_activity', { description: actForm.description, date: actForm.date, reference_doctype: 'Lead', reference_name: name }); ok('Đã thêm'); showAct.value = false; actForm.description = ''; load() } catch (e) { err(e?.message) } finally { savingAct.value = false } }
async function toggle(a) { try { await callApi('crm_ui.api.complete_activity', { name: a.name, reopen: a.status === 'Closed' ? 1 : 0 }); load() } catch (e) { err(e?.message) } }
</script>
