<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Lead (Tiềm năng)" icon="user-plus" icon-class="text-indigo-600">
      <button class="btn-secondary px-3 py-2 rounded-lg text-sm inline-flex items-center gap-1" @click="view = view === 'kanban' ? 'list' : 'kanban'">
        <FeatherIcon :name="view === 'kanban' ? 'list' : 'columns'" class="h-4 w-4" /> {{ view === 'kanban' ? 'Danh sách' : 'Kanban' }}
      </button>
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Thêm lead</button>
    </PageHeader>
    <main class="flex-1 p-4 max-w-full mx-auto w-full">
      <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
      <Kanban v-else-if="view === 'kanban'" :columns="cols" :items="leads" group-key="status" @move="onMove" @card-click="goDetail">
        <template #card="{ item }">
          <div class="font-medium text-sm truncate">{{ item.lead_name }}</div>
          <div class="text-xs text-gray-500 truncate">{{ item.company_name || '' }}</div>
          <div class="text-xs text-gray-400 mt-1 truncate">{{ item.email_id || item.mobile_no || '' }}</div>
        </template>
      </Kanban>
      <DataTable v-else :rows="leads" :columns="columns" search-placeholder="Tìm lead…" :search-keys="['lead_name', 'email_id', 'mobile_no', 'company_name']" @row-click="goDetail">
        <template #col-status="{ row }"><StatusBadge :status="row.status_vi" /></template>
      </DataTable>
    </main>
    <FormModal :show="show" title="Thêm lead" icon="user-plus" width="max-w-md" :saving="saving" @close="show = false" @save="save">
      <div class="space-y-3">
        <div><label class="text-xs text-gray-500">Tên *</label><input v-model="f.lead_name" class="inp" /></div>
        <div class="grid grid-cols-2 gap-3"><div><label class="text-xs text-gray-500">Email</label><input v-model="f.email" class="inp" /></div><div><label class="text-xs text-gray-500">SĐT</label><input v-model="f.mobile" class="inp" /></div></div>
        <div><label class="text-xs text-gray-500">Công ty</label><input v-model="f.company_name" class="inp" /></div>
      </div>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { PageHeader, Kanban, DataTable, FormModal, StatusBadge, useToast, callApi } from '@shared'
const router = useRouter(); const { toast, ok, err } = useToast()
const view = ref('kanban'); const leads = ref([]); const loading = ref(false)
const cols = [
  { key: 'Lead', label: 'Mới', color: 'blue' }, { key: 'Open', label: 'Mở', color: 'indigo' },
  { key: 'Replied', label: 'Đã liên hệ', color: 'amber' }, { key: 'Opportunity', label: 'Cơ hội', color: 'purple' },
  { key: 'Quotation', label: 'Báo giá', color: 'orange' }, { key: 'Interested', label: 'Quan tâm', color: 'green' },
  { key: 'Converted', label: 'Đã chuyển', color: 'green' },
]
const columns = [{ key: 'lead_name', label: 'Tên' }, { key: 'company_name', label: 'Công ty' }, { key: 'email_id', label: 'Email' }, { key: 'mobile_no', label: 'SĐT' }, { key: 'status', label: 'Trạng thái' }]
async function reload() { loading.value = true; try { leads.value = (await callApi('crm_ui.api.get_leads', { page_length: 500 }, 'GET'))?.entries || [] } finally { loading.value = false } }
reload()
async function onMove({ item, to }) { try { await callApi('crm_ui.api.move_lead_status', { name: item.name, status: to }); item.status = to; ok('Đã chuyển trạng thái') } catch (e) { err(e?.message); reload() } }
function goDetail(row) { router.push('/leads/' + row.name) }
const show = ref(false); const saving = ref(false)
const f = reactive({ lead_name: '', email: '', mobile: '', company_name: '' })
function openCreate() { Object.assign(f, { lead_name: '', email: '', mobile: '', company_name: '' }); show.value = true }
async function save() { if (!f.lead_name) return err('Nhập tên lead'); saving.value = true; try { await callApi('crm_ui.api.create_lead', { ...f }); ok('Đã thêm lead'); show.value = false; reload() } catch (e) { err(e?.message) } finally { saving.value = false } }
</script>
