<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="truck" class="h-5 w-5 text-emerald-600"/><h1 class="text-lg font-bold flex-1">Xuất giao (DN)</h1></header>
<main class="flex-1 p-4 max-w-4xl mx-auto"><div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có phiếu xuất</div>
<div v-for="dn in rows" :key="dn.name" class="flex items-center px-4 py-3"><div class="flex-1"><div class="font-medium">{{ dn.name }} <span :class="dn.docstatus===1?'text-emerald-600':'text-amber-600'">{{ dn.docstatus===1?'Đã xuất':'Nháp' }}</span></div><div class="text-xs text-gray-500">{{ dn.customer_name }} · {{ $fmtDate(dn.posting_date) }}</div></div>
<div class="text-right"><div class="font-semibold">{{ fmtVnd(dn.grand_total) }}</div></div></div></div>
</main></div></template>
<script setup>
import {ref} from 'vue'; import {FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const rows=ref([]),loading=ref(false)
async function reload(){loading.value=true;try{rows.value=(await callApi('kinhdoanh.api.get_delivery_notes',{},'GET'))?.entries||[]}finally{loading.value=false}};reload()
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
