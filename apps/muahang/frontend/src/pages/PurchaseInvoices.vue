<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<PageHeader title="Hóa đơn mua (PI)" icon="file-plus" icon-class="text-violet-600">
  <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Tạo hóa đơn</button>
</PageHeader>
<main class="flex-1 p-4 max-w-5xl mx-auto w-full">
<DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm HĐ / NCC / số NCC…" :search-keys="['name','supplier_name','bill_no']" @row-click="goDetail">
  <template #col-grand_total="{ value }"><span class="font-semibold">{{ fmtVnd(value) }}</span></template>
  <template #col-outstanding_amount="{ value }"><span :class="value>0?'text-rose-600 font-medium':'text-emerald-600'">{{ value>0?fmtVnd(value):'Đã trả' }}</span></template>
  <template #col-posting_date="{ value }">{{ $fmtDate(value) }}</template>
</DataTable>
</main>
<FormModal :show="show" title="Hóa đơn mua" icon="file-plus" width="max-w-3xl" :saving="saving" hide-footer @close="show = false">
  <div class="space-y-3">
    <div class="grid grid-cols-2 gap-3">
      <div><label class="text-xs text-gray-500">Nhà cung cấp *</label><EntityPicker v-model="f.supplier" api="muahang.api.get_suppliers" result-key="suppliers" value-key="name" label-key="supplier_name" icon="user" /></div>
      <div><label class="text-xs text-gray-500">Số HĐ NCC</label><input v-model="f.bill_no" class="inp" /></div>
    </div>
    <div><label class="text-xs text-gray-500">Dòng hàng</label><LineItemsEditor v-model="f.items" /></div>
  </div>
  <template #footer>
    <button class="btn-secondary px-4 py-2 rounded-lg text-sm" @click="show = false">Hủy</button>
    <button class="btn-primary px-4 py-2 rounded-lg text-sm font-medium" :disabled="saving" @click="save">{{ saving ? 'Đang lưu…' : 'Lưu & Ghi sổ' }}</button>
  </template>
</FormModal>
<div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
</div></template>
<script setup>
import { ref,reactive } from 'vue'; import { useRouter } from 'vue-router'; import { FeatherIcon } from 'frappe-ui'
import { PageHeader,DataTable,FormModal,EntityPicker,LineItemsEditor,useToast,callApi,fmtVnd,today } from '@shared'
const router = useRouter(); const { toast,ok,err } = useToast()
const rows = ref([]); const loading = ref(false)
const columns = [{ key:'name',label:'Số HĐ' },{ key:'supplier_name',label:'NCC' },{ key:'bill_no',label:'Số NCC' },{ key:'posting_date',label:'Ngày' },{ key:'grand_total',label:'Tổng tiền',align:'right' },{ key:'outstanding_amount',label:'Còn nợ',align:'right' }]
async function reload(){loading.value=true;try{rows.value=(await callApi('muahang.api.get_purchase_invoices',{page_length:200},'GET'))?.entries||[]}finally{loading.value=false}};reload()
const show = ref(false); const saving = ref(false); const f = reactive({ supplier:'',bill_no:'',items:[] })
function openCreate(){f.supplier='';f.bill_no='';f.items=[];show.value=true}
async function save(){const items=(f.items||[]).filter(l=>l.item_code&&l.qty);if(!items.length||!f.supplier)return err('Chọn NCC + ít nhất 1 dòng');saving.value=true;try{await callApi('muahang.api.create_purchase_invoice',{supplier:f.supplier,items:JSON.stringify(items.map(l=>({item_code:l.item_code,qty:l.qty,rate:l.rate}))),bill_no:f.bill_no||undefined,submit:1});ok('Đã ghi sổ HĐ');show.value=false;reload()}catch(e){err(e?.message)}finally{saving.value=false}}
function goDetail(row){router.push('/purchase-invoices/'+row.name)}
</script>
