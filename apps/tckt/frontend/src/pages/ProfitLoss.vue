<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3"><button @click="$router.push('/')" class="text-gray-500"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="trending-up" class="h-5 w-5 text-emerald-600"/><h1 class="text-lg font-bold flex-1">KQKD</h1></header>
<main class="flex-1 p-4 max-w-3xl mx-auto"><div class="flex gap-3 mb-3"><input type="date" v-model="fd" @change="reload" class="inp w-auto"/><span class="self-center">→</span><input type="date" v-model="td" @change="reload" class="inp w-auto"/></div>
<div v-if="loading" class="py-10"><LoadingIndicator/></div><template v-else>
<div class="rounded-xl border bg-white p-4 mb-3"><div class="font-bold text-emerald-600 mb-1">Doanh thu (Income)</div>
<div v-for="r in d.income||[]" :key="r.account" class="flex justify-between text-sm py-1"><span>{{ r.account_name }}</span><span class="text-emerald-700">{{ fmtVnd(r.balance) }}</span></div>
<div class="flex justify-between font-bold border-t pt-2 mt-2"><span>Tổng doanh thu</span><span>{{ fmtVnd(d.total_income) }}</span></div></div>
<div class="rounded-xl border bg-white p-4 mb-3"><div class="font-bold text-red-600 mb-1">Chi phí (Expense)</div>
<div v-for="r in d.expense||[]" :key="r.account" class="flex justify-between text-sm py-1"><span>{{ r.account_name }}</span><span class="text-red-700">{{ fmtVnd(r.balance) }}</span></div>
<div class="flex justify-between font-bold border-t pt-2 mt-2"><span>Tổng chi phí</span><span>{{ fmtVnd(d.total_expense) }}</span></div></div>
<div class="rounded-xl border bg-white p-4 flex justify-between font-bold text-lg" :class="d.net_profit>=0?'text-emerald-600':'text-red-600'"><span>Lợi nhuận ròng</span><span>{{ fmtVnd(d.net_profit) }}</span></div></template></main></div></template>
<script setup>
import {ref} from 'vue'; import {FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const d=ref({}),loading=ref(false),fd=ref('2026-01-01'),td=ref(new Date().toISOString().slice(0,10))
async function reload(){loading.value=true;try{d.value=await callApi('tckt.api.get_profit_loss',{from_date:fd.value,to_date:td.value},'GET')}finally{loading.value=false}};reload()
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
