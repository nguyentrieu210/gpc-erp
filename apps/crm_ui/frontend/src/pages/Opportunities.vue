<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="target" class="h-5 w-5 text-amber-600"/><h1 class="text-lg font-bold flex-1">Cơ hội</h1><Button variant="solid" @click="openCreate">+ Thêm</Button></header>
<main class="flex-1 p-4 max-w-6xl mx-auto">
<div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div><template v-else>
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3"><div v-if="!rows.length" class="col-span-full py-10 text-center text-gray-400">Chưa có cơ hội</div>
<div v-for="o in rows" :key="o.name" class="rounded-xl border bg-white p-4 shadow-sm"><div class="font-semibold">{{ o.title }}</div>
<div class="text-sm text-gray-500">{{ o.party_name||'' }}</div>
<div class="flex justify-between mt-2"><span class="text-sm font-bold text-amber-600">{{ fmtVnd(o.opportunity_amount) }}</span><span class="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">{{ o.stage_vi }}</span></div>
<div class="flex gap-2 mt-3"><select v-model="o._s" @change="move(o)" class="inp !py-1 text-xs"><option v-for="s in stages" :key="s.value" :value="s.value">{{ s.label }}</option></select>
<Button variant="solid" size="sm" theme="green" @click="convert(o)">→ KH</Button></div></div></div></template>
</main></div></template>
<script setup>
import {ref} from 'vue'; import {Button,FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const rows=ref([]),loading=ref(false)
const stages=[{value:'Open',label:'Mở'},{value:'Qualification',label:'Đánh giá'},{value:'Needs Analysis',label:'Phân tích'},{value:'Proposal',label:'Đề xuất'},{value:'Negotiation',label:'Đàm phán'},{value:'Closed Won',label:'Thắng'},{value:'Closed Lost',label:'Thua'}]
async function reload(){loading.value=true;try{rows.value=(await callApi('crm_ui.api.get_opportunities',{},'GET'))?.entries?.map(o=>({...o,_s:o.status}))||[]}finally{loading.value=false}};reload()
async function move(o){await callApi('crm_ui.api.move_opportunity_status',{name:o.name,status:o._s});reload()}
async function convert(o){try{await callApi('crm_ui.api.convert_opportunity_to_customer',{name:o.name});reload()}catch(e){alert('Lỗi: '+(e?.message||e))}}
const show=ref(false)
function openCreate(){show.value=true}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
