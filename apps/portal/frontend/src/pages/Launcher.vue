<template>
<div class="min-h-screen bg-gray-50">
  <header class="flex items-center justify-between border-b bg-white px-4 sm:px-6 py-3 sticky top-0 z-30 shadow-sm">
    <div class="flex items-center gap-3">
      <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white shrink-0">G</div>
      <span class="text-lg font-bold text-gray-900 hidden sm:inline">GPC ERP</span>
    </div>
    <!-- Global Search -->
    <div class="relative flex-1 max-w-lg mx-4">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input v-model="q" @input="doSearch" @keydown.escape="q='';results=[]" @focus="q.length>=2&&doSearch()"
               placeholder="Ctrl+K — Tìm kiếm mọi thứ (hàng hóa, NCC, KH, đơn hàng, NV...)" class="w-full rounded-xl border border-gray-300 pl-9 pr-4 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"/>
        <button v-if="q" @click="q='';results=[]" class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400"><FeatherIcon name="x" class="h-4 w-4"/></button>
      </div>
      <div v-if="results.length" class="absolute top-full mt-1 left-0 right-0 bg-white rounded-xl border shadow-xl max-h-[70vh] overflow-y-auto z-50">
        <div v-for="r in results" :key="r.doctype+':'+r.name" class="px-3 py-2 hover:bg-blue-50 cursor-pointer border-b last:border-0 flex items-center gap-3" @click="goResult(r)">
          <span class="text-[10px] px-1.5 py-0.5 rounded font-medium shrink-0 bg-gray-100 text-gray-600">{{ r.label_vi }}</span>
          <div class="flex-1 min-w-0"><div class="text-sm font-medium truncate">{{ r.display }}</div><div class="text-xs text-gray-400 truncate">{{ r.detail }}</div></div>
          <FeatherIcon name="arrow-right" class="h-3 w-3 text-gray-300"/>
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 shrink-0">
      <span class="text-sm text-gray-600 hidden sm:inline">{{ user?.full_name||'' }}</span>
      <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600">Đăng xuất</Button>
    </div>
  </header>

  <main class="mx-auto max-w-6xl px-4 sm:px-6 py-6 space-y-6">
    <!-- KPI row -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="rounded-xl border bg-white p-3 text-center shadow-sm hover:shadow-md cursor-pointer" @click="goApp('/kinhdoanh_app')"><div class="text-xl font-bold text-rose-600">{{ fmtShort(db.sales?.revenue_mtd) }}</div><div class="text-xs text-gray-500">Doanh thu tháng</div></div>
      <div class="rounded-xl border bg-white p-3 text-center shadow-sm hover:shadow-md cursor-pointer" @click="goApp('/kinhdoanh_app/receivables')"><div class="text-xl font-bold" :class="db.sales?.receivables?'text-red-600':'text-gray-400'">{{ fmtShort(db.sales?.receivables) }}</div><div class="text-xs text-gray-500">Phải thu KH</div></div>
      <div class="rounded-xl border bg-white p-3 text-center shadow-sm hover:shadow-md cursor-pointer" @click="goApp('/muahang_app/payables')"><div class="text-xl font-bold" :class="db.purchasing?.payables?'text-amber-600':'text-gray-400'">{{ fmtShort(db.purchasing?.payables) }}</div><div class="text-xs text-gray-500">Phải trả NCC</div></div>
      <div class="rounded-xl border bg-white p-3 text-center shadow-sm hover:shadow-md cursor-pointer" @click="goApp('/kho_app/balance')"><div class="text-xl font-bold text-emerald-600">{{ fmtShort(db.stock?.value) }}</div><div class="text-xs text-gray-500">Giá trị tồn kho</div></div>
    </div>

    <!-- Modules + Recent -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="lg:col-span-2">
        <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Phân hệ</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <a v-for="m in modules" :key="m.route_key" :href="m.subdomain_url" class="group flex items-center gap-3 rounded-xl border bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0" :style="{backgroundColor:m.color||'#2563eb'}"><FeatherIcon :name="m.icon||'grid'" class="h-5 w-5 text-white"/></div>
            <div class="flex-1 min-w-0"><div class="font-semibold text-gray-900 text-sm group-hover:text-blue-600 transition">{{ m.module_name }}</div><div class="text-xs text-gray-500 mt-0.5">{{ m.description }}</div></div>
            <div class="text-right shrink-0"><div class="text-xs font-bold" :style="{color:m.color||'#2563eb'}">{{ m._stat||'' }}</div></div>
          </a>
        </div>
      </div>
      <div class="rounded-xl border bg-white p-4">
        <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Gần đây</h3>
        <div v-if="!db.recent?.length" class="py-6 text-center text-xs text-gray-400">Chưa có giao dịch</div>
        <div v-for="r in db.recent" :key="r._doctype+':'+r.name" class="flex items-center gap-2 py-2 border-b last:border-0 text-sm cursor-pointer hover:bg-gray-50" @click="goDoc(r)">
          <span class="text-[10px] px-1.5 py-0.5 rounded font-medium shrink-0 bg-gray-100 text-gray-600">{{ dtTag(r._doctype) }}</span>
          <div class="flex-1 min-w-0"><div class="truncate text-xs font-medium">{{ r.name }}</div><div class="text-[10px] text-gray-400 truncate">{{ r.customer_name||r.supplier_name||r.lead_name||r.user_remark||r.stock_entry_type||'' }}</div></div>
          <div class="text-xs font-semibold text-right" v-if="r.grand_total">{{ fmtShort(r.grand_total) }}</div>
        </div>
      </div>
    </div>

    <!-- Bottom stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="rounded-xl border bg-white p-3 text-center cursor-pointer hover:shadow-md" @click="goApp('/hr_app')"><div class="text-base font-bold text-indigo-600">{{ db.hr?.employees||0 }}</div><div class="text-xs text-gray-500">Nhân viên</div><div class="text-[10px] text-gray-400 mt-0.5">{{ db.hr?.present||0 }} có mặt - {{ db.hr?.on_leave||0 }} nghỉ</div></div>
      <div class="rounded-xl border bg-white p-3 text-center cursor-pointer hover:shadow-md" @click="goApp('/crm_app')"><div class="text-base font-bold text-violet-600">{{ db.crm?.leads_open||0 }} / {{ db.crm?.opps_open||0 }}</div><div class="text-xs text-gray-500">Lead / Co hoi</div></div>
      <div class="rounded-xl border bg-white p-3 text-center cursor-pointer hover:shadow-md" @click="goApp('/kho_app/reorder')"><div class="text-base font-bold" :class="db.stock?.low?'text-red-600':'text-gray-400'">{{ db.stock?.low||0 }}</div><div class="text-xs text-gray-500">Sap het hang</div></div>
      <div class="rounded-xl border bg-white p-3 text-center cursor-pointer hover:shadow-md" @click="goApp('/tckt_app')"><div class="text-base font-bold text-green-600">{{ db.finance?.je_count||0 }}</div><div class="text-xs text-gray-500">Phieu ke toan</div><div class="text-[10px] text-gray-400 mt-0.5">{{ db.finance?.gl_count||0 }} but toan</div></div>
    </div>
  </main>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, FeatherIcon, frappeRequest } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'
const loggingOut=ref(false)
const {data:modules}=useFrappeApi('portal.api.get_my_modules',{initialData:[],onError:()=>{}})
const {data:user}=useFrappeApi('portal.api.get_current_user')
const db=ref({}),q=ref(''),results=ref([])
async function loadDash(){try{const res=await frappeRequest({url:'portal.api.get_unified_dashboard',method:'GET'});db.value=res;(modules.value||[]).forEach(md=>{if(md.route_key==='hr')md._stat=(db.value.hr?.employees||0)+' NV';else if(md.route_key==='kho')md._stat=fmtShort(db.value.stock?.value);else if(md.route_key==='muahang')md._stat=fmtShort(db.value.purchasing?.payables)+' no';else if(md.route_key==='kinhdoanh')md._stat=fmtShort(db.value.sales?.revenue_mtd)+' DT';else if(md.route_key==='tckt')md._stat=(db.value.finance?.je_count||0)+' phieu';else if(md.route_key==='crm_ui')md._stat=(db.value.crm?.leads_open||0)+' lead'})}catch{}}
onMounted(loadDash)
let st
function doSearch(){clearTimeout(st);if(q.value.length<2){results.value=[];return};st=setTimeout(async()=>{try{const r=await frappeRequest({url:'portal.api.global_search',method:'GET',params:{q:q.value}});results.value=r?.results||[]}catch{}},250)}
function goResult(r){q.value='';results.value=[];window.location.href=r.url}
function goDoc(r){const dt=r._doctype;let url='';if(dt==='Purchase Order')url='/muahang_app/po/'+encodeURIComponent(r.name);else if(dt==='Sales Order')url='/kinhdoanh_app/sales-orders';else if(dt==='Stock Entry')url='/kho_app/stock-entries';else if(dt==='Journal Entry')url='/tckt_app/journal-entries';else if(dt==='Sales Invoice')url='/kinhdoanh_app/sales-invoices';else if(dt==='Purchase Invoice')url='/muahang_app/purchase-invoices';else if(dt==='Lead')url='/crm_app/leads';if(url)window.location.href=url}
function goApp(p){window.location.href=p}
function dtTag(dt){if(dt==='Sales Order')return'SO';if(dt==='Purchase Order')return'PO';if(dt==='Stock Entry')return'Kho';if(dt==='Journal Entry')return'KT';if(dt==='Sales Invoice')return'SI';if(dt==='Purchase Invoice')return'PI';if(dt==='Lead')return'Lead';return dt.slice(0,4)}
async function logout(){loggingOut.value=true;try{await frappeRequest({url:'logout',method:'POST'})}catch{};document.cookie.split(";").forEach(c=>{const n=c.indexOf("=")>-1?c.substr(0,c.indexOf("=")).trim():c.trim();document.cookie=n+"=;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/"});window.location.href='/portal_app/login'}
function fmtShort(v){v=Number(v||0);if(v>=1e9)return (v/1e9).toFixed(1)+' ty';if(v>=1e6)return (v/1e6).toFixed(1)+' tr';return v.toLocaleString('vi-VN')}
</script>
