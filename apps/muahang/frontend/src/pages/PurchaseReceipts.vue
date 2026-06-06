<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<PageHeader title="Nhập mua (PR)" icon="truck" icon-class="text-emerald-600">
  <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Tạo phiếu</button>
</PageHeader>
<main class="flex-1 p-4 max-w-5xl mx-auto w-full">
<DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm phiếu nhập / NCC…" :search-keys="['name','supplier_name']" @row-click="goDetail">
  <template #col-grand_total="{ value }"><span class="font-semibold">{{ fmtVnd(value) }}</span></template>
  <template #col-docstatus="{ row }"><StatusBadge :status="row.docstatus === 1 ? 'Đã nhập' : 'Nháp'" /></template>
  <template #col-posting_date="{ value }">{{ $fmtDate(value) }}</template>
</DataTable>
</main>
<FormModal :show="show" title="Phiếu nhập mua" icon="truck" width="max-w-3xl" :saving="saving" hide-footer @close="show = false">
  <div class="space-y-3">
    <div class="grid grid-cols-2 gap-3">
      <div><label class="text-xs text-gray-500">Nhà cung cấp *</label><EntityPicker v-model="f.supplier" api="muahang.api.get_suppliers" result-key="suppliers" value-key="name" label-key="supplier_name" icon="user" /></div>
      <div><label class="text-xs text-gray-500">Kho nhập</label><EntityPicker v-model="f.warehouse" api="kho.api.get_warehouses" result-key="" value-key="name" label-key="warehouse_name" icon="home" /></div>
    </div>
    <div><label class="text-xs text-gray-500">Dòng hàng</label><LineItemsEditor v-model="f.items" /></div>
  </div>
  <template #footer>
    <button class="btn-secondary px-4 py-2 rounded-lg text-sm" @click="show = false">Hủy</button>
    <button class="btn-primary px-4 py-2 rounded-lg text-sm font-medium" :disabled="saving" @click="save">{{ saving ? 'Đang lưu…' : 'Lưu & Nhập kho' }}</button>
  </template>
</FormModal>
<div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
</div></template>
<script setup>
import { ref,reactive } from 'vue'; import { useRouter } from 'vue-router'; import { FeatherIcon } from 'frappe-ui'
import { PageHeader,DataTable,FormModal,EntityPicker,LineItemsEditor,StatusBadge,useToast,callApi,fmtVnd,today } from '@shared'
const router = useRouter(); const { toast,ok,err } = useToast()
const rows = ref([]); const loading = ref(false)
const columns = [{ key:'name',label:'Số PR' },{ key:'supplier_name',label:'NCC' },{ key:'posting_date',label:'Ngày' },{ key:'grand_total',label:'Tổng tiền',align:'right' },{ key:'docstatus',label:'Trạng thái' }]
async function reload(){loading.value=true;try{rows.value=(await callApi('muahang.api.get_purchase_receipts',{page_length:200},'GET'))?.entries||[]}finally{loading.value=false}};reload()
const show = ref(false); const saving = ref(false); const f = reactive({ supplier:'',warehouse:'',items:[] })
function openCreate(){f.supplier='';f.warehouse='';f.items=[];show.value=true}
async function save(){const items=(f.items||[]).filter(l=>l.item_code&&l.qty);if(!items.length||!f.supplier)return err('Chọn NCC + ít nhất 1 dòng');saving.value=true;try{await callApi('muahang.api.create_purchase_receipt',{supplier:f.supplier,items:JSON.stringify(items.map(l=>({item_code:l.item_code,qty:l.qty,rate:l.rate}))),set_warehouse:f.warehouse||undefined,submit:1});ok('Đã nhập kho');show.value=false;reload()}catch(e){err(e?.message)}finally{saving.value=false}}
function goDetail(row){router.push('/purchase-receipts/'+row.name)}
</script>
