<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<PageHeader title="Loại tài sản cố định" icon="folder" icon-class="text-blue-600"/>
<main class="flex-1 p-4 max-w-4xl mx-auto w-full">
<div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else class="space-y-2">
  <div v-for="c in cats" :key="c.name" class="app-card p-4 flex items-center gap-3">
    <div class="h-10 w-10 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center"><FeatherIcon name="folder" class="h-5 w-5"/></div>
    <div class="flex-1"><div class="font-semibold">{{ c.asset_category_name }}</div><div class="text-xs text-gray-500">{{ c.frequency_of_depreciation ? 'KH '+({12:'Tháng',3:'Quý',1:'Năm'}[c.total_number_of_depreciations]||c.total_number_of_depreciations+'/năm') : '' }}</div></div>
  </div>
  <div v-if="!cats.length" class="text-sm text-gray-400 text-center py-10">Chưa có loại TSCĐ. Vào Cấu hình để tạo.</div>
</div>
</main>
</div>
</template>
<script setup>
import { ref } from 'vue'; import { FeatherIcon,LoadingIndicator } from 'frappe-ui'; import { PageHeader,callApi } from '@shared'
const cats=ref([]); const loading=ref(false)
async function reload(){loading.value=true;try{cats.value=(await callApi('taisan.api.get_asset_categories',{},'GET'))?.entries||[]}finally{loading.value=false}};reload()
</script>
