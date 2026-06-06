<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="dollar-sign" class="h-5 w-5 text-red-600"/><h1 class="text-lg font-bold flex-1">Phải thu</h1></header>
<main class="flex-1 p-4 max-w-3xl mx-auto"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div><template v-else>
<div class="grid grid-cols-2 gap-3 mb-4"><div class="rounded-xl border bg-white p-3 text-center"><div class="text-xl font-bold text-red-600">{{ fmtVnd(d.total_outstanding) }}</div><div class="text-xs text-gray-500">Tổng phải thu</div></div><div class="rounded-xl border bg-white p-3 text-center"><div class="text-xl font-bold">{{ d.count??0 }}</div><div class="text-xs text-gray-500">KH còn nợ</div></div></div>
<div v-if="!d.customers?.length" class="rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-center text-emerald-700"><FeatherIcon name="check-circle" class="h-8 w-8 mx-auto mb-2"/>Không có công nợ phải thu.</div>
<div v-for="s in d.customers||[]" :key="s.customer" class="rounded-xl border bg-white mb-3">
<div class="flex items-center px-4 py-3 border-b"><div class="flex-1"><div class="font-semibold">{{ s.customer_name }}</div><div class="text-xs text-gray-500">{{ s.invoices?.length }} HĐ chưa trả</div></div><div class="text-lg font-bold text-red-600">{{ fmtVnd(s.outstanding) }}</div></div>
<div v-for="inv in s.invoices" :key="inv.name" class="flex items-center px-4 py-2.5 border-t text-sm"><div class="flex-1"><div>{{ inv.name }}</div><div class="text-xs text-gray-500">{{ $fmtDate(inv.due_date) }}</div></div>
<div class="mr-2 font-semibold">{{ fmtVnd(inv.outstanding_amount) }}</div>
<Button variant="solid" theme="emerald" size="sm" :loading="busy===inv.name" @click="pay(inv)">Thu</Button></div></div></template></main></div></template>
<script setup>
import {ref} from 'vue'; import {Button,FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {useFrappeApi,callApi} from '../composables/useFrappeApi'
const {data:d,loading,fetch}=useFrappeApi('kinhdoanh.api.get_receivables_summary',{initialData:{customers:[]}});const busy=ref('')
async function pay(inv){busy.value=inv.name;try{await callApi('kinhdoanh.api.make_payment_receive',{invoice:inv.name,submit:1});await fetch();alert('Đã thu: '+inv.name)}catch(e){alert('Lỗi: '+(e?.message||e))}finally{busy.value=''}}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
