<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<PageHeader title="Bảo dưỡng tài sản" icon="check-circle" icon-class="text-sky-600">
  <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4"/> Ghi nhận bảo dưỡng</button>
</PageHeader>
<main class="flex-1 p-4 max-w-5xl mx-auto w-full">
<DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm TS / NV phụ trách…" :search-keys="['asset_name','assign_to_name','task_name']" :clickable="false">
  <template #col-completion_date="{ value }">{{ $fmtDate(value) }}</template>
  <template #col-maintenance_status="{ row }"><StatusBadge :status="row.maintenance_status||'Planned'" :tone="row.maintenance_status==='Completed'?'green':(row.maintenance_status==='Overdue'?'red':'blue')"/></template>
</DataTable>
</main>
<FormModal :show="show" title="Ghi nhận bảo dưỡng" icon="check-circle" width="max-w-md" :saving="saving" @close="show=false" @save="save">
  <div class="space-y-3">
    <div><label class="text-xs text-gray-500">Tài sản *</label><EntityPicker v-model="f.asset_name" api="taisan.api.get_assets" result-key="entries" value-key="name" label-key="asset_name"/></div>
    <div class="grid grid-cols-2 gap-3">
      <div><label class="text-xs text-gray-500">Loại</label><select v-model="f.maintenance_type" class="inp"><option>Scheduled</option><option>Unscheduled</option><option>Breakdown</option></select></div>
      <div><label class="text-xs text-gray-500">NV phụ trách</label><input v-model="f.assign_to_name" class="inp"/></div>
    </div>
    <div><label class="text-xs text-gray-500">Mô tả</label><textarea v-model="f.description" rows="2" class="inp"/></div>
  </div>
</FormModal>
<div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅')?'bg-emerald-50 text-emerald-800 border border-emerald-200':'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
</div>
</template>
<script setup>
import { ref,reactive } from 'vue'; import { FeatherIcon } from 'frappe-ui'
import { PageHeader,DataTable,FormModal,EntityPicker,StatusBadge,useToast,callApi } from '@shared'
const { toast,ok,err }=useToast(); const rows=ref([]); const loading=ref(false)
const columns=[{key:'asset_name',label:'Tài sản'},{key:'maintenance_type',label:'Loại'},{key:'completion_date',label:'Ngày'},{key:'assign_to_name',label:'Phụ trách'},{key:'maintenance_status',label:'Trạng thái'}]
async function reload(){loading.value=true;try{rows.value=(await callApi('taisan.api.get_maintenance_logs',{page_length:200},'GET'))?.entries||[]}finally{loading.value=false}};reload()
const show=ref(false); const saving=ref(false); const f=reactive({asset_name:'',maintenance_type:'Scheduled',assign_to_name:'',description:''})
function openCreate(){Object.assign(f,{asset_name:'',maintenance_type:'Scheduled',assign_to_name:'',description:''});show.value=true}
async function save(){if(!f.asset_name)return err('Chọn tài sản');saving.value=true;try{await callApi('taisan.api.create_maintenance_log',{...f});ok('Đã ghi nhận');show.value=false;reload()}catch(e){err(e?.message)}finally{saving.value=false}}
</script>
