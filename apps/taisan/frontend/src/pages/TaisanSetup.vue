<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<PageHeader title="Cấu hình Tài sản" icon="settings" icon-class="text-gray-600"/>
<main class="flex-1 p-4 max-w-lg mx-auto w-full space-y-4">
  <div class="app-card p-4">
    <div class="text-sm font-semibold mb-2">Trạng thái</div>
    <div class="space-y-1 text-sm">
      <div class="flex justify-between"><span class="text-gray-500">Công ty</span><span>{{ s?.company }}</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Tài sản</span><span class="font-medium">{{ s?.asset_count }}</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Loại TSCĐ</span><span>{{ s?.category_count }}</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Vị trí</span><span>{{ s?.location_count }}</span></div>
    </div>
  </div>
  <button class="w-full btn-primary px-4 py-3 rounded-lg text-sm font-medium" :disabled="busy" @click="setup">{{ busy?'Đang tạo…':'Tạo loại TSCĐ mặc định' }}</button>
  <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅')?'bg-emerald-50 text-emerald-800 border border-emerald-200':'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
</main>
</div>
</template>
<script setup>
import { ref } from 'vue'; import { PageHeader,useToast,useFrappeApi,callApi } from '@shared'
const { toast,ok,err }=useToast(); const busy=ref(false)
const { data:s }=useFrappeApi('taisan.api.get_setup_status',{initialData:{}})
async function setup(){busy.value=true;try{const r=await callApi('taisan.api.setup_taisan');ok('Đã tạo '+((r?.categories_created||[]).length)+' loại TSCĐ')}catch(e){err(e?.message)}finally{busy.value=false}}
</script>
