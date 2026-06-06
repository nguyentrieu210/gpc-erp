<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="settings" class="h-5 w-5 text-gray-600"/><h1 class="text-lg font-bold flex-1">Cấu hình CRM</h1><Button variant="solid" :loading="running" @click="run">Chạy cấu hình</Button></header>
<main class="flex-1 p-4 max-w-2xl mx-auto space-y-3"><div class="rounded-xl border bg-white p-4"><div class="font-semibold text-emerald-600">✓ Sẵn sàng</div><div class="text-sm text-gray-500">Công ty: {{ s?.company }} · Nhóm KH: {{ s?.customer_group_count }}</div></div>
<div v-if="r" class="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">Đã chạy: {{ r.customer_groups_created?.length||0 }} nhóm KH mới</div></main></div></template>
<script setup>
import {ref} from 'vue'; import {Button,FeatherIcon} from 'frappe-ui'; import {useFrappeApi,callApi} from '../composables/useFrappeApi'
const {data:s}=useFrappeApi('crm_ui.api.get_crm_setup_status',{initialData:{}});const running=ref(false),r=ref(null)
async function run(){running.value=true;try{r.value=await callApi('crm_ui.api.setup_crm')}finally{running.value=false}}
</script>
