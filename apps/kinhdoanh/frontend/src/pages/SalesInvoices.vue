<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="file-plus" class="h-5 w-5 text-violet-600"/><h1 class="text-lg font-bold flex-1">Hóa đơn bán (SI)</h1></header>
<main class="flex-1 p-4 max-w-4xl mx-auto"><div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có hóa đơn</div>
<div v-for="si in rows" :key="si.name" class="flex items-center px-4 py-3"><div class="flex-1"><div class="font-medium">{{ si.name }} <span :class="si.docstatus===1?'text-emerald-600':'text-amber-600'">{{ si.docstatus===1?'Đã ghi':'Nháp' }}</span></div><div class="text-xs text-gray-500">{{ si.customer_name }} · {{ $fmtDate(si.posting_date) }} · hạn {{ $fmtDate(si.due_date) }}</div></div>
<div class="text-right"><div class="font-semibold">{{ fmtVnd(si.grand_total) }}</div><div class="text-xs" :class="si.outstanding_amount>0?'text-red-600':'text-gray-400'">{{ si.outstanding_amount>0?'Còn '+fmtVnd(si.outstanding_amount):'Đã trả' }}</div></div></div></div>
</main></div></template>
<script setup>
import {ref} from 'vue'; import {FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const rows=ref([]),loading=ref(false)
async function reload(){loading.value=true;try{rows.value=(await callApi('kinhdoanh.api.get_sales_invoices',{},'GET'))?.entries||[]}finally{loading.value=false}};reload()
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
