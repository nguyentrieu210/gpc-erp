<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="users" class="h-5 w-5 text-blue-600"/><h1 class="text-lg font-bold flex-1">Khách hàng</h1><Button variant="solid" theme="rose" @click="openCreate">+ Thêm KH</Button></header>
<main class="flex-1 p-4 max-w-4xl mx-auto"><div class="flex gap-2 mb-3"><input v-model="q" @input="debFetch" placeholder="Tìm KH..." class="inp flex-1 min-w-[180px]"/></div>
<div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có KH</div>
<div v-for="c in rows" :key="c.name" class="flex items-center px-4 py-3"><div class="h-9 w-9 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold shrink-0">{{ (c.customer_name||'?').slice(0,2).toUpperCase() }}</div>
<div class="flex-1 min-w-0 ml-3"><div class="font-medium truncate">{{ c.customer_name }}</div><div class="text-xs text-gray-500">{{ c.customer_group }}<span v-if="c.tax_id"> · MST:{{ c.tax_id }}</span></div></div>
<div class="text-right shrink-0"><div class="font-semibold" :class="c.outstanding>0?'text-red-600':'text-gray-400'">{{ fmtVnd(c.outstanding) }}</div><div class="text-xs text-gray-400">dư nợ</div></div></div></div>
</main>
<div v-if="show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="show=false"><div class="bg-white rounded-xl w-full max-w-sm p-5"><h3 class="font-semibold mb-4">Thêm KH</h3>
<label class="block mb-2"><span class="text-sm">Tên KH *</span><input v-model="f.customer_name" class="inp"/></label>
<label class="block mb-2"><span class="text-sm">MST</span><input v-model="f.tax_id" class="inp"/></label>
<label class="block mb-2"><span class="text-sm">SĐT</span><input v-model="f.mobile" class="inp"/></label>
<div class="flex justify-end gap-2 mt-5"><Button variant="subtle" @click="show=false">Hủy</Button><Button variant="solid" theme="rose" :loading="saving" @click="save">Lưu</Button></div></div></div></div></template>
<script setup>
import {ref,reactive} from 'vue'; import {Button,FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const rows=ref([]),loading=ref(false),q=ref('')
async function reload(){loading.value=true;try{rows.value=(await callApi('kinhdoanh.api.get_customers',{search:q.value},'GET'))?.entries||[]}finally{loading.value=false}};reload()
let t;function debFetch(){clearTimeout(t);t=setTimeout(reload,350)}
const show=ref(false),saving=ref(false);const f=reactive({customer_name:'',tax_id:'',mobile:'',email:''})
function openCreate(){Object.assign(f,{customer_name:'',tax_id:'',mobile:'',email:''});show.value=true}
async function save(){if(!f.customer_name)return;saving.value=true;try{await callApi('kinhdoanh.api.create_customer',{...f});show.value=false;reload()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{saving.value=false}}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
