<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Hoạt động / Việc cần làm" icon="check-square" icon-class="text-rose-600">
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Thêm việc</button>
    </PageHeader>
    <main class="flex-1 p-4 max-w-4xl mx-auto w-full space-y-3">
      <div class="flex gap-1">
        <button v-for="s in tabs" :key="s.k" class="text-xs px-3 py-1.5 rounded-full" :class="status === s.k ? 'bg-indigo-600 text-white' : 'bg-gray-100'" @click="status = s.k; reload()">{{ s.l }}</button>
      </div>
      <div class="app-card divide-y">
        <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
        <div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Không có hoạt động</div>
        <div v-for="a in rows" :key="a.name" class="flex items-center gap-3 px-4 py-2.5">
          <input type="checkbox" :checked="a.status === 'Closed'" @change="toggle(a)" />
          <div class="flex-1 min-w-0">
            <div class="text-sm" :class="a.status === 'Closed' ? 'line-through text-gray-400' : ''">{{ a.description }}</div>
            <div class="text-xs text-gray-400">{{ a.reference_type ? a.reference_type + ': ' + a.reference_name : '' }}</div>
          </div>
          <span class="text-xs px-2 py-0.5 rounded-full" :class="prio(a.priority)">{{ a.priority }}</span>
          <span class="text-xs text-gray-500">{{ $fmtDate(a.date) }}</span>
        </div>
      </div>
    </main>
    <FormModal :show="show" title="Thêm việc cần làm" icon="check-square" width="max-w-md" :saving="saving" @close="show = false" @save="save">
      <div class="space-y-3">
        <div><label class="text-xs text-gray-500">Nội dung *</label><input v-model="f.description" class="inp" /></div>
        <div class="grid grid-cols-2 gap-3"><div><label class="text-xs text-gray-500">Ngày</label><input v-model="f.date" type="date" class="inp" /></div><div><label class="text-xs text-gray-500">Ưu tiên</label><select v-model="f.priority" class="inp"><option>Low</option><option>Medium</option><option>High</option></select></div></div>
      </div>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { PageHeader, FormModal, useToast, callApi, today } from '@shared'
const { toast, ok, err } = useToast()
const rows = ref([]); const loading = ref(false); const status = ref('Open')
const tabs = [{ k: 'Open', l: 'Đang mở' }, { k: 'Closed', l: 'Hoàn thành' }, { k: '', l: 'Tất cả' }]
async function reload() { loading.value = true; try { rows.value = (await callApi('crm_ui.api.get_activities', { status: status.value || undefined, page_length: 300 }, 'GET'))?.entries || [] } finally { loading.value = false } }
reload()
async function toggle(a) { try { await callApi('crm_ui.api.complete_activity', { name: a.name, reopen: a.status === 'Closed' ? 1 : 0 }); reload() } catch (e) { err(e?.message) } }
const show = ref(false); const saving = ref(false)
const f = reactive({ description: '', date: today(), priority: 'Medium' })
function openCreate() { Object.assign(f, { description: '', date: today(), priority: 'Medium' }); show.value = true }
async function save() { if (!f.description) return err('Nhập nội dung'); saving.value = true; try { await callApi('crm_ui.api.create_activity', { ...f }); ok('Đã thêm'); show.value = false; reload() } catch (e) { err(e?.message) } finally { saving.value = false } }
function prio(p) { return { High: 'bg-rose-100 text-rose-700', Medium: 'bg-amber-100 text-amber-700', Low: 'bg-gray-100 text-gray-600' }[p] || 'bg-gray-100' }
</script>
