<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10">
<button class="text-gray-500 hover:text-gray-800" @click="$router.push('/purchase-orders')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button>
<FeatherIcon name="file-text" class="h-5 w-5 text-sky-600"/><h1 class="text-lg font-bold text-gray-900 flex-1 truncate">{{ po?.name || id }}</h1>
<div class="flex gap-1"><Button variant="subtle" @click="print">In</Button></div>
</header>
<main class="flex-1 p-4 max-w-3xl mx-auto w-full space-y-4">
<div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<template v-else-if="po">
<div class="rounded-xl border bg-white p-4"><div class="flex justify-between mb-3"><div><div class="text-sm text-gray-500">Nhà cung cấp</div><div class="font-semibold">{{ po.supplier_name }}</div></div>
<div class="text-right"><div class="text-sm text-gray-500">Ngày đặt</div><div class="font-semibold">{{ $fmtDate(po.transaction_date) }}</div></div>
<div><div class="text-sm text-gray-500">Trạng thái</div><span class="text-sm px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">{{ po.status_vi }}</span></div></div>
<div class="border-t pt-3"><table class="w-full text-sm"><thead><tr class="text-left text-xs text-gray-500"><th class="py-1">Hàng</th><th class="text-right">SL</th><th class="text-right">Đơn giá</th><th class="text-right">T.tiền</th></tr></thead>
<tbody><tr v-for="it in po.items" :key="it.name" class="border-t"><td class="py-1.5">{{ it.item_code }}<br/><span class="text-xs text-gray-400">{{ it.item_name }}</span></td><td class="text-right">{{ it.qty }}</td><td class="text-right">{{ fmtVnd(it.rate) }}</td><td class="text-right">{{ fmtVnd(it.amount) }}</td></tr></tbody></table></div>
<div class="border-t pt-2 mt-2 flex justify-between text-sm"><span>{{ po.total_taxes_and_charges>0 ? 'Đã gồm thuế GTGT' : '' }}</span><span class="font-bold text-base">{{ fmtVnd(po.grand_total) }}</span></div></div>
<div class="flex gap-2"><Button v-if="po.docstatus===1&&po.per_received<100" variant="solid" theme="emerald" :loading="busy==='pr'" @click="makePR">Tạo phiếu nhập (PR)</Button>
<Button v-if="po.docstatus===1&&po.per_billed<100" variant="solid" theme="violet" :loading="busy==='pi'" @click="makePI">Tạo hóa đơn (PI)</Button>
<Button v-if="po.docstatus===0" variant="solid" theme="green" :loading="busy==='sub'" @click="submit">Chốt đơn</Button></div>
<!-- Linked docs -->
<div v-if="links" class="rounded-xl border bg-white"><div class="px-4 py-3 border-b font-medium text-gray-700">Chứng từ liên quan</div>
<div v-if="links.receipts?.length" class="px-4 py-2 border-t"><div class="text-xs font-medium text-gray-500 mb-1">Phiếu nhập mua</div>
<div v-for="r in links.receipts" :key="r.name" class="flex items-center py-1 text-sm"><div class="flex-1">{{ r.name }} · {{ r.supplier_name }} · {{ $fmtDate(r.posting_date) }}</div><div class="font-semibold">{{ fmtVnd(r.grand_total) }}</div><span class="ml-2 text-xs" :class="r.docstatus===1?'text-emerald-600':'text-amber-600'">{{ r.docstatus===1?'Da nhap':'Nhap' }}</span></div></div>
<div v-if="links.invoices?.length" class="px-4 py-2 border-t"><div class="text-xs font-medium text-gray-500 mb-1">Hoa don mua</div>
<div v-for="r in links.invoices" :key="r.name" class="flex items-center py-1 text-sm"><div class="flex-1">{{ r.name }} · {{ r.supplier_name }} · {{ $fmtDate(r.posting_date) }}</div><div class="font-semibold">{{ fmtVnd(r.grand_total) }}</div><span v-if="r.outstanding_amount>0" class="ml-2 text-xs text-red-600">Con {{ fmtVnd(r.outstanding_amount) }}</span></div></div>
<div v-if="!links.receipts?.length && !links.invoices?.length" class="px-4 py-6 text-center text-gray-400 text-sm">Chua co chung tu lien quan</div></div>
<div v-if="msg" class="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{{ msg }}</div>
</template></main></div></template>
<script setup>
import { ref } from 'vue'; import { useRoute } from 'vue-router'; import { Button,FeatherIcon,LoadingIndicator } from 'frappe-ui'; import { callApi } from '../composables/useFrappeApi'
const route=useRoute(); const id=decodeURIComponent(route.params.id); const po=ref(null),links=ref(null),loading=ref(true),busy=ref(''),msg=ref('')
async function load(){loading.value=true;try{po.value=await callApi('muahang.api.get_purchase_order',{name:id},'GET');links.value=await callApi('muahang.api.get_linked_docs',{doctype:'Purchase Order',name:id},'GET')}finally{loading.value=false}};load()
async function submit(){busy.value='sub';try{await callApi('muahang.api.submit_purchase_order',{name:id});await load()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{busy.value=''}}
async function makePR(){busy.value='pr';try{const r=await callApi('muahang.api.make_purchase_receipt_from_po',{name:id,submit:1});msg.value='Đã tạo phiếu nhập: '+r.name}catch(e){alert('Lỗi: '+(e?.message||e))}finally{busy.value=''}}
async function makePI(){busy.value='pi';try{const r=await callApi('muahang.api.make_purchase_invoice_from_po',{name:id,submit:1});msg.value='Đã tạo hóa đơn: '+r.name}catch(e){alert('Lỗi: '+(e?.message||e))}finally{busy.value=''}}
async function print(){const h=await callApi('muahang.api.print_purchase_order',{name:id},'GET');const w=window.open('','_blank');w.document.write(h+'<script>window.onload=()=>window.print()<\/script>');w.document.close()}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
