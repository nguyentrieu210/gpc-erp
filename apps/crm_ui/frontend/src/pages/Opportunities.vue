<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Cơ hội bán hàng" icon="target" icon-class="text-amber-600">
      <button class="btn-secondary px-3 py-2 rounded-lg text-sm inline-flex items-center gap-1" @click="view = view === 'kanban' ? 'list' : 'kanban'"><FeatherIcon :name="view === 'kanban' ? 'list' : 'columns'" class="h-4 w-4" /> {{ view === 'kanban' ? 'Danh sách' : 'Kanban' }}</button>
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Thêm cơ hội</button>
    </PageHeader>
    <main class="flex-1 p-4 w-full">
      <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
      <Kanban v-else-if="view === 'kanban'" :columns="cols" :items="opps" group-key="status" @move="onMove" @card-click="goDetail">
        <template #card="{ item }">
          <div class="font-medium text-sm truncate">{{ item.title }}</div>
          <div class="text-xs text-gray-500 truncate">{{ item.party_name || '' }}</div>
          <div class="text-sm font-bold text-amber-600 mt-1">{{ fmtVnd(item.opportunity_amount) }}</div>
        </template>
      </Kanban>
      <DataTable v-else :rows="opps" :columns="columns" search-placeholder="Tìm cơ hội…" :search-keys="['title', 'party_name']" @row-click="goDetail">
        <template #col-opportunity_amount="{ value }"><span class="font-semibold">{{ fmtVnd(value) }}</span></template>
        <template #col-status="{ row }"><StatusBadge :status="row.stage_vi" /></template>
      </DataTable>
    </main>
    <FormModal :show="show" title="Thêm cơ hội" icon="target" width="max-w-md" :saving="saving" @close="show = false" @save="save">
      <div class="space-y-3">
        <div><label class="text-xs text-gray-500">Tiêu đề *</label><input v-model="f.title" class="inp" /></div>
        <div class="grid grid-cols-2 gap-3"><div><label class="text-xs text-gray-500">Giá trị</label><input v-model.number="f.opportunity_amount" type="number" class="inp" /></div><div><label class="text-xs text-gray-500">Dự kiến chốt</label><input v-model="f.expected_closing" type="date" class="inp" /></div></div>
      </div>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { PageHeader, Kanban, DataTable, FormModal, StatusBadge, useToast, callApi, fmtVnd } from '@shared'
const router = useRouter(); const { toast, ok, err } = useToast()
const view = ref('kanban'); const opps = ref([]); const loading = ref(false)
const cols = [
  { key: 'Open', label: 'Mở', color: 'blue' }, { key: 'Qualification', label: 'Đánh giá', color: 'indigo' },
  { key: 'Needs Analysis', label: 'Phân tích', color: 'amber' }, { key: 'Proposal', label: 'Đề xuất', color: 'orange' },
  { key: 'Negotiation', label: 'Đàm phán', color: 'purple' }, { key: 'Closed Won', label: 'Thắng', color: 'green' }, { key: 'Closed Lost', label: 'Thua', color: 'red' },
]
const columns = [{ key: 'title', label: 'Tiêu đề' }, { key: 'party_name', label: 'Đối tượng' }, { key: 'opportunity_amount', label: 'Giá trị', align: 'right' }, { key: 'status', label: 'Giai đoạn' }]
async function reload() { loading.value = true; try { opps.value = (await callApi('crm_ui.api.get_opportunities', { page_length: 500 }, 'GET'))?.entries || [] } finally { loading.value = false } }
reload()
async function onMove({ item, to }) { try { await callApi('crm_ui.api.move_opportunity_status', { name: item.name, status: to }); item.status = to; ok('Đã chuyển giai đoạn') } catch (e) { err(e?.message); reload() } }
function goDetail(row) { router.push('/opportunities/' + row.name) }
const show = ref(false); const saving = ref(false)
const f = reactive({ title: '', opportunity_amount: 0, expected_closing: '' })
function openCreate() { Object.assign(f, { title: '', opportunity_amount: 0, expected_closing: '' }); show.value = true }
async function save() { if (!f.title) return err('Nhập tiêu đề'); saving.value = true; try { await callApi('crm_ui.api.create_opportunity', { title: f.title, opportunity_amount: f.opportunity_amount, expected_closing: f.expected_closing || undefined }); ok('Đã thêm cơ hội'); show.value = false; reload() } catch (e) { err(e?.message) } finally { saving.value = false } }
</script>
