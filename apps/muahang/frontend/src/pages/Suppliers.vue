<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
<button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button>
<FeatherIcon name="users" class="h-5 w-5 text-blue-600"/><h1 class="text-lg font-bold text-gray-900 flex-1">Nhà cung cấp</h1>
<Button variant="solid" theme="sky" @click="openCreate">+ Thêm NCC</Button>
</header>
<main class="flex-1 p-4 max-w-5xl mx-auto w-full">
<div class="flex gap-2 mb-3"><input v-model="search" @input="debouncedFetch" placeholder="Tìm NCC..." class="inp flex-1 min-w-[180px]"/>
<select v-model="grp" @change="reload" class="inp w-auto"><option value="">Tất cả nhóm</option><option v-for="g in groups" :key="g.name" :value="g.name">{{ g.supplier_group_name }}</option></select></div>
<div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có nhà cung cấp</div>
<div v-for="s in rows" :key="s.name" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer" @click="$router.push('/suppliers/'+encodeURIComponent(s.name))">
<div class="h-9 w-9 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold shrink-0">{{ (s.supplier_name||'?').slice(0,2).toUpperCase() }}</div>
<div class="flex-1 min-w-0"><div class="font-medium truncate">{{ s.supplier_name }}</div><div class="text-xs text-gray-500 truncate">{{ s.supplier_group }}<span v-if="s.tax_id"> · MST {{ s.tax_id }}</span></div></div>
<div class="text-right shrink-0"><div class="text-sm font-semibold" :class="s.outstanding>0?'text-red-600':'text-gray-400'">{{ fmtVnd(s.outstanding) }}</div><div class="text-xs text-gray-400">dư nợ</div></div></div></div>
<div v-if="total>pl" class="flex justify-between mt-3 text-sm text-gray-600"><span>{{ total }} NCC · trang {{ page }}/{{ pages }}</span><div class="flex gap-2"><Button variant="subtle" :disabled="page<=1" @click="page--;reload()">‹</Button><Button variant="subtle" :disabled="page>=pages" @click="page++;reload()">›</Button></div></div>
</main>
<div v-if="show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="show=false"><div class="bg-white rounded-xl w-full max-w-md p-5 max-h-[90vh] overflow-y-auto">
<h3 class="text-lg font-semibold mb-4">Thêm nhà cung cấp</h3>
<div class="space-y-3">
<label class="block"><span class="text-sm text-gray-600 block mb-1">Tên NCC *</span><input v-model="f.supplier_name" class="inp"/></label>
<label class="block"><span class="text-sm text-gray-600 block mb-1">Nhóm</span><select v-model="f.supplier_group" class="inp"><option v-for="g in groups" :key="g.name" :value="g.name">{{ g.supplier_group_name }}</option></select></label>
<div class="grid grid-cols-2 gap-3"><label class="block"><span class="text-sm text-gray-600 block mb-1">MST</span><input v-model="f.tax_id" class="inp"/></label>
<label class="block"><span class="text-sm text-gray-600 block mb-1">Điện thoại</span><input v-model="f.mobile" class="inp"/></label></div>
<label class="block"><span class="text-sm text-gray-600 block mb-1">Email</span><input v-model="f.email" class="inp"/></label>
<label class="block"><span class="text-sm text-gray-600 block mb-1">Ghi chú</span><textarea v-model="f.details" rows="2" class="inp"></textarea></label>
</div>
<div class="flex justify-end gap-2 mt-5"><Button variant="subtle" @click="show=false">Hủy</Button><Button variant="solid" theme="sky" :loading="saving" @click="save">Lưu</Button></div></div></div>
</div></template>
<script setup>
import { ref,reactive } from 'vue'; import { Button,FeatherIcon,LoadingIndicator } from 'frappe-ui'; import { useFrappeApi,callApi } from '../composables/useFrappeApi'
const rows=ref([]),total=ref(0),pages=ref(1),page=ref(1),loading=ref(false),search=ref(''),grp=ref(''),pl=30
const { data:groups }=useFrappeApi('muahang.api.get_supplier_groups',{initialData:[]})
async function reload(){loading.value=true;try{const r=await callApi('muahang.api.get_suppliers',{search:search.value,supplier_group:grp.value,page:page.value,page_length:pl},'GET');rows.value=r?.suppliers||[];total.value=r?.total||0;pages.value=r?.pages||1}finally{loading.value=false}};reload()
let t;function debouncedFetch(){clearTimeout(t);t=setTimeout(()=>{page.value=1;reload()},350)}
const show=ref(false),saving=ref(false);const f=reactive({supplier_name:'',supplier_group:'NCC trong nước',tax_id:'',mobile:'',email:'',details:''})
function openCreate(){Object.assign(f,{supplier_name:'',supplier_group:'NCC trong nước',tax_id:'',mobile:'',email:'',details:''});show.value=true}
async function save(){if(!f.supplier_name){alert('Nhập tên NCC');return};saving.value=true;try{await callApi('muahang.api.create_supplier',{...f});show.value=false;page.value=1;await reload()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{saving.value=false}}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
