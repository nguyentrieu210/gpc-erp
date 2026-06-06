<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Liên hệ" icon="phone" icon-class="text-cyan-600">
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Thêm liên hệ</button>
    </PageHeader>
    <main class="flex-1 p-4 max-w-5xl mx-auto w-full">
      <DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm liên hệ…" :search-keys="['first_name', 'email_id', 'mobile_no', 'company_name']" :clickable="false">
        <template #col-first_name="{ row }"><div class="flex items-center gap-2"><Avatar :name="(row.first_name || '') + ' ' + (row.last_name || '')" :size="30" /><div><div class="font-medium">{{ row.first_name }} {{ row.last_name || '' }}</div><div class="text-xs text-gray-500">{{ row.designation || '' }}</div></div></div></template>
      </DataTable>
    </main>
    <FormModal :show="show" title="Thêm liên hệ" icon="user-plus" width="max-w-md" :saving="saving" @close="show = false" @save="save">
      <div class="space-y-3">
        <div class="grid grid-cols-2 gap-3"><div><label class="text-xs text-gray-500">Họ tên *</label><input v-model="f.first_name" class="inp" /></div><div><label class="text-xs text-gray-500">Chức danh</label><input v-model="f.designation" class="inp" /></div></div>
        <div class="grid grid-cols-2 gap-3"><div><label class="text-xs text-gray-500">Email</label><input v-model="f.email" class="inp" /></div><div><label class="text-xs text-gray-500">SĐT</label><input v-model="f.mobile" class="inp" /></div></div>
        <div><label class="text-xs text-gray-500">Công ty</label><input v-model="f.company_name" class="inp" /></div>
      </div>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { PageHeader, DataTable, FormModal, Avatar, useToast, callApi } from '@shared'
const { toast, ok, err } = useToast()
const rows = ref([]); const loading = ref(false)
const columns = [{ key: 'first_name', label: 'Họ tên' }, { key: 'email_id', label: 'Email' }, { key: 'mobile_no', label: 'SĐT' }, { key: 'company_name', label: 'Công ty' }]
async function reload() { loading.value = true; try { rows.value = (await callApi('crm_ui.api.get_contacts', { page_length: 300 }, 'GET'))?.entries || [] } finally { loading.value = false } }
reload()
const show = ref(false); const saving = ref(false)
const f = reactive({ first_name: '', last_name: '', email: '', mobile: '', company_name: '', designation: '' })
function openCreate() { Object.assign(f, { first_name: '', last_name: '', email: '', mobile: '', company_name: '', designation: '' }); show.value = true }
async function save() { if (!f.first_name) return err('Nhập họ tên'); saving.value = true; try { await callApi('crm_ui.api.create_contact', { ...f }); ok('Đã thêm liên hệ'); show.value = false; reload() } catch (e) { err(e?.message) } finally { saving.value = false } }
</script>
