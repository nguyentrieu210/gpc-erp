<template>
<DetailLayout :loading="loading" :title="doc?.asset_name||name" icon="tool" back="/assets"
  :heading="doc?.asset_name" :meta="doc?.asset_category" :status="doc?.status_vi" :amount="fmtVnd(doc?.purchase_amount)" amount-label="Nguyên giá" gradient="from-teal-600 to-cyan-600">
  <template #actions>
    <button v-if="doc?.status==='Submitted'||doc?.status==='Partially Depreciated'" class="btn-warning px-3 py-2 rounded-lg text-sm" @click="scrap">Ghi giảm</button>
    <button v-if="doc?.status==='Submitted'||doc?.status==='Partially Depreciated'" class="btn-danger px-3 py-2 rounded-lg text-sm" @click="sell">Bán</button>
  </template>
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Thông tin</div>
      <div class="space-y-1 text-sm">
        <div class="flex justify-between"><span class="text-gray-500">Mã TS</span><span class="font-medium">{{ doc?.name }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Loại</span><span>{{ doc?.asset_category }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Vị trí</span><span>{{ doc?.location||'—' }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Ngày mua</span><span>{{ $fmtDate(doc?.purchase_date) }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Ngày SD</span><span>{{ $fmtDate(doc?.available_for_use_date) }}</span></div>
        <div class="flex justify-between border-t pt-1 mt-1"><span class="text-gray-500">Nguyên giá</span><span class="font-bold">{{ fmtVnd(doc?.purchase_amount) }}</span></div>
      </div>
    </div>
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Khấu hao</div>
      <div class="space-y-1 text-sm" v-if="doc?.depreciation_schedule?.length">
        <div v-for="ds in doc.depreciation_schedule.slice(Math.max(0,doc.depreciation_schedule.length-6))" :key="ds.schedule_date" class="flex justify-between">
          <span class="text-gray-500">{{ $fmtDate(ds.schedule_date) }}</span>
          <span>{{ fmtVnd(ds.depreciation_amount) }}</span>
          <span class="text-gray-400">{{ fmtVnd(ds.accumulated_depreciation_amount) }}</span>
        </div>
      </div>
      <div v-else class="text-sm text-gray-400">Chưa có lịch khấu hao</div>
    </div>
  </div>
  <div class="app-card p-4" v-if="doc?.movements?.length">
    <div class="text-sm font-semibold mb-2">Điều chuyển</div>
    <div v-for="mv in doc.movements" :key="mv.name" class="flex items-center gap-2 py-1 text-sm"><span>{{ $fmtDate(mv.transaction_date) }}</span><span class="text-gray-400">{{ mv.source_location||'—' }}</span><span>→</span><span>{{ mv.target_location }}</span></div>
  </div>
  <template #sidebar>
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Bảo dưỡng</div>
      <div v-for="ml in doc?.maintenance_logs||[]" :key="ml.name" class="text-sm border-b last:border-0 py-1">
        <div class="font-medium">{{ ml.maintenance_type }} · {{ ml.task_name||'' }}</div>
        <div class="text-xs text-gray-500">{{ $fmtDate(ml.completion_date) }} · {{ ml.maintenance_status }}</div>
      </div>
      <div v-if="!(doc?.maintenance_logs||[]).length" class="text-sm text-gray-400">Chưa có</div>
    </div>
    <div class="app-card p-4"><div class="text-sm font-semibold mb-2">Hoạt động</div><ActivityTimeline :items="activity"/></div>
  </template>
  <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅')?'bg-emerald-50 text-emerald-800 border border-emerald-200':'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
</DetailLayout>
</template>
<script setup>
import { ref } from 'vue'; import { useRoute } from 'vue-router'
import { DetailLayout,ActivityTimeline,useToast,callApi,fmtVnd } from '@shared'
const route=useRoute(); const name=route.params.name; const { toast,ok,err }=useToast()
const doc=ref(null); const loading=ref(true); const activity=ref([])
async function load(){loading.value=true;try{doc.value=await callApi('taisan.api.get_asset',{name},'GET');activity.value=await callApi('taisan.api.get_doc_activity',{doctype:'Asset',name},'GET');if(doc.value)doc.value.status_vi={Submitted:'Đã ghi nhận','Partially Depreciated':'Đang KH','Fully Depreciated':'Hết KH',Scrapped:'Đã hủy',Sold:'Đã bán'}[doc.value.status]||doc.value.status}catch(e){err(e?.message)}finally{loading.value=false}};load()
async function scrap(){try{await callApi('taisan.api.scrap_asset',{name});ok('Đã ghi giảm');load()}catch(e){err(e?.message)}}
async function sell(){try{await callApi('taisan.api.sell_asset',{name});ok('Đã đánh dấu bán');load()}catch(e){err(e?.message)}}
</script>
