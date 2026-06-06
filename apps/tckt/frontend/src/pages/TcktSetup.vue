<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3"><button @click="$router.push('/')" class="text-gray-500"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="settings" class="h-5 w-5 text-gray-600"/><h1 class="text-lg font-bold flex-1">Cấu hình TC</h1><Button variant="solid" :loading="rng" @click="run">Chạy</Button></header>
<main class="flex-1 p-4 max-w-2xl mx-auto space-y-3"><div class="rounded-xl border bg-white p-4"><div class="font-bold text-emerald-600">✓ {{ s?.company }} ({{ s?.abbr }})</div><div class="text-sm text-gray-500 grid grid-cols-2 mt-2"><div>TK: {{ s?.account_count }}</div><div>GL: {{ s?.gl_entry_count }}</div><div>Phiếu KT: {{ s?.je_count }}</div><div>Năm TC: {{ s?.fiscal_year }}</div><div>Tiền: {{ s?.default_currency }}</div><div>Ready: {{ s?.ready?'✓':'✗' }}</div></div></div></main></div></template>
<script setup>
import {ref} from 'vue'; import {Button,FeatherIcon} from 'frappe-ui'; import {useFrappeApi,callApi} from '../composables/useFrappeApi'
const {data:s}=useFrappeApi('tckt.api.get_accounting_setup_status',{initialData:{}});const rng=ref(false)
async function run(){rng.value=true;try{await callApi('tckt.api.setup_accounting')}finally{rng.value=false}}
</script>
