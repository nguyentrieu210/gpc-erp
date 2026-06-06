<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
<button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button>
<FeatherIcon name="truck" class="h-5 w-5 text-emerald-600"/><h1 class="text-lg font-bold text-gray-900 flex-1">Nhập mua (PR)</h1>
<Button variant="solid" theme="sky" @click="openCreate">+ Tạo phiếu</Button>
</header>
<main class="flex-1 p-4 max-w-4xl mx-auto w-full">
<select v-model="sup" @change="reload" class="inp w-auto mb-3"><option value="">Tất cả NCC</option><option v-for="s in suppliers" :key="s.name" :value="s.name">{{ s.supplier_name }}</option></select>
<div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có phiếu nhập</div>
<div v-for="r in rows" :key="r.name" class="flex items-center px-4 py-3">
<div class="flex-1 min-w-0"><div class="font-medium">{{ r.name }} <span class="text-xs" :class="r.docstatus===1?'text-emerald-600':'text-amber-600'">{{ r.docstatus===1?'Đã nhập':'Nháp' }}</span></div>
<div class="text-xs text-gray-500">{{ r.supplier_name }} · {{ $fmtDate(r.posting_date) }}<span v-if="r.per_billed>0"> · Đã HĐ {{ r.per_billed }}%</span></div></div>
<div class="text-right shrink-0"><div class="font-semibold">{{ fmtVnd(r.grand_total) }}</div>
<div class="flex gap-2 mt-1"><Button v-if="r.docstatus===0" variant="solid" theme="green" size="sm" :loading="busy===r.name" @click="submit(r)">Chốt</Button>
<Button variant="subtle" size="sm" @click="print(r.name)">In</Button></div></div></div></div>
</main>
<div v-if="show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="show=false"><div class="bg-white rounded-xl w-full max-w-2xl p-5 max-h-[92vh] overflow-y-auto">
<h3 class="text-lg font-semibold mb-4">Phiếu nhập mua</h3>
<div class="grid grid-cols-2 gap-3 mb-3"><label class="block"><span class="text-sm text-gray-600 block mb-1">Nhà cung cấp *</span><select v-model="f.supplier" class="inp"><option value="">— chọn —</option><option v-for="s in suppliers" :key="s.name" :value="s.name">{{ s.supplier_name }}</option></select></label>
<label class="block"><span class="text-sm text-gray-600 block mb-1">Kho nhập</span><select v-model="f.warehouse" class="inp"><option v-for="w in warehouses" :key="w.name" :value="w.name">{{ w.warehouse_name }}</option></select></label></div>
<div class="border rounded-lg overflow-hidden mb-3"><div class="grid grid-cols-12 gap-1 bg-gray-50 px-2 py-1.5 text-xs font-medium text-gray-500"><div class="col-span-5">Hàng hóa</div><div class="col-span-2 text-right">SL</div><div class="col-span-3 text-right">Đơn giá</div><div class="col-span-2"></div></div>
<div v-for="(r,i) in f.items" :key="i" class="grid grid-cols-12 gap-1 px-2 py-1.5 items-center border-t">
<select v-model="r.item_code" class="col-span-5 inp !py-1 !text-xs"><option value="">— chọn —</option><option v-for="it in itemOpts" :key="it.name" :value="it.item_code">{{ it.item_name }}</option></select>
<input v-model.number="r.qty" type="number" class="col-span-2 inp !py-1 text-right"/><input v-model.number="r.rate" type="number" class="col-span-3 inp !py-1 text-right"/>
<button class="col-span-2 text-red-500 text-xs" @click="f.items.splice(i,1)">×</button></div></div>
<Button variant="subtle" size="sm" @click="f.items.push({item_code:'',qty:1,rate:0})">+ Thêm dòng</Button>
<div class="flex justify-end gap-2 mt-5"><Button variant="subtle" @click="show=false">Hủy</Button><Button variant="solid" theme="green" :loading="saving" @click="save">Lưu & Nhập kho</Button></div></div></div>
</div></template>
<script setup>
import { ref,reactive,computed } from 'vue'; import { Button,FeatherIcon,LoadingIndicator } from 'frappe-ui'; import { useFrappeApi,callApi } from '../composables/useFrappeApi'
const rows=ref([]),loading=ref(false),busy=ref(''),sup=ref('')
const { data:suppliers }=useFrappeApi('muahang.api.get_suppliers',{initialData:{suppliers:[]},params:{page_length:500}})
const { data:itemsR }=useFrappeApi('kho.api.get_items',{initialData:{items:[]},params:{page_length:500}})
const { data:warehouses }=useFrappeApi('kho.api.get_warehouses',{initialData:[]})
const itemOpts=computed(()=>itemsR.value?.items||[])
const stockWh=computed(()=>(warehouses.value||[]).filter(w=>!w.is_group))
async function reload(){loading.value=true;try{const r=await callApi('muahang.api.get_purchase_receipts',{supplier:sup.value},'GET');rows.value=r?.entries||[]}finally{loading.value=false}};reload()
const show=ref(false),saving=ref(false);const f=reactive({supplier:'',warehouse:'',items:[{item_code:'',qty:1,rate:0}]})
function openCreate(){f.supplier=suppliers.value?.suppliers?.[0]?.name||'';f.warehouse=stockWh.value?.[0]?.name||'';f.items=[{item_code:'',qty:1,rate:0}];show.value=true}
async function save(){const items=f.items.filter(r=>r.item_code&&r.qty);if(!items.length||!f.supplier){alert('Chọn NCC + ít nhất 1 dòng');return};saving.value=true;try{await callApi('muahang.api.create_purchase_receipt',{supplier:f.supplier,items:JSON.stringify(items),set_warehouse:f.warehouse,submit:1});show.value=false;await reload()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{saving.value=false}}
async function submit(r){busy.value=r.name;try{await callApi('muahang.api.submit_purchase_receipt',{name:r.name});await reload()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{busy.value=''}}
async function print(name){const h=await callApi('muahang.api.print_purchase_receipt',{name},'GET');const w=window.open('','_blank');w.document.write(h+'<script>window.onload=()=>window.print()<\/script>');w.document.close()}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
