<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Chiến dịch Marketing" icon="flag" icon-class="text-violet-600">
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Thêm chiến dịch</button>
    </PageHeader>
    <main class="flex-1 p-4 max-w-4xl mx-auto w-full">
      <DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm chiến dịch…" :search-keys="['campaign_name']" :clickable="false">
        <template #col-lead_count="{ value }"><span class="font-medium">{{ value }} lead</span></template>
      </DataTable>
    </main>
    <FormModal :show="show" title="Thêm chiến dịch" icon="flag" width="max-w-md" :saving="saving" @close="show = false" @save="save">
      <div class="space-y-3">
        <div><label class="text-xs text-gray-500">Tên chiến dịch *</label><input v-model="f.campaign_name" class="inp" /></div>
        <div><label class="text-xs text-gray-500">Mô tả</label><textarea v-model="f.description" rows="3" class="inp" /></div>
      </div>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { PageHeader, DataTable, FormModal, useToast, callApi } from '@shared'
const { toast, ok, err } = useToast()
const rows = ref([]); const loading = ref(false)
const columns = [{ key: 'campaign_name', label: 'Chiến dịch' }, { key: 'lead_count', label: 'Số lead', align: 'right' }]
async function reload() { loading.value = true; try { rows.value = (await callApi('crm_ui.api.get_campaigns', { page_length: 200 }, 'GET'))?.entries || [] } finally { loading.value = false } }
reload()
const show = ref(false); const saving = ref(false)
const f = reactive({ campaign_name: '', description: '' })
function openCreate() { Object.assign(f, { campaign_name: '', description: '' }); show.value = true }
async function save() { if (!f.campaign_name) return err('Nhập tên chiến dịch'); saving.value = true; try { await callApi('crm_ui.api.create_campaign', { ...f }); ok('Đã thêm chiến dịch'); show.value = false; reload() } catch (e) { err(e?.message) } finally { saving.value = false } }
</script>
