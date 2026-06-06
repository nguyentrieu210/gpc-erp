<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
<button class="text-gray-500 hover:text-gray-800" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button>
<FeatherIcon name="file-text" class="h-5 w-5 text-sky-600"/><h1 class="text-lg font-bold text-gray-900 flex-1">Đơn mua (PO)</h1>
<Button variant="solid" theme="sky" @click="openCreate">+ Tạo PO</Button>
</header>
<main class="flex-1 p-4 max-w-5xl mx-auto w-full">
<div class="flex flex-wrap gap-2 mb-3">
<div class="flex gap-1 overflow-x-auto"><button v-for="st in stFilters" :key="st.value" class="px-3 py-1.5 rounded-full text-sm border whitespace-nowrap" :class="st0===st.value?'bg-sky-600 text-white border-sky-600':'bg-white text-gray-600'" @click="st0=st.value;page=1;reload()">{{ st.label }}</button></div>
<select v-model="sup" @change="reload" class="inp w-auto"><option value="">Tất cả NCC</option><option v-for="s in suppliers" :key="s.name" :value="s.name">{{ s.supplier_name }}</option></select></div>
<div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có đơn mua</div>
<div v-for="po in rows" :key="po.name" class="flex items-center px-4 py-3 hover:bg-gray-50 cursor-pointer" @click="$router.push('/po/'+encodeURIComponent(po.name))">
<div class="flex-1 min-w-0"><div class="font-medium">{{ po.name }} <span class="text-xs px-2 py-0.5 rounded-full" :class="poBadge(po.status)">{{ po.status_vi }}</span></div>
<div class="text-xs text-gray-500">{{ po.supplier_name }} · {{ $fmtDate(po.transaction_date) }}<span v-if="po.per_received>0"> · Nhận {{ po.per_received }}%</span></div></div>
<div class="text-right shrink-0"><div class="font-semibold">{{ fmtVnd(po.grand_total) }}</div>
<div class="flex gap-2 mt-1"><Button v-if="po.docstatus===0" variant="solid" theme="green" size="sm" :loading="busy===po.name" @click.stop="submit(po)">Chốt</Button>
<Button variant="subtle" size="sm" @click.stop="print(po.name)">In</Button></div></div></div></div>
<div v-if="total>pl" class="flex justify-between mt-3 text-sm text-gray-600"><span>{{ total }} PO · {{ page }}/{{ pages }}</span><div class="flex gap-2"><Button variant="subtle" :disabled="page<=1" @click="page--;reload()">‹</Button><Button variant="subtle" :disabled="page>=pages" @click="page++;reload()">›</Button></div></div>
</main>
<div v-if="show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="show=false"><div class="bg-white rounded-xl w-full max-w-2xl p-5 max-h-[92vh] overflow-y-auto">
<h3 class="text-lg font-semibold mb-4">Tạo đơn mua</h3>
<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
<label class="block"><span class="text-sm text-gray-600 block mb-1">Nhà cung cấp *</span><select v-model="f.supplier" class="inp"><option value="">— chọn —</option><option v-for="s in suppliers" :key="s.name" :value="s.name">{{ s.supplier_name }}</option></select></label>
<label class="block"><span class="text-sm text-gray-600 block mb-1">Ngày đặt</span><input type="date" v-model="f.transaction_date" class="inp"/></label></div>
<div class="border rounded-lg overflow-hidden mb-3"><div class="grid grid-cols-12 gap-1 bg-gray-50 px-2 py-1.5 text-xs font-medium text-gray-500"><div class="col-span-5">Hàng hóa</div><div class="col-span-2 text-right">SL</div><div class="col-span-3 text-right">Đơn giá</div><div class="col-span-2"></div></div>
<div v-for="(r,i) in f.items" :key="i" class="grid grid-cols-12 gap-1 px-2 py-1.5 items-center border-t">
<select v-model="r.item_code" class="col-span-5 inp !py-1 !text-xs"><option value="">— chọn —</option><option v-for="it in itemOpts" :key="it.name" :value="it.item_code">{{ it.item_name }}</option></select>
<input v-model.number="r.qty" type="number" class="col-span-2 inp !py-1 text-right"/>
<input v-model.number="r.rate" type="number" class="col-span-3 inp !py-1 text-right"/>
<button class="col-span-2 text-red-500 text-xs" @click="f.items.splice(i,1)">×</button></div></div>
<Button variant="subtle" size="sm" @click="f.items.push({item_code:'',qty:1,rate:0})">+ Thêm dòng</Button>
<label class="flex items-center gap-2 mt-3 text-sm"><input type="checkbox" v-model="f.apply_tax"/> Áp thuế GTGT mặc định</label>
<div class="flex justify-end gap-2 mt-5"><Button variant="subtle" @click="show=false">Hủy</Button><Button variant="outline" :loading="saving" @click="save(0)">Lưu nháp</Button><Button variant="solid" theme="green" :loading="saving" @click="save(1)">Lưu & Chốt</Button></div></div></div>
</div></template>
<script setup>
import { ref,reactive,computed } from 'vue'; import { Button,FeatherIcon,LoadingIndicator } from 'frappe-ui'; import { useFrappeApi,callApi } from '../composables/useFrappeApi'
const rows=ref([]),total=ref(0),pages=ref(1),page=ref(1),loading=ref(false),busy=ref(''),st0=ref(''),sup=ref(''),pl=20
const { data:suppliers }=useFrappeApi('muahang.api.get_suppliers',{initialData:{suppliers:[]},params:{page_length:500}})
const { data:itemsR }=useFrappeApi('kho.api.get_items',{initialData:{items:[]},params:{page_length:500}})
const itemOpts=computed(()=>itemsR.value?.items||[])
const stFilters=[{value:'',label:'Tất cả'},{value:'Draft',label:'Nháp'},{value:'To Receive and Bill',label:'Chờ nhận & HĐ'},{value:'To Receive',label:'Chờ nhận'},{value:'Completed',label:'Hoàn tất'}]
async function reload(){loading.value=true;try{const r=await callApi('muahang.api.get_purchase_orders',{status:st0.value,supplier:sup.value,page:page.value,page_length:pl},'GET');rows.value=r?.entries||[];total.value=r?.total||0;pages.value=r?.pages||1}finally{loading.value=false}};reload()
const show=ref(false),saving=ref(false);const f=reactive({supplier:'',transaction_date:new Date().toISOString().slice(0,10),apply_tax:true,items:[{item_code:'',qty:1,rate:0}]})
function openCreate(){Object.assign(f,{supplier:suppliers.value?.suppliers?.[0]?.name||'',transaction_date:new Date().toISOString().slice(0,10),apply_tax:true,items:[{item_code:'',qty:1,rate:0}]});show.value=true}
async function save(s){const items=f.items.filter(r=>r.item_code&&r.qty);if(!items.length||!f.supplier){alert('Chọn NCC + ít nhất 1 dòng hàng');return};saving.value=true;try{await callApi('muahang.api.create_purchase_order',{supplier:f.supplier,items:JSON.stringify(items),transaction_date:f.transaction_date,apply_tax:f.apply_tax?1:0,submit:s});show.value=false;page.value=1;await reload()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{saving.value=false}}
async function submit(po){busy.value=po.name;try{await callApi('muahang.api.submit_purchase_order',{name:po.name});await reload()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{busy.value=''}}
async function print(name){const h=await callApi('muahang.api.print_purchase_order',{name},'GET');const w=window.open('','_blank');w.document.write(h+'<script>window.onload=()=>window.print()<\/script>');w.document.close()}
function poBadge(s){return{Completed:'bg-emerald-100 text-emerald-700',Draft:'bg-gray-100 text-gray-600','To Receive and Bill':'bg-amber-100 text-amber-700','To Receive':'bg-sky-100 text-sky-700'}[s]||'bg-gray-100 text-gray-600'}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
