<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<PageHeader title="Danh sách TSCĐ" icon="list" icon-class="text-teal-600">
  <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4"/> Ghi nhận tài sản</button>
</PageHeader>
<main class="flex-1 p-4 max-w-6xl mx-auto w-full">
<DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm TS…" :search-keys="['name','asset_name','item_code']" :filters="filterDefs" @row-click="goDetail">
  <template #col-gross_purchase_amount="{ value }"><span class="font-semibold">{{ fmtVnd(value) }}</span></template>
  <template #col-net_book_value="{ value }"><span :class="value>0?'text-emerald-600':'text-gray-400'">{{ fmtVnd(value) }}</span></template>
  <template #col-status="{ row }"><StatusBadge :status="row.status_vi"/></template>
  <template #col-available_for_use_date="{ value }">{{ $fmtDate(value) }}</template>
</DataTable>
</main>
<FormModal :show="show" title="Ghi nhận tài sản mới" icon="plus-circle" width="max-w-md" :saving="saving" @close="show=false" @save="save">
  <div class="space-y-3">
    <div><label class="text-xs text-gray-500">Tên tài sản *</label><input v-model="f.asset_name" class="inp"/></div>
    <div><label class="text-xs text-gray-500">Loại TSCĐ *</label><EntityPicker v-model="f.asset_category" api="taisan.api.get_asset_categories" result-key="entries" value-key="name" label-key="asset_category_name"/></div>
    <div><label class="text-xs text-gray-500">Mã hàng (Item)*</label><EntityPicker v-model="f.item_code" api="kho.api.get_items" result-key="items" value-key="item_code" label-key="item_name" sub-key="item_code"/></div>
    <div class="grid grid-cols-2 gap-3">
      <div><label class="text-xs text-gray-500">Nguyên giá *</label><input v-model.number="f.gross_purchase_amount" type="number" class="inp"/></div>
      <div><label class="text-xs text-gray-500">Ngày đưa vào SD</label><input v-model="f.available_for_use_date" type="date" class="inp"/></div>
    </div>
    <div><label class="text-xs text-gray-500">Vị trí</label><EntityPicker v-model="f.location" api="taisan.api.get_locations" result-key="entries" value-key="name" label-key="location_name"/></div>
  </div>
</FormModal>
<div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅')?'bg-emerald-50 text-emerald-800 border border-emerald-200':'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
</div>
</template>
<script setup>
import { ref,reactive } from 'vue'; import { useRouter } from 'vue-router'; import { FeatherIcon } from 'frappe-ui'
import { PageHeader,DataTable,FormModal,EntityPicker,StatusBadge,useToast,callApi,fmtVnd,today } from '@shared'
const router=useRouter(); const { toast,ok,err }=useToast()
const rows=ref([]); const loading=ref(false)
const columns=[
  {key:'name',label:'Mã TS'},{key:'asset_name',label:'Tên tài sản'},{key:'asset_category',label:'Loại'},
  {key:'purchase_amount',label:'Nguyên giá',align:'right'},{key:'net_book_value',label:'Giá trị còn lại',align:'right'},
  {key:'available_for_use_date',label:'Ngày SD'},{key:'status',label:'Trạng thái'},
]
const filterDefs=[{key:'status',label:'Trạng thái',options:[
  {value:'Submitted',label:'Đã ghi nhận'},{value:'Partially Depreciated',label:'Đang KH'},
  {value:'Fully Depreciated',label:'Hết KH'},{value:'Scrapped',label:'Đã hủy'},{value:'Sold',label:'Đã bán'},
]}]
async function reload(){loading.value=true;try{rows.value=(await callApi('taisan.api.get_assets',{page_length:200},'GET'))?.entries||[]}finally{loading.value=false}};reload()
const show=ref(false); const saving=ref(false)
const f=reactive({asset_name:'',asset_category:'',item_code:'',gross_purchase_amount:0,available_for_use_date:today(),location:''})
function openCreate(){Object.assign(f,{asset_name:'',asset_category:'',item_code:'',gross_purchase_amount:0,available_for_use_date:today(),location:''});show.value=true}
async function save(){if(!f.asset_name||!f.asset_category||!f.item_code)return err('Nhập tên + loại TS + mã hàng');saving.value=true;try{await callApi('taisan.api.create_asset',{...f,gross_purchase_amount:f.gross_purchase_amount||0,item_code:f.item_code,submit:1});ok('Đã ghi nhận TS');show.value=false;reload()}catch(e){err(e?.message)}finally{saving.value=false}}
function goDetail(row){router.push('/assets/'+row.name)}
</script>
