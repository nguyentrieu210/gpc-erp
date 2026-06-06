<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3"><button @click="$router.push('/')" class="text-gray-500"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="layers" class="h-5 w-5 text-amber-600"/><h1 class="text-lg font-bold flex-1">Cân đối TK</h1></header>
<main class="flex-1 p-4 max-w-5xl mx-auto"><div class="flex gap-3 mb-3"><input type="date" v-model="fd" @change="reload" class="inp w-auto"/><span class="self-center">→</span><input type="date" v-model="td" @change="reload" class="inp w-auto"/></div>
<div class="rounded-xl border bg-white overflow-x-auto"><table class="w-full text-sm min-w-[640px]"><thead><tr class="bg-gray-50 text-xs"><th class="px-3 py-2">TK</th><th class="px-3 py-2">Tên TK</th><th class="px-3 py-2 text-right">Nợ</th><th class="px-3 py-2 text-right">Có</th><th class="px-3 py-2 text-right">Dư</th></tr></thead>
<tbody><tr v-if="loading"><td colspan="5" class="py-8 text-center"><LoadingIndicator/></td></tr>
<tr v-else-if="!rows.length"><td colspan="5" class="py-8 text-center text-gray-400">Chưa có dữ liệu</td></tr>
<tr v-for="r in rows" :key="r.account" class="border-t"><td class="px-3 py-2">{{ r.account_number }}</td><td class="px-3 py-2">{{ r.account_name }}</td><td class="px-3 py-2 text-right text-emerald-600">{{ r.debit>0?fmtVnd(r.debit):'' }}</td><td class="px-3 py-2 text-right text-red-600">{{ r.credit>0?fmtVnd(r.credit):'' }}</td><td class="px-3 py-2 text-right" :class="r.balance>=0?'text-emerald-700':'text-red-700'">{{ fmtVnd(r.balance) }}</td></tr>
<tr class="font-bold border-t bg-gray-50"><td colspan="2" class="px-3 py-2 text-right">Tổng</td><td class="px-3 py-2 text-right">{{ fmtVnd(d.total_debit) }}</td><td class="px-3 py-2 text-right">{{ fmtVnd(d.total_credit) }}</td><td class="px-3 py-2 text-right" :class="d.balanced?'text-emerald-600':'text-red-600'">{{ d.balanced?'CÂN':'LỆCH!' }}</td></tr></tbody></table></div>
</main></div></template>
<script setup>
import {ref} from 'vue'; import {FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const rows=ref([]),d=ref({}),loading=ref(false),fd=ref('2026-01-01'),td=ref(new Date().toISOString().slice(0,10))
async function reload(){loading.value=true;try{d.value=await callApi('tckt.api.get_trial_balance',{from_date:fd.value,to_date:td.value},'GET');rows.value=d.value?.rows||[]}finally{loading.value=false}};reload()
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
