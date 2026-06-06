<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
<button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button>
<FeatherIcon name="edit-3" class="h-5 w-5 text-amber-600"/><h1 class="text-lg font-bold text-gray-900 flex-1">Đề nghị mua</h1>
<Button variant="solid" theme="sky" @click="openCreate">+ Tạo đề nghị</Button>
</header>
<main class="flex-1 p-4 max-w-3xl mx-auto w-full">
<div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có đề nghị mua</div>
<div v-for="r in rows" :key="r.name" class="px-4 py-3"><div class="flex items-center">
<div class="flex-1"><div class="font-medium">{{ r.name }}</div><div class="text-xs text-gray-500">{{ $fmtDate(r.transaction_date) }} · {{ r.status }}<span v-if="r.per_ordered>0"> · Đã đặt {{ r.per_ordered }}%</span></div></div>
<Button v-if="r.docstatus===1 && r.per_ordered<100" variant="solid" theme="sky" size="sm" :loading="busy===r.name" @click="makePo(r)">Tạo PO</Button></div></div></div>
</main>
<div v-if="show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="show=false"><div class="bg-white rounded-xl w-full max-w-2xl p-5 max-h-[92vh] overflow-y-auto">
<h3 class="text-lg font-semibold mb-4">Đề nghị mua hàng</h3>
<label class="block mb-3"><span class="text-sm text-gray-600 block mb-1">Ngày cần</span><input type="date" v-model="f.schedule_date" class="inp"/></label>
<div class="border rounded-lg overflow-hidden mb-3"><div class="grid grid-cols-12 gap-1 bg-gray-50 px-2 py-1.5 text-xs font-medium text-gray-500"><div class="col-span-7">Hàng hóa</div><div class="col-span-3 text-right">SL</div><div class="col-span-2"></div></div>
<div v-for="(r,i) in f.items" :key="i" class="grid grid-cols-12 gap-1 px-2 py-1.5 items-center border-t">
<select v-model="r.item_code" class="col-span-7 inp !py-1 !text-xs"><option value="">— chọn —</option><option v-for="it in itemOpts" :key="it.name" :value="it.item_code">{{ it.item_name }}</option></select>
<input v-model.number="r.qty" type="number" class="col-span-3 inp !py-1 text-right"/>
<button class="col-span-2 text-red-500 text-xs" @click="f.items.splice(i,1)">×</button></div></div>
<Button variant="subtle" size="sm" @click="f.items.push({item_code:'',qty:1})">+ Thêm dòng</Button>
<div class="flex justify-end gap-2 mt-5"><Button variant="subtle" @click="show=false">Hủy</Button><Button variant="solid" theme="sky" :loading="saving" @click="save">Lưu & Gửi</Button></div></div></div>
</div></template>
<script setup>
import { ref,reactive,computed } from 'vue'; import { Button,FeatherIcon,LoadingIndicator } from 'frappe-ui'; import { useFrappeApi,callApi } from '../composables/useFrappeApi'
const rows=ref([]),loading=ref(false),busy=ref('')
const { data: itemsR }=useFrappeApi('kho.api.get_items',{initialData:{items:[]},params:{page_length:500}})
const itemOpts=computed(()=>itemsR.value?.items||[])
async function reload(){loading.value=true;try{const r=await callApi('muahang.api.get_purchase_requests',{},'GET');rows.value=r?.entries||[]}finally{loading.value=false}};reload()
const show=ref(false),saving=ref(false);const f=reactive({schedule_date:new Date().toISOString().slice(0,10),items:[{item_code:'',qty:1}]})
function openCreate(){f.schedule_date=new Date().toISOString().slice(0,10);f.items=[{item_code:'',qty:1}];show.value=true}
async function save(){const items=f.items.filter(r=>r.item_code&&r.qty);if(!items.length){alert('Thêm ít nhất 1 dòng');return};saving.value=true;try{await callApi('muahang.api.create_purchase_request',{items:JSON.stringify(items),schedule_date:f.schedule_date,submit:1});show.value=false;await reload()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{saving.value=false}}
async function makePo(r){busy.value=r.name;try{await callApi('muahang.api.make_po_from_request',{name:r.name,submit:1});await reload();alert('Đã tạo PO')}catch(e){alert('Lỗi: '+(e?.message||e))}finally{busy.value=''}}
</script>
