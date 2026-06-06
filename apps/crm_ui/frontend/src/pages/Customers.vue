<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Khách hàng" icon="users" icon-class="text-emerald-600">
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Thêm KH</button>
    </PageHeader>
    <main class="flex-1 p-4 max-w-5xl mx-auto w-full">
      <DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm KH…" :search-keys="['name', 'customer_name', 'tax_id']" @row-click="goDetail">
        <template #col-customer_name="{ row }"><div class="flex items-center gap-2"><Avatar :name="row.customer_name" :size="30" /><div><div class="font-medium">{{ row.customer_name }}</div><div class="text-xs text-gray-500">{{ row.customer_group }}</div></div></div></template>
        <template #col-tax_id="{ value }">{{ value || '—' }}</template>
      </DataTable>
    </main>
    <FormModal :show="show" title="Thêm khách hàng" icon="user-plus" width="max-w-md" :saving="saving" @close="show = false" @save="save">
      <div class="space-y-3">
        <div><label class="text-xs text-gray-500">Tên *</label><input v-model="f.customer_name" class="inp" /></div>
        <div class="grid grid-cols-2 gap-3"><div><label class="text-xs text-gray-500">MST</label><input v-model="f.tax_id" class="inp" /></div><div><label class="text-xs text-gray-500">SĐT</label><input v-model="f.mobile" class="inp" /></div></div>
      </div>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import { PageHeader, DataTable, FormModal, Avatar, useToast, callApi } from '@shared'
const router = useRouter(); const { toast, ok, err } = useToast()
const rows = ref([]); const loading = ref(false)
const columns = [{ key: 'customer_name', label: 'Khách hàng' }, { key: 'customer_type', label: 'Loại' }, { key: 'tax_id', label: 'MST' }, { key: 'territory', label: 'Khu vực' }]
async function reload() { loading.value = true; try { rows.value = (await callApi('crm_ui.api.get_customers', { page_length: 300 }, 'GET'))?.entries || [] } finally { loading.value = false } }
reload()
const show = ref(false); const saving = ref(false)
const f = reactive({ customer_name: '', customer_type: 'Company', customer_group: 'Commercial', tax_id: '', mobile: '' })
function openCreate() { Object.assign(f, { customer_name: '', tax_id: '', mobile: '' }); show.value = true }
async function save() { if (!f.customer_name) return err('Nhập tên KH'); saving.value = true; try { await callApi('crm_ui.api.create_customer', { ...f }); ok('Đã thêm KH'); show.value = false; reload() } catch (e) { err(e?.message) } finally { saving.value = false } }
function goDetail(row) { router.push('/customers/' + row.name) }
</script>
