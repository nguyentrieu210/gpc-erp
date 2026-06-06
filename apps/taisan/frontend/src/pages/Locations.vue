<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<PageHeader title="Vị trí tài sản" icon="map-pin" icon-class="text-emerald-600">
  <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4"/> Thêm vị trí</button>
</PageHeader>
<main class="flex-1 p-4 max-w-4xl mx-auto w-full">
<div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else class="space-y-1">
  <div v-for="l in locs" :key="l.name" class="app-card p-4 flex items-center gap-3">
    <div class="h-10 w-10 rounded-lg text-emerald-700 flex items-center justify-center" :class="l.is_group?'bg-emerald-200':'bg-emerald-100'"><FeatherIcon :name="l.is_group?'folder':'map-pin'" class="h-5 w-5"/></div>
    <div class="flex-1"><div class="font-semibold">{{ l.location_name }}</div><div class="text-xs text-gray-500">{{ l.is_group?'Nhóm':'Vị trí' }} · {{ l.asset_count||0 }} tài sản</div></div>
  </div>
  <div v-if="!locs.length" class="text-sm text-gray-400 text-center py-10">Chưa có vị trí</div>
</div>
</main>
<FormModal :show="show" title="Thêm vị trí" icon="map-pin" width="max-w-sm" :saving="saving" @close="show=false" @save="save">
  <div class="space-y-3">
    <div><label class="text-xs text-gray-500">Tên vị trí *</label><input v-model="f.location_name" class="inp"/></div>
  </div>
</FormModal>
<div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅')?'bg-emerald-50 text-emerald-800 border border-emerald-200':'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
</div>
</template>
<script setup>
import { ref,reactive } from 'vue'; import { FeatherIcon,LoadingIndicator } from 'frappe-ui'
import { PageHeader,FormModal,useToast,callApi } from '@shared'
const { toast,ok,err }=useToast(); const locs=ref([]); const loading=ref(false)
async function reload(){loading.value=true;try{locs.value=(await callApi('taisan.api.get_locations',{page_length:200},'GET'))?.entries||[]}finally{loading.value=false}};reload()
const show=ref(false); const saving=ref(false); const f=reactive({location_name:''})
function openCreate(){f.location_name='';show.value=true}
async function save(){if(!f.location_name)return err('Nhập tên vị trí');saving.value=true;try{await callApi('taisan.api.create_location',{...f});ok('Đã thêm vị trí');show.value=false;reload()}catch(e){err(e?.message)}finally{saving.value=false}}
</script>
