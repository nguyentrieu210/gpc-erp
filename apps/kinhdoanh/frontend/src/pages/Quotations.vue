<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="file-text" class="h-5 w-5 text-amber-600"/><h1 class="text-lg font-bold flex-1">Báo giá</h1><Button variant="solid" theme="rose" @click="openCreate">+ Tạo BG</Button></header>
<main class="flex-1 p-4 max-w-4xl mx-auto"><div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có báo giá</div>
<div v-for="q in rows" :key="q.name" class="flex items-center px-4 py-3"><div class="flex-1"><div class="font-medium">{{ q.name }} <span :class="q.docstatus===1?'text-emerald-600':'text-amber-600'">{{ q.docstatus===1?'Đã gửi':'Nháp' }}</span></div><div class="text-xs text-gray-500">{{ q.customer_name }} · {{ $fmtDate(q.transaction_date) }}</div></div>
<div class="text-right"><div class="font-semibold">{{ fmtVnd(q.grand_total) }}</div><div v-if="q.status" class="text-xs" :class="q.status==='Draft'?'text-amber-600':'text-emerald-600'">{{ q.status }}</div></div></div></div>
</main></div></template>
<script setup>
import {ref} from 'vue'; import {Button,FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const rows=ref([]),loading=ref(false)
async function reload(){loading.value=true;try{rows.value=(await callApi('kinhdoanh.api.get_quotations',{},'GET'))?.entries||[]}finally{loading.value=false}};reload()
const show=ref(false)
function openCreate(){show.value=true}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
