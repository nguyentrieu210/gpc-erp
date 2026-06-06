<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center justify-between border-b bg-white px-4 py-3 sticky top-0 z-20">
  <div class="flex items-center gap-2"><FeatherIcon name="users" class="h-5 w-5 text-indigo-600"/><h1 class="text-lg font-bold text-gray-900">Nhân sự</h1></div>
  <div class="flex items-center gap-3">
    <Button variant="subtle" @click="goPortal" class="flex items-center gap-1"><FeatherIcon name="arrow-left" class="h-4 w-4"/><span>Cổng</span></Button>
    <div class="h-4 w-px bg-gray-200"/><span class="text-sm text-gray-600 font-medium">{{ user?.full_name||'Administrator' }}</span>
    <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600">Đăng xuất</Button>
  </div>
</header>
<main class="flex-1 p-4 max-w-6xl mx-auto w-full space-y-6">
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
    <StatCard label="Nhân viên" :value="stats.employees" icon="users" tone="indigo" to="/employees"/>
    <StatCard label="Đi làm hôm nay" :value="stats.present" icon="check-circle" tone="emerald"/>
    <StatCard label="Nghỉ phép" :value="stats.on_leave" icon="calendar" tone="amber" to="/leaves"/>
    <StatCard label="Mới tuyển" :value="stats.hired_this_month" icon="user-plus" tone="violet" to="/recruitment"/>
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
import { ref } from 'vue'
import { Button,FeatherIcon } from 'frappe-ui'
import { useFrappeApi,StatCard } from '@shared'
const { data:stats }=useFrappeApi('hr.api.get_hr_dashboard',{initialData:{employees:0,present:0,on_leave:0,hired_this_month:0}})
const { data:user }=useFrappeApi('portal.api.get_current_user')
const loggingOut=ref(false)
const mods=[
  {key:'emp',name:'Quản lý nhân sự',desc:'Hồ sơ NV, hợp đồng, quyết định, timeline',icon:'users',color:'text-indigo-600',bg:'bg-indigo-100',route:'/employees'},
  {key:'recruit',name:'Tuyển dụng',desc:'Pipeline, AI CV, phỏng vấn, thư mời',icon:'user-plus',color:'text-violet-600',bg:'bg-violet-100',route:'/recruitment'},
  {key:'leave',name:'Nghỉ phép',desc:'Đơn nghỉ, số dư ngày phép',icon:'calendar',color:'text-amber-600',bg:'bg-amber-100',route:'/leaves'},
  {key:'att',name:'Chấm công',desc:'Bảng công tháng',icon:'clock',color:'text-teal-600',bg:'bg-teal-100',route:'/attendance'},
  {key:'payroll',name:'Bảng lương',desc:'Chạy lương, chốt kỳ, in phiếu',icon:'dollar-sign',color:'text-emerald-600',bg:'bg-emerald-100',route:'/payroll'},
  {key:'benefits',name:'Thuế & Phúc lợi',desc:'Ước tính BHXH, thuế TNCN',icon:'shield',color:'text-rose-600',bg:'bg-rose-100',route:'/benefits'},
  {key:'expense',name:'Chi phí',desc:'Đề nghị thanh toán',icon:'credit-card',color:'text-orange-600',bg:'bg-orange-100',route:'/expenses'},
  {key:'perf',name:'Hiệu suất',desc:'KPI, đánh giá chu kỳ',icon:'trending-up',color:'text-sky-600',bg:'bg-sky-100',route:'/performance'},
  {key:'snr',name:'Thâm niên',desc:'Kỷ niệm, khen thưởng',icon:'award',color:'text-amber-600',bg:'bg-amber-100',route:'/seniority'},
  {key:'setup',name:'HR Setup',desc:'Danh mục phòng ban, chức vụ',icon:'settings',color:'text-gray-600',bg:'bg-gray-100',route:'/hr-setup'},
]
async function logout(){loggingOut.value=true;try{await fetch('/api/method/portal.api.portal_logout',{method:'GET',credentials:'include'})}catch(e){}document.cookie.split(';').forEach((c)=>{const n=c.split('=')[0].trim();document.cookie=n+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'});window.location.href='/portal_app/login'}
function goPortal(){window.location.href='/portal_app'}
</script>
