<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="shopping-cart" class="h-5 w-5 text-rose-600"/><h1 class="text-lg font-bold flex-1">Đơn bán (SO)</h1><Button variant="solid" theme="rose" @click="openCreate">+ Tạo SO</Button></header>
<main class="flex-1 p-4 max-w-5xl mx-auto"><div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có đơn bán</div>
<div v-for="so in rows" :key="so.name" class="flex items-center px-4 py-3"><div class="flex-1"><div class="font-medium">{{ so.name }} <span class="text-xs px-2 py-0.5 rounded-full bg-rose-100 text-rose-700">{{ so.status_vi }}</span></div><div class="text-xs text-gray-500">{{ so.customer_name }} · {{ $fmtDate(so.transaction_date) }}<span v-if="so.per_delivered>0"> · Giao {{ so.per_delivered }}%</span></div></div>
<div class="text-right"><div class="font-semibold">{{ fmtVnd(so.grand_total) }}</div><div class="flex gap-2 mt-1"><Button v-if="so.docstatus===0" variant="solid" theme="green" size="sm" @click="submit(so)">Chốt</Button></div></div></div></div>
</main></div></template>
<script setup>
import {ref} from 'vue'; import {Button,FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const rows=ref([]),loading=ref(false)
async function reload(){loading.value=true;try{rows.value=(await callApi('kinhdoanh.api.get_sales_orders',{},'GET'))?.entries||[]}finally{loading.value=false}};reload()
async function submit(so){await callApi('kinhdoanh.api.submit_sales_order',{name:so.name});reload()}
const show=ref(false)
function openCreate(){show.value=true}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
