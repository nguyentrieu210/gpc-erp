<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
<button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button>
<FeatherIcon name="settings" class="h-5 w-5 text-sky-600"/><h1 class="text-lg font-bold text-gray-900 flex-1">Cấu hình mua hàng</h1>
</header>
<main class="flex-1 p-4 max-w-3xl mx-auto w-full space-y-4">
<div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<template v-else>
<div class="rounded-xl border bg-white p-4 flex items-center gap-3" :class="s?.ready?'border-emerald-300':'border-amber-300'">
<FeatherIcon :name="s?.ready?'check-circle':'alert-triangle'" class="h-6 w-6" :class="s?.ready?'text-emerald-600':'text-amber-600'"/>
<div class="flex-1"><div class="font-semibold">{{ s?.ready ? 'Đã sẵn sàng mua hàng' : 'Chưa cấu hình đầy đủ' }}</div>
<div class="text-sm text-gray-500">Công ty: {{ s?.company }} ({{ s?.abbr }}) · VAT: {{ s?.purchase_tax_template || '—' }}</div></div>
<Button variant="solid" theme="sky" :loading="running" @click="run">Chạy cấu hình</Button></div>
<div class="rounded-xl border bg-white divide-y">
<div class="flex items-center gap-3 px-4 py-3"><FeatherIcon :name="s?.default_payable_account?'check':'x'" class="h-4 w-4 shrink-0" :class="s?.default_payable_account?'text-emerald-600':'text-red-500'"/>
<div class="flex-1"><div class="text-sm font-medium">TK phải trả (331)</div><div class="text-xs text-gray-500">{{ s?.default_payable_account || '— thiếu' }}</div></div></div>
<div class="flex items-center gap-3 px-4 py-3"><FeatherIcon :name="s?.default_expense_account?'check':'x'" class="h-4 w-4 shrink-0" :class="s?.default_expense_account?'text-emerald-600':'text-red-500'"/>
<div class="flex-1"><div class="text-sm font-medium">TK chi phí mặc định</div><div class="text-xs text-gray-500">{{ s?.default_expense_account || '— thiếu' }}</div></div></div>
<div class="flex items-center gap-3 px-4 py-3"><FeatherIcon :name="s?.stock_received_but_not_billed?'check':'x'" class="h-4 w-4 shrink-0" :class="s?.stock_received_but_not_billed?'text-emerald-600':'text-red-500'"/>
<div class="flex-1"><div class="text-sm font-medium">TK hàng mua chưa hóa đơn (SRBNB)</div><div class="text-xs text-gray-500">{{ s?.stock_received_but_not_billed || '— thiếu (chạy setup_kho trước)' }}</div></div></div>
<div class="flex items-center gap-3 px-4 py-3"><FeatherIcon :name="s?.cash_account?'check':'x'" class="h-4 w-4 shrink-0" :class="s?.cash_account?'text-emerald-600':'text-red-500'"/>
<div class="flex-1"><div class="text-sm font-medium">TK tiền thanh toán</div><div class="text-xs text-gray-500">{{ s?.cash_account || '— thiếu' }}</div></div></div>
<div class="flex items-center gap-3 px-4 py-3"><FeatherIcon :name="s?.cost_center?'check':'x'" class="h-4 w-4 shrink-0" :class="s?.cost_center?'text-emerald-600':'text-gray-300'"/>
<div class="flex-1"><div class="text-sm font-medium">Cost Center</div><div class="text-xs text-gray-500">{{ s?.cost_center || '—' }}</div></div></div></div>
<div v-if="res" class="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
<div class="font-medium mb-1">Đã chạy cấu hình:</div>
<div>· TK đã đổi: {{ (res.accounts?.changed||[]).join(', ')||'không có thay đổi' }} · Nhóm NCC mới: {{ (res.supplier_groups_created||[]).length }}</div></div></template></main></div></template>
<script setup>
import { ref } from 'vue'; import { Button,FeatherIcon,LoadingIndicator } from 'frappe-ui'; import { useFrappeApi,callApi } from '../composables/useFrappeApi'
const { data:s,loading,fetch }=useFrappeApi('muahang.api.get_muahang_setup_status',{initialData:null});const running=ref(false),res=ref(null)
async function run(){running.value=true;try{res.value=await callApi('muahang.api.setup_muahang');await fetch()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{running.value=false}}
</script>
