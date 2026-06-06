<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3"><button @click="$router.push('/')" class="text-gray-500"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="settings" class="h-5 w-5 text-gray-600"/><h1 class="text-lg font-bold flex-1">Cấu hình KD</h1><Button variant="solid" theme="rose" :loading="rng" @click="run">Chạy</Button></header>
<main class="flex-1 p-4 max-w-2xl mx-auto space-y-3"><div class="rounded-xl border bg-white p-4"><div class="font-bold" :class="s?.ready?'text-emerald-600':'text-red-600'">{{ s?.ready?'✓ Sẵn sàng':'✗ Chưa sẵn sàng' }}</div><div class="text-sm text-gray-500 mt-2 grid grid-cols-2 gap-1"><div>TK phải thu: {{ s?.default_receivable_account||'—' }}</div><div>TK doanh thu: {{ s?.default_income_account||'—' }}</div><div>Thuế: {{ s?.sales_tax_template||'—' }}</div><div>Bảng giá: {{ s?.sales_price_list||'—' }}</div><div>KH: {{ s?.customer_count }} / {{ s?.customer_group_count }} nhóm</div></div></div></main></div></template>
<script setup>
import {ref} from 'vue'; import {Button,FeatherIcon} from 'frappe-ui'; import {useFrappeApi,callApi} from '../composables/useFrappeApi'
const {data:s}=useFrappeApi('kinhdoanh.api.get_sales_setup_status',{initialData:{}});const rng=ref(false)
async function run(){rng.value=true;try{await callApi('kinhdoanh.api.setup_sales')}finally{rng.value=false}}
</script>
