<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="book-open" class="h-5 w-5 text-blue-600"/><h1 class="text-lg font-bold flex-1">Sổ cái (GL)</h1></header>
<main class="flex-1 p-4 max-w-6xl mx-auto"><div class="flex flex-wrap gap-2 mb-3"><select v-model="acct" @change="reload" class="inp w-auto"><option value="">Tất cả TK</option><option v-for="a in coaAccts" :key="a.name" :value="a.name">{{ a.account_number }} {{ a.account_name }}</option></select></div>
<div class="rounded-xl border bg-white overflow-x-auto"><table class="w-full text-sm min-w-[640px]"><thead><tr class="bg-gray-50 text-xs text-gray-500"><th class="px-3 py-2">Ngày</th><th class="px-3 py-2">TK</th><th class="px-3 py-2">Chứng từ</th><th class="px-3 py-2 text-right">Nợ</th><th class="px-3 py-2 text-right">Có</th></tr></thead>
<tbody><tr v-if="loading"><td colspan="5" class="py-8 text-center"><LoadingIndicator/></td></tr>
<tr v-else-if="!rows.length"><td colspan="5" class="py-8 text-center text-gray-400">Chưa có dữ liệu</td></tr>
<tr v-for="(r,i) in rows" :key="i" class="border-t"><td class="px-3 py-2 whitespace-nowrap">{{ $fmtDate(r.posting_date) }}</td><td class="px-3 py-2 text-xs">{{ short(r.account) }}</td><td class="px-3 py-2 text-xs">{{ r.voucher_no }}</td><td class="px-3 py-2 text-right text-emerald-600">{{ r.debit>0?fmtVnd(r.debit):'' }}</td><td class="px-3 py-2 text-right text-red-600">{{ r.credit>0?fmtVnd(r.credit):'' }}</td></tr>
<tr class="font-bold border-t"><td colspan="3" class="px-3 py-2 text-right">Tổng</td><td class="px-3 py-2 text-right text-emerald-600">{{ fmtVnd(d.debit_total) }}</td><td class="px-3 py-2 text-right text-red-600">{{ fmtVnd(d.credit_total) }}</td></tr></tbody></table></div>
</main></div></template>
<script setup>
import {ref} from 'vue'; import {FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {useFrappeApi,callApi} from '../composables/useFrappeApi'
const d=ref({entries:[],debit_total:0,credit_total:0}),rows=ref([]),loading=ref(false),acct=ref('')
const coaAccts=ref([])
async function reload(){loading.value=true;try{const r=await callApi('tckt.api.get_gl_entries',{account:acct.value},'GET');d.value=r;rows.value=r?.entries||[];if(!coaAccts.value.length){const c=await callApi('tckt.api.get_chart_of_accounts',{},'GET');coaAccts.value=c?.accounts||[]}}finally{loading.value=false}};reload()
function short(a) {return (a||'').split(' - ').slice(0,2).join(' - ')}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
