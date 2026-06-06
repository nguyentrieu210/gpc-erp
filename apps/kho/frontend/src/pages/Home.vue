<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center justify-between border-b bg-white px-4 py-3 sticky top-0 z-20">
  <div class="flex items-center gap-2"><FeatherIcon name="package" class="h-5 w-5 text-orange-600"/><h1 class="text-lg font-bold text-gray-900">Kho</h1></div>
  <div class="flex items-center gap-3">
    <Button variant="subtle" @click="goPortal" class="flex items-center gap-1"><FeatherIcon name="arrow-left" class="h-4 w-4"/><span>Cổng</span></Button>
    <div class="h-4 w-px bg-gray-200"/><span class="text-sm text-gray-600 font-medium">{{ user?.full_name||'Administrator' }}</span>
    <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600">Đăng xuất</Button>
  </div>
</header>
<main class="flex-1 p-4 max-w-6xl mx-auto w-full space-y-6">
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
    <StatCard label="Mặt hàng" :value="d?.total_items??0" icon="package" tone="orange" to="/items"/>
    <StatCard label="Giá trị tồn" :value="fmtShort(d?.total_stock_value)" icon="dollar-sign" tone="emerald" to="/balance"/>
    <StatCard label="Kho / Vị trí" :value="d?.warehouse_count??0" icon="home" tone="blue" to="/warehouses"/>
    <StatCard label="Hàng sắp hết" :value="d?.low_stock_count??0" icon="alert-triangle" :tone="(d?.low_stock_count)?'rose':'gray'" to="/reorder"/>
  </div>
  <div v-if="setup&&!setup.ready" class="app-card p-4 flex items-start gap-3 border-amber-200 bg-amber-50/50">
    <FeatherIcon name="alert-triangle" class="h-5 w-5 text-amber-600 shrink-0 mt-0.5"/>
    <div class="flex-1 text-sm text-amber-800"><div class="font-bold">Chưa cấu hình hạch toán kho</div><div class="text-xs mt-0.5">Cần bật Perpetual Inventory và chỉ định tài khoản kho.</div></div>
    <Button variant="solid" theme="orange" @click="$router.push('/setup')">Cấu hình</Button>
  </div>
  <div class="space-y-6">
    <div v-for="cat in categories" :key="cat.title" class="space-y-3">
      <div class="border-l-4 border-orange-400 pl-3"><h2 class="text-sm font-bold text-gray-900">{{ cat.title }}</h2><p class="text-xs text-gray-500">{{ cat.desc }}</p></div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="m in cat.items" :key="m.key" class="app-card-interactive p-5" @click="$router.push(m.route)">
          <div class="flex items-start gap-3"><div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0" :class="m.bg"><FeatherIcon :name="m.icon" class="h-5 w-5" :class="m.color"/></div><div class="flex-1 min-w-0"><h3 class="font-semibold text-sm">{{ m.name }}</h3><p class="text-xs text-gray-500 mt-1">{{ m.desc }}</p></div></div>
        </div>
      </div>
    </div>
  </div>
</main>
</div>
</template>
<script setup>
import { ref } from 'vue'
import { Button,FeatherIcon } from 'frappe-ui'
import { useFrappeApi,StatCard } from '@shared'
const { data:d }=useFrappeApi('kho.api.get_stock_value_dashboard',{initialData:{}})
const { data:setup }=useFrappeApi('kho.api.get_kho_setup_status',{initialData:null})
const { data:user }=useFrappeApi('portal.api.get_current_user')
const loggingOut=ref(false)
const categories=[
  {title:'1. Danh mục & Cấu trúc',desc:'Hàng hóa, sơ đồ kho, lô/serial.',
   items:[
    {key:'items',name:'Hàng hóa',desc:'Danh mục, ĐVT, nhãn hiệu',icon:'package',color:'text-orange-600',bg:'bg-orange-100',route:'/items'},
    {key:'warehouses',name:'Sơ đồ kho',desc:'Cây kho phân cấp',icon:'home',color:'text-blue-600',bg:'bg-blue-100',route:'/warehouses'},
    {key:'batches',name:'Lô & Serial',desc:'Theo dõi lô, hạn dùng',icon:'layers',color:'text-purple-600',bg:'bg-purple-100',route:'/items'},
   ]},
  {title:'2. Giao dịch kho',desc:'Nhập/Xuất/Chuyển, kiểm kê, yêu cầu vật tư.',
   items:[
    {key:'entries',name:'Phiếu kho',desc:'Nhập/Xuất/Chuyển kho',icon:'repeat',color:'text-violet-600',bg:'bg-violet-100',route:'/stock-entries'},
    {key:'recon',name:'Kiểm kê',desc:'Đối chiếu tồn thực tế',icon:'check-square',color:'text-teal-600',bg:'bg-teal-100',route:'/reconciliation'},
    {key:'mr',name:'Yêu cầu vật tư',desc:'Đề nghị cấp phát/mua',icon:'file-text',color:'text-rose-600',bg:'bg-rose-100',route:'/material-requests'},
   ]},
  {title:'3. Báo cáo',desc:'Cân đối tồn, thẻ kho, định mức.',
   items:[
    {key:'balance',name:'Cân đối tồn',desc:'SL & giá trị tồn mỗi kho',icon:'pie-chart',color:'text-emerald-600',bg:'bg-emerald-100',route:'/balance'},
    {key:'ledger',name:'Thẻ kho',desc:'Lịch sử nhập xuất từng mặt hàng',icon:'book-open',color:'text-cyan-600',bg:'bg-cyan-100',route:'/ledger'},
    {key:'reorder',name:'Định mức tồn',desc:'Cảnh báo hàng sắp hết',icon:'alert-triangle',color:'text-red-600',bg:'bg-red-100',route:'/reorder'},
   ]},
  {title:'4. Cấu hình',desc:'Kế toán kho, phương pháp định giá.',
   items:[
    {key:'setup',name:'Cấu hình kho',desc:'Perpetual Inventory & TK',icon:'settings',color:'text-gray-600',bg:'bg-gray-100',route:'/setup'},
   ]},
]
function fmtShort(v){v=Number(v||0);if(v>=1e9)return (v/1e9).toFixed(1)+' tỷ';if(v>=1e6)return (v/1e6).toFixed(1)+' tr';if(v>=1e3)return (v/1e3).toFixed(0)+'k';return v.toLocaleString('vi-VN')}
async function logout(){loggingOut.value=true;try{await fetch('/api/method/portal.api.portal_logout',{method:'GET',credentials:'include'})}catch(e){}document.cookie.split(';').forEach((c)=>{const n=c.split('=')[0].trim();document.cookie=n+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'});window.location.href='/portal_app/login'}
function goPortal(){window.location.href='/portal_app'}
</script>
