<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<PageHeader title="Sửa chữa tài sản" icon="alert-triangle" icon-class="text-rose-600">
  <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4"/> Ghi nhận sửa chữa</button>
</PageHeader>
<main class="flex-1 p-4 max-w-5xl mx-auto w-full">
<DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm TS…" :search-keys="['asset','asset_name','description']" :clickable="false">
  <template #col-failure_date="{ value }">{{ $fmtDate(value) }}</template>
  <template #col-repair_cost="{ value }"><span class="font-semibold">{{ fmtVnd(value) }}</span></template>
  <template #col-repair_status="{ row }"><StatusBadge :status="row.repair_status||'Pending'" :tone="row.repair_status==='Completed'?'green':'amber'"/></template>
</DataTable>
</main>
<FormModal :show="show" title="Ghi nhận sửa chữa" icon="tool" width="max-w-md" :saving="saving" @close="show=false" @save="save">
  <div class="space-y-3">
    <div><label class="text-xs text-gray-500">Tài sản *</label><EntityPicker v-model="f.asset" api="taisan.api.get_assets" result-key="entries" value-key="name" label-key="asset_name"/></div>
    <div class="grid grid-cols-2 gap-3">
      <div><label class="text-xs text-gray-500">Ngày hỏng</label><input v-model="f.failure_date" type="date" class="inp"/></div>
      <div><label class="text-xs text-gray-500">Chi phí sửa chữa</label><input v-model.number="f.repair_cost" type="number" class="inp"/></div>
    </div>
    <div><label class="text-xs text-gray-500">Mô tả</label><textarea v-model="f.description" rows="2" class="inp"/></div>
  </div>
</FormModal>
<div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅')?'bg-emerald-50 text-emerald-800 border border-emerald-200':'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
</div>
</template>
<script setup>
import { ref,reactive } from 'vue'; import { FeatherIcon } from 'frappe-ui'
import { PageHeader,DataTable,FormModal,EntityPicker,StatusBadge,useToast,callApi,fmtVnd,today } from '@shared'
const { toast,ok,err }=useToast(); const rows=ref([]); const loading=ref(false)
const columns=[{key:'asset_name',label:'Tài sản'},{key:'failure_date',label:'Ngày hỏng'},{key:'repair_cost',label:'Chi phí',align:'right'},{key:'repair_status',label:'Trạng thái'},{key:'description',label:'Mô tả'}]
async function reload(){loading.value=true;try{rows.value=(await callApi('taisan.api.get_asset_repairs',{page_length:200},'GET'))?.entries||[]}finally{loading.value=false}};reload()
const show=ref(false); const saving=ref(false); const f=reactive({asset:'',asset_name:'',failure_date:today(),repair_cost:0,description:''})
async function onPickAsset(r){if(r){f.asset=r.name;f.asset_name=r.asset_name}}
function openCreate(){Object.assign(f,{asset:'',asset_name:'',failure_date:today(),repair_cost:0,description:''});show.value=true}
async function save(){if(!f.asset)return err('Chọn tài sản');saving.value=true;try{await callApi('taisan.api.create_asset_repair',{...f});ok('Đã ghi nhận');show.value=false;reload()}catch(e){err(e?.message)}finally{saving.value=false}}
</script>
