<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3"><button @click="$router.push('/')" class="text-gray-500"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="bar-chart-2" class="h-5 w-5 text-indigo-600"/><h1 class="text-lg font-bold flex-1">Bảng CĐKT</h1></header>
<main class="flex-1 p-4 max-w-3xl mx-auto"><div class="flex gap-2 mb-3"><input type="date" v-model="dt" @change="reload" class="inp w-auto"/></div>
<div v-if="loading" class="py-10"><LoadingIndicator/></div><template v-else>
<div class="rounded-xl border bg-white p-4 mb-3"><div class="font-bold text-blue-600 mb-1">Tài sản (Asset)</div>
<div v-for="r in d.asset||[]" :key="r.account" class="flex justify-between text-sm py-1"><span>{{ r.account_name }}</span><span>{{ fmtVnd(r.balance) }}</span></div>
<div class="flex justify-between font-bold border-t pt-2 mt-2"><span>Tổng TS</span><span>{{ fmtVnd(d.total_asset) }}</span></div></div>
<div class="rounded-xl border bg-white p-4 mb-3"><div class="font-bold text-amber-600 mb-1">Nợ phải trả (Liability)</div>
<div v-for="r in d.liability||[]" :key="r.account" class="flex justify-between text-sm py-1"><span>{{ r.account_name }}</span><span>{{ fmtVnd(Math.abs(r.balance)) }}</span></div>
<div class="flex justify-between font-bold border-t pt-2 mt-2"><span>Tổng NPT</span><span>{{ fmtVnd(d.total_liability) }}</span></div></div>
<div class="rounded-xl border bg-white p-4 mb-3"><div class="font-bold text-violet-600 mb-1">Vốn CSH (Equity) <span class="text-sm text-gray-500">(gồm LN {{ fmtVnd(d.net_income) }})</span></div>
<div v-for="r in d.equity||[]" :key="r.account" class="flex justify-between text-sm py-1"><span>{{ r.account_name }}</span><span>{{ fmtVnd(Math.abs(r.balance)) }}</span></div>
<div class="flex justify-between font-bold border-t pt-2 mt-2"><span>Tổng VCSH</span><span>{{ fmtVnd(d.total_equity) }}</span></div></div>
<div class="rounded-xl border bg-white p-4 flex justify-between font-bold text-lg" :class="d.balanced?'text-emerald-600':'text-red-600'"><span>{{ d.balanced?'✓ CÂN BẰNG':'✗ LỆCH!' }}</span><span>{{ fmtVnd(d.total_asset) }} = {{ fmtVnd((d.total_liability||0)+(d.total_equity||0)) }}</span></div></template></main></div></template>
<script setup>
import {ref} from 'vue'; import {FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const d=ref({}),loading=ref(false),dt=ref(new Date().toISOString().slice(0,10))
async function reload(){loading.value=true;try{d.value=await callApi('tckt.api.get_balance_sheet',{as_of_date:dt.value},'GET')}finally{loading.value=false}};reload()
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
