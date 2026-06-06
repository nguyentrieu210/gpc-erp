<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
<button class="text-gray-500 hover:text-gray-800" @click="$router.push('/suppliers')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button>
<FeatherIcon name="users" class="h-5 w-5 text-blue-600"/><h1 class="text-lg font-bold text-gray-900 flex-1 truncate">{{ sup?.supplier_name || id }}</h1>
<Button variant="subtle" @click="openEdit">Sửa</Button>
</header>
<main class="flex-1 p-4 max-w-3xl mx-auto w-full space-y-4">
<div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<template v-else-if="sup">
<div class="rounded-xl border bg-white p-4"><div class="flex items-center gap-3"><div class="h-12 w-12 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold">{{ (sup.supplier_name||'?').slice(0,2).toUpperCase() }}</div>
<div class="flex-1"><div class="font-semibold text-gray-900">{{ sup.supplier_name }}</div><div class="text-sm text-gray-500">{{ sup.supplier_group }}<span v-if="sup.tax_id"> · MST: {{ sup.tax_id }}</span></div></div>
<span v-if="sup.disabled" class="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-600">Ngừng GD</span></div>
<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 text-center"><div class="p-2"><div class="text-base font-bold text-red-600">{{ fmtVnd(sup.outstanding) }}</div><div class="text-xs text-gray-500">Dư nợ</div></div>
<div class="p-2"><div class="text-base font-bold text-gray-700">{{ sup.recent_pos?.length || 0 }}</div><div class="text-xs text-gray-500">PO gần đây</div></div>
<div class="p-2"><div class="text-base font-bold text-gray-700">{{ sup.supplier_type || 'Company' }}</div><div class="text-xs text-gray-500">Loại</div></div>
<div class="p-2"><div class="text-base font-bold text-gray-700">{{ sup.default_currency || 'VND' }}</div><div class="text-xs text-gray-500">Tiền tệ</div></div></div>
<div v-if="sup.supplier_details" class="mt-3 text-sm text-gray-500 whitespace-pre-wrap">{{ sup.supplier_details }}</div></div>

<div class="rounded-xl border bg-white"><div class="px-4 py-3 border-b font-medium text-gray-700">Đơn mua gần đây</div>
<div v-if="!sup.recent_pos?.length" class="py-6 text-center text-gray-400 text-sm">Chưa có đơn mua</div>
<div v-for="po in sup.recent_pos" :key="po.name" class="flex items-center px-4 py-2.5 border-t text-sm">
<div class="flex-1"><div class="font-medium">{{ po.name }}</div><div class="text-xs text-gray-500">{{ $fmtDate(po.transaction_date) }} · {{ po.status }}</div></div>
<div class="text-right"><div class="font-semibold">{{ fmtVnd(po.grand_total) }}</div></div></div></div>

<div class="rounded-xl border bg-white"><div class="px-4 py-3 border-b font-medium text-gray-700">Sổ công nợ</div>
<div v-if="!sup.ledger?.length" class="py-6 text-center text-gray-400 text-sm">Chưa có phát sinh</div>
<div v-for="gl in sup.ledger" :key="gl.voucher_no" class="flex items-center px-4 py-2.5 border-t text-sm">
<div class="flex-1"><div class="font-medium">{{ gl.voucher_no }}</div><div class="text-xs text-gray-500">{{ $fmtDate(gl.posting_date) }} · {{ gl.voucher_type }}</div></div>
<div class="text-right"><div class="text-emerald-600">{{ gl.credit>0 ? fmtVnd(gl.credit) : '' }}</div><div class="text-red-600">{{ gl.debit>0 ? fmtVnd(gl.debit) : '' }}</div></div></div></div>
</template>
</main>
</div>
</template>
<script setup>
import { ref,reactive } from 'vue'; import { useRoute } from 'vue-router'; import { Button,FeatherIcon,LoadingIndicator } from 'frappe-ui'; import { callApi } from '../composables/useFrappeApi'
const route=useRoute(); const id=decodeURIComponent(route.params.id); const sup=ref(null),loading=ref(true)
async function load(){loading.value=true;try{sup.value=await callApi('muahang.api.get_supplier',{name:id},'GET')}finally{loading.value=false}};load()
function openEdit(){alert('Sửa NCC: chưa có UI modal, dùng update_supplier API.')}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
