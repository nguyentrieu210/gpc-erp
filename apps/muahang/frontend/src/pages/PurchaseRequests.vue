<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<PageHeader title="Đề nghị mua" icon="edit-3" icon-class="text-amber-600">
  <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Tạo đề nghị</button>
</PageHeader>
<main class="flex-1 p-4 max-w-4xl mx-auto w-full">
<DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm đề nghị…" :search-keys="['name']" @row-click="goDetail">
  <template #col-transaction_date="{ value }">{{ $fmtDate(value) }}</template>
  <template #col-docstatus="{ row }"><StatusBadge :status="row.docstatus === 1 ? 'Đã duyệt' : 'Nháp'" /></template>
</DataTable>
</main>
<FormModal :show="show" title="Đề nghị mua hàng" icon="edit-3" width="max-w-2xl" :saving="saving" hide-footer @close="show = false">
  <div class="space-y-3">
    <div><label class="text-xs text-gray-500">Ngày cần</label><input type="date" v-model="f.schedule_date" class="inp" /></div>
    <div><label class="text-xs text-gray-500">Mặt hàng</label><LineItemsEditor v-model="f.items" :show-uom="false" /></div>
  </div>
  <template #footer>
    <button class="btn-secondary px-4 py-2 rounded-lg text-sm" @click="show = false">Hủy</button>
    <button class="btn-primary px-4 py-2 rounded-lg text-sm font-medium" :disabled="saving" @click="save">{{ saving ? 'Đang lưu…' : 'Lưu & Gửi' }}</button>
  </template>
</FormModal>
<div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
</div></template>
<script setup>
import { ref,reactive } from 'vue'; import { useRouter } from 'vue-router'; import { FeatherIcon } from 'frappe-ui'
import { PageHeader,DataTable,FormModal,LineItemsEditor,StatusBadge,useToast,callApi,today } from '@shared'
const router = useRouter(); const { toast,ok,err } = useToast()
const rows = ref([]); const loading = ref(false)
const columns = [{ key:'name',label:'Số đề nghị' },{ key:'transaction_date',label:'Ngày' },{ key:'docstatus',label:'Trạng thái' }]
async function reload(){loading.value=true;try{rows.value=(await callApi('muahang.api.get_purchase_requests',{page_length:200},'GET'))?.entries||[]}finally{loading.value=false}};reload()
const show = ref(false); const saving = ref(false); const f = reactive({ schedule_date:today(),items:[] })
function openCreate(){f.schedule_date=today();f.items=[];show.value=true}
async function save(){const items=(f.items||[]).filter(l=>l.item_code&&l.qty);if(!items.length)return err('Thêm ít nhất 1 dòng');saving.value=true;try{await callApi('muahang.api.create_purchase_request',{items:JSON.stringify(items.map(l=>({item_code:l.item_code,qty:l.qty}))),schedule_date:f.schedule_date,submit:1});ok('Đã gửi đề nghị');show.value=false;reload()}catch(e){err(e?.message)}finally{saving.value=false}}
function goDetail(row){router.push('/purchase-requests/'+row.name)}
</script>
