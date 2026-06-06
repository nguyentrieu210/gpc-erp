<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<PageHeader title="Điều chuyển tài sản" icon="repeat" icon-class="text-amber-600">
  <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4"/> Điều chuyển</button>
</PageHeader>
<main class="flex-1 p-4 max-w-5xl mx-auto w-full">
<DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm TS / vị trí…" :search-keys="['asset','source_location','target_location']" :clickable="false">
  <template #col-transaction_date="{ value }">{{ $fmtDate(value) }}</template>
</DataTable>
</main>
<FormModal :show="show" title="Điều chuyển tài sản" icon="repeat" width="max-w-md" :saving="saving" @close="show=false" @save="save">
  <div class="space-y-3">
    <div><label class="text-xs text-gray-500">Tài sản *</label><EntityPicker v-model="f.asset" api="taisan.api.get_assets" result-key="entries" value-key="name" label-key="asset_name" sub-key="location"/></div>
    <div><label class="text-xs text-gray-500">Đến vị trí *</label><EntityPicker v-model="f.target_location" api="taisan.api.get_locations" result-key="entries" value-key="name" label-key="location_name"/></div>
    <div><label class="text-xs text-gray-500">Ngày</label><input v-model="f.transaction_date" type="date" class="inp"/></div>
  </div>
</FormModal>
<div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅')?'bg-emerald-50 text-emerald-800 border border-emerald-200':'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
</div>
</template>
<script setup>
import { ref,reactive } from 'vue'; import { FeatherIcon } from 'frappe-ui'
import { PageHeader,DataTable,FormModal,EntityPicker,useToast,callApi,today } from '@shared'
const { toast,ok,err }=useToast(); const rows=ref([]); const loading=ref(false)
const columns=[{key:'name',label:'Số phiếu'},{key:'asset',label:'Tài sản'},{key:'transaction_date',label:'Ngày'},{key:'source_location',label:'Từ'},{key:'target_location',label:'Đến'}]
async function reload(){loading.value=true;try{rows.value=(await callApi('taisan.api.get_asset_movements',{page_length:200},'GET'))?.entries||[]}finally{loading.value=false}};reload()
const show=ref(false); const saving=ref(false); const f=reactive({asset:'',target_location:'',source_location:'',transaction_date:today()})
function openCreate(){Object.assign(f,{asset:'',target_location:'',transaction_date:today()});show.value=true}
async function save(){if(!f.asset||!f.target_location)return err('Chọn TS + vị trí đích');saving.value=true;try{await callApi('taisan.api.create_asset_movement',{...f});ok('Đã điều chuyển');show.value=false;reload()}catch(e){err(e?.message)}finally{saving.value=false}}
</script>
