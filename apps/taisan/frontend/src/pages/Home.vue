<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center justify-between border-b bg-white px-4 py-3 sticky top-0 z-20">
  <div class="flex items-center gap-2"><FeatherIcon name="tool" class="h-5 w-5 text-teal-600"/><h1 class="text-lg font-bold text-gray-900">Tài sản</h1></div>
  <div class="flex items-center gap-3">
    <Button variant="subtle" @click="goPortal" class="flex items-center gap-1"><FeatherIcon name="arrow-left" class="h-4 w-4"/><span>Cổng</span></Button>
    <div class="h-4 w-px bg-gray-200"/><span class="text-sm text-gray-600 font-medium">{{ user?.full_name || 'Administrator' }}</span>
    <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600">Đăng xuất</Button>
  </div>
</header>
<main class="flex-1 p-4 max-w-6xl mx-auto w-full space-y-6">
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
    <StatCard label="Tổng tài sản" :value="d?.total_assets??0" icon="tool" tone="teal" to="/assets"/>
    <StatCard label="Nguyên giá" :value="fmtShort(d?.total_gross_value)" icon="dollar-sign" tone="indigo"/>
    <StatCard label="Khấu hao lũy kế" :value="fmtShort(d?.total_accumulated_depreciation)" icon="trending-down" tone="amber"/>
    <StatCard label="Giá trị còn lại" :value="fmtShort(d?.net_book_value)" icon="bar-chart-2" tone="emerald"/>
  </div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Theo trạng thái</div>
      <div v-for="s in d?.by_status||[]" :key="s.status" class="flex items-center gap-2 py-1 text-sm">
        <span class="flex-1 text-gray-600">{{ s.status }}</span><span class="font-medium">{{ s.count }}</span>
      </div>
      <div v-if="!(d?.by_status||[]).length" class="text-sm text-gray-400">Chưa có tài sản</div>
    </div>
    <div class="app-card p-4">
      <div class="flex items-center mb-2"><div class="text-sm font-semibold flex-1">Tài sản mới nhất</div><button class="text-xs text-indigo-600" @click="$router.push('/assets')">Xem tất cả →</button></div>
      <button v-for="a in d?.recent_assets||[]" :key="a.name" class="w-full flex items-center gap-2 py-1.5 text-sm border-b last:border-0" @click="$router.push('/assets/'+a.name)">
        <span class="flex-1 text-left truncate"><span class="font-medium">{{ a.asset_name }}</span> · {{ a.asset_category }}</span>
        <span class="font-semibold">{{ fmtShort(a.purchase_amount) }}</span>
        <StatusBadge :status="a.status_vi" :dot="false"/>
      </button>
    </div>
  </div>
  <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Phân hệ</h2>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    <div v-for="m in mods" :key="m.key" class="app-card-interactive p-5" @click="$router.push(m.route)">
      <div class="flex items-start gap-3"><div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0" :class="m.bg"><FeatherIcon :name="m.icon" class="h-5 w-5" :class="m.color"/></div><div class="flex-1 min-w-0"><h3 class="font-semibold">{{ m.name }}</h3><p class="text-sm text-gray-500 mt-0.5">{{ m.desc }}</p></div></div>
    </div>
  </div>
</main>
</div>
</template>
<script setup>
import { ref } from 'vue'; import { Button,FeatherIcon } from 'frappe-ui'
import { useFrappeApi,StatCard,StatusBadge } from '@shared'
const { data:d }=useFrappeApi('taisan.api.get_dashboard',{initialData:{}})
const { data:user }=useFrappeApi('portal.api.get_current_user')
const loggingOut=ref(false)
const mods=[
  {key:'assets',name:'Danh sách TSCĐ',desc:'Tạo, quản lý, khấu hao, ghi giảm',icon:'list',color:'text-teal-600',bg:'bg-teal-100',route:'/assets'},
  {key:'cat',name:'Loại tài sản',desc:'Danh mục & TK hạch toán',icon:'folder',color:'text-blue-600',bg:'bg-blue-100',route:'/categories'},
  {key:'loc',name:'Vị trí',desc:'Nơi đặt tài sản',icon:'map-pin',color:'text-emerald-600',bg:'bg-emerald-100',route:'/locations'},
  {key:'mv',name:'Điều chuyển',desc:'Lịch sử di chuyển TS',icon:'repeat',color:'text-amber-600',bg:'bg-amber-100',route:'/movements'},
  {key:'mt',name:'Bảo dưỡng',desc:'Lịch & nhật ký bảo dưỡng',icon:'check-circle',color:'text-sky-600',bg:'bg-sky-100',route:'/maintenance'},
  {key:'rep',name:'Sửa chữa',desc:'Ghi nhận & chi phí sửa chữa',icon:'alert-triangle',color:'text-rose-600',bg:'bg-rose-100',route:'/repairs'},
  {key:'cfg',name:'Cấu hình',desc:'Tạo loại TS, vị trí',icon:'settings',color:'text-gray-600',bg:'bg-gray-100',route:'/setup'},
]
function fmtShort(v){v=Number(v||0);if(v>=1e9)return (v/1e9).toFixed(1)+' tỷ';if(v>=1e6)return (v/1e6).toFixed(1)+' tr';return v.toLocaleString('vi-VN')}
async function logout(){loggingOut.value=true;try{await fetch('/api/method/portal.api.portal_logout',{method:'GET',credentials:'include'})}catch(e){}document.cookie.split(';').forEach((c)=>{const n=c.split('=')[0].trim();document.cookie=n+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'});window.location.href='/portal_app/login'}
function goPortal(){window.location.href='/portal_app'}
</script>
